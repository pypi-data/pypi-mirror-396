import typing, enum, vspyx

class Highlight:
	"""Highlight
	"""
	@enum.unique
	class EType(enum.IntEnum):
		NONE = 0
		Change = 1
		Callout = 2

	@enum.unique
	class EDirectionHint(enum.IntEnum):
		NONE = 0
		Up = 1
		Down = 2
		Left = 3
		Right = 4
		Indeterminite = 5

	Type: vspyx.MonitorView.Highlight.EType
	DirectionHint: vspyx.MonitorView.Highlight.EDirectionHint
	ChangedAgo: typing.Any
	LastChangedAgo: typing.Any
	Index: int

class AnnotatedValue:
	"""AnnotatedValue
	"""
	Data: vspyx.Runtime.Value
	Highlighting: typing.List[vspyx.MonitorView.Highlight]
	Units: str
	def __str__(self) -> str: ...

class Column(vspyx.Core.Object):
	"""Column
	"""
	ID: str

	@typing.overload
	def GetValue(self, uLine: vspyx.MonitorView.Line) -> vspyx.MonitorView.AnnotatedValue: ...


	@typing.overload
	def GetValue(self, line: vspyx.MonitorView.Line) -> vspyx.MonitorView.AnnotatedValue: ...

	def CloneState(self) -> typing.Any: ...

	def UpdateState(self, state: typing.Any) -> typing.Any: ...

class Line(vspyx.Core.Object):
	"""Line
	"""
	Children: typing.List[vspyx.MonitorView.Line]
	Count: int
	Description: str
	ID: int
	Name: str
	Parents: typing.List[vspyx.MonitorView.Line]
	Point: vspyx.Runtime.Point
	RelativeTimestamp: typing.Any
	RenderLineCount: int
	Statistics: vspyx.Runtime.Trace.Statistics
	def Serialize(self, columns: typing.List[vspyx.MonitorView.Column], dataBytesLimit: int) -> typing.Any: ...

	def ChildrenCount(self) -> int: ...

	def ParentsCount(self) -> int: ...

	def __str__(self) -> str: ...

class Instance(vspyx.Runtime.Component):
	"""Instance
	"""
	@enum.unique
	class ScrollModes(enum.IntEnum):
		Static = 0
		Scrolling = 1

	@enum.unique
	class TimestampModes(enum.IntEnum):
		Relative = 0
		Absolute = 1

	@enum.unique
	class NameModes(enum.IntEnum):
		Short = 0
		Long = 1

	@enum.unique
	class SortingModes(enum.IntEnum):
		NoSorting = 0
		Ascending = 1
		Descending = 2

	Columns: typing.List[vspyx.MonitorView.Column]
	DesiredLevel: vspyx.Runtime.PointLevel
	InReviewBuffer: bool
	MinimumLevel: vspyx.Runtime.PointLevel
	NameMode: vspyx.MonitorView.Instance.NameModes
	NumberOfLines: int
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	Paused: bool
	PercentBufferFilled: float
	PercentBufferPosition: float
	ScrollMode: vspyx.MonitorView.Instance.ScrollModes
	SortColumn: vspyx.MonitorView.Column
	SortMode: vspyx.MonitorView.Instance.SortingModes
	TimestampMode: vspyx.MonitorView.Instance.TimestampModes

	@staticmethod
	@typing.overload
	def New() -> vspyx.MonitorView.Instance: ...

	def SetupFromCommunicationComponent(self, component: vspyx.Communication.Component) -> typing.Any: ...

	def SetupFromBuffer(self, buffer: str) -> vspyx.Core.ScheduledTask_ef25277eaf: ...

	def Clear(self) -> typing.Any: ...

	def Save(self, path: str) -> typing.Any: ...

	def GetLines(self, start: int, num: int) -> typing.List[vspyx.MonitorView.Line]:
		"""Make the lines of the monitor

		:Parameter start: line number to begin returning from; set to 0 in scrolling mode to get latest lines
		:Parameter num: number of lines
		:Returns: the lines

		"""
		pass


	def RemoveFilter(self, id: str) -> bool: ...

	def AddFilter(self, name: str, mode: int, expression: str) -> typing.Any: ...

	def UpdateFilter(self, id: str, name: str, mode: int, expression: str) -> bool: ...


	@staticmethod
	@typing.overload
	def New(config: typing.Any) -> vspyx.MonitorView.Instance: ...

	def CloneConfiguration(self) -> typing.Any: ...

class Module(vspyx.Core.Module):
	"""Module
	"""

