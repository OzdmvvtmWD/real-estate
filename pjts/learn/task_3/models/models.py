from odoo import fields, models, api


class CustomersCredit(models.Model):
    _name = 'customer.credit'
    _description = 'task 3 model for pivot view'

    date_of_issue = fields.Date()
    credits_sum = fields.Float()
    credits_percent = fields.Float()
    credits_percent_sum = fields.Float(compute='_compute_credits_percent_sum', store=True)

    partner_id = fields.Many2one("res.partner", string="Customer")

    _sql_constraints = [('check_credits_percent',
                         'CHECK(credits_percent >= 0 AND credits_percent <=100)',
                         'A credits percent must be form 0% to 100%'),]


    @api.depends('credits_sum', 'credits_percent')
    def _compute_credits_percent_sum(self):
        for record in self:
            record.credits_percent_sum = record.credits_sum * record.credits_percent / 100
