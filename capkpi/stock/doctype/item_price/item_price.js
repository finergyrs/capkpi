// Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
// License: GNU General Public License v3. See license.txt

finergy.ui.form.on("Item Price", {
	onload: function (frm) {
		// Fetch price list details
		frm.add_fetch("price_list", "buying", "buying");
		frm.add_fetch("price_list", "selling", "selling");
		frm.add_fetch("price_list", "currency", "currency");

		// Fetch item details
		frm.add_fetch("item_code", "item_name", "item_name");
		frm.add_fetch("item_code", "description", "item_description");
		frm.add_fetch("item_code", "stock_uom", "uom");

		frm.set_df_property("bulk_import_help", "options",
			'<a href="/app/data-import-tool/Item Price">' + __("Import in Bulk") + '</a>');

		frm.set_query('batch_no', function() {
			return {
				filters: {
					'item': frm.doc.item_code
				}
			};
		});
	}
});
