// Copyright (c) 2016, Finergy Reporting Solutions SAS and contributors
// For license information, please see license.txt
/* eslint-disable */

finergy.query_reports["Procurement Tracker"] = {
	"filters": [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: finergy.defaults.get_user_default("Company"),
		},
		{
			fieldname: "cost_center",
			label: __("Cost Center"),
			fieldtype: "Link",
			options: "Cost Center",
		},
		{
			fieldname: "project",
			label: __("Project"),
			fieldtype: "Link",
			options: "Project",
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: finergy.defaults.get_user_default("year_start_date"),
		},
		{
			fieldname:"to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: finergy.defaults.get_user_default("year_end_date"),
		},
	]
}
