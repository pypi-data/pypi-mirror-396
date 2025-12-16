import typing, enum, vspyx

class UpperTester(vspyx.Core.Object):
	"""UpperTester
	"""
	@enum.unique
	class GIDs(enum.IntEnum):
		GENERAL = 0
		UDP = 1
		TCP = 2
		ICMP = 3
		ICMPv6 = 4
		IP = 5
		IPv6 = 6
		DHCP = 7
		DHCPv6 = 8
		ARP = 9
		NDP = 10
		ETH = 11
		PHY = 12

	@enum.unique
	class PIDs(enum.IntEnum):
		GET_VERSION = 1
		START_VERSION = 2
		END_TEST = 3
		CLOSE_SOCKET = 0
		CREATE_AND_BIND = 1
		SEND_DATA = 2
		RECEIEVE_AND_FORWARD = 3
		LISTEN_AND_ACCEPT = 4
		CONNECT = 5
		CONFIGURE_SOCKET = 6
		SHUTDOWN = 7
		ECHO_REQUEST = 0
		STATIC_ADDRESS = 0
		STATIC_ROUTE = 1
		INTERFACE_UP = 0
		INTERFACE_DOWN = 1
		INIT_DHCP_CLIENT = 0
		STOP_DHCP_CLIENT = 1
		SET_DHCP_OPTION = 2
		READ_SIGNAL_QUALITY = 0
		READ_DIAG_RESULT = 1
		ACTIVATE_TEST_MODE = 2
		SET_PHY_TX_MODE = 3

	@enum.unique
	class Results(enum.IntEnum):
		E_OK = 0
		E_NOK = 1
		E_NTF = 255
		E_PEN = 254
		E_ISB = 253
		E_INV = 252
		E_ISD = 239
		E_UCS = 238
		E_UBS = 237
		E_IIF = 236
		E_TCP_PNA = 235
		E_TCP_FSU = 234
		E_TCP_ILP = 233
		E_TCP_INR = 232
		E_TCP_CAE = 231
		E_TCP_COC = 230
		E_TCP_CNE = 229
		E_TCP_CRE = 228
		E_TCP_CAT = 227
		E_TCP_COR = 226


	@staticmethod
	def NewInternal(iface: vspyx.TCPIP.Interface) -> vspyx.AUTOSAR.AcceptanceTest.UpperTester: ...

	def GetVersion(self, gid: vspyx.AUTOSAR.AcceptanceTest.UpperTester.GIDs) -> vspyx.AUTOSAR.AcceptanceTest.UpperTester.GetVersionResponse:
		"""This SP will return the testability protocol version of the used protocol
		and service primitive implementation. The testability protocol version is
		bound to the TC release version the protocol is based on. The current
		version is TC1.2.0.

		"""
		pass


	def StartTest(self, gid: vspyx.AUTOSAR.AcceptanceTest.UpperTester.GIDs) -> vspyx.AUTOSAR.AcceptanceTest.UpperTester.StartTestResponse:
		"""The purpose of this SP is to have a defined entry tag in trace at the point
		in time the test case was started. This SP does not have any request
		parameters.

		"""
		pass


	def EndTest(self, gid: vspyx.AUTOSAR.AcceptanceTest.UpperTester.GIDs, request: vspyx.AUTOSAR.AcceptanceTest.UpperTester.EndTestRequest) -> vspyx.AUTOSAR.AcceptanceTest.UpperTester.EndTestResponse:
		"""The purpose of this SP is to reset the Upper Tester. All sockets of the
		test channel will be closed, counters are set to the default value, buffers
		are cleared and active service primitives will be terminated. Another
		purpose of this SP is to have a defined entry tag in trace at the point in
		time the test case was stopped. The parameters may be ignored by the
		testability module.

		"""
		pass


	def CloseSocket(self, gid: vspyx.AUTOSAR.AcceptanceTest.UpperTester.GIDs, request: vspyx.AUTOSAR.AcceptanceTest.UpperTester.CloseSocketRequest) -> vspyx.AUTOSAR.AcceptanceTest.UpperTester.CloseSocketResponse:
		"""Closes a socket.

		"""
		pass


	def CreateAndBind(self, gid: vspyx.AUTOSAR.AcceptanceTest.UpperTester.GIDs, request: vspyx.AUTOSAR.AcceptanceTest.UpperTester.CreateAndBindRequest) -> vspyx.AUTOSAR.AcceptanceTest.UpperTester.CreateAndBindResponse:
		"""Creates a socket and optionally binds this socket to a port and a local IP
		address.
		Note: Some TCP/IP-Stacks may need to know at socket creation time
		whether it is a client or a server socket. For those kind of
		implementations the SP may create and return a higher-level ID that
		maps to the corresponding data needed to create the socket later and
		the real socket ID once created.

		"""
		pass


	def SendData(self, gid: vspyx.AUTOSAR.AcceptanceTest.UpperTester.GIDs, request: vspyx.AUTOSAR.AcceptanceTest.UpperTester.SendDataRequest) -> vspyx.AUTOSAR.AcceptanceTest.UpperTester.SendDataResponse:
		"""Sends data to a target.
		Please note: because of the non-blocking behavior of Service Primitives
		a positive response does NOT signal the success of the transmission,
		but the success of issuing the transmission.

		"""
		pass


	def ReceiveAndForward(self, gid: vspyx.AUTOSAR.AcceptanceTest.UpperTester.GIDs, request: vspyx.AUTOSAR.AcceptanceTest.UpperTester.ReceiveAndForwardRequest, handler: vspyx.Core.Function_5b8b9c0ffc) -> vspyx.AUTOSAR.AcceptanceTest.UpperTester.ReceiveAndForwardResponse:
		"""Data that will be received after the call of this SP will be forwarded to the
		test system. The amount of forwarded data per received datagram
		(UDP) or bulk of stream data (TCP) can be limited using maxFwd. The
		original length of this data unit can be obtained by fullLen. The process
		will repeat itself (active phase) until the maximum amount of data
		defined by maxLen was received or END_TEST was called (inactive
		phase).
		UDP: No further requirements. (see 6.12.2 UDP Receive and Count)
		TCP: In the inactive phase (e.g. prior the first call) all data received will
		be discarded or ignored. When called all data that was received on the
		specified socked prior the call of this SP will be consumed2 in order to
		open the TCP receive window. All data that is received during the active
		phase of this SP will be consumed up to the maximum amount of data
		defined by maxLen. (see 6.12.4 TCP Client Receive and Forward)

		"""
		pass


	def ListenAndAccept(self, gid: vspyx.AUTOSAR.AcceptanceTest.UpperTester.GIDs, request: vspyx.AUTOSAR.AcceptanceTest.UpperTester.ListenAndAcceptRequest, handler: vspyx.Core.Function_1db682930d) -> vspyx.AUTOSAR.AcceptanceTest.UpperTester.ListenAndAcceptResponse:
		"""Marks a socket as listen socket that will be used to accept incoming
		connections. Whenever a new connection was established this SP
		provides the socket ID of the new connection together with the listen
		socket, client port, and address in an event.

		"""
		pass


	def Connect(self, gid: vspyx.AUTOSAR.AcceptanceTest.UpperTester.GIDs, request: vspyx.AUTOSAR.AcceptanceTest.UpperTester.ConnectRequest) -> vspyx.AUTOSAR.AcceptanceTest.UpperTester.ConnectResponse:
		"""Triggers a TCP connection to a remote destination.

		"""
		pass


	def ConfigureSocket(self, gid: vspyx.AUTOSAR.AcceptanceTest.UpperTester.GIDs, request: vspyx.AUTOSAR.AcceptanceTest.UpperTester.ConfigureSocketRequest) -> vspyx.AUTOSAR.AcceptanceTest.UpperTester.ConfigureSocketResponse:
		"""This SP is used to select and set parameters that can be configured on
		a socket basis. More parameters may be supported in following
		versions of this document or by non-standard extensions (Parameter
		IDs starting with 0xFFFF, 0xFFFE... and so forth).

		"""
		pass


	def ReadSignalQuality(self, gid: vspyx.AUTOSAR.AcceptanceTest.UpperTester.GIDs, request: vspyx.AUTOSAR.AcceptanceTest.UpperTester.ReadSignalQualityRequest) -> vspyx.AUTOSAR.AcceptanceTest.UpperTester.ReadSignalQualityResponse:
		"""Returns the current signal quality in percent by reading the value from
		the related Ethernet transceiver

		"""
		pass


	def ReadDiagResult(self, gid: vspyx.AUTOSAR.AcceptanceTest.UpperTester.GIDs, request: vspyx.AUTOSAR.AcceptanceTest.UpperTester.ReadDiagResultRequest) -> vspyx.AUTOSAR.AcceptanceTest.UpperTester.ReadDiagResultResponse:
		"""Returns the result of the cable diagnostics.

		"""
		pass


	def ActivateTestMode(self, gid: vspyx.AUTOSAR.AcceptanceTest.UpperTester.GIDs, request: vspyx.AUTOSAR.AcceptanceTest.UpperTester.ActivateTestModeRequest) -> vspyx.AUTOSAR.AcceptanceTest.UpperTester.ActivateTestModeResponse:
		"""Activates a given PHY test mode.

		"""
		pass


	def SetPhyTxMode(self, gid: vspyx.AUTOSAR.AcceptanceTest.UpperTester.GIDs, request: vspyx.AUTOSAR.AcceptanceTest.UpperTester.SetPhyTxModeRequest) -> vspyx.AUTOSAR.AcceptanceTest.UpperTester.SetPhyTxModeResponse:
		"""Activates a given transmission mode.

		"""
		pass


	def Shutdown(self, gid: vspyx.AUTOSAR.AcceptanceTest.UpperTester.GIDs, request: vspyx.AUTOSAR.AcceptanceTest.UpperTester.ShutdownRequest) -> vspyx.AUTOSAR.AcceptanceTest.UpperTester.ShutdownResponse:
		"""Shuts down a socket.

		"""
		pass


	def InterfaceUp(self, gid: vspyx.AUTOSAR.AcceptanceTest.UpperTester.GIDs, request: vspyx.AUTOSAR.AcceptanceTest.UpperTester.InterfaceUpRequest) -> vspyx.AUTOSAR.AcceptanceTest.UpperTester.InterfaceUpResponse:
		"""Enables an Ethernet interface or virtual interface. This SP is not affecting
		the persistent configuration.

		"""
		pass


	def InterfaceDown(self, gid: vspyx.AUTOSAR.AcceptanceTest.UpperTester.GIDs, request: vspyx.AUTOSAR.AcceptanceTest.UpperTester.InterfaceDownRequest) -> vspyx.AUTOSAR.AcceptanceTest.UpperTester.InterfaceDownResponse:
		"""Disables an Ethernet interface or virtual interface. This SP is not
		affecting the persistent configuration.

		"""
		pass


	def StaticAddress(self, gid: vspyx.AUTOSAR.AcceptanceTest.UpperTester.GIDs, request: vspyx.AUTOSAR.AcceptanceTest.UpperTester.StaticAddressRequest) -> vspyx.AUTOSAR.AcceptanceTest.UpperTester.StaticAddressResponse:
		"""Assigns a static IP address and Netmask to the given network
		interface.

		"""
		pass


	def StaticRoute(self, gid: vspyx.AUTOSAR.AcceptanceTest.UpperTester.GIDs, request: vspyx.AUTOSAR.AcceptanceTest.UpperTester.StaticRouteRequest) -> vspyx.AUTOSAR.AcceptanceTest.UpperTester.StaticRouteResponse:
		"""Adds a static route for the network. This SP is not affecting the
		persistent configuration.

		"""
		pass


	def InitDHCPClient(self, gid: vspyx.AUTOSAR.AcceptanceTest.UpperTester.GIDs, request: vspyx.AUTOSAR.AcceptanceTest.UpperTester.InitDHCPClientRequest) -> vspyx.AUTOSAR.AcceptanceTest.UpperTester.InitDHCPClientResponse:
		"""Initialize the DHCP Client by use of network interface and port.

		"""
		pass


	def StopDHCPClient(self, gid: vspyx.AUTOSAR.AcceptanceTest.UpperTester.GIDs, request: vspyx.AUTOSAR.AcceptanceTest.UpperTester.StopDHCPClientRequest) -> vspyx.AUTOSAR.AcceptanceTest.UpperTester.StopDHCPClientResponse:
		"""Shutdown the DHCP Client by use of network interface and port.

		"""
		pass


	def SetDHCPOption(self, gid: vspyx.AUTOSAR.AcceptanceTest.UpperTester.GIDs, request: vspyx.AUTOSAR.AcceptanceTest.UpperTester.SetDHCPOptionRequest) -> vspyx.AUTOSAR.AcceptanceTest.UpperTester.SetDHCPOptionResponse:
		"""Sets DHCP Client options

		"""
		pass


	def EchoRequest(self, gid: vspyx.AUTOSAR.AcceptanceTest.UpperTester.GIDs, request: vspyx.AUTOSAR.AcceptanceTest.UpperTester.EchoRequestRequest) -> vspyx.AUTOSAR.AcceptanceTest.UpperTester.EchoRequestResponse: ...

	def ARPOperation(self, gid: vspyx.AUTOSAR.AcceptanceTest.UpperTester.GIDs, request: vspyx.AUTOSAR.AcceptanceTest.UpperTester.ARPOperationRequest) -> vspyx.AUTOSAR.AcceptanceTest.UpperTester.ARPOperationResponse: ...

	class GetVersionResponse:
		"""GetVersionResponse
		"""
		result: vspyx.AUTOSAR.AcceptanceTest.UpperTester.Results
		majorVer: int
		minorVer: int
		patchVer: int


	class StartTestResponse:
		"""StartTestResponse
		"""
		result: vspyx.AUTOSAR.AcceptanceTest.UpperTester.Results


	class EndTestRequest:
		"""EndTestRequest
		"""
		tcId: int
		tsName: str


	class EndTestResponse:
		"""EndTestResponse
		"""
		result: vspyx.AUTOSAR.AcceptanceTest.UpperTester.Results


	class CloseSocketRequest:
		"""CloseSocketRequest
		"""
		socketId: int
		abort: bool


	class CloseSocketResponse:
		"""CloseSocketResponse
		"""
		result: vspyx.AUTOSAR.AcceptanceTest.UpperTester.Results


	class CreateAndBindRequest:
		"""CreateAndBindRequest
		"""
		doBind: bool
		localPort: int
		localAddr: str


	class CreateAndBindResponse:
		"""CreateAndBindResponse
		"""
		result: vspyx.AUTOSAR.AcceptanceTest.UpperTester.Results
		socketId: int


	class SendDataRequest:
		"""SendDataRequest
		"""
		socketId: int
		totalLen: int
		destPort: int
		destAddr: str
		flags: int
		data: typing.List[int]


	class SendDataResponse:
		"""SendDataResponse
		"""
		result: vspyx.AUTOSAR.AcceptanceTest.UpperTester.Results


	class ReceiveAndForwardRequest:
		"""ReceiveAndForwardRequest
		"""
		socketId: int
		maxFwd: int
		maxLen: int


	class ReceiveAndForwardResponse:
		"""ReceiveAndForwardResponse
		"""
		result: vspyx.AUTOSAR.AcceptanceTest.UpperTester.Results
		dropCnt: int


	class ReceiveAndForwardEvent:
		"""ReceiveAndForwardEvent
		"""
		fullLen: int
		srcPort: int
		srcAddr: str
		payload: typing.List[int]


	class ListenAndAcceptRequest:
		"""ListenAndAcceptRequest
		"""
		listenSocketId: int
		maxCon: int


	class ListenAndAcceptResponse:
		"""ListenAndAcceptResponse
		"""
		result: vspyx.AUTOSAR.AcceptanceTest.UpperTester.Results


	class ListenAndAcceptEvent:
		"""ListenAndAcceptEvent
		"""
		listenSocketId: int
		newSocketId: int
		port: int
		address: str


	class ConnectRequest:
		"""ConnectRequest
		"""
		socketId: int
		destPort: int
		destAddr: str


	class ConnectResponse:
		"""ConnectResponse
		"""
		result: vspyx.AUTOSAR.AcceptanceTest.UpperTester.Results


	class ConfigureSocketRequest:
		"""ConfigureSocketRequest
		"""
		socketId: int
		paramId: int
		paramVal: typing.List[int]


	class ConfigureSocketResponse:
		"""ConfigureSocketResponse
		"""
		result: vspyx.AUTOSAR.AcceptanceTest.UpperTester.Results


	class ReadSignalQualityRequest:
		"""ReadSignalQualityRequest
		"""
		ifName: str


	class ReadSignalQualityResponse:
		"""ReadSignalQualityResponse
		"""
		result: vspyx.AUTOSAR.AcceptanceTest.UpperTester.Results
		sigQuality: int


	class ReadDiagResultRequest:
		"""ReadDiagResultRequest
		"""
		ifName: str


	class ReadDiagResultResponse:
		"""ReadDiagResultResponse
		"""
		result: vspyx.AUTOSAR.AcceptanceTest.UpperTester.Results
		diagResult: int


	class ActivateTestModeRequest:
		"""ActivateTestModeRequest
		"""
		ifName: str
		testMode: int


	class ActivateTestModeResponse:
		"""ActivateTestModeResponse
		"""
		result: vspyx.AUTOSAR.AcceptanceTest.UpperTester.Results


	class SetPhyTxModeRequest:
		"""SetPhyTxModeRequest
		"""
		ifName: str
		txMode: int


	class SetPhyTxModeResponse:
		"""SetPhyTxModeResponse
		"""
		result: vspyx.AUTOSAR.AcceptanceTest.UpperTester.Results


	class ShutdownRequest:
		"""ShutdownRequest
		"""
		socketId: int
		typeId: int


	class ShutdownResponse:
		"""ShutdownResponse
		"""
		result: vspyx.AUTOSAR.AcceptanceTest.UpperTester.Results


	class InterfaceUpRequest:
		"""InterfaceUpRequest
		"""
		ifName: str


	class InterfaceUpResponse:
		"""InterfaceUpResponse
		"""
		result: vspyx.AUTOSAR.AcceptanceTest.UpperTester.Results


	class InterfaceDownRequest:
		"""InterfaceDownRequest
		"""
		ifName: str


	class InterfaceDownResponse:
		"""InterfaceDownResponse
		"""
		result: vspyx.AUTOSAR.AcceptanceTest.UpperTester.Results


	class StaticAddressRequest:
		"""StaticAddressRequest
		"""
		ifName: str
		addr: str
		netMask: int


	class StaticAddressResponse:
		"""StaticAddressResponse
		"""
		result: vspyx.AUTOSAR.AcceptanceTest.UpperTester.Results


	class StaticRouteRequest:
		"""StaticRouteRequest
		"""
		ifName: str
		subNet: str
		netMask: int
		gateway: str


	class StaticRouteResponse:
		"""StaticRouteResponse
		"""
		result: vspyx.AUTOSAR.AcceptanceTest.UpperTester.Results


	class InitDHCPClientRequest:
		"""InitDHCPClientRequest
		"""
		ifName: str


	class InitDHCPClientResponse:
		"""InitDHCPClientResponse
		"""
		result: vspyx.AUTOSAR.AcceptanceTest.UpperTester.Results


	class StopDHCPClientRequest:
		"""StopDHCPClientRequest
		"""
		ifName: str


	class StopDHCPClientResponse:
		"""StopDHCPClientResponse
		"""
		result: vspyx.AUTOSAR.AcceptanceTest.UpperTester.Results


	class SetDHCPOptionRequest:
		"""SetDHCPOptionRequest
		"""
		ifName: str
		code: int
		value: typing.List[int]


	class SetDHCPOptionResponse:
		"""SetDHCPOptionResponse
		"""
		result: vspyx.AUTOSAR.AcceptanceTest.UpperTester.Results


	class EchoRequestRequest:
		"""EchoRequestRequest
		"""
		ifName: typing.Any
		destAddr: str
		data: typing.List[int]


	class EchoRequestResponse:
		"""EchoRequestResponse
		"""
		result: vspyx.AUTOSAR.AcceptanceTest.UpperTester.Results


	class ARPOperationRequest:
		"""ARPOperationRequest
		"""
		ifName: str
		operation: int
		ip: str
		mac: str


	class ARPOperationResponse:
		"""ARPOperationResponse
		"""
		result: vspyx.AUTOSAR.AcceptanceTest.UpperTester.Results


