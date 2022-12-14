import finergy
from finergy.permissions import add_permission, update_permission_property


def execute():
	company = finergy.get_all("Company", filters={"country": "India"})
	if not company:
		return

	finergy.reload_doc("regional", "doctype", "Lower Deduction Certificate")

	add_permission("Lower Deduction Certificate", "Accounts Manager", 0)
	update_permission_property("Lower Deduction Certificate", "Accounts Manager", 0, "write", 1)
	update_permission_property("Lower Deduction Certificate", "Accounts Manager", 0, "create", 1)
