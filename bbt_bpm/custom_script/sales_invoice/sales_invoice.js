frappe.ui.form.on("Sales Invoice", {
	onload: function(frm){
		frm.trigger("hide_sidebar")
	},
	refresh: function(frm){
		frm.trigger("hide_sidebar")
	},

	hide_sidebar: function(frm){
		if ((frappe.session.user !="administrator") && frappe.user.has_role(["Customer"])){
			$(".form-sidebar").css("display", "none");
		}
	}	
})
	