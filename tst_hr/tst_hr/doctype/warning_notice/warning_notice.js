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
    employee(frm){
        get_previous_warning(frm)
        
    }
});

function get_previous_warning(frm) {
    // Clear old logs
    frm.clear_table("logs");
    frm.refresh_field("logs");

    if (!frm.doc.employee) return;

    frappe.call({
        method: "frappe.client.get_list",
        args: {
            doctype: "Warning Notice",
            filters: {
                employee: frm.doc.employee,
                docstatus:1,
                name: ["!=", frm.doc.name]  // Exclude current doc
            },
            fields: ["name", "date","first_warning", "second_warning", "final_warning"],
            order_by: "date desc"
        },
        callback: function (r) {
            if (r.message && r.message.length > 0) {
                r.message.forEach(row => {
                    let child = frm.add_child("logs");
                    child.warning = row.name;
                    child.date = row.date;

                    if (row.first_warning) child.type = "First Warning";
                    else if (row.second_warning) child.type = "Second Warning";
                    else if (row.final_warning) child.type = "Final Warning";
                });

                frm.refresh_field("logs");
            } 
        }
    });
}
