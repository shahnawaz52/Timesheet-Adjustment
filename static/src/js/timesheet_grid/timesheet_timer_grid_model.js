odoo.define('flyt_timesheet_grid.TimerGridModel', function (require) {
    "use strict";

    const TimerGridModel = require('timesheet_grid.TimerGridModel');

    const FlytTimerGridModel = TimerGridModel.extend({
        /**
         * @override
         */
        async __load(params) {
            const result = await this._super(...arguments);
            
            this._gridData.is_mytimesheets = true;

            return result;
        },
        /**
         * @override
         */
        async __reload(handle, params) {
            const result = await this._super(...arguments);

            this._gridData.is_mytimesheets = true;

            return result;
        },
        /**
         * @private
         * @param {Object[]} grid
         * @returns {{super: number, rows: {}, columns: {}, leave_columns: {}}}
         */
        _computeTotals: function (grid) {
            const result = this._super(...arguments);
            result.leave_columns = {}
            for (let i = 0; i < grid.length; i++) {
                const row = grid[i];
                for (let j = 0; j < row.length; j++) {
                    const cell = row[j];
                    result.leave_columns[j] = cell.unit_amount ? cell.unit_amount : (result.leave_columns[j] || 0);
                }
            }
            return result;
        },
    });

    return FlytTimerGridModel;
});
