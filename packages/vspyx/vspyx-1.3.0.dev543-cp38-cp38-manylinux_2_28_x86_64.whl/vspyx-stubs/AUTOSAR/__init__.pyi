import typing, enum, vspyx
from . import AcceptanceTest, Classic, Foundation

class Module(vspyx.Core.Module):
	"""Module
	"""
	def LoadARXML(self, path: str, serialized: bool, namespaced: bool) -> vspyx.Core.ScheduledTask_6b4128c881: ...

