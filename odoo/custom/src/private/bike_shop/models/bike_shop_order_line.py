# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class BikeShopOrderLine(models.Model):
    _name = 'bike_shop.order.line'
    _description = 'Bike Shop Order Line'
    _order = 'sequence, id'

    LINE_TYPE_PRODUCT = 'product'
    LINE_TYPE_SERVICE = 'service'
    
    LINE_TYPES = [
        (LINE_TYPE_PRODUCT, 'Product'),
        (LINE_TYPE_SERVICE, 'Service / Labor'),
    ]

    order_id = fields.Many2one(
        comodel_name='bike_shop.order',
        string='Order',
        required=True,
        ondelete='cascade',
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        related='order_id.company_id',
        store=True,
        readonly=True,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        related='order_id.currency_id',
        store=True,
        readonly=True,
    )
    
    # Line type selection
    line_type = fields.Selection(
        selection=LINE_TYPES,
        string='Item Type',
        required=True,
        default=LINE_TYPE_PRODUCT,
    )
    
    # Product or Service selection
    product_id = fields.Many2one(
        comodel_name='bike_shop.product',
        string='Product',
        domain=[('active', '=', True)],
    )
    service_id = fields.Many2one(
        comodel_name='bike_shop.service',
        string='Service',
        domain=[('active', '=', True)],
    )
    
    # Description
    description = fields.Text(
        string='Description',
        translate=True,
    )
    
    # Quantity and pricing
    quantity = fields.Float(
        string='Quantity',
        required=True,
        default=1.0,
        digits=(10, 2),
    )
    unit_price = fields.Monetary(
        string='Unit Price',
        required=True,
        default=0.0,
        currency_field='currency_id',
    )
    cost_unit_price = fields.Monetary(
        string='Unit Cost Price',
        default=0.0,
        currency_field='currency_id',
    )
    
    # Subtotals
    subtotal = fields.Monetary(
        string='Subtotal',
        compute='_compute_subtotal',
        store=True,
        currency_field='currency_id',
    )
    cost_subtotal = fields.Monetary(
        string='Cost Subtotal',
        compute='_compute_cost_subtotal',
        store=True,
        currency_field='currency_id',
    )
    
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )

    @api.constrains('quantity')
    def _check_quantity(self):
        """Ensure quantity is greater than zero"""
        for record in self:
            if record.quantity <= 0:
                raise ValidationError(_('Quantity must be greater than zero!'))

    @api.constrains('unit_price')
    def _check_unit_price(self):
        """Ensure unit price is not negative"""
        for record in self:
            if record.unit_price < 0:
                raise ValidationError(_('Unit price cannot be negative!'))

    @api.constrains('cost_unit_price')
    def _check_cost_unit_price(self):
        """Ensure cost unit price is not negative"""
        for record in self:
            if record.cost_unit_price < 0:
                raise ValidationError(_('Unit cost price cannot be negative!'))

    @api.constrains('product_id', 'service_id', 'line_type')
    def _check_required_items(self):
        """Ensure product or service is selected based on line type"""
        for record in self:
            if record.line_type == self.LINE_TYPE_PRODUCT and not record.product_id:
                raise ValidationError(_('Product must be selected for product lines!'))
            if record.line_type == self.LINE_TYPE_SERVICE and not record.service_id:
                raise ValidationError(_('Service must be selected for service lines!'))
            if record.line_type == self.LINE_TYPE_PRODUCT and record.service_id:
                raise ValidationError(_('Service must be empty for product lines!'))
            if record.line_type == self.LINE_TYPE_SERVICE and record.product_id:
                raise ValidationError(_('Product must be empty for service lines!'))

    @api.model_create_multi
    def create(self, vals_list):
        self._check_completed_order_modification(vals_list=vals_list)
        return super().create(vals_list)

    def write(self, vals):
        self._check_completed_order_modification(vals=vals)
        return super().write(vals)

    def unlink(self):
        self._check_completed_order_modification()
        return super().unlink()

    @api.onchange('line_type')
    def _onchange_line_type(self):
        """Clear previous selection when line type changes"""
        if self.line_type == self.LINE_TYPE_PRODUCT:
            self.service_id = False
            self.unit_price = 0.0
            self.cost_unit_price = 0.0
        else:
            self.product_id = False
            self.cost_unit_price = 0.0

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """Auto-fill product details"""
        if self.product_id:
            self.description = self.product_id.name
            self.unit_price = self.product_id.selling_price
            self.cost_unit_price = self.product_id.cost_price

    @api.onchange('service_id')
    def _onchange_service_id(self):
        """Auto-fill service details"""
        if self.service_id:
            self.description = self.service_id.name
            self.unit_price = self.service_id.price
            self.cost_unit_price = 0.0

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        """Calculate line subtotal"""
        for record in self:
            record.subtotal = record.quantity * record.unit_price

    @api.depends('quantity', 'cost_unit_price')
    def _compute_cost_subtotal(self):
        """Calculate line cost subtotal"""
        for record in self:
            record.cost_subtotal = record.quantity * record.cost_unit_price

    def _check_completed_order_modification(self, vals=None, vals_list=None):
        if vals_list:
            order_ids = [vals.get('order_id') for vals in vals_list if vals.get('order_id')]
            orders = self.env['bike_shop.order'].browse(order_ids)
        else:
            orders = self.mapped('order_id')

        if vals and vals.get('order_id'):
            orders |= self.env['bike_shop.order'].browse(vals['order_id'])

        if any(order.status == order.STATUS_COMPLETED for order in orders):
            raise ValidationError(_('Completed orders must be reopened before changing order lines.'))
