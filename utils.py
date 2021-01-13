from __future__ import unicode_literals
import frappe, erpnext
from frappe import _
from frappe.utils import formatdate, format_datetime, getdate, get_datetime, nowdate, flt, cstr, add_days, today
from frappe.model.document import Document
from frappe.desk.form import assign_to
from erpnext.hr.doctype.employee.employee import get_holiday_list_for_employee

from erpnext.hr.utils import (get_earned_leaves  ,
								get_leave_allocations,
								update_previous_leave_allocation ,
								check_effective_date ,
								create_additional_leave_ledger_entry)
from dateutil.relativedelta import relativedelta
@frappe.whitelist()
def allocate_earned_leaves():
	
	'''Allocate earned leaves to Employees'''
	today = getdate()
	e_leave_types = get_earned_leaves()
	for e_leave_type in e_leave_types:

		leave_allocations = get_leave_allocations(today, e_leave_type.name)

		for allocation in leave_allocations:
			

			leave_policy = allocation.leave_policy if allocation.leave_policy else frappe.db.get_value(
					"Leave Policy Assignment", allocation.leave_policy_assignment, ["leave_policy"])
			#for testing we add annual allocation is static componant 
			annual_allocation = 30
			from_date=allocation.from_date
			joining_date  = frappe.db.get_value("Employee", allocation.employee, "date_of_joining")
			
			if e_leave_type.based_on_date_of_joining_date:
				from_date  = joining_date
			if joining_date+relativedelta(years=5) >= today and e_leave_type.earned_leave_frequency == 'Monthly' :
				if check_effective_date(from_date, today, e_leave_type.earned_leave_frequency, e_leave_type.based_on_date_of_joining_date):
					update_previous_leave_allocation(allocation, annual_allocation, e_leave_type)

