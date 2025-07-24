import frappe

@frappe.whitelist()
def get_organization_tree(department=None, branch=None, section=None, company=None):
    head_filters = {"reports_to": ["in", ["", None]]}
    if department:
        head_filters["department"] = department
    if branch:
        head_filters["branch"] = branch
    if section:
        head_filters["section"] = section
    if company:
        head_filters["company"] = company

    heads = frappe.get_all(
        "Employee",
        filters=head_filters,
        fields=["name", "employee_name", "designation"]
    )

    all_emps = frappe.get_all(
        "Employee",
        fields=["name", "employee_name", "reports_to", "designation"]
    )
    emp_map = {e["name"]: e for e in all_emps}

    def build_node(emp_id):
        emp = emp_map[emp_id]
        node = {
            "name": emp["employee_name"],
            "id": emp["name"],
            "title": emp.get("designation", ""),
            "children": []
        }
        children = [e["name"] for e in all_emps if e.get("reports_to") == emp_id]
        for child_id in children:
            node["children"].append(build_node(child_id))
        if not node["children"]:
            node.pop("children")
        return node

    org_tree = {
        "name": "Organization",
        "id": "organization",
        "children": [build_node(h["name"]) for h in heads]
    }

    return org_tree