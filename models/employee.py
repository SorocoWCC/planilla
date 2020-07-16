# -*- coding: utf-8 -*-
 
from openerp import models, fields, api
from openerp import api
from openerp.exceptions import Warning
import datetime

# Clase Heredada - Empleado
class employee(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    salario = fields.Float(string='Salario Base')
    ccss = fields.Float(string='CCSS')
    fecha_ultimo_finiquito = fields.Date(string='Último Finiquito', readonly=True)
    fecha_proximo_finiquito = fields.Date(string='Próximo Finiquito')