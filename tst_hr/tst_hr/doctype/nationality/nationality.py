# Copyright (c) 2025, TST Developer and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Nationality(Document):
    def validate(self):
        self.rename_document()

    def rename_document(self):
        if not self.is_new():
            # Generate the new name
            new_name = f"{self.english_name} - {self.arabic_name}"

            # Rename the document
            if self.name != new_name:
                frappe.rename_doc("Nationality", self.name, new_name)
