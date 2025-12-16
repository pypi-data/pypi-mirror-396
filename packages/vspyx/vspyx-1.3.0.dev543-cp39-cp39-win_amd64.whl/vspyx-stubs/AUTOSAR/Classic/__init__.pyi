import typing, enum, vspyx

class Can_ConfigType:
	"""This is the type of the external data structure containing the overall
	 initialization data for the CAN driver and SFR settings affecting all
	 controllers. Furthermore it contains pointers to controller configuration
	 structures. The contents of the initialization data structure are CAN hardware
	 specific.
	 
	"""
	"""Can_ConfigType
	"""
	dummy: int

class CanIf_ConfigType:
	"""This type defines a data structure for the post build parameters of the CAN
	 interface for all underlying CAN drivers. At initialization the CanIf gets a
	 pointer to a structure of this type to get access to its configuration data,
	 which is necessary for initialization.
	 
	"""
	"""CanIf_ConfigType
	"""
	dummy: int

@enum.unique
class CanIf_PduModeType(enum.IntFlag):
	"""The PduMode of a channel defines its transmit or receive activity.\n Communication direction (transmission and/or reception) of the channel can be\n controlled separately or together by upper layers.\n 
"""
	CANIF_OFFLINE = 0
	CANIF_TX_OFFLINE = 1
	CANIF_TX_OFFLINE_ACTIVE = 2
	CANIF_ONLINE = 3

@enum.unique
class CanIf_NotifStatusType(enum.IntFlag):
	"""Return value of CAN L-PDU notification status.\n 
"""
	CANIF_NO_NOTIFICATION = 0
	CANIF_TX_RX_NOTIFICATION = 1

class CanNm_ConfigType:
	"""This type shall contain at least all parameters that are post-build able
	 according to chapter 10.
	 
	"""
	"""CanNm_ConfigType
	"""
	dummy: int

class Std_VersionInfoType:
	"""This type shall be used to request the version of a BSW module using the
	 <Module name>_GetVersionInfo() function.
	 
	"""
	"""Std_VersionInfoType
	"""
	moduleID: int
	sw_major_version: int
	sw_minor_version: int
	sw_patch_version: int
	vendorID: int

@enum.unique
class BufReq_ReturnType(enum.IntFlag):
	"""Variables of this type shall be used to store the result of a buffer request.\n 
"""
	BUFREQ_OK = 0
	BUFREQ_E_NOT_OK = 1
	BUFREQ_E_BUSY = 2
	BUFREQ_E_OVFL = 3

class PduInfoType:
	"""Variables of this type shall be used to store the basic information about a PDU
	 of any type, namely a pointer variable pointing to its SDU (payload), a pointer
	 to Meta Data of the PDU, and the corresponding length of the SDU in bytes.
	 
	"""
	"""PduInfoType
	"""
	SduLength: int

@enum.unique
class TPParameterType(enum.IntFlag):
	"""Specify the parameter to which the value has to be changed (BS or STmin).\n 
"""
	TP_STMIN = 0
	TP_BS = 1
	TP_BC = 2

@enum.unique
class TpDataStateType(enum.IntFlag):
	"""Variables of this type shall be used to store the state of TP buffer.\n 
"""
	TP_DATACONF = 0
	TP_DATARETRY = 1
	TP_CONFPENDING = 2

class RetryInfoType:
	"""Variables of this type shall be used to store the information about Tp buffer
	 handling.
	 
	"""
	"""RetryInfoType
	"""
	TpDataState: vspyx.AUTOSAR.Classic.TpDataStateType
	TxTpDataCnt: int

@enum.unique
class IcomSwitch_ErrorType(enum.IntFlag):
	"""IcomSwitch_ErrorType defines the errors which can occur when activating or\n deactivating Pretended Networking. \n 
"""
	ICOM_SWITCH_E_OK = 0
	ICOM_SWITCH_E_FAILED = 1

@enum.unique
class CanSM_StateType(enum.IntFlag):
	"""Defines the values of the internal states of the CanSM module\n 
"""
	pass

class CanSM_ConfigType:
	"""This type defines a data structure for the post build parameters of the CanSM.
	 At initialization the CanSM gets a pointer to a structure of this type to get
	 access to its configuration data, which is necessary for initialization.
	 
	"""
	"""CanSM_ConfigType
	"""
	dummy: int

class CanTSyn_ConfigType:
	"""This is the base type for the configuration of the Time Synchronization over
	 CAN.
	 
	 A pointer to an instance of this structure will be used in the initialization
	 of the Time Synchronization over CAN.
	 
	 The content of this structure is defined in chapter 10 Configuration
	 specification.
	 
	"""
	"""CanTSyn_ConfigType
	"""
	dummy: int

@enum.unique
class CanTSyn_TransmissionModeType(enum.IntFlag):
	"""Handles the enabling and disabling of the transmission mode\n 
"""
	CANTSYN_TX_OFF = 0
	CANTSYN_TX_ON = 1

class CanTp_ConfigType:
	"""Data structure type for the post-build configuration parameters.
	 
	"""
	"""CanTp_ConfigType
	"""
	dummy: int

class CanTrcv_ConfigType:
	"""This is the type of the external data structure containing the overall
	 initialization data for the CAN transceiver driver and settings affecting all
	 transceivers. Furthermore it contains pointers to transceiver configuration
	 structures. The contents of the initialization data structure are CAN
	 transceiver hardware specific.
	 
	"""
	"""CanTrcv_ConfigType
	"""
	dummy: int

@enum.unique
class CanTrcv_TrcvFlagStateType(enum.IntFlag):
	"""Provides the state of a flag in the transceiver hardware.\n 
"""
	CANTRCV_FLAG_SET = 0
	CANTRCV_FLAG_CLEARED = 1

@enum.unique
class CanTrcv_PNActivationType(enum.IntFlag):
	"""Datatype used for describing whether PN wakeup functionality in CanTrcv is\n enabled or disabled.\n 
"""
	PN_ENABLED = 0
	PN_DISABLED = 1

class Can_PduType:
	"""Can_PduType
	"""
	id: int
	length: int
	swPduHandle: int

@enum.unique
class CanTrcv_TrcvModeType(enum.IntFlag):
	"""Operating modes of the CAN Transceiver Driver.\n 
"""
	CANTRCV_TRCVMODE_NORMAL = 0
	CANTRCV_TRCVMODE_SLEEP = 1
	CANTRCV_TRCVMODE_STANDBY = 2

@enum.unique
class CanTrcv_TrcvWakeupReasonType(enum.IntFlag):
	"""This type denotes the wake up reason detected by the CAN transceiver in detail.\n 
"""
	CANTRCV_WU_ERROR = 0
	CANTRCV_WU_NOT_SUPPORTED = 1
	CANTRCV_WU_BY_BUS = 2
	CANTRCV_WU_INTERNALLY = 3
	CANTRCV_WU_RESET = 4
	CANTRCV_WU_POWER_ON = 5
	CANTRCV_WU_BY_PIN = 6
	CANTRCV_WU_BY_SYSERR = 7

@enum.unique
class CanTrcv_TrcvWakeupModeType(enum.IntFlag):
	"""This type shall be used to control the CAN transceiver concerning wake up\n events and wake up notifications.\n 
"""
	CANTRCV_WUMODE_ENABLE = 0
	CANTRCV_WUMODE_DISABLE = 1
	CANTRCV_WUMODE_CLEAR = 2

class Can_HwType:
	"""This type defines a data structure which clearly provides an Hardware Object
	 Handle including its corresponding CAN Controller and therefore CanDrv as well
	 as the specific CanId.
	 
	"""
	"""Can_HwType
	"""
	CanId: int
	ControllerId: int
	Hoh: int

@enum.unique
class Can_ControllerStateType(enum.IntFlag):
	"""States that are used by the several ControllerMode functions.\n 
"""
	CAN_CS_UNINIT = 0
	CAN_CS_STARTED = 1
	CAN_CS_STOPPED = 2
	CAN_CS_SLEEP = 3

@enum.unique
class Can_ErrorStateType(enum.IntFlag):
	"""Error states of a CAN controller.\n 
"""
	CAN_ERRORSTATE_ACTIVE = 0
	CAN_ERRORSTATE_PASSIVE = 1
	CAN_ERRORSTATE_BUSOFF = 2

@enum.unique
class Com_StatusType(enum.IntFlag):
	"""This is a status value returned by the API service Com_GetStatus().\n 
"""
	COM_UNINIT = 0
	COM_INIT = 1

class Com_ConfigType:
	"""This is the type of the data structure containing the initialization data for
	 COM.
	 
	"""
	"""Com_ConfigType
	"""
	dummy: int

class ComM_ConfigType:
	"""This type contains the implementation-specific post build configuration
	 structure.
	 
	"""
	"""ComM_ConfigType
	"""
	dummy: int

@enum.unique
class ComM_InitStatusType(enum.IntFlag):
	"""Initialization status of ComM.\n 
"""
	COMM_UNINIT = 0
	COMM_INIT = 1

@enum.unique
class ComM_PncModeType(enum.IntFlag):
	"""Current mode of a PNC\n 
"""
	COMM_PNC_REQUESTED = 0
	COMM_PNC_READY_SLEEP = 1
	COMM_PNC_PREPARE_SLEEP = 2
	COMM_PNC_NO_COMMUNICATION = 3

class Dcm_ConfigType:
	"""This type defines a data structure for the post build parameters of the DCM .
	 At initialization the DCM gets a pointer to a structure of this type to get
	 access to its configuration data, which is necessary for initialization.
	 
	"""
	"""Dcm_ConfigType
	"""
	dummy: int

class Dcm_MsgAddInfoType:
	"""Additional information on message request.
	 Datastructure: Bitfield
	 
	"""
	"""Dcm_MsgAddInfoType
	"""
	reqType: int
	suppressPosResponse: int

class Dcm_MsgContextType:
	"""This data structure contains all information which is necessary to process a
	 diagnostic message from request to response and response confirmation.
	 
	"""
	"""Dcm_MsgContextType
	"""
	dcmRxPduId: int
	idContext: int
	msgAddInfo: vspyx.AUTOSAR.Classic.Dcm_MsgAddInfoType
	reqDataLen: int
	resDataLen: int
	resMaxDataLen: int

class Dcm_ProgConditionsType:
	"""Used in Dcm_SetProgConditions() to allow the integrator to store relevant
	 information prior to jumping to bootloader / jump due to ECUReset request.
	 
	"""
	"""Dcm_ProgConditionsType
	"""
	ApplUpdated: int
	ConnectionId: int
	ReprogramingRequest: int
	ResponseRequired: int
	Sid: int
	SubFncId: int
	TesterAddress: int

class Dem_J1939DcmLampStatusType:
	"""For details refer SAE J1939-73
	 
	"""
	"""Dem_J1939DcmLampStatusType
	"""
	FlashLampStatus: int
	LampStatus: int

class Dem_J1939DcmDiagnosticReadiness1Type:
	"""This structure represents all data elemets of the DM05 message. The encoding
	 shall be done acording SAE J1939-73
	 
	"""
	"""Dem_J1939DcmDiagnosticReadiness1Type
	"""
	ActiveTroubleCodes: int
	ContinuouslyMonitoredSystemsSupport_Status: int
	NonContinuouslyMonitoredSystemsStatus7: int
	NonContinuouslyMonitoredSystemsStatus8: int
	NonContinuouslyMonitoredSystemsSupport5: int
	NonContinuouslyMonitoredSystemsSupport6: int
	OBDCompliance: int
	PreviouslyActiveDiagnosticTroubleCodes: int

class Dem_J1939DcmDiagnosticReadiness2Type:
	"""This structure represents all data elemets of the DM21 message. The encoding
	 shall be done acording SAE J1939-73
	 
	"""
	"""Dem_J1939DcmDiagnosticReadiness2Type
	"""
	DistanceSinceDTCsCleared: int
	DistanceTraveledWhileMILisActivated: int
	MinutesRunbyEngineWhileMILisActivated: int
	TimeSinceDiagnosticTroubleCodesCleared: int

class Dem_J1939DcmDiagnosticReadiness3Type:
	"""This structure represents all data elemets of the DM26 message. The encoding
	 shall be done acording SAE J1939-73
	 
	"""
	"""Dem_J1939DcmDiagnosticReadiness3Type
	"""
	ContinuouslyMonitoredSystemsEnableCompletedStatus: int
	NonContinuouslyMonitoredSystems7: int
	NonContinuouslyMonitoredSystems8: int
	NonContinuouslyMonitoredSystemsEnableStatus5: int
	NonContinuouslyMonitoredSystemsEnableStatus6: int
	NumberofWarmupsSinceDTCsCleared: int
	TimeSinceEngineStart: int

class Dem_ConfigType:
	"""This type of the external data structure shall contain the post build
	 initialization data for the Dem.
	 
	"""
	"""Dem_ConfigType
	"""
	dummy: int

class Det_ConfigType:
	"""Configuration data structure of the Det module.
	 
	"""
	"""Det_ConfigType
	"""
	dummy: int

class DoIP_ConfigType:
	"""Configuration data structure of the DoIP module
	 
	"""
	"""DoIP_ConfigType
	"""
	dummy: int

class Eth_ConfigType:
	"""Implementation specific structure of the post build configuration
	 
	"""
	"""Eth_ConfigType
	"""
	dummy: int

class EthIf_ConfigType:
	"""Implementation specific structure of the post build configuration
	 
	"""
	"""EthIf_ConfigType
	"""
	dummy: int

@enum.unique
class EthIf_StateType(enum.IntFlag):
	"""Status supervision used for Development Error Detection. The state shall be\n available for debugging.\n 
"""
	ETHCTRL_STATE_UNINIT = 0
	ETHCTRL_STATE_INIT = 1

class EthIf_SignalQualityResultType:
	"""EthIf_SignalQualityResultType
	"""
	ActualSignalQuality: int
	HighestSignalQuality: int
	LowestSignalQuality: int

@enum.unique
class EthSM_NetworkModeStateType(enum.IntFlag):
	"""This type shall define the states of the network mode state machine.\n 
"""
	ETHSM_STATE_OFFLINE = 0
	ETHSM_STATE_WAIT_TRCVLINK = 1
	ETHSM_STATE_WAIT_ONLINE = 2
	ETHSM_STATE_ONLINE = 3
	ETHSM_STATE_ONHOLD = 4
	ETHSM_STATE_WAIT_OFFLINE = 5

class EthTrcv_ConfigType:
	"""Implementation specific structure of the post build configuration
	 
	"""
	"""EthTrcv_ConfigType
	"""
	dummy: int

@enum.unique
class EthTrcv_LinkStateType(enum.IntFlag):
	"""This type defines the Ethernet link state. The link state changes after an\n Ethernet cable gets plugged in and the transceivers on both ends negotiated the\n transmission parameters (i.e. baud rate and duplex mode)\n 
"""
	ETHTRCV_LINK_STATE_DOWN = 0
	ETHTRCV_LINK_STATE_ACTIVE = 1

@enum.unique
class EthTrcv_ModeType(enum.IntFlag):
	"""This type defines the transceiver modes\n 
"""
	ETHTRCV_MODE_DOWN = 0
	ETHTRCV_MODE_ACTIVE = 1

@enum.unique
class EthTrcv_StateType(enum.IntFlag):
	"""Status supervision used for Development Error Detection. The state shall be\n available for debugging.\n 
"""
	ETHTRCV_STATE_UNINIT = 0
	ETHTRCV_STATE_INIT = 1

@enum.unique
class EthTrcv_DuplexModeType(enum.IntFlag):
	"""This type defines the Ethernet duplex mode. The duplex mode gets either\n negotiated between the connected transceivers or has to be configured.\n 
"""
	ETHTRCV_DUPLEX_MODE_HALF = 0
	ETHTRCV_DUPLEX_MODE_FULL = 1

@enum.unique
class EthTrcv_BaudRateType(enum.IntFlag):
	"""This type defines the Ethernet baud rate. The baud rate gets either negotiated\n between the connected transceivers or has to be configured.\n 
"""
	ETHTRCV_BAUD_RATE_10MBIT = 0
	ETHTRCV_BAUD_RATE_100MBIT = 1
	ETHTRCV_BAUD_RATE_1000MBIT = 2

@enum.unique
class Eth_ModeType(enum.IntFlag):
	"""This type defines the controller modes\n 
"""
	ETH_MODE_DOWN = 0
	ETH_MODE_ACTIVE = 1

@enum.unique
class Eth_StateType(enum.IntFlag):
	"""Status supervision used for Development Error Detection. The state shall be\n available for debugging.\n 
"""
	ETH_STATE_UNINIT = 0
	ETH_STATE_INIT = 1

class Eth_RxStatsType:
	"""Statistic counter for diagnostics.
	 
	"""
	"""Eth_RxStatsType
	"""
	RxStatsBroadcastPkts: int
	RxStatsCollisions: int
	RxStatsCrcAlignErrors: int
	RxStatsDropEvents: int
	RxStatsFragments: int
	RxStatsJabbers: int
	RxStatsMulticastPkts: int
	RxStatsOctets: int
	RxStatsOversizePkts: int
	RxStatsPkts: int
	RxStatsPkts1024to1518Octets: int
	RxStatsPkts128to255Octets: int
	RxStatsPkts256to511Octets: int
	RxStatsPkts512to1023Octets: int
	RxStatsPkts64Octets: int
	RxStatsPkts65to127Octets: int
	RxStatsUndersizePkts: int
	RxUnicastFrames: int

class Eth_TxStatsType:
	"""Statistic counter for diagnostics.
	 
	"""
	"""Eth_TxStatsType
	"""
	TxNUcastPkts: int
	TxNumberOfOctets: int
	TxUniCastPkts: int

class Eth_TxErrorCounterValuesType:
	"""Statistic counters for diagnostics.
	 
	"""
	"""Eth_TxErrorCounterValuesType
	"""
	TxDeferredTrans: int
	TxDroppedErrorPkts: int
	TxDroppedNoErrorPkts: int
	TxExcessiveCollison: int
	TxLateCollision: int
	TxMultipleCollision: int
	TxSingleCollision: int

@enum.unique
class Eth_RxStatusType(enum.IntFlag):
	"""Used as out parameter in Eth_Receive() indicates whether a frame has been\n received and if so, whether more frames are available or frames got lost.\n 
"""
	ETH_RECEIVED = 0
	ETH_NOT_RECEIVED = 1
	ETH_RECEIVED_MORE_DATA_AVAILABLE = 2

@enum.unique
class Eth_FilterActionType(enum.IntFlag):
	"""The Enumeration Type Eth_FilterActionType describes the action to be taklen for\n the MAC address given in *PhysAddrPtr.\n 
"""
	ETH_ADD_TO_FILTER = 0
	ETH_REMOVE_FROM_FILTER = 1

class Eth_TimeStampType:
	"""Variables of this type are used for expressing time stamps including relative
	 time and absolute calendar time. The absolute time starts at 1970-01-01.
	
	 0 to 281474976710655s
	 	== 3257812230d
	 	[0xFFFF FFFF FFFF]
	
	 0 to 999999999ns
	 	[0x3B9A C9FF]
	 	invalid value in nanoseconds: [0x3B9A CA00] to [0x3FFF FFFF]
	 	Bit 30 and 31 reserved, default: 0
	 
	"""
	"""Eth_TimeStampType
	"""
	nanoseconds: int
	seconds: int
	secondsHi: int

class Eth_TimeIntDiffType:
	"""Variables of this type are used to express time differences.
	 
	"""
	"""Eth_TimeIntDiffType
	"""
	diff: vspyx.AUTOSAR.Classic.Eth_TimeStampType
	sign: int

class Eth_RateRatioType:
	"""Variables of this type are used to express frequency ratios.
	 
	"""
	"""Eth_RateRatioType
	"""
	IngressTimeStampDelta: vspyx.AUTOSAR.Classic.Eth_TimeIntDiffType
	OriginTimeStampDelta: vspyx.AUTOSAR.Classic.Eth_TimeIntDiffType

class Eth_MacVlanType:
	"""This type is used to read out addresses from the address resolution logic (ARL)
	 table of the switch.
	 
	 typedef struct {
	  uint8  MacAddr[6U];
	  uint16 VlanId;
	  uint32 SwitchPort;
	 } Eth_MacVlanType;
	 
	 In case of Macaddr contains a Multicast Address MacVlanType.SwitchPort shall be
	 handled as Bitmask, each bit represents a Switch Port, Bit 0 represents
	 EthSwichtPortIdx = 0 , Bit 1 represents EthSwichtPortIdx = 1 and so on.
	 In case of Macaddr contains not a Multicast Address MacVlanType.SwitchPort
	 shall be handled as a value representing the EthSwitchPortIdx.
	 
	"""
	"""Eth_MacVlanType
	"""
	SwitchPort: int
	VlanId: int

class Eth_CounterType:
	"""Statistic counter for diagnostics.
	 
	"""
	"""Eth_CounterType
	"""
	AlgnmtErr: int
	DfrdPkt: int
	DiscInbdPkt: int
	DiscOtbdPkt: int
	DropPktBufOverrun: int
	DropPktCrc: int
	ErrInbdPkt: int
	ErrOtbdPkt: int
	HwDepCtr0: int
	HwDepCtr1: int
	HwDepCtr2: int
	HwDepCtr3: int
	LatCollPkt: int
	MultCollPkt: int
	OversizePkt: int
	SnglCollPkt: int
	SqeTestErr: int
	UndersizePkt: int

@enum.unique
class EthTrcv_WakeupModeType(enum.IntFlag):
	"""This type controls the transceiver wake up modes and/or clears the wake-up\n reason.\n 
"""
	ETHTRCV_WUM_DISABLE = 0
	ETHTRCV_WUM_ENABLE = 1
	ETHTRCV_WUM_CLEAR = 2

@enum.unique
class EthTrcv_WakeupReasonType(enum.IntFlag):
	"""This type defines the transceiver wake up reasons.\n 
"""
	ETHTRCV_WUR_NONE = 0
	ETHTRCV_WUR_GENERAL = 1
	ETHTRCV_WUR_BUS = 2
	ETHTRCV_WUR_INTERNAL = 3
	ETHTRCV_WUR_RESET = 4
	ETHTRCV_WUR_POWER_ON = 5
	ETHTRCV_WUR_PIN = 6
	ETHTRCV_WUR_SYSERR = 7

@enum.unique
class EthTrcv_PhyTestModeType(enum.IntFlag):
	"""Describes the possible PHY test modes\n 
"""
	ETHTRCV_PHYTESTMODE_NONE = 0
	ETHTRCV_PHYTESTMODE_1 = 1
	ETHTRCV_PHYTESTMODE_2 = 2
	ETHTRCV_PHYTESTMODE_3 = 3
	ETHTRCV_PHYTESTMODE_4 = 4
	ETHTRCV_PHYTESTMODE_5 = 5

@enum.unique
class EthTrcv_PhyLoopbackModeType(enum.IntFlag):
	"""Describes the possible PHY loopback modes\n 
"""
	ETHTRCV_PHYLOOPBACK_NONE = 0
	ETHTRCV_PHYLOOPBACK_INTERNAL = 1
	ETHTRCV_PHYLOOPBACK_EXTERNAL = 2
	ETHTRCV_PHYLOOPBACK_REMOTE = 3

@enum.unique
class EthTrcv_PhyTxModeType(enum.IntFlag):
	"""Describes the possible PHY transmit modes\n 
"""
	ETHTRCV_PHYTXMODE_NORMAL = 0
	ETHTRCV_PHYTXMODE_TX_OFF = 1
	ETHTRCV_PHYTXMODE_SCRAMBLER_OFF = 2

@enum.unique
class EthTrcv_CableDiagResultType(enum.IntFlag):
	"""Describes the results of the cable diagnostics.\n 
"""
	ETHTRCV_CABLEDIAG_OK = 0
	ETHTRCV_CABLEDIAG_ERROR = 1
	ETHTRCV_CABLEDIAG_SHORT = 2
	ETHTRCV_CABLEDIAG_OPEN = 3
	ETHTRCV_CABLEDIAG_PENDING = 4
	ETHTRCV_CABLEDIAG_WRONG_POLARITY = 5

@enum.unique
class EthSwt_StateType(enum.IntFlag):
	"""Status supervision used for Development Error Detection. The state shall be\n available for debugging.\n 
"""
	ETHSWT_STATE_UNINIT = 0
	ETHSWT_STATE_INIT = 1
	ETHSWT_STATE_ACTIVE = 2

@enum.unique
class EthSwt_MacLearningType(enum.IntFlag):
	"""The interpretation of this value \n 
"""
	ETHSWT_MACLEARNING_HWDISABLED = 0
	ETHSWT_MACLEARNING_HWENABLED = 1
	ETHSWT_MACLEARNING_SWENABLED = 2

class EthSwt_ConfigType:
	"""Implementation specific structure of the post build configuration.
	 
	"""
	"""EthSwt_ConfigType
	"""
	dummy: int

@enum.unique
class EthSwt_MgmtOwner(enum.IntFlag):
	"""Holds information if upper layer or EthSwt is owner of mgmt_obj.\n 
"""
	ETHSWT_MGMT_OBJ_UNUSED = 0
	ETHSWT_MGMT_OBJ_OWNED_BY_ETHSWT = 1
	ETHSWT_MGMT_OBJ_OWNED_BY_UPPER_LAYER = 2

class EthSwt_MgmtObjectValidType:
	"""Will be set from EthSwt and marks EthSwt_MgmtObject as valid or not.
	 So the upper layer will be able to detect inconsistencies.
	 
	"""
	"""EthSwt_MgmtObjectValidType
	"""
	EgressTimestampValid: int
	IngressTimestampValid: int
	MgmtInfoValid: int

class EthSwt_MgmtInfoType:
	"""Type for holding the management information received/transmitted on Switches
	 (ports).
	 
	"""
	"""EthSwt_MgmtInfoType
	"""
	SwitchIdx: int
	SwitchPortIdx: int

class EthSwt_MgmtObjectType:
	"""Provides information about all struct member elements. The ownership gives
	 information whether EthSwt has finished its activities in providing all struct
	 member elements.
	 
	"""
	"""EthSwt_MgmtObjectType
	"""
	EgressTimestamp: vspyx.AUTOSAR.Classic.Eth_TimeStampType
	IngressTimestamp: vspyx.AUTOSAR.Classic.Eth_TimeStampType
	MgmtInfo: vspyx.AUTOSAR.Classic.EthSwt_MgmtInfoType
	Ownership: vspyx.AUTOSAR.Classic.EthSwt_MgmtOwner
	Validation: vspyx.AUTOSAR.Classic.EthSwt_MgmtObjectValidType

class EthSwt_PortMirrorCfgType:
	"""The EthSwt_PortMirrorCfgType specify the port mirror configuration which is set
	 up per Ethernet switch. The configuration is written to the Ethernet switch
	 driver by calling EthSwt_WritePortMirrorConfiguration. One port mirror
	 configuration is maintained per Ethernet Switch.
	 
	"""
	"""EthSwt_PortMirrorCfgType
	"""
	CapturePortIdx: int
	DoubleTaggingVlanId: int
	MirroringMode: int
	MirroringPacketDivider: int
	ReTaggingVlanId: int
	TrafficDirectionEgressBitMask: int
	TrafficDirectionIngressBitMask: int
	VlanIdFilter: int

@enum.unique
class EthSwt_PortMirrorStateType(enum.IntFlag):
	"""Type to request or obtain the port mirroring state (enable/disable) for a\n particular port mirror configuration per Ethernet switch.\n 
"""
	PORT_MIRRORING_DISABLED = 0
	PORT_MIRRORING_ENABLED = 1

@enum.unique
class EthTSyn_TransmissionModeType(enum.IntFlag):
	"""Handles the enabling and disabling of the transmission mode\n 
"""
	ETHTSYN_TX_OFF = 0
	ETHTSYN_TX_ON = 1

class EthTSyn_ConfigType:
	"""This is the base type for the configuration of the Global Time Synchronization
	 over Ethernet.
	 A pointer to an instance of this structure will be used in the initialization
	 of the Global Time Synchronization over Ethernet.
	 The content of this structure is defined in chapter 10 Configuration
	 specification.
	 
	"""
	"""EthTSyn_ConfigType
	"""
	dummy: int

class FrArTp_ConfigType:
	"""This is the base type for the configuration of the FlexRay Transport Protocol.
	 
	 A pointer to an instance of this structure will be used in the initialization
	 of the FlexRay Transport Protocol.
	 
	 The outline of the structure is defined in chapter 10 Configuration
	 Specification.
	 
	"""
	"""FrArTp_ConfigType
	"""
	dummy: int

class FrIf_ConfigType:
	"""[SWS_FrIf_05301]
	 This type contains the implementation-specific post build time configuration
	 structure. Only pointers of this type are allowed.
	 
	"""
	"""FrIf_ConfigType
	"""

@enum.unique
class FrIf_StateType(enum.IntFlag):
	"""[SWS_FrIf_05755]\n Variables of this type are used to represent the FrIf_State of a FlexRay CC.\n 
"""
	FRIF_STATE_OFFLINE = 0
	FRIF_STATE_ONLINE = 1

@enum.unique
class FrIf_StateTransitionType(enum.IntFlag):
	"""[SWS_FrIf_05303]\n Variables of this type are used to represent the FrIf_State of a FlexRay CC.\n 
"""
	FRIF_GOTO_OFFLINE = 0
	FRIF_GOTO_ONLINE = 1

class FrNm_ConfigType:
	"""Contains configuration parameters.
	 
	"""
	"""FrNm_ConfigType
	"""
	dummy: int

class FrSM_ConfigType:
	"""This type contains the implementation-specific post build time configuration
	 structure that is for FrSM_Init.
	 
	"""
	"""FrSM_ConfigType
	"""
	dummy: int

@enum.unique
class FrSM_BswM_StateType(enum.IntFlag):
	"""This type defines the states that are reported to the BswM using\n BswM_FrSM_CurrentState.\n 
"""
	FRSM_BSWM_READY = 0
	FRSM_BSWM_READY_ECU_PASSIVE = 1
	FRSM_BSWM_STARTUP = 2
	FRSM_BSWM_STARTUP_ECU_PASSIVE = 3
	FRSM_BSWM_WAKEUP = 4
	FRSM_BSWM_WAKEUP_ECU_PASSIVE = 5
	FRSM_BSWM_HALT_REQ = 6
	FRSM_BSWM_HALT_REQ_ECU_PASSIVE = 7
	FRSM_BSWM_KEYSLOT_ONLY = 8
	FRSM_BSWM_KEYSLOT_ONLY_ECU_PASSIVE = 9
	FRSM_BSWM_ONLINE = 10
	FRSM_BSWM_ONLINE_ECU_PASSIVE = 11
	FRSM_BSWM_ONLINE_PASSIVE = 12
	FRSM_BSWM_ONLINE_PASSIVE_ECU_PASSIVE = 13
	FRSM_LOW_NUMBER_OF_COLDSTARTERS = 14
	FRSM_LOW_NUMBER_OF_COLDSTARTERS_ECU_PASSIVE = 15

@enum.unique
class FrTSyn_TransmissionModeType(enum.IntFlag):
	"""Handles the enabling and disabling of the transmission mode\n 
"""
	FRTSYN_TX_OFF = 0
	FRTSYN_TX_ON = 1

class FrTSyn_ConfigType:
	"""This is the base type for the configuration of the Time Synchronization over
	 FlexRay.
	 
	 A pointer to an instance of this structure will be used in the initialization
	 of the Time Synchronization over FlexRay.
	 
	 The content of this structure is defined in chapter 10 Configuration
	 specification.
	 
	"""
	"""FrTSyn_ConfigType
	"""
	dummy: int

class FrTp_ConfigType:
	"""This is the base type for the configuration of the FlexRay Transport Protocol
	 
	 A pointer to an instance of this structure will be used in the initialization
	 of the FlexRay Transport Protocol.
	 
	 The outline of the structure is defined in chapter 10 Configuration
	 Specification
	 
	"""
	"""FrTp_ConfigType
	"""
	dummy: int

@enum.unique
class FrTrcv_TrcvModeType(enum.IntFlag):
	"""Transceiver modes in state ACTIVE.\n 
"""
	FRTRCV_TRCVMODE_NORMAL = 0
	FRTRCV_TRCVMODE_STANDBY = 1
	FRTRCV_TRCVMODE_SLEEP = 2
	FRTRCV_TRCVMODE_RECEIVEONLY = 3

@enum.unique
class FrTrcv_TrcvWUReasonType(enum.IntFlag):
	"""This type to be used to specify the wake up reason detected by the FR\n transceiver in detail.\n 
"""
	FRTRCV_WU_NOT_SUPPORTED = 0
	FRTRCV_WU_BY_BUS = 1
	FRTRCV_WU_BY_PIN = 2
	FRTRCV_WU_INTERNALLY = 3
	FRTRCV_WU_RESET = 4
	FRTRCV_WU_POWER_ON = 5

class FrTrcv_ConfigType:
	"""Configuration data structure of the FrTrcv module.
	 
	"""
	"""FrTrcv_ConfigType
	"""
	dummy: int

class Fr_ConfigType:
	"""[SWS_Fr_91001]
	 This type contains the implementation-specific post build configuration structure.
	 
	"""
	"""Fr_ConfigType
	"""

@enum.unique
class Fr_POCStateType(enum.IntEnum):
	"""[SWS_Fr_00505]\n This formal definition refers to the description of type T_POCState in chapter 2.2.1.3\n POC status of [12].\n 
"""
	FR_POCSTATE_CONFIG = 0
	FR_POCSTATE_DEFAULT_CONFIG = 1
	FR_POCSTATE_HALT = 2
	FR_POCSTATE_NORMAL_ACTIVE = 3
	FR_POCSTATE_NORMAL_PASSIVE = 4
	FR_POCSTATE_READY = 5
	FR_POCSTATE_STARTUP = 6
	FR_POCSTATE_WAKEUP = 7

@enum.unique
class Fr_SlotModeType(enum.IntEnum):
	"""[SWS_Fr_00506]\n This formal definition refers to the description of type T_SlotMode in chapter 2.2.1.3\n POC status of [12].\n 
"""
	FR_SLOTMODE_KEYSLOT = 0
	FR_SLOTMODE_ALL_PENDING = 1
	FR_SLOTMODE_ALL = 2

@enum.unique
class Fr_ErrorModeType(enum.IntEnum):
	"""[SWS_Fr_00507]\n This formal definition refers to the description of type T_ErrorMode in chapter 2.2.1.3\n POC status of [12].\n 
"""
	FR_ERRORMODE_ACTIVE = 0
	FR_ERRORMODE_PASSIVE = 1
	FR_ERRORMODE_COMM_HALT = 2

@enum.unique
class Fr_WakeupStatusType(enum.IntEnum):
	"""[SWS_Fr_00508]\n This formal definition refers to the description of type T_WakeupStatus in chapter\n 2.2.1.3 POC status of [12].\n 
"""
	FR_WAKEUP_UNDEFINED = 0
	FR_WAKEUP_RECEIVED_HEADER = 1
	FR_WAKEUP_RECEIVED_WUP = 2
	FR_WAKEUP_COLLISION_HEADER = 3
	FR_WAKEUP_COLLISION_WUP = 4
	FR_WAKEUP_COLLISION_UNKNOWN = 5
	FR_WAKEUP_TRANSMITTED = 6

@enum.unique
class Fr_StartupStateType(enum.IntEnum):
	"""[SWS_Fr_00509]\n This formal definition refers to the description of type T_StartupState in chapter 2.2.1.3\n POC status of [12].\n 
"""
	FR_STARTUP_UNDEFINED = 0
	FR_STARTUP_COLDSTART_LISTEN = 1
	FR_STARTUP_INTEGRATION_COLDSTART_CHECK = 2
	FR_STARTUP_COLDSTART_JOIN = 3
	FR_STARTUP_COLDSTART_COLLISION_RESOLUTION = 4
	FR_STARTUP_COLDSTART_CONSISTENCY_CHECK = 5
	FR_STARTUP_INTEGRATION_LISTEN = 6
	FR_STARTUP_INITIALIZE_SCHEDULE = 7
	FR_STARTUP_INTEGRATION_CONSISTENCY_CHECK = 8
	FR_STARTUP_COLDSTART_GAP = 9
	FR_STARTUP_EXTERNAL_STARTUP = 10

class Fr_POCStatusType:
	"""[SWS_Fr_00510]
	 This formal definition refers to the description of type T_POCStatus in chapter
	 2.2.1.3 POC status of [12].
	 
	"""
	"""Fr_POCStatusType
	"""
	CHIHaltRequest: int
	ColdstartNoise: int
	ErrorMode: vspyx.AUTOSAR.Classic.Fr_ErrorModeType
	Freeze: int
	SlotMode: vspyx.AUTOSAR.Classic.Fr_SlotModeType
	StartupState: vspyx.AUTOSAR.Classic.Fr_StartupStateType
	State: vspyx.AUTOSAR.Classic.Fr_POCStateType
	WakeupStatus: vspyx.AUTOSAR.Classic.Fr_WakeupStatusType
	CHIReadyRequest: int

@enum.unique
class Fr_TxLPduStatusType(enum.IntEnum):
	"""[SWS_Fr_00511]\n These values are used to determine whether a LPdu has been transmitted or not.\n 
"""
	FR_TRANSMITTED = 0
	FR_TRANSMITTED_CONFLICT = 26
	FR_NOT_TRANSMITTED = 2

@enum.unique
class Fr_RxLPduStatusType(enum.IntEnum):
	"""[SWS_Fr_00512]\n These values are used to determine if a LPdu has been received or not.\n 
"""
	FR_RECEIVED = 0
	FR_NOT_RECEIVED = 1
	FR_RECEIVED_MORE_DATA_AVAILABLE = 2

@enum.unique
class Fr_ChannelType(enum.IntEnum):
	"""[SWS_Fr_00514]\n The values are used to reference channels on a CC.\n 
"""
	FR_CHANNEL_A = 1
	FR_CHANNEL_B = 2
	FR_CHANNEL_AB = 3

class Fr_SlotAssignmentType:
	"""[SWS_Fr_91002]
	 This structure contains information about the assignment of a FlexRay frame to a
	 cycle and a slot ID.
	 
	"""
	"""Fr_SlotAssignmentType
	"""
	Cycle: int
	SlotId: int
	channelId: vspyx.AUTOSAR.Classic.Fr_ChannelType

class IpduM_ConfigType:
	"""This is the type of the data structure containing the initialization data for
	 the I-PDU multiplexer.
	 
	"""
	"""IpduM_ConfigType
	"""
	dummy: int

class J1939Nm_ConfigType:
	"""This is the base type for the configuration of the J1939 Network Management
	 module.
	 
	 A pointer to an instance of this structure will be used in the initialization
	 of the J1939 Network Management module.
	 
	 The content of this structure is defined in chapter 10 Configuration
	 specification.
	 
	"""
	"""J1939Nm_ConfigType
	"""
	dummy: int

@enum.unique
class J1939Rm_StateType(enum.IntFlag):
	"""This type represents the communication state of the J1939 Request Manager.\n 
"""
	pass

class J1939Rm_ConfigType:
	"""This is the base type for the configuration of the J1939 Request Manager.
	 
	 A pointer to an instance of this structure will be used in the initialization
	 of the J1939 Request Manager.
	 
	 The content of this structure is defined in chapter 10 Configuration
	 specification.
	 
	"""
	"""J1939Rm_ConfigType
	"""
	dummy: int

@enum.unique
class J1939Rm_AckCode(enum.IntFlag):
	"""This type represents the available kinds of acknowledgements.\n 
"""
	pass

@enum.unique
class J1939Rm_ExtIdType(enum.IntFlag):
	"""This type represents the available kinds of extended identifier usage.\n 
"""
	pass

class J1939Rm_ExtIdInfoType:
	"""This type represents a set of extended identifiers.
	 
	"""
	"""J1939Rm_ExtIdInfoType
	"""
	extId1: int
	extId2: int
	extId3: int
	extIdType: vspyx.AUTOSAR.Classic.J1939Rm_ExtIdType

class J1939Tp_ConfigType:
	"""Data structure containing post-build configuration data of J1939-TP.
	 
	"""
	"""J1939Tp_ConfigType
	"""
	dummy: int

class Lin_ConfigType:
	"""This is the type of the external data structure containing the overall
	 initialization data for the LIN driver and the SFR settings affecting the LIN
	 channels. A pointer to such a structure is provided to the LIN driver
	 initialization routine for configuration of the driver, LIN hardware unit and
	 LIN hardware channels.
	 
	"""
	"""Lin_ConfigType
	"""
	dummy: int

@enum.unique
class LinTrcv_TrcvWakeupReasonType(enum.IntFlag):
	"""This type denotes the wake up reason detected by the LIN transceiver in detail.\n 
"""
	pass

@enum.unique
class LinTrcv_TrcvWakeupModeType(enum.IntFlag):
	"""Wake up operating modes of the LIN Transceiver Driver.\n 
"""
	pass

@enum.unique
class Lin_FrameCsModelType(enum.IntFlag):
	"""This type is used to specify the Checksum model to be used for the LIN Frame.\n 
"""
	LIN_ENHANCED_CS = 0
	LIN_CLASSIC_CS = 1

@enum.unique
class Lin_FrameResponseType(enum.IntFlag):
	"""This type is used to specify whether the frame processor is required to\n transmit the response part of the LIN frame.\n 
"""
	LIN_FRAMERESPONSE_TX = 0
	LIN_FRAMERESPONSE_RX = 1
	LIN_FRAMERESPONSE_IGNORE = 2

class Lin_PduType:
	"""This Type is used to provide PID, checksum model, data length and SDU pointer
	 from the LIN Interface to the LIN driver.
	 
	"""
	"""Lin_PduType
	"""
	Cs: vspyx.AUTOSAR.Classic.Lin_FrameCsModelType
	Dl: int
	Drc: vspyx.AUTOSAR.Classic.Lin_FrameResponseType
	Pid: int

@enum.unique
class Lin_StatusType(enum.IntFlag):
	"""LIN operation states for a LIN channel or frame, as returned by the API service\n Lin_GetStatus().\n 
"""
	LIN_NOT_OK = 0
	LIN_TX_OK = 1
	LIN_TX_BUSY = 2
	LIN_TX_HEADER_ERROR = 3
	LIN_TX_ERROR = 4
	LIN_RX_OK = 5
	LIN_RX_BUSY = 6
	LIN_RX_ERROR = 7
	LIN_RX_NO_RESPONSE = 8
	LIN_OPERATIONAL = 9
	LIN_CH_SLEEP = 10

@enum.unique
class Lin_SlaveErrorType(enum.IntFlag):
	"""This type represents the slave error types that are detected during header\n reception and response transmission / reception.\n 
"""
	LIN_ERR_HEADER = 0
	LIN_ERR_RESP_STOPBIT = 1
	LIN_ERR_RESP_CHKSUM = 2
	LIN_ERR_RESP_DATABIT = 3
	LIN_ERR_NO_RESP = 4
	LIN_ERR_INC_RESP = 5

class LinTp_ConfigType:
	"""This is the base type for the configuration of the LIN Transport Protocol
	 
	 A pointer to an instance of this structure will be used in the initialization
	 of the LIN Transport Protocol.
	 
	 The outline of the structure is defined in chapter 10 Configuration
	 Specification
	 
	"""
	"""LinTp_ConfigType
	"""
	dummy: int

@enum.unique
class LinTp_Mode(enum.IntFlag):
	"""This type denotes which Schedule table can be requested by LIN TP during\n diagnostic session\n 
"""
	LINTP_APPLICATIVE_SCHEDULE = 0
	LINTP_DIAG_REQUEST = 1
	LINTP_DIAG_RESPONSE = 2

class LinIf_ConfigType:
	"""A pointer to an instance of this structure will be used in the initialization
	 of the LIN Interface.
	 
	 The outline of the structure is defined in chapter 10 Configuration
	 Specification.
	 
	"""
	"""LinIf_ConfigType
	"""
	dummy: int

class LinSM_ConfigType:
	"""Data structure type for the post-build configuration parameters.
	 
	"""
	"""LinSM_ConfigType
	"""
	dummy: int

@enum.unique
class LinTrcv_TrcvModeType(enum.IntFlag):
	"""Operating modes of the LIN Transceiver Driver\n 
"""
	pass

class LinTrcv_ConfigType:
	"""Configuration data structure of the LinTrcv module.
	 
	"""
	"""LinTrcv_ConfigType
	"""
	dummy: int

@enum.unique
class AppModeType(enum.IntFlag):
	"""AppMode of the core shall be inherited from another core.\n 
"""
	DONOTCARE = 0

@enum.unique
class TryToGetSpinlockType(enum.IntFlag):
	"""The TryToGetSpinlockType indicates if the spinlock has been occupied or not.\n 
"""
	TRYTOGETSPINLOCK_SUCCESS = 0
	TRYTOGETSPINLOCK_NOSUCCESS = 1

@enum.unique
class Nm_StateType(enum.IntFlag):
	"""States of the network management state machine.\n 
"""
	NM_STATE_UNINIT = 0
	NM_STATE_BUS_SLEEP = 1
	NM_STATE_PREPARE_BUS_SLEEP = 2
	NM_STATE_READY_SLEEP = 3
	NM_STATE_NORMAL_OPERATION = 4
	NM_STATE_REPEAT_MESSAGE = 5
	NM_STATE_SYNCHRONIZE = 6
	NM_STATE_OFFLINE = 7

@enum.unique
class Nm_ModeType(enum.IntFlag):
	"""Operational modes of the network management.\n 
"""
	NM_MODE_BUS_SLEEP = 0
	NM_MODE_PREPARE_BUS_SLEEP = 1
	NM_MODE_SYNCHRONIZE = 2
	NM_MODE_NETWORK = 3

@enum.unique
class Nm_BusNmType(enum.IntFlag):
	"""BusNm Type\n 
"""
	NM_BUSNM_CANNM = 0
	NM_BUSNM_FRNM = 1
	NM_BUSNM_UDPNM = 2
	NM_BUSNM_GENERICNM = 3
	NM_BUSNM_UNDEF = 4
	NM_BUSNM_J1939NM = 5
	NM_BUSNM_LOCALNM = 6

class Nm_ConfigType:
	"""Configuration data structure of the Nm module.
	 
	"""
	"""Nm_ConfigType
	"""
	dummy: int

@enum.unique
class NvM_MultiBlockRequestType(enum.IntFlag):
	"""Identifies the type of request performed on multi block when signaled via the\n callback function or when reporting to BswM\n 
"""
	NVM_READ_ALL = 0
	NVM_WRITE_ALL = 1
	NVM_VALIDATE_ALL = 2
	NVM_FIRST_INIT_ALL = 3
	NVM_CANCEL_WRITE_ALL = 4

class NvM_ConfigType:
	"""Configuration data structure of the NvM module.
	 
	"""
	"""NvM_ConfigType
	"""
	dummy: int

@enum.unique
class StatusType(enum.IntEnum):
	E_OK = 0
	E_OS_ACCESS = 1
	E_OS_CALLEVEL = 2
	E_OS_ID = 3
	E_OS_LIMIT = 4
	E_OS_NOFUNC = 5
	E_OS_RESOURCE = 6
	E_OS_STATE = 7
	E_OS_VALUE = 8

class TickType:
	"""TickType
	"""
	Tick: int

@enum.unique
class AUTOSAR_ApplicationType(enum.IntFlag):
	"""This data type identifies the OS-Application.\n 
"""
	INVALID_OSAPPLICATION = 0

@enum.unique
class ApplicationStateType(enum.IntFlag):
	"""This data type identifies the state of an OS-Application.\n	 
"""
	APPLICATION_ACCESSIBLE = 0
	APPLICATION_RESTARTING = 1
	APPLICATION_TERMINATED = 2

@enum.unique
class ObjectAccessType(enum.IntFlag):
	"""This data type identifies if an OS-Application has access to an object.\n	 
"""
	ACCESS = 0
	NO_ACCESS = 1

@enum.unique
class ObjectTypeType(enum.IntFlag):
	"""This data type identifies an object.\n 
"""
	OBJECT_ALARM = 0
	OBJECT_COUNTER = 1
	OBJECT_ISR = 2
	OBJECT_RESOURCE = 3
	OBJECT_SCHEDULETABLE = 4
	OBJECT_TASK = 5

@enum.unique
class ISRType(enum.IntFlag):
	"""This data type identifies an interrupt service routine (ISR).\n	 
"""
	INVALID_ISR = 0

@enum.unique
class ScheduleTableStatusType(enum.IntFlag):
	"""This type describes the status of a schedule. The status can be one of the\n following:\n o	The schedule table is not started (SCHEDULETABLE_STOPPED)\n o	The schedule table will be started after the end of currently running\n schedule table (schedule table was used in NextScheduleTable() service)\n (SCHEDULETABLE_NEXT)\n o	The schedule table uses explicit synchronization, has been started and is\n waiting for the global time. (SCHEDULETABLE_WAITING)\n o	The schedule table is running, but is currently not synchronous to a global\n time source (SCHEDULETABLE_RUNNING)\n o	The schedule table is running and is synchronous to a global time source\n (SCHEDULETABLE_RUNNING_AND_SYNCHRONOUS)\n	 
"""
	SCHEDULETABLE_NEXT = 0
	SCHEDULETABLE_RUNNING = 1
	SCHEDULETABLE_RUNNING_AND_SYNCHRONOUS = 2
	SCHEDULETABLE_STOPPED = 3
	SCHEDULETABLE_WAITING = 4

@enum.unique
class ProtectionReturnType(enum.IntFlag):
	"""This data type identifies a value which controls further actions of the OS on\n return from the protection hook.\n	 
"""
	PRO_IGNORE = 0
	PRO_SHUTDOWN = 1
	PRO_TERMINATEAPPL = 2
	PRO_TERMINATEAPPL_RESTART = 3
	PRO_TERMINATETASKISR = 4

@enum.unique
class RestartType(enum.IntFlag):
	"""This data type defines the use of a Restart Task after terminating an OS-\n Application.\n	 
"""
	NO_RESTART = 0
	RESTART = 1

@enum.unique
class IdleModeType(enum.IntFlag):
	"""This data type identifies the idle mode behavior.\n	 
"""
	IDLE_NO_HALT = 0

class PduR_PBConfigType:
	"""Data structure containing post-build-time configuration data of the PDU Router.
	 
	"""
	"""PduR_PBConfigType
	"""
	dummy: int

@enum.unique
class PduR_StateType(enum.IntFlag):
	"""States of the PDU Router\n 
"""
	PDUR_UNINIT = 0
	PDUR_ONLINE = 1

@enum.unique
class Sd_ServerServiceSetStateType(enum.IntFlag):
	"""This type defines the Server states that are reported to the SD using the\n expected API Sd_ServerServiceSetState.\n 
"""
	SD_SERVER_SERVICE_DOWN = 0
	SD_SERVER_SERVICE_AVAILABLE = 1

@enum.unique
class Sd_ClientServiceSetStateType(enum.IntFlag):
	"""This type defines the Client states that are reported to the BswM using the\n expected API Sd_ClientServiceSetState.\n 
"""
	SD_CLIENT_SERVICE_RELEASED = 0
	SD_CLIENT_SERVICE_REQUESTED = 1

@enum.unique
class Sd_ConsumedEventGroupSetStateType(enum.IntFlag):
	"""This type defines the subscription policy by consumed EventGroup for the Client\n Service.\n 
"""
	SD_CONSUMED_EVENTGROUP_RELEASED = 0
	SD_CONSUMED_EVENTGROUP_REQUESTED = 1

@enum.unique
class Sd_ClientServiceCurrentStateType(enum.IntFlag):
	"""This type defines the modes to indicate the current mode request of a Client\n Service.\n 
"""
	SD_CLIENT_SERVICE_DOWN = 0
	SD_CLIENT_SERVICE_AVAILABLE = 1

class Sd_ConfigType:
	"""Configuration data structure of Sd module.
	 
	"""
	"""Sd_ConfigType
	"""
	dummy: int

@enum.unique
class Sd_ConsumedEventGroupCurrentStateType(enum.IntFlag):
	"""This type defines the subscription policy by consumed EventGroup for the Client\n Service.\n 
"""
	SD_CONSUMED_EVENTGROUP_DOWN = 0
	SD_CONSUMED_EVENTGROUP_AVAILABLE = 1

@enum.unique
class Sd_EventHandlerCurrentStateType(enum.IntFlag):
	"""This type defines the subscription policy by EventHandler for the Server\n Service.\n 
"""
	SD_EVENT_HANDLER_RELEASED = 0
	SD_EVENT_HANDLER_REQUESTED = 1

class SoAd_ConfigType:
	"""Configuration data structure of the SoAd module.
	 
	"""
	"""SoAd_ConfigType
	"""
	dummy: int

@enum.unique
class SoAd_SoConModeType(enum.IntFlag):
	"""type to specify the state of a SoAd socket connection.\n 
"""
	SOAD_SOCON_ONLINE = 0
	SOAD_SOCON_RECONNECT = 1
	SOAD_SOCON_OFFLINE = 2

class TcpIp_ArpCacheEntryType:
	"""TcpIp_ArpCacheEntries elements type
	 
	"""
	"""TcpIp_ArpCacheEntryType
	"""
	State: int

class TcpIp_NdpCacheEntryType:
	"""TcpIp_NdpCacheEntries elements type
	 
	"""
	"""TcpIp_NdpCacheEntryType
	"""
	State: int

class TcpIp_ConfigType:
	"""Configuration data structure of the TcpIp module.
	 
	"""
	"""TcpIp_ConfigType
	"""
	dummy: int

@enum.unique
class TcpIp_IpAddrAssignmentType(enum.IntFlag):
	"""Specification of IPv4/IPv6 address assignment policy.\n 
"""
	TCPIP_IPADDR_ASSIGNMENT_STATIC = 0
	TCPIP_IPADDR_ASSIGNMENT_LINKLOCAL_DOIP = 1
	TCPIP_IPADDR_ASSIGNMENT_DHCP = 2
	TCPIP_IPADDR_ASSIGNMENT_LINKLOCAL = 3
	TCPIP_IPADDR_ASSIGNMENT_IPV6_ROUTER = 4
	TCPIP_IPADDR_ASSIGNMENT_ALL = 5

@enum.unique
class TcpIp_StateType(enum.IntFlag):
	"""Specifies the TcpIp state for a specific EthIf controller.\n 
"""
	TCPIP_STATE_ONLINE = 0
	TCPIP_STATE_ONHOLD = 1
	TCPIP_STATE_OFFLINE = 2
	TCPIP_STATE_STARTUP = 3
	TCPIP_STATE_SHUTDOWN = 4

@enum.unique
class TcpIp_IpAddrStateType(enum.IntFlag):
	"""Specifies the state of local IP address assignment\n 
"""
	TCPIP_IPADDR_STATE_ASSIGNED = 0
	TCPIP_IPADDR_STATE_ONHOLD = 1
	TCPIP_IPADDR_STATE_UNASSIGNED = 2

@enum.unique
class TcpIp_ReturnType(enum.IntFlag):
	"""TcpIp specific return type.\n 
"""
	TCPIP_E_OK = 0
	TCPIP_E_NOT_OK = 1
	TCPIP_E_PHYS_ADDR_MISS = 2

@enum.unique
class TcpIp_EventType(enum.IntFlag):
	"""Events reported by TcpIp.\n 
"""
	TCPIP_TCP_RESET = 1
	TCPIP_TCP_CLOSED = 2
	TCPIP_TCP_FIN_RECEIVED = 3
	TCPIP_UDP_CLOSED = 4
	TCPIP_TLS_HANDSHAKE_SUCCEEDED = 5

@enum.unique
class TcpIp_ProtocolType(enum.IntFlag):
	"""Protocol type used by a socket.\n 
"""
	TCPIP_IPPROTO_TCP = 6
	TCPIP_IPPROTO_UDP = 17

class TcpIp_SockAddrInetType:
	"""This structure defines an IPv4 address type which can be derived from the
	 generic address structure via cast.
	 
	"""
	"""TcpIp_SockAddrInetType
	"""
	domain: int
	port: int

class TcpIp_SockAddrInet6Type:
	"""This structure defines a IPv6 address type which can be derived from the
	 generic address structure via cast.
	 
	"""
	"""TcpIp_SockAddrInet6Type
	"""
	domain: int
	port: int

class TcpIp_SockAddrType:
	"""Generic structure used by APIs to specify an IP address. (A specific address
	 type can be derived from this structure via a cast to the specific struct type.)
	 
	"""
	"""TcpIp_SockAddrType
	"""
	domain: int

	@staticmethod
	@typing.overload
	def From(addr: vspyx.Core.IPAddress, port: int) -> typing.Any: ...


	@staticmethod
	@typing.overload
	def From(addr: vspyx.Core.IPAddressAndPort) -> typing.Any: ...

@enum.unique
class Can_TTTimeSourceType(enum.IntFlag):
	"""TTCAN API functions\n Only functions which are additional to CAN are included\n \n\n Time source\n 
"""
	CAN_TT_CYCLE_TIME = 0
	CAN_TT_GLOBAL_TIME = 1
	CAN_TT_LOCAL_TIME = 2
	CAN_TT_UNDEFINED = 3

@enum.unique
class Can_TTErrorLevelEnumType(enum.IntFlag):
	"""Error level (S0-S3)\n 
"""
	CAN_TT_ERROR_S0 = 0
	CAN_TT_ERROR_S1 = 1
	CAN_TT_ERROR_S2 = 2
	CAN_TT_ERROR_S3 = 3

class Can_TTErrorLevelType:
	"""TTCAN error level including min and max values of message status count
	 
	"""
	"""Can_TTErrorLevelType
	"""
	errorLevel: vspyx.AUTOSAR.Classic.Can_TTErrorLevelEnumType
	maxMessageStatusCount: int
	minMessageStatusCount: int

@enum.unique
class Can_TTMasterSlaveModeType(enum.IntFlag):
	"""Master-Slave Mode\n 
"""
	CAN_TT_BACKUP_MASTER = 0
	CAN_TT_CURRENT_MASTER = 1
	CAN_TT_MASTER_OFF = 2
	CAN_TT_SLAVE = 3

@enum.unique
class Can_TTSyncModeEnumType(enum.IntFlag):
	"""Sync mode\n 
"""
	CAN_TT_IN_GAP = 0
	CAN_TT_IN_SCHEDULE = 1
	CAN_TT_SYNC_OFF = 2
	CAN_TT_SYNCHRONIZING = 3

class Can_TTMasterStateType:
	"""Master state type including sync mode, master-slave mode and current ref
	 trigger offset
	 
	"""
	"""Can_TTMasterStateType
	"""
	masterSlaveMode: vspyx.AUTOSAR.Classic.Can_TTMasterSlaveModeType
	refTriggerOffset: int
	syncMode: vspyx.AUTOSAR.Classic.Can_TTSyncModeEnumType

@enum.unique
class CanIf_TTSyncModeEnumType(enum.IntFlag):
	"""Sync mode\n 
"""
	CANIF_TT_IN_GAP = 0
	CANIF_TT_IN_SCHEDULE = 1
	CANIF_TT_SYNC_OFF = 2
	CANIF_TT_SYNCHRONIZING = 3

@enum.unique
class CanIf_TTErrorLevelEnumType(enum.IntFlag):
	"""Error level (S0-S3)\n 
"""
	CANIF_TT_ERROR_S0 = 0
	CANIF_TT_ERROR_S1 = 1
	CANIF_TT_ERROR_S2 = 2
	CANIF_TT_ERROR_S3 = 3

class CanIf_TTErrorLevelType:
	"""TTCAN error level including min and max values of message status count
	 
	"""
	"""CanIf_TTErrorLevelType
	"""
	errorLevel: vspyx.AUTOSAR.Classic.CanIf_TTErrorLevelEnumType
	maxMessageStatusCount: int
	minMessageStatusCount: int

@enum.unique
class CanIf_TTEventEnumType(enum.IntFlag):
	"""Event that causes a Timing/Error IRQ\n 
"""
	CANIF_TT_ERROR_LEVEL_CHANGED = 0
	CANIF_TT_INIT_WATCH_TRIGGER = 1
	CANIF_TT_NO_ERROR = 2
	CANIF_TT_SYNC_FAILED = 3
	CANIF_TT_TX_OVERFLOW = 4
	CANIF_TT_TX_UNDERFLOW = 5

@enum.unique
class CanIf_TTMasterSlaveModeType(enum.IntFlag):
	"""Master-Slave Mode\n 
"""
	CANIF_TT_BACKUP_MASTER = 0
	CANIF_TT_CURRENT_MASTER = 1
	CANIF_TT_MASTER_OFF = 2
	CANIF_TT_SLAVE = 3

class CanIf_TTMasterStateType:
	"""Master state type including sync mode, master-slave mode and current ref
	 trigger offset
	 
	"""
	"""CanIf_TTMasterStateType
	"""
	masterSlaveMode: vspyx.AUTOSAR.Classic.CanIf_TTMasterSlaveModeType
	refTriggerOffset: int
	syncMode: vspyx.AUTOSAR.Classic.CanIf_TTSyncModeEnumType

@enum.unique
class CanIf_TTSevereErrorEnumType(enum.IntFlag):
	"""Event that causes a severe error\n 
"""
	CANIF_TT_CONFIG_ERROR = 0
	CANIF_TT_WATCH_TRIGGER_REACHED = 1
	CANIF_TT_APPL_WATCHDOG = 2

@enum.unique
class CanIf_TTTimeSourceType(enum.IntFlag):
	"""Time source of time values in TTCAN\n 
"""
	CANIF_TT_CYCLE_TIME = 0
	CANIF_TT_GLOBAL_TIME = 1
	CANIF_TT_LOCAL_TIME = 2
	CANIF_TT_UNDEFINED = 3

class CanIf_TTTimingErrorIRQType:
	"""Combines all events that are reported by CanIf_TTTimingError (event indication
	 and error level)
	 
	"""
	"""CanIf_TTTimingErrorIRQType
	"""
	errorLevel: vspyx.AUTOSAR.Classic.CanIf_TTErrorLevelType
	event: vspyx.AUTOSAR.Classic.CanIf_TTEventEnumType

@enum.unique
class UdpNm_PduPositionType(enum.IntFlag):
	"""Used to define the position of the control bit vector within the NM PACKET.\n 
"""
	UDPNM_PDU_BYTE_0 = 0
	UDPNM_PDU_BYTE_1 = 1
	UDPNM_PDU_OFF = 255

class UdpNm_ConfigType:
	"""UdpNm_ConfigType
	"""
	dummy: int

class WEthTrcv_ConfigType:
	"""Implementation specific structure of the post build configuration
	 
	"""
	"""WEthTrcv_ConfigType
	"""
	dummy: int

@enum.unique
class WEthTrcv_GetChanRxParamIdType(enum.IntFlag):
	"""Wireless channel properties of the receive side \n 
"""
	WETHTRCV_GETCHRXPID_CBR = 0
	WETHTRCV_GETCHRXPID_CIT = 1

@enum.unique
class WEthTrcv_SetChanRxParamIdType(enum.IntFlag):
	"""Wireless channel settings for the receive side\n 
"""
	WETHTRCV_SETCHRXPID_BITRATE = 0
	WETHTRCV_SETCHRXPID_BANDWIDTH = 1
	WETHTRCV_SETCHRXPID_FREQ = 2
	WETHTRCV_SETCHRXPID_CSPWRTRESH = 3
	WETHTRCV_SETCHRXPID_RADIO_MODE = 4
	WETHTRCV_SETCHRXPID_ANTENNA = 5

@enum.unique
class WEthTrcv_SetChanTxParamIdType(enum.IntFlag):
	WETHTRCV_SETCHTXPID_BITRATE = 0
	WETHTRCV_SETCHTXPID_BANDWIDTH = 1
	WETHTRCV_SETCHTXPID_TXPOWER = 2
	WETHTRCV_SETCHTXPID_DCC_CBR = 3
	WETHTRCV_SETCHTXPID_TXQSEL = 4
	WETHTRCV_SETCHTXPID_TXQCFG_AIFSN = 5
	WETHTRCV_SETCHTXPID_TXQCFG_CWMIN = 6
	WETHTRCV_SETCHTXPID_TXQCFG_CWMAX = 7
	WETHTRCV_SETCHTXPID_TXQCFG_TXOP = 8
	WETHTRCV_SETCHTXPID_RADIO_MODE = 9
	WETHTRCV_SETCHTXPID_ANTENNA = 10
	WETHTRCV_SETCHTXPID_PACKET_INTERVAL = 12
	WETHTRCV_SETCHTXPID_DCC_STATE = 13

@enum.unique
class WEthTrcv_SetRadioParamIdType(enum.IntFlag):
	"""Wireless radio settings for the transceiver\n 
"""
	WETHTRCV_SETRADIOPID_SEL_TRCV_CHCFG = 1
	WETHTRCV_SETRADIOPID_SET_CHCFGID = 2
	WETHTRCV_SETRADIOPID_TOLLINGZONE_INFO = 3

@enum.unique
class WEth_BufWRxParamIdType(enum.IntFlag):
	"""Wireless radio parameters for a packet that has been received.\n 
"""
	WETH_BUFWRXPID_RSSI = 0
	WETH_BUFWRXPID_CHANNEL_ID = 1
	WETH_BUFWRXPID_FREQ = 2
	WETH_BUFWRXPID_TRANSACTION_ID_32 = 3
	WETH_BUFWRXPID_ANTENNA_ID = 4

@enum.unique
class WEth_BufWTxParamIdType(enum.IntFlag):
	"""Wireless radio parameters for a packet that has to be transmitted.\n 
"""
	WETH_BUFWTXPID_POWER = 0
	WETH_BUFWTXPID_CHANNEL_ID = 1
	WETH_BUFWTXPID_QUEUE_ID = 2
	WETH_BUFWTXPID_TRANSACTION_ID_16 = 3
	WETH_BUFWTXPID_ANTENNA_ID = 4

class WEth_ConfigType:
	"""Implementation specific structure of the post build configuration
	 
	"""
	"""WEth_ConfigType
	"""
	dummy: int

class Xcp_ConfigType:
	"""This is the type of the data structure containing the initialization data for
	 XCP.
	 
	"""
	"""Xcp_ConfigType
	"""
	dummy: int

@enum.unique
class Xcp_TransmissionModeType(enum.IntFlag):
	"""Handles the enabling and disabling of the transmission mode\n 
"""
	XCP_TX_OFF = 0
	XCP_TX_ON = 1

class BSW(vspyx.Core.Object):
	"""BSW
	"""
	def PreCompile(self, linkScope: vspyx.AUTOSAR.Classic.LinkScope) -> typing.Any: ...

	def Link(self, linkScope: vspyx.AUTOSAR.Classic.LinkScope) -> typing.Any: ...

	def PostBuild(self) -> typing.Any: ...

class CanIf(vspyx.AUTOSAR.Classic.BSW):
	"""CanIf
	"""

	@staticmethod
	def New(config: vspyx.AUTOSAR.Classic.ECUConfiguration) -> vspyx.AUTOSAR.Classic.CanIf: ...

class Can(vspyx.AUTOSAR.Classic.BSW):
	"""Can
	"""

	@staticmethod
	def New(config: vspyx.AUTOSAR.Classic.ECUConfiguration, globalInstanceId: int) -> vspyx.AUTOSAR.Classic.Can: ...

class CanTp(vspyx.AUTOSAR.Classic.BSW):
	"""CanTp
	"""

	@staticmethod
	def New(config: vspyx.AUTOSAR.Classic.ECUConfiguration) -> vspyx.AUTOSAR.Classic.CanTp: ...

class Cdd(vspyx.AUTOSAR.Classic.BSW):
	"""Cdd
	"""
	def Init(self) -> typing.Any: ...

	def MainFunction(self) -> typing.Any: ...

class Com(vspyx.AUTOSAR.Classic.BSW):
	"""Com
	"""
	@enum.unique
	class ReturnTypeValues(enum.IntFlag):
		SERVICE_NOT_AVAILABLE = 128
		BUSY = 129


	@staticmethod
	def New(config: vspyx.AUTOSAR.Classic.ECUConfiguration) -> vspyx.AUTOSAR.Classic.Com: ...

class Dcm(vspyx.AUTOSAR.Classic.BSW):
	"""Dcm
	"""

	@staticmethod
	def New(config: vspyx.AUTOSAR.Classic.ECUConfiguration) -> vspyx.AUTOSAR.Classic.Dcm: ...

class ECUConfiguration(vspyx.Core.ResolverObject):
	"""ECUConfiguration
	"""
	OnConfigurationMutation: vspyx.Core.Callback_634bd5c449

	@staticmethod
	@typing.overload
	def New() -> vspyx.AUTOSAR.Classic.ECUConfiguration: ...


	@staticmethod
	@typing.overload
	def New(config: typing.Any) -> vspyx.AUTOSAR.Classic.ECUConfiguration: ...

	def CloneConfiguration(self) -> typing.Any: ...

class ECUInstance(vspyx.Runtime.Component):
	"""ECUInstance
	"""
	ECUConfiguration: vspyx.AUTOSAR.Classic.ECUConfiguration
	LinkScope: vspyx.AUTOSAR.Classic.LinkScope

	@staticmethod
	def New(ecuConfig: vspyx.AUTOSAR.Classic.ECUConfiguration, linkScope: vspyx.AUTOSAR.Classic.LinkScope) -> vspyx.AUTOSAR.Classic.ECUInstance: ...

	def AddCddBSW(self, cdd: vspyx.AUTOSAR.Classic.Cdd) -> typing.Any: ...

	def Build(self) -> typing.Any: ...

	def SuppressConfigurationUpdates(self) -> typing.Any:
		"""This is called as a performance optimization when doing large
		updates to the configuration, such as when initially configuring
		the Stack.

		"""
		pass


	def UnsuppressConfigurationUpdates(self) -> typing.Any:
		"""Allow all suppressed confuiguration updates to take place.

		See SuppressConfigurationUpdates() for more information.

		"""
		pass


class EthIf(vspyx.AUTOSAR.Classic.BSW):
	"""EthIf
	"""

	@staticmethod
	def New(config: vspyx.AUTOSAR.Classic.ECUConfiguration) -> vspyx.AUTOSAR.Classic.EthIf: ...

class Eth(vspyx.AUTOSAR.Classic.BSW):
	"""Eth
	"""

	@staticmethod
	def New(config: vspyx.AUTOSAR.Classic.ECUConfiguration, globalInstanceId: int) -> vspyx.AUTOSAR.Classic.Eth: ...

class FrIf(vspyx.AUTOSAR.Classic.BSW):
	"""FrIf
	"""

	@staticmethod
	def New(config: vspyx.AUTOSAR.Classic.ECUConfiguration) -> vspyx.AUTOSAR.Classic.FrIf: ...

class Fr(vspyx.AUTOSAR.Classic.BSW):
	"""Fr
	"""

	@staticmethod
	def New(config: vspyx.AUTOSAR.Classic.ECUConfiguration, globalInstanceId: int) -> vspyx.AUTOSAR.Classic.Fr: ...

class IpduM(vspyx.AUTOSAR.Classic.BSW):
	"""IpduM
	"""

	@staticmethod
	def New(config: vspyx.AUTOSAR.Classic.ECUConfiguration) -> vspyx.AUTOSAR.Classic.IpduM: ...

class LinkScopeBase:
	"""LinkScopeBase
	"""

class LinkScope(vspyx.Core.Object):
	"""LinkScope
	"""
	CanIf: vspyx.AUTOSAR.Classic.LinkScopeBase
	CanNm: vspyx.AUTOSAR.Classic.LinkScopeBase
	CanTSyn: vspyx.AUTOSAR.Classic.LinkScopeBase
	CanTp: vspyx.AUTOSAR.Classic.LinkScopeBase
	Com: vspyx.AUTOSAR.Classic.LinkScopeBase
	Dcm: vspyx.AUTOSAR.Classic.LinkScopeBase
	Det: vspyx.AUTOSAR.Classic.LinkScopeBase
	DoIP: vspyx.AUTOSAR.Classic.LinkScopeBase
	EthIf: vspyx.AUTOSAR.Classic.LinkScopeBase
	EthSM: vspyx.AUTOSAR.Classic.LinkScopeBase
	FrArTp: vspyx.AUTOSAR.Classic.LinkScopeBase
	FrIf: vspyx.AUTOSAR.Classic.LinkScopeBase
	FrNm: vspyx.AUTOSAR.Classic.LinkScopeBase
	FrTSyn: vspyx.AUTOSAR.Classic.LinkScopeBase
	FrTp: vspyx.AUTOSAR.Classic.LinkScopeBase
	IpduM: vspyx.AUTOSAR.Classic.LinkScopeBase
	J1939Nm: vspyx.AUTOSAR.Classic.LinkScopeBase
	J1939Tp: vspyx.AUTOSAR.Classic.LinkScopeBase
	LinIf: vspyx.AUTOSAR.Classic.LinkScopeBase
	Os: vspyx.AUTOSAR.Classic.LinkScopeBase
	PduR: vspyx.AUTOSAR.Classic.LinkScopeBase
	Sd: vspyx.AUTOSAR.Classic.LinkScopeBase
	SoAd: vspyx.AUTOSAR.Classic.LinkScopeBase
	TcpIp: vspyx.AUTOSAR.Classic.LinkScopeBase
	UdpNm: vspyx.AUTOSAR.Classic.LinkScopeBase
	Xcp: vspyx.AUTOSAR.Classic.LinkScopeBase

	@staticmethod
	def New() -> vspyx.AUTOSAR.Classic.LinkScope: ...

	def TranslatePduId(self, destMip: str, globalPduRef: str) -> int: ...

	def RegisterPduId(self, localModuleMip: str, globalPduRef: str, localPduId: int) -> typing.Any: ...

	def CanInstance(self, id: int) -> vspyx.AUTOSAR.Classic.LinkScopeBase: ...

	def CanTrcvInstance(self, id: int) -> vspyx.AUTOSAR.Classic.LinkScopeBase: ...

	def GetCdd(self, id: int) -> vspyx.AUTOSAR.Classic.LinkScopeBase: ...

	def EthInstance(self, id: int) -> vspyx.AUTOSAR.Classic.LinkScopeBase: ...

	def EthSwtInstance(self, id: int) -> vspyx.AUTOSAR.Classic.LinkScopeBase: ...

	def EthTrcvInstance(self, id: int) -> vspyx.AUTOSAR.Classic.LinkScopeBase: ...

	def FrInstance(self, id: int) -> vspyx.AUTOSAR.Classic.LinkScopeBase: ...

	def FrTrcvInstance(self, id: int) -> vspyx.AUTOSAR.Classic.LinkScopeBase: ...

	def WEthInstance(self, id: int) -> vspyx.AUTOSAR.Classic.LinkScopeBase: ...

	def WEthTrcvInstance(self, id: int) -> vspyx.AUTOSAR.Classic.LinkScopeBase: ...

class CanIfLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""CanIfLinkScope
	"""
	ICS_AddRxPDU: vspyx.Core.Function_2fcce4c88f
	CheckTrcvWakeFlag: vspyx.Core.Function_d0db731c4e
	CheckTrcvWakeFlagIndication: vspyx.Core.Function_21ee470862
	CheckValidation: vspyx.Core.Function_552be9d574
	CheckWakeup: vspyx.Core.Function_552be9d574
	ClearTrcvWufFlag: vspyx.Core.Function_d0db731c4e
	ClearTrcvWufFlagIndication: vspyx.Core.Function_21ee470862
	ConfirmPnAvailability: vspyx.Core.Function_21ee470862
	ControllerBusOff: vspyx.Core.Function_21ee470862
	ControllerModeIndication: vspyx.Core.Function_10bc070061
	CurrentIcomConfiguration: vspyx.Core.Function_586a3394fa
	DeInit: vspyx.Core.Function_634bd5c449
	EnableBusMirroring: vspyx.Core.Function_74c6dc153a
	GetControllerErrorState: vspyx.Core.Function_e8dff68767
	GetControllerMode: vspyx.Core.Function_443b48a11c
	GetControllerRxErrorCounter: vspyx.Core.Function_2e41615af1
	GetControllerTxErrorCounter: vspyx.Core.Function_2e41615af1
	GetPduMode: vspyx.Core.Function_bea2002a9b
	GetTrcvMode: vspyx.Core.Function_0cc2484f95
	GetTrcvWakeupReason: vspyx.Core.Function_f01d4e266d
	GetTxConfirmationState: vspyx.Core.Function_91fc0f5c94
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_4ba5461526
	ReadRxNotifStatus: vspyx.Core.Function_20254a1b48
	ReadRxPduData: vspyx.Core.Function_89e6f567fe
	ReadTxNotifStatus: vspyx.Core.Function_20254a1b48
	RxIndication: vspyx.Core.Function_5c3674cd52
	SetBaudrate: vspyx.Core.Function_6caebc02a3
	SetControllerMode: vspyx.Core.Function_294209b1f8
	SetDynamicTxId: vspyx.Core.Function_0afff0c755
	SetIcomConfiguration: vspyx.Core.Function_74c6dc153a
	SetPduMode: vspyx.Core.Function_e6ef80b9ed
	SetTrcvMode: vspyx.Core.Function_f4ba7e61b0
	SetTrcvWakeupMode: vspyx.Core.Function_831ea2a383
	TTAckTimeMark: vspyx.Core.Function_d0db731c4e
	TTApplWatchdogError: vspyx.Core.Function_d0db731c4e
	TTCancelTimeMark: vspyx.Core.Function_d0db731c4e
	TTDisableTimeMarkIRQ: vspyx.Core.Function_d0db731c4e
	TTEnableTimeMarkIRQ: vspyx.Core.Function_d0db731c4e
	TTGap: vspyx.Core.Function_d0db731c4e
	TTGetControllerTime: vspyx.Core.Function_e0ebc0d4a5
	TTGetErrorLevel: vspyx.Core.Function_2fc36e6a70
	TTGetMasterState: vspyx.Core.Function_f0a3d49219
	TTGetNTUActual: vspyx.Core.Function_a522ba122e
	TTGetSyncQuality: vspyx.Core.Function_7ef33674ac
	TTGetTimeMarkIRQStatus: vspyx.Core.Function_2e41615af1
	TTGlobalTimePreset: vspyx.Core.Function_6caebc02a3
	TTJobListExec_Controller: vspyx.Core.Function_634bd5c449
	TTMasterStateChange: vspyx.Core.Function_a735ec45d0
	TTSetEndOfGap: vspyx.Core.Function_d0db731c4e
	TTSetExtClockSyncCommand: vspyx.Core.Function_d0db731c4e
	TTSetNTUAdjust: vspyx.Core.Function_a522ba122e
	TTSetNextIsGap: vspyx.Core.Function_d0db731c4e
	TTSetTimeCommand: vspyx.Core.Function_d0db731c4e
	TTSetTimeMark: vspyx.Core.Function_7e32c6cad0
	TTSevereError: vspyx.Core.Function_efb8873f58
	TTStartOfCycle: vspyx.Core.Function_74c6dc153a
	TTTimeDisc: vspyx.Core.Function_d0db731c4e
	TTTimingError: vspyx.Core.Function_ee5fe9fd44
	Transmit: vspyx.Core.Function_fcd25d59dc
	TrcvModeIndication: vspyx.Core.Function_12956d7520
	TriggerTransmit: vspyx.Core.Function_89e6f567fe
	TxConfirmation: vspyx.Core.Function_a2f38cfeb7

class CanLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""CanLinkScope
	"""
	CheckWakeup: vspyx.Core.Function_d0db731c4e
	DeInit: vspyx.Core.Function_634bd5c449
	DisableControllerInterrupts: vspyx.Core.Function_21ee470862
	EnableControllerInterrupts: vspyx.Core.Function_21ee470862
	GetControllerErrorState: vspyx.Core.Function_e8dff68767
	GetControllerMode: vspyx.Core.Function_443b48a11c
	GetControllerRxErrorCounter: vspyx.Core.Function_2e41615af1
	GetControllerTxErrorCounter: vspyx.Core.Function_2e41615af1
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_a78ba2365f
	MainFunction_BusOff: vspyx.Core.Function_634bd5c449
	MainFunction_Mode: vspyx.Core.Function_634bd5c449
	MainFunction_Read: vspyx.Core.Function_634bd5c449
	MainFunction_Wakeup: vspyx.Core.Function_634bd5c449
	MainFunction_Write: vspyx.Core.Function_634bd5c449
	SetBaudrate: vspyx.Core.Function_6caebc02a3
	SetControllerMode: vspyx.Core.Function_294209b1f8
	SetIcomConfiguration: vspyx.Core.Function_74c6dc153a
	TTAckTimeMark: vspyx.Core.Function_21ee470862
	TTCancelTimeMark: vspyx.Core.Function_21ee470862
	TTDisableTimeMarkIRQ: vspyx.Core.Function_21ee470862
	TTEnableTimeMarkIRQ: vspyx.Core.Function_21ee470862
	TTGetControllerTime: vspyx.Core.Function_0e95d1883d
	TTGetErrorLevel: vspyx.Core.Function_8526fd95a8
	TTGetMasterState: vspyx.Core.Function_84beac48eb
	TTGetNTUActual: vspyx.Core.Function_499d4012b8
	TTGetSyncQuality: vspyx.Core.Function_1326e953df
	TTGetTimeMarkIRQStatus: vspyx.Core.Function_30fd0fc629
	TTGlobalTimePreset: vspyx.Core.Function_85f4178355
	TTMainFunction_IRQ: vspyx.Core.Function_634bd5c449
	TTReceive: vspyx.Core.Function_083cdbeb6f
	TTSetEndOfGap: vspyx.Core.Function_21ee470862
	TTSetExtClockSyncCommand: vspyx.Core.Function_21ee470862
	TTSetNTUAdjust: vspyx.Core.Function_85f4178355
	TTSetNextIsGap: vspyx.Core.Function_21ee470862
	TTSetTimeCommand: vspyx.Core.Function_21ee470862
	TTSetTimeMark: vspyx.Core.Function_1ad0431e9e
	Write: vspyx.Core.Function_39882bfe86
	ICS_Attach: vspyx.Core.Function_771946cc9c
	ICS_Detach: vspyx.Core.Function_21ee470862

class CanNmLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""CanNmLinkScope
	"""
	CheckRemoteSleepIndication: vspyx.Core.Function_2e41615af1
	ConfirmPnAvailability: vspyx.Core.Function_21ee470862
	DeInit: vspyx.Core.Function_634bd5c449
	DisableCommunication: vspyx.Core.Function_d0db731c4e
	EnableCommunication: vspyx.Core.Function_d0db731c4e
	GetLocalNodeIdentifier: vspyx.Core.Function_2e41615af1
	GetNodeIdentifier: vspyx.Core.Function_2e41615af1
	GetPduData: vspyx.Core.Function_2e41615af1
	GetState: vspyx.Core.Function_40acffab2d
	GetUserData: vspyx.Core.Function_2e41615af1
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_11044c1996
	MainFunction: vspyx.Core.Function_634bd5c449
	NetworkRelease: vspyx.Core.Function_d0db731c4e
	NetworkRequest: vspyx.Core.Function_d0db731c4e
	PassiveStartUp: vspyx.Core.Function_d0db731c4e
	RepeatMessageRequest: vspyx.Core.Function_d0db731c4e
	RequestBusSynchronization: vspyx.Core.Function_d0db731c4e
	RxIndication: vspyx.Core.Function_a282387e18
	SetSleepReadyBit: vspyx.Core.Function_74c6dc153a
	SetUserData: vspyx.Core.Function_2fe29a5add
	Transmit: vspyx.Core.Function_fcd25d59dc
	TriggerTransmit: vspyx.Core.Function_89e6f567fe
	TxConfirmation: vspyx.Core.Function_378634c28f

class CanSMLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""CanSMLinkScope
	"""
	CheckTransceiverWakeFlagIndication: vspyx.Core.Function_21ee470862
	ClearTrcvWufFlagIndication: vspyx.Core.Function_21ee470862
	ConfirmPnAvailability: vspyx.Core.Function_21ee470862
	ControllerBusOff: vspyx.Core.Function_21ee470862
	ControllerModeIndication: vspyx.Core.Function_10bc070061
	CurrentIcomConfiguration: vspyx.Core.Function_586a3394fa
	DeInit: vspyx.Core.Function_634bd5c449
	GetCurrentComMode: vspyx.Core.Function_2e41615af1
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_81dd4d70de
	MainFunction: vspyx.Core.Function_634bd5c449
	RequestComMode: vspyx.Core.Function_74c6dc153a
	SetBaudrate: vspyx.Core.Function_6caebc02a3
	SetEcuPassive: vspyx.Core.Function_d0db731c4e
	SetIcomConfiguration: vspyx.Core.Function_74c6dc153a
	StartWakeupSource: vspyx.Core.Function_d0db731c4e
	StopWakeupSource: vspyx.Core.Function_d0db731c4e
	TransceiverModeIndication: vspyx.Core.Function_12956d7520
	TxTimeoutException: vspyx.Core.Function_21ee470862

class CanTSynLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""CanTSynLinkScope
	"""
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_59cec8a590
	MainFunction: vspyx.Core.Function_634bd5c449
	RxIndication: vspyx.Core.Function_a282387e18
	SetTransmissionMode: vspyx.Core.Function_4d9e6b70f6
	TxConfirmation: vspyx.Core.Function_378634c28f

class CanTpLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""CanTpLinkScope
	"""
	CancelReceive: vspyx.Core.Function_8c52b04f91
	CancelTransmit: vspyx.Core.Function_8c52b04f91
	ChangeParameter: vspyx.Core.Function_48f464a8f8
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_c51e8aa74c
	MainFunction: vspyx.Core.Function_634bd5c449
	ReadParameter: vspyx.Core.Function_47315e6f3b
	RxIndication: vspyx.Core.Function_a282387e18
	Shutdown: vspyx.Core.Function_634bd5c449
	Transmit: vspyx.Core.Function_fcd25d59dc
	TxConfirmation: vspyx.Core.Function_378634c28f

class CanTrcvLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""CanTrcvLinkScope
	"""
	CheckWakeFlag: vspyx.Core.Function_d0db731c4e
	CheckWakeup: vspyx.Core.Function_d0db731c4e
	ClearTrcvTimeoutFlag: vspyx.Core.Function_d0db731c4e
	ClearTrcvWufFlag: vspyx.Core.Function_d0db731c4e
	DeInit: vspyx.Core.Function_634bd5c449
	GetBusWuReason: vspyx.Core.Function_f01d4e266d
	GetOpMode: vspyx.Core.Function_0cc2484f95
	GetTrcvSystemData: vspyx.Core.Function_e3d7f2cf1e
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_e09fbce949
	MainFunction: vspyx.Core.Function_634bd5c449
	MainFunctionDiagnostics: vspyx.Core.Function_634bd5c449
	ReadTrcvSilenceFlag: vspyx.Core.Function_15a303acbd
	ReadTrcvTimeoutFlag: vspyx.Core.Function_15a303acbd
	SetOpMode: vspyx.Core.Function_f4ba7e61b0
	SetPNActivationState: vspyx.Core.Function_c6031c9092
	SetWakeupMode: vspyx.Core.Function_831ea2a383

class CddLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""CddLinkScope
	"""
	Init: vspyx.Core.Function_634bd5c449
	MainFunction: vspyx.Core.Function_634bd5c449
	def AddFunction(self, name: str, func: typing.Callable) -> typing.Any: ...

	def FindFunction(self, name: str) -> typing.Callable: ...

class ComLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""ComLinkScope
	"""
	CbkTxAck: vspyx.Core.Lookup_622daa8c11
	CbkTxErr: vspyx.Core.Lookup_622daa8c11
	CbkTxTOut: vspyx.Core.Lookup_622daa8c11
	CbkRxAck: vspyx.Core.Lookup_622daa8c11
	CbkRxTOut: vspyx.Core.Lookup_622daa8c11
	CbkInv: vspyx.Core.Lookup_622daa8c11
	CbkCounterErr: vspyx.Core.Lookup_e0009b14f2
	RxIpduCallout: vspyx.Core.Lookup_9bb5f9e691
	TxIpduCallout: vspyx.Core.Lookup_6c1beffc05
	CopyRxData: vspyx.Core.Function_a2f569d6de
	CopyTxData: vspyx.Core.Function_a83011c4da
	DeInit: vspyx.Core.Function_634bd5c449
	DisableReceptionDM: vspyx.Core.Function_a2f38cfeb7
	EnableReceptionDM: vspyx.Core.Function_a2f38cfeb7
	GetStatus: vspyx.Core.Function_758f77b121
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_10e1b11211
	InvalidateSignal: vspyx.Core.Function_8c52b04f91
	InvalidateSignalGroup: vspyx.Core.Function_8c52b04f91
	IpduGroupStart: vspyx.Core.Function_378634c28f
	IpduGroupStop: vspyx.Core.Function_a2f38cfeb7
	MainFunctionRouteSignals: vspyx.Core.Function_634bd5c449
	MainFunctionRx: vspyx.Core.Function_634bd5c449
	MainFunctionTx: vspyx.Core.Function_634bd5c449
	ReceiveDynSignal: vspyx.Core.Function_38755bef3b
	ReceiveSignal: vspyx.Core.Function_e0985dbb3b
	ReceiveSignalGroup: vspyx.Core.Function_8c52b04f91
	ReceiveSignalGroupArray: vspyx.Core.Function_066aa755c1
	RxIndication: vspyx.Core.Function_a282387e18
	SendDynSignal: vspyx.Core.Function_027b68d5f9
	SendSignal: vspyx.Core.Function_633b86a6df
	SendSignalGroup: vspyx.Core.Function_8c52b04f91
	SendSignalGroupArray: vspyx.Core.Function_75e7d1a8d9
	StartOfReception: vspyx.Core.Function_dc27da2c70
	SwitchIpduTxMode: vspyx.Core.Function_378634c28f
	TpRxIndication: vspyx.Core.Function_378634c28f
	TpTxConfirmation: vspyx.Core.Function_378634c28f
	TriggerIPDUSend: vspyx.Core.Function_8c52b04f91
	TriggerIPDUSendWithMetaData: vspyx.Core.Function_75e7d1a8d9
	TriggerTransmit: vspyx.Core.Function_89e6f567fe
	TxConfirmation: vspyx.Core.Function_378634c28f

class DcmLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""DcmLinkScope
	"""
	ComM_FullComModeEntered: vspyx.Core.Function_21ee470862
	ComM_NoComModeEntered: vspyx.Core.Function_21ee470862
	ComM_SilentComModeEntered: vspyx.Core.Function_21ee470862
	CopyRxData: vspyx.Core.Function_a2f569d6de
	CopyTxData: vspyx.Core.Function_a83011c4da
	DemTriggerOnDTCStatus: vspyx.Core.Function_f60db37ead
	GetActiveProtocol: vspyx.Core.Function_75d82c1883
	GetSecurityLevel: vspyx.Core.Function_540fc56e59
	GetSesCtrlType: vspyx.Core.Function_540fc56e59
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	GetVin: vspyx.Core.Function_540fc56e59
	Init: vspyx.Core.Function_ccd6000015
	MainFunction: vspyx.Core.Function_634bd5c449
	ResetToDefaultSession: vspyx.Core.Function_b9ef01da62
	SetActiveDiagnostic: vspyx.Core.Function_d0db731c4e
	SetDeauthenticatedRole: vspyx.Core.Function_066aa755c1
	StartOfReception: vspyx.Core.Function_dc27da2c70
	TpRxIndication: vspyx.Core.Function_378634c28f
	TpTxConfirmation: vspyx.Core.Function_378634c28f
	TriggerOnEvent: vspyx.Core.Function_d0db731c4e
	TxConfirmation: vspyx.Core.Function_378634c28f
	WriteFile: vspyx.Core.Function_5ff2fce1b8

class DemLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""DemLinkScope
	"""
	DcmGetInfoTypeValue08: vspyx.Core.Function_7ef33674ac
	DcmGetInfoTypeValue0B: vspyx.Core.Function_7ef33674ac
	DcmReadDataOfPID01: vspyx.Core.Function_540fc56e59
	DcmReadDataOfPID1C: vspyx.Core.Function_540fc56e59
	DcmReadDataOfPID21: vspyx.Core.Function_540fc56e59
	DcmReadDataOfPID30: vspyx.Core.Function_540fc56e59
	DcmReadDataOfPID31: vspyx.Core.Function_540fc56e59
	DcmReadDataOfPID41: vspyx.Core.Function_540fc56e59
	DcmReadDataOfPID4D: vspyx.Core.Function_540fc56e59
	DcmReadDataOfPID4E: vspyx.Core.Function_540fc56e59
	ClearDTC: vspyx.Core.Function_d0db731c4e
	ClearPrestoredFreezeFrame: vspyx.Core.Function_8c52b04f91
	DcmGetAvailableOBDMIDs: vspyx.Core.Function_956da5beda
	DcmGetDTCOfOBDFreezeFrame: vspyx.Core.Function_59b217fc4f
	DcmGetDTRData: vspyx.Core.Function_3f17f2e42c
	DcmGetNumTIDsOfOBDMID: vspyx.Core.Function_2e41615af1
	DcmReadDataOfOBDFreezeFrame: vspyx.Core.Function_f150285919
	DcmReadDataOfPID91: vspyx.Core.Function_540fc56e59
	DisableDTCRecordUpdate: vspyx.Core.Function_d0db731c4e
	DisableDTCSetting: vspyx.Core.Function_d0db731c4e
	EnableDTCRecordUpdate: vspyx.Core.Function_d0db731c4e
	EnableDTCSetting: vspyx.Core.Function_d0db731c4e
	GetB1Counter: vspyx.Core.Function_abe556ad31
	GetComponentFailed: vspyx.Core.Function_066aa755c1
	GetCycleQualified: vspyx.Core.Function_2e41615af1
	GetDTCByOccurrenceTime: vspyx.Core.Function_3ea86411fb
	GetDTCOfEvent: vspyx.Core.Function_386e219faf
	GetDTCSelectionResult: vspyx.Core.Function_d0db731c4e
	GetDTCSelectionResultForClearDTC: vspyx.Core.Function_d0db731c4e
	GetDTCSeverityAvailabilityMask: vspyx.Core.Function_2e41615af1
	GetDTCStatusAvailabilityMask: vspyx.Core.Function_2e41615af1
	GetDTCSuppression: vspyx.Core.Function_2e41615af1
	GetDataOfPID21: vspyx.Core.Function_540fc56e59
	GetDebouncingOfEvent: vspyx.Core.Function_066aa755c1
	GetEventExtendedDataRecordEx: vspyx.Core.Function_e2084bd7cc
	GetEventFreezeFrameDataEx: vspyx.Core.Function_f78886869e
	GetEventMemoryOverflow: vspyx.Core.Function_179c138892
	GetEventUdsStatus: vspyx.Core.Function_066aa755c1
	GetFaultDetectionCounter: vspyx.Core.Function_5e8065b6aa
	GetFunctionalUnitOfDTC: vspyx.Core.Function_2e41615af1
	GetIUMPRDenCondition: vspyx.Core.Function_2e41615af1
	GetIndicatorStatus: vspyx.Core.Function_2e41615af1
	GetMonitorStatus: vspyx.Core.Function_066aa755c1
	GetNextExtendedDataRecord: vspyx.Core.Function_cfab67cc2b
	GetNextFilteredDTC: vspyx.Core.Function_dc14980427
	GetNextFilteredDTCAndFDC: vspyx.Core.Function_2aff41fc00
	GetNextFilteredDTCAndSeverity: vspyx.Core.Function_4fc7072672
	GetNextFilteredRecord: vspyx.Core.Function_dc14980427
	GetNextFreezeFrameData: vspyx.Core.Function_cfab67cc2b
	GetNumberOfEventMemoryEntries: vspyx.Core.Function_179c138892
	GetNumberOfFilteredDTC: vspyx.Core.Function_c54e42977a
	GetNumberOfFreezeFrameRecords: vspyx.Core.Function_c54e42977a
	GetSeverityOfDTC: vspyx.Core.Function_2e41615af1
	GetSizeOfExtendedDataRecordSelection: vspyx.Core.Function_c54e42977a
	GetSizeOfFreezeFrameSelection: vspyx.Core.Function_c54e42977a
	GetStatusOfDTC: vspyx.Core.Function_2e41615af1
	GetTranslationType: vspyx.Core.Function_d0db731c4e
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_acd36324cb
	J1939DcmClearDTC: vspyx.Core.Function_dcc7dd41b3
	J1939DcmFirstDTCwithLampStatus: vspyx.Core.Function_21ee470862
	J1939DcmGetNextDTCwithLampStatus: vspyx.Core.Function_949d6a104b
	J1939DcmGetNextFilteredDTC: vspyx.Core.Function_d50dea3f3c
	J1939DcmGetNextFilteredRatio: vspyx.Core.Function_65dea8c9f5
	J1939DcmGetNextFreezeFrame: vspyx.Core.Function_f187d676b3
	J1939DcmGetNextSPNInFreezeFrame: vspyx.Core.Function_d50dea3f3c
	J1939DcmGetNumberOfFilteredDTC: vspyx.Core.Function_4825dedaf6
	J1939DcmReadDiagnosticReadiness1: vspyx.Core.Function_a750953b55
	J1939DcmReadDiagnosticReadiness2: vspyx.Core.Function_7a8a71bee3
	J1939DcmReadDiagnosticReadiness3: vspyx.Core.Function_fbec0d0c9e
	J1939DcmSetDTCFilter: vspyx.Core.Function_24a36f8002
	J1939DcmSetFreezeFrameFilter: vspyx.Core.Function_74c6dc153a
	J1939DcmSetRatioFilter: vspyx.Core.Function_ab1f70354c
	MainFunction: vspyx.Core.Function_634bd5c449
	PreInit: vspyx.Core.Function_634bd5c449
	PrestoreFreezeFrame: vspyx.Core.Function_8c52b04f91
	ReadDataOfPID01: vspyx.Core.Function_540fc56e59
	RepIUMPRDenRelease: vspyx.Core.Function_d0db731c4e
	RepIUMPRFaultDetect: vspyx.Core.Function_d0db731c4e
	ResetEventDebounceStatus: vspyx.Core.Function_0617fd6a29
	ResetEventStatus: vspyx.Core.Function_8c52b04f91
	RestartOperationCycle: vspyx.Core.Function_d0db731c4e
	SelectDTC: vspyx.Core.Function_35fc46fa99
	SelectExtendedDataRecord: vspyx.Core.Function_74c6dc153a
	SelectFreezeFrameData: vspyx.Core.Function_74c6dc153a
	SetComponentAvailable: vspyx.Core.Function_0617fd6a29
	SetCycleQualified: vspyx.Core.Function_d0db731c4e
	SetDTCFilter: vspyx.Core.Function_f4553c1908
	SetDTCSuppression: vspyx.Core.Function_74c6dc153a
	SetDTR: vspyx.Core.Function_f5499abc0a
	SetDataOfPID21: vspyx.Core.Function_1e2a0f96a2
	SetDataOfPID31: vspyx.Core.Function_1e2a0f96a2
	SetDataOfPID4D: vspyx.Core.Function_1e2a0f96a2
	SetDataOfPID4E: vspyx.Core.Function_1e2a0f96a2
	SetEnableCondition: vspyx.Core.Function_74c6dc153a
	SetEventAvailable: vspyx.Core.Function_0617fd6a29
	SetEventDisabled: vspyx.Core.Function_8c52b04f91
	SetEventFailureCycleCounterThreshold: vspyx.Core.Function_0617fd6a29
	SetEventStatus: vspyx.Core.Function_0617fd6a29
	SetEventStatusWithMonitorData: vspyx.Core.Function_8ba851a999
	SetFreezeFrameRecordFilter: vspyx.Core.Function_74c6dc153a
	SetIUMPRDenCondition: vspyx.Core.Function_74c6dc153a
	SetPtoStatus: vspyx.Core.Function_d0db731c4e
	SetStorageCondition: vspyx.Core.Function_74c6dc153a
	SetWIRStatus: vspyx.Core.Function_0617fd6a29
	Shutdown: vspyx.Core.Function_634bd5c449

class DetLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""DetLinkScope
	"""
	DetErrorHooks: vspyx.Core.Lookup_8a676d31c9
	DetReportRuntimeErrorCallouts: vspyx.Core.Lookup_8a676d31c9
	DetReportTransientFaultCallouts: vspyx.Core.Lookup_8a676d31c9
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_d94d5eba3e
	ReportError: vspyx.Core.Function_d58ad274de
	ReportRuntimeError: vspyx.Core.Function_d58ad274de
	ReportTransientFault: vspyx.Core.Function_d58ad274de
	Start: vspyx.Core.Function_634bd5c449

class DoIPLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""DoIPLinkScope
	"""
	ActivationLineSwitchActive: vspyx.Core.Function_634bd5c449
	ActivationLineSwitchInactive: vspyx.Core.Function_634bd5c449
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	IfCancelTransmit: vspyx.Core.Function_8c52b04f91
	IfTransmit: vspyx.Core.Function_fcd25d59dc
	Init: vspyx.Core.Function_47e9524cbc
	LocalIpAddrAssignmentChg: vspyx.Core.Function_343ba6cd45
	MainFunction: vspyx.Core.Function_634bd5c449
	SoAdIfTriggerTransmit: vspyx.Core.Function_89e6f567fe
	SoAdTpTriggerTransmit: vspyx.Core.Function_89e6f567fe
	SoAdIfRxIndication: vspyx.Core.Function_a282387e18
	SoAdIfTxConfirmation: vspyx.Core.Function_378634c28f
	SoAdTpCopyRxData: vspyx.Core.Function_a2f569d6de
	SoAdTpCopyTxData: vspyx.Core.Function_a83011c4da
	SoAdTpRxIndication: vspyx.Core.Function_378634c28f
	SoAdTpStartOfReception: vspyx.Core.Function_dc27da2c70
	SoAdTpTxConfirmation: vspyx.Core.Function_378634c28f
	SoConModeChg: vspyx.Core.Function_bc9980100d
	TpCancelReceive: vspyx.Core.Function_8c52b04f91
	TpCancelTransmit: vspyx.Core.Function_8c52b04f91
	TpTransmit: vspyx.Core.Function_fcd25d59dc

class EthIfLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""EthIfLinkScope
	"""
	User_RxIndication: vspyx.Core.Lookup_82c6226f53
	UL_TxConfirmation: vspyx.Core.Lookup_2113e3f1f0
	User_TrcvLinkStateChg: vspyx.Core.Lookup_fd2ad145df
	CheckWakeup: vspyx.Core.Function_552be9d574
	ClearSwitchPortSignalQuality: vspyx.Core.Function_74c6dc153a
	ClearTrcvSignalQuality: vspyx.Core.Function_d0db731c4e
	CtrlModeIndication: vspyx.Core.Function_1a36878ae0
	EnableEgressTimeStamp: vspyx.Core.Function_8cfc086487
	GetAndResetMeasurementData: vspyx.Core.Function_3ea86411fb
	GetArlTable: vspyx.Core.Function_7ecdad779f
	GetBufWRxParams: vspyx.Core.Function_0b0ec2a15c
	GetBufWTxParams: vspyx.Core.Function_71e3c17e3a
	GetCableDiagnosticsResult: vspyx.Core.Function_91201e25ee
	GetChanRxParams: vspyx.Core.Function_fae60a0b05
	GetControllerMode: vspyx.Core.Function_6004950ab0
	GetCtrlIdxList: vspyx.Core.Function_ed55d9b8a8
	GetCurrentTime_: vspyx.Core.Function_c2ae3ddfab
	GetEgressTimeStamp: vspyx.Core.Function_538ae0a476
	GetIngressTimeStamp: vspyx.Core.Function_9305a4b9b6
	GetPhyIdentifier: vspyx.Core.Function_1aa392315c
	GetPhysAddr: vspyx.Core.Function_30fd0fc629
	GetPortMacAddr: vspyx.Core.Function_e6a04685ef
	GetRxMgmtObject: typing.Any
	GetSwitchPortSignalQuality: vspyx.Core.Function_ff2e1d1587
	GetTransceiverWakeupMode: vspyx.Core.Function_ba6fb8bb78
	GetTrcvSignalQuality: vspyx.Core.Function_4089a2ae1e
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	GetVlanId: vspyx.Core.Function_c54e42977a
	Init: vspyx.Core.Function_c8d07bd634
	MainFunctionRx: vspyx.Core.Function_634bd5c449
	MainFunctionRx_PriorityProcessing: vspyx.Core.Function_9808ef8308
	MainFunctionState: vspyx.Core.Function_634bd5c449
	MainFunctionTx: vspyx.Core.Function_634bd5c449
	ResetConfiguration: vspyx.Core.Function_d0db731c4e
	RxIndication: vspyx.Core.Function_5b41fb63e2
	SetBufWTxParams: vspyx.Core.Function_4cb130ce40
	SetChanRxParams: vspyx.Core.Function_7dd09b80f1
	SetChanTxParams: vspyx.Core.Function_994f9cbf3e
	SetControllerMode: vspyx.Core.Function_4e191dc5cd
	SetForwardingMode: vspyx.Core.Function_74c6dc153a
	SetPhyLoopbackMode: vspyx.Core.Function_1f410d00a7
	SetPhyTestMode: vspyx.Core.Function_39d1672c39
	SetPhyTxMode: vspyx.Core.Function_0c03f162c7
	SetPhysAddr: vspyx.Core.Function_65ccff1720
	SetRadioParams: vspyx.Core.Function_470e3fff9f
	SetSwitchMgmtInfo: vspyx.Core.Function_f4a6e16e5c
	SetTransceiverWakeupMode: vspyx.Core.Function_fe5fe2d616
	StartAllPorts: vspyx.Core.Function_b9ef01da62
	StoreConfiguration: vspyx.Core.Function_d0db731c4e
	SwitchEnableTimeStamping: vspyx.Core.Function_f4a6e16e5c
	SwitchPortGroupRequestMode: vspyx.Core.Function_c1e6fc091c
	SwitchPortModeIndication: vspyx.Core.Function_2e3c3eb1c6
	Transmit: vspyx.Core.Function_49674ba094
	TrcvModeIndication: vspyx.Core.Function_8b98477959
	TxConfirmation: vspyx.Core.Function_5a831c5725
	UpdatePhysAddrFilter: vspyx.Core.Function_820aa6589e
	VerifyConfig: vspyx.Core.Function_2e41615af1

class EthLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""EthLinkScope
	"""
	EnableEgressTimeStamp: vspyx.Core.Function_8cfc086487
	GetControllerMode: vspyx.Core.Function_6004950ab0
	GetCounterValues: vspyx.Core.Function_4e6bcdc84c
	GetCurrentTime_: vspyx.Core.Function_c2ae3ddfab
	GetEgressTimeStamp: vspyx.Core.Function_538ae0a476
	GetIngressTimeStamp: vspyx.Core.Function_9305a4b9b6
	GetPhysAddr: vspyx.Core.Function_30fd0fc629
	GetRxStats: vspyx.Core.Function_04eb2fc8cd
	GetTxErrorCounterValues: vspyx.Core.Function_a21f0bea5d
	GetTxStats: vspyx.Core.Function_e2636e7a65
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_98b6e63125
	MainFunction: vspyx.Core.Function_634bd5c449
	ReadMii: vspyx.Core.Function_90dd68cc04
	Receive: vspyx.Core.Function_c0471d99f1
	SetControllerMode: vspyx.Core.Function_4e191dc5cd
	SetPhysAddr: vspyx.Core.Function_65ccff1720
	Transmit: vspyx.Core.Function_49674ba094
	TxConfirmation: vspyx.Core.Function_21ee470862
	UpdatePhysAddrFilter: vspyx.Core.Function_820aa6589e
	WriteMii: vspyx.Core.Function_e39bd47448

class EthSMLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""EthSMLinkScope
	"""
	CtrlModeIndication: vspyx.Core.Function_1a36878ae0
	GetCurrentComMode: vspyx.Core.Function_2e41615af1
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_634bd5c449
	MainFunction: vspyx.Core.Function_634bd5c449
	RequestComMode: vspyx.Core.Function_74c6dc153a
	TcpIpModeIndication: vspyx.Core.Function_7300c2cecc
	TrcvLinkStateChg: vspyx.Core.Function_de44a67ae9

class EthSwtLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""EthSwtLinkScope
	"""
	DeletePortMirrorConfiguration: vspyx.Core.Function_d0db731c4e
	EnableVlan: vspyx.Core.Function_428d510be7
	EthRxFinishedIndication: vspyx.Core.Function_953a209ede
	EthTxAdaptBufferLength: vspyx.Core.Function_f690b7ecd2
	EthTxFinishedIndication: vspyx.Core.Function_953a209ede
	GetArlTable: vspyx.Core.Function_7ecdad779f
	GetBaudRate: vspyx.Core.Function_8d2cf33465
	GetCfgDataInfo: vspyx.Core.Function_d7dca48dc8
	GetCfgDataRaw: vspyx.Core.Function_018806a67c
	GetCounterValues: vspyx.Core.Function_337a128045
	GetDuplexMode: vspyx.Core.Function_7b17081185
	GetLinkState: vspyx.Core.Function_062744b333
	GetMacLearningMode: vspyx.Core.Function_a8005a1f2e
	GetMaxFIFOBufferFillLevel: vspyx.Core.Function_d98f948150
	GetPortCableDiagnosticsResult: vspyx.Core.Function_22df6012b2
	GetPortIdentifier: vspyx.Core.Function_b4670da4e1
	GetPortMacAddr: vspyx.Core.Function_9050f193b5
	GetPortMirrorState: vspyx.Core.Function_cc47ba165d
	GetPortSignalQuality: vspyx.Core.Function_3ea86411fb
	GetRxStats: vspyx.Core.Function_8e534c9e50
	GetSwitchIdentifier: vspyx.Core.Function_956da5beda
	GetSwitchPortMode: vspyx.Core.Function_13aea01b0b
	GetSwitchReg: vspyx.Core.Function_cc1f2c4b3b
	GetTxErrorCounterValues: vspyx.Core.Function_da394132b9
	GetTxStats: vspyx.Core.Function_11f853e6bd
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_d9afe74e34
	MainFunction: vspyx.Core.Function_634bd5c449
	MgmtInit: vspyx.Core.Function_634bd5c449
	NvmSingleBlockCallback: vspyx.Core.Function_74c6dc153a
	PortEnableTimeStamp: vspyx.Core.Function_f4a6e16e5c
	PortLinkStateRequest: vspyx.Core.Function_7b1af255f7
	ReadPortMirrorConfiguration: vspyx.Core.Function_7daec85dd1
	ReadTrcvRegister: vspyx.Core.Function_90dd68cc04
	ResetConfiguration: vspyx.Core.Function_d0db731c4e
	RunPortCableDiagnostic: vspyx.Core.Function_74c6dc153a
	SetForwardingMode: vspyx.Core.Function_74c6dc153a
	SetMacLearningMode: vspyx.Core.Function_4c4f697706
	SetMgmtInfo: vspyx.Core.Function_3884f53088
	SetPortLoopbackMode: vspyx.Core.Function_5d95878626
	SetPortMirrorState: vspyx.Core.Function_f8f6a0e8b3
	SetPortTestMode: vspyx.Core.Function_db6b466cfb
	SetPortTxMode: vspyx.Core.Function_411a5e147d
	SetSwitchPortMode: vspyx.Core.Function_621b7e0d6c
	SetSwitchReg: vspyx.Core.Function_b7c9d341c9
	StartSwitchPortAutoNegotiation: vspyx.Core.Function_74c6dc153a
	StoreConfiguration: vspyx.Core.Function_d0db731c4e
	SwitchInit: vspyx.Core.Function_d0db731c4e
	VerifyConfig: vspyx.Core.Function_2e41615af1
	WritePortMirrorConfiguration: vspyx.Core.Function_1dfc5e60e4
	WriteTrcvRegister: vspyx.Core.Function_e39bd47448

class EthTSynLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""EthTSynLinkScope
	"""
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_e801180a74
	MainFunction: vspyx.Core.Function_634bd5c449
	RxIndication: vspyx.Core.Function_99ba9cc388
	SetTransmissionMode: vspyx.Core.Function_875ceae9d1
	TrcvLinkStateChg: vspyx.Core.Function_e397ac510c
	TxConfirmation: vspyx.Core.Function_8cfc086487

class EthTrcvLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""EthTrcvLinkScope
	"""
	CheckWakeup: vspyx.Core.Function_d0db731c4e
	GetBaudRate: vspyx.Core.Function_4b1a26ce95
	GetCableDiagnosticsResult: vspyx.Core.Function_91201e25ee
	GetDuplexMode: vspyx.Core.Function_023a8b6b4c
	GetLinkState: vspyx.Core.Function_02169e460c
	GetPhyIdentifier: vspyx.Core.Function_1aa392315c
	GetPhySignalQuality: vspyx.Core.Function_956da5beda
	GetTransceiverMode: vspyx.Core.Function_98f26f9608
	GetTransceiverWakeupMode: vspyx.Core.Function_ba6fb8bb78
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_230f655f58
	MainFunction: vspyx.Core.Function_634bd5c449
	ReadMiiIndication: vspyx.Core.Function_6cd52df3a8
	RunCableDiagnostic: vspyx.Core.Function_d0db731c4e
	SetPhyLoopbackMode: vspyx.Core.Function_1f410d00a7
	SetPhyTestMode: vspyx.Core.Function_39d1672c39
	SetPhyTxMode: vspyx.Core.Function_0c03f162c7
	SetTransceiverMode: vspyx.Core.Function_c1e6fc091c
	SetTransceiverWakeupMode: vspyx.Core.Function_fe5fe2d616
	StartAutoNegotiation: vspyx.Core.Function_d0db731c4e
	TransceiverLinkStateRequest: vspyx.Core.Function_e397ac510c
	WriteMiiIndication: vspyx.Core.Function_2e25e5b2c5

class FrArTpLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""FrArTpLinkScope
	"""
	CancelReceive: vspyx.Core.Function_8c52b04f91
	CancelTransmit: vspyx.Core.Function_8c52b04f91
	ChangeParameter: vspyx.Core.Function_48f464a8f8
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_6e02cf22a4
	MainFunction: vspyx.Core.Function_634bd5c449
	RxIndication: vspyx.Core.Function_a282387e18
	Shutdown: vspyx.Core.Function_634bd5c449
	Transmit: vspyx.Core.Function_fcd25d59dc
	TriggerTransmit: vspyx.Core.Function_89e6f567fe
	TxConfirmation: vspyx.Core.Function_378634c28f

class FrIfLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""FrIfLinkScope
	"""
	AbortCommunication: vspyx.Core.Function_d0db731c4e
	AckAbsoluteTimerIRQ: vspyx.Core.Function_74c6dc153a
	AllSlots: vspyx.Core.Function_d0db731c4e
	AllowColdstart: vspyx.Core.Function_d0db731c4e
	CancelAbsoluteTimer: vspyx.Core.Function_74c6dc153a
	CancelTransmit: vspyx.Core.Function_8c52b04f91
	ClearTransceiverWakeup: vspyx.Core.Function_d28acd7060
	ControllerInit: vspyx.Core.Function_d0db731c4e
	DisableAbsoluteTimerIRQ: vspyx.Core.Function_74c6dc153a
	DisableLPdu: vspyx.Core.Function_6caebc02a3
	DisableTransceiverBranch: vspyx.Core.Function_fc1d03e432
	EnableAbsoluteTimerIRQ: vspyx.Core.Function_74c6dc153a
	EnableBusMirroring: vspyx.Core.Function_74c6dc153a
	EnableTransceiverBranch: vspyx.Core.Function_fc1d03e432
	GetAbsoluteTimerIRQStatus: vspyx.Core.Function_3afad65160
	GetChannelStatus: vspyx.Core.Function_499f8a0650
	GetClockCorrection: vspyx.Core.Function_587a798fdd
	GetCycleLength: vspyx.Core.Function_64cc535cb2
	GetGlobalTime: vspyx.Core.Function_cfab67cc2b
	GetMacrotickDuration: vspyx.Core.Function_5722ee316f
	GetMacroticksPerCycle: vspyx.Core.Function_5722ee316f
	GetNmVector: vspyx.Core.Function_2e41615af1
	GetNumOfStartupFrames: vspyx.Core.Function_2e41615af1
	GetPOCStatus: vspyx.Core.Function_8f7ddda482
	GetState: vspyx.Core.Function_0da372cfc8
	GetSyncFrameList: vspyx.Core.Function_a95cfed895
	GetTransceiverError: vspyx.Core.Function_547104385c
	GetTransceiverMode: vspyx.Core.Function_9650b78610
	GetTransceiverWUReason: vspyx.Core.Function_60d029eaee
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	GetWakeupRxStatus: vspyx.Core.Function_2e41615af1
	HaltCommunication: vspyx.Core.Function_d0db731c4e
	Init: vspyx.Core.Function_c8af197f2e
	JobListExec: vspyx.Core.Function_9808ef8308
	MainFunction: vspyx.Core.Function_9808ef8308
	ReadCCConfig: vspyx.Core.Function_3ea86411fb
	ReconfigLPdu: vspyx.Core.Function_ead18bd741
	SendWUP: vspyx.Core.Function_d0db731c4e
	SetAbsoluteTimer: vspyx.Core.Function_e39bd47448
	SetState: vspyx.Core.Function_8f59847fe8
	SetTransceiverMode: vspyx.Core.Function_900ab470ef
	SetWakeupChannel: vspyx.Core.Function_d28acd7060
	StartCommunication: vspyx.Core.Function_d0db731c4e
	Transmit: vspyx.Core.Function_fcd25d59dc
	CheckWakeupByTransceiver: vspyx.Core.Function_43d2648c99

class FrLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""FrLinkScope
	"""
	AbortCommunication: vspyx.Core.Function_d0db731c4e
	AckAbsoluteTimerIRQ: vspyx.Core.Function_74c6dc153a
	AllSlots: vspyx.Core.Function_d0db731c4e
	AllowColdstart: vspyx.Core.Function_d0db731c4e
	CancelAbsoluteTimer: vspyx.Core.Function_74c6dc153a
	CancelTxLPdu: vspyx.Core.Function_6caebc02a3
	CheckTxLPduStatus: vspyx.Core.Function_1efe761dab
	ControllerInit: vspyx.Core.Function_d0db731c4e
	DisableAbsoluteTimerIRQ: vspyx.Core.Function_74c6dc153a
	DisableLPdu: vspyx.Core.Function_6caebc02a3
	EnableAbsoluteTimerIRQ: vspyx.Core.Function_74c6dc153a
	GetAbsoluteTimerIRQStatus: vspyx.Core.Function_3afad65160
	GetChannelStatus: vspyx.Core.Function_499f8a0650
	GetClockCorrection: vspyx.Core.Function_587a798fdd
	GetGlobalTime: vspyx.Core.Function_cfab67cc2b
	GetNmVector: vspyx.Core.Function_2e41615af1
	GetNumOfStartupFrames: vspyx.Core.Function_2e41615af1
	GetPOCStatus: vspyx.Core.Function_8f7ddda482
	GetSyncFrameList: vspyx.Core.Function_a95cfed895
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	GetWakeupRxStatus: vspyx.Core.Function_2e41615af1
	HaltCommunication: vspyx.Core.Function_d0db731c4e
	Init: vspyx.Core.Function_4ef6b83c53
	PrepareLPdu: vspyx.Core.Function_6caebc02a3
	ReadCCConfig: vspyx.Core.Function_3ea86411fb
	ReceiveRxLPdu: vspyx.Core.Function_ccb3e26b1d
	ReconfigLPdu: vspyx.Core.Function_ead18bd741
	SendWUP: vspyx.Core.Function_d0db731c4e
	SetAbsoluteTimer: vspyx.Core.Function_e39bd47448
	SetWakeupChannel: vspyx.Core.Function_d28acd7060
	StartCommunication: vspyx.Core.Function_d0db731c4e
	TransmitTxLPdu: vspyx.Core.Function_9eb3be4d89
	ICS_RxIndication: vspyx.Core.Function_49a7c975df
	ICS_GetReceivedRxLPduInfo: vspyx.Core.Function_932f66a296

class FrNmLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""FrNmLinkScope
	"""
	CheckRemoteSleepIndication: vspyx.Core.Function_2e41615af1
	DisableCommunication: vspyx.Core.Function_d0db731c4e
	EnableCommunication: vspyx.Core.Function_d0db731c4e
	GetLocalNodeIdentifier: vspyx.Core.Function_2e41615af1
	GetNodeIdentifier: vspyx.Core.Function_2e41615af1
	GetPduData: vspyx.Core.Function_2e41615af1
	GetState: vspyx.Core.Function_40acffab2d
	GetUserData: vspyx.Core.Function_2e41615af1
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_3e22ac12c5
	MainFunction: vspyx.Core.Function_634bd5c449
	NetworkRelease: vspyx.Core.Function_d0db731c4e
	NetworkRequest: vspyx.Core.Function_d0db731c4e
	PassiveStartUp: vspyx.Core.Function_d0db731c4e
	RepeatMessageRequest: vspyx.Core.Function_d0db731c4e
	RequestBusSynchronization: vspyx.Core.Function_d0db731c4e
	RxIndication: vspyx.Core.Function_a282387e18
	SetSleepReadyBit: vspyx.Core.Function_74c6dc153a
	SetUserData: vspyx.Core.Function_2fe29a5add
	StartupError: vspyx.Core.Function_21ee470862
	Transmit: vspyx.Core.Function_fcd25d59dc
	TriggerTransmit: vspyx.Core.Function_89e6f567fe
	TxConfirmation: vspyx.Core.Function_378634c28f

class FrSmLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""FrSmLinkScope
	"""
	AllSlots: vspyx.Core.Function_d0db731c4e
	Init: vspyx.Core.Function_ffc452019b
	SetEcuPassive: vspyx.Core.Function_d0db731c4e

class FrTSynLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""FrTSynLinkScope
	"""
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_e6fabad22b
	MainFunction: vspyx.Core.Function_634bd5c449
	RxIndication: vspyx.Core.Function_a282387e18
	SetTransmissionMode: vspyx.Core.Function_ab7596eecc
	TriggerTransmit: vspyx.Core.Function_89e6f567fe

class FrTpLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""FrTpLinkScope
	"""
	CancelReceive: vspyx.Core.Function_8c52b04f91
	CancelTransmit: vspyx.Core.Function_8c52b04f91
	ChangeParameter: vspyx.Core.Function_48f464a8f8
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_c43fd24ebf
	MainFunction: vspyx.Core.Function_634bd5c449
	RxIndication: vspyx.Core.Function_a282387e18
	Shutdown: vspyx.Core.Function_634bd5c449
	Transmit: vspyx.Core.Function_fcd25d59dc
	TriggerTransmit: vspyx.Core.Function_89e6f567fe
	TxConfirmation: vspyx.Core.Function_378634c28f

class FrTrcvLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""FrTrcvLinkScope
	"""
	CheckWakeupByTransceiver: vspyx.Core.Function_21ee470862
	ClearTransceiverWakeup: vspyx.Core.Function_d0db731c4e
	DisableTransceiverBranch: vspyx.Core.Function_74c6dc153a
	EnableTransceiverBranch: vspyx.Core.Function_74c6dc153a
	GetTransceiverError: vspyx.Core.Function_3ea86411fb
	GetTransceiverMode: vspyx.Core.Function_57b99cb6e6
	GetTransceiverWUReason: vspyx.Core.Function_eb974d60ec
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_3672b0179b
	MainFunction: vspyx.Core.Function_634bd5c449
	SetTransceiverMode: vspyx.Core.Function_adf9884c24

class IpduMLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""IpduMLinkScope
	"""
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_881f50ecca
	MainFunctionRx: vspyx.Core.Function_634bd5c449
	MainFunctionTx: vspyx.Core.Function_634bd5c449
	RxIndication: vspyx.Core.Function_a282387e18
	Transmit: vspyx.Core.Function_fcd25d59dc
	TriggerTransmit: vspyx.Core.Function_89e6f567fe
	TxConfirmation: vspyx.Core.Function_378634c28f

class J1939NmLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""J1939NmLinkScope
	"""
	DeInit: vspyx.Core.Function_634bd5c449
	GetBusOffDelay: vspyx.Core.Function_30fd0fc629
	GetState: vspyx.Core.Function_40acffab2d
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_082ffd6d60
	MainFunction: vspyx.Core.Function_634bd5c449
	NetworkRelease: vspyx.Core.Function_d0db731c4e
	NetworkRequest: vspyx.Core.Function_d0db731c4e
	PassiveStartUp: vspyx.Core.Function_d0db731c4e
	RequestIndication: vspyx.Core.Function_68f27b7953
	RxIndication: vspyx.Core.Function_a282387e18
	TxConfirmation: vspyx.Core.Function_378634c28f

class J1939TpLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""J1939TpLinkScope
	"""
	CancelReceive: vspyx.Core.Function_8c52b04f91
	CancelTransmit: vspyx.Core.Function_8c52b04f91
	ChangeParameter: vspyx.Core.Function_48f464a8f8
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_f437e639fa
	MainFunction: vspyx.Core.Function_634bd5c449
	RxIndication: vspyx.Core.Function_a282387e18
	Shutdown: vspyx.Core.Function_634bd5c449
	Transmit: vspyx.Core.Function_fcd25d59dc
	TxConfirmation: vspyx.Core.Function_378634c28f

class LinIfLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""LinIfLinkScope
	"""
	CheckWakeup: vspyx.Core.Function_552be9d574
	EnableBusMirroring: vspyx.Core.Function_74c6dc153a
	GetConfiguredNAD: vspyx.Core.Function_2e41615af1
	GetPIDTable: vspyx.Core.Function_7ef33674ac
	GetTrcvMode: vspyx.Core.Function_537bee6189
	GetTrcvWakeupReason: vspyx.Core.Function_9bf908a29b
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	GotoSleep: vspyx.Core.Function_d0db731c4e
	HeaderIndication: vspyx.Core.Function_1fe564f90b
	Init: vspyx.Core.Function_de7291667f
	LinErrorIndication: vspyx.Core.Function_4d2890a76a
	MainFunction: vspyx.Core.Function_634bd5c449
	RxIndication: vspyx.Core.Function_30fd0fc629
	ScheduleRequest: vspyx.Core.Function_74c6dc153a
	SetConfiguredNAD: vspyx.Core.Function_74c6dc153a
	SetPIDTable: vspyx.Core.Function_4b77e50939
	SetTrcvMode: vspyx.Core.Function_2d37e182bb
	SetTrcvWakeupMode: vspyx.Core.Function_fbe69082dc
	Transmit: vspyx.Core.Function_fcd25d59dc
	TxConfirmation: vspyx.Core.Function_21ee470862
	Wakeup: vspyx.Core.Function_d0db731c4e
	WakeupConfirmation: vspyx.Core.Function_4c548fc750

class LinLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""LinLinkScope
	"""
	CheckWakeup: vspyx.Core.Function_d0db731c4e
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	GoToSleep: vspyx.Core.Function_d0db731c4e
	GoToSleepInternal: vspyx.Core.Function_d0db731c4e
	Init: vspyx.Core.Function_c68d8a0f69
	SendFrame: vspyx.Core.Function_ee477ed3d8
	Wakeup: vspyx.Core.Function_d0db731c4e
	WakeupInternal: vspyx.Core.Function_d0db731c4e

class LinSMLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""LinSMLinkScope
	"""
	GetCurrentComMode: vspyx.Core.Function_2e41615af1
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	GotoSleepConfirmation: vspyx.Core.Function_dd319a691a
	GotoSleepIndication: vspyx.Core.Function_21ee470862
	Init: vspyx.Core.Function_04d9a7a6d7
	MainFunction: vspyx.Core.Function_634bd5c449
	RequestComMode: vspyx.Core.Function_74c6dc153a
	ScheduleRequest: vspyx.Core.Function_74c6dc153a
	ScheduleRequestConfirmation: vspyx.Core.Function_dd319a691a
	WakeupConfirmation: vspyx.Core.Function_dd319a691a

class LinTrcvLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""LinTrcvLinkScope
	"""
	CheckWakeup: vspyx.Core.Function_d0db731c4e
	GetBusWuReason: vspyx.Core.Function_9bf908a29b
	GetOpMode: vspyx.Core.Function_537bee6189
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_0a7b3e59c1
	SetOpMode: vspyx.Core.Function_2d37e182bb
	SetWakeupMode: vspyx.Core.Function_fbe69082dc

class OsLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""OsLinkScope
	"""
	TimeSinceBootCounter: int
	IncrementCounter: vspyx.Core.Function_34c15b4a8d
	GetCounterValue: vspyx.Core.Function_0118ae8cae
	GetElapsedValue: vspyx.Core.Function_5071f5d3aa
	OS_TICKS2NS_TimeSinceBootCounter: vspyx.Core.Function_2a3d41304f
	OS_TICKS2US_TimeSinceBootCounter: vspyx.Core.Function_2a3d41304f
	OS_TICKS2MS_TimeSinceBootCounter: vspyx.Core.Function_2a3d41304f
	OS_TICKS2SEC_TimeSinceBootCounter: vspyx.Core.Function_2a3d41304f

class PduRLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""PduRLinkScope
	"""
	CanIfRxIndication: vspyx.Core.Function_a282387e18
	CanIfTxConfirmation: vspyx.Core.Function_378634c28f
	CanNmRxIndication: vspyx.Core.Function_a282387e18
	CanNmTriggerTransmit: vspyx.Core.Function_89e6f567fe
	CanNmTxConfirmation: vspyx.Core.Function_378634c28f
	CanTpCopyRxData: vspyx.Core.Function_a2f569d6de
	CanTpCopyTxData: vspyx.Core.Function_a83011c4da
	CanTpRxIndication: vspyx.Core.Function_378634c28f
	CanTpStartOfReception: vspyx.Core.Function_dc27da2c70
	CanTpTxConfirmation: vspyx.Core.Function_378634c28f
	ComCancelTransmit: vspyx.Core.Function_8c52b04f91
	ComTransmit: vspyx.Core.Function_fcd25d59dc
	DbgTransmit: vspyx.Core.Function_fcd25d59dc
	DcmCancelReceive: vspyx.Core.Function_8c52b04f91
	DcmCancelTransmit: vspyx.Core.Function_8c52b04f91
	DcmTransmit: vspyx.Core.Function_fcd25d59dc
	DltTransmit: vspyx.Core.Function_fcd25d59dc
	DoIPIfTxConfirmation: vspyx.Core.Function_378634c28f
	DoIPTpCopyRxData: vspyx.Core.Function_a2f569d6de
	DoIPTpCopyTxData: vspyx.Core.Function_a83011c4da
	DoIPTpRxIndication: vspyx.Core.Function_378634c28f
	DoIPTpStartOfReception: vspyx.Core.Function_dc27da2c70
	DoIPTpTxConfirmation: vspyx.Core.Function_378634c28f
	FrArTpCopyRxData: vspyx.Core.Function_a2f569d6de
	FrArTpCopyTxData: vspyx.Core.Function_a83011c4da
	FrArTpRxIndication: vspyx.Core.Function_378634c28f
	FrArTpStartOfReception: vspyx.Core.Function_dc27da2c70
	FrArTpTxConfirmation: vspyx.Core.Function_378634c28f
	FrIfRxIndication: vspyx.Core.Function_a282387e18
	FrIfTriggerTransmit: vspyx.Core.Function_89e6f567fe
	FrIfTxConfirmation: vspyx.Core.Function_378634c28f
	FrNmTriggerTransmit: vspyx.Core.Function_89e6f567fe
	FrNmTxConfirmation: vspyx.Core.Function_378634c28f
	FrTpCopyRxData: vspyx.Core.Function_a2f569d6de
	FrTpCopyTxData: vspyx.Core.Function_a83011c4da
	FrTpRxIndication: vspyx.Core.Function_378634c28f
	FrTpStartOfReception: vspyx.Core.Function_dc27da2c70
	FrTpTxConfirmation: vspyx.Core.Function_378634c28f
	IpduMRxIndication: vspyx.Core.Function_a282387e18
	IpduMTransmit: vspyx.Core.Function_fcd25d59dc
	IpduMTriggerTransmit: vspyx.Core.Function_89e6f567fe
	IpduMTxConfirmation: vspyx.Core.Function_378634c28f
	J1939DcmCancelReceive: vspyx.Core.Function_8c52b04f91
	J1939DcmCancelTransmit: vspyx.Core.Function_8c52b04f91
	J1939DcmTransmit: vspyx.Core.Function_fcd25d59dc
	J1939RmTransmit: vspyx.Core.Function_fcd25d59dc
	J1939TpCopyRxData: vspyx.Core.Function_a2f569d6de
	J1939TpCopyTxData: vspyx.Core.Function_a83011c4da
	J1939TpRxIndication: vspyx.Core.Function_378634c28f
	J1939TpStartOfReception: vspyx.Core.Function_dc27da2c70
	J1939TpTxConfirmation: vspyx.Core.Function_378634c28f
	LdComTransmit: vspyx.Core.Function_fcd25d59dc
	LinIfRxIndication: vspyx.Core.Function_a282387e18
	LinIfTriggerTransmit: vspyx.Core.Function_89e6f567fe
	LinIfTxConfirmation: vspyx.Core.Function_378634c28f
	LinTpCopyRxData: vspyx.Core.Function_a2f569d6de
	LinTpCopyTxData: vspyx.Core.Function_a83011c4da
	LinTpRxIndication: vspyx.Core.Function_378634c28f
	LinTpStartOfReception: vspyx.Core.Function_dc27da2c70
	LinTpTxConfirmation: vspyx.Core.Function_378634c28f
	MirrorTransmit: vspyx.Core.Function_fcd25d59dc
	DisableRouting: vspyx.Core.Function_378634c28f
	EnableRouting: vspyx.Core.Function_a2f38cfeb7
	GetConfigurationId: vspyx.Core.Function_f470a03f0d
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_685978a5d1
	SecOCCancelReceive: vspyx.Core.Function_8c52b04f91
	SecOCCancelTransmit: vspyx.Core.Function_8c52b04f91
	SecOCCopyRxData: vspyx.Core.Function_a2f569d6de
	SecOCCopyTxData: vspyx.Core.Function_a83011c4da
	SecOCIfRxIndication: vspyx.Core.Function_a282387e18
	SecOCIfTxConfirmation: vspyx.Core.Function_378634c28f
	SecOCStartOfReception: vspyx.Core.Function_dc27da2c70
	SecOCTpRxIndication: vspyx.Core.Function_378634c28f
	SecOCTpTxConfirmation: vspyx.Core.Function_378634c28f
	SecOCTransmit: vspyx.Core.Function_fcd25d59dc
	SoConModeChg: vspyx.Core.Function_bc9980100d
	LocalIpAddrAssignmentChg: vspyx.Core.Function_343ba6cd45
	SoAdIfTxConfirmation: vspyx.Core.Function_378634c28f
	SoAdTpTxConfirmation: vspyx.Core.Function_378634c28f
	SoAdIfTriggerTransmit: vspyx.Core.Function_89e6f567fe
	SoAdIfRxIndication: vspyx.Core.Function_a282387e18
	SoAdTpRxIndication: vspyx.Core.Function_378634c28f
	SoAdTpStartOfReception: vspyx.Core.Function_dc27da2c70
	SoAdTpTriggerTransmit: vspyx.Core.Function_89e6f567fe
	SoAdTpCopyRxData: vspyx.Core.Function_a2f569d6de
	SoAdTpCopyTxData: vspyx.Core.Function_a83011c4da
	SomeIpTpCopyRxData: vspyx.Core.Function_a2f569d6de
	SomeIpTpCopyTxData: vspyx.Core.Function_a83011c4da
	SomeIpTpRxIndication: vspyx.Core.Function_378634c28f
	SomeIpTpStartOfReception: vspyx.Core.Function_dc27da2c70
	SomeIpTpTransmit: vspyx.Core.Function_fcd25d59dc
	SomeIpTpTxConfirmation: vspyx.Core.Function_378634c28f
	UdpNmRxIndication: vspyx.Core.Function_a282387e18
	UdpNmTriggerTransmit: vspyx.Core.Function_89e6f567fe
	UdpNmTxConfirmation: vspyx.Core.Function_378634c28f

class SdLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""SdLinkScope
	"""
	ClientServiceSetState: vspyx.Core.Function_53e5cdd22f
	ConsumedEventGroupSetState: vspyx.Core.Function_09aa546ea0
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_8898e96bc8
	LocalIpAddrAssignmentChg: vspyx.Core.Function_343ba6cd45
	MainFunction: vspyx.Core.Function_634bd5c449
	SoAdIfTxConfirmation: vspyx.Core.Function_378634c28f
	SoAdIfTriggerTransmit: vspyx.Core.Function_89e6f567fe
	RxIndication: vspyx.Core.Function_a282387e18
	SoAdIfRxIndication: vspyx.Core.Function_a282387e18
	ServerServiceSetState: vspyx.Core.Function_e4766b54ce
	SoConModeChg: vspyx.Core.Function_bc9980100d

class SoAdLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""SoAdLinkScope
	"""
	CloseSoCon: vspyx.Core.Function_0617fd6a29
	CopyTxData: vspyx.Core.Function_4efad67327
	DisableRouting: vspyx.Core.Function_d0db731c4e
	DisableSpecificRouting: vspyx.Core.Function_6caebc02a3
	EnableRouting: vspyx.Core.Function_d0db731c4e
	EnableSpecificRouting: vspyx.Core.Function_6caebc02a3
	GetAndResetMeasurementData: vspyx.Core.Function_3ea86411fb
	GetLocalAddr: vspyx.Core.Function_c6eac12677
	GetPhysAddr: vspyx.Core.Function_066aa755c1
	GetRemoteAddr: vspyx.Core.Function_31c1db4ec3
	GetSoConId: vspyx.Core.Function_b0c7a11145
	GetSoConMode: vspyx.Core.Function_1f61b10e8c
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	IfRoutingGroupTransmit: vspyx.Core.Function_d0db731c4e
	IfSpecificRoutingGroupTransmit: vspyx.Core.Function_6caebc02a3
	IfTransmit: vspyx.Core.Function_fcd25d59dc
	Init: vspyx.Core.Function_4363e98f1e
	LocalIpAddrAssignmentChg: vspyx.Core.Function_7e677b392b
	MainFunction: vspyx.Core.Function_634bd5c449
	OpenSoCon: vspyx.Core.Function_8c52b04f91
	ReadDhcpHostNameOption: vspyx.Core.Function_53158cf6a4
	ReleaseIpAddrAssignment: vspyx.Core.Function_8c52b04f91
	ReleaseRemoteAddr: vspyx.Core.Function_a2f38cfeb7
	RequestIpAddrAssignment: vspyx.Core.Function_40edaf836c
	RxIndication: vspyx.Core.Function_843dfb9e4a
	SetRemoteAddr: vspyx.Core.Function_900a6aa5f1
	SetUniqueRemoteAddr: vspyx.Core.Function_775774c85d
	TcpAccepted: vspyx.Core.Function_2d45cd33d3
	TcpConnected: vspyx.Core.Function_a2f38cfeb7
	TcpIpEvent: vspyx.Core.Function_94e557a30a
	TpCancelReceive: vspyx.Core.Function_8c52b04f91
	TpCancelTransmit: vspyx.Core.Function_8c52b04f91
	TpChangeParameter: vspyx.Core.Function_48f464a8f8
	TpTransmit: vspyx.Core.Function_fcd25d59dc
	TxConfirmation: vspyx.Core.Function_7608587d51
	WriteDhcpHostNameOption: vspyx.Core.Function_014124c847
	ICS_RxIndication: vspyx.Core.Function_f76f76b722

class TcpIpLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""TcpIpLinkScope
	"""
	Bind: vspyx.Core.Function_56ca159dda
	ChangeParameter: vspyx.Core.Function_014124c847
	Close: vspyx.Core.Function_0617fd6a29
	DhcpReadOption: vspyx.Core.Function_10e9091fa9
	DhcpV6ReadOption: vspyx.Core.Function_6cb08b97de
	DhcpV6WriteOption: vspyx.Core.Function_c122e5469c
	DhcpWriteOption: vspyx.Core.Function_417469245b
	GetAndResetMeasurementData: vspyx.Core.Function_3ea86411fb
	GetArpCacheEntries: vspyx.Core.Function_022638b7f7
	GetCtrlIdx: vspyx.Core.Function_2e41615af1
	GetIpAddr: vspyx.Core.Function_e364932036
	GetNdpCacheEntries: vspyx.Core.Function_cf76228978
	GetPhysAddr: vspyx.Core.Function_2e41615af1
	GetRemotePhysAddr: vspyx.Core.Function_0d1cf37935
	SoAdGetSocket: vspyx.Core.Function_402051a095
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	IcmpTransmit: vspyx.Core.Function_b4b0109a2b
	IcmpV6Transmit: vspyx.Core.Function_b4b0109a2b
	Init: vspyx.Core.Function_d27a7cfeae
	MainFunction: vspyx.Core.Function_634bd5c449
	ReleaseIpAddrAssignment: vspyx.Core.Function_d0db731c4e
	RequestComMode: vspyx.Core.Function_3f5bb5034b
	RequestIpAddrAssignment: vspyx.Core.Function_b3afbfc193
	ResetIpAssignment: vspyx.Core.Function_b9ef01da62
	RxIndication: vspyx.Core.Function_99ba9cc388
	TcpConnect: vspyx.Core.Function_900a6aa5f1
	TcpListen: vspyx.Core.Function_7130e2d59d
	TcpReceived: vspyx.Core.Function_42862c8550
	TcpTransmit: vspyx.Core.Function_9d28d57be2
	UdpTransmit: vspyx.Core.Function_f2c7ce2b02

class UdpNmLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""UdpNmLinkScope
	"""
	CheckRemoteSleepIndication: vspyx.Core.Function_2e41615af1
	DisableCommunication: vspyx.Core.Function_d0db731c4e
	EnableCommunication: vspyx.Core.Function_d0db731c4e
	GetLocalNodeIdentifier: vspyx.Core.Function_2e41615af1
	GetNodeIdentifier: vspyx.Core.Function_2e41615af1
	GetPduData: vspyx.Core.Function_2e41615af1
	GetState: vspyx.Core.Function_40acffab2d
	GetUserData: vspyx.Core.Function_2e41615af1
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_f403f67433
	MainFunction: vspyx.Core.Function_634bd5c449
	NetworkRelease: vspyx.Core.Function_d0db731c4e
	NetworkRequest: vspyx.Core.Function_d0db731c4e
	PassiveStartUp: vspyx.Core.Function_d0db731c4e
	RepeatMessageRequest: vspyx.Core.Function_d0db731c4e
	RequestBusSynchronization: vspyx.Core.Function_d0db731c4e
	SetSleepReadyBit: vspyx.Core.Function_74c6dc153a
	SetUserData: vspyx.Core.Function_2fe29a5add
	SoConModeChg: vspyx.Core.Function_bc9980100d
	LocalIpAddrAssignmentChg: vspyx.Core.Function_343ba6cd45
	SoAdIfTriggerTransmit: vspyx.Core.Function_89e6f567fe
	SoAdIfRxIndication: vspyx.Core.Function_a282387e18
	SoAdIfTxConfirmation: vspyx.Core.Function_378634c28f
	Transmit: vspyx.Core.Function_fcd25d59dc
	TriggerTransmit: vspyx.Core.Function_89e6f567fe

class WEthLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""WEthLinkScope
	"""
	GetBufWRxParams: vspyx.Core.Function_0b0ec2a15c
	GetBufWTxParams: vspyx.Core.Function_71e3c17e3a
	GetControllerMode: vspyx.Core.Function_6004950ab0
	GetPhysAddr: vspyx.Core.Function_30fd0fc629
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	GetWEtherStats32: vspyx.Core.Function_956da5beda
	GetWEtherStats64: vspyx.Core.Function_85a52153a3
	Init: vspyx.Core.Function_0fbc1d37d9
	MainFunction: vspyx.Core.Function_634bd5c449
	ReadTrcvRegs: vspyx.Core.Function_8302e97ddc
	Receive: vspyx.Core.Function_a47ba1e076
	SetBufWTxParams: vspyx.Core.Function_4cb130ce40
	SetControllerMode: vspyx.Core.Function_4e191dc5cd
	SetPhysAddr: vspyx.Core.Function_65ccff1720
	Transmit: vspyx.Core.Function_49674ba094
	TriggerPriorityQueueTransmit: vspyx.Core.Function_a2b471d826
	TxConfirmation: vspyx.Core.Function_21ee470862
	UpdatePhysAddrFilter: vspyx.Core.Function_724088b4ea
	WriteTrcvRegs: vspyx.Core.Function_20b65de5ae

class WEthTrcvLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""WEthTrcvLinkScope
	"""
	GetChanRxParams: vspyx.Core.Function_14877e3e48
	GetLinkState: vspyx.Core.Function_02169e460c
	GetTransceiverMode: vspyx.Core.Function_98f26f9608
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_4516932e16
	MainFunction: vspyx.Core.Function_634bd5c449
	SetChanRxParams: vspyx.Core.Function_7dd09b80f1
	SetChanTxParams: vspyx.Core.Function_994f9cbf3e
	SetRadioParams: vspyx.Core.Function_470e3fff9f
	SetTransceiverMode: vspyx.Core.Function_c1e6fc091c

class XcpLinkScope(vspyx.AUTOSAR.Classic.LinkScopeBase):
	"""XcpLinkScope
	"""
	CanIfRxIndication: vspyx.Core.Function_a282387e18
	CanIfTxConfirmation: vspyx.Core.Function_378634c28f
	FrIfRxIndication: vspyx.Core.Function_a282387e18
	FrIfTriggerTransmit: vspyx.Core.Function_89e6f567fe
	FrIfTxConfirmation: vspyx.Core.Function_378634c28f
	GetVersionInfo: vspyx.Core.Function_a7db2cec72
	Init: vspyx.Core.Function_621a7b1df0
	MainFunction: vspyx.Core.Function_634bd5c449
	SoConModeChg: vspyx.Core.Function_bc9980100d
	LocalIpAddrAssignmentChg: vspyx.Core.Function_343ba6cd45
	SoAdIfTxConfirmation: vspyx.Core.Function_378634c28f
	SoAdIfTriggerTransmit: vspyx.Core.Function_89e6f567fe
	SoAdIfRxIndication: vspyx.Core.Function_a282387e18
	SetTransmissionMode: vspyx.Core.Function_26b49bce44

class PduR(vspyx.AUTOSAR.Classic.BSW):
	"""PduR
	"""

	@staticmethod
	def New(config: vspyx.AUTOSAR.Classic.ECUConfiguration) -> vspyx.AUTOSAR.Classic.PduR: ...

class SimpleSoAdProcessor(vspyx.Runtime.Component):
	"""SimpleSoAdProcessor
	"""
	OnPDU: vspyx.Core.Callback_ab52505fda

	@staticmethod
	def New() -> vspyx.AUTOSAR.Classic.SimpleSoAdProcessor: ...


	@typing.overload
	def Attach(self, follower: vspyx.TCPIP.Follower) -> typing.Any: ...


	@typing.overload
	def Attach(self, socket: vspyx.TCPIP.Socket) -> typing.Any: ...


	@typing.overload
	def Detach(self) -> typing.Any: ...


	@typing.overload
	def Detach(self, socket: vspyx.TCPIP.Socket) -> typing.Any: ...

class SoAd(vspyx.AUTOSAR.Classic.BSW):
	"""SoAd
	"""

	@staticmethod
	def New(config: vspyx.AUTOSAR.Classic.ECUConfiguration) -> vspyx.AUTOSAR.Classic.SoAd: ...

class TcpIp(vspyx.AUTOSAR.Classic.BSW):
	"""TcpIp
	"""

	@staticmethod
	def New(config: vspyx.AUTOSAR.Classic.ECUConfiguration) -> vspyx.AUTOSAR.Classic.TcpIp: ...

