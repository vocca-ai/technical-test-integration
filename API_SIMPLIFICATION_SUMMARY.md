# Résumé des Simplifications des APIs

## Objectif
Rendre le test technique plus intéressant et complexe en créant des incohérences réalistes entre les deux APIs que le candidat devra gérer lors de l'intégration.

---

## 🔴 API 1 - MedScheduler

### ✅ Changements apportés

#### 1. **Suppression de `/auth/signature-helper`**
- ❌ **Supprimé** - Pas réaliste dans une vraie API de production
- Le candidat devra implémenter la logique HMAC lui-même

#### 2. **Schéma Patient modifié**
```json
{
  "id": "pat_001",
  "first_name": "Jean",           // Prénom séparé
  "last_name": "Dupont",           // Nom séparé
  "birthdate": "1985-03-15",       // Format: YYYY-MM-DD
  "phone_number": "+33123456789",  // Champ: phone_number
  "email": "jean.dupont@email.com",
  "created_at": "2024/01/15 10:30:00"
}
```
**Différences clés:**
- `first_name` + `last_name` séparés
- `birthdate` en format ISO (YYYY-MM-DD)
- `phone_number` au lieu de `phone`
- Pas de champ `address` structuré

#### 3. **Schéma Appointment modifié**
```json
{
  "id": "apt_001",
  "patient_id": "pat_001",
  "doctor_name": "Dr. Leblanc",
  "appointment_date": "2024-03-20",  // Format: YYYY-MM-DD
  "appointment_time": "14:30",       // Format: HH:MM (24h)
  "duration": 30,                    // Champ: duration (pas duration_minutes)
  "reason": "Consultation de routine",
  "created_at": "2024/01/15 11:00:00"
}
```
**Différences clés:**
- Format de date ISO simple
- Format d'heure 24h
- Champ `duration` au lieu de `duration_minutes`
- Champ `reason` au lieu de `notes`/`description`

#### 4. **Nouveau endpoint `/availabilities`**
```json
{
  "availabilities": [
    {
      "id": "avail_001",
      "doctor_name": "Dr. Leblanc",
      "date": "2024-03-20",
      "slots": ["09:00", "09:30", "10:00", "14:00", "14:30"]  // Array simple
    }
  ],
  "total": 1
}
```
**Format:** Liste simple de créneaux horaires

---

## 🔵 API 2 - HealthCare Pro

### ✅ Changements apportés

#### 1. **Suppression de `/api/patients/<patient_id>`**
- ❌ **Supprimé** - GET par ID n'existe plus
- Le candidat devra utiliser `/api/patients` et filtrer côté client
- Rend l'intégration plus complexe

#### 2. **Suppression de `PUT /api/patients/<patient_id>`**
- ❌ **Supprimé** - Pas de mise à jour de patients
- Simplifie l'API mais crée une asymétrie avec API1

#### 3. **Schéma Patient modifié**
```json
{
  "id": "hcp-patient-001",
  "patient_number": "HCP001",
  "full_name": "Pierre Michel Dubois",  // Nom complet en 1 seul champ !
  "email": "pierre.dubois@email.com",
  "contact_phone": "+33145678901",      // Champ: contact_phone
  "date_of_birth": "08/11/1978",        // Format: DD/MM/YYYY
  "gender": "M",                        // M/F/O (pas male/female)
  "street_address": "789 Boulevard de l'Hôpital",
  "city": "Marseille",
  "postal_code": "13001",
  "registered_date": "Mon, 15 Jan 2024 10:30:00 GMT"
}
```
**Différences clés:**
- `full_name` en UN SEUL champ (vs first_name/last_name)
- `date_of_birth` en format européen DD/MM/YYYY
- `contact_phone` au lieu de `phone_number`
- `gender` en code court (M/F/O)
- Adresse éclatée en plusieurs champs

#### 4. **Schéma Appointment modifié**
```json
{
  "appointment_id": "hcp-appointment-001",  // Champ: appointment_id (pas id)
  "patient_id": "hcp-patient-001",
  "practitioner": "Dr. Elena Garcia",       // Champ: practitioner (pas doctor_name)
  "datetime": "2024-03-22T10:00:00",       // Format: ISO 8601 complet
  "length_minutes": 30,                     // Champ: length_minutes
  "type": "checkup",
  "notes": "Consultation de suivi",
  "created": "Mon, 15 Jan 2024 11:30:00 GMT"
}
```
**Différences clés:**
- `appointment_id` au lieu de `id`
- `practitioner` au lieu de `doctor_name`
- `datetime` en ISO 8601 complet (date + heure fusionnées)
- `length_minutes` au lieu de `duration`
- `created` au lieu de `created_at`

#### 5. **Nouveau endpoint `/api/availabilities`**
```json
{
  "success": true,
  "data": [
    {
      "availability_id": "av_001",
      "practitioner": "Dr. Elena Garcia",
      "day": "2024-03-22",
      "time_slots": [
        {"time": "10:00:00", "available": true},   // Objets complexes
        {"time": "10:30:00", "available": false},
        {"time": "11:00:00", "available": true}
      ]
    }
  ],
  "total": 1,
  "timestamp": "Mon, 15 Jan 2024 11:30:00 GMT"
}
```
**Format:** Objets avec statut de disponibilité

---

## 🎯 Défis pour le candidat

### 1. **Schémas de données incohérents**
- **Noms**: `full_name` vs `first_name`/`last_name`
- **Dates de naissance**: `DD/MM/YYYY` vs `YYYY-MM-DD`
- **Téléphone**: `contact_phone` vs `phone_number`
- **Durée**: `length_minutes` vs `duration`
- **Médecin**: `practitioner` vs `doctor_name`

### 2. **Endpoints manquants**
- API2 n'a plus `/api/patients/<id>` → filtrage client nécessaire
- API1 a toujours `/patients/<id>` → approches différentes

### 3. **Formats de dates/heures différents**
- API1: date et heure séparées (`2024-03-20` + `14:30`)
- API2: datetime fusionné (`2024-03-22T10:00:00`)

### 4. **Authentification différente**
- API1: HMAC-SHA256 avec headers personnalisés (sans helper!)
- API2: OAuth 2.0 avec JWT + refresh tokens

### 5. **Disponibilités**
- API1: Liste simple de slots
- API2: Objets avec statut `available: true/false`
- Champs de filtrage différents: `date`/`doctor_name` vs `day`/`practitioner`

### 6. **Structure de réponse**
- API1: Réponse directe `{"appointments": [...], "total": 2}`
- API2: Enveloppe `{"success": true, "data": [...], "total": 2}`

---

## 📝 Points d'attention

Le candidat devra:
1. ✅ Parser et normaliser les noms (split/join `full_name`)
2. ✅ Convertir les formats de dates entre DD/MM/YYYY et YYYY-MM-DD
3. ✅ Mapper les noms de champs différents
4. ✅ Gérer l'absence de GET par ID sur API2
5. ✅ Implémenter l'authentification HMAC sans helper
6. ✅ Fusionner/séparer date et heure selon l'API
7. ✅ Normaliser les formats de disponibilités
8. ✅ Gérer les réponses enveloppées vs directes

---

## 🚀 Résultat

Un test technique réaliste qui simule des problèmes réels d'intégration entre systèmes hétérogènes, sans être artificiellement complexe. Les incohérences sont subtiles mais significatives.

