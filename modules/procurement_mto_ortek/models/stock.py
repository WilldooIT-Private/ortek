from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    ortek_mto_so_line_id = fields.Many2one('sale.order.line', readonly=True)

    def _prepare_procurement_values(self):
        result = super()._prepare_procurement_values()

        if self.ortek_mto_so_line_id:
            result['ortek_mto_so_line'] = self.ortek_mto_so_line_id
        elif self.procure_method == 'make_to_order' and self.sale_line_id:
            result['ortek_mto_so_line'] = self.sale_line_id
        return result


class StockRule(models.Model):
    _inherit = 'stock.rule'

    @api.model
    def _ortek_mto_so_line(self, values):
        return values.get('ortek_mto_so_line') or self.env['sale.order.line']

    def _get_custom_move_fields(self):
        result = super()._get_custom_move_fields()
        result.append('ortek_mto_so_line_id')
        return result

    def _make_po_get_domain(self, company_id, values, partner):
        """ Avoid to merge two RFQ for the same MPS replenish. """
        domain = super()._make_po_get_domain(company_id, values, partner)

        domain += (('ortek_mto_so_id', '=', self._ortek_mto_so_line(values).order_id.id),)
        return domain

    def _prepare_purchase_order(self, company_id, origins, values):
        result = super()._prepare_purchase_order(company_id, origins, values)
        if values:
            result['ortek_mto_so_id'] = self._ortek_mto_so_line(values[0]).order_id.id
        return result

    @api.model
    def _get_procurements_to_merge_groupby(self, procurement):
        """ Do not group purchase order line if they are linked to different
        sale order line. The purpose is to compute the delivered quantities.
        """
        return self._ortek_mto_so_line(procurement.values).id, super()._get_procurements_to_merge_groupby(procurement)

    @api.model
    def _get_procurements_to_merge_sorted(self, procurement):
        return self._ortek_mto_so_line(procurement.values).id, super(StockRule, self)._get_procurements_to_merge_sorted(procurement)

