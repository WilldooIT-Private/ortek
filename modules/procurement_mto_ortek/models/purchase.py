"""
The brief was quite explicit.

Procurement Orders for MTO items should never consolidate across
mltiple sales.

We could use the standard Odoo fields, but for non
identified drop shippings, etc, we don't want to risk altering
behaviour.

Our logic is to update the standard fields.

And, maintain a new value which identifies this PO differently.

Also, the description from the Sales Order, explicitly, is to go on the
Purchase Order.
"""

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    ortek_mto_so_id = fields.Many2one('sale.order', readonly=True)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _find_candidate(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values):
        if values.get('ortek_mto_so_line'):
            # ensure never merged, even if twice on same sale order
            return self.env['purchase.order.line']
        return super()._find_candidate(product_id, product_qty, product_uom, location_id, name, origin, company_id, values)

    @api.model
    def _prepare_purchase_order_line_from_procurement(self, product_id, product_qty, product_uom, company_id, values, po):
        result = super()._prepare_purchase_order_line_from_procurement(product_id, product_qty, product_uom, company_id, values, po)
        if values.get('ortek_mto_so_line'):
            result['name'] = values['ortek_mto_so_line'].name
        return result
