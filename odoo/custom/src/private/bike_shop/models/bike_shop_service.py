# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class BikeShopService(models.Model):
    _name = 'bike_shop.service'
    _description = 'Bike Shop Service'
    _rec_name = 'name'

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        related='company_id.currency_id',
        store=True,
        readonly=True,
    )
    name = fields.Char(
        string='Service Name',
        required=True,
        translate=True,
    )
    description = fields.Text(
        string='Description',
        translate=True,
    )
    price = fields.Monetary(
        string='Service Price',
        required=True,
        default=0.0,
        currency_field='currency_id',
    )
    active = fields.Boolean(
        string='Active',
        default=True,
    )

    @api.constrains('price')
    def _check_price(self):
        """Ensure price is not negative"""
        for record in self:
            if record.price < 0:
                raise ValidationError(_('Service price cannot be negative!'))
