import typing, enum, vspyx

@enum.unique
class SubscribeTypes(enum.IntEnum):
	Stop = 1
	Subscribe = 2
	Subscribe_ReInit = 3

class ServiceDiscoveryService(vspyx.SOMEIP.Service, vspyx.Core.Object):
	"""ServiceDiscoveryService
	"""
	AnnouncePeriod: typing.Any
	InitialDelayMax: typing.Any
	InitialDelayMin: typing.Any
	InitialRepeatOfferCountMax: int
	InitialRepeatOfferDelayBase: typing.Any
	IsAutoSubscribeEnabled: bool
	IsUnicastSupported: bool
	RequestResponseDelayMax: typing.Any
	RequestResponseDelayMin: typing.Any
	def NotifyInterfaceUp(self, state: bool) -> typing.Any: ...

	def EnableServiceOffer(self, name: str, isEnabled: bool) -> typing.Any: ...


	@typing.overload
	def AddAutoSubscribeRequest(self, subscriberEndpoint: vspyx.SOMEIP.EndpointOption, serviceId: int, eventgroupId: int) -> typing.Any: ...


	@typing.overload
	def AddAutoSubscribeRequest(self, subscriberEndpoint: vspyx.SOMEIP.EndpointOption, serviceId: int, eventgroupId: int, ttl: int) -> typing.Any: ...


	@typing.overload
	def AddAutoSubscribeRequest(self, subscriberEndpoint: vspyx.SOMEIP.EndpointOption, serviceId: int, eventgroupId: int, ttl: int, instanceId: int) -> typing.Any: ...


	@typing.overload
	def AddAutoSubscribeRequest(self, subscriberEndpoint: vspyx.SOMEIP.EndpointOption, serviceId: int, eventgroupId: int, ttl: int, instanceId: int, majorVersion: int) -> typing.Any: ...


	@typing.overload
	def AddAutoSubscribeRequest(self, subscriberEndpoint: vspyx.SOMEIP.EndpointOption, serviceId: int, eventgroupId: int, ttl: int, instanceId: int, majorVersion: int, minorVersion: int) -> typing.Any: ...


	@typing.overload
	def RemoveAutoSubscribeRequest(self, subscriberEndpoint: vspyx.SOMEIP.EndpointOption, serviceId: int, eventgroupId: int) -> typing.Any: ...


	@typing.overload
	def RemoveAutoSubscribeRequest(self, subscriberEndpoint: vspyx.SOMEIP.EndpointOption, serviceId: int, eventgroupId: int, instanceId: int) -> typing.Any: ...


	@typing.overload
	def RemoveAutoSubscribeRequest(self, subscriberEndpoint: vspyx.SOMEIP.EndpointOption, serviceId: int, eventgroupId: int, instanceId: int, majorVersion: int) -> typing.Any: ...


	@typing.overload
	def RemoveAutoSubscribeRequest(self, subscriberEndpoint: vspyx.SOMEIP.EndpointOption, serviceId: int, eventgroupId: int, instanceId: int, majorVersion: int, minorVersion: int) -> typing.Any: ...


	@typing.overload
	def RequestFindService(self, target: vspyx.SOMEIP.EndpointOption, serviceId: int) -> typing.Any: ...


	@typing.overload
	def RequestFindService(self, target: vspyx.SOMEIP.EndpointOption, serviceId: int, instanceId: int) -> typing.Any: ...


	@typing.overload
	def RequestFindService(self, target: vspyx.SOMEIP.EndpointOption, serviceId: int, instanceId: int, majorVersion: int) -> typing.Any: ...


	@typing.overload
	def RequestFindService(self, target: vspyx.SOMEIP.EndpointOption, serviceId: int, instanceId: int, majorVersion: int, minorVersion: int) -> typing.Any: ...


	@typing.overload
	def RequestFindService(self, target: vspyx.SOMEIP.EndpointOption, serviceId: int, instanceId: int, majorVersion: int, minorVersion: int, ttl: int) -> typing.Any: ...


	@typing.overload
	def RequestSubscribe(self, target: vspyx.SOMEIP.EndpointOption, subscribeType: vspyx.SOMEIP.SD.SubscribeTypes, subscriber: vspyx.SOMEIP.EndpointOption, serviceId: int, instanceId: int, majorVersion: int, eventgroupId: int) -> typing.Any: ...


	@typing.overload
	def RequestSubscribe(self, target: vspyx.SOMEIP.EndpointOption, subscribeType: vspyx.SOMEIP.SD.SubscribeTypes, subscriber: vspyx.SOMEIP.EndpointOption, serviceId: int, instanceId: int, majorVersion: int, eventgroupId: int, ttl: int) -> typing.Any: ...


	@typing.overload
	def RequestSubscribe(self, target: vspyx.SOMEIP.EndpointOption, subscribeType: vspyx.SOMEIP.SD.SubscribeTypes, subscriber: vspyx.SOMEIP.EndpointOption, serviceId: int, instanceId: int, majorVersion: int, eventgroupId: int, ttl: int, counter: int) -> typing.Any: ...

	def SendOfferService(self, target: vspyx.SOMEIP.EndpointOption, service: vspyx.SOMEIP.Service) -> typing.Any: ...

	def OnAddService(self, service: vspyx.SOMEIP.Service) -> typing.Any: ...

class ServiceDiscoveryEntry(vspyx.Core.Object):
	"""ServiceDiscoveryEntry
	"""
	@enum.unique
	class EntryTypes(enum.IntEnum):
		FindService = 0
		OfferService = 1
		SubscribeEventgroup = 6
		SubscribeEventgroupAck = 7

	@enum.unique
	class EntryCreateTypes(enum.IntEnum):
		FindServiceEntry = 0
		SubscribeEventgroupEntry = 1
		StopSubscribeEventgroupEntry = 2
		OfferServiceEntry = 3
		StopOfferServiceEntry = 4
		SubscribeEventgroupAckEntry = 5
		SubscribeEventgroupNackEntry = 6

	EntryType: vspyx.SOMEIP.SD.ServiceDiscoveryEntry.EntryTypes
	InstanceId: int
	MajorVersion: int
	OriginatingService: vspyx.SOMEIP.Service
	ServiceId: int
	TTL: int
	Target: vspyx.SOMEIP.EndpointOption
	Timestamp: typing.Any
	def __str__(self) -> str: ...


	@staticmethod
	def NewRequest(type: vspyx.SOMEIP.SD.ServiceDiscoveryEntry.EntryCreateTypes) -> vspyx.SOMEIP.SD.ServiceDiscoveryEntry: ...

class ServiceDiscoveryServiceEntry(vspyx.SOMEIP.SD.ServiceDiscoveryEntry):
	"""ServiceDiscoveryServiceEntry
	"""
	MinorVersion: int

	@staticmethod
	def Cast(entry: vspyx.SOMEIP.SD.ServiceDiscoveryEntry) -> vspyx.SOMEIP.SD.ServiceDiscoveryServiceEntry: ...

class ServiceDiscoveryEventgroupEntry(vspyx.SOMEIP.SD.ServiceDiscoveryEntry):
	"""ServiceDiscoveryEventgroupEntry
	"""
	Counter: int
	EventgroupId: int
	Reserved: int

	@staticmethod
	def Cast(entry: vspyx.SOMEIP.SD.ServiceDiscoveryEntry) -> vspyx.SOMEIP.SD.ServiceDiscoveryEventgroupEntry: ...

class EventgroupEntryPoint(vspyx.Runtime.Point):
	"""EventgroupEntryPoint
	"""

class IPv4EndpointPoint(vspyx.Runtime.Point):
	"""IPv4EndpointPoint
	"""

class IPv6EndpointPoint(vspyx.Runtime.Point):
	"""IPv6EndpointPoint
	"""

class PDUPoint(vspyx.Runtime.Point):
	"""PDUPoint
	"""

class ServiceDiscoveryMessage(vspyx.SOMEIP.SomeIpMessage, vspyx.Core.Object):
	"""ServiceDiscoveryMessage
	"""
	IsUnicastSupported: bool
	RebootFlag: bool
	Reserved0: int
	def AddEntry(self, entry: vspyx.SOMEIP.SD.ServiceDiscoveryEntry) -> typing.Any: ...


	@staticmethod
	def New() -> vspyx.SOMEIP.SomeIpMessage: ...


	@staticmethod
	def Cast(message: vspyx.SOMEIP.SomeIpMessage) -> vspyx.SOMEIP.SD.ServiceDiscoveryMessage: ...

class ServiceEntryPoint(vspyx.Runtime.Point):
	"""ServiceEntryPoint
	"""

