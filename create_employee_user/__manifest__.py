# -*- coding: utf-8 -*-
##############################################################################
#
#    This module you will create of the system user and contact from HR Employee
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
    'name': "HR Employee to system user",
    'summary': """HR Employee to system user with automatics task""",
    'description': """Creation of the system user and contact from HR Employee with automatics task.
    """,
    'version': '14.0.0.0.1',
    'category': 'Human Resources',
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
        'sale',
        'account',
        'mail',
        'hr_contract',
        'hr',
        'crm',
        'management_contract'
    ],
    'data': [
        'views/employee_user.xml',
        'data/create_user_data.xml',
    ],
    'images': [
        'static/description/screenshot_user.png'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
