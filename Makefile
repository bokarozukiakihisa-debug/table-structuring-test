.PHONY: setup run-one diff fmt

setup:
	pip install -r requirements.txt

run-one:
	@cat samples/input/sample_estimate_001.txt | python scripts/parse_and_validate.py

diff:
	@tools/diff_json.sh runs/*/success/sample.json samples/expected/sample_estimate_001.json || true

fmt:
	@python -m json.tool < samples/expected/sample_estimate_001.json > /dev/null
