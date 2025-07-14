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
    date: function(frm) {
        calculate_to_date(frm);
    },
    days: function(frm) {
        calculate_to_date(frm);
    }
});


// Function to calculate 'to_date' based on 'from_date' and 'no_of_days'
function calculate_to_date(frm) {
    const from_date = frm.doc.date;
    const no_of_days = frm.doc.days;

    // Proceed only if both values are present and valid
    if (from_date && no_of_days) {
        // Create a JS Date object from 'from_date'
        let date_obj = frappe.datetime.str_to_obj(from_date);

        // Add no_of_days - 1 to include the from_date in the duration
        date_obj.setDate(date_obj.getDate() + no_of_days - 1);

        // Convert date back to Frappe date string format (yyyy-mm-dd)
        let to_date = frappe.datetime.obj_to_str(date_obj);

        // Set the calculated date in 'to_date' field
        frm.set_value('to_date', to_date);
    } else {
        // If inputs are missing, clear 'to_date'
        frm.set_value('to_date', '');
    }
}
