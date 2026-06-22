from app.domain.shared.exceptions.domain_errors import DomainError


class DomainValidationError(DomainError):
    """
    Raised when domain input fails validation.

    Examples:
    - humidity outside 0–100%
    - malformed climate payload
    - invalid pest profile configuration
    - missing required biological parameters
    """

    default_message = "Domain input validation failed."