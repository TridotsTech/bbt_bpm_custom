// Copyright (c) 2016, Ashish and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Customer wise Stock demand report"] = {
	"filters": [
		{
			"label": "Customer",
			"fieldname": "customer",
			"fieldtype": "Link",
			"options":"Customer",
			"width": 150
		}
	]
};
