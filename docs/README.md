# docs

**テストと測定結果は `comfy-aicu` で管理する。**

測定結果は `feed/comfy-updates.json` を経て aicu.ai/comfy のブログになる
供給チェーンに乗せるため、チェーンの起点と同じ場所に置く（CEO 指示 2026-08-11）。

| 内容 | 置き場所 |
|---|---|
| LTS / Nightly の二本建てと判定基準 | `comfy-aicu:infra/docs/LTS_VS_NIGHTLY.md` |
| テスト対象リストと合否 | `comfy-aicu:infra/tests/BOOK_WORKFLOWS.md` |
| 機械可読の測定結果 | `comfy-aicu:infra/tests/workflows/book-workflows.json` |
| 監査ツール（本番運用） | `comfy-aicu:infra/scripts/workflow-audit.py` |

本リポジトリには **監査ツールの汎用部分**（`tools/`）だけを残す。
どの環境でも `/object_info` さえ取れれば動くので、公開して困らない。
