import typing, enum, vspyx
from . import ISO11898, Processors

class Connector(vspyx.Runtime.Component):
	"""An ECU uses Connector elements in order to describe its bus interfaces and
	 to specify the sending/receiving behavior.
	 
	"""
	"""Connector
	"""
	@enum.unique
	class IngressActions(enum.IntEnum):
		Ignored = 0
		Received = 1
		Forwarded = 2
		Rejected = 3

	Channel: vspyx.Communication.Channel
	Controller: vspyx.Communication.Controller
	Egress: vspyx.Core.Function_316d8f46e9
	EgressBlocked: bool
	EgressImmediate: vspyx.Core.Function_a6845211fe
	Ingress: vspyx.Core.Function_a6845211fe
	IngressBlocked: bool
	def RefreshActiveControllerAndChannel(self) -> typing.Any: ...

	def AddPort(self, port: vspyx.Communication.ConnectorPort, permanent: bool) -> typing.Any:
		"""Add a ConnectorPort to the Connector configuration by reference.

		The ConnectorPort will not be owned by the Connector.

		"""
		pass


	def AttachToChannel(self, channel: vspyx.Communication.Channel, permanent: bool) -> typing.Any:
		"""Attach this connector to the given channel, removing the connector
		from a previously attached channel, if present.

		"""
		pass


	def DefaultIngress(self, event: vspyx.Frames.NetworkEvent) -> vspyx.Communication.Connector.IngressActions: ...

	def DefaultEgress(self, event: vspyx.Frames.NetworkEvent) -> typing.Any: ...

	def DefaultEgressImmediate(self, event: vspyx.Frames.NetworkEvent) -> vspyx.Communication.Connector.IngressActions: ...

	def IncrementIngressCounter(self, action: vspyx.Communication.Connector.IngressActions) -> typing.Any: ...

	def IncrementEgressCounter(self) -> typing.Any: ...

class Controller(vspyx.Runtime.Component):
	"""Controller is a dedicated hardware device by means of which hosts are sending
	 frames to and receiving frames from the communication medium.
	 
	"""
	"""Controller
	"""
	ChannelName: typing.Any
	"""Returns the name of the connected Channel.
	 If multiple Channels are connected, they will be separated by ", ".
		 
	"""

	DriverDescription: str
	def NewConnector(self) -> vspyx.Communication.Connector:
		"""Make a connector with a ref pointing at this controller.
		Does not initialize the connector.

		"""
		pass


	def ObserveEvent(self, event: vspyx.Frames.NetworkEvent) -> vspyx.Communication.Connector.IngressActions:
		"""Notify the controller of a network event that has occurred.

		For example, the network may call this function to notify the controller
		of an incoming Frame.

		This function should not be called upstream of the controller
		(within the ECU).

		"""
		pass


	def SubmitEvent(self, event: vspyx.Frames.NetworkEvent) -> typing.Any:
		"""Ask the controller to schedule/perform an action based on the given event.

		For example, the ECU's communication stack may call this function to ask
		the controller to transmit a Frame.

		This function should not be called downstream of the controller
		(outside of the ECU, in the greater communication simulation).

		"""
		pass


	def SubmitEventImmediate(self, event: vspyx.Frames.NetworkEvent) -> vspyx.Communication.Connector.IngressActions: ...

	def ConfigureStack(self, stack: vspyx.Communication.Stack) -> typing.Any:
		"""Configure a Communication::Stack for this Controller, adding PointProcessors
		and configuring them as necessary.

		"""
		pass


	def UnconfigureStack(self, stack: vspyx.Communication.Stack) -> typing.Any:
		"""Unonfigure a Communication::Stack for this Controller, removing PointProcessors
		and re-configuring them as necessary.

		"""
		pass


class CommunicationPoint(vspyx.Runtime.Point):
	"""A Runtime::Point which holds extra information not visible from the Runtime module
	 
	"""
	"""CommunicationPoint
	"""
	Controller: vspyx.Communication.Controller
	DissectorMessage: vspyx.Dissector.Message
	def GetAttribute(self, type: vspyx.Core.Tag) -> vspyx.Runtime.Value: ...

class PDUPoint(vspyx.Communication.CommunicationPoint):
	"""A Point which describes its payload in terms of bytes
	 
	"""
	"""PDUPoint
	"""
	def GetPayload(self) -> vspyx.Core.BytesView: ...

	def GetAttribute(self, type: vspyx.Core.Tag) -> vspyx.Runtime.Value: ...

	def SetAttribute(self, type: vspyx.Core.Tag, value: vspyx.Runtime.Value) -> bool: ...

class DataLinkPDUPoint(vspyx.Communication.PDUPoint):
	"""Represents PDU level data point runtime access interface
	 
	"""
	"""DataLinkPDUPoint
	"""
	Confirmation: vspyx.Frames.Confirmation
	"""Get the confirmation associated with this DataLinkPDUPoint.
	 
	 At first, this will be nullptr. When a confirmation is received by the
	 controller, this value will be set. Note that this value may change after
	 the Point has finished being consumed.
		 
	"""

	Frame: vspyx.Frames.Frame

	@staticmethod
	@typing.overload
	def NewFromFrame(controller: vspyx.Communication.Controller, frame: vspyx.Frames.Frame) -> vspyx.Runtime.Point.Consuming_03654c56a8: ...


	@staticmethod
	@typing.overload
	def NewFromFrame(controller: vspyx.Communication.Controller, frame: vspyx.Frames.Frame, direction: vspyx.Runtime.Point.Direction) -> vspyx.Runtime.Point.Consuming_03654c56a8: ...

	def GetAttribute(self, type: vspyx.Core.Tag) -> vspyx.Runtime.Value: ...

class CANController(vspyx.Communication.Controller):
	"""Represents a CAN controller device interface
	"""
	"""CANController
	"""
	Driver: vspyx.Frames.CANDriver
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	@typing.overload
	def New() -> vspyx.Communication.CANController: ...

	def NewISO11898_1Interface(self) -> vspyx.Communication.ISO11898.ISO11898_1Interface: ...


	@staticmethod
	@typing.overload
	def New(config: typing.Any) -> vspyx.Communication.CANController: ...

	def CloneConfiguration(self) -> typing.Any: ...

class Channel(vspyx.Runtime.Component):
	"""A Channel is the transmission medium that is used to send and receive information between
	 communicating ECUs. Each Cluster has at least one Channel. Bus systems like
	 CAN and LIN only have exactly one Channel. A FlexRay Cluster may have more than one
	 Channels that may be used in parallel for redundant communication.
	 An ECU is part of a cluster if it contains at least one controller that is connected to at
	 least one channel of the cluster.
	 
	"""
	"""Channel
	"""
	Cluster: vspyx.Communication.Cluster
	"""Get the Cluster that this Channel is a member of
		 
	"""

	Connectors: typing.List[vspyx.Communication.Connector]
	EnableComStack: bool
	LastEvent: vspyx.Frames.NetworkEvent
	OffloadProcessing: bool
	OnFrameTriggeringsChanged: vspyx.Core.Callback_add982ce23
	OnTriggeringsChanged: vspyx.Core.Callback_634bd5c449
	"""Called whenever the Active Triggerings are changed.
	 
	 It is not guaranteed that this will only be called if an Active
	 Triggering has been added/removed.
		 
	"""

	RecommendedMappings: typing.List[str]
	TotalTraffic: int
	UtilizationPercent: vspyx.Runtime.Signal

	@staticmethod
	def Discovery(app: vspyx.Core.Application, driver: vspyx.Frames.Driver) -> vspyx.Communication.Channel: ...


	@typing.overload
	def AddFrameTriggering(self, frameTriggering: vspyx.Communication.FrameTriggering) -> typing.Any: ...


	@typing.overload
	def AddFrameTriggering(self, frameTriggering: vspyx.Communication.FrameTriggering, permanent: bool) -> typing.Any: ...


	@typing.overload
	def AddPDUTriggering(self, pduTriggering: vspyx.Communication.PDUTriggering) -> typing.Any: ...


	@typing.overload
	def AddPDUTriggering(self, pduTriggering: vspyx.Communication.PDUTriggering, permanent: bool) -> typing.Any: ...

	def MeasurePercentOfSecond(self, event: vspyx.Frames.NetworkEvent) -> float: ...

	def NewAttachedController(self, namePrefix: str, listenOnly: bool) -> typing.Any:
		"""Create a new controller of the correct type for this channel
		and attach it with a new connector.

		The caller is responsible for taking ownership of the returned
		objects.

		:Parameter namePrefix: Prefix for the created controller/connector
		names
		:Parameter listenOnly: Create the controller with parameters such
		that it will not influence the channel (ACKs, transmits, etc.)

		"""
		pass


	def NewConnector(self) -> vspyx.Communication.Connector: ...

	def ConnectAutoAttachConnectors(self, failSilently: bool) -> typing.Any: ...

	def IsDiscovery(self) -> bool: ...

	class SubmissionResult:
		"""SubmissionResult
		"""
		Acked: int
		Ignored: int
		Forwarded: int
		Rejected: int
		AssignedArbitrary: int
		VotedResult: vspyx.Communication.Connector.IngressActions
		"""The opinion of the Channel about this SubmissionResult.
		 Given every node's response, this is the overall takeaway.
		 
		 For instance, for CAN, any node rejecting with a NAK will
		 cause the entire bus to consider the frame to be NAKed.
				 
		"""

		def AddResult(self, action: vspyx.Communication.Connector.IngressActions) -> typing.Any:
			"""Add a single ingress action to the appropriate counter
			within the SubmissionResult.

			"""
			pass



		@staticmethod
		def Reject() -> vspyx.Communication.Channel.SubmissionResult: ...


class EthernetChannel(vspyx.Communication.Channel):
	"""EthernetChannel
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	@typing.overload
	def New() -> vspyx.Communication.EthernetChannel: ...


	@typing.overload
	def SetVLANIdentifier(self, id: typing.Any) -> typing.Any: ...


	@typing.overload
	def SetVLANIdentifier(self, id: typing.Any, priority: typing.Any) -> typing.Any: ...


	@typing.overload
	def SetVLANIdentifier(self, id: typing.Any, priority: typing.Any, isDropEligible: typing.Any) -> typing.Any: ...


	@staticmethod
	@typing.overload
	def New(config: typing.Any) -> vspyx.Communication.EthernetChannel: ...

	def CloneConfiguration(self) -> typing.Any: ...

	def CloneState(self) -> typing.Any: ...

	def UpdateState(self, state: typing.Any) -> typing.Any: ...

class Topology(vspyx.Core.ResolverObject):
	"""Definition of a network topology
	 
	"""
	"""Topology
	"""
	Channels: vspyx.Core.ResolverCollection
	Clusters: vspyx.Core.ResolverCollection
	Connectors: vspyx.Core.ResolverCollection
	Controllers: vspyx.Core.ResolverCollection
	ECUs: vspyx.Core.ResolverCollection
	Frames: vspyx.Core.ResolverCollection
	PDUGroups: vspyx.Core.ResolverCollection
	PDUs: vspyx.Core.ResolverCollection
	Signals: vspyx.Core.ResolverCollection

	@staticmethod
	@typing.overload
	def New() -> vspyx.Communication.Topology: ...


	@staticmethod
	@typing.overload
	def New(owning: bool) -> vspyx.Communication.Topology: ...

	def MergeIn(self, topology: vspyx.Communication.Topology) -> typing.Any: ...

class TopologySubset(vspyx.Core.ResolverObject):
	"""Network topology subset
	 
	"""
	"""TopologySubset
	"""
	Topology: vspyx.Communication.Topology

class AUTOSARDataType(vspyx.Core.ResolverObject):
	"""AUTOSARDataType
	"""

class AUTOSARDataPrototype(vspyx.Runtime.Traceable):
	"""AUTOSARDataPrototype
	"""
	DataType: vspyx.Communication.AUTOSARDataType

class SocketConnectionBundle(vspyx.Core.ResolverObject):
	"""A named group of SocketConnections, holding the connections
	 themselves and common properties between them.
	 
	"""
	"""SocketConnectionBundle
	"""
	@enum.unique
	class Side(enum.IntEnum):
		NONE = 0
		Server = 1
		Client = 2

	LengthEncoding: vspyx.intrepidcs.vspyx.rpc.Communication.SoAdPduHeaderLengthEncodingEnumType
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	PDUIdentifiers: typing.List[vspyx.Communication.SocketConnectionIPduIdentifier]
	ServerPort: vspyx.Communication.SocketAddress
	def GetSideForConnector(self, connector: vspyx.Communication.Connector) -> vspyx.Communication.SocketConnectionBundle.Side: ...


	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.SocketConnectionBundle: ...

	def CloneConfiguration(self) -> typing.Any: ...

class ServiceInstance(vspyx.Core.ResolverObject):
	"""ServiceInstance
	"""
	InstanceIdentifier: int
	LoadBalancingInfo: typing.Any
	MajorVersion: int
	MinorVersion: int
	ServerConfig: vspyx.Communication.SDServerConfig
	ServiceIdentifier: int
	ServiceName: str
	SocketConnectionIPduIdentifiers: typing.List[vspyx.Communication.SocketConnectionIPduIdentifier]
	TTL: int
	def IsReferenced(self, obj: vspyx.Core.ResolverObject) -> bool: ...

class ConnectorPort(vspyx.Core.ResolverObject):
	"""The Ecu communication relationship defines which signals, Pdus and frames are actually received and
	 transmitted by this ECU.
	
	 For each signal, Pdu or Frame that is transmitted or received and used by the Ecu an association
	 between an ISignalPort, IPduPort or FramePort with the corresponding Triggering shall be created.
	 
	"""
	"""ConnectorPort
	"""
	Direction: vspyx.intrepidcs.vspyx.rpc.Communication.Directions

class Triggering(vspyx.Core.ResolverObject):
	"""Triggering describes the pairing of a communication object to a channel and defines the manner of
	 triggering (timing information) and identification of the object on the channel.
	 
	 A CANFrameTriggering would, for instance, describe the Arbitration ID that a particular frame is
	 expected to be seen under on a particular channel. It would then go on to define the position of
	 PDUs in the Frame when seen on that channel, which would be PDUTriggerings.
	 
	"""
	"""Triggering
	"""
	OnPortsChanged: vspyx.Core.Callback_634bd5c449
	"""Called when the Ports on this Triggering have changed.
	 
	 It is not guaranteed that this will only be called if a Port has been added/removed.
		 
	"""

	def MakePort(self, direction: vspyx.intrepidcs.vspyx.rpc.Communication.Directions) -> vspyx.Communication.ConnectorPort:
		"""Make a Port for this Triggering, setting the direction as specified and leaving the rest of
		the options as default.

		The object will not be initialized as returned, nor will it be linked anywhere.

		"""
		pass


	def AddPort(self, port: vspyx.Communication.ConnectorPort, permanent: bool) -> typing.Any:
		"""Add a Port to this Triggering. If `permanent` is true, it will be added to the configuration.

		The Port will not be owned by the Triggering.

		"""
		pass


class PDUTriggering(vspyx.Communication.Triggering):
	"""PDUTriggering describes on which channel the ComPDU is transmitted.
	 
	"""
	"""PDUTriggering
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	PDU: vspyx.Communication.PDU

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.PDUTriggering: ...

	def CloneConfiguration(self) -> typing.Any: ...

class SocketConnectionIPduIdentifier(vspyx.Core.ResolverObject):
	"""SocketConnectionIPduIdentifier
	"""
	HeaderId: int
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	PduTriggering: vspyx.Communication.PDUTriggering

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.SocketConnectionIPduIdentifier: ...

	def CloneConfiguration(self) -> typing.Any: ...

class InitialSDDelayConfig(vspyx.Core.Object):
	"""InitialSDDelayConfig
	"""
	InitialDelayMaxValue: float
	InitialDelayMinValue: float
	InitialRepetitionsBaseDelay: typing.Any
	InitialRepetitionsMax: typing.Any
	def CloneState(self) -> typing.Any: ...

	def UpdateState(self, state: typing.Any) -> typing.Any: ...

class RequestResponseDelay(vspyx.Core.Object):
	"""RequestResponseDelay
	"""
	def MinValue(self) -> float: ...

	def MaxValue(self) -> float: ...

	def CloneState(self) -> typing.Any: ...

	def UpdateState(self, state: typing.Any) -> typing.Any: ...

class SDServerConfig(vspyx.Core.ResolverObject):
	"""SDServerConfig
	"""
	MajorVersion: typing.Any
	MinorVersion: typing.Any
	OfferCyclicDelay: typing.Any
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	TTL: int
	def InitialOfferBehavior(self) -> vspyx.Communication.InitialSDDelayConfig: ...

	def ReqResDelay(self) -> vspyx.Communication.RequestResponseDelay: ...


	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.SDServerConfig: ...

	def CloneConfiguration(self) -> typing.Any: ...

class EventHandler(vspyx.Core.ResolverObject):
	"""EventHandler
	"""
	EventGroupId: int
	SDConfig: vspyx.Communication.SDServerConfig
	SocketConnectionIPduIdentifiers: typing.List[vspyx.Communication.SocketConnectionIPduIdentifier]
	SubscriberEndpoint: vspyx.Communication.ApplicationEndpoint

class ProvidedEventGroup(vspyx.Communication.EventHandler):
	"""ProvidedEventGroup
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	def MulticastThreshold(self) -> typing.Any: ...


	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.ProvidedEventGroup: ...

	def CloneConfiguration(self) -> typing.Any: ...

class ConsumedEventGroup(vspyx.Communication.EventHandler):
	"""ConsumedEventGroup
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.ConsumedEventGroup: ...

	def CloneConfiguration(self) -> typing.Any: ...

class ProvidedServiceInstance(vspyx.Communication.ServiceInstance):
	"""ProvidedServiceInstance
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.ProvidedServiceInstance: ...

	def CloneConfiguration(self) -> typing.Any: ...

class ConsumedServiceInstance(vspyx.Communication.ServiceInstance):
	"""ConsumedServiceInstance
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	ProvidedServiceInstance: vspyx.Communication.ProvidedServiceInstance

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.ConsumedServiceInstance: ...

	def CloneConfiguration(self) -> typing.Any: ...

class ApplicationEndpoint(vspyx.Core.ResolverObject):
	"""The endpoint on an ECU in terms of application addressing
	 
	"""
	"""ApplicationEndpoint
	"""
	@enum.unique
	class TransportProtocols(enum.IntEnum):
		NONE = 0
		Generic = 1
		IEEE1722 = 2
		HTTP = 3
		TCP = 4
		UDP = 5
		RTP = 6

	ConsumedServiceInstances: typing.List[vspyx.Communication.ConsumedServiceInstance]
	NetworkEndpoint: vspyx.Communication.NetworkEndpoint
	"""Retrieve the network endpoint associated with this application endpoint,
	 if set and resolvable. Returns nullptr if either condition is not met.
		 
	"""

	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	Port: typing.Any
	ProvidedServiceInstances: typing.List[vspyx.Communication.ProvidedServiceInstance]
	TransportProtocol: vspyx.Communication.ApplicationEndpoint.TransportProtocols

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.ApplicationEndpoint: ...

	def CloneConfiguration(self) -> typing.Any: ...

class Stack(vspyx.Runtime.Component):
	"""A Communication Stack inside of an ECU
	 
	 The Stack works as a basic Runtime::Point broadcasting system.
	 When a Point is submitted, it is given to all* of the PointProcessors
	 registered with the Stack, then sent out via the OnPoint handler.
	 
	 Each of the PointProcessors contain filtering logic which determines
	 whether they will handle the Point. When a PointProcessor generates
	 a Point, it will give the Point back to the Stack so it can be
	 distributed, both to other PointProcessors that may use the new Point,
	 and to the outside world (Runtime::Environment, etc.).
	 
	 * PointProcessors can optionally specify a Controller. If they do,
	 they will only receive Points associated with that Controller.
	 
	"""
	"""Stack
	"""
	OnPoint: vspyx.Core.Callback_bf2c6c2abd
	"""Called for every Point that the Stack processes or generates.
		 
	"""


	@staticmethod
	def New() -> vspyx.Communication.Stack:
		"""Create a new empty Stack.

		"""
		pass


	def AddPointProcessor(self, processor: vspyx.Communication.PointProcessor) -> typing.Any:
		"""Add the given PointProcessor to the Stack.

		"""
		pass


	def RemovePointProcessor(self, processor: vspyx.Communication.PointProcessor) -> bool:
		"""Remove the given PointProcessor from the Stack.

		Use ReleasePointProcessor instead for proper reference counting
		of the PointProcessor's attachment.

		:Returns: true if the PointProcessor was found and removed

		"""
		pass


	def ReleasePointProcessor(self, processor: vspyx.Communication.PointProcessor) -> bool:
		"""Atomically decrement the UseCount of the PointProcessor, and
		remove it if no other objects are keeping it in the Stack
		(UseCount == 0).

		:Returns: true if the PointProcessor was found and removed

		"""
		pass


	def GetPointProcessorByID(self, id: str) -> vspyx.Communication.PointProcessor:
		"""Look up a PointProcessor in the Stack by its ID

		:Returns: the PointProcessor

		"""
		pass


	def SubmitPoint(self, point: vspyx.Runtime.Point.Consuming_1edf1860a4) -> vspyx.Communication.Connector.IngressActions:
		"""Submit a Point into the Stack for processing.

		Use SubmitNetworkEvent if you have a NetworkEvent, a Point will
		be created for you.

		"""
		pass



	@typing.overload
	def SubmitPointAndGetResponse(self, point: vspyx.Runtime.Point.Consuming_1edf1860a4) -> vspyx.Runtime.Point:
		"""Submit a Point for which we expect a point in response.

		Both the submitted Point and the response Point are expected
		out of OnPoint as well.

		"""
		pass



	@typing.overload
	def SubmitPointAndGetResponse(self, point: vspyx.Runtime.Point.Consuming_1edf1860a4, timeout: typing.Any) -> vspyx.Runtime.Point:
		"""Submit a Point for which we expect a point in response.

		Both the submitted Point and the response Point are expected
		out of OnPoint as well.

		"""
		pass


	def SubmitNetworkEvent(self, event: vspyx.Frames.NetworkEvent, controller: vspyx.Communication.Controller) -> vspyx.Communication.Connector.IngressActions:
		"""Submit a NetworkEvent into the stack.

		For frames, this will immediately create a new DataLinkPDUPoint
		with Direction::Receive and submit it into the stack.

		For confirmations, this will attempt to match the confirmation
		to a DataLinkPDUPoint we've seen.

		For other NetworkEvents, this will immediately create a new
		DataLinkEventPoint with direction::Receive and submit it into
		the stack.

		"""
		pass


	def SuppressConfigurationUpdates(self) -> typing.Any:
		"""This is called as a performance optimization when doing large
		updates to the configuration, such as when initially configuring
		the Stack.

		No Points will be dispatched to PointProcessors until
		UnsuppressConfigurationUpdates() is called.

		"""
		pass


	def UnsuppressConfigurationUpdates(self) -> typing.Any:
		"""Allow all suppressed confuiguration updates to take place.

		See SuppressConfigurationUpdates() for more information.

		"""
		pass


class Architecture(vspyx.Runtime.Environment):
	"""Architecture
	"""
	Stack: vspyx.Communication.Stack
	def SubmitPoint(self, point: vspyx.Runtime.Point) -> typing.Any: ...

class BufferUpdatePoint(vspyx.Communication.PDUPoint):
	"""Used to signal to a communication controller that the transmit buffer
	 should be updated. This is the case for time triggered network types,
	 where a DataLinkPDUPoint should not be immediately created by the
	 transmitting entity, rather a buffer update should be initiated and
	 the controller will create the DataLinkPDUPoint (as well as the
	 corresponding network traffic) when it is time.
	 
	"""
	"""BufferUpdatePoint
	"""
	NetworkEvent: vspyx.Frames.NetworkEvent

class CANChannel(vspyx.Communication.Channel):
	"""Represents a CAN channel interface
	"""
	"""CANChannel
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	@typing.overload
	def New() -> vspyx.Communication.CANChannel: ...

	def NewISO11898_1Interface(self) -> vspyx.Communication.ISO11898.ISO11898_1Interface: ...


	@staticmethod
	@typing.overload
	def New(config: typing.Any) -> vspyx.Communication.CANChannel: ...

	def CloneConfiguration(self) -> typing.Any: ...

	def CloneState(self) -> typing.Any: ...

	def UpdateState(self, state: typing.Any) -> typing.Any: ...

class Cluster(vspyx.Runtime.Component):
	"""Cluster is the main element to describe the topological connection of communicating ECUs.
	 A cluster describes the ensemble of ECUs, which are linked by a communication medium of arbitrary
	 topology (bus, star, ring, ...). The nodes within the cluster share the same communication protocol, which
	 may be event-triggered, time-triggered or a combination of both.
	 A Cluster aggregates one or more physical channels.
	 
	"""
	"""Cluster
	"""

	@staticmethod
	def Discovery(app: vspyx.Core.Application, source: vspyx.Communication.SourceHandle, driver: vspyx.Frames.Driver) -> vspyx.Communication.Cluster: ...

	def AddChannel(self, channel: vspyx.Communication.Channel) -> typing.Any: ...

	def RemoveChannel(self, channel: vspyx.Communication.Channel) -> typing.Any: ...

class CANCluster(vspyx.Communication.Cluster):
	"""Represents a CAN cluster
	"""
	"""CANCluster
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	@typing.overload
	def New() -> vspyx.Communication.CANCluster: ...


	@staticmethod
	@typing.overload
	def New(config: typing.Any) -> vspyx.Communication.CANCluster: ...

	def CloneConfiguration(self) -> typing.Any: ...

class CANConnector(vspyx.Communication.Connector):
	"""Represents a connection between an ECU and a CAN bus interface
	"""
	"""CANConnector
	"""
	CANController: vspyx.Communication.CANController
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	@typing.overload
	def New() -> vspyx.Communication.CANConnector: ...


	@staticmethod
	@typing.overload
	def New(config: typing.Any) -> vspyx.Communication.CANConnector: ...

	def CloneConfiguration(self) -> typing.Any: ...

	def CloneState(self) -> typing.Any: ...

	def UpdateState(self, state: typing.Any) -> typing.Any: ...

class CANDataLinkPDUPoint(vspyx.Communication.DataLinkPDUPoint):
	"""CANDataLinkPDUPoint
	"""

	@staticmethod
	@typing.overload
	def New(direction: vspyx.Runtime.Point.Direction, controller: vspyx.Communication.Controller) -> vspyx.Runtime.Point.Consuming_5056ff9b42: ...


	@staticmethod
	@typing.overload
	def New(direction: vspyx.Runtime.Point.Direction, controller: vspyx.Communication.Controller, upstreamPoints: typing.List[vspyx.Runtime.Point]) -> vspyx.Runtime.Point.Consuming_5056ff9b42: ...


	@staticmethod
	@typing.overload
	def New(direction: vspyx.Runtime.Point.Direction, controller: vspyx.Communication.Controller, frame: vspyx.Frames.CANFrame) -> vspyx.Runtime.Point.Consuming_5056ff9b42: ...


	@staticmethod
	@typing.overload
	def New(direction: vspyx.Runtime.Point.Direction, controller: vspyx.Communication.Controller, arbID: int, data: vspyx.Core.BytesView) -> vspyx.Runtime.Point.Consuming_5056ff9b42: ...


	@staticmethod
	@typing.overload
	def New(direction: vspyx.Runtime.Point.Direction, controller: vspyx.Communication.Controller, arbID: int, data: vspyx.Core.BytesView, isCANFD: bool) -> vspyx.Runtime.Point.Consuming_5056ff9b42: ...


	@staticmethod
	@typing.overload
	def New(direction: vspyx.Runtime.Point.Direction, controller: vspyx.Communication.Controller, arbID: int, data: vspyx.Core.BytesView, isCANFD: bool, baudrateSwitch: bool) -> vspyx.Runtime.Point.Consuming_5056ff9b42: ...


	@staticmethod
	@typing.overload
	def New(direction: vspyx.Runtime.Point.Direction, controller: vspyx.Communication.Controller, arbID: int, data: vspyx.Core.BytesView, isCANFD: bool, baudrateSwitch: bool, isExtended: typing.Any) -> vspyx.Runtime.Point.Consuming_5056ff9b42: ...


	@staticmethod
	@typing.overload
	def New(direction: vspyx.Runtime.Point.Direction, controller: vspyx.Communication.Controller, arbID: int, data: vspyx.Core.BytesView, isCANFD: bool, baudrateSwitch: bool, isExtended: typing.Any, dlc: typing.Any) -> vspyx.Runtime.Point.Consuming_5056ff9b42: ...


	@staticmethod
	@typing.overload
	def New(direction: vspyx.Runtime.Point.Direction, controller: vspyx.Communication.Controller, arbID: int, data: vspyx.Core.BytesView, isCANFD: bool, baudrateSwitch: bool, isExtended: typing.Any, dlc: typing.Any, isRemote: bool) -> vspyx.Runtime.Point.Consuming_5056ff9b42: ...

class InvocationOptions:
	"""Base type for structures which will be given as options to PointProcessor::Invoke
	 
	"""
	"""InvocationOptions
	"""

class PointProcessor(vspyx.Runtime.Component):
	"""An element of a Communication::Stack which processes points
	 
	"""
	"""PointProcessor
	"""
	@enum.unique
	class PriorityGroup(enum.IntEnum):
		Tagger = 0
		Consumer = 1
		LAST = 2

	@enum.unique
	class HandlerPriority(enum.IntEnum):
		NoHandler = 0
		Normal = 1

	OnPoint: vspyx.Core.Callback_66dc7ed174
	UseCount: int
	"""Get the current number of objects which have configured this PointProcessor.
	 
	 The UseCount starts at 1 when the PointProcessor is created.
	 
	 This allows the PointProcessor to be removed by the Stack if all objects using
	 it are removed.
		 
	"""

	def SubmitPoint(self, consuming: vspyx.Runtime.Point.Consuming_1edf1860a4) -> bool:
		"""SubmitPoint will be called by the Stack for every incoming point.
		If this processor will process this point, it should return true.

		"""
		pass


	def GetPriorityGroup(self) -> vspyx.Communication.PointProcessor.PriorityGroup:
		"""Get the Priority Group for this PointProcessor.

		"""
		pass


	def IsHandlerForPointWithResponse(self, arg0: vspyx.Runtime.Point.Consuming_1edf1860a4) -> vspyx.Communication.PointProcessor.HandlerPriority:
		"""Returns the priority of the handler if this PointProcessor will
		handle the Point if given through SubmitPointAndGetResponse.

		If NoHandler is returned, SubmitPointAndGetResponse should not be called.

		"""
		pass


	def SubmitPointAndGetResponse(self, consuming: vspyx.Runtime.Point.Consuming_1edf1860a4, timeout: typing.Any) -> vspyx.Runtime.Point:
		"""This function will be called by the Stack if this
		PointProcessor declares the highest prioriry for the Point in
		IsHandlerForPointWithResponse.

		The given promise is expected to be fulfilled or excepted at
		some point in the future.

		"""
		pass


	def Invoke(self, consuming: vspyx.Runtime.Point.Consuming_1edf1860a4, options: vspyx.Communication.InvocationOptions) -> bool:
		"""Invoke will be called by an Invoker PointProcessor when custom filtering logic
		dictates that this PointProcessor should process this point. Options are PointProcessor
		specific and are intended to direct this PointProcessor's behavior. For instance,
		options may be used to ask that the PointProcessor feeds this point to a non-standard
		entry point of the stack.

		"""
		pass


	def SetController(self, controller: vspyx.Communication.Controller) -> typing.Any:
		"""Set the controller associated with this PointProcessor, or std::nullopt for no
		association.

		See GetController() for an explanation of controllers on PointProcessors.

		"""
		pass


	def IncrementUseCount(self) -> int:
		"""Directly increment the UseCount of the PointProcessor.

		The UseCount starts at 1 when the PointProcessor is created, so you are
		not required to call this function when creating a PointProcessor.

		:Returns: the new UseCount

		"""
		pass


	def DecrementUseCount(self) -> int:
		"""Directly decrement the UseCount of the PointProcessor.

		Usually you should use Stack::ReleasePointProcessor instead, which will
		atomically remove the PointProcessor when the UseCount becomes 0.

		:Returns: the new UseCount

		"""
		pass


	def SuppressConfigurationUpdates(self) -> typing.Any:
		"""This is called as a performance optimization when doing large
		updates to the configuration, such as when initially configuring
		the stack.

		No Points will be received until UnsuppressConfigurationUpdates()
		is called.

		"""
		pass


	def UnsuppressConfigurationUpdates(self) -> typing.Any:
		"""Allow all suppressed confuiguration updates to take place.

		See SuppressConfigurationUpdates() for more information.

		"""
		pass


class CANDiscoveryProcessor(vspyx.Communication.PointProcessor):
	"""Represents a processor which handles PDU points containing CAN frames
	"""
	"""CANDiscoveryProcessor
	"""

	@staticmethod
	def New() -> vspyx.Communication.CANDiscoveryProcessor: ...

class DataLinkEventPoint(vspyx.Communication.CommunicationPoint):
	"""Represents PDU level data point runtime access interface
	 
	"""
	"""DataLinkEventPoint
	"""
	NetworkEvent: vspyx.Frames.NetworkEvent

class CANErrorCountsPoint(vspyx.Communication.DataLinkEventPoint):
	"""CANErrorCountsPoint
	"""

class Frame(vspyx.Runtime.Traceable):
	"""A Frame represents a general design object that is used
	 to describe the layout of the included Pdus as a reusable asset.
	 
	"""
	"""Frame
	"""
	Length: typing.Any

	@typing.overload
	def NewPoint(self, direction: vspyx.Runtime.Point.Direction, data: vspyx.Core.BytesView) -> vspyx.Runtime.Point.Consuming_6aef469678: ...


	@typing.overload
	def NewPoint(self, direction: vspyx.Runtime.Point.Direction, data: vspyx.Core.BytesView, upstreamPoints: typing.List[vspyx.Runtime.Point]) -> vspyx.Runtime.Point.Consuming_6aef469678: ...


	@typing.overload
	def NewPoint(self, direction: vspyx.Runtime.Point.Direction, data: vspyx.Core.BytesView, upstreamPoints: typing.List[vspyx.Runtime.Point], controller: vspyx.Communication.Controller) -> vspyx.Runtime.Point.Consuming_6aef469678: ...

class CANFrame(vspyx.Communication.Frame):
	"""Represents the CAN-specific layout of a frame object
	"""
	"""CANFrame
	"""

	@typing.overload
	def NewPoint(self, direction: vspyx.Runtime.Point.Direction, data: vspyx.Core.BytesView) -> vspyx.Runtime.Point.Consuming_6aef469678: ...


	@typing.overload
	def NewPoint(self, direction: vspyx.Runtime.Point.Direction, data: vspyx.Core.BytesView, upstreamPoints: typing.List[vspyx.Runtime.Point]) -> vspyx.Runtime.Point.Consuming_6aef469678: ...


	@typing.overload
	def NewPoint(self, direction: vspyx.Runtime.Point.Direction, data: vspyx.Core.BytesView, upstreamPoints: typing.List[vspyx.Runtime.Point], controller: vspyx.Communication.Controller) -> vspyx.Runtime.Point.Consuming_6aef469678: ...

	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@typing.overload
	def NewPoint(self, direction: vspyx.Runtime.Point.Direction, upstreamPoints: typing.List[vspyx.Runtime.Point], controller: vspyx.Communication.CANController, data: vspyx.Core.BytesView) -> vspyx.Runtime.Point.Consuming_6aef469678: ...


	@typing.overload
	def NewPoint(self, direction: vspyx.Runtime.Point.Direction, upstreamPoints: typing.List[vspyx.Runtime.Point], controller: vspyx.Communication.CANController, data: vspyx.Core.BytesView, arbID: typing.Any) -> vspyx.Runtime.Point.Consuming_6aef469678: ...


	@typing.overload
	def NewPoint(self, direction: vspyx.Runtime.Point.Direction, upstreamPoints: typing.List[vspyx.Runtime.Point], controller: vspyx.Communication.CANController, data: vspyx.Core.BytesView, arbID: typing.Any, isCANFD: typing.Any) -> vspyx.Runtime.Point.Consuming_6aef469678: ...


	@typing.overload
	def NewPoint(self, direction: vspyx.Runtime.Point.Direction, upstreamPoints: typing.List[vspyx.Runtime.Point], controller: vspyx.Communication.CANController, data: vspyx.Core.BytesView, arbID: typing.Any, isCANFD: typing.Any, baudrateSwitch: typing.Any) -> vspyx.Runtime.Point.Consuming_6aef469678: ...


	@typing.overload
	def NewPoint(self, direction: vspyx.Runtime.Point.Direction, upstreamPoints: typing.List[vspyx.Runtime.Point], controller: vspyx.Communication.CANController, data: vspyx.Core.BytesView, arbID: typing.Any, isCANFD: typing.Any, baudrateSwitch: typing.Any, isExtended: typing.Any) -> vspyx.Runtime.Point.Consuming_6aef469678: ...


	@typing.overload
	def NewPoint(self, direction: vspyx.Runtime.Point.Direction, upstreamPoints: typing.List[vspyx.Runtime.Point], controller: vspyx.Communication.CANController, data: vspyx.Core.BytesView, arbID: typing.Any, isCANFD: typing.Any, baudrateSwitch: typing.Any, isExtended: typing.Any, dlc: typing.Any) -> vspyx.Runtime.Point.Consuming_6aef469678: ...


	@typing.overload
	def NewPoint(self, direction: vspyx.Runtime.Point.Direction, upstreamPoints: typing.List[vspyx.Runtime.Point], controller: vspyx.Communication.CANController, data: vspyx.Core.BytesView, arbID: typing.Any, isCANFD: typing.Any, baudrateSwitch: typing.Any, isExtended: typing.Any, dlc: typing.Any, isRemote: typing.Any) -> vspyx.Runtime.Point.Consuming_6aef469678: ...


	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.CANFrame: ...

	def CloneConfiguration(self) -> typing.Any: ...

class FramePoint(vspyx.Communication.PDUPoint):
	"""FramePoint
	"""

class CANFramePoint(vspyx.Communication.FramePoint):
	"""CANFramePoint
	"""

	@staticmethod
	@typing.overload
	def New(direction: vspyx.Runtime.Point.Direction, upstreamPoints: typing.List[vspyx.Runtime.Point], controller: vspyx.Communication.CANController, frame: vspyx.Communication.CANFrame, data: vspyx.Core.BytesView) -> vspyx.Runtime.Point.Consuming_1dd119a6a6: ...


	@staticmethod
	@typing.overload
	def New(direction: vspyx.Runtime.Point.Direction, upstreamPoints: typing.List[vspyx.Runtime.Point], controller: vspyx.Communication.CANController, frame: vspyx.Communication.CANFrame, data: vspyx.Core.BytesView, arbID: typing.Any) -> vspyx.Runtime.Point.Consuming_1dd119a6a6: ...


	@staticmethod
	@typing.overload
	def New(direction: vspyx.Runtime.Point.Direction, upstreamPoints: typing.List[vspyx.Runtime.Point], controller: vspyx.Communication.CANController, frame: vspyx.Communication.CANFrame, data: vspyx.Core.BytesView, arbID: typing.Any, isCANFD: typing.Any) -> vspyx.Runtime.Point.Consuming_1dd119a6a6: ...


	@staticmethod
	@typing.overload
	def New(direction: vspyx.Runtime.Point.Direction, upstreamPoints: typing.List[vspyx.Runtime.Point], controller: vspyx.Communication.CANController, frame: vspyx.Communication.CANFrame, data: vspyx.Core.BytesView, arbID: typing.Any, isCANFD: typing.Any, baudrateSwitch: typing.Any) -> vspyx.Runtime.Point.Consuming_1dd119a6a6: ...


	@staticmethod
	@typing.overload
	def New(direction: vspyx.Runtime.Point.Direction, upstreamPoints: typing.List[vspyx.Runtime.Point], controller: vspyx.Communication.CANController, frame: vspyx.Communication.CANFrame, data: vspyx.Core.BytesView, arbID: typing.Any, isCANFD: typing.Any, baudrateSwitch: typing.Any, isExtended: typing.Any) -> vspyx.Runtime.Point.Consuming_1dd119a6a6: ...


	@staticmethod
	@typing.overload
	def New(direction: vspyx.Runtime.Point.Direction, upstreamPoints: typing.List[vspyx.Runtime.Point], controller: vspyx.Communication.CANController, frame: vspyx.Communication.CANFrame, data: vspyx.Core.BytesView, arbID: typing.Any, isCANFD: typing.Any, baudrateSwitch: typing.Any, isExtended: typing.Any, dlc: typing.Any) -> vspyx.Runtime.Point.Consuming_1dd119a6a6: ...


	@staticmethod
	@typing.overload
	def New(direction: vspyx.Runtime.Point.Direction, upstreamPoints: typing.List[vspyx.Runtime.Point], controller: vspyx.Communication.CANController, frame: vspyx.Communication.CANFrame, data: vspyx.Core.BytesView, arbID: typing.Any, isCANFD: typing.Any, baudrateSwitch: typing.Any, isExtended: typing.Any, dlc: typing.Any, isRemote: typing.Any) -> vspyx.Runtime.Point.Consuming_1dd119a6a6: ...


	@staticmethod
	@typing.overload
	def New(direction: vspyx.Runtime.Point.Direction, controller: vspyx.Communication.CANController, arbID: int, data: vspyx.Core.BytesView) -> vspyx.Runtime.Point.Consuming_1dd119a6a6:
		"""Create a CANFramePoint not associated with a Traceable.
		This is useful for creating points to send down.

		"""
		pass



	@staticmethod
	@typing.overload
	def New(direction: vspyx.Runtime.Point.Direction, controller: vspyx.Communication.CANController, arbID: int, data: vspyx.Core.BytesView, isCANFD: bool) -> vspyx.Runtime.Point.Consuming_1dd119a6a6:
		"""Create a CANFramePoint not associated with a Traceable.
		This is useful for creating points to send down.

		"""
		pass



	@staticmethod
	@typing.overload
	def New(direction: vspyx.Runtime.Point.Direction, controller: vspyx.Communication.CANController, arbID: int, data: vspyx.Core.BytesView, isCANFD: bool, baudrateSwitch: bool) -> vspyx.Runtime.Point.Consuming_1dd119a6a6:
		"""Create a CANFramePoint not associated with a Traceable.
		This is useful for creating points to send down.

		"""
		pass



	@staticmethod
	@typing.overload
	def New(direction: vspyx.Runtime.Point.Direction, controller: vspyx.Communication.CANController, arbID: int, data: vspyx.Core.BytesView, isCANFD: bool, baudrateSwitch: bool, isExtended: typing.Any) -> vspyx.Runtime.Point.Consuming_1dd119a6a6:
		"""Create a CANFramePoint not associated with a Traceable.
		This is useful for creating points to send down.

		"""
		pass



	@staticmethod
	@typing.overload
	def New(direction: vspyx.Runtime.Point.Direction, controller: vspyx.Communication.CANController, arbID: int, data: vspyx.Core.BytesView, isCANFD: bool, baudrateSwitch: bool, isExtended: typing.Any, dlc: typing.Any) -> vspyx.Runtime.Point.Consuming_1dd119a6a6:
		"""Create a CANFramePoint not associated with a Traceable.
		This is useful for creating points to send down.

		"""
		pass



	@staticmethod
	@typing.overload
	def New(direction: vspyx.Runtime.Point.Direction, controller: vspyx.Communication.CANController, arbID: int, data: vspyx.Core.BytesView, isCANFD: bool, baudrateSwitch: bool, isExtended: typing.Any, dlc: typing.Any, isRemote: bool) -> vspyx.Runtime.Point.Consuming_1dd119a6a6:
		"""Create a CANFramePoint not associated with a Traceable.
		This is useful for creating points to send down.

		"""
		pass


class FrameTriggering(vspyx.Communication.Triggering):
	"""FrameTriggering describes the instance of a frame sent on a channel and defines the manner of
	 triggering (timing information) and identification of a frame on the channel, on which it is sent.
	 
	"""
	"""FrameTriggering
	"""
	Frame: vspyx.Communication.Frame

class CANFrameTriggering(vspyx.Communication.FrameTriggering):
	"""Represents the timing and channel identification info relating to a transmitted CAN frame
	"""
	"""CANFrameTriggering
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.CANFrameTriggering: ...

	def CloneConfiguration(self) -> typing.Any: ...

class CPPImplementationDataType(vspyx.Communication.AUTOSARDataType):
	"""CPPImplementationDataType
	"""
	Category: str

class CPPImplementationDataTypeElement(vspyx.Runtime.Traceable):
	"""CPPImplementationDataTypeElement
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.CPPImplementationDataTypeElement: ...

	def CloneConfiguration(self) -> typing.Any: ...

class PDUInstance:
	"""An instance of PDU that is being processed by the Communication module.
	 This class is short-lived, and referencing it outside of the immediate callback
	 may result in unpredictable behavior.
	 
	"""
	"""PDUInstance
	"""
	Bytes: vspyx.Core.BytesView

class Component(vspyx.Runtime.Component):
	"""Represents a basic runtime component within the Communication runtime domain
	"""
	"""Component
	"""

	@staticmethod
	def New(sources: vspyx.Core.ResolverCollection, topology: vspyx.Communication.Topology) -> vspyx.Communication.Component: ...

class PDU(vspyx.Runtime.Traceable):
	"""A collection of bytes moved throughout the Communication Stack.
	 
	 Short for "Protocol Data Unit"
	 
	"""
	"""PDU
	"""
	Category: str
	Length: int
	"""The defined length of the PDU
		 
	"""

class IPDU(vspyx.Communication.PDU):
	"""IPDU represents any type of PDU that the Communication system can interact with
	 
	"""
	"""IPDU
	"""

class ContainerIPDUPoint(vspyx.Communication.PDUPoint):
	"""ContainerIPDUPoint
	"""

class ContainerIPDU(vspyx.Communication.IPDU):
	"""Represents a communication container PDU, defined to contain other PDUs
	"""
	"""ContainerIPDU
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.ContainerIPDU: ...

	def CloneConfiguration(self) -> typing.Any: ...

class DBC(vspyx.Communication.TopologySubset):
	"""Represents the CANdbc network topology and message specification
	"""
	"""DBC
	"""
	Objects: vspyx.Core.ResolverOwningCollection

class DataTransformation(vspyx.Core.ResolverObject):
	"""DataTransformation
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.DataTransformation: ...

	def CloneConfiguration(self) -> typing.Any: ...

class DataTransformationSet(vspyx.Core.ResolverObject):
	"""DataTransformationSet
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	def AddChild(self, child: vspyx.Core.ResolverObject) -> typing.Any: ...


	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.DataTransformationSet: ...

	def CloneConfiguration(self) -> typing.Any: ...

class DatagramPoint(vspyx.Communication.PDUPoint):
	"""A PDUPoint that also holds a header of bytes
	 
	"""
	"""DatagramPoint
	"""
	def GetHeader(self) -> vspyx.Core.BytesView: ...

	def GetAttribute(self, type: vspyx.Core.Tag) -> vspyx.Runtime.Value: ...

	def SetAttribute(self, type: vspyx.Core.Tag, value: vspyx.Runtime.Value) -> bool: ...

class DiagnosticIPDU(vspyx.Communication.IPDU):
	"""Represents a diagnostics communication PDU
	"""
	"""DiagnosticIPDU
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.DiagnosticIPDU: ...

	def CloneConfiguration(self) -> typing.Any: ...

class TransformationTechnology(vspyx.Core.ResolverObject):
	"""TransformationTechnology
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.TransformationTechnology: ...

	def CloneConfiguration(self) -> typing.Any: ...

class TransformationTechnology_EndToEnd(vspyx.Communication.TransformationTechnology):
	"""TransformationTechnology_EndToEnd
	"""

class TransformationTechnology_SOMEIP(vspyx.Communication.TransformationTechnology):
	"""TransformationTechnology_SOMEIP
	"""

class TransformationTechnologyConfig:
	"""TransformationTechnologyConfig
	"""
	ID: str
	Transform: vspyx.Communication.TransformationTechnology

class TransformationTechnologyConfig_EndToEnd(vspyx.Communication.TransformationTechnologyConfig):
	"""TransformationTechnologyConfig_EndToEnd
	"""
	DataIds: typing.List[int]
	DataLength: typing.Any
	MaxDataLength: typing.Any
	MinDataLength: typing.Any
	SourceId: typing.Any

class TransformationTechnologyConfig_SOMEIP(vspyx.Communication.TransformationTechnologyConfig):
	"""TransformationTechnologyConfig_SOMEIP
	"""

class ISignalPoint(vspyx.Runtime.SignalPoint):
	"""ISignalPoint
	"""
	Unit: vspyx.Runtime.Unit
	UnitString: str

class ISignal(vspyx.Runtime.Signal):
	"""Signal of the Communication system
	 
	"""
	"""ISignal
	"""
	CompuMethod: vspyx.Runtime.CompuMethod
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	SystemSignal: vspyx.Runtime.SystemSignal
	TargetDataType: typing.Any
	TransformationConfig: vspyx.Communication.TransformationTechnologyConfig
	def NewPoint(self, direction: vspyx.Runtime.Point.Direction, upstreamPoints: typing.List[vspyx.Runtime.Point], physicalValue: typing.Any, unit: vspyx.Runtime.Unit, internalValue: typing.Any, valid: bool) -> vspyx.Runtime.Point.Consuming_e473ff5c76: ...

	def NewTxPoint(self, physicalValue: typing.Any) -> vspyx.Runtime.Point.Consuming_e473ff5c76:
		"""Equivalent to NewPoint(vspyx.Runtime.Point.Direction.Transmit,
		[], physicalValue, '', None, True), this is a shortcut method
		to create a Point for transmitting.

		"""
		pass



	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.ISignal: ...

	def CloneConfiguration(self) -> typing.Any: ...

class ISignalGroupPoint(vspyx.Runtime.Point):
	"""ISignalGroupPoint
	"""
	Valid: bool

class ISignalGroup(vspyx.Runtime.Traceable):
	"""Represents a group of related communication signals
	 
	"""
	"""ISignalGroup
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	SystemSignalGroup: vspyx.Runtime.SystemSignalGroup
	TransformationConfig: vspyx.Communication.TransformationTechnologyConfig
	def NewPoint(self, direction: vspyx.Runtime.Point.Direction, upstreamPoints: typing.List[vspyx.Runtime.Point], valid: bool) -> vspyx.Runtime.Point.Consuming_e1c4fc4e95: ...


	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.ISignalGroup: ...

	def CloneConfiguration(self) -> typing.Any: ...

class ISignalToIPDUMapping(vspyx.Core.ResolverObject):
	"""ISignalToIPDUMapping
	"""
	ByteOrder: vspyx.Core.Codec.Endian
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	Signal: typing.Any
	StartPosition: int
	TargetDataType: typing.Any
	TransformationConfig: vspyx.Communication.TransformationTechnologyConfig
	Trigger: vspyx.Runtime.Trigger
	VariableDataPrototype: vspyx.Runtime.VariableDataPrototype

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.ISignalToIPDUMapping: ...

	def CloneConfiguration(self) -> typing.Any: ...

class ISignalIPDUPoint(vspyx.Communication.PDUPoint):
	"""Represents the translation between a signal-based PDU and a PDU point
	"""
	"""ISignalIPDUPoint
	"""

	@staticmethod
	def New(direction: vspyx.Runtime.Point.Direction, upstreamPoints: typing.List[vspyx.Runtime.Point], traceable: vspyx.Runtime.Traceable, data: vspyx.Core.BytesView) -> vspyx.Runtime.Point.Consuming_2215b345f6: ...

@enum.unique
class DataFilterTypes(enum.IntEnum):
	Always = 0
	MaskedNewDiffersMaskedOld = 1
	MaskedNewDiffersX = 2
	MaskedNewEqualsX = 3
	Never = 4
	NewIsOutside = 5
	NewIsWithin = 6
	OneEveryN = 7
	Unknown = 255

class TransmissionModeCondition:
	"""TransmissionModeCondition
	"""
	FilterType: vspyx.Communication.DataFilterTypes
	Mapping: vspyx.Communication.ISignalToIPDUMapping
	def assign(self, arg0: vspyx.Communication.TransmissionModeCondition) -> vspyx.Communication.TransmissionModeCondition: ...

class IPDUTiming(vspyx.Core.ResolverObject):
	"""IPDUTiming
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.IPDUTiming: ...

	def CloneConfiguration(self) -> typing.Any: ...

class ISignalIPDU(vspyx.Communication.IPDU):
	"""Signal-based PDU
	 
	"""
	"""ISignalIPDU
	"""
	ISignalToIPDUMapping: vspyx.Communication.ISignalToIPDUMapping
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	Timing: vspyx.Communication.IPDUTiming
	UnusedBitPattern: int
	def NewPoint(self, direction: vspyx.Runtime.Point.Direction, upstreamPoints: typing.List[vspyx.Runtime.Point], data: vspyx.Core.BytesView) -> vspyx.Runtime.Point.Consuming_2215b345f6: ...

	def Decode(self, value: typing.List[int]) -> typing.Any: ...


	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.ISignalIPDU: ...

	def CloneConfiguration(self) -> typing.Any: ...

class ECU(vspyx.Communication.Architecture):
	"""ECU describes the presence of a microcontroller in the vehicle. 
	 
	"""
	"""ECU
	"""
	@enum.unique
	class SOMEIPComplianceItems(enum.IntEnum):
		constr_5326 = 0

	Connectors: vspyx.Core.ResolverCollection
	Controllers: vspyx.Core.ResolverCollection
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	OwnedConnectors: vspyx.Core.ResolverOwningCollection
	OwnedControllers: vspyx.Core.ResolverOwningCollection
	SOMEIPInterfaces: typing.List[vspyx.SOMEIP.HostInterface]
	Transmits: vspyx.Core.ResolverOwningCollection

	@staticmethod
	@typing.overload
	def New() -> vspyx.Communication.ECU: ...

	def Initialize(self, app: vspyx.Core.Application, id: str, uuid: typing.Any, params: vspyx.Core.Serialization.CreationParameters) -> typing.Any: ...

	def ComponentStart(self) -> typing.Any: ...

	def ComponentStop(self) -> typing.Any: ...

	def AddTransmit(self, transmit: vspyx.Scripting.FunctionBlock) -> typing.Any: ...

	def SetMode(self, newMode: vspyx.intrepidcs.vspyx.rpc.Communication.ECUMode) -> typing.Any:
		"""Set the mode for this ECU. This will update the ECU configuration.

		A mode of `ECU::Mode::Disabled` is equivalent to a real-world ECU completely powered off.

		A mode of `ECU::Mode::Passive` allows the ECU to receive messages, but the ECU will not interact
		with the network in any way. This may be useful if the real-world ECU is powered on, but you wish
		to use the perspective of this ECU.

		A mode of `ECU::Mode::Active` attempts to emulate the real-world ECU as closely as possible.
		It will respond to messages and periodically transmit the messages that the real ECU would, if defined.

		"""
		pass



	@typing.overload
	def SetSignal(self, signalResolverLookup: str, physicalValue: typing.Any) -> typing.Any: ...


	@typing.overload
	def SetSignal(self, signal: vspyx.Communication.ISignal, physicalValue: typing.Any) -> typing.Any: ...


	@typing.overload
	def SendSignalGroup(self, signalGroupResolverLookup: str) -> typing.Any: ...


	@typing.overload
	def SendSignalGroup(self, signalGroup: vspyx.Communication.ISignalGroup) -> typing.Any: ...


	@typing.overload
	def TriggerIPDUSend(self, signalPduResolverLookup: str) -> typing.Any: ...


	@typing.overload
	def TriggerIPDUSend(self, signalPdu: vspyx.Communication.ISignalIPDU) -> typing.Any: ...

	def SetSOMEIPCompliance(self, item: vspyx.Communication.ECU.SOMEIPComplianceItems, comply: bool) -> typing.Any: ...

	def GetSOMEIPCompliance(self, item: vspyx.Communication.ECU.SOMEIPComplianceItems) -> bool: ...

	def ConfigureSOMEIP(self) -> typing.Any: ...

	def ConnectToChannel(self, channel: vspyx.Communication.Channel, listenOnly: bool) -> typing.Any:
		"""Create a new ECU-owned controller and connector, connecting
		this ECU to the provided Channel.

		:Parameter listenOnly: Create the controller with parameters such
		that it will not influence the channel (ACKs, transmits, etc.)

		"""
		pass


	def GetProvidedService(self, name: str) -> vspyx.SOMEIP.EventService: ...

	def GetConsumedService(self, name: str) -> vspyx.SOMEIP.EventService: ...

	def SuppressSOMEIPScheduler(self, tf: bool) -> typing.Any: ...


	@staticmethod
	@typing.overload
	def New(config: typing.Any) -> vspyx.Communication.ECU: ...

	def CloneConfiguration(self) -> typing.Any: ...

class EthernetCluster(vspyx.Communication.Cluster):
	"""EthernetCluster
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	@typing.overload
	def New() -> vspyx.Communication.EthernetCluster: ...


	@staticmethod
	@typing.overload
	def New(config: typing.Any) -> vspyx.Communication.EthernetCluster: ...

	def CloneConfiguration(self) -> typing.Any: ...

class NetworkEndpoint(vspyx.Core.ResolverObject):
	"""An object defining the network addressing for an endpoint
	 (such as an ECU).
	 
	"""
	"""NetworkEndpoint
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	def ConfigureStack(self, stack: vspyx.Communication.Stack, ctrl: vspyx.Communication.Controller, listenOnly: bool) -> typing.Any: ...

	def Network(self) -> vspyx.TCPIP.Network: ...


	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.NetworkEndpoint: ...

	def CloneConfiguration(self) -> typing.Any: ...

class EthernetConnector(vspyx.Communication.Connector):
	"""EthernetConnector
	"""
	EthernetController: vspyx.Communication.EthernetController
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.EthernetConnector: ...

	def CloneConfiguration(self) -> typing.Any: ...

	def CloneState(self) -> typing.Any: ...

	def UpdateState(self, state: typing.Any) -> typing.Any: ...

class EthernetController(vspyx.Communication.Controller):
	"""EthernetController
	"""
	MACAddress: str
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.EthernetController: ...

	def CloneConfiguration(self) -> typing.Any: ...

class EthernetDiscoveryProcessor(vspyx.Communication.PointProcessor):
	"""EthernetDiscoveryProcessor
	"""

	@staticmethod
	def New() -> vspyx.Communication.EthernetDiscoveryProcessor: ...

class EthernetFrame(vspyx.Communication.Frame):
	"""EthernetFrame
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.EthernetFrame: ...

	def CloneConfiguration(self) -> typing.Any: ...

class EthernetFrameTriggering(vspyx.Communication.FrameTriggering):
	"""EthernetFrameTriggering
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.EthernetFrameTriggering: ...

	def CloneConfiguration(self) -> typing.Any: ...

class Field(vspyx.Communication.AUTOSARDataPrototype):
	"""Field
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.Field: ...

	def CloneConfiguration(self) -> typing.Any: ...

class FlexRayBufferUpdatePoint(vspyx.Communication.BufferUpdatePoint):
	"""FlexRayBufferUpdatePoint
	"""

class FlexRayChannel(vspyx.Communication.Channel):
	"""FlexRayChannel
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	@typing.overload
	def New() -> vspyx.Communication.FlexRayChannel: ...


	@staticmethod
	@typing.overload
	def New(config: typing.Any) -> vspyx.Communication.FlexRayChannel: ...

	def CloneConfiguration(self) -> typing.Any: ...

	def CloneState(self) -> typing.Any: ...

	def UpdateState(self, state: typing.Any) -> typing.Any: ...

class FlexRayCluster(vspyx.Communication.Cluster):
	"""FlexRayCluster
	"""
	GlobalConfiguration: vspyx.Frames.FlexRayClusterConfiguration
	"""The configuration which is shared by every CC in the cluster.
	 
	 This value is read-only and can only be changed by modifying the protobuf configuration of the cluster.
		 
	"""

	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	@typing.overload
	def New() -> vspyx.Communication.FlexRayCluster: ...


	@staticmethod
	@typing.overload
	def New(config: typing.Any) -> vspyx.Communication.FlexRayCluster: ...

	def CloneConfiguration(self) -> typing.Any: ...

class FlexRayConnector(vspyx.Communication.Connector):
	"""FlexRayConnector
	"""
	FlexRayController: vspyx.Communication.FlexRayController
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.FlexRayConnector: ...

	def CloneConfiguration(self) -> typing.Any: ...

	def CloneState(self) -> typing.Any: ...

	def UpdateState(self, state: typing.Any) -> typing.Any: ...

class FlexRayController(vspyx.Communication.Controller):
	"""FlexRayController
	"""
	AllowColdstart: bool
	CCConfiguration: vspyx.Frames.FlexRayCCConfiguration
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	StartWhenGoingOnline: bool
	WakeupBeforeStart: bool
	def Start(self) -> typing.Any: ...

	def Halt(self) -> typing.Any: ...


	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.FlexRayController: ...

	def CloneConfiguration(self) -> typing.Any: ...

class FlexRayDataLinkPDUPoint(vspyx.Communication.DataLinkPDUPoint):
	"""FlexRayDataLinkPDUPoint
	"""

class FlexRayDiscoveryProcessor(vspyx.Communication.PointProcessor):
	"""FlexRayDiscoveryProcessor
	"""

	@staticmethod
	def New() -> vspyx.Communication.FlexRayDiscoveryProcessor: ...

class FlexRayFrame(vspyx.Communication.Frame):
	"""FlexRayFrame
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.FlexRayFrame: ...

	def CloneConfiguration(self) -> typing.Any: ...

class FlexRayFrameTriggering(vspyx.Communication.FrameTriggering):
	"""FlexRayFrameTriggering
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.FlexRayFrameTriggering: ...

	def CloneConfiguration(self) -> typing.Any: ...

class FramePort(vspyx.Communication.ConnectorPort):
	"""FramePort
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.FramePort: ...

	def CloneConfiguration(self) -> typing.Any: ...

class GeneralPurposeIPDU(vspyx.Communication.IPDU):
	"""Represents a general purpose interaction PDU used for XCP, SOME/IP segments, or DLT
	 
	"""
	"""GeneralPurposeIPDU
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	@typing.overload
	def New() -> vspyx.Communication.GeneralPurposeIPDU: ...


	@staticmethod
	@typing.overload
	def New(config: typing.Any) -> vspyx.Communication.GeneralPurposeIPDU: ...

	def CloneConfiguration(self) -> typing.Any: ...

class GeneralPurposePDU(vspyx.Communication.PDU):
	"""Represents a general purpose PDU used for DoIP, service discovery, or global timing
	 
	"""
	"""GeneralPurposePDU
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	@typing.overload
	def New() -> vspyx.Communication.GeneralPurposePDU: ...


	@staticmethod
	@typing.overload
	def New(config: typing.Any) -> vspyx.Communication.GeneralPurposePDU: ...

	def CloneConfiguration(self) -> typing.Any: ...

class IPDUPort(vspyx.Communication.ConnectorPort):
	"""Represents the PDU-specific triggered data binding related to a transmitted PDU
	"""
	"""IPDUPort
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.IPDUPort: ...

	def CloneConfiguration(self) -> typing.Any: ...

class ISOStandardizedServicePrimitiveInterface:
	"""Represents the generic ISO service handling function framework
	"""
	"""ISOStandardizedServicePrimitiveInterface
	"""
	@enum.unique
	class MessageType(enum.IntEnum):
		Diagnostics = 0
		RemoteDiagnostics = 1
		SecureDiagnostics = 2
		SecureRemoteDiagnostics = 3

	@enum.unique
	class TransportResult(enum.IntEnum):
		T_OK = 0

	TData_SOM_indication: vspyx.Core.Callback_023e2a5056
	TData_SOM_indicationSupported: bool
	TData_confirm: vspyx.Core.Callback_9d4c23c9b0
	TData_indication: vspyx.Core.Callback_bac0b1ebba
	def TData_request(self, Mtype: vspyx.Communication.ISOStandardizedServicePrimitiveInterface.MessageType, T_SA: int, T_TA: int, T_TAtype: int, T_AE: typing.Any, T_Data: vspyx.Core.BytesView, Length: int) -> typing.Any: ...

	def T_TAtypeIsFunctional(self, TAtype: int) -> bool: ...

	def T_TAtypeIsPhysical(self, TAtype: int) -> bool: ...

	def GetT_TAtype(self, messageType: vspyx.Communication.ISOStandardizedServicePrimitiveInterface.MessageType, sa: int, ta: int, ae: typing.Any, isFunctional: typing.Any) -> int: ...


	@staticmethod
	def DebugLogPDU(tag: str, prefix: str, Mtype: vspyx.Communication.ISOStandardizedServicePrimitiveInterface.MessageType, SA: int, TA: int, TAtype: int, AE: typing.Any, Data: typing.Any, rte: vspyx.Runtime.Scheduler) -> typing.Any: ...

class ISOStandardizedServicePrimitiveInterfaceTrampoline(vspyx.Communication.ISOStandardizedServicePrimitiveInterface, vspyx.Runtime.Component):
	"""Represents the functional implementation of a generic ISO service handler
	"""
	"""ISOStandardizedServicePrimitiveInterfaceTrampoline
	"""
	GetT_TAtype_trampoline: vspyx.Core.Function_16f83113e6
	TData_SOM_indication: vspyx.Core.Callback_023e2a5056
	TData_SOM_indicationSupported: bool
	TData_SOM_indicationSupported_trampoline: vspyx.Core.Function_32dce94434
	TData_confirm: vspyx.Core.Callback_9d4c23c9b0
	TData_indication: vspyx.Core.Callback_bac0b1ebba
	TData_request_trampoline: vspyx.Core.Function_633e09e382
	T_TAtypeIsFunctional_trampoline: vspyx.Core.Function_3ca61a3473
	T_TAtypeIsPhysical_trampoline: vspyx.Core.Function_3ca61a3473
	def TData_request(self, Mtype: vspyx.Communication.ISOStandardizedServicePrimitiveInterface.MessageType, T_SA: int, T_TA: int, T_TAtype: int, T_AE: typing.Any, T_Data: vspyx.Core.BytesView, Length: int) -> typing.Any: ...

	def T_TAtypeIsFunctional(self, TAtype: int) -> bool: ...

	def T_TAtypeIsPhysical(self, TAtype: int) -> bool: ...

	def GetT_TAtype(self, messageType: vspyx.Communication.ISOStandardizedServicePrimitiveInterface.MessageType, sa: int, ta: int, ae: typing.Any, isFunctional: typing.Any) -> int: ...

class ISO15765_2(vspyx.Communication.ISOStandardizedServicePrimitiveInterface, vspyx.Runtime.Component):
	"""Represents the functional implementation of the ISO-15765-2 transport protocol
	"""
	"""ISO15765_2
	"""
	@enum.unique
	class NetworkAddressType(enum.IntEnum):
		PhysicalClassicalCAN11Bit = 1
		FunctionalClassicalCAN11Bit = 2
		PhysicalCANFD11Bit = 3
		FunctionalCANFD11Bit = 4
		PhysicalClassicalCAN29Bit = 5
		FunctionalClassicalCAN29Bit = 6
		PhysicalCANFD29Bit = 7
		FunctionalCANFD29Bit = 8

	@enum.unique
	class Result(enum.IntEnum):
		N_OK = 0
		N_TIMEOUT_A = 1
		N_TIMEOUT_Bs = 2
		N_TIMEOUT_Cr = 3
		N_WRONG_SN = 4
		N_INVALID_FS = 5
		N_UNEXP_PDU = 6
		N_WFT_OVRN = 7
		N_BUFFER_OVFLW = 8
		N_ERROR = 9

	@enum.unique
	class Parameters(enum.IntEnum):
		ST_min = 0
		BS = 1
		Passive = 2
		PassiveStrictFC = 3

	@enum.unique
	class ChangeParametersResult(enum.IntEnum):
		N_OK = 0
		N_RX_ON = 1
		N_WRONG_PARAMETER = 2
		N_WRONG_VALUE = 3
		N_TX_ON = 4

	@enum.unique
	class Addressing(enum.IntEnum):
		Normal = 0
		Extended = 1
		Mixed = 2

	@enum.unique
	class FlowStatus(enum.IntEnum):
		ContinueToSend = 0
		Wait = 1
		Overflow = 2

	N_ChangeParameters_confirm: vspyx.Core.Callback_a72caefd1b
	N_USData_FF_indication: vspyx.Core.Callback_023e2a5056
	N_USData_confirm: vspyx.Core.Callback_9d4c23c9b0
	N_USData_indication: vspyx.Core.Callback_bac0b1ebba
	OnCANFrameRx: vspyx.Core.Callback_2ddc052380
	OnCANFrameTx: vspyx.Core.Callback_2ddc052380
	OnCFN_PDU: vspyx.Core.Callback_4318dcd5f2
	OnFCN_PDU: vspyx.Core.Callback_caf226155c
	OnFFN_PDU: vspyx.Core.Callback_76273522fe
	OnSFN_PDU: vspyx.Core.Callback_5eaebb1942
	TrackedL_Data_Request: vspyx.Core.Callback_04759c7c12
	TrackedN_USData_indication: vspyx.Core.Callback_294047f9ec

	@typing.overload
	def N_USData_request(self, Mtype: vspyx.Communication.ISOStandardizedServicePrimitiveInterface.MessageType, N_SA: int, N_TA: int, N_TAtype: int, N_AE: typing.Any, MessageData: vspyx.Core.BytesView, Length: int) -> typing.Any: ...


	@typing.overload
	def N_USData_request(self, Mtype: vspyx.Communication.ISOStandardizedServicePrimitiveInterface.MessageType, N_SA: int, N_TA: int, N_TAtype: int, N_AE: typing.Any, MessageData: vspyx.Core.BytesView, Length: int, consuming: vspyx.Runtime.Point.Consuming_1edf1860a4) -> typing.Any: ...

	def N_ChangeParameters_request(self, Mtype: vspyx.Communication.ISOStandardizedServicePrimitiveInterface.MessageType, N_SA: int, N_TA: int, N_TAtype: int, N_AE: typing.Any, Parameter: vspyx.Communication.ISO15765_2.Parameters, Parameter_Value: int) -> vspyx.Communication.ISO15765_2.ChangeParametersResult: ...


	@staticmethod
	@typing.overload
	def New(TX_DL: int) -> vspyx.Communication.ISO15765_2: ...


	@staticmethod
	@typing.overload
	def New(TX_DL: int, padding: typing.Any) -> vspyx.Communication.ISO15765_2: ...


	@staticmethod
	@typing.overload
	def New(TX_DL: int, padding: typing.Any, N_WFTmax: int) -> vspyx.Communication.ISO15765_2: ...


	@staticmethod
	@typing.overload
	def New(TX_DL: int, padding: typing.Any, N_WFTmax: int, receiveBufferSize: int) -> vspyx.Communication.ISO15765_2: ...

	def Attach(self, L_Data: vspyx.Communication.ISO11898.ISO11898_1Interface) -> typing.Any: ...

	def Detach(self) -> typing.Any: ...


	@typing.overload
	def L_Data_Indication(self, Identifier: int, format: vspyx.Communication.ISO11898.FrameFormats, DLC: int, Data: vspyx.Core.BytesView) -> typing.Any: ...


	@typing.overload
	def L_Data_Indication(self, Identifier: int, format: vspyx.Communication.ISO11898.FrameFormats, DLC: int, Data: vspyx.Core.BytesView, consuming: vspyx.Runtime.Point.Consuming_1edf1860a4) -> typing.Any: ...


	@typing.overload
	def L_Data_Confirm(self, Identifier: int, Transfer_Status: vspyx.Communication.ISO11898.TransferStatuses) -> typing.Any: ...


	@typing.overload
	def L_Data_Confirm(self, Identifier: int, Transfer_Status: vspyx.Communication.ISO11898.TransferStatuses, consuming: vspyx.Runtime.Point.Consuming_1edf1860a4) -> typing.Any: ...

	def AddRxNormalAddress(self, Mtype: vspyx.Communication.ISOStandardizedServicePrimitiveInterface.MessageType, N_SA: int, N_SA_CANID: int, N_SAtype: vspyx.Communication.ISO15765_2.NetworkAddressType, N_TA: int, N_TA_CANID: int, N_TAtype: vspyx.Communication.ISO15765_2.NetworkAddressType, N_AE: typing.Any, stMin: int, bs: int) -> typing.Any: ...

	def AddRxExtendedAddress(self, Mtype: vspyx.Communication.ISOStandardizedServicePrimitiveInterface.MessageType, N_SA: int, N_SA_CANID: int, N_SAtype: vspyx.Communication.ISO15765_2.NetworkAddressType, N_TA: int, N_TA_CANID: int, N_TAtype: vspyx.Communication.ISO15765_2.NetworkAddressType, N_AE: typing.Any, stMin: int, bs: int) -> typing.Any: ...

	def AddRxFixedAddress(self, Mtype: vspyx.Communication.ISOStandardizedServicePrimitiveInterface.MessageType, N_SA: int, N_TA: int, N_TAtype: vspyx.Communication.ISO15765_2.NetworkAddressType, N_AE: typing.Any, j1939: bool, stMin: int, bs: int) -> typing.Any: ...

	def AddTxNormalAddress(self, Mtype: vspyx.Communication.ISOStandardizedServicePrimitiveInterface.MessageType, N_SA: int, N_SA_CANID: int, N_SAtype: vspyx.Communication.ISO15765_2.NetworkAddressType, N_TA: int, N_TA_CANID: int, N_TAtype: vspyx.Communication.ISO15765_2.NetworkAddressType, N_AE: typing.Any, stMinMin: typing.Any) -> typing.Any: ...

	def AddTxExtendedAddress(self, Mtype: vspyx.Communication.ISOStandardizedServicePrimitiveInterface.MessageType, N_SA: int, N_SA_CANID: int, N_SAtype: vspyx.Communication.ISO15765_2.NetworkAddressType, N_TA: int, N_TA_CANID: int, N_TAtype: vspyx.Communication.ISO15765_2.NetworkAddressType, N_AE: typing.Any, stMinMin: typing.Any) -> typing.Any: ...

	def AddTxFixedAddress(self, Mtype: vspyx.Communication.ISOStandardizedServicePrimitiveInterface.MessageType, N_SA: int, N_TA: int, N_TAtype: vspyx.Communication.ISO15765_2.NetworkAddressType, N_AE: typing.Any, j1939: bool, stMinMin: typing.Any) -> typing.Any: ...

	def RemoveAddress(self, Mtype: vspyx.Communication.ISOStandardizedServicePrimitiveInterface.MessageType, N_SA: int, N_TA: int, N_TAtype: vspyx.Communication.ISO15765_2.NetworkAddressType, N_AE: typing.Any) -> typing.Any: ...

	def RemoveAllAddresses(self) -> typing.Any: ...


	@staticmethod
	def FrameFormatFromNetworkAddressType(nat: vspyx.Communication.ISO15765_2.NetworkAddressType) -> vspyx.Communication.ISO11898.FrameFormats: ...


	@staticmethod
	def MakeNetworkAddressType(frameFormat: vspyx.Communication.ISO11898.FrameFormats, functional: bool) -> vspyx.Communication.ISO15765_2.NetworkAddressType: ...


	@staticmethod
	def NetworkAddressTypeIsFunctional(nat: vspyx.Communication.ISO15765_2.NetworkAddressType) -> bool: ...

class ISO15765_2Processor(vspyx.Communication.PointProcessor, vspyx.Communication.ISOStandardizedServicePrimitiveInterface):
	"""Represents the signal point processor related to ISO-15765 signals
	"""
	"""ISO15765_2Processor
	"""
	Interface: vspyx.Communication.ISO15765_2

	@staticmethod
	def New(interface: vspyx.Communication.ISO15765_2) -> vspyx.Communication.ISO15765_2Processor: ...

class TDataPoint(vspyx.Communication.PDUPoint):
	"""TDataPoint
	"""
	Mtype: vspyx.Communication.ISOStandardizedServicePrimitiveInterface.MessageType
	N_AI: typing.Any
	N_Result: typing.Any
	T_AE: typing.Any
	T_SA: int
	T_TA: int
	T_TAtype: int

	@staticmethod
	def New(direction: vspyx.Runtime.Point.Direction, upstreamPoints: typing.List[vspyx.Runtime.Point], controller: vspyx.Communication.Controller, traceable: vspyx.Runtime.Traceable, Mtype: vspyx.Communication.ISOStandardizedServicePrimitiveInterface.MessageType, T_SA: int, T_TA: int, T_TAtype: int, T_AE: typing.Any, T_Data: vspyx.Core.BytesView, N_Result: typing.Any) -> vspyx.Runtime.Point.Consuming_fe9efbf398: ...

class ISignalIPDUGroup(vspyx.Core.ResolverObject):
	"""Group of Signal-based PDUs
	 
	"""
	"""ISignalIPDUGroup
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.ISignalIPDUGroup: ...

	def CloneConfiguration(self) -> typing.Any: ...

class ISignalPort(vspyx.Communication.ConnectorPort):
	"""ISignalPort
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.ISignalPort: ...

	def CloneConfiguration(self) -> typing.Any: ...

class ISignalTriggering(vspyx.Communication.Triggering):
	"""ISignalTriggering
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	Trigger: typing.Any

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.ISignalTriggering: ...

	def CloneConfiguration(self) -> typing.Any: ...

class LINChannel(vspyx.Communication.Channel):
	"""LINChannel
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	@typing.overload
	def New() -> vspyx.Communication.LINChannel: ...


	@staticmethod
	@typing.overload
	def New(config: typing.Any) -> vspyx.Communication.LINChannel: ...

	def CloneConfiguration(self) -> typing.Any: ...

	def CloneState(self) -> typing.Any: ...

	def UpdateState(self, state: typing.Any) -> typing.Any: ...

class LINCluster(vspyx.Communication.Cluster):
	"""LINCluster
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	@typing.overload
	def New() -> vspyx.Communication.LINCluster: ...


	@staticmethod
	@typing.overload
	def New(config: typing.Any) -> vspyx.Communication.LINCluster: ...

	def CloneConfiguration(self) -> typing.Any: ...

class LINController(vspyx.Communication.Controller):
	"""LINController
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.LINController: ...

	def CloneConfiguration(self) -> typing.Any: ...

class LINConnector(vspyx.Communication.Connector):
	"""LINConnector
	"""
	LINController: vspyx.Communication.LINController
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.LINConnector: ...

	def CloneConfiguration(self) -> typing.Any: ...

	def CloneState(self) -> typing.Any: ...

	def UpdateState(self, state: typing.Any) -> typing.Any: ...

class LINDiscoveryProcessor(vspyx.Communication.PointProcessor):
	"""LINDiscoveryProcessor
	"""

	@staticmethod
	def New() -> vspyx.Communication.LINDiscoveryProcessor: ...

class LINFrameTriggering(vspyx.Communication.FrameTriggering):
	"""LINFrameTriggering
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.LINFrameTriggering: ...

	def CloneConfiguration(self) -> typing.Any: ...

class Machine(vspyx.Communication.Architecture):
	"""Machine
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	@typing.overload
	def New() -> vspyx.Communication.Machine: ...

	def ComponentStart(self) -> typing.Any: ...

	def ComponentStop(self) -> typing.Any: ...


	@staticmethod
	@typing.overload
	def New(config: typing.Any) -> vspyx.Communication.Machine: ...

	def CloneConfiguration(self) -> typing.Any: ...

class MachineDesign(vspyx.Core.ResolverObject):
	"""MachineDesign
	"""
	Connectors: typing.List[vspyx.Communication.Connector]
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	def ConfigureStack(self, stack: vspyx.Communication.Stack) -> typing.Any: ...


	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.MachineDesign: ...

	def CloneConfiguration(self) -> typing.Any: ...

class Message(vspyx.Core.Object):
	"""Represents the functional basis of a message object
	"""
	"""Message
	"""
	OnReceived: vspyx.Core.Callback_634bd5c449
	def Transmit(self) -> typing.Any: ...

class Module(vspyx.Core.Module):
	"""Represents the communcation module
	"""
	"""Module
	"""
	Component: vspyx.Communication.Component
	Dissector: vspyx.Dissector.Engine
	PhysicalConnectors: vspyx.Core.ResolverCollection
	SourceHandles: vspyx.Core.ResolverCollection
	Topology: vspyx.Communication.Topology
	UserPhysicalConnectors: vspyx.Core.ResolverOwningCollection
	UserSourceHandles: vspyx.Core.ResolverOwningCollection
	UserTopology: vspyx.Communication.Topology

	@typing.overload
	def NewSourceHandleFromDescription(self, description: str) -> vspyx.Communication.SourceHandle: ...


	@typing.overload
	def NewSourceHandleFromDescription(self, description: str, owned: bool) -> vspyx.Communication.SourceHandle: ...


	@typing.overload
	def ConnectControllerToChannel(self, controller: vspyx.Communication.Controller, channel: vspyx.Communication.Channel) -> vspyx.Communication.Connector: ...


	@typing.overload
	def ConnectControllerToChannel(self, controller: vspyx.Communication.Controller, channel: vspyx.Communication.Channel, permanent: bool) -> vspyx.Communication.Connector: ...


	@typing.overload
	def ConnectDriverToCluster(self, source: vspyx.Communication.SourceHandle, driverDescription: str, cluster: vspyx.Communication.Cluster) -> vspyx.Communication.PhysicalConnector: ...


	@typing.overload
	def ConnectDriverToCluster(self, source: vspyx.Communication.SourceHandle, driverDescription: str, cluster: vspyx.Communication.Cluster, permanent: bool) -> vspyx.Communication.PhysicalConnector: ...

	def RefreshSources(self) -> typing.Any: ...

	def SetupDiscoveryClusters(self) -> typing.Any: ...

	def NewLoadVSDBTask(self, path: str, serialized: bool, namespaced: bool, missingNetworkType: vspyx.Frames.FrameType.Enum, createChannels: bool) -> vspyx.Core.Task_e80474c995: ...

	def NewLoadDBCTask(self, path: str, serialized: bool, namespaced: bool, createChannels: bool) -> vspyx.Core.Task_0431e75dc5: ...

class MultiplexedIPDUPoint(vspyx.Communication.PDUPoint):
	"""MultiplexedIPDUPoint
	"""
	SelectorFieldValue: int

	@staticmethod
	def New(direction: vspyx.Runtime.Point.Direction, upstreamPoints: typing.List[vspyx.Runtime.Point], multiplexedIPDU: vspyx.Communication.MultiplexedIPDU, data: vspyx.Core.BytesView, selectorFieldValue: int) -> vspyx.Runtime.Point.Consuming_9f8cd48833: ...

class MultiplexedIPDU(vspyx.Communication.IPDU):
	"""MultiplexedIPDU
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	StaticPDU: vspyx.Communication.ISignalIPDU
	def NewPoint(self, direction: vspyx.Runtime.Point.Direction, upstreamPoints: typing.List[vspyx.Runtime.Point], data: vspyx.Core.BytesView) -> vspyx.Runtime.Point.Consuming_9f8cd48833: ...


	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.MultiplexedIPDU: ...

	def CloneConfiguration(self) -> typing.Any: ...

class NetworkManagementPDU(vspyx.Communication.PDU):
	"""Represents a network management PDU
	"""
	"""NetworkManagementPDU
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.NetworkManagementPDU: ...

	def CloneConfiguration(self) -> typing.Any: ...

class NetworkPDU(vspyx.Communication.IPDU):
	"""NetworkPDU
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.NetworkPDU: ...

	def CloneConfiguration(self) -> typing.Any: ...

class PhysicalConnector(vspyx.Runtime.Component):
	"""A connection between a Driver and a Cluster
	 
	"""
	"""PhysicalConnector
	"""
	Cluster: vspyx.Communication.Cluster
	Driver: vspyx.Frames.Driver
	Egress: vspyx.Core.Function_316d8f46e9
	EgressBlocked: bool
	EgressImmediate: vspyx.Core.Function_a6845211fe
	Ingress: vspyx.Core.Function_a6845211fe
	IngressBlocked: bool
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	def RefreshConnections(self) -> typing.Any: ...

	def AttachToCluster(self, cluster: vspyx.Communication.Cluster, permanent: bool) -> typing.Any:
		"""Attach this connector to the given cluster, removing the PhysicalConnector
		from a previously attached cluster, if present.

		"""
		pass


	def DefaultIngress(self, event: vspyx.Frames.NetworkEvent) -> vspyx.Communication.Connector.IngressActions: ...

	def DefaultEgress(self, event: vspyx.Frames.NetworkEvent) -> typing.Any: ...

	def DefaultEgressImmediate(self, event: vspyx.Frames.NetworkEvent) -> vspyx.Communication.Connector.IngressActions: ...

	def IncrementIngressCounter(self, action: vspyx.Communication.Connector.IngressActions) -> typing.Any: ...

	def IncrementEgressCounter(self) -> typing.Any: ...


	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.PhysicalConnector: ...

	def CloneConfiguration(self) -> typing.Any: ...

class ServiceInterfaceDeployment(vspyx.Core.ResolverObject):
	"""ServiceInterfaceDeployment
	"""
	def ConfigureStack(self, stack: vspyx.Communication.Stack) -> typing.Any: ...

class SOMEIPServiceInterfaceDeployment(vspyx.Communication.ServiceInterfaceDeployment):
	"""SOMEIPServiceInterfaceDeployment
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	ServiceInterfaceID: int

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.SOMEIPServiceInterfaceDeployment: ...

	def CloneConfiguration(self) -> typing.Any: ...

class ServiceInstanceCollectionSet(vspyx.Core.ResolverObject):
	"""ServiceInstanceCollectionSet
	"""
	ConsumedServiceInstances: typing.List[vspyx.Communication.ConsumedServiceInstance]
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	ProvidedServiceInstances: typing.List[vspyx.Communication.ProvidedServiceInstance]

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.ServiceInstanceCollectionSet: ...

	def CloneConfiguration(self) -> typing.Any: ...

class SecuredIPDU(vspyx.Communication.PDU):
	"""Represents a general purpose PDU used for DoIP, service discovery, or global timing
	 
	"""
	"""SecuredIPDU
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	@typing.overload
	def New() -> vspyx.Communication.SecuredIPDU: ...


	@staticmethod
	@typing.overload
	def New(config: typing.Any) -> vspyx.Communication.SecuredIPDU: ...

	def CloneConfiguration(self) -> typing.Any: ...

class ServiceInterface(vspyx.Core.ResolverObject):
	"""ServiceInterface
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.ServiceInterface: ...

	def CloneConfiguration(self) -> typing.Any: ...

class SignalGroupInstance:
	"""An instance of a signal group that is being processed by the Communication module.
	 This class is short-lived, and referencing it outside of the immediate callback
	 may result in unpredictable behavior.
	 
	"""
	"""SignalGroupInstance
	"""
	Valid: bool
	SignalValues: typing.Any

class SignalInstance:
	"""An instance of a signal that is being processed by the Communication module.
	 This class is short-lived, and referencing it outside of the immediate callback
	 may result in unpredictable behavior.
	 
	"""
	"""SignalInstance
	"""
	Value: vspyx.Runtime.Value
	Valid: bool

class SimResetEventPoint(vspyx.Communication.DataLinkEventPoint):
	"""See documentation for Frames.SimResetEvent
	 
	"""
	"""SimResetEventPoint
	"""
	Interesting: vspyx.Runtime.Point.Interesting
	NetworkEvent: vspyx.Frames.NetworkEvent
	def GetAttribute(self, type: vspyx.Core.Tag) -> vspyx.Runtime.Value: ...

class StaticSocketConnection(vspyx.Core.ResolverObject):
	"""StaticSocketConnection
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	PDUs: typing.List[vspyx.Communication.SocketConnectionIPduIdentifier]

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.StaticSocketConnection: ...

	def CloneConfiguration(self) -> typing.Any: ...

class SocketAddress(vspyx.Core.ResolverObject):
	"""Represents the connection between an ApplicationEndpoint
	 and Connectors, either in a unicast or multicast scenario.
	 
	"""
	"""SocketAddress
	"""
	@enum.unique
	class ConnectorAssociationTypes(enum.IntEnum):
		NONE = 0
		Unicast = 1
		Multicast = 2

	ApplicationEndpoint: vspyx.Communication.ApplicationEndpoint
	"""Retrieve the ApplicationEndpoint referenced by this SocketAddress
	 if resolvable. Returns nullptr if not resolvable.
		 
	"""

	MulticastConnectors: typing.List[vspyx.Communication.Connector]
	"""Retrieve the multicast connectors associated with this socket address
	 if resolvable. Unresolved items are not included.
		 
	"""

	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	StaticSocketConnections: typing.List[vspyx.Communication.StaticSocketConnection]
	UnicastConnector: vspyx.Communication.Connector
	"""Retrieve the unicast connector associated with this socket address,
	 if set and resolvable. Returns nullptr if either condition is not met.
		 
	"""

	def GetAssociation(self, connector: vspyx.Communication.Connector) -> vspyx.Communication.SocketAddress.ConnectorAssociationTypes:
		"""Returns the type of association between the provided connector and the current object

		"""
		pass


	def IsAssociatedWith(self, connector: vspyx.Communication.Connector) -> bool:
		"""Returns true if the given connector is the unicast connector, or one
		of the multicast connectors, associated with this socket address.

		"""
		pass



	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.SocketAddress: ...

	def CloneConfiguration(self) -> typing.Any: ...

class SocketConnectionIPduIdentifierSet(vspyx.Core.ResolverObject):
	"""SocketConnectionIPduIdentifierSet
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.SocketConnectionIPduIdentifierSet: ...

	def CloneConfiguration(self) -> typing.Any: ...

class SourceHandle(vspyx.Core.ResolverObject):
	"""Represents a data source and discovery object relationship
	"""
	"""SourceHandle
	"""
	@enum.unique
	class NotReadyReason(enum.IntEnum):
		NotApplicable = 0
		NotFound = 1
		SourceWentAway = 2
		Initializing = 3

	Controllers: vspyx.Core.ResolverCollection
	Discovery: vspyx.Core.ResolverCollection
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	Source: vspyx.Frames.Source
	SourceState: vspyx.Frames.Source.State
	def GetNotReadyReason(self) -> vspyx.Communication.SourceHandle.NotReadyReason: ...

	def AddDiscovery(self, obj: vspyx.Core.ResolverObject) -> typing.Any: ...

	def GetDriverFromDescription(self, description: str) -> vspyx.Frames.Driver: ...

	def SearchFor(self) -> bool: ...

	def Open(self) -> vspyx.Core.Task_a3295bec43: ...

	def SetupDiscoveryClusters(self, forEachCluster: typing.Any) -> typing.Any: ...

	def Start(self) -> vspyx.Core.Task_a3295bec43: ...

	def Stop(self) -> vspyx.Core.Task_a3295bec43: ...

	def Close(self) -> vspyx.Core.Task_a3295bec43: ...

	def ResetSource(self) -> vspyx.Core.Task_a3295bec43: ...


	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.SourceHandle: ...

	def CloneConfiguration(self) -> typing.Any: ...

	def CloneState(self) -> typing.Any: ...

	def UpdateState(self, state: typing.Any) -> typing.Any: ...

class StdCPPImplementationDataType(vspyx.Communication.CPPImplementationDataType):
	"""StdCPPImplementationDataType
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.StdCPPImplementationDataType: ...

	def CloneConfiguration(self) -> typing.Any: ...

class TrafficSink(vspyx.Frames.Buffer):
	"""Represents a transaction buffer sink
	 
	"""
	"""TrafficSink
	"""

	@staticmethod
	def New() -> vspyx.Communication.TrafficSink: ...


	@staticmethod
	def FrameToString(event: vspyx.Frames.NetworkEvent, startTime: vspyx.Runtime.Timestamp, dissector: vspyx.Dissector.Engine) -> str: ...

	def AttachToChannel(self, channel: vspyx.Communication.Channel) -> typing.Any: ...

	def DetachFromChannel(self) -> typing.Any: ...

	def ClearFilters(self) -> typing.Any: ...

	def ClearFrames(self) -> typing.Any: ...


	@typing.overload
	def FindIf(self, predicate: vspyx.Frames.Predicate) -> vspyx.Frames.NetworkEvent: ...


	@typing.overload
	def FindIf(self, predicate: vspyx.Frames.Predicate, offset: int) -> vspyx.Frames.NetworkEvent: ...

	def WaitFor(self, predicate: vspyx.Frames.Predicate, sched: vspyx.Runtime.Scheduler, timeout: typing.Any) -> typing.List[vspyx.Frames.NetworkEvent]: ...

	def WatchFor(self, predicate: vspyx.Frames.Predicate) -> vspyx.Core.Event: ...

	def GetWatchForResults(self, predicate: vspyx.Frames.Predicate) -> typing.List[vspyx.Frames.NetworkEvent]: ...

	def FramesToString(self, dissector: vspyx.Dissector.Engine) -> str: ...

class UserDefinedPDU(vspyx.Communication.PDU):
	"""Represents a PDU with user-defined processing
	 
	"""
	"""UserDefinedPDU
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	@typing.overload
	def New() -> vspyx.Communication.UserDefinedPDU: ...


	@staticmethod
	@typing.overload
	def New(config: typing.Any) -> vspyx.Communication.UserDefinedPDU: ...

	def CloneConfiguration(self) -> typing.Any: ...

class VSDB(vspyx.Communication.TopologySubset):
	"""Represents the Intrepid VehicleSpy DB network topology and message specification
	"""
	"""VSDB
	"""
	Objects: vspyx.Core.ResolverOwningCollection

	@staticmethod
	def GetVehicleSpy3DefaultNetworkNames(network: int) -> typing.List[str]: ...


	@staticmethod
	def GetVehicleSpy3NetworkFromNetid(netid: int) -> typing.Any: ...

class VariableDataPrototype(vspyx.Communication.AUTOSARDataPrototype):
	"""VariableDataPrototype
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Communication.VariableDataPrototype: ...

	def CloneConfiguration(self) -> typing.Any: ...

