# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version
from frappe.utils import cstr, flt, getdate, cint, nowdate, add_days, get_link_to_form, strip_html
import frappe
from frappe import _

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
	"Delivery Note": "custom_script/delivery_note/delivery_note_list.js",
	"Sales Order": "custom_script/sales_order/sales_order_list.js",
	"Sales Invoice": "custom_script/sales_invoice/sales_invoice_list.js",
	"Customer": "custom_script/customer/customer_list.js"
}

doctype_js = {
	"Sales Order": "custom_script/sales_order/sales_order.js",
	"Stock Entry": "custom_script/stock_entry/stock_entry.js",
	"Quotation": "custom_script/quotation/quotation.js",
	"Item": "custom_script/item/item.js",
	"Pick List": "custom_script/pick_list/pick_list.js",
	"Customer": "custom_script/customer/customer.js",
	"Stock Reconciliation": "custom_script/stock_reconciliation/stock_reconciliation.js",
	"Batch": "custom_script/batch/batch.js",
	"Delivery Note": "custom_script/delivery_note/delivery_note.js"
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

permission_query_conditions = {
	"Customer": "bbt_bpm.custom_script.customer.customer.cust_get_permission_query_conditions",
	"Sales Order": "bbt_bpm.custom_script.sales_order.sales_order.so_get_permission_query_conditions",
	"Sales Invoice": "bbt_bpm.custom_script.sales_invoice.sales_invoice.si_get_permission_query_conditions",
	"Delivery Note": "bbt_bpm.custom_script.delivery_note.delivery_note.dn_get_permission_query_conditions",
	"Address": "bbt_bpm.custom_script.address.address.add_get_permission_query_conditions"
}
	

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
		"validate": "bbt_bpm.custom_script.sales_order.sales_order.validate",
		"on_update": "bbt_bpm.custom_script.sales_order.sales_order.on_update",
		"on_submit" : "bbt_bpm.custom_script.sales_order.sales_order.on_submit"
	},
	"Delivery Note": {
		"on_submit": "bbt_bpm.custom_script.delivery_note.delivery_note.on_submit",
		"on_update_after_submit": "bbt_bpm.custom_script.delivery_note.delivery_note.on_update_after_submit",
		"validate": "bbt_bpm.custom_script.delivery_note.delivery_note.save"
	},
	"Pick List": {
		"on_submit": "bbt_bpm.custom_script.pick_list.pick_list.on_submit",
		"validate": "bbt_bpm.custom_script.pick_list.pick_list.save",
		#"before_save": "bbt_bpm.custom_script.pick_list.pick_list.before_save"

	},
	"Sales Invoice": {
		"on_submit": "bbt_bpm.custom_script.sales_invoice.sales_invoice.on_submit",
		"on_update": "bbt_bpm.custom_script.sales_invoice.sales_invoice.save"

	},
	"Stock Reconciliation":{
		#"validate": "bbt_bpm.custom_script.stock_reconciliation.stock_reconciliation.get_warehouse_data"
	},
	"Batch":{
		# "before_save": "bbt_bpm.custom_script.batch.batch.before_save"
	},
	"User": {
		"validate": "bbt_bpm.custom_script.user.user.validate",
		"after_insert": "bbt_bpm.custom_script.user.user.after_insert"
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
#override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "bbt_bpm.event.get_events"
#	"erpnext.selling.doctype.sales_order.sales_order.validate_warehouse":"bbt_bpm.custom_script.sales_order.sales_order.validate_warehouse"
#}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "bbt_bpm.task.get_dashboard_data"
# }
from erpnext.selling.doctype.sales_order.sales_order import SalesOrder
@frappe.whitelist()
def validate_warehouse(self):
    #pass
		super(SalesOrder, self).validate_warehouse()

		for d in self.get("items"):
			if (frappe.get_cached_value("Item", d.item_code, "is_stock_item") == 0 or
				(self.has_product_bundle(d.item_code) and self.product_bundle_has_stock_item(d.item_code))) \
				and not d.warehouse and not cint(d.delivered_by_supplier):
				frappe.throw(_("stock item {0}").format(d.item_code),
					WarehouseRequired)
SalesOrder.validate_warehouse=validate_warehouse
