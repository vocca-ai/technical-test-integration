# Comparaison des Méthodes d'Authentification

## Vue d'ensemble

Les deux APIs utilisent des méthodes d'authentification **très différentes** pour démontrer la diversité des approches de sécurité :

## API 1 - MedScheduler : HMAC Signature

**Méthode ultra-sécurisée avec signatures cryptographiques**

### Caractéristiques

- **Type** : Authentification par signature HMAC-SHA256
- **Sécurité** : Très haute (protection contre replay attacks)
- **Complexité** : Élevée (nécessite calcul de signature)
- **Use case** : Intégrations B2B, APIs critiques

### Comment ça fonctionne

1. Le client calcule une signature HMAC-SHA256 de la requête
2. La signature inclut : méthode HTTP + path + timestamp + body
3. Le serveur vérifie la signature et le timestamp (validité 5 minutes)
4. Protection automatique contre les attaques de replay

### Headers requis

```http
X-Client-ID: medscheduler_client
X-Timestamp: 1679485200
X-Signature: base64_encoded_hmac_signature
```

### Exemple d'utilisation

```bash
# 1. Générer une signature (helper endpoint)
curl -X POST http://localhost:5001/auth/signature-helper \
  -H "Content-Type: application/json" \
  -d '{
    "method": "GET",
    "path": "/patients"
  }'

# 2. Utiliser la signature pour accéder à l'API
curl -X GET http://localhost:5001/patients \
  -H "X-Client-ID: medscheduler_client" \
  -H "X-Timestamp: 1679485200" \
  -H "X-Signature: generated_signature"
```

### Avantages

- ✅ Sécurité maximale
- ✅ Protection contre replay attacks
- ✅ Pas de tokens à stocker côté serveur
- ✅ Révocation instantanée (changement de secret)

### Inconvénients

- ❌ Complexité d'implémentation côté client
- ❌ Nécessite synchronisation d'horloge
- ❌ Calcul de signature à chaque requête

---

## API 2 - HealthCare Pro : OAuth 2.0 + JWT

**Méthode moderne avec tokens et scopes granulaires**

### Caractéristiques

- **Type** : OAuth 2.0 avec JWT + Refresh Tokens
- **Sécurité** : Haute (scopes, expiration courte)
- **Complexité** : Modérée (standard OAuth)
- **Use case** : Applications web/mobile, intégrations modernes

### Comment ça fonctionne

1. Le client s'authentifie et reçoit access + refresh tokens
2. L'access token (15 min) est utilisé pour les requêtes
3. Le refresh token (7 jours) permet de renouveler l'access token
4. Chaque token a des scopes spécifiques

### Grant types supportés

- `client_credentials` : Authentification initiale
- `refresh_token` : Renouvellement de tokens

### Scopes disponibles

- `read:patients` : Lecture des patients
- `write:patients` : Création/modification des patients
- `read:appointments` : Lecture des rendez-vous
- `write:appointments` : Gestion des rendez-vous
- `hl7:process` : Traitement des messages HL7

### Exemple d'utilisation

```bash
# 1. Obtenir des tokens
curl -X POST http://localhost:5002/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "grant_type": "client_credentials",
    "client_id": "healthcare_pro_client",
    "client_secret": "healthcare_secret_2024",
    "scope": "read:patients write:appointments"
  }'

# Réponse :
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "Bearer",
  "expires_in": 900,
  "scope": "read:patients write:appointments"
}

# 2. Utiliser l'access token
curl -X GET http://localhost:5002/api/patients \
  -H "Authorization: Bearer ACCESS_TOKEN"

# 3. Renouveler le token quand il expire
curl -X POST http://localhost:5002/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "grant_type": "refresh_token",
    "refresh_token": "REFRESH_TOKEN"
  }'
```

### Avantages

- ✅ Standard de l'industrie (OAuth 2.0)
- ✅ Scopes granulaires
- ✅ Refresh tokens pour UX fluide
- ✅ Facilité d'implémentation côté client

### Inconvénients

- ❌ Gestion des tokens côté serveur
- ❌ Possible vol de tokens
- ❌ Complexité de révocation

---

## Comparaison Directe

| Aspect                | API 1 (HMAC)    | API 2 (OAuth JWT)         |
| --------------------- | --------------- | ------------------------- |
| **Sécurité**          | 🟢 Très haute   | 🟡 Haute                  |
| **Complexité client** | 🔴 Élevée       | 🟢 Modérée                |
| **Standardisation**   | 🟡 Propriétaire | 🟢 Standard OAuth         |
| **Performance**       | 🟢 Calcul local | 🟡 Vérification token     |
| **Révocation**        | 🟢 Instantanée  | 🟡 Délai d'expiration     |
| **Scalabilité**       | 🟢 Stateless    | 🟡 Gestion refresh tokens |
| **Use case**          | B2B critique    | Applications modernes     |

## Recommandations d'usage

### Utilisez l'API 1 (HMAC) pour :

- Intégrations entre systèmes critiques
- APIs nécessitant une sécurité maximale
- Communications B2B avec partenaires techniques
- Systèmes où la révocation doit être instantanée

### Utilisez l'API 2 (OAuth JWT) pour :

- Applications web et mobiles
- Intégrations avec des systèmes tiers modernes
- APIs publiques avec différents niveaux d'accès
- Systèmes nécessitant des permissions granulaires

## Exemples de clients

### Client Python pour API 1 (HMAC)

```python
import hmac
import hashlib
import base64
import time
import requests

def create_signature(method, path, timestamp, body=""):
    secret = "medscheduler_secret_key_2024_very_secure"
    string_to_sign = f"{method}\n{path}\n{timestamp}\n{body}"
    signature = hmac.new(
        secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode('utf-8')

def api1_request(method, path, body=None):
    timestamp = str(int(time.time()))
    signature = create_signature(method, path, timestamp, body or "")

    headers = {
        'X-Client-ID': 'medscheduler_client',
        'X-Timestamp': timestamp,
        'X-Signature': signature
    }

    return requests.request(method, f"http://localhost:5001{path}",
                          headers=headers, data=body)
```

### Client Python pour API 2 (OAuth)

```python
import requests
import json

class API2Client:
    def __init__(self):
        self.access_token = None
        self.refresh_token = None

    def authenticate(self):
        response = requests.post('http://localhost:5002/auth/token', json={
            'grant_type': 'client_credentials',
            'client_id': 'healthcare_pro_client',
            'client_secret': 'healthcare_secret_2024'
        })

        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']

    def api_request(self, method, path, **kwargs):
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f'Bearer {self.access_token}'
        kwargs['headers'] = headers

        response = requests.request(method, f"http://localhost:5002{path}", **kwargs)

        # Auto-refresh si token expiré
        if response.status_code == 401 and 'expired' in response.text:
            self.refresh_access_token()
            headers['Authorization'] = f'Bearer {self.access_token}'
            response = requests.request(method, f"http://localhost:5002{path}", **kwargs)

        return response

    def refresh_access_token(self):
        response = requests.post('http://localhost:5002/auth/token', json={
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        })

        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']
```

Cette approche à double authentification permet de démontrer la richesse et la diversité des mécanismes de sécurité disponibles pour les APIs modernes.
