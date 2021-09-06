frappe.pages['lead_time_tracker'].on_page_load = function(wrapper) {
	frappe.lead_time_tracker = new frappe.lead_time_tracker(wrapper);
}

frappe.lead_time_tracker = Class.extend({
	init : function(wrapper){
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: 'Lead Time Tracker',
			single_column: true
		});
    	this.wrapper = wrapper
    	this.make()
		this.get_imp_data()
		this.add_filters()
		this.add_menus(wrapper)
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
	        "method": "bbt_bpm.bbt_bpm.page.lead_time_tracker.lead_time_tracker.get_po_details",
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
			label: __('Purchase Order'),
			fieldname: 'purchase_order',
			options: "Purchase Order",
			reqd: 1,
			onchange: function() {
				me.purchase_order = this.value?this.value:null
				me.get_imp_data()
			}

		})
		// me.page.add_field({
		// 	fieldtype: 'Link',
		// 	label: __('Printer Name'),
		// 	fieldname: 'printer_name',
		// 	options: "Supplier",
		// 	onchange: function() {
		// 		me.printer_name = this.value?this.value:null
		// 		me.get_imp_data()
		// 	}

		// })

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
  	},

  	add_menus:function(wrapper){
		var me = this
		wrapper.page.add_menu_item("Print",function(){
			me.print_pdf()
		})
	},

	print_pdf: function() {
		var me = this;
		var filters = {"purchase_order":me.purchase_order}
	    if (me.purchase_order){
	    	frappe.call({
	        	"method": "bbt_bpm.bbt_bpm.page.lead_time_tracker.lead_time_tracker.get_po_details",
		        args: {
		        	filters:filters
		        },
		        callback: function (r) {
		        	if (r.message){
		          		var html = r.message.html
						var formData = new FormData();
						formData.append("html", html);
						var blob = new Blob([], { type: "text/xml"});
						//formData.append("webmasterfile", blob);
						formData.append("blob", blob);

						var xhr = new XMLHttpRequest();
						/*xhr.open("POST", '/api/method/frappe.utils.print_format.report_to_pdf');*/
						xhr.open("POST", '/api/method/bbt_bpm.bbt_bpm.page.lead_time_tracker.lead_time_tracker.custome_report_to_pdf');

						xhr.setRequestHeader("X-Frappe-CSRF-Token", frappe.csrf_token);
						xhr.responseType = "arraybuffer";
						xhr.onload = function(success) {
							if (this.status === 200) {
								var blob = new Blob([success.currentTarget.response], {type: "application/pdf"});
								var objectUrl = URL.createObjectURL(blob);

								//Open report in a new window
								window.open(objectUrl);
							}
						};
						xhr.send(formData);
		        	}

		        }//calback end
		    })
	    }
	},
})