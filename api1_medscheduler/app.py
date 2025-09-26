#!/usr/bin/env python3
"""
MedScheduler API - API 1
Authentification: HMAC Signature (très sécurisée)
Format: JSON simple et direct
"""

from flask import Flask, request, jsonify
try:
    from flask_cors import CORS
except ImportError:
    CORS = None
from datetime import datetime, timedelta
import uuid
import json
import hmac
import hashlib
import base64
import time

app = Flask(__name__)
if CORS:
    CORS(app)  # Enable CORS for all routes

# Configuration HMAC
CLIENT_ID = "medscheduler_client"
SECRET_KEY = "medscheduler_secret_key_2024_very_secure"
SIGNATURE_VALIDITY_SECONDS = 300  # 5 minutes

# Base de données simulée
appointments = []
patients = []

# Données de test
test_patients = [
    {
        "id": "pat_001",
        "first_name": "Jean",
        "last_name": "Dupont",
        "birth_date": "15/03/1985",
        "phone": "+33123456789",
        "email": "jean.dupont@email.com",
        "address": "123 Rue de la Santé, 75014 Paris",
        "created_at": "2024/01/15 10:30:00"
    },
    {
        "id": "pat_002", 
        "first_name": "Marie",
        "last_name": "Martin",
        "birth_date": "22/07/1992",
        "phone": "+33987654321",
        "email": "marie.martin@email.com",
        "address": "456 Avenue des Médecins, 69001 Lyon",
        "created_at": "2024/01/20 14:15:00"
    }
]

test_appointments = [
    {
        "id": "apt_001",
        "patient_id": "pat_001",
        "doctor_name": "Dr. Leblanc",
        "appointment_date": "20-03-2024",
        "appointment_time": "2:30 PM",
        "duration_minutes": 30,
        "type": "consultation",
        "status": "scheduled",
        "notes": "Consultation de routine",
        "created_at": "2024/01/15 11:00:00"
    },
    {
        "id": "apt_002",
        "patient_id": "pat_002", 
        "doctor_name": "Dr. Rousseau",
        "appointment_date": "25-03-2024",
        "appointment_time": "9:15 AM",
        "duration_minutes": 45,
        "type": "specialist",
        "status": "confirmed",
        "notes": "Consultation spécialisée cardiologie",
        "created_at": "2024/01/20 15:30:00"
    }
]

# Initialiser avec les données de test
patients.extend(test_patients)
appointments.extend(test_appointments)

def generate_signature(method, path, timestamp, body=""):
    """Générer une signature HMAC pour la requête"""
    # Créer la chaîne à signer
    string_to_sign = f"{method}\n{path}\n{timestamp}\n{body}"
    
    # Générer la signature HMAC-SHA256
    signature = hmac.new(
        SECRET_KEY.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha256
    ).digest()
    
    # Encoder en base64
    return base64.b64encode(signature).decode('utf-8')

def require_hmac_auth(f):
    """Décorateur pour vérifier l'authentification HMAC"""
    def decorated_function(*args, **kwargs):
        # Récupérer les headers requis
        client_id = request.headers.get('X-Client-ID')
        timestamp = request.headers.get('X-Timestamp')
        signature = request.headers.get('X-Signature')
        
        if not all([client_id, timestamp, signature]):
            return jsonify({
                "error": "Missing authentication headers",
                "required": ["X-Client-ID", "X-Timestamp", "X-Signature"]
            }), 401
        
        # Vérifier le client ID
        if client_id != CLIENT_ID:
            return jsonify({"error": "Invalid client ID"}), 401
        
        # Vérifier que le timestamp est récent (protection contre replay attacks)
        try:
            request_time = int(timestamp)
            current_time = int(time.time())
            
            if abs(current_time - request_time) > SIGNATURE_VALIDITY_SECONDS:
                return jsonify({
                    "error": "Request timestamp too old or too far in the future",
                    "max_age_seconds": SIGNATURE_VALIDITY_SECONDS
                }), 401
        except ValueError:
            return jsonify({"error": "Invalid timestamp format"}), 401
        
        # Récupérer le body de la requête
        body = ""
        if request.method in ['POST', 'PUT', 'PATCH']:
            body = request.get_data(as_text=True)
        
        # Générer la signature attendue
        expected_signature = generate_signature(
            request.method,
            request.path,
            timestamp,
            body
        )
        
        # Vérifier la signature (comparaison sécurisée)
        if not hmac.compare_digest(signature, expected_signature):
            return jsonify({
                "error": "Invalid signature",
                "debug_info": {
                    "method": request.method,
                    "path": request.path,
                    "timestamp": timestamp,
                    "body_length": len(body)
                }
            }), 401
        
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "api": "MedScheduler",
        "version": "1.1.0",
        "authentication": "HMAC-SHA256 Signature",
        "timestamp": datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")
    })

@app.route('/auth/signature-helper', methods=['POST'])
def signature_helper():
    """Endpoint d'aide pour générer une signature (développement uniquement)"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "JSON data required"}), 400
    
    method = data.get('method', 'GET').upper()
    path = data.get('path', '/')
    body = data.get('body', '')
    timestamp = data.get('timestamp', str(int(time.time())))
    
    signature = generate_signature(method, path, timestamp, body)
    
    return jsonify({
        "signature": signature,
        "headers": {
            "X-Client-ID": CLIENT_ID,
            "X-Timestamp": timestamp,
            "X-Signature": signature
        },
        "string_to_sign": f"{method}\n{path}\n{timestamp}\n{body}",
        "expires_in": SIGNATURE_VALIDITY_SECONDS
    })

# PATIENTS ENDPOINTS
@app.route('/patients', methods=['GET'])
@require_hmac_auth
def get_patients():
    """Récupérer tous les patients"""
    return jsonify({
        "patients": patients,
        "total": len(patients)
    })

@app.route('/patients/<patient_id>', methods=['GET'])
@require_hmac_auth
def get_patient(patient_id):
    """Récupérer un patient spécifique"""
    patient = next((p for p in patients if p["id"] == patient_id), None)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    return jsonify(patient)

@app.route('/patients', methods=['POST'])
@require_hmac_auth
def create_patient():
    """Créer un nouveau patient"""
    data = request.get_json()
    
    required_fields = ["first_name", "last_name", "birth_date", "phone"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    patient = {
        "id": f"pat_{uuid.uuid4().hex[:8]}",
        "first_name": data["first_name"],
        "last_name": data["last_name"], 
        "birth_date": data["birth_date"],
        "phone": data["phone"],
        "email": data.get("email", ""),
        "address": data.get("address", ""),
        "created_at": datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")
    }
    
    patients.append(patient)
    return jsonify(patient), 201

# APPOINTMENTS ENDPOINTS
@app.route('/appointments', methods=['GET'])
@require_hmac_auth
def get_appointments():
    """Récupérer tous les rendez-vous"""
    # Filtrage optionnel par date
    date_filter = request.args.get('date')
    filtered_appointments = appointments
    
    if date_filter:
        filtered_appointments = [apt for apt in appointments if apt["appointment_date"] == date_filter]
    
    return jsonify({
        "appointments": filtered_appointments,
        "total": len(filtered_appointments)
    })

@app.route('/appointments/<appointment_id>', methods=['GET'])
@require_hmac_auth
def get_appointment(appointment_id):
    """Récupérer un rendez-vous spécifique"""
    appointment = next((a for a in appointments if a["id"] == appointment_id), None)
    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404
    return jsonify(appointment)

@app.route('/appointments', methods=['POST'])
@require_hmac_auth
def create_appointment():
    """Créer un nouveau rendez-vous"""
    data = request.get_json()
    
    required_fields = ["patient_id", "doctor_name", "appointment_date", "appointment_time"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Vérifier que le patient existe
    patient_exists = any(p["id"] == data["patient_id"] for p in patients)
    if not patient_exists:
        return jsonify({"error": "Patient not found"}), 400
    
    appointment = {
        "id": f"apt_{uuid.uuid4().hex[:8]}",
        "patient_id": data["patient_id"],
        "doctor_name": data["doctor_name"],
        "appointment_date": data["appointment_date"],
        "appointment_time": data["appointment_time"],
        "duration_minutes": data.get("duration_minutes", 30),
        "type": data.get("type", "consultation"),
        "status": data.get("status", "scheduled"),
        "notes": data.get("notes", ""),
        "created_at": datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S")
    }
    
    appointments.append(appointment)
    return jsonify(appointment), 201

@app.route('/appointments/<appointment_id>', methods=['PUT'])
@require_hmac_auth
def update_appointment(appointment_id):
    """Mettre à jour un rendez-vous"""
    appointment = next((a for a in appointments if a["id"] == appointment_id), None)
    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404
    
    data = request.get_json()
    
    # Mettre à jour les champs fournis
    updatable_fields = ["doctor_name", "appointment_date", "appointment_time", 
                       "duration_minutes", "type", "status", "notes"]
    
    for field in updatable_fields:
        if field in data:
            appointment[field] = data[field]
    
    return jsonify(appointment)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5001))
    print("🏥 MedScheduler API starting...")
    print("🔐 HMAC-SHA256 Authentication enabled")
    print("📋 Authentication details:")
    print(f"   Client ID: {CLIENT_ID}")
    print(f"   Signature validity: {SIGNATURE_VALIDITY_SECONDS} seconds")
    print("📚 Test data loaded:")
    print(f"   - {len(patients)} patients")
    print(f"   - {len(appointments)} appointments")
    print("🔧 Use /auth/signature-helper to generate signatures")
    app.run(debug=False, port=port, host='0.0.0.0')
