import { Suspense, useEffect, useRef, useState, type ReactNode } from "react";
import {
  AlertCircle,
  ArrowDown,
  ArrowUp,
  ArrowUpRight,
  Check,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  FileSearch,
  LoaderCircle,
  Search,
  ShieldCheck,
  X,
} from "lucide-react";
import { type Json, type CaseRecord, humanize, pct } from "../lib/types";
export function SkeletonLoader() {
  return (
    <div className="skeleton-grid" aria-label="Loading workspace" role="status">
      {[1, 2, 3, 4].map((i) => (
        <div className="skeleton" key={i} />
      ))}
    </div>
  );
}
export function Card({
  title,
  tag,
  children,
}: {
  title: string;
  tag?: string;
  children: ReactNode;
}) {
  return (
    <section className="card">
      <div className="card-title">
        <h2>{title}</h2>
        {tag && <span className="eyebrow">{tag}</span>}
      </div>
      <Suspense
        fallback={
          <div className="chart-loading" role="status">
            <LoaderCircle className="spin" size={20} />
            Loading visualisation…
          </div>
        }
      >
        {children}
      </Suspense>
    </section>
  );
}
export function PageHeader({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="page-heading">
      <div>
        <div className="eyebrow">RESPONSIBLE HOUSING INTELLIGENCE</div>
        <h1 tabIndex={-1} id="page-title">
          {title}
        </h1>
        <p>{description}</p>
      </div>
      {action}
    </div>
  );
}
export function MetricCard({
  label,
  value,
  hint,
  icon,
  tone = "indigo",
}: {
  label: string;
  value: ReactNode;
  hint: string;
  icon?: ReactNode;
  tone?: string;
}) {
  return (
    <div className={`metric-card ${tone}`}>
      <div className="metric-label">
        <span>{label}</span>
        {icon && <span className="metric-icon">{icon}</span>}
      </div>
      <strong>{value}</strong>
      <small>{hint}</small>
    </div>
  );
}
export function StatusBadge({ value }: { value: string }) {
  const labels: Record<string, string> = {
    pending: "Needs human review",
    routine: "Routine workflow",
    resolved: "Human reviewed",
    unassessed: "Awaiting assessment",
  };
  return (
    <span className={`status ${value}`}>
      <span className="status-dot" />
      {labels[value] ?? value}
    </span>
  );
}
export { StatusBadge as Status };
export function AuditFinding({
  status,
  children,
}: {
  status: string;
  children?: ReactNode;
}) {
  return (
    <div
      className={`audit-finding ${status.startsWith("Potential") ? "concern" : status.startsWith("Inconclusive") ? "inconclusive" : "clear"}`}
    >
      <ShieldCheck size={18} />
      <div>
        <strong>{status}</strong>
        {children && <p>{children}</p>}
      </div>
    </div>
  );
}
export function EmptyState({
  title = "No cases found",
  description = "Try another search or create an application.",
  action,
}: {
  title?: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="empty-state">
      <FileSearch size={28} />
      <h3>{title}</h3>
      <p>{description}</p>
      {action}
    </div>
  );
}
export function ErrorState({
  message,
  retry,
}: {
  message: string;
  retry?: () => void;
}) {
  return (
    <div role="alert" className="error">
      <AlertCircle size={19} />
      <div>
        <b>Something needs attention</b>
        <p>{message}</p>
      </div>
      {retry && (
        <button className="secondary" onClick={retry}>
          Retry
        </button>
      )}
    </div>
  );
}
export function ToastNotification({
  message,
  dismiss,
}: {
  message: string;
  dismiss: () => void;
}) {
  return (
    <div role="status" className="toast">
      <CheckCircle2 size={18} />
      <span>{message}</span>
      <button onClick={dismiss} aria-label="Dismiss notification">
        <X size={16} />
      </button>
    </div>
  );
}
export function SearchInput({
  value,
  onChange,
}: {
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div className="search">
      <Search size={17} />
      <input
        aria-label="Search cases"
        placeholder="Search by case reference…"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
      {value && (
        <button aria-label="Clear search" onClick={() => onChange("")}>
          <X size={14} />
        </button>
      )}
    </div>
  );
}
export function FilterBar({ children }: { children: ReactNode }) {
  return <div className="toolbar">{children}</div>;
}
export function ProgressIndicator({
  steps,
  current,
  onStep,
}: {
  steps: string[];
  current: number;
  onStep: (i: number) => void;
}) {
  return (
    <ol className="stepper" aria-label="Application progress">
      {steps.map((step, i) => (
        <li key={step}>
          <button
            type="button"
            className={
              i === current ? "current" : i < current ? "complete" : ""
            }
            onClick={() => onStep(i)}
            aria-current={i === current ? "step" : undefined}
          >
            <span>{i < current ? <Check size={13} /> : i + 1}</span>
            <b>{step}</b>
          </button>
        </li>
      ))}
    </ol>
  );
}
function Modal({
  title,
  children,
  onClose,
  drawer = false,
}: {
  title: string;
  children: ReactNode;
  onClose: () => void;
  drawer?: boolean;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const dialog = ref.current;
    if (dialog && !dialog.open) dialog.showModal();
    return () => {
      if (dialog?.open) dialog.close();
    };
  }, []);
  return (
    <dialog
      ref={ref}
      className={drawer ? "dialog drawer" : "dialog"}
      aria-labelledby="dialog-title"
      onCancel={(event) => {
        event.preventDefault();
        onClose();
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="dialog-header">
        <div>
          <span className="eyebrow">SYNTHETIC WORKSPACE</span>
          <h2 id="dialog-title">{title}</h2>
        </div>
        <button
          className="icon-button"
          onClick={onClose}
          aria-label="Close dialog"
          autoFocus
        >
          <X size={20} />
        </button>
      </div>
      {children}
    </dialog>
  );
}
export function ConfirmationDialog({
  title,
  children,
  onCancel,
  onConfirm,
  busy,
  confirmLabel = "Confirm review action",
}: {
  title: string;
  children: ReactNode;
  onCancel: () => void;
  onConfirm: () => void;
  busy: boolean;
  confirmLabel?: string;
}) {
  return (
    <Modal
      title={title}
      onClose={() => {
        if (!busy) onCancel();
      }}
    >
      <div className="dialog-body">{children}</div>
      <div className="dialog-actions">
        <button className="secondary" disabled={busy} onClick={onCancel}>
          Cancel
        </button>
        <button className="primary" disabled={busy} onClick={onConfirm}>
          {busy ? "Saving…" : confirmLabel}
        </button>
      </div>
    </Modal>
  );
}
export function AuditHistory({ history = [] }: { history?: Json[] }) {
  return (
    <div className="timeline">
      {history.map((e, i) => (
        <div className="event" key={`${e.timestamp}-${i}`}>
          <span className="event-dot" />
          <div>
            {e.application_id && <small>{e.application_id}</small>}
            <b>{humanize(e.action)}</b>
            <small>
              <time dateTime={e.timestamp}>
                {new Date(e.timestamp).toLocaleString("en-GB", {
                  timeZone: "Europe/London",
                })}{" "}
                UK
              </time>
            </small>
            <p>
              {e.detail.reason ??
                e.detail.provenance ??
                e.detail.category ??
                "Application submitted"}
            </p>
            {e.detail.outcome && (
              <span className="subtle-tag">{humanize(e.detail.outcome)}</span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
export function CaseDrawer({
  record,
  onClose,
  onExplain,
}: {
  record: CaseRecord;
  onClose: () => void;
  onExplain: () => void;
}) {
  return (
    <Modal title={record.id} onClose={onClose} drawer>
      <div className="dialog-body">
        <StatusBadge value={record.status} />
        <p className="muted">{record.provenance}</p>
        <div className="drawer-score">
          <small>Additional-review model score</small>
          <strong>
            {record.assessment?.score != null
              ? pct(record.assessment.score)
              : "Not assessed"}
          </strong>
          <p>
            {record.assessment?.category ??
              "Run an assessment to view the recommendation."}
          </p>
        </div>
        <div className="key-values">
          {Object.entries(record.payload)
            .filter(([key]) => key !== "synthetic_only")
            .map(([key, value]) => (
              <div key={key}>
                <span>{humanize(key)}</span>
                <b>{String(value)}</b>
              </div>
            ))}
        </div>
        <h3>Case history</h3>
        <AuditHistory history={record.history} />
      </div>
      <div className="dialog-actions">
        <button className="primary" onClick={onExplain}>
          Open assessment & review <ArrowUpRight size={16} />
        </button>
      </div>
    </Modal>
  );
}
export function DataTable({
  rows,
  onOpen,
  paginate = true,
  review = false,
}: {
  rows: CaseRecord[];
  onOpen: (id: string) => void;
  paginate?: boolean;
  review?: boolean;
}) {
  const [sort, setSort] = useState(review ? "priority" : paginate ? "id" : ""),
    [ascending, setAscending] = useState(true),
    [page, setPage] = useState(1),
    [size, setSize] = useState(5);
  const value = (r: CaseRecord, key: string): string | number =>
    key === "score"
      ? (r.assessment?.score ?? -1)
      : key === "priority"
        ? r.assessment?.failure
          ? 0
          : r.assessment?.uncertain
            ? 1
            : 2
        : key === "situation"
          ? r.payload.housing_situation
          : key === "status"
            ? r.status
            : r.id;
  const sorted = [...rows].sort((a, b) => {
    if (!sort) return 0;
    const x = value(a, sort),
      y = value(b, sort);
    return (
      (typeof x === "number" && typeof y === "number"
        ? x - y
        : String(x).localeCompare(String(y))) * (ascending ? 1 : -1) ||
      a.id.localeCompare(b.id)
    );
  });
  const total = Math.max(1, Math.ceil(rows.length / size)),
    current = Math.min(page, total),
    shown = paginate
      ? sorted.slice((current - 1) * size, current * size)
      : sorted;
  const cols = [
    ["id", "Case reference"],
    ["situation", "Intake context"],
    ["score", "Model score"],
    ["status", "Workflow status"],
    ...(review ? [["priority", "Review priority"]] : []),
  ];
  return (
    <div className="data-table">
      <div className="table-scroll" tabIndex={0} role="region" aria-label="Cases table">
        <table>
          <caption className="sr-only">
            Synthetic application register. Sort with column headings.
          </caption>
          <thead>
            <tr>
              {cols.map(([key, label]) => (
                <th
                  key={key}
                  scope="col"
                  aria-sort={
                    sort === key
                      ? ascending
                        ? "ascending"
                        : "descending"
                      : "none"
                  }
                >
                  <button
                    className="sort-button"
                    onClick={() => {
                      setSort(key);
                      setAscending(sort === key ? !ascending : true);
                      setPage(1);
                    }}
                  >
                    {label}
                    {sort === key ? (
                      ascending ? (
                        <ArrowUp size={12} />
                      ) : (
                        <ArrowDown size={12} />
                      )
                    ) : null}
                  </button>
                </th>
              ))}
              <th scope="col">
                <span className="sr-only">Open case</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {shown.map((c) => (
              <tr key={c.id}>
                <td>
                  <button className="case-link" onClick={() => onOpen(c.id)}>
                    {c.id}
                  </button>
                  <small>Housing Application</small>
                </td>
                <td className="capitalize">
                  {c.payload.housing_situation}
                  <small>
                    {c.payload.missing_document_count} missing evidence items
                  </small>
                </td>
                <td className="tabular">
                  {c.assessment?.score != null ? pct(c.assessment.score) : "—"}
                  {c.assessment?.uncertain && (
                    <small>Human fallback / uncertainty</small>
                  )}
                </td>
                <td>
                  <StatusBadge value={c.status} />
                </td>
                {review && (
                  <td>
                    <span className="subtle-tag">
                      {c.assessment?.failure
                        ? "Inference unavailable"
                        : c.assessment?.uncertain
                          ? "Uncertain prediction"
                          : "Additional review"}
                    </span>
                  </td>
                )}
                <td>
                  <button
                    className="icon-button"
                    aria-label={`Open ${c.id}`}
                    onClick={() => onOpen(c.id)}
                  >
                    <ChevronRight size={17} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {!rows.length && <EmptyState />}
      {paginate && rows.length > 0 && (
        <div className="pagination">
          <span>
            {(current - 1) * size + 1}–{Math.min(current * size, rows.length)}{" "}
            of {rows.length} cases
          </span>
          <label>
            Rows{" "}
            <select
              aria-label="Rows per page"
              value={size}
              onChange={(e) => {
                setSize(Number(e.target.value));
                setPage(1);
              }}
            >
              {[5, 10, 20, 50].map((n) => (
                <option key={n}>{n}</option>
              ))}
            </select>
          </label>
          <button
            className="icon-button"
            aria-label="Previous page"
            disabled={current <= 1}
            onClick={() => setPage(current - 1)}
          >
            <ChevronLeft size={17} />
          </button>
          <span aria-live="polite">
            {current} / {total}
          </span>
          <button
            className="icon-button"
            aria-label="Next page"
            disabled={current >= total}
            onClick={() => setPage(current + 1)}
          >
            <ChevronRight size={17} />
          </button>
        </div>
      )}
    </div>
  );
}
export function HumanReviewPanel({
  record,
  reason,
  setReason,
  outcome,
  setOutcome,
  busy,
  onResolve,
  onPolicy,
}: {
  record: CaseRecord;
  reason: string;
  setReason: (v: string) => void;
  outcome: string;
  setOutcome: (v: string) => void;
  busy: boolean;
  onResolve: () => void;
  onPolicy: () => void;
}) {
  return (
    <Card title="Human review" tag="YOU REMAIN IN CONTROL">
      <p className="muted">
        Record an intake-workflow action. This never allocates housing or
        determines eligibility.
      </p>
      <label>
        Review action
        <select value={outcome} onChange={(e) => setOutcome(e.target.value)}>
          <option value="routine">
            Complete review · routine human workflow
          </option>
          <option value="request_evidence">
            Request more evidence · keep in queue
          </option>
          <option value="escalate">
            Escalate to specialist · keep in queue
          </option>
          <option value="additional_review">
            Continue additional review · keep in queue
          </option>
        </select>
      </label>
      <label>
        Reviewer notes & mandatory reason
        <textarea
          minLength={8}
          maxLength={1000}
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="Describe the evidence, your reasoning and the next human action…"
        />
      </label>
      <small className="field-hint">
        At least 8 meaningful characters. Use synthetic notes only.
      </small>
      <button
        className="primary full-width"
        disabled={
          busy ||
          reason.trim().length < 8 ||
          !record.assessment ||
          record.status === "resolved"
        }
        onClick={onResolve}
      >
        {record.status === "resolved"
          ? "Review already completed"
          : "Record review action"}
      </button>
      <div className="callout">
        <b>Policy evidence is separate</b>
        {record.assessment?.policy_evidence?.prompts?.map((p: string) => (
          <p key={p}>{p}</p>
        ))}
        <p>
          Demo intake prompts are fictional assumptions. They are not statutory
          eligibility rules.
        </p>
        <button className="text-button" onClick={onPolicy}>
          View policy reference <ArrowUpRight size={15} />
        </button>
      </div>
    </Card>
  );
}
export function PolicyReferenceCard({ pack }: { pack: Json }) {
  return (
    <Card
      title={pack.functional ? "England reference" : "Future integration"}
      tag={pack.functional ? "ILLUSTRATIVE INTAKE" : "NOT IMPLEMENTED"}
    >
      <div className="policy-heading">
        <span className="policy-code">
          {pack.functional
            ? "EN"
            : pack.id === "india"
              ? "IN"
              : pack.id === "singapore"
                ? "SG"
                : "US"}
        </span>
        <div>
          <h3>{pack.name}</h3>
          <p className="muted">
            {pack.functional
              ? "Source linked · demo rules only"
              : "No verified country-specific rules"}
          </p>
        </div>
      </div>
      <p>{pack.rule_description}</p>
      {pack.functional && (
        <>
          <dl>
            <dt>Programme / version</dt>
            <dd>Fictional intake protocol · {pack.version}</dd>
            <dt>Reference checked</dt>
            <dd>
              {pack.reference_date} · source update {pack.source_updated}
            </dd>
            <dt>Applicability</dt>
            <dd>{pack.applicability}</dd>
          </dl>
          <a
            className="text-button"
            href={pack.source_url}
            target="_blank"
            rel="noreferrer"
          >
            Read GOV.UK guidance <ArrowUpRight size={15} />
          </a>
          <p className="callout">{pack.human_review_warning}</p>
        </>
      )}
    </Card>
  );
}

export function InfoTip({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <details className="info-tip">
      <summary aria-label={label}>
        How to read this <span aria-hidden="true">ⓘ</span>
      </summary>
      <div role="note">{children}</div>
    </details>
  );
}
