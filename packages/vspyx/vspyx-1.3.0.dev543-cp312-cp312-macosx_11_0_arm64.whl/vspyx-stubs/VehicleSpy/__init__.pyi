import typing, enum, vspyx

class Database(vspyx.Core.ResolverObject):
	"""Database
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	Topology: vspyx.Communication.Topology
	def Load(self) -> vspyx.Core.Task_a3295bec43: ...

	def UpdateAutomaticMappings(self) -> typing.Any: ...

	def AddAutomaticMapping(self, channelURI: str, driverMatch: str) -> typing.Any: ...

	def RemoveAutomaticMapping(self, channelURI: str) -> typing.Any: ...

	def SetAutomaticMapping(self, channelURI: str, driverMatch: str) -> typing.Any: ...

	def ClearAutomaticMappings(self) -> typing.Any: ...


	@staticmethod
	def New(config: typing.Any) -> vspyx.VehicleSpy.Database: ...

	def CloneConfiguration(self) -> typing.Any: ...

class DatabaseOpener(vspyx.Core.ResolverObject):
	"""DatabaseOpener
	"""
	def CanOpen(self, path: str) -> bool: ...

	def Open(self, path: str) -> vspyx.Core.Task_ca7052f7e4: ...

class Observer(vspyx.Communication.Architecture):
	"""Observer
	"""

	@staticmethod
	def New() -> vspyx.VehicleSpy.Observer: ...

class Module(vspyx.Core.Module):
	"""Module
	"""
	AvailableSources: vspyx.Core.ResolverOwningCollection
	Databases: vspyx.Core.ResolverOwningCollection
	IsRunning: bool
	Objects: vspyx.Core.ResolverOwningCollection
	Observer: vspyx.VehicleSpy.Observer
	"""The Observer is an element in the Environment that we create and attach
	 to every channel in the topology.
	 
	 Its purpose is to be all-seeing of network traffic in the
	 application, and provide the Runtime::Environment that the
	 MonitorView and other such views can watch.
		 
	"""

	OnAfterFileLoadOrClear: vspyx.Core.Callback_6ee07abf48
	OnAfterStartRunning: vspyx.Core.Callback_2cfb0f7969
	OnAfterStopRunning: vspyx.Core.Callback_634bd5c449
	OnBeforeFileLoadOrClear: vspyx.Core.Callback_634bd5c449
	OnBeforeStartRunning: vspyx.Core.Callback_634bd5c449
	OnBeforeStopRunning: vspyx.Core.Callback_634bd5c449
	Scheduler: vspyx.Runtime.Scheduler
	def New(self) -> typing.Any: ...

	def SaveAs(self, path: str) -> typing.Any: ...

	def ReviewBuffer(self, path: str) -> vspyx.Core.ScheduledTask_ef25277eaf: ...


	@typing.overload
	def PrepareForStart(self) -> vspyx.VehicleSpy.Observer: ...


	@typing.overload
	def PrepareForStart(self, analysisMode: bool) -> vspyx.VehicleSpy.Observer: ...


	@typing.overload
	def PrepareForStart(self, analysisMode: bool, ticker: vspyx.Runtime.SchedulerTicker) -> vspyx.VehicleSpy.Observer: ...

	def Start(self) -> vspyx.VehicleSpy.Observer: ...

	def Stop(self) -> typing.Any: ...


	@typing.overload
	def AddSource(self, description: str) -> vspyx.Communication.SourceHandle: ...

	def RemoveSource(self, handle: vspyx.Communication.SourceHandle) -> typing.Any: ...


	@typing.overload
	def AddSource(self, instance: vspyx.Communication.SourceHandle) -> typing.Any: ...

	def AddDatabaseOpener(self, opener: vspyx.VehicleSpy.DatabaseOpener) -> typing.Any: ...

	def AddDatabase(self, path: str) -> vspyx.VehicleSpy.Database: ...

	def RefreshAvailableSources(self) -> typing.Any: ...

	def CloneState(self) -> typing.Any: ...

	def UpdateState(self, state: typing.Any) -> typing.Any: ...

