"use client";

import { useState } from "react";
import type { CategoryGroup } from "@/lib/api";

interface Props {
  categories: CategoryGroup[];
  selectedBiomarker: string;
  selectedCategory: string;
  onSelectCategory: (cat: string) => void;
  onSelectBiomarker: (name: string) => void;
}

export function Sidebar({ categories, selectedBiomarker, selectedCategory, onSelectCategory, onSelectBiomarker }: Props) {
  return (
    <aside style={{
      width: 228,
      minWidth: 228,
      height: "100%",
      display: "flex",
      flexDirection: "column",
      background: "#fff",
      borderRight: "1px solid #E8E0D5",
      overflowY: "auto",
    }}>
      {/* Wordmark */}
      <div style={{ padding: "20px 20px 16px", borderBottom: "1px solid #E8E0D5" }}>
        <div style={{ fontFamily: "var(--font-outfit, Outfit, sans-serif)", fontWeight: 300, fontSize: 10, letterSpacing: "0.18em", color: "#78716C", textTransform: "uppercase", marginBottom: 2 }}>
          Health
        </div>
        <div style={{ fontFamily: "var(--font-outfit, Outfit, sans-serif)", fontWeight: 700, fontSize: 18, color: "#0D1B2A", lineHeight: 1.1 }}>
          Dashboard
        </div>
      </div>

      {/* Category + biomarker nav */}
      <nav style={{ flex: 1, padding: "10px 8px" }}>
        {categories.map((group) => {
          const isCatActive = selectedCategory === group.category;
          return (
            <div key={group.category} style={{ marginBottom: 2 }}>
              <button
                onClick={() => onSelectCategory(group.category)}
                style={{
                  width: "100%",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  padding: "7px 12px",
                  borderRadius: 8,
                  border: "none",
                  cursor: "pointer",
                  background: isCatActive ? "#F1F8E9" : "transparent",
                  color: isCatActive ? "#3A5C09" : "#1C1917",
                  fontFamily: "var(--font-outfit, Outfit, sans-serif)",
                  fontWeight: isCatActive ? 600 : 400,
                  fontSize: 13,
                  textAlign: "left",
                  transition: "background 0.15s",
                }}
                onMouseEnter={e => { if (!isCatActive) (e.currentTarget as HTMLElement).style.background = "#F5F3EF"; }}
                onMouseLeave={e => { if (!isCatActive) (e.currentTarget as HTMLElement).style.background = "transparent"; }}
              >
                {group.category}
                <span style={{ fontSize: 9, color: isCatActive ? "#4D7C0F" : "#B5A99A" }}>
                  {isCatActive ? "▾" : "▸"}
                </span>
              </button>

              {isCatActive && (
                <div style={{ paddingLeft: 12, paddingBottom: 4 }}>
                  {group.biomarkers.map((name) => {
                    const isActive = selectedBiomarker === name;
                    return (
                      <button
                        key={name}
                        onClick={() => onSelectBiomarker(name)}
                        style={{
                          width: "100%",
                          display: "block",
                          padding: "5px 10px",
                          borderRadius: 6,
                          border: "none",
                          cursor: "pointer",
                          background: isActive ? "#ECFCCB" : "transparent",
                          color: isActive ? "#3A5C09" : "#78716C",
                          fontFamily: "var(--font-outfit, Outfit, sans-serif)",
                          fontWeight: isActive ? 500 : 400,
                          fontSize: 12.5,
                          textAlign: "left",
                          transition: "all 0.1s",
                          marginBottom: 1,
                        }}
                        onMouseEnter={e => { if (!isActive) { (e.currentTarget as HTMLElement).style.background = "#F5F3EF"; (e.currentTarget as HTMLElement).style.color = "#1C1917"; } }}
                        onMouseLeave={e => { if (!isActive) { (e.currentTarget as HTMLElement).style.background = "transparent"; (e.currentTarget as HTMLElement).style.color = "#78716C"; } }}
                      >
                        {name}
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </nav>

      <div style={{ padding: "12px 20px", borderTop: "1px solid #E8E0D5" }}>
        <span style={{ fontFamily: "var(--font-dm-mono, 'DM Mono', monospace)", fontSize: 9.5, color: "#B5A99A", letterSpacing: "0.12em", textTransform: "uppercase" }}>
          Local · Private
        </span>
      </div>
    </aside>
  );
}
