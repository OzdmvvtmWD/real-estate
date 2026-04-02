from odoo import fields, models, api


class RealEstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "real estate property type model"
    _order = "sequence,name"

    name = fields.Char(required=True)
    sequence = fields.Integer('Sequence', default=1,
                              help="Used to order types. Lower is better.")

    property_ids = fields.One2many(
        comodel_name="estate.property",
        inverse_name="property_type_id",
        string="Property"
    )

    offer_ids = fields.One2many(
        comodel_name="estate.property.offer",
        inverse_name="property_type_id",
        string="Offers"
    )

    offer_count = fields.Integer(compute='_compute_offer_count', store=True)

    _sql_constraints = [('type_unique',
                         'unique(name)',
                         'A property property type name must be unique')]


    @api.depends("offer_ids")
    def _compute_offer_count(self):
        for record in self:
            offers = record.offer_ids
            record.offer_count = len(offers) if offers else 0
