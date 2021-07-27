##############################################################################
#
#    This module you will Modify Design List View for all views tree.
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
    'name': 'Design List View',
    'summary': """Modify Design List View""",
    'description': """
       Modify Design List View for all views tree. Sticky Header. List Sticky Header.
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
        'web',
        'base',
    ],
    'data': [
        'views/template_design.xml',
    ],
    'images': [
        'static/description/screenshot_design.png'
    ],
    'qweb': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}
