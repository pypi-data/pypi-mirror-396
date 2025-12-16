import typing, enum, vspyx

@enum.unique
class Directions(enum.IntFlag):
	DIRECTION_IN = 0
	DIRECTION_OUT = 1
	Directions_INT_MIN_SENTINEL_DO_NOT_USE_ = -2147483648
	Directions_INT_MAX_SENTINEL_DO_NOT_USE_ = 2147483647

@enum.unique
class SoAdPduHeaderLengthEncodingEnumType(enum.IntFlag):
	SoAdPduHeaderLengthStandard = 0
	SoAdPduHeaderLengthCANFD = 1
	SoAdPduHeaderLengthEncodingEnumType_INT_MIN_SENTINEL_DO_NOT_USE_ = -2147483648
	SoAdPduHeaderLengthEncodingEnumType_INT_MAX_SENTINEL_DO_NOT_USE_ = 2147483647

@enum.unique
class ECUMode(enum.IntFlag):
	Disabled = 0
	Passive = 1
	Active = 2
	ECUMode_INT_MIN_SENTINEL_DO_NOT_USE_ = -2147483648
	ECUMode_INT_MAX_SENTINEL_DO_NOT_USE_ = 2147483647

