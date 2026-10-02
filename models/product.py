from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        user = self.env.user

        # Managers see all variants
        if user.has_group('stock.group_stock_manager'):
            return super(ProductProduct, self).search(args, offset=offset, limit=limit, order=order, count=count)

        # Restrict by user's allowed locations
        if user.location_ids:
            allowed_product_ids = self.env['stock.quant'].search([
                ('location_id', 'in', user.location_ids.ids)
            ]).mapped('product_id.id')

            args = [('id', 'in', allowed_product_ids)] + list(args)

        return super(ProductProduct, self).search(args, offset=offset, limit=limit, order=order, count=count)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    allowed_qty = fields.Float(
        string='Allowed Qty',
        compute='_compute_allowed_qty',
        store=False,  # always compute dynamically
    )

    @api.depends('product_variant_ids.qty_available')
    def _compute_allowed_qty(self):
        """Compute quantity only in allowed locations for the current user"""
        user = self.env.user
        for product in self:
            if user.has_group('stock.group_stock_manager'):
                # Managers see total quantity on hand
                product.allowed_qty = sum(product.mapped('product_variant_ids.qty_available'))
            elif user.location_ids:
                # For regular users, sum quants only in allowed locations
                quants = self.env['stock.quant'].search([
                    ('product_id', 'in', product.product_variant_ids.ids),
                    ('location_id', 'in', user.location_ids.ids),
                ])
                product.allowed_qty = sum(quants.mapped('quantity'))
            else:
                # If user has no allowed locations, show 0
                product.allowed_qty = 0

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        user = self.env.user

        # Managers see all products
        if user.has_group('stock.group_stock_manager'):
            return super(ProductTemplate, self).search(args, offset=offset, limit=limit, order=order, count=count)

        # Restrict by user's allowed locations
        if user.location_ids:
            allowed_product_tmpl_ids = self.env['stock.quant'].search([
                ('location_id', 'in', user.location_ids.ids)
            ]).mapped('product_tmpl_id.id')

            args = [('id', 'in', allowed_product_tmpl_ids)] + list(args)

        return super(ProductTemplate, self).search(args, offset=offset, limit=limit, order=order, count=count)

    def action_open_allowed_quants(self):
        self.ensure_one()

        allowed_locations = self.env.user.location_ids.ids

        quants = self.env['stock.quant'].search([
            ('product_id', 'in', self.product_variant_ids.ids),
            ('location_id', 'in', allowed_locations),
        ])

        if not quants:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "No Stock",
                    "message": "No quantities available in your allowed locations.",
                    "sticky": False,
                },
            }

        # If only 1 quant → open form view directly
        if len(quants) == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Stock Quant',
                'res_model': 'stock.quant',
                'view_mode': 'form',
                'res_id': quants.id,
                'target': 'current',
            }

        # If multiple quants → open tree view filtered
        return {
            'type': 'ir.actions.act_window',
            'name': 'Stock Quants',
            'res_model': 'stock.quant',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', quants.ids)],
            'target': 'current',
        }

class StockQuant(models.Model):
    _inherit = 'stock.quant'