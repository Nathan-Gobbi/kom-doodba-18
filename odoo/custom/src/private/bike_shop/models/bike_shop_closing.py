# -*- coding: utf-8 -*-

from datetime import datetime, time, timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class BikeShopClosing(models.Model):
    _name = 'bike_shop.closing'
    _description = 'Bike Shop Financial Closing'
    _order = 'date_end desc, id desc'

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
        string='Closing Name',
        required=True,
        readonly=True,
        compute='_compute_name',
        store=True,
        precompute=True,
    )
    
    # Period
    date_start = fields.Date(
        string='Start Date',
        required=True,
    )
    date_end = fields.Date(
        string='End Date',
        required=True,
    )
    
    # Consolidated data - computed orders will be retrieved via method
    # This will be displayed in the view
    
    quantity_orders = fields.Integer(
        string='Number of Orders',
        compute='_compute_consolidation',
        store=True,
    )
    
    # Sales breakdown
    total_products_sales = fields.Monetary(
        string='Total Products Sales',
        compute='_compute_consolidation',
        store=True,
        currency_field='currency_id',
    )
    total_services_sales = fields.Monetary(
        string='Total Services Sales',
        compute='_compute_consolidation',
        store=True,
        currency_field='currency_id',
    )
    total_sales = fields.Monetary(
        string='Total Sales',
        compute='_compute_consolidation',
        store=True,
        currency_field='currency_id',
    )
    
    # Costs and margins
    total_product_costs = fields.Monetary(
        string='Total Product Costs',
        compute='_compute_consolidation',
        store=True,
        currency_field='currency_id',
    )
    total_discounts = fields.Monetary(
        string='Total Discounts',
        compute='_compute_consolidation',
        store=True,
        currency_field='currency_id',
    )
    net_value = fields.Monetary(
        string='Net Value (Profit)',
        compute='_compute_consolidation',
        store=True,
        currency_field='currency_id',
    )
    
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('done', 'Completed'),
        ],
        string='State',
        default='draft',
    )

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        """Ensure end date is after start date"""
        for record in self:
            if record.date_end < record.date_start:
                raise ValidationError(_('End date must be after start date!'))

    @api.depends('date_start', 'date_end')
    def _compute_name(self):
        """Generate closing name from dates"""
        for record in self:
            if record.date_start and record.date_end:
                record.name = _(
                    'Closing {start} to {end}'
                ).format(
                    start=record.date_start.strftime('%d/%m/%Y'),
                    end=record.date_end.strftime('%d/%m/%Y'),
                )
            else:
                record.name = 'New Closing'

    def _get_orders(self):
        """Get completed orders in period"""
        self.ensure_one()
        if not self.date_start or not self.date_end:
            return self.env['bike_shop.order']

        start_dt = datetime.combine(self.date_start, time.min)
        end_dt = datetime.combine(self.date_end + timedelta(days=1), time.min)
        orders = self.env['bike_shop.order'].search([
            ('status', '=', 'completed'),
            ('company_id', '=', self.company_id.id),
            ('order_date', '>=', fields.Datetime.to_string(start_dt)),
            ('order_date', '<', fields.Datetime.to_string(end_dt)),
        ])
        return orders

    @api.depends('date_start', 'date_end')
    def _compute_consolidation(self):
        """Calculate consolidated values"""
        for record in self:
            if not record.date_start or not record.date_end:
                record.quantity_orders = 0
                record.total_products_sales = 0.0
                record.total_services_sales = 0.0
                record.total_sales = 0.0
                record.total_product_costs = 0.0
                record.total_discounts = 0.0
                record.net_value = 0.0
                continue

            orders = record._get_orders()
            
            # Count orders
            record.quantity_orders = len(orders)
            
            # Calculate sales by type and totals
            total_products = 0
            total_services = 0
            total_costs = 0
            total_discounts = 0
            
            for order in orders:
                total_discounts += order.discount_value
                total_costs += order.cost_total
                
                for line in order.order_line_ids:
                    if line.line_type == 'product':
                        total_products += line.subtotal
                    else:  # service
                        total_services += line.subtotal
            
            total_sales = total_products + total_services - total_discounts
            net_value = total_sales - total_costs
            
            record.total_products_sales = total_products
            record.total_services_sales = total_services
            record.total_sales = total_sales
            record.total_product_costs = total_costs
            record.total_discounts = total_discounts
            record.net_value = net_value

    def action_complete(self):
        """Mark closing as completed"""
        for record in self:
            if record.state == 'done':
                raise ValidationError(_('Closing is already completed!'))
            record.state = 'done'

    def action_reset(self):
        """Reset closing to draft"""
        for record in self:
            if record.state == 'draft':
                raise ValidationError(_('Closing is already in draft!'))
            record.state = 'draft'
