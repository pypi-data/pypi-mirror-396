import typing, enum, vspyx

class Module(vspyx.Core.Module):
	"""Module
	"""
	TAtype_Functional: int
	TAtype_Physical: int
	def SecurityLibraryGetKey(self, libraryUnlockKey: str, seed: vspyx.Core.BytesView, fixedBytes: vspyx.Core.BytesView, algorithmType: int) -> typing.List[int]: ...

	def SetSecurityLibraryExternalPath(self, path: str) -> typing.Any: ...

	def NewCtphAdapterAttachAndAddToRuntime(self, app: vspyx.Core.Application, id: str, sched: vspyx.Runtime.Scheduler, appId: int, channel: vspyx.Communication.CANChannel) -> vspyx.Communication.ISOStandardizedServicePrimitiveInterface: ...

	def CtphAdapterRegisterCANID(self, ctphAdapter: vspyx.Communication.ISOStandardizedServicePrimitiveInterface, id: int) -> typing.Any: ...

	def LoadVBF(self, path: str, verifyChecksums: bool) -> vspyx.Core.ScheduledTask_bd3c109fb4: ...

class OVTPTransportLayer(vspyx.Communication.ISOStandardizedServicePrimitiveInterface, vspyx.Runtime.Component):
	"""OVTPTransportLayer
	"""
	@enum.unique
	class OVTPApplication(enum.IntEnum):
		PARSED = 10
		PARSED_PUSH = 11
		OTA = 9

	@enum.unique
	class NetworkAddressType(enum.IntEnum):
		Physical = 1
		Functional = 2

	def SetTx_STmin(self, N_SA: int, N_TA: int, N_TAtype: vspyx.Ford.OVTPTransportLayer.NetworkAddressType, app: vspyx.Ford.OVTPTransportLayer.OVTPApplication, Tx_STmin: int) -> typing.Any: ...

class OVTPClientPresentationLayer(vspyx.Runtime.Component):
	"""OVTPClientPresentationLayer
	"""
	ClientAddress: int
	FunctionalAddress: int
	OVTPApplication: vspyx.Ford.OVTPTransportLayer.OVTPApplication
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	ServerAddress: int

	@staticmethod
	@typing.overload
	def New() -> vspyx.Ford.OVTPClientPresentationLayer: ...

	def Attach(self, session: vspyx.Ford.OVTPTransportLayer) -> typing.Any: ...

	def Detach(self) -> typing.Any: ...

	def OpenSession(self, persistent: bool, sessionTimeout: typing.Any, Tx_STmin: typing.Any) -> int: ...

	def CloseSession(self) -> typing.Any: ...


	@typing.overload
	def PhysicalRequest(self, P_Data: vspyx.Core.BytesView) -> typing.Any: ...


	@typing.overload
	def PhysicalRequest(self, P_Data: vspyx.Core.BytesView, includeSSNInHeader: bool) -> typing.Any: ...


	@typing.overload
	def PhysicalRequest(self, P_Data: vspyx.Core.BytesView, includeSSNInHeader: bool, positiveResponseSuppressed: bool) -> typing.Any: ...


	@typing.overload
	def FunctionalRequest(self, P_Data: vspyx.Core.BytesView) -> typing.List[typing.Any]: ...


	@typing.overload
	def FunctionalRequest(self, P_Data: vspyx.Core.BytesView, includeSSNInHeader: bool) -> typing.List[typing.Any]: ...


	@typing.overload
	def FunctionalRequest(self, P_Data: vspyx.Core.BytesView, includeSSNInHeader: bool, positiveResponseSuppressed: bool) -> typing.List[typing.Any]: ...


	@staticmethod
	@typing.overload
	def New(config: typing.Any) -> vspyx.Ford.OVTPClientPresentationLayer: ...

	def CloneConfiguration(self) -> typing.Any: ...

	def CloneState(self) -> typing.Any: ...

	def UpdateState(self, state: typing.Any) -> typing.Any: ...

class OVTPoCAN(vspyx.Ford.OVTPTransportLayer):
	"""OVTPoCAN
	"""

	@staticmethod
	def New(passive: bool) -> vspyx.Ford.OVTPoCAN: ...

	def Attach(self, L_Data: vspyx.Communication.ISO11898.ISO11898_1Interface) -> typing.Any: ...

	def Detach(self) -> typing.Any: ...


	@typing.overload
	def AddRxAddress(self, N_SA: int, N_TA: int, N_TAtype: vspyx.Ford.OVTPTransportLayer.NetworkAddressType, app: vspyx.Ford.OVTPTransportLayer.OVTPApplication) -> typing.Any: ...


	@typing.overload
	def AddRxAddress(self, N_SA: int, N_TA: int, N_TAtype: vspyx.Ford.OVTPTransportLayer.NetworkAddressType, app: vspyx.Ford.OVTPTransportLayer.OVTPApplication, priority: int) -> typing.Any: ...


	@typing.overload
	def AddTxAddress(self, N_SA: int, N_TA: int, N_TAtype: vspyx.Ford.OVTPTransportLayer.NetworkAddressType, app: vspyx.Ford.OVTPTransportLayer.OVTPApplication) -> typing.Any: ...


	@typing.overload
	def AddTxAddress(self, N_SA: int, N_TA: int, N_TAtype: vspyx.Ford.OVTPTransportLayer.NetworkAddressType, app: vspyx.Ford.OVTPTransportLayer.OVTPApplication, priority: int) -> typing.Any: ...


	@staticmethod
	def MakeCANID(priority: int, app: vspyx.Ford.OVTPTransportLayer.OVTPApplication, ta: int, sa: int) -> int: ...

class OVTPoIP(vspyx.Ford.OVTPTransportLayer):
	"""OVTPoIP
	"""
	@enum.unique
	class Result(enum.IntEnum):
		N_OK = 0
		N_NO_TX_IN_PASSIVE_MODE = 1
		N_UNKNOWN_ADDRESS = 2
		N_NO_CLIENT_FOR_SERVER_ADDRESS = 3
		N_FAILED_CONNECTION = 4
		N_CONNECTION_CLOSED = 5

	ConnectTimeout: typing.Any
	OVTPPort: int

	@staticmethod
	def New(passive: bool) -> vspyx.Ford.OVTPoIP: ...


	@typing.overload
	def Attach(self, L_Data: vspyx.Communication.EthernetChannel) -> typing.Any: ...


	@typing.overload
	def Attach(self, network: vspyx.TCPIP.Network) -> typing.Any: ...

	def Detach(self) -> typing.Any: ...

	def AddServerAddress(self, N_SA: int, N_TA: int, N_TAtype: vspyx.Ford.OVTPTransportLayer.NetworkAddressType, app: vspyx.Ford.OVTPTransportLayer.OVTPApplication, ip: str) -> typing.Any: ...

	def AddClientAddress(self, N_SA: int, N_TA: int, N_TAtype: vspyx.Ford.OVTPTransportLayer.NetworkAddressType, app: vspyx.Ford.OVTPTransportLayer.OVTPApplication, ip: str) -> typing.Any: ...


	@staticmethod
	def MakeAUTOSARPDUID(app: vspyx.Ford.OVTPTransportLayer.OVTPApplication, ta: int, sa: int) -> int: ...

class SWDL(vspyx.Runtime.Component):
	"""SWDL
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Ford.SWDL: ...

	def CloneConfiguration(self) -> typing.Any: ...

	def CloneState(self) -> typing.Any: ...

	def UpdateState(self, state: typing.Any) -> typing.Any: ...

class VBFBlock:
	"""VBFBlock
	"""
	StartAddress: int
	Checksum: int
	Data: vspyx.Core.BytesView

class VBF(vspyx.Core.Object):
	"""VBF
	"""
	@enum.unique
	class SwPartTypes(enum.IntEnum):
		CARCFG = 0
		CUSTOM = 1
		DATA = 2
		EXE = 3
		GBL = 4
		SBL = 5
		SIGCFG = 6
		TEST = 7

	@enum.unique
	class FrameFormats(enum.IntEnum):
		CAN_STANDARD = 0
		CAN_EXTENDED = 1

	Blocks: typing.List[vspyx.Ford.VBFBlock]
	Call: typing.Any
	DataFormatIdentifier: int
	Description: typing.List[str]
	ECUAddress: typing.List[int]
	Erase: typing.List[typing.Any]
	FileChecksum: int
	FrameFormat: vspyx.Ford.VBF.FrameFormats
	Omit: typing.List[typing.Any]
	PublicKeyHash: typing.List[int]
	SwPartNumber: typing.List[str]
	SwPartType: vspyx.Ford.VBF.SwPartTypes
	SwSignature: typing.List[typing.List[int]]
	VerificationStructureAddress: typing.List[int]

