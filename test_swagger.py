#!/usr/bin/env python3
"""
Script de test pour vérifier que la documentation Swagger fonctionne correctement
"""

import requests
import json
import time
import subprocess
import sys
from threading import Thread
import os

def start_docs_app():
    """Démarrer l'application de documentation en arrière-plan"""
    os.chdir('docs_app')
    subprocess.run([sys.executable, 'app.py'], capture_output=True)

def test_endpoints():
    """Tester les endpoints de documentation"""
    base_url = "http://localhost:3000"
    
    # Attendre que l'application démarre
    print("⏳ Attente du démarrage de l'application...")
    time.sleep(3)
    
    endpoints_to_test = [
        "/",
        "/health", 
        "/api/medscheduler/spec",
        "/api/healthcare-pro/spec",
        "/medscheduler",
        "/healthcare-pro"
    ]
    
    results = {}
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            results[endpoint] = {
                "status": response.status_code,
                "success": response.status_code == 200
            }
            print(f"✅ {endpoint}: {response.status_code}")
        except Exception as e:
            results[endpoint] = {
                "status": "ERROR",
                "success": False,
                "error": str(e)
            }
            print(f"❌ {endpoint}: {str(e)}")
    
    return results

def validate_swagger_specs():
    """Valider les spécifications Swagger"""
    print("\n🔍 Validation des spécifications Swagger...")
    
    try:
        # Test API 1 spec
        response = requests.get("http://localhost:3000/api/medscheduler/spec", timeout=5)
        if response.status_code == 200:
            spec1 = response.json()
            print(f"✅ API 1 - {spec1['info']['title']} v{spec1['info']['version']}")
            print(f"   Endpoints: {len(spec1.get('paths', {}))}")
            print(f"   Authentification: {list(spec1.get('components', {}).get('securitySchemes', {}).keys())}")
        else:
            print(f"❌ API 1 spec: HTTP {response.status_code}")
            
        # Test API 2 spec  
        response = requests.get("http://localhost:3000/api/healthcare-pro/spec", timeout=5)
        if response.status_code == 200:
            spec2 = response.json()
            print(f"✅ API 2 - {spec2['info']['title']} v{spec2['info']['version']}")
            print(f"   Endpoints: {len(spec2.get('paths', {}))}")
            print(f"   Authentification: {list(spec2.get('components', {}).get('securitySchemes', {}).keys())}")
        else:
            print(f"❌ API 2 spec: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erreur validation: {e}")

if __name__ == "__main__":
    print("🧪 Test de la documentation Swagger")
    print("=" * 50)
    
    # Démarrer l'app de documentation en arrière-plan
    print("🚀 Démarrage de l'application de documentation...")
    app_thread = Thread(target=start_docs_app, daemon=True)
    app_thread.start()
    
    # Tester les endpoints
    results = test_endpoints()
    
    # Valider les spécifications
    validate_swagger_specs()
    
    # Résumé
    print("\n📊 Résumé des tests:")
    successful = sum(1 for r in results.values() if r["success"])
    total = len(results)
    print(f"   Réussis: {successful}/{total}")
    
    if successful == total:
        print("🎉 Tous les tests sont passés avec succès!")
        sys.exit(0)
    else:
        print("⚠️  Certains tests ont échoué.")
        sys.exit(1)
