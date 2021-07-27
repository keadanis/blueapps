from odoo import api, fields, models, _
from odoo.exceptions import UserError
import pyodbc


class QueryMSSQL(models.Model):
    _name = "mssql.query"
    _description = "MS SQL queries from Odoo interface"

    name = fields.Text('Query', help='For Example : SELECT name FROM Account')
    connection_id = fields.Many2one('mssql.connection', string='Database', required=True)
    rowcount = fields.Text(string='Rowcount')
    html = fields.Html(string='HTML')
    valid_query_name = fields.Char()
    show_raw_output = fields.Boolean(string='Show the raw output of the query')
    raw_output = fields.Text(string='Raw output')

    # def print_result(self):
    #     return {
    #         'name': _("Select orientation of the PDF's result"),
    #         'view_mode': 'form',
    #         'res_model': 'pdforientation',
    #         'type': 'ir.actions.act_window',
    #         'target': 'new',
    #         'context': {
    #             'default_query_name': self.valid_query_name,
    #             'default_connection_id': self.connection_id.id,
    #             'default_html': self.html,
    #         },
    #     }

    def execute_query(self):
        self.show_raw_output = False
        self.raw_output = ''
        self.rowcount = ''
        self.html = '<br></br>'
        self.valid_query_name = ''

        if self.name:
            cnxn = self.connection_id.query()
            cursor = cnxn.cursor()
            headers = []
            datas = []
            try:
                no_fetching = ['update', 'delete', 'create', 'insert', 'alter', 'drop']
                max_n = len(max(no_fetching))
                is_insides = [(o in self.name.lower().strip()[:max_n]) for o in no_fetching]
                if True not in is_insides:
                    cursor.execute(self.name)
                    headers = [column[0] for column in cursor.description]
                    datas = cursor.fetchall()
                    rowcount = len(datas)
                    self.rowcount = "{0} row{1} processed".format(rowcount, 's' if 1 < rowcount else '')
                else:
                    cursor.execute(self.name)
                    cnxn.commit()
                    self.rowcount = "Command(s) completed successfully"
            except Exception as e:
                raise UserError(e)

            if headers and datas:
                self.valid_query_name = self.name
                self.raw_output = datas
                header_html = "".join(["<th style='border: 1px solid'>" + str(header) + "</th>" for header in headers])
                header_html = "<tr>" + "<th style='background-color:white !important'/>" + header_html + "</tr>"

                body_html = ""
                i = 0
                for data in datas:
                    i += 1
                    body_line = "<tr>"+"<td style='border-right: 1px solid; border-bottom: 1px solid; background-color: white'>{0}</td>".format(i)
                    for value in data:
                        body_line += "<td style='border: 1px solid; background-color: {0}'>{1}</td>".format('#CCCCCC' if i%2 == 0 else '#FFFFFF', str(value) if (value is not None) else '')

                    body_line += "</tr>"
                    body_html += body_line

                self.html = """
                <div style="width:1100px;overflow:visible !important;">
                <table style="text-align: center">
                  <thead style="color: black;background-color: #999999;">
                    {0}
                  </thead>
                  <tbody>
                    {1}
                  </tbody>
                </table>
                </div>
                """.format(header_html, body_html)


class ConnectionMSSQL(models.Model):
    _name = "mssql.connection"
    _description = "MS SQL Connection from Odoo interface"

    name = fields.Char("Name", required=True)
    server_ip = fields.Char('SQL Server IP', help="For Example : 192.168.0.1", required=True)
    server_db = fields.Char('SQL Database', required=True)
    server_login = fields.Char('SQL User Login', required=True)
    server_password = fields.Char('SQL User Password', required=True)

    def test_sync(self):
        try:
            query = 'DRIVER={ODBC Driver 17 for SQL Server};  \
                                  SERVER=' + self.server_ip + '; \
                                  DATABASE=' + self.server_db + ';\
                                  UID=' + self.server_login + ';\
                                  PWD=' + self.server_password + ';\
                                  Trusted_Connection=no;'
            cnxn = pyodbc.connect(query)
            title = _("Success !")
            message = _("Connection Succeeded!")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': title,
                    'message': message,
                    'sticky': False,
                }
            }
        except pyodbc.OperationalError:
            raise UserError(_('No response received. Check server Name.'))
        except pyodbc.ProgrammingError:
            raise UserError(_('Check Database Name.'))
        except pyodbc.InterfaceError:
            raise UserError(_('Check User and Password.'))

    def query(self):
        try:
            query = 'DRIVER={ODBC Driver 17 for SQL Server};  \
                                  SERVER=' + self.server_ip + '; \
                                  DATABASE=' + self.server_db + ';\
                                  UID=' + self.server_login + ';\
                                  PWD=' + self.server_password + ';\
                                  Trusted_Connection=no;'
            cnxn = pyodbc.connect(query)
            return cnxn
        except pyodbc.OperationalError:
            raise UserError(_('No response received. Check server Name.'))
        except pyodbc.ProgrammingError:
            raise UserError(_('Check Database Name.'))
        except pyodbc.InterfaceError:
            raise UserError(_('Check User and Password.'))