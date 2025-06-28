frappe.ui.form.on("Interview",{
    refresh:function(frm){
        setTimeout(()=>{
            frm.trigger("add_custom_buttons");
        })
    },
	custom_offer_term_template:function(frm){
		fetch_terms_data(frm)
	},
    add_custom_buttons: async function (frm) {
		if (frm.doc.docstatus === 2 || frm.doc.__islocal) return;

		const has_submitted_feedback = await frappe.db.get_value(
			"Interview Feedback",
			{
				interviewer: frappe.session.user,
				interview: frm.doc.name,
				docstatus: ("!=", 2),
			},
			"name",
		)?.message?.name;

		if (has_submitted_feedback) return;

		const allow_feedback_submission = frm.doc.interview_details.some(
			(interviewer) => interviewer.interviewer === frappe.session.user,
		);

		if (allow_feedback_submission) {
			frm.page.set_primary_action(__("Submit Feedback"), () => {
                submit_feedback(frm)
				// frm.trigger("submit_feedback");
			});
		} else {
			const button = frm.add_custom_button(__("Submit Feedback"), () => {
                submit_feedback(frm)
				// frm.trigger("submit_feedback");
			});
			button
				.prop("disabled", true)
				.attr("title", __("Only interviewers can submit feedback"))
				.tooltip({ delay: { show: 600, hide: 100 }, trigger: "hover" });
		}
	},

	
    show_feedback_dialog: function (frm, data) {
		let fields = frm.events.get_fields_for_feedback();

		let d = new frappe.ui.Dialog({
			title: __("Submit Feedback"),
			fields: [
				{
					fieldname: "skill_set",
					fieldtype: "Table",
					label: __("Skill Assessment"),
					cannot_add_rows: false,
					in_editable_grid: true,
					reqd: 1,
					fields: fields,
					data: data,
				},
				{
					fieldname: "result",
					fieldtype: "Select",
					options: ["", "Cleared", "Rejected"],
					label: __("Result"),
					reqd: 1,
				},
				{
					fieldname: "feedback",
					fieldtype: "Small Text",
					label: __("Feedback"),
				},
                {
					fieldname: "salary",
					fieldtype: "Float",
					label: __("Salary"),
				},
			],
			size: "large",
			minimizable: true,
			static: true,
			primary_action: function (values) {
				frappe
					.call({
						method: "tst_hr.triggers.hr.interview.interview.create_interview_feedback",
						args: {
							data: values,
							interview_name: frm.doc.name,
							interviewer: frappe.session.user,
							job_applicant: frm.doc.job_applicant,
                            salary:values.salary,
						},
					})
					.then(() => {
						frm.refresh();
					});
				d.hide();
			},
		});
		d.show();
		d.get_close_btn().show();
	},
    get_fields_for_feedback: function () {
		return [
			{
				fieldtype: "Link",
				fieldname: "skill",
				options: "Skill",
				in_list_view: 1,
				label: __("Skill"),
			},
			{
				fieldtype: "Rating",
				fieldname: "rating",
				label: __("Rating"),
				in_list_view: 1,
				reqd: 1,
			},
		];
	},
})

function submit_feedback(frm){
		frappe.call({
			method: "hrms.hr.doctype.interview.interview.get_expected_skill_set",
			args: {
				interview_round: frm.doc.interview_round,
			},
			callback: function (r) {
				frm.events.show_feedback_dialog(frm, r.message);
				// frm.refresh();
			},
		});
	}



function fetch_terms_data(frm){
	if (frm.doc.custom_offer_term_template){
		frm.clear_table("custom_offer_terms")
		frappe.call({
			method:"frappe.client.get_list",
			args:{
				doctype:"Job Offer Term",
				filters:{
					"parent":frm.doc.custom_offer_term_template,
					"parentfield":"offer_terms",
					"parenttype":"Job Offer Term Template"
				},
				fields:["offer_term","value"],
				parent:"Job Offer Term Template"
			},
			callback:function(response){
				if (response.message){
					let terms_data = response.message
					console.log(terms_data)
					terms_data.forEach(function(row){
						new_row = frm.add_child("custom_offer_terms")
						new_row.offer_term = row.offer_term
						new_row.value__description = row.value
					})

				}
				frm.refresh_field("custom_offer_terms")
			}
		})
	}
}