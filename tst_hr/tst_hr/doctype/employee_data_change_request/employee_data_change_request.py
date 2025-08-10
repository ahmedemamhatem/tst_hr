# Copyright (c) 2025, TST Developer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class EmployeeDataChangeRequest(Document):
    def validate(self):
        if self.docstatus == 1:
            if not self.employee:
                frappe.throw("Employee is required")

            if self.update_personal_data:
                update_employee_field(self.employee, "marital_status", self.new_marital_status)
                update_employee_field(self.employee, "current_address", self.new_address)
                update_employee_field(self.employee, "personal_email", self.new_email)
                update_employee_field(self.employee, "cell_number", self.new_mobile_no)
                update_employee_field(self.employee, "custom_sponsor", self.new_sponsor)
                update_employee_field(self.employee, "custom_iqama_expiry_date", self.new_iqama_expiry_date)
                update_employee_field(self.employee, "custom_iqama_number", self.new_iqama_no)

            elif self.update_insurance_data:
                update_employee_field(self.employee, "custom_insurance_policy_type", self.new_insurance_policy_type)
                # update_employee_field(self.employee, "custom_expiry_date", self.new_expiry_date)
                # update_employee_field(self.employee, "health_insurance_provider", self.new_health_insurance_provider)

            elif self.update_bank_data:
                update_employee_field(self.employee, "bank_ac_no", self.new_bank_acount)
                update_employee_field(self.employee, "bank_name", self.new_bank_name)
                update_employee_field(self.employee, "bank_namibane", self.new_iban)
        if (self.repayment_periods and self.repayment_periods > 3) and (self.insurance_upgrade_cost and self.insurance_upgrade_cost <= 3000):
            frappe.throw(_("Insurance upgrade cost must be greater than 3000 if repayment periods exceed 3."))


def update_employee_field(employee, fieldname, value):
    if value:
        frappe.db.set_value("Employee", employee, fieldname, value)