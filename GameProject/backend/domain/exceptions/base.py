# Base exceptions
class DomainError(Exception):
	pass


class InvariantViolation(DomainError):
	pass


class IllegalState(DomainError):
	pass
