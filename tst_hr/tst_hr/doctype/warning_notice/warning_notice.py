# Copyright (c) 2025, TST Developer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_months,today,getdate

class WarningNotice(Document):
    @frappe.whitelist()
    def validate(self):
        # check if first warning already exist
        self.check_warning()   
        
        if self.docstatus == 1:
            send_email(self)  
        
    def check_warning(self):
        # Try to get last submitted warning
        if self.first_warning and frappe.db.exists("Warning Notice",{"employee":self.employee,"docstatus":1,"name":["!=",self.name],"first_warning":1}):
            last_warning = frappe.get_last_doc("Warning Notice",filters = {"employee":self.employee,"docstatus":1,"name":["!=",self.name],"first_warning":1})
            
            if last_warning.first_warning:
                # calaculate six months from last warning
                six_months = add_months(last_warning.date,6)
                
                if getdate(today()) < six_months:
                    frappe.throw(f"First Warning ALready Exist For This Employee <a href='/app/warning-notice/{last_warning.name}' target ='_blank'>{last_warning.name}</a>")
                    
                    
def send_email(self):
    # get employee user 
    user = frappe.get_cached_value("Employee",{"name":self.employee},"user_id")
    if not user:
        frappe.throw(_(f"please set employee user in Employee <a href='/app/employee/{self.employee}' target ='_blank'>{self.employee}</a>"))
    # Generate the main print format PDF
    pdf_content = frappe.get_print(self.doctype, self.name, print_format="Warning Notice", as_pdf=True)
    filename = f"{self.name}.pdf"

    # Attachments list
    attachments = [{
        "fname": filename,
        "fcontent": pdf_content
    }]

    # Send email
    frappe.sendmail(
        recipients=user,
        subject=f"Warning",
        message="""
            <p>Warning</p>
        """,
        attachments=attachments
    )