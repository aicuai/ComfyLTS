#!/usr/bin/env python3
"""ワークフローの静的検査 (C-1)。
未登録ノードと、実機に無いモデル参照を検出する。
ブラウザ不要。/object_info を1回引くだけ。"""
import json, os, glob, sys, urllib.request

OBJ = os.environ["OBJECT_INFO"]          # /object_info の JSON をファイルで渡す
WF  = sys.argv[1] if len(sys.argv) > 1 else "."

obj = json.load(open(OBJ))
known_nodes = set(obj.keys())
# フロント側の仮想ノード。/object_info には出ないが正常に動く。
VIRTUAL = {"Reroute", "Note", "MarkdownNote", "PrimitiveNode", "Primitive",
           "workflow", "Anything Everywhere", "Anything Everywhere3",
           "Anything Everywhere?", "Prompts Everywhere", "Seed Everywhere"}
known_nodes |= VIRTUAL

# 各ノードの入力候補（enum）を集める = 実機にあるモデル一覧
available = set()
for spec in obj.values():
    inp = (spec.get("input") or {})
    for group in ("required", "optional"):
        for _name, v in (inp.get(group) or {}).items():
            # /object_info の選択肢は2形式ある:
            #   旧: [["a.safetensors", "b.safetensors"], {...}]
            #   新: ["COMBO", {"options": ["a.safetensors", ...]}]
            # 新形式を読み落とすと「実機にあるのに無い」と誤判定する（実際に踏んだ）。
            opts = []
            if isinstance(v, list) and v:
                if isinstance(v[0], list):
                    opts = v[0]
                elif v[0] == "COMBO" and len(v) > 1 and isinstance(v[1], dict):
                    opts = v[1].get("options") or []
            for opt in opts:
                if isinstance(opt, str):
                    available.add(opt)

MODEL_EXT = (".safetensors", ".ckpt", ".pt", ".pth", ".bin", ".gguf", ".onnx", ".sft")
rows = []
for f in sorted(glob.glob(os.path.join(WF, "*.json"))):
    try:
        g = json.load(open(f))
    except Exception as e:
        rows.append((os.path.basename(f), ["(読めない)"], [], str(e)[:60])); continue
    if not isinstance(g, dict) or "nodes" not in g:
        continue
    miss_nodes, miss_models = set(), set()
    for n in g.get("nodes", []):
        t = n.get("type")
        if t and t not in known_nodes:
            miss_nodes.add(t)
        for w in (n.get("widgets_values") or []):
            if isinstance(w, str) and w.lower().endswith(MODEL_EXT):
                if w not in available:
                    miss_models.add(w)
    if miss_nodes or miss_models:
        rows.append((os.path.basename(f), sorted(miss_nodes), sorted(miss_models), ""))

print(f"検査 {len(glob.glob(os.path.join(WF,'*.json')))} 本 / 問題あり {len(rows)} 本\n")
json.dump([{"file":a,"nodes":b,"models":c,"err":d} for a,b,c,d in rows],
          open(os.environ.get("AUDIT_OUT","/tmp/audit.json"),"w"), ensure_ascii=False, indent=1)
for name, nodes, models, err in rows:
    print(f"■ {name}")
    if nodes:  print(f"   未登録ノード: {', '.join(nodes)}")
    if models: print(f"   無いモデル  : {', '.join(models)}")
    if err:    print(f"   エラー      : {err}")
