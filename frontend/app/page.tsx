"use client";

import { useEffect, useState, useCallback } from "react";
import { BiomarkerChart } from "@/components/BiomarkerChart";
import { VitalsPanel } from "@/components/VitalsPanel";
import { PersonSwitcher } from "@/components/PersonSwitcher";
import {
  api,
  isFlagCurrent,
  type CategoryGroup,
  type BiomarkerHistory,
  type LatestValue,
  type VitalsPoint,
  type Person,
} from "@/lib/api";

const PERSON_NAME: Record<Person, string> = { AK: "Anirudh Kashyap", RK: "Rashmi Kashyap" };

// Portfolio design tokens — light "Warm Olive" theme
const C = {
  bg:         "#FAF7F2",
  surface:    "#F0EBE0",
  card:       "#FFFFFF",
  border:     "rgba(77,124,15,0.11)",
  borderHover:"rgba(77,124,15,0.28)",
  olive:      "#4D7C0F",
  oliveLight: "#65A30D",
  amber:      "#B45309",
  green:      "#15803D",
  red:        "#DC2626",
  text:       "#1C1917",
  muted:      "#78716C",
  ghost:      "#A8A099",
  // subtle tints
  oliveTint:  "rgba(77,124,15,0.06)",
  redTint:    "rgba(220,38,38,0.08)",
  amberTint:  "rgba(180,83,9,0.08)",
};

const SANS = "'Satoshi', system-ui, sans-serif";
const MONO = "var(--font-dm-mono, 'DM Mono', monospace)";
const EASE = "cubic-bezier(0.25, 0.46, 0.45, 0.94)";
const TRANSITION = `all 0.3s ${EASE}`;

function flagColor(flag: string | null) {
  if (!flag) return C.olive;
  return flag.toUpperCase() === "H" ? C.red : C.amber;
}

function isQuantitative(v: LatestValue) { return v.value !== null; }

// Section eyebrow — matches portfolio's `section-eyebrow` style
function Eyebrow({ children }: { children: React.ReactNode }) {
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: "0.6rem",
      fontFamily: MONO, fontSize: "0.72rem", fontWeight: 500,
      letterSpacing: "0.14em", textTransform: "uppercase", color: C.olive,
      marginBottom: "0.85rem",
    }}>
      <span style={{ height: 1, width: "2rem", background: C.olive, flexShrink: 0 }} />
      {children}
      <span style={{ height: 1, width: "2rem", background: C.olive, flexShrink: 0 }} />
    </div>
  );
}

function StatCard({
  v, isSelected, onClick, inReport, onToggleReport,
}: { v: LatestValue; isSelected: boolean; onClick: () => void; inReport: boolean; onToggleReport: () => void }) {
  const color = flagColor(v.flag);
  const tint = v.flag
    ? (v.flag.toUpperCase() === "H" ? C.redTint : C.amberTint)
    : isSelected ? C.oliveTint : "transparent";

  return (
    <button
      onClick={onClick}
      style={{
        background: C.card,
        border: `1px solid ${isSelected ? C.borderHover : C.border}`,
        borderRadius: 12,
        padding: "16px 18px",
        textAlign: "left",
        cursor: "pointer",
        width: "100%",
        transition: TRANSITION,
        position: "relative",
        overflow: "hidden",
      }}
      onMouseEnter={e => {
        const el = e.currentTarget as HTMLElement;
        el.style.borderColor = color === C.olive ? C.borderHover : `${color}44`;
        el.style.transform = "translateY(-2px)";
        el.style.boxShadow = "0 4px 16px rgba(77,124,15,0.09)";
      }}
      onMouseLeave={e => {
        const el = e.currentTarget as HTMLElement;
        el.style.borderColor = isSelected ? C.borderHover : C.border;
        el.style.transform = "translateY(0)";
        el.style.boxShadow = "none";
      }}
    >
      {/* Top accent bar on selected */}
      {isSelected && (
        <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: C.olive }} />
      )}
      {/* Flag tint bg */}
      {v.flag && (
        <div style={{ position: "absolute", inset: 0, background: tint, pointerEvents: "none" }} />
      )}

      {/* Add-to-print-report checkbox */}
      <div
        role="checkbox"
        aria-checked={inReport}
        title={inReport ? "Remove from print report" : "Add to print report"}
        onClick={e => { e.stopPropagation(); onToggleReport(); }}
        style={{
          position: "absolute", top: 10, right: 10, zIndex: 2,
          width: 16, height: 16, borderRadius: 4,
          border: `1.5px solid ${inReport ? C.olive : C.border}`,
          background: inReport ? C.olive : C.card,
          display: "flex", alignItems: "center", justifyContent: "center",
          cursor: "pointer", transition: TRANSITION,
        }}
      >
        {inReport && <span style={{ color: C.card, fontSize: 10, lineHeight: 1, fontWeight: 700 }}>✓</span>}
      </div>

      <div style={{ fontFamily: MONO, fontSize: "0.68rem", fontWeight: 500, color: C.muted, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 8, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis", position: "relative" }}>
        {v.name}
      </div>
      <div style={{ display: "flex", alignItems: "baseline", gap: 4, position: "relative" }}>
        <span style={{ fontFamily: MONO, fontSize: 24, fontWeight: 500, color, lineHeight: 1 }}>
          {v.value}
        </span>
        {v.unit && (
          <span style={{ fontFamily: MONO, fontSize: 10, color: C.ghost }}>{v.unit}</span>
        )}
      </div>
      {v.flag && (
        <div style={{
          marginTop: 7, display: "inline-flex", alignItems: "center", gap: 4,
          fontFamily: MONO, fontSize: "0.65rem", fontWeight: 600,
          color, letterSpacing: "0.07em",
          background: v.flag.toUpperCase() === "H" ? "rgba(220,38,38,0.1)" : "rgba(180,83,9,0.1)",
          padding: "2px 8px", borderRadius: 100,
          position: "relative",
        }}>
          {v.flag.toUpperCase() === "H" ? "↑ High" : "↓ Low"}
        </div>
      )}
      {v.delta != null && !v.flag && (
        <div style={{ marginTop: 5, fontFamily: MONO, fontSize: "0.65rem", color: v.delta === 0 ? C.ghost : v.delta > 0 ? C.red : C.green, position: "relative" }}>
          {v.delta > 0 ? "+" : ""}{v.delta} vs prev
        </div>
      )}
    </button>
  );
}

export default function Dashboard() {
  const [person, setPerson] = useState<Person>("AK");
  const [categories, setCategories] = useState<CategoryGroup[]>([]);
  const [activeTab, setActiveTab] = useState("overview");
  const [selectedBiomarker, setSelectedBiomarker] = useState("");
  const [chartData, setChartData] = useState<BiomarkerHistory | null>(null);
  const [chartLoading, setChartLoading] = useState(false);
  const [latest, setLatest] = useState<LatestValue[]>([]);
  const [vitals, setVitals] = useState<VitalsPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reportSelection, setReportSelection] = useState<Set<string>>(new Set());

  const toggleReport = useCallback((name: string) => {
    setReportSelection(prev => {
      const next = new Set(prev);
      if (next.has(name)) next.delete(name); else next.add(name);
      return next;
    });
  }, []);

  useEffect(() => {
    setLoading(true);
    setError(null);
    setActiveTab("overview");
    setSelectedBiomarker("");
    setChartData(null);
    setReportSelection(new Set());
    Promise.all([api.categories(person), api.latest(person), api.vitals(person)])
      .then(([cats, lat, vit]) => {
        setCategories(cats);
        // A flag from a report older than the recency window is stale —
        // clear it so no downstream view (stats bar, flagged grid, StatCard
        // color) treats it as currently out of range. See CLAUDE.md "Flag
        // recency rule".
        setLatest(lat.filter(isQuantitative).map(v => isFlagCurrent(v.date) ? v : { ...v, flag: null }));
        setVitals(vit);
      })
      .catch(() => setError("Cannot reach the API — is FastAPI running on port 8000?"))
      .finally(() => setLoading(false));
  }, [person]);

  const openBiomarker = useCallback(async (name: string, tab?: string) => {
    if (name === selectedBiomarker) {
      setSelectedBiomarker(""); setChartData(null); return;
    }
    setSelectedBiomarker(name);
    if (tab) setActiveTab(tab);
    setChartLoading(true); setChartData(null);
    try { setChartData(await api.biomarker(name, person)); }
    catch { setChartData(null); }
    finally { setChartLoading(false); }
  }, [selectedBiomarker, person]);

  const switchTab = (id: string) => {
    setActiveTab(id); setSelectedBiomarker(""); setChartData(null);
  };

  const flaggedCount = latest.filter(v => v.flag).length;

  const tabs = [
    { id: "overview", label: "Overview" },
    ...categories.map(c => ({ id: c.category, label: c.category })),
    { id: "vitals", label: "Vitals" },
  ];

  const categoryLatest = (cat: string) => {
    const group = categories.find(c => c.category === cat);
    return latest.filter(v => group?.biomarkers.includes(v.name));
  };

  const ChartPanel = () => (
    chartLoading ? (
      <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 13, padding: "48px 24px", textAlign: "center" }}>
        <p style={{ fontFamily: MONO, color: C.muted, fontSize: 13 }}>Loading…</p>
      </div>
    ) : chartData ? (
      <BiomarkerChart data={chartData} person={person} />
    ) : null
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh", background: C.bg }}>

      {/* ── Header ───────────────────────────────────────────────── */}
      <header style={{
        position: "sticky", top: 0, zIndex: 100,
        borderBottom: `1px solid rgba(77,124,15,0.12)`,
        padding: "0 9%",
        background: "rgba(250,247,242,0.92)",
        backdropFilter: "blur(14px)",
        WebkitBackdropFilter: "blur(14px)",
        boxShadow: "0 1px 24px rgba(77,124,15,0.06)",
      }}>
        {/* Top row */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "1.1rem 0 0" }}>
          <div>
            <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: "1rem", color: C.text, letterSpacing: "-0.01em" }}>
              {PERSON_NAME[person].toUpperCase()}
            </div>
            <div style={{ fontFamily: MONO, fontSize: "0.68rem", color: C.muted, marginTop: 2, letterSpacing: "0.04em" }}>
              {latest.length} biomarkers · {vitals.length} visits · 2010 – 2026
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <PersonSwitcher person={person} onChange={setPerson} />
            {flaggedCount > 0 && (
              <div style={{
                display: "flex", alignItems: "center", gap: 6,
                background: "rgba(220,38,38,0.08)",
                border: "1px solid rgba(220,38,38,0.2)",
                color: C.red, padding: "5px 14px", borderRadius: 100,
                fontFamily: MONO, fontSize: "0.72rem", fontWeight: 500,
              }}>
                <span style={{ width: 6, height: 6, borderRadius: "50%", background: C.red }} />
                {flaggedCount} flagged
              </div>
            )}
          </div>
        </div>

        {/* Tab bar */}
        <div className="tab-scroll" style={{ display: "flex", gap: 0, overflowX: "auto", marginTop: "0.5rem" }}>
          {tabs.map(t => {
            const isActive = activeTab === t.id;
            return (
              <button key={t.id} onClick={() => switchTab(t.id)} style={{
                padding: "0.65rem 1.1rem",
                border: "none",
                borderBottom: isActive ? `2px solid ${C.olive}` : "2px solid transparent",
                background: "transparent",
                cursor: "pointer",
                fontFamily: SANS,
                fontSize: "0.82rem",
                fontWeight: isActive ? 600 : 400,
                color: isActive ? C.text : C.muted,
                transition: TRANSITION,
                whiteSpace: "nowrap",
                marginBottom: -1,
                letterSpacing: isActive ? "-0.01em" : "0",
              }}
              onMouseEnter={e => { if (!isActive) (e.currentTarget as HTMLElement).style.color = C.olive; }}
              onMouseLeave={e => { if (!isActive) (e.currentTarget as HTMLElement).style.color = C.muted; }}
              >
                {t.label}
              </button>
            );
          })}
        </div>
      </header>

      {/* ── Main ─────────────────────────────────────────────────── */}
      <main style={{ flex: 1, padding: "3rem 9%", maxWidth: 1400, width: "100%", alignSelf: "center" }}>

        {error && (
          <div style={{ background: "rgba(220,38,38,0.06)", border: "1px solid rgba(220,38,38,0.2)", borderRadius: 12, padding: "20px 24px", textAlign: "center", marginBottom: 28 }}>
            <p style={{ fontFamily: MONO, color: C.red, fontSize: 13 }}>{error}</p>
            <p style={{ fontFamily: SANS, color: C.muted, fontSize: 13, marginTop: 8 }}>
              Run: <code style={{ background: C.surface, padding: "2px 8px", borderRadius: 5, fontFamily: MONO, fontSize: 12 }}>uvicorn backend.main:app --reload</code>
            </p>
          </div>
        )}

        {loading && !error && (
          <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "50vh" }}>
            <p style={{ fontFamily: MONO, color: C.muted, fontSize: 13 }}>Loading…</p>
          </div>
        )}

        {/* ── Overview ──────────────────────────────────────────── */}
        {!loading && !error && activeTab === "overview" && (
          <div className="fade-up" style={{ display: "flex", flexDirection: "column", gap: 36 }}>

            {/* ── 5-Year Narrative (hardcoded per-person medical history) ── */}
            {person === "AK" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
              <Eyebrow>5-Year Health Narrative</Eyebrow>

              {/* Prose card */}
              <div style={{
                background: C.card, border: `1px solid ${C.border}`, borderRadius: 13,
                padding: "28px 32px",
                boxShadow: "0 2px 12px rgba(77,124,15,0.05)",
              }}>
                <h2 style={{ fontFamily: SANS, fontWeight: 800, fontSize: "clamp(1.3rem,2.2vw,1.75rem)", color: C.text, letterSpacing: "-0.03em", lineHeight: 1.15, marginBottom: 12 }}>
                  15 years of data. One surgery. A lipid story still in progress.
                </h2>
                <p style={{ fontFamily: SANS, fontSize: 15, color: C.muted, lineHeight: 1.85, maxWidth: 760, marginBottom: 16 }}>
                  From 2010 onward, routine panels across CBC, lipids, metabolic, thyroid, and vitamins have
                  built one of the more complete personal health records possible. The defining event was a{" "}
                  <strong style={{ color: C.text, fontWeight: 600 }}>total thyroidectomy for papillary thyroid carcinoma (PTC) in April 2025</strong>,
                  now well behind — thyroglobulin is suppressed and TSH is titrated on levothyroxine.
                </p>
                <p style={{ fontFamily: SANS, fontSize: 15, color: C.muted, lineHeight: 1.85, maxWidth: 760, marginBottom: 16 }}>
                  <strong style={{ color: C.text, fontWeight: 600 }}>Lipids</strong> are the active front. LDL sits modestly elevated, HDL has run chronically low,
                  and triglycerides trend high — a pattern consistent across multiple years that points squarely
                  at the cardiometabolic axis: refined carbohydrates, insufficient aerobic volume, or both.
                  The Cholesterol/HDL ratio above 5.0 confirms this isn't just one number out of range.
                </p>
                <p style={{ fontFamily: SANS, fontSize: 15, color: C.muted, lineHeight: 1.85, maxWidth: 760, marginBottom: 0 }}>
                  <strong style={{ color: C.text, fontWeight: 600 }}>Vitamins</strong> tell a better story. After years of documented deficiencies,
                  supplementation has brought key markers — Vitamin D, B12 — into or near normal range.
                  That recovery arc is one of the clearest positive trends across the full dataset.
                </p>
              </div>

              {/* Timeline — milestone events */}
              <div style={{
                background: C.surface, border: `1px solid ${C.border}`, borderRadius: 13,
                padding: "22px 28px",
              }}>
                <div style={{ fontFamily: MONO, fontSize: "0.68rem", fontWeight: 500, letterSpacing: "0.12em", textTransform: "uppercase", color: C.olive, marginBottom: 16 }}>
                  Key Milestones
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>
                  {[
                    { date: "2010", label: "First recorded labs", note: "Beginning of longitudinal record" },
                    { date: "2018", label: "Sunrise Medical panel excluded", note: "Data quality issue — removed from trending" },
                    { date: "2024", label: "Thyroid nodule workup", note: "Ultrasound & fine-needle biopsy initiated" },
                    { date: "Apr 2025", label: "Total Thyroidectomy (PTC)", note: "Papillary thyroid carcinoma, curative surgery", highlight: true },
                    { date: "2025–", label: "Post-surgical surveillance", note: "Levothyroxine titration · TSH / Thyroglobulin monitoring" },
                  ].map((m, i, arr) => (
                    <div key={m.date} style={{ display: "flex", gap: 18, position: "relative" }}>
                      {/* Vertical connector */}
                      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 16, flexShrink: 0 }}>
                        <div style={{
                          width: m.highlight ? 12 : 8, height: m.highlight ? 12 : 8,
                          borderRadius: "50%",
                          background: m.highlight ? C.amber : C.olive,
                          border: `2px solid ${C.card}`,
                          flexShrink: 0, marginTop: 3,
                        }} />
                        {i < arr.length - 1 && (
                          <div style={{ width: 1, flex: 1, background: `rgba(77,124,15,0.2)`, minHeight: 20 }} />
                        )}
                      </div>
                      <div style={{ paddingBottom: i < arr.length - 1 ? 20 : 0 }}>
                        <div style={{ display: "flex", alignItems: "baseline", gap: 10 }}>
                          <span style={{ fontFamily: MONO, fontSize: 11, color: C.muted, letterSpacing: "0.05em", minWidth: 72 }}>{m.date}</span>
                          <span style={{ fontFamily: SANS, fontWeight: m.highlight ? 700 : 500, fontSize: 14, color: m.highlight ? C.amber : C.text }}>
                            {m.label}
                          </span>
                        </div>
                        <div style={{ fontFamily: MONO, fontSize: 11, color: C.ghost, marginTop: 2, paddingLeft: 82 }}>
                          {m.note}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Dynamic trend chips — derived from latest values */}
              {latest.length > 0 && (() => {
                const flaggedHigh = latest.filter(v => v.flag?.toUpperCase() === "H");
                const flaggedLow  = latest.filter(v => v.flag?.toUpperCase() === "L");
                const normal      = latest.filter(v => !v.flag);
                return (
                  <div style={{
                    background: C.card, border: `1px solid ${C.border}`, borderRadius: 13,
                    padding: "20px 28px",
                    display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 24,
                  }}>
                    {[
                      { label: "Currently normal", count: normal.length, color: C.olive, bg: "rgba(77,124,15,0.07)" },
                      { label: "Flagged high", count: flaggedHigh.length, color: C.red, bg: "rgba(220,38,38,0.07)" },
                      { label: "Flagged low", count: flaggedLow.length, color: C.amber, bg: "rgba(180,83,9,0.07)" },
                    ].map(s => (
                      <div key={s.label} style={{ display: "flex", alignItems: "center", gap: 16 }}>
                        <div style={{ width: 48, height: 48, borderRadius: 12, background: s.bg, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                          <span style={{ fontFamily: MONO, fontWeight: 700, fontSize: 20, color: s.color }}>{s.count}</span>
                        </div>
                        <div>
                          <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 14, color: C.text }}>{s.label}</div>
                          <div style={{ fontFamily: MONO, fontSize: 11, color: C.ghost }}>of {latest.length} biomarkers</div>
                        </div>
                      </div>
                    ))}
                  </div>
                );
              })()}
            </div>
            )}

            {/* ── 5-Year Narrative (RK — hardcoded medical history) ── */}
            {person === "RK" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
              <Eyebrow>5-Year Health Narrative</Eyebrow>

              {/* Prose card */}
              <div style={{
                background: C.card, border: `1px solid ${C.border}`, borderRadius: 13,
                padding: "28px 32px",
                boxShadow: "0 2px 12px rgba(77,124,15,0.05)",
              }}>
                <h2 style={{ fontFamily: SANS, fontWeight: 800, fontSize: "clamp(1.3rem,2.2vw,1.75rem)", color: C.text, letterSpacing: "-0.03em", lineHeight: 1.15, marginBottom: 12 }}>
                  Six years under hematology follow-up. A splenectomy behind her. A new arrival ahead.
                </h2>
                <p style={{ fontFamily: SANS, fontSize: 15, color: C.muted, lineHeight: 1.85, maxWidth: 760, marginBottom: 16 }}>
                  Since 2019, frequent CBC and differential panels — many drawn in-office at Northern Virginia
                  Hematology Oncology Associates, others sent out to LabCorp — have built a close-interval
                  record of blood counts. The defining event was a{" "}
                  <strong style={{ color: C.text, fontWeight: 600 }}>splenectomy in May 2022</strong>,
                  after which platelet counts commonly run higher than a pre-surgical baseline — a well
                  documented consequence of losing splenic platelet sequestration — so that shift is expected
                  rather than a new concern.
                </p>
                <p style={{ fontFamily: SANS, fontSize: 15, color: C.muted, lineHeight: 1.85, maxWidth: 760, marginBottom: 0 }}>
                  <strong style={{ color: C.text, fontWeight: 600 }}>March 2026</strong> brought the newest
                  chapter: the birth of their child. The visit cadence in this record reflects years of careful
                  monitoring — a fitting backdrop for the milestone that followed.
                </p>
              </div>

              {/* Timeline — milestone events */}
              <div style={{
                background: C.surface, border: `1px solid ${C.border}`, borderRadius: 13,
                padding: "22px 28px",
              }}>
                <div style={{ fontFamily: MONO, fontSize: "0.68rem", fontWeight: 500, letterSpacing: "0.12em", textTransform: "uppercase", color: C.olive, marginBottom: 16 }}>
                  Key Milestones
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>
                  {[
                    { date: "2019", label: "Hematology monitoring begins", note: "Regular CBC / differential follow-up at Northern Virginia Hematology Oncology Associates" },
                    { date: "May 2022", label: "Splenectomy", note: "Surgical spleen removal", highlight: true, color: C.amber },
                    { date: "2022–2025", label: "Post-splenectomy CBC surveillance", note: "Close-interval blood count monitoring continues" },
                    { date: "Mar 2026", label: "Birth of their child", note: "🎉", highlight: true, color: C.green },
                  ].map((m, i, arr) => (
                    <div key={m.date} style={{ display: "flex", gap: 18, position: "relative" }}>
                      {/* Vertical connector */}
                      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 16, flexShrink: 0 }}>
                        <div style={{
                          width: m.highlight ? 12 : 8, height: m.highlight ? 12 : 8,
                          borderRadius: "50%",
                          background: m.highlight ? (m.color ?? C.amber) : C.olive,
                          border: `2px solid ${C.card}`,
                          flexShrink: 0, marginTop: 3,
                        }} />
                        {i < arr.length - 1 && (
                          <div style={{ width: 1, flex: 1, background: `rgba(77,124,15,0.2)`, minHeight: 20 }} />
                        )}
                      </div>
                      <div style={{ paddingBottom: i < arr.length - 1 ? 20 : 0 }}>
                        <div style={{ display: "flex", alignItems: "baseline", gap: 10 }}>
                          <span style={{ fontFamily: MONO, fontSize: 11, color: C.muted, letterSpacing: "0.05em", minWidth: 72 }}>{m.date}</span>
                          <span style={{ fontFamily: SANS, fontWeight: m.highlight ? 700 : 500, fontSize: 14, color: m.highlight ? (m.color ?? C.amber) : C.text }}>
                            {m.label}
                          </span>
                        </div>
                        <div style={{ fontFamily: MONO, fontSize: 11, color: C.ghost, marginTop: 2, paddingLeft: 82 }}>
                          {m.note}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Dynamic trend chips — derived from latest values */}
              {latest.length > 0 && (() => {
                const flaggedHigh = latest.filter(v => v.flag?.toUpperCase() === "H");
                const flaggedLow  = latest.filter(v => v.flag?.toUpperCase() === "L");
                const normal      = latest.filter(v => !v.flag);
                return (
                  <div style={{
                    background: C.card, border: `1px solid ${C.border}`, borderRadius: 13,
                    padding: "20px 28px",
                    display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 24,
                  }}>
                    {[
                      { label: "Currently normal", count: normal.length, color: C.olive, bg: "rgba(77,124,15,0.07)" },
                      { label: "Flagged high", count: flaggedHigh.length, color: C.red, bg: "rgba(220,38,38,0.07)" },
                      { label: "Flagged low", count: flaggedLow.length, color: C.amber, bg: "rgba(180,83,9,0.07)" },
                    ].map(s => (
                      <div key={s.label} style={{ display: "flex", alignItems: "center", gap: 16 }}>
                        <div style={{ width: 48, height: 48, borderRadius: 12, background: s.bg, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                          <span style={{ fontFamily: MONO, fontWeight: 700, fontSize: 20, color: s.color }}>{s.count}</span>
                        </div>
                        <div>
                          <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 14, color: C.text }}>{s.label}</div>
                          <div style={{ fontFamily: MONO, fontSize: 11, color: C.ghost }}>of {latest.length} biomarkers</div>
                        </div>
                      </div>
                    ))}
                  </div>
                );
              })()}
            </div>
            )}

            {/* Stats row — matches portfolio stat bar style */}
            <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 13, display: "grid", gridTemplateColumns: "repeat(3, 1fr)" }}>
              {[
                { label: "Biomarkers tracked", value: String(latest.length), sub: "distinct quantitative markers" },
                { label: "Flagged values", value: String(flaggedCount), sub: "out of range · latest labs", alert: flaggedCount > 0 },
                { label: "Categories", value: String(categories.length), sub: "health domains" },
              ].map((s, i) => (
                <div key={s.label} style={{
                  padding: "1.75rem 2rem",
                  borderRight: i < 2 ? `1px solid ${C.border}` : "none",
                  textAlign: "center",
                }}>
                  <div style={{ fontFamily: MONO, fontSize: "0.68rem", fontWeight: 400, letterSpacing: "0.1em", textTransform: "uppercase", color: C.muted, marginBottom: 6 }}>
                    {s.label}
                  </div>
                  <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: "clamp(2rem,3vw,3rem)", letterSpacing: "-0.03em", lineHeight: 1, color: s.alert ? C.red : C.olive, marginBottom: 4 }}>
                    {s.value}
                  </div>
                  <div style={{ fontFamily: MONO, fontSize: "0.68rem", color: C.ghost }}>{s.sub}</div>
                </div>
              ))}
            </div>

            {/* Flagged */}
            {flaggedCount > 0 && (
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "1rem" }}>
                  <span style={{ height: 1, width: "2rem", background: C.red, flexShrink: 0 }} />
                  <span style={{ fontFamily: MONO, fontSize: "0.72rem", fontWeight: 500, letterSpacing: "0.14em", textTransform: "uppercase", color: C.red }}>
                    Flagged Values
                  </span>
                  <span style={{ height: 1, width: "2rem", background: C.red, flexShrink: 0 }} />
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10 }}>
                  {latest.filter(v => v.flag).map(v => (
                    <StatCard key={v.name} v={v} isSelected={selectedBiomarker === v.name} onClick={() => openBiomarker(v.name, "overview")} inReport={reportSelection.has(v.name)} onToggleReport={() => toggleReport(v.name)} />
                  ))}
                </div>
              </div>
            )}

            {selectedBiomarker && activeTab === "overview" && <ChartPanel />}

            {/* All latest */}
            <div>
              <Eyebrow>Latest Values</Eyebrow>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10 }}>
                {latest.map(v => (
                  <StatCard key={v.name} v={v} isSelected={selectedBiomarker === v.name} onClick={() => openBiomarker(v.name, "overview")} inReport={reportSelection.has(v.name)} onToggleReport={() => toggleReport(v.name)} />
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ── Category tab ──────────────────────────────────────── */}
        {!loading && !error && categories.some(c => c.category === activeTab) && (
          <div className="fade-up" style={{ display: "flex", flexDirection: "column", gap: 24 }}>
            <div>
              <Eyebrow>{activeTab}</Eyebrow>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10 }}>
                {categoryLatest(activeTab).map(v => (
                  <StatCard key={v.name} v={v} isSelected={selectedBiomarker === v.name} onClick={() => openBiomarker(v.name, activeTab)} inReport={reportSelection.has(v.name)} onToggleReport={() => toggleReport(v.name)} />
                ))}
              </div>
            </div>
            {selectedBiomarker && <ChartPanel />}
          </div>
        )}

        {/* ── Vitals ────────────────────────────────────────────── */}
        {!loading && !error && activeTab === "vitals" && (
          <VitalsPanel data={vitals} />
        )}
      </main>

      <footer style={{ borderTop: `1px solid rgba(77,124,15,0.08)`, padding: "1.2rem 9%", textAlign: "center", fontFamily: MONO, fontSize: "0.72rem", color: C.ghost }}>
        {PERSON_NAME[person]} · Personal Health Record · Local &amp; Private
      </footer>

      {/* Floating print-report bar */}
      {reportSelection.size > 0 && (
        <div style={{
          position: "fixed", bottom: 24, left: "50%", transform: "translateX(-50%)",
          display: "flex", alignItems: "center", gap: 14,
          background: C.text, color: C.bg, borderRadius: 100,
          padding: "10px 12px 10px 20px",
          boxShadow: "0 8px 32px rgba(28,25,23,0.25)",
          zIndex: 50,
        }}>
          <span style={{ fontFamily: SANS, fontWeight: 600, fontSize: 13.5 }}>
            {reportSelection.size} test{reportSelection.size !== 1 ? "s" : ""} selected
          </span>
          <button
            onClick={() => setReportSelection(new Set())}
            style={{
              fontFamily: SANS, fontSize: 12.5, color: C.ghost, background: "transparent",
              border: "none", cursor: "pointer", padding: "6px 4px",
            }}
          >
            Clear
          </button>
          <a
            href={`/print?person=${person}&markers=${encodeURIComponent(Array.from(reportSelection).join(","))}`}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              fontFamily: SANS, fontWeight: 600, fontSize: 13.5,
              background: C.oliveLight, color: C.text,
              borderRadius: 100, padding: "9px 18px",
              textDecoration: "none", whiteSpace: "nowrap",
            }}
          >
            Export as Print PDF →
          </a>
        </div>
      )}
    </div>
  );
}
