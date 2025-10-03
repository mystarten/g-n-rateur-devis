# models.py
class DevisItem:
    def __init__(self, description, details=None, quantite=1, prix_unitaire=0, tva_taux=20, remise=0):
        self.description = description
        self.details = details or []
        self.quantite = quantite
        self.prix_unitaire = prix_unitaire
        self.tva_taux = tva_taux
        self.remise = remise
        self.total_ht = (quantite * prix_unitaire) - remise

class Devis:
    def __init__(self, numero, date_emission, date_expiration, 
                 fournisseur_nom, fournisseur_adresse, fournisseur_ville, fournisseur_email, fournisseur_siret,
                 client_nom, client_adresse, client_ville, client_siret, client_tva,
                 **kwargs):
        self.numero = numero
        self.date_emission = date_emission
        self.date_expiration = date_expiration
        
        # Fournisseur
        self.fournisseur_nom = fournisseur_nom
        self.fournisseur_adresse = fournisseur_adresse
        self.fournisseur_ville = fournisseur_ville
        self.fournisseur_email = fournisseur_email
        self.fournisseur_siret = fournisseur_siret
        self.fournisseur_telephone = kwargs.get('fournisseur_telephone', '')
        
        # Client
        self.client_nom = client_nom
        self.client_adresse = client_adresse
        self.client_ville = client_ville
        self.client_siret = client_siret
        self.client_tva = client_tva
        self.client_telephone = kwargs.get('client_telephone', '')
        self.client_email = kwargs.get('client_email', '')
        
        # Logo de l'entreprise
        self.logo_url = kwargs.get('logo_url', '')
        
        # Autres champs
        self.banque_nom = kwargs.get('banque_nom', '')
        self.banque_iban = kwargs.get('banque_iban', '')
        self.banque_bic = kwargs.get('banque_bic', '')
        self.conditions_paiement = kwargs.get('conditions_paiement', '')
        self.penalites_retard = kwargs.get('penalites_retard', '')
        self.texte_intro = kwargs.get('texte_intro', '')
        self.texte_conclusion = kwargs.get('texte_conclusion', '')
        
        self.items = []
        self.total_ht = 0
        self.total_tva = 0
        self.total_ttc = 0
    
    def calculate_totals(self):
        self.total_ht = sum(item.total_ht for item in self.items)
        self.total_tva = sum((item.total_ht * item.tva_taux / 100) for item in self.items)
        self.total_ttc = self.total_ht + self.total_tva

class Facture:
    def __init__(self, numero, date_emission, date_echeance,
                 fournisseur_nom, fournisseur_adresse, fournisseur_ville, fournisseur_email, fournisseur_siret,
                 client_nom, client_adresse, client_ville, client_siret, client_tva,
                 **kwargs):
        self.numero = numero
        self.date_emission = date_emission
        self.date_echeance = date_echeance
        
        # Fournisseur
        self.fournisseur_nom = fournisseur_nom
        self.fournisseur_adresse = fournisseur_adresse
        self.fournisseur_ville = fournisseur_ville
        self.fournisseur_email = fournisseur_email
        self.fournisseur_siret = fournisseur_siret
        self.fournisseur_telephone = kwargs.get('fournisseur_telephone', '')
        
        # Client
        self.client_nom = client_nom
        self.client_adresse = client_adresse
        self.client_ville = client_ville
        self.client_siret = client_siret
        self.client_tva = client_tva
        self.client_telephone = kwargs.get('client_telephone', '')
        self.client_email = kwargs.get('client_email', '')
        
        # Logo de l'entreprise
        self.logo_url = kwargs.get('logo_url', '')
        
        # Spécifique facture
        self.statut_paiement = kwargs.get('statut_paiement', 'En attente')
        self.numero_commande = kwargs.get('numero_commande', '')
        self.reference_devis = kwargs.get('reference_devis', '')
        
        # Autres champs
        self.banque_nom = kwargs.get('banque_nom', '')
        self.banque_iban = kwargs.get('banque_iban', '')
        self.banque_bic = kwargs.get('banque_bic', '')
        self.conditions_paiement = kwargs.get('conditions_paiement', '')
        self.penalites_retard = kwargs.get('penalites_retard', '')
        
        self.items = []
        self.total_ht = 0
        self.total_tva = 0
        self.total_ttc = 0
    
    def calculate_totals(self):
        self.total_ht = sum(item.total_ht for item in self.items)
        self.total_tva = sum((item.total_ht * item.tva_taux / 100) for item in self.items)
        self.total_ttc = self.total_ht + self.total_tva
