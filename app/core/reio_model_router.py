"""
REIŌ Native Model Router
========================

Architecture:

    OpenRouter Primary
    OpenRouter Secondary
    Ollama Assistant 1
    Ollama Assistant 2

This module intentionally contains no OmniRoute dependency.

The evidence/provenance layer remains authoritative.
LLM output is always treated as a candidate result.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config" / "reio_multi_model_routing.json"


class REIOModelRouter:
    """Native four-route REIŌ model router."""

    def __init__(self, config_path: Path = CONFIG_PATH):
        self.config_path = Path(config_path)

        with self.config_path.open(
            "r",
            encoding="utf-8",
        ) as handle:
            self.config = json.load(handle)

        self.routes = self.config["routes"]

    def route(self, route_name: str) -> dict[str, Any]:
        """Return configuration for a named route."""
        if route_name not in self.routes:
            raise KeyError(f"Unknown REIŌ route: {route_name}")

        route = self.routes[route_name]

        if not route.get("enabled", False):
            raise RuntimeError(
                f"REIŌ route is disabled: {route_name}"
            )

        return route

    def list_routes(self) -> dict[str, dict[str, Any]]:
        """Return all configured routes."""
        return self.routes

    def ollama_available(
        self,
        route_name: str,
        timeout: float = 2.0,
    ) -> bool:
        """Check whether an Ollama route is reachable."""
        route = self.route(route_name)

        if route["provider"] != "ollama":
            return False

        url = route["base_url"].rstrip("/") + "/api/tags"

        try:
            request = urllib.request.Request(
                url,
                method="GET",
            )

            with urllib.request.urlopen(
                request,
                timeout=timeout,
            ) as response:
                return response.status == 200

        except (
            urllib.error.URLError,
            TimeoutError,
            OSError,
        ):
            return False

    def environment_status(self) -> dict[str, Any]:
        """Return non-secret environment readiness."""
        return {
            "openrouter_api_key_present": bool(
                os.getenv("OPENROUTER_API_KEY")
            ),
            "ollama_assistant_1_reachable": self.ollama_available(
                "ollama_assistant_1"
            ),
            "ollama_assistant_2_reachable": self.ollama_available(
                "ollama_assistant_2"
            ),
        }


if __name__ == "__main__":
    router = REIOModelRouter()

    print("REIŌ Model Router")
    print("=" * 60)

    for name, route in router.list_routes().items():
        print(
            f"{name}: "
            f"{route['provider']} / {route['model']}"
        )

    print("=" * 60)
    print(json.dumps(
        router.environment_status(),
        indent=2,
    ))
