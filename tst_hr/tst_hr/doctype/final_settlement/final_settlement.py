# Copyright (c) 2025, TST Developer and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime
from frappe.model.document import Document
from frappe.utils import get_first_day, get_last_day, nowdate,getdate
from hrms.hr.doctype.leave_application.leave_application import get_leave_details
import math

class FinalSettlement(Document):
    def before_insert(self):
        get_employee_remaining_balance(self)
        
    def validate(self):
        self.calculate_end_of_service_data()
        if self.docstatus == 1:
            if self.end_of_service_benefit and self.end_of_service_benefit > 0.0:
                create_end_of_service_additional_salary(self.employee,self.company,self.name, self.end_of_service_benefit, self.end_date)
            create_payroll_for_employee(self.employee, self.company, self.name, posting_date=None, end_date = self.end_date)
            update_employee_status(self.employee,"Left",self.end_date)
            create_final_clearance(self)
            
    def on_cancel(self):
        update_employee_status(self.employee,"Active",None)
        


    def calculate_end_of_service_data(self):
        """
        Calculate gratuity, adjust it based on deductions/earnings,
        and set working years and end of service benefit.
        """
        # Step 1: Calculate base gratuity
        self.working_years, gratuity_amount = calculate_end_of_service_gratuity(
            self.date_of_joining, self.end_date, self.current_salary
        )

        # Step 2: Adjust based on additional earnings/deductions
        if self.additional_salary:
            for row in self.additional_salary:
                if row.type == "Deduction":
                    gratuity_amount -= row.amount
                elif row.type == "Earning":
                    gratuity_amount += row.amount

        # Step 3: Prevent negative gratuity
        gratuity_amount = max(gratuity_amount, 0)

        # Step 4: Final total = gratuity + leave encashment
        self.end_of_service_benefit = gratuity_amount + (self.leave_amount or 0)

        # Step 5: Round years to 2 decimal places
        self.working_years = round(self.working_years, 2)


def calculate_end_of_service_gratuity(date_of_joining, end_date, monthly_salary):
    if not (date_of_joining and end_date and monthly_salary):
        return 0, 0

    # Parse strings if needed
    if isinstance(date_of_joining, str):
        date_of_joining = getdate(date_of_joining)
    if isinstance(end_date, str):
        end_date = getdate(end_date)


    # Calculate years of service
    years_of_service = math.floor((end_date - date_of_joining).days / 365.0)

    # Apply gratuity rule
    if years_of_service < 5:
        gratuity = years_of_service  * (monthly_salary / 2)
    else:
        gratuity = years_of_service * monthly_salary

    return years_of_service, round(gratuity, 2)



def create_end_of_service_additional_salary(employee,company,document, end_of_service_benefit, posting_date=None):
    if not posting_date:
        posting_date = nowdate()

    # Find the salary component marked as end of service
    component = frappe.get_value("Salary Component", {"custom_is_end_of_service": 1}, "name")
    if not component:
        frappe.throw("No Salary Component found with 'End of Service' marked (custom_is_end_of_service = 1)")

    # Create the Additional Salary record
    additional_salary = frappe.new_doc("Additional Salary")
    additional_salary.employee = employee
    additional_salary.salary_component = component
    additional_salary.amount = end_of_service_benefit
    additional_salary.payroll_date = posting_date
    additional_salary.company = company
    additional_salary.custom_reference_doctype = "Final Settlement"
    additional_salary.custom_reference_link = document
    
    additional_salary.overwrite_salary_structure_amount = 1
    additional_salary.insert()
    additional_salary.submit()

    return additional_salary.name



def create_payroll_for_employee(employee, company, document, posting_date=None, end_date=None):
    """
    Creates and submits a payroll entry for a specific employee.
    
    Args:
        employee (str): Employee ID
        company (str): Company name
        document (str): Reference document name
        posting_date (str, optional): Posting date for payroll. Defaults to current date.
        end_date (str, optional): End date of payroll period. Required.
        
    Returns:
        str: Name of the created payroll entry
        
    Raises:
        frappe.exceptions.ValidationError: If payroll creation fails
    """
    if not posting_date:
        posting_date = nowdate()
        
    if not end_date:
        raise ValueError("end_date parameter is required")

    # Define payroll period
    start_date = get_first_day(posting_date)

    try:
        # Create Payroll Entry
        payroll_entry = frappe.get_doc({
            "doctype": "Payroll Entry",
            "company": company,
            "payroll_frequency": "Monthly",
            "custom_reference_doctype": "Final Settlement",
            "custom_reference_link": document,
            "start_date": start_date,
            "end_date": end_date,
            "posting_date": posting_date,
            "exchange_rate": 1,
            "payroll_payable_account": get_default_payment_account(company)
            # "payroll_payable_account": "2120 - Payroll Payable - T"
        })

        # Add only the current employee
        payroll_entry.append("employees", {
            "employee": employee
        })

        # Insert the document
        payroll_entry.insert(ignore_permissions=True)
        
        # Refresh the document to ensure it exists
        frappe.db.commit()
        payroll_entry.reload()

        if not payroll_entry.name:
            raise frappe.ValidationError("Payroll Entry creation failed")

        # Submit the document
        payroll_entry.submit()
        
        # Submit salary slips - called as instance method
        payroll_entry.submit_salary_slips()
        
        # Commit changes
        frappe.db.commit()
        
        return payroll_entry.name

    except Exception as e:
        frappe.log_error(f"Failed to create payroll for employee {employee}: {str(e)}")
        frappe.db.rollback()
        raise


def get_default_payment_account(company):
    return frappe.get_value("Company", company, "default_payroll_payable_account")

def get_employee_remaining_balance(doc):
    if not doc.employee or not doc.posting_date:
        return

    leave_details = get_leave_details(doc.employee, doc.posting_date)

    if not leave_details or "leave_allocation" not in leave_details:
        return

    annual_leave = leave_details["leave_allocation"].get("Annual", {})
    remaining_annual_leave = annual_leave.get("remaining_leaves", 0)

    # Set remaining leave days
    doc.remaining_leave_days = remaining_annual_leave

    # Calculate salary per day
    salary_per_day = doc.current_salary / 30 if doc.current_salary else 0
    
    # Set Salary Per Day
    doc.salary_per_day = salary_per_day

    # Calculate leave amount
    doc.leave_amount = salary_per_day * remaining_annual_leave


def update_employee_status(employee,status,relieving_date):
    frappe.db.sql("""
                  update `tabEmployee` set status = %(status)s,relieving_date = %(relieving_date)s where name = %(employee)s
                  """,{
                      "status":status,
                      "employee":employee,
                      "relieving_date":relieving_date
                  })
    
    
def create_final_clearance(self):
    final_clearance = frappe.new_doc("Final Clearance")
    final_clearance.employee = self.employee
    final_clearance.reference_doctype = "Final Settlement"
    final_clearance.reference_link = self.name
    
    final_clearance.insert()