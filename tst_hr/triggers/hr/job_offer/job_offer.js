frappe.ui.form.on("Job Offer", {
    onload: function (frm) {
        if (frm.doc.__islocal){
            // When the Job Offer form is loaded, fetch related offer terms
            get_offer_terms(frm);
        }
    }
});

function get_offer_terms(frm) {
    // Step 1: Get the Interview record linked to this job applicant
    frappe.db.get_value("Interview", { job_applicant: frm.doc.job_applicant, status:"Cleared" }, "name")
        .then(r => {
            const interview_name = r.message?.name;
            if (!interview_name) return; // If no Interview is found, stop here

            // Step 2: Fetch approved offer terms (custom_approve = 1) from that Interview
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Offer Terms",
                    filters: {
                        approve: 1,     // Only fetch approved terms
                        parent: interview_name // Link to the found Interview
                    },
                    fields: ["offer_term", "value__description"], // Only fetch necessary fields
                    parent: "Interview"
                },
                callback: function (response) {
                    if (response.message) {
                        let offers_data = response.message;

                        // Step 3: Add each offer term to the Job Offer's offer_terms table
                        offers_data.forEach(element => {
                            let new_row = frm.add_child("offer_terms");
                            new_row.offer_term = element.offer_term;
                            new_row.value = element.value__description;
                        });

                        // Step 4: Refresh the child table UI to show the added rows
                        frm.refresh_field("offer_terms");
                    }
                }
            });
        });
}
