# -*- coding: utf-8 -*-
#################################################################################
# Author      : Syncoria Inc (<https://www.syncoria.com/>)
# Copyright(c): 2004-Present Syncoria Inc
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
#################################################################################

{
  'name':'Restaurant Sync',
  'description': 'Theme for Restaurant',
  'version':'14.0.1.0.0',
  'author': "Syncoria Inc.",
  'website': "https://www.syncoria.com",
  'company': 'Syncoria Inc.',
  'maintainer': 'Syncoria Inc.',
  'depends': ['base', 'website', 'website_blog'],
  'data': [ 
		'views/layout.xml',
		'views/inherit_template.xml',
		'views/snippets_information.xml',
		'views/snippets_hotsales.xml',
		'views/snippets_restextimg.xml',
		'views/snippets_resspecialty.xml',
		'views/snippets_resreservation.xml',
		'views/snippets_recipe.xml',
		'views/snippets_resmenu.xml',
		'views/snippets_restestimonial.xml',
		'views/pages.xml',
        'views/pages_alt.xml'		
		],
    'category': 'Theme/Services',
    'summary': 'Restaurants, Bars, Pubs, Cafes, Catering, Food, Drinks, Concerts, Events, Shows, Musics, Dance, Party',
    'images': [
        'static/description/banner.png',
        'static/description/theme_restaurantsync_screenshot.png',
    ],
    'live_test_url': "http://restaurantsyncdemo14.syncoria.com/",
    'license': 'OPL-1',
    'support': "support@syncoria.com",
    'application': False,
    "installable": True,
}
