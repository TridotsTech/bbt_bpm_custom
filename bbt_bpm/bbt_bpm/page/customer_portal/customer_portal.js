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
	    var filters = {"language":me.language}
	    frappe.call({
	        "method": "bbt_bpm.bbt_bpm.page.customer_portal.customer_portal.get_items_data",
	        args: {
	        	filters:filters
	        },
	        callback: function (r) {
	        	if (r.message){
	          		var html = r.message.html
					$('.frappe-list').html(html)
					$('[data-fieldname="language"]').show()
					$('[data-fieldname="home"]').hide()
					me.item_order_qty(me)
	    			me.add_to_card(me)
	    			me.new_order(me)
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

	    	if (stock_in_qty == "None"){
	    		frappe.throw(__("Books {0} Out Of Stock.",[item]));
	    		frappe.validated = false;
	    	}

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

	new_order: function(){
		$(".submit").click(function(){
			client_feedback = $(".comment").val()
			frappe.call({
		        "method": "bbt_bpm.bbt_bpm.page.customer_portal.customer_portal.new_order",
		        args: {
		        	client_feedback:client_feedback
		        },
		        callback: function (r) {
		        	if (r.message){
		        		window.location.reload()
		        	}

		        }//calback end
		    })	
		})
	},

	item_order_qty: function(me){
		$(".item_order_qty").click(function(){
			var no_of_items_can_be_packed = $(this).attr("no_of_items_can_be_packed")
	    	var order_qty=jQuery($(this).closest('tr').children('td.col9')[0]).find("input[type='number']").val()
			no_of_cartons = 0.0
	    	no_of_cartons = Math.round(parseFloat(order_qty)/parseFloat(no_of_items_can_be_packed))
	    	total_req_qty = no_of_cartons*parseFloat(no_of_items_can_be_packed)
	    	if (total_req_qty && total_req_qty!=0 && parseFloat(order_qty)!=parseFloat(total_req_qty)){
	    		frappe.msgprint(__("Add min {0} qty to fulfill Cartons Size", [total_req_qty]));
	    	}
		})
	},

	update_qty_on_cart: function(){
		$(".cart_order_qty").click(function(){
			var item = $(this).attr("item")
			var language = $(this).attr("language")
			var rate = $(this).attr("rate")
			var order_qty=jQuery($(this).closest('tr').children('td.col9')[0]).find("input[type='number']").val()
			var amount = parseFloat(order_qty)*parseFloat(rate)
			var a = jQuery($(this).closest('tr').children('td.col11')[0]).html(amount)
			frappe.call({
		        "method": "bbt_bpm.bbt_bpm.page.customer_portal.customer_portal.update_qty_on_cart",
		        args: {
		        	item:item,
		        	language:language,
		        	order_qty:order_qty,
		        	rate:rate
		        },
		        callback: function (r) {
		        	if (r.message){
		        		data = r.message
		        		$(".total_amount").html(data.amount)
		        		$(".total_ordered_qty").html(data.total_ordered_qty)
		        		$(".total_cartons_qty").html(data.total_cartons_qty)
		        	}

		        }//calback end
		    })
		})

		$(".cart_cartan_order_qty").click(function(){
			var amount = 0.0 
			var item = $(this).attr("item")
			var language = $(this).attr("language")
			var rate = $(this).attr("rate")
			var book_per_cartons = $(this).attr("book_per_cartons")
			var cartan_order_qty=jQuery($(this).closest('tr').children('td.col10')[0]).find("input[type='number']").val()
			var qty = parseFloat(book_per_cartons)*parseFloat(cartan_order_qty)
			var amount = parseFloat(qty)*parseFloat(rate)
			var a = jQuery($(this).closest('tr').children('td.col11')[0]).html(amount)
			frappe.call({
		        "method": "bbt_bpm.bbt_bpm.page.customer_portal.customer_portal.update_cartons_qty_on_cart",
		        args: {
		        	item:item,
		        	language:language,
		        	rate: rate,
		        	cartan_order_qty:cartan_order_qty,
		        	book_per_cartons:book_per_cartons
		        },
		        callback: function (r) {
		        	if (r.message){
		        		data = r.message[0]
		        		$(".total_amount").html(data.amount)
		        		$(".total_ordered_qty").html(data.total_ordered_qty)
		        		$(".total_cartons_qty").html(data.total_cartons_qty)
		        		// $("input").val(r.message[1]); 
		    //     		jQuery($(this).closest('tr').children('td.col9')[0]).find("input[type='number']").innerHTMLer=r.message[1]
						// console.log("=============",jQuery($(this).closest('tr').children('td.col9')[0]).find("input[type='number']").innerHTMLer=r.message[1])

		        	}

		        }//calback end
		    })
		})

	},

	add_filters:function(){
		var me = this
		me.page.add_field({
			fieldtype: 'Button',
			label: __('Home'),
			fieldname: 'home',
			click: function() {
				me.home = this.value?this.value:null
				me.get_imp_data()
			}
		})

		me.page.add_field({
			fieldtype: 'Select',
			label: __('Language'),
			fieldname: 'language',
			options: [ "", "Assamese", "Bengali", "Chhattisgarhi", "English", "French", "Gujarati", "Hindi", "Japanese", "Kannada", "Marathi", "Korean", "Nepali", "Odia", "Punjabi", "Sinhala", "Tamil", "Telugu", "Urdu"],
			reqd: 0,
			onchange: function() {
				me.language = this.value?this.value:null
				me.get_imp_data()
			}
		})

		// me.page.add_field({
		// 	fieldtype: 'Button',
		// 	label: __('New Order'),
		// 	fieldname: 'new_order',
		// 	click: function() {
		// 		me.new_order = this.value?this.value:null
		// 		client_feedback = $(".comment").val()
		// 		frappe.call({
		// 	        "method": "bbt_bpm.bbt_bpm.page.customer_portal.customer_portal.new_order",
		// 	        args: {
		// 	        	client_feedback:client_feedback
		// 	        },
		// 	        callback: function (r) {
		// 	        	if (r.message){
		// 	        		window.location.reload()
		// 	        	}

		// 	        }//calback end
		// 	    })
		// 	}
		// })

		me.page.add_field({
			fieldtype: 'Button',
			label: __('View Cart'),
			fieldname: 'add_to_cart_items',
			click: function() {
				me.add_to_cart_items = this.value?this.value:null
				$('[data-fieldname="home"]').show()
				$('[data-fieldname="language"]').hide()
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
							me.update_qty_on_cart()
							me.new_order()
			        	}

			        }//calback end
			    })
			}
		})
	}
})