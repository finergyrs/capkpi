# Copyright (c) 2021, Finergy and Contributors
# License: GNU General Public License v3. See license.txt

import finergy


def execute():
	finergy.reload_doc("manufacturing", "doctype", "production_plan")
	finergy.db.sql(
		"""
		UPDATE `tabProduction Plan` ppl
		SET status = "Completed"
		WHERE ppl.name IN (
			SELECT ss.name FROM (
				SELECT
					(
						count(wo.status = "Completed") =
						count(pp.name)
					) =
					(
						pp.status != "Completed"
						AND pp.total_produced_qty >= pp.total_planned_qty
					) AS should_set,
					pp.name AS name
				FROM
					`tabWork Order` wo INNER JOIN`tabProduction Plan` pp
					ON wo.production_plan = pp.name
				GROUP BY pp.name
				HAVING should_set = 1
			) ss
		)
	"""
	)
