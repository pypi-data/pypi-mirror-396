import typing, enum, vspyx

class FieldInstance(vspyx.Core.Object):
	"""FieldInstance
	"""
	@enum.unique
	class FormatTypes(enum.IntEnum):
		NONE = 0
		DEFAULT = 1
		HEX = 2
		DECIMAL = 4
		HEX_DECIMAL = 6
		TRUE_FALSE = 8
		FALSE_TRUE = 16
		SHORT_FORMAT = 32
		LONG_FORMAT = 64
		SHORT_NAME = 128

	Children: typing.List[vspyx.Dissector.FieldInstance]
	DefaultFormat: vspyx.Dissector.FieldInstance.FormatTypes
	End: typing.Any
	Field: vspyx.Dissector.Field
	Size: typing.Any
	SourceMessage: vspyx.Dissector.Message
	Start: typing.Any
	Value: typing.Any

	@typing.overload
	def AsString(self) -> str: ...


	@typing.overload
	def AsString(self, formatBitField: vspyx.Dissector.FieldInstance.FormatTypes) -> str: ...

	def GetChild(self, tag: vspyx.Dissector.Tag) -> vspyx.Dissector.FieldInstance: ...


	@staticmethod
	def NumericAsString(formatBitField: vspyx.Dissector.FieldInstance.FormatTypes, inst: vspyx.Dissector.FieldInstance) -> str: ...


	@staticmethod
	def MACAddressAsString(requestedFormatType: vspyx.Dissector.FieldInstance.FormatTypes, inst: vspyx.Dissector.FieldInstance) -> str: ...

	class State:
		"""State
		"""
		Description: str
		End: vspyx.Core.Numeric
		Name: str
		Start: vspyx.Core.Numeric


class ProtocolInstance(vspyx.Dissector.FieldInstance):
	"""ProtocolInstance
	"""
	def GetChildValue(self, tag: vspyx.Dissector.Tag) -> typing.Any: ...

	def GetChildSize(self, tag: vspyx.Dissector.Tag) -> typing.Any: ...

	def GetChildStart(self, tag: vspyx.Dissector.Tag) -> typing.Any: ...

	def GetChildEnd(self, tag: vspyx.Dissector.Tag) -> typing.Any: ...

class Field(vspyx.Core.Object):
	"""Field
	"""
	LongName: str
	ShortName: str
	Tag: vspyx.Dissector.Tag
	def __eq__(self, rhs: vspyx.Dissector.Field) -> bool: ...

class Expression(vspyx.Core.Object):
	"""Expression
	"""

	@staticmethod
	@typing.overload
	def GenExpression(numeric: vspyx.Core.Numeric) -> vspyx.Dissector.Expression: ...


	@staticmethod
	@typing.overload
	def GenExpression(str: str) -> vspyx.Dissector.Expression: ...

	class Token:
		"""Token
		"""
		@enum.unique
		class TokenType(enum.IntEnum):
			Operator = 0
			Operand = 1
			Variable = 2
			Tokens = 3

		@enum.unique
		class OperatorType(enum.IntEnum):
			Add = 0
			Subtract = 1
			Divide = 2
			Multiply = 3
			Power = 4
			Equal = 5
			NotEqual = 6
			GreaterThen = 7
			GreaterThenEqualTo = 8
			LessThen = 9
			LessThenEqualTo = 10
			Or = 11
			And = 12
			Not = 13

		@enum.unique
		class VariableType(enum.IntFlag):
			Value = 0
			Start = 1
			End = 2
			Length = 3

		Operand: vspyx.Core.Numeric
		Operator: vspyx.Dissector.Expression.Token.OperatorType
		Variable: vspyx.Dissector.Tag
		def assign(self, arg0: vspyx.Dissector.Expression.Token) -> vspyx.Dissector.Expression.Token: ...

		def GetTokenType(self) -> vspyx.Dissector.Expression.Token.TokenType: ...

		def GetVariableType(self) -> vspyx.Dissector.Expression.Token.VariableType: ...


class Protocol(vspyx.Dissector.Field):
	"""Protocol
	"""
	def Dissect(self, dissecting: vspyx.Dissector.Dissecting) -> typing.Any: ...

class Dissecting(vspyx.Core.Object):
	"""Dissecting
	"""
	CurrentBit: vspyx.Core.Numeric
	CurrentByte: vspyx.Core.Numeric
	CurrentData: vspyx.Core.BytesView

	@staticmethod
	@typing.overload
	def New(engine: vspyx.Dissector.Engine, frame: vspyx.Frames.Frame) -> vspyx.Dissector.Dissecting: ...


	@staticmethod
	@typing.overload
	def New(engine: vspyx.Dissector.Engine, data: vspyx.Core.BytesView) -> vspyx.Dissector.Dissecting: ...

	def AddProtocolInstance(self, protocolInstance: vspyx.Dissector.ProtocolInstance) -> typing.Any: ...

	def AdvanceCurrentBit(self, amount: vspyx.Core.Numeric) -> typing.Any: ...

	def CheckSpaceLeft(self, more: vspyx.Core.Numeric) -> bool: ...

	def GetRangeValue(self, bit_start: int, bit_end: int, is_big_endian: bool) -> typing.Any: ...

	def AddHook(self, Hook: vspyx.Dissector.Hook) -> typing.Any: ...

	def RemoveHook(self, Hook: vspyx.Dissector.Hook) -> typing.Any: ...

	def GetFieldValue(self, tag: vspyx.Dissector.Tag) -> typing.Any: ...

	def GetFieldSize(self, tag: vspyx.Dissector.Tag) -> typing.Any: ...

	def GetFieldStart(self, tag: vspyx.Dissector.Tag) -> typing.Any: ...

	def GetFieldEnd(self, tag: vspyx.Dissector.Tag) -> typing.Any: ...

	def GetFieldInstance(self, field: vspyx.Dissector.Tag) -> vspyx.Dissector.FieldInstance: ...

	def GetHijackingProtocol(self, hijackLocation: vspyx.Dissector.Tag) -> vspyx.Dissector.Protocol: ...

	def SetMessageState(self, protocol: typing.Any, state: vspyx.Dissector.State) -> typing.Any: ...

	def GetMessageState(self, protocol: typing.Any) -> vspyx.Dissector.State: ...


	@staticmethod
	@typing.overload
	def GetTagRef(field: vspyx.Dissector.Field) -> vspyx.Dissector.Tag: ...


	@staticmethod
	@typing.overload
	def GetTagRef(inst: vspyx.Dissector.FieldInstance) -> vspyx.Dissector.Tag: ...


	@staticmethod
	def GetFieldRef(inst: vspyx.Dissector.FieldInstance) -> vspyx.Dissector.Field: ...

class Message(vspyx.Core.Object):
	"""Message
	"""
	RootField: vspyx.Dissector.FieldInstance

	@staticmethod
	def New(arg0: vspyx.Dissector.Dissecting) -> vspyx.Dissector.Message: ...

	def GetFieldValue(self, tag: vspyx.Dissector.Tag) -> typing.Any: ...

	def GetFieldSize(self, tag: vspyx.Dissector.Tag) -> typing.Any: ...

	def GetFieldStart(self, tag: vspyx.Dissector.Tag) -> typing.Any: ...

	def GetFieldEnd(self, tag: vspyx.Dissector.Tag) -> typing.Any: ...

	def GetFieldInstance(self, field: vspyx.Dissector.Tag) -> vspyx.Dissector.FieldInstance: ...

class Module(vspyx.Core.Module):
	"""Module
	"""
	def NewEngine(self) -> vspyx.Dissector.Engine: ...

	def GenHooksFromWDBFile(self, filepath: str) -> typing.List[vspyx.Dissector.Hook]: ...

	def GenHooksFromWDBString(self, str: str) -> typing.List[vspyx.Dissector.Hook]: ...

class Engine(vspyx.Core.ResolverObject):
	"""Engine
	"""
	def AddHook(self, Hook: vspyx.Dissector.Hook) -> typing.Any: ...

	def RemoveHook(self, Hook: vspyx.Dissector.Hook) -> bool: ...

	def GetProtocol(self, tag: vspyx.Dissector.Tag) -> vspyx.Dissector.Protocol: ...

	def DissectFrame(self, frame: vspyx.Frames.Frame) -> vspyx.Dissector.Message: ...

class Tag(vspyx.Core.Object):
	"""Tag
	"""
	KeyHash: int
	String: str
	ValueHash: int

	@staticmethod
	@typing.overload
	def New(val: str) -> vspyx.Dissector.Tag: ...


	@staticmethod
	@typing.overload
	def New(val: str, aliases: typing.List[str]) -> vspyx.Dissector.Tag: ...


	@typing.overload
	def __eq__(self, rhs: vspyx.Dissector.Tag) -> bool: ...


	@typing.overload
	def __eq__(self, rhs: vspyx.Dissector.Tag) -> bool: ...


	@typing.overload
	def __eq__(self, rhs: vspyx.Dissector.Tag) -> bool: ...

class FieldDefinition(vspyx.Dissector.Field):
	"""FieldDefinition
	"""
	@enum.unique
	class EndianType(enum.IntEnum):
		Big = 0
		Little = 1

	@enum.unique
	class LoopType(enum.IntEnum):
		Once = 0
		Fill = 1
		WhileLoop = 2
		DoWhileLoop = 3
		ForLoop = 4

	def SetShortName(self, name: str) -> typing.Any: ...

	def SetLongName(self, name: str) -> typing.Any: ...

	def SetTag(self, tag: str, aliases: typing.List[str]) -> typing.Any: ...

	def SetEndianType(self, endianType: vspyx.Dissector.FieldDefinition.EndianType) -> typing.Any: ...

	def SetLoopType(self, loopType: vspyx.Dissector.FieldDefinition.LoopType) -> typing.Any: ...

	def SetEnabled(self, enabled: vspyx.Dissector.Expression) -> typing.Any: ...

	def SetLoop(self, loop: vspyx.Dissector.Expression) -> typing.Any: ...

	def SetLength(self, length: vspyx.Dissector.Expression) -> typing.Any: ...

	def SetStart(self, start: vspyx.Dissector.Expression) -> typing.Any: ...

class FieldDefinitionFactory:
	"""FieldDefinitionFactory
	"""

	@staticmethod
	def GenFloatFieldDefinition() -> vspyx.Dissector.FieldDefinition: ...


	@staticmethod
	def GenFixedLengthStringFieldDefinition() -> vspyx.Dissector.FieldDefinition: ...


	@staticmethod
	def GenNullTermStringFieldDefinition() -> vspyx.Dissector.FieldDefinition: ...


	@staticmethod
	def GenProtocol(fieldDefinition: vspyx.Dissector.FieldDefinition) -> vspyx.Dissector.Protocol: ...

class Hook(vspyx.Core.Object):
	"""Hook
	"""
	Expression: vspyx.Dissector.Expression
	HijackLocation: vspyx.Dissector.Tag
	Protocol: vspyx.Dissector.Protocol

class State(vspyx.Core.Object):
	"""State
	"""

