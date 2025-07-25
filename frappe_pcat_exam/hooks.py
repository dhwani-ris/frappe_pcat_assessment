app_name = "frappe_pcat_exam"
app_title = "Frappe Pcat Exam"
app_publisher = "Dhwani RIS"
app_description = "Frappe App to create RIASEC Based Quiz On the top of LMS"
app_email = "bhushan.barbuddhe@dhwaniris.com"
app_license = "mit"

# Apps
# ------------------

required_apps = ["lms"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "frappe_pcat_exam",
# 		"logo": "/assets/frappe_pcat_exam/logo.png",
# 		"title": "Frappe Pcat Exam",
# 		"route": "/frappe_pcat_exam",
# 		"has_permission": "frappe_pcat_exam.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/frappe_pcat_exam/css/frappe_pcat_exam.css"
# app_include_js = "/assets/frappe_pcat_exam/js/frappe_pcat_exam.js"

# include js, css files in header of web template
# web_include_css = "/assets/frappe_pcat_exam/css/frappe_pcat_exam.css"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "frappe_pcat_exam/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "LMS Question": "public/js/pcat_question.js",
    "LMS Quiz": "public/js/pcat_quiz.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "frappe_pcat_exam/public/icons.svg"

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

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "frappe_pcat_exam.utils.jinja_methods",
# 	"filters": "frappe_pcat_exam.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "frappe_pcat_exam.install.before_install"
after_install = "frappe_pcat_exam.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "frappe_pcat_exam.uninstall.before_uninstall"
# after_uninstall = "frappe_pcat_exam.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "frappe_pcat_exam.utils.before_app_install"
# after_app_install = "frappe_pcat_exam.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "frappe_pcat_exam.utils.before_app_uninstall"
# after_app_uninstall = "frappe_pcat_exam.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "frappe_pcat_exam.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
    "PCAT Submission": "frappe_pcat_exam.frappe_pcat_exam.doctype.pcat_submission.pcat_submission.get_permission_query_conditions",
}

has_permission = {
    "PCAT Submission": "frappe_pcat_exam.frappe_pcat_exam.doctype.pcat_submission.pcat_submission.has_permission",
}

# Document Events
# ---------------
# Hook on document methods and events



# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"frappe_pcat_exam.tasks.all"
# 	],
# 	"daily": [
# 		"frappe_pcat_exam.tasks.daily"
# 	],
# 	"hourly": [
# 		"frappe_pcat_exam.tasks.hourly"
# 	],
# 	"weekly": [
# 		"frappe_pcat_exam.tasks.weekly"
# 	],
# 	"monthly": [
# 		"frappe_pcat_exam.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "frappe_pcat_exam.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	"lms.lms.doctype.lms_quiz.lms_quiz.quiz_summary": "frappe_pcat_exam.api.quiz_summary"
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "frappe_pcat_exam.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["frappe_pcat_exam.utils.before_request"]
# after_request = ["frappe_pcat_exam.utils.after_request"]

# Job Events
# ----------
# before_job = ["frappe_pcat_exam.utils.before_job"]
# after_job = ["frappe_pcat_exam.utils.after_job"]

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
# 	"frappe_pcat_exam.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

fixtures = [
    {
        "doctype": "Property Setter",
        "filters": {
            "name": ["in", ["LMS Quiz-passing_percentage-mandatory"]] 
        },
    },
]