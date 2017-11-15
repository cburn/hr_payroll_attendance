# -*- coding: utf-8 -*-

import time
from datetime import datetime
from datetime import time as datetime_time

import babel

from odoo import api, fields, models, _

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        """
        @param contract: Browse record of contracts
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        res = []
        # fill only if the contract as a working schedule linked
        for contract in contracts.filtered(lambda contract: contract.resource_calendar_id):
            day_from = datetime.combine(fields.Date.from_string(date_from), datetime_time.min)
            day_to = datetime.combine(fields.Date.from_string(date_to), datetime_time.max)

            # compute leave days
            leaves = {}
            day_leave_intervals = contract.employee_id.iter_leaves(day_from, day_to, calendar=contract.resource_calendar_id)
            for day_intervals in day_leave_intervals:
                for interval in day_intervals:
                    holiday = interval[2]['leaves'].holiday_id
                    current_leave_struct = leaves.setdefault(holiday.holiday_status_id, {
                        'name': holiday.holiday_status_id.name,
                        'sequence': 5,
                        'code': holiday.holiday_status_id.code,
                        'number_of_days': 0.0,
                        'number_of_hours': 0.0,
                        'contract_id': contract.id,
                    })
                    leave_time = (interval[1] - interval[0]).seconds / 3600
                    current_leave_struct['number_of_hours'] += leave_time
                    work_hours = contract.employee_id.get_day_work_hours_count(interval[0].date(), calendar=contract.resource_calendar_id)
                    current_leave_struct['number_of_days'] += leave_time / work_hours

            # compute worked days
            work_data = contract.employee_id.get_work_days_data(day_from, day_to, calendar=contract.resource_calendar_id)
            attendances = {
                'name': _("Normal Working Days paid at 100%"),
                'sequence': 1,
                'code': 'WORK100',
                'number_of_days': work_data['days'],
                'number_of_hours': work_data['hours'],
                'contract_id': contract.id,
            }

            res.append(attendances)
            res.extend(leaves.values())

        def create_empty_worked_lines(employee_id, contract_id, date_from, date_to):
            attendance = {
                'name': 'Timesheet Attendance',
                'sequence': 10,
                'code': 'ATTN',
                'number_of_days': 0.0,
                'number_of_hours': 0.0,
                'contract_id': contract_id,
            }

            valid_days = [
                ('employee_id', '=', employee_id),
                ('check_in', '>=', date_from),
                ('check_in', '<=', date_to),
            ]
            return attendance, valid_days

        attendances = []

        for contract in contracts:
            attendance, valid_days = create_empty_worked_lines(
                contract.employee_id.id,
                contract.id,
                date_from,
                date_to
            )

            for day in self.env['hr.attendance'].search(valid_days):
                if day.worked_hours >= 0.0:
                    attendance['number_of_days'] += 1
                    attendance['number_of_hours'] += day.worked_hours

            # needed so that the shown hours matches any calculations you use them for
            attendance['number_of_hours'] = round(attendance['number_of_hours'], 2)
            res.append(attendance)

        return res
