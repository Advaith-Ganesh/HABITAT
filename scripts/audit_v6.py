"""Read-only verification of the preserved model, data, SHAP and fairness."""
from scripts.audit_v2 import main
from ml.common import save_json
from ml.safeguard import measure

if __name__ == "__main__":
    main("reports/v6-ml-audit.json")
    save_json("reports/v6-safeguard.json", measure())
