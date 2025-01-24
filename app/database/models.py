from datetime import datetime, timedelta
from enum import Enum as PYEnum

import pytz
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship

from .sql_client import Base

IST = pytz.timezone('Asia/Kolkata')

def get_current_time():
    return datetime.now(IST) + timedelta(hours=5, minutes=30)




class InvoiceStatus(PYEnum):
    PENDING = "Pending"
    PAID = "Paid"
    CANCELLED = "Cancelled"


class InvoiceType(PYEnum):
    PAYABLE = "Payable"
    RECEIVABLE = "Receivable"


class InvoiceHeaders(Base):
    __tablename__ = "invoice_headers"

    invoice_id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    invoice_number = Column(String(50), unique=True, nullable=False)  
    order_date = Column(Date, nullable=False)  
    due_date = Column(Date, nullable=True)  
    invoice_from = Column(String(225), nullable=False) 
    invoice_to = Column(String(225), nullable=False)  
    total_amount = Column(Numeric(16, 2), nullable=False)  
    currency = Column(String(20), default="USD", nullable=True)  
    tax = Column(Numeric(10, 2), nullable=True)  
    # tax1 = Column(Numeric(10, 2), nullable=True)  
    invoice_status = Column(Enum(InvoiceStatus), default= InvoiceStatus.PENDING, nullable= False)
    invoice_type = Column(Enum(InvoiceType), default= InvoiceType.RECEIVABLE, nullable=False)

    created_at = Column(DateTime, default= get_current_time())
    updated_at = Column(DateTime, default= get_current_time())

    customer_id = Column(Integer, ForeignKey('customer_master.customer_id'), nullable=True)  

    # relationships
    customer = relationship("CustomerMaster", back_populates="invoices")
    line_items = relationship("InvoiceLineItems", back_populates="invoice",cascade="delete")
    payment = relationship("Payments", back_populates="invoice")



class InvoiceLineItems(Base):
    __tablename__ = "invoice_line_items"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # foreign key for invoice_headers table
    invoice_id = Column(Integer, ForeignKey('invoice_headers.invoice_id'), nullable=False)  

    item = Column(String(124), nullable=False)  
    quantity = Column(Integer, nullable=True, default= 1 )
    unit_price = Column(Numeric(16, 2), nullable=False) 
    unit_tax = Column(Numeric(10, 2), nullable=False)  
    line_price = Column(Numeric(16,2), nullable=False) 


    invoice = relationship("InvoiceHeaders", back_populates="line_items")


class Payments(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key= True, autoincrement= True, index= True)
    customer_id = Column(Integer, ForeignKey('customer_master.customer_id'), nullable=False)
    invoice_id = Column(Integer, ForeignKey('invoice_headers.invoice_id'), nullable=True)

    transaction_on = Column(Date, nullable= False)  
    transaction_amount = Column(Numeric(16, 2), nullable= False)
    currency = Column(String(20), default= "USD", nullable= True)  
    payment_status = Column(Enum(InvoiceStatus), default= InvoiceStatus.PENDING,nullable=False )
    reference_id = Column(String(64), unique=True, nullable=False)
    transaction_id = Column(String(64), nullable=True)

    invoice = relationship("InvoiceHeaders", back_populates="payment")
    customer = relationship("CustomerMaster", back_populates="customer_payments")


class CustomerMaster(Base):
    __tablename__ = "customer_master"

    customer_id = Column(Integer, primary_key= True, autoincrement= True, index= True)
    customer_name = Column(String(100), nullable= False)  
    email = Column(String(100), nullable= True, unique= True, index= True)
    phone = Column(String(16), nullable= True)
    address = Column(String(225), nullable= False)  
    gst_number = Column(String(64), unique= True, nullable= True) 
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
 

    invoices = relationship("InvoiceHeaders", back_populates="customer")
    customer_payments = relationship("Payments", back_populates="customer", cascade="all, delete-orphan")



class Companies(Base):
    __tablename__ = "companies"

    company_id = Column(Integer, primary_key=True, autoincrement=True, index= True)
    company_name = Column(String(125))
    # company_address = Column(String(225))
    

    