import typing, enum, vspyx

class Base(vspyx.Frames.EthernetFrame):
	"""Base
	"""
	Arbitrary: int
	Data: vspyx.Core.BytesView
	IsFCSAvailable: bool
	IsFrameTooShort: bool
	IsNoPadding: bool
	IsPreemptionEnabled: bool
	MaskView: vspyx.Core.BytesView
	Network: vspyx.Frames.NetworkIdentifier
	PreemptionFlags: int
	Source: vspyx.Frames.SourceIdentifier
	Timestamp: vspyx.Runtime.Timestamp
	Type: vspyx.Frames.FrameType
	def Clone(self) -> vspyx.Frames.NetworkEvent: ...

	def BuildFrame(self) -> vspyx.Frames.Frame: ...

	def GetBytes(self) -> typing.List[int]: ...

	def GetMask(self) -> typing.List[int]: ...

class ARPBuilder(vspyx.Frames.EthernetFrameBuilder.Base):
	"""ARPBuilder
	"""
	@enum.unique
	class HardwareTypes(enum.IntEnum):
		Reserved = 0
		Ethernet = 1

	@enum.unique
	class ProtocolTypes(enum.IntEnum):
		Reserved = 0
		IPv4 = 2048

	@enum.unique
	class Operations(enum.IntEnum):
		Request = 1
		Reply = 2

	def HardwareType(self, ht: vspyx.Frames.EthernetFrameBuilder.ARPBuilder.HardwareTypes) -> vspyx.Frames.EthernetFrameBuilder.ARPBuilder: ...

	def ProtocolType(self, pt: vspyx.Frames.EthernetFrameBuilder.ARPBuilder.ProtocolTypes) -> vspyx.Frames.EthernetFrameBuilder.ARPBuilder: ...

	def HardwareAddressLength(self, hal: int) -> vspyx.Frames.EthernetFrameBuilder.ARPBuilder: ...

	def ProtocolAddressLength(self, pal: int) -> vspyx.Frames.EthernetFrameBuilder.ARPBuilder: ...

	def Operation(self, operation: vspyx.Frames.EthernetFrameBuilder.ARPBuilder.Operations) -> vspyx.Frames.EthernetFrameBuilder.ARPBuilder: ...

	def SenderHardwareAddress(self, set: str) -> vspyx.Frames.EthernetFrameBuilder.ARPBuilder: ...

	def SenderProtocolAddress(self, set: str) -> vspyx.Frames.EthernetFrameBuilder.ARPBuilder: ...

	def TargetHardwareAddress(self, set: str) -> vspyx.Frames.EthernetFrameBuilder.ARPBuilder: ...

	def TargetProtocolAddress(self, set: str) -> vspyx.Frames.EthernetFrameBuilder.ARPBuilder: ...

class ICMPBuilder(vspyx.Frames.EthernetFrameBuilder.Base):
	"""ICMPBuilder
	"""
	@enum.unique
	class Types(enum.IntEnum):
		EchoReply = 0
		DestinationUnreachable = 3
		SourceQuench = 4
		RedirectMessage = 5
		EchoRequest = 8
		RouterAdvertisement = 9
		RouterSolicitation = 10
		TimeExceeded = 11
		ParameterProblem = 12
		Timestamp = 13
		TimestampReply = 14
		InformationRequest = 15
		InformationReply = 16
		AddressMaskRequst = 17
		AddressMaskReply = 18
		Traceroute = 30
		ExtendedEchoRequest = 42
		ExtendedEchoReply = 43

	@enum.unique
	class Codes(enum.IntEnum):
		EchoReply = 0
		DestinationNetworkUnreachable = 0
		DestinationHostUnreachable = 1
		DestinationProtocolUnreachable = 2
		DestinationPortUnreachable = 3
		FragmentationRequired = 4
		SourceRouteFailed = 5
		DestinationNetworkUnknown = 6
		DestinationHostUnknown = 7
		SourceHostIsolated = 8
		NetworkAdministrativelyProhibited = 9
		HostAdministrativelyProhibited = 10
		NetworkUnreachable = 11
		HostUnreachable = 12
		CommunicationAdministrativelyProhibited = 13
		HostPrecedenceViolation = 14
		PrecedenceCutoffInEffect = 15
		SourceQuench = 0
		RedirectDatagramForTheNetwork = 0
		RedirectDatagramForTheHost = 1
		RedirectDatagramForTheToSAndNetwork = 2
		RedirectDatagramForTheToSAndHost = 3
		EchoRequest = 0
		RouterAdvertisement = 0
		RouterSolicitation = 0
		TTLExpiredInTransit = 0
		FragmentReassemblyTimeExceeded = 1
		PointerIndicatesTheError = 0
		MissingARequiredOption = 1
		BadLength = 2
		Timestamp = 0
		TimestampReply = 0
		InformationRequest = 0
		InformationReply = 0
		AddressMaskRequest = 0
		AddressMaskReply = 0
		RequestExtendedEcho = 0
		NoError = 0
		MalformedQuery = 1
		NoSuchInterface = 2
		NoSuchTableEntry = 3
		MultipleInterfacesSatisfyQuery = 4

	def ICMPType(self, type: vspyx.Frames.EthernetFrameBuilder.ICMPBuilder.Types) -> vspyx.Frames.EthernetFrameBuilder.ICMPBuilder: ...

	def Code(self, code: vspyx.Frames.EthernetFrameBuilder.ICMPBuilder.Codes) -> vspyx.Frames.EthernetFrameBuilder.ICMPBuilder: ...

	def Checksum(self, checksum: int) -> vspyx.Frames.EthernetFrameBuilder.ICMPBuilder: ...

	def RestOfHeader(self, roh: int) -> vspyx.Frames.EthernetFrameBuilder.ICMPBuilder: ...

class UDPBuilder(vspyx.Frames.EthernetFrameBuilder.Base):
	"""UDPBuilder
	"""
	def SourcePort(self, port: int) -> vspyx.Frames.EthernetFrameBuilder.UDPBuilder: ...

	def DestinationPort(self, port: int) -> vspyx.Frames.EthernetFrameBuilder.UDPBuilder: ...

	def Length(self, length: int) -> vspyx.Frames.EthernetFrameBuilder.UDPBuilder: ...

	def Checksum(self, checksum: int) -> vspyx.Frames.EthernetFrameBuilder.UDPBuilder: ...

	def AppendPayload(self, data: vspyx.Core.BytesView) -> vspyx.Frames.EthernetFrameBuilder.UDPBuilder: ...

	def UpdateChecksum(self) -> vspyx.Frames.EthernetFrameBuilder.UDPBuilder: ...

class TCPBuilder(vspyx.Frames.EthernetFrameBuilder.Base):
	"""TCPBuilder
	"""
	def SourcePort(self, port: int) -> vspyx.Frames.EthernetFrameBuilder.TCPBuilder: ...

	def DestinationPort(self, port: int) -> vspyx.Frames.EthernetFrameBuilder.TCPBuilder: ...

	def SequenceNumber(self, num: int) -> vspyx.Frames.EthernetFrameBuilder.TCPBuilder: ...

	def AcknowledgmentNumber(self, num: int) -> vspyx.Frames.EthernetFrameBuilder.TCPBuilder: ...

	def DataOffset(self, offset: int) -> vspyx.Frames.EthernetFrameBuilder.TCPBuilder: ...

	def Flags(self, flags: int) -> vspyx.Frames.EthernetFrameBuilder.TCPBuilder: ...

	def WindowSize(self, size: int) -> vspyx.Frames.EthernetFrameBuilder.TCPBuilder: ...

	def Checksum(self, checksum: int) -> vspyx.Frames.EthernetFrameBuilder.TCPBuilder: ...

	def UrgentPointer(self, urg: int) -> vspyx.Frames.EthernetFrameBuilder.TCPBuilder: ...

	def AppendOption(self, option: int) -> vspyx.Frames.EthernetFrameBuilder.TCPBuilder: ...

	def AppendPayload(self, data: vspyx.Core.BytesView) -> vspyx.Frames.EthernetFrameBuilder.TCPBuilder: ...

class IPv4RawBuilder(vspyx.Frames.EthernetFrameBuilder.Base):
	"""IPv4RawBuilder
	"""
	def AppendPayload(self, data: vspyx.Core.BytesView) -> vspyx.Frames.EthernetFrameBuilder.IPv4RawBuilder: ...

class IPv4Builder(vspyx.Frames.EthernetFrameBuilder.Base):
	"""IPv4Builder
	"""
	@enum.unique
	class Protocols(enum.IntEnum):
		ICMP = 1
		IGMP = 2
		IPv4 = 3
		TCP = 6
		UDP = 17

	def ICMP(self) -> vspyx.Frames.EthernetFrameBuilder.ICMPBuilder: ...

	def UDP(self) -> vspyx.Frames.EthernetFrameBuilder.UDPBuilder: ...

	def Raw(self) -> vspyx.Frames.EthernetFrameBuilder.IPv4RawBuilder: ...

	def TCP(self) -> vspyx.Frames.EthernetFrameBuilder.TCPBuilder: ...

	def DifferentiatedServicesCodePoint(self, dscp: int) -> vspyx.Frames.EthernetFrameBuilder.IPv4Builder: ...

	def ExplicitCongestionNotification(self, ecn: int) -> vspyx.Frames.EthernetFrameBuilder.IPv4Builder: ...

	def TotalLength(self, tl: int) -> vspyx.Frames.EthernetFrameBuilder.IPv4Builder: ...

	def Identification(self, id: int) -> vspyx.Frames.EthernetFrameBuilder.IPv4Builder: ...

	def Flags(self, flags: int) -> vspyx.Frames.EthernetFrameBuilder.IPv4Builder: ...

	def FragmentOffset(self, fo: int) -> vspyx.Frames.EthernetFrameBuilder.IPv4Builder: ...

	def TimeToLive(self, ttl: int) -> vspyx.Frames.EthernetFrameBuilder.IPv4Builder: ...

	def Protocol(self, protocol: vspyx.Frames.EthernetFrameBuilder.IPv4Builder.Protocols) -> vspyx.Frames.EthernetFrameBuilder.IPv4Builder: ...

	def HeaderChecksum(self, hc: int) -> vspyx.Frames.EthernetFrameBuilder.IPv4Builder: ...

	def SourceIPAddress(self, set: str) -> vspyx.Frames.EthernetFrameBuilder.IPv4Builder: ...

	def DestinationIPAddress(self, set: str) -> vspyx.Frames.EthernetFrameBuilder.IPv4Builder: ...

	def AppendOption(self, option: int) -> vspyx.Frames.EthernetFrameBuilder.IPv4Builder: ...

	def UpdateChecksum(self) -> vspyx.Frames.EthernetFrameBuilder.IPv4Builder: ...

class VLANBuilder(vspyx.Frames.EthernetFrameBuilder.Base):
	"""VLANBuilder
	"""
	def IPv4(self) -> vspyx.Frames.EthernetFrameBuilder.IPv4Builder: ...

	def PriorityCodePoint(self, pcp: int) -> vspyx.Frames.EthernetFrameBuilder.VLANBuilder: ...

	def DropEligibleIndicator(self, dei: int) -> vspyx.Frames.EthernetFrameBuilder.VLANBuilder: ...

	def VLANIdentifier(self, vid: int) -> vspyx.Frames.EthernetFrameBuilder.VLANBuilder: ...

class FrameBuilder(vspyx.Frames.EthernetFrameBuilder.Base):
	"""FrameBuilder
	"""
	@enum.unique
	class EtherTypes(enum.IntEnum):
		IPv4 = 2048
		ARP = 2054
		VLAN = 33024
		IPv6 = 34525

	def ARP(self) -> vspyx.Frames.EthernetFrameBuilder.ARPBuilder: ...

	def IPv4(self) -> vspyx.Frames.EthernetFrameBuilder.IPv4Builder: ...

	def VLAN(self) -> vspyx.Frames.EthernetFrameBuilder.VLANBuilder: ...

	def DestinationMACAddress(self, set: str) -> vspyx.Frames.EthernetFrameBuilder.FrameBuilder: ...

	def SourceMACAddress(self, set: str) -> vspyx.Frames.EthernetFrameBuilder.FrameBuilder: ...

	def EtherType(self, set: vspyx.Frames.EthernetFrameBuilder.FrameBuilder.EtherTypes) -> vspyx.Frames.EthernetFrameBuilder.FrameBuilder: ...

