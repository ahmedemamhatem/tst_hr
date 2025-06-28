import frappe
from frappe.utils import getdate
from collections import defaultdict

@frappe.whitelist()
def get_monthly_leave_summary(designation=None, department=None):
    
    conditions = "docstatus = 1"
    if designation:
        conditions += f" AND employee IN (SELECT name FROM `tabEmployee` WHERE designation = '{designation}')"
    if department:
        conditions += f" AND employee IN (SELECT name FROM `tabEmployee` WHERE department = '{department}')"

    leave_apps = frappe.db.sql(f"""
        SELECT from_date
        FROM `tabLeave Application`
        WHERE {conditions}
    """, as_dict=True)

    summary = defaultdict(int)
    for row in leave_apps:
        month = getdate(row.from_date).month
        summary[month] += 1

    return summary
