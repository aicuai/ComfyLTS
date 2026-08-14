# tools

## workflow-audit.py — ワークフローの静的検査

ワークフロー（UI形式 JSON）が、いま動く状態かを **実行せずに** 判定する。

```bash
# 稼働中の ComfyUI から /object_info を取る
curl -s http://127.0.0.1:8188/object_info > /tmp/object_info.json

# 検査
OBJECT_INFO=/tmp/object_info.json ./workflow-audit.py /path/to/workflows
```

### 何を見るか

| 検査 | 内容 |
|---|---|
| 未登録ノード | `nodes[].type` が `/object_info` に無い（カスタムノード未導入 or import 失敗） |
| 無いモデル | `widgets_values` のモデル参照が、どのノードの選択肢にも無い |

ブラウザ不要・HTTP 1本なので CI で回せる。

### 実装上の注意

**`/object_info` の選択肢には2形式ある。**

```jsonc
// 旧: [["a.safetensors", "b.safetensors"], {...}]
// 新: ["COMBO", {"options": ["a.safetensors", ...]}]
```

新形式を読み落とすと「実機にあるのに無い」と誤判定する（2026-08-11 に実際に踏んだ）。

**仮想ノードは除外する。** `Reroute` / `Note` / `PrimitiveNode` などは
フロント側の実装で `/object_info` に出ないが、正常に動く。

### 「モデルが無い」の原因は3種類

1. **実体はあるが `extra_model_paths.yaml` にカテゴリが無い** → パス登録で解決（ワークフロー無変更）
2. 本当に無い → ダウンロードが要る
3. 読み手のカスタムノードが無い → モデルを置いても選択肢に出ない

1 を先に潰すこと。設定1ファイルで直り、ワークフローにも書籍にも影響しない。
