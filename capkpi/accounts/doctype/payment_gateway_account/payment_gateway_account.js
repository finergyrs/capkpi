// Copyright (c) 2019, Finergy Reporting Solutions SAS and Contributors
// License: GNU General Public License v3. See license.txt

finergy.ui.form.on('Payment Gateway Account', {
	refresh(frm) {
		if(!frm.doc.__islocal) {
			frm.set_df_property('payment_gateway', 'read_only', 1);
		}
	}
});
