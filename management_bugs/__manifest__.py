# -*- coding: utf-8 -*-
##############################################################################
#
#    This module you will Support for Odoo Open source platform.
#    Error control and bug fixes.
#    It will process the data entered and return a message indicating whether
#    the company is eligible or not.
#
#    Copyright (C) 2020- todooweb.com (https://www.todooweb.com)
#    @author ToDOO (https://www.linkedin.com/company/todooweb)
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
{
    'name': "System Bugs Management",
    'summary': """System Bugs Management""",
    'description': """
        System Bugs Management. Error control and bug fixes in the Odoo Open source platform
    """,
    'version': '14.0.0.0.1',
    'category': 'Tools',
    'license': 'LGPL-3',
    'author': "ToDOO (www.todooweb.com)",
    'website': "https://todooweb.com/",
    'contributors': [
        "Equipo Dev <devtodoo@gmail.com>",
        "Edgar Naranjo <edgarnaranjof@gmail.com>",
        "Tatiana Rosabal <tatianarosabal@gmail.com>",
    ],
    'support': 'devtodoo@gmail.com',
    'depends': [
        'base',
        'project',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/management_bug_security.xml',
        'views/management_bug.xml',
        'data/bugs_data.xml',
    ],
    
    'images': [
        'static/description/screenshot_management_bug.png',
        ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
