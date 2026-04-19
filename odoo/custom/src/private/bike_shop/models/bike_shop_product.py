# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class BikeShopProduct(models.Model):
    _name = 'bike_shop.product'
    _description = 'Bike Shop Product'
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
        string='Product Name',
        required=True,
        translate=True,
    )
    code = fields.Char(
        string='Product Code',
        required=True,
        copy=False,
        help='Unique identifier for the product',
    )
    barcode = fields.Char(
        string='Barcode',
        copy=False,
        help='EAN-13 or similar product barcode',
    )
    color = fields.Char(
        string='Color',
        translate=True,
    )
    description = fields.Text(
        string='Description',
        translate=True,
    )
    ncm = fields.Char(
        string='NCM',
        help='Nomenclatura Comum do Mercosul (Brazilian product classification)',
    )
    
    # Stock
    stock = fields.Integer(
        string='Stock Quantity',
        default=0,
        required=True,
    )
    
    # Pricing
    cost_price = fields.Monetary(
        string='Cost Price',
        required=True,
        default=0.0,
        currency_field='currency_id',
    )
    selling_price = fields.Monetary(
        string='Selling Price',
        required=True,
        default=0.0,
        currency_field='currency_id',
    )
    
    # Status
    active = fields.Boolean(
        string='Active',
        default=True,
    )

    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Product code must be unique!'),
        ('barcode_unique', 'unique(barcode)', 'Product barcode must be unique (when informed)!'),
    ]

    @api.constrains('stock')
    def _check_stock(self):
        """Ensure stock is not negative"""
        for record in self:
            if record.stock < 0:
                raise ValidationError(_('Stock quantity cannot be negative!'))

    @api.constrains('cost_price')
    def _check_cost_price(self):
        """Ensure cost price is not negative"""
        for record in self:
            if record.cost_price < 0:
                raise ValidationError(_('Cost price cannot be negative!'))

    @api.constrains('selling_price')
    def _check_selling_price(self):
        """Ensure selling price is not negative"""
        for record in self:
            if record.selling_price < 0:
                raise ValidationError(_('Selling price cannot be negative!'))

    @api.onchange('barcode')
    def _onchange_barcode(self):
        """Validate barcode format if provided"""
        if self.barcode and self.barcode.strip():
            # Allow various barcode formats (EAN-13, UPC, etc.)
            if not self.barcode.isdigit():
                raise ValidationError(_('Barcode must contain only digits!'))
            if len(self.barcode) not in [8, 12, 13, 14]:
                raise ValidationError(_('Barcode must be 8, 12, 13 or 14 digits long!'))
