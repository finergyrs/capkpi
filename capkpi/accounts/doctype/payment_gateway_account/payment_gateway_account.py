# Copyright (c) 2015, Finergy Reporting Solutions SAS and contributors
# For license information, please see license.txt


import finergy
from finergy.model.document import Document


class PaymentGatewayAccount(Document):
	def autoname(self):
		self.name = self.payment_gateway + " - " + self.currency

	def validate(self):
		self.currency = finergy.db.get_value("Account", self.payment_account, "account_currency")

		self.update_default_payment_gateway()
		self.set_as_default_if_not_set()

	def update_default_payment_gateway(self):
		if self.is_default:
			finergy.db.sql(
				"""update `tabPayment Gateway Account` set is_default = 0
				where is_default = 1 """
			)

	def set_as_default_if_not_set(self):
		if not finergy.db.get_value(
			"Payment Gateway Account", {"is_default": 1, "name": ("!=", self.name)}, "name"
		):
			self.is_default = 1
