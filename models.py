# -*- coding: utf-8 -*-
 
from openerp import models, fields, api
from openerp.exceptions import Warning

# Clase Heredada - Empleado
class employee(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    salario = fields.Float(string='Salario Base')
    ccss = fields.Float(string='CCSS')

# Clase Calculo Salario
class calculo_salario(models.Model):
    _name = "calculo_salario"
    total_salario = fields.Float(compute='_calcular_salario', store=True, string="Total")
    ccss = fields.Float('CCSS:', readonly=True)
    rebajos = fields.Float(string='Rebajos')
    notas = fields.Text('Observaciones')
    planilla_id= fields.Many2one(comodel_name='planilla', string='Planilla ID', delegate=True, required=True)
    empleado_id= fields.Many2one(comodel_name='hr.employee', string='Empleado', delegate=True, required=True)
    lunes = fields.Selection([('1', 'Presente'), ('0', 'Ausente'), ('0.5', 'Medio Dia'), ('2', 'Feriado')  ])
    martes = fields.Selection([('1', 'Presente'), ('0', 'Ausente'), ('0.5', 'Medio Dia'), ('2', 'Feriado')  ])
    miercoles = fields.Selection([('1', 'Presente'), ('0', 'Ausente'), ('0.5', 'Medio Dia'), ('2', 'Feriado')  ])
    jueves = fields.Selection([('1', 'Presente'), ('0', 'Ausente'), ('0.5', 'Medio Dia'), ('2', 'Feriado')  ])
    viernes = fields.Selection([('1', 'Presente'), ('0', 'Ausente'), ('0.5', 'Medio Dia'), ('2', 'Feriado')  ])
    sabado = fields.Selection([('1', 'Presente'), ('0', 'Ausente'), ('0.5', 'Medio Dia'), ('2', 'Feriado')  ])
    _defaults = {
    'cajero_id': lambda self, cr, uid, ctx=None: uid
    }


# Calculo del Salario
    @api.one
    @api.depends('lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'empleado_id', 'rebajos')
    def _calcular_salario(self):
			salario_diario= float(self.empleado_id.salario) / 6
			dias_laborados= float(self.lunes) + float(self.martes) + float(self.miercoles) + float(self.jueves) + float(self.viernes) + float(self.sabado)
			total= (((salario_diario * dias_laborados) - float(self.empleado_id.ccss) - float(self.rebajos) ))
			self.total_salario= total

# Clase Planilla
class planillla(models.Model):
    _name = "planilla"
    _description = "Planilla"
    state = fields.Selection ([('new','Nuevo'), ('progress', 'En Proceso'), ('closed','Cerrado')], string='state', readonly=True)
    total_planilla_sanmiguel = fields.Float(compute='_calcular_planillas', store=True, string="Planilla San Miguel")
    total_planilla_parqueo = fields.Float(compute='_calcular_planillas', store=True, string="Planilla Parqueo")
    total_planilla_alajuelita = fields.Float(compute='_calcular_planillas', store=True, string="Planilla Alajuelita")
    total_planilla = fields.Float(string='Total')
    fecha_inicio = fields.Date(string='Fecha Inicio', required=True)
    fecha_final = fields.Date(string='Fecha Final',  required=True)
    calculo_salario_ids = fields.One2many(comodel_name='calculo_salario',inverse_name='planilla_id', string="Gastos")
    notas= fields.Text(string='Notas')
    total_planilla = fields.Float(compute='_calcular_planillas', store=True, string="Total")
    _defaults = { 
    'fecha_inicio': fields.Date.today(),
    'state': 'new'
    }

 	# Metodo: Calculo de Planillas
    @api.one
    @api.depends('calculo_salario_ids.lunes', 'calculo_salario_ids.martes', 'calculo_salario_ids.miercoles', 'calculo_salario_ids.jueves', 'calculo_salario_ids.viernes', 'calculo_salario_ids.ccss',  'calculo_salario_ids.rebajos' )
    def _calcular_planillas(self):
			total_planilla = 0 
			total_planilla_alajuelita = 0
			total_planilla_parqueo = 0
			total_planilla_sanmiguel = 0
			for calculo_salario in self.calculo_salario_ids:
				if str(calculo_salario.empleado_id.department_id.name) == "Alajuelita" :
					total_planilla += float(calculo_salario.total_salario)
					total_planilla_alajuelita += float(calculo_salario.total_salario)
					self.total_planilla = float(total_planilla)
					self.total_planilla_alajuelita = float(total_planilla_alajuelita)
				elif str(calculo_salario.empleado_id.department_id.name) == "Parqueo" :
					total_planilla += float(calculo_salario.total_salario)
					total_planilla_parqueo += float(calculo_salario.total_salario)
					self.total_planilla = float(total_planilla)
					self.total_planilla_parqueo = float(total_planilla_parqueo)
				elif str(calculo_salario.empleado_id.department_id.name) == "San Miguel" :
					total_planilla += float(calculo_salario.total_salario)
					total_planilla_sanmiguel += float(calculo_salario.total_salario)
					self.total_planilla = float(total_planilla)
					self.total_planilla_sanmiguel = float(total_planilla_sanmiguel)
				else : 
					raise Warning ("El Colaborador: " + str(employee.empleado_id.name) + " No tiene un departamento asignado")


# Generar lista de empleados   
    @api.one
    def action_generar_lista(self):
   		res= self.env['hr.employee'].search([('active', '=', 'True')])
   		for employee in res:
				self.calculo_salario_ids.create({'empleado_id': str(employee.id), 'ccss': str(employee.ccss), 'rebajos': '0', 'planilla_id': str(self.id) })
   		self.state= 'progress'	

# Cambiar el estado de la planilla a cerrado 
    @api.one
    def action_estado_planilla(self): 		
   		self.state= 'closed'	
