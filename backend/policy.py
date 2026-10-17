"""Versioned policy-pack interface. No statutory eligibility checks."""

from typing import Protocol
import json
from ml.common import ROOT


class PolicyPack(Protocol):
    def evaluate(self, record: dict) -> dict: ...
class EnglandDemoPack:
    def __init__(self):
        self.metadata = json.loads(
            (ROOT / "policy_packs/england-demo.json").read_text()
        )

    def evaluate(self, record: dict) -> dict:
        prompts = []
        if record.get("missing_document_count", 0) > 0:
            prompts.append(
                "Ask a human to clarify missing evidence under the fictional intake protocol."
            )
        if record.get("conflicting_information"):
            prompts.append("Ask a human to reconcile contradictory information.")
        if record.get("housing_situation") == "unclear":
            prompts.append("Ask a human to clarify reported housing circumstances.")
        return {
            "pack_id": self.metadata["id"],
            "version": self.metadata["version"],
            "prompts": prompts,
            "source_url": self.metadata["source_url"],
            "applicability": self.metadata["applicability"],
            "warning": self.metadata["human_review_warning"],
            "origin": "Fictional demo assumptions; these prompts are not extracted statutory rules.",
        }


def load_policy(pack_id="england-demo") -> PolicyPack:
    if pack_id != "england-demo":
        raise ValueError("Jurisdiction placeholder is not implemented")
    return EnglandDemoPack()
