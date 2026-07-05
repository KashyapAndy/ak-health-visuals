"use client";

import type { Person } from "@/lib/api";

const SANS = "'Satoshi', system-ui, sans-serif";

const PERSON_LABEL: Record<Person, string> = { AK: "Anirudh", RK: "Rashmi" };

export function PersonSwitcher({ person, onChange }: { person: Person; onChange: (p: Person) => void }) {
  return (
    <div style={{ display: "flex", gap: 2, background: "#F0EBE0", border: "1px solid rgba(77,124,15,0.11)", borderRadius: 99, padding: 3 }}>
      {(["AK", "RK"] as Person[]).map((p) => (
        <button
          key={p}
          onClick={() => onChange(p)}
          style={{
            padding: "5px 16px",
            borderRadius: 99,
            border: "none",
            cursor: "pointer",
            fontFamily: SANS,
            fontSize: 13,
            fontWeight: person === p ? 600 : 400,
            background: person === p ? "#4D7C0F" : "transparent",
            color: person === p ? "#FAF7F2" : "#78716C",
            transition: "all 0.2s",
          }}
        >
          {PERSON_LABEL[p]}
        </button>
      ))}
    </div>
  );
}
