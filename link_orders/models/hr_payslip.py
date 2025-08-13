# from odoo import models, fields, api
# import pytz
# from datetime import datetime


# class HrPayslip(models.Model):
#     _inherit = 'hr.payslip'

#     def _get_attendance_overtime_hours(self):
#         self.ensure_one()
#         employee = self.employee_id
#         user_tz = self.env.user.tz or 'UTC'

#         attendances = self.env['hr.attendance'].search([
#             ('employee_id', '=', employee.id),
#             ('check_in', '>=', self.date_from),
#             ('check_out', '<=', self.date_to),
#         ])

#         weekend_days = [5, 6]
#         ot_normal_hours = 0.0
#         ot_weekend_hours = 0.0

#         for attendance in attendances:
#             validated_hours = attendance.validated_overtime_hours or 0.0
#             if validated_hours <= 0:
#                 continue

#             check_in = fields.Datetime.from_string(attendance.check_in)
#             check_in = self._convert_to_tz(check_in, user_tz)

#             is_weekend = check_in.weekday() in weekend_days
#             is_public_holiday = self.env['resource.calendar.leaves'].search_count([
#                 ('calendar_id', '=', employee.resource_calendar_id.id),
#                 ('date_from', '<=', check_in),
#                 ('date_to', '>=', check_in),
#                 ('resource_id', '=', employee.resource_id.id)
#             ]) > 0

#             if is_weekend or is_public_holiday:
#                 ot_weekend_hours += validated_hours
#             else:
#                 ot_normal_hours += validated_hours

#         return ot_normal_hours, ot_weekend_hours

#     def _convert_to_tz(self, dt, tz_name):
#         if not dt:
#             return dt
#         if not isinstance(dt, datetime):
#             dt = fields.Datetime.from_string(dt)
#         user_tz = pytz.timezone(tz_name)
#         dt = dt.replace(tzinfo=pytz.utc).astimezone(user_tz)
#         return dt


#     def _get_worked_day_lines(self):
#         # Call the original method
#         worked_days = super(HrPayslip, self)._get_worked_day_lines()
#         print("-----^^^^^^^^worked_days^^^^^^^^^^^^^", worked_days)

#         # Remove any default "Overtime" entries
#         cleaned_worked_days = []
#         for wd in worked_days:
#             code = wd.get('code')
#             print("-----^^^^^^^^code^^^^^^^^^^^^^", code)

#             if code in ('OVERTIME', 'Overtime Hours'):
#                 continue
#             cleaned_worked_days.append(wd)

#         # Add custom overtime values from attendance
#         ot_normal, ot_holiday = self._get_attendance_overtime_hours()
#         contract = self.contract_id
#         print("-----^^^^^^^^contract^^^^^^^^^^^^^", contract)

#         if ot_normal:
#             cleaned_worked_days.append({
#                 'name': 'Normal Overtime',
#                 'code': 'OT_NORMAL',
#                 'number_of_days': 0.0,
#                 'number_of_hours': ot_normal,
#                 'amount': 120.0,
#                 'contract_id': contract.id,
#                 'work_entry_type_id': self.env.ref('link_orders.work_entry_type_ot_normal').id,
#             })

#         if ot_holiday:
#             cleaned_worked_days.append({
#                 'name': 'Holiday Overtime',
#                 'code': 'OT_HOLIDAY',
#                 'number_of_days': 0.0,
#                 'number_of_hours': ot_holiday,
#                 'contract_id': contract.id,
#                 'work_entry_type_id': self.env.ref('link_orders.work_entry_type_ot_holiday').id,
#             })

#         return cleaned_worked_days



from odoo import models, fields, api, _
from datetime import datetime, time, timedelta

import pytz

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    normal_overtime_hours = fields.Float(string='Normal Overtime Hours', default=0.0)
    weekend_overtime_hours = fields.Float(string='Weekend/PH Overtime Hours', default=0.0)

    normal_overtime_amount = fields.Monetary(string='Normal OT Amount', compute='_compute_overtime_amounts', store=True)
    weekend_overtime_amount = fields.Monetary(string='Weekend OT Amount', compute='_compute_overtime_amounts', store=True)
    total_overtime_amount = fields.Monetary(string='Total OT Amount', compute='_compute_overtime_amounts', store=True)

    @api.depends('normal_overtime_hours', 'weekend_overtime_hours', 'contract_id.hourly_rate')
    def _compute_overtime_amounts(self):
        for payslip in self:
            rate = payslip.contract_id.hourly_rate or 0.0
            print("--------_compute_overtime_amounts------rate-----------", rate)
            payslip.normal_overtime_amount = payslip.normal_overtime_hours * rate * 1.25
            print("--------_compute_overtime_amounts------payslip.normal_overtime_amount-----------", payslip.normal_overtime_amount)
            payslip.weekend_overtime_amount = payslip.weekend_overtime_hours * rate * 1.5
            print("--------_compute_overtime_amounts------payslip.weekend_overtime_amount-----------", payslip.weekend_overtime_amount)
            payslip.total_overtime_amount = payslip.normal_overtime_amount + payslip.weekend_overtime_amount
            print("--------_compute_overtime_amounts------payslip.total_overtime_amount-----------", payslip.total_overtime_amount)


    def _get_worked_day_lines_values(self, domain=None):
        res = super()._get_worked_day_lines_values(domain=domain)
        print("-----------------------res--------------------", res)
        default_ot_type = self.env.ref('hr_work_entry.overtime_work_entry_type', raise_if_not_found=False)
        print("-----------------------default_ot_type--------------------", default_ot_type)
        if default_ot_type:
            res = [line for line in res if line.get('work_entry_type_id') != default_ot_type.id]
            print("-----------------------default_ot_type------res--------------", res)
        
        return res


    def compute_overtime_from_attendance(self):
        for payslip in self:
            normal_ot = 0.0
            weekend_ot = 0.0

            if not payslip.employee_id or not payslip.contract_id:
                continue

            calendar = payslip.contract_id.resource_calendar_id
            if not calendar:
                continue

            tz = pytz.timezone(payslip.employee_id.tz or 'UTC')

            # Get attendances for the payslip period
            attendances = self.env['hr.attendance'].search([
                ('employee_id', '=', payslip.employee_id.id),
                ('check_in', '>=', payslip.date_from),
                ('check_out', '<=', payslip.date_to),
            ])

            # Group worked hours per day (employee local time)
            attendance_by_day = {}
            for att in attendances:
                check_in_local = fields.Datetime.context_timestamp(self, att.check_in)
                worked_hours = att.worked_hours or 0.0
                day = check_in_local.date()
                attendance_by_day.setdefault(day, 0.0)
                attendance_by_day[day] += worked_hours

            # Get public holiday dates
            ph_dates = set()
            public_holidays = self.env['resource.calendar.leaves'].search([
                ('date_from', '<=', payslip.date_to),
                ('date_to', '>=', payslip.date_from),
                ('calendar_id', '=', calendar.id),
                ('time_type', '=', 'leave'),
            ])
            for ph in public_holidays:
                dt = ph.date_from.date()
                while dt <= ph.date_to.date():
                    ph_dates.add(dt)
                    dt += timedelta(days=1)

            # Loop through each day in the period
            current_day = payslip.date_from
            while current_day <= payslip.date_to:
                is_weekend = current_day.weekday() >= 5
                is_ph = current_day in ph_dates

                # Correct scheduled hours calculation for Odoo 18
                scheduled_hours = calendar.get_work_hours_count(
                    datetime.combine(current_day, time.min),
                    datetime.combine(current_day, time.max)
                ) or 0.0

                worked = attendance_by_day.get(current_day, 0.0)
                extra = max(0.0, worked - scheduled_hours)

                if is_weekend or is_ph or scheduled_hours == 0.0:
                    weekend_ot += extra
                else:
                    normal_ot += extra

                current_day += timedelta(days=1)

            payslip.normal_overtime_hours = normal_ot
            payslip.weekend_overtime_hours = weekend_ot

    def compute_sheet(self):
        res = super().compute_sheet()

        for payslip in self:
            payslip.compute_overtime_from_attendance()

            # Remove default OT lines if needed
            default_ot_type = self.env.ref('hr_work_entry.overtime_work_entry_type', raise_if_not_found=False)
            if default_ot_type:
                payslip.worked_days_line_ids.filtered(
                    lambda l: l.work_entry_type_id == default_ot_type
                ).unlink()

            # Add Normal OT line
            if payslip.normal_overtime_hours > 0:
                payslip.worked_days_line_ids.create({
                    'payslip_id': payslip.id,
                    'work_entry_type_id': self.env.ref('link_orders.work_entry_type_ot_normal').id,
                    'number_of_days': 0.0,
                    'number_of_hours': payslip.normal_overtime_hours,
                    'amount': payslip.normal_overtime_amount,
                    'contract_id': payslip.contract_id.id,
                })

            # Add Weekend OT line
            if payslip.weekend_overtime_hours > 0:
                payslip.worked_days_line_ids.create({
                    'payslip_id': payslip.id,
                    'work_entry_type_id': self.env.ref('link_orders.work_entry_type_ot_holiday').id,
                    'number_of_days': 0.0,
                    'number_of_hours': payslip.weekend_overtime_hours,
                    'amount': payslip.weekend_overtime_amount,
                    'contract_id': payslip.contract_id.id,
                })

            # --- Force Net Salary as sum of worked days + inputs ---
            worked_days_total = sum(line.amount for line in payslip.worked_days_line_ids)
            inputs_total = sum(line.amount for line in payslip.input_line_ids)
            net_total = worked_days_total + inputs_total

            net_line = payslip.line_ids.filtered(lambda l: l.code == 'NET')
            if net_line:
                net_line.total = net_total
                net_line.amount = net_total

        return res
