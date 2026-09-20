from pathlib import Path
import json
import guardpycfn
from cfnlint.decode import decode
root = Path(__file__).resolve().parents[1]
template, errors = decode(str(root / 'template.yaml'))
if errors:
    raise SystemExit(str(errors))
result = guardpycfn.validate_with_guard(json.dumps(template), (root / 'tests/security.guard').read_text(), verbose=True)
print(result)
if 'FAIL' in str(result):
    raise SystemExit(1)
