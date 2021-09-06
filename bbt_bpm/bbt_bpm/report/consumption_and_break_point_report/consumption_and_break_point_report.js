// Copyright (c) 2016, Ashish and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Consumption and Break Point Report"] = {
	"filters": [
		{
			"fieldname":"item",
			"label": __("Item"),
			"fieldtype": "Link",
			"options":'Item'
		},
		{
			"fieldname":"company",
			"label": __("Branch"),
			"fieldtype": "Link",
			"options":'Company'
		}

		
	]
};
