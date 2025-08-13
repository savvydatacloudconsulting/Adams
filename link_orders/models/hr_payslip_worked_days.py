from odoo import models, fields, api

class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    manual_amount = fields.Float(string="Manual Amount")  # optional if you want to store the raw value

    @api.depends('work_entry_type_id', 'number_of_hours', 'contract_id', 'payslip_id')
    def _compute_amount(self):
        for line in self:
            # Check for your OT types
            if line.work_entry_type_id == self.env.ref('link_orders.work_entry_type_ot_normal', raise_if_not_found=False):
                line.amount = line.payslip_id.normal_overtime_amount
            elif line.work_entry_type_id == self.env.ref('link_orders.work_entry_type_ot_holiday', raise_if_not_found=False):
                line.amount = line.payslip_id.weekend_overtime_amount
            else:
                super(HrPayslipWorkedDays, line)._compute_amount()
