import logging

from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
from odoo.exceptions import ValidationError
from datetime import timedelta
from odoo.exceptions import UserError
from odoo.tools.translate import _

logger = logging.getLogger(__name__)

class LibraryBook(models.Model):
    _name = 'library.book'
    _inherit = ['base.archive']
    _description = 'Library book' #add a user-friendly title to the model
    _order = 'date_release desc, name' #To sort the records first (from newer to older, and then by title)
    _rec_name = 'short_name' #To use the short_name field as the record representation
    short_name = fields.Char('Short Title', required = 'True')
    notes = fields.Text(('Internal notes'))
    state = fields.Selection(
        [('draft', 'Unavailable'),
         ('available', 'Available'),
         ('borrowed', 'Borrowed'),
         ('lost', 'Lost')],
        'State', default = "draft"
    )
    description = fields.Html('Description')
    cover = fields.Binary('Book cover')
    out_of_print = fields.Boolean('Out of print?')
    name = fields.Char('Title', required=True)
    date_release = fields.Date('Release Date')
    date_update = fields.Datetime('Last updated')
    pages = fields.Integer('Number of pages')
    author_ids = fields.Many2many('res.partner', string='Authors')
    cost_price = fields.Float('Book Cost', dp.get_precision('Book Price'))
    currency_id = fields.Many2one('res.currency', string='Currency')
    retail_price = fields.Monetary(
            'Retail Price',
            #optioanal: currency_field = 'currency_id',
    )
    publisher_id = fields.Many2one('res.partner', string='Publisher',
        #optional
        ondelete='set null',
        context={},
        domain=[])

    publisher_city = fields.Char(
        'Publisher City',
        related='publisher_id.city',
        readonly=True
    )

    category_id = fields.Many2one('library.book.category')
    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (name)',
         'Book Title must be unique')
        ]

    age_days = fields.Float(
        string="Days since release",
        compute="_compute_age",
        inverse="_inverse_age",
        search="_search_age",
        store=False, #optional
        compute_sudo=False #optional
    )

    manager_remarks = fields.Text('Manager Remarks')
    old_edition = fields.Many2one('library.book', string='Old Edition')

    @api.model
    def _referencable_models(self):
        #models = self.env['ir.model'].search([('field_id.name', '=', 'message_ids')])
        #return [(x.model, x.name) for x in models]
        return [('res.users', 'User'), ('res.partner', 'Partner')]


    ref_doc_id = fields.Reference(selection='_referencable_models', string='Reference Document')

    @api.constrains('date_release')
    def _check_release_date(self):
        for record in self:
            if record.date_release and record.date_release > fields.Date.today():
                raise models.ValidationError('Release date must be in the past')

    @api.depends('date_release')
    def _compute_age(self):
        today = fields.Date.today()
        for book in self.filtered('date_release'):
            delta = today - book.date_release
            book.age_days = delta.days

    @api.depends('age_days')
    def _inverse_age(self):
        today = fields.Date.today()
        for book in self.filtered('date_release'):
            d = today - timedelta(days=book.age_days)
            book.date_release = d

    def _search_age(self, operator, value):
        today = fields.Date.today()
        value_days = timedelta(days=value)
        value_date = today - value_days
        # convert the operator:
        # book with age > value have a date < value_date
        operator_map = { '>': '<', '>=': '<=', '<': '>', '<=': '>=', }
        new_op = operator_map.get(operator, operator)
        return [('date_release', new_op, value_date)]

    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [
            ('draft', 'available'),
            ('available', 'borrowed'),
            ('borrowed', 'available'),
            ('available', 'lost'),
            ('borrowed', 'lost'),
            ('lost', 'available')]

        return (old_state, new_state) in allowed

    @api.multi
    def change_state(self, new_state):
        for book in self:
            if book.is_allowed_transition(book.state, new_state):
                book.state = new_state
            else:
                msg = _('Moving from %s to %s is not allowed') % (book.state, new_state)
                raise UserError(msg)

    def make_available(self):
        self.change_state('available')

    def make_borrowed(self):
        self.change_state('borrowed')

    def make_lost(self):
        self.change_state('lost')

    @api.model
    def get_all_library_members(self):
        library_member_model = self.env['library.member']
        return library_member_model.search([])

    def create_categories(self):
        categ1 = {'name': 'Child category 1', 'description': 'Description for child 1'}
        categ2 = {'name': 'Child category 2', 'description': 'Description for child 2'}
        parent_category_val = {
            'name': 'Parent category',
            'email': 'Description for parent category',
            'child_ids': [
                (0, 0, categ1),
                (0, 0, categ2),
            ]
        }

        record = self.env['library.book.category'].create(parent_category_val)

    @api.multi
    def change_update_date(self):
        self.ensure_one()
        self.date_update = fields.Datetime.now()

    def find_book(self):
        domain = [
            '|',
                '&',    ('name', 'ilike', 'Book Name'),
                        ('category_id.name', 'ilike', 'Category Name'),
                '&',    ('name', 'ilike', 'Book Name 2'),
                        ('category_id.name', 'ilike', 'Category Name 2')
        ]
        books = self.search(domain)

        logger.info('Books found: %s', books)
        return True

    def filter_books(self):
        all_books = self.search([])
        filtered_books = self.books_with_multiple_authors(all_books)
        logger.info('Filtered Books: %s', filtered_books)

    @api.model
    def books_with_multiple_authors(self, all_book):
        def predicate(book):
             if len(book.author_ids) > 1:
                 return True
             else:
                return False
        result = all_book.filtered(predicate)
        return all_book

    def mapped_books(self):
        all_books = self.search([])
        books_authors = self.get_author_names(all_books)
        logger.info('Books Authors: %s', books_authors)

    @api.model
    def get_author_names(self, books):
        return books.mapped('author_ids.name')

    def sort_books(self):
        all_books = self.search([])
        books_sorted = self.sort_books_by_date(all_books)
        logger.info('Books before sorting: %s', all_books)
        logger.info('Books after sorting: %s', books_sorted)

    @api.model
    def sort_books_by_date(self, books):
        return books.sorted(key='date_release')

    @api.model
    def create(self, values):
        if not self.user_has_groups('my_library.acl_book_librarian'):
            if 'manager_remarks' in values: raise UserError( 'You are not allowed to modify ' 'manager_remarks' )
        return super(LibraryBook, self).create(values)

    @api.multi
    def write(self, values):
        test =  self.user_has_groups('my_library.acl_book_librarian')
        if not self.user_has_groups('my_library.acl_book_librarian'):
            if 'manager_remarks' in values:
                raise UserError( 'You are not allowed to modify ' 'manager_remarks' )
        return super(LibraryBook, self).write(values)

    @api.multi
    def name_get(self):
        result = []

        for book in self:
            authors = book.author_ids.mapped('name')
            name = '%s (%s)' % (book.name, ', '.join(authors))
            result.append((book.id, name))
            return result

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        args = [] if args is None else args.copy()
        if not(name == '' and operator == 'ilike'):
            args += ['|', '|',
                     ('name', operator, name),
                     ('isbn', operator, name),
                     ('author_ids.name', operator, name)
                     ]
        return super(LibraryBook, self)._name_search(
            name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

    def grouped_data(self):
        data = self._get_average_cost()
        logger.info("Groupped Data %s" % data)

    @api.model
    def _get_average_cost(self):
        grouped_result = self.read_group(
            [('cost_price', "!=", False)], # Domain
            ['category_id', 'cost_price:avg'], # Fields to access
            ['category_id'] # group_by
            )
        return grouped_result

    @api.model
    def _update_book_price(self, category, amount_to_increase):
        category_books = self.search(['category_id', '=', category])
        for book in category_books:
            book.cost_price += amount_to_increase
        # all_books = self.search([])
        # for book in all_books:
        #     book.cost_price += 10






