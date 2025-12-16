import typing, enum, vspyx

class Value(typing.Any):
	pass

class ComponentInterface:
	"""Represents the basic interface of a runtime component
	"""
	"""ComponentInterface
	"""
	Initialized: bool
	Running: bool
	def InitializeEnvironment(self, sched: vspyx.Runtime.Scheduler, env: vspyx.Runtime.Environment) -> typing.Any: ...


	@typing.overload
	def StartComponent(self) -> typing.Any: ...


	@typing.overload
	def StartComponent(self, sched: vspyx.Runtime.Scheduler) -> typing.Any: ...


	@typing.overload
	def StartComponent(self, sched: vspyx.Runtime.Scheduler, env: vspyx.Runtime.Environment) -> typing.Any: ...

	def StopComponent(self) -> typing.Any: ...

	def ShutdownEnvironment(self) -> typing.Any: ...

class Component(vspyx.Core.ResolverObject, vspyx.Runtime.ComponentInterface):
	"""A component is the basic piece of functionality that the runtime is composed of.
	 
	"""
	"""Component
	"""
	Initialized: bool
	Running: bool
	def InitializeEnvironment(self, sched: vspyx.Runtime.Scheduler, env: vspyx.Runtime.Environment) -> typing.Any: ...


	@typing.overload
	def StartComponent(self) -> typing.Any: ...


	@typing.overload
	def StartComponent(self, sched: vspyx.Runtime.Scheduler) -> typing.Any: ...


	@typing.overload
	def StartComponent(self, sched: vspyx.Runtime.Scheduler, env: vspyx.Runtime.Environment) -> typing.Any: ...

	def StopComponent(self) -> typing.Any: ...

	def ShutdownEnvironment(self) -> typing.Any: ...

class Timestamp:
	"""Represents a signal point value timestamp
	"""
	"""Timestamp
	"""
	DateTime: typing.Any
	NanosSince1Jan2007: typing.Any
	def assign(self, rhs: vspyx.Runtime.Timestamp) -> vspyx.Runtime.Timestamp: ...


	@staticmethod
	def FromUnixTime(unixTime: int) -> vspyx.Runtime.Timestamp: ...


	@staticmethod
	def Now() -> vspyx.Runtime.Timestamp: ...


	@staticmethod
	def MakeTimestampDiffString(now: vspyx.Runtime.Timestamp, then: vspyx.Runtime.Timestamp) -> str: ...

	def __str__(self) -> str: ...

	def __eq__(self, rhs: vspyx.Runtime.Timestamp) -> bool: ...

	def __ne__(self, rhs: vspyx.Runtime.Timestamp) -> bool: ...


	@typing.overload
	def __sub__(self, rhs: vspyx.Runtime.Timestamp) -> typing.Any: ...

	def __add__(self, rhs: typing.Any) -> vspyx.Runtime.Timestamp: ...


	@typing.overload
	def __sub__(self, rhs: typing.Any) -> vspyx.Runtime.Timestamp: ...

	def __isub__(self, rhs: vspyx.Runtime.Timestamp) -> vspyx.Runtime.Timestamp: ...

	def __iadd__(self, rhs: vspyx.Runtime.Timestamp) -> vspyx.Runtime.Timestamp: ...

class PointLevel:
	"""Represents the data flow level of a given data element or sub-element
	"""
	"""PointLevel
	"""
	@enum.unique
	class Primary(enum.IntFlag):
		Unknown = 0
		DataLinkPDU = 1
		NetworkPDU = 2
		InteractionPDU = 3
		SignalPDU = 4
		Signal = 5

	primary: vspyx.Runtime.PointLevel.Primary
	secondary: int

	@staticmethod
	def PrimaryToString(p: vspyx.Runtime.PointLevel.Primary) -> int: ...


	@staticmethod
	def MaxSecondary() -> int: ...

	def __str__(self) -> str: ...

	def __eq__(self, other: vspyx.Runtime.PointLevel) -> bool: ...

	def __ne__(self, other: vspyx.Runtime.PointLevel) -> bool: ...

@enum.unique
class ProcessingFlags(enum.IntEnum):
	NONE = 0
	Export = 1
	InhibitTrafficDistributed = 2
	InhibitTraceSubmit = 4

class Point(vspyx.Core.Linkable):
	"""An instance of a Topology Object (e.g. PDU, Signal, etc)
	 While those Topology Objects describe the long running state of the object,
	 a Point describes a single occurence of that Topology Object in time.
	 
	"""
	"""Point
	"""
	@enum.unique
	class Direction(enum.IntEnum):
		Receive = 0
		Transmit = 1

	@enum.unique
	class Interesting(enum.IntEnum):
		"""How interesting is the Point? In other words, is\n the user likely to care about a Point at this level,\n or would it have to turn into something more before\n it is interesting to the user?\n \n As an example, CAN DataLinkPDUs are interesting\n on their own. An ISO11898-1 LDataPoint will be\n created from it, but the user will still be more\n interested in the DataLinkPDUPoint until the\n LDataPoint becomes an ISO15765-2 TDataPoint, etc.\n	 
	"""
		Yes = 0
		SuccessorsMayBe = 1
		No = 2

	Level: vspyx.Runtime.PointLevel
	"""The level of this point
		 
	"""

	PointDirection: vspyx.Runtime.Point.Direction
	"""The direction of this point, named to avoid clashes with
	 enum Point::Direction
		 
	"""

	Timestamp: vspyx.Runtime.Timestamp
	"""The time that this point was created/set
		 
	"""

	Traceable: vspyx.Runtime.Traceable
	"""The tracable this point is associated with
	 
	 If the point is not associated with a traceable or 
	 the traceable has expired, nullptr will be returned.
		 
	"""

	def IncrementConsumers(self) -> typing.Any: ...

	def DecrementConsumers(self) -> typing.Any:
		"""Decrement the count of current consumers, use the AcquireConsumerLock() RAII helper instead when possible

		See AcquireConsumerLock() for more information about the ConsumerLock

		This operation is thread-safe

		"""
		pass


	def IsDoneBeingConsumed(self) -> bool: ...

	def TimestampSet(self, nTimestamp: vspyx.Runtime.Timestamp) -> typing.Any:
		"""Set the timestamp for this point

		This should generally not be used, as in most circumstances
		as in most circumstances a timestamp will be set
		automatically for you.

		This should only be done while the point is Consuming

		"""
		pass


	def GetAttribute(self, type: vspyx.Core.Tag) -> vspyx.Runtime.Value:
		"""Get an attribute of this point by its tag

		If the attribute doesn't exist, an empty
		Runtime::Value will be returned.

		"""
		pass


	def SetAttribute(self, type: vspyx.Core.Tag, value: vspyx.Runtime.Value) -> bool:
		"""Set an attribute on this point dynamically

		Returns true if the attribute could be set

		The attribute can not be set if a subclass implements
		a read-only attribute on this point (built-in
		attributes are read-only by default, unless a setter
		is explicitly provided)

		This should only be done while the point is Consuming

		These "dynamic" attributes are lower in priority than
		built-in attributes, but higher in priority than any
		inherited attributes.

		"""
		pass


	def GetInteresting(self) -> vspyx.Runtime.Point.Interesting:
		"""See documentation for Runtime.Point.Interesting.

		"""
		pass


	def VisitDownstreamPoints(self, fn: vspyx.Core.Function_5230b09a44) -> typing.Any:
		"""Call :Parameter fn: for each of the downstream points

		If the returned bool from :Parameter fn: is false,
		the visiting breaks early.

		"Downstream" points are the child points in case
		of Direction::Receive, and the parent points in
		case of Direction::Transmit.

		"""
		pass


	def VisitUpstreamPoints(self, fn: vspyx.Core.Function_5230b09a44) -> typing.Any:
		"""Call :Parameter fn: for each of the upstream points

		If the returned bool from :Parameter fn: is false,
		the visiting breaks early.

		"Upstream" points are the parent points in case
		of Direction::Receive, and the child points in
		case of Direction::Transmit.

		"""
		pass



	@typing.overload
	def LinkUpstream(self, upstream: vspyx.Runtime.Point) -> typing.Any:
		"""Invoke the Linkable::Link function to link the
		specified :Parameter upstream: with this point.

		For Points with Direction::Transmit, these will
		linked as children, while for Direction::Receieve
		they will be linked as parents.

		By default, this function resets the timestamp
		and PointLevel for this point as if the incoming
		Point was passed to the initial constructor.

		"""
		pass



	@typing.overload
	def LinkUpstream(self, upstream: vspyx.Runtime.Point, inheritAndRelevel: bool) -> typing.Any:
		"""Invoke the Linkable::Link function to link the
		specified :Parameter upstream: with this point.

		For Points with Direction::Transmit, these will
		linked as children, while for Direction::Receieve
		they will be linked as parents.

		By default, this function resets the timestamp
		and PointLevel for this point as if the incoming
		Point was passed to the initial constructor.

		"""
		pass



	@typing.overload
	def LinkUpstream(self, upstream: typing.List[vspyx.Runtime.Point]) -> typing.Any:
		"""Helper for LinkUpstream that links a vector of
		points, such as might be received in the
		New functions for Points.

		By default, this function resets the timestamp
		and PointLevel for these points as if the incoming
		Points were passed to the initial constructor.

		"""
		pass



	@typing.overload
	def LinkUpstream(self, upstream: typing.List[vspyx.Runtime.Point], inheritAndRelevel: bool) -> typing.Any:
		"""Helper for LinkUpstream that links a vector of
		points, such as might be received in the
		New functions for Points.

		By default, this function resets the timestamp
		and PointLevel for these points as if the incoming
		Points were passed to the initial constructor.

		"""
		pass


	def LinkChild(self, newChild: vspyx.Core.Linkable) -> typing.Any: ...

	def UnlinkChild(self, newChild: vspyx.Core.Linkable) -> typing.Any: ...

	def GetProcessingFlags(self) -> vspyx.Runtime.ProcessingFlags: ...


	@typing.overload
	def SetProcessingFlags(self, set: vspyx.Runtime.ProcessingFlags) -> vspyx.Runtime.ProcessingFlags: ...


	@typing.overload
	def SetProcessingFlags(self, set: vspyx.Runtime.ProcessingFlags, clear: vspyx.Runtime.ProcessingFlags) -> vspyx.Runtime.ProcessingFlags: ...

	class Consuming_1edf1860a4:
		"""Consuming<Runtime::Point>
		"""

		@typing.overload
		def assign(self, rhs: vspyx.Runtime.Point.Consuming_1edf1860a4) -> vspyx.Runtime.Point.Consuming_1edf1860a4: ...

		Point: vspyx.Runtime.Point

		@typing.overload
		def assign(self, rhs: vspyx.Runtime.Point.Consuming_1edf1860a4) -> vspyx.Runtime.Point.Consuming_1edf1860a4: ...


	class Consuming_03654c56a8:
		"""Consuming<Communication::DataLinkPDUPoint>
		"""
		Point: vspyx.Runtime.Point
		def assign(self, rhs: vspyx.Runtime.Point.Consuming_03654c56a8) -> vspyx.Runtime.Point.Consuming_03654c56a8: ...


	class Consuming_5056ff9b42:
		"""Consuming<Communication::CANDataLinkPDUPoint>
		"""
		Point: vspyx.Runtime.Point
		def assign(self, rhs: vspyx.Runtime.Point.Consuming_5056ff9b42) -> vspyx.Runtime.Point.Consuming_5056ff9b42: ...


	class Consuming_6aef469678:
		"""Consuming<Communication::FramePoint>
		"""
		Point: vspyx.Runtime.Point
		def assign(self, rhs: vspyx.Runtime.Point.Consuming_6aef469678) -> vspyx.Runtime.Point.Consuming_6aef469678: ...


	class Consuming_1dd119a6a6:
		"""Consuming<Communication::CANFramePoint>
		"""
		Point: vspyx.Runtime.Point
		def assign(self, rhs: vspyx.Runtime.Point.Consuming_1dd119a6a6) -> vspyx.Runtime.Point.Consuming_1dd119a6a6: ...


	class Consuming_e473ff5c76:
		"""Consuming<Communication::ISignalPoint>
		"""
		Point: vspyx.Runtime.Point
		def assign(self, rhs: vspyx.Runtime.Point.Consuming_e473ff5c76) -> vspyx.Runtime.Point.Consuming_e473ff5c76: ...


	class Consuming_e1c4fc4e95:
		"""Consuming<Communication::ISignalGroupPoint>
		"""
		Point: vspyx.Runtime.Point
		def assign(self, rhs: vspyx.Runtime.Point.Consuming_e1c4fc4e95) -> vspyx.Runtime.Point.Consuming_e1c4fc4e95: ...


	class Consuming_50a4704bd5:
		"""Consuming<Runtime::SystemSignalPoint>
		"""
		Point: vspyx.Runtime.Point
		def assign(self, rhs: vspyx.Runtime.Point.Consuming_50a4704bd5) -> vspyx.Runtime.Point.Consuming_50a4704bd5: ...


	class Consuming_2215b345f6:
		"""Consuming<Communication::ISignalIPDUPoint>
		"""
		Point: vspyx.Runtime.Point
		def assign(self, rhs: vspyx.Runtime.Point.Consuming_2215b345f6) -> vspyx.Runtime.Point.Consuming_2215b345f6: ...


	class Consuming_99a0dbe01e:
		"""Consuming<Communication::ISO11898::LConfirmPoint>
		"""
		Point: vspyx.Runtime.Point
		def assign(self, rhs: vspyx.Runtime.Point.Consuming_99a0dbe01e) -> vspyx.Runtime.Point.Consuming_99a0dbe01e: ...


	class Consuming_a508b640d2:
		"""Consuming<Communication::ISO11898::LDataPoint>
		"""
		Point: vspyx.Runtime.Point
		def assign(self, rhs: vspyx.Runtime.Point.Consuming_a508b640d2) -> vspyx.Runtime.Point.Consuming_a508b640d2: ...


	class Consuming_fe9efbf398:
		"""Consuming<Communication::TDataPoint>
		"""
		Point: vspyx.Runtime.Point
		def assign(self, rhs: vspyx.Runtime.Point.Consuming_fe9efbf398) -> vspyx.Runtime.Point.Consuming_fe9efbf398: ...


	class Consuming_9f8cd48833:
		"""Consuming<Communication::MultiplexedIPDUPoint>
		"""
		Point: vspyx.Runtime.Point
		def assign(self, rhs: vspyx.Runtime.Point.Consuming_9f8cd48833) -> vspyx.Runtime.Point.Consuming_9f8cd48833: ...


	class AttributeRecord:
		"""AttributeRecord
		"""
		AliasTo: vspyx.Core.Tag
		Inherited: bool
		Inheritable: bool
		Dynamic: bool
		RenderingHint: vspyx.Core.Numeric.RenderingHint

		@staticmethod
		@typing.overload
		def MakeBuiltIn() -> vspyx.Runtime.Point.AttributeRecord: ...


		@staticmethod
		@typing.overload
		def MakeBuiltIn(inheritable: bool) -> vspyx.Runtime.Point.AttributeRecord: ...


		@staticmethod
		def MakeDynamic() -> vspyx.Runtime.Point.AttributeRecord: ...


		@staticmethod
		def MakeAlias(to: vspyx.Core.Tag) -> vspyx.Runtime.Point.AttributeRecord: ...


class Traceable(vspyx.Core.ResolverObject):
	"""Represents the basis of a value which can be contually monitored (traced) at runtime
	"""
	"""Traceable
	"""
	@enum.unique
	class UpdateMethods(enum.IntEnum):
		AsynchronouslyUpdated = 0
		SynchronousRead = 1

	Description: str
	LongName: str
	ReadFunction: vspyx.Core.Function_1d184840f7
	UpdateMethod: vspyx.Runtime.Traceable.UpdateMethods

	@staticmethod
	def New() -> vspyx.Runtime.Traceable:
		"""Create a new generic asynchronously updated Traceable.

		When working in Python, creating a more specific Traceable
		is correct rather than creating this generic one, unless you
		are implementing your own protocol.

		"""
		pass


class Tracer:
	"""A class which facilitates the storage of Runtime::Traces for the user
	 
	 Designed to easily be tacked onto another class with multiple inheritance
	 
	 Locking is all handled internally, the member functions are thread safe
	 
	"""
	"""Tracer
	"""

	@typing.overload
	def ResolveTrace(self, traceable: vspyx.Runtime.Traceable) -> vspyx.Runtime.Trace:
		"""If the given Traceable is traced here, return the Trace.

		Returns None/nullptr if the Traceable is not traced here.

		"""
		pass



	@typing.overload
	def ResolveTrace(self, point: vspyx.Runtime.Point) -> vspyx.Runtime.Trace:
		"""If the given Point is associated with a Traceable traced here, return the Trace.

		Returns None/nullptr if Point is not associated with a Traceable or the Traceable is not traced here.

		"""
		pass



	@typing.overload
	def ResolveOrNewTrace(self, traceable: vspyx.Runtime.Traceable, env: vspyx.Runtime.Environment, scheduler: vspyx.Runtime.Scheduler) -> vspyx.Runtime.Trace:
		"""For the given Traceable, return the Trace, creating a new one if necessary.

		"""
		pass



	@typing.overload
	def ResolveOrNewTrace(self, point: vspyx.Runtime.Point, env: vspyx.Runtime.Environment, scheduler: vspyx.Runtime.Scheduler) -> vspyx.Runtime.Trace:
		"""For the given Point, return the Trace, creating a new one if necessary.

		Returns None/nullptr if the Point is not associated with a Traceable.

		"""
		pass


	def ClearTraces(self) -> typing.Any:
		"""Remove all Traces traced here.

		"""
		pass


	def AddTrace(self, trace: vspyx.Runtime.Trace) -> typing.Any:
		"""Manually add a Trace.

		Throws a RuntimeError if the Traceable is already traced here.

		"""
		pass


class Environment(vspyx.Runtime.Component):
	"""Represents the runtime domain of managed and monitored datapoints
	"""
	"""Environment
	"""
	def AddComponent(self, com: vspyx.Runtime.Component) -> typing.Any: ...

	def RemoveComponent(self, com: vspyx.Runtime.Component) -> typing.Any: ...

	def AddTrace(self, trace: vspyx.Runtime.Trace) -> typing.Any:
		"""Manually add a Trace.

		Throws a RuntimeError if the Traceable is already traced here.

		"""
		pass


	OnPoint: vspyx.Core.Callback_bf2c6c2abd

	@staticmethod
	def New() -> vspyx.Runtime.Environment: ...

	def GetTrace(self, pdu: vspyx.Runtime.Traceable) -> vspyx.Runtime.Trace: ...

	def SubmitPoint(self, point: vspyx.Runtime.Point) -> typing.Any: ...

class SignalPoint(vspyx.Runtime.Point):
	"""Represents a specfic value of a signal at a point in time.
	
	 The data type of the physical value and the internal value may be
	 different. For example, state encoded signals have a numeric internal
	 value, but a string physical value.
	 
	"""
	"""SignalPoint
	"""
	InternalValue: typing.Any
	"""Get native representation of the signal
		 
	"""

	PhysicalValue: typing.Any
	"""Get the interpreted or "logical" value, 
	 which is calculated from the internal value.
		 
	"""

	Valid: bool
	"""Denotes if the signal's value is "invalid" (when set to false).
	 This is different from being not present. An invalid value
	 means the signal was set, but the value it was set to
	 was outside some validation parameters.
		 
	"""

class Signal(vspyx.Runtime.Traceable):
	"""A signal, which is an abstract quantity of information that has a definite value at a given point in time
	 
	"""
	"""Signal
	"""
	Definition: vspyx.Runtime.DataDefinition
	"""Get the definition of the value of this signal. A signal may
	 have no definition
		 
	"""

class Unit(vspyx.Core.ResolverObject):
	"""Represents a unit for a physical value, such as "volts" or "mph".
	
	 This is optionally its own object, as that's how AUTOSAR represents CompuMethod Units,
	 however in our archicture this can also be bypassed by setting a Unit directly on
	 the CompuMethod.
	 
	"""
	"""Unit
	"""
	DisplayName: str
	"""Get the "Display Name" of the Unit, AKA the Unit String
	 
	 Examples are "V" for volts, "mph", or "1/min" for engine speed.
		 
	"""

	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	@typing.overload
	def New(displayName: str) -> vspyx.Runtime.Unit: ...


	@staticmethod
	@typing.overload
	def New(config: typing.Any) -> vspyx.Runtime.Unit: ...

	def CloneConfiguration(self) -> typing.Any: ...

class DataConstraint(vspyx.Core.ResolverObject):
	"""DataConstraint
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Runtime.DataConstraint: ...

	def CloneConfiguration(self) -> typing.Any: ...

class CompuMethod(vspyx.Core.ResolverObject):
	"""Represents the conversion and scaling between runtime values and their physical representations
	"""
	"""CompuMethod
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@typing.overload
	def InternalToPhysical(self, internal: vspyx.Core.Numeric) -> typing.Any: ...


	@typing.overload
	def InternalToPhysical(self, internal: vspyx.Core.Numeric, constraints: vspyx.Runtime.DataConstraint) -> typing.Any: ...


	@typing.overload
	def PhysicalToInternal(self, physical: typing.Any) -> vspyx.Core.Numeric: ...


	@typing.overload
	def PhysicalToInternal(self, physical: typing.Any, constraints: vspyx.Runtime.DataConstraint) -> vspyx.Core.Numeric: ...


	@staticmethod
	def New(config: typing.Any) -> vspyx.Runtime.CompuMethod: ...

	def CloneConfiguration(self) -> typing.Any: ...

class ImplementableDataType(vspyx.Core.ResolverObject):
	"""ImplementableDataType
	"""
	CompuMethod: vspyx.Runtime.CompuMethod
	DataConstraints: vspyx.Runtime.DataConstraint
	ImplementationDataType: vspyx.Runtime.ImplementationDataType
	Quantity: vspyx.Runtime.ImplementableDataType.Range
	def AddElement(self, element: vspyx.Runtime.ImplementableDataType) -> typing.Any: ...

	class Range:
		"""Range
		"""
		Min: int
		Max: int


class ImplementationDataType(vspyx.Runtime.ImplementableDataType):
	"""ImplementationDataType
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	Size: int

	@staticmethod
	def New(config: typing.Any) -> vspyx.Runtime.ImplementationDataType: ...

	def CloneConfiguration(self) -> typing.Any: ...

class ApplicationPrimitiveDataType(vspyx.Runtime.ImplementableDataType):
	"""ApplicationPrimitiveDataType
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Runtime.ApplicationPrimitiveDataType: ...

	def CloneConfiguration(self) -> typing.Any: ...

class ApplicationRecordElement(vspyx.Runtime.ImplementableDataType):
	"""ApplicationRecordElement
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Runtime.ApplicationRecordElement: ...

	def CloneConfiguration(self) -> typing.Any: ...

class ApplicationRecordDataType(vspyx.Runtime.ImplementableDataType):
	"""ApplicationRecordDataType
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Runtime.ApplicationRecordDataType: ...

	def CloneConfiguration(self) -> typing.Any: ...

class ApplicationArrayDataType(vspyx.Runtime.ImplementableDataType):
	"""ApplicationArrayDataType
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	def SetElement(self, element: vspyx.Runtime.ApplicationArrayElement) -> typing.Any: ...


	@staticmethod
	def New(config: typing.Any) -> vspyx.Runtime.ApplicationArrayDataType: ...

	def CloneConfiguration(self) -> typing.Any: ...

class ApplicationArrayElement(vspyx.Runtime.ImplementableDataType):
	"""ApplicationArrayElement
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Runtime.ApplicationArrayElement: ...

	def CloneConfiguration(self) -> typing.Any: ...

class SenderReceiverInterface(vspyx.Core.ResolverObject):
	"""SenderReceiverInterface
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Runtime.SenderReceiverInterface: ...

	def CloneConfiguration(self) -> typing.Any: ...

class VariableDataPrototype(vspyx.Core.ResolverObject):
	"""VariableDataPrototype
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	RecordDataType: vspyx.Runtime.ImplementableDataType

	@staticmethod
	def New(config: typing.Any) -> vspyx.Runtime.VariableDataPrototype: ...

	def CloneConfiguration(self) -> typing.Any: ...

class TriggerInterface(vspyx.Core.ResolverObject):
	"""TriggerInterface
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Runtime.TriggerInterface: ...

	def CloneConfiguration(self) -> typing.Any: ...

class Trigger(vspyx.Core.ResolverObject):
	"""Trigger
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Runtime.Trigger: ...

	def CloneConfiguration(self) -> typing.Any: ...

class SystemMapping(vspyx.Core.ResolverObject):
	"""SystemMapping
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Runtime.SystemMapping: ...

	def CloneConfiguration(self) -> typing.Any: ...

class DataMapping:
	"""DataMapping
	"""
	Target: typing.Any
	def assign(self, arg0: vspyx.Runtime.DataMapping) -> vspyx.Runtime.DataMapping: ...

	def IsSystemSignalMatch(self, ref: str) -> bool: ...

class SystemSignalPoint(vspyx.Runtime.SignalPoint):
	"""Represents a system signal value at a given time
	"""
	"""SystemSignalPoint
	"""

	@staticmethod
	def New(systemSignal: vspyx.Runtime.SystemSignal, physicalValue: typing.Any, internalValue: typing.Any, valid: bool, timestamp: vspyx.Runtime.Timestamp) -> vspyx.Runtime.Point.Consuming_50a4704bd5: ...

class SystemSignal(vspyx.Runtime.Signal):
	"""Represents a runtime signal which contains data internal to the function of the runtime system (eg pending traffic, pending frame count, etc)
	"""
	"""SystemSignal
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	@typing.overload
	def New() -> vspyx.Runtime.SystemSignal: ...


	@staticmethod
	@typing.overload
	def New(description: str, read: vspyx.Core.Function_1d184840f7) -> vspyx.Runtime.SystemSignal: ...

	def NewPoint(self, physicalValue: typing.Any, internalValue: typing.Any, valid: bool, timestamp: vspyx.Runtime.Timestamp) -> vspyx.Runtime.Point.Consuming_50a4704bd5: ...


	@staticmethod
	@typing.overload
	def New(config: typing.Any) -> vspyx.Runtime.SystemSignal: ...

	def CloneConfiguration(self) -> typing.Any: ...

class SystemSignalGroup(vspyx.Runtime.Traceable):
	"""Represents a group of related system signals
	 
	"""
	"""SystemSignalGroup
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	@typing.overload
	def New() -> vspyx.Runtime.SystemSignalGroup: ...


	@staticmethod
	@typing.overload
	def New(description: str) -> vspyx.Runtime.SystemSignalGroup: ...


	@staticmethod
	@typing.overload
	def New(config: typing.Any) -> vspyx.Runtime.SystemSignalGroup: ...

	def CloneConfiguration(self) -> typing.Any: ...

class Scheduler(vspyx.Runtime.Component):
	"""Represents a periodic and time-scalable, managed runtime task
	"""
	"""Scheduler
	"""
	IsRunning: bool
	Now: vspyx.Runtime.Timestamp
	OnStarted: vspyx.Core.Callback_634bd5c449
	Realtime: bool
	Ticker: vspyx.Runtime.SchedulerTicker
	TimeScale: float
	TimeSinceStart: typing.Any

	@staticmethod
	def New() -> vspyx.Runtime.Scheduler: ...


	@typing.overload
	def GetTimingCallback(self, interval: typing.Any) -> vspyx.Core.Callback_b113cdf49d:
		"""Get a callback that will be raised at an interval.
		The callbacks registered by this function should be short lived and not block. In particular,
		they must never call Runtime::Wait, Runtime::WaitFor or Runtime::WaitUntil.
		:Parameter micros: duration, in microseconds, between successive raises of the callback
		:Parameter component: Optional component that was previously added with AddComponent. If specified, the callback may occur on a separate processing thread for the component
		:Returns: callback object

		"""
		pass



	@typing.overload
	def GetTimingCallback(self, interval: typing.Any, component: vspyx.Runtime.Component) -> vspyx.Core.Callback_b113cdf49d:
		"""Get a callback that will be raised at an interval.
		The callbacks registered by this function should be short lived and not block. In particular,
		they must never call Runtime::Wait, Runtime::WaitFor or Runtime::WaitUntil.
		:Parameter micros: duration, in microseconds, between successive raises of the callback
		:Parameter component: Optional component that was previously added with AddComponent. If specified, the callback may occur on a separate processing thread for the component
		:Returns: callback object

		"""
		pass



	@typing.overload
	def GetMainCallback(self) -> vspyx.Core.Callback_b113cdf49d:
		"""Get a callback that will be raised on every "main" processing loop.
		The callbacks registered by this function should be short lived and not block. In particular,
		they must never call Runtime::Wait, Runtime::WaitFor, Runtime::WaitUntil.
		:Parameter component: Optional component that was previously added with AddComponent. If specified, the callback may occur on a separate processing thread for the component

		"""
		pass



	@typing.overload
	def GetMainCallback(self, component: vspyx.Runtime.Component) -> vspyx.Core.Callback_b113cdf49d:
		"""Get a callback that will be raised on every "main" processing loop.
		The callbacks registered by this function should be short lived and not block. In particular,
		they must never call Runtime::Wait, Runtime::WaitFor, Runtime::WaitUntil.
		:Parameter component: Optional component that was previously added with AddComponent. If specified, the callback may occur on a separate processing thread for the component

		"""
		pass


	def NewThread(self, func: typing.Callable) -> typing.Any: ...

	def Wait(self, interrupt: vspyx.Core.Event) -> typing.Any:
		"""Wait indefinitely for the given Core::Event to be set.

		Throws if the scheduler stops while waiting.

		"""
		pass



	@typing.overload
	def WaitFor(self, nanos: typing.Any) -> typing.Any:
		"""Wait for the given amount of time.

		Throws if the scheduler stops while waiting.

		"""
		pass



	@typing.overload
	def WaitFor(self, nanos: typing.Any, interrupt: vspyx.Core.Event) -> bool:
		"""Wait either for the given Core::Event to be set,
		or the given amount of time.

		Returns true if the event was set, or false if the
		timeout was reached.

		Throws if the scheduler stops while waiting.

		"""
		pass



	@typing.overload
	def WaitUntil(self, timestamp: vspyx.Runtime.Timestamp) -> typing.Any:
		"""Wait until the given timestamp.

		Throws if the scheduler stops while waiting.

		"""
		pass



	@typing.overload
	def WaitUntil(self, timestamp: vspyx.Runtime.Timestamp, interrupt: vspyx.Core.Event) -> bool:
		"""Wait either for the given Core::Event to be set,
		or until the given timestamp.

		Returns true if the event was set, or false if
		the given timestamp was reached.

		Throws if the scheduler stops while waiting.

		"""
		pass


	def AddComponent(self, com: vspyx.Runtime.Component) -> typing.Any: ...

	def RemoveComponent(self, com: vspyx.Runtime.Component) -> typing.Any: ...

	def Start(self) -> typing.Any: ...

	def Stop(self) -> typing.Any: ...

	def Log(self, tag: str) -> vspyx.Core.Log: ...

	def CloneState(self) -> typing.Any: ...

	def UpdateState(self, state: typing.Any) -> typing.Any: ...

class SchedulerTicker(vspyx.Core.Object):
	"""SchedulerTicker
	"""
	def GetNextTimeAdvance(self, scheduler: vspyx.Runtime.Scheduler) -> typing.Any: ...

class Trace(vspyx.Core.Object):
	"""Represents a continually observed and runtime manipulatable interface to a datapoint
	"""
	"""Trace
	"""
	BeforeLastPoint: vspyx.Runtime.Point
	Count: int
	LastPoint: vspyx.Runtime.Point
	NewPointEvent: vspyx.Core.Event
	OnPoint: vspyx.Core.Callback_2fac57aba0
	Present: bool
	Traceable: vspyx.Runtime.Traceable
	def Read(self) -> vspyx.Runtime.Point: ...

	def SetNotPresent(self) -> typing.Any: ...

	class Statistics:
		"""Statistics
		"""
		Present: bool
		Count: int
		CountChangeTime: vspyx.Runtime.Trace.Statistics.ChangeTime
		LastPoint: vspyx.Runtime.Point
		BeforeLastPoint: vspyx.Runtime.Point
		PayloadChangeTimes: typing.List[vspyx.Runtime.Trace.Statistics.ChangeTime]
		def PushPoint(self, point: vspyx.Runtime.Point) -> typing.Any: ...

		def Reset(self) -> typing.Any: ...

		def SetNotPresent(self) -> typing.Any: ...

		class ChangeTime:
			"""ChangeTime
			"""
			@enum.unique
			class Direction(enum.IntEnum):
				NONE = 0
				Up = 1
				Down = 2

			LastTime: typing.Any
			BeforeLastTime: typing.Any
			ChangeDirection: vspyx.Runtime.Trace.Statistics.ChangeTime.Direction

			@typing.overload
			def Push(self, thisTime: typing.Any) -> typing.Any: ...


			@typing.overload
			def Push(self, thisTime: typing.Any, thisChangeDirection: vspyx.Runtime.Trace.Statistics.ChangeTime.Direction) -> typing.Any: ...



class BaseType(vspyx.Core.ResolverObject):
	"""Represents the serializable base type identifier information associated with a given resolvable object
	"""
	"""BaseType
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	Size: int

	@staticmethod
	def New(config: typing.Any) -> vspyx.Runtime.BaseType: ...

	def CloneConfiguration(self) -> typing.Any: ...

class DataDefinition(vspyx.Core.ResolverObject):
	"""DataDefinition gives the definition of how a piece of data
	 should be stored and presented 
	 
	"""
	"""DataDefinition
	"""
	BaseType: vspyx.Runtime.BaseType
	"""Get the base type
		 
	"""

	CompuMethod: vspyx.Runtime.CompuMethod
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	@typing.overload
	def New(baseType: vspyx.Runtime.BaseType, compuMethod: vspyx.Runtime.CompuMethod) -> vspyx.Runtime.DataDefinition: ...


	@staticmethod
	@typing.overload
	def New(config: typing.Any) -> vspyx.Runtime.DataDefinition: ...

	def CloneConfiguration(self) -> typing.Any: ...

class DataTypeMappingSet(vspyx.Core.ResolverObject):
	"""DataTypeMappingSet
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Runtime.DataTypeMappingSet: ...

	def CloneConfiguration(self) -> typing.Any: ...

class DataTypeMapping:
	"""DataTypeMapping
	"""
	ApplicationDataType: vspyx.Runtime.ImplementableDataType
	ImplementationDataType: vspyx.Runtime.ImplementationDataType
	def assign(self, arg0: vspyx.Runtime.DataTypeMapping) -> vspyx.Runtime.DataTypeMapping: ...

class Module(vspyx.Core.Module):
	"""Represents a runtime module
	"""
	"""Module
	"""

class PointCache(vspyx.Core.Object):
	"""Represents a managed collection of cacheable point objects with controlled access to their values
	"""
	"""PointCache
	"""
	MaximumSize: int
	def PullLatestValues(self) -> typing.List[vspyx.Runtime.Point]: ...

class System(vspyx.Core.ResolverObject):
	"""System
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Runtime.System: ...

	def CloneConfiguration(self) -> typing.Any: ...

class Utilization(vspyx.Runtime.Component):
	"""Represents channel utilization statistics
	"""
	"""Utilization
	"""
	Signal: vspyx.Runtime.Signal

	@staticmethod
	@typing.overload
	def New() -> vspyx.Runtime.Utilization: ...


	@staticmethod
	@typing.overload
	def New(averageSamples: int) -> vspyx.Runtime.Utilization: ...

	def AddUtilized(self, percentOfSecond: float) -> typing.Any: ...

