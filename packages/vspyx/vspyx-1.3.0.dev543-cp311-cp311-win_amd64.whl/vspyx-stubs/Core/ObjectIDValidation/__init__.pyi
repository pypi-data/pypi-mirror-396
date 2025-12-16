import typing, enum, vspyx

@enum.unique
class ValidationResult(enum.IntFlag):
	ValidatedOK = 0
	InvalidEmpty = 1
	InvalidBeginsWithWhitespace = 2
	InvalidEndsWithWhitespace = 3

