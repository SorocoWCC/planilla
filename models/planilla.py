# -*- coding: utf-8 -*-
 
from openerp import models, fields, api
from openerp import api
from openerp.exceptions import Warning
import datetime


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
            feriados += 1
        if float(self.martes) == 2 :
            feriados += 1
        if float(self.miercoles) == 2 :
            feriados += 1	
        if float(self.jueves) == 2 :
            feriados += 1		
        if float(self.viernes) == 2 :
            feriados += 1
        if float(self.sabado) == 2 :
            feriados += 1

        self.feriados = feriados * salario_diario



# Clase Planilla
class planillla(models.Model):
   
    _name = "planilla"
    _description = "Planilla"
    _inherit = 'mail.thread'
    name = fields.Char(string='Name', readonly=True, copy=False)
    state = fields.Selection ([('new','Nuevo'), ('progress', 'En Proceso'), ('closed','Cerrado')], string='state', readonly=True, default='new')
    total_planilla = fields.Float(string='Total')
    fecha_inicio = fields.Date(string='Fecha Inicio', required=True)
    fecha_final = fields.Date(string='Fecha Final',  required=True)
    calculo_salario_ids = fields.One2many(comodel_name='calculo_salario',inverse_name='planilla_id', string="Gastos")
    notas= fields.Text(string='Notas')
    total_planilla = fields.Float(compute='_calcular_planillas', store=True, string="Total")


    # Generar lista de empleados   
    @api.one
    def action_generar_lista(self):
        lista_empleados= self.env['hr.employee'].search([('active', '=', 'True')])
        # Aplica el abono al prestamo  
        for employee in lista_empleados:
            abono_prestamo = 0
            prestamo= self.env['prestamo'].search([['tipo', '=', 'empleado'], ['state', '=', 'abierto'], ['empleado_id.id', '=', employee.id]])

            if prestamo:
                if prestamo[0].saldo >= 10000:
                    abono_prestamo = 10000
                else:
                    abono_prestamo = prestamo[0].saldo

            self.calculo_salario_ids.create({'empleado_id': str(employee.id), 'ccss': str(employee.ccss), 'rebajos': '0', 'prestamos': abono_prestamo,  'planilla_id': str(self.id) })
        self.name = str("Planilla " + str(self.fecha_inicio) + " al " + str(self.fecha_final))
        self.state= 'progress'	

    @api.one
    @api.depends('calculo_salario_ids.lunes', 'calculo_salario_ids.martes', 'calculo_salario_ids.miercoles', 'calculo_salario_ids.jueves',
     'calculo_salario_ids.viernes','calculo_salario_ids.ccss',  'calculo_salario_ids.rebajos', 'calculo_salario_ids.sabado', 'calculo_salario_ids.sabado',
     'calculo_salario_ids.prestamos', 'calculo_salario_ids.bonificaciones' )
    def _calcular_planillas(self):

        for employee in self.calculo_salario_ids:
            self.total_planilla += employee.total_salario 

# Cambiar el estado de la planilla a cerrado y procesar abonos a prestamos
    @api.multi
    def action_cerrar_planilla(self):       
        # Notas para incluir en el detalle del abono
        notas = 'Planilla del ' + str(self.fecha_inicio) + ' al ' + str(self.fecha_final)
        for employee in self.calculo_salario_ids:
            # valida si hay un abono al prestamos en la planilla
            if employee.prestamos > 0 :
                prestamo= self.env['prestamo'].search([['tipo', '=', 'empleado'], ['state', '=', 'abierto'], ['empleado_id.id', '=', employee.empleado_id.id]])
                
                # Valida si el empleado tiene prestamo
                if prestamo:
                    
                    if employee.prestamos <= prestamo[0].saldo:
                        prestamo[0].abono_ids.create({'detalle': self.name, 'monto': employee.prestamos, 'prestamo_id': prestamo[0].id})
                    else:
                        # En caso que el abono al prestamo sea mayor que el saldo
                        employee.prestamos = prestamo[0].saldo
                        prestamo[0].abono_ids.create({'detalle': self.name, 'monto': employee.prestamos, 'prestamo_id': prestamo[0].id})
                else:
                    # En caso de abono prestamo mal aplicado 
                    employee.prestamos = 0
        self.total_planilla += employee.total_salario             

        # Estado de los prestamos para mostrar en el reporte de planilla
        for employee in self.calculo_salario_ids:
            prestamos= self.env['prestamo'].search([['tipo', '=', 'empleado'], ['state', '=', 'abierto'], ['empleado_id.id', '=', employee.empleado_id.id]])
            if prestamos:
                for i in prestamos:
                    employee.saldo_prestamo += i.saldo
                    employee.monto_prestamo += i.monto
        # Cierra la planilla                  
        self.state= 'closed'
'''
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
'''