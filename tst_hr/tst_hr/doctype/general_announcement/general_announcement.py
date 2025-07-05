# Copyright (c) 2025, TST Developer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.file_manager import get_file

class GeneralAnnouncement(Document):
	@frappe.whitelist()
	def validate(self):
		self.validate_filters()
  
	@frappe.whitelist()
	def on_submit(self):
		recipients = self.get_recipients()
		send_announcement_email(self.name,self.doctype,"General Announcement",self.subject,recipients,self.attach_enof)
	
  
	def validate_filters(self):
		# If no specific employee is selected, ensure at least one filter is selected
		if not self.employee:
			if not (self.department or self.designation or self.branch or self.section):
				frappe.throw("يرجى اختيار موظف معين أو تحديد واحد على الأقل من: القسم، المسمى الوظيفي، الفرع، أو القسم الفرعي.")

	def get_recipients(self):
		recipients = []

		# If employee is selected, get the user_id for that employee
		if self.employee:
			recipients = frappe.get_cached_value("Employee", {"name": self.employee}, ["user_id"])
		else:
			conditions = ""  
			params = {}

			if self.department:
				conditions += " AND department = %(department)s"
				params["department"] = self.department

			if self.designation:
				conditions += " AND designation = %(designation)s"
				params["designation"] = self.designation

			if self.branch:
				conditions += " AND branch = %(branch)s"
				params["branch"] = self.branch

			if self.section:
				conditions += " AND custom_section = %(section)s"
				params["section"] = self.section

			users = frappe.db.sql(
				f"""
				SELECT user_id
				FROM `tabEmployee`
				WHERE status = 'Active' AND {conditions}
				""",
				params
			)

			recipients = [user[0] for user in users if user[0]]  # Skip None values

		return recipients


def send_announcement_email(docname, doctype, print_format, subject, recipients=None, attatchement = None):

    # Generate the main print format PDF
    pdf_content = frappe.get_print(doctype, docname, print_format=print_format, as_pdf=True)
    filename = f"{docname}.pdf"

    # Attachments list
    attachments = [{
        "fname": filename,
        "fcontent": pdf_content
    }]

    # Check if attach_enof has a file attached
    if attatchement:
        # Get the file object
        file_doc = frappe.get_doc("File", {"file_url": attatchement})
        file_content = get_file(attatchement)[1]
        
        # Append to attachments
        attachments.append({
            "fname": file_doc.file_name,
            "fcontent": file_content
        })

    # Send email
    frappe.sendmail(
        recipients=recipients,
        subject=f"تعميم: {subject}",
        message="""
            <p>يرجى العثور على التعميم الرسمي في الملفات المرفقة.</p>
            <p>مع التحية،</p>
        """,
        attachments=attachments
    )

