# HealthCare Pro API - Exemples d'utilisation

## Vue d'ensemble

L'API HealthCare Pro est une API hybride qui combine :
- **API REST classique** pour la gestion des patients et rendez-vous (JSON simple)
- **Endpoints HL7** pour les messages ADT (Admit, Discharge, Transfer)

## Authentification

Toutes les requêtes (REST et HL7) nécessitent un token JWT :

```bash
# Obtenir un token
curl -X POST http://localhost:5002/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "healthcare_pro_client",
    "client_secret": "healthcare_secret_2024"
  }'
```

## API REST - Patients

### Lister tous les patients
```bash
curl -X GET http://localhost:5002/api/patients \
  -H "Authorization: Bearer <token>"
```

Réponse :
```json
{
  "success": true,
  "data": [
    {
      "id": "hcp-patient-001",
      "patient_number": "HCP001",
      "first_name": "Pierre",
      "last_name": "Dubois",
      "email": "pierre.dubois@email.com",
      "phone": "+33145678901",
      "gender": "male",
      "birth_date": "1978-11-08",
      "address": {
        "street": "789 Boulevard de l'Hôpital",
        "city": "Marseille",
        "postal_code": "13001",
        "country": "FR"
      },
      "active": true
    }
  ],
  "total": 2
}
```

### Créer un patient
```bash
curl -X POST http://localhost:5002/api/patients \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Jean",
    "last_name": "Dupont",
    "email": "jean.dupont@email.com",
    "birth_date": "1985-03-15",
    "phone": "+33123456789",
    "gender": "male"
  }'
```

## API REST - Rendez-vous

### Lister les rendez-vous
```bash
curl -X GET http://localhost:5002/api/appointments \
  -H "Authorization: Bearer <token>"
```

### Créer un rendez-vous
```bash
curl -X POST http://localhost:5002/api/appointments \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "hcp-patient-001",
    "doctor_id": "dr-smith",
    "doctor_name": "Dr. Smith",
    "start_time": "2024-04-15T10:00:00.000Z",
    "end_time": "2024-04-15T10:30:00.000Z",
    "description": "Consultation de routine",
    "appointment_type": "routine"
  }'
```

## API HL7 - Messages ADT

### Envoyer un message ADT
```bash
curl -X POST http://localhost:5002/hl7/ADT \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/hl7-v2" \
  -d "MSH|^~\&|SENDING_APP|SENDING_FACILITY|HEALTHCARE_PRO|HCP_SYSTEM|20240322143000||ADT^A01|12345|P|2.4
EVN|A01|20240322143000
PID|1||HCP001^^^HCP^MR||Dubois^Pierre^Michel||19781108|M||||||^PRN^PH^^^33^145678901
PV1|1|I|ICU^101^1|||^Garcia^Elena^Dr|||||||||||12345|||||||||||||||||||||20240322100000"
```

### Obtenir un exemple de message HL7
```bash
curl -X GET http://localhost:5002/hl7/sample
```

## Filtrage et recherche

### Recherche de patients
```bash
curl -X GET "http://localhost:5002/api/patients?search=pierre&active=true" \
  -H "Authorization: Bearer <token>"
```

### Filtrage des rendez-vous
```bash
curl -X GET "http://localhost:5002/api/appointments?date=2024-03-22&status=booked" \
  -H "Authorization: Bearer <token>"
```

## Différences clés

### REST API
- **Format** : JSON simple et lisible
- **Usage** : Opérations CRUD standard
- **Endpoints** : `/api/patients`, `/api/appointments`
- **Réponses** : Structure `{success, data, message}`

### HL7 API
- **Format** : Messages HL7 v2.4
- **Usage** : Intégration avec systèmes hospitaliers
- **Endpoints** : `/hl7/ADT`, `/hl7/sample`
- **Réponses** : Messages HL7 (ACK/NACK)

Cette approche hybride permet d'utiliser :
- L'API REST pour les applications web/mobiles modernes
- Les endpoints HL7 pour l'intégration avec les systèmes hospitaliers existants
