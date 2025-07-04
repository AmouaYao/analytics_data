{
    'name': 'Coverage Analytics',
    'version': '1.0',
    'category': 'Inventory',
    'summary': 'Couverture analytic de données commerciale par magasin',
    'author': 'TonNom',
    'depends': ['product', 'stock', 'sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/coverage_cron.xml',
        'views/analyses_coverage_views.xml',
        'views/coverage_archive_views.xml',

    ],
    'installable': True,
    'application': False,
}
