# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class Holidays(models.Model):
    _inherit = "hr.leave"

    def _validate_leave_request(self):
        return super(Holidays, self.with_context(non_working_day=True))._validate_leave_request()
