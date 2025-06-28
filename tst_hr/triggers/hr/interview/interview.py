import frappe
from frappe import _
from frappe.utils import get_link_to_form

@frappe.whitelist()
def create_interview_feedback(data, interview_name, interviewer, job_applicant,salary):
	import json

	if isinstance(data, str):
		data = frappe._dict(json.loads(data))

	if frappe.session.user != interviewer:
		frappe.throw(_("Only Interviewer Are allowed to submit Interview Feedback"))

	interview_feedback = frappe.new_doc("Interview Feedback")
	interview_feedback.interview = interview_name
	interview_feedback.interviewer = interviewer
	interview_feedback.job_applicant = job_applicant
	interview_feedback.custom_salary = salary

	for d in data.skill_set:
		d = frappe._dict(d)
		interview_feedback.append("skill_assessment", {"skill": d.skill, "rating": d.rating})

	interview_feedback.feedback = data.feedback
	interview_feedback.result = data.result

	interview_feedback.save()
	interview_feedback.submit()

	frappe.msgprint(
		_("Interview Feedback {0} submitted successfully").format(
			get_link_to_form("Interview Feedback", interview_feedback.name)
		)
	)