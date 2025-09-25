#!/usr/bin/env python3
"""
Documentation Web App
Interface moderne pour afficher les documentations Swagger des APIs
"""

from flask import Flask, render_template, jsonify, send_from_directory
import os
import yaml
import json

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'docs_app_secret_key_2024'

def load_swagger_spec(file_path):
    """Charger une spécification OpenAPI depuis un fichier YAML"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except Exception as e:
        print(f"Erreur lors du chargement de {file_path}: {e}")
        return None

@app.route('/')
def index():
    """Page d'accueil avec les deux documentations"""
    return render_template('index.html')

@app.route('/medscheduler')
def medscheduler_docs():
    """Documentation Swagger pour MedScheduler API"""
    return render_template('swagger.html', 
                         api_name='MedScheduler API (HMAC Auth)',
                         api_description='API simple avec authentification HMAC-SHA256 ultra-sécurisée',
                         spec_url='/api/medscheduler/spec')

@app.route('/healthcare-pro')
def healthcare_pro_docs():
    """Documentation Swagger pour HealthCare Pro API"""
    return render_template('swagger.html',
                         api_name='HealthCare Pro API (OAuth2 + JWT)', 
                         api_description='API hybride REST/HL7 avec OAuth 2.0 et refresh tokens',
                         spec_url='/api/healthcare-pro/spec')

@app.route('/api/medscheduler/spec')
def medscheduler_spec():
    """Retourner la spécification OpenAPI pour MedScheduler"""
    spec_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                            'swagger_specs', 'medscheduler_api.yaml')
    spec = load_swagger_spec(spec_path)
    if spec:
        return jsonify(spec)
    return jsonify({"error": "Specification not found"}), 404

@app.route('/api/healthcare-pro/spec')
def healthcare_pro_spec():
    """Retourner la spécification OpenAPI pour HealthCare Pro"""
    spec_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                            'swagger_specs', 'healthcare_pro_api.yaml')
    spec = load_swagger_spec(spec_path)
    if spec:
        return jsonify(spec)
    return jsonify({"error": "Specification not found"}), 404

@app.route('/health')
def health_check():
    """Health check pour l'app de documentation"""
    return jsonify({
        "status": "healthy",
        "service": "Documentation App",
        "version": "1.0.0"
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 3000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    print("📚 Documentation App starting...")
    print(f"🌐 Access at: http://localhost:{port}")
    print(f"🔧 Debug mode: {debug_mode}")
    print("📖 Available endpoints:")
    print("   - / : Page d'accueil")
    print("   - /medscheduler : Documentation MedScheduler API")
    print("   - /healthcare-pro : Documentation HealthCare Pro API")
    app.run(debug=debug_mode, port=port, host='0.0.0.0')
