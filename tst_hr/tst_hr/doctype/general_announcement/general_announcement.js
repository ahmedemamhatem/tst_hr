// Copyright (c) 2025, TST Developer and contributors
// For license information, please see license.txt

frappe.ui.form.on("General Announcement", {
	refresh(frm) {
        apply_filter_section(frm)

	},
});


function apply_filter_section(frm){
    frm.fields_dict["section"].get_query = function(doc){
        return {
            filters:[
                ["Sections","department","=",frm.doc.department]
            ]
        }
    }
}