"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { BiomarkerChart } from "@/components/BiomarkerChart";
import { api, type BiomarkerHistory, type Person } from "@/lib/api";

const PERSON_NAME: Record<Person, string> = { AK: "Anirudh Kashyap", RK: "Rashmi Kashyap" };
const SANS = "'Satoshi', system-ui, sans-serif";
const MONO = "var(--font-dm-mono, 'DM Mono', monospace)";

function PrintReport() {
  const params = useSearchParams();
  const person = (params.get("person") as Person) === "RK" ? "RK" : "AK";
  const markers = (params.get("markers") ?? "").split(",").map(s => s.trim()).filter(Boolean);

  const [data, setData] = useState<Record<string, BiomarkerHistory>>({});
  const [loading, setLoading] = useState(true);
  const [failed, setFailed] = useState<string[]>([]);
  const [detail, setDetail] = useState<"detailed" | "graph">("detailed");

  useEffect(() => {
    if (markers.length === 0) { setLoading(false); return; }
    setLoading(true);
    Promise.allSettled(markers.map(name => api.biomarker(name, person)))
      .then(results => {
        const map: Record<string, BiomarkerHistory> = {};
        const errs: string[] = [];
        results.forEach((r, i) => {
          if (r.status === "fulfilled") map[markers[i]] = r.value;
          else errs.push(markers[i]);
        });
        setData(map);
        setFailed(errs);
      })
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [person, markers.join("|")]);

  const generatedOn = new Date().toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" });

  return (
    <div style={{ maxWidth: 820, margin: "0 auto", padding: "40px 32px 60px", background: "#FAF7F2", minHeight: "100vh" }}>
      <style>{`
        @media print {
          .no-print { display: none !important; }
          html, body { background: #fff !important; }
        }
        .print-section { break-inside: avoid; page-break-inside: avoid; }
        @page { margin: 0.6in; }
      `}</style>

      <div className="no-print" style={{ display: "flex", justifyContent: "flex-end", alignItems: "center", gap: 14, marginBottom: 24 }}>
        <div style={{ display: "flex", gap: 2, background: "#F0EBE0", border: "1px solid rgba(77,124,15,0.11)", borderRadius: 99, padding: 3 }}>
          {(["detailed", "graph"] as const).map(m => (
            <button
              key={m}
              onClick={() => setDetail(m)}
              style={{
                padding: "6px 16px", borderRadius: 99, border: "none", cursor: "pointer",
                fontFamily: SANS, fontSize: 13,
                fontWeight: detail === m ? 600 : 400,
                background: detail === m ? "#4D7C0F" : "transparent",
                color: detail === m ? "#FAF7F2" : "#78716C",
              }}
            >
              {m === "detailed" ? "Detailed (with summary)" : "Graph only"}
            </button>
          ))}
        </div>
        <button
          onClick={() => window.print()}
          style={{
            fontFamily: SANS, fontWeight: 600, fontSize: 14, padding: "10px 22px",
            background: "#4D7C0F", color: "#FAF7F2", border: "none", borderRadius: 8,
            cursor: "pointer", boxShadow: "0 2px 8px rgba(77,124,15,0.25)",
          }}
        >
          Print / Save as PDF
        </button>
      </div>

      <div style={{ marginBottom: 32, borderBottom: "2px solid #1C1917", paddingBottom: 16 }}>
        <h1 style={{ fontFamily: SANS, fontWeight: 800, fontSize: 26, margin: 0, color: "#1C1917", letterSpacing: "-0.02em" }}>
          Health Report — {PERSON_NAME[person]}
        </h1>
        <p style={{ fontFamily: MONO, fontSize: 12, color: "#78716C", marginTop: 8 }}>
          Generated {generatedOn} · {markers.length} test{markers.length !== 1 ? "s" : ""} · For clinical review
        </p>
      </div>

      {markers.length === 0 ? (
        <p style={{ fontFamily: SANS, color: "#78716C" }}>No tests selected. Go back to the dashboard and select tests to include.</p>
      ) : loading ? (
        <p style={{ fontFamily: MONO, color: "#78716C" }}>Loading…</p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 28 }}>
          {markers.map(name => data[name] && (
            <div key={name} className="print-section">
              <BiomarkerChart data={data[name]} person={person} showInfo={detail === "detailed"} />
            </div>
          ))}
          {failed.length > 0 && (
            <p style={{ fontFamily: MONO, fontSize: 12, color: "#B45309" }}>
              Could not load: {failed.join(", ")}
            </p>
          )}
        </div>
      )}

      <div style={{ marginTop: 40, paddingTop: 16, borderTop: "1px solid #E8E0D5", fontFamily: MONO, fontSize: 10, color: "#A8A099", textAlign: "center" }}>
        Generated from a personal health record · Not a substitute for professional medical advice
      </div>
    </div>
  );
}

export default function PrintPage() {
  return (
    <Suspense fallback={<div style={{ padding: 40, fontFamily: MONO, color: "#78716C" }}>Loading…</div>}>
      <PrintReport />
    </Suspense>
  );
}
