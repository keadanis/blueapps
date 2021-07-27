###################################################################################
# 
#    Copyright (C) 2020 Cetmix OÜ
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU LESSER GENERAL PUBLIC LICENSE as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

{
    "name": "Scheduled Actions Shortcuts",
    "version": "14.0.1.0.0",
    "summary": "Run Scheduled Actions from tray menu in one click",
    "author": "Cetmix",
    "maintainer": "Anton Goroshkin, Ivan Sokolov",
    "license": "LGPL-3",
    "category": "Productivity",
    "website": "https://cetmix.com",
    "live_test_url": "https://demo.cetmix.com",
    "description": """
    Run Scheduled Actions from tray menu in one click
    """,
    "images": ["static/description/banner.png"],
    "depends": ["base_setup"],
    "data": ["views/ir_cron_view.xml", "views/assets.xml"],
    "qweb": ["static/src/xml/systray/systray.xml"],
    "installable": True,
    "application": False,
}
