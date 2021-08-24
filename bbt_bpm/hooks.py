# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "bbt_bpm"
app_title = "Bbt Bpm"
app_publisher = "Ashish"
app_description = "bbt_bpm"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "ashishkumar.r@indictrans.in"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/bbt_bpm/css/bbt_bpm.css"
# app_include_js = "/assets/bbt_bpm/js/bbt_bpm.js"

# include js, css files in header of web template
# web_include_css = "/assets/bbt_bpm/css/bbt_bpm.css"
# web_include_js = "/assets/bbt_bpm/js/bbt_bpm.js"


fixtures = ["Custom Field"]

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}
doctype_list_js = {
	"Delivery Note": "custom_script/delivery_note/delivery_note_list.js"
}

doctype_js = {
	"Sales Order": "custom_script/sales_order/sales_order.js",
	"Stock Entry": "custom_script/stock_entry/stock_entry.js",
	"Quotation": "custom_script/quotation/quotation.js"
}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "bbt_bpm.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "bbt_bpm.install.before_install"
# after_install = "bbt_bpm.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "bbt_bpm.notifications.get_notification_config"

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

# Document Events
# ---------------
# Hook on document methods and events
doc_events = {
	"Stock Entry": {
		"on_submit": "bbt_bpm.custom_script.stock_entry.stock_entry.on_submit",
		"on_cancel": "bbt_bpm.custom_script.stock_entry.stock_entry.on_cancel"
	},
	"Sales Order": {
		"validate": "bbt_bpm.custom_script.sales_order.sales_order.validate"
	},
	"Delivery Note": {
		"on_submit": "bbt_bpm.custom_script.delivery_note.delivery_note.on_submit",
		"on_update_after_submit": "bbt_bpm.custom_script.delivery_note.delivery_note.on_update_after_submit"
	}
}

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"bbt_bpm.tasks.all"
# 	],
# 	"daily": [
# 		"bbt_bpm.tasks.daily"
# 	],
# 	"hourly": [
# 		"bbt_bpm.tasks.hourly"
# 	],
# 	"weekly": [
# 		"bbt_bpm.tasks.weekly"
# 	]
# 	"monthly": [
# 		"bbt_bpm.tasks.monthly"
# 	]
# }

# Testing
# -------

# before_tests = "bbt_bpm.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "bbt_bpm.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "bbt_bpm.task.get_dashboard_data"
# }

