"use client";

import {
  ComposedChart, Area, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ReferenceArea, ReferenceLine, ResponsiveContainer,
} from "recharts";
import type { BiomarkerHistory, Person } from "@/lib/api";
import { getBiomarkerInfo } from "@/lib/biomarker-info";

const C = {
  bg: "#FAF7F2", card: "#FFFFFF", surface: "#F0EBE0",
  border: "rgba(77,124,15,0.11)",
  olive: "#4D7C0F", oliveLight: "#65A30D",
  amber: "#B45309", red: "#DC2626",
  text: "#1C1917", muted: "#78716C", ghost: "#A8A099",
  grid: "rgba(77,124,15,0.07)",
};

const SANS = "'Satoshi', system-ui, sans-serif";
const MONO = "var(--font-dm-mono, 'DM Mono', monospace)";

// Scoped per person — AK's and RK's surgical histories are unrelated and
// must never cross-contaminate each other's charts.
const EVENTS: { date: string; label: string; color: string; person: Person }[] = [
  { date: "2025-04", label: "Thyroidectomy (PTC)", color: "#B45309", person: "AK" },
  { date: "2022-05", label: "Splenectomy", color: "#B45309", person: "RK" },
];

function flagColor(flag: string | null) {
  if (!flag) return C.olive;
  return flag.toUpperCase() === "H" ? C.red : C.amber;
}

function CustomDot(props: any) {
  const { cx, cy, payload } = props;
  if (payload.value == null) return null;
  const color = flagColor(payload.flag);
  const abnormal = !!payload.flag;
  if (!abnormal) return <circle cx={cx} cy={cy} r={3} fill={C.olive} stroke={C.card} strokeWidth={1.5} />;
  return <circle cx={cx} cy={cy} r={5} fill={color} stroke={C.card} strokeWidth={2} />;
}

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;
  const d = payload[0]?.payload;
  if (!d) return null;
  const color = flagColor(d.flag);
  return (
    <div style={{
      background: C.card, border: `1px solid ${C.border}`, borderRadius: 10,
      padding: "10px 14px", boxShadow: "0 4px 20px rgba(77,124,15,0.1)", minWidth: 130,
    }}>
      <div style={{ fontFamily: MONO, fontSize: 10, color: C.muted, marginBottom: 5, letterSpacing: "0.06em" }}>{d.date}</div>
      <div style={{ fontFamily: MONO, fontSize: 24, fontWeight: 500, color, lineHeight: 1 }}>{d.value ?? "—"}</div>
      {d.flag && (
        <div style={{
          marginTop: 7, display: "inline-block", padding: "2px 8px", borderRadius: 100,
          fontSize: 10, fontWeight: 600,
          background: d.flag.toUpperCase() === "H" ? "rgba(220,38,38,0.09)" : "rgba(180,83,9,0.09)",
          color, letterSpacing: "0.07em",
        }}>
          {d.flag.toUpperCase() === "H" ? "↑ High" : "↓ Low"}
        </div>
      )}
    </div>
  );
}

export function BiomarkerChart({ data, person }: { data: BiomarkerHistory; person: Person }) {
  const { name, unit, ref_low, ref_high } = data;
  const points = data.data.filter(p => p.value !== null);
  if (!points.length) return null;

  const values = points.map(p => p.value as number);
  const allBounds = [...values, ...(ref_low != null ? [ref_low] : []), ...(ref_high != null ? [ref_high] : [])];
  const rangeMin = Math.min(...allBounds);
  const rangeMax = Math.max(...allBounds);
  const pad = (rangeMax - rangeMin) * 0.22 || Math.abs(rangeMax) * 0.2 || 5;
  const yMin = Math.max(0, rangeMin - pad);
  const yMax = rangeMax + pad;

  const latest = points.at(-1)!;
  const latestColor = flagColor(latest.flag);
  const isAbnormal = !!latest.flag;

  const baseChartData = points.map(p => ({ ...p, date: p.date.slice(0, 7) }));
  const gradId = `grad-${name.replace(/\W+/g, "")}`;
  const info = getBiomarkerInfo(name);

  // Inject event dates as null placeholders so XAxis includes them even if no lab on that month
  const baseChartDates = baseChartData.map(d => d.date);
  const firstDate = baseChartDates[0];
  const lastDate = baseChartDates[baseChartDates.length - 1];
  const relevantEvents = EVENTS.filter(e => e.person === person && e.date >= firstDate && e.date <= lastDate);
  const chartData = [...baseChartData];
  for (const ev of relevantEvents) {
    if (!baseChartDates.includes(ev.date)) {
      const insertIdx = chartData.findIndex(d => d.date > ev.date);
      const nullPoint = { date: ev.date, value: null, text_value: null, flag: null };
      if (insertIdx === -1) chartData.push(nullPoint);
      else chartData.splice(insertIdx, 0, nullPoint);
    }
  }
  const chartDates = chartData.map(d => d.date);

  return (
    <div className="fade-up" style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      {/* Chart card */}
      <div style={{
        background: C.card, borderRadius: 13, border: `1px solid ${C.border}`,
        padding: "24px 26px 18px",
        boxShadow: "0 2px 12px rgba(77,124,15,0.06)",
      }}>
        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
          <div>
            <h2 style={{ fontFamily: SANS, fontWeight: 700, fontSize: 20, color: C.text, margin: 0, lineHeight: 1.1, letterSpacing: "-0.02em" }}>
              {name}
            </h2>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 5 }}>
              {unit && (
                <span style={{ fontFamily: MONO, fontSize: 10, color: C.ghost, textTransform: "uppercase", letterSpacing: "0.12em" }}>{unit}</span>
              )}
              {(ref_low != null || ref_high != null) && (
                <span style={{ fontFamily: MONO, fontSize: 10, color: C.muted }}>
                  ref {ref_low ?? "—"} – {ref_high ?? "∞"}
                </span>
              )}
            </div>
          </div>

          {/* Latest callout */}
          <div style={{ textAlign: "right" }}>
            <div style={{ fontFamily: MONO, fontSize: 40, fontWeight: 500, color: latestColor, lineHeight: 1 }}>
              {latest.value}
            </div>
            <div style={{ marginTop: 5 }}>
              {isAbnormal ? (
                <span style={{
                  display: "inline-block", padding: "3px 10px", borderRadius: 100,
                  fontSize: 11, fontWeight: 600,
                  background: latest.flag!.toUpperCase() === "H" ? "rgba(220,38,38,0.09)" : "rgba(180,83,9,0.09)",
                  color: latestColor, letterSpacing: "0.07em",
                }}>
                  {latest.flag!.toUpperCase() === "H" ? "↑ High" : "↓ Low"}
                </span>
              ) : (
                <span style={{ display: "inline-block", padding: "3px 10px", borderRadius: 100, fontSize: 11, fontWeight: 600, background: "rgba(77,124,15,0.09)", color: C.olive, letterSpacing: "0.07em" }}>
                  Normal
                </span>
              )}
            </div>
            <div style={{ fontFamily: MONO, fontSize: 10, color: C.ghost, marginTop: 5 }}>{latest.date}</div>
          </div>
        </div>

        {/* Chart */}
        <ResponsiveContainer width="100%" height={260}>
          <ComposedChart data={chartData} margin={{ top: 4, right: 6, bottom: 0, left: 0 }}>
            <defs>
              <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={isAbnormal ? C.red : C.olive} stopOpacity={0.18} />
                <stop offset="90%" stopColor={isAbnormal ? C.red : C.olive} stopOpacity={0.01} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="2 6" stroke={C.grid} vertical={false} />

            {ref_low != null && ref_high != null && (
              <ReferenceArea y1={ref_low} y2={ref_high} fill={C.olive} fillOpacity={0.05} />
            )}
            {ref_low != null && (
              <ReferenceLine y={ref_low} stroke={C.olive} strokeDasharray="4 4" strokeOpacity={0.4} strokeWidth={1} />
            )}
            {ref_high != null && (
              <ReferenceLine y={ref_high} stroke={C.amber} strokeDasharray="4 4" strokeOpacity={0.35} strokeWidth={1} />
            )}

            {relevantEvents.map(ev => (
              <ReferenceLine key={ev.date} x={ev.date} stroke={ev.color} strokeWidth={1.5} strokeDasharray="5 3"
                label={{ value: ev.label, position: "insideTopLeft", fontSize: 9, fill: ev.color, fontFamily: MONO, dx: 4, dy: -2 }}
              />
            ))}

            <XAxis dataKey="date" tick={{ fontFamily: MONO, fontSize: 10, fill: C.muted }} tickLine={false} axisLine={false} interval="preserveStartEnd" />
            <YAxis domain={[yMin, yMax]} tick={{ fontFamily: MONO, fontSize: 10, fill: C.muted }} tickLine={false} axisLine={false} width={42} tickFormatter={v => Number(v.toFixed(1)).toString()} />
            <Tooltip content={<CustomTooltip />} />

            <Area type="monotone" dataKey="value" stroke="none" fill={`url(#${gradId})`} connectNulls={true} />
            <Line type="monotone" dataKey="value" stroke={isAbnormal ? C.red : C.olive} strokeWidth={2.5}
              dot={<CustomDot />} activeDot={{ r: 5, fill: latestColor, stroke: C.card, strokeWidth: 2 }} connectNulls={true}
            />
          </ComposedChart>
        </ResponsiveContainer>

        <div style={{ marginTop: 12, fontFamily: MONO, fontSize: 10, color: C.ghost }}>
          {points.length} readings · min {Math.min(...values)} · max {Math.max(...values)}
        </div>
      </div>

      {/* Info blurb — matches portfolio's mantra/attr-card aesthetic */}
      {info && (
        <div style={{
          background: C.surface, borderRadius: 13, border: `1px solid ${C.border}`,
          padding: "20px 24px",
          display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 24,
        }}>
          {[
            { label: "What it measures", body: info.summary },
            { label: "Good ranges", body: info.goodRange },
            { label: "How to improve", body: info.howToImprove },
          ].map(s => (
            <div key={s.label}>
              <div style={{ fontFamily: MONO, fontSize: "0.68rem", fontWeight: 500, letterSpacing: "0.12em", textTransform: "uppercase", color: C.olive, marginBottom: 8 }}>
                {s.label}
              </div>
              <p style={{ fontFamily: SANS, fontSize: 13, color: C.muted, lineHeight: 1.7, margin: 0 }}>
                {s.body}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
