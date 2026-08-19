#!/usr/bin/env python3
"""固定台帳（lts/*.yaml）を読んで、検証・出力する。

台帳は書いただけでは守られない。**そこから実際のインストール手順を生成**して
初めて「台帳と環境が一致している」と言える。

    ./lts-resolve.py lts/LTS26.9.yaml --check       # 台帳の妥当性を見る（CI 用）
    ./lts-resolve.py lts/LTS26.9.yaml --sh          # bash のインストール手順を出す
    ./lts-resolve.py lts/LTS26.9.yaml --notebook    # Colab セル用の Python を出す

`--check` は次を見る。ネットワークは使わない（CI を速く保つ）。

  - 必須フィールドの欠落
  - ref / sha の書式（タグ名は残す。SHA だけにしない ― 人が読めなくなる）
  - status が approved なのに license: unknown が残っていないか
    ライセンス整理が ComfyLTS の存在理由なので、ここは落とす
"""
import argparse, re, sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML が要る: pip install pyyaml")

SHA = re.compile(r"^[0-9a-f]{7,40}$")


def check(d: dict) -> list[str]:
    errs = []
    md, rt = d.get("metadata", {}), d.get("runtime", {})
    for k in ("name", "status"):
        if not md.get(k):
            errs.append(f"metadata.{k} がない")
    c = rt.get("comfyui", {})
    for k in ("repo", "ref", "sha"):
        if not c.get(k):
            errs.append(f"runtime.comfyui.{k} がない")
    if c.get("sha") and not SHA.match(str(c["sha"])):
        errs.append(f"runtime.comfyui.sha が SHA に見えない: {c['sha']}")

    for n in d.get("customNodes", []):
        if not (n.get("repo") and n.get("ref")):
            errs.append(f"customNodes[{n.get('name','?')}] に repo/ref がない")

    # 承認済みを名乗るなら、ライセンス未確認を残さない
    if md.get("status") == "approved":
        unk = [m["repo"] for m in d.get("modelSources", []) if m.get("license") in (None, "unknown")]
        if unk:
            errs.append("status: approved だが license: unknown が残っている: " + ", ".join(unk))

    # 検証結果が pass でないものを黙って通さない
    for r in d.get("verification", {}).get("routes", []):
        if r.get("result") != "pass":
            errs.append(f"verification.routes[{r.get('id')}] が pass ではない: {r.get('result')}")
    return errs


def emit_sh(d: dict) -> str:
    c = d["runtime"]["comfyui"]
    out = [f"# {d['metadata']['name']} — 生成物。手で編集しない", "set -euo pipefail", ""]
    out.append(f"git clone --depth 1 --branch {c['ref']} {c['repo']} ComfyUI")
    out.append(f"git -C ComfyUI rev-parse HEAD | grep -q '^{c['sha']}' "
               f"|| echo '[WARN] {c['ref']} の SHA が台帳と違う（上流がタグを付け替えた可能性）'")
    out.append("")
    out.append("mkdir -p ComfyUI/custom_nodes && cd ComfyUI/custom_nodes")
    for n in d.get("customNodes", []):
        out.append(f"git clone {n['repo']} {n['name']} && git -C {n['name']} checkout -q {n['ref']}")
    return "\n".join(out) + "\n"


def emit_notebook(d: dict) -> str:
    c = d["runtime"]["comfyui"]
    nodes = ",\n".join(f'    ("{n["name"]}", "{n["repo"]}", "{n["ref"]}")' for n in d.get("customNodes", []))
    return f'''# {d["metadata"]["name"]} — ComfyLTS 固定台帳より生成。手で編集しない
COMFYUI_REF = "{c["ref"]}"          # {c["repo"]}
COMFYUI_SHA = "{c["sha"]}"          # タグが付け替えられたら気づけるように

PINNED_NODES = [
{nodes}
]
'''


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--sh", action="store_true")
    ap.add_argument("--notebook", action="store_true")
    a = ap.parse_args()
    d = yaml.safe_load(open(a.manifest, encoding="utf-8"))

    if a.check or not (a.sh or a.notebook):
        errs = check(d)
        md = d.get("metadata", {})
        print(f"{md.get('name')}  status={md.get('status')}  "
              f"nodes={len(d.get('customNodes', []))}  routes={len(d.get('verification', {}).get('routes', []))}")
        unk = [m["repo"] for m in d.get("modelSources", []) if m.get("license") in (None, "unknown")]
        if unk:
            print(f"  ライセンス未確認 {len(unk)}件: " + ", ".join(unk))
        if errs:
            print("\n🔴 " + "\n🔴 ".join(errs))
            sys.exit(1)
        print("✅ 台帳は妥当")
    if a.sh:
        print(emit_sh(d))
    if a.notebook:
        print(emit_notebook(d))


if __name__ == "__main__":
    main()
