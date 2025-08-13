from odoo import models, fields, api

class OvertimeEntryWizard(models.TransientModel):
    _name = 'overtime.entry.wizard'
    _description = 'Overtime Entry Wizard'

    employee_id = fields.Many2one('hr.employee', required=True)
    ot_type = fields.Selection([
        ('OT_NORMAL', 'Normal Overtime'),
        ('OT_HOLIDAY', 'Holiday/Weekend Overtime')
    ], required=True)
    hours = fields.Float("Hours", required=True)
    date = fields.Date(required=True)

    def action_add_overtime(self):
        work_entry_type = self.env['hr.work.entry.type'].search([('code', '=', self.ot_type)], limit=1)
        contract = self.employee_id.contract_id
        self.env['hr.work.entry'].create({
            'name': f"{self.ot_type} - {self.date}",
            'employee_id': self.employee_id.id,
            'work_entry_type_id': work_entry_type.id,
            'date_start': self.date,
            'date_stop': self.date,
            'contract_id': contract.id,
            'number_of_hours': self.hours,
        })
