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
	    			me.add_to_card(me)
	        	}

	        }//calback end
	    })

	},

	add_to_card: function(me){
	    $('.add_to_card').click(function() {
	    	var item = $(this).attr("item")
	    	var rate = $(this).attr("rate")
	    	var stock_in_qty = $(this).attr("stock_in_qty")
	    	var carton_qty = $(this).attr("carton_qty")
	    	var no_of_items_can_be_packed = $(this).attr("no_of_items_can_be_packed")
	    	var order_qty=jQuery($(this).closest('tr').children('td.col9')[0]).find("input[type='number']").val()
	    	var cartan_order_qty=jQuery($(this).closest('tr').children('td.col10')[0]).find("input[type='number']").val()
	    	var language= $(this).closest('tr').children('td.first_col').text();

	    	var filters = {"item":item, "rate":rate, "stock_in_qty":stock_in_qty, "carton_qty":carton_qty, "no_of_items_can_be_packed":no_of_items_can_be_packed, "order_qty":order_qty, "cartan_order_qty":cartan_order_qty, "language":language}

	    	frappe.call({
		        "method": "bbt_bpm.bbt_bpm.page.customer_portal.customer_portal.add_to_cart_item",
		        args: {
		        	filters:filters
		        },
		        callback: function (r) {
		        	if (r.message){
		          		
		        	}

		        }//calback end
		    })	
	    })
	},

	delete_add_to_cart_item: function(){
		$(".check").click(function(){

			if($('.check').is(":checked")){
				$( ".check_row").prop('checked', true);
				$(".delete").show()
			} else{
				$( ".check_row").prop('checked', false);
				$(".delete").hide()
			}
		})

		$(".check_row").click(function(){
			$('.delete').show()
		})


		$(".delete").click(function(){
			row_name = []
			$.each($("input[type='checkbox']:checked"), function(){
                row_name.push($(this).val());
            });
           	frappe.call({
		        "method": "bbt_bpm.bbt_bpm.page.customer_portal.customer_portal.delete_add_to_cart_item",
		        args: {
		        	user:frappe.session.user,
		        	name:row_name
		        },
		        callback: function (r) {
		        	if (r.message){
		        		window.location.reload()
		        	}

		        }//calback end
		    })
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
			click: function() {
				me.new_order = this.value?this.value:null
				frappe.call({
			        "method": "bbt_bpm.bbt_bpm.page.customer_portal.customer_portal.new_order",
			        args: {
			        	user:frappe.session.user
			        },
			        callback: function (r) {
			        	if (r.message){
			        		window.location.reload()
			        	}

			        }//calback end
			    })
			}
		})

		me.page.add_field({
			fieldtype: 'Button',
			label: __('Add To Cart Items'),
			fieldname: 'add_to_cart_items',
			click: function() {
				me.add_to_cart_items = this.value?this.value:null
				frappe.call({
			        "method": "bbt_bpm.bbt_bpm.page.customer_portal.customer_portal.add_to_cart_details",
			        args: {
			        	user:frappe.session.user
			        },
			        callback: function (r) {
			        	if (r.message){
			          		var html = r.message.html
							$('.frappe-list').html(html)
							$('.delete').hide()
							me.delete_add_to_cart_item()
			        	}

			        }//calback end
			    })
			}
		})
	}
})