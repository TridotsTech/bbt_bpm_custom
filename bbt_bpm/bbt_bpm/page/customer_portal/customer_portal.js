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
		// $('[data-fieldname="language"]').val("Search By Language")
		// frm.set_df_property("language", "placeholder", "Search By Language");
	},

	make: function() {
		var me = this;
		$(`<div class="frappe-list list-container"></div>`).appendTo(me.page.main);
	},

	get_imp_data:function(){
	    var me = this
	    $('.frappe-list').html("")
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

	     	frappe.call({
				method : "bbt_bpm.bbt_bpm.page.customer_portal.customer_portal.create_doc",
				args : { //"user": frappe.session.user,
						 "name": name},

				callback: function(r){
					if (r.message){
						frappe.msgprint(__("Issue generated"));

					}
				}
			})
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
		var me = this
		me.page.add_field({
			"fieldtype": 'Button',
			"label": __('Back'),
			"fieldname": 'home',
			click: function() {
				me.home = this.value?this.value:null
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
		// var option = [ "", "Books", "Calendar", "Carton", "Catalogue", "CD", "Consumable", "Diary", "Poster"];
		$('[data-fieldname="category"]').css({"border": "1px solid Brown","width": "90px"})
		// $('[data-fieldname="category"]').autocomplete({source: option})

		me.page.add_field({
			"fieldtype": 'Autocomplete',
			"label": __("Item Code"),
			"fieldname": "item_code",
			// "placeholder":"Search By Language",
			"options": ["SCP001","HND041", "HND022", "ENG046", "BNG001", "HND097", "HND029", "HND115", "HND021", "HND016", "HND013", "HND145", "HND060", "HND139", "ENG080", "HND042", "HND017", "HND014", "HND162", "SCP004", "HND151", "HND018", "ENG101","HND072","HND121","HND102","HND040","ENG304","ENG224", "ENG164","ENG161","ENG113","ENG035","ENG034","ENG033","ENG031","ENG023","ENG020","ENG012","ENG010","ENG009","ENG002","ENG015","HND179","HND161","HND160","HND157","HND147","HND144","HND133","HND094","HND082","HND020","ENG313","ENG312","ENG225","ENG162","ENG145","ENG127","ENG123","ENG121","ENG102","ENG068","ENG064","ENG051","ENG043","ENG041","ENG039","ENG027","ENG025","ENG019","ENG018","ENG017","ENG014","ENG013","ENG011","ENG008","ENG007","ENG003","HND152","ENG337","ENG042","HND001","GJT050","HND114","MRT001","GJT080","HND078","BNG092","BNG033","ENG001","MRT082","HND127","GJT054","GJT024","GJT055","HND134","HND023","GJT051","GJT004","TLG031","ORY001","BNG050","BNG022","GJT041","BNG054","JPN004","JPN003","JPN002","BNG081","ORY004","BNG034","BNG012","BNG008","BNG091","BNG069","BNG104","BNG098","BNG071","BNG049","GJT081","GJT076","GJT070","GJT063","GJT026","GJT011","GJT014","HND116","GJT085","GJT078","GJT077","GJT074","GJT072","GJT071","GJT068","HND149","HND035","HND010","GJT066","GJT056","ENG342","ENG206","ENG196","ENG128","ENG006","HND164","GJT079","ENG133","MRT061","MRT059","MRT007","HND166","MRT081","MRT055","MRT051","MRT050","GJT001","MRT080","HND165","ENG308","PO108L","PO132S","PO134S","PO143L","PO105S","PO141S","PO119S","PO111S","PO133S","PO133B","PO129M","PO153S","PO153L","PO110S","BNG015","BNG002","Batch Test 2","Batch Test","ASM00878","HND178","HND150","HND103","HND101","HND024","GJT083","GJT082","GJT075","GJT06A","GJT069","GJT067","GJT064","GJT015","GJT013","GJT012","GJT010","GJT005","GJT003","ENG339","ENG303","TML001","MRT040","ENG273","ENG309","TML090","TML082","TML075","TML046","TML026","TML015","TML013","TML010","TML009","TML008","TML006","TLG062","TLG056","TLG054","TLG021","TLG010","TLG006","ORY088","ORY087","ORY084","ORY083","ORY040","ORY027","ORY025","ORY016","ORY012","MRT069","MRT067","MRT054","MRT047","MRT022",
 						"MRT020","MRT005","HND158","ENG338","ENG291","ENG216","BNG093","BNG072","BNG007","ENG215", "ENG126","NEP037","TLG020","TLG018","BNG082","ENGMCM","BNG040","ENG340","PNJ004","MRT078","MRT077","MRT073","MRT072","MRT068","MRT066","MRT064","MRT056","MRT048","MRT046","MRT045","MRT038","MRT036","MRT035","MRT029","MRT027","MRT018","MRT017","MRT014","MRT013","MRT011","MRT006","MRT004","MRT003","MRT002","ENG212","TLG033","ORY033","BNG095","BNG087","BNG041","BNG035","ENG210","ENG203","HND002","TLG052","TLG057","TLG019","TML071","TML069","TLG060","ORY005","ENG208","HND177","HND156","ENG038","TML091","BNG103","BNG064","ENG299","MRT076","GJT027","ENG213","TML093","TLG063","PO147B","GJT084","TML022","ORY008","ORY007","NEP001","BNG097","BNG059","BNG005","BNG010","BNG003","SC-39","HND176","ORY019","BNG016","HND074","TLG064","TLG061","PO147S","PO134M","PO117M","ENG343","NEP027","TML056","BNG101","BNG099","BNG089","BNG078","BNG076","BNG062","BNG052","BNG036","BNG026","BNG024","HND026","BNG061","CTG001","ENG214","FRE001","FRE007","FRE004","GJT062","MRT039","NEP010","NEP011","ORY032","ORY011","ORY026","ORY010","PNJ001","SND003","TML012","TML058","PO130M","PO211S","PO135M","PO133M","PO122S","PO123M","PO116M","PO119M","PO120S","PO106B","PO170S","PO146M","PO125L","PO132L","PO230S","PO150M","PO102M","PO103B","PO103M","PO103S","PO104B","PO104L","PO104M","PO105B","PO105M","PO106M","PO106S","PO107B","PO107M","PO107S","PO108B","PO108S","PO109B","PO109M","PO110B","PO111M","PO112B","PO112M","PO113B","PO113M","PO115B","PO115S","PO116B","PO116S","PO117B","PO118B","PO118S","PO119B","PO120B","PO121S","PO122B","PO124M","PO124S","PO125B","PO126B","PO126S","PO127B","PO127L","PO127M","PO127S","PO128M","PO129B","PO129L","PO131B","PO131L","PO131M","PO131S","PO132B","PO134B","PO134L","PO135B","PO135S","PO136B","PO136S","PO138M","PO141B","PO142B","PO142M","PO142S","PO143B","PO147M","PO148B","PO148L","PO148M","PO151M","PO151S","PO153B","PO154M","PO156M","PO157B","PO157L","PO157M","PO158B","PO158M","PO161M","PO161S","PO162M","PO163M","PO163S","PO164M","PO165M","PO166M","PO167M","PO168M","PO169M","PO201B","PO201M","PO201S","PO206M","PO206S",
 						"PO207M","PO207S","PO208B","PO208L","PO208M","PO208S","PO209M","PO210M","PO211B","PO211M","PO213B","PO215B","PO218B","PO218M","PO219B","PO228M","PO230M","PO109S","PO132M","PO167S","PO227M","PO229M","PO120M","PO121B","PO121M","PO104S","PO108M","PO110M","PO112L","PO112S","PO115M","PO117S","PO118M","PO122M","PO125M","PO125S","PO129S","PO136M","PO141M","PO143M","PO143S","PO144M","PO150B","PO153M","PO154B","PO154S","PO157S","PO203M","PO203S","PO214M","PO225M","PO226M","PO231M","SCP002","ASM003","PO102B","PO170M","BNG086","BNG090","BNG057","BNG056","BNG096","BNG088","BNG055","BNG100","BNG094","BNG080","BNG102","BNG014","BNG046","BNG023","ENG311","ENG290","ENG316","ENG037","ENG219","ENG217","ENG307","ENG301","ENG022","ENG026","ENG201","ENG289","ENG292","ENG293","ENG202","ENG314","ZPO008","FRN132","GJT034","GJT025","GJT020","GJT057","GJT073","HND081","HND120","HND039","HND153","HND132","HND141","HND143","HND148","HND154","HND155","HND163","KND068","KOR004","KOR003","KOR002","MRT034","MRT074","MRT075","MRT015","NEP023","NEP024","NEP020","NEP008","NEP029","NEP022","NEP003","NEP009","NEP026","NEP007","NEP025","NEP021","NEP012","NEP017","NEP034","NEP031","NEP006","NEP030","NEP004","NEP015","NEP035","NEP018","NEP033","NEP036","NEP014","NEP016","NEP013","NEP019","NEP032","ORY021","ORY089","ORY009","ORY039","ORY085","ORY086","ORY082","ORY017","ORY090","ORY006","ORY003","ORY002","ORY043","ORY042","ORY013","ORY037","ORY020","ORY028","PNJ003","SNL005","SNL004","SNL003","SNL008","SNL006","SNL010","SNL009","SNL002","SNL007","TML027","TML018","TML089","TML016","TML024","TML023","TML014","TML044","TML092","TML047","TML019","TML038","TML017","TML066","TML041","TML021","TML072","TML094","TLG029","TLG058","TLG030","TLG047","TLG005","TLG022","TLG026","TLG002","TLG053","TLG049","TLG004","TLG012","TLG008","TLG059","TLG048","TLG027","TLG015","TLG023","URD001","SC-48","ENG060","CL2001","TMCD01","GJT090","CL2002","HNCD14","DR2001","SCP003","PO102S"],
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
			// "placeholder":"Search By Language",
			"options": [ "","small Size Cartons","On The Way To Krishna (Krishna ki Aur)","Beyond Birth &amp; Death (Janma Mrutyu se Pare)","Srimad Bhagavatam (18 Volume Set)","Bhagavad Gita As It Is (Srimad Bhagavad Gita Jathajatha)","Transcendental Teachings of Prahlad Maharaj (Prahlad Maharaj Ka Divya Updesh) (Big Size)","The Perfection of Yoga (Yoga ki Purnata)","The Laws of Nature (Prakruti Ke Niyam)","Perfect Questions Perfect Answers (Purna Prashna Purna Uttar)","Raja-vidya: The King of Knowledge", "Coming Back (Punaragaman)", "Prabhupada (Condensed)", "Krishna The Reservoir of Pleasure (Rasaraj Sri Krishna) (Big Size)", "Message of Godhead (Karma Yoga)", "Prabhupada (Condensed)", "Krishna Consciousness: The Matchless Gift (Krishna Bhavnamrita ek Anupam Upahar)", "Elevation to Krishna Consciousness (Krishna Bhavanamrit Ki Prapti)", "The Topmost Yoga System (Sarvottam Yog Paddhati)", "Finding Our Lost Happiness (Khoye Hue Ananda ki Punah Prapti)", "Medium Size cartons", "Srila Prabhupada Lilamrita (Vol. 1 &amp; 2)", "The Nectar of Devotion (Bhakti Rasamrit Sindhu)", "Krsna, The Reservoir of Pleasure", "Srimad Bhagavatam (18 Volume Set)", "Teachings Of Lord Chaitanya: The Golden Avatara (Bhagavan Sri Chaitanya Mahaprabhu Ka Shikshamrita)", "The Journey of Self Discovery (Atma Ka Pravas)", "The Nectar of Instruction (Upadeshamrita)", "Finding Our Lost Happiness", "Bhakti - The Art of Eternal Love", "Beyond Illusion &amp; Doubt", "The Nectar of Devotion", "Srimad Bhagavatam First Canto", "Teachings of Lord Caitanya, The Golden Avatara", "A Second Chance", "The Journey of Self Discovery", "Perfect Questions &amp; Perfect Answers", "Coming Back", "Krsna Consciousness: The Matchless Gift", "The Path of Perfection", "Easy Journey to Other Planets", "Consciousness, The Missing Link", "The Science of Self - Realization", "Teachings of Lord Kapila, The Son of Devahuti", "Chanting Hare Krishna ( Hare Krishna Kirtan)", "Chant and Be Happy (Harinaam Jaap ki Mahima)", "Beyond Illusion and Doubt (Moha tatha Sanshay se Pare)", "Selected Verses From the Vedic Scriptures (Vedic Shastron se Chune Huve Shlok)", "Lord Chaitanya His Life and Teachings (Bhagavan Sri Chaitanya Mahaprabhu unka Jivan\nTatha Sikshamrita)", "Mukunda Mala Stotra", "Narada Bhakti Sutra", "Teachings Of Queen Kunti (Maharani Kunti Ki Shikshaen)", "Harinam Kirtan Guide (Harinaam Kirtan Nirdarshika)", "Easy Journey to Other Planets (Anya Grahon Ki Sugam Yatra)", "Transcendental Teachings of Narada Muni", "Meditation - Finding The Supersoul Within", "Spiritual Yoga", "The Nectar of Instruction", "Dharma: The Way of Transcendence", "The Quest for Enlightenment", "Introduction to Bhagavad Gita", "On The Way to Krsna", "Transcendental Teachings of Prahlada Maharaja", "Light of the Bhagavata", "Chanting Hare Krishna", "Mukunda Mala Stotra", "The Laws of Nature", "Narada Bhakti Sutra", "Message of Godhead", "The Hare Krishna Challenge", "Sri Brahma - Samhita", "Elevation To Krsna Consciousness", "The Perfection of Yoga", "Beyond Birth and Death", "Raja-vidya: The King of Knowledge", "The Topmost Yoga System", "Chant and Be Happy", "Sri Isopanisad", "Life Comes From Life", "Teachings Of Queen Kunti", "Narad Muni &amp; The Hunter (Narada Muni aur Mrugari) (Pocket Size)", "Modern Times, Vedic Perspective", "A Beginner's Guide to Krsna Conciousness", "Bhagavad Gita As It Is ( Bhagavad Gita - Yathaaroop)", "Krsna, The Supreme Personality of Godhead", "Bhagavad Gita As It Is (Deluxe Edition)", "<div>Bhagavad Gita As It Is ( Bhagavad Gita - Jasi ahe tasi)</div>", "Prabhupada (Condensed)", "Sri Caitanya Caritamrta ( 9 Volume Set)", "Transcendental Teachings of Prahlad Maharaj (Prahlad Maharaj Dibyo Upodesh)", "Srila Prabhupada - Spiritual Master For This Age (Yugacharya Srila Prabhupada)", "Bhagavad Gita As It Is", "Srimad Bhagavatam (18 Volume Set)", "The Hare Krishna Challenge (Hare Krishna Chunauti)", "Introduction to Bhagavad Gita (Gita Saar)", "Beyond Birth &amp; Death (Janam Aane Mrutyu ni Pehle Par)", "Transcendental Teachings of Prahlad Maharaja (Prahlad Maharaj na Divya Upadesho)", "Civilization and Transcendence (Adhyatma Aur Ekkisvi Sadi)", "Krsna, The Supreme Personality of Godhead", "The Nectar of Devotion (Bhakti Rasamrit Sindhu)", "The Nectar of Instruction (Upadeshamrita)",
						 "Bhagavad Gita As It Is (Bhagavad Gita - Yathathathamu )","Bhagavad Gita As It Is (Bhagavad Gita, Moulika Rupare)","Topics about the Supreme Lord (Bhogobaner Kotha)","Sri Caitanya Caritamrta (4 Volume Set)","Srimad Bhagavatam (18 Volume Set)","Lord Chaitanya His Life and Teachings (Sri Chaitanya Mahaprabhu Tar Jiboni O Shikha)\n(Pocket Size)","Beyond Birth &amp; Death","Perfection of Yoga","Perfect Question Perfect Answer","Srimad Bhagavatam (18 Volume Set) (Without Inner Baby Carton)","Srimad Bhagavatam (18 Volume Set)","Teachings Of Queen Kunti (Kuntidebir Shikha)","The Nectar of Instruction (Sri Upadeshamrita)","Perfect Questions Perfect Answers (Adarsh Proshno Adarsh Uttor)","Beyond Birth and Death (Janma Mrityur poropare)","Enlightenment Through Pancharatra Worshipping System (Pancharatra Prodip)","Introduction to Bhagavad Gita (Gita Saar)","Nectar Of Prabhupada's Teachings (Srila Prabhupada Kathamrita)","Easy Journey to Other Planets (Porolokay Sugom Yatra)","Verses for the Vaishnava Devotees (Baishnav Shlokabali)","Lord Caitanya His Life and Teachings (Bhagavan Sri Caitanya Mahaprabhu Temnu \nJivan Ane Upadesh) (Pocket Size)","Bhakti - The Art of Eternal Love ( Bhakti - ???vata pr?man? ka??)","Message of Godhead (Karma Yoga)","On the Way to Krishna (Krishna na Panthe)","Krishna The Reservoir Of Pleasure (Rasraj Shri Krishna)","Raja-vidya: The King of Knowledge","Life Comes From Life (Jivanno Mod Che Jivan)","Introduction to Bhagavad Gita (Gita Saar)","A Second Chance (Mr?tyun? par?jaya)","Dharma The Way of Transcendence (Dharma Divya tano Marg)","Teachings Of Queen Kunti (Mah?r??? kunt?n? upad???)","Spiritual Yoga (Adhyatmik Yoga)","The Path of Perfection (Yog Path)","Journey of Self Discovery (Aatmanobhuti no Parvas)","The Laws Of Nature (Prakruthi na Niyamo)","Bhagavad Gita As It Is (Pocket Edition ) (Flexi Bound)","Damodar Lila (Pocket Size)","Life Comes from Life (Jivan Ka Strot Jivan)","The Quest for Enlightenment (Gyan ni Shodhama)","The Topmost Yoga System (Sarvottam Yog Paddathi)","Vaisnava Ke? What Kind of Devotee Are You ?","Srimad Bhagavatam (44 Volume Set)","Krsna, The Supreme Personality of Godhead","Selected Verses From the Vedic Scriptures","Bhagavad Gita As It Is (Deluxe Edition)","Srimad Bhagavatam In Story Form (Srimad Bhagavatam Katharup)","Sri Caitanya Caritamrta ( 9 Volume Set)","Sri Caitanya Caritamrta ( 9 Volume Set)","Message of Godhead (Karma Yoga)","Prabhupada (Condensed)","The Science of Self - Realization (Atma Sakshatkarache Vidya)","Ramayana","The Quest for Enlightenment (Atma Shakshatkara cha Shodhat)","A Second Chance (Aani Oshalala Mrityu)","Life Comes From Life (Jivan Shakti Cha Ugam)","Krsna, The Supreme Personality of Godhead","Bhagavad Gita As It Is (Bhagavad Gita Tena Mod Rupe)","Srimad Bhagavatam in Story Form (Srimad Bhagavatam  Sanshikpt Gostirupat)","Words Of Wisdom From The Puranas (Purano se Gyanprakash)","Devotional Dishes (Recipes for Ekadasi Fasting)","Krishna Blesses The Fruit Vendor_L_27\" X 37\"","Ras Lila_S_11\" X 14\"","Radha Krishna &amp; 8 Gopies_S_11\" X 14\"","Paarth Sarthi_L_27\" X 37\"","Murli Krishna_S_11\" X 14\"","Lord Keshav_S_11\" X 14\"","Krishna Chastises Kalia_S_11\" X 14\"","Krishna Caught Stealing_S_11\" X 14\"","Gopinath_S_11\" X 14\"","Gopinath_B_19\" X 27\"","Divine Couple_M_14\" X 19\"","Divine Protector_S_11\" X 14\"","Divine Protector_L_27\" X 37\"","Butter Thieves_S_11\" X 14\"","Prabhupada (Condensed)(Soft Bound)","Life Comes From Life (Jibon Ase Jibon Theke)","Batc","Bat","ASM00878","Basics of Bhagavad Gita ( Bhagavad Gita Kee Moolbhoot shikshaen)","The Drama of Lord Jagannatha (Jagannath Priya Natakam)","A Second Chance (Mrityu Ki Parajay)","The Path of Perfection (Yoga Path)","The Science of Self - Realization (Atma Sakshatkar ka Vigyan)","Narada Bhakti Sutra","Mukunda Mala Stotra","Consciousness, The Missing Link (Khothi Kadi Chetna)","The Perfection of Yoga (Yog ki Purnata)","Civilization &amp; Transcendence (21 me Sadhi Aane Adhyatam)","Krishna Consciousness: The Matchless Gift (Anupam Bhet)","Elevation to Krishna Counsciousness (Krishna Bhakti ni Prapti)","Teachings of Lord Caitanya, The Golden Avatara (Bhagavan Sri Caitanya Mahaprabhu \nna Divya Upadesho)","Sri Isopanishad","Perfect Questions Perfect Answers (Purna Prashna Purna Uttar)","Coming Back (Punaragaman)","Easy Journey to Other Planets (Anya Grahon ni Saral Yatra )","The Science Of Self-Realization",
						 "Basics of Bhagavad - Gita","The Drama of Lord Jagannatha","Bhagavad Gita As It Is (Bhagavad Gita - U?maiyuruvil)","Sri Caitanya Caritamrta ( 9 Volume Set)" ,"Srila Prabhupada Lilamrta (7 Volume Set)" ,"The Science of Self - Realization (Deluxe Edition)" ,"Introduction To Bhagavad-Gita" ,"The Laws of Nature (Iyarkaiin sa??a?ga?)" ,"Transcendental Teachings of Prahlad Maharaj ( Pirakal?tari? Tivya upat?sa?ka?)" ,"Vaishnava Song Book (Vai??ava ?cc?riyarka?i? p?dalka?)" ,"The Nectar of Devotion ( Bhakti Rasamrita Sindhu)" ,"Beyond Birth and Death ( PIRAPUKUM IRAPAKUM APAL)" ,"Sri Isopanisad" ,"On the Way to Krishna ( Kiru??arukk??a va?iyil )" ,"Perfect Questions Perfect Answers (Pakkuvamana Kelvikalum Pakkuvamana Padhilkalum)" ,"The Perfection of Yoga  (Y?gatti? p?ra?attuvam.)" ,"Raja-vidya: The King of Knowledge ( A?ivi? arasa? )" ,"Message of Godhead (bhagavatsandheshamu)" ,"Krishna The Reservoir of Pleasure (Ananda Nidhi Sri Krishna Bhagavanudu)" ,"Srimad Bhagavatam (18 Volume Set)" ,"Beyond Birth and Death (Janma Mrityulaku Avatala)" ,"Krsna, The Supreme Personality of Godhead" ,"The Perfection of Yoga  (Yoga Paripurnata)" ,"Dharma The Way Of Transcendence (Dharma Dibyatar Marga)" ,"Civilization and Transcendence (Sabhyata O Aparthibata)" ,"Bhakti - The Art of Eternal Love (Bhakti, Saswata Premara Kala)" ,"Message of Godhead (Bhagavad Vani)" ,"Narada Bhakti Sutra (Narada Bhakti Sutra)" ,"Coming Back (Punarugamana)" ,"On The Way to Krishna (Krushna Bhaktira Pathe)" ,"The Perfection of Yoga (Jogara Purnata)" ,"Prabhupada (Condensed)" ,"Teachings Of Queen Kunti (Maharani Kunti Chi Shikvan)" ,"Lord Chaitanya His Life and Teachings (Bhagavan Sri Chaitanya Mahaprabhu Jivan ani \nShikvan)" ,"Dharma The Way of Transcendence (Sanatana Dharma)" ,"On the Way to Krishna (Premsagar SriKrishna)" ,"Raja-vidya: The King of Knowledge" ,"A Beginner's Guide to Krishna Consciousness (Krishna Bhavanemadhe Pahile Paul)" ,"Beyond Birth &amp; Death (Janma Mrityuchya Palikade)" ,"Jaya Jagannatha (Dhruv Maharaja Dasa)" ,"Brihad Bhagavatamrta Concisely Retold" ,"Krishna Art Book (Coffe Table Book)" ,"Lord Caitanya's Pilgrimage" ,"Coming Back (Punaragamon)" ,"The Supreme Father (Param Pita)" ,"Sri Isopanishad" ,"Mahabharata" ,"Sri Namamrta (The Nectar of The Holy Name)" ,"Bhagavad-gita As It Is (Pocket Size)" ,"The Nectar of Instruction (Upadeshamritam)" ,"Sri Isopanishad" ,"BHAKTIGITI SANCHAYAN" ,"Bhagavad Gita As It Is (Macmillan Edition)" ,"Songs of Bhagavad Gita (Gitar Gaan)(Soft Bound)" ,"Bhagavad Gita As It Is (Pocket Edition ) (Flexi Bound)" ,"Bhagavad Gita As It Is" ,"Bhakti - The Art Of Eternal Love (Bhakti - Shashvat Premachi Kala)" ,"Mukunda Mala Stotra" ,"Teachings of Lord Kapila, The Son of Devahuti (Bhagvan Kapil Deva Che Updesh)" ,"The Path of Perfection (Purnatvakade Vatchal)" ,"Sri Chaitanya Charitamrita (Adi Lila Vol.1)" ,"Bhagavad Gita As It Is (Pocket Edition ) (Flexi Bound)" ,"The Nectar of Devotion (Bhakti Rasamrit Sindhu)" ,"Krishna The Reservoir of Pleasure (Rasaraj Sri Krishna)" ,"Chant &amp; Be Happy (Hare Krishna Mantrashakti Aani Kimya)" ,"Civilization &amp; Transcendence (Adhyatma Aani 21ve Shatak)" ,"Elevation to Krishna Consciousness (Krishna Bhavnacha Subodhbhanu)" ,"Light of Bhagavata (Bhagavata cha Prakash)" ,"Srimad Bhagavatam First Canto  (Srimad Bhagavatam Bhag 1)" ,"Introduction to Bhagavad Gita (Gita Saar - Bhagavad Gitecha Parichay)" ,"Transcendental Teachings of Prahlad Maharaj (Prahalad Maharajachi Divya Shikvan)" ,"Prabhupada Booklet" ,"Krsna Consciousness: The Matchless Gift (Krishna Bhavanamurt - Ek Anupam Bhet)" ,"The Topmost Yoga System (Sarvottam Yog)" ,"Coming Back (Punaragaman)" ,"The Hare Krishna Challenge (Hare Krishna Aavhan)" ,"The Nectar of Instruction (Upadeshamrita)" ,"Sri Isopanishad" ,"The Perfection of Yoga (Yogachi Purnata)" ,"Easy Journey to Other Planets (Etar Grahancha Sugam Pravas)" ,"Teachings of Lord Chaitanya (Sri Chaitanya Shikshamrit)" ,"Srimad Bhagavatam in Story Form" ,"Srimad Bhagavatam First Canto" ,"Srimad Bhagavatam in Story Form ( Srimad Bhagavatam Sankhipta Rupare )" ,"Narada Bhakti Sutra" ,"Mukunda Mala Stotra" ,"Bhagavad Gita As It Is (Deluxe Edition)" ,"Who is a Vaishnava (Baishnav Ke?)" ,"Jaya Jagannatha (Dhruv Maharaja Dasa)" ,"Valmiki's Ramayana ( Purnaprajna Dasa)" ,"Srimad Bhagavatam First Canto  (Srimad Bhagavatam Pratham Skand)" ,"Bhagavad Gita As It Is (Pocket Edition ) (Flexi Bound)" ,"Transcendental Teachings of Prahlad Maharaja (Prahalada Maharaju divya b?dhanalu )" ,"Perfect Questions Perfect Answers (uttama prashnalu uttama samadhanalu)" ,"Sri Caitanya Caritamrta ( 9 Volume Set)" ,"Srimad Bhagavatam (18 Volume Set)" ,"Sri Caitanya Caritamrta ( 9 Volume Set)" ,"Sri Caitanya Caritamrta ( 9 Volume Set)" ,"Words of Wisdom from the Puranas" ,"Sri Chaitanya Bhagavata" ,"Prem Pradipa" ,"Civilization and Transcendence" ,"Coming Back  (Marupiravi)","Srimad Bhagavatam First Canto", "Glories of Srimad Bhagavad Gita (Srimad Bhagavad Gita Mahatmya)", "Ramayana - Coffee Table Book", "Ramayana", "Beginner's Guide to Krsna Consciousness (Krishna Bhavanamrit Pratham Pagalu)", "Shri Chaitanya Charitamrita (Condensed)", "Chaitanya Charitamrta (Condensed) (Sr? caita?ya carit?mrutam)", "Kaliyugamlo Pancha Mahayajnalu", "Universal Form of the Lord_B_19\" X 27\"", "Chaitanya Charitamrta (Condensed)", "Srimad Bhagavatam First Canto  ( Srimad Bhagavatam Mudal k???am )", "The Path of Perfection (Sidhi Lavara Pathe)", "Raja-vidya: The King of Knowledge", "Bhagavad-gita As It Is", "Srimad Bhagavatam (18 Volume Set) (With 3 Inner Baby Cartons)", "Glories of Ekadashi (Ekadasi Mahatmya)", "Teachings of Lord Kapila, The Son of Devahuti (Devahutinandana Kapiladeber Shikha)", "Elevation to Krishna Consciousness_BNG", "Krishna The Reservoir of Pleasure_BNG", "39*39*39", "Srila Prabhupada Booklet", "Krsna, The Supreme Personality of Godhead  (Shree Krushna)", "Parameshwar Bhogoban Sri Krishna (Pocket Size)_BNG", "A Beginner's Guide to Krishna Consciousness (Krsna Bhavnamrit mey Pahela Kadam)", "Sukhamaya Jeevananiki Nalagu Niyamalu", "Srimad Bhagavatam in story form (Bhagavatha Kathalu)", "Universal Form of the Lord_S_11\" X 14\"", "Radha Krishna &amp; 8 Gopies_M_14\" X 19\"", "Krishna Balaram &amp; Gopas_M_14\" X 19\"", "Srimad Bhagavatam 10 Volume Set (Upto 10th Canto)", "Srimad Bhagavatam Canto 1", "Krsna, The Supreme Personality of Godhead", "Renunciation Through Wisdom (Bairagya Vidya)", "Rescuing Sita (Ramayan Sita Uddhar)", "Krishna Consciousness: The Matchless Gift (Krishnabhabanamrita ek Anupam Upahar)", "The Laws of Nature (Prakritir Niyam- Karmer Abashyambhabi Phal)", "Most Merciful Lord Krishna (Krishna Boro Doyamoy)", "Preaching is the Essence (Paropakar)", "Recitation Of Verses In Glorification (Bhaktivedanta Stotrabali)", "The Science of Self Realization (Atmagyan Labher Pantha)", "Nectar Of Krishna Consciousness (Krishnabhabana Amrita)", "On the Way to Krishna (Sri Krishner Sondhane)", "Teachings of Lord Kapila, The Son of Devahuti (Bhagavan Kapila ka Sikshamrita)", "The Hare Krishna Challenge (Hare Krishna Andolan)", "Light of the Bhagwata", "Sri Caitanya Bhagavata Of Vrndavana Dasa Thakura (Condensed)", "Bhagavad Gita As It Is", "Krishna Book", "Life Comes From Life", "The Drama of Lord Jagannatha (Bhagavan Jagannatha Natak)", "Bhagavad Gita As It Is (Deluxe Edition)", "Krsna Consciousness The Topmost Yoga System", "The Journey Of Self-Discovery", "Valmiki's Ramayana", "Teachings of Lord Chaitanya", "Life Comes Form Life", "Nectar of Devotion", "Isopanishad", "Krishna (R.O.P.)", "The Path Of Perfection", "Narada - Bhakti - Sutra: The Secrets Of Transcendental Love", "Divine Love_M_14\" X 19\"", "Gita Upadesh_S_11\" X 14\"", "Gopijana-Vallabh_M_14\" X 19\"", "Gopinath_M_14\" X 19\"", "Goverdhan Dhari_S_11\" X 14\"", "Krishna &amp; Peakcock_M_14\" X 19\"", "Krishna Balaram Leave For Forest_M_14\" X 19\"", "Krishna Chastises Kalia_M_14\" X 19\"", "Krishna in Vrindavan_S_11\" X 14\"", "Krishna Shows the Universe_B_19\" X 27\"", "Krishna Sports with His Queens in the Water_S_11\" X 14\"", "Kurukshetra_M_14\" X 19\"", "Radha &amp; Krishna_L_27\" X 37\"", "Ras Lila_L_27\" X 37\"", "Shri Shir Radha Rasbihariji_S_11\" X 14\"", "The Super Soul_M_14\" X 19\"", "Birth of Lord Krishna_M_14\"X19\"", "Vasudev Takes Krishna to Gokul_B_19\"X27\"", "Vasudev Takes Krishna to Gokul_M_14\"X19\"", "Vasudev Takes Krishna to Gokul_S_11\"X14\"", "Mother Yashoda_B_19\"X27\"", "Mother Yashoda_L_27\"X37\"", "Mother Yashoda_M_14\"X19\"", "Murli Krishna_B_19\"X27\"", "Murli Krishna_M_14\"X19\"", "Krishna Shows the Universe_M_14\"X19\"", "Krishna Shows the Universe_S_11\"X14\"", "Yashoda Chases Krishna_B_19\"X27\"", "Yashoda Chases the Krishna_M_14\"X19\"", "Yashoda Chases Krishna_S_11\"X14\"", "Krishna Blesses The Fruit Vendor_B_19\"X27\"", "Krishna Blesses The Fruit Vendor_S_11\"X14\"", "Makhan Chor_B_19\"X27\"", "Makhan Chor_M_14\"X19\"", "Butter Thieves_B_19\"X27\"", "Krishna Caught Stealing_M_14\"X19\"", "Yasoda Bounds Krishna_B_19\"X27\"", "Yasoda Bounds Krishna_M_14\"X19\"", "Krishna Captivates Gopi's_B_19\"X27\"","Yasoda Decorates Krishna_B_19\"X27\"","Yasoda Decorates Krishna_S_11\"X14\"","Krishna Balaram Leave for Forest_B_19\"X27\"","Krishna Balaram Leave For Forest_S_11\"X14\"","Krishna Balaram &amp; Gopas_B_19\"X27\"","Krishna Enjoying Lunch in the Forest_B_19\"X27\"","Krishna Enjoying Lunch in the Forest_S_11\"X14\"","Krishna Chastises Kalia_B_19\"X27\"","Krishna in Vrindavan_B_19\"X27\"","Krishna Returns From the Forest_S_11\"X14\"","Goverdhan Dhari_B_19\"X27\"","Venu Gopal_M_14\"X19\"","Venu Gopal_S_11\"X14\"","Radha &amp; Krishna_B_19\"X27\"","Divine Love Swing_B_19\"X27\"","Divine Love Swing_S_11\"X14\"","Jhulan Yatra_B_19\"X27\"","Jhulan Yatra_L_27\"X37\"","Jhulan Yatra_M_14\"X19\"","Jhulan Yatra_S_11\"X14\"","Radha Krishna Meet_M_14\"X19\"","Divine Couple_B_19\"X27\"","Divine Couple_L_27\"X37\"","Sri Sri Radha Kunjbihari_B_19\"X27\"","Sri Sri Radha Kunjbihari_L_27\"X37\"","Sri Sri Radha Kunjbihari_M_14\"X19\"","Sri Sir Radha Kunjbihari_S_11\"X14\"","Ras Lila_B_19\"X27\"","Radha Krishna &amp; 8 Gopies_B_19\"X27\"","Radha Krishna &amp; 8 Gopies_L_27\"X37\"","Gopijana-Vallabh_B_19\"X27\"","Gopijana-Vallabh_S_11\"X14\"","Sri Radhe Worships_B_19\"X27\"","Sri Radhe Worships_S_11\"X14\"","The Lord Delivers_M_14\"X19\"","Lord Keshav_B_19\"X27\"","Gopal Krishna_B_19\"X27\"","Gopal Krishna_M_14\"X19\"","Gopal Krishna_S_11\"X14\"","Paarth Sarthi_B_19\"X27\"","Universal Form of the Lord_M_14\"X19\"","Krishna Reveals the Divine Form_B_19\"X27\"","Krishna Reveals the Divine Form_L_27\"X37\"","Krishna Reveals the Divine Form_M_14\"X19\"","Ten Incarnations of the Lord_M_14\"X19\"","Ten Incarnations of the Lord_S_11\"X14\"","Divine Protector_B_19\"X27\"","Lord Chaitanya_M_14\"X19\"","Panch Tattva_M_14\"X19\"","Lord Chaitanyas Sankirtan_B_19\"X27\"","Lord Chaitanyas Sankirtan_L_27\"X37\"","Lord Chaitanyas Sankirtan_M_14\"X19\"","Srila Prabhupada_B_19\"X27\"","Srila Prabhupada_M_14\"X19\"","Bathing Ceremony of Krishna_M_14\"X19\"","Bathing Ceremony of Krishna_S_11\"X14\"","Cowherd Men &amp; Boys at Govardhan_M_14\"X19\"","Krishna Delivers the Yamala Arjuna Trees_M_14\"X19\"","Krishna Delivers The Yamala Arjuna Trees_S_11\"X14\"","Krishna Rescues 16100 Princes_M_14\"X19\"","Krishna Meets with Gopies at Kurukshetra_M_14\"X19\"","Lord Narsimhadev (Mayapur)_M_14\"X19\"","Krishna Kills The Cart Demon_M_14\"X19\"","Lord Chaitanya's Sankirtan in Moon Light_M_14\"X19\"","Krishna Enjoys Forest_M_14\"X19\"","Sri Sri Radha Rasbihariji_B_19\"X27\"","Sri Sri Radha Rasbihariji_M_14\"X19\"","Sri Sri Radha Rasbihariji_S_11\"X14\"","Sri Sri Radha Shyam Sunder (Vrindavan)_M_14\"X19\"","Sri Sri Radha Shyam Sunder (Vrindavan)_S_11\"X14\"","Sri Sri Radha Shyam  Sunder_M_14\"X19\"","Sri Sri Radha Shyam Sunder_S_11\"X14\"","Sri Sri Radha Govind_B_19\"X27\"","Sri Sri  Radha  Govind_L_27\"X37\"","Sri Sri Radha Govind_M_14\"X19\"","Sri Sri  Radha Govind_S_11\"X14\"","Krishna Pleases Bhisma_M_14\"X19\"","Krishna Master of Flute_M_14\"X19\"","Gita Upadesh_B_19\"X27\"","Gita Upadesh_M_14\"X19\"","Radha Ras Bihariji (Red)_B_19\"X27\"","Shri Gaur Nitai_B_19\"X27\"","Vamandev_B_19\"X27\"","Vamandev_M_14\"X19\"","Kurukshetra_B_19\"X27\"","Lord Krishna Known As Govinda_M_14\"X19\"","Shri Shir Radha Rasbihariji_M_14\"X19\"","Makhan Chor_S_11\"X14\"","Ras Lila_M_14\"X19\"","Krishna Kills The Cart Demon_S_11\"X14\"","Krishna Playing Flute_M_14\"X19\"","The Sound of Krishna's Flute_M_14\"X19\"","Krishna In Vrindavan _M_14\"X19\"","Krishna Returns From The Forest_B_19\"X27\"","Krishna Returns From The Forest_M_14\"X19\"","Mother Yashoda_S_11\"X14\"","Krishna Blesses The Fruit Vendor_M_14\"X19\"","Butter Thieves_M_14\"X19\"","Krishna Caught Stealing_L_27\"X37\"",
						 "Krishna Captivates Gopi's_M_14\"X19\"", "Yasoda Bounds Krishna_S_11\"X14\"","Yasoda Decorates Krishna_M_14\"X19\"","Krishna Balaram &amp; Gopas_S_11\"X14\"","Krishna Enjoying Lunch In The Forest_M_14\"X19\"","Goverdhan Dhari_M_14\"X19\"","Radha &amp; Krishna_M_14\"X19\"","Radha &amp; Krishna_S_11\"X14\"","Divine Couple_S_11\"X14\"","Sri Radhe Worships_M_14\"X19\"","Lord Keshav_M_14\"X19\"","Paarth Sarthi_M_14\"X19\"","Paarth Sarthi_S_11\"X14\"","Krishna &amp; Arjuna Blowing Conch Shell_M_14\"X19\"","The Super Soul_B_19\"X27\"","Divine Protector_M_14\"X19\"","Lord Chaitanya_B_19\"X27\"","Lord Chaitanya_S_11\"X14\"","Lord Chaitanyas Sankirtan_S_11\"X14\"","Sri Sri Rasbihariji_M_14\"X19\"","Sri Sri Rasbihariji_S_11\"X14\"","Radha Ras Bihariji_M_14\"X19\"","Krishna &amp; Balarama Milking The Cows_M_14\"X19\"","Krishna &amp; Balarama In Vrindavan_M_14\"X19\"","Gopal Charms The Cows_M_14\"X19\"","Big Size Carton","Srimad Bhagavatam in Story Form","Birth of Lord Krishna_B_19\"X27\"","Krishna Sports with His Queens in the Water_M_14\"X19\"","A Second Chance (Ar Ekti Sujog)","Chant and Be Happy (Kirtan Korun Ebong Khushi Hon)","Devotion to Lord Krishna - The Topmost Science (Krishna Bhakti Sarbottam Bigyan)","In search of God (Ishwarer Shandhane)","Jagannath Priya Natakam","Journey of Self Discovery (Atmanushondhan ek Paramarthik Yatra)","Krsna, The Supreme Personality of Godhead  (Lila Purushottam Sri Krishna)","Lord Caitanya In Five Features (Panchatattvarupe Bhogoban Sri Chaitanya Mahaprabhu)","Lord Chaitanya His Life And Teachings (Sri Chaitanya Mahaprabhu Tar Jiboni O Shikha)","Prashna Karun Uttar Paben Part 1","Prashna Korun Uttar Paben Part 2","Teachings Of Lord Chaitanya (Sri Chaitanya Mahaprabhur Shikha)","The Nectar of Devotion (Bhakti Rasamrita Sindhu)","The Path of Perfection (Yog Siddhi)","Bhagavad Gita As It Is Further Explained","Lord Caitanya His Life &amp; Teachings","Prabhupada Booklet","Songs of the Vaisnava Acaryas","Srila Prabhupada (Srila Prabhupada’s rare pictures) \n(Foreign Edition) (Size 13” x 15.5”)","The Hare Krishna Book of Vegetarian Cooking","The Path of Perfection ( Deluxe Edition )","The Stories of Krsna (4 Volume Set )","Rama Colouring Book","The Scientific Basis Of Krishna Consciousness","Stories From Puranas","A Shower Of Divine Compassion","King Ambarisha The Most Exalted Devotee Of The Lord - Coloring Book","Vamana - Coloring Book","Gita for Daily Enrichment","Our Family Business","Vedic Encyclopedia 108 vol. Mailer cum Catalog","This Is My Request_FRN","Srila Prabhupada Booklet","The Hare Krishna Challenge (Hare Krishna Padhakar)","Srimad Bhagavatam First Canto","Light Of The Bhagavata (Bhagavad Na Prakash)","Valmiki's Ramayana","Light of Bhagavat (Bhagavat Ka Prakash)","Sri Brahma - Samhita","Sri Isopanishad","The Stories of Krsna (4 Volume Set )(Sri Krishna ki Kahaaniya)","Sword Of Knowledge (Gyan Ki Talwar)","Transcendental Teachings Of Prahlada Maharaja (Prahlad Maharaj Ka Divya Updesh) (Pocket Size)","Krsna, The Reservoir Of Pleasure (Rasaraj Sri Krishna) (Pocket Size)","Lord Caitanya His Life &amp; Teachings (Bhagavan Sri Chaitanya Mahaprabhu Unka Jivan Tatha Sikshamrita)","Braj Lila: Bhagavan Krishn Ka Janm (Pocket Size)","The Scientific Basis Of Krishna Consciousness (Krishna Bhavanamrita Ka Vaignanik Adhaar)","Goverdhan Brajvasi Leela (Pocket Size)","Beginner's Guide to Krishna Consciousness","Beyond Birth &amp; Death","Perfection of Yoga","Perfect Question Perfect Answer","The Laws of Nature (Prakruti Che Niyam)","Sri Chaitanya Bhagavata","Stories From The Puranas (Puranatil Katha)","Perfect Questions Perfect Answers (Purna Prashna Purna Uttar)","Beginner's Guide To Krishna Consciousness","Civilization &amp; Transcendence","Coming Back","Dharma","Easy Journey to Other Planets","Elevation to Krishna Consciousness","Hare Krishna Challenge","Introduction to Bhagavad Gita","Krishna, The Reservoir of Pleasure","Krsna, The Supreme Personality of Godhead","Laws of Nature","Light of Bhagavata","Matchless Gift","Message of Godhead","Mukunda-Mala Stotra","Nectar of Instruction",
						 "Perfect Question Perfect Answers","Perfection of Yoga","Raja Vidya","Science of Self Realization","Songs of the Vaishnava Acharyas","Spiritual Yoga","Teachings of Lord Chaitanya","Teachings of Lord Kapila","Teachings of Queen Kunti","The Path of Perfection","The Scientific Basis Of Krishna Consciousness","A Second Chance: The Story Of A Near-Death Experience","Srimad Bhagavatam Second Canto","Beyond Birth and Death (Janma Mrutyura Parapare)","Chant and Be Happy (Japa Kara Ebon Sukhi Ruha)","Easy Journey to Other Planets (Anya Grahaku Sugama Jatra)","Journey of Self Discovery (Atma Anwesanara Pathe)","Krishna The Reservoir of Pleasure (Rasaraja Shree Krushna)","Lord Caitanya His Life and Teachings (Bhagaban Shree Chaitanya Mahapravu Tankara \nJibani Abom Sikhshyamrita)","Narada Bhakti Sutra (Narada Bhakti Sutra)","Perfect Questions Perfect Answers (Adarsha Prashna Adarsha Uttara)","Spiritual Yoga (Adhyatmika Yoga)","Sri Isopanishad","Teachings of Lord Kapila, The Son of Devahuti (Devahuti Nandana Shree Kapila \nSikhshyamruta)","Teachings of Queen Kunti (Rani Kuntinka Sikshya)","The Hare Krishna Challenge (Hare Krishna Andolan)","The Nectar of Instruction (Shree Upadeshamruta)","The Science of Self - Realization (Atma Bigyana)","The Topmost Yoga System (Krishna Bhabana Sarbashrestha Yoga Padhati)","Transcendental Teachings of Prahlad Maharaja (Prahalad Maharajanka Divya Upadesha)","The Laws Of Nature: An Infallible Justice (Prakrutira Niyama)","Beginner's Guide To Krishna Consciousness","Beginner's Guide to Krishna Consciousness","Beyond Birth and Death","Coming Back","Isophanishad","Laws of Nature","On the Way to Krishna","Perfection of Yoga","Raja Vidya","The Topmost Yoga System","A Beginner's Guide to Krishna Consciousness (?r arampanilai va?ik???i)","Civilization and Transcendence (??m?ka v??kkai)","Dharma The Way Of Transcendence (Dharmam)","Elevation to Krishna Consciousness ( Amaitiy??a v??vukku va?i)","Krishna The Reservoir of Pleasure (Kiru??ar i?patti? iruppidam )","Krsna Consciousness: The Matchless Gift  (Kr??a u?arvu ??u i?aiya??a varam)","Life Comes From Life (Uyiriliruntu uyir t???uki?atu)","Prabhupada (Condensed) ( Prabhupada)","Spiritual Yoga ( atma yogam )","Sri Brahma - Samhita ( Sri Brahma Samhitai)","Teachings of Lord Kapila, The Son of Devahuti (D?vah?tiyi? kum?ra? kapil?vi? p?ta?aika?)","Teachings Of Queen Kunti (Kunti mak?r??iyi? p?ta?aika?)","The Hare Krishna Challenge ( Saval)","The Nectar of Instruction (Upadeshamritam)","The Science of Self - Realization  (Ta??aiya?iyum vińń??am)","The Topmost Yoga System  (miga unnatha yogam)","Ramayana of Valmiki ( Valmiki Ramayanam)","Bhagavad Gita As It Is (Pocket Size)","A Beginner's Guide to Krishna Conciousness (Prarambha Kulaku Krishna Chaitanya Margadarshini)","Bhakti - The Art of Eternal Love ( bhakti )","Chant and Be Happy (Harinama Sankirtana cheyandhi Anadani Pondhanti  )","Dharma The Way Of Transcendence ( Sarvasrestamayana Margam Dharmamu)","Easy Journey to Other Planets (Grahantara Sulabhayanamu )","Elevation to Krishna Consciousness (Krishna Chaitanya Sadhana)","Introduction to Bhagavad Gita (Gita Saram )","Krsna Consciousness: The Matchless Gift  (Advitiya Vara Prasadam )","Lord Chaitanya His Life and Teachings (Sri Chaitanya Mahaprabhu Jivitacharitra Mariyu \nUpadeshamlu )","Mukunda Mala Stotra (Mukundhamala Stotramu )","On the Way to Krishna (Sri Krishnuni Chere Margam)","Prabhupada Booklet (Adyatmika Jagatu sandhesani Tiskoni ochina Srila Prabhupadu )","Raja-vidya: The King of Knowledge ( Raja Vidya )","Spiritual Yoga  (Adhyatmika Yogam)","The Laws of Nature (prakruti niyamalu)","The Path of Perfection (purnatvapatham )","The Science of Self - Realization  (atma sakshatkara Shasramu)","The Topmost Yoga System  (Krishna Chaitanyame Sarvottamam Yogam)","Bhagavad Gita As It Is","48*48*23","Srila Prabhupada Vyasa Puja 2019","Gopala krishna 12 Sheeter Calenders","COLLECTED LECTURES ON SRIMAD BHAGAVAD GITA (MP3)","Hare Krishna Challenge","Goloka Table Calenders","Srila Prabhupada Vani (Lectures &amp; Bhajans)","Utsav Diary","Large Size Carton","Birth of Lord Krishna_S_11\"X14\""],
			"reqd": 0,
			onchange: function() {
				me.description = this.value?this.value:null
				me.get_imp_data()
			}
		})
		$('[data-fieldname="description"]').css({"border": "1px solid Brown", "width": "190px"})

		// me.page.add_field({
		// 	"fieldtype": 'Data',
		// 	"label": __("Books Per Carton"),
		// 	"fieldname": "books_carton",
		// 	// "placeholder":"Search By Language",
		// 	// "options": [ "", "Assamese", "Bengali", "Chhattisgarhi", "English", "French", "Gujarati", "Hindi", "Japanese", "Kannada", "Marathi", "Korean", "Nepali", "Odia", "Punjabi", "Sinhala", "Tamil", "Telugu", "Urdu"],
		// 	"reqd": 0,
		// 	onchange: function() {
		// 		me.books_carton = this.value?this.value:null
		// 		me.get_imp_data()
		// 	}
		// })
		// $('[data-fieldname="books_carton"]').css({"border": "1px solid Brown", "width": "110px"})

		me.page.add_field({
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
