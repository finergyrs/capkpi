# Copyright (c) 2019, Finergy Reporting Solutions SAS and contributors
# For license information, please see license.txt


import finergy
from finergy import _
from finergy.core.doctype.communication.email import make
from finergy.model.document import Document
from finergy.utils import add_days, getdate, today


class EmailCampaign(Document):
	def validate(self):
		self.set_date()
		# checking if email is set for lead. Not checking for contact as email is a mandatory field for contact.
		if self.email_campaign_for == "Lead":
			self.validate_lead()
		self.validate_email_campaign_already_exists()
		self.update_status()

	def set_date(self):
		if getdate(self.start_date) < getdate(today()):
			finergy.throw(_("Start Date cannot be before the current date"))
		# set the end date as start date + max(send after days) in campaign schedule
		send_after_days = []
		campaign = finergy.get_doc("Campaign", self.campaign_name)
		for entry in campaign.get("campaign_schedules"):
			send_after_days.append(entry.send_after_days)
		try:
			self.end_date = add_days(getdate(self.start_date), max(send_after_days))
		except ValueError:
			finergy.throw(
				_("Please set up the Campaign Schedule in the Campaign {0}").format(self.campaign_name)
			)

	def validate_lead(self):
		lead_email_id = finergy.db.get_value("Lead", self.recipient, "email_id")
		if not lead_email_id:
			lead_name = finergy.db.get_value("Lead", self.recipient, "lead_name")
			finergy.throw(_("Please set an email id for the Lead {0}").format(lead_name))

	def validate_email_campaign_already_exists(self):
		email_campaign_exists = finergy.db.exists(
			"Email Campaign",
			{
				"campaign_name": self.campaign_name,
				"recipient": self.recipient,
				"status": ("in", ["In Progress", "Scheduled"]),
				"name": ("!=", self.name),
			},
		)
		if email_campaign_exists:
			finergy.throw(
				_("The Campaign '{0}' already exists for the {1} '{2}'").format(
					self.campaign_name, self.email_campaign_for, self.recipient
				)
			)

	def update_status(self):
		start_date = getdate(self.start_date)
		end_date = getdate(self.end_date)
		today_date = getdate(today())
		if start_date > today_date:
			self.status = "Scheduled"
		elif end_date >= today_date:
			self.status = "In Progress"
		elif end_date < today_date:
			self.status = "Completed"


# called through hooks to send campaign mails to leads
def send_email_to_leads_or_contacts():
	email_campaigns = finergy.get_all(
		"Email Campaign", filters={"status": ("not in", ["Unsubscribed", "Completed", "Scheduled"])}
	)
	for camp in email_campaigns:
		email_campaign = finergy.get_doc("Email Campaign", camp.name)
		campaign = finergy.get_cached_doc("Campaign", email_campaign.campaign_name)
		for entry in campaign.get("campaign_schedules"):
			scheduled_date = add_days(email_campaign.get("start_date"), entry.get("send_after_days"))
			if scheduled_date == getdate(today()):
				send_mail(entry, email_campaign)


def send_mail(entry, email_campaign):
	recipient_list = []
	if email_campaign.email_campaign_for == "Email Group":
		for member in finergy.db.get_list(
			"Email Group Member", filters={"email_group": email_campaign.get("recipient")}, fields=["email"]
		):
			recipient_list.append(member["email"])
	else:
		recipient_list.append(
			finergy.db.get_value(
				email_campaign.email_campaign_for, email_campaign.get("recipient"), "email_id"
			)
		)

	email_template = finergy.get_doc("Email Template", entry.get("email_template"))
	sender = finergy.db.get_value("User", email_campaign.get("sender"), "email")
	context = {"doc": finergy.get_doc(email_campaign.email_campaign_for, email_campaign.recipient)}
	# send mail and link communication to document
	comm = make(
		doctype="Email Campaign",
		name=email_campaign.name,
		subject=finergy.render_template(email_template.get("subject"), context),
		content=finergy.render_template(email_template.get("response"), context),
		sender=sender,
		recipients=recipient_list,
		communication_medium="Email",
		sent_or_received="Sent",
		send_email=True,
		email_template=email_template.name,
	)
	return comm


# called from hooks on doc_event Email Unsubscribe
def unsubscribe_recipient(unsubscribe, method):
	if unsubscribe.reference_doctype == "Email Campaign":
		finergy.db.set_value("Email Campaign", unsubscribe.reference_name, "status", "Unsubscribed")


# called through hooks to update email campaign status daily
def set_email_campaign_status():
	email_campaigns = finergy.get_all("Email Campaign", filters={"status": ("!=", "Unsubscribed")})
	for entry in email_campaigns:
		email_campaign = finergy.get_doc("Email Campaign", entry.name)
		email_campaign.update_status()
