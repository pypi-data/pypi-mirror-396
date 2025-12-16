import typing, enum, vspyx

@enum.unique
class Nrc(enum.IntEnum):
	PR = 0
	GR = 16
	SNS = 17
	SFNS = 18
	IMLOIF = 19
	RTL = 20
	BRR = 33
	CNC = 34
	RSE = 36
	NRFSC = 37
	FPEORA = 38
	ROOR = 49
	SAD = 51
	AR = 52
	IK = 53
	ENOA = 54
	RTDNE = 55
	SDTR = 56
	SDTNA = 57
	SDTF = 58
	CVFITP = 80
	CVFIS = 81
	CVFICOT = 82
	CVFIT = 83
	CVFIF = 84
	CVFIC = 85
	CVFISCP = 86
	CVFICERT = 87
	OVF = 88
	CCF = 89
	SARF = 90
	SKCDF = 91
	CDUF = 92
	DAF = 93
	UDNA = 112
	TDS = 113
	GPF = 114
	WBSC = 115
	RCRRP = 120
	SFNSIAS = 126
	SNSIAS = 127
	RPMTH = 129
	RPMTL = 130
	EIR = 131
	EINR = 132
	ERTTL = 133
	TEMPTH = 134
	TEMPTL = 135
	VSTH = 136
	VSTL = 137
	TPTH = 138
	TPTL = 139
	TRNIN = 140
	TRNIG = 141
	BSNC = 143
	SLNIP = 144
	TCCL = 145
	VTH = 146
	VTL = 147
	RTNA = 148

@enum.unique
class ServiceId(enum.IntEnum):
	Unknown = 0
	ResponseFlag = 64
	NegativeResponse = 127
	SessionControl = 16
	EcuReset = 17
	ClearDtcs = 20
	ReadDtcs = 25
	ReadDataById = 34
	ReadMemoryByAddress = 35
	SecurityAccess = 39
	CommControl = 40
	Authentication = 41
	ReadDataByPeriodicId = 42
	WriteDataById = 46
	IoControlById = 47
	RoutineControl = 49
	RequestDownload = 52
	RequestUpload = 53
	TransferData = 54
	RequestTransferExit = 55
	RequestFileTransfer = 56
	WriteMemoryByAddress = 61
	TesterPresent = 62
	ControlDtcSetting = 133

class Message:
	"""Message
	"""
	AssociatedService: vspyx.Diagnostics.ISO14229_1.Service
	Dissection: vspyx.Dissector.Message
	IsNegativeResponse: bool
	IsPositiveResponseSuppressedSpecified: bool
	PDU: typing.Any
	SID: vspyx.Diagnostics.ISO14229_1.ServiceId
	def assign(self, arg0: vspyx.Diagnostics.ISO14229_1.Message) -> vspyx.Diagnostics.ISO14229_1.Message: ...

	def ToRaw(self) -> vspyx.Core.BytesView: ...

class SubfunctionInfo:
	"""SubfunctionInfo
	"""
	Id: int
	SupportedSessions: typing.List[int]
	def assign(self, arg0: vspyx.Diagnostics.ISO14229_1.SubfunctionInfo) -> vspyx.Diagnostics.ISO14229_1.SubfunctionInfo: ...

	def MergeSupportedSessions(self, supportedSessions: typing.List[int]) -> typing.Any: ...

class Service:
	"""Service
	"""
	SECURITY_ANY: int
	SUBFUNCTION_SUPPRESS_RESPONSE: int
	DoService: vspyx.Core.Function_5a9221b5e8
	Name: str
	P4ServerMax: typing.Any
	RequestDecoder: vspyx.Core.Function_0667241c51
	ResponseDecoder: vspyx.Core.Function_0667241c51
	ResponseServiceId: vspyx.Diagnostics.ISO14229_1.ServiceId
	SecurityMask: int
	ServiceId: vspyx.Diagnostics.ISO14229_1.ServiceId
	ServiceSpecificChecks: vspyx.Core.Function_3e9c74fb75
	SupportedSessions: typing.List[int]

	@typing.overload
	def Configure(self, supportedSessions: typing.List[int], p4ServerMax: typing.Any) -> typing.Any: ...


	@typing.overload
	def Configure(self, supportedSessions: typing.List[int], p4ServerMax: typing.Any, supportedSubfunctions: typing.Any) -> typing.Any: ...


	@typing.overload
	def Configure(self, supportedSessions: typing.List[int], p4ServerMax: typing.Any, supportedSubfunctions: typing.Any, securityMask: typing.Any) -> typing.Any: ...

	def GetSubfunction(self, subfunction: int) -> vspyx.Diagnostics.ISO14229_1.SubfunctionInfo: ...

	def SetSupportedSubfunctions(self, supportedSubfunctions: typing.List[int]) -> typing.Any: ...

	def EnableSubfunctionsBySession(self, sessionId: int, supportedSubfunctions: typing.List[int]) -> typing.Any: ...

	def IsServiceIdMatch(self, sid: int) -> bool: ...

	def IsResponseRequired(self, data: typing.List[int]) -> bool: ...

	def IsServiceSupportedInSession(self, sessionId: int) -> bool: ...

	def IsSubfunctionSupported(self, subfunction: int, sessionId: typing.Any) -> bool: ...

	def Execute(self, message: vspyx.Diagnostics.ISO14229_1.Message) -> vspyx.Diagnostics.ISO14229_1.Message: ...

