import {
  Activity,
  ArrowRight,
  ArrowUpRight,
  ClipboardCheck,
  Files,
  ShieldCheck,
  Users,
} from "lucide-react";
import { Card, MetricCard, DataTable, AuditFinding } from "../components/ui";
import Chart from "../components/Chart";
import { type Json, pct, humanize } from "../lib/types";
export default function OverviewPage({
  overview: o,
  fair,
  navigate,
  onOpen,
}: {
  overview: Json;
  fair?: Json;
  navigate: (p: string) => void;
  onOpen: (id: string) => void;
}) {
  const metrics = o.metrics;
  const concerns = fair?.groups.filter(
    (g: Json) => g.status === "Potential concern",
  ).length;
  return (
    <>
      <div className="overview-banner">
        <div className="banner-icon">
          <ShieldCheck size={23} />
        </div>
        <div>
          <b>Decision support with a clear line of accountability.</b>
          <p>
            Real model reasoning. Visible limitations. Every housing decision
            stays with a qualified human.
          </p>
        </div>
        <button
          className="text-button"
          onClick={() => navigate("Model Performance")}
        >
          Inspect the evidence <ArrowUpRight size={15} />
        </button>
      </div>
      <div className="stats">
        <MetricCard
          label="Synthetic applications"
          value={o.applications}
          hint="Saved in this local workspace"
          icon={<Files size={18} />}
        />
        <MetricCard
          label="Additional-review class"
          value={o.additional_review_classifications}
          hint="Model classification · not allocation"
          icon={<Activity size={18} />}
        />
        <MetricCard
          label="Human review queue"
          value={o.pending_reviews}
          hint={`${o.uncertain_cases} assessed cases flagged uncertain`}
          icon={<Users size={18} />}
          tone="amber"
        />
        <MetricCard
          label="Completed human reviews"
          value={o.resolved_reviews}
          hint={`${o.routine_reviews} cases in routine workflow`}
          icon={<ClipboardCheck size={18} />}
          tone="teal"
        />
      </div>
      <div className="overview-main">
        <Card title="Review classification" tag="WORKSPACE CASES">
          <Chart kind="distribution" data={o.classification_distribution} />
          <p className="muted">
            Additional review is an intake route, never a housing-selection
            decision.
          </p>
        </Card>
        <Card
          title="Model evaluation"
          tag={`${metrics.test_records} HELD-OUT RECORDS`}
        >
          <div className="performance-tiles">
            {["accuracy", "precision", "recall", "f1"].map((key) => (
              <div key={key}>
                <span>{key === "f1" ? "F1 score" : key}</span>
                <strong>{pct(metrics[key])}</strong>
                <div className="micro-bar">
                  <span style={{ width: pct(metrics[key]) }} />
                </div>
              </div>
            ))}
          </div>
          <div className="card-note">
            <ShieldCheck size={15} />
            <span>Synthetic-label agreement, not real-world validation.</span>
          </div>
          <button
            className="text-button"
            onClick={() => navigate("Model Performance")}
          >
            Compare with the checklist <ArrowRight size={14} />
          </button>
        </Card>
        <Card title="Audit status" tag="NO UNIVERSAL FAIRNESS CLAIM">
          <div className="audit-count">
            <strong>{concerns ?? "—"}</strong>
            <span>
              synthetic groups with
              <br />a potential concern
            </span>
          </div>
          <AuditFinding
            status={
              metrics.validation_target_met
                ? "No concern detected in this test"
                : "Potential concern"
            }
          >
            Validation routing recall {pct(metrics.validation_routing_recall)}{" "}
            against target {pct(metrics.validation_routing_recall_target)}.{" "}
            {metrics.validation_target_met
              ? "Target met on synthetic validation only."
              : "Target was not met."}
          </AuditFinding>
          <p className="muted">
            {fair
              ? `Observed FNR gap: ${(fair.disparities.false_negative_rate * 100).toFixed(1)} percentage points.`
              : "Loading group audit…"}
          </p>
          <button
            className="text-button"
            onClick={() => navigate("Fairness Lab")}
          >
            Open fairness laboratory <ArrowUpRight size={14} />
          </button>
        </Card>
      </div>
      <div className="two-col activity-row">
        <Card title="Recorded workspace activity" tag="APPEND-ONLY EVENTS">
          <Chart kind="activity" data={o.activity_distribution} />
          <p className="muted">
            Actual event counts by UTC calendar date. A single-day demo may show
            one point.
          </p>
        </Card>
        <Card title="Recent review activity" tag="LOCAL SQLITE">
          {o.recent_activity.map((e: Json, i: number) => (
            <div className="activity-item" key={i}>
              <span className="activity-icon">
                <ShieldCheck size={15} />
              </span>
              <div>
                <button
                  className="case-link"
                  onClick={() => onOpen(e.application_id)}
                >
                  {e.application_id}
                </button>
                <small>
                  {humanize(e.action)}
                  {e.detail.outcome ? ` · ${humanize(e.detail.outcome)}` : ""}
                </small>
              </div>
              <time dateTime={e.timestamp}>
                {new Date(e.timestamp).toLocaleTimeString("en-GB", {
                  timeZone: "Europe/London",
                  hour: "2-digit",
                  minute: "2-digit",
                })}{" "}
                UK
              </time>
            </div>
          ))}
        </Card>
      </div>
      <Card title="Recent applications" tag="LIVE CASE REGISTER">
        <DataTable rows={o.recent} onOpen={onOpen} paginate={false} />
        <button
          className="text-button"
          onClick={() => navigate("Applications")}
        >
          View application register <ArrowRight size={15} />
        </button>
      </Card>
    </>
  );
}
