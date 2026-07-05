"use client";

import type { LatestValue } from "@/lib/api";

function getStatus(v: LatestValue): "high" | "low" | "normal" | "qualitative" {
  if (v.value === null) return "qualitative";
  if (v.flag?.toUpperCase() === "H") return "high";
  if (v.flag?.toUpperCase() === "L") return "low";
  if (v.ref_high != null && v.value > v.ref_high) return "high";
  if (v.ref_low  != null && v.value < v.ref_low)  return "low";
  return "normal";
}

const STATUS: Record<string, { dot: string; val: string }> = {
  high:        { dot: "#DC2626", val: "#DC2626" },
  low:         { dot: "#D97706", val: "#D97706" },
  normal:      { dot: "#4D7C0F", val: "#1C1917" },
  qualitative: { dot: "#B5A99A", val: "#78716C" },
};

interface Props { v: LatestValue; onClick: () => void; }

export function LatestCard({ v, onClick }: Props) {
  const s = getStatus(v);
  const colors = STATUS[s];
  const displayVal = v.value !== null ? v.value : (v.text_value ?? "—");

  return (
    <button
      onClick={onClick}
      style={{
        width: "100%",
        display: "flex",
        alignItems: "center",
        gap: 12,
        padding: "12px 14px",
        background: "#fff",
        border: "1px solid #E8E0D5",
        borderRadius: 12,
        cursor: "pointer",
        textAlign: "left",
        transition: "box-shadow 0.15s, border-color 0.15s",
        boxShadow: "0 1px 3px rgba(0,0,0,0.04)",
      }}
      onMouseEnter={e => {
        (e.currentTarget as HTMLElement).style.boxShadow = "0 4px 16px rgba(0,0,0,0.09)";
        (e.currentTarget as HTMLElement).style.borderColor = "#D0C8BE";
      }}
      onMouseLeave={e => {
        (e.currentTarget as HTMLElement).style.boxShadow = "0 1px 3px rgba(0,0,0,0.04)";
        (e.currentTarget as HTMLElement).style.borderColor = "#E8E0D5";
      }}
    >
      {/* Status dot */}
      <span style={{ width: 7, height: 7, borderRadius: "50%", background: colors.dot, flexShrink: 0 }} />

      {/* Name */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontFamily: "var(--font-outfit, Outfit, sans-serif)", fontSize: 12.5, color: "#78716C", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
          {v.name}
        </div>
      </div>

      {/* Value + delta */}
      <div style={{ textAlign: "right", flexShrink: 0 }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 3, justifyContent: "flex-end" }}>
          <span style={{ fontFamily: "var(--font-dm-mono, 'DM Mono', monospace)", fontSize: 15, fontWeight: 500, color: colors.val }}>
            {displayVal}
          </span>
          {v.unit && (
            <span style={{ fontFamily: "var(--font-dm-mono, monospace)", fontSize: 9.5, color: "#B5A99A" }}>{v.unit}</span>
          )}
        </div>
        {v.delta != null && (
          <div style={{
            fontFamily: "var(--font-dm-mono, monospace)",
            fontSize: 10,
            color: v.delta === 0 ? "#B5A99A" : v.delta > 0 ? "#DC2626" : "#4D7C0F",
            marginTop: 1,
          }}>
            {v.delta > 0 ? "+" : ""}{v.delta}
          </div>
        )}
      </div>
    </button>
  );
}
