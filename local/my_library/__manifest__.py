{
	'name':  'My Library',
	'summary': "Manage books easily", 
	'description': """Long description""", 
	'author': "Rakoun.com",
	'website': "http://www.example.com", 
	'category': 'Uncategorized', 
	'version': '12.0.1.11',
	'depends': ['base', 'decimal_precision', 'stock'],
	'data': [
		'security/groups.xml',
		'security/ir.model.access.csv',
		'views/library_book.xml',
		'views/library_book_categ.xml',
		'views/library_member.xml',
		'views/product_view.xml',
		'data/data.xml',
		'data/test_delete.xml',
	],
	'demo': [
		'demo/demo.xml',
	],
}