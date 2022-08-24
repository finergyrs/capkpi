import finergy


def execute():
	"""Remove barcodes field from "Copy Fields to Variants" table because barcodes must be unique"""

	settings = finergy.get_doc("Item Variant Settings")
	settings.remove_invalid_fields_for_copy_fields_in_variants()
