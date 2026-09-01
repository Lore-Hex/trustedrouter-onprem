# Upstream Sync Policy

TrustedRouterOnPrem tracks `experientiallabs/experiential` while preserving a small product policy
layer.

## Source

- Upstream repository: `https://github.com/experientiallabs/experiential`
- Upstream branch: `main`
- Initial reviewed commit: `c8220b0543ad6d5f426f831377f9efcd67be0aa1`
- Last reviewed commit: `c86f5359dfbda5a539f87caa2e977adcd8ca71d6`
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
