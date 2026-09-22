# REIŌ Portable Runtime

## Purpose

REIŌ is designed so Google Colab is a development and testing
environment rather than a permanent project dependency.

Supported environments:

- Google Colab
- Local development machines
- GPU servers
- CPU environments where performance permits

## Active architecture

REIŌ uses a native sequential model gateway.

```text
                    REIŌ
                      |
                Native Router
                      |
          +-----------+-----------+
          |                       |
      OpenRouter               Ollama
          |                       |
    +-----+-----+           +-----+-----+
    |           |           |           |
 Claude 4.5   GPT-5.4     Qwen3      Llama 3.1
```

Execution order:

Claude 4.5
    |
GPT-5.4
    |
Qwen3
    |
Llama 3.1

OmniRoute and Ruflo are not active components.

## Environment variables

- REIO_PROJECT_ROOT
- REIO_OLLAMA_URL
- OPENROUTER_API_KEY

OPENROUTER_API_KEY is runtime-only.

It must not be written to source files, configuration, reports,
Git history, or repository files.

## Ollama models

- qwen3:latest
- llama3.1:8b

Model weights remain outside Git.

## Health check

Run:

python scripts/reio_healthcheck.py

## Portability rule

Core REIŌ code must not depend on /content, Google Colab, or Tesla T4.

Colab-specific setup belongs in development/bootstrap tooling.
