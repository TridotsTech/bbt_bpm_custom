frappe.listview_settings['Sales Invoice'] = {
	onload: function(listview) {
		if ((frappe.session.user !="administrator") && frappe.user.has_role(["Customer"])){
			$(".list-sidebar").hide()
		}
	},
	refresh: function(listview) {
		if ((frappe.session.user !="administrator") && frappe.user.has_role(["Customer"])){
			$(".list-sidebar").hide()
		}
	}
};