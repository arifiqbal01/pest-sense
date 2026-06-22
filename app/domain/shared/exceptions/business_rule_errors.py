from app.domain.shared.exceptions.domain_errors import DomainError


class BusinessRuleViolation(DomainError):
    """
    Raised when a business/domain rule prevents an operation.

    Examples:
    - intervention blocked due to incompatible pest stage
    - recommendation generation blocked by missing required context
    - forecast execution blocked under unsupported simulation mode
    """

    default_message = "A domain business rule prevented this operation."