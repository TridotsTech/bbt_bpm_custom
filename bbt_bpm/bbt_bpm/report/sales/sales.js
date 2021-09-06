// Copyright (c) 2016, Ashish and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales"] = {
	"filters": [
		{
			"fieldname":"voucher_number",
			"label": __("Voucher Number"),
			"fieldtype": "Link",
			"options":'Sales Invoice'
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date"
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date"
		}
	]
};
