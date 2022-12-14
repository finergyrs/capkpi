// Copyright (c) 2016, Finergy Reporting Solutions SAS and contributors
// For license information, please see license.txt
/* eslint-disable */

finergy.query_reports["Loan Security Status"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"reqd": 1,
			"default": finergy.defaults.get_user_default("Company")
		},
		{
			"fieldname":"applicant_type",
			"label": __("Applicant Type"),
			"fieldtype": "Select",
			"options": ["Customer", "Employee"],
			"reqd": 1,
			"default": "Customer",
			on_change: function() {
				finergy.query_report.set_filter_value('applicant', "");
			}
		},
		{
			"fieldname": "applicant",
			"label": __("Applicant"),
			"fieldtype": "Dynamic Link",
			"get_options": function() {
				var applicant_type = finergy.query_report.get_filter_value('applicant_type');
				var applicant = finergy.query_report.get_filter_value('applicant');
				if(applicant && !applicant_type) {
					finergy.throw(__("Please select Applicant Type first"));
				}
				return applicant_type;
			}
		},
		{
			"fieldname":"pledge_status",
			"label": __("Pledge Status"),
			"fieldtype": "Select",
			"options": ["", "Requested", "Pledged", "Partially Pledged", "Unpledged"],
		},
	]
};
