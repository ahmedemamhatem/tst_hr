# Copyright (c) 2025, TST Developer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_months, getdate, nowdate, add_days
from frappe import _

class InternalDisciplinaryInvestigation(Document):
    def validate(self):
        # --- Investigators Table Validation ---
        all_confirmed = True
        if self.investigators:
            for inv in self.investigators:
                if inv.confirm and not inv.notes:
                    frappe.throw(_("Please enter notes for every investigator row where 'Confirm' is checked."))
                if not inv.confirm:
                    all_confirmed = False
            self.investigators_confirm = 1 if all_confirmed else 0
        else:
            self.investigators_confirm = 0

        # --- Share doc with users in investigators table if not already shared ---
        self.share_with_investigators()

        # --- Existing logic below ---
        if self.docstatus == 1:
            if self.terminate_employment:
                # update_employee_status(self.employee, "Inactive")
                create_employee_termination(self)
            elif self.salary_deduction:
                self.create_absent_attendance()
            elif self.issue_warning:
                create_warning_if_needed(self.name, self.employee, self.date)

    def after_insert(self):
        # --- Share doc with users in investigators table if not already shared ---
        self.share_with_investigators()

    def share_with_investigators(self):
        if not self.is_new():
            # Share the doc with each User (if any) linked to Employee in investigators table
            for inv in self.investigators or []:
                # Get user linked to employee
                user = frappe.db.get_value("Employee", inv.employee, "user_id")
                if user:
                    # Check if already shared
                    already_shared = frappe.db.exists(
                        "DocShare",
                        {
                            "user": user,
                            "share_doctype": self.doctype,
                            "share_name": self.name
                        }
                    )
                    if not already_shared:
                        # Share with read and write permissions
                        frappe.share.add(
                            self.doctype,
                            self.name,
                            user,
                            read=1,
                            write=1,
                            share=0,
                            everyone=0
                        )

    def create_absent_attendance(self):
        # Ensure required fields are present
        if not self.employee or not self.from_date or not self.deduction_days:
            frappe.throw("Employee, Deduction From Date, and Deduction Days are required")

        from_date = getdate(self.from_date)

        for i in range(self.deduction_days):
            attendance_date = add_days(from_date, i)

            # Check if attendance already exists for that day
            existing = frappe.db.exists(
                "Attendance",
                {
                    "employee": self.employee,
                    "attendance_date": attendance_date
                }
            )
            if existing:
                continue  # Skip if already exists

            attendance = frappe.new_doc("Attendance")
            attendance.employee = self.employee
            attendance.attendance_date = attendance_date
            attendance.status = "Absent"
            attendance.custom_reference_doctype = self.doctype
            attendance.custom_reference_link = self.name
            attendance.company = self.company
            attendance.docstatus = 1  # Mark as submitted
            attendance.insert(ignore_permissions=True)

def update_employee_status(employee, status):
    frappe.db.sql("""
                update `tabEmployee` set status = %(status)s where name = %(employee)s  
                """, {
        "status": status,
        "employee": employee
    })
    frappe.db.commit()

@frappe.whitelist()
def create_warning_if_needed(id, employee, date=None):
    if not employee:
        frappe.throw("Employee is required.")

    if not date:
        date = nowdate()

    date = getdate(date)

    # Create new Warning Notice
    warning = frappe.new_doc("Warning Notice")
    warning.employee = employee
    warning.reference_doctype = "Internal Disciplinary Investigation"
    warning.reference_link = id
    warning.date = date

    warning_type = None
    last_warning = None

    # Try to get last submitted warning
    if frappe.db.exists("Warning Notice", {"employee": employee, "docstatus": 1}):
        last_warning = frappe.get_last_doc("Warning Notice", filters={"employee": employee, "docstatus": 1})

    if not last_warning:
        # No previous warning → First warning
        warning.first_warning = 1
        warning_type = "First Warning"

    else:
        last = last_warning
        last_date = getdate(last.date)
        six_months_ago = add_months(last_date, 6)

        if last.first_warning:
            if date >= six_months_ago:
                # Already has recent first warning → same
                warning.first_warning = 1
                warning_type = "First Warning"
            else:
                # First warning is older than 6 months → second warning
                warning.second_warning = 1
                warning_type = "Second Warning"

        elif last.second_warning:
            # Previous was second warning → final
            warning.final_warning = 1
            warning_type = "Final Warning"

        elif last.final_warning:
            # Already has final warning → still issue another final
            warning.final_warning = 1
            warning_type = "Final Warning"

    if not warning_type:
        frappe.throw("Unable to determine warning type.")

    warning.insert(ignore_permissions=True)

    if warning.name:
        document_link = f"<a href='/app/warning-notice/{warning.name}' target='_blank'>{warning.name}</a>"
        frappe.msgprint(
            _(f"{warning_type} {document_link} Created Successfully"),
            title="Warning Notice Created",
            indicator="green"
        )
        send_email(employee,document_link,id)
        
        
def create_employee_termination(self):
    employee_termination = frappe.new_doc("Termination of Contract")
    employee_termination.employee = self.employee
    employee_termination.reason = self.reason
    employee_termination.type = "Not Extend"
    employee_termination.date_of_termination = self.date_of_termination
    employee_termination.reference_doctype = "Internal Disciplinary Investigation"
    employee_termination.reference_link = self.name
    
    employee_termination.insert()
    
    if employee_termination.name:
        document_link = f"<a href='/app/termination-of-contract/{employee_termination.name}' target='_blank'>{employee_termination.name}</a>"
        frappe.msgprint(
            _(f"Termination of Contract  Created Successfully {document_link}"),
            title="Termination of Contract Created",
            indicator="green"
        )
        
        send_email(self.employee,document_link,self.name)
        
def get_users_with_any_role(role_list):
    users = frappe.get_all(
        "Has Role",
        filters={"role": ["in", role_list],"parenttype":"User","parentfield":"roles"},
        fields=["parent as user"]
    )
    return list({u.user for u in users})

def send_email(employee,document_link,document_name):
    # get employee user 
    roles = ["HR Manager","HR User"]
    users = get_users_with_any_role(roles)
    # Generate the main print format PDF
    pdf_content = frappe.get_print("Internal Disciplinary Investigation", document_name, print_format="Internal Disciplinary Investigation", as_pdf=True)
    filename = f"{document_name}.pdf"

    # Attachments list
    attachments = [{
        "fname": filename,
        "fcontent": pdf_content
    }]

    # Send email
    frappe.sendmail(
        recipients=users,
        subject=f"Internal Disciplinary Investigation",
        message=f"""
            <p>Internal Disciplinary Investigation</p>
            <p>click here to see document {document_link}</p>
        """,
        attachments=attachments
    )