## FastAPI_Gad – Product API

Dieses Projekt ist die Umsetzung der ersten FastAPI‑Aufgabe „Product API“.

### Projektstruktur

```text
fastapi_Gad/
├─ app/
│  ├─ __init__.py
│  └─ main.py
├─ requirements.txt
└─ README.md
```

### Installation

1. Python 3.10+ installieren.
2. (Empfohlen) Virtuelle Umgebung anlegen:

```bash
python -m venv .venv
.\.venv\Scripts\activate   # Windows
```

3. Abhängigkeiten installieren:

```bash
pip install -r requirements.txt
```

4. Server starten:

```bash
fastapi dev app/main.py
```

5. API‑Dokumentation im Browser öffnen:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

