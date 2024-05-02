# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Timesheet Adjustments',
    'description':"""
    Task Id = '2779409'
    """,
    'version' : '15.0.1.0.3',
    'author': 'Odoo S.A',
    'category': 'Custom Development',
    'depends' : ['timesheet_grid', 'hr_holidays'],
    'data': [
        'views/hr_timesheet_views.xml',
    ],
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
    'assets': {
        'web.assets_backend': [
            'flyt_timesheet_grid/static/src/js/timesheet_grid/timesheet_grid_view.js',
            'flyt_timesheet_grid/static/src/js/timesheet_grid/timesheet_timer_grid_model.js',
            'flyt_timesheet_grid/static/src/js/timesheet_grid/timesheet_timer_grid_renderer.js',
            'flyt_timesheet_grid/static/src/js/timesheet_grid/timesheet_timer_grid_view.js',
            'flyt_timesheet_grid/static/src/js/widgets/timesheets_m2o_avatar_employee.js',
        ],
        'web.assets_qweb': [
            'flyt_timesheet_grid/static/src/xml/**/*',
        ],
    }
}
