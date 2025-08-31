cat > scripts/parse_and_validate.py <<'PY'
import json, re, sys, hashlib, os
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

JST = ZoneInfo("Asia/Tokyo")
RUN_STAMP = datetime.now(JST).strftime("%Y%m%d_%H%M%S")
OUTDIR = Path(f"runs/{RUN_STAMP}")
(OUTDIR / "success").mkdir(parents=True, exist_ok=True)
(OUTDIR / "errors").mkdir(parents=True, exist_ok=True)
(OUTDIR / "raw").mkdir(parents=True, exist_ok=True)

SAMPLE_NAME = os.environ.get("SAMPLE_NAME", "sample")

def largest_json_block(text: str):
    start_idx = None
    depth = 0
    best = None
    for i, ch in enumerate(text):
        if ch == '{':
            if depth == 0:
                start_idx = i
            depth += 1
        elif ch == '}':
            if depth > 0:
                depth -= 1
                if depth == 0 and start_idx is not None:
                    cand = text[start_idx:i+1]
                    if best is None or len(cand) > len(best):
                        best = cand
    return best

def try_load_json(text: str):
    try:
        return json.loads(text)
    except Exception:
        pass
    no_fence = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)
    try:
        return json.loads(no_fence)
    except Exception:
        pass
    block = largest_json_block(text)
    if block:
        try:
            return json.loads(block)
        except Exception:
            pass
    return None

def business_checks(doc: dict) -> list[str]:
    errs = []
    try:
        lines = doc.get("明細", [])
        subtotal = sum([x.get("金額", 0) for x in lines if isinstance(x, dict)])
        if "小計" in doc and isinstance(doc["小計"], (int, float)):
            if abs(float(doc["小計"]) - float(subtotal)) > 1e-6:
                errs.append(f"小計不一致: 期待={subtotal} 実値={doc['小計']}")
        if "合計" in doc and "小計" in doc:
            expected_total = float(doc.get("小計", 0)) + float(doc.get("消費税", 0))
            if abs(float(doc["合計"]) - expected_total) > 1e-6:
                errs.append(f"合計不一致: 期待={expected_total} 実値={doc['合計']}")
    except Exception as e:
        errs.append(f"business_checks例外: {e}")
    return errs

def save_json_sorted(path: Path, obj: dict):
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)

def sha256_of(obj: dict) -> str:
    b = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(b.encode("utf-8")).hexdigest()

def handle_one(sample_name: str, model_text: str):
    (OUTDIR / "raw" / f"{sample_name}.txt").write_text(model_text, encoding="utf-8")

    obj = try_load_json(model_text)
    if obj is None:
        err_doc = {"_error": {
            "type": "PARSE_ERROR",
            "reason": "JSON decode failed",
            "hint": "出力は純JSONのみ。コメント/フェンス/説明文禁止。"
        }}
        save_json_sorted(OUTDIR / "errors" / f"{sample_name}.json", err_doc)
        return ("error", err_doc, None)

    if isinstance(obj, dict) and "_error" in obj:
        save_json_sorted(OUTDIR / "errors" / f"{sample_name}.json", obj)
        return ("error", obj, None)

    berrs = business_checks(obj)
    if berrs:
        obj["_warnings"] = {"business_checks": berrs}

    out_path = OUTDIR / "success" / f"{sample_name}.json"
    save_json_sorted(out_path, obj)
    return ("ok", obj, sha256_of(obj))

if __name__ == "__main__":
    text = sys.stdin.read()
    status, obj, digest = handle_one(SAMPLE_NAME, text)
    print({"status": status, "name": SAMPLE_NAME, "sha256": digest})
PY
