from odoo import models, fields, api, _


class HelpdeskTicket(models.Model):
    _name = 'helpdesk.ticket'
    _description = 'Ticket'
    _inherit = {'project.task': 'task_id'}


    task_id = fields.Many2one(
        comodel_name='project.task',
        string='Task',
        auto_join=True, index=True, ondelete="cascade", required=True)
    action_corrective = fields.Html(
        string='Corrective Action',
        help='Descrive corrective actions to do')
    action_preventive = fields.Html(
        string='Preventive Action',
        help='Descrive preventive actions to do')

    def action_assign_to_me(self):
        self.ensure_one()
        return self.task_id.action_assign_to_me()

    def action_subtask(self):
        self.ensure_one()
        return self.task_id.action_subtask()

    def action_recurring_tasks(self):
        self.ensure_one()
        return self.task_id.action_recurring_task()

    def _message_get_suggested_recipients(self):
        self.ensure_one()
        return self.task_id._message_get_suggested_recipients()