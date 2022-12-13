frappe.provide('frappe.dashboards.chart_sources');

frappe.dashboards.chart_sources["Pending for acceptance"] = {
	method: "bbt_bpm.bbt_bpm.dashboard_chart_source.pending_for_acceptance.pending_for_acceptance.get_data",
	filters: [
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: ["Draft","On Hold","To Deliver and Bill",
			"To Bill","To Deliver","Completed"]
			// default: frappe.defaults.get_user_default("Company"),
			// reqd: 1
		},
		// {
		// 	fieldname: "account",
		// 	label: __("Account"),
		// 	fieldtype: "Link",
		// 	options: "Account",
		// 	reqd: 1
		// },
	]
};