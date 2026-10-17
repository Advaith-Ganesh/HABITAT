import { useState } from "react";
import { Download } from "lucide-react";
import {
  Card,
  AuditFinding,
  FilterBar,
  PolicyReferenceCard,
} from "../components/ui";
import Chart from "../components/Chart";
import { type Json, pct } from "../lib/types";
export default function AuditPages({
  page,
  fair,
  metrics,
  comparison,
  policies,
  dataset,
  pairs,
  busy,
  runPairs,
  runAudit,
  metadata,
  running,
}: {
  page: string;
  fair?: Json;
  metrics?: Json;
  comparison?: Json;
  policies: Json[];
  dataset?: Json;
  pairs?: Json;
  busy: boolean;
  runPairs: () => void;
  runAudit: () => void;
  metadata?: Json;
  running?: "fair" | "pairs" | null;
}) {
  const [group, setGroup] = useState("all"),
    [pairIndex, setPairIndex] = useState(0);
  const filteredGroups =
    fair?.groups.filter((g: Json) => group === "all" || g.group === group) ??
    [];
  return (
    <>
      {" "}
      {page === "Fairness Lab" && fair && (
        <>
          <div className="callout">
            <b>Fairness is a question we keep testing.</b>
            <p>
              {fair.warning} Selection means additional review, never housing
              selection.
            </p>
          </div>
          <div className="two-col">
            <Card title="Group error rates" tag="FAIRLEARN · HELD-OUT TEST">
              <FilterBar>
                <label className="compact-label">
                  Synthetic group
                  <select
                    aria-label="Filter audit group"
                    value={group}
                    onChange={(e) => setGroup(e.target.value)}
                  >
                    <option value="all">All groups</option>
                    {fair.groups.map((g: Json) => (
                      <option key={g.group}>{g.group}</option>
                    ))}
                  </select>
                </label>
                <button
                  className="secondary"
                  disabled={busy}
                  onClick={runAudit}
                >
                  {running === "fair" ? "Calculating…" : "Run group analysis"}
                </button>
              </FilterBar>
              <Chart kind="fairness" data={filteredGroups} />
            </Card>
            <Card title="Paired audit-attribute test" tag="OUTSIDE TRAINING">
              <div className="big-number">
                {(pairs ?? fair.counterfactual).pairs}
                <small>
                  counterfactual pairs / {(pairs ?? fair.counterfactual).rows}{" "}
                  records
                </small>
              </div>
              <p>
                {(pairs ?? fair.counterfactual).differing_classifications}{" "}
                differing classifications · maximum score difference{" "}
                {(pairs ?? fair.counterfactual).maximum_score_difference}
              </p>
              <p className="muted">{fair.counterfactual.limitation}</p>
              <p className="warning">Identical paired predictions do not establish absence of proxy discrimination.</p>
              <button
                className="primary"
                disabled={busy}
                onClick={() => void runPairs()}
              >
                {running === "pairs"
                  ? "Running…"
                  : `Rerun ${(pairs ?? fair.counterfactual).pairs} paired comparisons`}
              </button>
            </Card>
          </div>
          <Card title="Group-level findings" tag="DESCRIPTIVE · NOT CAUSAL">
            <div className="table-scroll" tabIndex={0} role="region" aria-label="Group-level findings table">
              <table>
                <thead>
                  <tr>
                    <th>Synthetic group</th>
                    <th>n / positive / negative</th>
                    <th>Selection rate</th>
                    <th>Accuracy</th>
                    <th>False positive rate</th>
                    <th>False negative rate</th>
                    <th>Finding</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredGroups.map((g: Json) => (
                    <tr key={g.group}>
                      <td>{g.group}</td>
                      <td>
                        {g.count} / {g.positive_count} / {g.negative_count}
                      </td>
                      <td>{pct(g.selection_rate)}</td>
                      <td>{pct(g.accuracy)}</td>
                      <td>{pct(g.false_positive_rate)}</td>
                      <td>{pct(g.false_negative_rate)}</td>
                      <td>
                        <AuditFinding status={g.status} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="muted">
              A group needs at least{" "}
              {metadata?.fairness_method.minimum_positive_and_negative} positive
              and negative labels. Concern flag: group FNR differs from overall
              by more than{" "}
              {metadata
                ? metadata.fairness_method.fnr_gap_flag * 100
                : "unavailable"}{" "}
              percentage points. No confidence interval or legal fairness
              conclusion is implied.
            </p>
          </Card>
          <Card title="Proxy correlation checks">
            <p>
              Largest absolute Pearson correlation between numeric model inputs
              and one-hot synthetic audit membership:{" "}
              <b>{fair.maximum_absolute_proxy_correlation.toFixed(3)}</b>.
            </p>
            <p className="muted">
              Low pairwise correlation cannot rule out nonlinear or combined
              proxies. Group error-rate differences remain visible above.
            </p>
            <div className="pair-comparison">
              <h3>Inspect a paired comparison</h3>
              <label>
                Example pair
                <select
                  aria-label="Counterfactual example"
                  value={pairIndex}
                  onChange={(e) => setPairIndex(Number(e.target.value))}
                >
                  {(pairs ?? fair.counterfactual).examples.map(
                    (p: Json, i: number) => (
                      <option key={p.pair_id} value={i}>
                        Pair {p.pair_id + 1}
                      </option>
                    ),
                  )}
                </select>
              </label>
              {[(pairs ?? fair.counterfactual).examples[pairIndex]].map(
                (p: Json) =>
                  p && (
                    <div className="pair-grid" key={p.pair_id}>
                      <div>
                        <span>{p.attribute_a}</span>
                        <strong>{pct(p.score_a)}</strong>
                        <small>Estimated review score</small>
                      </div>
                      <div>
                        <span>{p.attribute_b}</span>
                        <strong>{pct(p.score_b)}</strong>
                        <small>Same task-relevant inputs</small>
                      </div>
                    </div>
                  ),
              )}
              <p className="muted">
                {(pairs ?? fair.counterfactual).examples.length} actual example
                pairs are inspectable; summary statistics cover all{" "}
                {(pairs ?? fair.counterfactual).pairs} comparisons. Mean
                absolute score difference:{" "}
                {(pairs ?? fair.counterfactual).average_score_difference}.
              </p>
            </div>
          </Card>
        </>
      )}
      {page === "Policy Packs" && (
        <>
          <div className="callout">
            One project-defined intake framework is functional. The reference guidance
            does not provide a universal local allocation scheme.
          </div>
          <div className="policy-grid">
            {policies.map((p) => (
              <PolicyReferenceCard key={p.id} pack={p} />
            ))}
          </div>
        </>
      )}
      {page === "Dataset Explorer" && dataset && (
        <>
          <div className="stats">
            <div>
              <span>Original records</span>
              <strong>{dataset.records.toLocaleString()}</strong>
              <small>
                {dataset.scenario_families.toLocaleString()} related scenario
                families
              </small>
            </div>
            <div>
              <span>Training / validation / test</span>
              <strong className="smaller">
                {dataset.splits.train.size.toLocaleString()} /{" "}
                {dataset.splits.validation.size} / {dataset.splits.test.size}
              </strong>
              <small>Group-isolated, seed 42</small>
            </div>
            <div>
              <span>Generator version</span>
              <strong>{dataset.version}</strong>
              <small>Deterministic public benchmark</small>
            </div>
            <div>
              <span>Personal records</span>
              <strong>0</strong>
              <small>Entirely synthetic</small>
            </div>
          </div>
          <div className="two-col">
            <Card title="Synthetic class balance" tag="SOURCE LABELS">
              <Chart
                kind="counts"
                data={dataset.class_balance.map((d: Json) => ({
                  name: d.label,
                  count: d.count,
                }))}
              />
            </Card>
            <Card title="Reported housing context" tag="SOURCE DISTRIBUTION">
              <Chart kind="counts" data={dataset.housing_distribution} />
            </Card>
          </div>{" "}
          <Card title="Public dataset" tag="CC0-1.0 SYNTHETIC RECORDS">
            <p>{dataset.provenance}</p>
            <p className="muted">
              Entirely synthetic; not real housing applicants. Labels come from
              a project-defined probabilistic intake protocol. This is a circular
              synthetic benchmark, not external validation.
            </p>
            <a className="primary inline-flex" href="/api/dataset/download">
              <Download size={17} />
              Download 2,000-record CSV
            </a>
            <div className="table-scroll" tabIndex={0} role="region" aria-label="Dataset preview table">
              <table>
                <thead>
                  <tr>
                    {[
                      "Reference",
                      "Scenario",
                      "Housing situation",
                      "Missing evidence",
                      "Completeness",
                      "Synthetic label",
                    ].map((x) => (
                      <th key={x}>{x}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {dataset.preview.map((d: Json) => (
                    <tr key={d.application_id}>
                      <td>{d.application_id}</td>
                      <td>{d.scenario_id}</td>
                      <td>{d.housing_situation}</td>
                      <td>{d.missing_document_count}</td>
                      <td>{d.application_completeness_score}%</td>
                      <td>{d.case_review_required}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
          <Card title="Feature dictionary" tag="SOURCE-BACKED">
            <p className="muted">
              All {dataset.dictionary.length} source columns. Only the model's
              documented allowlist is used for inference.
            </p>
            <div className="dictionary-list">
              {dataset.dictionary.map((d: Json) => (
                <div key={d.feature}>
                  <code>{d.feature}</code>
                  <p>{d.description}</p>
                </div>
              ))}
            </div>
          </Card>
          <Card title="Generator, provenance & reproduction">
            <p>
              Version {dataset.version}, seed {dataset.seed}. Labels use a
              published project-defined probabilistic intake protocol with latent
              ambiguity and limited noise. Related scenario families stay
              together across partitions. Agreement with these labels is partly
              circular and does not validate housing decisions.
            </p>
            <div className="link-row">
              <a className="secondary" href="/api/dataset/card">
                Download dataset card
              </a>
              <a className="secondary" href="/api/dataset/dictionary">
                Download dictionary
              </a>
            </div>
            <pre>bash scripts/reproduce.sh</pre>
            <p className="muted break-all">Source SHA-256: {dataset.sha256}</p>
          </Card>{" "}
        </>
      )}
      {page === "Model Performance" && metrics && comparison && (
        <>
          <div className="callout">
            <b>Model evaluation — held-out test set</b>
            <div className="evaluation-meta">
              <span>Model {metadata?.model_version}</span>
              <span>Test size: {metrics.test_records}</span>
              <span>
                Evaluation verified:{" "}
                {metadata?.evaluation_verified_at
                  ? new Date(
                      metadata.evaluation_verified_at,
                    ).toLocaleDateString("en-GB", { timeZone: "Europe/London" })
                  : "Not verified for current artifacts"}
              </span>
            </div>
            <p className="field-hint">{metadata?.date_note}</p>
            <p>
              One Random Forest trained on {metadata?.training_records} records;
              threshold and uncertainty margin selected using{" "}
              {metadata?.validation_records} validation records. These results
              use {metrics.test_records} held-out records.
            </p>
          </div>
          <div className="stats">
            {["accuracy", "precision", "recall", "f1"].map((k) => (
              <div key={k}>
                <span className="capitalize">{k}</span>
                <strong>{pct(metrics[k])}</strong>
                <small>Random Forest · positive class 1</small>
              </div>
            ))}
          </div>
          <div className="two-col">
            <Card title="Model vs transparent checklist">
              <Chart kind="comparison" data={comparison} />
              <p className="muted">
                The model is not assumed superior. The checklist flags any
                missing evidence, conflict, specialist request, completeness
                below {metadata?.baseline_method.completeness_below}, or unclear
                housing context.
              </p>
            </Card>
            <Card title="Confusion matrix" tag="ACTUAL × PREDICTED">
              <div className="matrix">
                {metrics.confusion_matrix.flatMap((row: number[], i: number) =>
                  row.map((v, j) => (
                    <div
                      key={`${i}-${j}`}
                      className={i === j ? "diagonal" : ""}
                    >
                      <small>
                        {["Routine", "Additional"][i]} →{" "}
                        {["Routine", "Additional"][j]}
                      </small>
                      <strong>{v}</strong>
                    </div>
                  )),
                )}
              </div>
              <p>
                FPR {pct(metrics.false_positive_rate)} · FNR{" "}
                {pct(metrics.false_negative_rate)} · ROC-AUC{" "}
                {metrics.roc_auc.toFixed(3)}
              </p>
              <p>
                Positive support: {metrics.positive_support} /{" "}
                {metrics.test_records}
              </p>
            </Card>
          </div>
          <Card title="Uncertainty and workload trade-off">
            {!metrics.validation_target_met && (
              <div className="warning">
                Validation routing recall target{" "}
                {pct(metrics.validation_routing_recall_target)} was not met. The
                selected maximum uncertainty margin achieved{" "}
                {pct(metrics.validation_routing_recall)}. This safeguard remains
                unresolved.
              </div>
            )}
            <p>
              Classification review rate:{" "}
              <b>{pct(metrics.human_review_rate)}</b>. Routing with uncertain
              cases: <b>{pct(metrics.routing_review_rate)}</b>. Routing recall:{" "}
              <b>{pct(metrics.routing_recall)}</b>.
            </p>
            <p className="muted">
              Routine workflow still requires human handling. These are model
              routing rates, not measured automation savings or service
              outcomes.
            </p>
          </Card>
        </>
      )}
    </>
  );
}
