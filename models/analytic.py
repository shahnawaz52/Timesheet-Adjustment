# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import pytz
from datetime import datetime, timedelta, time
import collections
from collections import defaultdict
from odoo import fields, models, api, _
from odoo.addons.resource.models.resource import make_aware
from odoo.exceptions import AccessError

ColumnMetadata = collections.namedtuple('ColumnMetadata', 'grouping domain prev next initial values format')


class AnalyticLine(models.Model):
    _name = 'account.analytic.line'
    _inherit = ['account.analytic.line', 'mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2one(tracking=True)
    unit_amount = fields.Float('Hours Spent')
    unit_amount_string = fields.Char(tracking=True, store=True, compute='_compute_unit_amount')

    @api.depends('unit_amount')
    def _compute_unit_amount(self):
        for rec in self:
            if rec.unit_amount:
                rec.unit_amount_string = str('{0:02.0f}:{1:02.0f}'.format(*divmod(rec.unit_amount * 60, 60)))

    def _mail_track(self, tracked_fields, initial):
        changes, tracking_value_ids = super()._mail_track(tracked_fields, initial)
        if tracking_value_ids and tracking_value_ids[0][2].get('field_desc') == 'Unit Amount String':
            tracking_value_ids[0][2].update({'field_desc': 'Hours Spent'})
        return changes, tracking_value_ids

    def _action_open_to_validate_timesheet_view(self, type_view='week'):
        action = super(AnalyticLine, self)._action_open_to_validate_timesheet_view(type_view)
        if (type_view == 'current week'):
            action['context'].update({
                'grid_anchor': fields.Date.today()
            })
        return action

    @api.model_create_multi
    def create(self, vals_list):
        if self._context.get('non_working_day'):
            Task = self.env['project.task']
            for val_list in vals_list:
                task_id = val_list.get('task_id')
                if task_id:
                    task = Task.browse(task_id)
                    if val_list.get('global_leave_id'):
                        raise AccessError(_("You can not create timesheet for the non-working day."))
        return super().create(vals_list)

    def adjust_grid(self, row_domain, column_field, column_value, cell_field, change):
        return super(AnalyticLine, self.with_context(flyt_adjust_grid=True)).adjust_grid(row_domain, column_field, column_value, cell_field, change)

    def write(self, values):
        res = super(AnalyticLine, self).write(values)
        all_leave_timesheets = self.filtered(lambda t: t.task_id.leave_ids)
        global_leave_timesheets = all_leave_timesheets.filtered(lambda t: t.global_leave_id)
        regular_leave_timesheets = all_leave_timesheets - global_leave_timesheets
        if self._context.get('flyt_adjust_grid') and global_leave_timesheets:
            raise AccessError(_("You can not add/modify timesheet for the '%s' Task." %
                global_leave_timesheets[0].task_id.display_name))
        elif not self._context.get('non_working_day') and regular_leave_timesheets:
            if 'date' in values or 'employee_id' in values or 'unit_amount' in values:
                raise AccessError(_("You can not add/modify timesheet for the non-working day."))
            elif 'amount' in values:
                raise AccessError(_("You can not add/modify timesheet for the '%s' Task." %
                    regular_leave_timesheets[0].task_id.display_name))
        # If User wants to restrict modifications for unavailable days then comment out below code
        # else:
        #     for timesheet in (self - all_leave_timesheets):
        #         unavailable_days = self._get_unavailable_dates(timesheet.date, timesheet.date)
        #         if unavailable_days:
        #             raise AccessError(_("You can not add/modify timesheet for the non-working day."))
        return res

    @api.model
    def read_grid(self, row_fields, col_field, cell_field, domain=None, range=None, readonly_field=None, orderby=None):        
        result = super(AnalyticLine, self.with_context(date_domain=domain)).read_grid(row_fields, col_field, cell_field, domain, range, readonly_field, orderby)
        print('--------domain--------->>>>', domain)
        time = self.search(domain)
        # domain_search = []
        # for rule in domain:
        #     if len(rule) == 3 and rule[0] == 'date':
        #         name, operator, _rule = rule
        #         print('--------rule------', name, operator, _rule)
              
        # for t in time:
        #     print('------------time----', t.unit_amount)
        Timesheet = self.env['account.analytic.line']
        for grid in result['grid']:
            for value in grid:
                timesheets = self.search(value['domain']) if value and value.get('domain') else Timesheet
                for timesheet in timesheets.filtered(lambda t: t.task_id.leave_ids):
                    value.update({'unit_amount': timesheet.unit_amount})
        return result

    def _grid_column_info(self, name, range):        
        if not range:
            range = {}
        field = self._fields[name]
        context_anchor = self.env.context.get('grid_anchor')
        if field.type == 'date':
            # seemingly sane defaults
            step = range.get('step', 'day')
            span = range.get('span', 'month')

            today = anchor = field.from_string(field.context_today(self))
            if context_anchor:
                anchor = field.from_string(context_anchor)

            r = self._grid_range_of(span, step, anchor, field)
            dates = [d for d in r.iter(step)]
            pagination = self._grid_pagination(field, span, step, anchor)

            #TODO: Find a way to update collection namedtuple dictionary inside values list
            return ColumnMetadata(
                grouping='{}:{}'.format(name, step),
                domain=[
                    '&',
                    (name, '>=', field.to_string(r.start)),
                    (name, '<=', field.to_string(r.end))
                ],
                prev=pagination.get('prev'),
                next=pagination.get('next'),
                initial=pagination.get('initial'),
                values=[{
                        'values': {
                            name: self._get_date_column_label(d, field, span, step)
                        },
                        'domain': ['&',
                                   (name, '>=', field.to_string(d)),
                                   (name, '<', field.to_string(d + self._grid_step_by(step)))],
                        'is_current': self._grid_date_is_current(field, span, step, d),
                        'is_unavailable': self._grid_datetime_is_unavailable(field, span, step, d),
                        'is_unavailable_half_day': self._grid_datetime_is_unavailable_half_day(field, span, step, d, dates),
                        'planned_hours': self.expected_planned_hours(field, span, step, d, dates),
                        'timesheet_column_date': d,
                    } for d in r.iter(step)
                ],
                format=lambda a: a and a[0],
            )
        elif field.type == 'datetime':
            # seemingly sane defaults
            step = range.get('step', 'day')
            span = range.get('span', 'month')

            anchor = field.from_string(field.today(self))
            if context_anchor:
                anchor = field.from_string(context_anchor)

            r = self._grid_range_of(span, step, anchor, field)
            dates = [d for d in r.iter()]
            pagination = self._grid_pagination(field, span, step, anchor)

            #TODO: Find a way to update collection namedtuple dictionary inside values list
            return ColumnMetadata(
                grouping='{}:{}'.format(name, step),
                domain=[
                    '&',
                    (name, '>=', r.start_utc),
                    (name, '<=', r.end_utc)
                ],
                prev=pagination.get('prev'),
                next=pagination.get('next'),
                initial=pagination.get('initial'),
                values=[{
                        'values': {
                            name: self._get_date_column_label(d[0], field, span, step)
                        },
                        'domain': ['&',
                                   (name, '>=', field.to_string(d[0])),
                                   (name, '<', field.to_string(d[1]))],
                        'is_current': self._grid_datetime_is_current(field, span, step, d),
                        'is_unavailable': self._grid_datetime_is_unavailable(field, span, step, d),
                        'is_unavailable_half_day': self._grid_datetime_is_unavailable_half_day(field, span, step, d, dates),
                        'planned_hours': self.expected_planned_hours(field, span, step, d, dates),
                        'timesheet_column_date': d,
                        } for d in r.iter()],
                format=lambda a: a and a[0],
            )
        return super()._grid_column_info(name, range)

    def expected_planned_hours(self, field, span, step, column_dates, date_list):
        calendar = self.env.user.employee_id.resource_calendar_id or self.env.company.resource_calendar_id
        date_from = datetime.combine(fields.Date.from_string(min(date_list)), time.min)
        date_to = datetime.combine(fields.Date.from_string(max(date_list)), time.max).strftime('%Y-%m-%d %H:%M:%S')
        time_off_leaves = self.env['hr.leave'].search([
            ('employee_id', '=', self.env.user.employee_id.id),
            ('date_from', '<=', date_to),
            ('date_to', '>=', date_from),
            ('state', '=', 'validate')
        ])

        expected_hours = []
        res = {}
        date_domain = self.env.context.get('date_domain', False)
        # print('--------<<<<date_domain--->>>', date_domain)


        datetime_min = datetime.combine(fields.Date.from_string(min(date_list)), time.min).replace(tzinfo=pytz.UTC)
        datetime_max = datetime.combine(fields.Date.from_string(max(date_list)), time.max).replace(tzinfo=pytz.UTC)
        intervals = calendar._work_intervals_batch(datetime_min, datetime_max)[False]
        result = defaultdict(float)
        for start, stop, meta in intervals:
            result[str(start.date())] += (stop - start).total_seconds() / 3600

        for index, date in enumerate(result):
            working_data = dict(result)
            if date == str(column_dates):
                expected_hours.append([date, working_data[date]])

        for leave in time_off_leaves.mapped('timesheet_ids'):
            for data in expected_hours:
                if data and str(leave.date) == data[0]:
                    data[1] -= leave.unit_amount

        for data in expected_hours:
            # print('-----------rule-------', rule[0])
            for rule in date_domain:
            #     if len(rule) == 1 or len(rule) == 3:
            #         if len(rule) == 3 and rule[0] == 'date': 
            #             name, operator, _rule = rule
            #             print('-------tle-------', name, operator, _rule)
            #             if operator == '=':
            #                 if _rule != data[0]:
            #                     data[1] = 0

                if len(rule) == 3 and rule[0] == 'date':
                    name, operator, _rule = rule
                    if operator == '>':
                        print('---inside: > ')
                        if _rule >= data[0]:
                            data[1] = 0
                    if operator == '=':
                        if _rule != data[0]:
                            data[1] = 0
                    if operator == '!=':
                        print('---inside: != ')
                        if _rule == data[0]:
                            data[1] = 0
                    if operator == '<':
                        print('---inside: < ')
                        if _rule <= data[0]:
                            data[1] = 0
                    if operator == '>=':
                        print('---inside: >= ')
                        if _rule > data[0]:
                            data[1] = 0
                    if operator == '<=':
                        print('---inside: <= ')
                        if _rule < data[0]:
                            data[1] = 0

                    # for n in range(4, len(date_domain)):
                    #     # print('-------n----->>>>', len(date_domain[n]))
                    #     if date_domain[n] == '|':
                    #         print('------name---------', name, operator, _rule)
                    #         if operator == '=':
                    #             print('------between-------------')
                    #             if _rule != data[0]:
                    #                 print('---------------data[1]--->>>', _rule, data[0])
                    #                 data[1] = 0

        # print('-----------expected-------->>>', expected_hours)
        return expected_hours

    def _grid_datetime_is_unavailable_half_day(self, field, span, step, column_dates, date_list):
        """
            :param column_dates: tuple of start/stop dates of a grid column, timezoned in UTC
        """
        calendar = self.env.user.employee_id.resource_calendar_id
        date_from = datetime.strptime(str(min(date_list)), '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
        date_to = datetime.strptime(str(max(date_list)), '%Y-%m-%d').strftime('%Y-%m-%d %H:%M:%S')
        unassigned_leaves = self.env['resource.calendar.leaves'].search([
            ('calendar_id', '=', False),
            ('date_from', '<=', date_to),
            ('date_to', '>=', date_from),
            ('company_id', '=', self.env.company.id)
        ])

        global_leaves = self.env.company.resource_calendar_id.global_leave_ids | unassigned_leaves
        hours_per_day = self.env.company.resource_calendar_id.hours_per_day
        if calendar:
            global_leaves = calendar.global_leave_ids | unassigned_leaves
            hours_per_day = calendar.hours_per_day

        unavailable_days = set()
        time_off_leaves = self.env['hr.leave'].search([
            ('employee_id', '=', self.env.user.employee_id.id),
            ('date_from', '<=', date_to),
            ('date_to', '>=', date_from),
            ('state', '=', 'validate')
        ])

        for leave in time_off_leaves.mapped('timesheet_ids'):
            if leave or leave.unit_amount < hours_per_day:
                unavailable_days.add(leave.date)

        work_hours_data = calendar.global_leave_ids._work_time_per_day()
        public_leaves = global_leaves.filtered(lambda l: str(l.date_from) <= date_to and str(l.date_to) >= date_from)

        for leave in public_leaves:
            for index, (day_date, work_hours_count) in enumerate(work_hours_data[leave.id]):
                if leave or work_hours_count < hours_per_day:
                    unavailable_days.add(leave.date_from.date())

        if unavailable_days and column_dates in unavailable_days:
            return True

    def _get_unavailable_dates(self, start_date, end_date):
        """
        Returns the list of days when the current company is closed (we, or holidays)
        """
        unavailable_days = super()._get_unavailable_dates(start_date, end_date)
        calendar = self.env.user.employee_id.resource_calendar_id
        if not calendar:
            return unavailable_days
        start_dt = datetime(year=start_date.year, month=start_date.month, day=start_date.day)
        end_dt = datetime(year=end_date.year, month=end_date.month, day=end_date.day, hour=23, minute=59, second=59)
        # naive datetimes are made explicit in UTC
        from_datetime, dummy = make_aware(start_dt)
        to_datetime, dummy = make_aware(end_dt)
        # We need to display in grey the unavailable full days
        # We start by getting the availability intervals to avoid false positive with range outside the office hours
        items = calendar._work_intervals_batch(from_datetime, to_datetime)[False]
        # get the dates where some work can be done in the interval. It returns a list of sets.
        available_dates = list(map(lambda item: {item[0].date(), item[1].date()}, items))
        avaibilities = [date for dates in available_dates for date in dates]
        unavailable_days = []
        cur_day = from_datetime
        while cur_day <= to_datetime:
            if not cur_day.date() in avaibilities:
                unavailable_days.append(cur_day.date())
            cur_day = cur_day + timedelta(days=1)
        return set(unavailable_days)
