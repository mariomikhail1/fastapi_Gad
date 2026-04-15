import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../api";
import { useAuth } from "../AuthContext";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const makeForm = () => {
      const formData = new URLSearchParams();
      formData.append("username", username.trim());
      formData.append("password", password);
      return formData;
    };

    try {
      const response = await api.post("/token", makeForm(), {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      login(response.data.access_token);
      navigate("/products", { replace: true });
    } catch (err: any) {
      // If user does not exist yet, create and retry once.
      if (err?.response?.status === 401) {
        try {
          await api.post("/users/", {
            username: username.trim(),
            password,
          });

          const retry = await api.post("/token", makeForm(), {
            headers: {
              "Content-Type": "application/x-www-form-urlencoded",
            },
          });
          login(retry.data.access_token);
          navigate("/products", { replace: true });
          return;
        } catch {
          // fall through to standard error below
        }
      }

      setError(
        "Login fehlgeschlagen. Prüfe Username/Passwort oder ob das Backend läuft."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 420, margin: "2rem auto", fontFamily: "Arial" }}>
      <h1>Login</h1>
      <form onSubmit={onSubmit}>
        <div style={{ marginBottom: 12 }}>
          <label>Username</label>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            style={{ display: "block", width: "100%", padding: 8 }}
            required
          />
        </div>

        <div style={{ marginBottom: 12 }}>
          <label>Passwort</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{ display: "block", width: "100%", padding: 8 }}
            required
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Lädt..." : "Einloggen"}
        </button>
      </form>

      {error && <p style={{ color: "crimson" }}>{error}</p>}
    </div>
  );
}

