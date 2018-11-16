# -*- coding: utf-8 -*-

from datetime import date

from odoo import api, fields, models, _
from odoo.tools import ustr
from odoo.exceptions import UserError

SEXE = [
    ('m', 'M'),
    ('f', 'F'),
]

TYPE_DENT = [
    ('11','11'),
    ('12','12'),
    ('13','13'),
    ('14','14'),
    ('15','15'),
    ('16','16'),
    ('17','17'),
    ('18','18'),
    ('21','21'),
    ('22','22'),
    ('23','23'),
    ('24','24'),
    ('25','25'),
    ('26','26'),
    ('27','27'),
    ('28','28'),
    ('31','31'),
    ('32','32'),
    ('33','33'),
    ('34','34'),
    ('35','35'),
    ('36','36'),
    ('37','37'),
    ('38','38'),
    ('41','41'),
    ('42','42'),
    ('43','43'),
    ('44','44'),
    ('45','45'),
    ('46','46'),
    ('47','47'),
    ('48','48'),
    
    ('51','51'),
    ('52','52'),
    ('53','53'),
    ('54','54'),
    ('55','55'),
    ('61','61'),
    ('62','62'),
    ('63','63'),
    ('64','64'),
    ('65','65'),
    ('71','71'),
    ('72','72'),
    ('73','73'),
    ('74','74'),
    ('75','75'),
    ('81','81'),
    ('82','82'),
    ('83','83'),
    ('84','84'),
    ('85','85'),
]

# ---------------------------------------------------------
# Patient Info
# ---------------------------------------------------------
class PatientInfo(models.Model):
    _name = "gestion.clinique.patient.info"
    _description = "La fiche patient"
    _order = "sequence"

    sequence = fields.Char(string='Code Patient', readonly=True)
    name = fields.Char(string='Nom', required=True)
    firstname = fields.Char(string='Prénom', required='True')
    age = fields.Integer(string="Age")
    sexe = fields.Selection(SEXE, String='Sexe')
    adresse = fields.Char(String='Adresse')
    numero_telephone = fields.Char(string="Numéro de téléphone")

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        vals['sequence'] = self.env['ir.sequence'].get('gestion.clinique.patient.info')
        res  =  super(PatientInfo, self).create(vals)        
        return res

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if record.name:
                name = record.name 
            if record.name and record.firstname:
                name = record.firstname +' '+record.name
            if record.sequence and record.name:
                name = record.sequence +' '+record.name
            if record.sequence and record.name and record.firstname:
                name = record.sequence +' '+record.name+' '+record.firstname
            result.append((record.id, name))
        return result
        
# ---------------------------------------------------------
# Patient
# ---------------------------------------------------------
class PATIENT(models.Model):
    _name = "gestion.clinique.patient"
    _description = "La fiche patient"

    date_consultation = fields.Date(string="Date Consultation")
    motif_consultation = fields.Char(string='Motif de la consultation')
    antecedents = fields.Text(string='Antécédents')
    femme_enceinte = fields.Boolean(string="Femme enceinte")
    observation = fields.Text(string='Obervation')

    patient_info_id = fields.Many2one('gestion.clinique.patient.info', string='Patient', required=True)

    patient_rdv_ids = fields.One2many('gestion.clinique.patient.rdv', 'patient_id', string='Patient RDV')
    radiographie_ids = fields.One2many('gestion.clinique.radiographie', 'patient_id', string='Radiographie')
    diagnostic_ids = fields.One2many('gestion.clinique.diagnostic', 'patient_id', string='Diagnostic')
    traitement_ids = fields.One2many('gestion.clinique.traitement', 'patient_id', string='Traitement')



    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        vals['date_consultation'] = str(date.today())
        res  =  super(PATIENT, self).create(vals)        
        return res

    @api.multi
    def write(self, vals):
        rep  =  super(PATIENT, self).write(vals)
        return rep

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if record.patient_info_id.name:
                name = record.patient_info_id.name 
            if record.patient_info_id.name and record.patient_info_id.firstname:
                name = record.patient_info_id.firstname +' '+record.patient_info_id.name
            if record.patient_info_id.sequence and record.patient_info_id.name:
                name = record.patient_info_id.sequence +' '+record.patient_info_id.name
            if record.patient_info_id.sequence and record.patient_info_id.name and record.patient_info_id.firstname:
                name = record.patient_info_id.sequence +' '+record.patient_info_id.name+' '+record.patient_info_id.firstname
            result.append((record.id, name))
        return result

class PatientRDV(models.Model):
    _name = "gestion.clinique.patient.rdv"
    _description = "RDV Patient"

    currency_id = fields.Many2one('res.currency', 'Currency', required=True,\
        default=lambda self: self.env.user.company_id.currency_id.id)

    sequence_rdv = fields.Char('Sequence', compute='compute_numero_rdv', store=True)
    date_rdv = fields.Date(string='Date', required=True)
    avance = fields.Monetary()
    reste = fields.Monetary()

    patient_id = fields.Many2one('gestion.clinique.patient', string='Patient', required=True)
    mes_rendez_vous_id = fields.Many2one('mes.rendez.vous', string='Mes rendez vous')
    
    @api.multi
    @api.depends('patient_id')
    def compute_numero_rdv(self):
        for patient in self.mapped('patient_id'):
            number = 0
            for line in patient.patient_rdv_ids:
                line.sequence_rdv =  'RDV ' + str(number)
                number += 1

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        res  =  super(PatientRDV, self).create(vals)        
        return res

    @api.multi
    def write(self, vals):
        rep  =  super(PatientRDV, self).write(vals)
        return rep

class Radiographie(models.Model):
    _name = "gestion.clinique.radiographie"
    _description = "Radiographie"

    lien = fields.Char(string="Lien", required=True)
    nom = fields.Char()
    commentaire = fields.Char()

    patient_id = fields.Many2one('gestion.clinique.patient', string='Radiographie')

class PatientDiagnostic(models.Model):
    _name = "gestion.clinique.diagnostic"
    _description = "Diagnostic"

    type = fields.Selection(TYPE_DENT,string="Type dent", required=True)
    nom = fields.Char(string='Nom', required=True)

    patient_id = fields.Many2one('gestion.clinique.patient', string='Diagnostic')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = record.type +' '+ record.nom 
            result.append((record.id, name))
        return result

class PatientTraitement(models.Model):
    _name = "gestion.clinique.traitement"
    _description = "Traitement"

    type = fields.Selection(TYPE_DENT,string="Type dent", required=True)
    nom = fields.Char(string='Nom', required=True)

    patient_id = fields.Many2one('gestion.clinique.patient', string='Traitement')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = record.type +' '+record.nom 
            result.append((record.id, name))
        return result


