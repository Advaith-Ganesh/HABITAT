"""Read-only V4 audit: preserve training artifacts, write versioned evidence only."""
from scripts.audit_v2 import main
from ml.safeguard import measure
from ml.common import save_json

if __name__ == '__main__':
    main('reports/v4-ml-audit.json')
    save_json('reports/v4-safeguard.json', measure())
