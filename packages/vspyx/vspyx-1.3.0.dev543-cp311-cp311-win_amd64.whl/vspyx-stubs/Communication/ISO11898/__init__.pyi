import typing, enum, vspyx

@enum.unique
class FrameFormats(enum.IntEnum):
	ClassicalBase = 0
	ClassicalExtended = 1
	FDBase = 2
	FDExtended = 3

@enum.unique
class TransferStatuses(enum.IntEnum):
	Complete = 0
	Not_Complete = 1
	Aborted = 2

class ISO11898_1Interface:
	"""ISO11898_1Interface
	"""
	L_Data_Confirm: vspyx.Core.Callback_ce976d3471
	L_Data_Indication: vspyx.Core.Callback_b9cb223583
	def L_Data_Request(self, Identifier: int, Format: vspyx.Communication.ISO11898.FrameFormats, DLC: int, data: vspyx.Core.BytesView) -> typing.Any: ...

class ISO11898_1Processor(vspyx.Communication.PointProcessor, vspyx.Communication.ISO11898.ISO11898_1Interface):
	"""This processor deals with `CANFramePoint`s and `CANFrameConfirmationPoint`s
	 on the bottom end, with `LDataPoint`s and `LConfirmPoint`s on the top end.
	 
	 `CANFramePoint`s are both input and output for this processor.
	 On input going up, an `LDataPoint` will be generated.
	 
	 `LDataPoint`s are both input and output for this processor.
	 On input going down, a `CANFramePoint` will be generated.
	 
	 `LConfirmPoints` are output only from this processor, being
	 generated when a `CANFrameConfirmationPoint` is taken as input.
	 
	"""
	"""ISO11898_1Processor
	"""

	@staticmethod
	def New() -> vspyx.Communication.ISO11898.ISO11898_1Processor: ...

class LConfirmPoint(vspyx.Communication.CommunicationPoint):
	"""LConfirmPoint
	"""
	Identifier: int
	Interesting: vspyx.Runtime.Point.Interesting
	TransferStatus: vspyx.Communication.ISO11898.TransferStatuses

	@staticmethod
	def New(direction: vspyx.Runtime.Point.Direction, upstreamPoints: typing.List[vspyx.Runtime.Point], controller: vspyx.Communication.Controller, identifer: int, transferStatus: vspyx.Communication.ISO11898.TransferStatuses) -> vspyx.Runtime.Point.Consuming_99a0dbe01e: ...

class LDataPoint(vspyx.Communication.PDUPoint):
	"""LDataPoint
	"""
	DLC: int
	Format: vspyx.Communication.ISO11898.FrameFormats
	Identifier: int
	Interesting: vspyx.Runtime.Point.Interesting

	@staticmethod
	def New(direction: vspyx.Runtime.Point.Direction, upstreamPoints: typing.List[vspyx.Runtime.Point], controller: vspyx.Communication.Controller, identifier: int, format: vspyx.Communication.ISO11898.FrameFormats, dlc: int, data: vspyx.Core.BytesView) -> vspyx.Runtime.Point.Consuming_a508b640d2: ...

