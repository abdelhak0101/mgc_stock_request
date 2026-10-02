# MGC Stock Request

Custom Odoo 14 module extending stock request and inventory workflows with location-based product access, stock visibility, manager validation, and stock picking integration.

## Overview

`mgc_stock_request` is an Odoo 14 customization built on top of Odoo Inventory and the existing Stock Request functionality.

The module adds custom stock request fields and workflows while restricting product visibility and stock quantities according to each user's allowed stock locations.

## Main Features

### Stock Request Customization

* Extends `stock.request.order`.
* Adds source and destination stock locations.
* Adds operation type and picking type information.
* Adds applicant, service, and order-related fields.
* Adds custom request states:

  * Draft
  * Sent to Manager
  * Confirmed
  * Open
  * Done
* Builds stock moves using the request's source and destination locations.
* Adds a custom stock request product line model.

### Location-Based Product Access

Users can be assigned specific **Allowed Locations**.

For regular stock users:

* Products are restricted according to their allowed locations.
* Product variants are restricted according to their allowed locations.
* Users cannot access products that have no stock in their allowed locations.
* Stock managers and system administrators have unrestricted product access.

The module implements this using both:

* Odoo record rules
* Python-level product filtering

### Allowed Stock Quantity

The module adds an **Allowed Qty** field to products.

For regular users, the quantity is calculated from stock quants located in their allowed locations.

Stock managers can see the total quantity available for the product.

If a user has no allowed locations, the allowed quantity is displayed as `0`.

### Stock Picking Integration

The module extends `stock.picking` with additional fields including:

* Stock Request
* Service
* Delivery Order Number
* Supplier Name

It can automatically link a stock picking to a stock request based on:

* The picking origin
* The related purchase order

When a linked picking is validated, the related stock request is moved to the `Done` state.

### Validation Email Notification

The module extends the tier validation process.

When a validation request is submitted, an email can be sent to users belonging to the **Stock Manager** group using the configured stock request email template.

### User Location Configuration

Additional fields are added to `res.users`:

* **Allowed Locations**
* **Delivery Source Location**

These fields are used by the custom location-based stock and product logic.

### Access Rights

Custom access rights are defined for the stock request product line model.

* Stock Request Users can read, create, and modify product lines.
* Stock Request Managers have full access, including deletion.

## Technical Stack

* **Odoo 14**
* **Python**
* **XML**
* **Odoo ORM**
* **PostgreSQL**
* **Odoo Inventory / Stock**
* **OCA Stock Request functionality**

## Module Structure

```text
mgc_stock_request/
├── data/
│   ├── sequence.xml
│   └── stock_request_mail_template_data.xml
├── i18n/
│   └── fr.po
├── models/
│   ├── delivery_stock_request.py
│   ├── product.py
│   ├── res_user.py
│   ├── stock_picking.py
│   └── tier_validation.py
├── reports/
│   └── stock_request_order_report.xml
├── security/
│   ├── ir.model.access.csv
│   └── security.xml
├── views/
│   ├── delivery_stock_request_view.xml
│   ├── product_template.xml
│   ├── res_users_view.xml
│   ├── stock_move_view.xml
│   ├── stock_picking_view.xml
│   └── stock_request_menu.xml
├── __init__.py
├── __manifest__.py
└── README.md
```

## Installation

1. Copy the `mgc_stock_request` directory into your Odoo addons path.
2. Make sure the required Odoo modules and dependencies are installed.
3. Restart the Odoo server.
4. Update the Apps list.
5. Search for the module.
6. Install the module.

## Dependencies

The module manifest declares the following dependencies:

* `stock`
* `stock_request`
* `stock_request_picking_type`

## Odoo Version

**Odoo 14.0**

## License

LGPL-3.0

## Credits

This customization extends existing Odoo and OCA Stock Request functionality.

The module manifest credits **ForgeFlow** and the **Odoo Community Association (OCA)** for the underlying Stock Request components.

This repository contains customizations and extensions built for the project's stock request and inventory requirements.

