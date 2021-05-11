from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta

class HelpdeskTicketAction(models.Model):
    _name = 'helpdesk.ticket.action'
    _description = 'Action'

    name = fields.Char()
    date = fields.Date()
    ticket_id = fields.Many2one(
        comodel_name='helpdesk.ticket',
        string='Ticket')

class HelpdeskTicketTag(models.Model):
    _name = 'helpdesk.ticket.tag'
    _description = 'Tag'

    name = fields.Char()
    public = fields.Boolean()    
    ticket_ids = fields.Many2many(
        comodel_name='helpdesk.ticket',
        relation='helpdesk_ticket_tag_rel',
        column1='tag_id',
        column2='ticket_id',
        string='Tickets')

    @api.model
    def cron_delete_tag(self):
        tickets = self.search([('ticket_ids', '=', False)])
        tickets.unlink()

class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _description='Ticket'

    def _date_default_today(self):
        return fields.Date.today()

    tag_ids = fields.Many2many(
        comodel_name='helpdesk.ticket.tag',
        relation='helpdesk_ticket_tag_rel',
        column1='ticket_id',
        column2='tag_id',
        string='Tags')

    action_ids = fields.One2many(
        comodel_name='helpdesk.ticket.action',
        inverse_name='ticket_id',
        string='Actions')
    name = fields.Char(
        string='Name',
        required=True)
    description = fields.Text(
        string='Description',
        translate=True)
    date = fields.Date(
        string='Date',
        default=_date_default_today)
    state = fields.Selection(
         [('nuevo', 'Nuevo'), 
         ('asignado', 'Asignado'), 
         ('proceso', 'En proceso'), 
         ('pendiente', 'Pendiente'), 
         ('resuelto', 'Resuelto'),
         ('cancelado', 'Cancelado')],
        string='State',
        default='nuevo') 
    time = fields.Float(
        string='Time') 
    assigned = fields.Boolean(
        string='Assigned',
        compute='_compute_assigned') 
    date_limit = fields.Date(
        string='Date Limit') 
    action_corrective = fields.Html(
        string='Corrective Action',
        help='Descrive corrective actions to do') 
    action_preventive = fields.Html(
        string='Preventive Action',
        help='Descrive preventive actions to do') 
    
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Assigned to')

    def asignar(self):
        self.ensure_one()
        self.write({
            'state': 'asignado',
            'assigned': True})

    def proceso(self):
        self.ensure_one()
        self.state = 'proceso'

    def pendiente(self):
        self.ensure_one()
        self.state = 'pendiente'

    def finalizar(self):
        self.ensure_one()
        self.state = 'resuelto'

    def cancelado(self):
        self.ensure_one()
        self.state = 'cancelado'

    @api.depends('user_id')
    def _compute_assigned(self):
        for record in self:
            record.assigned = self.user_id and True or False


    ticket_qty = fields.Integer(
        string='Ticket Qty',
        compute='_compute_ticket_qty')

    @api.depends('user_id')
    def _compute_ticket_qty(self):
        for record in self:
            other_tickets = self.env['helpdesk.ticket'].search([('user_id', '=', record.user_id.id)])
            record.ticket_qty = len(other_tickets)


    tag_name = fields.Char(
        string='Tag Name')        

    def create_tag(self):
        self.ensure_one()

        # self.write({
        #     'tag_ids': [(0,0, {'name': self.tag_name})]
        # })

        # self.tag_name = False
        # tag = self.env['helpdesk.ticket.tag'].create({
        #    'name': self.tag_name
        # })

        # tag = self.env['helpdesk.ticket.tag'].create({
        #     'name': self.tag_name,
        #     'ticket_ids': [(6, 0, self.ids)]
        # })

        # self.write({
        #     'tag_ids': [(4,tag.id, 0)]
        # })
        action = self.env.ref('helpdesk_marioherencia.action_new_tag').read()[0]
        action['context'] = {
            'default_name': self.tag_name,
            'default_ticket_ids': [(6, 0, self.ids)]
        }
        # action['res_id'] = tag.id
        self.tag_name = False
        return action


    @api.constrains('time')
    def _time_positive(self):
        for ticket in self:
            if ticket.time and ticket.time < 0:
                raise ValidationError(_("The time must be positive."))

    @api.onchange('date')
    def _onchange_date(self):
        date_limit = self.date and self.date + timedelta(days=1)
        self.date_limit = date_limit
