import argparse
import sys

import requests


def main() -> int:
    parser = argparse.ArgumentParser(
        description="C2: Registrierung -> Token -> Produkte abrufen"
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="Base URL vom FastAPI Backend (Default: http://127.0.0.1:8000)",
    )
    parser.add_argument(
        "--username",
        default="neuer_testuser",
        help="Username für Registrierung/Login",
    )
    parser.add_argument(
        "--password",
        default="geheimespasswort",
        help="Passwort für Registrierung/Login",
    )
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")

    # 1. Registrieren (Neuen User anlegen)
    print("--- Schritt 1: Registrierung ---")
    register_response = requests.post(
        f"{base_url}/users/",
        json={"username": args.username, "password": args.password},
        timeout=10,
    )
    print("Registrierung Response:", register_response.json())

    # 2. Login, um den Token zu bekommen (OAuth2: form-data!)
    print("\n--- Schritt 2: Login & Token Request ---")
    login_data = {"username": args.username, "password": args.password}
    token_response = requests.post(
        f"{base_url}/token", data=login_data, timeout=10
    )
    token_json = token_response.json()
    print("Token Response:", token_json)

    token = token_json.get("access_token")
    if not token:
        print("Kein access_token erhalten, Script wird beendet.")
        return 1

    # 3. Request mit Token-Authentifizierung
    print("\n--- Schritt 3: Produkte abrufen ---")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # Produkte abrufen
    get_response = requests.get(
        f"{base_url}/products", headers=headers, timeout=10
    )
    print("Produkte Liste:", get_response.json())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

