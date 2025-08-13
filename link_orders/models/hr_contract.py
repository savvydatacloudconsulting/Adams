from odoo import models, fields, api

class HrContract(models.Model):
    _inherit = 'hr.contract'

    hourly_rate = fields.Float(string='Hourly Rate', compute='_compute_hourly_rate', store=True)

    @api.depends('wage')
    def _compute_hourly_rate(self):
        for contract in self:
            contract.hourly_rate = contract.wage / 184 if contract.wage else 0.0
