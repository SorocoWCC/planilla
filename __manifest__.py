# -*- coding: utf-8 -*-
{
    'name': "planillas",

    'summary': """
       San MIguel - Manejo de Planillas""",

    'description': """
        Manejo de Planillas
    """,

    'author': "Warren Castro",
    'website': "http://www.recicladorasanmiguel.com.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr'],
    # always loaded
    'data': [
        'views/planilla.xml',
        'views/employee.xml',
        'planillas_report.xml',       
        'views/report_planilla.xml',
        'views/report_asistencia.xml',
        'views/report_firmas.xml',
        'views/report_sobres.xml'
        #'views/report_abonos.xml',
        #'views/report_finiquito_laboral.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}
