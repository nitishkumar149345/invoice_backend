from datetime import date
from typing import List, Optional

from database.constants import OPENAI_API_KEY
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, EmailStr, Field


class LineItemFields(BaseModel):

    service: str = Field(..., description="The service or item of the invoice")
    quantity: int = Field(..., description="The quantity of the service or item")
    unit_price: float = Field(..., description="The price of each service or item")
    unit_tax: float = Field(..., description= "The tax imposed on each service or item")
    line_price: float = Field(..., description="Total price of the line, after including quantity, unit tax to unit price")




class InvoiceFields(BaseModel):

    invoice_number: str = Field(..., description="Unique identifier for the invoice.")
    order_date: date = Field(..., description="Date when the order was placed.")
    due_date: Optional[date] = Field(None, description="Date by which payment is due.If not use null")
    invoice_from: str = Field(..., description="Address details of the issuer of the invoice.")
    invoice_to: str = Field(..., description="Address details of the recipient of the invoice.")
    total_amount: float = Field(..., description="Total amount payable for the invoice.")
    currency: Optional[str] = Field(None, description="Currency in which the invoice is issued.")
    tax: float = Field(..., description="Total tax applied to the invoice.")

    line_items: List[LineItemFields] = Field(..., description="List of line items with details 'services','quantity', 'unit_price', 'unit_tax', representing the details of line items of the invoice")

    customer_name: str = Field(..., description="Name of the customer or business.")
    email: Optional[EmailStr] = Field(None, description="Email address of the customer.")
    phone: Optional[str] = Field(None, description="Phone number of the customer.")
    address: str = Field(..., description="Address of the customer.")
    gst_number: Optional[str] = Field(None, description="GST or tax identification number.")



def extract_invoice_details(context: str):
    """
    Extract specific invoice details from the provided content using an LLM.

    Args:
        context (str): The raw invoice content as input.

    Returns:
        Union[InvoiceFields, None]: Parsed invoice details or None if the extraction fails.
    """
    llm_model = ChatOpenAI(temperature=0, api_key=OPENAI_API_KEY)

    prompt_template = ChatPromptTemplate.from_messages([
        ('system', '''
            Role: Act as a Document Analyst.
            Task: Your task is to identify the following details from the provided unstructured invoice content:
                - Invoice number, order date, due date, invoice from, invoice to, total amount, currency, tax, line items, 
                quantity, unit price, unit tax, line price, customer name, email, phone, address, gst number, and format them as JSON.
                - For fields having no data, keep None for string type fields and 1 as default for numerical fields.
                - Format the date fields properly, use yyyy-mm-dd format.
                - \n\n{format_instructions}
            '''),
        ('user', '{context}')
    ])


    parser = JsonOutputParser(pydantic_object=InvoiceFields)
    # try:

    chain = prompt_template | llm_model | parser

    result = chain.invoke({
        "format_instructions": parser.get_format_instructions(),
        "context": context
    })

    return result  
    # except Exception as e:
        # print(f"Error extracting invoice details: {e}")
        # return None

