// Flexible report fields mirror the existing JSON artifacts; core case data is typed.
export type Json = Record<string, any>;
export type CaseRecord = {
  id: string;
  payload: Json;
  assessment: Json | null;
  status: string;
  provenance: string;
  history?: Json[];
  documents?: Json;
  latest_review?: Json;
};
export const pct = (value: number) =>
  Number.isFinite(value) ? `${(value * 100).toFixed(1)}%` : "Unavailable";
export const humanize = (value: string) => value.replaceAll("_", " ");
