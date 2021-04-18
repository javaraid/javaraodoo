import json
import requests
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

AUTHENTICATION_URL = '/v1/integration_merchants/token'

class TadaAuthenticate(models.TransientModel):
    _name = 'tada.authenticate'
    _description = 'Tada Authentication'
    
    name = fields.Char('Password', required=True)
    
    def act_authenticate(self):
        context = self._context
        tada_id = self.env[context['active_model']].browse(context['active_id'])
        base_api_url = self.env['ir.config_parameter'].sudo().get_param('tada.base_api_url')
        API_KEY = self.env['ir.config_parameter'].sudo().get_param('tada.api_key')
        API_SECRET = self.env['ir.config_parameter'].sudo().get_param('tada.api_secret')
        body = {'username': tada_id.username, 'password': self.name, "grant_type": "password", "scope": "offline_access"}
        bodyJson = json.dumps(body)
        headers = {'Content-Type': 'application/json'}
        auth_response = requests.post(base_api_url + AUTHENTICATION_URL, auth=(API_KEY, API_SECRET), data=bodyJson, headers=headers)
        if auth_response.status_code != 200:
            raise ValidationError(_('Please check your username or password'))
        resp_json = auth_response.json()
        tada_id.write({'state': 'establish',
                       'access_token': resp_json['access_token'],
                       'expired_at': resp_json['expired_at']})
        self.unlink()
        return
    
    