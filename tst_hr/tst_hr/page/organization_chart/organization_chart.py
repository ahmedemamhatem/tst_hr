import frappe
from frappe.query_builder.functions import Count

@frappe.whitelist()
def get_children(parent=None, company=None, exclude_node=None, department=None, designation=None, branch=None):
    # Always return at least an empty list
    try:
        filters = [["status", "=", "Active"]]
        
        # Apply filters
        if company and company != "All Companies":
            filters.append(["company", "=", company])
        
        if department and department != "All Departments":
            filters.append(["department", "=", department])
        
        # Fix typo: "designation" instead of "designation"
        if designation and designation != "All Designations":
            filters.append(["designation", "=", designation])

        if branch and branch != "All Branches":
            filters.append(["branch", "=", branch])

        # Improved parent node handling
        if parent and parent != "null" and parent != "undefined":
            filters.append(["reports_to", "=", parent])
        else:
            filters.append(["reports_to", "=", ""])  # Get root nodes

        if exclude_node:
            filters.append(["name", "!=", exclude_node])

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
                "department",
                "designation",
                "branch"
            ],
            filters=filters,
            order_by="name",
        )

        for employee in employees:
            employee.connections = get_connections(
                employee.id, 
                employee.lft, 
                employee.rgt,
                department=department,
                designation=designation,
                branch=branch
            )
            employee.expandable = bool(employee.connections)

        return employees or []  # Ensure we always return a list

    except Exception as e:
        frappe.log_error(f"Error in get_children: {str(e)}")
        return []

def get_connections(employee: str, lft: int, rgt: int, department=None, designation=None, branch=None) -> int:
    try:
        Employee = frappe.qb.DocType("Employee")
        query = (
            frappe.qb.from_(Employee)
            .select(Count(Employee.name))
            .where(
                (Employee.lft > lft) & 
                (Employee.rgt < rgt) & 
                (Employee.status == "Active")
            )
        )
        
        if department and department != "All Departments":
            query = query.where(Employee.department == department)

        if designation and designation != "All Designations":
            query = query.where(Employee.designation == designation)

        if branch and branch != "All Branches":
            query = query.where(Employee.branch == branch)

        return query.run()[0][0] or 0
    except Exception as e:
        frappe.log_error(f"Error in get_connections: {str(e)}")
        return 0