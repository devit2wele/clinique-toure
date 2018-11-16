# -*- coding: utf-8 -*-

from datetime import date
from datetime import datetime
from calendar import monthrange

from odoo import api, fields, models, _
from odoo.tools import ustr
from odoo.exceptions import UserError

TYPE = [
    ('recette', 'recette'),
    ('depense', 'depense'),
]

TYPE_RECETTE = [
    ('consultation', 'consultation'),
    ('soins', 'soins'),
]

TYPE_DEPENSE = [
    ('depense_journaliere', 'depense journaliere'),
    ('autres depenses', 'autres depenses'),
]

MOIS = [
    ('01', 'Janvier'),
    ('02', 'Fevrier'),
    ('03', 'Mars'),
    ('04', 'Avril'),
    ('05', 'Mai'),
    ('06', 'Juin'),
    ('07', 'Juillet'),
    ('08', 'Aout'),
    ('09', 'Septembre'),
    ('10', 'Octobre'),
    ('11', 'Novembre'),
    ('12', 'Decembre'),
]


class RecetteDepense(models.Model):
    _name = "recette.depense"
    _description = "Recette Depense"

    currency_id = fields.Many2one('res.currency', 'Currency', required=True,\
        default=lambda self: self.env.user.company_id.currency_id.id)

    type = fields.Selection(TYPE, required=True)
    montant = fields.Monetary(string='Montant', required=True)
    date = fields.Date(string='Date', required=True)
    type_recette = fields.Selection(TYPE_RECETTE, store=True)
    type_depense = fields.Selection(TYPE_DEPENSE, store=True)
    commentaire = fields.Text(store=True)
    filtre = fields.Integer(compute='_compute_filtre', store=True)
    filtre_com = fields.Integer(compute='_compute_filtre_com', store=True)

    amount_recette_depense_id = fields.Many2one('amount.recette.depense', string="Amount Recette Depense", store=True)

    @api.model
    def default_get(self, fields):    
        res = super(RecetteDepense, self).default_get(fields)        
        if 'date' in fields:        
            res.update({
                'date' : str(date.today()),

            })    
        return res

    @api.one
    @api.depends('type')
    def _compute_filtre(self):
        if self.type == 'recette':
            self.type_depense = False
            self.filtre = 1
        elif self.type == 'depense':
            self.type_recette = False
            self.filtre = 2
            if self.type_depense == 'autres depenses':
                self.filtre_com = 2
            else:
                self.filtre_com = 1 
        else:
            self.type_depense = False
            self.type_recette = False
            self.filtre = 0

    @api.one
    @api.depends('type_depense')
    def _compute_filtre_com(self):
        if self.type_depense == 'autres depenses':
            self.filtre_com = 2
        else:
            self.filtre_com = 1 


class AmountRecetteDepense(models.Model):
    _name = "amount.recette.depense"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = "Amount Recette Depense"

    @api.depends('mois')
    def _compute_amount_recette_depense(self):
        if self.mois:
            recette=depense=0
            
            year = date.today().year
            month = int(self.mois)
            last_day_in_month = monthrange(year, month)[1]
            date_from = '-'.join(map(str,[year, self.mois, '01']))
            date_to = '-'.join(map(str,[year,self.mois,last_day_in_month]))

            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()

            recette_depense_by_mois = self.env['recette.depense'].search([
                ('date', '>=', fields.Date.to_string(date_from)),
                ('date', '<=', fields.Date.to_string(date_to)),
            ])

            for recette_depense_by_day in recette_depense_by_mois:
                recette += recette_depense_by_day.montant if recette_depense_by_day.type_recette else 0
                depense += recette_depense_by_day.montant if recette_depense_by_day.type_depense else 0

            self.amount_recette = recette
            self.amount_depense = depense
            self.solde = recette - depense
            self.recette_depense_ids = recette_depense_by_mois

    currency_id = fields.Many2one('res.currency', 'Currency', required=True,\
        default=lambda self: self.env.user.company_id.currency_id.id)


    mois = fields.Selection(MOIS, required=True)
    amount_recette = fields.Monetary(string='Recette', compute='_compute_amount_recette_depense', store=True)
    amount_depense = fields.Monetary(string='Depense', compute='_compute_amount_recette_depense', store=True)
    solde = fields.Monetary(compute='_compute_amount_recette_depense', store=True)

    recette_depense_ids = fields.One2many('recette.depense', 'amount_recette_depense_id', string='Amount Recette Depense', compute='_compute_amount_recette_depense', store=True)

    @api.multi
    def action_print_rd(self):
        return self.env['report'].get_action(self, 'gestion_clinique.report_recettedepense')

    @api.multi
    def action_send_rd(self):

        self.ensure_one()
        
        ir_model_data = self.env['ir.model.data']
        
        try:
            template_id = ir_model_data.get_object_reference('gestion_clinique', 'email_template_edi_recette_depense')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'amount.recette.depense',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        })
        
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }




