Implementierungsstand nach Aufgabenstellung 01b + 01c
======================================================

Backend (FastAPI, SQLAlchemy, Dependency Injection, JWT, Protected Endpoints)
-----------------------------------------------------------------------------
1) SQLAlchemy + Dependency Injection
- SQLite Datenbank über `app/database.py`
- SQLAlchemy Modelle in `app/models.py`
  - `Product`
  - `User`
- Pydantic Schemas in `app/schemas.py`
  - Product: Create/Update/Read
  - User: Create/Read
  - Token-Response
- DB-Session als Dependency via `get_db()` (in `app/auth.py`)
- Tabellen-Erzeugung beim Startup in `app/main.py`

2) User-Management (Minimal)
- `POST /users/` implementiert:
  - erwartet `username`, `password`
  - Passwort wird gehasht gespeichert
- `GET /users/me` implementiert (protected)

3) Authentication mit JWT
- `POST /token` mit `OAuth2PasswordRequestForm` implementiert
- JWT-Erzeugung über `create_access_token(...)`
- Password Hashing/Verify über `passlib`
- Dependencies implementiert:
  - `get_current_user`
  - `get_current_active_user`

4) Protected Endpoints
- Geschützt (Bearer Token notwendig):
  - `POST /products/`
  - `PUT /products/{product_id}`
  - `DELETE /products/{product_id}`
- Öffentlich:
  - `GET /products/`
  - `GET /products/{product_id}`
  - `GET /health`

5) Swagger & CORS
- Swagger über `/docs` verfügbar
- Root `/` leitet auf `/docs` weiter
- CORS für React Dev-Server aktiviert:
  - `http://localhost:5173`

Backend-Test (durchgeführt)
---------------------------
Automatischer Integrationstest mit FastAPI TestClient:
- User registrieren: 201
- Token holen: 200
- Protected Endpoint ohne Token: 401
- Protected Endpoint mit Token: 201
- Public GET /products/: 200
- GET /users/me mit Token: 200


Frontend (React + TypeScript + JWT)
-----------------------------------
Frontend-Struktur in `frontend/` angelegt:
- Vite/TypeScript Grundsetup:
  - `package.json`
  - `vite.config.ts`
  - `tsconfig*.json`
  - `index.html`
- API Layer:
  - `src/api.ts` (Axios, Bearer Token Interceptor)
- Auth State:
  - `src/AuthContext.tsx` (token/login/logout, LocalStorage)
- Routing + Protected Route:
  - `src/App.tsx`
- UI Komponenten:
  - `src/components/Login.tsx`
  - `src/components/ProductList.tsx`
- Entry:
  - `src/main.tsx`

Wichtiger Hinweis zum aktuellen System:
- Node.js / npm sind auf diesem Rechner derzeit nicht installiert
  (`node` und `npm` wurden im Terminal nicht gefunden).
- Darum konnte `npm install` / `npm run dev` hier noch nicht ausgeführt werden.
- Nach Installation von Node.js genügt:
  1. `cd frontend`
  2. `npm install`
  3. `npm run dev`


Abhängigkeiten / Konfiguration
------------------------------
- `requirements.txt` für Python 3.13 kompatibel angepasst
- Zusätzliche Backend-Abhängigkeiten:
  - `python-jose[cryptography]`
  - `passlib[bcrypt]`
  - `bcrypt<4` (Kompatibilität mit passlib)
  - `python-multipart`
- `.gitignore` erweitert für Frontend-Artefakte:
  - `frontend/node_modules/`
  - `frontend/dist/`

