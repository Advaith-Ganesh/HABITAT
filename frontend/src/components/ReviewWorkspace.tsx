import { useState } from "react";
import { ArrowRight, CheckCircle2, FileQuestion } from "lucide-react";
import { AuditHistory, Card, EmptyState, SearchInput } from "./ui";
import { ExplanationChart } from "./Chart";
import { type Json, type CaseRecord, humanize, pct } from "../lib/types";
import { api } from "../lib/api";
function displayInput(feature: string, value: unknown) {
  if (feature.endsWith("_available"))
    return value === 1 ? "present" : "missing";
  if (
    [
      "conflicting_information",
      "specialist_support_requested",
      "housing_insecurity_reported",
    ].includes(feature)
  )
    return value === 1 ? "reported" : "not reported";
  return typeof value === "number" && !Number.isInteger(value)
    ? value.toFixed(1)
    : String(value);
}
export function statusText(record: CaseRecord) {
  if (record.status === "unassessed") return "Awaiting assessment";
  if (record.status === "resolved") return "Administrative review completed";
  const last =
    record.history?.filter((e) => e.action === "human_override").at(-1) ??
    (record.latest_review ? { detail: record.latest_review } : undefined);
  if (
    record.status === "pending" &&
    last?.detail.outcome === "request_evidence"
  )
    return "Additional information requested";
  return record.status === "pending"
    ? "Human review required"
    : "Routine review workflow";
}
export function Documents({ record }: { record: CaseRecord }) {
  const d = record.documents;
  if (!d) return <p>Document status unavailable. Refresh this application.</p>;
  return (
    <div className="documents">
      <div className="document-head">
        <span>Documentation completeness</span>
        <strong>{d.percentage.toFixed(1)}%</strong>
      </div>
      <progress
        value={d.present_count}
        max={d.required}
        aria-label="Documentation completeness"
      />
      <p>
        {d.present_count} of {d.required} required categories declared present.
      </p>
      <div className="document-list">
        {d.present.map((name: string) => (
          <div key={name}>
            <CheckCircle2 size={16} />
            <span>{name}</span>
            <small>Present</small>
          </div>
        ))}
        {d.missing.map((name: string) => (
          <div key={name}>
            <FileQuestion size={16} />
            <span>{name}</span>
            <small>Missing</small>
          </div>
        ))}
      </div>
      <p className="field-hint">
        Document requirements: income evidence, identity evidence and current
        housing evidence. Declarations only; no uploads or legal sufficiency
        checks.
      </p>
    </div>
  );
}
export function ApplicationDetails({ record }: { record: CaseRecord }) {
  return (
    <>
      <div className="detail-heading">
        <span className="reference">{record.id}</span>
        <span className="status-badge">{statusText(record)}</span>
      </div>
      <div className="key-values">
        <div>
          <span>Household members</span>
          <b>{record.payload.household_size}</b>
        </div>
        <div>
          <span>Monthly household income</span>
          <b>
            £{Number(record.payload.monthly_income).toLocaleString("en-GB")}
          </b>
        </div>
        <div>
          <span>Housing situation</span>
          <b>{humanize(record.payload.housing_situation)}</b>
        </div>
      </div>
      <p className="field-hint">{record.payload.application_completeness_score == null
        ? "Calculated intake completeness: unavailable. Compatibility with the trained feature is not established; human review is required without a model score. Document completeness is separate."
        : `Historical completeness input: ${Number(record.payload.application_completeness_score).toFixed(1)}%. Previously recorded, not recalculated or validated by this update. Separate from document completeness.`}</p>
      <Documents record={record} />
    </>
  );
}
export function ApplicationTable({
  records,
  onOpen,
}: {
  records: CaseRecord[];
  onOpen: (id: string) => void;
}) {
  const [query, setQuery] = useState(""),
    [page, setPage] = useState(1),
    [filter, setFilter] = useState("all");
  const rows = records.filter(
    (r) =>
      (filter === "all" || r.status === filter) &&
      `${r.id} ${r.payload.housing_situation}`
        .toLowerCase()
        .includes(query.toLowerCase()),
  );
  const pages = Math.max(1, Math.ceil(rows.length / 6)),
    current = Math.min(page, pages);
  return (
    <>
      <div className="filter-bar">
        <SearchInput
          value={query}
          onChange={(v) => {
            setQuery(v);
            setPage(1);
          }}
        />
        <label className="compact-label">
          Status
          <select
            aria-label="Filter application status"
            value={filter}
            onChange={(e) => {
              setFilter(e.target.value);
              setPage(1);
            }}
          >
            <option value="all">All statuses</option>
            <option value="unassessed">Awaiting assessment</option>
            <option value="pending">Human review required</option>
            <option value="routine">Routine review workflow</option>
            <option value="resolved">Review completed</option>
          </select>
        </label>
      </div>
      {rows.length ? (
        <>
          <div className="table-scroll" tabIndex={0} role="region" aria-label="Submitted applications table">
            <table>
              <caption className="sr-only">Submitted applications</caption>
              <thead>
                <tr>
                  {[
                    "Reference",
                    "Household",
                    "Monthly income",
                    "Housing situation",
                    "Documents",
                    "Status",
                    "Details",
                  ].map((t) => (
                    <th key={t}>{t}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.slice((current - 1) * 6, current * 6).map((r) => (
                  <tr key={r.id}>
                    <td>
                      <button
                        className="table-reference"
                        onClick={() => onOpen(r.id)}
                      >
                        {r.id}
                      </button>
                    </td>
                    <td>{r.payload.household_size}</td>
                    <td>
                      £
                      {Number(r.payload.monthly_income).toLocaleString("en-GB")}
                    </td>
                    <td>{humanize(r.payload.housing_situation)}</td>
                    <td>
                      {r.documents?.present_count}/{r.documents?.required}
                      <small className="block">
                        {r.documents?.percentage.toFixed(1)}% complete
                      </small>
                    </td>
                    <td>{statusText(r)}</td>
                    <td>
                      <button
                        className="icon-button"
                        aria-label={`Open ${r.id}`}
                        onClick={() => onOpen(r.id)}
                      >
                        <ArrowRight size={17} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="pagination">
            <span>{rows.length} applications</span>
            <button
              className="secondary"
              disabled={current === 1}
              onClick={() => setPage(current - 1)}
            >
              Previous
            </button>
            <span>
              {current} / {pages}
            </span>
            <button
              className="secondary"
              disabled={current === pages}
              onClick={() => setPage(current + 1)}
            >
              Next
            </button>
          </div>
        </>
      ) : (
        <EmptyState
          title="No matching applications"
          description="Try a different reference or status."
        />
      )}
    </>
  );
}
export function Assessment({
  record,
  explanation,
  explanationError,
  explanationLoading = false,
}: {
  record: CaseRecord;
  explanation?: Json;
  explanationError: string;
  explanationLoading?: boolean;
}) {
  const a = record.assessment;
  return (
    <>
      <div className="assessment-hero">
        <div>
          <span className="eyebrow">
            {record.id} · {a?.model_version ?? "Version not recorded"}
            {a?.assessed_at && <> · Assessed {new Date(a.assessed_at).toLocaleString()}</>}
          </span>
          <h2>
            {!a
              ? "Ready for assessment"
              : a.score == null
                ? "Assessment unavailable"
                : a.requires_review
                  ? "Additional human review recommended"
                  : "Routine human review workflow recommended"}
          </h2>
          <p>
            {a?.failure === "InputCompatibilityUnavailable"
              ? a.limitations
              : a
              ? "A review-routing recommendation. It is not housing approval or eligibility."
              : "Check input compatibility before running the saved Random Forest."}
          </p>
        </div>
        <div>
          <strong>{a?.score != null ? pct(a.score) : "—"}</strong>
          <small>Model-estimated additional review probability</small>
        </div>
      </div>
      <div className="two-col">
        <Card title="Why this recommendation?" tag={a?.score != null ? "GENUINE TREE SHAP" : "SHAP UNAVAILABLE"}>
          {explanation && a?.score != null ? (
            <>
              <div className="explanation-summary">
                {explanation.attributions.slice(0, 3).map((x: Json) => (
                  <p key={x.feature}>
                    <b>{humanize(x.feature)}</b> (
                    {displayInput(x.feature, x.value)}):{" "}
                    {x.attribution === 0
                      ? "no measured shift"
                      : `associated with a ${x.attribution > 0 ? "higher" : "lower"} model score`}{" "}
                    ({x.attribution > 0 ? "+" : ""}
                    {(x.attribution * 100).toFixed(1)} percentage points).
                  </p>
                ))}
              </div>
              <ExplanationChart explanation={explanation} />
              <p className="muted">
                Petrol: toward additional review. Sage: toward routine. Base
                value {pct(explanation.base_value)}; adding contributions gives{" "}
                {pct(explanation.score)}. These are associations, not causes or
                legal reasons.
              </p>
              <details>
                <summary>All measured contributions</summary>
                <div className="table-scroll" tabIndex={0} role="region" aria-label="SHAP contribution values table">
                  <table>
                    <thead>
                      <tr>
                        <th>Input</th>
                        <th>Value</th>
                        <th>SHAP contribution</th>
                      </tr>
                    </thead>
                    <tbody>
                      {explanation.attributions.map((x: Json) => (
                        <tr key={x.feature}>
                          <td>{humanize(x.feature)}</td>
                          <td>{String(x.value)}</td>
                          <td>{x.attribution.toFixed(4)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </details>
            </>
          ) : (
            <p role="status">
              {explanationLoading
                ? "Calculating explanation from the saved model…"
                : explanationError ||
                  (a
                    ? "Explanation unavailable. A caseworker can continue the review."
                    : "Assess this application to see the explanation.")}{" "}
              {a && "Human review remains available."}
            </p>
          )}
        </Card>
        <Card title="Documents & next steps">
          <Documents record={record} />
          {record.status === "pending" && record.latest_review && (
            <p className="warning">
              Caseworker follow-up remains open:{" "}
              {humanize(record.latest_review.outcome)}. Reassessment does not
              complete this human action.
            </p>
          )}
          {!!a?.input_validation?.warnings?.length && <div className="warning" role="status"><b>Input checks require human handling</b><ul>{a.input_validation.warnings.map((w: string) => <li key={w}>{w}</li>)}</ul><p>{a.input_validation.scope}</p></div>}
          {a && (
            <div className="callout">
              <b>
                {a.score == null
                  ? "Refer to a caseworker"
                  : a.uncertain
                    ? "Uncertain score: human escalation"
                    : a.requires_review
                      ? "Refer for additional human review"
                      : "Continue the routine human workflow"}
              </b>
              <p>{a.limitations}</p>
            </div>
          )}
        </Card>
      </div>
    </>
  );
}
export function Sandbox({
  records,
  onError,
}: {
  records: CaseRecord[];
  onError: (message: string) => void;
}) {
  const [id, setId] = useState(records[0]?.id ?? ""),
    [field, setField] = useState("synthetic_audit_group"),
    [value, setValue] = useState("Audit B"),
    [result, setResult] = useState<Json>(),
    [busy, setBusy] = useState(false);
  const selected = records.find((r) => r.id === id);
  function clear() {
    setResult(undefined);
  }
  async function run() {
    setBusy(true);
    clear();
    onError("");
    try {
      setResult(
        await api("/api/sandbox/compare", {
          application_id: id,
          field,
          value: field === "conflicting_information" ? Number(value) : value,
        }),
      );
    } catch (e) {
      onError(String(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <Card
      title="Compare Two Applications"
      tag="REAL INFERENCE · NO SAVED CHANGES"
    >
      <p>
        Change one input, compare two real predictions and inspect how the
        explanation changes. The saved case is untouched.
      </p>
      <div className="sandbox-controls">
        <label>
          Sample application
          <select
            aria-label="Sandbox application"
            value={id}
            onChange={(e) => {
              setId(e.target.value);
              clear();
            }}
          >
            {records.map((r) => (
              <option key={r.id}>{r.id}</option>
            ))}
          </select>
        </label>
        <label>
          Input to change
          <select
            aria-label="Sandbox input"
            value={field}
            onChange={(e) => {
              setField(e.target.value);
              setValue(
                e.target.value === "conflicting_information" ? "1" : "Audit B",
              );
              clear();
            }}
          >
            <option value="synthetic_audit_group">
              Audit group · excluded from model
            </option>
            <option value="conflicting_information">
              Conflicting information · model input
            </option>
          </select>
        </label>
        <label>
          Comparison value
          <select
            aria-label="Comparison value"
            value={value}
            onChange={(e) => {
              setValue(e.target.value);
              clear();
            }}
          >
            {(field === "synthetic_audit_group"
              ? ["Audit A", "Audit B", "Audit C"]
              : ["0", "1"]
            ).map((v) => (
              <option key={v}>{v}</option>
            ))}
          </select>
        </label>
      </div>
      <p className="muted">
        Original value:{" "}
        {field === "synthetic_audit_group"
          ? "Audit A (comparison baseline)"
          : String(selected?.payload.conflicting_information ?? "Unavailable")}
        .{" "}
        {field === "synthetic_audit_group"
          ? "Only the synthetic audit label changes."
          : "0 means no conflict reported; 1 means conflicting information."}
      </p>
      <button
        className="primary"
        disabled={!id || busy}
        onClick={() => void run()}
      >
        {busy ? "Comparing…" : "Run comparison"}
      </button>
      {result && (
        <div className="sandbox-result">
          <p role="status">
            {result.changed
              ? `Changed ${humanize(result.field)} from ${result.before_value} to ${result.after_value}.`
              : "No input changed. Choose a different value to test sensitivity."}
          </p>
          <div className="two-col">
            {(["before", "after"] as const).map((k) => (
              <div key={k}>
                <h3>{k === "before" ? "Original inputs" : "Changed input"}</h3>
                <strong className="comparison-score">
                  {result[k].prediction.score == null
                    ? "Assessment unavailable"
                    : pct(result[k].prediction.score)}
                </strong>
                <p>{result[k].prediction.category}</p>
                {result[k].explanation ? (
                  <ul>
                    {result[k].explanation.attributions
                      .slice(0, 3)
                      .map((x: Json) => (
                        <li key={x.feature}>
                          {humanize(x.feature)}: {x.attribution.toFixed(4)}
                        </li>
                      ))}
                  </ul>
                ) : (
                  <p>Explanation unavailable; refer to human review.</p>
                )}
              </div>
            ))}
          </div>
          <p className="callout">{result.limitation}</p>
        </div>
      )}
    </Card>
  );
}
export function HistoryCard({ record }: { record: CaseRecord }) {
  return (
    <Card title="Review history" tag="SAVED IN SQLITE">
      <AuditHistory history={record.history} />
    </Card>
  );
}
