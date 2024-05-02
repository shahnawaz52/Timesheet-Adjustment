odoo.define('flyt_timesheet_grid.TimerGridView', function (require) {
    "use strict";

    const viewRegistry = require('web.view_registry');
    const TimerGridView = require('timesheet_grid.TimerGridView');
    const FlytTimerGridModel = require('flyt_timesheet_grid.TimerGridModel');
    const FlytTimerGridRenderer = require('flyt_timesheet_grid.TimerGridRenderer');

    const FlytTimerGridView = TimerGridView.extend({
        config: _.extend({}, TimerGridView.prototype.config, {
            Model: FlytTimerGridModel,
            Renderer: FlytTimerGridRenderer,
        })
    });

    viewRegistry.add('flyt_timesheet_timer_grid', FlytTimerGridView);

    return FlytTimerGridView;
});
