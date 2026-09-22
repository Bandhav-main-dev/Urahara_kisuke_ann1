
"""
REIŌ Model Gateway
==================

Application-level multi-model fallback gateway.

Design:

    REIŌ task
       |
       v
    Model 1
       |
       +-- success --> result
       |
       +-- fallback error --> Model 2
                              |
                              +--> Model 3
                                     |
                                     +--> Model 4

API credentials are supplied at runtime.

The gateway intentionally keeps provider/model routing separate
from REIŌ's cognitive data pipeline.
"""

from __future__ import annotations

import os
import time
from typing import Any, Dict, List

import requests


OPENROUTER_ENDPOINT = (
    "https://openrouter.ai/api/v1/chat/completions"
)


DEFAULT_MODELS = [

    "anthropic/claude-sonnet-4.5",

    "openai/gpt-5.4",

    "google/gemini-2.5-pro",

    "deepseek/deepseek-chat"

]


def _fallback_error(
    status_code: int | None,
    text: str
) -> bool:

    text = str(text).lower()

    if status_code in {
        408,
        409,
        425,
        429,
        500,
        502,
        503,
        504
    }:

        return True

    keywords = [

        "rate limit",
        "rate_limit",
        "too many requests",
        "quota",
        "insufficient",
        "capacity",
        "overloaded",
        "temporarily unavailable",
        "timeout",
        "timed out",
        "provider error",
        "upstream error",
        "credits"

    ]

    return any(
        item in text
        for item in keywords
    )


class REIOModelGateway:

    def __init__(
        self,
        api_key: str | None = None,
        models: List[str] | None = None,
        timeout: int = 120
    ):

        self.api_key = (
            api_key
            or os.environ.get(
                "OPENROUTER_API_KEY"
            )
        )

        if not self.api_key:

            raise ValueError(
                "OPENROUTER_API_KEY is required."
            )

        self.models = (
            models
            or list(DEFAULT_MODELS)
        )

        self.timeout = timeout

    def _headers(self) -> Dict[str, str]:

        return {

            "Authorization":
                "Bearer " + self.api_key,

            "Content-Type":
                "application/json",

            "User-Agent":
                "REIO-URAHARA-ANN001/1.0",

            "HTTP-Referer":
                "https://github.com",

            "X-Title":
                "REIO-URAHARA-ANN001"

        }

    def call(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0,
        max_tokens: int = 100
    ) -> Dict[str, Any]:

        attempts = []

        for index, model in enumerate(
            self.models,
            start=1
        ):

            started = time.time()

            payload = {

                "model":
                    model,

                "messages":
                    messages,

                "temperature":
                    temperature,

                "max_tokens":
                    max_tokens

            }

            try:

                response = requests.post(

                    OPENROUTER_ENDPOINT,

                    headers=self._headers(),

                    json=payload,

                    timeout=self.timeout

                )

                latency = round(
                    time.time() - started,
                    3
                )

                try:

                    data = response.json()

                except Exception:

                    data = {}

                if response.status_code == 200:

                    choices = data.get(
                        "choices",
                        []
                    )

                    content = ""

                    if choices:

                        content = str(
                            choices[0]
                            .get("message", {})
                            .get("content", "")
                        )

                    result = {

                        "success":
                            True,

                        "selected_model":
                            data.get(
                                "model",
                                model
                            ),

                        "requested_model":
                            model,

                        "attempt_number":
                            index,

                        "attempts":
                            attempts,

                        "content":
                            content,

                        "usage":
                            data.get("usage"),

                        "latency_seconds":
                            latency

                    }

                    return result

                error = data.get(
                    "error",
                    response.text[:1000]
                )

                error_text = str(
                    error
                )

                attempt = {

                    "success":
                        False,

                    "model":
                        model,

                    "status_code":
                        response.status_code,

                    "latency_seconds":
                        latency,

                    "fallback_eligible":
                        _fallback_error(
                            response.status_code,
                            error_text
                        ),

                    "error":
                        error_text[:2000]

                }

                attempts.append(
                    attempt
                )

                if not attempt[
                    "fallback_eligible"
                ]:

                    break

            except requests.Timeout as exc:

                attempts.append({

                    "success":
                        False,

                    "model":
                        model,

                    "status_code":
                        None,

                    "latency_seconds":
                        round(
                            time.time() - started,
                            3
                        ),

                    "fallback_eligible":
                        True,

                    "error":
                        f"Timeout: {exc}"

                })

            except Exception as exc:

                attempts.append({

                    "success":
                        False,

                    "model":
                        model,

                    "status_code":
                        None,

                    "latency_seconds":
                        round(
                            time.time() - started,
                            3
                        ),

                    "fallback_eligible":
                        True,

                    "error":
                        str(exc)[:2000]

                })

        return {

            "success":
                False,

            "selected_model":
                None,

            "requested_model":
                None,

            "attempt_number":
                len(attempts),

            "attempts":
                attempts,

            "content":
                None,

            "usage":
                None

        }
    def call_native(
        self,
        messages,
        model,
        provider=None,
        temperature=0,
        max_tokens=100,
        timeout=180,
    ):
        """
        Native REIŌ provider-aware gateway.

        Supported providers:
          - openrouter
          - ollama

        Qwen3 explicitly disables thinking for short ANN pipeline
        requests so the generation budget is not consumed by reasoning.
        """
        import os
        import requests

        if not model:
            raise ValueError("model is required")

        if provider is None:
            if model.startswith("anthropic/") or model.startswith("openai/"):
                provider = "openrouter"
            else:
                provider = "ollama"

        provider = str(provider).strip().lower()

        # --------------------------------------------------------------
        # OPENROUTER
        # --------------------------------------------------------------
        if provider == "openrouter":

            api_key = os.environ.get(
                "OPENROUTER_API_KEY",
                ""
            ).strip()

            if not api_key:
                raise RuntimeError(
                    "OPENROUTER_API_KEY is not available in runtime."
                )

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": (
                    "https://github.com/"
                    "Bandhav-main-dev/Urahara_kisuke_ann1"
                ),
                "X-Title": "REIO Urahara Kisuke ANN #001",
            }

            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=timeout,
            )

            response.raise_for_status()

            data = response.json()

            choices = data.get("choices") or []

            if not choices:
                raise RuntimeError(
                    f"OpenRouter returned no choices: {data}"
                )

            message = choices[0].get("message") or {}

            content = message.get("content") or ""

            if not content:
                raise RuntimeError(
                    "OpenRouter returned empty content."
                )

            return {
                "provider": "openrouter",
                "model": model,
                "content": content,
                "raw": data,
            }

        # --------------------------------------------------------------
        # OLLAMA
        # --------------------------------------------------------------
        if provider == "ollama":

            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            }

            # IMPORTANT:
            # Qwen3 previously consumed the entire small generation
            # budget in its thinking channel.
            if model.startswith("qwen3"):
                payload["think"] = False

            response = requests.post(
                "http://127.0.0.1:11434/api/chat",
                json=payload,
                timeout=timeout,
            )

            response.raise_for_status()

            data = response.json()

            message = data.get("message") or {}

            content = message.get("content") or ""

            # Compatibility with generate-style responses.
            if not content:
                content = data.get("response") or ""

            if not content:
                raise RuntimeError(
                    f"Ollama returned empty content: {data}"
                )

            return {
                "provider": "ollama",
                "model": model,
                "content": content,
                "raw": data,
            }

        raise ValueError(
            f"Unsupported native provider: {provider}"
        )
