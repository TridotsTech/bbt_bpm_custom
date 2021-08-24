frappe.ui.form.on("Item",
{
    onload(frm){
        frm.fields_dict["carton"].get_query = function()
        {
            return {
                filters:{
                        "item_group":['in',["carton", "packaging material"]]
                        }
                    }
        }
    }
});