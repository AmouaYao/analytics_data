from odoo import models, fields

class StockLocation(models.Model):
    _inherit = 'stock.location'

    is_entrepot_central = fields.Boolean("Est un entrepôt central", compute="_compute_is_entrepot_central", store=True)

    def _compute_is_entrepot_central(self):
        warehouse_lots = self.env['stock.warehouse'].search([]).mapped('lot_stock_id.id')
        for location in self:
            location.is_entrepot_central = location.id in warehouse_lots
