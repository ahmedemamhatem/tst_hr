app_name = "tst_hr"
app_title = "Tst Hr"
app_publisher = "TST Developer"
app_description = "tst_hr"
app_email = "ahmedemamhatem@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "tst_hr",
# 		"logo": "/assets/tst_hr/logo.png",
# 		"title": "Tst Hr",
# 		"route": "/tst_hr",
# 		"has_permission": "tst_hr.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/tst_hr/css/tst_hr.css"
# app_include_js = "/assets/tst_hr/js/tst_hr.js"

# include js, css files in header of web template
# web_include_css = "/assets/tst_hr/css/tst_hr.css"
# web_include_js = "/assets/tst_hr/js/tst_hr.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "tst_hr/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Interview" : "triggers/hr/interview/interview.js",
    "Job Offer":"triggers/hr/job_offer/job_offer.js",
    "Employee":"triggers/setup/employee/employee.js"
    }
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "tst_hr/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "tst_hr.utils.jinja_methods",
# 	"filters": "tst_hr.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "tst_hr.install.before_install"
# after_install = "tst_hr.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "tst_hr.uninstall.before_uninstall"
# after_uninstall = "tst_hr.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "tst_hr.utils.before_app_install"
# after_app_install = "tst_hr.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "tst_hr.utils.before_app_uninstall"
# after_app_uninstall = "tst_hr.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "tst_hr.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"Payroll Entry": "tst_hr.overrides.payroll.payroll_entry.payroll_entry.CustomPayrollEntry"
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Employee":{
        "validate":"tst_hr.triggers.setup.employee.employee.validate"
    },
    "Salary Structure Assignment":{
		"before_insert":"tst_hr.triggers.hr.salary_structure_assignment.salary_structure_assignment.before_insert",
		"on_submit":"tst_hr.triggers.hr.salary_structure_assignment.salary_structure_assignment.on_submit"
	}
	# "*": {
	# 	"on_update": "method",
	# 	"on_cancel": "method",
	# 	"on_trash": "method"
	# }
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	# "all": [
	# 	"tst_hr.tasks.all"
	# ],
	"daily": [
		"tst_hr.tasks.daily"
	],
	# "hourly": [
	# 	"tst_hr.tasks.hourly"
	# ],
	# "weekly": [
	# 	"tst_hr.tasks.weekly"
	# ],
	# "monthly": [
	# 	"tst_hr.tasks.monthly"
	# ],
}

fixtures = [
    # {"dt": "Custom Field", "filters": [["module", "=", "Tst Hr"]]},
    # {"dt": "Property Setter", "filters": [["module", "=", "Tst Hr"]]},
    {"dt": "Print Format", "filters": [["module", "=", "Tst Hr"]]},
]

# Testing
# -------

# before_tests = "tst_hr.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "tst_hr.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "tst_hr.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["tst_hr.utils.before_request"]
# after_request = ["tst_hr.utils.after_request"]

# Job Events
# ----------
# before_job = ["tst_hr.utils.before_job"]
# after_job = ["tst_hr.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"tst_hr.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

