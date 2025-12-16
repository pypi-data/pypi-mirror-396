import typing, enum, vspyx

class OutputFormat(vspyx.Core.Object):
	"""OutputFormat
	"""
	@enum.unique
	class Stage(enum.IntEnum):
		BeforePreProcess = 0
		AfterPreProcess = 1
		BeforeProcess = 2
		AfterProcess = 3

	def OnStage(self, environment: vspyx.Runtime.Environment, scheduler: vspyx.Runtime.Scheduler, stage: vspyx.Exporter.OutputFormat.Stage) -> typing.Any: ...

	def Process(self, point: vspyx.Runtime.Point, progress: float) -> typing.Any: ...

	def NeedsPreProcess(self) -> bool: ...

	def PreProcess(self, point: vspyx.Runtime.Point, progress: float) -> typing.Any: ...

class CSVOutputFormat(vspyx.Exporter.OutputFormat):
	"""CSVOutputFormat
	"""

@enum.unique
class FileType(enum.IntEnum):
	Capture = 0
	Script = 1
	Persistent = 2
	Audio = 3
	Manual = 4
	Raw = 5
	Last = 6

@enum.unique
class NetworkType(enum.IntEnum):
	NONE = 0
	Cellular = 2
	WiFi = 4
	Ethernet = 6

class UploadInfo:
	"""UploadInfo
	"""
	uploadType: vspyx.Exporter.FileType
	startSector: int
	startTimestamp: int
	captureIndex: int
	scriptChecksum: str
	uploadChecksum: str
	coreminiCreateTime: int
	coreminiVersion: int
	tripId: str
	vin: str

class ResumeOffsets:
	"""ResumeOffsets
	"""
	logicalOffset: int
	nativeOffset: int

class DataFile:
	"""DataFile
	"""
	ID: vspyx.Frames.VSA.FileId
	NetType: vspyx.Exporter.NetworkType
	Path: str
	Primary: int
	Secondary: int
	Type: vspyx.Exporter.FileType
	def HasNetType(self, netType: vspyx.Exporter.NetworkType) -> bool: ...

	def AddNetType(self, netType: vspyx.Exporter.NetworkType) -> typing.Any: ...

	def MarkUploaded(self, filesystem: vspyx.IO.Filesystem) -> typing.Any: ...

	def OpenInputStream(self, seekLocation: int, filesystem: vspyx.IO.Filesystem, resumeInfo: typing.Any) -> vspyx.IO.InputStream: ...

	def GetUploadInfo(self, filesystem: vspyx.IO.Filesystem) -> vspyx.Exporter.UploadInfo: ...

	def ToStringStream(self, filesystem: vspyx.IO.Filesystem) -> typing.Any: ...

	def RequiresScript(self) -> bool: ...

	def __eq__(self, rhs: vspyx.Exporter.DataFile) -> bool: ...

class DataFileComparator:
	"""DataFileComparator
	"""
	def assign(self, arg0: vspyx.Exporter.DataFileComparator) -> vspyx.Exporter.DataFileComparator: ...

	def __call__(self, fileA: vspyx.Exporter.DataFile, fileB: vspyx.Exporter.DataFile) -> bool: ...

class DefaultComparator(vspyx.Exporter.DataFileComparator):
	"""DefaultComparator
	"""
	def __call__(self, fileA: vspyx.Exporter.DataFile, fileB: vspyx.Exporter.DataFile) -> bool: ...

class VSAComparator(vspyx.Exporter.DataFileComparator):
	"""VSAComparator
	"""
	def __call__(self, fileA: vspyx.Exporter.DataFile, fileB: vspyx.Exporter.DataFile) -> bool: ...

class DBOutputFormat(vspyx.Exporter.OutputFormat):
	"""DBOutputFormat
	"""

class VSADataFile(vspyx.Exporter.DataFile):
	"""VSADataFile
	"""
	ID: vspyx.Frames.VSA.FileId
	def MarkUploaded(self, filesystem: vspyx.IO.Filesystem) -> typing.Any: ...

	def OpenInputStream(self, seekLocation: int, filesystem: vspyx.IO.Filesystem, resumeOffsets: typing.Any) -> vspyx.IO.InputStream: ...

	def RequiresScript(self) -> bool: ...

class AudioDataFile(vspyx.Exporter.VSADataFile):
	"""AudioDataFile
	"""
	def GetUploadInfo(self, filesystem: vspyx.IO.Filesystem) -> vspyx.Exporter.UploadInfo: ...

	def ToStringStream(self, filesystem: vspyx.IO.Filesystem) -> typing.Any: ...

	def RequiresScript(self) -> bool: ...

class CaptureDataFile(vspyx.Exporter.VSADataFile):
	"""CaptureDataFile
	"""
	def GetUploadInfo(self, filesystem: vspyx.IO.Filesystem) -> vspyx.Exporter.UploadInfo: ...

	def ToStringStream(self, filesystem: vspyx.IO.Filesystem) -> typing.Any: ...

	def RequiresScript(self) -> bool: ...

class ManualDataFile(vspyx.Exporter.VSADataFile):
	"""ManualDataFile
	"""
	def GetUploadInfo(self, filesystem: vspyx.IO.Filesystem) -> vspyx.Exporter.UploadInfo: ...

	def ToStringStream(self, filesystem: vspyx.IO.Filesystem) -> typing.Any: ...

	def RequiresScript(self) -> bool: ...

class PersistentDataFile(vspyx.Exporter.VSADataFile):
	"""PersistentDataFile
	"""
	def GetUploadInfo(self, filesystem: vspyx.IO.Filesystem) -> vspyx.Exporter.UploadInfo: ...

	def ToStringStream(self, filesystem: vspyx.IO.Filesystem) -> typing.Any: ...

	def RequiresScript(self) -> bool: ...

class RawDataFile(vspyx.Exporter.VSADataFile):
	"""RawDataFile
	"""
	def GetUploadInfo(self, filesystem: vspyx.IO.Filesystem) -> vspyx.Exporter.UploadInfo: ...

	def ToStringStream(self, filesystem: vspyx.IO.Filesystem) -> typing.Any: ...

class ScriptDataFile(vspyx.Exporter.VSADataFile):
	"""ScriptDataFile
	"""
	def MarkUploaded(self, filesystem: vspyx.IO.Filesystem) -> typing.Any: ...

	def GetUploadInfo(self, filesystem: vspyx.IO.Filesystem) -> vspyx.Exporter.UploadInfo: ...

	def ToStringStream(self, filesystem: vspyx.IO.Filesystem) -> typing.Any: ...

class DataQueue:
	"""DataQueue
	"""
	AllPaths: typing.List[str]
	def assign(self, arg0: vspyx.Exporter.DataQueue) -> vspyx.Exporter.DataQueue: ...

	def Add(self, file: vspyx.Exporter.DataFile) -> typing.Any: ...

	def Remove(self, file: vspyx.Exporter.DataFile) -> bool: ...

	def Clear(self) -> typing.Any: ...

	def HasFile(self, file: vspyx.Exporter.DataFile) -> bool: ...

	def Size(self) -> int: ...


	@typing.overload
	def GetNext(self) -> vspyx.Exporter.DataFile: ...


	@typing.overload
	def GetNext(self, netType: vspyx.Exporter.NetworkType) -> vspyx.Exporter.DataFile: ...

	def Get(self, path: str) -> vspyx.Exporter.DataFile: ...

class QueueModifier:
	"""QueueModifier
	"""
	OnAddDataFile: vspyx.Core.Callback_abb7f0dc96
	OnOverwrittenDataFile: vspyx.Core.Callback_abb7f0dc96
	OnRemoveDataFile: vspyx.Core.Callback_abb7f0dc96
	OnSyncDataFiles: vspyx.Core.Callback_bb99a2e43e
	OnUpdateDataFile: vspyx.Core.Callback_abb7f0dc96

class RunningQueueModifier(vspyx.Exporter.QueueModifier):
	"""RunningQueueModifier
	"""
	def Start(self) -> typing.Any: ...

	def Stop(self) -> typing.Any: ...

class OneshotQueueModifier(vspyx.Exporter.QueueModifier):
	"""OneshotQueueModifier
	"""
	def Execute(self) -> typing.Any: ...

class AddQueueSubscriber:
	"""AddQueueSubscriber
	"""
	OnAddDataFile: vspyx.Core.Callback_abb7f0dc96

class RemoveQueueSubscriber:
	"""RemoveQueueSubscriber
	"""
	OnRemoveDataFile: vspyx.Core.Callback_abb7f0dc96

class EmptyQueueSubscriber:
	"""EmptyQueueSubscriber
	"""
	OnEmptyQueue: vspyx.Core.Callback_634bd5c449

class OverwrittenQueueSubscriber:
	"""OverwrittenQueueSubscriber
	"""
	OnOverwrittenDataFile: vspyx.Core.Callback_abb7f0dc96

class QueueManager:
	"""QueueManager
	"""
	AllPaths: typing.List[str]
	def assign(self, arg0: vspyx.Exporter.QueueManager) -> vspyx.Exporter.QueueManager: ...


	@typing.overload
	def GetNext(self) -> vspyx.Exporter.DataFile: ...


	@typing.overload
	def GetNext(self, type: vspyx.Exporter.NetworkType) -> vspyx.Exporter.DataFile: ...

	def Get(self, path: str) -> vspyx.Exporter.DataFile: ...

	def Size(self) -> int: ...

	def Clear(self) -> typing.Any: ...

	def HasFile(self, file: vspyx.Exporter.DataFile) -> bool: ...

	def GetNumberFilesOfNetType(self, netType: vspyx.Exporter.NetworkType) -> int: ...

	def Start(self) -> typing.Any: ...

	def Stop(self) -> typing.Any: ...

class DataProcessor:
	"""DataProcessor
	"""
	ProcessTask: vspyx.Core.Task_a3295bec43

class MDFOutputFormat(vspyx.Exporter.OutputFormat):
	"""MDFOutputFormat
	"""

	@staticmethod
	@typing.overload
	def Sort(inputPath: str, outputPath: str) -> typing.Any: ...


	@staticmethod
	@typing.overload
	def Sort(inputPath: str, outputPath: str, doColumnOriented: bool) -> typing.Any: ...

class Module(vspyx.Core.Module):
	"""Module
	"""

	@typing.overload
	def Export(self, bufferPath: str, databasePaths: typing.List[str], output: vspyx.Exporter.OutputFormat) -> bool: ...


	@typing.overload
	def Export(self, bufferPath: str, databasePaths: typing.List[str], output: vspyx.Exporter.OutputFormat, connectionsConfigPath: str) -> bool: ...


	@typing.overload
	def Export(self, bufferPath: str, databasePaths: typing.List[str], outputPath: str) -> bool: ...


	@typing.overload
	def Export(self, bufferPath: str, databasePaths: typing.List[str], outputPath: str, connectionsConfigPath: str) -> bool: ...


	@typing.overload
	def Export(self, bufferPath: str, databasePaths: typing.List[str], outputPath: str, connectionsConfigPath: str, signalsOnly: bool) -> bool: ...

class AddSelectionQueueModifier(vspyx.Exporter.OneshotQueueModifier):
	"""AddSelectionQueueModifier
	"""

class AddWatchQueueModifier(vspyx.Exporter.RunningQueueModifier):
	"""AddWatchQueueModifier
	"""

class OverwrittenWatchQueueModifier(vspyx.Exporter.RunningQueueModifier):
	"""OverwrittenWatchQueueModifier
	"""

class RemoveSelectionQueueModifier(vspyx.Exporter.OneshotQueueModifier):
	"""RemoveSelectionQueueModifier
	"""

class SyncSelectionQueueModifier(vspyx.Exporter.OneshotQueueModifier):
	"""SyncSelectionQueueModifier
	"""

class UpdateSelectionQueueModifier(vspyx.Exporter.OneshotQueueModifier):
	"""UpdateSelectionQueueModifier
	"""

class UploadedQueueModifier(vspyx.Exporter.OneshotQueueModifier):
	"""UploadedQueueModifier
	"""

