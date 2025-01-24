import os
from datetime import date
from typing import Annotated, List

from database.models import Companies, CustomerMaster, InvoiceHeaders, InvoiceLineItems
from database.sql_client import Base, SessionLocal, engine
from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from utility import field_extract
from utility.doc_parser import DocParser
from utility.input_output_models import (
    CompaniesDate,
    CompaniesResponseModel,
    CustomerResponseModel,
    InvoiceData,
    InvoiceResponseModel,
    TopCustomers,
    TopServices,
)
from utility.utilis import (
    get_customer_model,
    get_invoice_header_model,
    get_invoice_line_model,
)


def get_db():
    """
    Creates a database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


db_dependency = Annotated[Session, Depends(get_db)]
Base.metadata.create_all(bind=engine)

uploads_dir = "/Users/omniadmin/Desktop/invoice_remittance_project/app/uploads"


@app.get("/")
def testing_api(request: Request):
    return JSONResponse(content="apis are working", status_code=status.HTTP_200_OK)


# @app.middleware("http")
# async def log_request_body(request: Request, call_next):
#     body = await request.body()
#     print("Raw Request Body:", body.decode("utf-8"))  # Logs the raw body
#     response = await call_next(request)
#     return response


@app.post("/v1/upload_file", status_code=status.HTTP_200_OK)
async def upload_invoice(request: Request, file: UploadFile = File(...)):
    """
    Uploads an invoice file, parses it, and returns extracted invoice details.
    1. Saves uploaded file to disk
    2. Parses the document using DocParser
    3. Extracts invoice details using field_extract utility
    """

    file_path = os.path.join(uploads_dir, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    parser = DocParser(file=file_path)
    data = parser.parse_doc()

    json_fields = field_extract.extract_invoice_details(context=data)
    return json_fields


@app.post("/v1/companies", status_code=status.HTTP_201_CREATED)
def add_super_customer(customer: CompaniesDate, request: Request, db: db_dependency):
    """
    Creates a new company record in the database
    """
    super_customer = Companies(
        company_name=customer.company_name,
    )

    db.add(super_customer)
    db.commit()
    db.refresh(super_customer)
    return super_customer


@app.get("/v1/companies", response_model=List[CompaniesResponseModel])
def get_super_customers(request: Request, db: db_dependency):
    """
    Retrieves all companies from the database
    Returns empty list if no companies found
    """
    companies = db.query(Companies).all()
    if not companies:
        return JSONResponse(content=[], status_code=status.HTTP_200_OK)

    return companies


@app.put("/v1/companies/{company_id}", status_code=status.HTTP_200_OK)
def update_super_customer(
    request: Request,
    db: db_dependency,
    company_id: int,
    name: str | None = None,
    address: str | None = None,
):
    """
    Updates company information by company_id
    Optional parameters: name, address
    Returns 204 if company not found
    """
    company = db.query(Companies).filter_by(company_id=company_id).first()
    if not company:
        raise HTTPException(
            detail=f"No record found with id:{company_id}, can not update",
            status_code=status.HTTP_204_NO_CONTENT,
        )

    if name:
        company.company_name = name
    if address:
        company.company_address = address

    db.commit()
    db.refresh(company)
    return JSONResponse(
        content={"message": "company updated successfully"},
        status_code=status.HTTP_200_OK,
    )


@app.delete("/v1/companies/{company_id}", status_code=status.HTTP_200_OK)
def delete_super_companie(request: Request, db: db_dependency, company_id: int):
    """
    Deletes a company by company_id
    Returns 204 if company not found
    """
    company = db.query(Companies).filter_by(company_id=company_id).first()
    if not company:
        raise HTTPException(
            detail=f"No record found with id:{company_id}, can not update",
            status_code=status.HTTP_204_NO_CONTENT,
        )

    db.delete(company)
    db.commit()

    return JSONResponse(
        content={"message": "company deleted successfully"}, status_code=200
    )


@app.post("/v1/add_invoices", status_code=status.HTTP_200_OK)
def post_invoice(invoice: InvoiceData, request: Request, db: db_dependency):
    """
    Adds a new invoice to the database:
    1. Creates or retrieves customer
    2. Creates invoice header
    3. Creates invoice line items
    4. Handles invoice type (PAYABLE) for non-company customers
    """

    # raw_body = await request.body()
    # print("Raw Request Body:", raw_body.decode("utf-8"))

    # Convert the input body into a CustomerMaster model object
    new_customer = get_customer_model(invoice=invoice)

    # Check if the customer already exists in the database
    customer = (
        db.query(CustomerMaster)
        .filter_by(customer_name=new_customer.customer_name)
        .first()
    )
    if customer:
        customer_id = customer.customer_id  # Use existing customer's ID

    if not customer:
        # If the customer doesn't exist, create a new customer
        try:
            db.add(new_customer)
            db.commit()
            db.refresh(new_customer)

            customer_id = (
                new_customer.customer_id
            )  # Get the newly created customer's ID
        except Exception as e:
            raise HTTPException(
                detail=f"Error writing customer into db:{e}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

    # Create an invoice header for the new or existing customer

    invoice_header = get_invoice_header_model(invoice=invoice, customer_id=customer_id)

    is_owner = (
        db.query(Companies).filter_by(company_name=new_customer.customer_name).first()
    )

    if not is_owner:
        invoice_header.invoice_type = "PAYABLE"

    try:
        db.add(invoice_header)
        db.commit()
        db.refresh(invoice_header)
    except Exception as e:
        raise HTTPException(
            detail=f"Error writing invoice_header into db:{e}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Create line items for the invoice
    invoice_line_items = get_invoice_line_model(
        invoice=invoice, invoice_header_id=invoice_header.invoice_id
    )
    try:
        db.bulk_save_objects(invoice_line_items)
        db.commit()

    except Exception as e:
        raise HTTPException(
            detail=f"Error writing invoice_line_items into db:{e}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return JSONResponse(
        content="invoice data saved successfully", status_code=status.HTTP_200_OK
    )


@app.get(
    "/v1/list_invoices",
    response_model=List[InvoiceResponseModel],
    status_code=status.HTTP_200_OK,
)
def list_invoice(
    request: Request,
    db: db_dependency,
    order_date: date | None = None,
    invoice_status: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    customer_id: int | None = None,
):
    """
    Get invoices with multiple filter options:
    - order_date: Filter by specific date
    - invoice_status: Filter by status
    - customer_id: Filter by customer
    - start_date/end_date: Filter by date range
    Returns ordered by invoice_id
    """
    query = db.query(InvoiceHeaders)

    if order_date:
        query = query.filter(InvoiceHeaders.order_date == order_date)
    if invoice_status:
        query = query.filter(InvoiceHeaders.invoice_status == invoice_status)
    if customer_id:
        query = query.filter(InvoiceHeaders.customer_id == customer_id)
    if start_date:
        query = query.filter(InvoiceHeaders.order_date >= start_date)
    if end_date and start_date:
        query = query.filter(
            InvoiceHeaders.order_date >= start_date,
            InvoiceHeaders.order_date <= end_date,
        )

    invoices = query.order_by(InvoiceHeaders.invoice_id).all()
    if not invoices:
        return JSONResponse(content=[], status_code=status.HTTP_200_OK)

    return invoices


@app.get("/v1/get_invoices/{invoice_id}", response_model=InvoiceResponseModel)
def get_invoice_by_id(request: Request, invoice_id: int, db: db_dependency):
    """
    Retrieves a specific invoice by its ID
    Returns empty list if invoice not found
    """
    invoice = (
        db.query(InvoiceHeaders).filter(InvoiceHeaders.invoice_id == invoice_id).first()
    )
    if not invoice:
        return JSONResponse(content=[], status_code=status.HTTP_200_OK)

    return invoice


@app.get(
    "/v1/list_customers",
    response_model=List[CustomerResponseModel],
    status_code=status.HTTP_200_OK,
)
def list_customers(request: Request, db: db_dependency):
    """
    Retrieves all customers from database
    Returns ordered by customer_id
    Only returns customer_id and customer_name fields
    """
    try:
        customers = (
            db.query(CustomerMaster.customer_id, CustomerMaster.customer_name)
            .order_by(CustomerMaster.customer_id)
            .all()
        )
    except Exception as e:
        raise HTTPException(
            detail=f"Error getting customers:{e}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if not customers:
        return JSONResponse(content=[], status_code=status.HTTP_200_OK)

    return customers


@app.get("/v1/top_services", response_model=List[TopServices])
def fetch_top_services(request: Request, db: db_dependency):
    """
    Retrieves top 5 services/items based on total price:
    - Groups by item name
    - Sums unit prices
    - Orders by total price descending
    - Limits to top 5 results
    """
    try:
        services = (
            db.query(
                InvoiceLineItems.item,
                func.sum(InvoiceLineItems.unit_price).label("price"),
            )
            .group_by(InvoiceLineItems.item)
            .order_by(desc("price"))
            .limit(5)
        )

        return services
    except Exception as e:
        raise HTTPException(
            detail=f"Error fetching top services or items:{e}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@app.get("/v1/top_customers", response_model=List[TopCustomers])
def fetch_top_customers(request: Request, db: db_dependency):
    """
    Retrieves top 5 customers based on total invoice amounts:
    - Joins with CustomerMaster table
    - Groups by customer
    - Sums total invoice amounts
    - Orders by total amount descending
    - Limits to top 5 results
    """
    try:
        query = (
            db.query(
                InvoiceHeaders.customer_id,
                CustomerMaster.customer_name,
                func.sum(InvoiceHeaders.total_amount).label("amount"),
            )
            .join(CustomerMaster)
            .group_by(InvoiceHeaders.customer_id)
            .order_by(desc("amount"))
            .limit(5)
        )
        if not query:
            return JSONResponse(content=[], status_code=status.HTTP_200_OK)

        return query
    except Exception as e:
        raise HTTPException(
            detail=f"Error fetching top customers:{e}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI application using uvicorn server
    uvicorn.run(app, host="0.0.0.0", port=8000)
