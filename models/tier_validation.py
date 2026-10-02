from odoo import models, fields, api


class TierValidation(models.AbstractModel):
    _inherit = "tier.validation"


    def request_validation(self):
        res = super(TierValidation, self).request_validation()

        template = self.env.ref('mgc_stock_request.email_template_stock_request', raise_if_not_found=False)
        if template:
            for rec in self:
                # Example: manager is the stock manager group
                managers = self.env.ref('stock.group_stock_manager').users
                if managers:
                    # Set email_to to managers' emails
                    email_list = ','.join(managers.mapped('email'))
                    template.email_to = email_list
                    template.email_from = self.env.user.email  # sender is current user
                    template.send_mail(rec.id, force_send=True)

        return res