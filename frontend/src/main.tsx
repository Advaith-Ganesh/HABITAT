import {
  lazy,
  Suspense,
  useCallback,
  useEffect,
  useRef,
  useState,
  type FormEvent,
} from "react";
import { createRoot } from "react-dom/client";
import "@fontsource-variable/inter";
import "./style.css";
import { AppShell, adminPages, applicantPages } from "./components/AppShell";
import {
  AuditHistory,
  Card,
  ConfirmationDialog,
  EmptyState,
  ErrorState,
  HumanReviewPanel,
  MetricCard,
  PageHeader,
  SkeletonLoader,
  InfoTip,
  ToastNotification,
} from "./components/ui";
import {
  ApplicationDetails,
  ApplicationTable,
  Assessment,
  HistoryCard,
  Sandbox,
  statusText,
} from "./components/ReviewWorkspace";
import { api } from "./lib/api";
import { type Json, type CaseRecord, pct } from "./lib/types";
const NewCaseForm = lazy(() => import("./components/NewCaseForm"));
const AuditPages = lazy(() => import("./pages/AuditPages"));
function stored(key: string) {
  try {
    return localStorage.getItem(key) ?? "";
  } catch {
    return "";
  }
}
function route() {
  try {
    const [p, page] = decodeURIComponent(location.hash.slice(1)).split("/");
    const portal = p === "admin" ? "admin" : "applicant";
    return {
      portal,
      page: (portal === "admin" ? adminPages : applicantPages).includes(page)
        ? page
        : portal === "admin"
          ? "Overview"
          : "Apply for Housing",
    };
  } catch {
    return { portal: "applicant", page: "Apply for Housing" };
  }
}
const initial: Json = {
  synthetic_only: true,
  household_size: 2,
  monthly_income: 1500,
  monthly_housing_cost: 600,
  current_bedrooms: 1,
  housing_situation: "stable",
  housing_insecurity_reported: 0,
  missing_document_count: 0,
  income_document_available: 1,
  identity_document_available: 1,
  housing_evidence_available: 1,
  accessibility_support_requested: 0,
  specialist_support_requested: 0,
  conflicting_information: 0,
};
function factualForm(value: Json): Json {
  return Object.fromEntries(Object.keys(initial).map((key) => [key, value[key] ?? initial[key]]));
}
function pendingSubmission(): { key: string; payload: Json } | undefined {
  try {
    const saved = JSON.parse(stored("habitat.v7.pendingSubmission") || "null");
    return saved && typeof saved.key === "string" && saved.payload?.synthetic_only === true ? saved : undefined;
  } catch { return undefined; }
}
function App() {
  const [restoredSubmission] = useState(pendingSubmission);
  const pending = useRef(restoredSubmission);
  const [runningAudit, setRunningAudit] = useState<"fair" | "pairs" | null>(
    null,
  );
  const [view, setView] = useState(route),
    [health, setHealth] = useState<Json>(),
    [overview, setOverview] = useState<Json>(),
    [records, setRecords] = useState<CaseRecord[]>([]),
    [applicantRecords, setApplicantRecords] = useState<CaseRecord[]>([]),
    [audit, setAudit] = useState<Json>(),
    [loading, setLoading] = useState(false);
  const [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [notice, setNotice] = useState(""),
    [refresh, setRefresh] = useState(0),
    [sessionId, setSessionId] = useState(() =>
      stored("habitat.v4.application"),
    ),
    [reference, setReference] = useState(""),
    [selectedId, setSelectedId] = useState(() =>
      stored("habitat.v4.adminCase"),
    );
  const [record, setRecord] = useState<CaseRecord>(),
    [explanation, setExplanation] = useState<Json>(),
    [explanationError, setExplanationError] = useState(""),
    [explanationLoading, setExplanationLoading] = useState(false),
    [reason, setReason] = useState(""),
    [outcome, setOutcome] = useState("routine"),
    [confirm, setConfirm] = useState(false),
    [policyOpen, setPolicyOpen] = useState(false);
  const [form, setForm] = useState<Json>(() => restoredSubmission ? factualForm(restoredSubmission.payload) : { ...initial }),
    [draftExists, setDraftExists] = useState(
      () => !!stored("habitat.v4.draft"),
    );
  const sequence = useRef(0);
  const admin = view.portal === "admin",
    wantedId = admin ? selectedId : sessionId,
    current = record?.id === wantedId ? record : undefined;
  function navigate(page: string, portal = view.portal) {
    location.hash = `${portal}/${encodeURIComponent(page)}`;
    setView({ portal, page });
    setError("");
  }
  useEffect(() => {
    const f = () => {
      if (location.hash !== "#main-content") setView(route());
    };
    window.addEventListener("hashchange", f);
    return () => window.removeEventListener("hashchange", f);
  }, []);
  useEffect(() => {
    const changed = (event: StorageEvent) => {
      if (event.key === "habitat.v5.revision") setRefresh((v) => v + 1);
    };
    const visible = () => {
      if (document.visibilityState === "visible") setRefresh((v) => v + 1);
    };
    window.addEventListener("storage", changed);
    document.addEventListener("visibilitychange", visible);
    return () => {
      window.removeEventListener("storage", changed);
      document.removeEventListener("visibilitychange", visible);
    };
  }, []);
  function announceChange() {
    try {
      localStorage.setItem("habitat.v5.revision", String(Date.now()));
    } catch {
      /* Same-tab refetch still works; other tabs can use Refresh. */
    }
  }
  const invalidateCase = useCallback(() => {
    sequence.current += 1;
  }, []);
  const loadCase = useCallback(
    async (id: string, includeExplanation = true) => {
      const serial = ++sequence.current;
      try {
        const r = await api(`/api/applications/${encodeURIComponent(id)}`);
        if (serial !== sequence.current) return;
        setRecord(r);
        setExplanation(undefined);
        setExplanationError("");
        if (includeExplanation && r.assessment?.score != null) {
          setExplanationLoading(true);
          try {
            const e = await api(
              `/api/applications/${encodeURIComponent(id)}/explanation`,
            );
            if (serial === sequence.current) setExplanation(e);
          } catch (e) {
            if (serial === sequence.current) setExplanationError(String(e));
          } finally {
            if (serial === sequence.current) setExplanationLoading(false);
          }
        } else {
          setExplanationLoading(false);
        }
      } catch (e) {
        if (serial === sequence.current) {
          setRecord(undefined);
          setError(String(e));
        }
      }
    },
    [],
  );
  useEffect(() => {
    let active = true;
    async function load() {
      if (!admin && view.page !== "My Applications") {
        setLoading(false);
        return;
      }
      setLoading(true);
      try {
        if (admin) {
          const [o, r, h] = await Promise.all([
            api("/api/dashboard"),
            api("/api/applications"),
            api("/health").catch(() => ({ model: { ready: false } })),
          ]);
          if (!active) return;
          setOverview(o);
          setRecords(r);
          setHealth(h);
        }
        if (!admin) {
          const r = await api("/api/applicant/applications");
          if (active) setApplicantRecords(r);
        }
        if (admin && view.page === "Fairness & Sandbox") {
          const [fair, metrics, comparison, safeguard, dataset, metadata, investigation] =
            await Promise.all([
              api("/api/fairness/metrics"),
              api("/api/model/metrics"),
              api("/api/model/baseline"),
              api("/api/model/safeguard"),
              api("/api/dataset/metadata"),
              api("/api/model/metadata"),
              api("/api/audit/investigation"),
            ]);
          if (active)
            setAudit({
              fair,
              metrics,
              comparison,
              safeguard,
              dataset,
              metadata,
              investigation,
            });
        }
        if (
          wantedId &&
          ((!admin && view.page === "My Applications") ||
            (admin &&
              ["Applications", "AI Assessment", "Human Review"].includes(
                view.page,
              )))
        )
          await loadCase(wantedId, admin);
      } catch (e) {
        if (active) setError(String(e));
      } finally {
        if (active) setLoading(false);
      }
    }
    void load();
    return () => {
      active = false;
      invalidateCase();
    };
  }, [admin, view.page, wantedId, refresh, loadCase, invalidateCase]);
  function persist(key: string, value: string) {
    try {
      localStorage.setItem(key, value);
    } catch {
      setNotice(
        "Browser storage unavailable; keep your reference before leaving.",
      );
    }
  }
  function choose(id: string, page?: string) {
    setSelectedId(id);
    persist("habitat.v4.adminCase", id);
    setReason("");
    if (page) navigate(page);
    else setRefresh((v) => v + 1);
  }
  function update(key: string, value: any) {
    setForm((previous) => {
      const next = { ...previous, [key]: value };
      next.missing_document_count =
        3 -
        next.income_document_available -
        next.identity_document_available -
        next.housing_evidence_available;
      return next;
    });
  }
  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const previous = pending.current;
      const key = previous && JSON.stringify(factualForm(previous.payload)) === JSON.stringify(factualForm(form)) ? previous.key : crypto.randomUUID();
      const submissionPayload = previous?.key === key ? previous.payload : factualForm(form);
      pending.current = { key, payload: submissionPayload };
      persist("habitat.v7.pendingSubmission", JSON.stringify(pending.current));
      const saved = await api("/api/applications", submissionPayload, { idempotencyKey: key });
      pending.current = undefined;
      try { localStorage.removeItem("habitat.v7.pendingSubmission"); } catch { /* Stored submission remains safe. */ }
      announceChange();
      setSessionId(saved.id);
      setSelectedId(saved.id);
      persist("habitat.v4.application", saved.id);
      persist("habitat.v4.adminCase", saved.id);
      setForm({ ...initial });
      try {
        localStorage.removeItem("habitat.v4.draft");
      } catch {
        /* Stored submission remains safe. */
      }
      setDraftExists(false);
      setNotice(
        "Application submitted. Keep your reference; an administrator will assess it.",
      );
      navigate("My Applications");
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }
  async function assess() {
    if (!current) return;
    setBusy(true);
    setError("");
    try {
      const result = await api(`/api/applications/${current.id}/assess`, {});
      announceChange();
      await loadCase(current.id);
      setRefresh((v) => v + 1);
      setNotice(result.score == null ? "Model inference unavailable. Human review fallback saved." : "Assessment saved using the trained model.");
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }
  async function review() {
    if (!current) return;
    setBusy(true);
    setError("");
    try {
      await api(`/api/reviews/${current.id}/resolve`, { outcome, reason });
      announceChange();
      await loadCase(current.id);
      setReason("");
      setConfirm(false);
      setRefresh((v) => v + 1);
      setNotice("Review action saved. Applicant status updated.");
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }
  async function rerun(kind: "fair" | "pairs") {
    setBusy(true);
    setRunningAudit(kind);
    setError("");
    try {
      const r = await api(
        kind === "fair" ? "/api/fairness/run" : "/api/fairness/counterfactual",
        {},
      );
      setAudit((p) => (p ? { ...p, [kind]: r } : p));
      setNotice("Audit recomputed from the saved model.");
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
      setRunningAudit(null);
    }
  }
  const auditProps = {
    metrics: audit?.metrics,
    running: runningAudit,
    metadata: audit?.metadata,
    fair: audit?.fair,
    comparison: audit?.comparison,
    policies: [],
    dataset: audit?.dataset,
    pairs: audit?.pairs,
    busy,
    runPairs: () => void rerun("pairs"),
    runAudit: () => void rerun("fair"),
  };
  return (
    <AppShell
      portal={view.portal}
      page={view.page}
      navigate={navigate}
      switchPortal={() =>
        navigate(
          admin ? "My Applications" : sessionId ? "Applications" : "Overview",
          admin ? "applicant" : "admin",
        )
      }
      health={health}
    >
      <PageHeader
        title={view.page}
        description={
          admin
            ? "A clearer path from application to accountable human review."
            : "Fairer Housing. Clearer Decisions."
        }
        action={
          view.page !== "Apply for Housing" &&
          view.page !== "Help & Transparency" && (
            <button
              className="secondary"
              disabled={loading || busy}
              onClick={() => {
                setError("");
                setRefresh((v) => v + 1);
              }}
            >
              Refresh {view.page === "My Applications" ? "status" : "data"}
            </button>
          )
        }
      />
      {error && (
        <ErrorState
          message={error}
          retry={() => {
            setError("");
            setRefresh((v) => v + 1);
          }}
        />
      )}
      {loading && !current && <SkeletonLoader />}
      <Suspense fallback={<SkeletonLoader />}>
        {!admin && view.page === "Apply for Housing" && (
          <>
            <section className="product-intro">
              <img src="/habitat-logo.svg" width="48" height="48" alt="" />
              <div>
                <h2>
                  Housing Application Bias, Integrity, Transparency &amp;
                  Accountability Toolkit.
                </h2>
                <p>
                  A clearer application process. Accountable human review. This
                  is a synthetic-data sandbox, not a live housing service.
                </p>
              </div>
            </section>
            <NewCaseForm
              form={form}
              update={update}
              submit={submit}
              busy={busy}
              draftExists={draftExists}
              save={() => {
                try {
                  localStorage.setItem(
                    "habitat.v4.draft",
                    JSON.stringify(form),
                  );
                  setDraftExists(true);
                  setNotice("Draft saved in this browser.");
                } catch {
                  setError("Draft could not be stored.");
                }
              }}
              restore={() => {
                try {
                  setForm(factualForm(JSON.parse(stored("habitat.v4.draft"))));
                  setNotice("Saved draft restored.");
                } catch {
                  setError("Saved draft could not be read.");
                }
              }}
              reset={() => {
                setForm({ ...initial });
                try {
                  localStorage.removeItem("habitat.v4.draft");
                } catch {
                  /* Memory reset succeeds. */
                }
                setDraftExists(false);
                setNotice(
                  "Draft cleared. Submitted applications remain saved.",
                );
              }}
            />
          </>
        )}
        {!admin && view.page === "My Applications" && (
          <>
            <Card title="Applications in this sandbox session">
              <p className="muted">{applicantRecords.length} saved applications. Select a reference to view its current status.</p>
              {applicantRecords.map((r) => (
                <div className="session-application" key={r.id}>
                  <button className="secondary" aria-pressed={sessionId === r.id} onClick={() => {
                    setSessionId(r.id); persist("habitat.v4.application", r.id); setRefresh((v) => v + 1);
                  }}>{r.id}</button>
                  <span>{statusText(r)}</span>
                </div>
              ))}
              <button className="secondary" onClick={() => navigate("Apply for Housing")}>Start another application</button>
            </Card>
            <form
              className="reference-loader"
              onSubmit={(e) => {
                e.preventDefault();
                setError("");
                setSessionId(reference.trim());
                persist("habitat.v4.application", reference.trim());
                setRefresh((v) => v + 1);
              }}
            >
              <label>
                Application reference
                <input
                  aria-label="Application reference"
                  value={reference}
                  placeholder={sessionId || "HAB-XXXXXXXX"}
                  onChange={(e) => setReference(e.target.value)}
                />
              </label>
              <button
                className="secondary"
                disabled={!reference.trim() || loading}
              >
                Load reference
              </button>
            </form>
            {current ? (
              <>
                <Card title="Your application">
                  <ApplicationDetails record={current} />
                  <p className="status-callout" role="status">
                    {statusText(current)}
                  </p>
                  {current.status === "resolved" ? (
                    <p>
                      Your administrative review is complete. This is not a
                      housing approval or allocation.
                    </p>
                  ) : (
                    current.history
                      ?.filter((e) => e.action === "human_override")
                      .at(-1)?.detail.outcome === "request_evidence" && (
                      <div className="callout">
                        <b>A caseworker has requested more information</b>
                        <p>
                          {
                            current.history
                              .filter((e) => e.action === "human_override")
                              .at(-1)?.detail.reason
                          }
                        </p>
                        <p>
                          Contact a caseworker in a real service. This sandbox
                          accepts no document uploads.
                        </p>
                      </div>
                    )
                  )}
                </Card>
                <HistoryCard record={current} />
              </>
            ) : (
              !loading && (
                <EmptyState
                  title="No application loaded"
                  description="Submit an application or enter a saved reference."
                  action={
                    <button
                      className="primary"
                      onClick={() => navigate("Apply for Housing")}
                    >
                      Start application
                    </button>
                  }
                />
              )
            )}
          </>
        )}
        {!admin && view.page === "Help & Transparency" && (
          <div className="help-grid">
            <Card title="About HABITAT AI">
              <p>
                <b>
                  Housing Application Bias, Integrity, Transparency &amp;
                  Accountability Toolkit.
                </b>
              </p>
              <p>
                Our aim is a clearer, inspectable application-review process,
                with people responsible for every housing decision. This project generated
                the original, reproducible dataset of 2,000 synthetic housing
                application records, published openly on GitHub.
              </p>
            </Card>
            <Card title="How it works">
              <ol>
                <li>Submit household details and document declarations.</li>
                <li>An administrator runs an assessment.</li>
                <li>
                  A caseworker records the next action. Refresh My Applications
                  to track it.
                </li>
              </ol>
              <p>No account is needed in this sandbox. Keep your reference.</p>
            </Card>
            <Card title="What the AI does">
              <p>
                One trained Random Forest estimates whether this simulated
                intake needs extra human review. It cannot approve housing or
                decide eligibility. Caseworkers can inspect the explanation and
                override the routing recommendation.
              </p>
              <p>
                Evaluations use generated housing scenarios. Synthetic-label tests
                do not establish real-world usefulness or fairness. Real-world
                validation is not implemented.
              </p>
            </Card>
            <Card title="Documents & privacy">
              <p>
                Document completeness uses three categories: income evidence, identity evidence and
                current housing evidence. The training-time intake completeness feature cannot be derived compatibly from these declarations. New applications require human review without a model score; document completeness remains separate. Declare availability only. Never enter
                real names, government IDs or personal records.
              </p>
              <p>
                This browser stores a sandbox session key and your selected reference. Applications and session associations are saved in SQLite. Clearing browser storage removes access to the session list; keep references to reload cases. References and
                portal switching are not authentication. Production authentication
                is not implemented. Operational use requires authentication,
                role-based access control and privacy safeguards.
              </p>
              <a href="/api/dataset/card">Read the synthetic dataset card</a>
            </Card>
          </div>
        )}
        {admin && view.page === "Overview" && overview && (
          <>
            <div className="stats metric-grid">
              {[
                [
                  "Total saved applications",
                  overview.applications,
                  "Saved in this workspace",
                ],
                [
                  "Awaiting assessment",
                  overview.awaiting_assessment,
                  "Ready for an administrator",
                ],
                [
                  "Human review required",
                  overview.pending_reviews,
                  "Cases in the review queue",
                ],
                [
                  "Completed administrative reviews",
                  overview.resolved_reviews,
                  "Recorded caseworker completions",
                ],
                [
                  "Information requests",
                  overview.information_requests,
                  "Latest action requests more evidence",
                ],
              ].map(([label, value, hint]) => (
                <MetricCard
                  key={label}
                  label={String(label)}
                  value={value}
                  hint={String(hint)}
                />
              ))}
            </div>
            <Card title="Recent activity" tag="ACTUAL DATABASE EVENTS">
              <AuditHistory history={overview.recent_activity} />
            </Card>
            <details className="business-summary">
              <summary>Business model & pilot assumptions</summary>
              <p>
                B2B SaaS for subsidised-housing administrators, housing
                authorities and NGOs. Starter £299/month; institutional
                £999/month. Pricing hypotheses, not sales.
              </p>
              <p>
                Example assumptions: 1,000 cases/month, 20 routine minutes for every case plus 10 additional minutes for 60% of cases, £25/hour, £100 infrastructure and £299 software. Estimated per-case cost = (1000 × (20 + 10 × 0.6)/60 × 25 + 100 + 299) / 1000 = £11.23. No measured savings or customers are claimed.
              </p>
              <p>
                International expansion needs validated country/programme policy
                configuration and local governance.
              </p>
            </details>
          </>
        )}
        {admin && view.page === "Applications" && (
          <Card title="Submitted applications">
            {loading && !records.length ? (
              <p role="status">Loading submitted applications…</p>
            ) : (
              <ApplicationTable records={records} onOpen={(id) => choose(id)} />
            )}
            {current && (
              <div className="selected-details">
                <ApplicationDetails record={current} />
                <button
                  className="primary"
                  onClick={() => navigate("AI Assessment")}
                >
                  Open AI assessment
                </button>
              </div>
            )}
          </Card>
        )}
        {admin && ["AI Assessment", "Human Review"].includes(view.page) && (
          <>
            <Card
              title={
                view.page === "AI Assessment"
                  ? "Select an application"
                  : "Caseworker review queue"
              }
            >
              <label>
                Application
                <select
                  aria-label="Select application"
                  value={selectedId}
                  onChange={(e) => choose(e.target.value)}
                >
                  <option value="">Choose an application</option>
                  {(view.page === "Human Review"
                    ? records.filter(
                        (r) => r.status === "pending" || r.id === selectedId,
                      )
                    : records
                  ).map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.id} · {statusText(r)}
                    </option>
                  ))}
                </select>
              </label>
              {view.page === "Human Review" && (
                <p className="muted">
                  {records.filter((r) => r.status === "pending").length} cases
                  awaiting human review. The selected case stays visible after
                  completion.
                </p>
              )}
              {view.page === "AI Assessment" && (
                <button
                  className="primary assess-button"
                  disabled={!current || busy || current.status === "resolved"}
                  onClick={() => void assess()}
                >
                  {busy
                    ? "Assessing…"
                    : current?.status === "resolved"
                      ? "Review already completed"
                      : "Run AI Assessment"}
                </button>
              )}
            </Card>
            {current ? (
              <>
                <Assessment
                  record={current}
                  explanation={explanation}
                  explanationError={explanationError}
                  explanationLoading={explanationLoading}
                />
                {view.page === "AI Assessment" && (
                  <button
                    className="secondary"
                    disabled={!current.assessment}
                    onClick={() => navigate("Human Review")}
                  >
                    Continue to human review
                  </button>
                )}
                {view.page === "Human Review" && (
                  <HumanReviewPanel
                    record={current}
                    reason={reason}
                    setReason={setReason}
                    outcome={outcome}
                    setOutcome={setOutcome}
                    busy={busy}
                    onResolve={() => setConfirm(true)}
                    onPolicy={() => setPolicyOpen(!policyOpen)}
                  />
                )}
                {policyOpen && view.page === "Human Review" && (
                  <Card title="Policy reference">
                    <p>
                      Intake prompts are project-defined. General English
                      guidance is not a universal local allocation scheme.
                    </p>
                    <a
                      href="https://www.gov.uk/guidance/allocation-of-accommodation-guidance-for-local-authorities"
                      target="_blank"
                      rel="noreferrer"
                    >
                      Read source guidance
                    </a>
                  </Card>
                )}
                <HistoryCard record={current} />
              </>
            ) : (
              !loading && (
                <EmptyState
                  title="Select an application"
                  description="Open a submitted application to begin."
                />
              )
            )}
          </>
        )}
        {admin && view.page === "Fairness & Sandbox" && audit && (
          <>
            <div className="section-label">
              <h2 className="section-heading">Model Performance</h2>
              <InfoTip label="Explain model performance">
                Measured against the preserved held-out synthetic labels, not
                live application outcomes. These numbers stay fixed until the
                model or test data changes.
              </InfoTip>
            </div>
            <AuditPages page="Model Performance" {...auditProps} />
            <Card
              title="Measured uncertainty safeguard"
              tag="HELD-OUT TEST · VALIDATION-SELECTED"
            >
              <p>
                Before any human escalation:{" "}
                {audit.safeguard.before_human_escalation.routing_errors}/
                {audit.safeguard.before_human_escalation.cases} routing errors (
                {pct(
                  audit.safeguard.before_human_escalation.routing_error_rate,
                )}
                ). The table measures errors only among cases remaining in the
                routine route.
              </p>
              <div className="table-scroll" tabIndex={0} role="region" aria-label="Uncertainty safeguard table">
                <table>
                  <thead>
                    <tr>
                      <th>Routing policy</th>
                      <th>Human escalation</th>
                      <th>Remaining routine cases</th>
                      <th>Errors in remaining route</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(["without_uncertainty", "with_uncertainty"] as const).map(
                      (k) => (
                        <tr key={k}>
                          <td>
                            {k === "with_uncertainty"
                              ? "Additional + uncertain"
                              : "Additional class only"}
                          </td>
                          <td>
                            {pct(audit.safeguard[k].human_escalation_rate)} (
                            {audit.safeguard[k].human_escalation_count})
                          </td>
                          <td>{audit.safeguard[k].remaining_routed_count}</td>
                          <td>
                            {audit.safeguard[k].remaining_routing_errors} ·{" "}
                            {pct(
                              audit.safeguard[k].remaining_routing_error_rate,
                            )}
                          </td>
                        </tr>
                      ),
                    )}
                  </tbody>
                </table>
              </div>
              <p>{audit.safeguard.limitation}</p>
              <p>
                More escalation means more workload. The validation recall
                target remains unmet; no test-based threshold changes were made.
              </p>
            </Card>
            <div className="section-label">
              <h2 className="section-heading">Fairness Across Groups</h2>
              <InfoTip label="Explain fairness across groups">
                False positives are extra-review flags on routine labels. False
                negatives are missed extra-review labels. Compare rates
                alongside group counts; small synthetic samples cannot prove
                fairness.
              </InfoTip>
            </div>
            <AuditPages page="Fairness Lab" {...auditProps} />
            {audit.investigation && <Card title="Group routing and case-mix investigation" tag="DESCRIPTIVE · UNCHANGED POLICY">
              <p className="warning">{audit.investigation.warning}</p>
              <p><b>{audit.investigation.paired_warning}</b></p>
              <div className="table-scroll" tabIndex={0} role="region" aria-label="Group routing table"><table><caption>Classification misses and uncertainty escalation</caption><thead><tr><th>Group</th><th>Positive labels / cases</th><th>False negatives</th><th>Uncertain cases</th><th>Extra-review route</th><th>Misses after routing</th></tr></thead><tbody>
                {audit.investigation.groups.map((g: Json) => <tr key={g.group}><td>{g.group}</td><td>{g.positive_count} / {g.count}</td><td>{g.false_negative_count} / {g.positive_count}</td><td>{g.uncertain_count} ({pct(g.uncertain_rate)})</td><td>{g.extra_review_count} ({pct(g.extra_review_rate)})</td><td>{g.routing_missed_positive_count}</td></tr>)}
              </tbody></table></div>
              <details><summary>Inspect differences in case characteristics</summary><div className="table-scroll" tabIndex={0} role="region" aria-label="Group case characteristics table"><table><thead><tr><th>Group</th><th>Mean missing categories</th><th>Mean information completeness</th><th>Unclear housing</th><th>Conflicting details</th><th>Specialist request</th></tr></thead><tbody>
                {audit.investigation.groups.map((g: Json) => <tr key={g.group}><td>{g.group}</td><td>{g.characteristics.mean_missing_categories.toFixed(2)}</td><td>{g.characteristics.mean_information_completeness.toFixed(1)}</td><td>{pct(g.characteristics.unclear_housing_rate)}</td><td>{pct(g.characteristics.conflicting_information_rate)}</td><td>{pct(g.characteristics.specialist_requested_rate)}</td></tr>)}
              </tbody></table></div><p>Observed case mix is not a causal explanation for the error gaps. These routing measurements use the original benchmark policy; live input-range escalation is an additional safeguard.</p></details>
            </Card>}
            <div className="section-label">
              <InfoTip label="Explain application comparisons">
                Two copies of one case change one input. Changing an excluded
                audit label is an invariance check; changing a model input is
                sensitivity, not proof of discrimination. No saved case changes.
              </InfoTip>
            </div>
            <Sandbox records={records} onError={setError} />
            <details className="business-summary">
              <summary>Dataset, training & reproducibility</summary>
              <p>
                {audit.dataset.records} synthetic records;{" "}
                {audit.dataset.splits.train.size}/
                {audit.dataset.splits.validation.size}/
                {audit.dataset.splits.test.size} training/validation/test. One
                saved model; no retraining during this integration. Synthetic-label agreement
                does not prove real-world usefulness.
              </p>
              <div className="link-row">
                <a href="/api/dataset/download">Download CSV</a>
                <a href="/api/dataset/card">Dataset card</a>
                <a href="/api/dataset/dictionary">Feature dictionary</a>
              </div>
            </details>
          </>
        )}
      </Suspense>
      {notice && (
        <ToastNotification message={notice} dismiss={() => setNotice("")} />
      )}
      {confirm && current && (
        <ConfirmationDialog
          title="Save this review action?"
          onCancel={() => setConfirm(false)}
          onConfirm={() => void review()}
          busy={busy}
        >
          <p>
            {current.id} · {outcome.replaceAll("_", " ")}
          </p>
          <p>{reason}</p>
          <p>This updates intake review status, never housing allocation.</p>
        </ConfirmationDialog>
      )}
    </AppShell>
  );
}
createRoot(document.getElementById("root")!).render(<App />);
