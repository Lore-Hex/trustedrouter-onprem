# TrustedRouterOnPrem Agent Setup

Paste the prompt below into a trusted coding agent from the directory where you want to operate
the gateway. Replace the placeholder with a key created at
`https://trustedrouter.com/console/keys`.

```text
Install TrustedRouterOnPrem from
https://github.com/Lore-Hex/trustedrouter-onprem and configure it on this machine.

Use this TrustedRouter API key:
TRUSTEDROUTER_API_KEY=sk-tr-v1-REPLACE_ME

Requirements:
1. Keep the key out of source control, command output, logs, and chat responses.
2. Install the project in an isolated Python 3.12 or newer environment.
3. Run `tr-onprem login` with TRUSTEDROUTER_API_KEY in the process environment.
4. Start `tr-onprem` on loopback only.
5. Capture the one-time local gateway key without printing it after setup.
6. Verify `GET http://127.0.0.1:8000/v1/models` with the local gateway key.
7. Send one OpenAI SDK request to model `trustedrouter/auto` asking:
   "What is the capital of France?"
8. Confirm the answer is Paris, then stop. Do not configure any other public router.
9. Report only the installed version, local URL, health result, and model used. Redact keys.
```

## Manual Setup

```bash
git clone https://github.com/Lore-Hex/trustedrouter-onprem.git
cd trustedrouter-onprem
uv sync --extra dev
export TRUSTEDROUTER_API_KEY="sk-tr-v1-..."
uv run tr-onprem login
uv run tr-onprem
```

The CLI stores provider credentials in the user credential store and writes only secret-free
connection metadata to the local model catalog. The canonical managed endpoint is fixed at
`https://api.trustedrouter.com/v1`.

## OpenAI SDK Check

Use the local gateway URL and one-time local key printed during first-run setup:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:8000/v1",
    api_key="<local gateway key>",
)

result = client.chat.completions.create(
    model="trustedrouter/auto",
    messages=[{"role": "user", "content": "What is the capital of France?"}],
)
assert "Paris" in (result.choices[0].message.content or "")
```

## Managed Backend Policy

TrustedRouter model access uses the native provider at `https://api.trustedrouter.com/v1`.
Customer-controlled direct provider keys remain available as BYOK connections, and
`openai-compatible` can target a server on infrastructure the customer controls. Neither path is
an automatic fallback from TrustedRouter.
