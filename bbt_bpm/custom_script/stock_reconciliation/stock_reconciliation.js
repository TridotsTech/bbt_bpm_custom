frappe.ui.form.on('Stock Reconciliation', {
    
    refresh: function(frm) {
		if(frm.doc.docstatus < 1) {
			frm.add_custom_button(__("Fetch Items from Warehouse"), function() {
				frm.events.get_items(frm);
			});
		}
	},
	
	get_items: function(frm) {
		frappe.prompt([{label:"Warehouse", fieldname: "warehouse", fieldtype:"Link", options:"Warehouse", 
		                reqd: 1, 
		                "get_query": function() { 
			                return { 
			                	"filters": { "company": frm.doc.company, }
			                };
		                }},
		                {label:"Item Code", fieldname: "item_code", fieldtype:"Link", options:"Item", reqd: 0},
		                {label:"Language", fieldname: "book_language", fieldtype:"Link", options:"Book Language", reqd: 0},
		                ],

		                (values) => {
		                        
        		                       frappe.call({
        			                            method: "bbt_bpm.custom_script.stock_reconciliation.stock_reconciliation.get_warehouse_data",
        			                            args:{warehouse:values.warehouse,
        			                                  company:frm.doc.company,
        			                                  posting_date: frm.doc.posting_date,
        						                      posting_time: frm.doc.posting_time,
        						                      item_code: values.item_code,
        						                      book_language: values.book_language,
        						                   
        											  },
        			                                callback: function(r) {
        												var items = [];
        												frm.clear_table("items");
        												for(var i=0; i< r.message.length; i++) {
        													var d = frm.add_child("items");
        													$.extend(d, r.message[i]);
        													if(!d.qty) d.qty = null;
        													if(!d.valuation_rate) d.valuation_rate = null;
        												}
        												frm.refresh_field("items");
        											}
        			                        }); // frappe call ends
		                    
		                } // values ends
		                ,  __("Get Items"), __("Update")

		                
		              ); // frappe prompt ends
	        } // get_items ends
		  
    });