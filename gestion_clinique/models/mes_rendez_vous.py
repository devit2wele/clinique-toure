# -*- coding: utf-8 -*-

from datetime import date
from odoo import api, fields, models, _


class MesRendezVous(models.Model):
    _name = "mes.rendez.vous"
    _description = "Mes rendez vous"



    date = fields.Date(store=True)
    patient_rdv_ids = fields.One2many('gestion.clinique.patient.rdv', 'mes_rendez_vous_id', string='Mes Rendez Vous', store=True)

    @api.multi
    def action_mes_rendez_vous(self):
        rdv_today = self.env['gestion.clinique.patient.rdv'].search([
            ('date_rdv', '=', fields.Date.to_string(date.today())),
        ])

        
        self.date = date.today()
        self.patient_rdv_ids = rdv_today



