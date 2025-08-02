// Copyright (c) 2025, TST Developer and contributors
// For license information, please see license.txt

frappe.ui.form.on("Final Settlement", {
	employee(frm) {
        get_employee_remaining_balance(frm)

	},
});


function get_employee_remaining_balance(frm){
    if (frm.doc.employee && frm.doc.posting_date){
        frappe.call({
            method:"hrms.hr.doctype.leave_application.leave_application.get_leave_details",
            args:{
                employee:frm.doc.employee,
                date:frm.doc.posting_date
            },
            callback:function(response){
                available_leave = response.message;
                remainig_annual_leave = available_leave["leave_allocation"]["Annual"]["remaining_leaves"]
                frm.set_value("remaining_leave_days",remainig_annual_leave)
                // calculate salary per day
                salary_per_day = frm.doc.current_salary / 30

                frm.set_value("leave_amount",salary_per_day * remainig_annual_leave)
                
            }
        })
    }
}