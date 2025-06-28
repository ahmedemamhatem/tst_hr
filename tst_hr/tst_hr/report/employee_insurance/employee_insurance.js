// Copyright (c) 2025, TST Developer and contributors
// For license information, please see license.txt

frappe.query_reports["Employee Insurance"] = {
	filters: [
			{
				fieldname: "designation",
				label: "Designation",
				fieldtype: "Link",
				options: "Designation",
				reqd: 0
			},
			{
				fieldname: "department",
				label: "Department",
				fieldtype: "Link",
				options: "Department",
				reqd: 0
			}
		]
};
