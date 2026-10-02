from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    location_ids = fields.Many2many(
        'stock.location',
        'res_users_stock_location_rel',
        'user_id',
        'location_id',
        string='Allowed Locations',
        help="The user will only see products available in these stock locations."
    )
    delivery_source_location_id = fields.Many2one(
        'stock.location',
        string='Delivery Source Location',
        help='Default source location for Delivery Orders created by this user.'
    )
