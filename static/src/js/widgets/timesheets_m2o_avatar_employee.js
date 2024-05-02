/** @odoo-module alias=flyt_timesheet_grid.FlytTimesheetM2OAvatarEmployee **/
import TimesheetM2OAvatarEmployee from '@timesheet_grid/js/widgets/timesheets_m2o_avatar_employee';

const FlytTimesheetM2OAvatarEmployee = TimesheetM2OAvatarEmployee.extend({
    /**
     * @returns boolean should show the hours line in red ?
     */
    _shouldShowHoursInRed() {
        var result = this._super.apply(this, arguments);
        if (moment(this.timeContext.end) > moment() && moment(this.timeContext.start) < moment()) {
            result = (this.cacheWorkedHours < this.cacheHours) && (moment(this.timeContext.end) > moment());
        }
        return result;
    },
    /**
     * @returns boolean should show the hours line
     */
    _shouldShowHours() {
        var result = this._super.apply(this, arguments);
        if (moment(this.timeContext.end) > moment() && moment(this.timeContext.start) < moment()) {
            result = this.cacheWorkedHours !== undefined && this.cacheWorkedHours != null && this.cacheWorkedHours - this.cacheHours != 0 && moment(this.timeContext.end) > moment();
        }
        return result;
    },
});

export default FlytTimesheetM2OAvatarEmployee;
