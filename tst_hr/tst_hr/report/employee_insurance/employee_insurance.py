# Copyright (c) 2025, TST Developer and contributors
# For license information, please see license.txt

import frappe
from datetime import date, timedelta

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": "Employee Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 200},
        {"label": "Iqama No", "fieldname": "iqama_number", "fieldtype": "Data", "width": 150},
        {"label": "Insurance Expiry Date", "fieldname": "custom_expiry_date", "fieldtype": "Date", "width": 120},
    ]

def get_data(filters):
    today = date.today()
    one_month_later = today + timedelta(days=30)

    conditions = {
        "status": "Active",
        "custom_expiry_date": ["between", [today, one_month_later]]
    }

    if filters.get("designation"):
        conditions["designation"] = filters["designation"]

    if filters.get("department"):
        conditions["department"] = filters["department"]

    return frappe.db.get_all(
        "Employee",
        fields=[
            "employee_name",
            "custom_iqama_number as iqama_number",
            "custom_expiry_date as custom_expiry_date"
        ],
        filters=conditions,
        order_by="custom_expiry_date asc"
    )

