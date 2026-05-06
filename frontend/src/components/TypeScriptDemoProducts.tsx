interface Produkt {
  id: number;
  name: string;
  preis: number;
  kategorie: string;
  istVerfuegbar: boolean;
}

const apfelGala: Produkt = {
  id: 1,
  name: "Apfel Gala",
  preis: 1.99,
  kategorie: "Obst",
  istVerfuegbar: true,
};

const vollmilch1L: Produkt = {
  id: 2,
  name: "Vollmilch 1L",
  preis: 0.99,
  kategorie: "Milchprodukte",
  istVerfuegbar: true,
};

const bioKarotten500g: Produkt = {
  id: 3,
  name: "Bio-Karotten 500g",
  preis: 2.49,
  kategorie: "Gemüse",
  istVerfuegbar: false,
};

// Intentionally wrong id type for the course screenshot (VS Code red underline)
const fehlerhaftesProdukt: Produkt = {
  // @ts-expect-error - used for teaching the TypeScript error
  id: "abc",
  name: "Fehlerhaftes Produkt",
  preis: 1.49,
  kategorie: "Backwaren",
  istVerfuegbar: false,
};

const produkte: Produkt[] = [
  apfelGala,
  vollmilch1L,
  bioKarotten500g,
  fehlerhaftesProdukt,
];

const CheckMark = () => (
  <span style={{ color: "#2e7d32", fontWeight: 700 }}>✓</span>
);

const XMark = () => (
  <span style={{ color: "#d32f2f", fontWeight: 700 }}>✗</span>
);

export default function TypeScriptDemoProducts() {
  return (
    <div
      style={{
        maxWidth: 980,
        margin: "2rem auto",
        fontFamily: "Arial",
      }}
    >
      <h1 style={{ marginBottom: 8 }}>Produktverwaltung</h1>
      <p style={{ marginTop: 0, color: "#666" }}>
        Anzahl Produkte: {produkte.length}
      </p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: 16,
        }}
      >
        {produkte.map((p) => (
          <div
            key={p.id}
            style={{
              border: "1px solid #e0e0e0",
              borderRadius: 8,
              padding: 14,
              boxShadow: "0 1px 2px rgba(0,0,0,0.04)",
              background: "#fff",
            }}
          >
            <h3 style={{ margin: "0 0 6px" }}>{p.name}</h3>
            <div style={{ color: "#666", marginBottom: 2 }}>
              Kategorie: {p.kategorie}
            </div>
            <div style={{ marginBottom: 8 }}>Preis: {p.preis.toFixed(2)}€</div>

            {p.istVerfuegbar ? (
              <div>
                <CheckMark /> Verfügbar
              </div>
            ) : (
              <div>
                <XMark /> Nicht verfügbar
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

