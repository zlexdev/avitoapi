"""Challenge solver seam (captcha / WAF). Avito Partner API does not need one."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ChallengeRequest(BaseModel):
    """Input to :meth:`ChallengeSolver.solve`."""

    model_config = ConfigDict(strict=True, frozen=True)

    kind: str = Field(..., description="Solver-specific challenge id, e.g. ``hcaptcha``.")
    page_url: HttpUrl = Field(..., description="URL where the challenge was encountered.")
    site_key: str | None = Field(default=None, description="Provider-issued site key.")


class ChallengeSolution(BaseModel):
    """Output of :meth:`ChallengeSolver.solve`."""

    model_config = ConfigDict(strict=True, frozen=True)

    token: str = Field(..., description="Token to replay into the challenge form.")
    metadata: dict[str, str] = Field(default_factory=dict)


class ChallengeSolver(ABC):
    """Pluggable solver for captcha / browser-challenge surfaces."""

    @abstractmethod
    async def solve(self, request: ChallengeRequest) -> ChallengeSolution: ...


class NullSolver(ChallengeSolver):
    """Default. Refuses to solve anything — Partner API never asks."""

    async def solve(self, request: ChallengeRequest) -> ChallengeSolution:
        raise NotImplementedError(
            "Avito Partner API does not require captcha. Install an extra "
            "([playwright]/[twocaptcha]/[capsolver]) and inject a real solver "
            "to handle the mobile/web surface.",
        )
