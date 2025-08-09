# Copyright (c) 2025, TST Developer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FinalClearance(Document):
	def on_submit(self):
		create_experience_certificate(self)

def create_experience_certificate(self):
    final_clearance = frappe.new_doc("Experience Certificate")
    final_clearance.employee = self.employee
    final_clearance.subject = "شهادة خبرة"
    final_clearance.reference_doctype = "Final Clearance"
    final_clearance.reference_link = self.name
    
    final_clearance.insert()