#!/usr/bin/env python3

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.reio_runtime import runtime_report


def main() -> int:
    report = runtime_report()
    runtime = report['runtime']
    ollama = report['ollama']
    models = report['required_models']
    architecture = report['architecture']

    print('=' * 80)
    print('REIŌ — PORTABLE RUNTIME HEALTH CHECK')
    print('=' * 80)

    print('[ENVIRONMENT]')
    print('Environment      :', runtime['environment'])
    print('Python           :', runtime['python_version'])
    print('Platform         :', runtime['platform'])
    print('Machine          :', runtime['machine'])
    print('Project root     :', runtime['project_root'])

    print('[GPU]')
    print('Available        :', runtime['gpu_available'])
    print('Device           :', runtime['gpu_name'])

    print('[OLLAMA]')
    print('Binary           :', runtime['ollama_binary'])
    print('Endpoint         :', runtime['ollama_url'])
    print('Reachable        :', ollama['reachable'])

    if ollama['reachable']:
        print('Installed models :', len(ollama['models']))
    else:
        print('Error            :', ollama['error'])

    print('[MODELS]')
    print('Qwen3            :', models['qwen3'])
    print('Llama 3.1        :', models['llama3'])

    print('[OPENROUTER]')
    print('Runtime key      :', runtime['openrouter_key_present'])
    print('Persistence      : DISABLED')

    print('[ARCHITECTURE]')
    print('Router           :', architecture['router'])
    print('Execution        :', architecture['execution'])
    print('OpenRouter       :', architecture['openrouter'])
    print('Ollama           :', architecture['ollama'])
    print('OmniRoute        :', architecture['omniroute'])
    print('Ruflo            :', architecture['ruflo'])

    ready = (
        ollama['reachable']
        and models['qwen3']
        and models['llama3']
    )

    print('=' * 80)

    if ready:
        print('[PASS] Runtime infrastructure READY')
        return 0

    print('[INFO] Runtime infrastructure incomplete')
    print('[INFO] This is allowed on machines without Ollama/models.')
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
