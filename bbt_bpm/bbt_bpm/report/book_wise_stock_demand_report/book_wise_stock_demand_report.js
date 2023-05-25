// Copyright (c) 2016, Ashish and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Book wise stock demand report"] = {
	"filters": [
		{
			"label": "Item Code",
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options":"Item",
			"width": 150
		}
	]
};
