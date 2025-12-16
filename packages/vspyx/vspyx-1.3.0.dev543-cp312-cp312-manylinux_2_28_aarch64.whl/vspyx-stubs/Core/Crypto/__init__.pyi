import typing, enum, vspyx

@enum.unique
class HashFunctions(enum.IntEnum):
	SHA1 = 0
	SHA256 = 1
	MD5 = 2

@enum.unique
class PKCSEncodings(enum.IntEnum):
	PKCS1_V15 = 0
	PKCS1_V21 = 1

