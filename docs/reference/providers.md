# Model providers

TrustedRouterOnPrem resolves models from a secret-free `.exp/models.toml` catalog.
`RuntimeModelCatalog` is the only construction service. Provider names do not imply capabilities
or prices. Every completion or embedding alias must declare the protocol features and token prices
it uses.

Configure connections with `tr-onprem config providers` or the first `tr-onprem build` on a clean
checkout. The first-party hosted provider is `trustedrouter`. It is fixed to
`https://api.trustedrouter.com/v1` and uses `TRUSTEDROUTER_API_KEY`. Another public router cannot be
selected through setup and is never used as an automatic fallback.

Direct OpenAI, Anthropic, Gemini, Azure, Bedrock, and Vertex connections are customer-controlled
BYOK lanes. `openai-compatible` is for an explicitly configured endpoint, including a local or
private-network model server. These explicit connections are not first-party hosted backends and
never replace TrustedRouter silently.

Agents can skip the interactive provider list with repeatable `--provider` flags:
`trustedrouter`, `openai`, `anthropic`, `gemini`, `openai-compatible`, `azure`, or `bedrock`.
Unsupported or duplicate values fail before any catalog write. Azure and Bedrock require manual
model IDs. Other selected providers use account model discovery when credentials are available.

`tr-onprem login` reads `TRUSTEDROUTER_API_KEY`, or prompts for it through hidden terminal input,
then stores the key in the user credential file and synchronizes account models. It persists a
native `provider = "trustedrouter"` connection. The base URL is built into the provider adapter and
cannot be overridden by catalog data.

Setup writes only secret-free catalog fields and never prints a credential value. Interactive
`tr-onprem config providers` persists pasted API keys outside the repository in the user-data file
(`$XDG_DATA_HOME/exp/auth.json` or `~/.local/share/exp/auth.json` on Linux).
When the operator edits an existing provider that already has a stored key, the same wizard
can keep, replace, or remove that record. Known providers keep their canonical environment
override names internally. Custom OpenAI-compatible connections keep a generated or
already-configured override name, but the operator pastes the key rather than typing a
variable name.

Runtime credential resolution for one connection ID:

1. An explicit environment mapping supplied by the caller, when one is present
2. Otherwise the configured process environment variable, when it is non-empty
3. The stored local credential for that exact connection

The caller mapping, when supplied, is the only environment consulted and does not rewrite the
store. Runtime, `--non-interactive`, and CI paths never prompt. A missing credential fails with
the environment name and a recovery that points at `tr-onprem config providers`. Amazon Bedrock is
unchanged: it uses the AWS credential chain and has no stored API key.

## Supported providers

| Provider | Catalog `provider` | Credential | Endpoint identity |
|---|---|---|---|
| OpenAI | `openai` | `api_key_env` (suggested `OPENAI_API_KEY`) | Official OpenAI origin |
| TrustedRouter | `trustedrouter` | `api_key_env` (suggested `TRUSTEDROUTER_API_KEY`) | Official TrustedRouter origin |
| Anthropic | `anthropic` | `api_key_env` (suggested `ANTHROPIC_API_KEY`) | Official Anthropic origin |
| Gemini | `gemini` | `api_key_env` (suggested `GEMINI_API_KEY`) | Official Gemini origin |
| OpenAI-compatible | `openai-compatible` | `api_key_env` plus explicit `base_url` | Catalog `base_url` |
| Azure OpenAI / Foundry | `azure` | `api_key_env` plus explicit resource endpoint and `api_version` | Endpoint and API version |
| Amazon Bedrock | `bedrock` | AWS credential chain. No `api_key_env` | Optional catalog `region` |
| Vertex AI | `vertex` | `api_key_env` holding service-account JSON | Project-and-location `base_url` |
| Tinker sampling | `tinker` | `api_key_env` | Official Tinker origin |

Native fixed-origin providers reject a custom `base_url`. Use `openai-compatible` for a trusted
third-party OpenAI-compatible host.

## TrustedRouter listing metadata

`trustedrouter` lists its catalog from the TrustedRouter origin. Setup keeps the completion and
embedding roles from
`trustedrouter.supports_chat` and `trustedrouter.supports_embeddings`, `context_length`,
`top_provider.max_completion_tokens`, and the `pricing` per-token prices.

`supported_parameters` is read when a model publishes it. The array is
optional: a model that omits it keeps tool, structured-output, sampling, and reasoning support
**unknown** rather than reporting them as unsupported. Because that listing can return an unproven
model, `trustedrouter` joins `openai-compatible` in the operator-declaration path, so such a model
stays visible and the operator declares the minimum fields a selected role needs instead of the
model being dropped from the role choices. A model that reports a non-positive `context_length`
keeps an unknown context window rather than borrowing one from a neighboring field.

## OpenAI-compatible listing metadata

`provider = "openai-compatible"` is the only OpenAI-shaped listing path that reads optional
extension fields. Official `openai` listing stays identity-only: extra keys on a model object are
discarded so unofficial metadata cannot become verified OpenAI capabilities or prices.

Discovery and verification stay separate. `tr-onprem config providers --provider openai-compatible`
lists every identity returned by a trusted operator-supplied endpoint. Official `openai` listing
never becomes a capability source. When the compatible host also publishes the following optional
fields, setup copies only values that match the declared types. Absent or wrongly typed fields
stay unknown. No context window or cache-write price is inferred from a neighboring value.

Identity-only rows remain visible and selectable. Setup labels them `unknown capabilities/prices`
and does not assign a build role until the operator declares the minimum fields that role needs.
The interactive flow confirms published values and asks only for missing required fields. The
deterministic equivalent is `tr-onprem config providers --non-interactive` with `--connection-json` and
`--model-json`, or a hand-authored `.exp/models.toml` record. Those declarations become configured
catalog metadata. Downstream cost and router-candidate preflights stay fail-closed while a
required price or limit remains unknown.

| Field | Type | Meaning |
|---|---|---|
| `supports_completions` | boolean | The alias serves chat or responses completions |
| `supports_tools` | boolean | The alias accepts tools |
| `supports_structured_output` | boolean | The alias accepts structured output |
| `maximum_output_tokens` | positive integer | Declared output ceiling |
| `context_window_tokens` | positive integer | Declared context window, only when the host publishes one |
| `pricing.input_micro_usd_per_million_tokens` | integer `>= 0` | Configured input price in micro-USD per million tokens |
| `pricing.output_micro_usd_per_million_tokens` | integer `>= 0` | Configured output price in micro-USD per million tokens |
| `pricing.cached_input_micro_usd_per_million_tokens` | integer `>= 0` | Configured cached-input price in micro-USD per million tokens |

Micro-USD prices convert to catalog USD-per-million-token prices by dividing by `1_000_000`.
When a trusted third-party compatible host publishes these fields, completion, tool,
structured-output, and input/output price declarations can assign world-model and judge roles
without a questionnaire. Router-candidate setup still requires a published or
operator-declared context window and both cache prices. Setup never invents missing values.

The hosted gateway `/v1/models` response is the strict OpenAI discovery surface. Its list
envelope contains only `object` and `data`; each model contains only `id`, `object`,
`created`, and `owned_by`. Hosted capability and price discovery belongs to the platform
catalog API, not to additive fields on the OpenAI endpoint.

## Azure

Use `provider = "azure"`. The connection needs:

- `base_url`: the Azure resource endpoint, for example `https://myresource.openai.azure.com`
- `api_key_env`: the environment-variable name that holds that resource's key
- `api_version`: `v1` for the current Azure OpenAI and Foundry `/openai/v1` routes, or a dated
  Azure OpenAI version such as `2024-10-21` for classic deployment-in-path routing

The model record `model` field is the exact Azure deployment identifier sent on the wire. TrustedRouterOnPrem never
derives a deployment from an alias or a base-model name. Use a separate alias for an embedding
deployment.

`AZURE_OPENAI_API_KEY` is paired with `AZURE_OPENAI_ENDPOINT` when that endpoint variable is set.
A catalog endpoint that is not the same resource cannot use that key. Comparison lowercases the
scheme and host, treats default HTTPS and HTTP ports as equivalent to an omitted port, keeps path
case, and ignores a trailing slash. Credentials may not appear in the endpoint URL, query string,
or fragment.

```toml
[connections.azure]
provider = "azure"
base_url = "https://myresource.openai.azure.com"
api_key_env = "AZURE_OPENAI_API_KEY"
api_version = "v1"

[models.gpt]
connection = "azure"
model = "gpt-5-deployment"
[models.gpt.capabilities]
supports_completions = true
supports_tools = true
input_cost_per_million_tokens_usd = 0
output_cost_per_million_tokens_usd = 0
cached_input_cost_per_million_tokens_usd = 0
cache_write_cost_per_million_tokens_usd = 0

[models.embed]
connection = "azure"
model = "text-embedding-deployment"
[models.embed.capabilities]
supports_embeddings = true
input_cost_per_million_tokens_usd = 0
```

## Bedrock

Use `provider = "bedrock"`. Do not set `api_key_env`. Credentials come from the standard AWS chain
(environment keys, shared config, profile, role, web identity, container, or instance role). Static
`AWS_ACCESS_KEY_ID` variables are optional.

Region is resolved in this order:

1. Catalog `region`
2. `AWS_REGION`
3. The boto session chain, including `AWS_DEFAULT_REGION`, the active profile region, and the
   instance role

The catalog region is recommended and is part of connection identity when set. Catalog loading and
`snapshot()` do not import boto or inspect instance metadata.

The model record `model` field is the exact foundation-model or inference-profile ID. Use a
separate alias for an embedding model such as Titan. Do not combine completion and embedding IDs
on one record.

```toml
[connections.bedrock]
provider = "bedrock"
region = "us-east-1"

[models.claude]
connection = "bedrock"
model = "us.anthropic.claude-sonnet-4-5"
[models.claude.capabilities]
supports_completions = true
supports_tools = true
input_cost_per_million_tokens_usd = 0
output_cost_per_million_tokens_usd = 0
cached_input_cost_per_million_tokens_usd = 0
cache_write_cost_per_million_tokens_usd = 0

[models.titan]
connection = "bedrock"
model = "amazon.titan-embed-text-v2:0"
[models.titan.capabilities]
supports_embeddings = true
input_cost_per_million_tokens_usd = 0
```

## Vertex AI

Use `provider = "vertex"` for Google-published models served from a Google Cloud project.
The connection needs two values: `base_url` naming the project-and-location root, and
`api_key_env` naming an environment variable whose value is the full service-account JSON key
file contents. The runtime mints short-lived OAuth bearer tokens from that credential; the
JSON itself never travels on the wire, and the endpoint host is pinned to HTTPS
`*.aiplatform.googleapis.com` so the token can never be sent to an operator-chosen host.
Requests use the same `generateContent` wire protocol as the Gemini provider on
`publishers/google/models/` routes.

Vertex is catalog-and-API configuration only: the interactive `tr-onprem config providers` picker
does not offer it. Like Azure and Bedrock, provider names do not imply protocol support or
prices, so every Vertex alias declares explicit capabilities. Embeddings are not supported on
Vertex connections; use a `gemini` connection for Gemini embeddings.

```toml
[connections.vertex]
provider = "vertex"
base_url = "https://us-central1-aiplatform.googleapis.com/v1/projects/PROJECT/locations/us-central1"
api_key_env = "VERTEX_SERVICE_ACCOUNT_JSON"

[models.gemini-pro]
connection = "vertex"
model = "gemini-2.5-pro"
[models.gemini-pro.capabilities]
supports_completions = true
supports_tools = true
input_cost_per_million_tokens_usd = 0
output_cost_per_million_tokens_usd = 0
```

## Errors

Missing credentials name the environment variable and the `tr-onprem config providers` recovery, never
a secret value. A missing Bedrock region lists the AWS resolution order. Azure endpoint and key
mismatches name `AZURE_OPENAI_ENDPOINT`, not the key. A malformed user-data credential file
fails closed and tells the operator to move or delete it, then run `tr-onprem config providers`.
Malformed provider responses fail closed and do not write partial catalog or evidence artifacts.
