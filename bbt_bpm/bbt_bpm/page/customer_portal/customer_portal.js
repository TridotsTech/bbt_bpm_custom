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
    	$('.viewcustomcart').click(function() {
    		window.location.href = '/desk#customer_portal?viewcart=true'
    		window.location.reload()
    	})
    	this.make()
		this.get_imp_data()
		this.add_filters()

    	var view_cart = window.location.href.split('?').reverse()[0]
    	
	},

	make: function() {
		var me = this;
		$(`<div class="frappe-list list-container"></div>`).appendTo(me.page.main);
	},

	show_view_cart_template:function(me){
			var me = this;
			$('.frappe-list').html('')
			me.add_to_cart_items = this.value?this.value:null
			$('[data-fieldname="home"]').show()
			$('[data-fieldname="language"]').hide()
			$('[data-fieldname="category"]').hide()
			$('[data-fieldname="item_code"]').hide()
			$('[data-fieldname="description"]').hide()
			frappe.call({
		        "method": "bbt_bpm.bbt_bpm.page.customer_portal.customer_portal.add_to_cart_details",
		        args: {
		        	user:frappe.session.user,
		        	filters: {"language":me.language,"category":me.category,"item_code":me.item_code,"description":me.description}
		        },
		        callback: function (r) {
		        	if (r.message){
		          		var html = r.message.html
						$('.frappe-list').html(html)
						$('.delete').hide()
						me.delete_add_to_cart_item()
						me.update_qty_on_cart()
						me.new_order()
						me.sort_table()
						$('[data-fieldname="download_pdf"]').hide()
						$('[data-fieldname="language"]').hide()
						$('[data-fieldname="category"]').hide()
						$('[data-fieldname="item_code"]').hide()
						$('[data-fieldname="description"]').hide()

		        	}

		        }
		    })
	},

	show_book_list_template(){
		var me = this;
		var filters = {"language":me.language,"category":me.category,"item_code":me.item_code,"description":me.description}
	    frappe.call({
	        "method": "bbt_bpm.bbt_bpm.page.customer_portal.customer_portal.get_items_data",
	        args: {
	        	filters:filters
	        },
	        callback: function (r) {
	        	if (r.message){
	          		var html = r.message.html
	          		//console.log(html)
					$('.frappe-list').html(html)
					$('[data-fieldname="language"]').show()
					$('[data-fieldname="category"]').show()
					$('[data-fieldname="item_code"]').show()
					$('[data-fieldname="description"]').show()
					$('[data-fieldname="home"]').hide()
					me.item_order_qty(me)
	    			me.add_to_card(me)
	    			me.notify_me(me)
	    			me.new_order(me)
	    			me.sort_table(me)

	        	}

	        }//calback end
	    })

	},

	
	get_imp_data:function(){
	    var me = this
	    $('.frappe-list').html("")

	    var view_cart = window.location.href.split('?').reverse()[0]
	    
	    if (view_cart == "viewcart=true"){
	    	me.show_view_cart_template()
	    }else{
	    	me.show_book_list_template()
	    }

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

			if (!cartan_order_qty){
				cartan_order_qty = Math.ceil(parseFloat(order_qty)/parseFloat(no_of_items_can_be_packed))
			}
	    	var filters = {"item":item, "rate":rate, "stock_in_qty":stock_in_qty, "carton_qty":carton_qty, "no_of_items_can_be_packed":no_of_items_can_be_packed, "order_qty":order_qty, "cartan_order_qty":cartan_order_qty, "language":language}
	    	if (stock_in_qty<=0 || stock_in_qty=="None"){
	    		frappe.throw(__("Books {0} Out Of Stock.",[item]));
	    		frappe.validated = false;
	    	}

	    	stock_order_qty = 0.0
	    	stock_order_qty = parseFloat(no_of_items_can_be_packed)*parseFloat(cartan_order_qty)
	    	if (flt(order_qty)>flt(stock_in_qty)){
	    		frappe.throw(__("Please enter order qty less than stock qty."));
	    		frappe.validated = false;
	    	}

	    	if (flt(carton_qty)<flt(cartan_order_qty)) {
	    		frappe.throw(__("Please enter cartons qty less than stock in cartons."));
	    		frappe.validated = false;
	    	}
			var no_of_items_can_be_packed = $(this).attr("no_of_items_can_be_packed")
	    	var order_qty=jQuery($(this).closest('tr').children('td.col9')[0]).find("input[type='number']").val()
			no_of_cartons = 0.0
	    	no_of_cartons = Math.ceil(parseFloat(order_qty)/parseFloat(no_of_items_can_be_packed))
	    	total_req_qty = no_of_cartons*parseFloat(no_of_items_can_be_packed)
	    	if (total_req_qty && total_req_qty!=0 && parseFloat(order_qty)!=parseFloat(total_req_qty)){
				var msg = "Add min "+total_req_qty+" qty to fulfill Carton's Size OR to continue please click Yes" 
				frappe.confirm(
					msg,
					()=>{
						frappe.call({
						    "method": "bbt_bpm.bbt_bpm.page.customer_portal.customer_portal.add_to_cart_item",
						    args: {
						    	filters:filters
						    },
						    callback: function (r) {
						    	if (r.message){
						      		frappe.msgprint(__("Item Added in Cart"));
						    	}
			
						    }//calback end
						})
					},
					()=>{
							window.close();
					},
				)
			}
			else{
				frappe.call({
					"method": "bbt_bpm.bbt_bpm.page.customer_portal.customer_portal.add_to_cart_item",
					args: {
						filters:filters
					},
					callback: function (r) {
						if (r.message){
							  frappe.msgprint(__("Item Added in Cart"));
						}
	
					}//calback end
				})

			}
	    		
	    })
	},

	notify_me: function(me){
	    $('.notify_me').click(function() {
	    	let name = $(this).closest('tr').children('td.col4').text()
			
	     	var d = new frappe.ui.Dialog({
			fields: [
				{
					"label" : "Required QTY",
					"fieldname": "required_qty",
					"fieldtype": "Data",
					

				},
				{
					"label" : "Remark",
					"fieldname": "remark",
					"fieldtype": "Small Text",
					

				}
			],
			primary_action: function() {
	     		var data = d.get_values();

				frappe.call({
				method : "bbt_bpm.bbt_bpm.page.customer_portal.customer_portal.create_doc",
				args : { //"user": frappe.session.user,
						 "name": name,
						 "required_qty":data.required_qty,
						 "remark":data.remark,
						},

				callback: function(r){
					if (r.message){
						frappe.msgprint(__("Issue generated"));

					}
				}
			});
			d.hide();
			},
		});
		d.show();
	})

	},

	sort_table: function(){
		$(".table").ready(function(){
			// console.log('Hi');
			function sortTableByColumn(table, column, asc = true) {
				const dirModifier = asc ? 1 : -1;
				const tBody = table.tBodies[0];
				const rows = Array.from(tBody.querySelectorAll("tr"));

				// Sort each row
				const sortedRows = rows.sort((a, b) => {
					const aColText = a.querySelector(`td:nth-child(${ column + 1 })`).textContent.trim();
        			const bColText = b.querySelector(`td:nth-child(${ column + 1 })`).textContent.trim();
					// console.log(aColText);
					// console.log(bColText);

					return aColText > bColText ? (1 * dirModifier) : (-1 * dirModifier);

				});
				// console.log(sortedRows);

				while (tBody.firstChild) {
			        tBody.removeChild(tBody.firstChild);
			    }

			    // Re-add the newly sorted rows
			    tBody.append(...sortedRows);

			    // Remember how the column is currently sorted
			    table.querySelectorAll("th").forEach(th => th.classList.remove("th-sort-asc", "th-sort-desc"));
			    table.querySelector(`th:nth-child(${ column + 1})`).classList.toggle("th-sort-asc", asc);
			    table.querySelector(`th:nth-child(${ column + 1})`).classList.toggle("th-sort-desc", !asc);

			}
			// sortTableByColumn(document.querySelector('table'),1);

			document.querySelectorAll(".table-sortable th").forEach(headerCell => {
			    headerCell.addEventListener("click", () => {
			        const tableElement = headerCell.parentElement.parentElement.parentElement;
			        const headerIndex = Array.prototype.indexOf.call(headerCell.parentElement.children, headerCell);
			        const currentIsAscending = headerCell.classList.contains("th-sort-asc");

			        sortTableByColumn(tableElement, headerIndex, !currentIsAscending);
			    });
			});
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
			contact_person = $(".c_p").val()
			transportation_mode = $(".transp_mode").val()
			preferred_transporter = $(".p_t").val()
			freight_charges = $(".f_c").val()
			delivery_type = $(".d_t").val()
			shipping_address = $(".s_address").val()
			billing_address = $(".b_address").val()
			instruction_delivery = $(".i_d").val()
			special_instruction = $(".s_i").val()
			frappe.call({
		        "method": "bbt_bpm.bbt_bpm.page.customer_portal.customer_portal.new_order",
		        args: {
		        	client_feedback:client_feedback,
		        	contact_person: contact_person,
		        	transportation_mode: transportation_mode,
		        	preferred_transporter: preferred_transporter,
		        	freight_charges: freight_charges,
		        	delivery_type: delivery_type,
		        	shipping_address: shipping_address,
		        	billing_address: billing_address,
		        	instruction_delivery: instruction_delivery,
		        	special_instruction: special_instruction
		        },
		        //headers: {'content-type': 'application/json'},
		        callback: function (r) {
		        	if (r.message){
		        		window.location.reload()
		        	}

		        }//calback end
		    })	
		})
	},

	item_order_qty: function(me){
		$( ".item_order_qty" ).change(function() {
			var no_of_items_can_be_packed = $(this).attr("no_of_items_can_be_packed")
	    	var order_qty=jQuery($(this).closest('tr').children('td.col9')[0]).find("input[type='number']").val()
			no_of_cartons = 0.0
	    	no_of_cartons = Math.ceil(parseFloat(order_qty)/parseFloat(no_of_items_can_be_packed))
	    	total_req_qty = no_of_cartons*parseFloat(no_of_items_can_be_packed)
	    	if (total_req_qty && total_req_qty!=0 && parseFloat(order_qty)!=parseFloat(total_req_qty)){
	    		// frappe.msgprint(__("Add min {0} qty to fulfill Carton's Size OR to continue please click on add to cart again", [total_req_qty]));
			}
		});
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

		// const arr2 = [];
		// const icc = [];
		// frappe.db.get_list('Item',{fields: ['item_code'],limit: 1000,
		// 		}).then(res => {
					
		// 			// console.log(res);
		// 			for(var i=0; i < res.length; i++){
		// 				// console.log(typeof res[i]['item_code']);
		// 				// console.log(res[i]['item_code']);
		// 				// icc.push(res[i]['item_code']);
		// 				icc[i] = res[i]['item_code'];
		// 			}
		// 		});
		// console.log(icc);
		// console.log(icc.length); --> 0
        
        // 1. Item Code
		var icc=[];
        frappe.call({
    		method:"bbt_bpm.bbt_bpm.page.customer_portal.customer_portal.get_item_code",
    		args: {
    	        	user: frappe.session.user
	
    	    },
    		async:false, 
    		callback: function(r) {
				// console.log(r.message);
				// console.log(r);
			    icc = r.message.slice()	
				}
		});

        // 2. Description
        var descrip=[];
        frappe.call({
    		method:"bbt_bpm.bbt_bpm.page.customer_portal.customer_portal.get_description",
    		args: {
    	        	user: frappe.session.user
	
    	    },
    		async:false, 
    		callback: function(r) {
				// console.log(r.message);
				// console.log(r);
			    descrip = r.message.slice()	
				}
		});

		var me = this
		me.page.add_field({
			"fieldtype": 'Button',
			"label": __('Back'),
			"fieldname": 'home',
			click: function() {
				me.home = this.value?this.value:null
				window.location.href = "desk#customer_portal"
				window.location.reload()
				me.get_imp_data()
			}
		})

		me.page.add_field({
			"fieldtype": 'Autocomplete',
			"label": __("Language"),
			"fieldname": "language",
			"placeholder":"Search By Language",
			"options": [ "", "Assamese", "Bengali", "Chhattisgarhi", "English", "French", "Gujarati", "Hindi", "Japanese", "Kannada", "Marathi", "Korean", "Nepali", "Odia", "Punjabi", "Sinhala", "Tamil", "Telugu", "Urdu","Calendar","Diary","CD"],
			"reqd": 0,
			onchange: function() {
				me.language = this.value?this.value:null
				me.get_imp_data()
			}
		})
		$('[data-fieldname="language"]').css({"border": "1px solid Brown", "width": "90px"})

		me.page.add_field({
			"fieldtype": 'Autocomplete',
			"label": __("Category"),
			"fieldname": "category",
			// "placeholder":"Search By Language",
			"options": [ "", "Books", "Calendar", "Carton", "Catalogue", "CD", "Consumable", "Diary", "Poster"],
			"reqd": 0,
			onchange: function() {
				me.category = this.value?this.value:null
				me.get_imp_data()
			}
		})
		$('[data-fieldname="category"]').css({"border": "1px solid Brown","width": "90px"})

		me.page.add_field({
			"fieldtype": 'Autocomplete',
			"label": __("Item Code"),
			"fieldname": "item_code",
			"options": icc,
			"reqd": 0,
			onchange: function() {
				me.item_code = this.value?this.value:null
				me.get_imp_data()
			}
		})
		$('[data-fieldname="item_code"]').css({"border": "1px solid Brown", "width": "80px"})

		me.page.add_field({
			"fieldtype": 'Autocomplete',
			"label": __("Description"),
			"fieldname": "description",
			"options": descrip,
			"reqd": 0,
			onchange: function() {
				me.description = this.value?this.value:null
				me.get_imp_data()
			}
		})
		$('[data-fieldname="description"]').css({"border": "1px solid Brown", "width": "190px"})

		this.view_cart_button =  me.page.add_field({
			"fieldtype": 'Button',
			"label": __('View Cart'),
			"fieldname": 'add_to_cart_items',
			click: function() {
				me.add_to_cart_items = this.value?this.value:null
				$('[data-fieldname="home"]').show()
				$('[data-fieldname="language"]').hide()
				$('[data-fieldname="category"]').hide()
				$('[data-fieldname="item_code"]').hide()
				$('[data-fieldname="description"]').hide()
				frappe.call({
			        "method": "bbt_bpm.bbt_bpm.page.customer_portal.customer_portal.add_to_cart_details",
			        args: {
			        	user:frappe.session.user,
			        	filters: {"language":me.language,"category":me.category,"item_code":me.item_code,"description":me.description}
			        },
			        callback: function (r) {
			        	if (r.message){
			          		var html = r.message.html
							$('.frappe-list').html(html)
							$('.delete').hide()
							me.delete_add_to_cart_item()
							me.update_qty_on_cart()
							me.new_order()
							me.sort_table()
							$('[data-fieldname="download_pdf"]').hide()
			        	}

			        }//calback end
			    })
			}
		})
		$('[data-fieldname="add_to_cart_items"]').addClass("btn-primary")

		me.page.add_field({
		"fieldtype": 'Button',
		"label": __('Download Pdf'),
		"fieldname": 'download_pdf',
		click: function() {
			//var me = this;
			//console.log(me)
			//var language = $(this).closest('tr').children('td.first_col').text();

			//var language = $(this).attr("language");
		
			var filters = {"language":me.language};
			console.log(filters);

			//if (me.purchase_order){
				frappe.call({
					"method": "bbt_bpm.bbt_bpm.page.customer_portal.customer_portal.get_pdf_data",
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
							xhr.open("POST", '/api/method/bbt_bpm.bbt_bpm.page.customer_portal.customer_portal.download_pdf');
	
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
	    })


    }		
})


