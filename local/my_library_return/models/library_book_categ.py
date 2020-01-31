from odoo import models, fields, api

class BookCategory(models.Model):
    inherit = 'library.book.category'

    max_borrow_days = fields.Integer('Maximum borrow days', help='For how many days book can be borrow', default = 10)