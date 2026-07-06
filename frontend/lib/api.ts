const BASE = "http://localhost:8000";

export type Person = "AK" | "RK";

export interface CategoryGroup {
  category: string;
  biomarkers: string[];
}

export interface BiomarkerPoint {
  date: string;
  value: number | null;
  text_value: string | null;
  flag: string | null;
}

export interface BiomarkerHistory {
  name: string;
  unit: string;
  ref_low: number | null;
  ref_high: number | null;
  data: BiomarkerPoint[];
}

export interface LatestValue {
  name: string;
  value: number | null;
  text_value: string | null;
  unit: string;
  ref_low: number | null;
  ref_high: number | null;
  flag: string | null;
  date: string;
  delta: number | null;
  prev_value: number | null;
  prev_date: string | null;
}

export interface VitalsPoint {
  report_date: string;
  weight_lbs: number | null;
  height_in: number | null;
  bmi: number | null;
  bp_systolic: number | null;
  bp_diastolic: number | null;
  pulse: number | null;
  temperature: number | null;
}

// A biomarker only counts as flagged if its latest report is within this
// many years — an out-of-range result from years ago isn't clinically
// relevant today. Applies to both AK and RK. See CLAUDE.md "Flag recency rule".
const FLAG_RECENCY_YEARS = 2;

export function isFlagCurrent(dateStr: string): boolean {
  const cutoff = new Date();
  cutoff.setFullYear(cutoff.getFullYear() - FLAG_RECENCY_YEARS);
  return new Date(dateStr) >= cutoff;
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`);
  return res.json();
}

export const api = {
  persons: () => get<string[]>("/api/persons"),
  categories: (person: Person) =>
    get<CategoryGroup[]>(`/api/categories?person=${person}`),
  biomarker: (name: string, person: Person) =>
    get<BiomarkerHistory>(
      `/api/biomarker?name=${encodeURIComponent(name)}&person=${person}`
    ),
  vitals: (person: Person) =>
    get<VitalsPoint[]>(`/api/vitals?person=${person}`),
  latest: (person: Person) =>
    get<LatestValue[]>(`/api/latest?person=${person}`),
};
