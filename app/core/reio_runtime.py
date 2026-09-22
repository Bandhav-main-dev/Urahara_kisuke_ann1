# REIŌ Portable Runtime Layer

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import urllib.request

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


DEFAULT_OLLAMA_URL = 'http://127.0.0.1:11434'

DEFAULT_MODELS = {
    'qwen3': 'qwen3:latest',
    'llama3': 'llama3.1:8b',
}


@dataclass(frozen=True)
class RuntimeInfo:
    environment: str
    python_version: str
    platform: str
    machine: str
    project_root: str
    gpu_available: bool
    gpu_name: str | None
    ollama_binary: str | None
    ollama_url: str
    openrouter_key_present: bool


def project_root() -> Path:
    configured = os.getenv('REIO_PROJECT_ROOT')
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(__file__).resolve().parents[2]


def detect_environment() -> str:
    if os.getenv('COLAB_RELEASE_TAG') or Path('/content/drive').exists():
        return 'colab'
    if os.getenv('KAGGLE_KERNEL_RUN_TYPE'):
        return 'kaggle'
    if os.getenv('CODESPACES'):
        return 'codespaces'
    if os.getenv('GITHUB_ACTIONS'):
        return 'github_actions'
    return 'local_or_server'


def detect_gpu() -> tuple[bool, str | None]:
    try:
        import torch
        if torch.cuda.is_available():
            return True, str(torch.cuda.get_device_name(0))
    except Exception:
        pass

    nvidia = shutil.which('nvidia-smi')
    if nvidia:
        try:
            result = subprocess.run(
                [nvidia, '--query-gpu=name', '--format=csv,noheader'],
                capture_output=True,
                text=True,
                timeout=5,
                check=False
            )
            names = [
                x.strip()
                for x in result.stdout.splitlines()
                if x.strip()
            ]
            if names:
                return True, names[0]
        except Exception:
            pass

    return False, None


def ollama_url() -> str:
    return os.getenv(
        'REIO_OLLAMA_URL',
        DEFAULT_OLLAMA_URL
    ).rstrip('/')


def openrouter_key_present() -> bool:
    return bool(os.getenv('OPENROUTER_API_KEY', '').strip())


def find_ollama_binary() -> str | None:
    return shutil.which('ollama')


def check_ollama(timeout: float = 5.0) -> dict[str, Any]:
    url = ollama_url() + '/api/tags'
    result = {
        'url': url,
        'reachable': False,
        'models': [],
        'error': None
    }

    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            payload = json.loads(response.read().decode('utf-8'))

        result['reachable'] = True
        result['models'] = [
            item.get('name')
            for item in payload.get('models', [])
            if item.get('name')
        ]

    except Exception as exc:
        result['error'] = str(exc)

    return result


def check_required_models() -> dict[str, Any]:
    status = check_ollama()
    installed = set(status.get('models', []))

    required = [
        DEFAULT_MODELS['qwen3'],
        DEFAULT_MODELS['llama3']
    ]

    return {
        'ollama_reachable': status['reachable'],
        'qwen3': DEFAULT_MODELS['qwen3'] in installed,
        'llama3': DEFAULT_MODELS['llama3'] in installed,
        'installed_models': sorted(installed),
        'missing': [x for x in required if x not in installed]
    }


def runtime_info() -> RuntimeInfo:
    gpu_available, gpu_name = detect_gpu()

    return RuntimeInfo(
        environment=detect_environment(),
        python_version=platform.python_version(),
        platform=platform.system(),
        machine=platform.machine(),
        project_root=str(project_root()),
        gpu_available=gpu_available,
        gpu_name=gpu_name,
        ollama_binary=find_ollama_binary(),
        ollama_url=ollama_url(),
        openrouter_key_present=openrouter_key_present()
    )


def runtime_report() -> dict[str, Any]:
    return {
        'runtime': asdict(runtime_info()),
        'ollama': check_ollama(),
        'required_models': check_required_models(),
        'architecture': {
            'router': 'native',
            'execution': 'sequential',
            'openrouter': True,
            'ollama': True,
            'omniroute': False,
            'ruflo': False
        }
    }
