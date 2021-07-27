from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import Home
import pyttsx3

class Extension_Home(Home):
    @http.route()
    def web_login(self, redirect=None, **kw):
        if 'login' in kw:
            uid = request.session.authenticate(kw['db'], kw['login'], kw['password'])
            req_user = request.env['res.users'].sudo().search([('id','=',uid)])
            
            def speak(text):
                engine = pyttsx3.init()
                engine.setProperty("rate", 150)
                voices = engine.getProperty("voices")
                engine.setProperty("voice", voices[13].id)
                engine.say(text)
                engine.runAndWait()
            speak("welcome to odoo %s" %req_user.name)
        return super(Extension_Home, self).web_login()