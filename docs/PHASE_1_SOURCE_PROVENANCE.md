# REIŌ — Urahara Kisuke ANN #001

## Phase 1 — Source & Provenance

Phase 1 establishes the source ingestion, extraction,
evidence and provenance layer.

## Pipeline

```text
Source
  ↓
MarkItDown
  ↓
Raw Markdown
  ↓
SHA-256
  ↓
Evidence Segments
  ↓
Provenance
  ↓
Validation
```

## Important Rules

- Phase 1 does not train ANN #001.
- Phase 1 does not infer hidden thoughts.
- Phase 1 does not assign IQ.
- Phase 1 does not automatically declare CANON.
- Extracted evidence starts as REVIEW.
- Historical facts are not automatically cognitive training data.

## Evidence Classes

- CANON
- RECONSTRUCTED
- SYNTHETIC
- REVIEW

Phase 1 defaults extracted evidence to REVIEW.

## Output Structure

```text
data/phase1_source_provenance/
├── raw_markdown/
├── evidence/
│   ├── evidence.jsonl
│   └── evidence_review.md
├── sources/
│   └── source_registry.json
├── quarantine/
├── review/
├── manifests/
│   ├── extraction_manifest.json
│   └── rejected_quarantine.json
└── logs/
```

## Extraction Engine

Microsoft MarkItDown.

## Run Information

- Run ID: `20260918_092909`
- Sources registered: 0
- Sources extracted: 0
- Evidence records: 0
- Rejected/quarantined: 0

## Next Phase

Phase 2 — Urahara Knowledge Representation.
