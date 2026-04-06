{
    'name': "Test3 Module",
    'version': '1.2',
    'depends': ['base'],
    'author': "Bohdan",
    'category': 'Test',
    'description': """The test project for learning pivotal view and PDF reports""",
    'data': [
        'security/ir.model.access.csv',

        'report/customer_contact_templates.xml',
        'report/customer_contact_reports.xml',

        'views/customer_credits_views.xml',
        'views/customer_credits_menu.xml',
    ],
    'demo': [],
    # 'application': True,
}
