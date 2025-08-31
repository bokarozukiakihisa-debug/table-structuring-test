#estim-json-lab/
├─ README.md
├─ .gitignore
├─ .editorconfig
├─ requirements.txt
├─ Makefile
├─ .vscode/
│  ├─ settings.json
│  ├─ launch.json
│  └─ tasks.json
├─ .devcontainer/
│  └─ devcontainer.json
├─ prompts/
│  ├─ system.md
│  ├─ user.md
│  └─ assistant.md
├─ scripts/
│  ├─ parse_and_validate.py
│  ├─ run_one.sh
│  └─ validate_schema.py
├─ schemas/
│  └─ estimate.schema.json
├─ samples/
│  ├─ input/
│  │  └─ sample_estimate_001.txt   # テスト入力（OCR結果など）
│  └─ expected/
│     └─ sample_estimate_001.json  # 人手で作った「正解JSON」
├─ runs/          # 実行結果（自動生成; gitignore 推奨）
└─ tools/
   └─ diff_json.sh
