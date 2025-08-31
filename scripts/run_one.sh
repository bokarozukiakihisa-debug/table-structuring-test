#!/usr/bin/env bash
set -euo pipefail

STAMP=$(TZ=Asia/Tokyo date +"%Y%m%d_%H%M%S")
mkdir -p "runs/${STAMP}"

# 例：モデル出力をファイルに保存してから検証
# 実際の取得はあなたの手順で（CLI・API・手動コピー等）
INFILE="samples/input/sample_estimate_001.txt"

cat "${INFILE}" | python scripts/parse_and_validate.py | tee "runs/${STAMP}/result.txt"
