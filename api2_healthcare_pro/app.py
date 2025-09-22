#!/usr/bin/env python3
"""
HealthCare Pro API - API 2
Authentification: JWT/OAuth
Format: JSON complexe avec structure FHIR-like
Inclut un endpoint HL7 simulé
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, timedelta
import uuid
import jwt
import json
from functools import wraps

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration JWT
JWT_SECRET = "healthcare_pro_secret_key_2024"
JWT_ALGORITHM = "HS256"

# Base de données simulée
patients_db = []
appointments_db = []

# Données de test avec format complexe
test_patients_data = [
    {
        "resourceType": "Patient",
        "id": "hcp-patient-001",
        "meta": {
            "versionId": "1",
            "lastUpdated": "2024-01-15T10:30:00.000Z",
            "profile": ["http://healthcare-pro.com/fhir/Patient"]
        },
        "identifier": [
            {
                "use": "usual",
                "type": {
                    "coding": [{"system": "http://terminology.hl7.org/CodeSystem/v2-0203", "code": "MR"}]
                },
                "value": "HCP001"
            }
        ],
        "active": True,
        "name": [
            {
                "use": "official",
                "family": "Dubois",
                "given": ["Pierre", "Michel"]
            }
        ],
        "telecom": [
            {"system": "phone", "value": "+33145678901", "use": "home"},
            {"system": "email", "value": "pierre.dubois@email.com", "use": "home"}
        ],
        "gender": "male",
        "birthDate": "1978-11-08",
        "address": [
            {
                "use": "home",
                "line": ["789 Boulevard de l'Hôpital"],
                "city": "Marseille",
                "postalCode": "13001",
                "country": "FR"
            }
        ],
        "contact": [
            {
                "relationship": [
                    {"coding": [{"system": "http://terminology.hl7.org/CodeSystem/v2-0131", "code": "C"}]}
                ],
                "name": {"family": "Dubois", "given": ["Marie"]},
                "telecom": [{"system": "phone", "value": "+33145678902"}]
            }
        ]
    },
    {
        "resourceType": "Patient", 
        "id": "hcp-patient-002",
        "meta": {
            "versionId": "1",
            "lastUpdated": "2024-01-22T09:15:00.000Z",
            "profile": ["http://healthcare-pro.com/fhir/Patient"]
        },
        "identifier": [
            {
                "use": "usual",
                "type": {
                    "coding": [{"system": "http://terminology.hl7.org/CodeSystem/v2-0203", "code": "MR"}]
                },
                "value": "HCP002"
            }
        ],
        "active": True,
        "name": [
            {
                "use": "official", 
                "family": "Leroy",
                "given": ["Sophie", "Anne"]
            }
        ],
        "telecom": [
            {"system": "phone", "value": "+33156789012", "use": "mobile"},
            {"system": "email", "value": "sophie.leroy@email.com", "use": "work"}
        ],
        "gender": "female",
        "birthDate": "1990-05-14",
        "address": [
            {
                "use": "home",
                "line": ["321 Rue des Soins"],
                "city": "Toulouse", 
                "postalCode": "31000",
                "country": "FR"
            }
        ]
    }
]

test_appointments_data = [
    {
        "resourceType": "Appointment",
        "id": "hcp-appointment-001",
        "meta": {
            "versionId": "1", 
            "lastUpdated": "2024-01-15T11:30:00.000Z",
            "profile": ["http://healthcare-pro.com/fhir/Appointment"]
        },
        "status": "booked",
        "serviceCategory": [
            {
                "coding": [
                    {"system": "http://terminology.hl7.org/CodeSystem/service-category", "code": "17", "display": "General Practice"}
                ]
            }
        ],
        "serviceType": [
            {
                "coding": [
                    {"system": "http://snomed.info/sct", "code": "11429006", "display": "Consultation"}
                ]
            }
        ],
        "appointmentType": {
            "coding": [
                {"system": "http://terminology.hl7.org/CodeSystem/v2-0276", "code": "ROUTINE"}
            ]
        },
        "reasonCode": [
            {
                "coding": [
                    {"system": "http://snomed.info/sct", "code": "185349003", "display": "Encounter for check up"}
                ]
            }
        ],
        "priority": 5,
        "description": "Consultation de suivi médical général",
        "start": "2024-03-22T10:00:00.000Z",
        "end": "2024-03-22T10:30:00.000Z",
        "minutesDuration": 30,
        "participant": [
            {
                "actor": {
                    "reference": "Patient/hcp-patient-001",
                    "display": "Pierre Michel Dubois"
                },
                "required": "required",
                "status": "accepted"
            },
            {
                "actor": {
                    "reference": "Practitioner/dr-garcia",
                    "display": "Dr. Elena Garcia"
                },
                "required": "required", 
                "status": "accepted"
            }
        ],
        "requestedPeriod": [
            {
                "start": "2024-03-22T09:00:00.000Z",
                "end": "2024-03-22T12:00:00.000Z"
            }
        ]
    },
    {
        "resourceType": "Appointment",
        "id": "hcp-appointment-002",
        "meta": {
            "versionId": "1",
            "lastUpdated": "2024-01-22T14:45:00.000Z", 
            "profile": ["http://healthcare-pro.com/fhir/Appointment"]
        },
        "status": "confirmed",
        "serviceCategory": [
            {
                "coding": [
                    {"system": "http://terminology.hl7.org/CodeSystem/service-category", "code": "408", "display": "Cardiology"}
                ]
            }
        ],
        "serviceType": [
            {
                "coding": [
                    {"system": "http://snomed.info/sct", "code": "40701008", "display": "Echocardiography"}
                ]
            }
        ],
        "appointmentType": {
            "coding": [
                {"system": "http://terminology.hl7.org/CodeSystem/v2-0276", "code": "FOLLOWUP"}
            ]
        },
        "priority": 3,
        "description": "Échocardiographie de contrôle post-opératoire",
        "start": "2024-03-28T14:15:00.000Z", 
        "end": "2024-03-28T15:00:00.000Z",
        "minutesDuration": 45,
        "participant": [
            {
                "actor": {
                    "reference": "Patient/hcp-patient-002",
                    "display": "Sophie Anne Leroy"
                },
                "required": "required",
                "status": "accepted"
            },
            {
                "actor": {
                    "reference": "Practitioner/dr-bernard",
                    "display": "Dr. Thomas Bernard"
                },
                "required": "required",
                "status": "accepted"
            }
        ]
    }
]

# Initialiser avec les données de test
patients_db.extend(test_patients_data)
appointments_db.extend(test_appointments_data)

def generate_jwt_token(user_id="healthcare_user"):
    """Générer un token JWT"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow(),
        'scope': ['read:patients', 'write:patients', 'read:appointments', 'write:appointments']
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def require_jwt_auth(f):
    """Décorateur pour vérifier le token JWT"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({"error": "Invalid authorization header format"}), 401
        
        if not token:
            return jsonify({"error": "Missing authorization token"}), 401
        
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            request.current_user = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "operational",
        "service": "HealthCare Pro API",
        "version": "2.1.0",
        "fhir_version": "R4",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

@app.route('/auth/token', methods=['POST'])
def get_token():
    """Endpoint pour obtenir un token JWT (simulation OAuth)"""
    data = request.get_json()
    
    # Simulation d'authentification simple
    if data and data.get('client_id') == 'healthcare_pro_client' and data.get('client_secret') == 'healthcare_secret_2024':
        token = generate_jwt_token()
        return jsonify({
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": 86400,
            "scope": "read:patients write:patients read:appointments write:appointments"
        })
    
    return jsonify({"error": "Invalid credentials"}), 401

# PATIENTS ENDPOINTS
@app.route('/fhir/Patient', methods=['GET'])
@require_jwt_auth
def get_patients():
    """Récupérer tous les patients (format FHIR Bundle)"""
    bundle = {
        "resourceType": "Bundle",
        "id": str(uuid.uuid4()),
        "type": "searchset",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total": len(patients_db),
        "entry": [
            {
                "resource": patient,
                "search": {"mode": "match"}
            } for patient in patients_db
        ]
    }
    return jsonify(bundle)

@app.route('/fhir/Patient/<patient_id>', methods=['GET'])
@require_jwt_auth
def get_patient(patient_id):
    """Récupérer un patient spécifique"""
    patient = next((p for p in patients_db if p["id"] == patient_id), None)
    if not patient:
        return jsonify({
            "resourceType": "OperationOutcome",
            "issue": [{
                "severity": "error",
                "code": "not-found",
                "diagnostics": f"Patient with id '{patient_id}' not found"
            }]
        }), 404
    return jsonify(patient)

# APPOINTMENTS ENDPOINTS  
@app.route('/fhir/Appointment', methods=['GET'])
@require_jwt_auth
def get_appointments():
    """Récupérer tous les rendez-vous (format FHIR Bundle)"""
    # Filtrage optionnel par date
    date_filter = request.args.get('date')
    filtered_appointments = appointments_db
    
    if date_filter:
        # Filtrer par date de début
        filtered_appointments = [
            apt for apt in appointments_db 
            if apt["start"].startswith(date_filter)
        ]
    
    bundle = {
        "resourceType": "Bundle",
        "id": str(uuid.uuid4()),
        "type": "searchset", 
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total": len(filtered_appointments),
        "entry": [
            {
                "resource": appointment,
                "search": {"mode": "match"}
            } for appointment in filtered_appointments
        ]
    }
    return jsonify(bundle)

@app.route('/fhir/Appointment/<appointment_id>', methods=['GET'])
@require_jwt_auth
def get_appointment(appointment_id):
    """Récupérer un rendez-vous spécifique"""
    appointment = next((a for a in appointments_db if a["id"] == appointment_id), None)
    if not appointment:
        return jsonify({
            "resourceType": "OperationOutcome", 
            "issue": [{
                "severity": "error",
                "code": "not-found",
                "diagnostics": f"Appointment with id '{appointment_id}' not found"
            }]
        }), 404
    return jsonify(appointment)

# ENDPOINT HL7 SIMULÉ
@app.route('/hl7/ADT', methods=['POST'])
@require_jwt_auth
def process_hl7_adt():
    """
    Endpoint HL7 simulé pour les messages ADT (Admit, Discharge, Transfer)
    Accepte du pseudo-HL7 et retourne une confirmation
    """
    content_type = request.headers.get('Content-Type', '')
    
    if 'application/hl7-v2' not in content_type and 'text/plain' not in content_type:
        return jsonify({
            "error": "Invalid content type. Expected application/hl7-v2 or text/plain"
        }), 400
    
    hl7_message = request.data.decode('utf-8')
    
    # Simulation de parsing HL7
    lines = hl7_message.split('\n')
    msh_segment = next((line for line in lines if line.startswith('MSH')), None)
    
    if not msh_segment:
        return jsonify({
            "error": "Invalid HL7 message: Missing MSH segment"
        }), 400
    
    # Extraire quelques informations basiques
    segments = msh_segment.split('|')
    message_control_id = segments[9] if len(segments) > 9 else str(uuid.uuid4())
    
    # Simuler le processing
    response_hl7 = f"""MSH|^~\\&|HEALTHCARE_PRO|HCP_SYSTEM|SENDING_APP|SENDING_FACILITY|{datetime.utcnow().strftime('%Y%m%d%H%M%S')}||ACK|{message_control_id}|P|2.4
MSA|AA|{message_control_id}|Message accepted and processed successfully"""
    
    return response_hl7, 200, {'Content-Type': 'application/hl7-v2'}

@app.route('/hl7/sample', methods=['GET'])
def get_hl7_sample():
    """Retourner un exemple de message HL7 ADT"""
    sample_hl7 = """MSH|^~\\&|SENDING_APP|SENDING_FACILITY|HEALTHCARE_PRO|HCP_SYSTEM|20240322143000||ADT^A01|12345|P|2.4
EVN|A01|20240322143000
PID|1||HCP001^^^HCP^MR||Dubois^Pierre^Michel||19781108|M||||||^PRN^PH^^^33^145678901
PV1|1|I|ICU^101^1|||^Garcia^Elena^Dr|||||||||||12345|||||||||||||||||||||20240322100000"""
    
    return sample_hl7, 200, {'Content-Type': 'application/hl7-v2'}

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5002))
    print("🏥 HealthCare Pro API starting...")
    print("🔐 JWT Authentication enabled")
    print("📋 Test credentials:")
    print("   client_id: healthcare_pro_client")
    print("   client_secret: healthcare_secret_2024")
    print("📚 Test data loaded:")
    print(f"   - {len(patients_db)} patients (FHIR format)")
    print(f"   - {len(appointments_db)} appointments (FHIR format)")
    print("🔗 HL7 endpoint available at /hl7/ADT")
    app.run(debug=False, port=port, host='0.0.0.0')
