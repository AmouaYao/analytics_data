{
    'name': 'Coverage Analytics',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Couverture analytic de données commerciale par magasin',
    'author': 'TonNom',
    'depends': ['product', 'stock', 'sale'],
    'data': [
        'data/coverage_cron.xml',
        'views/analyses_coverage_views.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
}
