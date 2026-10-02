from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class StockRequest(models.Model):
    _inherit = 'stock.request'



class StockRequestOrder(models.Model):
    _inherit = 'stock.request.order'

    request_id = fields.Many2one(
        'stock.request', string='Stock Request', required=False
    )
    # Main fields
    product_id = fields.Many2one(
        'product.product', string="Product",
        required=False,
        readonly=True,
        state={"draft": [("readonly", False)]},
    )
    product_uom_id = fields.Many2one(
        'uom.uom', string="Unit of Measure",
        required=False,
        readonly=True,
        state={"draft": [("readonly", False)]},
    )
    # Picking related fields
    picking_type_id = fields.Many2one('stock.picking.type', string="Operation Type", readonly=True)
    operation_type = fields.Char(string="Operation", compute="_compute_operation_type", store=True)
    state = fields.Selection(
        [
            ('draft', 'Draft'),  # User working
            ('sent', 'Sent to Manager'),  # User sent
            ('confirmed', 'Confirmed'),  # Manager approved
            ('open', 'Open'),
            ('done', 'Done'),

        ],
        string='Status',
        default='draft',
        tracking=True
    )

    location_dest_id = fields.Many2one('stock.location', string='Destination location')

    location_id = fields.Many2one(
        'stock.location',
        string='Source Location',
        default=lambda self: self._get_default_location(),
        required=True,
        domain=lambda self: self._domain_location()
    )
    picking_type_code = fields.Char(
        string='Picking Type Code',
        compute='_compute_picking_type_code',
        store=True,
        readonly=True
    )
    service = fields.Char(string="Service")
    num_of_order = fields.Char(string="Receipt Order Number")
    applicant = fields.Many2one('res.users', string="Applicant",domain="[('company_ids', 'in', [company_id or 0]), ('active','=',True)]")

    @api.model
    def _get_default_location(self):
        """Return the first allowed location of the current user (normal users only)"""
        user = self.env.user
        stock_manager_group = self.env.ref('stock.group_stock_manager')
        if stock_manager_group not in user.groups_id:
            allowed = user.location_ids
            return allowed[:1] and allowed[0] or False
        return False  # Managers: no default

    @api.model
    def _domain_location(self):
        """Return allowed locations for normal users, all locations for managers"""
        user = self.env.user
        stock_manager_group = self.env.ref('stock.group_stock_manager')
        if stock_manager_group not in user.groups_id:
            return [('id', 'in', user.location_ids.ids)]
        return []  # empty domain = no restriction

    @api.model
    def create(self, vals):
        user = self.env.user
        stock_manager_group = self.env.ref('stock.group_stock_manager')

        # Restrict location if not stock manager
        if stock_manager_group not in user.groups_id:
            allowed_ids = user.location_ids.ids or []
            if 'location_id' not in vals or vals['location_id'] not in allowed_ids:
                vals['location_id'] = allowed_ids[0] if allowed_ids else False

        # Get location record
        location = False
        if vals.get('location_id'):
            location = self.env['stock.location'].browse(vals['location_id'])

        # # Build prefix from location name (first 3 letters)
        # prefix = ''
        # if location:
        #     prefix = location.name[:3].upper() + '/IN/'
        #
        # # 1️⃣ Set 'name' field (existing logic)
        # seq_name = self.env['ir.sequence'].next_by_code('stock.request.order')
        # vals['name'] = prefix + seq_name
        #
        # prefix = ''
        # if location:
        #     prefix = location.name[:3].upper() + '/'
        # # 2️⃣ Set 'num_of_order' field using a different sequence
        # seq_num = self.env['ir.sequence'].next_by_code('my.stock.request.order')
        # vals['num_of_order'] = prefix + seq_num

        return super().create(vals)

    @api.depends('picking_type_id')
    def _compute_operation_type(self):
        for rec in self:
            if rec.picking_type_id and rec.picking_type_id.code:
                rec.operation_type = rec.picking_type_id.code.capitalize()
            else:
                rec.operation_type = 'Incoming'

    def _prepare_picking_moves(self):
        # Use the notebook (stock move lines) instead of hidden product lines
        lines = self.stock_request_ids or []

        if not lines:
            # Still raise error if truly empty
            raise UserError(_('Please add at least one product with a quantity.'))

        moves = []
        for line in lines:
            moves.append({
                'name': line.product_id.display_name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_uom_qty,
                'product_uom': line.product_uom_id.id,

                # REQUIRED FIELDS
                'location_id': self.location_id.id,  # SOURCE LOCATION
                'location_dest_id': self.location_dest_id.id,  # DESTINATION LOCATION

                'company_id': self.company_id.id,
                'picking_type_id': self.picking_type_id.id,
            })
        return moves


    def action_confirm(self):
        res = super().action_confirm()
        for rec in self:
            rec.state = 'sent'
        return res

    def action_confirm_manager(self):
        res = super().action_confirm()
        for rec in self:
            rec.state = 'confirmed'
        return res

    @api.depends('picking_type_id')
    def _compute_picking_type_code(self):
        for rec in self:
            rec.picking_type_code = rec.picking_type_id.code if rec.picking_type_id else False



class StockRequestProductLine(models.Model):
    _name = 'stock.request.product.line'
    _description = 'Stock Request Product Line'

    request_id = fields.Many2one(
        'stock.request.order',
        string="Request",
        ondelete='cascade',
        required=True
    )
    product_id = fields.Many2one('product.product', string="Product", required=True)
    product_uom_id = fields.Many2one('uom.uom', string="Unit of Measure", required=True)
    location_id = fields.Many2one(
        'stock.location',
        string='Source Location',
        related='request_id.location_id',  # always same as order
        store=True,
        readonly=True
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id
