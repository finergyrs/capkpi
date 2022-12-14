# Copyright (c) 2017, Finergy and Contributors
# License: GNU General Public License v3. See license.txt


import finergy


def execute():
	finergy.reload_doc("buying", "doctype", "buying_settings")
	finergy.db.set_value(
		"Buying Settings", None, "backflush_raw_materials_of_subcontract_based_on", "BOM"
	)

	finergy.reload_doc("stock", "doctype", "stock_entry_detail")
	finergy.db.sql(
		""" update `tabStock Entry Detail` as sed,
		`tabStock Entry` as se, `tabPurchase Order Item Supplied` as pois
		set
			sed.subcontracted_item = pois.main_item_code
		where
			se.purpose = 'Send to Subcontractor' and sed.parent = se.name
			and pois.rm_item_code = sed.item_code and se.docstatus = 1
			and pois.parenttype = 'Purchase Order'"""
	)
