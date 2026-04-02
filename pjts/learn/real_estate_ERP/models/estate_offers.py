from odoo import fields, models, api
from datetime import timedelta
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero


class Offer(models.Model):
    _name = "estate.property.offer"
    _description = "real estate property offer model"
    _order = "price desc"

    price = fields.Float()
    status = fields.Selection(
        string='Type',
        selection=[('refuse', 'Refuse'),
                   ('accepted', 'Accepted')],
        copy=False, readonly=True
    )

    validity = fields.Integer(default=7)
    date_deadline = fields.Date(compute='_compute_total_area', inverse="_inverse_total_area")

    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    property_id = fields.Many2one("estate.property", string="Property", required=True)

    property_type_id = fields.Many2one("estate.property.type",
                                       string="Type",
                                       related='property_id.property_type_id',
                                       store=True,
                                       required=True)

    _sql_constraints = [('check_offer_price_positive',
                         'CHECK(price > 0)',
                         'An offer price must be strictly positive')]

    def _get_create_data(self):
        return (self.create_date or fields.Datetime.now()).date()

    @api.depends("validity", "create_date")
    def _compute_total_area(self):
        for record in self:
            create_dt = record._get_create_data()
            record.date_deadline = timedelta(days=record.validity) + create_dt

    def _inverse_total_area(self):
        for record in self:
            create_dt = record._get_create_data()
            record.validity = (record.date_deadline - create_dt).days

    def accepted_offer(self):
        for record in self:
            record.status = 'accepted'

            record.property_id.selling_price = record.price
            record.property_id.buyer = record.partner_id

            refuse_offers = self.env['estate.property.offer'].search([
                ('id', '!=', record.id),
                ('property_id', '=', record.property_id.id),
            ])

            refuse_offers.write({'status': 'refuse'})

    def refuse_offer(self):
        for record in self:
            record.status = 'refuse'

            accepted_offers = self.env['estate.property.offer'].search([
                ('id', '!=', record.id),
                ('property_id', '=', record.property_id.id),
                ('status', '=', 'accepted')
            ])

            if not accepted_offers:
                record.property_id.selling_price = 0
                record.property_id.buyer = None

    @api.model
    def create(self, vals):
        property_ids = vals['property_id']
        property_record = self.env['estate.property'].browse(property_ids)

        existing_offers = self.env['estate.property.offer'].search([
            ('property_id', '=', property_ids),
        ])
        if existing_offers:
            max_offer = max(existing_offers.mapped('price'))
            if float_compare(vals.get('price', 0.0), max_offer, precision_rounding=5) < 0:
                raise UserError("User tries to create an offer with a lower amount "
                                "than an existing offer")

        property_record.state = 'accepted'

        return super(Offer, self).create(vals)
