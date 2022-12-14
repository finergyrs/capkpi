// Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
// License: GNU General Public License v3. See license.txt

finergy.query_reports["Supplier-Wise Sales Analytics"] = {
	"filters": [
		{
			"fieldname":"supplier",
			"label": __("Supplier"),
			"fieldtype": "Link",
			"options": "Supplier",
			"width": "80"
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": finergy.datetime.month_start()
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"width": "80",
			"default": finergy.datetime.month_end()
		},
	]
}
