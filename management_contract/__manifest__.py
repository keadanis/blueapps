# -*- coding: utf-8 -*-
##############################################################################
#
#    This module you will Follow flow contract. Report contract. Review the status of a Contract.
#    Check the Contract List. Management Employee, Agreement.
#    Generate contract from Sale Order/ Product (type=Service).
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
    'name': "HR Contract Management",
    'summary': """HR Contract Management""",
    'description': """Contract Management. Report contract. Review the status of a Contract. Generate contract from Sale Order/ Product (type=Service).
    """,
    'version': '14.1.0.1.1',
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
        'sale_crm',
        'account',
        'mail',
        'hr_contract',
        'hr',
        'crm',
    ],
    'data': [
        'security/management_contract_security.xml',
        'security/ir.model.access.csv',
        'views/management_contract_views.xml',
        'data/contract_data.xml',
    ],
    'images': [
        'static/description/screenshot_management.png'
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
