# REIŌ Model Architecture

## Active Architecture

REIŌ uses four model routes:

1. OpenRouter Primary — Claude Sonnet 4.5
2. OpenRouter Secondary — GPT-5.4
3. Ollama Assistant 1 — Qwen3
4. Ollama Assistant 2 — Llama 3.1 8B

## Data Authority

LLM output is never considered authoritative evidence.

The authoritative chain remains:

Source
→ MarkItDown
→ normalized document
→ SHA-256
→ segment
→ evidence
→ cognitive pattern
→ ANN representation
→ training candidate

## Model Responsibilities

### OpenRouter Primary

Used for:

- deep reasoning
- cognitive pattern analysis
- complex evidence interpretation
- research-oriented reasoning

### OpenRouter Secondary

Used for:

- independent structured reasoning
- candidate generation
- schema generation
- verification

### Ollama Assistant 1

Model:

`qwen3:latest`

Used for:

- local preprocessing
- classification
- formatting
- lightweight reasoning

### Ollama Assistant 2

Model:

`llama3.1:8b`

Used for:

- local validation
- consistency checks
- schema validation
- candidate review

## Fallback

If an OpenRouter route is unavailable, REIŌ may use an Ollama assistant for suitable tasks.

If Ollama is unavailable, REIŌ may use an OpenRouter route.

If all model routes are unavailable, REIŌ must return a controlled failure.

REIŌ must never fabricate source evidence.

## OmniRoute

OmniRoute is removed from the active REIŌ architecture.

No active REIŌ component should depend on OmniRoute.
