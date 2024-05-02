# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class Task(models.Model):
    _inherit = "project.task"

    leave_ids = fields.One2many('hr.leave.type', 'timesheet_task_id', 'Time Off')
