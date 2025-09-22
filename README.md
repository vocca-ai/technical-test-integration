# 📚 API Documentation Hub

Une interface web moderne et élégante pour explorer les documentations Swagger de nos APIs médicales.

## 🏥 APIs Disponibles

### 1. MedScheduler API
- **Port**: 5001
- **Authentification**: API Key (`X-API-Key: medscheduler_key_12345`)
- **Format**: JSON simple et direct
- **Fonctionnalités**:
  - Gestion des patients
  - Gestion des rendez-vous médicaux
  - Format simple pour intégrations rapides

### 2. HealthCare Pro API
- **Port**: 5002
- **Authentification**: JWT/OAuth (`Authorization: Bearer <token>`)
- **Format**: FHIR R4 + HL7 v2.4
- **Fonctionnalités**:
  - Patients au format FHIR
  - Rendez-vous au format FHIR
  - Messages HL7 ADT
  - Standards d'interopérabilité

### 3. Documentation Web App
- **Port**: 3000
- **Interface**: Swagger UI intégré
- **Fonctionnalités**:
  - Documentation interactive
  - Interface moderne et responsive
  - Test des APIs directement depuis l'interface

## 🚀 Démarrage Rapide

### Prérequis
```bash
pip install -r requirements.txt
```

### Lancement des services

1. **Démarrer MedScheduler API** (Terminal 1):
```bash
cd api1_medscheduler
python app.py
```
→ API disponible sur http://localhost:5001

2. **Démarrer HealthCare Pro API** (Terminal 2):
```bash
cd api2_healthcare_pro
python app.py
```
→ API disponible sur http://localhost:5002

3. **Démarrer la Documentation Web App** (Terminal 3):
```bash
cd docs_app
python app.py
```
→ Documentation disponible sur http://localhost:3000

## 📖 Utilisation de la Documentation

### Interface Web
1. Accédez à http://localhost:3000
2. Choisissez l'API à explorer :
   - **MedScheduler** : Documentation simple avec authentification par API Key
   - **HealthCare Pro** : Documentation avancée avec JWT et standards FHIR

### Authentification

#### MedScheduler API
```bash
# Exemple de requête
curl -H "X-API-Key: medscheduler_key_12345" \
     http://localhost:5001/patients
```

#### HealthCare Pro API
```bash
# 1. Obtenir un token
curl -X POST http://localhost:5002/auth/token \
     -H "Content-Type: application/json" \
     -d '{
       "client_id": "healthcare_pro_client",
       "client_secret": "healthcare_secret_2024"
     }'

# 2. Utiliser le token
curl -H "Authorization: Bearer <token>" \
     http://localhost:5002/fhir/Patient
```

## 🎨 Fonctionnalités de l'Interface

### Page d'Accueil
- **Vue d'ensemble** des deux APIs
- **Comparaison** des fonctionnalités
- **Démarrage rapide** avec exemples de code
- **Navigation intuitive**

### Documentation Swagger
- **Interface Swagger UI** moderne et responsive
- **Test interactif** des endpoints
- **Authentification intégrée**
- **Exemples de requêtes/réponses**
- **Schémas de données détaillés**

### Design
- **Interface moderne** avec Tailwind CSS
- **Responsive design** pour mobile et desktop
- **Thème cohérent** avec dégradés et animations
- **Navigation fluide** entre les sections

## 📁 Structure du Projet

```
├── api1_medscheduler/          # API MedScheduler
│   └── app.py
├── api2_healthcare_pro/        # API HealthCare Pro
│   └── app.py
├── docs_app/                   # Application de documentation
│   ├── app.py                  # Serveur Flask
│   └── templates/
│       ├── base.html           # Template de base
│       ├── index.html          # Page d'accueil
│       └── swagger.html        # Interface Swagger
├── swagger_specs/              # Spécifications OpenAPI
│   ├── medscheduler_api.yaml   # Spec MedScheduler
│   └── healthcare_pro_api.yaml # Spec HealthCare Pro
├── requirements.txt            # Dépendances Python
├── render.yaml                 # Configuration déploiement
└── README.md                   # Cette documentation
```

## 🌐 Déploiement

Le projet est configuré pour le déploiement sur Render.com avec 3 services :

1. **medscheduler-api** : API MedScheduler
2. **healthcare-pro-api** : API HealthCare Pro  
3. **api-documentation** : Interface de documentation

### Configuration Render
```yaml
services:
  - type: web
    name: api-documentation
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: cd docs_app && python app.py
    plan: free
```

## 🔧 Développement

### Ajouter une nouvelle API
1. Créer la spécification OpenAPI dans `swagger_specs/`
2. Ajouter une route dans `docs_app/app.py`
3. Mettre à jour la navigation dans les templates

### Personnaliser l'interface
- **Styles** : Modifier les CSS dans `templates/base.html`
- **Couleurs** : Utiliser les classes Tailwind CSS
- **Contenu** : Éditer les templates HTML

## 📊 Endpoints de Santé

Chaque service expose un endpoint `/health` :
- http://localhost:5001/health (MedScheduler)
- http://localhost:5002/health (HealthCare Pro)
- http://localhost:3000/health (Documentation)

## 🛡️ Sécurité

- **MedScheduler** : Authentification par API Key
- **HealthCare Pro** : Authentification JWT avec expiration
- **Documentation** : Accès public pour consultation

## 📝 Standards Supportés

- **OpenAPI 3.0.3** : Spécifications des APIs
- **FHIR R4** : Standard d'interopérabilité des données de santé
- **HL7 v2.4** : Messages ADT (Admit, Discharge, Transfer)
- **JWT** : Tokens d'authentification sécurisés

---

## 🚀 Prêt à explorer ?

1. Lancez les 3 services
2. Ouvrez http://localhost:3000
3. Explorez les documentations interactives !

**Bon développement ! 🎉**
