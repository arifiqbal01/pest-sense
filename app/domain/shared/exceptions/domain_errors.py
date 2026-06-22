class DomainError(Exception):
    """
    Base exception for all domain-layer failures.

    Raised when domain logic cannot safely proceed due to
    invalid state, invariant violations, or business constraints.
    """

    default_message = "A domain error occurred."

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.default_message)


class DomainInvariantError(DomainError):
    """
    Raised when a core domain invariant is violated.

    Examples:
    - lifecycle stage order is invalid
    - accumulated GDD becomes negative
    - stage transition skips biological constraints
    """

    default_message = "A domain invariant was violated."