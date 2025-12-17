class OasisError(RuntimeError):
    """SDK 공통 최상위 예외."""


class OasisRateLimitError(OasisError):
    """공급자 RateLimit 오류 래핑."""

    @classmethod
    def from_openai(cls, exc: Exception) -> "OasisRateLimitError":
        return cls(str(exc))
