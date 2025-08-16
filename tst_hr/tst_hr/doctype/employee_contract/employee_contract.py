# Copyright (c) 2025, TST Developer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EmployeeContract(Document):
    @frappe.whitelist()
    def after_insert(self):
        self.contract_no = self.name
  
    @frappe.whitelist()
    def on_submit(self):
        self.create_salary_structure()
  
  
    def create_salary_structure(self):
        earnings = []
        deductions = []

        if self.earnings:
            for row in self.earnings:
                earnings.append({
                    "salary_component":row.salary_component,
                    "amount":row.amount,
                })
    
        if self.deductions:
            for row in self.deductions:
                deductions.append({
                    "salary_component":row.salary_component,
                    "amount":row.amount,
                })
    
        salary_structure = frappe.get_doc({
            "doctype":"Salary Structure",
            "__newname":self.name,
            "company":self.company,
            "is_active":"Yes",
            "payroll_frequency":"Monthly",
            "custom_reference_doctype":self.doctype,
            "custom_reference_link":self.name,
            "deductions":deductions,
            "earnings":earnings
        })
        
        salary_structure.insert()
        salary_structure.submit()
        
        
        # create salary structure assignment for employee
        self.create_salary_structure_assignment(salary_structure.name)
        
        
    def create_salary_structure_assignment(self,salary_structure):
        salary_structure_assignment = frappe.get_doc({
            "doctype":"Salary Structure Assignment",
            "employee":self.employee_id,
            "salary_structure":salary_structure,
            "company":self.company,
            "from_date":self.start_date
        })
        
        salary_structure_assignment.insert()
        salary_structure_assignment.submit()
        
        
