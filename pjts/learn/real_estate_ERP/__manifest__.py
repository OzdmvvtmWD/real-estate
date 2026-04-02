{
    'name': "Real Estate",
    'version': '1.2',
    'depends': ['base'],
    'author': "Bohdan",
    'category': 'Real Estate',
    'description': """The test project""",
    # data files always loaded at installation
    'data': [
        'security/ir.model.access.csv',

        'data/inherit_user_views.xml',
        'data/property_tag_views.xml',
        'data/offer_views.xml',
        'data/property_type_views.xml',
        'data/estate_property_views.xml',
        'data/estate_menus.xml',
    ],
    # data files containing optionally loaded demonstration data
    'demo': [
        #'demo/demo_data.xml',
    ],
    'application': True,

}