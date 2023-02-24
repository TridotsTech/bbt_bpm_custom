frappe.ui.form.on("Sales Invoice", {
	onload: function(frm){
		frm.trigger("hide_sidebar")
	},
	refresh: function(frm){
		frm.trigger("hide_sidebar")
		if (frappe.session.user != "Administrator" && frappe.user_roles.includes("Customer User")){
			$(".form-footer").hide()
		}
	},

	hide_sidebar: function(frm){
		if ((frappe.session.user !="Administrator") && frappe.user.has_role(["Customer"])){
			$(".form-sidebar").css("display", "none");
		}
	},
	company:function(frm) {
		if (frm.doc.company == 'Bhaktivedanta Book Trust'){
			set_field_options("naming_series", 'BBT-SINV-.####');
		} else if (frm.doc.company == 'Sri Sri Sitaram Seva Trust'){
			set_field_options("naming_series", 'SRST-SINV-.####');
		}else {
			set_field_options("naming_series", ['SRST-SINV-.####','BBT-SINV-.####','OB-BBT/INV-.####','OB-SRST/INV-.####']);
		}
		
	}	
})
	