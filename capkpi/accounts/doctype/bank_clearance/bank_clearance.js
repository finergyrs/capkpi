// Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
// License: GNU General Public License v3. See license.txt

finergy.ui.form.on("Bank Clearance", {
	setup: function(frm) {
		frm.add_fetch("account", "account_currency", "account_currency");
	},

	onload: function(frm) {

		let default_bank_account =  finergy.defaults.get_user_default("Company")?
			locals[":Company"][finergy.defaults.get_user_default("Company")]["default_bank_account"]: "";
		frm.set_value("account", default_bank_account);

		frm.set_query("account", function() {
			return {
				"filters": {
					"account_type": ["in",["Bank","Cash"]],
					"is_group": 0
				}
			};
		});

		frm.set_value("from_date", finergy.datetime.month_start());
		frm.set_value("to_date", finergy.datetime.month_end());
	},

	refresh: function(frm) {
		frm.disable_save();
	},

	update_clearance_date: function(frm) {
		return finergy.call({
			method: "update_clearance_date",
			doc: frm.doc,
			callback: function(r, rt) {
				frm.refresh_field("payment_entries");
				frm.refresh_fields();
			}
		});
	},
	get_payment_entries: function(frm) {
		return finergy.call({
			method: "get_payment_entries",
			doc: frm.doc,
			callback: function(r, rt) {
				frm.refresh_field("payment_entries");
				frm.refresh_fields();

				$(frm.fields_dict.payment_entries.wrapper).find("[data-fieldname=amount]").each(function(i,v){
					if (i !=0){
						$(v).addClass("text-right")
					}
				})
			}
		});
	}
});
