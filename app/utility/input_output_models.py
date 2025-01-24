from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel


class LineItemFields(BaseModel):

    service: str 
    quantity: int 
    unit_price: float
    unit_tax: float 
    line_price: float




class InvoiceData(BaseModel):
    '''
    pydantic class representing input model for post api
    '''

    # invoice headers table data
    invoice_number: str
    order_date: date
    due_date: Optional[date] = None
    invoice_from: str
    invoice_to: str
    total_amount: float
    currency: Optional[str]
    tax: float

    # invoice line items table data
    line_items: List[LineItemFields]


    # customer master table data
    customer_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: str
    gst_number: Optional[str] = None




class InvoiceResponseModel(BaseModel):

    invoice_id: int
    invoice_number: str
    order_date: date
    due_date: Optional[datetime] = None
    invoice_from: str
    invoice_to: str
    total_amount: float
    currency: Optional[str] = None
    tax: float
    invoice_status: str
    invoice_type: str
    created_at: datetime
    # updated_at: datetime
    customer_id: int

class CustomerResponseModel(BaseModel):

    customer_id: int
    customer_name: str
    

class TopServices(BaseModel):

    item: str
    price: float

class TopCustomers(BaseModel):

    customer_id: int
    customer_name: str
    amount: float


class CompaniesDate(BaseModel):

    company_name: str
    # company_address: str


class CompaniesResponseModel(BaseModel):

    company_id: int
    company_name: str
    # company_address: str