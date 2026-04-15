# React Frontend Setup Tutorial für FastAPI & JWT

## Einleitung

Dieses Tutorial zeigt dir Schritt für Schritt, wie du ein modernes React-Frontend (mit TypeScript) aufbaust, das mit unserem FastAPI-Backend inkl. JWT-Authentifizierung kommuniziert.

---

## 1. Node.js Setup (Betriebssysteme)

Bevor wir starten können, benötigen wir Node.js (die Laufzeitumgebung) und `npm` (Node Package Manager).

### Windows
1. Gehe auf [nodejs.org](https://nodejs.org/).
2. Lade den "LTS" (Long Term Support) Installer herunter.
3. Führe die `.msi`-Datei aus und klicke auf "Next" durch die Standard-Einstellungen.

### macOS
Entweder über den Installer auf [nodejs.org](https://nodejs.org/) oder via Homebrew (empfohlen):
```bash
brew install node
```

### Linux (Ubuntu/Debian)
```bash
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**Verifizieren der Installation:**
Öffne ein Terminal und tippe:
```bash
node -v
npm -v
```

---

## 2. TypeScript vs. JavaScript

Wir werden **TypeScript** für unser React-Projekt verwenden. 
- **JavaScript** ist dynamisch typisiert. Das bedeutet, dass Variablen jeden Datentyp (Zahl, Text, Objekt) annehmen können. Dies ist zwar flexibel, führt aber oft zu versteckten Fehlern zur Laufzeit.
- **TypeScript** erweitert JavaScript um feste Typen (Typisierung). Wenn eine Variable als `number` deklariert ist, wird der Code gar nicht erst kompiliert, wenn man dort einen Text (`string`) speichert. Das hilft ungemein, Fehler bereits im Code-Editor (wie VS Code) zu erkennen und bietet hervorragende Autovervollständigung.

---

## 3. Die wichtigsten Entwicklungsschritte

### 1. Enable CORS in FastAPI (Backend Prep)
Damit unser Frontend (das auf Port 5173 laufen wird) mit unserem Backend (auf Port 8000) reden darf, müssen wir "Cross-Origin Resource Sharing" (CORS) aktivieren. 

Füge in deiner `app/main.py` im Backend folgendes nach der Zeile `app = FastAPI(...)` hinzu:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # URL des React Dev-Servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Scaffold the React App
Wir nutzen **Vite**, ein blitzschnelles Build-Tool für moderne Web-Projekte. Öffne ein neues Terminal (im gleichen Hauptordner, in dem auch der Backend-Ordner liegt) und tippe:

```bash
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
```

### 3. Setup Axios for API Calls
Wir verwenden `axios`, um HTTP-Anfragen an unser Backend zu stellen. 
```bash
npm install axios
```

Erstelle eine Datei `src/api.ts`. Wir konfigurieren Axios so, dass es automatisch unser JWT-Token mitschickt:

```typescript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
});

// Füge das Token automatisch zu jedem Request hinzu
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

**Login Request (WICHTIG):**
Das FastAPI `/token` Endpoint erwartet Formulardaten (`application/x-www-form-urlencoded`), kein JSON! Der Login-Call sieht also so aus:

```typescript
const formData = new URLSearchParams();
formData.append('username', 'meinUser');
formData.append('password', 'meinPasswort');

const response = await api.post('/token', formData, {
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
});
```

### 4. Implement Auth State Management
Dein Frontend muss wissen, ob der Benutzer eingeloggt ist. Dafür nutzen wir die React **Context API**.

Erstelle `src/AuthContext.tsx`:

```typescript
import React, { createContext, useState, useContext } from 'react';

type AuthContextType = {
  token: string | null;
  login: (token: string) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));

  const login = (newToken: string) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext)!;
```

### 5. Setup Routing & Protected Routes
Für einfache Navigation zwischen Seiten installieren wir React Router:
```bash
npm install react-router-dom
```

In deiner `src/App.tsx` wickelst du alles ein und erstellst eine Komponente für geschützte Routen:

```typescript
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './AuthContext';
// ... import components ...

const ProtectedRoute = ({ children }: { children: JSX.Element }) => {
  const { token } = useAuth();
  if (!token) return <Navigate to="/login" replace />;
  return children;
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/products" element={
            <ProtectedRoute>
              <ProductList />
            </ProtectedRoute>
          } />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
```

### 6. Build the UI Components

**Login Formular (`src/components/Login.tsx`):**
Ein einfaches Formular, das den Axios-Call durchführt und das Token über den Context (`login(token)`) im State und LocalStorage speichert.

**Product List (`src/components/ProductList.tsx`):**
Hier holst du dir (z.B. mittels Reacts `useEffect` Hook) die Daten von der `/products` API. Da du Axios via Interceptor konfiguriert hast, wird das JWT bei jedem Call an `/products` automatisch im Authorization-Header mitgeschickt, womit deine "Protected Endpoints" in FastAPI reibungslos funktionieren.

---
Viel Erfolg bei der Implementierung!
