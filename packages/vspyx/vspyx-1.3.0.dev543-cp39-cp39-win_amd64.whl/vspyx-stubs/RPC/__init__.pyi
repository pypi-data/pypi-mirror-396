import typing, enum, vspyx

class Module(vspyx.Core.Module):
	"""Module
	"""
	def Start(self, listenSpec: str) -> typing.Any:
		"""Start the RPC server in insecure mode with all services that have been
		added up to the point of the call.

		:Parameter listenSpec: , iface:port specification to listen for incoming connections, for example localhost:19870 or 0.0.0.0:19870

		"""
		pass


	def StartSecure(self, listenSpec: str, privateKeyPem: str, fullCertChainPem: str, secretToken: str) -> typing.Any:
		"""Start the RPC server in secure mode with all services that have been
		added up to the point of the call.

		:Parameter listenSpec: , iface:port specification to listen for incoming connections, for example localhost:19870 or 0.0.0.0:19870
		:Parameter privateKeyPem: path to the private key .pem file
		:Parameter fullCertChainPem: path to the certificate chain .pem file
		:Parameter secretToken: a secret token that must every client must provide. sent as x-intrepidcs-vspyx-token auth metadata

		"""
		pass


	def Stop(self) -> typing.Any:
		"""Stop the RPC server

		"""
		pass


	def AddService(self, service: vspyx.RPC.Service) -> typing.Any:
		"""Adds a service to the RPC server. The service will be
		served on the next invocation of Start()

		:Parameter service: the service to add

		"""
		pass


	def RemoveService(self, service: vspyx.RPC.Service) -> typing.Any:
		"""Removes a service from the RPC server. If the server is already
		running the service won't be removed until Stop() is called.

		:Parameter service: the service to remove

		"""
		pass


	def ClearServices(self) -> typing.Any:
		"""Clears all services from the RPC server. If the server is already
		running the services won't be removed until Stop() is called.

		"""
		pass


class Service(vspyx.Core.Object):
	"""Service
	"""
	def Shutdown(self) -> typing.Any: ...

