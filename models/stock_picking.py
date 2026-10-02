from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


# ==================================================
# Stock Picking
# ==================================================
class StockPicking(models.Model):
    _inherit = 'stock.picking'

    p_service = fields.Char(string="Service")
    request_id = fields.Many2one(
        'stock.request.order',
        string='Stock Request',
        index=True
    )
    num_of_order = fields.Char(string="Delivery Order Number")
    supp_name = fields.Char(string="Supplier Name", required=True)


    def _link_stock_request(self):
        for picking in self:
            if picking.request_id:
                continue

            request = False

            # Case 1: Outgoing picking → origin = request name
            if picking.origin:
                request = self.env['stock.request.order'].search(
                    [('name', '=', picking.origin)],
                    limit=1
                )

            # Case 2: Incoming picking → linked to Purchase Order
            if (
                    not request
                    and 'purchase_id' in picking._fields
                    and picking.purchase_id
            ):
                request = self.env['stock.request.order'].search(
                    [('purchase_order_id', '=', picking.purchase_id.id)],
                    limit=1
                )

            if request:
                picking.request_id = request.id
                picking.p_service = request.service
                _logger.info(
                    "Picking %s linked to request %s",
                    picking.name, request.name
                )

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

        # Build prefix from location name (first 3 letters)
        # prefix = ''
        # if location:
        #     prefix = location.name[:3].upper() + '/OUT/'
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

    def button_validate(self):
        res = super().button_validate()
        self._link_stock_request()

        for picking in self:
            if picking.request_id:
                picking.request_id.state = 'done'

        return res

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)

        picking_type = self.env.ref(
            'stock.picking_type_out',
            raise_if_not_found=False
        )
        if picking_type:
            res['picking_type_id'] = picking_type.id

        return res


# ==================================================
# Stock Move
# ==================================================
class StockMove(models.Model):
    _inherit = 'stock.move'

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        domain=[('type', 'in', ['product', 'consu', 'service'])],
        required=True
    )

    m_service = fields.Char(
        related='picking_id.p_service',
        store=True,
        string='Service'
    )


# ==================================================
# Stock Move Line
# ==================================================
class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    l_service = fields.Char(
        related='picking_id.p_service',
        store=True,
        string='Service'
    )
