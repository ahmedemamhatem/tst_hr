import frappe
@frappe.whitelist()
def before_insert(doc,methode = None):
    calculate_base_salary(doc)
    
def on_submit(doc,method = None):
    update_employee_salary(doc)
    
    
def calculate_base_salary(doc):
    if doc.salary_structure:
        # Get total earnings and total deductions from Salary Detail in one query
        result = frappe.db.sql("""
            SELECT
                SUM(CASE WHEN parentfield = 'earnings' THEN amount ELSE 0 END) AS total_earning,
                SUM(CASE WHEN parentfield = 'deductions' THEN amount ELSE 0 END) AS total_deduction
            FROM `tabSalary Detail`
            WHERE parent = %(salary_structure)s
              AND parenttype = 'Salary Structure'
        """, {
            "salary_structure": doc.salary_structure
        })

        # Extract values or default to 0.0
        total_earning = result[0][0] or 0.0
        total_deduction = result[0][1] or 0.0

        # Calculate net salary
        net_salary = total_earning - total_deduction

        # Set base salary on the document
        doc.base = net_salary

        
def update_employee_salary(doc):
    # get employee doc to update it and append new log for salary update
    employee_doc = frappe.get_doc("Employee",doc.employee)
    employee_doc.ctc = doc.base

    employee_doc.append("custom_salary_logs",{
        "previous_salary":employee_doc.ctc,
        "current_salary":doc.base,
        "reference_doctype":"Salary Structure Assignment",
        "reference_link":doc.name,
        # "change_reason":doc.request_reason,
        "date":frappe.utils.today()
    })

    employee_doc.save()   
        
        