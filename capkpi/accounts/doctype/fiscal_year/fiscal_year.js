// Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
// License: GNU General Public License v3. See license.txt

finergy.ui.form.on('Fiscal Year', {
	onload: function(frm) {
		if(frm.doc.__islocal) {
			frm.set_value("year_start_date",
				finergy.datetime.add_days(finergy.defaults.get_default("year_end_date"), 1));
		}
	},
	refresh: function (frm) {
		if (!frm.doc.__islocal && (frm.doc.name != finergy.sys_defaults.fiscal_year)) {
			frm.add_custom_button(__("Set as Default"), () => frm.events.set_as_default(frm));
			frm.set_intro(__("To set this Fiscal Year as Default, click on 'Set as Default'"));
		} else {
			frm.set_intro("");
		}
	},
	set_as_default: function(frm) {
		return frm.call('set_as_default');
	},
	year_start_date: function(frm) {
		if (!frm.doc.is_short_year) {
			let year_end_date =
				finergy.datetime.add_days(finergy.datetime.add_months(frm.doc.year_start_date, 12), -1);
			frm.set_value("year_end_date", year_end_date);
		}
	},
});
