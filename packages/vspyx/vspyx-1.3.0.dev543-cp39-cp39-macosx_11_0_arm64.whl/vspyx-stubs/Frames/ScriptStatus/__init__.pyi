import typing, enum, vspyx

@enum.unique
class Parameter(enum.IntEnum):
	CoreMiniRunning = 0
	SectorOverflow = 1
	RemainingSectors = 2
	LastSector = 3
	ReadBinSize = 4
	MinSector = 5
	MaxSector = 6
	CurrentSector = 7
	CoreMiniCreateTime = 8
	FileChecksum = 9
	CoreMiniVersion = 10
	CoreMiniHeaderSize = 11
	DiagnosticErrorCode = 12
	DiagnosticErrorCodeCount = 13
	MaxCoreMiniSize = 14
	Logging = 15
	IsEncrypted = 16

class Message:
	"""Message
	"""
	CoreMiniCreateTime: int
	CoreMiniHeaderSize: int
	CoreMiniVersion: int
	CurrentSector: int
	DiagnosticErrorCode: int
	DiagnosticErrorCodeCount: int
	FileChecksum: int
	LastSector: int
	MaxCoreMiniSize: int
	MaxSector: int
	MinSector: int
	NumRemainingSectorBuffers: int
	NumSectorOverflows: int
	ReadBinSize: int
	def IsCoreMiniRunning(self) -> bool: ...

	def IsEncrypted(self) -> bool: ...

