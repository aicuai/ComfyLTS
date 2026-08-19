# LTS 26.9

**Status: 提案（未確定）** — 実測の裏付けはあるが、ComfyLTS としての承認は未了。

Wan2.2（I2V / FLF2V）と Seedance2.0（R2V）を対象に加えた LTS ラインの提案。
書籍『【キャラクターを創り動かす】画像・動画生成AI スタートガイド』（2026-09-19 発売）の
付属ノートブックが依存するため、**刊行に間に合う固定値**が要る。

## 提案する固定値

| 対象 | 版 | 根拠 |
|---|---|---|
| **ComfyUI** | **`v0.33.0`**（`2f35f4a08176`） | 下記の実測で全経路が通った |
| `comfyui-videohelpersuite` | `2984ec4c4b93292421888f38db74a5e8802a8ff8`（2026-04-06） | ワークフロー4本中3本がこの版で保存されている |
| `comfyui-gguf` (Isi-dev) | `1.1.10` | 全ワークフローで一致 |
| `comfyui-logicutils` | `1.7.2` | 同上 |
| `rgthree-comfy` | `1.0.2604070017` | 同上 |
| `comfyui_essentials` | `9d9f4bedfc9f0321c19faf71855e228c93bd0dc9` | 同上 |
| `comfyui-kjnodes` | `a6b867b63a29ca48ddb15c589e17a9f2d8530d57` | 同上 |
| `comfyui-frame-interpolation` | `26545cc2dd95bc3d27f056016300673bdeee78f5` | 同上 |
| `GACLove/ComfyUI-VFI` | `62c60feff88f651c24e12006567ba48260ab43aa` | 同上 |
| `princepainter/ComfyUI-PainterI2V` | `652565fc032c77855a99a941f2c3a33e603a8258` | I2V のみ使用 |
| `seedvr2_videoupscaler` | `4490bd1f482e026674543386bb2a4d176da245b9` | R2V / UpScale |

固定値は**ワークフローの `properties.ver` から機械的に抽出**した。
ComfyUI が保存時に記録する値なので、推測ではなく「そのワークフローが作られた環境」そのもの。

## 実測（2026-08-19 / Google Colab A100-SXM4-80GB / ComfyUI v0.33.0）

| 経路 | 結果 | 所要 | 出力 |
|---|---|---|---|
| Wan2.2 I2V | ✅ 実走 | 約208秒 | 640×816 |
| Wan2.2 FLF2V | ✅ 実走 | 約246秒 | 640×848 |
| Seedance2.0 R2V | ✅ 実走 | 約230秒 | 361フレーム / 864×496 |
| SeedVR2 アップスケール | ✅ 実走 | 約250秒 | 1254×720 |

Forge Classic（SDXL / ControlNet / ADetailer）は無料枠 T4 と有料 L4 の両方で実走。
T4 は**システムメモリ13GB**のため ControlNet のプリプロセッサ追加モデル読み込みで停止することがある
（`depth_anything` は初回に DINOv2 1.13GB を追加取得する）。L4 以上を推奨。

## なぜ v0.33.0 か

ワークフローの保存時バージョンは揃っていなかった。

| ワークフロー | 保存時の `comfy-core` | 日付 |
|---|---|---|
| Wan2.2 I2V | `v0.3.45` | 2025-07-21 |
| Wan2.2 FLF2V | `v0.3.45` | 2025-07-21 |
| Seedance2.0 R2V | `v0.20.1` | 2026-04-27 |

**約9か月の開き**がある。どちらかに寄せる必要があり、
`v0.3.45`（2025-07-21）は現在の最新から遠すぎる。

新しい側に寄せる判断は、**理屈ではなく上記の実測**による。
`v0.3.45` 時代に保存されたワークフローが、`v0.33.0` で問題なく動いた。

`v0.33.0` を提案するのは、**実際に4経路を通したのがこの版**だから。

:::caution v0.33.0 に GitHub Release はない
`v0.33.0` は **git タグとしてのみ存在**する（`2f35f4a08176`）。
リリースページは作られていないため、`/releases/tag/v0.33.0` を参照先にしない。

```bash
git clone --depth 1 --branch v0.33.0 https://github.com/comfyanonymous/ComfyUI   # 通る
```

同様に `v0.33.2`（`7cee3ceb1a35`）もタグのみで Release がない。
**Release がある最新は `v0.33.1`（2026-08-13）**。
上流はタグと Release を必ずしも対にしていないので、
固定値は**タグ名とコミットSHAの対**で持つこと。
:::

## MiniMax H3 ライン（`v0.31.0`）との関係

`notebooks/MiniMaxH3_Colab.ipynb` は `v0.31.0` に固定されている。
本提案は**それを置き換えるものではない**。対象モデルが異なり、検証も別に行われている。

同一の LTS ラインに統合できるかは、両方を同じ版で通してから判断すべき。
現時点では**モデル系統ごとに固定値を持つ**のが正直な状態だと考える。

## ブランチとタグの扱い

comfy-aicu の Nightly が現状これに相当する。
ブランチ（進行中）とタグ（確定）で分ければ足りるという整理。

```
nightly        … 追従。壊れることがある
LTS26.9        … タグ。書籍刊行時点の固定値
```

書籍は刷ったら直せないため、**刊行後は LTS26.9 を動かさない**。
改善は次のタグへ入れる。

## 参照

- 実測レポート: 道草雑草子氏「SG26 Notebook 動作確認報告」2026-08-19
- 静的検査と昇格ゲート: aicuai/comfy-aicu#29（private）
- 統合テスト: aicuai/Book-SG26#8

## モデルのライセンス（2026-08-20 実査）

HuggingFace API の `cardData.license` を機械的に取得したもの。
**「同梱してよいか」の判断は書かない。**材料だけ置く。

| 配布元 | license | 同梱の可否 |
|---|---|---|
| `Comfy-Org/Wan_2.2_ComfyUI_Repackaged` | `apache-2.0` | ✅ 問題なし |
| `Comfy-Org/Wan_2.1_ComfyUI_repackaged` | `apache-2.0` | ✅ 問題なし |
| `QuantStack/Wan2.2-I2V-A14B-GGUF` | `apache-2.0` | ✅ 上流 `Wan-AI/Wan2.2-I2V-A14B` も apache-2.0 |
| `QuantStack/Wan2.2-T2V-A14B-GGUF` | `apache-2.0` | ✅ 上流 `Wan-AI/Wan2.2-T2V-A14B` も apache-2.0 |
| `stabilityai/sdxl-vae` | `mit` | ✅ 問題なし |
| **`Kijai/WanVideo_comfy`** | **未指定** | ⚠️ 下記 |
| **`bluepen5805/mellow_pencil-XL`** | **`faipl-1.0-sd`** | ⚠️ 下記 |

### ⚠️ `Kijai/WanVideo_comfy` — ライセンス未指定

モデルカードに `license` フィールドがない。`base_model` に上流が記録されており、
[`Wan-AI/Wan2.1-VACE-14B`](https://huggingface.co/Wan-AI/Wan2.1-VACE-14B) は `apache-2.0`。

ただし**再配布者が明示していない**ため、コンテナへ同梱するなら作者への確認が要る。
参照（読者が各自ダウンロード）であれば上流の条件で足りる。

### ⚠️ `bluepen5805/mellow_pencil-XL` — Fair AI Public License 1.0-SD

[`faipl-1.0-sd`](https://freedevproject.org/faipl-1.0-sd/) は**コピーレフト系**。
派生物は同一ライセンスでの公開が要る。Stable Diffusion の Prohibited Uses と
互換になるよう設計された変種。

**同梱・再配布は条件付き。**参照（各自ダウンロード）が安全。

### Civitai

作者ごとに異なる。**RAIL-M 等の問題ないものを収録している。**
許諾フラグ（`Image` / `RentCivit` / `Rent` / `Sell`）の意味と個別の調査結果は、
comfy-aicu の `infra/tests/MODEL_LICENSE_REVIEW.md` にある。

> `CIVITAI_KEY` の「ダウンロードへのアクセス」を ON にしないと**静かに失敗**し、
> LoRA が効いていない結果が出る。読者に伝える必要がある。

### コンテナ化への含意

7件中5件は `apache-2.0` / `mit` で同梱に支障がない。
**残る2件が同梱の可否を分ける**ので、[Issue #5](../../issues/5) の
「モデルは同梱せず、環境だけコンテナ化」から始める案は、この結果とも整合する。

---

## 機械可読な台帳

この文書は読み物で、**正本は [`LTS26.9.yaml`](LTS26.9.yaml)** です。

```bash
tools/lts-resolve.py lts/LTS26.9.yaml --check      # 妥当性（CI が回す）
tools/lts-resolve.py lts/LTS26.9.yaml --sh         # bash のインストール手順
tools/lts-resolve.py lts/LTS26.9.yaml --notebook   # Colab セル用の定数
```

台帳は書いただけでは守られません。**そこから実際の手順を生成**して初めて、
台帳と環境が一致していると言えます。手で書いた手順は必ずずれます。

`--check` は `status: approved` で `license: unknown` が残っていると落とします。
ライセンス整理が ComfyLTS の存在理由なので、そこは通しません。
**現在7件が未確認です**（`proposed` のうちは警告のみ）。
