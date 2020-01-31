from odoo import models, fields, api

class LibraryMember(models.Model):
    _name = 'library.member'
    _inherits = {'res.partner' : 'partner_id'}
    partner_id = fields.Many2one('res.partner', ondelete='cascade')
    date_start = fields.Date('Member Since')
    date_end = fields.Date('Termination Date')
    member_number = fields.Char()
    date_of_birth = fields.Date('Date of birth')
