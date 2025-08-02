# Copyright (c) 2025, TST Developer and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime
from frappe.model.document import Document
from frappe.utils import get_first_day, get_last_day, nowdate,getdate
from hrms.payroll.doctype.payroll_entry.payroll_entry import PayrollEntry
from hrms.hr.doctype.leave_application.leave_application import get_leave_details
import math

class FinalSettlement(Document):
    def before_insert(self):
        get_employee_remaining_balance(self)
        
    def validate(self):
        self.calculate_end_of_service_data()
        if self.docstatus == 1:
            create_end_of_service_additional_salary(self.employee,self.company, self.end_of_service_benefit, self.resignation_date)
            create_payroll_for_employee(self.employee, self.company, posting_date=None, resignation_date = None)


    def calculate_end_of_service_data(self):
        """
        Calculate gratuity, adjust it based on deductions/earnings,
        and set working years and end of service benefit.
        """
        # Step 1: Calculate base gratuity
        self.working_years, gratuity_amount = calculate_end_of_service_gratuity(
            self.date_of_joining, self.resignation_date, self.current_salary
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


def calculate_end_of_service_gratuity(date_of_joining, resignation_date, monthly_salary):
    if not (date_of_joining and resignation_date and monthly_salary):
        return 0, 0

    # Parse strings if needed
    if isinstance(date_of_joining, str):
        date_of_joining = getdate(date_of_joining)
    if isinstance(resignation_date, str):
        resignation_date = getdate(resignation_date)


    # Calculate years of service
    years_of_service = math.floor((resignation_date - date_of_joining).days / 365.0)

    # Apply gratuity rule
    if years_of_service < 5:
        gratuity = years_of_service  * (monthly_salary / 2)
    else:
        gratuity = years_of_service * monthly_salary

    return years_of_service, round(gratuity, 2)



def create_end_of_service_additional_salary(employee,company, end_of_service_benefit, posting_date=None):
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
    additional_salary.overwrite_salary_structure_amount = 1
    additional_salary.insert()
    additional_salary.submit()

    return additional_salary.name



def create_payroll_for_employee(employee,company, posting_date=None, resignation_date = None):
    if not posting_date:
        posting_date = nowdate()

    # Define payroll period (resignation month)
    start_date = get_first_day(posting_date)
    end_date = get_last_day(resignation_date)

    # Create Payroll Entry
    payroll_entry = frappe.new_doc("Payroll Entry")
    payroll_entry.company = company
    payroll_entry.payroll_frequency = "Monthly"
    payroll_entry.start_date = start_date
    payroll_entry.end_date = end_date
    payroll_entry.posting_date = posting_date
    payroll_entry.exchange_rate = 1
    # payroll_entry.payroll_payable_account = get_default_payment_account(company)
    payroll_entry.payroll_payable_account = "2120 - Payroll Payable - T"

    # Add only the current employee
    payroll_entry.append("employees", {
        "employee": employee
    })

    # Insert and submit
    payroll_entry.insert()
    payroll_entry.submit()
    
    PayrollEntry.submit_salary_slips(payroll_entry)

    return payroll_entry.name

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

    # Calculate leave amount
    doc.leave_amount = salary_per_day * remaining_annual_leave
