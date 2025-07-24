// Copyright (c) 2025, TST Developer and contributors
// For license information, please see license.txt

frappe.ui.form.on("Employee Evaluation", {
	evaluation_template(frm) {
        get_evaluation_clause(frm)
	},
    refresh(frm){
        hide_evaluation_add_row(frm)
        apply_employee_filter(frm)
    }
});

frappe.ui.form.on("Evaluations", {
    excellent: function (frm, cdt, cdn) {
        handle_rating_change(cdt, cdn, "excellent");
    },
    very_good: function (frm, cdt, cdn) {
        handle_rating_change(cdt, cdn, "very_good");
    },
    good: function (frm, cdt, cdn) {
        handle_rating_change(cdt, cdn, "good");
    },
    acceptable: function (frm, cdt, cdn) {
        handle_rating_change(cdt, cdn, "acceptable");
    },
    poor: function (frm, cdt, cdn) {
        handle_rating_change(cdt, cdn, "poor");
    }
});

function handle_rating_change(cdt, cdn, selected_rating) {
    const ratings = ["excellent", "very_good", "good", "acceptable", "poor"];
    let row = locals[cdt][cdn];

    if (row[selected_rating]) {
        ratings.forEach(rating => {
            if (rating !== selected_rating) {
                frappe.model.set_value(cdt, cdn, rating, 0);
            }
        });
    }
}



async function get_evaluation_clause(frm){
    if (frm.doc.evaluation_template){
        frm.clear_table("evaluation")
        await frappe.call({
            method:"frappe.client.get_list",
            args:{
                doctype:"Evaluations",
                filters:{"parent":frm.doc.evaluation_template},
                fields:["poor","acceptable","good","very_good","excellent","clause"],
                parent:"Evaluation Template"
            },
            callback:function(response){
                evaluation_data = response.message;
                if (evaluation_data){
                    evaluation_data.forEach(function(row){

                        new_row = frm.add_child("evaluation")
                        new_row.poor = row.poor
                        new_row.acceptable = row.acceptable
                        new_row.good = row.good
                        new_row.very_good = row.very_good
                        new_row.excellent = row.excellent
                        new_row.clause = row.clause
                    })

                    frm.refresh_field("evaluation")
                    
                }
            }
        })
    }
}


function hide_evaluation_add_row(frm) {

    frm.get_field('evaluation').grid.cannot_add_rows = true;
    frm.fields_dict['evaluation'].grid.wrapper.find('.grid-remove-rows').hide();
    
}

async function apply_employee_filter(frm){
    await frappe.call({
        method:"tst_hr.tst_hr.doctype.late_or_absence_record.late_or_absence_record.get_employee",
        callback:function(response){
            if (response.message){
                employees = response.message
                frm.fields_dict["employee"].get_query = function (doc){
                    return {
                        filters:[
                            ["Employee","name","in",employees]
                        ]
                    }
                }
            }
        }
    })
}