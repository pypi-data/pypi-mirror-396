import typing, enum, vspyx
from . import EthernetFrameBuilder, ScriptStatus, VSA

@enum.unique
class CANControllerState(enum.IntEnum):
	ErrorActive = 0
	ErrorPassive = 1
	BusOff = 2

@enum.unique
class FlexRayStrobePoint(enum.IntEnum):
	SPP5 = 0
	SPP4 = 1
	SPP6 = 2

class NetworkEvent(vspyx.Core.Object):
	"""Represents an event that a controller would observe/create regarding a network.
	 
	 It is the basis for Frame, ACK, NAK, Error State Change, Link State Change, etc.
	"""
	"""NetworkEvent
	"""
	CountsAsTraffic: bool
	"""Whether or not this NetworkEvent counts as "traffic" for the purposes of
	 statistics reporting, i.e. for the Channel's "total traffic" counter.
		 
	"""

	Network: vspyx.Frames.NetworkIdentifier
	Source: vspyx.Frames.SourceIdentifier
	Timestamp: vspyx.Runtime.Timestamp
	def Clone(self) -> vspyx.Frames.NetworkEvent: ...

	def GetProcessingFlags(self) -> vspyx.Runtime.ProcessingFlags: ...


	@typing.overload
	def SetProcessingFlags(self, set: vspyx.Runtime.ProcessingFlags) -> vspyx.Runtime.ProcessingFlags: ...


	@typing.overload
	def SetProcessingFlags(self, set: vspyx.Runtime.ProcessingFlags, clear: vspyx.Runtime.ProcessingFlags) -> vspyx.Runtime.ProcessingFlags: ...

class Frame(vspyx.Frames.NetworkEvent):
	"""Represents the basis of a physical communication frame
	"""
	"""Frame
	"""
	Arbitrary: int
	CountsAsTraffic: bool
	Data: vspyx.Core.BytesView
	Type: vspyx.Frames.FrameType

class Confirmation(vspyx.Frames.NetworkEvent):
	"""Represents the completion of a pending Frame forward/transmit
	"""
	"""Confirmation
	"""
	CountsAsTraffic: bool
	Frame: vspyx.Frames.Frame
	IsError: bool
	Network: vspyx.Frames.NetworkIdentifier
	Source: vspyx.Frames.SourceIdentifier

class Driver(vspyx.Core.Object):
	"""Represents the functional basis for a communication driver interface
	 
	"""
	"""Driver
	"""
	@enum.unique
	class IngressResult(enum.IntEnum):
		Nop = 0
		Requested = 1
		Successful = 2
		Failed = 3

	BaudRate: int
	Identifier: vspyx.Frames.DriverIdentifier
	OnEvent: vspyx.Core.Callback_316d8f46e9
	"""Called when the driver reports an occurrence of a Network Event.
	 
	 This could be a Frames::Frame or any other event that the Driver can detect.
		 
	"""

	def SubmitEvent(self, event: vspyx.Frames.NetworkEvent) -> vspyx.Frames.Driver.IngressResult:
		"""Submit an event to the driver.

		For instance, the event may be a Frame, in which case we expect the Driver
		to Transmit the Frame.

		"""
		pass


class CANFrame(vspyx.Frames.Frame):
	"""Represents a CAN communication frame
	"""
	"""CANFrame
	"""
	ArbID: int
	BaudrateSwitch: bool
	DLC: int
	IsCANFD: bool
	IsExtended: bool
	IsRemote: bool

class CANDriver(vspyx.Frames.Driver):
	"""Represents CAN driver function
	 
	"""
	"""CANDriver
	"""
	@enum.unique
	class TxStatus(enum.IntEnum):
		Transmitted = 0
		Aborted = 1
		ArbitrationLost = 2

	FDBaudRate: typing.Any

class EthernetDriver(vspyx.Frames.Driver):
	"""Rerepsents an Ethernet device driver
	 
	"""
	"""EthernetDriver
	"""
	@enum.unique
	class TxStatus(enum.IntEnum):
		Transmitted = 0
		Dropped = 1

class CANErrorCountsEvent(vspyx.Frames.NetworkEvent):
	"""Represents an event emitted onto the channel by a CAN Controller
	 when its error counts change. It does not represent an event that
	 would occur on a physical CAN bus, but is propagated for display
	 reasons.
	 
	"""
	"""CANErrorCountsEvent
	"""
	BusOff: bool
	ControllerState: vspyx.Frames.CANControllerState
	"""The error state of the CAN controller
		 
	"""

	CountsAsTraffic: bool
	ErrorWarning: bool
	"""Some CAN controllers have an "error warning"
	 threshold when either counter goes above 95.
	 
	 Since it is not a standardized error state,
	 it is not reported as the controller state,
	 but the value can be read here.
		 
	"""

	ReceiveErrorCount: int
	TransmitErrorCount: int

	@staticmethod
	def New(timestamp: vspyx.Runtime.Timestamp, source: vspyx.Frames.SourceIdentifier, network: vspyx.Frames.NetworkIdentifier, tec: int, rec: int, busOff: bool) -> vspyx.Frames.CANErrorCountsEvent: ...

@enum.unique
class FlexRaySymbol(enum.IntEnum):
	NONE = 0
	Unknown = 1
	Wakeup = 2
	CAS = 3

@enum.unique
class FlexRayCRCStatus(enum.IntEnum):
	OK = 0
	Error = 1
	NoCRC = 2

@enum.unique
class FlexRayChannel(enum.IntEnum):
	A = 0
	B = 1
	AB = 2

class FlexRayFrame(vspyx.Frames.Frame):
	"""Represents a Flexray frame
	 
	"""
	"""FlexRayFrame
	"""
	CRCStatus: vspyx.Frames.FlexRayCRCStatus
	Channel: vspyx.Frames.FlexRayChannel
	Cycle: int
	FrameCRC: int
	FrameLen: float
	HeaderCRC: int
	HeaderCRCStatus: vspyx.Frames.FlexRayCRCStatus
	IsDynamicFrame: bool
	IsNullFrame: bool
	IsStartupFrame: bool
	IsSyncFrame: bool
	PayloadPreamble: bool
	ReservedBit: bool
	SlotID: int
	Symbol: vspyx.Frames.FlexRaySymbol
	TSSLen: float

class FlexRayTransmitBufferUpdate(vspyx.Frames.NetworkEvent):
	"""Transmitted onto a FlexRayChannel when a Controller
	 updates its transmit buffer.
	 
	 This way, any physical FrameSources can update their
	 internal transmit buffers as necessary to create this
	 traffic on the physical bus when the time comes.
	 
	"""
	"""FlexRayTransmitBufferUpdate
	"""
	@enum.unique
	class Mode(enum.IntEnum):
		OneShot = 0
		Continuous = 1
		FIFO = 2
		Clear = 3

	BaseCycle: int
	Channel: vspyx.Frames.FlexRayChannel
	CountsAsTraffic: bool
	CycleRepetition: int
	Data: vspyx.Core.BytesView
	IsDynamic: bool
	IsKeySlot: bool
	IsNetworkManagementFrame: bool
	IsStartup: bool
	IsSync: bool
	SlotID: int

	@staticmethod
	@typing.overload
	def New(data: vspyx.Core.BytesView, timestamp: vspyx.Runtime.Timestamp, source: vspyx.Frames.SourceIdentifier, network: vspyx.Frames.NetworkIdentifier, baseCycle: int, cycleRepetition: int, mode: vspyx.Frames.FlexRayTransmitBufferUpdate.Mode, channel: vspyx.Frames.FlexRayChannel, slotId: int) -> vspyx.Frames.FlexRayTransmitBufferUpdate: ...


	@staticmethod
	@typing.overload
	def New(data: vspyx.Core.BytesView, timestamp: vspyx.Runtime.Timestamp, source: vspyx.Frames.SourceIdentifier, network: vspyx.Frames.NetworkIdentifier, baseCycle: int, cycleRepetition: int, mode: vspyx.Frames.FlexRayTransmitBufferUpdate.Mode, channel: vspyx.Frames.FlexRayChannel, slotId: int, dynamic: bool) -> vspyx.Frames.FlexRayTransmitBufferUpdate: ...


	@staticmethod
	@typing.overload
	def New(data: vspyx.Core.BytesView, timestamp: vspyx.Runtime.Timestamp, source: vspyx.Frames.SourceIdentifier, network: vspyx.Frames.NetworkIdentifier, baseCycle: int, cycleRepetition: int, mode: vspyx.Frames.FlexRayTransmitBufferUpdate.Mode, channel: vspyx.Frames.FlexRayChannel, slotId: int, dynamic: bool, networkManagement: bool) -> vspyx.Frames.FlexRayTransmitBufferUpdate: ...


	@staticmethod
	@typing.overload
	def New(data: vspyx.Core.BytesView, timestamp: vspyx.Runtime.Timestamp, source: vspyx.Frames.SourceIdentifier, network: vspyx.Frames.NetworkIdentifier, baseCycle: int, cycleRepetition: int, mode: vspyx.Frames.FlexRayTransmitBufferUpdate.Mode, channel: vspyx.Frames.FlexRayChannel, slotId: int, dynamic: bool, networkManagement: bool, keySlot: bool) -> vspyx.Frames.FlexRayTransmitBufferUpdate: ...


	@staticmethod
	@typing.overload
	def New(data: vspyx.Core.BytesView, timestamp: vspyx.Runtime.Timestamp, source: vspyx.Frames.SourceIdentifier, network: vspyx.Frames.NetworkIdentifier, baseCycle: int, cycleRepetition: int, mode: vspyx.Frames.FlexRayTransmitBufferUpdate.Mode, channel: vspyx.Frames.FlexRayChannel, slotId: int, dynamic: bool, networkManagement: bool, keySlot: bool, sync: bool) -> vspyx.Frames.FlexRayTransmitBufferUpdate: ...


	@staticmethod
	@typing.overload
	def New(data: vspyx.Core.BytesView, timestamp: vspyx.Runtime.Timestamp, source: vspyx.Frames.SourceIdentifier, network: vspyx.Frames.NetworkIdentifier, baseCycle: int, cycleRepetition: int, mode: vspyx.Frames.FlexRayTransmitBufferUpdate.Mode, channel: vspyx.Frames.FlexRayChannel, slotId: int, dynamic: bool, networkManagement: bool, keySlot: bool, sync: bool, startup: bool) -> vspyx.Frames.FlexRayTransmitBufferUpdate: ...

	def GetMode(self) -> vspyx.Frames.FlexRayTransmitBufferUpdate.Mode: ...

	def Matches(self, other: vspyx.Frames.FlexRayTransmitBufferUpdate) -> bool:
		"""Returns true if the given FlexRayTransmitBufferUpdate would use the
		same message buffer as the current FlexRayTransmitBufferUpdate would.

		"""
		pass


class LiveDataMessage:
	"""LiveDataMessage
	"""
	CommandMessage: vspyx.icsneo.LiveDataCommandMessage
	Handle: int

class Source(vspyx.Runtime.Component):
	"""Represents the basis of a message frame data source
	"""
	"""Source
	"""
	@enum.unique
	class State(enum.IntEnum):
		Uninitialized = 0
		NotReady = 1
		Ready = 2
		Opening = 3
		Open = 4
		Online = 5
		Closing = 6
		Disconnected = 7

	@enum.unique
	class RootDirectoryEntryFlags(enum.IntEnum):
		UploadPriority = 0
		CellularEnabled = 1
		WiFiEnabled = 2
		Uploaded = 3

	AvailableDrivers: typing.List[vspyx.Frames.Driver]
	Description: str
	DisplayName: str
	Filesystem: vspyx.IO.Filesystem
	Identifier: vspyx.Frames.SourceIdentifier
	OnCaptureFinished: vspyx.Core.Callback_932b18a011
	OnCoreMiniCreateTimeChanged: vspyx.Core.Callback_40fa3759e0
	OnCoreMiniHeaderSizeChanged: vspyx.Core.Callback_40fa3759e0
	OnCoreMiniRunningChanged: vspyx.Core.Callback_40fa3759e0
	OnCoreMiniVersionChanged: vspyx.Core.Callback_40fa3759e0
	OnCurrentSectorChanged: vspyx.Core.Callback_40fa3759e0
	OnDiagnosticErrorCodeChanged: vspyx.Core.Callback_40fa3759e0
	OnDiagnosticErrorCodeCountChanged: vspyx.Core.Callback_40fa3759e0
	OnEncryptionModeChanged: vspyx.Core.Callback_40fa3759e0
	OnFileChecksumChanged: vspyx.Core.Callback_40fa3759e0
	OnLastSectorChanged: vspyx.Core.Callback_40fa3759e0
	OnLogDataMessageReceived: vspyx.Core.Callback_6ee07abf48
	OnLoggingChanged: vspyx.Core.Callback_40fa3759e0
	OnMaxCoreMiniSizeChanged: vspyx.Core.Callback_40fa3759e0
	OnMaxSectorChanged: vspyx.Core.Callback_40fa3759e0
	OnMinSectorChanged: vspyx.Core.Callback_40fa3759e0
	OnNetworkEvent: vspyx.Core.Callback_316d8f46e9
	OnReadBinSizeChanged: vspyx.Core.Callback_40fa3759e0
	OnRemainingSectorsChanged: vspyx.Core.Callback_40fa3759e0
	OnSectorOverflowChanged: vspyx.Core.Callback_40fa3759e0
	OnSleepRequested: vspyx.Core.Callback_a2f38cfeb7
	OnVINAvailable: vspyx.Core.Callback_634bd5c449
	ScriptStatus: typing.Any
	SleepRequested: typing.Any
	SourceState: vspyx.Frames.Source.State
	SourceStream: vspyx.IO.SeekableInputOutputStream
	TypeString: str
	UniqueIdentifierString: str
	VIN: typing.Any

	@staticmethod
	def StateString(state: vspyx.Frames.Source.State) -> int: ...

	def Open(self) -> vspyx.Core.Task_a3295bec43: ...

	def Start(self) -> vspyx.Core.Task_a3295bec43: ...

	def Stop(self) -> vspyx.Core.Task_a3295bec43: ...

	def Close(self) -> vspyx.Core.Task_a3295bec43: ...

	def SubscribeLiveData(self, subscription: vspyx.Frames.LiveDataMessage) -> bool: ...

	def UnsubscribeLiveData(self, subscription: vspyx.Frames.LiveDataMessage) -> bool: ...

	def GetOnLiveDataReceived(self, subscription: vspyx.Frames.LiveDataMessage) -> vspyx.Core.Callback_d36abe9a65: ...

	def IsVINEnabled(self) -> typing.Any: ...


	@typing.overload
	def AllowSleep(self) -> typing.Any: ...


	@typing.overload
	def AllowSleep(self, remoteWakeup: bool) -> typing.Any: ...

	def SetRootDirectoryEntryFlag(self, flag: vspyx.Frames.Source.RootDirectoryEntryFlags, value: int, entryPosition: int) -> typing.Any: ...

	def LoadScript(self, arg0: vspyx.Core.BytesView, clearScriptFirst: bool, logProgress: bool) -> typing.Any: ...

	def LoadReadBin(self, arg0: vspyx.Core.BytesView, readBinStartLocation: int, logProgress: bool) -> typing.Any: ...

	def StartScript(self) -> typing.Any: ...

	def StopScript(self) -> typing.Any: ...

	def ClearScript(self) -> typing.Any: ...

	def CloneState(self) -> typing.Any: ...

	def UpdateState(self, state: typing.Any) -> typing.Any: ...

	class WiVIUpload:
		"""WiVIUpload
		"""
		cellular: bool
		wifi: bool
		isPrePost: bool
		isPreTime: bool
		preTriggerSize: int
		priority: int
		captureIndex: int
		startSector: int
		endSector: int


class FrameType(vspyx.Core.Object):
	"""Represents message frame type identification info
	 
	"""
	"""FrameType
	"""
	@enum.unique
	class Enum(enum.IntFlag):
		CAN = 2
		LIN = 3
		FlexRay = 4
		MOST = 5
		Ethernet = 6
		ISO9141 = 9
		I2C = 10
		A2B = 11
		SPI = 12
		MDIO = 13
		Unknown = 65535


	@staticmethod
	def TypeToString(e: vspyx.Frames.FrameType.Enum) -> int: ...

	def __eq__(self, compare: vspyx.Frames.FrameType.Enum) -> bool: ...

	def assign(self, e: vspyx.Frames.FrameType.Enum) -> vspyx.Frames.FrameType: ...

	def GetEnum(self) -> vspyx.Frames.FrameType.Enum: ...

	def __str__(self) -> str: ...

class Buffer(vspyx.Core.ResolverObject):
	"""Represents the functional basis of a transaction buffer consisting of zero or more frames
	 
	"""
	"""Buffer
	"""
	Duration: typing.Any
	FileName: str
	Identifer: vspyx.Frames.SourceIdentifier
	NumberOfFrames: int
	TypeString: str
	def __getitem__(self, index: int) -> vspyx.Frames.NetworkEvent: ...

	def IsPrepared(self) -> bool: ...

	def Prepare(self, task: vspyx.Core.TaskInterface) -> typing.Any: ...

class Predicate:
	"""Represents a predicate handler used in comparison of message frame objects of various types
	 
	"""
	"""Predicate
	"""
	Function: vspyx.Core.Function_9f3a3da547

class BufferOpener(vspyx.Core.ResolverObject):
	"""Represents the function of reading recorded message frame buffer data
	 
	"""
	"""BufferOpener
	"""
	TypeString: str
	def CanOpen(self, path: str) -> bool: ...

	def Open(self, path: str) -> vspyx.Core.Task_0f35f34819: ...

class BufferSource(vspyx.Frames.Source):
	"""Represents the functional basis of time-varied frame buffer data hosting
	 
	"""
	"""BufferSource
	"""
	Buffer: vspyx.Frames.Buffer
	BufferEndEvent: vspyx.Core.Event
	Loop: bool
	LoopCount: int
	OnLooped: vspyx.Core.Callback_634bd5c449
	Paused: bool
	Position: float
	TimeMultiplier: float
	TimeSkipDetectionThreshold: typing.Any
	"""Get/set the current threshold of elapsed time that indicates
	 we were frozen (in a suspended VM, say).
	 
	 If we detect we were frozen, we will skip the time in the
	 buffer rather than attempting to catch up to where we
	 would have been if all that time had elapsed.
	 
	 This prevents us from entering a death spiral of processing
	 in these cases.
	 
	 The default threshold is one second, and it will not trigger
	 if the Scheduler is in non-realtime mode.
	 
	 This API is not guaranteed and should not be relied on long
	 term, but it is provided in case the threshold is causing
	 problems and a quick workaround is needed.
		 
	"""

	UseSimulationTime: bool
	"""Used to select whether the timestamps of the buffer
	 should be synchronized with the beginning of the
	 simulation (true) or the beginning of the buffer
	 (false).
	 
	 This defaults to true when running realtime for
	 correct synchronization with real hardware, and
	 false when running non-realtime for accurate timestamps
	 while processing.
	 
	 Note that even when false, the buffer source creates
	 timestamps after the final frame for buffer looping.
	 
	 The value is latched during ComponentStart, so if
	 the value is changed while running it will take effect
	 the next time the source is started.
		 
	"""

	def MakeSchedulerTicker(self) -> vspyx.Runtime.SchedulerTicker: ...

	def SetProcessingFlags(self, flags: vspyx.Runtime.ProcessingFlags) -> typing.Any: ...

class CANConfirmation(vspyx.Frames.Confirmation):
	"""Represents the completion of a pending CANFrame forward/transmit
	"""
	"""CANConfirmation
	"""
	CANFrame: vspyx.Frames.CANFrame
	Status: vspyx.Frames.CANDriver.TxStatus

	@staticmethod
	def New(frame: vspyx.Frames.CANFrame, status: vspyx.Frames.CANDriver.TxStatus) -> vspyx.Frames.CANConfirmation: ...

class CANFrameBuilder(vspyx.Frames.CANFrame):
	"""Represents CAN frame construction support functionality
	 
	"""
	"""CANFrameBuilder
	"""
	ArbID: int
	ArbIDMask: int
	Arbitrary: int
	BaudrateSwitch: bool
	BaudrateSwitchMask: bool
	CANFDMask: bool
	DLC: int
	DLCMask: int
	Data: vspyx.Core.BytesView
	ExtendedMask: bool
	IsCANFD: bool
	IsExtended: bool
	IsRemote: bool
	Mask: vspyx.Core.BytesView
	Network: vspyx.Frames.NetworkIdentifier
	RemoteMask: bool
	Source: vspyx.Frames.SourceIdentifier
	Timestamp: vspyx.Runtime.Timestamp
	Type: vspyx.Frames.FrameType

	@staticmethod
	def CAN_DLCToDL(dlc: int, fd: bool) -> int:
		"""Convert a given CAN DLC nibble to a CAN data length.

		If `fd` is false, only 0-8 are acceptable, throwing
		otherwise.

		If `fd is true, then 0-64 are acceptable, throwing
		otherwise.

		"""
		pass



	@staticmethod
	def CAN_DLToDLC(dataLength: int, fd: bool) -> int:
		"""Convert a given CAN data length to a CAN DLC nibble.

		If `fd` is false, only 0-8 are acceptable, throwing
		otherwise.

		If `fd is true, then hex 0-F are acceptable, throwing
		otherwise.

		"""
		pass


	def Clone(self) -> vspyx.Frames.NetworkEvent: ...


	@typing.overload
	def ArbIDSet(self, set: int) -> vspyx.Frames.CANFrameBuilder: ...


	@typing.overload
	def ArbIDSet(self, set: int, mask: int) -> vspyx.Frames.CANFrameBuilder: ...


	@typing.overload
	def DLCSet(self, set: int) -> vspyx.Frames.CANFrameBuilder: ...


	@typing.overload
	def DLCSet(self, set: int, mask: int) -> vspyx.Frames.CANFrameBuilder: ...


	@typing.overload
	def RemoteSet(self, set: bool) -> vspyx.Frames.CANFrameBuilder: ...


	@typing.overload
	def RemoteSet(self, set: bool, mask: bool) -> vspyx.Frames.CANFrameBuilder: ...


	@typing.overload
	def ExtendedSet(self, set: bool) -> vspyx.Frames.CANFrameBuilder: ...


	@typing.overload
	def ExtendedSet(self, set: bool, mask: bool) -> vspyx.Frames.CANFrameBuilder: ...


	@typing.overload
	def CANFDSet(self, set: bool) -> vspyx.Frames.CANFrameBuilder: ...


	@typing.overload
	def CANFDSet(self, set: bool, mask: bool) -> vspyx.Frames.CANFrameBuilder: ...


	@typing.overload
	def BaudrateSwitchSet(self, set: bool) -> vspyx.Frames.CANFrameBuilder: ...


	@typing.overload
	def BaudrateSwitchSet(self, set: bool, mask: bool) -> vspyx.Frames.CANFrameBuilder: ...

	def DLCAutosetFromDataSizeAndCANFDFlag(self) -> vspyx.Frames.CANFrameBuilder:
		"""Automatically set the DLC given the currently set Data.

		Checks the current IsCANFD flag to enable the upper 4 DLC bits.

		Throws std::runtime_error if the Data is too long for the
		current frame type (2.0 vs FD)

		"""
		pass



	@typing.overload
	def Byte(self, index: int, value: int) -> vspyx.Frames.CANFrameBuilder: ...


	@typing.overload
	def Byte(self, index: int, value: int, mask: int) -> vspyx.Frames.CANFrameBuilder: ...


	@typing.overload
	def DataSet(self, bytes: typing.List[int]) -> typing.Any: ...


	@typing.overload
	def DataSet(self, bytes: vspyx.Core.BytesView) -> typing.Any: ...

class Identifier(vspyx.Core.Object):
	"""Represents an identity associated with an object
	 
	"""
	"""Identifier
	"""
	def __str__(self) -> str: ...

	def __eq__(self, rhs: vspyx.Frames.Identifier) -> bool: ...

class DriverIdentifier(vspyx.Frames.Identifier):
	"""Represents the general classification of a driver identify
	 
	"""
	"""DriverIdentifier
	"""
	Description: str

class EthernetConfirmation(vspyx.Frames.Confirmation):
	"""Represents the completion of a pending EthernetFrame forward/transmit
	"""
	"""EthernetConfirmation
	"""
	EthernetFrame: vspyx.Frames.EthernetFrame
	Status: vspyx.Frames.EthernetDriver.TxStatus

	@staticmethod
	def New(frame: vspyx.Frames.EthernetFrame, status: vspyx.Frames.EthernetDriver.TxStatus) -> vspyx.Frames.EthernetConfirmation: ...

class EthernetFrame(vspyx.Frames.Frame):
	"""Represents an Ethernet message frame
	 
	"""
	"""EthernetFrame
	"""
	IsFCSAvailable: bool
	IsFrameTooShort: bool
	IsNoPadding: bool
	IsPreemptionEnabled: bool
	PreemptionFlags: int

	@staticmethod
	def New(data: vspyx.Core.BytesView, timestamp: vspyx.Runtime.Timestamp, source: vspyx.Frames.SourceIdentifier, network: vspyx.Frames.NetworkIdentifier, arbitrary: int) -> vspyx.Frames.EthernetFrame: ...

class FlexRayClusterConfiguration:
	"""FlexRayClusterConfiguration
	"""
	ActionPointOffset: int
	CASRxLowMax: int
	ColdStartAttempts: int
	CycleDurationMicroSec: int
	DynamicSlotIdlePhaseMinislots: int
	ListenNoiseMacroticks: int
	MacroticksPerCycle: int
	MacrotickDurationMicroSec: int
	MaxWithoutClockCorrectionFatal: int
	MaxWithoutClockCorrectionPassive: int
	MinislotActionPointOffsetMacroticks: int
	MinislotDurationMacroticks: int
	NetworkIdleTimeMacroticks: int
	NetworkManagementVectorLengthBytes: int
	NumberOfMinislots: int
	NumberOfStaticSlots: int
	OffsetCorrectionStartMacroticks: int
	PayloadLengthOfStaticSlotInWords: int
	StaticSlotMacroticks: int
	SymbolWindowMacroticks: int
	SymbolWindowActionPointOffsetMacroticks: int
	SyncFrameIDCountMax: int
	TransmissionStartSequenceDurationBits: int
	WakeupRxIdleBits: int
	WakeupRxLowBits: int
	WakeupRxWindowBits: int
	WakeupTxActiveBits: int
	WakeupTxIdleBits: int

class FlexRayCCConfiguration:
	"""FlexRayCCConfiguration
	"""
	AcceptStartupRangeMicroticks: int
	AllowHaltDueToClock: bool
	AllowPassiveToActiveCyclePairs: int
	ClusterDriftDamping: int
	ChannelA: bool
	ChannelB: bool
	DecodingCorrectionMicroticks: int
	DelayCompensationAMicroticks: int
	DelayCompensationBMicroticks: int
	ExternOffsetCorrectionControl: int
	ExternRateCorrectionControl: int
	ExternOffsetCorrectionMicroticks: int
	ExternRateCorrectionMicroticks: int
	KeySlotID: int
	KeySlotOnlyEnabled: bool
	KeySlotUsedForStartup: bool
	KeySlotUsedForSync: bool
	LatestTxMinislot: int
	ListenTimeout: int
	MacroInitialOffsetA: int
	MacroInitialOffsetB: int
	MicroInitialOffsetA: int
	MicroInitialOffsetB: int
	MicroPerCycle: int
	MTSOnA: bool
	MTSOnB: bool
	OffsetCorrectionOutMicroticks: int
	RateCorrectionOutMicroticks: int
	SecondKeySlotID: int
	TwoKeySlotMode: bool
	WakeupPattern: int
	WakeupOnChannelB: bool
	GlobalConfiguration: vspyx.Frames.FlexRayClusterConfiguration

class FlexRayDriver(vspyx.Frames.Driver):
	"""Represents a Flexray driver
	 
	"""
	"""FlexRayDriver
	"""
	def SetCCConfiguration(self, idx: int, config: vspyx.Frames.FlexRayCCConfiguration) -> typing.Any: ...

	def Start(self, idx: int) -> typing.Any: ...

	def Halt(self, idx: int) -> typing.Any: ...

	def GetStartWhenGoingOnline(self, idx: int) -> bool: ...

	def SetStartWhenGoingOnline(self, idx: int, enable: bool) -> typing.Any: ...

	def GetAllowColdstart(self, idx: int) -> bool: ...

	def SetAllowColdstart(self, idx: int, enable: bool) -> typing.Any: ...

	def GetWakeupBeforeStart(self, idx: int) -> bool: ...

	def SetWakeupBeforeStart(self, idx: int, enable: bool) -> typing.Any: ...

class FlexRayFrameBuilder(vspyx.Frames.FlexRayFrame):
	"""FlexRayFrameBuilder
	"""
	Arbitrary: int
	Data: vspyx.Core.BytesView
	Network: vspyx.Frames.NetworkIdentifier
	Source: vspyx.Frames.SourceIdentifier
	Timestamp: vspyx.Runtime.Timestamp
	Type: vspyx.Frames.FrameType
	def Clone(self) -> vspyx.Frames.NetworkEvent: ...

	def GetCycle(self) -> int: ...

	def GetSlotID(self) -> int: ...

	def GetTSSLen(self) -> float: ...

	def GetFrameLen(self) -> float: ...

	def GetSymbol(self) -> vspyx.Frames.FlexRaySymbol: ...

	def GetHeaderCRCStatus(self) -> vspyx.Frames.FlexRayCRCStatus: ...

	def GetHeaderCRC(self) -> int: ...

	def GetCRCStatus(self) -> vspyx.Frames.FlexRayCRCStatus: ...

	def GetFrameCRC(self) -> int: ...

	def GetChannel(self) -> vspyx.Frames.FlexRayChannel: ...

	def GetIsNullFrame(self) -> bool: ...

	def GetReservedBit(self) -> bool: ...

	def GetPayloadPreamble(self) -> bool: ...

	def GetIsSyncFrame(self) -> bool: ...

	def GetIsStartupFrame(self) -> bool: ...

	def GetIsDynamicFrame(self) -> bool: ...

	def SetCycle(self, cycle: int) -> vspyx.Frames.FlexRayFrameBuilder: ...

	def SetSlotID(self, slotID: int) -> vspyx.Frames.FlexRayFrameBuilder: ...

	def SetTSSLen(self, TSSLen: float) -> vspyx.Frames.FlexRayFrameBuilder: ...

	def SetFrameLen(self, FrameLen: float) -> vspyx.Frames.FlexRayFrameBuilder: ...

	def SetSymbol(self, symbol: vspyx.Frames.FlexRaySymbol) -> vspyx.Frames.FlexRayFrameBuilder: ...

	def SetHeaderCRCStatus(self, headerCRCStatus: vspyx.Frames.FlexRayCRCStatus) -> vspyx.Frames.FlexRayFrameBuilder: ...

	def SetHeaderCRC(self, headerCRC: int) -> vspyx.Frames.FlexRayFrameBuilder: ...

	def SetCRCStatus(self, CRCStatus: vspyx.Frames.FlexRayCRCStatus) -> vspyx.Frames.FlexRayFrameBuilder: ...

	def SetFrameCRC(self, frameCRC: int) -> vspyx.Frames.FlexRayFrameBuilder: ...

	def SetChannel(self, channel: vspyx.Frames.FlexRayChannel) -> vspyx.Frames.FlexRayFrameBuilder: ...

	def SetIsNullFrame(self, isNullFrame: bool) -> vspyx.Frames.FlexRayFrameBuilder: ...

	def SetReservedBit(self, isReservedBit: bool) -> vspyx.Frames.FlexRayFrameBuilder: ...

	def SetPayloadPreamble(self, payloadPreamble: bool) -> vspyx.Frames.FlexRayFrameBuilder: ...

	def SetIsSyncFrame(self, isSyncFrame: bool) -> vspyx.Frames.FlexRayFrameBuilder: ...

	def SetIsStartupFrame(self, isStartupFrame: bool) -> vspyx.Frames.FlexRayFrameBuilder: ...

	def SetIsDynamicFrame(self, isDynamicFrame: bool) -> vspyx.Frames.FlexRayFrameBuilder: ...


	@typing.overload
	def DataSet(self, bytes: typing.List[int]) -> typing.Any: ...


	@typing.overload
	def DataSet(self, bytes: vspyx.Core.BytesView) -> typing.Any: ...

class FrameBuilder(vspyx.Frames.Frame):
	"""Represents the basis of a message frame builder
	 
	"""
	"""FrameBuilder
	"""
	Arbitrary: int
	Data: vspyx.Core.BytesView
	Timestamp: vspyx.Runtime.Timestamp
	def Clone(self) -> vspyx.Frames.NetworkEvent: ...

	def GetType(self) -> vspyx.Frames.FrameType: ...

	def GetSource(self) -> vspyx.Frames.SourceIdentifier: ...

	def GetNetwork(self) -> vspyx.Frames.NetworkIdentifier: ...

	def SetType(self, type: vspyx.Frames.FrameType) -> vspyx.Frames.FrameBuilder: ...

	def SetSource(self, source: vspyx.Frames.SourceIdentifier) -> vspyx.Frames.FrameBuilder: ...

	def SetNetwork(self, network: vspyx.Frames.NetworkIdentifier) -> vspyx.Frames.FrameBuilder: ...

	def DataSet(self, bytes: typing.List[int]) -> vspyx.Frames.FrameBuilder: ...

class LINDriver(vspyx.Frames.Driver):
	"""Rerepsents an LIN device driver
	 
	"""
	"""LINDriver
	"""

class Module(vspyx.Core.Module):
	"""Represents the generic basis of frame modules
	 
	"""
	"""Module
	"""
	def AddSourceFinder(self, finder: vspyx.Frames.SourceFinder) -> typing.Any: ...

	def DiscoverAllSources(self) -> typing.List[vspyx.Frames.Source]: ...

	def FindSourceByDescription(self, description: str) -> typing.List[vspyx.Frames.Source]: ...

	def AddBufferOpener(self, opener: vspyx.Frames.BufferOpener) -> typing.Any: ...

	def OpenBuffer(self, path: str) -> vspyx.Core.Task_0f35f34819: ...

	def CanOpenBuffer(self, path: str) -> bool: ...

	def NewSourceFromBuffer(self, buffer: vspyx.Frames.Buffer) -> vspyx.Frames.BufferSource: ...

	def AddWritableBufferOpener(self, opener: vspyx.Frames.WritableBufferOpener) -> typing.Any: ...

	def OpenWritableBuffer(self, path: str) -> vspyx.Frames.WritableBuffer: ...

	def CanWriteBuffer(self, path: str) -> bool: ...

class NetworkIdentifier(vspyx.Frames.Identifier):
	"""Represents a network object identifier
	 
	"""
	"""NetworkIdentifier
	"""
	Description: str
	Type: vspyx.Frames.FrameType

class SimResetEvent(vspyx.Frames.NetworkEvent):
	"""Represents an event propogating over the network when we know that a simulation
	 source has reset and closed its connections. While it is not always possible to
	 know that a source has reset connections, we can send this when a buffer file
	 simulation loops or a simulated ECU resets to make heuristic followers act
	 in a more user-friendly way.
	"""
	"""SimResetEvent
	"""
	CountsAsTraffic: bool

	@staticmethod
	def New(timestamp: vspyx.Runtime.Timestamp, source: vspyx.Frames.SourceIdentifier, network: vspyx.Frames.NetworkIdentifier) -> vspyx.Frames.SimResetEvent: ...

class SourceFinder(vspyx.Core.ResolverObject):
	"""Resolves message data source handler objects
	"""
	"""SourceFinder
	"""
	def Discover(self) -> typing.List[vspyx.Frames.Source]: ...

	def IsHandlerFor(self, description: str) -> bool: ...

	def Find(self, description: str) -> typing.List[vspyx.Frames.Source]: ...

class SourceIdentifier(vspyx.Frames.Identifier):
	"""Rerepesents the identification info for a data source object
	"""
	"""SourceIdentifier
	"""

class WritableBuffer(vspyx.Core.ResolverObject):
	"""Represents a writable output frame buffer
	"""
	"""WritableBuffer
	"""
	FileName: str
	NumberOfFrames: int
	TypeString: str
	def Append(self, frame: vspyx.Frames.Frame) -> typing.Any: ...

class WritableBufferOpener(vspyx.Core.ResolverObject):
	"""Represents the function of opening an output buffer for writing message frames
	"""
	"""WritableBufferOpener
	"""
	TypeString: str
	def CanWrite(self, path: str) -> bool: ...

	def Open(self, path: str) -> vspyx.Frames.WritableBuffer: ...

