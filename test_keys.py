#!/usr/bin/env python3
"""Send one tiny chat request to every provider that has a key in .env and report PASS/FAIL.

Usage:  python3 test_keys.py            # all providers
        python3 test_keys.py groq nvidia  # only these
The .env file is read from the script's directory (override with ENV_FILE=/path/to/.env).
Standard library only.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.environ.get("ENV_FILE", os.path.join(HERE, ".env"))

if os.path.exists(ENV_FILE):
    for line in open(ENV_FILE):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

E = os.environ.get

# name: (base_url, key env var, test model)
PROVIDERS = {
    "sensenova":    ("https://token.sensenova.ai/v1", "SENSENOVA_API_KEY", "sensenova-6.8-flash-lite"),
    "gemini":       ("https://generativelanguage.googleapis.com/v1beta/openai", "GEMINI_API_KEY", "gemini-flash-lite-latest"),
    "zai":          ("https://api.z.ai/api/paas/v4", "ZAI_API_KEY", "glm-4.5-flash"),
    "cloudflare":   (f"https://api.cloudflare.com/client/v4/accounts/{E('CLOUDFLARE_ACCOUNT_ID')}/ai/v1",
                     "CLOUDFLARE_API_TOKEN", "@cf/meta/llama-3.3-70b-instruct-fp8-fast"),
    "groq":         ("https://api.groq.com/openai/v1", "GROQ_API_KEY", "openai/gpt-oss-20b"),
    "openrouter":   ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY", "openrouter/free"),
    "cohere":       ("https://api.cohere.ai/compatibility/v1", "COHERE_API_KEY", "command-a-03-2025"),
    "sambanova":    ("https://api.sambanova.ai/v1", "SAMBANOVA_API_KEY", "gemma-4-31B-it"),
    "requesty":     ("https://router.requesty.ai/v1", "REQUESTY_API_KEY", "google/gemma-4-31b-it"),
    "mistral":      ("https://api.mistral.ai/v1", "MISTRAL_API_KEY", "ministral-8b-latest"),
    "nvidia":       ("https://integrate.api.nvidia.com/v1", "NVIDIA_API_KEY", "openai/gpt-oss-20b"),
    "kilo":         ("https://api.kilo.ai/api/gateway", "KILO_API_KEY", "kilo-auto/free"),
    "pollinations": ("https://gen.pollinations.ai/v1", "POLLINATIONS_API_KEY", "openai/gpt-5.4-nano"),
    "llmkiwi":      ("https://api.llm.kiwi/v1", "LLMKIWI_API_KEY", "auto"),
    # One-time signup credit only (HTTP 402 once it is spent); not a recurring free tier.
    "siliconflow":  ("https://api.siliconflow.com/v1", "SILICONFLOW_API_KEY", "Qwen/Qwen3-8B"),
}


def test(name, base, key, model):
    body = {"model": model, "max_tokens": 400,
            "messages": [{"role": "user", "content": "Reply with exactly: OK"}]}
    if name == "sensenova":  # always reasons; max_tokens also caps the reasoning
        body.update(max_tokens=3000, reasoning_effort="none")
    req = urllib.request.Request(
        base + "/chat/completions", data=json.dumps(body).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": "curl/8"})
    t = time.time()
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            d = json.load(r)
        text = (d["choices"][0]["message"].get("content") or "").strip().replace("\n", " ")[:40]
        return f"PASS  {time.time() - t:5.1f}s  {text!r}"
    except urllib.error.HTTPError as e:
        return f"FAIL  HTTP {e.code}  {e.read()[:160].decode(errors='replace')}"
    except Exception as e:  # network errors, timeouts
        return f"FAIL  {e}"


def main():
    only = sys.argv[1:]
    for name, (base, env, model) in PROVIDERS.items():
        if only and name not in only:
            continue
        key = E(env)
        if not key:
            print(f"{name:13} SKIP  ({env} not set)")
            continue
        print(f"{name:13} {model:42} {test(name, base, key, model)}", flush=True)


if __name__ == "__main__":
    main()
