from odoo import fields, models


class RealEstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "real estate property tag model"
    _order = "name"

    name = fields.Char(required=True)
    color = fields.Integer()

    _sql_constraints = [('tag_unique',
                         'unique(name)',
                         'A property tag name must be unique')]
