# Copyright (c) 2025, TST Developer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TerminationofContract(Document):
    def validate(self):
        if self.docstatus == 1:
            create_final_settlement(self.employee, self.name, self.date_of_termination)
            send_email(self)

def create_final_settlement(employee,document_name, termination_of_contract_date):
    # Create the document
    final_settlement = frappe.new_doc("Final Settlement")
    final_settlement.employee = employee
    final_settlement.reference_doctype = "Termination of Contract"
    final_settlement.reference_link = document_name
    final_settlement.end_date = termination_of_contract_date

    # Insert into the database (saved as draft)
    final_settlement.insert()

    return final_settlement.name


def send_email(self):
    # get employee user 
    user = frappe.get_cached_value("Employee",{"name":self.employee},"user_id")
    if not user:
        frappe.throw(_(f"please set employee user in Employee <a href='/app/employee/{self.employee}' target ='_blank'>{self.employee}</a>"))
    # Generate the main print format PDF
    pdf_content = frappe.get_print(self.doctype, self.name, print_format="Termination of Contract", as_pdf=True)
    filename = f"{self.name}.pdf"

    # Attachments list
    attachments = [{
        "fname": filename,
        "fcontent": pdf_content
    }]

    # Send email
    frappe.sendmail(
        recipients=user,
        subject=f"Termination of Contract",
        message="""
            <p>Termination of Contract</p>
        """,
        attachments=attachments
    )