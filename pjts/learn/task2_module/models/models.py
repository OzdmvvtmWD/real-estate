from odoo import fields, models, api, _


class CRMLead(models.Model):
    _inherit = "crm.lead"

    days_in_the_work = fields.Integer(compute='_compute_days_in_the_work',
                                      store=False)
    client_risk_level_name = fields.Char()

    @api.depends('create_date')
    def _compute_days_in_the_work(self):
        for record in self:
            record.days_in_the_work = (fields.Date.today() - record.create_date.date()).days

    def action_set_client_risk_level(self):
        return {'type': 'ir.actions.act_window',
                'name': _('Client Risk Level Action'),
                'res_model': 'client.risk.level',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {
                    'default_lead_id': self.id,  # important!
                    'default_name': self.client_risk_level_name
                }
                }


class ClientRiskLevel(models.TransientModel):
    _name = 'client.risk.level'
    _description = 'model for wizard'

    name = fields.Selection(
        string='Risk Level',
        selection=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
    )
    lead_id = fields.Many2one('crm.lead', string="CRM Lead")

    def set_client_risk_level(self):
        for record in self:
            record.lead_id.client_risk_level_name = record.name
