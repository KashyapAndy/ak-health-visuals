"use client";

import type { VaccineRecord } from "@/lib/api";

const C = {
  card: "#FFFFFF", surface: "#F0EBE0",
  border: "rgba(77,124,15,0.11)",
  olive: "#4D7C0F", text: "#1C1917", muted: "#78716C", ghost: "#A8A099",
};
const SANS = "'Satoshi', system-ui, sans-serif";
const MONO = "var(--font-dm-mono, 'DM Mono', monospace)";

interface Props { data: VaccineRecord[] }

export function VaccinesPanel({ data }: Props) {
  if (!data.length) {
    return (
      <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 13, padding: "48px 24px", textAlign: "center" }}>
        <p style={{ fontFamily: MONO, color: C.muted, fontSize: 13 }}>No vaccination records on file.</p>
      </div>
    );
  }

  const groups = new Map<string, VaccineRecord[]>();
  for (const v of data) {
    if (!groups.has(v.vaccine_name)) groups.set(v.vaccine_name, []);
    groups.get(v.vaccine_name)!.push(v);
  }
  // data arrives sorted DESC by date_given from the API; each group inherits that order.
  const sortedGroups = Array.from(groups.entries()).sort(
    (a, b) => b[1][0].date_given.localeCompare(a[1][0].date_given)
  );

  const mostRecent = data[0]?.date_given;

  return (
    <div className="fade-up" style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      {/* Stat bar */}
      <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 13, display: "grid", gridTemplateColumns: "repeat(3, 1fr)" }}>
        {[
          { label: "Vaccines Recorded", value: String(data.length), sub: "individual doses" },
          { label: "Vaccine Types", value: String(groups.size), sub: "distinct vaccines" },
          { label: "Most Recent", value: mostRecent ?? "—", sub: "last dose given" },
        ].map((s, i) => (
          <div key={s.label} style={{ padding: "1.5rem 1.75rem", textAlign: "center", borderRight: i < 2 ? `1px solid ${C.border}` : "none" }}>
            <div style={{ fontFamily: MONO, fontSize: "0.68rem", letterSpacing: "0.1em", textTransform: "uppercase", color: C.muted, marginBottom: 6 }}>
              {s.label}
            </div>
            <div style={{ fontFamily: MONO, fontSize: 24, fontWeight: 500, color: C.olive, lineHeight: 1, marginBottom: 4 }}>
              {s.value}
            </div>
            <div style={{ fontFamily: MONO, fontSize: "0.68rem", color: C.ghost }}>{s.sub}</div>
          </div>
        ))}
      </div>

      {/* Grouped timeline, one card per vaccine name */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
        {sortedGroups.map(([name, records]) => (
          <div key={name} style={{
            background: C.card, border: `1px solid ${C.border}`, borderRadius: 13,
            padding: "18px 22px", boxShadow: "0 1px 6px rgba(77,124,15,0.05)",
          }}>
            <div style={{ display: "flex", alignItems: "baseline", justifyContent: "space-between", marginBottom: 12 }}>
              <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 15, color: C.text, letterSpacing: "-0.01em" }}>
                {name}
              </div>
              <div style={{ fontFamily: MONO, fontSize: "0.65rem", color: C.ghost }}>
                {records.length} dose{records.length !== 1 ? "s" : ""}
              </div>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {records.map((r, i) => (
                <div key={`${r.date_given}-${i}`} style={{ display: "flex", alignItems: "baseline", gap: 10 }}>
                  <span style={{ width: 6, height: 6, borderRadius: "50%", background: C.olive, flexShrink: 0 }} />
                  <span style={{ fontFamily: MONO, fontSize: 12, color: C.text, minWidth: 82 }}>{r.date_given}</span>
                  {r.provider && (
                    <span style={{ fontFamily: SANS, fontSize: 12.5, color: C.muted }}>{r.provider}</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
