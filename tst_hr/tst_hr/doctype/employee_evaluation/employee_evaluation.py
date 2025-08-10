# Copyright (c) 2025, TST Developer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class EmployeeEvaluation(Document):
    def validate(self):
        if self.employee_probation == "Confirmed" and self.probation_period in ["90 Days", "180 Days"]:
            frappe.throw(f"Can't Change Employee probation from {self.employee_probation} to {self.probation_period}")
            
        if self.docstatus == 1:
            if self.employee_probation != self.probation_period:
                self.update_employee_evaluation()
            send_email(self)
   
   
    def update_employee_evaluation(self):
        frappe.db.set_value("Employee", self.employee, "custom_probation_and_confirmation_period", self.probation_period)
        frappe.db.commit()


def send_email(self):
    # get employee user 
    user = frappe.get_cached_value("Employee",{"name":self.employee},"user_id")
    if not user:
        frappe.throw(_(f"please set employee user in Employee <a href='/app/employee/{self.employee}' target ='_blank'>{self.employee}</a>"))
    # Generate the main print format PDF
    pdf_content = frappe.get_print(self.doctype, self.name, print_format="Employee Evaluation", as_pdf=True)
    filename = f"{self.name}.pdf"

    # Attachments list
    attachments = [{
        "fname": filename,
        "fcontent": pdf_content
    }]

    # Send email
    frappe.sendmail(
        recipients=user,
        subject=f"Employee Evaluation",
        message="""
            <p>Employee Evaluation</p>
        """,
        attachments=attachments
    )