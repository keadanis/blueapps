{
    "name": "Color By Company",

    "category": "web",

    "version": "14.0.1.0.0",

    "summary": "Cambia los colores de tu tema de odoo con tu seleccion personal.",

    "author": "AXOLOT",

    "website": "",

    "depends": ["base", 
                "web", 
                "base_sparse_field", 
                "base_setup", 
                "mail"],

    "data": ["view/assets.xml", 
            "view/res_company.xml", 
            "data/ir_cron_data.xml"],

    "qweb": ["view/base.xml"],

    "uninstall_hook": "uninstall_hook",

    "post_init_hook": "post_init_hook",

    "auto_install": False,

    "installable": True,
}
