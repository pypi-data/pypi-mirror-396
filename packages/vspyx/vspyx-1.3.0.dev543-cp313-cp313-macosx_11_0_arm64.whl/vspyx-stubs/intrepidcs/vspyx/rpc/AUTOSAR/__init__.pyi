import typing, enum, vspyx

@enum.unique
class ComSignalTypeEnumType(enum.IntFlag):
	ComSignalType_BOOLEAN = 0
	ComSignalType_FLOAT32 = 1
	ComSignalType_FLOAT64 = 2
	ComSignalType_SINT16 = 3
	ComSignalType_SINT32 = 4
	ComSignalType_SINT64 = 5
	ComSignalType_SINT8 = 6
	ComSignalType_UINT16 = 7
	ComSignalType_UINT32 = 8
	ComSignalType_UINT64 = 9
	ComSignalType_UINT8 = 10
	ComSignalType_UINT8_DYN = 11
	ComSignalType_UINT8_N = 12
	ComSignalTypeEnumType_INT_MIN_SENTINEL_DO_NOT_USE_ = -2147483648
	ComSignalTypeEnumType_INT_MAX_SENTINEL_DO_NOT_USE_ = 2147483647

