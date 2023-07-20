frappe.listview_settings['Delivery Note'] = {
	add_fields: ["customer", "customer_name", "base_grand_total", "per_installed", "per_billed",
		"transporter_name", "grand_total", "is_return", "status", "currency", "delivered"],
	get_indicator: function(doc) {
		if(cint(doc.is_return)==1) {
			return [__("Return"), "darkgrey", "is_return,=,Yes"];
		} 
		else if (doc.status === "Closed") {
			return [__("Closed"), "green", "status,=,Closed"];
		}
		// else if (flt(doc.delivered, 2) == 100) {
		// 	return [__("Completed"), "green", "per_billed,=,100"];
		// } 
		else if (doc.status === "Completed" && doc.delivered == 1){
			return [__("Completed"), "darkgrey", "status,=,Completed|delivered,=,1"];
		}
		else if (doc.status === 'To Bill' && doc.delivered == 0){
			return [__("Goods-In-Transit"), "green", "status,=,To Bill|delivered,=,0"];
		} 
		else if (doc.status === 'Completed' && doc.delivered == 0){
			return [__("Submitted"), "black", "status,=,Completed|delivered,=,0"];
		}
		else if (doc.delivered == 1){
			return [__("Delivered"), "blue", "delivered,=,1|status,=,To Bill"];
		}

	},

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
}