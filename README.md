# Free LLM API list

LLM providers that give a **free API key with a recurring quota** (daily, hourly or monthly reset),
**no credit card**. Every provider below was signed up for and **tested with a real request on
31 Oct 2026** (`test_keys.py`). Z.ai and SambaNova pass on some runs and return a temporary 429
("overloaded" / "high demand") on others. Limits change often; check the provider's console before you depend on one.

All of them speak the **OpenAI chat-completions API**: change `base_url`, key and model, nothing else.

## At a glance

| Provider | Free quota (resets) | Base URL | Tested model | Notes |
|---|---|---|---|---|
| [SenseNova](#sensenova) | Points quota in console | `https://token.sensenova.ai/v1` | `sensenova-6.8-flash-lite` | Always reasons; 429 at ~16 parallel requests |
| [Google Gemini](#google-gemini) | Per model RPM/RPD (≈15 RPM on Flash-Lite) | `https://generativelanguage.googleapis.com/v1beta/openai` | `gemini-flash-lite-latest` | Free-tier prompts may be used for training |
| [Z.ai (GLM)](#zai-glm) | Free `*-flash` models | `https://api.z.ai/api/paas/v4` | `glm-4.5-flash`, `glm-4.7-flash` | `glm-5.3-flash` is **not** free; 4.7-flash sometimes "overloaded" |
| [Cloudflare Workers AI](#cloudflare-workers-ai) | 10,000 neurons / day | `https://api.cloudflare.com/client/v4/accounts/<ACCOUNT_ID>/ai/v1` | `@cf/meta/llama-3.3-70b-instruct-fp8-fast` | Needs account ID + token |
| [Groq](#groq) | Per model, e.g. 1,000 req/day, 8K tokens/min | `https://api.groq.com/openai/v1` | `openai/gpt-oss-20b` | Very fast |
| [OpenRouter](#openrouter) | 20 req/min, 50 req/day (1,000/day after a one-time $10 top-up) | `https://openrouter.ai/api/v1` | `openrouter/free`, `*:free` | Free models often rate-limited upstream |
| [Cohere](#cohere) | 1,000 calls / month (trial key), 20 RPM | `https://api.cohere.ai/compatibility/v1` | `command-a-03-2025` | Trial key: non-commercial use |
| [SambaNova](#sambanova) | Free tier, rate-limited | `https://api.sambanova.ai/v1` | `gemma-4-31B-it` | Most models answered "high demand" (429) |
| [Requesty](#requesty) | 200 req/day across free models | `https://router.requesty.ai/v1` | `google/gemma-4-31b-it` | 13 free models (price 0) |
| [Mistral](#mistral) | Experiment plan, per-model limits | `https://api.mistral.ai/v1` | `ministral-8b-latest` | Phone (SMS) verification; may train on data |
| [NVIDIA NIM](#nvidia-nim) | Up to ~40 RPM | `https://integrate.api.nvidia.com/v1` | `openai/gpt-oss-20b` | Old models get retired (HTTP 410) |
| [Kilo Gateway](#kilo-gateway) | 200 req/hour per IP on free models | `https://api.kilo.ai/api/gateway` | `kilo-auto/free` | `kilo-auto/free` picks a free model |
| [Pollinations](#pollinations) | Daily "pollen" credit grant | `https://gen.pollinations.ai/v1` | `openai/gpt-5.4-nano` | Models are priced in pollen |
| [LLM.Kiwi](#llmkiwi) | Small hourly limit (header showed 20) | `https://api.llm.kiwi/v1` | `auto` | 5 models |
| [AIHubMix](#aihubmix) | Per free model: 100–500 req/day, 1M tokens/day, 5 RPM | `https://aihubmix.com/v1` | `coding-glm-5.3-free` | ~40 free models: GLM-5.x, Kimi K3, MiniMax M3, MiMo |
| [Routeway](#routeway) | 200 req/day on `:free` models | `https://api.routeway.ai/v1` | `muse-glimmer-30b:free` | Free list rotates |
| [Agnes AI](#agnes-ai) | Flash models at $0 (promotion), RPM shown in console | `https://apihub.agnes-ai.com/v1` | `agnes-3.0-flash` | May train on data |
| [OpenTyphoon](#opentyphoon) | 200 req/min, no daily cap | `https://api.opentyphoon.ai/v1` | `typhoon-v2.5-30b-a3b-instruct` | Thai-tuned Qwen3-30B; English works too |
| [SEA-LION](#sea-lion) | 10 req/min, no daily cap | `https://api.sea-lion.ai/v1` | `aisingapore/Qwen-SEA-LION-v4.5-27B-IT` | For prototyping |
| [LLMTR](#llmtr) | Daily allowance per free model | `https://llmtr.com/v1` | `qwen/qwen3.8-27b-free` | Turkish gateway; dated free previews |
| [Token Harbor](#token-harbor) | Rolling 7-day allowance on `:free` models | `https://tokenharbor.ai/v1` | `deepseek-v4.1-flash:free` | Verify your email first, or every request fails |


Tested but **not** a recurring free tier (kept for reference):

| Provider | What you actually get | Base URL |
|---|---|---|
| [SiliconFlow (international)](#siliconflow-international-one-time-credit-only) | One-time ~$1 signup credit; every model is paid | `https://api.siliconflow.com/v1` |
| [SiliconFlow (China)](#siliconflow-international-one-time-credit-only) | ~10 permanently free small models, but needs Chinese real-name ID verification | `https://api.siliconflow.cn/v1` |

## Quick start

```sh
cp .env.example .env      # paste your keys
chmod 600 .env
python3 test_keys.py      # one tiny request per provider -> PASS/FAIL
```

### Use from Python (any provider)

```python
import os
from openai import OpenAI          # pip install openai

client = OpenAI(base_url="https://api.groq.com/openai/v1",
                api_key=os.environ["GROQ_API_KEY"])
r = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[{"role": "user", "content": "Hello"}],
)
print(r.choices[0].message.content)
```

### Use from the shell (any provider)

```sh
curl -s "$BASE_URL/chat/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"MODEL","messages":[{"role":"user","content":"Hello"}]}'
```

List the models a key can use: `curl -s "$BASE_URL/models" -H "Authorization: Bearer $API_KEY"`
(not supported by Cloudflare; see its section).

### Load the keys into your shell

bash/zsh: `set -a; . ./.env; set +a`

csh/tcsh (no `export`): turn `.env` into `setenv` lines once, then source it:

```csh
sed -n 's/^\([A-Z_0-9]*\)=\(.*\)$/setenv \1 "\2"/p' .env > keys.env.csh
chmod 600 keys.env.csh
source keys.env.csh
```

---

## Providers

### SenseNova

**Get a key**
1. Sign up on the SenseNova token platform (`https://token.sensenova.ai`).
2. Open **API Keys** and create a key.

**Use it**
- Env: `SENSENOVA_API_KEY`
- Base URL: `https://token.sensenova.ai/v1`
- Models: `sensenova-6.8-flash-lite`, `sensenova-u1-fast`, `sensenova-u1.5-lite`
- The model always reasons. `reasoning_effort: "none"` shortens the reasoning but does not turn it off,
  and `max_tokens` caps the reasoning too, so keep it high (≥ 2000) or you get no answer.

### Google Gemini

**Get a key**
1. Go to <https://aistudio.google.com/apikey> and sign in with Google.
2. **Create API key** → pick or create a project.
3. Do **not** enable billing on the project; that moves it off the free tier.

**Use it**
- Env: `GEMINI_API_KEY`
- Base URL: `https://generativelanguage.googleapis.com/v1beta/openai`
- Models: `gemini-flash-lite-latest`, `gemini-2.5-flash`, `gemma-4-26b-a4b-it` (see `/models`)
- Limits per model are shown in AI Studio → *Rate limits*. The OpenAI-compatible endpoint rejects
  `logprobs`, `seed` and `n > 1`.

### Z.ai (GLM)

**Get a key**
1. Sign up at <https://z.ai>.
2. Go to <https://z.ai/manage-apikey/apikey-list> → **Create API key**.

**Use it**
- Env: `ZAI_API_KEY`
- Base URL: `https://api.z.ai/api/paas/v4`
- Free models: `glm-4.7-flash`, `glm-4.5-flash`. Other models (`glm-5.3-flash`, `glm-5.x`) return
  *"Insufficient balance"*.
- `glm-4.7-flash` sometimes returns 429 code 1305 ("temporarily overloaded"); retry or use `glm-4.5-flash`.

### Cloudflare Workers AI

**Get a key** (two values)
1. Sign up at <https://dash.cloudflare.com>.
2. **Account ID**: *Workers & Pages* → copy it from the right sidebar.
3. **Token**: *My Profile → API Tokens → Create Token* → template **Workers AI**.

**Use it**
- Env: `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN`
- Base URL: `https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/ai/v1`
- Models: `@cf/meta/llama-3.3-70b-instruct-fp8-fast`, `@cf/openai/gpt-oss-20b`, `@cf/openai/gpt-oss-120b`,
  `@cf/zai-org/glm-4.7-flash`, `@cf/qwen/qwen3-30b-a3b-fp8`, …
- `GET /models` is not supported. List models with:
  ```sh
  curl -s "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/ai/models/search?task=Text%20Generation" \
    -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN"
  ```
- Retired models return HTTP 410 (e.g. `@cf/meta/llama-3.1-8b-instruct`).

### Groq

**Get a key**
1. Sign in at <https://console.groq.com> (Google, GitHub or email).
2. <https://console.groq.com/keys> → **Create API Key**. It is shown only once.

**Use it**
- Env: `GROQ_API_KEY`
- Base URL: `https://api.groq.com/openai/v1`
- Models: `openai/gpt-oss-20b`, `openai/gpt-oss-120b`, `qwen/qwen3.8-27b`
- Your limits come back in `x-ratelimit-*` response headers and are listed at
  <https://console.groq.com/settings/limits>.

### OpenRouter

**Get a key**
1. Sign in at <https://openrouter.ai>.
2. <https://openrouter.ai/settings/keys> → **Create Key** (leave the credit limit empty).

**Use it**
- Env: `OPENROUTER_API_KEY`
- Base URL: `https://openrouter.ai/api/v1`
- Only model IDs ending in `:free` are free, plus `openrouter/free`, which picks a free model for you.
  Examples: `nvidia/nemotron-3.5-lightning:free`, `google/gemma-4-31b-it:free`, `poolside/laguna-s-2.1:free`.
- Popular free models are often rate-limited upstream (429); fall back to `openrouter/free`.
- The daily cap is per account, so extra keys don't raise it.

### Cohere

**Get a key**
1. Sign up at <https://dashboard.cohere.com>.
2. A **Trial key** is created for you at <https://dashboard.cohere.com/api-keys>.

**Use it**
- Env: `COHERE_API_KEY`
- Base URL (OpenAI-compatible): `https://api.cohere.ai/compatibility/v1`
- Models: `command-a-03-2025`, `command-r-plus`, `c4ai-aya-expanse-32b`
- Trial keys are for non-commercial use.

### SambaNova

**Get a key**
1. Sign in at <https://cloud.sambanova.ai>.
2. <https://cloud.sambanova.ai/apis> → **Generate API Key**.

**Use it**
- Env: `SAMBANOVA_API_KEY`
- Base URL: `https://api.sambanova.ai/v1`
- Models: `gemma-4-31B-it` (worked), `DeepSeek-V3.2`, `DeepSeek-V3.1`, `gpt-oss-120b`,
  `Meta-Llama-3.3-70B-Instruct`, `MiniMax-M3.1-Flash`
- In testing, every model except `gemma-4-31B-it` returned *"currently experiencing high demand"* (429).
  Treat it as a backup.

### Requesty

**Get a key**
1. Sign in at <https://app.requesty.ai>.
2. <https://app.requesty.ai/api-keys> → create a key.

**Use it**
- Env: `REQUESTY_API_KEY`
- Base URL: `https://router.requesty.ai/v1`
- Free models (price 0): `google/gemma-4-31b-it`, `nvidia/nemotron-3-super-120b-a12b`,
  `nvidia/nemotron-3-ultra-550b-a55b`, `nvidia/nemotron-3.5-lightning-30b-a3b`, `mistral/leanstral-1-5`,
  `poolside/laguna-m.1`, `novita/ling-3.1-flash`, … (full list: <https://www.requesty.ai/free-models>)
- Other models are paid; check `input_price`/`output_price` in `/models` before you use one.

### Mistral

**Get a key**
1. Sign up at <https://console.mistral.ai>.
2. *Workspace → Billing / Plans* → choose **Experiment** (free).
3. Verify your phone number (SMS). No card needed.
4. *API Keys* → **Create new key**.

**Use it**
- Env: `MISTRAL_API_KEY`
- Base URL: `https://api.mistral.ai/v1`
- Models: `ministral-8b-latest`, `ministral-14b-latest`, `mistral-small-latest`, `mistral-medium-latest`,
  `codestral-latest`, `magistral-small-latest`
- Limits are per model. `mistral-small-latest` hit 429 while `ministral-8b-latest` was fine.
  Free-plan data may be used for training (opt out in the Admin panel).

### NVIDIA NIM

**Get a key**
1. Sign in at <https://build.nvidia.com> (NVIDIA account; it may ask for a phone number).
2. Open any model → **Get API Key** → **Generate Key**. The key starts with `nvapi-`.

**Use it**
- Env: `NVIDIA_API_KEY`
- Base URL: `https://integrate.api.nvidia.com/v1`
- Models: `openai/gpt-oss-20b`, `nvidia/nemotron-3.5-lightning-30b-a3b`, `nvidia/nemotron-3-super-120b-a12b`,
  `z-ai/glm-5.3-flash`, `deepseek-ai/deepseek-v4.1-flash`
- Retired models return HTTP 410 (e.g. `meta/llama-3.3-70b-instruct` since Aug 2026); re-check `/models`.

### Kilo Gateway

**Get a key**
1. Sign in at <https://kilo.ai>.
2. Copy the API key from your profile page (it is a long token starting with `eyJ`).

**Use it**
- Env: `KILO_API_KEY`
- Base URL: `https://api.kilo.ai/api/gateway`
- Free models: `kilo-auto/free` (picks one for you), `nvidia/nemotron-3.5-super-vl:free`,
  `inclusionai/ling-3.1-flash-1019-free`, other IDs ending in `:free` or `-free`.

### Pollinations

**Get a key**
1. Go to <https://enter.pollinations.ai> and sign in.
2. Create a **secret key** (`sk_...`). Keys starting with `pk_` are publishable (front-end) keys.

**Use it**
- Env: `POLLINATIONS_API_KEY`
- Base URL: `https://gen.pollinations.ai/v1`
- Models: `openai/gpt-5.4-nano` and about 150 more. Each model is priced in *pollen* (credit). The account
  gets a free pollen grant, and cheap models such as `gpt-5.4-nano` use very little of it.
- Model prices: `curl -s https://gen.pollinations.ai/text/models`
- Checking your balance needs a key with the `account:usage` permission.

### LLM.Kiwi

**Get a key**
1. Sign up at <https://llm.kiwi>.
2. Create a key in the dashboard (`sk_kiwi_...`).

**Use it**
- Env: `LLMKIWI_API_KEY`
- Base URL: `https://api.llm.kiwi/v1`
- Models: `auto`, `minimax-m3`, `minimax-m2.5`, `nemotron-3-ultra`, `nemotron-3-super`
- Small limit: check the `X-Ratelimit-*` response headers.

### AIHubMix

**Get a key**
1. Sign up at <https://aihubmix.com> (email or Google/GitHub).
2. <https://console.aihubmix.com/workspaces/default/keys> → create a key (`sk-...`).

**Use it**
- Env: `AIHUBMIX_API_KEY`
- Base URL: `https://aihubmix.com/v1` (Anthropic-format base for Claude Code: `https://aihubmix.com`)
- Only IDs ending in `-free` or `:free` are free. Examples: `coding-glm-5.3-free`, `coding-kimi-k3-free`,
  `coding-minimax-m3-free`, `xiaomi-mimo-v2.6-pro-free`, `coding-glm-5.3-flash-free`, `glm-4.7-flash-free`,
  `gemma-4-31b-it-free`, `nemotron-3-ultra-550b-a55b-free`.
- Limits are per model: 5 req/min, 1M tokens/day, and 100 req/day (most `coding-*` routes) or 500 req/day
  (e.g. `coding-minimax-m3-free`, `glm-4.7-flash-free`). Using several models multiplies the quota.
- The other ~600 models are paid.

### Routeway

**Get a key**
1. Sign up at <https://routeway.ai>.
2. <https://routeway.ai/dashboard/keys> → create a key.

**Use it**
- Env: `ROUTEWAY_API_KEY`
- Base URL: `https://api.routeway.ai/v1`
- Only IDs ending in `:free` are free; the set rotates. On 31 Oct 2026: `muse-glimmer-30b:free`,
  `minimax-m3.1-flash:free`, `deepseek-v4.1-flash:free` (timed out in testing), plus several
  `gemma-4-26b-a4b-it-*:free` roleplay fine-tunes.
- 200 free requests/day; the per-minute cap is 5 or 20 (Routeway's docs disagree).

### Agnes AI

**Get a key**
1. Sign up at <https://platform.agnes-ai.com>.
2. Create an API key in the dashboard.

**Use it**
- Env: `AGNES_API_KEY`
- Base URL: `https://apihub.agnes-ai.com/v1`
- Free models: `agnes-3.0-flash`, `agnes-2.5-flash`. The `-pro` models are paid.
- The $0 price is a promotion with no announced end date. Per-minute limits are shown in the console.
  Inputs may be used to improve Agnes models.

### OpenTyphoon

**Get a key**
1. Sign up at <https://opentyphoon.ai>.
2. <https://playground.opentyphoon.ai/api-key> → create a key.

**Use it**
- Env: `OPENTYPHOON_API_KEY`
- Base URL: `https://api.opentyphoon.ai/v1`
- Chat model: `typhoon-v2.5-30b-a3b-instruct` (a Thai fine-tune of Qwen3-30B-A3B; answers in English fine).
- Free "research showcase": 200 req/min, 5 req/s, no daily cap. Usage data is collected to improve the model.

### SEA-LION

**Get a key**
1. Sign in at <https://playground.sea-lion.ai>.
2. <https://playground.sea-lion.ai/key-manager> → create a **Trial API Key**.

**Use it**
- Env: `SEALION_API_KEY`
- Base URL: `https://api.sea-lion.ai/v1`
- Models: `aisingapore/Qwen-SEA-LION-v4.5-27B-IT`, `aisingapore/Nemotron-SEA-LION-v4.8-120B-A12B`,
  `aisingapore/Gemma-SEA-LION-v4-27B-IT`, `aisingapore/Llama-SEA-LION-v3-70B-IT`, plus embedding models.
- 10 req/min, no published daily cap. Intended for prototyping.

### LLMTR

**Get a key**
1. Sign up at <https://llmtr.com>.
2. <https://llmtr.com/dashboard/api-keys> → create a key (`llmtr-...`).

**Use it**
- Env: `LLMTR_API_KEY`
- Base URL: `https://llmtr.com/v1`
- Free models (IDs ending in `-free`): `qwen/qwen3.8-27b-free`, `nvidia/nemotron-3.5-super-vl-free`,
  `minimax/minimax-m3.1-flash-free`, … Some are dated previews that stop being free on a set day.
- Each free model has its own daily allowance (e.g. 200K tokens/day on some previews). Some previews
  need a previous top-up.

### Token Harbor

**Get a key**
1. Sign up at <https://tokenharbor.ai>.
2. **Verify your email:** open the confirmation link Token Harbor emails you (check spam). If it never
   arrived, request a new one at <https://tokenharbor.ai/dashboard>. Until you verify, every API request
   fails with `email_verification_required`, even with a valid key.
3. <https://tokenharbor.ai/dashboard/api-keys> → create a key (`thk_live_...`).
4. In the dashboard, turn on the free (`:free`) routes.

**Use it**
- Env: `TOKENHARBOR_API_KEY`
- Base URL: `https://tokenharbor.ai/v1` (Anthropic-format base: `https://tokenharbor.ai`)
- Free models: `deepseek-v4.1-flash:free`, `mimo-v2.6-flash:free` (the set rotates).
- The allowance renews over a rolling 7 days; the dashboard shows usage as a percentage. Requests stop
  when it runs out; you are never charged.

### SiliconFlow (international): one-time credit only

Not a recurring free tier. The international site lists every model as paid and gives about **$1 of credit once**.
In testing, three tiny requests worked, then every model returned HTTP 402 *"account balance is insufficient"*.

The **China site** (`cloud.siliconflow.cn`, base URL `https://api.siliconflow.cn/v1`) does have permanently free
small models (price 0 on <https://siliconflow.cn/pricing>, Oct 2026): `Qwen/Qwen3-8B`, `Qwen/Qwen3.5-4B`,
`Qwen/Qwen2.5-7B-Instruct`, `THUDM/GLM-4-9B-0414`, `THUDM/GLM-Z1-9B-0414`, `deepseek-ai/DeepSeek-R1-0528-Qwen3-8B`,
`tencent/Hunyuan-MT-7B`, `XingChenAGI/Xing4.0-29B`, plus free embedding/rerank (`BAAI/bge-m3`, `bge-reranker-v2-m3`).
The catch: since 15 May 2026 the China site requires **real-name verification** (实名认证) before any API call:
a +86 phone, a Chinese ID document and a face check. Most people outside China can't complete it. Verified accounts
also get a one-time ¥16 voucher (valid 180 days).

**Get a key**
1. Sign up at <https://cloud.siliconflow.com>, then *Account → API Keys* → create a key (`sk-...`).

**Use it**
- Env: `SILICONFLOW_API_KEY`
- Base URL: `https://api.siliconflow.com/v1` (an international key gets 401 on `api.siliconflow.cn`)
- Models: `Qwen/Qwen3-8B`, `Qwen/Qwen3.5-9B`, `openai/gpt-oss-20b`, … (all paid; see
  <https://www.siliconflow.com/pricing>)

---

## Rules worth following

- Never enable billing on Google, Mistral or Cloudflare; that leaves the free tier.
- One account per provider. Making accounts to multiply quota breaks the terms and gets you banned.
- Gemini (free tier), Mistral Experiment, OpenRouter free models, Agnes AI and OpenTyphoon may train on
  your prompts. Don't send private or work data.
- Keep keys in `.env` (git-ignored) and never paste them into commits or chats.
