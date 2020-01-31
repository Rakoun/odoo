# -*- coding: utf-8 -*-
{
    'name': 'My Library Returns Date',
    'summary': "Manage return dates for books",
    'description': """Long description""",
    'author': "Régis GEROMEGNACE",
    'website': "http://www.example.com",
    'category': 'Uncategorized',
    'version': '12.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['my_library'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}