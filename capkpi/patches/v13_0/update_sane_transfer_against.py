import finergy


def execute():
	bom = finergy.qb.DocType("BOM")

	(
		finergy.qb.update(bom)
		.set(bom.transfer_material_against, "Work Order")
		.where(bom.with_operations == 0)
	).run()
