# auth/solvers/

Captcha / WAF challenge solver seam. Avito Partner API does not require
one — `NullSolver` raises `NotImplementedError` if called. Real solvers
land later behind optional extras (`[playwright]`, `[twocaptcha]`,
`[capsolver]`).

## Contract

- `ChallengeSolver.solve(request) -> ChallengeSolution`.
- Implementations may be stateful (own a Playwright browser pool, hold
  vendor API credentials) but must be safe to call concurrently or
  document their own concurrency story.

## Don'ts

- Don't fall back to the real Avito mobile / web surface in this SDK —
  it's gated by Cloudflare + Yandex SmartCaptcha and out of scope.
- Don't pre-import heavy dependencies (`playwright`, `2captcha-python`)
  at module top; lazy-import inside concrete solvers.
