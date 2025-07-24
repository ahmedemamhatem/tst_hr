// Copyright (c) 2025, TST Developer and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Employee Data Change Request", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Employee Data Change Request', {
    update_personal_data(frm) {
        if (frm.doc.update_personal_data) {
            frm.set_value('update_bank_data', 0);
            frm.set_value('update_insurance_data', 0);
        }
    },
    update_bank_data(frm) {
        if (frm.doc.update_bank_data) {
            frm.set_value('update_personal_data', 0);
            frm.set_value('update_insurance_data', 0);
        }
    },
    update_insurance_data(frm) {
        if (frm.doc.update_insurance_data) {
            frm.set_value('update_personal_data', 0);
            frm.set_value('update_bank_data', 0);
        }
    },
    
});
