#!/usr/bin/env python3
"""
HealthCare Pro API - API 2 (Hybride REST/HL7)
Authentification: JWT/OAuth
Format: API REST classique pour patients/rendez-vous + Endpoints HL7 spécialisés
- REST API: /api/patients, /api/appointments (JSON simple)
- HL7 API: /hl7/ADT, /hl7/sample (messages HL7)
"""

from flask import Flask, request, jsonify
try:
    from flask_cors import CORS
except ImportError:
    CORS = None
from datetime import datetime, timedelta
import uuid
import jwt
import json
from functools import wraps

app = Flask(__name__)
if CORS:
    CORS(app)  # Enable CORS for all routes

# Configuration JWT avec refresh tokens
JWT_SECRET = "healthcare_pro_secret_key_2024"
JWT_REFRESH_SECRET = "healthcare_pro_refresh_secret_2024"
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 10  # Token d'accès très court (10 secondes)
REFRESH_TOKEN_EXPIRE_DAYS = 7     # Refresh token plus long

# Base de données des refresh tokens (en production, utiliser Redis/DB)
active_refresh_tokens = set()

# Base de données simulée
patients_db = []
appointments_db = []

# Données de test avec format REST classique
test_patients_data = [
    {
        "id": "hcp-patient-001",
        "patient_number": "HCP001",
        "first_name": "Pierre",
        "last_name": "Dubois",
        "middle_name": "Michel",
        "email": "pierre.dubois@email.com",
        "phone": "+33145678901",
        "gender": "male",
        "birth_date": "08.11.1978",
        "address": {
            "street": "789 Boulevard de l'Hôpital",
            "city": "Marseille",
            "postal_code": "13001",
            "country": "FR"
        },
        "emergency_contact": {
            "name": "Marie Dubois",
            "phone": "+33145678902",
            "relationship": "spouse"
        },
        "active": True,
        "created_at": "Mon, 15 Jan 2024 10:30:00 GMT",
        "updated_at": "Mon, 15 Jan 2024 10:30:00 GMT"
    },
    {
        "id": "hcp-patient-002",
        "patient_number": "HCP002",
        "first_name": "Sophie",
        "last_name": "Leroy",
        "middle_name": "Anne",
        "email": "sophie.leroy@email.com",
        "phone": "+33156789012",
        "gender": "female",
        "birth_date": "14.05.1990",
        "address": {
            "street": "321 Rue des Soins",
            "city": "Toulouse",
            "postal_code": "31000",
            "country": "FR"
        },
        "emergency_contact": None,
        "active": True,
        "created_at": "Mon, 22 Jan 2024 09:15:00 GMT",
        "updated_at": "Mon, 22 Jan 2024 09:15:00 GMT"
    }
]

test_appointments_data = [
    {
        "id": "hcp-appointment-001",
        "patient_id": "hcp-patient-001",
        "patient_name": "Pierre Michel Dubois",
        "doctor_id": "dr-garcia",
        "doctor_name": "Dr. Elena Garcia",
        "appointment_type": "routine",
        "service_category": "General Practice",
        "service_type": "Consultation",
        "status": "booked",
        "priority": "normal",
        "description": "Consultation de suivi médical général",
        "start_time": "22 Mar 2024, 10:00",
        "end_time": "22 Mar 2024, 10:30",
        "duration_minutes": 30,
        "reason": "Encounter for check up",
        "notes": "",
        "created_at": "Mon, 15 Jan 2024 11:30:00 GMT",
        "updated_at": "Mon, 15 Jan 2024 11:30:00 GMT"
    },
    {
        "id": "hcp-appointment-002",
        "patient_id": "hcp-patient-002",
        "patient_name": "Sophie Anne Leroy",
        "doctor_id": "dr-bernard",
        "doctor_name": "Dr. Thomas Bernard",
        "appointment_type": "followup",
        "service_category": "Cardiology",
        "service_type": "Echocardiography",
        "status": "confirmed",
        "priority": "high",
        "description": "Échocardiographie de contrôle post-opératoire",
        "start_time": "28 Mar 2024, 14:15",
        "end_time": "28 Mar 2024, 15:00",
        "duration_minutes": 45,
        "reason": "Post-operative follow-up",
        "notes": "Post-surgical cardiac monitoring",
        "created_at": "Mon, 22 Jan 2024 14:45:00 GMT",
        "updated_at": "Mon, 22 Jan 2024 14:45:00 GMT"
    }
]

# Initialiser avec les données de test
patients_db.extend(test_patients_data)
appointments_db.extend(test_appointments_data)

def generate_tokens(user_id="healthcare_user", scopes=None):
    """Générer un access token et un refresh token"""
    if scopes is None:
        scopes = ['read:patients', 'write:patients', 'read:appointments', 'write:appointments', 'hl7:process']
    
    now = datetime.utcnow()
    
    # Access Token (courte durée)
    access_payload = {
        'user_id': user_id,
        'type': 'access',
        'exp': now + timedelta(seconds=ACCESS_TOKEN_EXPIRE_SECONDS),
        'iat': now,
        'scope': scopes
    }
    access_token = jwt.encode(access_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    # Refresh Token (longue durée)
    refresh_token_id = str(uuid.uuid4())
    refresh_payload = {
        'user_id': user_id,
        'type': 'refresh',
        'token_id': refresh_token_id,
        'exp': now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        'iat': now,
        'scope': scopes
    }
    refresh_token = jwt.encode(refresh_payload, JWT_REFRESH_SECRET, algorithm=JWT_ALGORITHM)
    
    # Stocker le refresh token comme actif
    active_refresh_tokens.add(refresh_token_id)
    
    return access_token, refresh_token

def require_jwt_auth(required_scopes=None):
    """Décorateur pour vérifier le token JWT avec scopes optionnels"""
    def decorator(f):
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
                
                # Vérifier que c'est un access token
                if payload.get('type') != 'access':
                    return jsonify({"error": "Invalid token type"}), 401
                
                # Vérifier les scopes si requis
                if required_scopes:
                    user_scopes = payload.get('scope', [])
                    missing_scopes = [scope for scope in required_scopes if scope not in user_scopes]
                    if missing_scopes:
                        return jsonify({
                            "error": "Insufficient permissions",
                            "missing_scopes": missing_scopes
                        }), 403
                
                request.current_user = payload
            except jwt.ExpiredSignatureError:
                return jsonify({
                    "error": "Access token has expired",
                    "message": "Use refresh token to get a new access token"
                }), 401
            except jwt.InvalidTokenError:
                return jsonify({"error": "Invalid access token"}), 401
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    # Support pour utilisation avec ou sans paramètres
    if callable(required_scopes):
        func = required_scopes
        required_scopes = None
        return decorator(func)
    
    return decorator

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "operational",
        "service": "HealthCare Pro API (Hybride REST/HL7)",
        "version": "2.2.0",
        "api_types": {
            "rest": "/api/* (patients, appointments)",
            "hl7": "/hl7/* (ADT messages)"
        },
        "authentication": "JWT Bearer Token",
        "timestamp": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    })

@app.route('/auth/token', methods=['POST'])
def get_token():
    """Endpoint pour obtenir des tokens JWT (OAuth 2.0 avec refresh)"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "JSON data required"}), 400
    
    grant_type = data.get('grant_type')
    
    if grant_type == 'client_credentials':
        # Authentification client
        if data.get('client_id') == 'healthcare_pro_client' and data.get('client_secret') == 'healthcare_secret_2024':
            # Scopes personnalisés selon le client
            requested_scopes = data.get('scope', '').split()
            available_scopes = ['read:patients', 'write:patients', 'read:appointments', 'write:appointments', 'hl7:process']
            granted_scopes = [scope for scope in requested_scopes if scope in available_scopes] or available_scopes
            
            access_token, refresh_token = generate_tokens(scopes=granted_scopes)
            
            return jsonify({
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_SECONDS,
                "scope": " ".join(granted_scopes),
                "refresh_expires_in": REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600
            })
        else:
            return jsonify({"error": "Invalid client credentials"}), 401
    
    elif grant_type == 'refresh_token':
        # Renouvellement de token
        refresh_token = data.get('refresh_token')
        if not refresh_token:
            return jsonify({"error": "Missing refresh_token"}), 400
        
        try:
            payload = jwt.decode(refresh_token, JWT_REFRESH_SECRET, algorithms=[JWT_ALGORITHM])
            
            # Vérifier que c'est un refresh token
            if payload.get('type') != 'refresh':
                return jsonify({"error": "Invalid token type"}), 401
            
            # Vérifier que le token est encore actif
            token_id = payload.get('token_id')
            if token_id not in active_refresh_tokens:
                return jsonify({"error": "Refresh token has been revoked"}), 401
            
            # Générer de nouveaux tokens
            user_id = payload.get('user_id')
            scopes = payload.get('scope', [])
            new_access_token, new_refresh_token = generate_tokens(user_id, scopes)
            
            # Révoquer l'ancien refresh token
            active_refresh_tokens.discard(token_id)
            
            return jsonify({
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": "Bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_SECONDS,
                "scope": " ".join(scopes),
                "refresh_expires_in": REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600
            })
            
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Refresh token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid refresh token"}), 401
    
    else:
        return jsonify({
            "error": "Unsupported grant type",
            "supported_grants": ["client_credentials", "refresh_token"]
        }), 400

@app.route('/auth/revoke', methods=['POST'])
@require_jwt_auth(['write:tokens'])
def revoke_token():
    """Révoquer un refresh token"""
    data = request.get_json()
    refresh_token = data.get('token')
    
    if not refresh_token:
        return jsonify({"error": "Missing token"}), 400
    
    try:
        payload = jwt.decode(refresh_token, JWT_REFRESH_SECRET, algorithms=[JWT_ALGORITHM])
        token_id = payload.get('token_id')
        
        if token_id in active_refresh_tokens:
            active_refresh_tokens.discard(token_id)
            return jsonify({"message": "Token revoked successfully"})
        else:
            return jsonify({"message": "Token was already revoked"})
    
    except jwt.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 400

# PATIENTS ENDPOINTS (REST API)
@app.route('/api/patients', methods=['GET'])
@require_jwt_auth(['read:patients'])
def get_patients():
    """Récupérer tous les patients (format REST classique)"""
    # Filtrage optionnel
    search = request.args.get('search', '').lower()
    active_only = request.args.get('active') == 'true'
    
    filtered_patients = patients_db
    
    if search:
        filtered_patients = [
            p for p in filtered_patients 
            if search in p.get('first_name', '').lower() 
            or search in p.get('last_name', '').lower()
            or search in p.get('patient_number', '').lower()
        ]
    
    if active_only:
        filtered_patients = [p for p in filtered_patients if p.get('active', True)]
    
    return jsonify({
        "success": True,
        "data": filtered_patients,
        "total": len(filtered_patients),
        "timestamp": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    })

@app.route('/api/patients/<patient_id>', methods=['GET'])
@require_jwt_auth(['read:patients'])
def get_patient(patient_id):
    """Récupérer un patient spécifique"""
    patient = next((p for p in patients_db if p["id"] == patient_id), None)
    if not patient:
        return jsonify({
            "success": False,
            "error": "Patient not found",
            "message": f"Patient with id '{patient_id}' not found"
        }), 404
    
    return jsonify({
        "success": True,
        "data": patient
    })

@app.route('/api/patients', methods=['POST'])
@require_jwt_auth(['write:patients'])
def create_patient():
    """Créer un nouveau patient"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            "success": False,
            "error": "Invalid request",
            "message": "JSON data required"
        }), 400
    
    # Validation des champs requis
    required_fields = ['first_name', 'last_name', 'email', 'birth_date']
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        return jsonify({
            "success": False,
            "error": "Missing required fields",
            "missing_fields": missing_fields
        }), 400
    
    # Créer le nouveau patient
    new_patient = {
        "id": f"hcp-patient-{str(uuid.uuid4())[:8]}",
        "patient_number": f"HCP{len(patients_db) + 1:03d}",
        "first_name": data.get('first_name'),
        "last_name": data.get('last_name'),
        "middle_name": data.get('middle_name', ''),
        "email": data.get('email'),
        "phone": data.get('phone', ''),
        "gender": data.get('gender', ''),
        "birth_date": data.get('birth_date'),
        "address": data.get('address', {}),
        "emergency_contact": data.get('emergency_contact'),
        "active": data.get('active', True),
        "created_at": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"),
        "updated_at": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    }
    
    patients_db.append(new_patient)
    
    return jsonify({
        "success": True,
        "data": new_patient,
        "message": "Patient created successfully"
    }), 201

@app.route('/api/patients/<patient_id>', methods=['PUT'])
@require_jwt_auth(['write:patients'])
def update_patient(patient_id):
    """Mettre à jour un patient"""
    patient = next((p for p in patients_db if p["id"] == patient_id), None)
    if not patient:
        return jsonify({
            "success": False,
            "error": "Patient not found"
        }), 404
    
    data = request.get_json()
    if not data:
        return jsonify({
            "success": False,
            "error": "Invalid request",
            "message": "JSON data required"
        }), 400
    
    # Mettre à jour les champs
    updatable_fields = [
        'first_name', 'last_name', 'middle_name', 'email', 'phone', 
        'gender', 'birth_date', 'address', 'emergency_contact', 'active'
    ]
    
    for field in updatable_fields:
        if field in data:
            patient[field] = data[field]
    
    patient['updated_at'] = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    return jsonify({
        "success": True,
        "data": patient,
        "message": "Patient updated successfully"
    })

# APPOINTMENTS ENDPOINTS (REST API)
@app.route('/api/appointments', methods=['GET'])
@require_jwt_auth(['read:appointments'])
def get_appointments():
    """Récupérer tous les rendez-vous (format REST classique)"""
    # Filtrage optionnel
    date_filter = request.args.get('date')
    status_filter = request.args.get('status')
    patient_id = request.args.get('patient_id')
    doctor_id = request.args.get('doctor_id')
    
    filtered_appointments = appointments_db
    
    if date_filter:
        filtered_appointments = [
            apt for apt in filtered_appointments 
            if apt["start_time"].startswith(date_filter)
        ]
    
    if status_filter:
        filtered_appointments = [
            apt for apt in filtered_appointments 
            if apt["status"] == status_filter
        ]
    
    if patient_id:
        filtered_appointments = [
            apt for apt in filtered_appointments 
            if apt["patient_id"] == patient_id
        ]
    
    if doctor_id:
        filtered_appointments = [
            apt for apt in filtered_appointments 
            if apt["doctor_id"] == doctor_id
        ]
    
    return jsonify({
        "success": True,
        "data": filtered_appointments,
        "total": len(filtered_appointments),
        "timestamp": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    })

@app.route('/api/appointments/<appointment_id>', methods=['GET'])
@require_jwt_auth(['read:appointments'])
def get_appointment(appointment_id):
    """Récupérer un rendez-vous spécifique"""
    appointment = next((a for a in appointments_db if a["id"] == appointment_id), None)
    if not appointment:
        return jsonify({
            "success": False,
            "error": "Appointment not found",
            "message": f"Appointment with id '{appointment_id}' not found"
        }), 404
    
    return jsonify({
        "success": True,
        "data": appointment
    })

@app.route('/api/appointments', methods=['POST'])
@require_jwt_auth(['write:appointments'])
def create_appointment():
    """Créer un nouveau rendez-vous"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            "success": False,
            "error": "Invalid request",
            "message": "JSON data required"
        }), 400
    
    # Validation des champs requis
    required_fields = ['patient_id', 'doctor_id', 'start_time', 'end_time', 'description']
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        return jsonify({
            "success": False,
            "error": "Missing required fields",
            "missing_fields": missing_fields
        }), 400
    
    # Vérifier que le patient existe
    patient = next((p for p in patients_db if p["id"] == data.get('patient_id')), None)
    if not patient:
        return jsonify({
            "success": False,
            "error": "Patient not found"
        }), 400
    
    # Créer le nouveau rendez-vous
    new_appointment = {
        "id": f"hcp-appointment-{str(uuid.uuid4())[:8]}",
        "patient_id": data.get('patient_id'),
        "patient_name": f"{patient['first_name']} {patient['last_name']}",
        "doctor_id": data.get('doctor_id'),
        "doctor_name": data.get('doctor_name', f"Dr. {data.get('doctor_id')}"),
        "appointment_type": data.get('appointment_type', 'routine'),
        "service_category": data.get('service_category', 'General Practice'),
        "service_type": data.get('service_type', 'Consultation'),
        "status": data.get('status', 'booked'),
        "priority": data.get('priority', 'normal'),
        "description": data.get('description'),
        "start_time": data.get('start_time'),
        "end_time": data.get('end_time'),
        "duration_minutes": data.get('duration_minutes', 30),
        "reason": data.get('reason', ''),
        "notes": data.get('notes', ''),
        "created_at": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"),
        "updated_at": datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    }
    
    appointments_db.append(new_appointment)
    
    return jsonify({
        "success": True,
        "data": new_appointment,
        "message": "Appointment created successfully"
    }), 201

@app.route('/api/appointments/<appointment_id>', methods=['PUT'])
@require_jwt_auth(['write:appointments'])
def update_appointment(appointment_id):
    """Mettre à jour un rendez-vous"""
    appointment = next((a for a in appointments_db if a["id"] == appointment_id), None)
    if not appointment:
        return jsonify({
            "success": False,
            "error": "Appointment not found"
        }), 404
    
    data = request.get_json()
    if not data:
        return jsonify({
            "success": False,
            "error": "Invalid request",
            "message": "JSON data required"
        }), 400
    
    # Mettre à jour les champs
    updatable_fields = [
        'doctor_id', 'doctor_name', 'appointment_type', 'service_category', 
        'service_type', 'status', 'priority', 'description', 'start_time', 
        'end_time', 'duration_minutes', 'reason', 'notes'
    ]
    
    for field in updatable_fields:
        if field in data:
            appointment[field] = data[field]
    
    appointment['updated_at'] = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    return jsonify({
        "success": True,
        "data": appointment,
        "message": "Appointment updated successfully"
    })

@app.route('/api/appointments/<appointment_id>', methods=['DELETE'])
@require_jwt_auth(['write:appointments'])
def delete_appointment(appointment_id):
    """Supprimer un rendez-vous"""
    appointment = next((a for a in appointments_db if a["id"] == appointment_id), None)
    if not appointment:
        return jsonify({
            "success": False,
            "error": "Appointment not found"
        }), 404
    
    appointments_db.remove(appointment)
    
    return jsonify({
        "success": True,
        "message": "Appointment deleted successfully"
    })

# ENDPOINT HL7 SIMULÉ
@app.route('/hl7/ADT', methods=['POST'])
@require_jwt_auth(['hl7:process'])
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
    print("🏥 HealthCare Pro API (Hybride REST/HL7) starting...")
    print("🔐 OAuth 2.0 with JWT + Refresh Tokens enabled")
    print("📋 Test credentials:")
    print("   client_id: healthcare_pro_client")
    print("   client_secret: healthcare_secret_2024")
    print("   grant_types: client_credentials, refresh_token")
    print("📚 Test data loaded:")
    print(f"   - {len(patients_db)} patients (REST format)")
    print(f"   - {len(appointments_db)} appointments (REST format)")
    print("🔑 Available scopes:")
    print("   - read:patients, write:patients")
    print("   - read:appointments, write:appointments")
    print("   - hl7:process")
    print("⏱️  Token lifetimes:")
    print(f"   - Access tokens: {ACCESS_TOKEN_EXPIRE_SECONDS} seconds")
    print(f"   - Refresh tokens: {REFRESH_TOKEN_EXPIRE_DAYS} days")
    print("🌐 REST API endpoints:")
    print("   - GET/POST /api/patients")
    print("   - GET/PUT /api/patients/<id>")
    print("   - GET/POST/PUT/DELETE /api/appointments")
    print("🔗 HL7 endpoints:")
    print("   - POST /hl7/ADT (ADT messages)")
    print("   - GET /hl7/sample (sample message)")
    app.run(debug=False, port=port, host='0.0.0.0')
