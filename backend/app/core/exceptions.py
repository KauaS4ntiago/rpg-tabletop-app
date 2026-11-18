class DomainError(Exception):
    """Base class for errors that carry business meaning."""


class EmailAlreadyRegisteredError(DomainError):
    pass


class UsernameAlreadyTakenError(DomainError):
    pass