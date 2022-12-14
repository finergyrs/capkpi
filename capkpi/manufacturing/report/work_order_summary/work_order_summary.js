// Copyright (c) 2016, Finergy Reporting Solutions SAS and contributors
// For license information, please see license.txt
/* eslint-disable */

finergy.query_reports["Work Order Summary"] = {
	"filters": [
		{
			label: __("Company"),
			fieldname: "company",
			fieldtype: "Link",
			options: "Company",
			default: finergy.defaults.get_user_default("Company"),
			reqd: 1
		},
		{
			fieldname: "fiscal_year",
			label: __("Fiscal Year"),
			fieldtype: "Link",
			options: "Fiscal Year",
			default: finergy.defaults.get_user_default("fiscal_year"),
			reqd: 1,
			on_change: function(query_report) {
				var fiscal_year = query_report.get_values().fiscal_year;
				if (!fiscal_year) {
					return;
				}
				finergy.model.with_doc("Fiscal Year", fiscal_year, function(r) {
					var fy = finergy.model.get_doc("Fiscal Year", fiscal_year);
					finergy.query_report.set_filter_value({
						from_date: fy.year_start_date,
						to_date: fy.year_end_date
					});
				});
			}
		},
		{
			label: __("From Posting Date"),
			fieldname:"from_date",
			fieldtype: "Date",
			default: finergy.defaults.get_user_default("year_start_date"),
			reqd: 1
		},
		{
			label: __("To Posting Date"),
			fieldname:"to_date",
			fieldtype: "Date",
			default: finergy.defaults.get_user_default("year_end_date"),
			reqd: 1,
		},
		{
			label: __("Status"),
			fieldname: "status",
			fieldtype: "Select",
			options: ["", "Not Started", "In Process", "Completed", "Stopped", "Closed"]
		},
		{
			label: __("Sales Orders"),
			fieldname: "sales_order",
			fieldtype: "MultiSelectList",
			get_data: function(txt) {
				return finergy.db.get_link_options('Sales Order', txt);
			}
		},
		{
			label: __("Production Item"),
			fieldname: "production_item",
			fieldtype: "MultiSelectList",
			get_data: function(txt) {
				return finergy.db.get_link_options('Item', txt);
			}
		},
		{
			label: __("Age"),
			fieldname:"age",
			fieldtype: "Int",
			default: "0"
		},
		{
			label: __("Charts Based On"),
			fieldname:"charts_based_on",
			fieldtype: "Select",
			options: ["Status", "Age", "Quantity"],
			default: "Status"
		},
	]
};
