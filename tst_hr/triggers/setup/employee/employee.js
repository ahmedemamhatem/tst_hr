frappe.ui.form.on('Employee', {
    custom_iqama_number: function(frm) {
        validate_custom_iqama_number(frm)
    },
    validate:function(frm){
        validate_custom_iqama_number(frm)

    },
    refresh:function(frm){
        open_employment_certificate(frm)
        apply_filter_section(frm)
        hide_salary_logs_add_row(frm)
        create_contract(frm)
    },
    onload:function(frm){
        hide_salary_logs_add_row(frm)
        
    },
    before_save: function (frm) {
        return handle_salary_change(frm);
    }
});

function validate_custom_iqama_number(frm){
    if (!/^\d{10}$/.test(frm.doc.custom_iqama_number)) {
        frappe.throw(__("Iqama Number must be exactly 10 digits."));
    }
}

function apply_filter_section(frm){
    frm.fields_dict["custom_section"].get_query = function(doc){
        return {
            filters:[
                ["Sections","department","=",frm.doc.department]
            ]
        }
    }
}


function hide_salary_logs_add_row(frm) {

    frm.get_field('custom_salary_logs').grid.cannot_add_rows = true;
    frm.fields_dict['custom_salary_logs'].grid.wrapper.find('.grid-remove-rows').hide();
    
}

function handle_salary_change(frm) {
    // Prevent repeated prompts
    if (frm.__salary_prompted__) return;

    return new Promise((resolve, reject) => {
        frappe.db.get_value("Employee", frm.doc.name, "ctc")
            .then(r => {
                let previous_salary = r?.message?.ctc;
                let current_salary = frm.doc.ctc;

                if (!previous_salary || !current_salary) return resolve();

                if (parseFloat(previous_salary) !== parseFloat(current_salary)) {
                    // Prompt user for reason and stop original save
                    frappe.prompt([
                        {
                            fieldname: 'reason',
                            label: 'Reason for Salary Change',
                            fieldtype: 'Small Text',
                            reqd: true
                        }
                    ], function (values) {
                        // Add new log entry
                        frm.add_child("custom_salary_logs", {
                            previous_salary: previous_salary,
                            current_salary: current_salary,
                            change_reason: values.reason,
                            date: frappe.datetime.get_today()
                        });

                        frm.refresh_field("custom_salary_logs");

                        // Flag to avoid infinite loop
                        frm.__salary_prompted__ = true;

                        // Manually trigger save
                        frm.save();
                    }, 'Salary Changed', 'Submit');

                    return reject(); // Stop original save
                }

                // No salary change, continue saving
                return resolve();
            })
            .catch(() => resolve()); // fallback to continue on error
    });
}


function open_employment_certificate(frm) {
    if (!frm.is_new()) {
        frm.add_custom_button(__('Employment Certificate'), function() {
            var url = `/printview?doctype=Employee&name=${frm.doc.name}&format=Employment Certificate`;
            window.open(url, '_blank');
        }).addClass('btn-primary');
    }
}


function create_contract(frm){
    if (!frm.is_new()) {
        frm.add_custom_button(__('Contract'), function() {
            // Create a new Contract doc in memory
            let doc = frappe.model.get_new_doc("Employee Contract");

            // Prefill fields from Employee
            doc.employee_id = frm.doc.name;
            doc.full_name = frm.doc.employee_name;
            doc.nationality = frm.doc.custom_nationality;
            doc.reports_to = frm.doc.reports_to;
            doc.joining_date = frm.doc.date_of_joining;

            // Redirect to new Contract form (unsaved)
            frappe.set_route("Form", "Employee Contract", doc.name);
        }, __('Create'));
    }
    
}
