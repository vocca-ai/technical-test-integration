#!/usr/bin/env python3
"""
MedScheduler API - API 1
Authentification: API Key
Format: JSON simple et direct
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import uuid
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
API_KEY = "medscheduler_key_12345"

# Base de données simulée
appointments = []
patients = []

# Données de test
test_patients = [
    {
        "id": "pat_001",
        "first_name": "Jean",
        "last_name": "Dupont",
        "birth_date": "1985-03-15",
        "phone": "+33123456789",
        "email": "jean.dupont@email.com",
        "address": "123 Rue de la Santé, 75014 Paris",
        "created_at": "2024-01-15T10:30:00Z"
    },
    {
        "id": "pat_002", 
        "first_name": "Marie",
        "last_name": "Martin",
        "birth_date": "1992-07-22",
        "phone": "+33987654321",
        "email": "marie.martin@email.com",
        "address": "456 Avenue des Médecins, 69001 Lyon",
        "created_at": "2024-01-20T14:15:00Z"
    }
]

test_appointments = [
    {
        "id": "apt_001",
        "patient_id": "pat_001",
        "doctor_name": "Dr. Leblanc",
        "appointment_date": "2024-03-20",
        "appointment_time": "14:30",
        "duration_minutes": 30,
        "type": "consultation",
        "status": "scheduled",
        "notes": "Consultation de routine",
        "created_at": "2024-01-15T11:00:00Z"
    },
    {
        "id": "apt_002",
        "patient_id": "pat_002", 
        "doctor_name": "Dr. Rousseau",
        "appointment_date": "2024-03-25",
        "appointment_time": "09:15",
        "duration_minutes": 45,
        "type": "specialist",
        "status": "confirmed",
        "notes": "Consultation spécialisée cardiologie",
        "created_at": "2024-01-20T15:30:00Z"
    }
]

# Initialiser avec les données de test
patients.extend(test_patients)
appointments.extend(test_appointments)

def require_api_key(f):
    """Décorateur pour vérifier l'API key"""
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != API_KEY:
            return jsonify({"error": "Invalid or missing API key"}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "api": "MedScheduler",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

# PATIENTS ENDPOINTS
@app.route('/patients', methods=['GET'])
@require_api_key
def get_patients():
    """Récupérer tous les patients"""
    return jsonify({
        "patients": patients,
        "total": len(patients)
    })

@app.route('/patients/<patient_id>', methods=['GET'])
@require_api_key
def get_patient(patient_id):
    """Récupérer un patient spécifique"""
    patient = next((p for p in patients if p["id"] == patient_id), None)
    if not patient:
        return jsonify({"error": "Patient not found"}), 404
    return jsonify(patient)

@app.route('/patients', methods=['POST'])
@require_api_key
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
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    
    patients.append(patient)
    return jsonify(patient), 201

# APPOINTMENTS ENDPOINTS
@app.route('/appointments', methods=['GET'])
@require_api_key
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
@require_api_key
def get_appointment(appointment_id):
    """Récupérer un rendez-vous spécifique"""
    appointment = next((a for a in appointments if a["id"] == appointment_id), None)
    if not appointment:
        return jsonify({"error": "Appointment not found"}), 404
    return jsonify(appointment)

@app.route('/appointments', methods=['POST'])
@require_api_key
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
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    
    appointments.append(appointment)
    return jsonify(appointment), 201

@app.route('/appointments/<appointment_id>', methods=['PUT'])
@require_api_key
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
    print(f"📋 API Key: {API_KEY}")
    print("📚 Test data loaded:")
    print(f"   - {len(patients)} patients")
    print(f"   - {len(appointments)} appointments")
    app.run(debug=False, port=port, host='0.0.0.0')
