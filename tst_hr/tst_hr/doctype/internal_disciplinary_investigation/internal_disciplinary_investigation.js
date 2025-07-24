// Copyright (c) 2025, TST Developer and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Internal Disciplinary Investigation", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Internal Disciplinary Investigation", {
    terminate_employment: function (frm) {
        handle_rating_change(frm, "terminate_employment");
    },
    salary_deduction: function (frm) {
        handle_rating_change(frm, "salary_deduction");
    },
    issue_warning: function (frm) {
        handle_rating_change(frm, "issue_warning");
    },
    issue_verbal_warning: function (frm) {
        handle_rating_change(frm, "issue_verbal_warning");
    },
    archive_case: function (frm) {
        handle_rating_change(frm, "archive_case");
    },
    from_date: function(frm){
        calculate_to_date(frm,frm.doc.from_date,frm.doc.deduction_days,"to_date");
    },
    deduction_days: function(frm){
        calculate_to_date(frm,frm.doc.from_date,frm.doc.deduction_days,"to_date");
    }
});

function handle_rating_change(frm,selected_rating) {
    const ratings = ["terminate_employment", "salary_deduction", "issue_warning", "issue_verbal_warning", "archive_case"];

    if (frm.doc[selected_rating]) {
        ratings.forEach(rating => {
            if (rating !== selected_rating) {
                frm.set_value(rating, 0);
            }
        });
    }
}


// Function to calculate 'to_date' based on 'from_date' and 'no_of_days'
function calculate_to_date(frm,from_date,no_of_days,to_date_field) {

    // Proceed only if both values are present and valid
    if (from_date && no_of_days) {
        // Create a JS Date object from 'from_date'
        let date_obj = frappe.datetime.str_to_obj(from_date);

        // Add no_of_days - 1 to include the from_date in the duration
        date_obj.setDate(date_obj.getDate() + no_of_days - 1);

        // Convert date back to Frappe date string format (yyyy-mm-dd)
        let to_date = frappe.datetime.obj_to_str(date_obj);

        // Set the calculated date in 'to_date' field
        frm.set_value(to_date_field, to_date);
    } else {
        // If inputs are missing, clear 'to_date'
        frm.set_value(to_date_field, '');
    }
}