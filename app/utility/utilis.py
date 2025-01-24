from database.models import CustomerMaster, InvoiceHeaders, InvoiceLineItems


def get_customer_model(invoice: dict)-> dict:
    try:
        customer = CustomerMaster(
            customer_name=invoice.customer_name,
            email=invoice.email,
            phone=invoice.phone,
            address=invoice.address,
            gst_number=invoice.gst_number,
        )
    except Exception as e:
        raise Exception(f"Serialization Error:{e}")
    
    return customer




def get_invoice_header_model(invoice: dict, customer_id:int)-> dict:
    try:
        invoice_header_data = InvoiceHeaders(
        invoice_number=invoice.invoice_number,
        order_date=invoice.order_date,
        due_date=invoice.due_date,
        invoice_from=invoice.invoice_from,
        invoice_to = invoice.invoice_to,
        total_amount=invoice.total_amount,
        currency=invoice.currency,
        tax=invoice.tax,
        customer_id = customer_id
    )
    except Exception as e:
        raise Exception(f"Serialization Error:{e}")
    
    return invoice_header_data





def get_invoice_line_model(invoice: dict, invoice_header_id:int)-> list:


    line_items = [
        InvoiceLineItems(
            invoice_id = invoice_header_id,
            item = item.service,
            quantity = item.quantity,
            unit_price = item.unit_price,
            unit_tax = item.unit_tax,
            line_price = item.line_price
        )
        for item in invoice.line_items
    ]
    return line_items
