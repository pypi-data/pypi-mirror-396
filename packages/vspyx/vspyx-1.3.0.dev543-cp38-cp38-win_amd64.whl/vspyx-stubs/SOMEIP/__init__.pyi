import typing, enum, vspyx
from . import SD

class Option:
	"""Option
	"""
	@enum.unique
	class OptionTypes(enum.IntEnum):
		NONE = 0
		Configuration = 1
		LoadBalancing = 2
		IPv4Endpoint = 4
		IPv6Endpoint = 6
		Multicast = 16
		IPv4MulticastEndpoint = 20
		IPv6MulticastEndpoint = 22
		SD = 32
		IPv4SDEndpoint = 36
		IPv6SDEndpoint = 38

	Hash: int
	IsDiscardable: bool
	Length: int
	Reserved0: int
	Type: vspyx.SOMEIP.Option.OptionTypes
	def assign(self, arg0: vspyx.SOMEIP.Option) -> vspyx.SOMEIP.Option: ...

	def __str__(self) -> str: ...

	def Serialize(self, buffer: typing.List[int]) -> int: ...

class EndpointOption(vspyx.SOMEIP.Option, vspyx.Core.Object):
	"""EndpointOption
	"""
	@enum.unique
	class L4ProtoTypes(enum.IntEnum):
		TCP = 6
		UDP = 17

	IpAddress: vspyx.Core.IPAddressAndPort
	IsMulticast: bool
	L4ProtoType: vspyx.SOMEIP.EndpointOption.L4ProtoTypes
	RebootFlag: bool
	def GetSessionId(self, clientId: int) -> int: ...

	def SetSessionId(self, clientId: int, sessionId: int) -> typing.Any: ...

	def IsSDEndpoint(self) -> bool: ...

	def IncrementSessionId(self, clientId: int) -> typing.Any: ...


	@staticmethod
	@typing.overload
	def NewTCPEndpoint() -> vspyx.SOMEIP.EndpointOption: ...


	@staticmethod
	@typing.overload
	def NewTCPEndpoint(address: str) -> vspyx.SOMEIP.EndpointOption: ...


	@staticmethod
	@typing.overload
	def NewTCPEndpoint(address: str, port: int) -> vspyx.SOMEIP.EndpointOption: ...


	@staticmethod
	@typing.overload
	def NewUDPEndpoint() -> vspyx.SOMEIP.EndpointOption: ...


	@staticmethod
	@typing.overload
	def NewUDPEndpoint(address: str) -> vspyx.SOMEIP.EndpointOption: ...


	@staticmethod
	@typing.overload
	def NewUDPEndpoint(address: str, port: int) -> vspyx.SOMEIP.EndpointOption: ...

class ConfigValue:
	"""ConfigValue
	"""
	Name: str
	Value: typing.Any

class ConfigurationOption(vspyx.SOMEIP.Option, vspyx.Core.Object):
	"""ConfigurationOption
	"""
	def AddConfigValue(self, expression: str) -> typing.Any: ...


	@staticmethod
	def New() -> vspyx.SOMEIP.ConfigurationOption: ...

class LoadBalancingOption(vspyx.SOMEIP.Option, vspyx.Core.Object):
	"""LoadBalancingOption
	"""
	PWeight: int
	Priority: int
	def SetWeight(self, weight: int) -> typing.Any: ...


	@staticmethod
	def New(priority: int, weight: int) -> vspyx.SOMEIP.LoadBalancingOption: ...

@enum.unique
class MessageTypes(enum.IntEnum):
	Request = 0
	RequestNoReturn = 1
	Notification = 2
	Response = 128
	Error = 129
	TP = 32
	TP_Request = 32
	TP_RequestNoReturn = 33
	TP_Notification = 34
	TP_Response = 160
	TP_Error = 161

@enum.unique
class ReturnCodes(enum.IntEnum):
	E_OK = 0
	E_NOT_OK = 1
	E_UNKNOWN_SERVICE = 2
	E_UNKNOWN_METHOD = 3
	E_NOT_READY = 4
	E_NOT_REACHABLE = 5
	E_TIMEOUT = 6
	E_WRONG_PROTOCOL_VERSION = 7
	E_WRONG_INTERFACE_VERSION = 8
	E_MALFORMED_MESSAGE = 9
	E_WRONG_MESSAGE_TYPE = 10
	E_E2E_REPEATED = 11
	E_E2E_WRONG_SEQUENCE = 12
	E_E2E = 13
	E_E2E_NOT_AVAILABLE = 14
	E_E2E_NO_NEW_DATA = 15

class SomeIpHeaderInfo_t:
	"""SomeIpHeaderInfo_t
	"""
	ServiceId: int
	MethodId: int
	ProtocolVersion: int
	InterfaceVersion: int
	MessageType: vspyx.SOMEIP.MessageTypes
	ReturnCode: vspyx.SOMEIP.ReturnCodes
	Length: int
	ClientId: int
	SessionId: int
	BodyLength: int

class RequestResponseTransaction:
	"""RequestResponseTransaction
	"""
	Request: vspyx.SOMEIP.SomeIpMessage
	Response: vspyx.SOMEIP.SomeIpMessage
	ReturnCode: typing.Any
	WaitHandle: vspyx.Core.Event

class SomeIpMessage:
	"""SomeIpMessage
	"""
	ClientId: int
	DestinationEndpoint: vspyx.SOMEIP.EndpointOption
	InterfaceVersion: int
	MessageType: vspyx.SOMEIP.MessageTypes
	MethodId: int
	Payload: vspyx.Core.BytesView
	ProtocolVersion: int
	ReturnCode: vspyx.SOMEIP.ReturnCodes
	ServiceId: int
	SessionId: int
	SourceEndpoint: vspyx.SOMEIP.EndpointOption
	Timestamp: typing.Any
	def assign(self, arg0: vspyx.SOMEIP.SomeIpMessage) -> vspyx.SOMEIP.SomeIpMessage: ...

	def Serialize(self) -> typing.List[int]: ...

	def __str__(self) -> str: ...

class Service:
	"""Service
	"""
	MulticastEndpoint: vspyx.SOMEIP.EndpointOption
	Name: str
	OnEnqueueMessage: vspyx.Core.Function_7d63b03003
	OnServiceStateChange: vspyx.Core.Function_b1fe9a4c54
	ServiceId: int
	ServiceUp: bool
	TCPEndpoint: vspyx.SOMEIP.EndpointOption
	UDPEndpoint: vspyx.SOMEIP.EndpointOption
	def Attach(self, sched: vspyx.Runtime.Scheduler) -> typing.Any: ...

	def SetTCPAddress(self, address: str, port: int) -> typing.Any: ...

	def SetUDPAddress(self, address: str, port: int) -> typing.Any: ...

	def SetMulticastAddress(self, address: str, port: int) -> typing.Any: ...

	def ExecutePeriodicTask(self, now: typing.Any) -> typing.Any: ...

	def OnSending(self, message: vspyx.SOMEIP.SomeIpMessage) -> typing.Any: ...

	def DecodeMessage(self, header: vspyx.SOMEIP.SomeIpHeaderInfo_t, buffer: vspyx.Core.BytesView, startOffset: int, source: vspyx.SOMEIP.EndpointOption, dest: vspyx.SOMEIP.EndpointOption) -> vspyx.SOMEIP.SomeIpMessage: ...

	def OnRequest(self, message: vspyx.SOMEIP.SomeIpMessage, isResponseExpected: bool) -> typing.Any: ...

	def OnResponse(self, message: vspyx.SOMEIP.SomeIpMessage) -> typing.Any: ...

	def OnNotification(self, message: vspyx.SOMEIP.SomeIpMessage) -> typing.Any: ...

	def OnError(self, message: vspyx.SOMEIP.SomeIpMessage) -> typing.Any: ...

class Eventgroup:
	"""Eventgroup
	"""
	EventgroupId: int
	Events: typing.Any
	Name: str
	def assign(self, arg0: vspyx.SOMEIP.Eventgroup) -> vspyx.SOMEIP.Eventgroup: ...

	def AddEvent(self, event: vspyx.SOMEIP.Event) -> typing.Any: ...

@enum.unique
class EventNotificationTypes(enum.IntEnum):
	Manual = 0
	Cyclic = 1
	OnChange = 2
	OnEpsilonChange = 3

class Event:
	"""Event
	"""
	@enum.unique
	class SubscriptionUpdateModes(enum.IntEnum):
		Add = 0
		Update = 1
		Remove = 2

	EventId: int
	Name: str
	OnSignalValueUpdated: vspyx.Core.Callback_48191cef53
	OnSubscriptionUpdated: vspyx.Core.Callback_1f153d3f02
	OnValueChangeNotify: vspyx.Core.Function_82dd974354
	OnValueUpdated: vspyx.Core.Callback_e1fed82819
	PhysicalValue: typing.Any
	Value: typing.List[int]
	def IsMemberOfEventgroup(self, eventgroupId: int) -> bool: ...

	def JoinEventgroup(self, eventgroup: vspyx.SOMEIP.Eventgroup) -> bool: ...


	@typing.overload
	def UpdateValue(self, value: typing.List[int], silent: bool) -> typing.Any: ...


	@typing.overload
	def UpdateValue(self, values: typing.Any, silent: bool) -> typing.Any: ...

	def GetEventNotificationType(self) -> vspyx.SOMEIP.EventNotificationTypes: ...

	def SetEventNotificationType(self, type: vspyx.SOMEIP.EventNotificationTypes, param: typing.Any) -> typing.Any: ...

	def SetISignalIPDU(self, iSignalIPDU: vspyx.Communication.ISignalIPDU) -> typing.Any: ...

	def Notify(self) -> typing.Any: ...

class LoadBalancingInfo:
	"""LoadBalancingInfo
	"""
	Priority: int
	Weight: int

@enum.unique
class RequestTypes(enum.IntEnum):
	RequestNoReturn = 0
	RequestAsync = 1
	RequestSync = 2

class EventService(vspyx.SOMEIP.Service, vspyx.Core.Object):
	"""EventService
	"""
	ConfigurationOptions: typing.List[str]
	Eventgroups: typing.Any
	Events: typing.Any
	InstanceId: int
	LoadBalancingInfo: typing.Any
	MajorVersion: int
	MinorVersion: int
	OfferEnabled: bool
	OnError: vspyx.Core.Callback_771934bc25
	OnNotification: vspyx.Core.Callback_771934bc25
	OnRequest: vspyx.Core.Function_59b1b8ac6d
	OnResponse: vspyx.Core.Callback_d959bb42a9
	OnSending: vspyx.Core.Callback_771934bc25
	OnSubscriptionUpdated: vspyx.Core.Callback_6ea70db291
	SDConfig: vspyx.SOMEIP.SomeipSdConfig
	TTL: int

	@typing.overload
	def GetSubscriberCount(self) -> int: ...


	@typing.overload
	def GetSubscriberCount(self, eventgroupId: int) -> int: ...

	def OnFindServiceRequest(self, sender: vspyx.SOMEIP.EndpointOption) -> bool: ...

	def OnSubscribe(self, sender: vspyx.SOMEIP.EndpointOption, subscriberEndpoint: vspyx.SOMEIP.EndpointOption, eventgroupId: int, ttl: int) -> bool: ...

	def OnStopSubscribe(self, sender: vspyx.SOMEIP.EndpointOption, subscriberEndpoint: vspyx.SOMEIP.EndpointOption, eventgroupId: int) -> bool: ...

	def AddEvent(self, eventId: int) -> vspyx.SOMEIP.Event: ...


	@typing.overload
	def GetEvent(self, name: str) -> vspyx.SOMEIP.Event: ...


	@typing.overload
	def GetEvent(self, eventId: int) -> vspyx.SOMEIP.Event: ...

	def AddEventgroup(self, eventgroupId: int) -> vspyx.SOMEIP.Eventgroup: ...

	def GetEventgroup(self, name: str) -> vspyx.SOMEIP.Eventgroup: ...

	def AddConfigurationOption(self, expression: str) -> typing.Any: ...

	def RemoveConfigurationOption(self, expression: str) -> typing.Any: ...


	@typing.overload
	def Request(self, target: vspyx.SOMEIP.EndpointOption, serviceId: int, methodId: int, payload: typing.List[int]) -> vspyx.SOMEIP.RequestResponseTransaction: ...


	@typing.overload
	def Request(self, target: vspyx.SOMEIP.EndpointOption, serviceId: int, methodId: int, payload: typing.List[int], requestType: vspyx.SOMEIP.RequestTypes) -> vspyx.SOMEIP.RequestResponseTransaction: ...


	@typing.overload
	def Request(self, target: vspyx.SOMEIP.EndpointOption, serviceId: int, methodId: int, payload: typing.List[int], requestType: vspyx.SOMEIP.RequestTypes, clientId: typing.Any) -> vspyx.SOMEIP.RequestResponseTransaction: ...


	@staticmethod
	def New(name: str, serviceId: int, instanceId: int, versionMajor: int, versionMinor: int, ttl: int, isOfferEnabled: bool, isServiceUp: bool) -> vspyx.SOMEIP.EventService: ...

class SomeipSdConfig:
	"""SomeipSdConfig
	"""
	RequestResponseDelayMin: typing.Any
	RequestResponseDelayMax: typing.Any
	InitialDelayMax: typing.Any
	InitialDelayMin: typing.Any
	InitialRepeatOfferDelayBase: typing.Any
	InitialRepeatOfferCountMax: int
	AnnouncePeriod: typing.Any
	IsUnicastSupported: bool
	ClientIdPrefix: int
	ClientId: typing.Any
	AddressInfo_TCP: vspyx.SOMEIP.EndpointOption
	AddressInfo_UDP: vspyx.SOMEIP.EndpointOption
	MulticastAddressInfo: vspyx.SOMEIP.EndpointOption

class MutableBufferHolder:
	"""MutableBufferHolder
	"""
	def Data(self) -> vspyx.Core.BytesView: ...

	def Append(self, data: vspyx.Core.BytesView) -> typing.Any: ...

	def Insert(self, startOffset: int, data: vspyx.Core.BytesView) -> typing.Any: ...

	def Overwrite(self, startOffset: int, data: vspyx.Core.BytesView) -> typing.Any: ...

	def Remove(self, startOffset: int, count: int) -> typing.Any: ...

class HostInterface(vspyx.Runtime.Component):
	"""Represents the SOME/IP Host Module
	"""
	"""HostInterface
	"""
	InterfaceVersion: typing.Any
	Name: str
	OnMessageReceive: vspyx.Core.Callback_def3f1bba6
	OnMessageSend: vspyx.Core.Callback_def3f1bba6
	OnRxPreprocess: vspyx.Core.Function_ccc203de8f
	OnTxPreprocess: vspyx.Core.Function_870b6fb2ea
	ProtocolVersion: typing.Any
	SD: vspyx.SOMEIP.SD.ServiceDiscoveryService
	ServiceCount: int

	@staticmethod
	@typing.overload
	def New() -> vspyx.SOMEIP.HostInterface: ...


	@staticmethod
	@typing.overload
	def New(config: vspyx.SOMEIP.SomeipSdConfig) -> vspyx.SOMEIP.HostInterface: ...


	@typing.overload
	def Attach(self, network: vspyx.TCPIP.Network) -> typing.Any: ...


	@typing.overload
	def Attach(self, applicationEndpoint: vspyx.Communication.ApplicationEndpoint) -> typing.Any: ...

	def Detach(self) -> typing.Any: ...

	def AddService(self, service: vspyx.SOMEIP.Service) -> typing.Any: ...

	def GetService(self, name: str) -> vspyx.SOMEIP.Service: ...

	def IsAddressInfoValid(self) -> bool: ...

	def SetInterfaceUp(self, isUp: bool) -> typing.Any: ...

class ArrayPoint(vspyx.Runtime.Point):
	"""ArrayPoint
	"""

class Datatype(vspyx.Core.Object):
	"""Datatype
	"""
	def Deserialize(self, input: vspyx.Core.BytesView, upstreamPoint: vspyx.Runtime.Point, outputPoints: typing.List[vspyx.Runtime.Point.Consuming_1edf1860a4]) -> int:
		"""If decoding succeeds, the number of bytes read for the type will be returned

		"""
		pass


class ArrayType(vspyx.SOMEIP.Datatype):
	"""ArrayType
	"""

	@staticmethod
	def New(traceable: vspyx.Runtime.Traceable, type: vspyx.SOMEIP.Datatype) -> vspyx.SOMEIP.ArrayType: ...

class BoolPoint(vspyx.Runtime.Point):
	"""BoolPoint
	"""

class BoolType(vspyx.SOMEIP.Datatype):
	"""BoolType
	"""

	@staticmethod
	def New(traceable: vspyx.Runtime.Traceable) -> vspyx.SOMEIP.BoolType: ...

class Module(vspyx.Core.Module):
	"""Module
	"""

class NumericPoint(vspyx.Runtime.Point):
	"""NumericPoint
	"""

class NumericType(vspyx.SOMEIP.Datatype):
	"""NumericType
	"""
	@enum.unique
	class Type(enum.IntEnum):
		UINT8 = 0
		UINT16 = 1
		UINT32 = 2
		UINT64 = 3
		SINT8 = 4
		SINT16 = 5
		SINT32 = 6
		SINT64 = 7
		FLOAT32 = 8
		FLOAT64 = 9


	@staticmethod
	@typing.overload
	def New(traceable: vspyx.Runtime.Traceable, type: vspyx.SOMEIP.NumericType.Type) -> vspyx.SOMEIP.NumericType: ...


	@staticmethod
	@typing.overload
	def New(traceable: vspyx.Runtime.Traceable, type: vspyx.SOMEIP.NumericType.Type, compuMethod: vspyx.Runtime.CompuMethod) -> vspyx.SOMEIP.NumericType: ...

class PDUPoint(vspyx.Communication.PDUPoint):
	"""PDUPoint
	"""
	@enum.unique
	class MessageType(enum.IntEnum):
		Request = 0
		RequestNoReturn = 1
		Notification = 2
		Response = 128
		Error = 129
		TPRequest = 32
		TPRequestNoReturn = 33
		TPNotification = 34
		TPResponse = 160
		TPError = 161

class Processor(vspyx.Communication.PointProcessor):
	"""Processor
	"""

	@staticmethod
	def New() -> vspyx.SOMEIP.Processor: ...

class StringPoint(vspyx.Runtime.Point):
	"""StringPoint
	"""

class StringType(vspyx.SOMEIP.Datatype):
	"""StringType
	"""

	@staticmethod
	def New(traceable: vspyx.Runtime.Traceable) -> vspyx.SOMEIP.StringType: ...

class StructPoint(vspyx.Runtime.Point):
	"""StructPoint
	"""

class StructType(vspyx.SOMEIP.Datatype):
	"""StructType
	"""

