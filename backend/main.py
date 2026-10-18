import json
import os
import uuid
import hashlib
from starlette.requests import Request
from starlette.concurrency import run_in_threadpool
from functools import lru_cache
from datetime import datetime, timezone
from typing import Any, Literal
from contextlib import asynccontextmanager
import pandas as pd
from fastapi import FastAPI, HTTPException, Header, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import create_engine, Column, String, Text, ForeignKey, event, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, sessionmaker
from ml.common import ROOT, EVALUATION_INPUTS
from ml.predict import predict, artifacts
from ml.explain import explain
from backend.policy import load_policy

sandbox_folder = ROOT / ".test-runtime"
sandbox_folder.mkdir(mode=0o700, exist_ok=True)

engine = create_engine(
    os.getenv("HABITAT_DATABASE_URL", f"sqlite:///{sandbox_folder/'sandbox.db'}"),
    connect_args={"check_same_thread": False, "timeout": 15},
)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Application(Base):
    __tablename__ = "applications"
    id = Column(String, primary_key=True)
    payload = Column(Text, nullable=False)
    assessment = Column(Text)
    status = Column(String, nullable=False, default="unassessed")


class ApplicantSessionApplication(Base):
    __tablename__ = "applicant_session_applications"
    application_id = Column(String, ForeignKey("applications.id"), primary_key=True)
    session_id = Column(String, nullable=False, index=True)


class SubmissionRequest(Base):
    __tablename__ = "submission_requests"
    key_hash = Column(String, primary_key=True)
    payload_hash = Column(String, nullable=False)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)


class EvidenceDocument(Base):
    __tablename__ = "evidence_documents"
    id = Column(String, primary_key=True)
    session_id = Column(String, nullable=False, index=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=True, index=True)
    analysis = Column(Text, nullable=False)
    sha256 = Column(String, nullable=False)
    created_at = Column(String, nullable=False)


class Event(Base):
    __tablename__ = "events"
    id = Column(String, primary_key=True)
    application_id = Column(String, ForeignKey("applications.id"), nullable=False)
    timestamp = Column(String, nullable=False)
    action = Column(String, nullable=False)
    detail = Column(Text, nullable=False)


@event.listens_for(engine, "connect")
def sqlite_config(connection, record):
    connection.execute("PRAGMA foreign_keys=ON")


def log(db, aid, action, detail):
    db.add(
        Event(
            id=str(uuid.uuid4()),
            application_id=aid,
            timestamp=datetime.now(timezone.utc).isoformat(),
            action=action,
            detail=json.dumps(detail),
        )
    )


def init():
    Base.metadata.create_all(engine)
    database_file = engine.url.database
    if os.name == "posix" and database_file and database_file != ":memory:":
        os.chmod(database_file, 0o600)
    with engine.begin() as conn:
        for verb in ["UPDATE", "DELETE"]:
            conn.exec_driver_sql(
                f"CREATE TRIGGER IF NOT EXISTS events_no_{verb.lower()} BEFORE {verb} ON events BEGIN SELECT RAISE(ABORT, 'Append-only event history'); END"
            )
    with Session() as db:
        if not db.query(Application).first():
            # Separate hand-authored UI scenarios. Never seed from evaluation data.
            for row in json.loads((ROOT / "data/demo/applications.json").read_text()):
                payload = Case.model_validate(row["payload"]).model_dump()
                aid = row["id"]
                assessment = predict(payload)
                assessment.update(model_version="rf-1.0", assessed_at=datetime.now(timezone.utc).isoformat())
                db.add(Application(id=aid, payload=json.dumps(payload), assessment=json.dumps(assessment),
                                   status="pending" if assessment["requires_review"] else "routine"))
                db.flush()
                log(db, aid, "seeded", {"provenance": "Independent hand-authored sandbox scenario", "scenario": row["scenario"]})
                log(db, aid, "assessed", assessment)
            db.commit()


@asynccontextmanager
async def lifespan(app):
    init()
    yield


app = FastAPI(title="HABITAT AI Sandbox", version="7.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Sandbox-Session", "Idempotency-Key"],
    expose_headers=["Idempotency-Replayed"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "[::1]", "testserver"])


@lru_cache(maxsize=1)
def model_fingerprint():
    return hashlib.sha256(
        (ROOT / "models/habitat_review_model.joblib").read_bytes()
    ).hexdigest()


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Cache-Control"] = (
        "no-store" if request.url.path.startswith("/api") else "no-cache"
    )
    if request.url.path in {"/", "/index.html"}:
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'"
        )
    return response


@app.exception_handler(SQLAlchemyError)
async def database_failure(request, exc):
    return JSONResponse(
        status_code=503,
        content={
            "detail": "Local storage unavailable. No successful review has been confirmed; retry or refer to a human."
        },
        headers={"Retry-After": "5"},
    )


SAFEGUARD_FIELDS = {"safe_to_stay_tonight", "evidence_help_needed", "evidence_ids"}
EVIDENCE_KEYS = {"income": "income_document_available", "identity": "identity_document_available", "housing": "housing_evidence_available"}


class Case(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    synthetic_only: Literal[True] = True
    household_size: int = Field(default=2, ge=1, le=20)
    monthly_income: float = Field(default=1500, ge=0, le=100000)
    monthly_housing_cost: float = Field(default=600, ge=0, le=100000)
    current_bedrooms: int = Field(default=1, ge=0, le=20)
    housing_situation: Literal["stable", "temporary", "unclear"] = "stable"
    housing_insecurity_reported: Literal[0, 1] = 0
    missing_document_count: int = Field(default=0, ge=0, le=3)
    income_document_available: Literal[0, 1] = 1
    identity_document_available: Literal[0, 1] = 1
    housing_evidence_available: Literal[0, 1] = 1
    accessibility_support_requested: Literal[0, 1] = 0
    specialist_support_requested: Literal[0, 1] = 0
    conflicting_information: Literal[0, 1] = 0
    application_completeness_score: float | None = Field(default=None, ge=0, le=100, description="Historical model input. Ignored on new submissions; cannot be derived compatibly from applicant declarations.")

    evidence_ids: list[str] = Field(default_factory=list, max_length=3)

    # Non-model declarations: never inferred from the Random Forest score.
    safe_to_stay_tonight: Literal["yes", "no", "unsure"] | None = None
    evidence_help_needed: list[Literal["income", "identity", "housing"]] = Field(default_factory=list)

    @model_validator(mode="after")
    def consistent_documents(self):
        if (
            self.missing_document_count
            != 3
            - self.income_document_available
            - self.identity_document_available
            - self.housing_evidence_available
        ):
            raise ValueError(
                "Missing-document count must agree with the three evidence flags"
            )
        if len(set(self.evidence_ids)) != len(self.evidence_ids):
            raise ValueError("Evidence document IDs must be unique")
        if len(set(self.evidence_help_needed)) != len(self.evidence_help_needed):
            raise ValueError("Evidence help requests must be unique")
        if any(getattr(self, EVIDENCE_KEYS[k]) != 0 for k in self.evidence_help_needed):
            raise ValueError("Evidence needing help must be declared unavailable")
        return self


class Submission(Case):
    @model_validator(mode="before")
    @classmethod
    def require_intake_fields(cls, values):
        required = set(Case.model_fields) - {"application_completeness_score"} - SAFEGUARD_FIELDS
        missing = required - set(values) if isinstance(values, dict) else required
        if missing:
            raise ValueError("Required submission fields missing: " + ", ".join(sorted(missing)))
        return values


def assess_record(payload):
    # The trained feature contains unobserved generator noise. Never substitute
    # document percentages, an applicant guess, or the fitted imputer for it.
    if payload.get("application_completeness_score") is None:
        return {
            "score": None, "classification": None, "category": "Human review fallback",
            "uncertain": True, "requires_review": True,
            "failure": "InputCompatibilityUnavailable",
            "limitations": "Calculated intake completeness is unavailable: the training feature cannot be derived compatibly from submitted declarations. Human review is required; no model prediction or SHAP has been produced.",
            "input_validation": {"out_of_distribution": True, "imputed_features": [],
                "warnings": ["Training-time intake completeness is unavailable; feature compatibility is not established."],
                "scope": "No replacement value or model imputation is used for new applications."},
        }
    return predict(payload)


def sandbox_session(value):
    if value is None:
        return None
    try:
        return str(uuid.UUID(value))
    except (ValueError, AttributeError):
        raise HTTPException(422, "Sandbox session must be a UUID")


class Resolution(BaseModel):
    model_config = ConfigDict(extra="forbid")
    outcome: Literal["routine", "additional_review", "request_evidence", "escalate"]
    reason: str = Field(min_length=8, max_length=1000)

    @model_validator(mode="after")
    def reason_present(self):
        if len(self.reason.strip()) < 8:
            raise ValueError("Provide a meaningful review reason")
        return self


class PairRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    attribute: Literal["synthetic_audit_group"] = "synthetic_audit_group"


class EventResponse(BaseModel):
    timestamp: str
    action: str
    detail: dict[str, Any]


class CaseResponse(BaseModel):
    id: str
    payload: Case
    assessment: dict[str, Any] | None
    status: Literal["unassessed", "pending", "routine", "resolved"]
    provenance: str
    history: list[EventResponse] | None = None
    documents: dict[str, Any]
    latest_review: dict[str, Any] | None = None


DOCUMENT_REQUIREMENTS = {
    "income_document_available": "Income evidence",
    "identity_document_available": "Identity evidence",
    "housing_evidence_available": "Current housing evidence",
}


def document_summary(payload):
    present = [
        label for key, label in DOCUMENT_REQUIREMENTS.items() if payload[key] == 1
    ]
    missing = [
        label for key, label in DOCUMENT_REQUIREMENTS.items() if payload[key] != 1
    ]
    return {
        "required": len(DOCUMENT_REQUIREMENTS),
        "present_count": len(present),
        "percentage": 100 * len(present) / len(DOCUMENT_REQUIREMENTS),
        "present": present,
        "missing": missing,
        "help_needed": [DOCUMENT_REQUIREMENTS[EVIDENCE_KEYS[k]] for k in payload.get("evidence_help_needed", [])],
        "verification_status": "Not verified; human verification required for all declared evidence.",
        "basis": "Three document categories in the project-defined intake framework; declarations only, no uploads or legal sufficiency checks.",
    }


class SandboxComparison(BaseModel):
    model_config = ConfigDict(extra="forbid")
    application_id: str
    field: Literal["synthetic_audit_group", "conflicting_information"]
    value: str | int

    @model_validator(mode="after")
    def valid_change(self):
        if self.field == "synthetic_audit_group" and self.value not in [
            "Audit A",
            "Audit B",
            "Audit C",
        ]:
            raise ValueError("Choose a synthetic audit group")
        if self.field == "conflicting_information" and (
            type(self.value) is not int or self.value not in [0, 1]
        ):
            raise ValueError("Conflicting information must be 0 or 1")
        return self


def report(name):
    return json.loads((ROOT / f"reports/{name}.json").read_text())


def latest_reviews(db):
    result = {}
    for e in (
        db.query(Event)
        .filter_by(action="human_override")
        .order_by(Event.timestamp, Event.id)
    ):
        result[e.application_id] = {"timestamp": e.timestamp, **json.loads(e.detail)}
    return result


def serialize(a, review=None):
    return {
        "id": a.id,
        "payload": json.loads(a.payload),
        "assessment": json.loads(a.assessment) if a.assessment else None,
        "status": a.status,
        "documents": document_summary(json.loads(a.payload)),
        "latest_review": review,
        "provenance": "Entirely synthetic; not real housing applicants",
    }


def require(db, aid):
    a = db.get(Application, aid)
    if not a:
        raise HTTPException(404, "Synthetic application not found")
    return a


@app.get("/health")
def health():
    try:
        pipe, cfg = artifacts()
        ready = hasattr(pipe["classifier"], "estimators_")
        with Session() as db:
            db.connection().exec_driver_sql("SELECT 1")
        return {
            "status": "ok" if ready else "degraded",
            "sandbox": True,
            "model": {
                "ready": ready,
                "version": "rf-1.0",
                "trees": len(pipe["classifier"].estimators_),
                "training_records": cfg["training_records"],
            },
            "database": "available",
            "application_version": "7.0.0",
        }
    except (
        OSError,
        EOFError,
        KeyError,
        TypeError,
        AttributeError,
        ValueError,
        RuntimeError,
        SQLAlchemyError,
    ):
        return JSONResponse(
            status_code=503,
            content={
                "status": "degraded",
                "sandbox": True,
                "model": {"ready": False},
                "detail": "Service check failed; use human review.",
            },
        )


@app.get("/api/model/metrics")
def metrics():
    return report("evaluation")


@app.get("/api/model/baseline")
def comparison():
    return report("model_comparison")


@app.get("/api/model/metadata")
def model_metadata():
    pipe, cfg = artifacts()
    paths = EVALUATION_INPUTS
    hashes = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}
    verification = ROOT / "reports/evaluation_verification.json"
    try:
        recorded = json.loads(verification.read_text())
    except (OSError, ValueError):
        recorded = {}
    verified = recorded.get("artifact_hashes") == hashes
    return {
        "model_version": "rf-1.0",
        "classifier": type(pipe["classifier"]).__name__,
        "trees": len(pipe["classifier"].estimators_),
        "training_records": cfg["training_records"],
        "validation_records": len(pd.read_csv(ROOT / "data/splits/validation.csv")),
        "test_records": len(pd.read_csv(ROOT / "data/splits/test.csv")),
        "threshold": cfg["threshold"],
        "uncertainty_margin": cfg["uncertainty_margin"],
        "verification_status": (
            "verified" if verified else "not_verified_for_current_artifacts"
        ),
        "evaluation_verified_at": recorded.get("verified_at") if verified else None,
        "date_note": "Date of read-only metric recomputation. Original evaluation creation date was not recorded.",
        "artifact_hashes": hashes,
        "fairness_method": {"minimum_positive_and_negative": 20, "fnr_gap_flag": 0.1},
        "baseline_method": {"completeness_below": 70, "missing_evidence_at_least": 1},
    }


@app.get("/api/audit/investigation")
def audit_investigation():
    from ml.audit_v7 import investigate
    return investigate()


@app.get("/api/model/safeguard")
def safeguard():
    from ml.safeguard import measure

    return measure()


@app.post("/api/sandbox/compare")
def sandbox_compare(body: SandboxComparison):
    with Session() as db:
        record = require(db, body.application_id)
        before = json.loads(record.payload)
    # The audit attribute is not an input; add it solely for this comparison.
    if body.field == "synthetic_audit_group":
        before[body.field] = "Audit A"
    after = {**before, body.field: body.value}
    valid_before = Case.model_validate(
        {k: v for k, v in before.items() if k in Case.model_fields}
    )
    valid_after = Case.model_validate(
        {k: v for k, v in after.items() if k in Case.model_fields}
    )
    results = []
    for payload, validated in [(before, valid_before), (after, valid_after)]:
        prediction = assess_record(payload)
        explanation_result = None
        if prediction["score"] is not None:
            try:
                explanation_result = explain(validated.model_dump())
            except (
                ValueError,
                KeyError,
                TypeError,
                AttributeError,
                OSError,
                EOFError,
                RuntimeError,
            ):
                pass
        results.append({"prediction": prediction, "explanation": explanation_result})
    return {
        "application_id": body.application_id,
        "field": body.field,
        "before_value": before[body.field],
        "after_value": after[body.field],
        "changed": before[body.field] != after[body.field],
        "before": results[0],
        "after": results[1],
        "saved_application_modified": False,
        "limitation": (
            "Audit group is excluded from inference. Identical scores do not establish absence of proxy bias."
            if body.field == "synthetic_audit_group"
            else "Conflicting information is a genuine model input. A changed score is a sensitivity demonstration, not evidence of discrimination or causation."
        ),
    }


@app.get("/api/fairness/metrics")
def fairness():
    return report("fairness")


@app.post("/api/fairness/run")
def run_fairness():
    from ml.evaluate import fairness_audit

    return fairness_audit()


@app.post("/api/fairness/counterfactual")
def pairs(body: PairRequest):
    from ml.evaluate import counterfactual

    return counterfactual()


@app.get("/api/dashboard")
def dashboard():
    with Session() as db:
        rows = db.query(Application).all()
        timestamps = dict(
            db.query(Event.application_id, func.min(Event.timestamp))
            .group_by(Event.application_id)
            .all()
        )
        latest_review = {}
        for e in (
            db.query(Event).filter_by(action="human_override").order_by(Event.timestamp)
        ):
            latest_review[e.application_id] = json.loads(e.detail).get("outcome")
        return {
            "applications": len(rows),
            "pending_reviews": sum(a.status == "pending" for a in rows),
            "resolved_reviews": sum(a.status == "resolved" for a in rows),
            "awaiting_assessment": sum(a.status == "unassessed" for a in rows),
            "information_requests": sum(
                a.status == "pending" and latest_review.get(a.id) == "request_evidence"
                for a in rows
            ),
            "metrics": metrics(),
            "routine_reviews": sum(a.status == "routine" for a in rows),
            "additional_review_classifications": sum(
                json.loads(a.assessment).get("classification") == 1
                for a in rows
                if a.assessment
            ),
            "uncertain_cases": sum(
                bool(json.loads(a.assessment).get("uncertain"))
                for a in rows
                if a.assessment
            ),
            "classification_distribution": [
                {
                    "name": label,
                    "count": sum(
                        json.loads(a.assessment).get("classification") == value
                        for a in rows
                        if a.assessment
                    ),
                }
                for value, label in [(0, "Routine"), (1, "Additional")]
            ]
            + [
                {
                    "name": "Unassessed / unavailable",
                    "count": sum(
                        not a.assessment
                        or json.loads(a.assessment).get("classification") is None
                        for a in rows
                    ),
                }
            ],
            "recent": [
                serialize(a)
                for a in sorted(
                    rows, key=lambda a: timestamps.get(a.id, ""), reverse=True
                )[:6]
            ],
            "recent_activity": [
                {
                    "application_id": e.application_id,
                    "action": e.action,
                    "timestamp": e.timestamp,
                    "detail": json.loads(e.detail),
                }
                for e in db.query(Event).order_by(Event.timestamp.desc()).limit(6)
            ],
            "activity_distribution": [
                {"date": day, "events": count}
                for day, count in db.query(
                    func.substr(Event.timestamp, 1, 10), func.count(Event.id)
                )
                .group_by(func.substr(Event.timestamp, 1, 10))
                .order_by(func.substr(Event.timestamp, 1, 10))
                .all()
            ],
            "sandbox": True,
        }


@app.post(
    "/api/applications",
    status_code=201,
    response_model=CaseResponse,
    response_model_exclude_none=True,
)
def create(body: Submission, response: Response, x_sandbox_session: str | None = Header(default=None), idempotency_key: str | None = Header(default=None)):
    session_id = sandbox_session(x_sandbox_session)
    request_key = sandbox_session(idempotency_key)
    key_hash = hashlib.sha256(f"{session_id or 'anonymous'}:{request_key}".encode()).hexdigest() if request_key else None
    legacy_payload = body.model_dump()
    payload = {**legacy_payload, "application_completeness_score": None}
    payload_hash = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    with Session() as db:
        # Serialize the lookup + insert across SQLite connections, including simultaneous retries.
        # No reservation is committed if validation/storage fails.
        db.connection().exec_driver_sql("BEGIN IMMEDIATE")
        previous = db.get(SubmissionRequest, key_hash) if key_hash else None
        if previous:
            # Replays of pre-V7.1 requests retain their saved records and hashes.
            historical_payload = json.loads(require(db, previous.application_id).payload)
            # Upgrades add optional non-model metadata. Match old hashes only
            # when absent metadata remains empty; never ignore a changed concern/help request.
            candidate = dict(legacy_payload if historical_payload.get("application_completeness_score") is not None else payload)
            for field in SAFEGUARD_FIELDS:
                if field not in historical_payload and not candidate[field]:
                    candidate.pop(field)
            legacy_hash = hashlib.sha256(json.dumps(candidate, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            historical_replay = previous.payload_hash == legacy_hash
            if previous.payload_hash != payload_hash and not historical_replay:
                raise HTTPException(409, "Idempotency key was already used with different application data")
            response.headers["Idempotency-Replayed"] = "true"
            return serialize(require(db, previous.application_id), latest_reviews(db).get(previous.application_id))
        documents = [db.get(EvidenceDocument, eid) for eid in body.evidence_ids]
        if any(d is None or d.session_id != session_id or d.application_id is not None for d in documents):
            raise HTTPException(409, "Evidence must belong to this sandbox session and be unattached")
        aid = "HAB-" + uuid.uuid4().hex[:8].upper()
        a = Application(id=aid, payload=json.dumps(payload), status="unassessed")
        db.add(a)
        db.flush()
        for document in documents:
            document.application_id = aid
        if session_id:
            db.add(ApplicantSessionApplication(application_id=aid, session_id=session_id))
        if key_hash:
            db.add(SubmissionRequest(key_hash=key_hash, payload_hash=payload_hash, application_id=aid))
        log(db, aid, "submitted", {"synthetic_only": True})
        db.commit()
        response.headers["Idempotency-Replayed"] = "false"
        return serialize(a)


@app.get(
    "/api/applications",
    response_model=list[CaseResponse],
    response_model_exclude_none=True,
)
def applications():
    with Session() as db:
        reviews = latest_reviews(db)
        return [serialize(a, reviews.get(a.id)) for a in db.query(Application).all()]


@app.get("/api/applicant/applications", response_model=list[CaseResponse], response_model_exclude_none=True)
def applicant_applications(x_sandbox_session: str = Header()):
    session_id = sandbox_session(x_sandbox_session)
    with Session() as db:
        reviews = latest_reviews(db)
        rows = db.query(Application).join(ApplicantSessionApplication).filter(ApplicantSessionApplication.session_id == session_id).all()
        return [serialize(a, reviews.get(a.id)) for a in rows]


@app.get(
    "/api/applications/{aid}",
    response_model=CaseResponse,
    response_model_exclude_none=True,
)
def get_case(aid: str):
    with Session() as db:
        a = require(db, aid)
        result = serialize(a)
        result["history"] = [
            {
                "timestamp": e.timestamp,
                "action": e.action,
                "detail": json.loads(e.detail),
            }
            for e in db.query(Event)
            .filter_by(application_id=aid)
            .order_by(Event.timestamp)
            .all()
        ]
        result["latest_review"] = next(
            (
                e["detail"] | {"timestamp": e["timestamp"]}
                for e in reversed(result["history"])
                if e["action"] == "human_override"
            ),
            None,
        )
        return result


@app.post("/api/applications/{aid}/assess")
def assess(aid: str):
    with Session() as db:
        a = require(db, aid)
        if a.status == "resolved":
            raise HTTPException(
                409,
                "A completed human review cannot be silently reopened by reassessment",
            )
        result = assess_record(json.loads(a.payload))
        result["model_version"] = "rf-1.0"
        result["assessed_at"] = datetime.now(timezone.utc).isoformat()
        if result["score"] is not None:
            result["model_sha256"] = model_fingerprint()
        result["policy_evidence"] = load_policy().evaluate(json.loads(a.payload))
        a.assessment = json.dumps(result)
        follow_up = latest_reviews(db).get(aid, {}).get("outcome")
        human_follow_up_open = a.status == "pending" and follow_up in {
            "request_evidence",
            "escalate",
            "additional_review",
        }
        a.status = (
            "pending"
            if result["requires_review"] or human_follow_up_open
            else "routine"
        )
        log(db, aid, "assessed", result)
        db.commit()
        return result


@app.get("/api/applications/{aid}/explanation")
def explanation(aid: str):
    with Session() as db:
        a = require(db, aid)
        if not a.assessment:
            raise HTTPException(
                409, "Assess this case before requesting an explanation"
            )
        stored = json.loads(a.assessment)
        if stored.get("score") is None or stored.get("failure"):
            raise HTTPException(
                409, "Assessment unavailable; keep this case in human review"
            )
        try:
            result = explain(json.loads(a.payload))
            if abs(result["score"] - stored["score"]) > 1e-6:
                raise HTTPException(
                    409,
                    "Explanation differs from the recorded assessment; request human review and reassess",
                )
            return result
        except (
            ValueError,
            KeyError,
            TypeError,
            AttributeError,
            OSError,
            EOFError,
            RuntimeError,
        ):
            raise HTTPException(503, "Explanation unavailable; refer to human review")


@app.get(
    "/api/reviews", response_model=list[CaseResponse], response_model_exclude_none=True
)
def reviews():
    with Session() as db:
        review_events = latest_reviews(db)
        return [
            serialize(a, review_events.get(a.id))
            for a in db.query(Application).filter_by(status="pending").all()
        ]


@app.post(
    "/api/reviews/{aid}/resolve",
    response_model=CaseResponse,
    response_model_exclude_none=True,
)
def resolve(aid: str, body: Resolution):
    with Session() as db:
        a = require(db, aid)
        if not a.assessment:
            raise HTTPException(409, "Assessment required before human override")
        if a.status == "resolved":
            raise HTTPException(
                409, "This review is already completed; its history is preserved"
            )
        a.status = "resolved" if body.outcome == "routine" else "pending"
        log(
            db,
            aid,
            "human_override",
            {**body.model_dump(), "workflow_status": a.status},
        )
        db.commit()
        return get_case(aid)


@app.get("/api/policies")
def policies():
    pack = json.loads((ROOT / "policy_packs/england-demo.json").read_text())
    return [pack] + [
        {
            "id": x.lower(),
            "name": x + " · not implemented",
            "functional": False,
            "rule_description": "No country-specific eligibility rules implemented.",
        }
        for x in ["United States", "India", "Singapore"]
    ]


@lru_cache(maxsize=1)
def dataset_metadata():
    df = pd.read_csv(ROOT / "data/public/habitat_synthetic_2000.csv")
    dictionary = []
    for line in (ROOT / "data/DATA_DICTIONARY.md").read_text().splitlines():
        if line.startswith("| `"):
            parts = line.split("|")
            dictionary.append(
                {
                    "feature": parts[1].strip().strip("`"),
                    "description": parts[2].strip(),
                }
            )
    return {
        "records": len(df),
        "scenario_families": int(df.scenario_id.nunique()),
        "version": "1.0.0",
        "seed": 42,
        "provenance": "Generated synthetic benchmark — no personal data — not representative of any national housing applicant population.",
        "splits": report("splits"),
        "sha256": hashlib.sha256(
            (ROOT / "data/public/habitat_synthetic_2000.csv").read_bytes()
        ).hexdigest(),
        "preview": df.head(8).to_dict(orient="records"),
        "dictionary": dictionary,
        "class_balance": [
            {
                "label": (
                    "Routine human workflow" if k == 0 else "Additional human review"
                ),
                "count": int(v),
            }
            for k, v in df.case_review_required.value_counts().sort_index().items()
        ],
        "housing_distribution": [
            {"name": k, "count": int(v)}
            for k, v in df.housing_situation.value_counts().items()
        ],
    }


@app.get("/api/dataset/metadata")
def metadata():
    return dataset_metadata()


@app.get("/api/dataset/card")
def dataset_card():
    return FileResponse(
        ROOT / "data/DATASET_CARD.md",
        media_type="text/markdown",
        filename="DATASET_CARD.md",
    )


@app.get("/api/dataset/dictionary")
def dictionary():
    return FileResponse(
        ROOT / "data/DATA_DICTIONARY.md",
        media_type="text/markdown",
        filename="DATA_DICTIONARY.md",
    )


@app.get("/api/dataset/download")
def download():
    return FileResponse(
        ROOT / "data/public/habitat_synthetic_2000.csv",
        media_type="text/csv",
        filename="habitat_synthetic_2000.csv",
    )


# Evidence analysis never changes Case availability flags or the nine RF inputs.
@app.post("/api/evidence/analyse", status_code=201)
async def analyse_evidence(request: Request, category: Literal["income", "identity", "housing"],
                           x_sandbox_session: str = Header(), x_synthetic_only: Literal["true"] = Header()):
    from backend.document_analysis import MAX_BYTES
    from backend.document_service import process_pdf
    session_id = sandbox_session(x_sandbox_session)
    if request.headers.get("content-type", "").split(";")[0] != "application/pdf":
        raise HTTPException(415, "Only application/pdf is accepted")
    data = bytearray()
    async for chunk in request.stream():
        data.extend(chunk)
        if len(data) > MAX_BYTES:
            raise HTTPException(413, "PDF exceeds 2 MiB limit")
    try:
        result = await run_in_threadpool(process_pdf, bytes(data), category)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    except RuntimeError:
        raise HTTPException(429, "Document processing busy; retry later")
    eid = str(uuid.uuid4())
    created = datetime.now(timezone.utc).isoformat()
    with Session() as db:
        db.add(EvidenceDocument(id=eid, session_id=session_id, analysis=json.dumps(result),
                               sha256=hashlib.sha256(data).hexdigest(), created_at=created))
        db.commit()
    return {"id": eid, "created_at": created, "analysis": result, "reviews": [], "raw_pdf_retained": False}


def evidence_record(db, document):
    reviews = []
    if document.application_id:
        reviews = [{"timestamp": e.timestamp, **json.loads(e.detail)} for e in db.query(Event).filter_by(application_id=document.application_id, action="evidence_review").order_by(Event.timestamp, Event.id) if json.loads(e.detail).get("evidence_id") == document.id]
    return {"id": document.id, "created_at": document.created_at, "analysis": json.loads(document.analysis), "reviews": reviews, "raw_pdf_retained": False}


@app.get("/api/applications/{aid}/evidence")
def application_evidence(aid: str):
    with Session() as db:
        require(db, aid)
        return [evidence_record(db, d) for d in db.query(EvidenceDocument).filter_by(application_id=aid).order_by(EvidenceDocument.created_at)]


@app.get("/api/evidence/{eid}")
def get_evidence(eid: str, x_sandbox_session: str = Header()):
    sid = sandbox_session(x_sandbox_session)
    with Session() as db:
        document = db.get(EvidenceDocument, eid)
        if document is None or (document.application_id is None and document.session_id != sid):
            raise HTTPException(404, "Evidence not found in this sandbox session")
        return evidence_record(db, document)


class EvidenceReview(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action: Literal["confirm", "correct", "insufficient", "request_clarification", "escalate"]
    observation_id: str | None = None
    corrected_value: str | None = Field(default=None, max_length=300)
    reason: str = Field(min_length=8, max_length=1000)

    @model_validator(mode="after")
    def reason_and_observation(self):
        if len(self.reason.strip()) < 8: raise ValueError("Provide a meaningful synthetic review reason")
        if self.action in ["confirm", "correct"] and not self.observation_id: raise ValueError("Select a specific observation")
        if self.action == "correct" and not (self.corrected_value or "").strip(): raise ValueError("Provide the corrected observation")
        return self


@app.post("/api/evidence/{eid}/review")
def review_evidence(eid: str, body: EvidenceReview):
    with Session() as db:
        document = db.get(EvidenceDocument, eid)
        if document is None or not document.application_id: raise HTTPException(404, "Attach evidence to an application before review")
        observations = json.loads(document.analysis)["observations"]
        if body.observation_id and body.observation_id not in [o["id"] for o in observations]: raise HTTPException(422, "Observation does not exist")
        log(db, document.application_id, "evidence_review", {"evidence_id": eid, **body.model_dump(), "reviewer_identity": "Unverified sandbox caseworker", "scope": "Review of extracted text only; not document authentication or statutory determination"})
        db.commit()
        return evidence_record(db, document)


@app.get("/api/evidence-fixtures/{name}")
def evidence_fixture(name: Literal["dev-income", "dev-identity", "dev-housing"]):
    return FileResponse(ROOT / "evidence_benchmark/dev" / (name + ".pdf"), media_type="application/pdf", filename=name + ".pdf")


# Optional same-origin serving of the verified production bundle.
if (ROOT / "frontend/dist/index.html").exists():
    app.mount(
        "/", StaticFiles(directory=ROOT / "frontend/dist", html=True), name="frontend"
    )
