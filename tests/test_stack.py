import requests
import subprocess
import json

BASE_URL = "http://localhost:80"

def test_1_proxy_routing_api():
    """Vérifie que le Proxy redirige bien vers l'API"""
    print("Testing Proxy -> API Routing...")
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert "GUESS WHO" in response.text
    print("✅ Proxy routing OK")

def test_2_api_healthcheck():
    """Vérifie que le healthcheck est accessible via le proxy"""
    print("Testing API Healthcheck...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✅ Healthcheck OK")

def test_3_security_non_root():
    """Vérifie que l'utilisateur n'est pas root (Test de structure)"""
    print("Testing Security (Non-root user)...")
    # directement dans le conteneur actif
    result = subprocess.run(
    ["docker", "exec", "pixel-api", "whoami"],
    capture_output=True, text=True
    )
    user = result.stdout.strip()
    assert user != "root"
    assert user == "appuser"
    print(f"✅ Security OK (User is: {user})")

if __name__ == "__main__":
    try:
        test_1_proxy_routing_api()
        test_2_api_healthcheck()
        test_3_security_non_root()
        print("\n========= TOUS LES TESTS SONT PASSÉS AVEC SUCCÈS !=========")
    except AssertionError as e:
        print(f"\n❌ ÉCHEC DU TEST : {e}")
    except Exception as e:
        print(f"\n❌ ERREUR LORS DES TESTS : {e}")