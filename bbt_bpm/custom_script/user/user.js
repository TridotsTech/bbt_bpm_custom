frappe.ui.form.on('User', {
  refresh: function(frm) {
    if (frappe.user_roles.includes("Customer")) {
		$('input[type="checkbox"][data-module="Desk"]').prop('checked', false);
		$('input[type="checkbox"][data-module="Settings"]').prop('checked', false);
		$('input[type="checkbox"][data-module="Users and Permissions"]').prop('checked', false);
		$('input[type="checkbox"][data-module="Customization"]').prop('checked', false);
		$('input[type="checkbox"][data-module="Integrations"]').prop('checked', false);
		$('input[type="checkbox"][data-module="Core"]').prop('checked', false);
		$('input[type="checkbox"][data-module="Website"]').prop('checked', false);
		$('input[type="checkbox"][data-module="Social"]').prop('checked', false);
		$('input[type="checkbox"][data-module="Leaderboard"]').prop('checked', false);
		$('input[type="checkbox"][data-module="dashboard"]').prop('checked', false);
		$('input[type="checkbox"][data-module="Getting Started"]').prop('checked', false);
		$('input[type="checkbox"][data-module="Accounts"]').prop('checked', false);
		$('input[type="checkbox"][data-module="Buying"]').prop('checked', false);
		$('input[type="checkbox"][data-module="Selling"]').prop('checked', false);
		$('input[type="checkbox"][data-module="Stock"]').prop('checked', false);
		$('input[type="checkbox"][data-module="Projects"]').prop('checked', false);
		$('input[type="checkbox"][data-module="Support"]').prop('checked', false);
		$('input[type="checkbox"][data-module="Quality Management"]').prop('checked', false);
		$('input[type="checkbox"][data-module="Marketplace"]').prop('checked', false);
		$('input[type="checkbox"][data-module="Assets"]').prop('checked', false);
		$('input[type="checkbox"][data-module="CRM"]').prop('checked', false);
		$('input[type="checkbox"][data-module="HR"]').prop('checked', false);
		$('input[type="checkbox"][data-module="Help"]').prop('checked', false);

    }
  },
  validate: function(frm) {
  
  }
});
