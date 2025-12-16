# Future of This Project

I want to organize some thoughts about the future of this repository and project, in the form of a ROADMAP.

---

## Where We Are Now

### We are currently on v0.2.0b2

This repo is published to PyPI (pre-release) and users can install it, but it is untested and not guaranteed to be stable—even though it is passing all tests. 0.1.0 is stable and on PyPI, but only contained the _image-processing_ module.

I screwed up the release of 0.2.0 and had to yank it, so the next stable will be **v0.2.1**.

### The Bigger Picture

There are actually three legacy codebases that feed into this project:

1. **semiautomatic** (this repo) — The core library. General-purpose tools for creative AI workflows. This is what gets published to PyPI.

2. **semiautomatic-legacy** — The previous monolith. It contained what is now semiautomatic core, plus aesthetics-specific tools, plus the HuggingFace dataset/model tracking. Needs to be decomposed.

3. **semi_utils** — An even older project predating semiautomatic-legacy. Contains ~40 utility scripts, some of which are valuable and never made it forward.

The goal is to:
- Stabilize and ship semiautomatic as a clean, well-documented core library
- Extract aesthetics-specific work into a new project called **aesthetics-lab** (powered by semiautomatic)
- Triage the legacy tools and migrate the valuable ones forward

---

## Phase 1: Stabilize & Ship

### Step 1: Release v0.2.1 to PyPI

I want to release this version as stable—but I need to thoroughly test it as a user before proceeding. I'm using aesthetics-lab as my test project, which also becomes the future home for aesthetics-specific tooling.

- [x] Create aesthetics-lab repository
- [ ] Setup pyproject.toml with semiautomatic as dependency
- [ ] Establish project structure
- [ ] Create initial README explaining scope (aesthetics-specific, not general-purpose)
- [ ] Follow all of the semiautomatic tutorials (final pass on the text)
- [ ] Log any bugs
- [ ] Final CHANGELOG.md review
- [ ] Merge to main
- [ ] Tag v0.2.1
- [ ] Publish to PyPI

---



---

## Phase 2: Triage & Audit

Before migrating tools, I need to audit what exists and decide where each thing goes.

### Audit Framework

For each tool, determine:
- **Destination:** `semiautomatic` (core) | `aesthetics-lab` | `deprecate`
- **Overlap:** Does this functionality already exist in semiautomatic v0.2.1?
- **Complexity:** How much work to migrate?
- **Notes:** Any dependencies, design decisions needed, etc.

### Audit: semiautomatic-legacy

The following tools/modules exist in semiautomatic-legacy and need to be classified:

**Aesthetics-specific tools** (likely → aesthetics-lab):
- [ ] catalog generator script
- [ ] day runner script
- [ ] aesthetics-scorecard
- [ ] aesthetic_intents_to_images (and its recraft variant)
- [ ] aesthetic_images_to_videos
- [ ] aesthetic-judge
- [ ] prep-dataset
- [ ] train-lora

**Potentially general-purpose tools** (audit for core vs deprecate):
- [ ] post-production module (crt, degrade, glitch, grainify)
- [ ] get-captions — *compare to Vision & Captioning in v0.2.1*
- [ ] text-rendering
- [ ] scraper
- [ ] video-tools/ace.py
- [ ] video-tools/stack.py
- [ ] video-tools/stitch.py

**Pipelines** (need careful audit—may overlap with core):
- [ ] concat_chain — *does video processing in core cover this?*
- [ ] generate_chain — *does this just orchestrate generate-image/video?*
- [ ] restyle_video — *what does this actually do?*

### Audit: semi_utils

These are older tools that never made it to semiautomatic-legacy. Many are probably superseded or deprecated, but some may be valuable.

**Likely superseded by semiautomatic core** (verify and deprecate):
- freepik_generate_image
- getcaptions
- getimage
- getprompts
- getvideo
- grab_frame
- img_converter
- magnific_upscale
- processVideo
- prompttools
- resize_image

**Potentially valuable** (audit for migration):
- topaz-enhance
- topaz_video_enhance
- compare_images
- cropper
- detect_beats
- dither
- editimage
- pixelsort
- gifMaker
- scraper
- strip_metadata
- vidOptimizer
- viewComfy_api
- ostris_trainer

**Probably deprecate** (one-offs, outdated, or unclear purpose):
- full_clip
- generate_widget
- getaudio
- getsequence
- getwidget
- google_test
- imgtools
- num_widget
- prep_filenames
- prompt_copy
- sandbox
- temp

### Audit Output

After completing the audits, produce a prioritized migration backlog organized into waves:

- **Wave 1:** High-value, low-complexity, no blockers
- **Wave 2:** Medium complexity or has dependencies on Wave 1
- **Wave 3:** High complexity, requires design decisions

---

## Phase 3: Migration Waves

Once the audits are complete and the backlog is prioritized, migration happens in waves. Each wave is an independently shippable increment.

### Wave Template

For each tool being migrated:
- [ ] Extract from legacy codebase
- [ ] Adapt to target project structure (semiautomatic or aesthetics-lab)
- [ ] Add/update tests
- [ ] Add CLI command if applicable
- [ ] Document
- [ ] PR and merge

Each wave culminates in a release (semiautomatic vX.X.X or aesthetics-lab vX.X.X).

### Preliminary Wave Assignments (to be refined after audit)

**Wave 1 Candidates** (likely quick wins):
- post-production module → semiautomatic
- text-rendering → semiautomatic
- video-tools (stack, stitch) → semiautomatic

**Wave 2 Candidates** (medium effort):
- scraper → semiautomatic
- aesthetic-judge → aesthetics-lab
- aesthetics workflow tools → aesthetics-lab

**Wave 3 Candidates** (needs design work):
- Pipelines (after determining if redundant)
- train-lora → aesthetics-lab
- prep-dataset → aesthetics-lab

---

## Future Considerations

- Development of an edit-image module for semiautomatic
- Integration patterns between semiautomatic and aesthetics-lab

### HuggingFace: Fix Warning & Publishing Strategy

**The problem:** Current aesthetics repo is Dataset type but contains safetensors. HF warns about this. You can't change repo type after creation.

**To fix the warning (~1 hour):**
1. Create new Model repo (e.g., `darylanselmo/semiautomatic-aesthetics`)
2. Push everything from old repo to new repo
3. Update sync-aesthetics to point to new repo
4. Delete old Dataset repo

**When publishing an aesthetic:**
1. Create public Model repo: `darylanselmo/aesthetic-{name}`
2. Copy that specific aesthetic's files (safetensors + dataset)
3. Write a README
4. Done

Private dev repo structure doesn't constrain publishing structure. Publish one aesthetic at a time, however makes sense for that release.

---

## Agent Instructions

This document will be used to coordinate work across multiple Claude Code agents:

**semiautomatic agent:** Has full context on the core library scope and vision. When auditing legacy tools, assess against v0.2.1 capabilities (see README). Flag overlaps explicitly. Output structured audit results.

**semi_utils agent:** Generate inventory with brief description of each tool's actual functionality (not just the name). Flag anything that appears superseded by semiautomatic core.

**aesthetics-lab agent:** Once scaffolded, receives migrated aesthetics tools. Maintains clear dependency on semiautomatic—no duplicating core functionality.

**Coordination:** Agents output structured audit tables. I (Daryl) consolidate, validate, and prioritize. Then I assign migration tasks back to the appropriate agent.
