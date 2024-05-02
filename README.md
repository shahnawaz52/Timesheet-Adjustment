# Timesheet-Adjustment

## Description
This module introduces critical enhancements to the Gantt view and timesheet functionalities in Odoo, aimed at improving project management and scheduling capabilities on SAAS platforms. It integrates new features for calculating expected working hours and displaying delta working hours directly within the Gantt view. This allows managers to easily analyze and manage employee workloads and productivity.

## Key Features
### Enhanced Gantt View
- **Expected Working Hours**: Displays expected working hours based on the standard hours and public holidays (including half-days, which are newly supported).
- **Delta Working Hours**: Shows the difference between actual and expected working hours, enabling managers to quickly assess employee performance and address discrepancies.

### Timesheet Adjustments
- **Managerial Control Over Timesheets**: Direct modifications to timesheets by employees are restricted, reinforcing managerial oversight. Only managers can adjust timesheets, which helps maintain accuracy and compliance.
- **Public Holiday and Half-Day Support**: The system now correctly recognizes and accounts for public holidays and half-days in calculating expected hours, a feature previously unavailable in Odoo.

## Technical Details
### Models
- `account.analytic.line`: Extended to enhance the tracking and presentation of timesheet data, with new fields for managing and displaying calculated working hours.

### Server Actions
- **Automated Timesheet Adjustments**: Ensures that timesheets reflect accurate working hours, adjusting for public holidays and manager-approved changes.

### Views
- **React-based Gantt Component**: A newly designed React component integrated into the Gantt view, enhancing the visual representation of expected and actual hours, alongside delta analytics.

## Installation Instructions
To install this enhanced Timesheet and Gantt View module, follow these steps:

1. Ensure you have a working installation of Odoo.
2. Clone the repository to your server:
git clone https://github.com/yourusername/enhanced-timesheet-gantt.git
3. 3. Add the module to your Odoo addons path:
--addons-path=/path/to/your/addons,/path/to/enhanced-timesheet-gantt
4. Update your Odoo module list and install the module from the Odoo backend interface.

## Usage
Once installed, the module will automatically enhance the Gantt view with expected and delta working hours displayed. Managers will have the ability to adjust timesheets as needed, directly from the Gantt view or through the timesheet module, ensuring all data remains accurate and compliant with company policies.


