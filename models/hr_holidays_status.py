# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HolidaysType(models.Model):
    _inherit = 'hr.holidays.status'

    code = fields.Char('Payroll Code', required=True, translate=True, default='LEAVE')
