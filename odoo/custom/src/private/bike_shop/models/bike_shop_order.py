# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class BikeShopOrder(models.Model):
    _name = 'bike_shop.order'
    _description = 'Bike Shop Order'
    _order = 'order_date desc, id desc'

    STATUS_OPEN = 'open'
    STATUS_COMPLETED = 'completed'
    
    STATUSES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_COMPLETED, 'Completed'),
    ]

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

    # Order identification
    name = fields.Char(
        string='Order Number',
        required=True,
        copy=False,
        readonly=True,
        default='/',
    )
    order_date = fields.Datetime(
        string='Order Date',
        required=True,
        default=fields.Datetime.now,
        readonly=True,
    )
    
    # Customer information
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        required=True,
        ondelete='restrict',
    )
    
    # Customer data fields (denormalized for historical preservation)
    partner_name = fields.Char(
        string='Customer Name',
    )
    partner_phone = fields.Char(
        string='Phone',
    )
    partner_mobile = fields.Char(
        string='Mobile',
    )
    partner_email = fields.Char(
        string='Email',
    )
    partner_street = fields.Char(
        string='Street',
    )
    partner_street2 = fields.Char(
        string='Street 2',
    )
    partner_city = fields.Char(
        string='City',
    )
    partner_state_id = fields.Char(
        string='State',
    )
    partner_zip = fields.Char(
        string='ZIP Code',
    )
    
    # Status
    status = fields.Selection(
        selection=STATUSES,
        string='Status',
        required=True,
        default=STATUS_OPEN,
        readonly=True,
    )
    
    # Order lines
    order_line_ids = fields.One2many(
        comodel_name='bike_shop.order.line',
        inverse_name='order_id',
        string='Order Lines',
    )
    
    # Discount
    discount_percentage = fields.Selection(
        selection=[
            ('0', '0%'),
            ('5', '5%'),
            ('10', '10%'),
            ('15', '15%'),
            ('20', '20%'),
            ('25', '25%'),
            ('30', '30%'),
        ],
        string='Discount Percentage',
        default='0',
    )
    
    # Totals
    subtotal = fields.Monetary(
        string='Subtotal',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    discount_value = fields.Monetary(
        string='Discount Value',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    total = fields.Monetary(
        string='Total',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    cost_total = fields.Monetary(
        string='Cost Total',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    net_value = fields.Monetary(
        string='Net Value',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    
    # Notes
    notes = fields.Text(
        string='Notes',
        translate=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Generate sequential order number and freeze partner data."""
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('bike_shop.order') or '/'
            vals.update(self._prepare_partner_snapshot(vals.get('partner_id')))
        return super().create(vals_list)

    def write(self, vals):
        if set(vals) - {'status'} and any(record.status == record.STATUS_COMPLETED for record in self):
            raise ValidationError(_('Completed orders must be reopened before editing.'))

        if 'partner_id' in vals:
            vals = dict(vals)
            vals.update(self._prepare_partner_snapshot(vals.get('partner_id')))

        return super().write(vals)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        """Load partner data into order"""
        self.update(self._prepare_partner_snapshot(self.partner_id.id))

    @api.depends('order_line_ids.subtotal', 'order_line_ids.cost_subtotal', 'discount_percentage')
    def _compute_totals(self):
        """Calculate all totals"""
        for record in self:
            # Calculate base subtotal
            subtotal = sum(line.subtotal for line in record.order_line_ids)
            
            # Calculate discount
            discount_pct = float(record.discount_percentage or 0)
            discount_value = subtotal * (discount_pct / 100)
            
            # Calculate final totals
            total = subtotal - discount_value
            cost_total = sum(line.cost_subtotal for line in record.order_line_ids)
            net_value = total - cost_total
            
            record.subtotal = subtotal
            record.discount_value = discount_value
            record.total = total
            record.cost_total = cost_total
            record.net_value = net_value

    def _prepare_partner_snapshot(self, partner_id):
        if not partner_id:
            return {
                'partner_name': False,
                'partner_phone': False,
                'partner_mobile': False,
                'partner_email': False,
                'partner_street': False,
                'partner_street2': False,
                'partner_city': False,
                'partner_state_id': False,
                'partner_zip': False,
            }

        partner = self.env['res.partner'].browse(partner_id)
        return {
            'partner_name': partner.name,
            'partner_phone': partner.phone,
            'partner_mobile': partner.mobile,
            'partner_email': partner.email,
            'partner_street': partner.street,
            'partner_street2': partner.street2,
            'partner_city': partner.city,
            'partner_state_id': partner.state_id.code if partner.state_id else False,
            'partner_zip': partner.zip,
        }

    def action_complete(self):
        """Complete the order and decrease stock"""
        for record in self:
            if record.status == self.STATUS_COMPLETED:
                raise ValidationError(_('Order is already completed!'))
            if not record.order_line_ids:
                raise ValidationError(_('Add at least one order line before completing the order.'))
            
            # Validate stock before completing
            record._check_stock_availability()
            
            # Decrease stock for products
            for line in record.order_line_ids:
                if line.line_type == 'product' and line.product_id:
                    line.product_id.stock -= line.quantity
            
            # Mark as completed
            record.status = self.STATUS_COMPLETED

    def action_reopen(self):
        """Reopen the order and restore stock"""
        for record in self:
            if record.status == self.STATUS_OPEN:
                raise ValidationError(_('Order is already open!'))
            
            # Restore stock for products
            for line in record.order_line_ids:
                if line.line_type == 'product' and line.product_id:
                    line.product_id.stock += line.quantity
            
            # Mark as open
            record.status = self.STATUS_OPEN

    def _check_stock_availability(self):
        """Verify stock availability for all products in order"""
        self.ensure_one()
        insufficient_stock = []
        
        for line in self.order_line_ids:
            if line.line_type == 'product' and line.product_id:
                if line.product_id.stock < line.quantity:
                    insufficient_stock.append({
                        'product': line.product_id.name,
                        'required': line.quantity,
                        'available': line.product_id.stock,
                    })
        
        if insufficient_stock:
            message = _('Insufficient stock for completion:\n\n')
            for item in insufficient_stock:
                message += _(
                    '{product}: Required {required}, Available {available}\n'
                ).format(**item)
            raise ValidationError(message)
