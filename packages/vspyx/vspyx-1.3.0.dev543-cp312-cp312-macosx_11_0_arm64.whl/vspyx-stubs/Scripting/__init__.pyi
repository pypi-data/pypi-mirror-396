import typing, enum, vspyx

class FunctionBlockStepHandler:
	pass

class FunctionBlock:
	pass

class Component(vspyx.Runtime.Component):
	"""A Component with a Tick() function, and rules about when to call it.
	 
	"""
	"""Component
	"""
	def Trigger(self) -> typing.Any:
		"""Schedule the Tick to be executed as soon as possible

		Generally you want to call this rather than Tick() directly,
		so that Tick() is executed on its own thread and will not block
		the current thread.

		"""
		pass


	def Tick(self) -> typing.Any:
		"""Execute the contents of the Scripting::Component

		Generally this is called on the ticking thread, triggered by
		Trigger(), rather than being called directly.

		"""
		pass


	def EnvironmentInitialize(self) -> typing.Any: ...

	def ComponentStart(self) -> typing.Any: ...

	def EnvironmentShutdown(self) -> typing.Any: ...

class PythonComponent(vspyx.Scripting.Component):
	"""A Scripting::Component whose Tick() function is implemented in Python.
	 
	"""
	"""PythonComponent
	"""
	Code: str
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	def New(config: typing.Any) -> vspyx.Scripting.PythonComponent: ...

	def CloneConfiguration(self) -> typing.Any: ...

class FunctionBlock(vspyx.Runtime.Component):
	"""A collection of steps that generate a PythonComponent, which is automatically added as a child.
	 
	"""
	"""FunctionBlock
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449
	def Trigger(self) -> typing.Any:
		"""Run the Function Block now

		"""
		pass



	@staticmethod
	def New(config: typing.Any) -> vspyx.Scripting.FunctionBlock: ...

	def CloneConfiguration(self) -> typing.Any: ...

	class CompilationContext:
		"""CompilationContext
		"""
		Imports: typing.Any
		Tick: vspyx.Scripting.FunctionBlock.CompilationContext.Func

		class Func:
			"""Func
			"""
			Ops: typing.List[str]
			def PushOp(self, op: str) -> typing.Any: ...

			def PushIndentingOp(self, op: str) -> typing.Any: ...

			def PopIndent(self) -> typing.Any: ...



class FunctionBlockStepHandler:
	"""An object which compiles a particular FunctionBlock Step into a FunctionBlock's CompilationContext.
	 
	"""
	"""FunctionBlockStepHandler
	"""
	HandlesType: str
	"""Returns the protobuf type string for the type that this StepHandler will handle.
		 
	"""

class Module(vspyx.Core.Module):
	"""Module
	"""
	ActivePythonScript: vspyx.Scripting.PythonScript

	@typing.overload
	def NewPythonScript(self) -> vspyx.Scripting.PythonScript: ...


	@typing.overload
	def NewPythonScript(self, argv: typing.List[str]) -> vspyx.Scripting.PythonScript: ...


	@typing.overload
	def NewPythonScript(self, argv: typing.List[str], extraPackagePaths: typing.List[str]) -> vspyx.Scripting.PythonScript: ...

	def RegisterFunctionBlockStepHandler(self, handler: vspyx.Scripting.FunctionBlockStepHandler) -> typing.Any: ...

	def DeregisterFunctionBlockStepHandler(self, handler: vspyx.Scripting.FunctionBlockStepHandler) -> typing.Any: ...

	def GetFunctionBlockStepHandler(self, stepType: str) -> vspyx.Scripting.FunctionBlockStepHandler: ...

class Script(vspyx.Core.Object):
	"""Script
	"""
	@enum.unique
	class RunResult(enum.IntEnum):
		Finished = 0
		Error = 1
		Paused = 2

	LastError: str
	"""Get a description of the last error that occured
	
	 :Returns: description of the last error
		
	"""

	OnOutput: vspyx.Core.Callback_6ee07abf48
	"""Callback for when the script produces text output
		 
	"""

	OnStart: vspyx.Core.Callback_634bd5c449
	"""Callback for when script starts
		 
	"""

	def Run(self) -> vspyx.Scripting.Script.RunResult:
		"""Run the script. In the case of an error, use GetLastError()
		to retreive error information.

		:Returns: result of running

		"""
		pass


	def Stop(self) -> typing.Any: ...

class PythonScript(vspyx.Scripting.Script, vspyx.Core.Environment):
	"""PythonScript
	"""
	Application: vspyx.Core.Application
	LastErrorTraceback: str
	def RunSource(self, source: str) -> typing.Any: ...

	def RunPath(self, path: str) -> typing.Any: ...

	def RunModule(self, mod: str) -> typing.Any: ...

class TextAPI(vspyx.Core.ResolverObject):
	"""TextAPI
	"""
	Script: vspyx.Scripting.PythonScript

	@staticmethod
	def New() -> vspyx.Scripting.TextAPI: ...

	def Execute(self, cmd: str) -> str:
		"""Execute a command

		:Parameter cmd: the command
		:Returns: the result

		"""
		pass


	def Intellisense(self, additionalNamespace: str) -> typing.List[str]:
		"""Perform an intellisense operation

		This will provide available options in the current namespace, as well as
		additional namespace appended to it. Only full namespaces should be passed;
		partially finished namespaces should be handled by the client. The type of access
		should be included. For example, to get intellisense for the user typing "Core.St",
		additionalNamespace should be "Core."

		:Parameter additionalNamespace: an additional namespace after the current namespace
		:Returns: all available items

		"""
		pass


