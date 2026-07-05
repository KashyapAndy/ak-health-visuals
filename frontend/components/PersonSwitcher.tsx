"use client";

import type { Person } from "@/lib/api";

export function PersonSwitcher({ person, onChange }: { person: Person; onChange: (p: Person) => void }) {
  return (
    <div style={{ display: "flex", gap: 2, background: "#F0EBE3", borderRadius: 99, padding: 3 }}>
      {(["AK", "RK"] as Person[]).map((p) => (
        <button
          key={p}
          onClick={() => onChange(p)}
          style={{
            padding: "5px 16px",
            borderRadius: 99,
            border: "none",
            cursor: "pointer",
            fontFamily: "var(--font-outfit, Outfit, sans-serif)",
            fontSize: 13,
            fontWeight: person === p ? 600 : 400,
            background: person === p ? "#0D1B2A" : "transparent",
            color: person === p ? "#FAF7F2" : "#78716C",
            transition: "all 0.2s",
          }}
        >
          {p === "AK" ? "Anirudh" : "Rashmi"}
        </button>
      ))}
    </div>
  );
}
