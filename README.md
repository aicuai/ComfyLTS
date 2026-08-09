# ComfyLTS

**A license-cleared, region-safe, long-term-support ComfyUI base — built and maintained by AICU Japan.**

> ComfyUI moves fast. Custom nodes drift. Model licenses are tangled. Third-party base
> images can revoke redistribution permission at any time. ComfyLTS exists so that you —
> and we — can run ComfyUI on a **stable, license-cleared, reproducible** foundation instead
> of rebuilding that trust from scratch every time.

## Why this exists

Running ComfyUI *well* in production turned out to be less about ComfyUI itself and more about
everything around it:

- **Version drift breaks things.** Bleeding-edge ComfyUI + auto-updating custom nodes means a
  restart can silently move versions and take the UI down (frontend/backend mismatch, deprecated
  APIs). An LTS line — pinned ComfyUI + frontend + torch — keeps a known-good stack.
- **Licenses are tangled.** Models (SD1.5/SDXL are OpenRAIL, MiniMax H3 has territorial limits,
  Animagine is OpenRAIL++…) and custom nodes (MIT/Apache/GPL/AGPL/unclear) each carry conditions.
  Shipping a container without clearing these is a legal risk. ComfyLTS classifies every bundled
  component and only ships what is safe to ship.
- **Third-party bases are a business risk.** Some popular ComfyUI base images use custom licenses
  where *"distribution of derived images requires the author's explicit permission, revocable at
  any time."* Building a commercial service on top of that is unstable regardless of anything else.
  ComfyLTS is built from **PyTorch's official image + a pinned ComfyUI**, under our own control.

The value is not any single image. It is **an accumulating body of know-how** — which quantized
models load, which nodes are safe to bake, which torch/CUDA build matches which GPU generation,
what breaks on upgrade — captured in a place we control.

## Where it's used

The same "safe, license-cleared ComfyUI base" is needed everywhere we run ComfyUI, not just one product:

- **ComfyPods** — AICU's browser-based, auth-gated GPU service. Age/region are established by AICU
  auth, so even region-restricted models (e.g. MiniMax H3, not for EU/UK/KR/US) can be offered
  compliantly to eligible users.
- **Google Colab** — notebooks that need a reproducible, license-clean ComfyUI without hand-assembling
  the stack each time. Same base, same guarantees.
- **RunPod / cloud bursts** — pull a public, license-cleared image with no per-token distribution
  overhead; fetch heavier or restricted models at runtime.
- **Anyone** who wants a ComfyUI they can trust to be stable and legally clean.

## Design principles

1. **Own the base.** `FROM pytorch/pytorch` + a pinned ComfyUI clone. No dependency on a
   permission-revocable third-party base.
2. **Pin the LTS line.** ComfyUI, `comfyui-frontend-package`, and torch/CUDA are pinned together so
   frontend and backend never drift apart. New upstream releases are evaluated deliberately, not
   auto-adopted.
3. **Don't bake what you can't distribute.** Restricted-license models (territorial / non-commercial)
   are **fetched at runtime**, never baked into a public image. The public image stays light; models
   arrive from a cold storage layer on demand.
4. **Clear every license.** Each bundled model and node is classified (allow / conditional / review).
   Conditional (OpenRAIL etc.) ships with full license text and use-restriction notices.
5. **Meet the obligations.** ComfyUI core and frontend are GPL-3.0; this repository is the
   corresponding-source home and the place to ship `NOTICE` / `THIRD-PARTY-LICENSES`.

## Naming

"Japan-region-loved, safe container." That's the whole idea — a ComfyUI base that people in and
beyond Japan can pull and trust. Built images are published to GitHub Container Registry as
`ghcr.io/aicuai/...`; **this repository is their source of record** (each image's
`org.opencontainers.image.source` points here) and the channel for **support, change requests,
and bug reports via GitHub Issues**.

## Notebooks

Reproducible, well-documented notebooks that exercise the ComfyLTS stack live in [`notebooks/`](notebooks/):

- **[`notebooks/MiniMaxH3_Colab.ipynb`](notebooks/MiniMaxH3_Colab.ipynb)** — run **MiniMax H3** audio+video
  generation on Google Colab against a pinned **ComfyUI 0.31.0**. Documents the verified quality config from
  our RTX 4000 Ada 20 GB runs (int8 UNET + fp16 video VAE + SageAttention + **20-step, no turbo LoRA**), the
  H3 frame-count rule (`length = 5 + 17n`), model downloads from `Comfy-Org/MiniMax-H3`, and honest GPU
  requirements (A100 40 GB recommended; free-tier **T4 16 GB is not enough** for the full stack).
  ⚠️ **License:** the MiniMax H3 Community License is region-restricted (**not for EU/UK/Korea/US**); the
  notebook is for **evaluation** only. Production serving gates region/age via AICU auth in **ComfyPods**.

## Status

Early. This repository starts as the **vision and knowledge base**; the pinned build and the public
image follow once the base is migrated off the third-party dependency and the license/GPL obligations
are packaged. Track the strategy and progress in the AICU infrastructure repos.

---

*ComfyUI is © its authors, licensed under GPL-3.0. ComfyLTS is an AICU Japan effort to package and
maintain a stable, license-cleared distribution of it; it is not affiliated with or endorsed by the
upstream ComfyUI project.*
