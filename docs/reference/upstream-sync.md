# Upstream Sync Policy

TrustedRouterOnPrem tracks `experientiallabs/experiential` while preserving a small product policy
layer.

## Source

- Upstream repository: `https://github.com/experientiallabs/experiential`
- Upstream branch: `main`
- Initial reviewed commit: `c8220b0543ad6d5f426f831377f9efcd67be0aa1`
- Last reviewed commit: `b3061af6787dfbca011e4782dc26529514206ad3`
- Fork repository: `https://github.com/Lore-Hex/trustedrouter-onprem`

## Invariants

Every upstream commit is reviewed and ported separately in chronological order. A sync must retain
all of these properties:

1. Public product branding remains TrustedRouterOnPrem.
2. TrustedRouter remains available through its native provider at
   `https://api.trustedrouter.com/v1`.
3. Local and customer-controlled BYOK connections remain explicit and never become silent
   fallbacks from TrustedRouter.
4. Product telemetry remains disabled by default and never uses upstream telemetry credentials.
5. The Apache 2.0 license and upstream attribution remain intact.
6. The full lint, type, unit, and release gates pass before a port is pushed.

Each ported commit records the upstream SHA in its commit message. Conflicting or skipped commits
are reported with a precise reason rather than being silently flattened into a later sync.

## September 9, 2026 Review

Nine commits after `421a3b53` were ported separately through upstream 0.7.60.
The four release commits retain the `trustedrouter-onprem` distribution name and lockfile
identity. The Vertex documentation retains the `tr-onprem` command, and tokenizer recovery
errors name this distribution. No upstream commit was skipped.

The ports accept validated Copilot image MIME hints, support explicitly configured Vertex
Model Garden connections, reshape Anthropic-family tool schemas with admission disclosure,
and accept the AI SDK `promptCacheKey` spelling. When both cache-key spellings occur, the
canonical field wins and the ignored alias is disclosed. These compatibility changes do not
introduce another default hosted provider or an automatic fallback from TrustedRouter.

Input reservations now use a packaged, digest-checked tokenizer with 15 percent headroom,
media estimates, and a long-context pricing margin. This is a planning estimate, not a hard
upper bound; actual usage replaces it at settlement and can exceed the reservation. The
tokenizer loads locally without a runtime download. Telemetry defaults and Apache attribution
remain unchanged.
