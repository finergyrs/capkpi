import inspect

import finergy

__version__ = "14.0.2"


def get_default_company(user=None):
	"""Get default company for user"""
	from finergy.defaults import get_user_default_as_list

	if not user:
		user = finergy.session.user

	companies = get_user_default_as_list(user, "company")
	if companies:
		default_company = companies[0]
	else:
		default_company = finergy.db.get_single_value("Global Defaults", "default_company")

	return default_company


def get_default_currency():
	"""Returns the currency of the default company"""
	company = get_default_company()
	if company:
		return finergy.get_cached_value("Company", company, "default_currency")


def get_default_cost_center(company):
	"""Returns the default cost center of the company"""
	if not company:
		return None

	if not finergy.flags.company_cost_center:
		finergy.flags.company_cost_center = {}
	if not company in finergy.flags.company_cost_center:
		finergy.flags.company_cost_center[company] = finergy.get_cached_value(
			"Company", company, "cost_center"
		)
	return finergy.flags.company_cost_center[company]


def get_company_currency(company):
	"""Returns the default company currency"""
	if not finergy.flags.company_currency:
		finergy.flags.company_currency = {}
	if not company in finergy.flags.company_currency:
		finergy.flags.company_currency[company] = finergy.db.get_value(
			"Company", company, "default_currency", cache=True
		)
	return finergy.flags.company_currency[company]


def set_perpetual_inventory(enable=1, company=None):
	if not company:
		company = "_Test Company" if finergy.flags.in_test else get_default_company()

	company = finergy.get_doc("Company", company)
	company.enable_perpetual_inventory = enable
	company.save()


def encode_company_abbr(name, company=None, abbr=None):
	"""Returns name encoded with company abbreviation"""
	company_abbr = abbr or finergy.get_cached_value("Company", company, "abbr")
	parts = name.rsplit(" - ", 1)

	if parts[-1].lower() != company_abbr.lower():
		parts.append(company_abbr)

	return " - ".join(parts)


def is_perpetual_inventory_enabled(company):
	if not company:
		company = "_Test Company" if finergy.flags.in_test else get_default_company()

	if not hasattr(finergy.local, "enable_perpetual_inventory"):
		finergy.local.enable_perpetual_inventory = {}

	if not company in finergy.local.enable_perpetual_inventory:
		finergy.local.enable_perpetual_inventory[company] = (
			finergy.get_cached_value("Company", company, "enable_perpetual_inventory") or 0
		)

	return finergy.local.enable_perpetual_inventory[company]


def get_default_finance_book(company=None):
	if not company:
		company = get_default_company()

	if not hasattr(finergy.local, "default_finance_book"):
		finergy.local.default_finance_book = {}

	if not company in finergy.local.default_finance_book:
		finergy.local.default_finance_book[company] = finergy.get_cached_value(
			"Company", company, "default_finance_book"
		)

	return finergy.local.default_finance_book[company]


def get_party_account_type(party_type):
	if not hasattr(finergy.local, "party_account_types"):
		finergy.local.party_account_types = {}

	if not party_type in finergy.local.party_account_types:
		finergy.local.party_account_types[party_type] = (
			finergy.db.get_value("Party Type", party_type, "account_type") or ""
		)

	return finergy.local.party_account_types[party_type]


def get_region(company=None):
	"""Return the default country based on flag, company or global settings

	You can also set global company flag in `finergy.flags.company`
	"""
	if company or finergy.flags.company:
		return finergy.get_cached_value("Company", company or finergy.flags.company, "country")
	elif finergy.flags.country:
		return finergy.flags.country
	else:
		return finergy.get_system_settings("country")


def allow_regional(fn):
	"""Decorator to make a function regionally overridable

	Example:
	@capkpi.allow_regional
	def myfunction():
	  pass"""

	def caller(*args, **kwargs):
		overrides = finergy.get_hooks("regional_overrides", {}).get(get_region())
		function_path = f"{inspect.getmodule(fn).__name__}.{fn.__name__}"

		if not overrides or function_path not in overrides:
			return fn(*args, **kwargs)

		# Priority given to last installed app
		return finergy.get_attr(overrides[function_path][-1])(*args, **kwargs)

	return caller
