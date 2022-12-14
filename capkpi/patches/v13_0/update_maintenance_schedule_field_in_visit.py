import finergy


def execute():
	finergy.reload_doctype("Maintenance Visit")
	finergy.reload_doctype("Maintenance Visit Purpose")

	# Updates the Maintenance Schedule link to fetch serial nos
	from finergy.query_builder.functions import Coalesce

	mvp = finergy.qb.DocType("Maintenance Visit Purpose")
	mv = finergy.qb.DocType("Maintenance Visit")

	finergy.qb.update(mv).join(mvp).on(mvp.parent == mv.name).set(
		mv.maintenance_schedule, Coalesce(mvp.prevdoc_docname, "")
	).where(
		(mv.maintenance_type == "Scheduled") & (mvp.prevdoc_docname.notnull()) & (mv.docstatus < 2)
	).run(
		as_dict=1
	)
