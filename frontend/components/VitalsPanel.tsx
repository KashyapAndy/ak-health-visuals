"use client";

import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer,
} from "recharts";
import type { VitalsPoint } from "@/lib/api";

const C = {
  card: "#FFFFFF", surface: "#F0EBE0",
  border: "rgba(77,124,15,0.11)",
  olive: "#4D7C0F", text: "#1C1917", muted: "#78716C", ghost: "#A8A099",
  grid: "rgba(77,124,15,0.07)",
};
const SANS = "'Satoshi', system-ui, sans-serif";
const MONO = "var(--font-dm-mono, 'DM Mono', monospace)";

interface Props { data: VitalsPoint[] }

function MiniArea({ data, dataKey, color }: { data: any[]; dataKey: string; color: string }) {
  const vals = data.map(d => d[dataKey]).filter((v): v is number => v != null);
  if (!vals.length) return <div style={{ height: 80, display: "flex", alignItems: "center", justifyContent: "center" }}><span style={{ fontFamily: MONO, fontSize: 11, color: C.ghost }}>no data</span></div>;
  const min = Math.min(...vals), max = Math.max(...vals);
  const pad = (max - min) * 0.3 || 5;
  const gradId = `vg-${dataKey}`;
  return (
    <ResponsiveContainer width="100%" height={88}>
      <AreaChart data={data} margin={{ top: 4, right: 2, bottom: 0, left: 0 }}>
        <defs>
          <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity={0.2} />
            <stop offset="90%" stopColor={color} stopOpacity={0.01} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="2 6" stroke={C.grid} vertical={false} />
        <XAxis dataKey="date" hide />
        <YAxis domain={[Math.max(0, min - pad), max + pad]} hide />
        <Tooltip
          contentStyle={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, padding: "6px 10px", fontFamily: MONO, fontSize: 11, boxShadow: "0 4px 12px rgba(77,124,15,0.08)" }}
          labelStyle={{ color: C.muted, marginBottom: 2, fontSize: 10 }}
          itemStyle={{ color }}
        />
        <Area type="monotone" dataKey={dataKey} stroke={color} strokeWidth={2} fill={`url(#${gradId})`}
          dot={{ r: 2.5, fill: color, stroke: C.card, strokeWidth: 1.5 }} connectNulls={false}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function VitalsPanel({ data }: Props) {
  if (!data.length) return null;

  const chartData = data.map(v => ({
    date: v.report_date.slice(0, 7),
    weight: v.weight_lbs, systolic: v.bp_systolic,
    diastolic: v.bp_diastolic, pulse: v.pulse, bmi: v.bmi,
  }));

  const latest = data.at(-1)!;

  const metrics = [
    { label: "Weight", value: latest.weight_lbs ? `${latest.weight_lbs}` : "—", unit: "lbs", dataKey: "weight", color: "#4D7C0F" },
    { label: "BMI", value: latest.bmi ? `${latest.bmi}` : "—", unit: "", dataKey: "bmi", color: "#15803D" },
    { label: "Blood Pressure", value: latest.bp_systolic ? `${latest.bp_systolic}/${latest.bp_diastolic}` : "—", unit: "mmHg", dataKey: "systolic", color: "#B45309" },
    { label: "Pulse", value: latest.pulse ? `${latest.pulse}` : "—", unit: "bpm", dataKey: "pulse", color: "#0369A1" },
  ];

  return (
    <div className="fade-up" style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      {/* Stat bar — matches portfolio stats-grid */}
      <div style={{
        background: C.card, border: `1px solid ${C.border}`, borderRadius: 13,
        display: "grid", gridTemplateColumns: "repeat(4, 1fr)",
      }}>
        {metrics.map((m, i) => (
          <div key={m.label} style={{
            padding: "1.5rem 1.75rem", textAlign: "center",
            borderRight: i < 3 ? `1px solid ${C.border}` : "none",
          }}>
            <div style={{ fontFamily: MONO, fontSize: "0.68rem", letterSpacing: "0.1em", textTransform: "uppercase", color: C.muted, marginBottom: 6 }}>
              {m.label}
            </div>
            <div style={{ display: "flex", alignItems: "baseline", gap: 5, justifyContent: "center" }}>
              <span style={{ fontFamily: MONO, fontSize: 28, fontWeight: 500, color: m.color, lineHeight: 1 }}>{m.value}</span>
              {m.unit && <span style={{ fontFamily: MONO, fontSize: 11, color: C.ghost }}>{m.unit}</span>}
            </div>
          </div>
        ))}
      </div>

      {/* Charts 2x2 */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
        {metrics.map(m => (
          <div key={m.label} style={{
            background: C.card, border: `1px solid ${C.border}`, borderRadius: 13,
            padding: "20px 22px 16px",
            boxShadow: "0 1px 6px rgba(77,124,15,0.05)",
          }}>
            <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 15, color: C.text, letterSpacing: "-0.01em", marginBottom: 3 }}>
              {m.label}
            </div>
            <div style={{ fontFamily: MONO, fontSize: "0.68rem", color: C.ghost, marginBottom: 12 }}>
              {chartData.filter(d => d[m.dataKey as keyof typeof d] != null).length} readings
            </div>
            <MiniArea
              data={chartData.filter(d => d[m.dataKey as keyof typeof d] != null)}
              dataKey={m.dataKey}
              color={m.color}
            />
          </div>
        ))}
      </div>
    </div>
  );
}
