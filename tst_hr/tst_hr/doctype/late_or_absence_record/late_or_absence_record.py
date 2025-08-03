# Copyright (c) 2025, TST Developer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days, getdate


class LateorAbsenceRecord(Document):
    def share_with_investigators(self):
        if not self.is_new():
            # Get user linked to employee
            user = frappe.db.get_value("Employee", self.employee, "user_id")
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

    def after_insert(self):
        self.share_with_investigators()

    @frappe.whitelist()
    def validate(self):
        self.share_with_investigators()
        if self.docstatus == 1:
            self.take_action()
   
    def take_action(self):
        if self.action == "Deduct from leave days":
            self.create_leave_application()
        else:
            self.create_absent_attendance()
            
            
    def create_leave_application(self):

        # Create a new Leave Application document
        leave_app = frappe.new_doc("Leave Application")
        leave_app.employee = self.employee
        leave_app.custom_reference_doctype = self.doctype
        leave_app.custom_reference_link = self.name
        leave_app.leave_type = "Annual"
        leave_app.from_date = self.from_date
        leave_app.to_date = self.to_date_action
        leave_app.posting_date = frappe.utils.nowdate()
        leave_app.description = "Auto-created due to deduction"
        leave_app.company = self.company
        leave_app.status = "Approved"
        leave_app.save(ignore_permissions=True)
        leave_app.submit()

        # Optionally store the created leave application reference
        self.leave_application = leave_app.name
        
        
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


@frappe.whitelist()
def get_employee():
    """
    Fetches employees who report to the current session user.

    Steps:
    1. Get the Employee record linked to the current logged-in user.
    2. Fetch all employees whose 'reports_to' field is set to this employee.
    3. Return a list of employee names.
    """

    # Step 1: Get the employee name associated with the current session user
    employee = frappe.get_cached_value("Employee", {"user_id": frappe.session.user}, "name")

    # Step 2: Get all employees who report to this employee
    employees = frappe.get_all("Employee", {"reports_to": employee}, pluck="name")

    # Step 3: Return the list of employee names
    return employees
