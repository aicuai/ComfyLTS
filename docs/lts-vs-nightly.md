# ComfyJapan LTS と Nightly の二本建て

**判定は感覚ではなく「動くワークフローの本数」で行う。**

作成 2026-08-11 / 対象 `Book-SD-MasterGuide/workflows`（34本）

---

## なぜ二本建てにするか

ComfyUI 本体は速く動く。upstream に追随すれば新機能と修正が入るが、
**本体の API 変更でカスタムノードが壊れる**。実例:

```
Cannot import efficiency-nodes-comfyui:
  cannot import name 'CompVisVDenoiser' from 'comfy.samplers'
IMPORT FAILED
```

追随しなければ壊れないが、新しいモデルが動かず、修正も入らない。
**どちらか一方を選ぶ構造が間違っている。** 二本立てて、役割を分ける。

| | LTS | Nightly |
|---|---|---|
| 対象 | 顧客向け共有Pod（GPU0/1） | 実験枠（GPU2/3） |
| 更新 | **動くワークフローが減らないと確認できたときだけ** | upstream に随時追随 |
| 保証 | 書籍ワークフローが動くこと | 保証しない |
| 壊れたら | 前のバージョンに戻す | 直すか、放置して次を待つ |

LTS が保証するのは「最新であること」ではなく **「動くこと」**。
Nightly が引き受けるのは「壊れること」。

---

## 判定基準

**更新の可否は、更新後に動くワークフローの本数で決める。**

```
更新後の動作本数 >= 更新前の動作本数  →  上げてよい
更新後の動作本数 <  更新前の動作本数  →  上げない（何が壊れたかを特定してから）
```

本数は `tools/workflow-audit.py` が機械的に出す。人の感覚を挟まない。

```bash
curl -s http://127.0.0.1:8188/object_info > /tmp/object_info.json
OBJECT_INFO=/tmp/object_info.json ./tools/workflow-audit.py path/to/workflows
```

### なぜ本数なのか

「動いた気がする」「たぶん大丈夫」で本番を上げると、**壊れたことに誰も気づかない**。
実際、本日まで**34本中24本が壊れていること自体が把握されていなかった**。

本数なら、
- 更新の可否を1つの数字で判断できる
- 壊れた本数が増えたとき、どれが壊れたかがそのまま分かる
- CI に載せられる（配布前に必ず通す）

---

## 現在地（2026-08-11 実測）

### バージョン

| | ComfyUI |
|---|---|
| 顧客向け共有Pod (`comfypods`) | **0.17.0**（commit 2026-03-15） |
| GPU0 master | **0.17.0** |
| upstream 最新 | **0.32.0** |

**約5ヶ月・15マイナー版の乖離。**
H3 検証で報告した 0.31.0 は別コンテナ（`h3-review`）であり、顧客環境には入っていない。

### LTS の基準値: **34本中 10本（29%）**

| 区分 | 本数 |
|---|---|
| 動く | **10** |
| 問題あり | **24** |
| └ モデルのみ不足 | 12 |
| └ ノードとモデル両方 | 11 |
| └ ノードのみ不足 | 1 |

**動く10本**

```
inpaint_advanced.json
ipadapter_basic.json
workflow_animatediff_t2v.json
workflow_animatediff_t2v_with_ipadapter.json
workflow_i2i-basic.json
workflow_i2i-inpainting-change-hair.json
workflow_i2i-inpainting-face.json
workflow_i2i-outpainting.json
workflow_sdxl_lora.json
workflow_t2i_hires-fix.json
```

この10本が **LTS が守るべき最低ライン**。更新でこれを下回ってはいけない。

### 不足しているものの内訳

**モデル（13種）** — 影響本数の多い順

```
10本  controlnet-union-sdxl-1.0-promax.safetensors  ← 名前違いの疑い (#3)
 6本  CN-anytest_v4-marged.safetensors
 3本  realvisxlInpainting_v5lightning.safetensors
 2本  rife47.pth / add-detail-xl / Envy-Zoom-Slider-XL
 1本  RealVisXL_V5.0_fp16 / leosams-helloworld-xl / atomix_anime_xl /
      aamXLAnimeMix_v10HalfturboEulera / glowneon_xl_v1
```

**カスタムノード（13種）**

```
5本  ACN_AdvancedControlNetApply      → ComfyUI-Advanced-ControlNet（未インストール）
4本  ControlNetLoaderAdvanced          → 同上
3本  Eff. Loader SDXL / KSampler SDXL (Eff.) / XY Plot
                                       → efficiency-nodes-comfyui（**IMPORT FAILED**）
2本  RIFE VFI                          → ComfyUI-Frame-Interpolation（未インストール）
2本  Local Save                        → 要特定
1本  LayerMask: SegmentAnythingUltra V2 / LatentKeyframeTiming /
     ACN_AdvancedControlNetApply_v2 / XY Input: Prompt S/R
```

---

## v0.32.0 を上げるか

**上げない。** ただし理由は「新しいから怖い」ではない。

1. **効くのが H3 関連**（VAE最適化・NestedTensor クラッシュ修正・ピークメモリ改善）で、
   これは **GPU2/3 の実験枠の話**。画像生成が主の顧客向けPodには効かない
2. **壊れる面が広い** — 既に24本が壊れている状態で5ヶ月分を飛ばすと、
   何が原因で何本減ったのか切り分けられなくなる
3. **判定に必要な数字が出せていない** — v0.32.0 環境で監査を回していないので、
   10本が何本になるか分からない。**分からないまま上げない**

### 先にやること

- [ ] Nightly（GPU2/3）に v0.32.0 を立て、同じ監査を回して本数を出す
- [ ] LTS 側で不足モデル・ノードを埋め、基準値を 10本から引き上げる
      （上げ幅が大きいほど、更新の影響が見えやすくなる）
- [ ] 両者の本数を並べて、初めて更新の可否を判断する

---

## LTS が宣言すべきもの

現状、**何と何の組み合わせで動くのかがどこにも書かれていない。**

- ComfyUI 本体のバージョンが宣言されていない
- `custom_nodes.yaml` が実機と乖離している
  （実機にあって yaml に無い: `efficiency-nodes-comfyui` / `comfyui_controlnet_aux` /
  `comfyui-inpaint-nodes` / `rgthree-comfy` / `was-node-suite-comfyui`）
- `models.yaml` / `book_models.yaml` に宣言済みでも実機に無いものがある

**「この本体 × このノード群 × このモデル群で、この34本が動く」と書き下すこと自体が LTS の中身。**
宣言と実体が合っていない限り、何を保証しているのか誰にも言えない。

---

## 関連

- 監査の詳細: [#1](https://github.com/aicuai/ComfyLTS/issues/1)
- ControlNet-union の名前違い調査: [#3](https://github.com/aicuai/ComfyLTS/issues/3)
- 監査ツール: `tools/workflow-audit.py`
- v0.32.0 の判断: [aicuai/comfy-aicu#9](https://github.com/aicuai/comfy-aicu/issues/9)
