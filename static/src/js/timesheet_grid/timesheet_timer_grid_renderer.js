odoo.define('flyt_timesheet_grid.TimerGridRenderer', function (require) {
    "use strict";

    const TimerGridRenderer = require('timesheet_grid.TimerGridRenderer');

    class FlytTimerGridRenderer extends TimerGridRenderer {
        constructor(parent, props) {
            super(...arguments);
        }
        /**
         * Get the information needed to display the total expected hours of a grid
         *
         * @returns {number}
         */
        get gridTotalHours() {
            var columns = _.size(this.props.data[0].cols);
            var total = 0;
            for (var i=0; i<columns; i++) {
                if (!this.props.data[0].cols[i].is_unavailable) {
                    total += this.props.data[0].cols[i].planned_hours[0][1];
                }
            }
            return total;
        }
        /**
         * Get the information needed to display the total delta hours of a grid
         *
         * @returns {number}
         */
        get gridDeltaTotalHours() {
            var columns = _.size(this.props.data[0].cols);
            var total = 0;
            for (var i=0; i<columns; i++) {
                if (this.props.data[0].cols[i].is_unavailable_half_day && this.props.totals.columns[i]) {
                    total += this.props.totals.leave_columns[i];
                }
            }
            return total;
        }

        //----------------------------------------------------------------------
        // Private
        //----------------------------------------------------------------------

        /**
         * @private
         * @param {integer} index
         * @returns {date, date, value: number}
         */
        _getWorkhours(index) {
            let size = _.size(this.props.data[0].cols[index].planned_hours);
            if(size == 1) {
                return {
                    date: this.props.data[0].cols[index].planned_hours[0][0],
                    value: this.props.data[0].cols[index].planned_hours[0][1],
                }
            }
            else if(this.props.data[0].cols[index].is_unavailable) {
                return {
                    date: this.props.data[0].cols[index].timesheet_column_date,
                    value: 0,
                }
            }
            else {
                return {}
            }
        }
        /**
         * @private
         * @param {any} value
         * @returns {string}
         */
        _format(value) {
            this.props.cellComponentOptions = { noLeadingZeroHour: true };
            return super._format(...arguments);
        }
        /**
         * @private
         * @param {integer} index
         * @returns {value: number, smallerThanZero: boolean, muted: boolean}
         */
        _formatCellContentTotals(index) {
            const result = super._formatCellContentTotals(...arguments);
            result.new_value = this.props.totals.columns[index] - this.props.totals.leave_columns[index];
            return result;
        }
    }

    FlytTimerGridRenderer.props = Object.assign({}, TimerGridRenderer.props, {
        is_mytimesheets: Boolean,
    });
    FlytTimerGridRenderer.props.data[0].cols[0].is_unavailable_half_day = Boolean
    FlytTimerGridRenderer.props.data[0].cols[0].planned_hours = Array
    FlytTimerGridRenderer.props.data[0].cols[0].timesheet_column_date = Date
    FlytTimerGridRenderer.props.data[0].grid[0].is_unavailable_half_day = Boolean
    FlytTimerGridRenderer.props.data[0].grid[0].planned_hours = Array
    FlytTimerGridRenderer.props.data[0].grid[0].timesheet_column_date = Date

    return FlytTimerGridRenderer;
});
