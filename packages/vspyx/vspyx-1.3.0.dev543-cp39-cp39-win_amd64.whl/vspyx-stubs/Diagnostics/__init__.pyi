import typing, enum, vspyx
from . import ISO14229_1, ISO14229_Services

class ISO13400_2(vspyx.Communication.ISOStandardizedServicePrimitiveInterface, vspyx.Runtime.Component):
	"""Represents the ISO-13400 transport layer
	 
	"""
	"""ISO13400_2
	"""
	@enum.unique
	class DoIPHeaderNackCodes(enum.IntEnum):
		IncorrectPatternFormat = 0
		UnknownPayloadType = 1
		MessageTooLarge = 2
		OutOfMemory = 3
		InvalidPayloadLength = 4

	@enum.unique
	class ProtocolVersions(enum.IntEnum):
		Reserved_00 = 0
		ISO13400_2_2010 = 1
		ISO13400_2_2012 = 2
		VehicleIdentificationRequestDefault = 255
		Legacy_HSFZ = 0

	@enum.unique
	class DoIP_PayloadTypes(enum.IntEnum):
		GenericDoIPHeaderNegativeAck = 0
		VehicleIdentificationRequest = 1
		VehicleIdentificationRequestWithEID = 2
		VehicleIdentificationRequestWithVIN = 3
		VehicleIdentificationResponse = 4
		VehicleAnnouncement = 4
		RoutingActivationRequest = 5
		RoutingActivationResponse = 6
		AliveCheckRequest = 7
		AliveCheckResponse = 8
		DoIPEntityStatusRequest = 16385
		DoIPEntityStatusResponse = 16386
		DiagnosticPowerModeInfoRequest = 16387
		DiagnosticPowerModeInfoResponse = 16388
		DiagnosticMessage = 32769
		DiagnosticMessagePositiveAck = 32770
		DiagnosticMessageNegativeAck = 32771

	@enum.unique
	class HSFZ_PayloadTypes(enum.IntEnum):
		DiagnosticMessage = 1
		DiagnosticMessageAck = 2
		Terminal15Control = 16
		VehicleIdentificationData = 17
		AliveCheck = 18
		StatusDataInquiry = 19
		Error_IncorrectTesterAddress = 64
		Error_IncorrectControlWord = 65
		Error_IncorrectFormat = 66
		Error_IncorrectDestinationAddress = 67
		Error_MessageTooLarge = 68
		Error_DiagnosticApplicationNotReady = 69
		Error_OutOfMemory = 255

	@enum.unique
	class EntityIdActivationRequirements(enum.IntEnum):
		NoFurtherActionRequired = 0
		ActivationRequiredForCentralSecurity = 16

	@enum.unique
	class EntityIdSyncStatuses(enum.IntEnum):
		Synchronized = 0
		Incomplete = 16

	@enum.unique
	class RoutingActivationTypes(enum.IntEnum):
		Default = 0
		WWH_OBD = 1
		CentralSecurity = 224

	@enum.unique
	class RoutingActivationResponseCode(enum.IntEnum):
		UnknownSourceAddress = 0
		HostUnavailable = 1
		SocketAlreadyInUse = 2
		SocketAlreadyActivated = 3
		MissingAuthentication = 4
		ConfirmationRejected = 5
		UnsupportedRoutingActivationType = 6
		Success = 16
		ConfirmationPending = 17

	@enum.unique
	class DiagnosticAckCodes(enum.IntEnum):
		Confirm = 0
		InvalidSourceAddress = 2
		UnknownTargetAddress = 3
		DiagnosticMessageTooLarge = 4
		OutOfMemory = 5
		TargetUnreachable = 6
		UnknownNetwork = 7
		TransportProtocolError = 8

	@enum.unique
	class DiagnosticPowerModes(enum.IntEnum):
		NotReady = 0
		Ready = 1
		NotSupported = 2

	@enum.unique
	class EntityNodeTypes(enum.IntEnum):
		Gateway = 0
		Node = 1

	@enum.unique
	class ConnectionStates(enum.IntEnum):
		Inactive = 0
		Initialized = 1
		Registered = 128
		Registered_PendingAuth = 144
		Registered_PendingConf = 160
		Registered_RoutingActive = 192
		Finalize = 2

	OnDoIPNack: vspyx.Core.Function_547343b45b
	OnGetEntityInfo: vspyx.Core.Function_73ca7225f3
	OnRoutingActivationRequested: vspyx.Core.Function_5249a6cbf7
	OnRoutingActivationResponse: vspyx.Core.Function_5249a6cbf7
	OnValidateRoutingActivationRequest: vspyx.Core.Function_5249a6cbf7
	OnRouteClose: vspyx.Core.Function_5249a6cbf7
	OnVehicleAnnouncement: vspyx.Core.Function_28e4df9122
	OnDiagnosticPowerModeRequest: vspyx.Core.Function_61306504cc
	OnDiagnosticPowerModeResponse: vspyx.Core.Function_0c9c5a29fc
	OnEntityStatusRequest: vspyx.Core.Function_e4191e7529
	OnEntityStatusResponse: vspyx.Core.Function_09abcda68b
	Port_HSFZ_ClientDiscovery: int
	Port_HSFZ_Control: int
	Port_HSFZ_Diagnostics: int
	Port_HSFZ_Discovery: int
	Port_TcpData: int
	Port_UdpDiscovery: int

	@staticmethod
	@typing.overload
	def New() -> vspyx.Diagnostics.ISO13400_2: ...


	@staticmethod
	@typing.overload
	def New(isEntityHost: bool) -> vspyx.Diagnostics.ISO13400_2: ...


	@staticmethod
	@typing.overload
	def New(isEntityHost: bool, isIPv6: bool) -> vspyx.Diagnostics.ISO13400_2: ...


	@staticmethod
	@typing.overload
	def New(isEntityHost: bool, isIPv6: bool, maxVersion: vspyx.Diagnostics.ISO13400_2.ProtocolVersions) -> vspyx.Diagnostics.ISO13400_2: ...

	def Attach(self, network: vspyx.TCPIP.Network) -> typing.Any: ...

	def Detach(self) -> typing.Any: ...


	@typing.overload
	def AddDoIPEntity(self, address: str, entityAddress: int) -> typing.Any: ...


	@typing.overload
	def AddDoIPEntity(self, address: str, entityAddress: int, vin: typing.Any) -> typing.Any: ...


	@typing.overload
	def AddDoIPEntity(self, address: str, entityAddress: int, vin: typing.Any, eid: typing.Any) -> typing.Any: ...


	@typing.overload
	def AddDoIPEntity(self, address: str, entityAddress: int, vin: typing.Any, eid: typing.Any, gid: typing.Any) -> typing.Any: ...

	def SetBroadcastAddress(self, address: str) -> typing.Any: ...

	def SetClientDiscoveryPort(self, port: int) -> typing.Any: ...

	def SetCurrentVersion(self, version: vspyx.Diagnostics.ISO13400_2.ProtocolVersions) -> typing.Any: ...

	def SetNodeType(self, nodeType: vspyx.Diagnostics.ISO13400_2.EntityNodeTypes) -> typing.Any: ...

	def SetMaxDataChannelCount(self, maxConnectionCount: int) -> typing.Any: ...

	def SetMaxPayloadLength(self, maxLength: int) -> typing.Any: ...

	def SetAvailableMemory(self, availableMemory: int) -> typing.Any: ...

	def SetAliveCheckResponseInhibit(self, inhibit: bool) -> typing.Any: ...

	def SetAutoVehicleIdentificationRequest(self, enabled: bool) -> typing.Any: ...

	def SetDiagnosticAckInhibit(self, inhibit: bool) -> typing.Any: ...

	def SetClientDiagnosticAckExpected(self, enable: bool) -> typing.Any: ...

	def NotifyAuthOrConfChange(self, ipAddress: vspyx.Core.IPAddressAndPort, entityAddress: int) -> typing.Any: ...

	def GetVehicleIdentification(self, address: typing.Any) -> typing.Any: ...

	def GetVehicleIdentificationByEID(self, eid: typing.List[int], address: typing.Any) -> typing.Any: ...

	def GetVehicleIdentificationByVIN(self, vin: typing.List[int], address: typing.Any) -> typing.Any: ...

	def GetPowerMode(self, address: vspyx.Core.IPAddress) -> typing.Any: ...

	def GetEntityStatusInfo(self, address: vspyx.Core.IPAddress) -> typing.Any: ...

	def SendAliveCheckRequest(self, address: typing.Any) -> typing.Any: ...

	def SendAliveCheckResponse(self, address: typing.Any) -> typing.Any: ...

	class EntityStatusInfo:
		"""EntityStatusInfo
		"""
		NodeType: vspyx.Diagnostics.ISO13400_2.EntityNodeTypes
		TcpSocketsMax: int
		TcpSocketsCount: int
		DataSizeMax: typing.Any


	class DoIPHeader:
		"""DoIPHeader
		"""
		ProtocolVersion: vspyx.Diagnostics.ISO13400_2.ProtocolVersions
		PayloadType: vspyx.Diagnostics.ISO13400_2.DoIP_PayloadTypes
		PayloadLength: int
		PayloadStartOffset: int


	class EntityIdentificationInfo:
		"""EntityIdentificationInfo
		"""
		Address: int
		VIN: typing.List[int]
		GID: typing.List[int]
		EID: typing.List[int]
		ActivationRequirement: vspyx.Diagnostics.ISO13400_2.EntityIdActivationRequirements
		SyncStatus: typing.Any
		def Initialize(self, vin: int, eid: int, gid: int, activationRequirement: typing.Any, syncStatus: typing.Any) -> typing.Any: ...


	class RouteAuthenticationInfo:
		"""RouteAuthenticationInfo
		"""
		IsAuthenticated: bool
		def assign(self, arg0: vspyx.Diagnostics.ISO13400_2.RouteAuthenticationInfo) -> vspyx.Diagnostics.ISO13400_2.RouteAuthenticationInfo: ...


	class RouteConfirmationInfo:
		"""RouteConfirmationInfo
		"""
		@enum.unique
		class Status(enum.IntEnum):
			Pending = 0
			Confirmed = 1
			Rejected = 2

		State: vspyx.Diagnostics.ISO13400_2.RouteConfirmationInfo.Status
		def assign(self, arg0: vspyx.Diagnostics.ISO13400_2.RouteConfirmationInfo) -> vspyx.Diagnostics.ISO13400_2.RouteConfirmationInfo: ...


	class EntityRouteStatus:
		"""EntityRouteStatus
		"""
		Address: int
		HostedAddresses: typing.List[int]
		IsActivationTypeValid: bool
		AuthenticationInfo: vspyx.Diagnostics.ISO13400_2.RouteAuthenticationInfo
		ConfirmationInfo: vspyx.Diagnostics.ISO13400_2.RouteConfirmationInfo


	class ActivationRequestArgs:
		"""ActivationRequestArgs
		"""
		IPAddress: vspyx.Core.IPAddressAndPort
		Address: int
		ActivationType: typing.Any
		ISOReservedData_Req: typing.Any
		ISOReservedData_Rsp: typing.Any
		OEMReservedData_Req: typing.Any
		OEMReservedData_Rsp: typing.Any
		Result: typing.Any


class ISO14229_2(vspyx.Runtime.Component):
	"""Represents the ISO-14229 session layer management function
	 
	"""
	"""ISO14229_2
	"""
	@enum.unique
	class Result(enum.IntEnum):
		S_OK_ = 0
		S_NOK = 1

	@enum.unique
	class SessionOperation(enum.IntEnum):
		NONE = 0
		PendingResponse = 1
		NegativeResponse = 2
		ChangeSessionToDefault = 3
		ChangeSessionToNonDefault = 4
		KeepAlive = 5

	@enum.unique
	class PerformanceRequirements(enum.IntEnum):
		P2server = 0
		P2star_server = 1
		P4server = 2

	@enum.unique
	class Timers(enum.IntEnum):
		P2server = 0
		S3server = 1
		Pclient = 2
		P3client_phys = 3
		P3client_func = 4
		S3client = 5

	GetServiceCompletionEstimate: vspyx.Core.Function_bdddaff1f6
	GetSessionParameters: vspyx.Core.Function_56e4d3d208
	KeepAliveRequired_P2: vspyx.Core.Function_3959d5f14a
	KeepAliveRequired_S3: vspyx.Core.Function_3959d5f14a
	OnActivityStarted: vspyx.Core.Callback_634bd5c449
	OnActivityStopped: vspyx.Core.Callback_634bd5c449
	OnPerformanceRequirementMeasured: vspyx.Core.Callback_bb1915aca6
	OnTimerExpired: vspyx.Core.Callback_6f8935cd9b
	OnTimerStarted: vspyx.Core.Callback_6f8935cd9b
	S_Data_confirm: vspyx.Core.Callback_517595a0fb
	S_Data_indication: vspyx.Core.Callback_0da149c8bd
	SessionId: int
	T_Data: vspyx.Communication.ISOStandardizedServicePrimitiveInterface

	@typing.overload
	def S_Data_request(self, S_Mtype: vspyx.Communication.ISOStandardizedServicePrimitiveInterface.MessageType, S_SA: int, S_TA: int, S_TAtype: int, S_AE: typing.Any, S_Data: vspyx.Core.BytesView, S_Length: int) -> typing.Any: ...


	@typing.overload
	def S_Data_request(self, S_Mtype: vspyx.Communication.ISOStandardizedServicePrimitiveInterface.MessageType, S_SA: int, S_TA: int, S_TAtype: int, S_AE: typing.Any, S_Data: vspyx.Core.BytesView, S_Length: int, responseRequired: bool) -> typing.Any: ...


	@staticmethod
	def DefaultP2_server_max() -> typing.Any: ...


	@staticmethod
	def DefaultP2star_server_max() -> typing.Any: ...


	@staticmethod
	def DefaultDeltaP2() -> typing.Any: ...


	@staticmethod
	def DefaultDeltaP6() -> typing.Any: ...


	@staticmethod
	def DefaultP2_client_max() -> typing.Any: ...


	@staticmethod
	def DefaultP2star_client_max() -> typing.Any: ...


	@staticmethod
	def DefaultP3_client_func_max() -> typing.Any: ...


	@staticmethod
	def DefaultP6_client_max() -> typing.Any: ...


	@staticmethod
	def DefaultP6star_client_max() -> typing.Any: ...


	@staticmethod
	def DefaultS3_client_timeout() -> typing.Any: ...


	@staticmethod
	def DefaultS3_server_timeout() -> typing.Any: ...


	@staticmethod
	def DefaultP2_server_keepalive_ratio() -> float: ...


	@staticmethod
	def DefaultExtractSessionOperation() -> vspyx.Core.Function_d90e283472: ...


	@staticmethod
	@typing.overload
	def NewServer() -> vspyx.Diagnostics.ISO14229_2: ...


	@staticmethod
	@typing.overload
	def NewServer(parameters: vspyx.Diagnostics.ISO14229_2.Parameters) -> vspyx.Diagnostics.ISO14229_2: ...


	@staticmethod
	@typing.overload
	def NewClient() -> vspyx.Diagnostics.ISO14229_2: ...


	@staticmethod
	@typing.overload
	def NewClient(parameters: vspyx.Diagnostics.ISO14229_2.Parameters) -> vspyx.Diagnostics.ISO14229_2: ...

	def Attach(self, T_Data: vspyx.Communication.ISOStandardizedServicePrimitiveInterface) -> typing.Any: ...

	def Detach(self) -> typing.Any: ...

	def GetClientResponseLimit(self, isFunctional: bool) -> int: ...

	def NotifyServiceStarting(self, Mtype: vspyx.Communication.ISOStandardizedServicePrimitiveInterface.MessageType, SA: int, TA: int, TAtype: int, AE: typing.Any, Data: vspyx.Core.BytesView, Length: int) -> bool: ...

	def NotifyServiceComplete(self) -> bool: ...

	def ConfirmServerSessionChange(self, sessionId: int, isDefaultSession: bool, p2server_max: typing.Any, p2starServer_max: typing.Any) -> typing.Any: ...

	def GetTimerRemaining(self, timer: vspyx.Diagnostics.ISO14229_2.Timers) -> typing.Any: ...

	class SessionParameters:
		"""SessionParameters
		"""
		P2timeout: typing.Any
		P2starTimeout: typing.Any
		S3timeout: typing.Any
		SessionId: typing.Any


	class Parameters:
		"""Parameters
		"""
		P2_server_max: typing.Any
		P2star_server_max: typing.Any
		DeltaP2: typing.Any
		DeltaP6: typing.Any
		P2_client_max: typing.Any
		P2star_client_max: typing.Any
		P3_client_func_max: typing.Any
		P6_client_max: typing.Any
		P6star_client_max: typing.Any
		S3_client_timeout: typing.Any
		S3_server_timeout: typing.Any
		MaxRetries: int
		P2_server_keepalive_ratio_Max: float
		P2_server_keepalive_ratio_Min: float
		P2_server_keepalive_ratio: float
		MaxFunctionalReplies: int
		ExtractSessionOperation: vspyx.Core.Function_d90e283472


class ISO14229_1ClientApplicationLayerProtocol(vspyx.Runtime.Component):
	"""Represents the ISO-14229 client application protocol layer function
	 
	"""
	"""ISO14229_1ClientApplicationLayerProtocol
	"""
	OnEvent: vspyx.Core.Function_69a627028d
	CreateKeepAliveMessage_S3: vspyx.Core.Function_d13314ef69

	@staticmethod
	def New() -> vspyx.Diagnostics.ISO14229_1ClientApplicationLayerProtocol: ...

	def Attach(self, session: vspyx.Diagnostics.ISO14229_2) -> typing.Any: ...

	def Detach(self) -> typing.Any: ...


	@typing.overload
	def Request(self, pdu: typing.Any) -> typing.List[typing.Any]: ...


	@typing.overload
	def Request(self, pdu: typing.Any, positiveResponseSuppressed: bool) -> typing.List[typing.Any]: ...

class ISO14229_1ServerApplicationLayerProtocol(vspyx.Runtime.Component):
	"""Represents the ISO-14229 server application protocol layer function
	 
	"""
	"""ISO14229_1ServerApplicationLayerProtocol
	"""
	GetHostAddressInfo: vspyx.Core.Function_cd10fb84ee
	GetServiceCompletionEstimate: vspyx.Core.Function_bdddaff1f6
	VetServiceOemSpecificPhase1: vspyx.Core.Function_3e9c74fb75
	VetServiceSupported: vspyx.Core.Function_3e9c74fb75
	VetServiceSecurityCheck: vspyx.Core.Function_3e9c74fb75
	VetServiceOemSpecificPhase2: vspyx.Core.Function_3e9c74fb75
	IsServiceWithSubfunction: vspyx.Core.Function_67e255d395
	VetServiceSubfunction: vspyx.Core.Function_3e9c74fb75
	VetServiceSubfunctionSecurityCheck: vspyx.Core.Function_3e9c74fb75
	VetServiceSubfunctionSequence: vspyx.Core.Function_3e9c74fb75
	VetServiceSubfunctionOemSpecific: vspyx.Core.Function_3e9c74fb75
	VetServiceSpecificChecks: vspyx.Core.Function_3e9c74fb75
	CreateNegativeResponse: vspyx.Core.Function_d13314ef69
	CreateKeepAliveMessage_P2: vspyx.Core.Function_d13314ef69
	OnServiceStartRequest: vspyx.Core.Callback_69a627028d
	SessionId: int

	@staticmethod
	def New() -> vspyx.Diagnostics.ISO14229_1ServerApplicationLayerProtocol: ...

	def Attach(self, session: vspyx.Diagnostics.ISO14229_2) -> typing.Any: ...

	def Detach(self) -> typing.Any: ...

	def NotifyServiceComplete(self) -> bool: ...

	def Respond(self, messageType: vspyx.Communication.ISOStandardizedServicePrimitiveInterface.MessageType, ta: int, ae: typing.Any, rawMessage: vspyx.Core.BytesView) -> typing.Any: ...

class ISO14229_ServiceClient(vspyx.Runtime.Component):
	"""Represents the ISO-14229 client application service layer function
		 
	"""
	"""ISO14229_ServiceClient
	"""
	TargetAddress: typing.Any
	ResolveDecoder: vspyx.Core.Function_0667241c51
	OnResponse: vspyx.Core.Function_5a9221b5e8
	OnUnsolicitedResponse: vspyx.Core.Function_5a9221b5e8
	ServiceConfig: vspyx.Diagnostics.ISO14229_Services.ServiceConfig

	@staticmethod
	def New() -> vspyx.Diagnostics.ISO14229_ServiceClient: ...

	def Attach(self, client: vspyx.Diagnostics.ISO14229_1ClientApplicationLayerProtocol) -> typing.Any: ...

	def Detach(self) -> typing.Any: ...


	@typing.overload
	def GenericService(self, request: vspyx.Core.BytesView) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def GenericService(self, request: vspyx.Core.BytesView, address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def GenericService(self, request: vspyx.Core.BytesView, address: typing.Any, isPositiveResponseSuppressed: bool) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def SessionControl(self, sessionId: int) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def SessionControl(self, sessionId: int, address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def SessionControl(self, sessionId: int, address: typing.Any, isPositiveResponseSuppressed: bool) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def EcuReset(self, resetType: vspyx.Diagnostics.ISO14229_Services.EcuResetTypes) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def EcuReset(self, resetType: vspyx.Diagnostics.ISO14229_Services.EcuResetTypes, address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def EcuReset(self, resetType: vspyx.Diagnostics.ISO14229_Services.EcuResetTypes, address: typing.Any, isPositiveResponseSuppressed: bool) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ClearDtcs(self, group: int) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ClearDtcs(self, group: int, memorySelection: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ClearDtcs(self, group: int, memorySelection: typing.Any, address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDtcs(self, reportType: vspyx.Diagnostics.ISO14229_Services.ReadDtcsReportTypes) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDtcs(self, reportType: vspyx.Diagnostics.ISO14229_Services.ReadDtcsReportTypes, address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDtcs(self, reportType: vspyx.Diagnostics.ISO14229_Services.ReadDtcsReportTypes, address: typing.Any, isPositiveResponseSuppressed: bool) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDtcs_ByStatusMaskOrRecordNr(self, reportType: vspyx.Diagnostics.ISO14229_Services.ReadDtcsReportTypes, statusMaskOrRecordNr: int) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDtcs_ByStatusMaskOrRecordNr(self, reportType: vspyx.Diagnostics.ISO14229_Services.ReadDtcsReportTypes, statusMaskOrRecordNr: int, address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDtcs_ByStatusMaskOrRecordNr(self, reportType: vspyx.Diagnostics.ISO14229_Services.ReadDtcsReportTypes, statusMaskOrRecordNr: int, address: typing.Any, isPositiveResponseSuppressed: bool) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDtcs_SnapshotRecordByDtc(self, dtcMask: int, snapshotRecordNr: int) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDtcs_SnapshotRecordByDtc(self, dtcMask: int, snapshotRecordNr: int, address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDtcs_SnapshotRecordByDtc(self, dtcMask: int, snapshotRecordNr: int, address: typing.Any, isPositiveResponseSuppressed: bool) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDtcs_ExtDataByDtc(self, reportType: vspyx.Diagnostics.ISO14229_Services.ReadDtcsReportTypes, dtcMask: int, recordNr: int) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDtcs_ExtDataByDtc(self, reportType: vspyx.Diagnostics.ISO14229_Services.ReadDtcsReportTypes, dtcMask: int, recordNr: int, address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDtcs_ExtDataByDtc(self, reportType: vspyx.Diagnostics.ISO14229_Services.ReadDtcsReportTypes, dtcMask: int, recordNr: int, address: typing.Any, isPositiveResponseSuppressed: bool) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDtcs_BySeverity(self, reportType: vspyx.Diagnostics.ISO14229_Services.ReadDtcsReportTypes, severityMask: int, statusMask: int) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDtcs_BySeverity(self, reportType: vspyx.Diagnostics.ISO14229_Services.ReadDtcsReportTypes, severityMask: int, statusMask: int, address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDtcs_BySeverity(self, reportType: vspyx.Diagnostics.ISO14229_Services.ReadDtcsReportTypes, severityMask: int, statusMask: int, address: typing.Any, isPositiveResponseSuppressed: bool) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDtcs_SeverityInfoOfDtc(self, dtcMask: int) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDtcs_SeverityInfoOfDtc(self, dtcMask: int, address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDtcs_SeverityInfoOfDtc(self, dtcMask: int, address: typing.Any, isPositiveResponseSuppressed: bool) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDtcs_UserMemDtcByStatus(self, statusMask: int, memorySelection: int) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDtcs_UserMemDtcByStatus(self, statusMask: int, memorySelection: int, address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDtcs_UserMemDtcByStatus(self, statusMask: int, memorySelection: int, address: typing.Any, isPositiveResponseSuppressed: bool) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDtcs_UserMemExtDataByDtc(self, reportType: vspyx.Diagnostics.ISO14229_Services.ReadDtcsReportTypes, dtcMask: typing.Any, recordNr: int, memorySelection: int) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDtcs_UserMemExtDataByDtc(self, reportType: vspyx.Diagnostics.ISO14229_Services.ReadDtcsReportTypes, dtcMask: typing.Any, recordNr: int, memorySelection: int, address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDtcs_UserMemExtDataByDtc(self, reportType: vspyx.Diagnostics.ISO14229_Services.ReadDtcsReportTypes, dtcMask: typing.Any, recordNr: int, memorySelection: int, address: typing.Any, isPositiveResponseSuppressed: bool) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDtcs_ObdDtc(self, reportType: vspyx.Diagnostics.ISO14229_Services.ReadDtcsReportTypes, functionalGroupId: int, statusMask: typing.Any, severityMask: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDtcs_ObdDtc(self, reportType: vspyx.Diagnostics.ISO14229_Services.ReadDtcsReportTypes, functionalGroupId: int, statusMask: typing.Any, severityMask: typing.Any, address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDtcs_ObdDtc(self, reportType: vspyx.Diagnostics.ISO14229_Services.ReadDtcsReportTypes, functionalGroupId: int, statusMask: typing.Any, severityMask: typing.Any, address: typing.Any, isPositiveResponseSuppressed: bool) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDataById(self, dids: typing.List[int]) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDataById(self, dids: typing.List[int], address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadMemoryByAddress(self, memorySpecifierSize: int, addressSpecifierSize: int, memoryAddress: int, memorySize: int) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadMemoryByAddress(self, memorySpecifierSize: int, addressSpecifierSize: int, memoryAddress: int, memorySize: int, address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def SecurityAccess(self, accessType: int) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def SecurityAccess(self, accessType: int, parameter: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def SecurityAccess(self, accessType: int, parameter: typing.Any, address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def SecurityAccess(self, accessType: int, parameter: typing.Any, address: typing.Any, isPositiveResponseSuppressed: bool) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def CommunicationControl(self, controlType: vspyx.Diagnostics.ISO14229_Services.CommControlTypes, commType: int) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def CommunicationControl(self, controlType: vspyx.Diagnostics.ISO14229_Services.CommControlTypes, commType: int, nodeId: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def CommunicationControl(self, controlType: vspyx.Diagnostics.ISO14229_Services.CommControlTypes, commType: int, nodeId: typing.Any, address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def CommunicationControl(self, controlType: vspyx.Diagnostics.ISO14229_Services.CommControlTypes, commType: int, nodeId: typing.Any, address: typing.Any, isPositiveResponseSuppressed: bool) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def Authentication_DeAuthenticate(self) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def Authentication_DeAuthenticate(self, address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def Authentication_DeAuthenticate(self, address: typing.Any, isPositiveResponseSuppressed: bool) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def Authentication_Configuration(self) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def Authentication_Configuration(self, address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def Authentication_Configuration(self, address: typing.Any, isPositiveResponseSuppressed: bool) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def Authentication_VerifyCertificate(self, isBidirectional: bool, communicationConfiguration: int, certificateClient: typing.List[int], challengeClient: typing.List[int]) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def Authentication_VerifyCertificate(self, isBidirectional: bool, communicationConfiguration: int, certificateClient: typing.List[int], challengeClient: typing.List[int], address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def Authentication_VerifyCertificate(self, isBidirectional: bool, communicationConfiguration: int, certificateClient: typing.List[int], challengeClient: typing.List[int], address: typing.Any, isPositiveResponseSuppressed: bool) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def Authentication_ProofOfOwnership(self, proofOfOwnershipClient: typing.List[int], ephemeralPublicKeyClient: typing.List[int]) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def Authentication_ProofOfOwnership(self, proofOfOwnershipClient: typing.List[int], ephemeralPublicKeyClient: typing.List[int], address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def Authentication_ProofOfOwnership(self, proofOfOwnershipClient: typing.List[int], ephemeralPublicKeyClient: typing.List[int], address: typing.Any, isPositiveResponseSuppressed: bool) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def Authentication_TransmitCertificate(self, certificateEvaluationId: int, certificateData: typing.List[int]) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def Authentication_TransmitCertificate(self, certificateEvaluationId: int, certificateData: typing.List[int], address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def Authentication_TransmitCertificate(self, certificateEvaluationId: int, certificateData: typing.List[int], address: typing.Any, isPositiveResponseSuppressed: bool) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def Authentication_RequestChallenge(self, communicationConfiguration: int, algorithmIndicator: typing.List[int]) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def Authentication_RequestChallenge(self, communicationConfiguration: int, algorithmIndicator: typing.List[int], address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def Authentication_RequestChallenge(self, communicationConfiguration: int, algorithmIndicator: typing.List[int], address: typing.Any, isPositiveResponseSuppressed: bool) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def Authentication_VerifyProofOfOwnership(self, isBidirectional: bool, algorithmIndicator: typing.List[int], proofOfOwnershipClient: typing.List[int], challengeClient: typing.List[int], additionalParameter: typing.List[int]) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def Authentication_VerifyProofOfOwnership(self, isBidirectional: bool, algorithmIndicator: typing.List[int], proofOfOwnershipClient: typing.List[int], challengeClient: typing.List[int], additionalParameter: typing.List[int], address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def Authentication_VerifyProofOfOwnership(self, isBidirectional: bool, algorithmIndicator: typing.List[int], proofOfOwnershipClient: typing.List[int], challengeClient: typing.List[int], additionalParameter: typing.List[int], address: typing.Any, isPositiveResponseSuppressed: bool) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDataByPeriodicId(self, mode: vspyx.Diagnostics.ISO14229_Services.TransmissionMode, pids: typing.List[int]) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ReadDataByPeriodicId(self, mode: vspyx.Diagnostics.ISO14229_Services.TransmissionMode, pids: typing.List[int], address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def WriteDataById(self, did: int, record: typing.List[int]) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def WriteDataById(self, did: int, record: typing.List[int], address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def IoControlById(self, did: int, controlType: vspyx.Diagnostics.ISO14229_Services.IoControlTypes, record: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def IoControlById(self, did: int, controlType: vspyx.Diagnostics.ISO14229_Services.IoControlTypes, record: typing.Any, mask: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def IoControlById(self, did: int, controlType: vspyx.Diagnostics.ISO14229_Services.IoControlTypes, record: typing.Any, mask: typing.Any, address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def RoutineControl(self, controlType: vspyx.Diagnostics.ISO14229_Services.RoutineControlTypes, rid: int, options: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def RoutineControl(self, controlType: vspyx.Diagnostics.ISO14229_Services.RoutineControlTypes, rid: int, options: typing.Any, address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def RoutineControl(self, controlType: vspyx.Diagnostics.ISO14229_Services.RoutineControlTypes, rid: int, options: typing.Any, address: typing.Any, isPositiveResponseSuppressed: bool) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def RequestDownload(self, memorySpecifierSize: int, addressSpecifierSize: int, memoryAddress: int, memorySize: int) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def RequestDownload(self, memorySpecifierSize: int, addressSpecifierSize: int, memoryAddress: int, memorySize: int, compressionMethod: int) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def RequestDownload(self, memorySpecifierSize: int, addressSpecifierSize: int, memoryAddress: int, memorySize: int, compressionMethod: int, encryptionMethod: int) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def RequestDownload(self, memorySpecifierSize: int, addressSpecifierSize: int, memoryAddress: int, memorySize: int, compressionMethod: int, encryptionMethod: int, address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def RequestUpload(self, memorySpecifierSize: int, addressSpecifierSize: int, memoryAddress: int, memorySize: int) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def RequestUpload(self, memorySpecifierSize: int, addressSpecifierSize: int, memoryAddress: int, memorySize: int, compressionMethod: int) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def RequestUpload(self, memorySpecifierSize: int, addressSpecifierSize: int, memoryAddress: int, memorySize: int, compressionMethod: int, encryptionMethod: int) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def RequestUpload(self, memorySpecifierSize: int, addressSpecifierSize: int, memoryAddress: int, memorySize: int, compressionMethod: int, encryptionMethod: int, address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def TransferData(self, blockSequenceCounter: int, record: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def TransferData(self, blockSequenceCounter: int, record: typing.Any, address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def RequestTransferExit(self, parameters: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def RequestTransferExit(self, parameters: typing.Any, address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def RequestFileTransfer(self, modeOfOperation: vspyx.Diagnostics.ISO14229_Services.FileTransfer_ModeOfOperation, filePathAndName: typing.List[int], compressionMethod: typing.Any, encryptionMethod: typing.Any, fileSizeParameterLength: typing.Any, fileSizeUnCompressed: typing.Any, fileSizeCompressed: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def RequestFileTransfer(self, modeOfOperation: vspyx.Diagnostics.ISO14229_Services.FileTransfer_ModeOfOperation, filePathAndName: typing.List[int], compressionMethod: typing.Any, encryptionMethod: typing.Any, fileSizeParameterLength: typing.Any, fileSizeUnCompressed: typing.Any, fileSizeCompressed: typing.Any, address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def WriteMemoryByAddress(self, memorySpecifierSize: int, addressSpecifierSize: int, memoryAddress: int, memorySize: int, record: typing.List[int]) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def WriteMemoryByAddress(self, memorySpecifierSize: int, addressSpecifierSize: int, memoryAddress: int, memorySize: int, record: typing.List[int], address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def TesterPresent(self) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def TesterPresent(self, address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def TesterPresent(self, address: typing.Any, isPositiveResponseSuppressed: bool) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ControlDtcSetting(self, settingType: vspyx.Diagnostics.ISO14229_Services.ControlDtcSettingTypes) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ControlDtcSetting(self, settingType: vspyx.Diagnostics.ISO14229_Services.ControlDtcSettingTypes, parameter: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ControlDtcSetting(self, settingType: vspyx.Diagnostics.ISO14229_Services.ControlDtcSettingTypes, parameter: typing.Any, address: typing.Any) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...


	@typing.overload
	def ControlDtcSetting(self, settingType: vspyx.Diagnostics.ISO14229_Services.ControlDtcSettingTypes, parameter: typing.Any, address: typing.Any, isPositiveResponseSuppressed: bool) -> vspyx.Diagnostics.ISO14229_Services.TransactionResults: ...

	def DefaultCreateKeepAliveMessage_S3(self, pdu: typing.Any, nrc: typing.Any) -> vspyx.Core.BytesView: ...

	def DefaultOnEvent(self, pdu: typing.Any) -> typing.Any: ...

class ISO14229_ServiceServer(vspyx.Runtime.Component):
	"""Represents the ISO-14229 server application service layer function
		 
	"""
	"""ISO14229_ServiceServer
	"""
	ResolveDecoder: vspyx.Core.Function_0667241c51
	OnRequest: vspyx.Core.Function_5a9221b5e8
	ServiceConfig: vspyx.Diagnostics.ISO14229_Services.ServiceConfig

	@staticmethod
	def New() -> vspyx.Diagnostics.ISO14229_ServiceServer: ...

	def Attach(self, interface: vspyx.Diagnostics.ISO14229_1ServerApplicationLayerProtocol) -> typing.Any: ...

	def Detach(self) -> typing.Any: ...

	def HandleService(self, message: vspyx.Diagnostics.ISO14229_1.Message) -> vspyx.Diagnostics.ISO14229_1.Message: ...

	def DefaultGetServiceCompletionEstimate(self, S_Data: vspyx.Core.BytesView, S_Length: int) -> typing.Any: ...

	def DefaultIsServiceWithSubfunction(self, service: vspyx.Diagnostics.ISO14229_1.Service, pdu: typing.Any) -> bool: ...

	def DefaultVetServiceSupported(self, service: vspyx.Diagnostics.ISO14229_1.Service, pdu: typing.Any) -> vspyx.Diagnostics.ISO14229_1.Nrc: ...

	def DefaultVetServiceSubfunction(self, service: vspyx.Diagnostics.ISO14229_1.Service, pdu: typing.Any) -> vspyx.Diagnostics.ISO14229_1.Nrc: ...

	def DefaultVetServiceSpecificChecks(self, service: vspyx.Diagnostics.ISO14229_1.Service, pdu: typing.Any) -> vspyx.Diagnostics.ISO14229_1.Nrc: ...

	def DefaultCreateNegativeResponse(self, pdu: typing.Any, nrc: typing.Any) -> vspyx.Core.BytesView: ...

	def DefaultCreateKeepAliveMessage_P2(self, pdu: typing.Any, nrc: typing.Any) -> vspyx.Core.BytesView: ...

class Module(vspyx.Core.Module):
	"""Represents the diagnostics module object
	 
	"""
	"""Module
	"""

