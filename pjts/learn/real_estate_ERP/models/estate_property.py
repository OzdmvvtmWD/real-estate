from datetime import date, timedelta

from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero

MONTHS = 3


class RealEstate(models.Model):
    _name = "estate.property"
    _description = "real estate model"
    _order = "id desc"

    active = fields.Boolean('Active', default=True)

    name = fields.Char(required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(copy=False,
                                    default=fields.Date.today() + timedelta(days=MONTHS * 30))
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        string='Garden orientation',
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
        help="Type is used to separate Leads and Opportunities"
    )

    state = fields.Selection(
        string='Status',
        selection=[('new', 'New'), ('received', 'Offer Received'),
                   ('accepted', 'Offer Accepted'), ('sold', 'Sold'), ('canceled', 'Canceled')],
        help="Status is used to monitor property status",
        default='new', compute='_compute_state', store=True
    )

    total_area = fields.Integer(compute="_compute_total_area")
    best_price = fields.Float(compute="_compute_best_price")

    property_type_id = fields.Many2one("estate.property.type",
                                       string="RealEstatePropertyType")
    buyer = fields.Many2one("res.partner", string="Buyer", copy=False)
    salesperson = fields.Many2one("res.users", string="Salesperson",
                                  default=lambda self: self.env.user)
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")

    offer_ids = fields.One2many(
        comodel_name="estate.property.offer",
        inverse_name="property_id",
        string="Offers"
    )

    _sql_constraints = [('check_selling_price_positive',
                         'CHECK(selling_price >= 0)',
                         'A property selling price must be positive'),
                        ('check_price_must_be_strictly_positive',
                         'CHECK(expected_price > 0)',
                         'A property expected price must be strictly positive')]

    @api.depends("garden_area", "living_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.garden_area + record.living_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            prices = record.offer_ids.mapped('price')
            record.best_price = max(prices) if prices else 0.0

    @api.depends("offer_ids.status")
    def _compute_state(self):
        for record in self:
            if record.state == 'sold' or record.state == 'canceled':
                continue

            offer_status = record.offer_ids.mapped('status')

            if not offer_status:
                record.state = 'new'

            if offer_status:
                record.state = 'received'

            if 'accepted' in offer_status:
                record.state = 'accepted'

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'

        else:
            self.garden_area = None
            self.garden_orientation = None

    def cancel_property(self):
        for record in self:
            if record.state != 'sold':
                record.state = 'canceled'
            else:
                raise UserError("A sold property cannot be canceled")

    def sold_property(self):
        for record in self:
            if record.state != 'canceled':
                record.state = 'sold'
            else:
                raise UserError("A canceled property cannot be set as sold")

    @api.constrains('selling_price')
    def _check_selling_price(self):
        for record in self:
            ninth_percent = record.expected_price * 0.9

            if float_compare(record.selling_price, ninth_percent, precision_rounding=2) < 0 and \
                    not float_is_zero(record.selling_price, precision_rounding=2):
                raise ValidationError("The selling price cannot be lower than 90% of the expected price \n"
                                      "The selling price is zero until an offer is validated")

    @api.ondelete(at_uninstall=False)
    def _unlink_if_property_is_not_canceled_or_new(self):
        if any(record.state not in ('new', 'canceled') for record in self):
            raise UserError("Can't delete, state is not ‘New’ or ‘Canceled’!")
