import typing, enum, vspyx

@enum.unique
class LiveDataValueType(enum.IntEnum):
	GPS_LATITUDE = 2
	GPS_LONGITUDE = 3
	GPS_ALTITUDE = 4
	GPS_SPEED = 5
	GPS_VALID = 6
	GPS_ENABLE = 62
	MANUAL_TRIGGER = 108
	TIME_SINCE_MSG = 111
	GPS_ACCURACY = 120
	GPS_BEARING = 121
	GPS_TIME = 122
	GPS_TIME_VALID = 123
	DAQ_ENABLE = 124

