import typing, enum, vspyx

@enum.unique
class TransmissionMode(enum.IntEnum):
	Unknown = 0
	SendAtSlowRate = 1
	SendAtMediumRate = 2
	SendAtFastRate = 3
	StopSending = 4

@enum.unique
class FileTransfer_ModeOfOperation(enum.IntEnum):
	Unknown = 0
	FileAdd = 1
	FileDelete = 2
	FileReplace = 3
	FileRead = 4
	DirRead = 5
	FileResume = 6

@enum.unique
class DTCFormatIdentifier(enum.IntEnum):
	SAE_J2012_DA_00 = 0
	ISO_14229_1 = 1
	SAE_J1939_73 = 2
	ISO_11992_4 = 3
	SAE_J2012_DA_04 = 4

class DtcInfo:
	"""DtcInfo
	"""
	Code: int
	Status: typing.Any
	def assign(self, arg0: vspyx.Diagnostics.ISO14229_Services.DtcInfo) -> vspyx.Diagnostics.ISO14229_Services.DtcInfo: ...

	def __str__(self) -> str: ...

class DTC_ISO_14229_1(vspyx.Diagnostics.ISO14229_Services.DtcInfo):
	"""DTC_ISO_14229_1
	"""
	def __str__(self) -> str: ...

class DTC_ISO_15031_6(vspyx.Diagnostics.ISO14229_Services.DtcInfo):
	"""DTC_ISO_15031_6
	"""
	def __str__(self) -> str: ...

class MessageImpl(vspyx.Diagnostics.ISO14229_1.Message):
	"""MessageImpl
	"""
	AssociatedService: vspyx.Diagnostics.ISO14229_1.Service
	Dissection: vspyx.Dissector.Message
	IsNegativeResponse: bool
	IsPositiveResponseSuppressedSpecified: bool
	PDU: typing.Any
	SID: vspyx.Diagnostics.ISO14229_1.ServiceId
	def ToRaw(self) -> vspyx.Core.BytesView: ...

	def ReadData(self, offset: int, size: int) -> vspyx.Core.BytesView: ...

class TransactionResults:
	"""TransactionResults
	"""
	StartTime: typing.Any
	EndTime: typing.Any
	RequestPDU: typing.Any
	Responses: typing.List[vspyx.Diagnostics.ISO14229_1.Message]
	IsValid: bool
	Duration: typing.Any
	RequestMessageSize: int
	TotalResponseMessagesSize: int

class MessageWithSubfunction(vspyx.Diagnostics.ISO14229_Services.MessageImpl):
	"""MessageWithSubfunction
	"""
	IsPositiveResponseSuppressedSpecified: bool
	Subfunction: int
	def GetSubfunctionCode(self, removeSuppressBit: bool) -> int: ...

class NegativeResponse(vspyx.Diagnostics.ISO14229_Services.MessageImpl):
	"""NegativeResponse
	"""
	FailedSID: vspyx.Diagnostics.ISO14229_1.ServiceId
	IsNegativeResponse: bool
	NRC: vspyx.Diagnostics.ISO14229_1.Nrc

class SessionControlRequest(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""SessionControlRequest
	"""
	SessionType: int

class SessionControlResponse(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""SessionControlResponse
	"""
	P2ServerMax: int
	P2StarServerMax: int
	SessionType: int

@enum.unique
class EcuResetTypes(enum.IntEnum):
	Reserved = 0
	HardReset = 1
	KeyOffOnReset = 2
	SoftReset = 3
	EnableRapidPowerShutDown = 4
	DisableRapidPowerShutDown = 5
	VehicleManufacturerSpecific_LO = 64
	VehicleManufacturerSpecific_HI = 95
	SystemSupplierSpecific_LO = 96
	SystemSupplierSpecific_HI = 126

class EcuResetRequest(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""EcuResetRequest
	"""
	ResetType: vspyx.Diagnostics.ISO14229_Services.EcuResetTypes

class EcuResetResponse(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""EcuResetResponse
	"""
	PowerDownTime: typing.Any
	ResetType: vspyx.Diagnostics.ISO14229_Services.EcuResetTypes

class ClearDtcsRequest(vspyx.Diagnostics.ISO14229_Services.MessageImpl):
	"""ClearDtcsRequest
	"""
	GroupInfo: int
	MemorySelection: typing.Any

class ClearDtcsResponse(vspyx.Diagnostics.ISO14229_Services.MessageImpl):
	"""ClearDtcsResponse
	"""

@enum.unique
class ReadDtcsReportTypes(enum.IntEnum):
	Reserved = 0
	ReportNumberOfDTCByStatusMask = 1
	ReportDTCByStatusMask = 2
	ReportDTCSnapshotIdentification = 3
	ReportDTCSnapshotRecordByDTCNumber = 4
	ReportDTCStoredDataByRecordNumber = 5
	ReportDTCExtDataRecordByDTCNumber = 6
	ReportNumberOfDTCBySeverityMaskRecord = 7
	ReportDTCBySeverityMaskRecord = 8
	ReportSeverityInformationOfDTC = 9
	ReportSupportedDTC = 10
	ReportFirstTestFailedDTC = 11
	ReportFirstConfirmedDTC = 12
	ReportMostRecentTestFailedDTC = 13
	ReportMostRecentConfirmedDTC = 14
	ReportDTCFaultDetectionCounter = 20
	ReportDTCWithPermanentStatus = 21
	ReportDTCExtDataRecordByRecordNumber = 22
	ReportUserDefMemoryDTCByStatusMask = 23
	ReportUserDefMemoryDTCSnapshotRecordByDTCNumber = 24
	ReportUserDefMemoryDTCExtDataRecordByDTCNumber = 25
	ReportDTCExtendedDataRecordIdentification = 26
	ReportWWHOBDDTCByMaskRecord = 66
	ReportWWHOBDDTCWithPermanentStatus = 85
	ReportDTCInformationByDTCReadinessGroupIdentifier = 86

class ReadDtcsRequest(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""ReadDtcsRequest
	"""
	DtcMask: int
	RecordNumber: int
	ReportType: vspyx.Diagnostics.ISO14229_Services.ReadDtcsReportTypes
	SeverityMask: int
	StatusMask: int

class ReadDtcsResponse(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""ReadDtcsResponse
	"""
	ReportType: vspyx.Diagnostics.ISO14229_Services.ReadDtcsReportTypes
	def AddDtcRecord(self, isByDtcNr: bool, dtc: int, status: typing.Any, dataRecordNr: typing.Any, dataRecordIdentifierCount: typing.Any) -> typing.Any: ...

	def AddDtcAndStatus(self, dtc: int, status: typing.Any) -> typing.Any: ...

	def AddDtcSeverityRecord(self, dtc: int, status: int, severity: int, functionalUnit: typing.Any) -> typing.Any: ...

	def AddDtcFaultCountRecord(self, dtc: int, faultCount: int) -> typing.Any: ...

	def AddDataRecordHeader(self, dataRecordNr: int, dataRecordIdentifierCount: typing.Any) -> typing.Any: ...

	def AddDataRecord(self, dataId: typing.Any, data: typing.List[int]) -> typing.Any: ...

	def AddRecord(self, record: typing.List[int]) -> typing.Any: ...

	def GetDtcCountInfo(self) -> vspyx.Diagnostics.ISO14229_Services.ReadDtcsResponse.DtcCountInfo: ...

	def GetDtcStatusInfo(self, format: vspyx.Diagnostics.ISO14229_Services.DTCFormatIdentifier) -> vspyx.Diagnostics.ISO14229_Services.ReadDtcsResponse.DtcStatusInfo: ...

	def GetSnapshotIdentificationInfo(self, format: vspyx.Diagnostics.ISO14229_Services.DTCFormatIdentifier) -> vspyx.Diagnostics.ISO14229_Services.ReadDtcsResponse.DtcSnapshotIdentificationInfo: ...

	def GetDtcSeverityInfo(self, format: vspyx.Diagnostics.ISO14229_Services.DTCFormatIdentifier) -> vspyx.Diagnostics.ISO14229_Services.ReadDtcsResponse.DtcSeverityInfo: ...

	def GetExtOrSnapshotDataInfo(self, format: vspyx.Diagnostics.ISO14229_Services.DTCFormatIdentifier) -> typing.Any: ...

	class DtcCountInfo:
		"""DtcCountInfo
		"""
		StatusAvailabilityMask: int
		FormatIdentifier: vspyx.Diagnostics.ISO14229_Services.DTCFormatIdentifier
		Count: int


	class DtcStatusInfo:
		"""DtcStatusInfo
		"""
		StatusAvailabilityMask: int
		Dtcs: typing.List[vspyx.Diagnostics.ISO14229_Services.DtcInfo]


	class DtcSnapshotIdentificationInfo:
		"""DtcSnapshotIdentificationInfo
		"""
		Records: typing.List[vspyx.Diagnostics.ISO14229_Services.ReadDtcsResponse.DtcSnapshotIdentificationInfo.SnapshotNumberPair]
		def AddRecord(self, dtc: vspyx.Diagnostics.ISO14229_Services.DtcInfo, snapshotNumber: int) -> typing.Any: ...

		class SnapshotNumberPair:
			"""SnapshotNumberPair
			"""
			Dtc: vspyx.Diagnostics.ISO14229_Services.DtcInfo
			SnapshotRecordNumber: int



	class DtcSeverityRecord:
		"""DtcSeverityRecord
		"""
		Severity: int
		FunctionalUnit: int
		Dtc: vspyx.Diagnostics.ISO14229_Services.DtcInfo


	class DtcSeverityInfo:
		"""DtcSeverityInfo
		"""
		StatusAvailabilityMask: int
		Records: typing.List[vspyx.Diagnostics.ISO14229_Services.ReadDtcsResponse.DtcSeverityRecord]
		def AddRecord(self, severity: int, functionalUnit: int, dtc: vspyx.Diagnostics.ISO14229_Services.DtcInfo) -> typing.Any: ...


	class DtcDataInfo:
		"""DtcDataInfo
		"""
		IsSnapshotData: bool
		Dtc: vspyx.Diagnostics.ISO14229_Services.DtcInfo
		CurrentRecordNumber: typing.Any
		CurrentSnapshotIdentifier: typing.Any
		CurrentSnapshotIdentifierCount: typing.Any
		HasData: bool
		HasRecord: bool
		def GetCurrentData(self, dataSize: int) -> typing.Any: ...

		def NextRecord(self) -> bool: ...

		def NextData(self, recordSize: int) -> bool: ...


class ReadDataByIdRequest(vspyx.Diagnostics.ISO14229_Services.MessageImpl):
	"""ReadDataByIdRequest
	"""
	Ids: typing.List[int]

class ReadDataByIdResponse(vspyx.Diagnostics.ISO14229_Services.MessageImpl):
	"""ReadDataByIdResponse
	"""
	DataStart: vspyx.Diagnostics.ISO14229_Services.ReadDataByIdResponse.RecordHandle
	def ReadId(self, handle: vspyx.Diagnostics.ISO14229_Services.ReadDataByIdResponse.RecordHandle) -> int: ...

	def ReadParameterData(self, handle: vspyx.Diagnostics.ISO14229_Services.ReadDataByIdResponse.RecordHandle, size: int) -> vspyx.Core.BytesView: ...

	def WriteId(self, did: int) -> typing.Any: ...

	def WriteData(self, data: typing.List[int]) -> typing.Any: ...

	class RecordHandle:
		"""RecordHandle
		"""
		CurrentOffset: int
		Size: int
		def IsValid(self) -> bool: ...


class ReadOrWriteMemoryByAddressMessage(vspyx.Diagnostics.ISO14229_Services.MessageImpl):
	"""ReadOrWriteMemoryByAddressMessage
	"""
	MemoryAddress: int
	MemoryAddressLength: int
	MemorySize: int
	MemorySizeLength: int

class ReadMemoryByAddressRequest(vspyx.Diagnostics.ISO14229_Services.ReadOrWriteMemoryByAddressMessage):
	"""ReadMemoryByAddressRequest
	"""

class ReadMemoryByAddressResponse(vspyx.Diagnostics.ISO14229_Services.MessageImpl):
	"""ReadMemoryByAddressResponse
	"""
	Data: vspyx.Core.BytesView
	def WriteData(self, data: typing.List[int]) -> typing.Any: ...

class WriteMemoryByAddressRequest(vspyx.Diagnostics.ISO14229_Services.ReadOrWriteMemoryByAddressMessage):
	"""WriteMemoryByAddressRequest
	"""
	Data: vspyx.Core.BytesView
	def WriteData(self, data: typing.List[int]) -> typing.Any: ...

class WriteMemoryByAddressResponse(vspyx.Diagnostics.ISO14229_Services.ReadOrWriteMemoryByAddressMessage):
	"""WriteMemoryByAddressResponse
	"""

class SecurityAccessRequest(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""SecurityAccessRequest
	"""
	IsSeedRequest: bool
	Level: int
	Parameter: vspyx.Core.BytesView
	SecurityAccessType: int

class SecurityAccessResponse(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""SecurityAccessResponse
	"""
	IsSeedRequest: bool
	Level: int
	Parameter: vspyx.Core.BytesView
	SecurityAccessType: int

@enum.unique
class CommControlTypes(enum.IntEnum):
	EnableRxAndTx = 0
	EnableRxAndDisableTx = 1
	DisableRxAndEnableTx = 2
	DisableRxAndTx = 3
	EnableRxAndDisableTxWithEnhancedAddressInformation = 4
	EnableRxAndTxWithEnhancedAddressInformation = 5
	VehicleManufacturerSpecific_LO = 64
	VehicleManufacturerSpecific_HI = 95
	SystemSupplierSpecific_LO = 96
	SystemSupplierSpecific_HI = 126

class CommControlRequest(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""CommControlRequest
	"""
	CommSubnet: int
	CommType: int
	ControlType: vspyx.Diagnostics.ISO14229_Services.CommControlTypes
	NodeId: typing.Any

class CommControlResponse(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""CommControlResponse
	"""
	ControlType: vspyx.Diagnostics.ISO14229_Services.CommControlTypes

@enum.unique
class AuthenticationTask(enum.IntEnum):
	DeAuthenticate = 0
	VerifyCertificateUnidirectional = 1
	VerifyCertificateBidirectional = 2
	ProofOfOwnership = 3
	TransmitCertificate = 4
	RequestChallengeForAuthentication = 5
	VerifyProofOfOwnershipUnidirectional = 6
	VerifyProofOfOwnershipBidirectional = 7
	AuthenticationConfiguration = 8

@enum.unique
class AuthenticationReturnParameter(enum.IntEnum):
	RequestAccepted = 0
	GeneralReject = 1
	AuthConfig_APCE = 2
	AuthConfig_ACRwAsymmetricCrypt = 3
	AuthConfig_ACRwSymmetricCrypt = 4
	DeAuthenticationSuccessful = 16
	CertificateVerified_OwnershipVerificationNecessary = 17
	OwnershipVerified_AuthenticationComplete = 18
	CertificateVerified = 19
	VehicleManufacturerSpecific_LO = 160
	VehicleManufacturerSpecific_HI = 207
	SystemSupplierSpecific_LO = 208
	SystemSupplierSpecific_HI = 254

class AuthenticationRequest(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""AuthenticationRequest
	"""
	AuthenticationTask: vspyx.Diagnostics.ISO14229_Services.AuthenticationTask

	@staticmethod
	def CreateRequest(pdu: typing.Any, message: vspyx.Dissector.Message) -> vspyx.Diagnostics.ISO14229_1.Message: ...

class AuthenticationVerifyCertificateRequest(vspyx.Diagnostics.ISO14229_Services.AuthenticationRequest):
	"""AuthenticationVerifyCertificateRequest
	"""
	CertificateClient: vspyx.Core.BytesView
	ChallengeClient: vspyx.Core.BytesView
	CommunicationConfig: int
	def IsBidirectional(self) -> bool: ...

class AuthenticationProofOfOwnershipRequest(vspyx.Diagnostics.ISO14229_Services.AuthenticationRequest):
	"""AuthenticationProofOfOwnershipRequest
	"""
	EphemeralPublicKeyClient: vspyx.Core.BytesView
	ProofOfOwnershipClient: vspyx.Core.BytesView

class AuthenticationTransmitCertificateRequest(vspyx.Diagnostics.ISO14229_Services.AuthenticationRequest):
	"""AuthenticationTransmitCertificateRequest
	"""
	CertificateData: vspyx.Core.BytesView
	CertificateEvaluationId: int

class AuthenticationRequestChallengeRequest(vspyx.Diagnostics.ISO14229_Services.AuthenticationRequest):
	"""AuthenticationRequestChallengeRequest
	"""
	AlgorithmIndicator: vspyx.Core.BytesView
	CommunicationConfig: int

class AuthenticationVerifyProofOfOwnershipRequest(vspyx.Diagnostics.ISO14229_Services.AuthenticationRequest):
	"""AuthenticationVerifyProofOfOwnershipRequest
	"""
	AdditionalParameter: vspyx.Core.BytesView
	AlgorithmIndicator: vspyx.Core.BytesView
	ChallengeClient: vspyx.Core.BytesView
	ProofOfOwnershipClient: vspyx.Core.BytesView
	def IsBidirectional(self) -> bool: ...

class AuthenticationResponse(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""AuthenticationResponse
	"""
	AuthenticationTask: vspyx.Diagnostics.ISO14229_Services.AuthenticationTask
	ReturnValue: vspyx.Diagnostics.ISO14229_Services.AuthenticationReturnParameter

	@staticmethod
	def CreateResponse(pdu: typing.Any, message: vspyx.Dissector.Message) -> vspyx.Diagnostics.ISO14229_1.Message: ...

class AuthenticationVerifyCertificateResponse(vspyx.Diagnostics.ISO14229_Services.AuthenticationResponse):
	"""AuthenticationVerifyCertificateResponse
	"""
	CertificateServer: vspyx.Core.BytesView
	ChallengeServer: vspyx.Core.BytesView
	EphemeralPublicKeyServer: vspyx.Core.BytesView
	ProofOfOwnershipServer: vspyx.Core.BytesView
	def IsBidirectional(self) -> bool: ...

class AuthenticationProofOfOwnershipResponse(vspyx.Diagnostics.ISO14229_Services.AuthenticationResponse):
	"""AuthenticationProofOfOwnershipResponse
	"""
	SessionKeyInfo: vspyx.Core.BytesView

class AuthenticationRequestChallengeResponse(vspyx.Diagnostics.ISO14229_Services.AuthenticationResponse):
	"""AuthenticationRequestChallengeResponse
	"""
	AlgorithmIndicator: vspyx.Core.BytesView
	ChallengeServer: vspyx.Core.BytesView
	NeededAdditionalParameter: vspyx.Core.BytesView

class AuthenticationVerifyProofOfOwnershipResponse(vspyx.Diagnostics.ISO14229_Services.AuthenticationResponse):
	"""AuthenticationVerifyProofOfOwnershipResponse
	"""
	AlgorithmIndicator: vspyx.Core.BytesView
	ProofOfOwnershipServer: vspyx.Core.BytesView
	SessionKeyInfo: vspyx.Core.BytesView
	def IsBidirectional(self) -> bool: ...

class ReadDataByPeriodicIdRequest(vspyx.Diagnostics.ISO14229_Services.MessageImpl):
	"""ReadDataByPeriodicIdRequest
	"""
	Ids: vspyx.Core.BytesView
	TransmissionMode: vspyx.Diagnostics.ISO14229_Services.TransmissionMode

class ReadDataByPeriodicIdResponse(vspyx.Diagnostics.ISO14229_Services.MessageImpl):
	"""ReadDataByPeriodicIdResponse
	"""

class WriteDataByIdRequest(vspyx.Diagnostics.ISO14229_Services.MessageImpl):
	"""WriteDataByIdRequest
	"""
	DataId: int
	Parameter: vspyx.Core.BytesView

class WriteDataByIdResponse(vspyx.Diagnostics.ISO14229_Services.MessageImpl):
	"""WriteDataByIdResponse
	"""
	DataId: int

@enum.unique
class IoControlTypes(enum.IntEnum):
	ReturnControlToECU = 0
	ResetToDefault = 1
	FreezeCurrentState = 2
	ShortTermAdjustment = 3

class IoControlByIdRequest(vspyx.Diagnostics.ISO14229_Services.MessageImpl):
	"""IoControlByIdRequest
	"""
	ControlType: vspyx.Diagnostics.ISO14229_Services.IoControlTypes
	DataId: int
	Parameter: vspyx.Core.BytesView

class IoControlByIdResponse(vspyx.Diagnostics.ISO14229_Services.MessageImpl):
	"""IoControlByIdResponse
	"""
	DataId: int
	Parameter: vspyx.Core.BytesView
	Status: int

@enum.unique
class RoutineControlTypes(enum.IntEnum):
	Reserved = 0
	StartRoutine = 1
	StopRoutine = 2
	RequestRoutineResults = 3

class RoutineControlRequest(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""RoutineControlRequest
	"""
	ControlType: vspyx.Diagnostics.ISO14229_Services.RoutineControlTypes
	OptionData: vspyx.Core.BytesView
	RoutineId: int

class RoutineControlResponse(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""RoutineControlResponse
	"""
	ControlType: vspyx.Diagnostics.ISO14229_Services.RoutineControlTypes
	RoutineId: int
	StatusData: vspyx.Core.BytesView

class RequestDownloadRequest(vspyx.Diagnostics.ISO14229_Services.MessageImpl):
	"""RequestDownloadRequest
	"""
	CompressionMethod: int
	EncryptionMethod: int
	MemoryAddress: int
	MemoryAddressLength: int
	MemorySize: int
	MemorySizeLength: int

class RequestDownloadResponse(vspyx.Diagnostics.ISO14229_Services.MessageImpl):
	"""RequestDownloadResponse
	"""
	LengthFormat: int
	MaxBlockLength: int

class RequestUploadRequest(vspyx.Diagnostics.ISO14229_Services.MessageImpl):
	"""RequestUploadRequest
	"""
	CompressionMethod: int
	EncryptionMethod: int
	MemoryAddress: int
	MemoryAddressLength: int
	MemorySize: int
	MemorySizeLength: int

class RequestUploadResponse(vspyx.Diagnostics.ISO14229_Services.MessageImpl):
	"""RequestUploadResponse
	"""
	LengthFormat: int
	MaxBlockLength: int

class TransferDataRequest(vspyx.Diagnostics.ISO14229_Services.MessageImpl):
	"""TransferDataRequest
	"""
	BlockSequenceCounter: int
	Data: vspyx.Core.BytesView

class TransferDataResponse(vspyx.Diagnostics.ISO14229_Services.MessageImpl):
	"""TransferDataResponse
	"""
	BlockSequenceCounter: int
	Data: vspyx.Core.BytesView

class RequestTransferExitRequest(vspyx.Diagnostics.ISO14229_Services.MessageImpl):
	"""RequestTransferExitRequest
	"""
	Parameter: vspyx.Core.BytesView

class RequestTransferExitResponse(vspyx.Diagnostics.ISO14229_Services.MessageImpl):
	"""RequestTransferExitResponse
	"""
	Parameter: vspyx.Core.BytesView

class RequestFileTransferRequest(vspyx.Diagnostics.ISO14229_Services.MessageImpl):
	"""RequestFileTransferRequest
	"""
	CompressionMethod: int
	EncryptionMethod: int
	FilePathAndName: vspyx.Core.BytesView
	FileSizeCompressed: int
	FileSizeUnCompressed: int
	ModeOfOperation: vspyx.Diagnostics.ISO14229_Services.FileTransfer_ModeOfOperation

class RequestFileTransferResponse(vspyx.Diagnostics.ISO14229_Services.MessageImpl):
	"""RequestFileTransferResponse
	"""
	CompressionMethod: int
	EncryptionMethod: int
	FileSizeCompressed: int
	FileSizeUnCompressed: int
	MaxBlockLength: int
	ModeOfOperation: vspyx.Diagnostics.ISO14229_Services.FileTransfer_ModeOfOperation

class TesterPresentRequest(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""TesterPresentRequest
	"""

class TesterPresentResponse(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""TesterPresentResponse
	"""

@enum.unique
class ControlDtcSettingTypes(enum.IntEnum):
	Reserved = 0
	On = 1
	Off = 2
	VehicleManufacturerSpecific_LO = 64
	VehicleManufacturerSpecific_HI = 95
	SystemSupplierSpecific_LO = 96
	SystemSupplierSpecific_HI = 126

class ControlDtcSettingRequest(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""ControlDtcSettingRequest
	"""
	DtcsSettingType: vspyx.Diagnostics.ISO14229_Services.ControlDtcSettingTypes
	Parameter: vspyx.Core.BytesView

class ControlDtcSettingResponse(vspyx.Diagnostics.ISO14229_Services.MessageWithSubfunction):
	"""ControlDtcSettingResponse
	"""
	DtcsSettingType: vspyx.Diagnostics.ISO14229_Services.ControlDtcSettingTypes

class ServiceConfig:
	"""ServiceConfig
	"""

	@typing.overload
	def AddService(self, sid: int, name: str, supportedSessions: typing.List[int], p4ServerMax: typing.Any) -> vspyx.Diagnostics.ISO14229_1.Service: ...


	@typing.overload
	def AddService(self, sid: int, name: str, supportedSessions: typing.List[int], p4ServerMax: typing.Any, supportedSubfunctions: typing.Any) -> vspyx.Diagnostics.ISO14229_1.Service: ...


	@typing.overload
	def AddService(self, sid: int, name: str, supportedSessions: typing.List[int], p4ServerMax: typing.Any, supportedSubfunctions: typing.Any, securityMask: typing.Any) -> vspyx.Diagnostics.ISO14229_1.Service: ...


	@typing.overload
	def ConfigureService(self, name: str, supportedSessions: typing.List[int], p4ServerMax: typing.Any) -> vspyx.Diagnostics.ISO14229_1.Service: ...


	@typing.overload
	def ConfigureService(self, name: str, supportedSessions: typing.List[int], p4ServerMax: typing.Any, supportedSubfunctions: typing.Any) -> vspyx.Diagnostics.ISO14229_1.Service: ...


	@typing.overload
	def ConfigureService(self, name: str, supportedSessions: typing.List[int], p4ServerMax: typing.Any, supportedSubfunctions: typing.Any, securityMask: typing.Any) -> vspyx.Diagnostics.ISO14229_1.Service: ...

	def GetService(self, sid: typing.Any, name: typing.Any) -> vspyx.Diagnostics.ISO14229_1.Service: ...

	def ResolveDecoder(self, sid: vspyx.Diagnostics.ISO14229_1.ServiceId, pdu: typing.Any, message: vspyx.Dissector.Message) -> vspyx.Diagnostics.ISO14229_1.Message: ...

