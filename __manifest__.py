# -*- coding: utf-8 -*-
{
    'name': "hr_payroll_attendance",

    'summary': """
        Add Attendance to Payslips""",

    'description': """
        When creating payslips, this finds all attendance records with in the payslip
        dates and adds the days worked and hours worked to the payslip.

        Also adds a 'payroll code' to the holiday types, so you can calculate pay on leaves using 'worked_days.PAYROLL_CODE'.
    """,

    'author': "Chris Burn",
    'category': 'Human Resources',
    'version': '0.1',

    'depends': [
        'base',
        'hr_payroll',
        'hr_attendance',
    ],

    'data': [
        'views/hr_holidays_status.xml',
    ],
}
