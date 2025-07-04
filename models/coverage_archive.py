from odoo import models, fields, api

class ProductStockCoverageArchive(models.Model):
    _name = 'product.stock.coverage.archive'
    _description = "Archive Couverture de Stock"

    product_tmpl_id = fields.Many2one('product.template', string="Produit", required=True)
    warehouse_id = fields.Many2one('stock.warehouse', string="Entrepôt")
    company_id = fields.Many2one('res.company', string="Société")
    qty_available_magasin = fields.Float(string="Qté magasin")
    qty_total_stock = fields.Float(string="Qté entrepôt")
    qty_sold_14d = fields.Float(string="Qté vendue (14j)")
    avg_daily_sale = fields.Float(string="VMJ")
    coverage_days = fields.Float(string="Couverture (jrs)")
    status = fields.Selection([
        ('ok', 'Suffisant'),
        ('low', 'Seuil d\'alerte'),
        ('order', 'À commander'),
        ('out', 'Plus de stock'),
        ('unknown', 'Inconnu'),
    ], string="Statut")
    archived_date = fields.Date(string="Date archivage", default=fields.Date.context_today)

    @api.model
    def archive_stock_data(self):
        lines = self.env['product.stock.coverage.line'].search([])
        for line in lines:
            self.create({
                'product_tmpl_id': line.product_tmpl_id.id,
                'warehouse_id': line.warehouse_id.id,
                'company_id': line.company_id.id,
                'qty_available_magasin': line.qty_available_magasin,
                'qty_total_stock': line.qty_total_stock,
                'qty_sold_14d': line.qty_sold_14d,
                'avg_daily_sale': line.avg_daily_sale,
                'coverage_days': line.coverage_days,
                'status': line.status,
            })

            def archive_now(self):
                self.archive_stock_data()

            def export_to_excel(self):
                import io
                import xlsxwriter
                from odoo.http import request

                buffer = io.BytesIO()
                workbook = xlsxwriter.Workbook(buffer)
                sheet = workbook.add_worksheet('Archives')

                headers = [
                    'Date', 'Produit', 'Entrepôt', 'Qté magasin', 'Qté stock',
                    'Qté vendue (14j)', 'VMJ', 'Couverture (j)', 'Statut'
                ]
                for idx, col in enumerate(headers):
                    sheet.write(0, idx, col)

                archives = self.search([], limit=1000)
                for row, rec in enumerate(archives, start=1):
                    sheet.write(row, 0, str(rec.archived_date or ''))
                    sheet.write(row, 1, rec.product_tmpl_id.name or '')
                    sheet.write(row, 2, rec.warehouse_id.name or '')
                    sheet.write(row, 3, rec.qty_available_magasin)
                    sheet.write(row, 4, rec.qty_total_stock)
                    sheet.write(row, 5, rec.qty_sold_14d)
                    sheet.write(row, 6, rec.avg_daily_sale)
                    sheet.write(row, 7, rec.coverage_days)
                    sheet.write(row, 8, rec.status or '')

                workbook.close()
                buffer.seek(0)

                return request.make_response(
                    buffer.getvalue(),
                    headers=[
                        ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                        ('Content-Disposition', 'attachment; filename="archives_stock.xlsx"')
                    ]
                )


