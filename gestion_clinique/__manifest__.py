# -*- coding: utf-8 -*-
{
    'name': 'Gestion Clinique',
    'description': 'Gestion Clinique',
    'version': '1.0',
    'category': 'MEDECINE',
    'depends': [
        'base',
        'report',
        'mail',
    ],
    'author': 'Aliou Samba WELE',
    'website': 'www.gestion-clinique-demba-toure.com',
    'license': 'AGPL-3',
    'data': [
        'data/sequence.xml',
        'report/gestion_clinique_reports.xml',
        'report/recette_depense_template.xml',
        'data/mail_template_data.xml',
        'security/gestion_clinique_security.xml',
        'security/ir.model.access.csv',
        'views/gestion_clinique_views.xml',
    ],
    'demo': [

    ],
    'installable': True,
    'application': True,
}
