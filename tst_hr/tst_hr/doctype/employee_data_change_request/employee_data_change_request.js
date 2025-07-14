// Copyright (c) 2025, TST Developer and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Employee Data Change Request", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Employee Data Change Request', {
    update_personal_data(frm) {
        if (frm.doc.update_personal_data && frm.doc.update_bank_data) {
            // frappe.msgprint(__('You cannot select both Personal Data and Bank Data update at the same time.'));
            frm.set_value('update_bank_data', 0);
        }
    },
    update_bank_data(frm) {
        if (frm.doc.update_bank_data && frm.doc.update_personal_data) {
            // frappe.msgprint(__('You cannot select both Bank Data and Personal Data update at the same time.'));
            frm.set_value('update_personal_data', 0);
        }
    }
});
