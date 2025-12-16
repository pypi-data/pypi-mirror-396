import typing, enum, vspyx

@enum.unique
class Directory(enum.IntEnum):
	Captures = 0
	Scripts = 1
	PersistentFiles = 2
	ManualFiles = 3
	RawDataFiles = 4
	AudioFiles = 5
	CurrentScript = 6
	OverwrittenCaptures = 7
	Last = 8

@enum.unique
class NumericAttribute(enum.IntEnum):
	Timestamp = 0
	EndTimestamp = 1
	Size = 2
	Priority = 3
	WiFi = 4
	Cellular = 5
	StartSector = 6
	EndSector = 7
	Uploaded = 8
	CoreMiniCreateTime = 9
	CoreMiniVersion = 10
	CaptureIndex = 11
	Overwritten = 12
	BackupTimestamp = 13
	Last = 14

@enum.unique
class StringAttribute(enum.IntEnum):
	FileId = 0
	Name = 1
	FileName = 2
	ScriptChecksum = 3
	CaptureType = 4
	FileType = 5
	UploadChecksum = 6
	TripId = 7
	VIN = 8
	Last = 9

@enum.unique
class FileType(enum.IntEnum):
	Script = 0
	Persistent = 1
	Capture = 2
	Audio = 3
	Manual = 4
	Raw = 5
	Last = 6

@enum.unique
class UploadPriority(enum.IntEnum):
	Script = 0
	Persistent = 1
	Immediate = 2
	High = 3
	Medium = 4
	Normal = 5

class FileId:
	"""FileId
	"""
	CaptureIndex: int
	StartSector: int
	Timestamp: vspyx.Runtime.Timestamp
	UnixTimestamp: int
	def assign(self, arg0: vspyx.Frames.VSA.FileId) -> vspyx.Frames.VSA.FileId: ...

	def __str__(self) -> str: ...

class Record:
	"""Record
	"""
	Header: int
	Index: int
	SequenceNumber: int
	Timestamp: vspyx.Runtime.Timestamp
	def assign(self, arg0: vspyx.Frames.VSA.Record) -> vspyx.Frames.VSA.Record: ...

	def IsValidRecordForPreTrigger(self, functionBlockId: int) -> bool: ...

	def HasValidChecksum(self) -> bool: ...

	def MatchesCaptureMask(self, captureMask: int) -> bool: ...

	def UpdateCaptureMask(self, captureMask: int) -> typing.Any: ...

	def IsExtendedRecord(self) -> bool: ...

class VIN:
	"""VIN
	"""
	mVin: str
	mTimestamp: vspyx.Runtime.Timestamp

class VSAFile:
	"""VSAFile
	"""
	AccessorNumericAttributes: typing.List[vspyx.Frames.VSA.NumericAttribute]
	AccessorStringAttributes: typing.List[vspyx.Frames.VSA.StringAttribute]
	AssociatedFiles: typing.List[str]
	BackupTimestamp: vspyx.Runtime.Timestamp
	CaptureIndex: int
	CoreMiniCreateTime: vspyx.Runtime.Timestamp
	EndPosition: int
	EndSector: int
	EndTimestamp: vspyx.Runtime.Timestamp
	FileId: vspyx.Frames.VSA.FileId
	"""String Attributes *
	"""

	FileName: str
	FileType: vspyx.Frames.VSA.FileType
	MutatorNumericAttributes: typing.List[vspyx.Frames.VSA.NumericAttribute]
	MutatorStringAttributes: typing.List[vspyx.Frames.VSA.StringAttribute]
	Name: str
	Priority: vspyx.Frames.VSA.UploadPriority
	ScriptChecksum: str
	Size: int
	StartPosition: int
	StartSector: int
	Timestamp: vspyx.Runtime.Timestamp
	"""Numeric Attributes *
	"""

	TripId: str
	UploadChecksum: str
	VIN: vspyx.Frames.VSA.VIN
	def IsWiFi(self) -> bool: ...

	def SetWiFi(self, wiFi: bool) -> typing.Any: ...

	def IsCellular(self) -> bool: ...

	def SetCellular(self, cellular: bool) -> typing.Any: ...

	def IsOverwritten(self) -> bool: ...

	def SetOverwritten(self, overwritten: bool) -> typing.Any: ...

	def IsUploaded(self) -> bool: ...

	def IsPrePost(self) -> bool: ...

	def NeedsScript(self) -> bool:
		"""Filesystem related *
		"""
		pass


	def HasAssociatedFile(self, file: vspyx.Frames.VSA.VSAFile) -> bool: ...

	def AddAssociatedFile(self, file: vspyx.Frames.VSA.VSAFile) -> typing.Any: ...

	def RemoveAssociatedFile(self, file: vspyx.Frames.VSA.VSAFile) -> typing.Any: ...

class SecondSource:
	"""SecondSource
	"""
	Files: typing.List[vspyx.Frames.VSA.VSAFile]
	OnFileAddedCallback: vspyx.Core.Callback_8c5c190ae4
	def Remove(self, path: str) -> typing.Any: ...

	def OpenFileForRead(self, path: str) -> vspyx.IO.FileInputStream: ...

	def OpenFileForWrite(self, path: str) -> vspyx.IO.FileOutputStream: ...

class AudioSource(vspyx.Frames.VSA.SecondSource):
	"""AudioSource
	"""
	Files: typing.List[vspyx.Frames.VSA.VSAFile]
	def Remove(self, path: str) -> typing.Any: ...

	def OpenFileForRead(self, path: str) -> vspyx.IO.FileInputStream: ...

	def OpenFileForWrite(self, path: str) -> vspyx.IO.FileOutputStream: ...

class CoreminiHeaderNotFound(typing.Any):
	"""CoreminiHeaderNotFound
	"""

class Coremini:
	"""Coremini
	"""
	CollectionNames: typing.List[str]
	CreateTime: vspyx.Runtime.Timestamp
	EncryptedMode: bool
	EncryptedSize: int
	FirstLogSector: int
	Hash: vspyx.Core.BytesView
	PersistentLogDataOffset: int
	PersistentLogDataSector: int
	ReadBinSizeSectors: int
	ReadBinStartSector: int
	RootDirectorySector: int
	RootDirectorySize: int
	TripCollectionIndex: int
	Version: int
	def assign(self, arg0: vspyx.Frames.VSA.Coremini) -> vspyx.Frames.VSA.Coremini: ...


	@staticmethod
	def GetVersion(inputStream: vspyx.IO.FileInputStream) -> int: ...

	def GetCollectionName(self, functionBlockIndex: int) -> str: ...

	def HasEnhancedRootDirectory(self) -> bool: ...

	def GenerateBinary(self) -> vspyx.Core.BytesView: ...


	@staticmethod
	def GetCoreminiNetId(record: int) -> int: ...


	@staticmethod
	def GetChecksum(bytes: typing.List[int], filesize: int) -> int: ...

class VSADirectory:
	"""VSADirectory
	"""
	AllPaths: typing.List[str]
	def Size(self) -> int: ...

	def FileExists(self, path: str) -> bool: ...

	def GetFile(self, path: str) -> vspyx.Frames.VSA.VSAFile: ...

	def AddFile(self, file: vspyx.Frames.VSA.VSAFile) -> bool: ...

	def RemoveFile(self, path: str) -> bool: ...

	def Enumerate(self, path: str) -> typing.List[str]: ...

class VSAFilesystem(vspyx.IO.Filesystem):
	"""VSAFilesystem
	"""
	def DirectoryExists(self, path: str) -> bool: ...

	def FileExists(self, path: str) -> bool: ...

	def OpenFileForRead(self, path: str) -> vspyx.IO.FileInputStream: ...

	def OpenFileForWrite(self, path: str) -> vspyx.IO.FileOutputStream: ...

	def OpenMemoryMappedFile(self, path: str, writable: bool, writableFileSize: typing.Any) -> vspyx.IO.MemoryMappedFile: ...

	def EnumerateDirectory(self, path: str) -> typing.List[str]: ...

	def MakeDirectory(self, path: str) -> typing.Any: ...

	def Remove(self, path: str) -> typing.Any: ...

	def RemoveAll(self, path: str) -> typing.Any: ...

	def GetRootDirectoryOfPath(self, path: str) -> str: ...

	def GetRootNameOfPath(self, path: str) -> str: ...

	def GetRootPathOfPath(self, path: str) -> str: ...

	def GetFilenameOfPath(self, path: str) -> str: ...

	def GetStemOfPath(self, path: str) -> str: ...

	def GetExtensionOfPath(self, path: str) -> str: ...

	def GetParentPathOfPath(self, path: str) -> str: ...

	def AbsolutePath(self, path: str) -> str: ...

	def CanonicalPath(self, path: str) -> str: ...

	def RelativePath(self, relativeFrom: str, path: str) -> str: ...

	def SystemAbsolutePath(self, path: str) -> str: ...

	def PathIsAbsolute(self, path: str) -> bool: ...

	def PathIsRelative(self, path: str) -> bool: ...

	def ComparePaths(self, path1: str, path2: str) -> int: ...

	def CombinePaths(self, path1: str, path2: str) -> str: ...


	@typing.overload
	def GetNumericAttribute(self, path: str, key: str) -> vspyx.Core.Numeric: ...


	@typing.overload
	def GetNumericAttribute(self, path: str, attr: vspyx.Frames.VSA.NumericAttribute) -> vspyx.Core.Numeric: ...


	@typing.overload
	def GetStringAttribute(self, path: str, key: str) -> str: ...


	@typing.overload
	def GetStringAttribute(self, path: str, attr: vspyx.Frames.VSA.StringAttribute) -> str: ...

	def SetNumericAttribute(self, path: str, key: str, value: vspyx.Core.Numeric) -> typing.Any: ...

	def SetStringAttribute(self, path: str, key: str, value: str) -> typing.Any: ...

class DynamicFilesystem(vspyx.Frames.VSA.VSAFilesystem):
	"""DynamicFilesystem
	"""
	OnRootDirectoryEntryChanged: vspyx.Core.Callback_a468f1a1f6
	def SetPrintHexDebug(self, printDebug: bool) -> typing.Any: ...


	@typing.overload
	def AddManualUploads(self, rangeStartSector: int, rangeEndSector: int, captureMask: int) -> int: ...


	@typing.overload
	def AddManualUploads(self, rangeStartTime: vspyx.Runtime.Timestamp, rangeEndTime: vspyx.Runtime.Timestamp, captureMask: int) -> int: ...

	def AddExistingManualUpload(self, startSector: int, endSector: int, startTime: vspyx.Runtime.Timestamp, endTime: vspyx.Runtime.Timestamp, captureMask: int, scriptChecksum: str) -> bool: ...

	def AddRawUpload(self, startSector: int, endSector: int) -> bool: ...

class RecordFilterInputStream(vspyx.IO.FileInputStream):
	"""RecordFilterInputStream
	"""

class StaticFilesystem(vspyx.Frames.VSA.VSAFilesystem):
	"""StaticFilesystem
	"""

class StreamOnChangeParameters(vspyx.IO.OnChangeParameters):
	"""StreamOnChangeParameters
	"""
	CaptureIndex: int
	EndSector: int
	PreTriggerSize: int
	Priority: int
	StartSector: int
	def IsPrePost(self) -> bool: ...

	def IsPreTime(self) -> bool: ...

	def IsCellularEnabled(self) -> bool: ...

	def IsWiFIEnabled(self) -> bool: ...

