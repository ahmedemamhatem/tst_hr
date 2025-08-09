# Copyright (c) 2025, TST Developer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TerminationofContract(Document):
	def validate(self):
		if self.docstatus == 1:
			create_final_settlement(self.employee, self.name, self.date_of_termination)


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
