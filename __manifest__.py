# Copyright 2017-2020 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "Deliviry Stock Request",
    "summary": "Internal request for stock",
    "version": "14.0.1.9.0",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/stock-logistics-warehouse",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "category": "Warehouse Management",
    "depends": ["stock", "stock_request", "stock_request_picking_type"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/stock_request_mail_template_data.xml",
        "data/sequence.xml",
        "views/delivery_stock_request_view.xml",
        "views/stock_request_menu.xml",
        "views/stock_move_view.xml",
        "views/stock_picking_view.xml",
        "views/res_users_view.xml",
        "views/product_template.xml",
        "reports/stock_request_order_report.xml",
    ],
    "installable": True,
}
