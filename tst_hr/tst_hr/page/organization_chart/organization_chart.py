import frappe
from frappe.query_builder.functions import Count


@frappe.whitelist()
def get_children(parent=None, company=None, exclude_node=None, department=None, branch=None, section=None):
    frappe.msgprint(str(department))
    filters = [["status", "=", "Active"]]

    if company and company != "All Companies":
        filters.append(["company", "=", company])

    if parent and company and parent != company:
        filters.append(["reports_to", "=", parent])
    else:
        filters.append(["reports_to", "=", ""])

    if exclude_node:
        filters.append(["name", "!=", exclude_node])

    # ✅ Apply filters from the frontend
    if department:
        filters.append(["department", "=", department])
    if branch:
        filters.append(["branch", "=", branch])
    if section:
        filters.append(["custom_section", "=", section])

    employees = frappe.get_all(
        "Employee",
        fields=[
            "employee_name as name",
            "name as id",
            "lft",
            "rgt",
            "reports_to",
            "image",
            "designation as title",
        ],
        filters=filters,
        order_by="name",
    )

    for employee in employees:
        employee.connections = get_connections(employee.id, employee.lft, employee.rgt)
        employee.expandable = bool(employee.connections)

    return employees




def get_connections(employee: str, lft: int, rgt: int) -> int:
    Employee = frappe.qb.DocType("Employee")
    query = (
        frappe.qb.from_(Employee)
        .select(Count(Employee.name))
        .where((Employee.lft > lft) & (Employee.rgt < rgt) & (Employee.status == "Active"))
    ).run()

    return query[0][0]
