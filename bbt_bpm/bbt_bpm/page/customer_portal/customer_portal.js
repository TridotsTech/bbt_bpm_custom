// frappe.pages['customer_portal'].on_page_load = function(wrapper) {
// 	var page = frappe.ui.make_app_page({
// 		parent: wrapper,
// 		title: 'Customer Portal',
// 		single_column: true
// 	});
// }


frappe.pages['customer_portal'].on_page_load = function(wrapper) {
	frappe.customer_portal = new frappe.customer_portal(wrapper);
}

frappe.customer_portal = Class.extend({
	init : function(wrapper){
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Customer Portal',
			single_column: true
		});
    	this.wrapper = wrapper
    	this.make()
		this.get_imp_data()
		this.add_filters()
	},

	make: function() {
		var me = this;
		$(`<div class="frappe-list list-container"></div>`).appendTo(me.page.main);
	},

	get_imp_data:function(){
	    var me = this
	    $('.frappe-list').html("")
	    var filters = {"purchase_order":me.purchase_order}
	    frappe.call({
	        "method": "bbt_bpm.bbt_bpm.page.customer_portal.customer_portal.get_items_data",
	        args: {
	        	filters:filters
	        },
	        callback: function (r) {
	        	if (r.message){
	          		var html = r.message.html
					$('.frappe-list').html(html)
	        	}

	        }//calback end
	    })
	},

	add_filters:function(){
		var me = this
		me.page.add_field({
			fieldtype: 'Link',
			label: __('Language'),
			fieldname: 'language',
			options: "Language",
			reqd: 1,
			onchange: function() {
				me.language = this.value?this.value:null
				me.get_imp_data()
			}

		})
		me.page.add_field({
			fieldtype: 'Button',
			label: __('New Order'),
			fieldname: 'new_order',
			onchange: function() {
				me.printer_name = this.value?this.value:null
				me.get_imp_data()
			}
		})

		// const today = frappe.datetime.get_today();
		// me.page.add_field({
		// 	fieldtype: 'Date',
		// 	label: __('Start Date'),
		// 	fieldname: 'start_date',
		// 	default:"",
		// 	// reqd:1,
		// 	onchange: function() {
		// 		me.start_date = this.value?this.value:null
		// 		me.get_imp_data()
		// 	}
		// })
		// // const today = frappe.datetime.get_today();
		// me.page.add_field({
		// 	fieldtype: 'Date',
		// 	label: __('To Date'),
		// 	fieldname: 'to_date',
		// 	default:"",
		// 	// reqd:1,
		// 	onchange: function() {
		// 		me.to_date = this.value?this.value:null
		// 		me.get_imp_data()
		// 	}
		// })
  	}
})