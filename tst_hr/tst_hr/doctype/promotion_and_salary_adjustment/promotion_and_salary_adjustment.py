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

		if self.docstatus == 1:
			self.update_employee_data()
   
   
   
	def update_employee_data(self):
		if self.new_job_title and not self.new_salary:
			frappe.db.sql("""
					update `tabEmployee` set designation = %(new_designation)s where name = %(employee_name)s
                 """,{
					"new_designation":self.new_job_title,
					"employee_name":self.employee
				 })
		else:
			# get employee doc to update it and append new log for salary update
			employee_doc = frappe.get_doc("Employee",self.employee)
			if self.new_job_title:
				employee_doc.designation = self.new_job_title
			employee_doc.ctc = self.new_salary
   
			employee_doc.append("custom_salary_logs",{
				"previous_salary":self.current_salary,
				"current_salary":self.new_salary,
				"change_reason":self.request_reason,
				"date":frappe.utils.today()
			})

			employee_doc.save()