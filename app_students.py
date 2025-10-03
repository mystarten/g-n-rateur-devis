# app_students.py - Application Flask pour les élèves
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime, timedelta
import uuid
import os
from functools import wraps
from models import Devis, DevisItem, Facture
from pdf_generator_students import generate_student_style_devis, generate_pdf_facture
from pdf_generator_students import generate_student_style_devis, generate_pdf_facture, generate_pdf_devis
# Créer l'application Flask
app = Flask(__name__)
CORS(app)  # Permet les requêtes depuis d'autres domaines

# Configuration
app.config['UPLOAD_FOLDER'] = 'generated'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Clés API (à stocker dans des variables d'environnement en production)
API_KEY_1 = os.environ.get('API_KEY_1', 'your-secret-key-1-here')
API_KEY_2 = os.environ.get('API_KEY_2', 'your-secret-key-2-here')

# Thèmes disponibles
THEMES_DISPONIBLES = ['bleu', 'vert', 'rouge', 'violet', 'orange', 'noir']

def require_api_keys(f):
    """Décorateur pour vérifier les 2 clés API"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Vérifier les headers
        key1 = request.headers.get('X-API-Key-1')
        key2 = request.headers.get('X-API-Key-2')
        
        if not key1 or not key2:
            return jsonify({"error": "Clés API manquantes"}), 401
        
        if key1 != API_KEY_1 or key2 != API_KEY_2:
            return jsonify({"error": "Clés API invalides"}), 401
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET'])
def documentation():
    """
    Page d'accueil avec la documentation de l'API
    """
    doc = {
        "titre": "🧾 API Générateur de Devis - Version Formation",
        "description": "API simple pour générer des devis PDF avec un design professionnel",
        "version": "1.0.0",
        "author": "Formation Développement Web",
        
        "endpoints": {
            "GET /": "Cette documentation",
            "GET /health": "Vérifier l'état de l'API",
            "GET /api/themes": "Obtenir la liste des thèmes disponibles",
            "GET /api/exemple": "Obtenir un exemple de données JSON",
            "POST /api/devis": "Créer un devis personnalisé",
            "POST /api/facture": "Créer une facture personnalisée",
            "POST /api/test": "Générer un devis de test rapide",
            "GET /api/test-auth": "Tester l'authentification avec les clés API"
        },
        
        "authentification": {
            "description": "Cette API nécessite 2 clés API dans les headers",
            "headers_requis": {
                "X-API-Key-1": "Votre première clé API",
                "X-API-Key-2": "Votre deuxième clé API"
            },
            "exemple_curl_auth": """
curl -X GET http://localhost:5000/api/test-auth \\
  -H "X-API-Key-1: your-secret-key-1-here" \\
  -H "X-API-Key-2: your-secret-key-2-here"
            """
        },
        
        "utilisation": {
            "exemple_curl": """
curl -X POST http://localhost:5000/api/devis \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key-1: your-secret-key-1-here" \\
  -H "X-API-Key-2: your-secret-key-2-here" \\
  -d '{
    "client_nom": "Mon Client",
    "client_adresse": "123 Rue Example, Paris",
    "fournisseur_nom": "Ma Société",
    "theme": "bleu",
    "format": "pdf",
    "items": [
      {
        "description": "Formation web",
        "prix_unitaire": 500.0,
        "quantite": 2
      }
    ]
  }' \\
  --output devis.pdf
            """,
            
            "exemple_javascript": """
fetch('/api/devis', {
  method: 'POST',
  headers: { 
    'Content-Type': 'application/json',
    'X-API-Key-1': 'your-secret-key-1-here',
    'X-API-Key-2': 'your-secret-key-2-here'
  },
  body: JSON.stringify({
    client_nom: 'Mon Client',
    theme: 'vert',
    format: 'docx',
    items: [{
      description: 'Ma prestation',
      prix_unitaire: 500.0,
      quantite: 1
    }]
  })
})
.then(response => response.blob())
.then(blob => {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'devis.docx';
  a.click();
});
            """
        },
        
        "champs_obligatoires": ["client_nom", "items"],
        "formats_supportes": ["pdf", "docx"],
        "themes_disponibles": THEMES_DISPONIBLES,
        "note": "📚 Parfait pour apprendre le développement d'API avec Flask !"
    }
    
    return jsonify(doc), 200

@app.route('/health', methods=['GET'])
def health_check():
    """
    Vérifier que l'API fonctionne correctement
    """
    return jsonify({
        "status": "healthy",
        "message": "✅ API Devis Formation - Tout fonctionne !",
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "version": "1.0.0"
    }), 200

@app.route('/api/themes', methods=['GET'])
def get_themes():
    """Retourner la liste des thèmes disponibles"""
    return jsonify({
        "themes_disponibles": THEMES_DISPONIBLES,
        "theme_par_defaut": "bleu"
    }), 200

@app.route('/api/exemple', methods=['GET'])
def get_exemple():
    """
    Retourner un exemple complet de données JSON pour créer un devis
    """
    exemple = {
        "numero": f"FORM-{datetime.now().strftime('%Y%m%d')}-001",
        "date_emission": datetime.now().strftime('%d/%m/%Y'),
        "date_expiration": (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y'),
        "date_debut": (datetime.now() + timedelta(days=7)).strftime('%d/%m/%Y'),
        
        # Informations fournisseur (modifiables)
        "fournisseur_nom": "Formation Web Academy",
        "fournisseur_adresse": "123 Rue de la Formation",
        "fournisseur_ville": "75001 Paris, France",
        "fournisseur_email": "contact@formation-web.fr",
        "fournisseur_siret": "12345678901234",
        "fournisseur_telephone": "+33 1 23 45 67 89",
        
        # Informations client
        "client_nom": "Entreprise Cliente SARL",
        "client_adresse": "456 Avenue du Commerce",
        "client_ville": "69000 Lyon, France",
        "client_email": "client@entreprise.com",
        "client_siret": "98765432109876",
        "client_telephone": "+33 4 56 78 90 12",
        "client_tva": "FR12345678901",
        
        # Informations bancaires
        "banque_nom": "Banque Populaire",
        "banque_iban": "FR76 1234 5678 9012 3456 7890 123",
        "banque_bic": "CCBPFRPPXXX",
        
        # Logo et thème
        "logo_url": "https://example.com/logo.png",
        "theme": "bleu",
        "format": "pdf",
        
        # Textes personnalisés
        "texte_intro": "Suite à notre entretien, nous avons le plaisir de vous proposer nos services.",
        "texte_conclusion": "Nous restons à votre disposition pour toute information complémentaire.",
        
        # Articles/prestations
        "items": [
            {
                "description": "Formation développement web complète",
                "prix_unitaire": 800.0,
                "quantite": 5,
                "tva_taux": 20,
                "remise": 0,
                "details": [
                    "HTML5 / CSS3 avancé",
                    "JavaScript ES6+",
                    "Framework React",
                    "API REST"
                ]
            },
            {
                "description": "Support technique post-formation",
                "prix_unitaire": 150.0,
                "quantite": 2,
                "tva_taux": 20,
                "remise": 0
            },
            {
                "description": "Accès plateforme e-learning (1 an)",
                "prix_unitaire": 299.0,
                "quantite": 1,
                "tva_taux": 20,
                "remise": 50
            }
        ]
    }
    
    return jsonify({
        "message": "📝 Exemple de données pour créer un devis",
        "exemple_donnees": exemple,
        "total_exemple": sum((item['prix_unitaire'] * item['quantite']) - item.get('remise', 0) for item in exemple['items']),
        "instructions": {
            "endpoint": "/api/devis",
            "methode": "POST",
            "content_type": "application/json",
            "champs_requis": ["client_nom", "items"],
            "formats_disponibles": ["pdf", "docx"],
            "note": "💡 Les autres champs ont des valeurs par défaut si non spécifiés"
        }
    }), 200

@app.route('/api/devis', methods=['POST'])
@require_api_keys
def create_devis():
    """
    Créer un devis personnalisé avec les données fournies
    """
    try:
        # Récupérer les données JSON
        data = request.json
        
        if not data:
            return jsonify({"error": "❌ Aucune donnée reçue"}), 400
        
        # Récupérer et valider le thème
        theme = data.get('theme', 'bleu')
        if theme not in THEMES_DISPONIBLES:
            theme = 'bleu'  # fallback vers le thème par défaut
        
        # Valider les champs obligatoires
        if not data.get('client_nom'):
            return jsonify({"error": "❌ Le champ 'client_nom' est obligatoire"}), 400
        
        if not data.get('items') or len(data.get('items', [])) == 0:
            return jsonify({"error": "❌ Au moins un article est requis"}), 400
        
        # Créer l'objet devis avec toutes les options modifiables
        devis = Devis(
            numero=data.get('numero', f"D-{datetime.now().year}-{str(uuid.uuid4())[:3]}"),
            date_emission=data.get('date_emission', datetime.now().strftime('%d/%m/%Y')),
            date_expiration=data.get('date_expiration', (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y')),
            
            # Informations fournisseur (tout modifiable)
            fournisseur_nom=data.get('fournisseur_nom', 'Infinytia'),
            fournisseur_adresse=data.get('fournisseur_adresse', '61 Rue De Lyon'),
            fournisseur_ville=data.get('fournisseur_ville', '75012 Paris, FR'),
            fournisseur_email=data.get('fournisseur_email', 'contact@infinytia.com'),
            fournisseur_siret=data.get('fournisseur_siret', '93968736400017'),
            fournisseur_telephone=data.get('fournisseur_telephone', '+33 1 23 45 67 89'),
            
            # Informations client
            client_nom=data.get('client_nom'),
            client_adresse=data.get('client_adresse', ''),
            client_ville=data.get('client_ville', ''),
            client_siret=data.get('client_siret', ''),
            client_tva=data.get('client_tva', ''),
            client_telephone=data.get('client_telephone', ''),
            client_email=data.get('client_email', ''),
            
            # Logo de l'entreprise
            logo_url=data.get('logo_url', ''),
            
            # Informations bancaires (modifiables)
            banque_nom=data.get('banque_nom', 'BNP Paribas'),
            banque_iban=data.get('banque_iban', 'FR76 3000 4008 2800 0123 4567 890'),
            banque_bic=data.get('banque_bic', 'BNPAFRPPXXX'),
            
            # Conditions de paiement
            conditions_paiement=data.get('conditions_paiement', 'Paiement à 30 jours'),
            penalites_retard=data.get('penalites_retard', 'En cas de retard de paiement, une pénalité de 3 fois le taux d\'intérêt légal sera appliquée'),
            
            # Texte personnalisé
            texte_intro=data.get('texte_intro', ''),
            texte_conclusion=data.get('texte_conclusion', 'Nous restons à votre disposition pour toute information complémentaire.'),
            
            # Articles
            items=[]
        )
        
        # Ajouter les articles
        for item_data in data.get('items', []):
            item = DevisItem(
                description=item_data.get('description'),
                details=item_data.get('details', []),
                quantite=item_data.get('quantite', 1),
                prix_unitaire=item_data.get('prix_unitaire', 0),
                tva_taux=item_data.get('tva_taux', 20),
                remise=item_data.get('remise', 0)
            )
            devis.items.append(item)
        
        # Calculer les totaux
        devis.calculate_totals()
        
        # Format de sortie demandé
        output_format = data.get('format', 'pdf').lower()
        
        if output_format == 'pdf':
            filename = generate_pdf_devis(devis, theme=theme)
            mimetype = 'application/pdf'
        elif output_format == 'docx':
            filename = generate_docx_devis(devis, theme=theme)
            mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        else:
            return jsonify({"error": "Format non supporté. Utilisez 'pdf' ou 'docx'"}), 400
        
        # Retourner le fichier
        return send_file(
            filename,
            mimetype=mimetype,
            as_attachment=True,
            download_name=f"devis_{devis.numero}_{theme}.{output_format}"
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/facture', methods=['POST'])
@require_api_keys
def create_facture():
    """Créer une nouvelle facture avec les données reçues"""
    try:
        data = request.json
        
        # Récupérer et valider le thème
        theme = data.get('theme', 'bleu')
        if theme not in THEMES_DISPONIBLES:
            theme = 'bleu'  # fallback vers le thème par défaut
        
        # Créer l'objet facture
        facture = Facture(
            numero=data.get('numero', f"F-{datetime.now().year}-{str(uuid.uuid4())[:3]}"),
            date_emission=data.get('date_emission', datetime.now().strftime('%d/%m/%Y')),
            date_echeance=data.get('date_echeance', (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y')),
            
            # Informations fournisseur
            fournisseur_nom=data.get('fournisseur_nom', 'Infinytia'),
            fournisseur_adresse=data.get('fournisseur_adresse', '61 Rue De Lyon'),
            fournisseur_ville=data.get('fournisseur_ville', '75012 Paris, FR'),
            fournisseur_email=data.get('fournisseur_email', 'contact@infinytia.com'),
            fournisseur_siret=data.get('fournisseur_siret', '93968736400017'),
            fournisseur_telephone=data.get('fournisseur_telephone', '+33 1 23 45 67 89'),
            
            # Informations client
            client_nom=data.get('client_nom'),
            client_adresse=data.get('client_adresse'),
            client_ville=data.get('client_ville'),
            client_siret=data.get('client_siret'),
            client_tva=data.get('client_tva'),
            client_telephone=data.get('client_telephone', ''),
            client_email=data.get('client_email', ''),
            
            # Logo de l'entreprise
            logo_url=data.get('logo_url', ''),
            
            # Informations bancaires
            banque_nom=data.get('banque_nom', 'BNP Paribas'),
            banque_iban=data.get('banque_iban', 'FR76 3000 4008 2800 0123 4567 890'),
            banque_bic=data.get('banque_bic', 'BNPAFRPPXXX'),
            
            # Conditions et statut
            conditions_paiement=data.get('conditions_paiement', 'Paiement à réception'),
            penalites_retard=data.get('penalites_retard', 'En cas de retard de paiement, une pénalité de 3 fois le taux d\'intérêt légal sera appliquée'),
            statut_paiement=data.get('statut_paiement', 'En attente'),
            
            # Références
            numero_commande=data.get('numero_commande', ''),
            reference_devis=data.get('reference_devis', ''),
            
            # Articles
            items=[]
        )
        
        # Ajouter les articles
        for item_data in data.get('items', []):
            item = DevisItem(
                description=item_data.get('description'),
                details=item_data.get('details', []),
                quantite=item_data.get('quantite', 1),
                prix_unitaire=item_data.get('prix_unitaire', 0),
                tva_taux=item_data.get('tva_taux', 20),
                remise=item_data.get('remise', 0)
            )
            facture.items.append(item)
        
        # Calculer les totaux
        facture.calculate_totals()
        
        # Format de sortie
        output_format = data.get('format', 'pdf').lower()
        
        if output_format == 'pdf':
            filename = generate_pdf_facture(facture, theme=theme)
            mimetype = 'application/pdf'
        elif output_format == 'docx':
            filename = generate_docx_facture(facture, theme=theme)
            mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        else:
            return jsonify({"error": "Format non supporté"}), 400
        
        return send_file(
            filename,
            mimetype=mimetype,
            as_attachment=True,
            download_name=f"facture_{facture.numero}_{theme}.{output_format}"
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/test', methods=['POST'])
@require_api_keys
def test_devis():
    """
    Générer un devis de test rapidement (sans paramètres)
    """
    try:
        # Données de test prédéfinies
        test_data = {
            "numero": f"TEST-{datetime.now().strftime('%H%M%S')}",
            "date_emission": datetime.now().strftime('%d/%m/%Y'),
            "date_expiration": (datetime.now() + timedelta(days=30)).strftime('%d/%m/%Y'),
            
            "fournisseur_nom": "Formation Test Academy",
            "fournisseur_adresse": "123 Rue de Test",
            "fournisseur_ville": "75001 Paris, France",
            "fournisseur_email": "test@formation.fr",
            
            "client_nom": "Client de Test",
            "client_adresse": "456 Avenue du Test",
            "client_ville": "69000 Lyon",
            "client_email": "client.test@exemple.com",
            
            "banque_nom": "Banque de Test",
            "banque_iban": "FR76 1234 5678 9012 3456 7890 123",
            "banque_bic": "TESTFRPP",
            
            "items": [
                {
                    "description": "Formation développement web",
                    "prix_unitaire": 750.0,
                    "quantite": 3,
                    "tva_taux": 20,
                    "remise": 0
                },
                {
                    "description": "Support technique",
                    "prix_unitaire": 100.0,
                    "quantite": 1,
                    "tva_taux": 20,
                    "remise": 0
                }
            ]
        }
        
        # Créer l'objet devis
        devis = Devis(
            numero=test_data['numero'],
            date_emission=test_data['date_emission'],
            date_expiration=test_data['date_expiration'],
            
            fournisseur_nom=test_data['fournisseur_nom'],
            fournisseur_adresse=test_data['fournisseur_adresse'],
            fournisseur_ville=test_data['fournisseur_ville'],
            fournisseur_email=test_data['fournisseur_email'],
            fournisseur_siret='12345678901234',
            
            client_nom=test_data['client_nom'],
            client_adresse=test_data['client_adresse'],
            client_ville=test_data['client_ville'],
            client_siret='98765432109876',
            client_tva='FR98765432109',
            
            banque_nom=test_data['banque_nom'],
            banque_iban=test_data['banque_iban'],
            banque_bic=test_data['banque_bic']
        )
        
        # Ajouter les articles
        for item_data in test_data['items']:
            item = DevisItem(
                description=item_data['description'],
                prix_unitaire=item_data['prix_unitaire'],
                quantite=item_data['quantite'],
                tva_taux=item_data.get('tva_taux', 20),
                remise=item_data.get('remise', 0)
            )
            devis.items.append(item)
        
        # Calculer les totaux
        devis.calculate_totals()
        
        # Générer le PDF
        filename = generate_pdf_devis(devis)
        
        print(f"🧪 Devis de test généré : {test_data['numero']}")
        
        return send_file(
            filename,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"devis_test_{test_data['numero']}.pdf"
        )
        
    except Exception as e:
        print(f"❌ Erreur test: {str(e)}")
        return jsonify({"error": f"Erreur lors du test: {str(e)}"}), 500

@app.route('/api/test-auth', methods=['GET'])
@require_api_keys
def test_auth():
    """Endpoint pour tester l'authentification"""
    return jsonify({"message": "Authentification réussie!"}), 200

# Gestionnaire d'erreur 404
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "❌ Endpoint non trouvé",
        "message": "Consultez la documentation sur '/' pour voir les endpoints disponibles",
        "endpoints_disponibles": ["/", "/health", "/api/exemple", "/api/devis", "/api/test", "/api/test-auth", "/api/themes", "/api/facture"]
    }), 404

# Gestionnaire d'erreur 500
@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "❌ Erreur serveur",
        "message": "Une erreur interne s'est produite"
    }), 500

# Configuration pour Railway
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
