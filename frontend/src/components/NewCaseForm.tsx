import { useRef, useState, type FormEvent } from "react";
import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  ClipboardPlus,
  RotateCcw,
  Save,
  ShieldCheck,
} from "lucide-react";
import { Card, ProgressIndicator, ConfirmationDialog } from "./ui";
import { type Json } from "../lib/types";
const labels: Record<string, string> = {
  household_size: "Household members",
  monthly_income: "Monthly household income (£)",
  monthly_housing_cost: "Monthly housing cost (£)",
  current_bedrooms: "Current bedrooms",
  housing_situation: "Housing situation",
  housing_insecurity_reported: "Housing insecurity reported",
  missing_document_count: "Missing document categories",
  income_document_available: "Income evidence available",
  identity_document_available: "Identity evidence available",
  housing_evidence_available: "Housing evidence available",
  accessibility_support_requested: "Accessibility support requested",
  specialist_support_requested: "Specialist review requested",
  conflicting_information: "Information needs clarification",
  application_completeness_score: "Intake information completeness",
};
const steps = [
  "Household",
  "Housing & income",
  "Evidence",
  "Support & clarification",
  "Check & submit",
];
export default function NewCaseForm({
  form,
  update,
  submit,
  busy,
  reset,
  save,
  restore,
  draftExists,
}: {
  form: Json;
  update: (key: string, value: any) => void;
  submit: (e: FormEvent) => void;
  busy: boolean;
  reset: () => void;
  save: () => void;
  restore: () => void;
  draftExists: boolean;
}) {
  const [validationError, setValidationError] = useState(""),
    [invalidId, setInvalidId] = useState("");
  const [step, setStep] = useState(0),
    [confirmReset, setConfirmReset] = useState(false);
  const ref = useRef<HTMLFormElement>(null);
  function move(next: number) {
    if (next < step || ref.current?.reportValidity()) setStep(next);
  }
  const number = (
    key: string,
    label: string,
    min: number,
    max: number,
    hint: string,
    integer = false,
  ) => (
    <label key={key}>
      {label}
      <input
        required
        type="number"
        id={key}
        aria-label={label}
        aria-describedby={`${key}-help${invalidId === key ? " form-validation" : ""}`}
        aria-invalid={invalidId === key || undefined}
        min={min}
        max={max}
        step={integer ? 1 : "any"}
        value={form[key]}
        onChange={(e) =>
          update(key, e.target.value === "" ? "" : Number(e.target.value))
        }
      />
      <small className="field-hint" id={`${key}-help`}>
        {hint}
      </small>
    </label>
  );
  const checkbox = (key: string, label: string, hint?: string) => (
    <label className="checkbox" key={key}>
      <input
        type="checkbox"
        aria-label={label}
        aria-describedby={hint ? `${key}-help` : undefined}
        checked={!!form[key]}
        onChange={(e) => update(key, e.target.checked ? 1 : 0)}
      />
      <span>
        {label}
        {hint && <small id={`${key}-help`}>{hint}</small>}
      </span>
    </label>
  );
  return (
    <>
      <ProgressIndicator steps={steps} current={step} onStep={move} />
      <div className="form-layout">
        <form
          ref={ref}
          onInvalid={(e) => { const field = e.target as HTMLInputElement; setInvalidId(field.id); setValidationError(`${field.getAttribute("aria-label") || "Confirmation"}: ${field.validationMessage}`); }}
          onChange={() => { setValidationError(""); setInvalidId(""); }}
          onSubmit={(e) => {
            e.preventDefault();
            if (step < 4) move(step + 1);
            else submit(e);
          }}
        >
          <Card title={steps[step]} tag={`SECTION ${step + 1} OF 5`}>
            {validationError && <p id="form-validation" className="warning" role="alert">{validationError}</p>}
            {step === 0 && (
              <>
                <p className="muted">
                  Tell us about your household. No names, addresses or
                  identity numbers.
                </p>
                <div className="form-grid">
                  {number(
                    "household_size",
                    "Household members",
                    1,
                    20,
                    "Number of people in the household.",
                    true,
                  )}
                  {number(
                    "current_bedrooms",
                    "Current bedrooms",
                    0,
                    20,
                    "Context only; this is not a statutory overcrowding check.",
                    true,
                  )}
                </div>
              </>
            )}
            {step === 1 && (
              <>
                <div className="form-grid">
                  {number(
                    "monthly_income",
                    "Monthly income (£)",
                    0,
                    100000,
                    "Monthly household income before deductions.",
                  )}
                  {number(
                    "monthly_housing_cost",
                    "Monthly housing cost (£)",
                    0,
                    100000,
                    "Monthly housing cost in GBP.",
                  )}
                </div>
                <label>
                  Housing situation
                  <select
                    value={form.housing_situation}
                    onChange={(e) =>
                      update("housing_situation", e.target.value)
                    }
                  >
                    <option value="stable">Stable</option>
                    <option value="temporary">Temporary</option>
                    <option value="unclear">Unclear</option>
                  </select>
                </label>
                {checkbox(
                  "housing_insecurity_reported",
                  "Housing insecurity reported",
                )}
              </>
            )}
            {step === 2 && (
              <>
                <p className="muted">
                  Evidence availability influences intake routing. Missing
                  evidence never means an applicant is rejected.
                </p>
                {checkbox(
                  "income_document_available",
                  "Income evidence available",
                )}
                {checkbox(
                  "identity_document_available",
                  "Identity evidence available",
                )}
                {checkbox(
                  "housing_evidence_available",
                  "Housing evidence available",
                )}
                <div className="evidence-summary">
                  <CheckCircle2 size={18} />
                  {3 - form.missing_document_count} of 3 evidence types
                  available<span>{form.missing_document_count} missing</span>
                </div>
                <p className="muted">
                  Documentation completeness:{" "}
                  {(((3 - form.missing_document_count) / 3) * 100).toFixed(1)}%.
                  Calculated from the three declarations above. No files are
                  uploaded.
                </p>
              </>
            )}
            {step === 3 && (
              <>
                {number("application_completeness_score", "Intake information completeness", 0, 100,
                  "Synthetic estimate of completeness and clarity across all intake information. Separate from the document percentage. A real service needs a validated caseworker measurement protocol.")}

                {checkbox(
                  "conflicting_information",
                  "Information needs clarification",
                  "Flag any conflicting details for a caseworker.",
                )}
                {checkbox(
                  "specialist_support_requested",
                  "Specialist review requested",
                  "Ask for a specialist to review this application.",
                )}
                {checkbox(
                  "accessibility_support_requested",
                  "Accessibility support requested",
                  "Excluded from the model; never treated as a disadvantage.",
                )}
              </>
            )}
            {step === 4 && (
              <>
                <div className="callout">
                  <ShieldCheck size={17} />
                  <b>Ready for human-led assessment</b>
                  <p>
                    The model recommends an intake workflow. It cannot approve
                    housing, reject an applicant or decide eligibility.
                  </p>
                </div>
                <div className="key-values">
                  {Object.entries(form)
                    .filter(([key]) => key !== "synthetic_only")
                    .map(([key, value]) => (
                      <div key={key}>
                        <span>{labels[key] ?? key}</span>
                        <b>
                          {key === "application_completeness_score"
                            ? `${Number(value).toFixed(1)}%`
                            : key.endsWith("_available") ||
                                key.endsWith("_requested") ||
                                [
                                  "conflicting_information",
                                  "housing_insecurity_reported",
                                ].includes(key)
                              ? value
                                ? "Yes"
                                : "No"
                              : String(value)}
                        </b>
                      </div>
                    ))}
                </div>
                <label className="checkbox consent">
                  <input required id="synthetic-consent" aria-invalid={invalidId === "synthetic-consent" || undefined} aria-describedby={invalidId === "synthetic-consent" ? "form-validation" : undefined} type="checkbox" />I confirm all values are
                  synthetic.
                </label>
              </>
            )}
            <div className="form-actions">
              <button
                type="button"
                className="secondary"
                disabled={step === 0 || busy}
                onClick={() => setStep(step - 1)}
              >
                <ArrowLeft size={15} />
                Back
              </button>
              <button className="primary" type="submit" disabled={busy}>
                {busy
                  ? "Submitting…"
                  : step === 4
                    ? "Submit application"
                    : "Continue"}
                {step === 4 ? (
                  <ClipboardPlus size={16} />
                ) : (
                  <ArrowRight size={16} />
                )}
              </button>
            </div>
          </Card>
        </form>
        <aside className="form-aside">
          <Card title="Your working draft" tag="LOCAL ONLY">
            <p className="muted">
              Save synthetic values in this browser to continue later. Drafts are not
              submitted to the API.
            </p>
            <button
              className="secondary full-width"
              onClick={save}
              disabled={busy}
            >
              <Save size={15} />
              Save draft
            </button>
            {draftExists && (
              <button
                className="text-button"
                onClick={() => {
                  restore();
                  setStep(0);
                }}
              >
                Restore saved draft
              </button>
            )}
            <button
              className="text-button danger-text"
              disabled={busy}
              onClick={() => setConfirmReset(true)}
            >
              <RotateCcw size={14} />
              Reset form & remove draft
            </button>
          </Card>
          <div className="form-help">
            <ShieldCheck size={22} />
            <h3>People, before predictions.</h3>
            <p>
              All cases remain human-led. Borderline or unavailable predictions
              are routed for additional human review.
            </p>
            <p>
              Submitted cases and review actions persist in the local sandbox
              database.
            </p>
          </div>
        </aside>
      </div>
      {confirmReset && (
        <ConfirmationDialog
          title="Reset application draft?"
          confirmLabel="Reset form"
          onCancel={() => setConfirmReset(false)}
          onConfirm={() => {
            reset();
            setStep(0);
            setConfirmReset(false);
          }}
          busy={false}
        >
          <p>
            This clears the form and this browser’s saved draft. Submitted
            applications remain in the workspace.
          </p>
        </ConfirmationDialog>
      )}
    </>
  );
}
