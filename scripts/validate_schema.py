import sys, json
from jsonschema import validate, Draft202012Validator
from pathlib import Path

schema = json.loads(Path("schemas/estimate.schema.json").read_text(encoding="utf-8"))
doc = json.loads(sys.stdin.read())

v = Draft202012Validator(schema)
errors = sorted(v.iter_errors(doc), key=lambda e: e.path)
if errors:
    for e in errors:
        print(f"[SCHEMA] {list(e.path)}: {e.message}")
    sys.exit(1)
else:
    print("[SCHEMA] OK")
