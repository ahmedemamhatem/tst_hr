# Copyright (c) 2025, TST Developer and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class PromotionandSalaryAdjustment(Document):
	@frappe.whitelist()
	def validate(self):
		if self.designation and self.new_job_title and (self.designation == self.new_job_title):
			frappe.throw(_("No Changes In Job Title."))

		if self.current_salary and self.new_salary and (self.current_salary == self.new_salary):
			frappe.throw(_("No Changes In Salary."))
