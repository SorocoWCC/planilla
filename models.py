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

# Clase Calculo Salario
class calculo_salario(models.Model):
    _name = "calculo_salario"
    total_salario = fields.Float(compute='_calcular_salario', store=True, string="Total")
    ccss = fields.Float(compute='_action_ccss', string='CCSS', readonly=True)
    rebajos = fields.Float(string='Rebajos')
    ausencias = fields.Float(string='Ausencias')
    bonificaciones = fields.Float(string='Bonificación')
    feriados = fields.Float(string='Feriados')
    prestamos = fields.Float(string='Prestamos')
    saldo_prestamo = fields.Float(string='Saldo Prestamos')
    monto_prestamo = fields.Float(string='Total Prestamo')
    notas = fields.Text('Observaciones')
    planilla_id= fields.Many2one(comodel_name='planilla', string='Planilla ID', delegate=True, required=True)
    empleado_id= fields.Many2one(comodel_name='hr.employee', string='Empleado', delegate=True, required=True)
    lunes = fields.Selection([('1', 'Presente'), ('0', 'Ausente'), ('0.5', 'Medio Dia'), ('2', 'Feriado')  ], default="1")
    martes = fields.Selection([('1', 'Presente'), ('0', 'Ausente'), ('0.5', 'Medio Dia'), ('2', 'Feriado')  ], default="1")
    miercoles = fields.Selection([('1', 'Presente'), ('0', 'Ausente'), ('0.5', 'Medio Dia'), ('2', 'Feriado')  ], default="1")
    jueves = fields.Selection([('1', 'Presente'), ('0', 'Ausente'), ('0.5', 'Medio Dia'), ('2', 'Feriado')  ], default="1")
    viernes = fields.Selection([('1', 'Presente'), ('0', 'Ausente'), ('0.5', 'Medio Dia'), ('2', 'Feriado')  ], default="1")
    sabado = fields.Selection([('1', 'Presente'), ('0', 'Ausente'), ('0.5', 'Medio Dia'), ('2', 'Feriado')  ], default="1")
    _defaults = {
    'cajero_id': lambda self, cr, uid, ctx=None: uid

    }
#  Asigna el monto de la ccss
    @api.one
    @api.depends('empleado_id')
    def _action_ccss(self):
		self.ccss = float(self.empleado_id.ccss)

# Calculo del Salario
    @api.one
    @api.depends('lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'empleado_id', 'rebajos', 'bonificaciones', 'prestamos')
    def _calcular_salario(self):
			ausencias= 0
			feriados = 0
			salario_diario= float(self.empleado_id.salario) / 6
			dias_laborados= float(self.lunes) + float(self.martes) + float(self.miercoles) + float(self.jueves) + float(self.viernes) + float(self.sabado)
			
			# Calculo de salarios
			total= ((((salario_diario * dias_laborados) + self.bonificaciones )- float(self.empleado_id.ccss) - (float(self.rebajos) + float(self.prestamos) ) ))
			if total < 0 :
				self.total_salario= 0
			else :
				self.total_salario= total

			# Calculo de Ausencias
			if float(self.lunes) == 0 :
				ausencias += 1
			if float(self.martes) == 0 :
				ausencias += 1
			if float(self.miercoles) == 0 :
				ausencias += 1	
			if float(self.jueves) == 0 :
				ausencias += 1		
			if float(self.viernes) == 0 :
				ausencias += 1
			if float(self.sabado) == 0 :
				ausencias += 1

			self.ausencias = ausencias * salario_diario

			# Calculo de Feriados
			if float(self.lunes) == 2 :
				print 'Lunes'
				feriados += 1
			if float(self.martes) == 2 :
				print 'Martes'
				feriados += 1
			if float(self.miercoles) == 2 :
				print 'miercoles'
				feriados += 1	
			if float(self.jueves) == 2 :
				print 'jueves'
				feriados += 1		
			if float(self.viernes) == 2 :
				print 'viernes'
				feriados += 1
			if float(self.sabado) == 2 :
				print 'sabado'
				feriados += 1

			self.feriados = feriados * salario_diario

# Clase Planilla
class planillla(models.Model):
    _name = "planilla"
    _description = "Planilla"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    state = fields.Selection ([('new','Nuevo'), ('progress', 'En Proceso'), ('closed','Cerrado')], string='state', readonly=True)
    name = fields.Char(compute='_action_name', string='Nombre', readonly=True)
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

#  Asigna el nombre de la planilla
    @api.one
    def _action_name(self):
		self.name = "Planilla " + str(self.fecha_inicio) + " al " + str(self.fecha_final)

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
   				if employee.department_id.name == "San Miguel" or employee.department_id.name == "Alajuelita" or employee.department_id.name == "Parqueo" : 
					self.calculo_salario_ids.create({'empleado_id': str(employee.id), 'ccss': str(employee.ccss), 'rebajos': '0', 'planilla_id': str(self.id) })
   		self.state= 'progress'	

# Cambiar el estado de la planilla a cerrado y procesar abonos a prestamos
    @api.one
    def action_estado_planilla(self): 		
   		lista_prestamos= self.env['empleado.allowance'].search([('state', '=', 'new')])
   		# Notas para incluir en el detalle del abono
   		notas = 'Planilla del ' + str(self.fecha_inicio) + ' al ' + str(self.fecha_final)
   		for employee in self.calculo_salario_ids:
   			# valida si hay un abono al prestamos en la planilla
   			if employee.prestamos > 0 :
   				# Busca si el empleado tiene un prestamo activo
   				for prestamo in lista_prestamos :
   					if employee.empleado_id == prestamo.res_employee_id :
					# Valida si tiene el salario suficiente para abonar al prestamo
						if employee.total_salario > 0 :
							# Valida si todavia hay saldo en el prestamo antes de hacer el abono
							if prestamo.saldo >= employee.prestamos :
								# Crea el abono al prestamos
								prestamo.abono_ids.create({'libro_id': str(prestamo.id), 'monto': float(employee.prestamos), 'notas': str(notas) })
							else :
								raise Warning ("El Colaborador: " + str(employee.empleado_id.name) + " El abono al prestamo excede su saldo.")	
   						else :
   							raise Warning ("El Colaborador: " + str(employee.empleado_id.name) + " No tiene salario sufuciente para aplicar un abono al prestamo")	

   		# Estado de los prestamos para mostrar en el reporte de planilla
   		for employee in self.calculo_salario_ids:
   		 	for prestamo in lista_prestamos :
   				if employee.empleado_id == prestamo.res_employee_id :
   					employee.saldo_prestamo = prestamo.saldo
   					employee.monto_prestamo = prestamo.total_amortizable
   		#Cierra la planilla					
   		self.state= 'closed'

# --------------------------   FINIQUITO LABORAL ----------------------
class finiquito_laboral(models.Model):
    _name = "finiquito_laboral"
    _description = "Finiquito Laboral"
    state = fields.Selection ([('new','Nuevo'), ('cancel','Cancelado'), ('closed','Cerrado')], string='state', readonly=True)
    name = fields.Char( string='Nombre', readonly=True)
    responsable = fields.Char( string='Responsable', readonly=True)
    total = fields.Float(string='Total',)
    fecha_inicio = fields.Date(string='Fecha Inicio', required=True)
    fecha_final = fields.Date(string='Fecha Final',  required=True)
    empleado_id= fields.Many2one(comodel_name='hr.employee', string='Empleado', delegate=True, required=True)

    _defaults = { 
      'state': 'new',
    }

# Calcular el monto del finiquito laboral
    @api.onchange('empleado_id')
    def _action_calcular_finiquito(self):
      vacaciones = (((float(self.empleado_id.salario) * 4.33 ) / 30 ) * 3)
      aguinaldo =  (((float(self.empleado_id.salario) * 4.33 ) / 12 ) * 3)
      self.total = vacaciones + aguinaldo

# Cambiar el estado de la planilla a cerrado
    @api.one
    def action_estado_cerrado(self):
      self.responsable = str(self.env.user.name)
      self.empleado_id.fecha_ultimo_finiquito = self.fecha_final
      self.empleado_id.fecha_proximo_finiquito = str(datetime.datetime.strptime(self.fecha_final, '%Y-%m-%d') + datetime.timedelta(days=91) )
      self.state= 'closed'

# Cambiar el estado de la planilla a cancelado
    @api.one
    def action_estado_cancelado(self):
      self.responsable = str(self.env.user.name)  
      self.state= 'cancel'

# --------------------------   PLANILLAS POR PRODUCCION ----------------------



