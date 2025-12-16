import typing, enum, vspyx

class Stream:
	"""Stream
	"""
	IsClosed: bool
	def assign(self, arg0: vspyx.IO.Stream) -> vspyx.IO.Stream: ...

	def Close(self) -> typing.Any: ...

	def Clone(self) -> typing.Any: ...

class InputStream(vspyx.IO.Stream):
	"""InputStream
	"""
	AvailableBytes: int
	PositionInfo: typing.Any
	ReadRate: int
	""":Returns: Rate of writing in bytes per millisecond
	 	
	"""

	def Read(self, buffer: typing.Any, len: int) -> int: ...

	def LogReadStatisticOnClose(self, logLevel: vspyx.Core.Logger.Level) -> typing.Any:
		"""Log the read statistics on stream close at the given log level

		:Parameter log: Log level to log the stats to

		"""
		pass


	def ResetReadStatistics(self) -> typing.Any: ...

	class PositionInfo:
		"""PositionInfo
		"""
		LogicalOffset: int
		NativeOffset: int


class OutputStream(vspyx.IO.Stream):
	"""OutputStream
	"""
	WriteRate: int
	""":Returns: Rate of writing in bytes per millisecond
	 	
	"""

	def Flush(self) -> typing.Any: ...

	def Write(self, buffer: typing.Any, len: int) -> int: ...

	def LogWriteStatisticOnClose(self, logLevel: vspyx.Core.Logger.Level) -> typing.Any:
		"""Log the read statistics on stream close at the given log level

		:Parameter log: Log level to log the stats to

		"""
		pass


	def ResetWriteStatistics(self) -> typing.Any: ...

class InputOutputStream(vspyx.IO.InputStream, vspyx.IO.OutputStream):
	"""InputOutputStream
	"""

class SeekableStream(vspyx.IO.Stream):
	"""SeekableStream
	"""
	Position: int
	def Seek(self, offset: int, origin: int) -> typing.Any: ...

class OnChangeParameters:
	"""OnChangeParameters
	"""

class OnChangeReturn:
	"""OnChangeReturn
	"""

class SeekableInputStream(vspyx.IO.InputStream, vspyx.IO.SeekableStream):
	"""SeekableInputStream
	"""
	def SeekNative(self, logicalOffset: int, nativeOffset: int) -> typing.Any: ...

class SeekableOutputStream(vspyx.IO.OutputStream, vspyx.IO.SeekableStream):
	"""SeekableOutputStream
	"""

class FileStream(vspyx.IO.Stream):
	"""FileStream
	"""
	FilePath: str
	Size: int
	UnixModifiedTime: int

class FileInputStream(vspyx.IO.FileStream, vspyx.IO.SeekableInputStream):
	"""FileInputStream
	"""

class FileOutputStream(vspyx.IO.FileStream, vspyx.IO.SeekableOutputStream):
	"""FileOutputStream
	"""

class Filesystem(vspyx.Core.Object):
	"""Filesystem
	"""
	def DirectoryExists(self, path: str) -> bool: ...

	def FileExists(self, path: str) -> bool: ...

	def OpenFileForRead(self, path: str) -> vspyx.IO.FileInputStream: ...

	def OpenFileForWrite(self, path: str) -> vspyx.IO.FileOutputStream: ...


	@typing.overload
	def OpenMemoryMappedFile(self, path: str, writable: bool) -> vspyx.IO.MemoryMappedFile: ...


	@typing.overload
	def OpenMemoryMappedFile(self, path: str, writable: bool, writableFileSize: typing.Any) -> vspyx.IO.MemoryMappedFile: ...

	def EnumerateDirectory(self, path: str) -> typing.List[str]: ...

	def MakeDirectory(self, path: str) -> typing.Any: ...

	def Remove(self, path: str) -> typing.Any: ...

	def RemoveAll(self, path: str) -> typing.Any: ...

	def GetRootNameOfPath(self, path: str) -> str: ...

	def GetRootDirectoryOfPath(self, path: str) -> str: ...

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

	def GetNumericAttribute(self, path: str, key: str) -> vspyx.Core.Numeric: ...

	def GetStringAttribute(self, path: str, key: str) -> str: ...

	def SetNumericAttribute(self, path: str, key: str, value: vspyx.Core.Numeric) -> typing.Any: ...

	def SetStringAttribute(self, path: str, key: str, value: str) -> typing.Any: ...

class SeekableInputOutputStream(vspyx.IO.FileInputStream, vspyx.IO.FileOutputStream):
	"""SeekableInputOutputStream
	"""

class SeekableInputSubstream(vspyx.IO.FileInputStream):
	"""SeekableInputSubstream
	"""
	AvailableBytes: int
	FilePath: str
	IsClosed: bool
	Position: int
	Size: int
	UnixModifiedTime: int
	def Seek(self, offset: int, origin: int) -> typing.Any: ...

	def Read(self, buffer: typing.Any, len: int) -> int: ...

	def Close(self) -> typing.Any: ...

	def Clone(self) -> typing.Any: ...

class BufferedInputStream(vspyx.IO.SeekableInputStream):
	"""BufferedInputStream
	"""

class MemoryInputOutputStream(vspyx.IO.SeekableInputStream, vspyx.IO.SeekableOutputStream):
	"""MemoryInputOutputStream
	"""

class MemoryMappedFile(vspyx.IO.FileStream):
	"""MemoryMappedFile
	"""
	def GetView(self, offset: int, size: int) -> vspyx.Core.BytesView: ...

class Module(vspyx.Core.Module):
	"""Module
	"""
	AppDataFilesystem: vspyx.IO.Filesystem
	AppDataFilesystemRoot: str
	BuiltInFilesystem: vspyx.IO.Filesystem
	BuiltInFilesystemIsOSFilesystem: bool
	BuiltInFilesystemRoot: str
	OSFilesystem: vspyx.IO.Filesystem
	SetupFilesystem: vspyx.IO.Filesystem
	UserFilesystem: vspyx.IO.Filesystem
	UserFilesystemRoot: str

	@staticmethod
	def SetBuiltInFilesystemRootOverride(path: str) -> typing.Any: ...


	@staticmethod
	def SetUserFilesystemRootOverride(path: str) -> typing.Any: ...


	@staticmethod
	def SetAppDataFilesystemRootOverride(path: str) -> typing.Any: ...

	def NewTemporaryFilesystem(self) -> vspyx.IO.Filesystem: ...

	def NewChrootFilesystem(self, systemPath: str) -> vspyx.IO.Filesystem: ...

	def OpenFileForRead(self, path: str) -> vspyx.IO.FileInputStream: ...

	def OpenFileForWrite(self, path: str) -> vspyx.IO.FileOutputStream: ...


	@typing.overload
	def OpenMemoryMappedFile(self, path: str, writable: bool) -> vspyx.IO.MemoryMappedFile: ...


	@typing.overload
	def OpenMemoryMappedFile(self, path: str, writable: bool, writableFileSize: typing.Any) -> vspyx.IO.MemoryMappedFile: ...

class SeekableOutputSubstream(vspyx.IO.FileOutputStream):
	"""SeekableOutputSubstream
	"""
	FilePath: str
	IsClosed: bool
	Position: int
	Size: int
	UnixModifiedTime: int
	def Seek(self, offset: int, origin: int) -> typing.Any: ...

	def Write(self, buffer: typing.Any, len: int) -> int: ...

	def Flush(self) -> typing.Any: ...

	def Close(self) -> typing.Any: ...

	def Clone(self) -> typing.Any: ...

class TextReader(vspyx.Core.Object):
	"""TextReader
	"""
	@enum.unique
	class Encoding(enum.IntEnum):
		UTF8 = 0
		UTF16_LITTLE_ENDIAN = 1
		UTF16_BIG_ENDIAN = 2
		UTF32_LITTLE_ENDIAN = 3
		UTF32_BIG_ENDIAN = 4

	LastReadLine: str

	@staticmethod
	@typing.overload
	def New(source: vspyx.IO.SeekableInputStream) -> vspyx.IO.TextReader:
		"""Create a new TextReader and attempt to detect encoding

		The encoding will be set automatically by checking for a BOM. 
		The source stream should be at the beginning of a file.
		If no BOM is found, UTF-8 will be assumed

		"""
		pass



	@staticmethod
	@typing.overload
	def New(source: vspyx.IO.InputStream, encoding: vspyx.IO.TextReader.Encoding) -> vspyx.IO.TextReader:
		"""Create a new TextReader with the specified encoding


		"""
		pass


	def ReadNextLineIfAvailable(self) -> bool: ...

@enum.unique
class Mode(enum.IntEnum):
	Read = 0
	Write = 1
	Append = 2
	UpdateRead = 3
	UpdateWrite = 4
	UpdateAppend = 5

class ZstdOutputStream(vspyx.IO.OutputStream):
	"""ZstdOutputStream
	"""

	@staticmethod
	def InputBufferSize() -> int: ...


	@staticmethod
	def OutputBufferSize() -> int: ...

	def SetCompressionLevel(self, level: int) -> typing.Any: ...

