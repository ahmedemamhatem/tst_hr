# Copyright (c) 2025, TST Developer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EmployeeEvaluation(Document):
    def validate(self):
        if self.employee_probation == "Confirmed" and self.probation_period in ["90 Days", "180 Days"]:
            frappe.throw(f"Can't Change Employee probation from {self.employee_probation} to {self.probation_period}")
            
        if self.docstatus == 1:
            if self.employee_probation != self.probation_period:
                self.update_employee_evaluation()
   
   
    def update_employee_evaluation(self):
        frappe.db.set_value("Employee", self.employee, "custom_probation_and_confirmation_period", self.probation_period)
        frappe.db.commit()
