odoo.define('flyt_timesheet_grid.GridView', function (require) {
    "use strict";

    const viewRegistry = require('web.view_registry');
    const { ComponentAdapter } = require('web.OwlCompatibility');
    const TimesheetGridView = require('timesheet_grid.GridView');
    const TimesheetGridRenderer = require('timesheet_grid.GridRenderer');
    const FlytTimesheetM2OAvatarEmployee = require('flyt_timesheet_grid.FlytTimesheetM2OAvatarEmployee');


    class FlytTimesheetGridRenderer extends TimesheetGridRenderer {
        constructor() {
            super(...arguments);
            this.widgetComponents = Object.assign({}, this.widgetComponents, {
                FlytTimesheetM2OAvatarEmployee: FlytTimesheetM2OAvatarEmployee
            })
        }
    }

    const FlytTimesheetGridView = TimesheetGridView.extend({
        config: _.extend({}, TimesheetGridView.prototype.config, {
            Renderer: FlytTimesheetGridRenderer,
        })
    });

    viewRegistry.add('flyt_timesheet_m2o_avatar_widget', FlytTimesheetGridView);

    return FlytTimesheetGridView;
});
