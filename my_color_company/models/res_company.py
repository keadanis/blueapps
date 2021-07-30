import base64
from colorsys import hls_to_rgb, rgb_to_hls

from odoo import api, fields, models, _

from ..utils import convert_to_image, image_to_rgb, n_rgb_to_hex
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
from odoo import modules

URL_BASE = "~/my_color_company/static/src/scss/"
URL_SCSS_GEN_TEMPLATE = URL_BASE + "custom_colors.%d.gen.scss"



class ResCompany(models.Model):
    _inherit = "res.company"

    
    SCSS_TEMPLATE_IMAGE = """

        .o_form_sheet_bg {
            background-color: %(sheet_background_color)s !important;
        }
        .o_form_sheet {
            background-color: %(sheet_color)s !important;
        }

        .o_control_panel {
            background-color: %(control_sheet_color)s !important;
        }
        .breadcrumb {
            background-color: %(control_sheet_color)s !important;
        }
        .o_searchview .o_searchview_input {
            background-color: %(control_sheet_color)s !important;
        }

        .o_base_settings .o_control_panel .o_panel .o_setting_search .searchInput {
            background-color: %(control_sheet_color)s !important;
        }
        .o_form_view .o_form_statusbar {
            background-color: %(control_sheet_color)s !important;
        }




        .o_field_widget input.o_input, .o_input {
            color: %(general_text_color)s;
            background-color: %(sheet_color)s;
            filter:brightness(1.1);
        }

        .o_form_view .o_notebook > .o_notebook_headers > .nav.nav-tabs > .nav-item > .nav-link.active {
            color: %(general_text_color)s;
            border-color: #ced4da;
            border-top-color: rgb(206, 212, 218);
            border-bottom-color: rgb(206, 212, 218);
            background-color: %(sheet_color)s;
            filter:brightness(0.95);

        }

        .o_form_view .o_notebook > .o_notebook_headers > .nav.nav-tabs > .nav-item > .nav-link {
            color: %(general_text_color)s;
            border-color: #ced4da;
            border-top-color: rgb(206, 212, 218);
            border-bottom-color: rgb(206, 212, 218);
            background-color: %(sheet_color)s;
            filter:brightness(0.95);
        }

        .o_list_view .o_list_table > thead > tr > * {
            color: %(general_text_color)s;
            border-color: #ced4da;
            border-top-color: rgb(206, 212, 218);
            border-bottom-color: rgb(206, 212, 218);
            background-color: %(sheet_color)s;
            filter:brightness(0.95);
        }

        .o_list_view .o_list_table > tbody > tr > * {
            color: %(general_text_color)s;
            border-color: #ced4da;
            border-top-color: rgb(206, 212, 218);
            border-bottom-color: rgb(206, 212, 218);
            background-color: %(sheet_color)s;
            filter:brightness(1.05);
        }

        .o_list_view .o_list_table > tbody > tr > *:hover {
            color: %(general_text_color)s;
            border-color: #ced4da;
            border-top-color: rgb(206, 212, 218);
            border-bottom-color: rgb(206, 212, 218);
            background-color: %(sheet_color)s;
            filter:brightness(1);
        }

        .o_list_view .o_list_table > tbody > tr {
            color: %(general_text_color)s;
            border-color: #ced4da;
            border-top-color: rgb(206, 212, 218);
            border-bottom-color: rgb(206, 212, 218);
            background-color: %(sheet_color)s;
            filter:brightness(1.05);
        }

        .o_list_view .o_list_table > tbody > tr:hover {
            color: %(general_text_color)s;
            border-color: #ced4da;
            border-top-color: rgb(206, 212, 218);
            border-bottom-color: rgb(206, 212, 218);
            background-color: %(sheet_color)s;
            filter:brightness(1);
        }

        .btn-link {
            color: %(general_text_color)s;
            filter:brightness(0.9);
        }

        .o_kanban_view .o_kanban_record {
            background-color: %(sheet_color)s;
        }

        .o_kanban_view .o_kanban_record:hover {
            background-color: %(sheet_color)s;
            filter:brightness(0.9);
        }

        .o_control_panel .breadcrumb > li {
            color: %(general_text_color)s;
            filter:brightness(0.9);
        }




        body {
            font-family: "Roboto", "Odoo Unicode Support Noto", sans-serif;
            font-size: 1.08333333rem;
            font-weight: 400;
            line-height: 1.5;
            color: %(general_text_color)s;
            text-align: left;
        }

        h1, h2, h3, h4, h5, h6, .h1, .h2, .h3, .h4, .h5, .h6 {
            font-weight: 400;
            line-height: 1.2;
            color: %(general_text_color)s;
        }

        .o_form_view .o_notebook > .o_notebook_headers > .nav.nav-tabs > .nav-item > .nav-link:hover {
            color: %(link_text_color)s;
        }


        body a,
        a,
        .o_form_view .o_form_uri,
        .o_form_view .o_form_uri > span:first-child,
        .o_form_view .oe_button_box .oe_stat_button .o_button_icon {
            color: %(link_text_color)s;
            text-decoration: none;
            background-color: transparent;
        }

        body a:hover,
        a:hover,
        .o_form_view .o_form_uri:hover,
        .o_form_view .o_form_uri > span:first-child:hover,
        .o_form_view .oe_button_box .oe_stat_button .o_button_icon:hover {
            color: darken(%(link_text_color)s,30);
            text-decoration: none;
            background-color: transparent;
        }

        .btn-primary {
            color: %(button_color_primary_font)s;
            background-color: %(button_color_primary)s;
            border: 0;
        }
        .btn-primary:hover,
        .btn-primary:not(:disabled):not(.disabled):active,
        .btn-primary:not(:disabled):not(.disabled).active {
            color: %(button_color_primary_font)s;
            background-color: darken(%(button_color_primary)s,20);
        }

        .btn-primary:focus,
        .btn-primary.focus {
            color: %(button_color_primary_font)s;
            background-color: darken(%(button_color_primary)s,20);
        }

        .btn-secondary {
            color: %(button_color_secondary_font)s;
            background-color: %(button_color_secondary)s;
        }
        .btn-secondary:hover,
        .btn-secondary:focus,
        .btn-secondary.focus,
        .btn-secondary:not(:disabled):not(.disabled):active,
        .btn-secondary:not(:disabled):not(.disabled).active {
            color: %(button_color_secondary_font)s;
            background-color: darken(%(button_color_secondary)s,10);
        }



        

        .o_main_navbar {
          background-color: %(color_navbar_bg)s !important;
          color: %(color_navbar_text)s !important;

            > a, > button {
                &:hover, &:focus {
                    background-color: darken(%(color_navbar_bg)s,20) !important;
                    color: inherit;
                }
            }

          > .o_menu_brand {
            color: %(color_navbar_text)s !important;
            &:hover, &:focus, &:active, &:focus:active {
              background-color: darken(%(color_navbar_bg)s,20) !important;
            }
          }

          .show {
            .dropdown-toggle {
              background-color: darken(%(color_navbar_bg)s,20) !important;
            }
          }

          > ul {
            > li {
              > a, > label {
                color: %(color_navbar_text)s !important;

                &:hover, &:focus, &:active, &:focus:active {
                  background-color: darken(%(color_navbar_bg)s,20) !important;
                }
              }
            }
          }
        }


        .o_home_menu_background {
            background-image: url(data:image/png;base64,%(color_background_img)s) !important;
        }
    """

    SCSS_TEMPLATE_IMAGE_DEFAULT = """

        .o_home_menu_background {
            background-image: url(/my_color_company/static/src/img/fondo2.jpg) !important;
        }

        .o_main_navbar {
          background-color: %(color_navbar_bg)s !important;
          color: %(color_navbar_text)s !important;

            > a, > button {
                &:hover, &:focus {
                    background-color: %(color_navbar_bg_hover)s !important;
                    color: inherit;
                }
            }

          > .o_menu_brand {
            color: %(color_navbar_text)s !important;
            &:hover, &:focus, &:active, &:focus:active {
              background-color: %(color_navbar_bg_hover)s !important;
            }
          }

          .show {
            .dropdown-toggle {
              background-color: %(color_navbar_bg_hover)s !important;
            }
          }

          > ul {
            > li {
              > a, > label {
                color: %(color_navbar_text)s !important;

                &:hover, &:focus, &:active, &:focus:active {
                  background-color: %(color_navbar_bg_hover)s !important;
                }
              }
            }
          }
        }
    """

    SCSS_TEMPLATE = """

        .o_form_sheet_bg {
            background-color: %(sheet_background_color)s !important;
        }
        .o_form_sheet {
            background-color: %(sheet_color)s !important;
        }

        .o_control_panel {
            background-color: %(control_sheet_color)s !important;
        }
        .breadcrumb {
            background-color: %(control_sheet_color)s !important;
        }
        .o_searchview .o_searchview_input {
            background-color: %(control_sheet_color)s !important;
        }

        .o_base_settings .o_control_panel .o_panel .o_setting_search .searchInput {
            background-color: %(control_sheet_color)s !important;
        }
        .o_form_view .o_form_statusbar {
            background-color: %(control_sheet_color)s !important;
        }


        .o_field_widget input.o_input, .o_input {
            color: %(general_text_color)s;
            background-color: %(sheet_color)s;
            filter:brightness(1.1);
        }

        .o_form_view .o_notebook > .o_notebook_headers > .nav.nav-tabs > .nav-item > .nav-link.active {
            color: %(general_text_color)s;
            border-color: #ced4da;
            border-top-color: rgb(206, 212, 218);
            border-bottom-color: rgb(206, 212, 218);
            background-color: %(sheet_color)s;
            filter:brightness(0.95);

        }

        .o_form_view .o_notebook > .o_notebook_headers > .nav.nav-tabs > .nav-item > .nav-link {
            color: %(general_text_color)s;
            border-color: #ced4da;
            border-top-color: rgb(206, 212, 218);
            border-bottom-color: rgb(206, 212, 218);
            background-color: %(sheet_color)s;
            filter:brightness(0.95);
        }

        .o_list_view .o_list_table > thead > tr > * {
            color: %(general_text_color)s;
            border-color: #ced4da;
            border-top-color: rgb(206, 212, 218);
            border-bottom-color: rgb(206, 212, 218);
            background-color: %(sheet_color)s;
            filter:brightness(0.95);
        }

        .o_list_view .o_list_table > tbody > tr > * {
            color: %(general_text_color)s;
            border-color: #ced4da;
            border-top-color: rgb(206, 212, 218);
            border-bottom-color: rgb(206, 212, 218);
            background-color: %(sheet_color)s;
            filter:brightness(1.05);
        }

        .o_list_view .o_list_table > tbody > tr > *:hover {
            color: %(general_text_color)s;
            border-color: #ced4da;
            border-top-color: rgb(206, 212, 218);
            border-bottom-color: rgb(206, 212, 218);
            background-color: %(sheet_color)s;
            filter:brightness(1);
        }

        .o_list_view .o_list_table > tbody > tr {
            color: %(general_text_color)s;
            border-color: #ced4da;
            border-top-color: rgb(206, 212, 218);
            border-bottom-color: rgb(206, 212, 218);
            background-color: %(sheet_color)s;
            filter:brightness(1.05);
        }

        .o_list_view .o_list_table > tbody > tr:hover {
            color: %(general_text_color)s;
            border-color: #ced4da;
            border-top-color: rgb(206, 212, 218);
            border-bottom-color: rgb(206, 212, 218);
            background-color: %(sheet_color)s;
            filter:brightness(1);
        }

        .btn-link {
            color: %(general_text_color)s;
            filter:brightness(0.9);
        }

        .o_kanban_view .o_kanban_record {
            background-color: %(sheet_color)s;
        }

        .o_kanban_view .o_kanban_record:hover {
            background-color: %(sheet_color)s;
            filter:brightness(0.9);
        }

        .o_control_panel .breadcrumb > li {
            color: %(general_text_color)s;
            filter:brightness(0.9);
        }




        body {
            font-family: "Roboto", "Odoo Unicode Support Noto", sans-serif;
            font-size: 1.08333333rem;
            font-weight: 400;
            line-height: 1.5;
            color: %(general_text_color)s;
            text-align: left;
        }

        h1, h2, h3, h4, h5, h6, .h1, .h2, .h3, .h4, .h5, .h6 {
            font-weight: 400;
            line-height: 1.2;
            color: %(general_text_color)s;
        }

        .o_form_view .o_notebook > .o_notebook_headers > .nav.nav-tabs > .nav-item > .nav-link:hover {
            color: %(link_text_color)s;
        }


        body a,
        a,
        .o_form_view .o_form_uri,
        .o_form_view .o_form_uri > span:first-child,
        .o_form_view .oe_button_box .oe_stat_button .o_button_icon {
            color: %(link_text_color)s;
            text-decoration: none;
            background-color: transparent;
        }

        body a:hover,
        a:hover,
        .o_form_view .o_form_uri:hover,
        .o_form_view .o_form_uri > span:first-child:hover,
        .o_form_view .oe_button_box .oe_stat_button .o_button_icon:hover {
            color: darken(%(link_text_color)s,30);
            text-decoration: none;
            background-color: transparent;
        }

        .btn-primary {
            color: %(button_color_primary_font)s;
            background-color: %(button_color_primary)s;
            border: 0;
        }
        .btn-primary:hover,
        .btn-primary:not(:disabled):not(.disabled):active,
        .btn-primary:not(:disabled):not(.disabled).active {
            color: %(button_color_primary_font)s;
            background-color: darken(%(button_color_primary)s,20);
        }

        .btn-primary:focus,
        .btn-primary.focus {
            color: %(button_color_primary_font)s;
            background-color: darken(%(button_color_primary)s,20);
        }

        .btn-secondary {
            color: %(button_color_secondary_font)s;
            background-color: %(button_color_secondary)s;
        }
        .btn-secondary:hover,
        .btn-secondary:focus,
        .btn-secondary.focus,
        .btn-secondary:not(:disabled):not(.disabled):active,
        .btn-secondary:not(:disabled):not(.disabled).active {
            color: %(button_color_secondary_font)s;
            background-color: darken(%(button_color_secondary)s,10);
        }



        

        .o_main_navbar {
          background-color: %(color_navbar_bg)s !important;
          color: %(color_navbar_text)s !important;

            > a, > button {
                &:hover, &:focus {
                    background-color: darken(%(color_navbar_bg)s,20) !important;
                    color: inherit;
                }
            }

          > .o_menu_brand {
            color: %(color_navbar_text)s !important;
            &:hover, &:focus, &:active, &:focus:active {
              background-color: darken(%(color_navbar_bg)s,20) !important;
            }
          }

          .show {
            .dropdown-toggle {
              background-color: darken(%(color_navbar_bg)s,20) !important;
            }
          }

          > ul {
            > li {
              > a, > label {
                color: %(color_navbar_text)s !important;

                &:hover, &:focus, &:active, &:focus:active {
                  background-color: darken(%(color_navbar_bg)s,20) !important;
                }
              }
            }
          }
        }



        .o_home_menu_background {
            background: url(/web_enterprise/static/src/img/home-menu-bg-overlay.svg),
                linear-gradient(to right bottom, %(color_background_first_grad)s, %(color_background_second_grad)s) !important;
            background-size: cover;
        }
    """


    company_colors = fields.Serialized()
    color_navbar_bg = fields.Char("Navbar Background Color", default="#156d9d", sparse="company_colors")
    color_navbar_bg_hover = fields.Char(
        "Navbar Background Color Hover", default="#3fb7e3", sparse="company_colors"
    )
    color_navbar_text = fields.Char("Navbar Text Color",default="#000000", sparse="company_colors")

    legend = fields.Char(
        string='legend',
        default='Enterprise Edition',
    )
    legend_exist = fields.Boolean(
        string='Modify legend',
    )

    color_background = fields.Boolean(
        string='Background Color', 
    )

    color_image = fields.Boolean(
        string='Background Image', default=True, 
    )
    background_select = fields.Selection([('gradient','Gradient'),('image','Image')], default="gradient")
    color_image_defult = fields.Boolean(
        string='Background Image default', default=True
    )

    color_background_first_grad = fields.Char("Background Color 1", default="#156d9d", sparse="company_colors")
    color_background_second_grad = fields.Char("Background Color 2", default="#0c9ed4", sparse="company_colors")
    color_background_image = fields.Binary('Background Image')

    color_background_img = fields.Char("Imagen", sparse="company_colors")
    color_background_image_name = fields.Char(string='name')

    color_defult = fields.Boolean(
        string='Color defult', default=True
    )

    sheet_background_color = fields.Char("Background Sheet Color", default="#F9F9F9", sparse="company_colors")
    sheet_color = fields.Char("Sheet Color", default="#FFFFFF", sparse="company_colors")
    control_sheet_color = fields.Char("Control Sheet Color", default="#FFFFFF", sparse="company_colors")

    button_color_primary = fields.Char("Primary Button Color", default="#007A77", sparse="company_colors")
    button_color_secondary = fields.Char("Secondary Button Color", default="#FFFFFF", sparse="company_colors")
    button_color_primary_font = fields.Char("Primary Button Font Color", default="#FFFFFF", sparse="company_colors")
    button_color_secondary_font = fields.Char("Secondary Button Font Color", default="#007A77", sparse="company_colors")


    link_text_color = fields.Char("Link Text Color", default="#00e025", sparse="company_colors")
    general_text_color = fields.Char("General Text Color", default="#000000", sparse="company_colors")

    @api.onchange("legend_exist")
    def onchange_company_id(self):
        company = self.env["res.company"].search([])
        for x in company:
            if x.legend_exist == True:
                raise UserError(_("it was modified from another company"))

    @api.model
    def color_defults(self):
        for rec in self:
            company = self.env.ref('base.main_company')
            if company.color_defult == True:
                values = {
                    'color_navbar_bg': '#156d9d', 'color_navbar_bg_hover': '#3fb7e3', 'color_navbar_text': '#ffffff','color_background_first_grad': '#156d9d','color_background_second_grad':'#0c9ed4'
                }
                company.write(values)

    @api.model_create_multi
    def create(self, vals_list):
        
        records = super().create(vals_list)
        records.scss_create_or_update_attachment()
        return records

    def unlink(self):
        IrAttachmentObj = self.env["ir.attachment"]
        for record in self:
            IrAttachmentObj.sudo().search(
                [("url", "=", record.scss_get_url()), ("company_id", "=", record.id)]
            ).sudo().unlink()
        return super().unlink()

    def write(self, values):
        
        if not self.env.context.get("ignore_company_color", False):
            fields_to_check = (
                "color_navbar_bg",
                "color_navbar_bg_hover",
                "color_navbar_text",
                "color_background_first_grad",
                "color_background_second_grad",
                "color_background",
                "color_background_image",
                "background_select",
                "sheet_background_color",
                "sheet_color",
                "button_color_primary",
                "button_color_secondary",
                "button_color_primary_font",
                "button_color_secondary_font",
                "link_text_color",
                "general_text_color",
                "control_sheet_color",
            )
            if "logo" in values:
                if values["logo"]:
                    _r, _g, _b = image_to_rgb(convert_to_image(values["logo"]))
                    # Make color 10% darker
                    _h, _l, _s = rgb_to_hls(_r, _g, _b)
                    _l = max(0, _l - 0.1)
                    _rd, _gd, _bd = hls_to_rgb(_h, _l, _s)

                    _a = 1 - (0.2126 * _r + 0.7152 * _g + 0.0722 * _b)
                    values.update(
                        {
                            "color_navbar_bg": n_rgb_to_hex(_r, _g, _b),
                            "color_navbar_bg_hover": n_rgb_to_hex(_rd, _gd, _bd),
                            "color_navbar_text": "#000" if _a < 0.5 else "#fff",
                            "color_background_first_grad": n_rgb_to_hex(_r, _g, _b),
                            "color_background_second_grad": n_rgb_to_hex(_r, _g, _b),
                        }
                    )
                else:
                    values.update(self.default_get(fields_to_check))

            result = super().write(values)
            if any([field in values for field in fields_to_check]):
                self.scss_create_or_update_attachment()
            
        else:
            result = super().write(values)
        return result

    def _scss_get_sanitized_values(self):
        self.ensure_one()

        values = dict(self.company_colors or {})
        
        values.update(
            {
                "general_text_color": (values.get("general_text_color") or "#000000"),
                "sheet_background_color": (values.get("sheet_background_color") or "#F9F9F9"),
                "link_text_color": (values.get("link_text_color") or "#F9F9F9"),
                "sheet_color": (values.get("sheet_color") or "#FFFFFF"),
                "button_color_primary": (values.get("button_color_primary") or "#007A77"),
                "button_color_secondary": (values.get("button_color_secondary") or "#FFFFFF"),
                "button_color_secondary_font": (values.get("button_color_secondary_font") or "#007A77"),
                "button_color_primary_font": (values.get("button_color_primary_font") or "#FFFFFF"),
                "control_sheet_color": (values.get("control_sheet_color") or "#FFFFFF"),
                "color_navbar_bg": (values.get("color_navbar_bg") or "$o-brand-odoo"),
                "color_navbar_bg_hover": (
                    values.get("color_navbar_bg_hover")
                    or "$o-navbar-inverse-link-hover-bg"
                ),
                "color_navbar_text": (values.get("color_navbar_text") or "#FFF"),
                "color_background_first_grad": (values.get("color_background_first_grad") or "#77717e"),
                "color_background_second_grad": (values.get("color_background_second_grad") or "#c9a8a9"),
            }
        )
        return values

    def _scss_generate_content(self):
        self.ensure_one()
        # ir.attachment need files with content to work
        if not self.company_colors:
            return "// No Web Company Color SCSS Content\n"
        self.color_background_img = self.color_background_image
        if self.background_select == 'gradient':
            return self.SCSS_TEMPLATE % self._scss_get_sanitized_values()
        if self.background_select == 'image':
            return self.SCSS_TEMPLATE_IMAGE % self._scss_get_sanitized_values()
       
       

    def scss_get_url(self):
        for rec in self:
            rec.ensure_one()
            return URL_SCSS_GEN_TEMPLATE % rec.id

    def scss_create_or_update_attachment(self):
        
        IrAttachmentObj = self.env["ir.attachment"]
        for record in self:
            datas = base64.b64encode(record._scss_generate_content().encode("utf-8"))
            custom_url = record.scss_get_url()
            custom_attachment = IrAttachmentObj.sudo().search(
                [("url", "=", custom_url), ("company_id", "=", record.id)]
            )
            values = {
                "datas": datas,
                "db_datas": datas,
                "url": custom_url,
                "name": custom_url,
                "company_id": record.id,
            }
            if custom_attachment:
                custom_attachment.sudo().write(values)
            else:
                values.update({"type": "binary", "mimetype": "text/scss"})
                IrAttachmentObj.sudo().create(values)
        self.env["ir.qweb"].sudo().clear_caches()
