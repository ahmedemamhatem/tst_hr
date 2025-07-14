// Copyright (c) 2025, TST Developer and contributors
// For license information, please see license.txt

frappe.ui.form.on("Late or Absence Record", {
	absence(frm) {
        if (frm.doc.absence){
            frm.set_value("late",0)
            
        }
    },
    late(frm) {
        if (frm.doc.late){
            frm.set_value("absence",0)
        }
    },
});
