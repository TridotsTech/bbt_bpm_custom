frappe.listview_settings['Customer'] = {
	onload: function(listview) {
		if ((frappe.session.user !="Administrator") && frappe.user.has_role(["Customer"])){
			$(".list-sidebar").hide()
		}
	},
	refresh: function(listview) {
		if ((frappe.session.user !="Administrator") && frappe.user.has_role(["Customer"])){
			$(".list-sidebar").hide()
		}
	}
};