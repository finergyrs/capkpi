// Copyright (c) 2019, Finergy Reporting Solutions SAS and contributors
// For license information, please see license.txt

finergy.ui.form.on('Process Deferred Accounting', {
	setup: function(frm) {
		frm.set_query("document_type", function() {
			return {
				filters: {
					'name': ['in', ['Sales Invoice', 'Purchase Invoice']]
				}
			};
		});
	},

	type: function(frm) {
		if (frm.doc.company && frm.doc.type) {
			frm.set_query("account", function() {
				return {
					filters: {
						'company': frm.doc.company,
						'root_type': frm.doc.type === 'Income' ? 'Liability' : 'Asset',
						'is_group': 0
					}
				};
			});
		}
	},

	validate: function() {
		return new Promise((resolve) => {
			return finergy.db.get_single_value('Accounts Settings', 'automatically_process_deferred_accounting_entry')
				.then(value => {
					if(value) {
						finergy.throw(__('Manual entry cannot be created! Disable automatic entry for deferred accounting in accounts settings and try again'));
					}
					resolve(value);
				});
		});
	},

	end_date: function(frm) {
		if (frm.doc.end_date && frm.doc.end_date < frm.doc.start_date) {
			finergy.throw(__("End date cannot be before start date"));
		}
	},

	onload: function(frm) {
		if (frm.doc.posting_date && frm.doc.docstatus === 0) {
			frm.set_value('start_date', finergy.datetime.add_months(frm.doc.posting_date, -1));
			frm.set_value('end_date', frm.doc.posting_date);
		}
	}
});
