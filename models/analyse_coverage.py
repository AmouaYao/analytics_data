from odoo import models, fields


class ProductStockCoverageLine(models.Model):
    _name = 'product.stock.coverage.line'
    _description = "Analyse Couverture Stock"
    _auto = False

    id = fields.Integer()
    product_tmpl_id = fields.Many2one('product.template', string="Produit", readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', string="Entrepôt", readonly=True)
    location_id = fields.Many2one('stock.location', string="Emplacement", readonly=True)
    qty_available_magasin = fields.Float(string="Stock magasin(s)", readonly=True)
    qty_total_stock = fields.Float(string="Stock entrepôt(s)", readonly=True)
    uom_id = fields.Many2one('uom.uom', string="Unité de Mesure", readonly=True)
    qty_sold_14d = fields.Float(string="Ventes/(14j)", readonly=True)
    avg_daily_sale = fields.Float(string="VMJ (14j)", readonly=True)
    coverage_days = fields.Float(string="Couverture (jours)", readonly=True)
    company_id = fields.Many2one('res.company', string="Société", readonly=True, index=True)
    status = fields.Selection([
        ('ok', 'Suffisant'),
        ('low', 'Seuil d\'alerte'),
        ('order', 'À commander'),
        ('out', 'Rupture de stock'),
    ], string="Statut", readonly=True)
    storage_type = fields.Selection([
        ('entrepot', 'Entrepôt'),
        ('magasin', 'Magasin')
    ], string="Type de stockage", readonly=True)

    def init(self):
        self.env.cr.execute("DROP VIEW IF EXISTS product_stock_coverage_line CASCADE")
        self.env.cr.execute("""
            CREATE VIEW product_stock_coverage_line AS (
                WITH 
                stock_entrepot AS (
                    SELECT 
                        pt.id AS product_tmpl_id,
                        sl.company_id,
                        SUM(sq.quantity) AS qty_entrepot
                    FROM stock_quant sq
                    JOIN stock_location sl ON sl.id = sq.location_id
                    JOIN product_product pp ON pp.id = sq.product_id
                    JOIN product_template pt ON pt.id = pp.product_tmpl_id
                    WHERE sl.usage = 'internal' AND sl.complete_name LIKE 'WH/Stock%'
                    GROUP BY pt.id, sl.company_id
                ),

                stock_magasin AS (
                    SELECT 
                        pt.id AS product_tmpl_id,
                        sl.company_id,
                        SUM(sq.quantity) AS qty_magasin
                    FROM stock_quant sq
                    JOIN stock_location sl ON sl.id = sq.location_id
                    JOIN product_product pp ON pp.id = sq.product_id
                    JOIN product_template pt ON pt.id = pp.product_tmpl_id
                    WHERE sl.usage = 'internal' AND sl.complete_name NOT LIKE 'WH/Stock%'
                    GROUP BY pt.id, sl.company_id
                ),

                ventes_14j AS (
                    SELECT 
                        pt.id AS product_tmpl_id,
                        so.warehouse_id,
                        SUM(sol.product_uom_qty) AS qty_vendue
                    FROM sale_order_line sol
                    JOIN sale_order so ON so.id = sol.order_id
                    JOIN product_product pp ON pp.id = sol.product_id
                    JOIN product_template pt ON pt.id = pp.product_tmpl_id
                    JOIN stock_warehouse sw ON sw.id = so.warehouse_id
                    JOIN stock_location sl ON sl.id = sw.lot_stock_id
                    WHERE so.state IN ('sale', 'done')
                      AND so.date_order >= NOW() - INTERVAL '14 days'
                      AND sl.complete_name NOT LIKE 'WH/Stock%'
                    GROUP BY pt.id, so.warehouse_id
                ),

                derniere_vente AS (
                    SELECT 
                        pt.id AS product_tmpl_id,
                        so.warehouse_id,
                        MAX(so.date_order) AS last_sale_date
                    FROM sale_order_line sol
                    JOIN sale_order so ON so.id = sol.order_id
                    JOIN product_product pp ON pp.id = sol.product_id
                    JOIN product_template pt ON pt.id = pp.product_tmpl_id
                    WHERE so.state IN ('sale', 'done')
                    GROUP BY pt.id, so.warehouse_id
                )

                SELECT
                    ROW_NUMBER() OVER() AS id,
                    pt.id AS product_tmpl_id,
                    sw.id AS warehouse_id,
                    sl.id AS location_id,
                    pt.uom_id,
                    sw.company_id,

                    COALESCE(sm.qty_magasin, 0) AS qty_available_magasin,
                    COALESCE(se.qty_entrepot, 0) AS qty_total_stock,
                    COALESCE(v14.qty_vendue, 0) AS qty_sold_14d,

                    CASE 
                        WHEN v14.qty_vendue IS NULL THEN NULL
                        ELSE ROUND(v14.qty_vendue / 14.0, 2)
                    END AS avg_daily_sale,

                    CASE 
                        WHEN v14.qty_vendue IS NULL OR v14.qty_vendue = 0 THEN NULL
                        ELSE ROUND(COALESCE(sm.qty_magasin, 0) / NULLIF(v14.qty_vendue / 14.0, 0), 2)
                    END AS coverage_days,

                    CASE
                        WHEN COALESCE(sm.qty_magasin, 0) = 0 AND COALESCE(se.qty_entrepot, 0) > 0 THEN 'order'
                        WHEN COALESCE(sm.qty_magasin, 0) > 0 AND (v14.qty_vendue IS NULL OR v14.qty_vendue = 0) THEN 'ok'
                        WHEN v14.qty_vendue IS NOT NULL AND (COALESCE(sm.qty_magasin, 0) / NULLIF(v14.qty_vendue / 14.0, 0)) < 7 THEN 'low'
                        WHEN v14.qty_vendue IS NOT NULL AND (COALESCE(sm.qty_magasin, 0) / NULLIF(v14.qty_vendue / 14.0, 0)) < 14 THEN 'order'
                        WHEN COALESCE(sm.qty_magasin, 0) = 0 AND COALESCE(se.qty_entrepot, 0) = 0 THEN 'out'
                        ELSE 'ok'
                    END AS status,

                    CASE
                        WHEN sl.complete_name LIKE 'WH/Stock%' THEN 'entrepot'
                        ELSE 'magasin'
                    END AS storage_type,

                    dv.last_sale_date

                FROM product_template pt
                CROSS JOIN stock_warehouse sw
                JOIN stock_location sl ON sl.id = sw.lot_stock_id

                LEFT JOIN stock_entrepot se 
                    ON se.product_tmpl_id = pt.id AND se.company_id = sw.company_id
                LEFT JOIN stock_magasin sm 
                    ON sm.product_tmpl_id = pt.id AND sm.company_id = sw.company_id
                LEFT JOIN ventes_14j v14 
                    ON v14.product_tmpl_id = pt.id AND v14.warehouse_id = sw.id
                LEFT JOIN derniere_vente dv 
                    ON dv.product_tmpl_id = pt.id AND dv.warehouse_id = sw.id

                GROUP BY 
                    pt.id, sw.id, sl.id, pt.uom_id, sw.company_id,
                    se.qty_entrepot, sm.qty_magasin, v14.qty_vendue, dv.last_sale_date,
                    sl.complete_name
            )
        """)
