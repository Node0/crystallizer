# Crystallizer

**A provenance-first research engine for serious primary-source corpora.**

> 🚧 **Major rearchitecture underway.** Much of this document describes where Crystallizer is heading, not what ships today. See [Status](#status) for what's locked, what's in progress, and what's still being designed. The legacy Python tool at the bottom of this README is what actually runs right now.

Crystallizer started as a Map → Reduce insight-extraction tool: chunk a long document, run each piece through an LLM, merge the results. That worked, but it had no memory of a source's structure, no way to prove a claim traced back to a specific page, and no way to get smarter as research accumulated across missions.

The project is being rebuilt around a different premise: **research on serious primary sources requires knowing exactly where every claim came from — down to the character offset on a specific physical page** — and that this fidelity is what makes deep automation trustworthy enough to run, largely unsupervised, across corpora spanning thousands of scanned pages.

## What's changing

**One frontend, one substrate, one binary.**
- **DiamondJS** is now the shared frontend framework across every project in the Liminaris umbrella, Crystallizer included — no longer a Crystallizer-specific choice.
- **SurrealDB**, vendored as a single binary, replaces the prior database layer as Crystallizer's unified store for documents, vectors, and graph relationships (citations, lineage) — no separate vector DB, no JSONB foreign-key arrays standing in for real edges.
- **Morphic**, previously a standalone OCR/document-structure tool, is being folded in as Crystallizer's ingestion subsystem rather than something called out to externally — it ships inside, running as a PyInstaller sidecar behind a JSON-over-stdio boundary.
- The whole system compiles to a **single Bun binary**, with callable dependencies packaged to work as installed rather than assembled from a pip/npm scavenger hunt.

**Provenance is structural, not aspirational.**
Every scanned page runs through a deterministic spine — Tesseract OCR plus ONNX layout/table detection — before any LLM touches it. Each span of extracted text carries a *locus* with four independently computed coordinates (canonical codepoint offset, line/column, physical bounding box, literary folio) plus a self-verifying quote anchor. A page cannot produce citable content until it clears quarantine — that's enforced by the schema itself, not by convention.

Fidelity is tracked as separate component scores — text, layout, reading order, table structure — combined multiplicatively rather than blended into one fuzzy number, so a badly reconstructed table can't quietly launder a page's overall score.

**LLM-accelerated quarantine is load-bearing, not a hedge.**
When the deterministic spine can't resolve a page with confidence, an LLM tier resolves it — batched by document and issue type, using the first approved fix as a worked example for the rest, escalating from a fast local model to a stronger one only when needed. This isn't a convenience fallback with manual editing as the "real" path; for corpora at the scale Crystallizer targets, LLM-first remediation is what makes ingestion tractable at all.

**Built against archival-grade sources, not toy PDFs.**
This design isn't theoretical. It's being shaped in parallel with an actual project: unbinding and scanning physical books at full color fidelity, chapter by chapter, toward a multi-thousand-page corpus of primary neuroscience texts. That discipline — accounting for every physical page, preserving provenance through OCR, catching fidelity loss before it silently compounds across a corpus — is exactly what a tool built for serious primary sources has to earn, not just claim.

**Research value compounds instead of resetting.**
Each research mission produces "crystals" — synthesized insight objects tied back to the exact sources that produced them. The source corpus stays fixed, but the crystal layer accumulates on top of it: the more missions you run, the more interpretive value sits on the same frozen books. That's the core move — mutable insight over immutable sources — that separates Crystallizer from single-shot summarization tools.

## Next-generation retrieval (in active design, not yet locked)

The newest architectural thread — still being worked through, not schema yet — asks whether corpus retrieval should get a term-level index alongside vector search: a concept vocabulary at the corpus level, typed postings distinguishing where a term merely appears from where it's meaningfully discussed, and two-signal retrieval that confirms a vector-similarity hit against exact term co-presence before trusting it. Serious nonfiction books already ship with authorial back-of-book indexes — part of the open question is whether that human-curated index can seed and evaluate an automated one, rather than going unused. This is honestly still open, but it's the direction the last few design sessions have converged on, and it's the kind of capability the rest of the rearchitecture is making room for.

## Status

| | |
|---|---|
| **Locked** | SurrealDB schema (7 core tables), four-locus provenance system, multiplicative fidelity formula, quarantine remediation design, ingest UX spec, Bun/TypeScript/DiamondJS stack |
| **In progress** | Morphic-as-sidecar implementation, single-binary packaging |
| **In design (unlocked)** | Corpus-level concept vocabulary, typed postings, two-signal retrieval |
| **Legacy (being replaced)** | The Python CLI and config format below |

## Legacy usage (current, pre-migration)

This is what actually runs today, ahead of the Bun/SurrealDB rewrite landing.

### Installation

**Requirements**: Python 3.11+

```bash
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python crystallizer.py --help
```

### Usage

```bash
python crystallizer.py \
  --system-prompt system_prompt.j2 \
  --haystack-path ./chat_logs \
  --connection ollama-local \
  --task-label gluon_design \
  --output-dir ./crystals
```

### Configuration

```json
{
  "inference_service_connections": {
    "ollama-local": {
      "api_type": "ollama",
      "base_url": "http://localhost:11434",
      "default_model": "qwen2.5-coder:32b",
      "default_ctx_len": 18000
    },
    "openai-main": {
      "api_type": "openai",
      "base_url": "https://api.openai.com/v1",
      "api_key": "sk-...",
      "default_model": "gpt-4o-mini",
      "default_ctx_len": 128000
    }
  }
}
```

### Legacy feature set

- **Token-Aware Windowing** — chunks large documents to fit LLM context limits
- **Multi-Provider Support** — Ollama (local) and OpenAI (cloud) backends
- **Template-Driven Prompts** — Jinja2 templates for custom system prompts
- **Hierarchical Processing** — 3-segment micro-windowing with merge strategies
- **Professional Logging** — semantic progress tracking with contextual semaphores
- **Batch Processing** — single files or entire directories

## License
GNU AGPLv3