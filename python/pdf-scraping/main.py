import json
import re
from os import path

import PyPDF2

CURRENT_DIR = path.dirname(__file__)

output = {}

with open(path.join(CURRENT_DIR, "invoice.pdf"), "rb") as pdf_file:
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    page_obj = pdf_reader.pages[0]
    page_text = page_obj.extract_text()
    page_text_lines = page_text.splitlines()

    [email, invoice_number] = (
        re.search(
            r"(?P<email>.*)Invoice Number (?P<invoice_number>.*)", page_text_lines[8]
        )
        .groupdict()
        .values()
    )
    [order_number] = (
        re.search(r"Order Number (?P<order_number>.*)", page_text_lines[9])
        .groupdict()
        .values()
    )
    [invoice_date] = (
        re.search(r"Invoice Date (?P<invoice_date>.*)", page_text_lines[10])
        .groupdict()
        .values()
    )
    [due_date] = (
        re.search(r"Due Date (?P<due_date>.*)", page_text_lines[11])
        .groupdict()
        .values()
    )
    [total_due] = (
        re.search(r"Total Due .(?P<total_due>.*)", page_text_lines[12])
        .groupdict()
        .values()
    )

    articles = []
    start_items_list_position = page_text_lines.index(
        "Hrs/Qty Service Rate/Price Adjust Sub Total"
    )
    [end_items_list_position] = [
        i for i, item in enumerate(page_text_lines) if item.startswith("Sub Total")
    ]
    for i in range(start_items_list_position + 1, end_items_list_position, 2):
        [amount, name] = (
            re.search(r"(?P<amount>[\d\.]*)(?P<name>.*)", page_text_lines[i])
            .groupdict()
            .values()
        )
        [description, price] = (
            re.search(
                r"(?P<description>.*)\$(?P<price>[\d\.]*)\s[\d\.]*%\s\$[\d\.]*",
                page_text_lines[i + 1],
            )
            .groupdict()
            .values()
        )
        articles.append(
            {"amount": amount, "name": name, "description": description, "price": price}
        )

    start_to_position = page_text_lines.index("To:")
    [start_from_position] = [
        i for i, item in enumerate(page_text_lines) if "From:" in item
    ]
    contact = {
        "from": page_text_lines[start_from_position + 1],
        "to": page_text_lines[start_to_position + 1],
    }

    output["email"] = email
    output["invoice_number"] = invoice_number
    output["order_number"] = order_number
    output["invoice_date"] = invoice_date
    output["due_date"] = due_date
    output["total_due"] = total_due
    output["articles"] = articles
    output["contact"] = contact

    print(json.dumps(output, indent=2))


# Output:
# {
#   "email": "admin@slicedinvoices.com",
#   "invoice_number": "INV-3337",
#   "order_number": "12345",
#   "invoice_date": "January 25, 2016",
#   "due_date": "January 31, 2016",
#   "total_due": "93.50",
#   "articles": [
#     {
#       "amount": "1.00",
#       "name": "Web Design",
#       "description": "This is a sample description...",
#       "price": "85.00"
#     }
#   ],
#   "contact": {
#     "from": "DEMO - Sliced Invoices",
#     "to": "Test Business"
#   }
# }
