# Copyright (c) 2015, Finergy Reporting Solutions SAS and Contributors
# License: GNU General Public License v3. See license.txt


import json

import finergy
from finergy import _, throw
from finergy.desk.form.assign_to import clear, close_all_assignments
from finergy.model.mapper import get_mapped_doc
from finergy.utils import add_days, cstr, date_diff, flt, get_link_to_form, getdate, today
from finergy.utils.nestedset import NestedSet


class CircularReferenceError(finergy.ValidationError):
	pass


class EndDateCannotBeGreaterThanProjectEndDateError(finergy.ValidationError):
	pass


class Task(NestedSet):
	nsm_parent_field = "parent_task"

	def get_feed(self):
		return "{0}: {1}".format(_(self.status), self.subject)

	def get_customer_details(self):
		cust = finergy.db.sql("select customer_name from `tabCustomer` where name=%s", self.customer)
		if cust:
			ret = {"customer_name": cust and cust[0][0] or ""}
			return ret

	def validate(self):
		self.validate_dates()
		self.validate_parent_expected_end_date()
		self.validate_parent_project_dates()
		self.validate_progress()
		self.validate_status()
		self.update_depends_on()
		self.validate_dependencies_for_template_task()
		self.validate_completed_on()

	def validate_dates(self):
		if (
			self.exp_start_date
			and self.exp_end_date
			and getdate(self.exp_start_date) > getdate(self.exp_end_date)
		):
			finergy.throw(
				_("{0} can not be greater than {1}").format(
					finergy.bold("Expected Start Date"), finergy.bold("Expected End Date")
				)
			)

		if (
			self.act_start_date
			and self.act_end_date
			and getdate(self.act_start_date) > getdate(self.act_end_date)
		):
			finergy.throw(
				_("{0} can not be greater than {1}").format(
					finergy.bold("Actual Start Date"), finergy.bold("Actual End Date")
				)
			)

	def validate_parent_expected_end_date(self):
		if self.parent_task:
			parent_exp_end_date = finergy.db.get_value("Task", self.parent_task, "exp_end_date")
			if parent_exp_end_date and getdate(self.get("exp_end_date")) > getdate(parent_exp_end_date):
				finergy.throw(
					_(
						"Expected End Date should be less than or equal to parent task's Expected End Date {0}."
					).format(getdate(parent_exp_end_date))
				)

	def validate_parent_project_dates(self):
		if not self.project or finergy.flags.in_test:
			return

		expected_end_date = finergy.db.get_value("Project", self.project, "expected_end_date")

		if expected_end_date:
			validate_project_dates(
				getdate(expected_end_date), self, "exp_start_date", "exp_end_date", "Expected"
			)
			validate_project_dates(
				getdate(expected_end_date), self, "act_start_date", "act_end_date", "Actual"
			)

	def validate_status(self):
		if self.is_template and self.status != "Template":
			self.status = "Template"
		if self.status != self.get_db_value("status") and self.status == "Completed":
			for d in self.depends_on:
				if finergy.db.get_value("Task", d.task, "status") not in ("Completed", "Cancelled"):
					finergy.throw(
						_(
							"Cannot complete task {0} as its dependant task {1} are not ccompleted / cancelled."
						).format(finergy.bold(self.name), finergy.bold(d.task))
					)

			close_all_assignments(self.doctype, self.name)

	def validate_progress(self):
		if flt(self.progress or 0) > 100:
			finergy.throw(_("Progress % for a task cannot be more than 100."))

		if self.status == "Completed":
			self.progress = 100

	def validate_dependencies_for_template_task(self):
		if self.is_template:
			self.validate_parent_template_task()
			self.validate_depends_on_tasks()

	def validate_parent_template_task(self):
		if self.parent_task:
			if not finergy.db.get_value("Task", self.parent_task, "is_template"):
				parent_task_format = """<a href="#Form/Task/{0}">{0}</a>""".format(self.parent_task)
				finergy.throw(_("Parent Task {0} is not a Template Task").format(parent_task_format))

	def validate_depends_on_tasks(self):
		if self.depends_on:
			for task in self.depends_on:
				if not finergy.db.get_value("Task", task.task, "is_template"):
					dependent_task_format = """<a href="#Form/Task/{0}">{0}</a>""".format(task.task)
					finergy.throw(_("Dependent Task {0} is not a Template Task").format(dependent_task_format))

	def validate_completed_on(self):
		if self.completed_on and getdate(self.completed_on) > getdate():
			finergy.throw(_("Completed On cannot be greater than Today"))

	def update_depends_on(self):
		depends_on_tasks = ""
		for d in self.depends_on:
			if d.task and d.task not in depends_on_tasks:
				depends_on_tasks += d.task + ","
		self.depends_on_tasks = depends_on_tasks

	def update_nsm_model(self):
		finergy.utils.nestedset.update_nsm(self)

	def on_update(self):
		self.update_nsm_model()
		self.check_recursion()
		self.reschedule_dependent_tasks()
		self.update_project()
		self.unassign_todo()
		self.populate_depends_on()

	def unassign_todo(self):
		if self.status == "Completed":
			close_all_assignments(self.doctype, self.name)
		if self.status == "Cancelled":
			clear(self.doctype, self.name)

	def update_time_and_costing(self):
		tl = finergy.db.sql(
			"""select min(from_time) as start_date, max(to_time) as end_date,
			sum(billing_amount) as total_billing_amount, sum(costing_amount) as total_costing_amount,
			sum(hours) as time from `tabTimesheet Detail` where task = %s and docstatus=1""",
			self.name,
			as_dict=1,
		)[0]
		if self.status == "Open":
			self.status = "Working"
		self.total_costing_amount = tl.total_costing_amount
		self.total_billing_amount = tl.total_billing_amount
		self.actual_time = tl.time
		self.act_start_date = tl.start_date
		self.act_end_date = tl.end_date

	def update_project(self):
		if self.project and not self.flags.from_project:
			finergy.get_cached_doc("Project", self.project).update_project()

	def check_recursion(self):
		if self.flags.ignore_recursion_check:
			return
		check_list = [["task", "parent"], ["parent", "task"]]
		for d in check_list:
			task_list, count = [self.name], 0
			while len(task_list) > count:
				tasks = finergy.db.sql(
					" select %s from `tabTask Depends On` where %s = %s " % (d[0], d[1], "%s"),
					cstr(task_list[count]),
				)
				count = count + 1
				for b in tasks:
					if b[0] == self.name:
						finergy.throw(_("Circular Reference Error"), CircularReferenceError)
					if b[0]:
						task_list.append(b[0])

				if count == 15:
					break

	def reschedule_dependent_tasks(self):
		end_date = self.exp_end_date or self.act_end_date
		if end_date:
			for task_name in finergy.db.sql(
				"""
				select name from `tabTask` as parent
				where parent.project = %(project)s
					and parent.name in (
						select parent from `tabTask Depends On` as child
						where child.task = %(task)s and child.project = %(project)s)
			""",
				{"project": self.project, "task": self.name},
				as_dict=1,
			):
				task = finergy.get_doc("Task", task_name.name)
				if (
					task.exp_start_date
					and task.exp_end_date
					and task.exp_start_date < getdate(end_date)
					and task.status == "Open"
				):
					task_duration = date_diff(task.exp_end_date, task.exp_start_date)
					task.exp_start_date = add_days(end_date, 1)
					task.exp_end_date = add_days(task.exp_start_date, task_duration)
					task.flags.ignore_recursion_check = True
					task.save()

	def has_webform_permission(self):
		project_user = finergy.db.get_value(
			"Project User", {"parent": self.project, "user": finergy.session.user}, "user"
		)
		if project_user:
			return True

	def populate_depends_on(self):
		if self.parent_task:
			parent = finergy.get_doc("Task", self.parent_task)
			if self.name not in [row.task for row in parent.depends_on]:
				parent.append(
					"depends_on", {"doctype": "Task Depends On", "task": self.name, "subject": self.subject}
				)
				parent.save()

	def on_trash(self):
		if check_if_child_exists(self.name):
			throw(_("Child Task exists for this Task. You can not delete this Task."))

		self.update_nsm_model()

	def after_delete(self):
		self.update_project()

	def update_status(self):
		if self.status not in ("Cancelled", "Completed") and self.exp_end_date:
			from datetime import datetime

			if self.exp_end_date < datetime.now().date():
				self.db_set("status", "Overdue", update_modified=False)
				self.update_project()


@finergy.whitelist()
def check_if_child_exists(name):
	child_tasks = finergy.get_all("Task", filters={"parent_task": name})
	child_tasks = [get_link_to_form("Task", task.name) for task in child_tasks]
	return child_tasks


@finergy.whitelist()
@finergy.validate_and_sanitize_search_inputs
def get_project(doctype, txt, searchfield, start, page_len, filters):
	from capkpi.controllers.queries import get_match_cond

	meta = finergy.get_meta(doctype)
	searchfields = meta.get_search_fields()
	search_columns = ", " + ", ".join(searchfields) if searchfields else ""
	search_cond = " or " + " or ".join(field + " like %(txt)s" for field in searchfields)

	return finergy.db.sql(
		""" select name {search_columns} from `tabProject`
		where %(key)s like %(txt)s
			%(mcond)s
			{search_condition}
		order by name
		limit %(page_len)s offset %(start)s""".format(
			search_columns=search_columns, search_condition=search_cond
		),
		{
			"key": searchfield,
			"txt": "%" + txt + "%",
			"mcond": get_match_cond(doctype),
			"start": start,
			"page_len": page_len,
		},
	)


@finergy.whitelist()
def set_multiple_status(names, status):
	names = json.loads(names)
	for name in names:
		task = finergy.get_doc("Task", name)
		task.status = status
		task.save()


def set_tasks_as_overdue():
	tasks = finergy.get_all(
		"Task",
		filters={"status": ["not in", ["Cancelled", "Completed"]]},
		fields=["name", "status", "review_date"],
	)
	for task in tasks:
		if task.status == "Pending Review":
			if getdate(task.review_date) > getdate(today()):
				continue
		finergy.get_doc("Task", task.name).update_status()


@finergy.whitelist()
def make_timesheet(source_name, target_doc=None, ignore_permissions=False):
	def set_missing_values(source, target):
		target.append(
			"time_logs",
			{
				"hours": source.actual_time,
				"completed": source.status == "Completed",
				"project": source.project,
				"task": source.name,
			},
		)

	doclist = get_mapped_doc(
		"Task",
		source_name,
		{"Task": {"doctype": "Timesheet"}},
		target_doc,
		postprocess=set_missing_values,
		ignore_permissions=ignore_permissions,
	)

	return doclist


@finergy.whitelist()
def get_children(doctype, parent, task=None, project=None, is_root=False):

	filters = [["docstatus", "<", "2"]]

	if task:
		filters.append(["parent_task", "=", task])
	elif parent and not is_root:
		# via expand child
		filters.append(["parent_task", "=", parent])
	else:
		filters.append(['ifnull(`parent_task`, "")', "=", ""])

	if project:
		filters.append(["project", "=", project])

	tasks = finergy.get_list(
		doctype,
		fields=["name as value", "subject as title", "is_group as expandable"],
		filters=filters,
		order_by="name",
	)

	# return tasks
	return tasks


@finergy.whitelist()
def add_node():
	from finergy.desk.treeview import make_tree_args

	args = finergy.form_dict
	args.update({"name_field": "subject"})
	args = make_tree_args(**args)

	if args.parent_task == "All Tasks" or args.parent_task == args.project:
		args.parent_task = None

	finergy.get_doc(args).insert()


@finergy.whitelist()
def add_multiple_tasks(data, parent):
	data = json.loads(data)
	new_doc = {"doctype": "Task", "parent_task": parent if parent != "All Tasks" else ""}
	new_doc["project"] = finergy.db.get_value("Task", {"name": parent}, "project") or ""

	for d in data:
		if not d.get("subject"):
			continue
		new_doc["subject"] = d.get("subject")
		new_task = finergy.get_doc(new_doc)
		new_task.insert()


def on_doctype_update():
	finergy.db.add_index("Task", ["lft", "rgt"])


def validate_project_dates(project_end_date, task, task_start, task_end, actual_or_expected_date):
	if task.get(task_start) and date_diff(project_end_date, getdate(task.get(task_start))) < 0:
		finergy.throw(
			_("Task's {0} Start Date cannot be after Project's End Date.").format(actual_or_expected_date)
		)

	if task.get(task_end) and date_diff(project_end_date, getdate(task.get(task_end))) < 0:
		finergy.throw(
			_("Task's {0} End Date cannot be after Project's End Date.").format(actual_or_expected_date)
		)
