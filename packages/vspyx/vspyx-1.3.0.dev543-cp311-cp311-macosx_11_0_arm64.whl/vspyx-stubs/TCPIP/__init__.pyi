import typing, enum, vspyx

@enum.unique
class AddressFamily(enum.IntEnum):
	Unspecified = 0
	IPv4 = 1
	IPv6 = 2

@enum.unique
class Protocol(enum.IntEnum):
	IPv4 = 0
	ICMPv4 = 1
	IGMP = 2
	TCP = 6
	UDP = 17
	IPv6 = 41
	ICMPv6 = 58

@enum.unique
class SocketType(enum.IntEnum):
	Unspecified = 0
	Stream = 1
	Datagram = 2
	Raw = 3

@enum.unique
class IPProtocol(enum.IntEnum):
	"""Represents a protocol type (TCP or UDP)
"""
	TCP = 6
	UDP = 17

class TCPUDPEndpoint:
	"""Represents a TCP/UDP endpoint identifier
	"""
	"""TCPUDPEndpoint
	"""
	Version: vspyx.Core.IPVersion
	Proto: vspyx.TCPIP.IPProtocol
	SourceAddress: vspyx.Core.IPAddress
	SourcePort: int
	DestinationAddress: vspyx.Core.IPAddress
	DestinationPort: int
	def __eq__(self, rhs: vspyx.TCPIP.TCPUDPEndpoint) -> bool: ...

	def __str__(self) -> str: ...

class Follower(vspyx.Runtime.Component):
	"""Represents TCP/IP packet handling object
	"""
	"""Follower
	"""
	@enum.unique
	class FilterMode(enum.IntEnum):
		OnlyFilters = 0
		AllButFilters = 1

	@enum.unique
	class ConnectionStateChange(enum.IntEnum):
		Error = 0
		OpenedOrDetected = 1
		Closed = 2

	OnTCPConnectionStateChanged: vspyx.Core.Callback_43999c9b56
	OnTCPData: vspyx.Core.Callback_bf209425cf

	@staticmethod
	def New() -> vspyx.TCPIP.Follower: ...

	def SetFilterMode(self, set: vspyx.TCPIP.Follower.FilterMode) -> typing.Any: ...

	def GetFilterMode(self) -> vspyx.TCPIP.Follower.FilterMode: ...


	@typing.overload
	def AddFilter(self, ipVersion: vspyx.Core.IPVersion, ipProtocol: vspyx.TCPIP.IPProtocol, address: str, port: int) -> typing.Any: ...


	@typing.overload
	def AddFilter(self, ipVersion: vspyx.Core.IPVersion, ipProtocol: vspyx.TCPIP.IPProtocol, address: str, port: int, otherAddress: typing.Any) -> typing.Any: ...

	def ClearFilters(self) -> typing.Any: ...

	def Attach(self, channel: vspyx.Communication.EthernetChannel) -> typing.Any: ...

	def Detach(self) -> typing.Any: ...

class Network(vspyx.Communication.PointProcessor):
	"""Represents a managed collection of network interfaces
	"""
	"""Network
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	@typing.overload
	def New() -> vspyx.TCPIP.Network: ...

	def AddInterface(self, iface: vspyx.TCPIP.Interface) -> typing.Any: ...

	def NewIPv4TCPSocket(self) -> vspyx.TCPIP.Socket: ...

	def NewIPv4UDPSocket(self) -> vspyx.TCPIP.Socket: ...

	def NewIPv6TCPSocket(self) -> vspyx.TCPIP.Socket: ...

	def NewIPv6UDPSocket(self) -> vspyx.TCPIP.Socket: ...

	def NewRawIPv4Socket(self, protocol: vspyx.TCPIP.Protocol) -> vspyx.TCPIP.Socket: ...

	def NewRawIPv6Socket(self, protocol: vspyx.TCPIP.Protocol) -> vspyx.TCPIP.Socket: ...

	def NewSocket(self, af: vspyx.TCPIP.AddressFamily, type: vspyx.TCPIP.SocketType, protocol: vspyx.TCPIP.Protocol) -> vspyx.TCPIP.Socket: ...


	@staticmethod
	@typing.overload
	def New(config: typing.Any) -> vspyx.TCPIP.Network: ...

	def CloneConfiguration(self) -> typing.Any: ...

class CurlRequestAuthentication:
	"""CurlRequestAuthentication
	"""
	CACertificate: str
	Certificate: str
	Key: str
	def SetCACert(self, caCert: str) -> typing.Any: ...

	def HasAllCredentials(self) -> bool: ...

class CurlRequest:
	"""CurlRequest
	"""
	@enum.unique
	class HttpVersion(enum.IntEnum):
		HTTP_1_0 = 1
		HTTP_1_1 = 2

	@enum.unique
	class TlsVersion(enum.IntEnum):
		Insecure = 0
		TLS_1_2 = 6

	@enum.unique
	class RequestMethod(enum.IntEnum):
		GET = 0
		POST = 1
		PUT = 2

	LastHttpVersionUsed: vspyx.TCPIP.CurlRequest.HttpVersion

	@typing.overload
	def Download(self, url: str) -> vspyx.Core.BytesView: ...


	@typing.overload
	def Download(self, url: str, responseCode: int) -> vspyx.Core.BytesView: ...


	@typing.overload
	def Download(self, url: str, responseCode: int, requestMethod: vspyx.TCPIP.CurlRequest.RequestMethod) -> vspyx.Core.BytesView: ...


	@typing.overload
	def Download(self, url: str, responseCode: int, requestMethod: vspyx.TCPIP.CurlRequest.RequestMethod, postField: str) -> vspyx.Core.BytesView: ...


	@typing.overload
	def Download(self, url: str, outputStream: vspyx.IO.OutputStream) -> int: ...


	@typing.overload
	def Download(self, url: str, outputStream: vspyx.IO.OutputStream, responseCode: int) -> int: ...


	@typing.overload
	def Download(self, url: str, outputStream: vspyx.IO.OutputStream, responseCode: int, requestMethod: vspyx.TCPIP.CurlRequest.RequestMethod) -> int: ...


	@typing.overload
	def Download(self, url: str, outputStream: vspyx.IO.OutputStream, responseCode: int, requestMethod: vspyx.TCPIP.CurlRequest.RequestMethod, postField: str) -> int: ...


	@typing.overload
	def Upload(self, url: str, srcBuffer: vspyx.Core.BytesView) -> vspyx.TCPIP.CurlRequest.UploadStats: ...


	@typing.overload
	def Upload(self, url: str, srcBuffer: vspyx.Core.BytesView, responseCode: int) -> vspyx.TCPIP.CurlRequest.UploadStats: ...


	@typing.overload
	def Upload(self, url: str, inputStream: vspyx.IO.InputStream) -> vspyx.TCPIP.CurlRequest.UploadStats: ...


	@typing.overload
	def Upload(self, url: str, inputStream: vspyx.IO.InputStream, responseCode: int) -> vspyx.TCPIP.CurlRequest.UploadStats: ...

	def RequestVerified(self) -> bool: ...

	def ShowProgress(self, showProgress: bool) -> typing.Any: ...

	def SetTimeout(self, timeout: typing.Any) -> typing.Any: ...

	class UploadStats:
		"""UploadStats
		"""
		uploadSpeed: int
		totalTime: int


class IPDatagramPoint(vspyx.Communication.DatagramPoint):
	"""IPDatagramPoint
	"""
	IsRoutingLayer: bool
	IsRoutingLayerTag: vspyx.Core.Tag
	def GetAttribute(self, type: vspyx.Core.Tag) -> vspyx.Runtime.Value: ...

class IPDiscoveryProcessor(vspyx.Communication.PointProcessor):
	"""IPDiscoveryProcessor
	"""
	EphemeralPortRange: typing.Any
	"""Get the range [min, max] of ports which are considered ephemeral.
	 
	 Ephemeral ports will be coalesced into a single Traceable, as long
	 as both ports are not in the ephemeral range.
		 
	"""


	@staticmethod
	def New() -> vspyx.TCPIP.IPDiscoveryProcessor: ...

class IPv4Follower(vspyx.Communication.PointProcessor):
	"""Represents raw IP data handling and processing
	"""
	"""IPv4Follower
	"""
	OnRawDatagram: vspyx.Core.Callback_cc25a8fde8
	VerifyChecksums: bool

	@staticmethod
	def New() -> vspyx.TCPIP.IPv4Follower: ...

	def ProcessDatagram(self, data: vspyx.Core.BytesView) -> typing.Any: ...

class Interface(vspyx.Runtime.Component):
	"""Represents an Ethernet interface
	"""
	"""Interface
	"""
	AttachedChannel: vspyx.Communication.EthernetChannel
	IPv4Address: vspyx.Core.IPv4Address
	IPv4Gateway: vspyx.Core.IPv4Address
	IPv4Netmask: vspyx.Core.IPv4Address
	InterfaceID: int
	MACAddress: str
	Network: vspyx.TCPIP.Network
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	OnEgress: vspyx.Core.Callback_92f40c8a1f
	Up: bool

	@staticmethod
	@typing.overload
	def New() -> vspyx.TCPIP.Interface: ...

	def Attach(self, channel: vspyx.Communication.EthernetChannel) -> typing.Any: ...

	def Detach(self) -> typing.Any: ...

	def Ingress(self, frame: vspyx.Frames.Frame) -> vspyx.Communication.Connector.IngressActions: ...

	def BindToIPv6Address(self, set: vspyx.Core.IPv6Address) -> bool: ...

	def AutoconfigureIPv6Address(self, prefix: vspyx.Core.IPv6Address) -> bool: ...

	def ClearARPTable(self) -> typing.Any: ...

	def AddARPEntry(self, ip: str, mac: str) -> typing.Any: ...

	def RemoveARPEntry(self, ip: str) -> bool: ...

	def SendARPRequest(self, ip: str) -> typing.Any: ...

	def GetARPTableEntry(self, ip: str) -> str: ...


	@staticmethod
	@typing.overload
	def New(config: typing.Any) -> vspyx.TCPIP.Interface: ...

	def CloneConfiguration(self) -> typing.Any: ...

class Socket(vspyx.Core.Object):
	"""Represents a standard TCP/UDP socket object
	"""
	"""Socket
	"""
	@enum.unique
	class State(enum.IntEnum):
		CLOSED = 0
		CLOSING = 1
		CONNECTING = 2
		CONNECTED = 3
		LISTENING = 4

	ActivityEvent: vspyx.Core.Event
	IPProtocol: vspyx.TCPIP.IPProtocol
	IPVersion: vspyx.Core.IPVersion
	IsClosed: bool
	Linger: bool
	LingerTime: typing.Any
	Name: str
	NoDelay: bool
	PeerName: str
	ReceiveTimeout: typing.Any
	SendTimeout: typing.Any

	@typing.overload
	def Bind(self, address: str, port: typing.Any) -> typing.Any: ...


	@typing.overload
	def Bind(self, address: str, port: typing.Any, iface: vspyx.TCPIP.Interface) -> typing.Any: ...

	def Listen(self, maxIncomingConnections: int) -> typing.Any: ...

	def Accept(self) -> typing.Any: ...


	@typing.overload
	def Connect(self, address: str, port: int) -> typing.Any: ...


	@typing.overload
	def Connect(self, address: str, port: int, iface: vspyx.TCPIP.Interface) -> typing.Any: ...

	def Receive(self, maxReceiveSize: int) -> typing.Any: ...

	def ReceiveFrom(self, maxReceiveSize: int) -> typing.Any: ...


	@typing.overload
	def Send(self, data: vspyx.Core.BytesView) -> int: ...


	@typing.overload
	def Send(self, data: vspyx.Core.BytesView, outOfBand: bool) -> int: ...


	@typing.overload
	def SendTo(self, data: vspyx.Core.BytesView, address: str, port: typing.Any) -> int: ...


	@typing.overload
	def SendTo(self, data: vspyx.Core.BytesView, address: str, port: typing.Any, outOfBand: bool) -> int: ...


	@typing.overload
	def SendTo(self, data: vspyx.Core.BytesView, address: str, port: typing.Any, outOfBand: bool, iface: vspyx.TCPIP.Interface) -> int: ...


	@typing.overload
	def Shutdown(self) -> typing.Any: ...


	@typing.overload
	def Shutdown(self, readDisabled: bool) -> typing.Any: ...


	@typing.overload
	def Shutdown(self, readDisabled: bool, writeDisabled: bool) -> typing.Any: ...

	def Close(self) -> typing.Any: ...


	@typing.overload
	def AddMulticastMembership(self, address: str) -> typing.Any: ...


	@typing.overload
	def AddMulticastMembership(self, address: str, iface: vspyx.TCPIP.Interface) -> typing.Any: ...


	@typing.overload
	def DropMulticastMembership(self, address: str) -> typing.Any: ...


	@typing.overload
	def DropMulticastMembership(self, address: str, iface: vspyx.TCPIP.Interface) -> typing.Any: ...

	def GetKeepAlive(self, set: int, idleTime: int, interval: int, maxCount: int) -> typing.Any: ...


	@typing.overload
	def SetKeepAlive(self, set: bool) -> typing.Any: ...


	@typing.overload
	def SetKeepAlive(self, set: bool, idleTime: int) -> typing.Any: ...


	@typing.overload
	def SetKeepAlive(self, set: bool, idleTime: int, interval: int) -> typing.Any: ...


	@typing.overload
	def SetKeepAlive(self, set: bool, idleTime: int, interval: int, maxCount: int) -> typing.Any: ...

	def GetState(self) -> vspyx.TCPIP.Socket.State: ...

	class Accepted:
		"""Accepted
		"""
		AcceptedSocket: vspyx.TCPIP.Socket
		Endpoint: vspyx.TCPIP.TCPUDPEndpoint


	class ReceivedFrom:
		"""ReceivedFrom
		"""
		Received: vspyx.Core.BytesView
		Endpoint: vspyx.TCPIP.TCPUDPEndpoint


class TCPHostSocket(vspyx.TCPIP.Socket):
	"""TCPHostSocket
	"""
	ActivityEvent: vspyx.Core.Event
	AvailableBytes: int
	IsClosed: bool
	Linger: bool
	LingerTime: typing.Any
	NoDelay: bool
	ReceiveTimeout: typing.Any
	SendTimeout: typing.Any
	State: vspyx.TCPIP.Socket.State
	def Listen(self, maxIncomingConnections: int) -> typing.Any: ...

	def Receive(self, maxReceiveSize: int) -> typing.Any: ...

	def Send(self, data: vspyx.Core.BytesView, outOfBand: bool) -> int: ...

	def Shutdown(self, readDisabled: bool, writeDisabled: bool) -> typing.Any: ...

	def Close(self) -> typing.Any: ...

	def GetKeepAlive(self, set: int, idleTime: int, interval: int, maxCount: int) -> typing.Any: ...

	def SetKeepAlive(self, set: bool, idleTime: int, interval: int, maxCount: int) -> typing.Any: ...

class IPv4TCPHostSocket(vspyx.TCPIP.TCPHostSocket):
	"""IPv4TCPHostSocket
	"""

class IPv6Follower(vspyx.Communication.PointProcessor):
	"""A PointProcessor which creates IPDatagramPoints from IPv6 traffic.
	 
	 Does not yet reassemble fragmented datagrams.
	 
	"""
	"""IPv6Follower
	"""

	@staticmethod
	def New() -> vspyx.TCPIP.IPv6Follower: ...

class IPv6TCPHostSocket(vspyx.TCPIP.TCPHostSocket):
	"""IPv6TCPHostSocket
	"""

class Module(vspyx.Core.Module):
	"""Represents a TCP/IP module interface
	"""
	"""Module
	"""
	def AddNetwork(self, network: vspyx.TCPIP.Network) -> typing.Any: ...

class SocketInputOutputStream(vspyx.IO.InputOutputStream):
	"""SocketInputOutputStream
	"""
	def Connect(self, hostname: str, port: int) -> typing.Any: ...

	def SetReadTimeout(self, timeout: typing.Any) -> typing.Any: ...

	def SetSendTimeout(self, timeout: typing.Any) -> typing.Any: ...


	@typing.overload
	def SetKeepAlive(self, set: bool) -> typing.Any: ...


	@typing.overload
	def SetKeepAlive(self, set: bool, idleTime: int) -> typing.Any: ...


	@typing.overload
	def SetKeepAlive(self, set: bool, idleTime: int, interval: int) -> typing.Any: ...


	@typing.overload
	def SetKeepAlive(self, set: bool, idleTime: int, interval: int, maxCount: int) -> typing.Any: ...

class SocketStateChangePoint(vspyx.Runtime.Point):
	"""SocketStateChangePoint
	"""
	Interesting: vspyx.Runtime.Point.Interesting
	def GetAttribute(self, type: vspyx.Core.Tag) -> vspyx.Runtime.Value: ...

class TCPACKPoint(vspyx.Runtime.Point):
	"""TCPACKPoint
	"""
	Interesting: vspyx.Runtime.Point.Interesting
	def GetAttribute(self, type: vspyx.Core.Tag) -> vspyx.Runtime.Value: ...

class TCPFollower(vspyx.Communication.PointProcessor):
	"""Represents TCP packet reconstruction handling and connection state management
	 
	"""
	"""TCPFollower
	"""
	OnConnectionStateChanged: vspyx.Core.Callback_43999c9b56
	OnConnectionStateChangedTracked: vspyx.Core.Callback_1a217d45a3
	OnData: vspyx.Core.Callback_bf209425cf
	OnTrackedData: vspyx.Core.Callback_0e55a84967

	@staticmethod
	def New() -> vspyx.TCPIP.TCPFollower: ...

	def ProcessIPDatagram(self, ipVersion: vspyx.Core.IPVersion, data: vspyx.Core.BytesView) -> typing.Any: ...

class TLSHostSocket(vspyx.TCPIP.Socket):
	"""TLSHostSocket
	"""

class UDPFollower(vspyx.Communication.PointProcessor):
	"""Watches for routing layer (IPv4 or IPv6) IPDatagramPoints
	 and creates UDP layer IPDatagramPoints, optionally checking
	 the checksum.
	 
	"""
	"""UDPFollower
	"""

	@staticmethod
	def New() -> vspyx.TCPIP.UDPFollower: ...

