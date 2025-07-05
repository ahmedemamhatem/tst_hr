// Copyright (c) 2025, TST Developer and contributors
// For license information, please see license.txt

frappe.ui.form.on("Warning Notice", {
	first_warning(frm) {
        if (frm.doc.first_warning){
            frm.set_value("second_warning",0)
            frm.set_value("final_warning",0)
        }
	},
    second_warning(frm) {
        if (frm.doc.second_warning){
            frm.set_value("first_warning",0)
            frm.set_value("final_warning",0)
        }
	},
    final_warning(frm) {
        if (frm.doc.final_warning){
            frm.set_value("second_warning",0)
            frm.set_value("first_warning",0)
        }
	},
});
