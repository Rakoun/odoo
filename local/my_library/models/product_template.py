# -*- coding: utf-8 -*-
from os.path import join
from odoo import models, api, exceptions
EXPORTS_DIR = '/home/rgeromegnace/odoo-dev12/odoo_cookbook/logs'
import  logging

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def export_stock_level_button(self):
        stock_locations = self.env['stock.location']
        stock_locations = stock_locations.search([])
        stock_location = stock_locations[6]
        self.export_stock_level(stock_location)

    def export_stock_level(self, stock_location):
        _logger.info('export stock level for %s', stock_location.name)
        products = self.with_context(location=stock_location.id).search([])
        products = products.filtered('qty_available')
        _logger.debug('%d products in the location', len(products))
        fname = join(EXPORTS_DIR, 'stock_level.txt')
        try:
            with open(fname, 'w') as fobj:
                for prod in products:
                    fobj.write('%s\t%f\n' % (prod.name, prod.qty_available))
        except IOError:
            _logger.exception('Error while writing to %s in %s', 'stock_level.txt', EXPORTS_DIR)
            raise exceptions.UserError('unable to save file')
