
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
