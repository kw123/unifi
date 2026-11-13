"""deviceTables.py - dynamic state + property tables for all UniFi/Protect device types.

Imported by plugin.py; used in getDeviceStateList() to build each device's state list at runtime
(the Devices.xml <States> blocks are empty). State EXISTENCE is keyed on deviceTypeId ONLY - stable and
known at startup before any dict is read - so the list is correct from the first call and never
fluctuates with dict content.

Each state maps to a type code:  "s"=string  "i"=integer  "n"=number(float)  "b"=bool(true/false)
"""

def _sp(*names):    return {"sensor_protect_" + n for n in names}   # _sp("entry","motion") -> {"sensor_protect_entry","sensor_protect_motion"}


# base shared by every "full" Protect device (all sensors + gateway + speaker); relay_protect and
# light_protect carry a reduced base in their own bucket instead (see K_PROTECT_USES_COMMON).
K_PROTECT_COMMON_STATES = {
	"status":           "s",
	"name":             "s",
	"MAC":              "s",
	"id":               "s",
	"type":             "s",
	"firmwareVersion":  "s",
	"isConnected":      "b",
	"isAdopted":        "b",
	"lastSeen":         "s",
	"connectedSince":   "s",
	"lastStatusChange": "s",
	"created":          "s",
	"groupMember":      "s",
}


# shared layers stacked on the base, each applied to an explicit set of deviceTypeIds. Membership matches
# the previous static XML exactly - a shared state now lives in ONE place instead of N device blocks.
K_PROTECT_LAYERS = (
	# radio signal + firmware-update state - every non-PoE device (all but the wired air-quality sensor)
	({
		"btSignalQuality":     "i",
		"btSignalStrength":    "i",
		"btSignalNoiseRatio":  "i",
		"firmwareUpdateState": "s",
	}, {"relay_protect"} | _sp("allInOne", "entry", "motion", "environmental", "glassbreak", "siren", "smoke_co", "keyfob")),

	# the SuperLink bridge the device is paired to
	({
		"bridge_used": "s",
	}, {"relay_protect"} | _sp("entry", "motion", "environmental", "glassbreak", "keyfob")),

	# the SuperLink bridges the device can currently hear (all LoRa devices)
	({
		"bridgeCandidate1": "s",
		"bridgeCandidate2": "s",
		"bridgeCandidate3": "s",
	}, {"relay_protect"} | _sp("entry", "motion", "environmental", "glassbreak", "siren", "smoke_co", "keyfob")),

	# status-LED enabled flag
	({
		"ledEnabled": "b",
	}, {"relay_protect"} | _sp("allInOne", "entry", "motion", "environmental", "glassbreak", "siren", "smoke_co")),

	# function-button press timestamps
	({
		"sensorButtonPressedAt":      "s",
		"sensorButtonPressedAt_Last": "s",
	}, {"relay_protect", "relay_protect_input"} | _sp("allInOne", "entry", "motion", "environmental", "glassbreak")),
)


# per-type states - everything not already provided by the base + the layers above
K_PROTECT_TYPE_STATES = {

	"sensor_protect_allInOne": {
		"temperature":                "n",
		"humidity":                   "n",
		"light":                      "n",
		"motionDetected":             "b",
		"motionDetectedAt":           "s",
		"motionDetectedAt_Last":      "s",
		"isOpened":                   "b",
		"mountType":                  "s",
		"openStatusChangedAt":        "s",
		"openStatusChangedAt_Last":   "s",
		"motionEnabled":              "b",
		"motionSensitivity":          "n",
		"motionSensitivityWhenArmed": "n",
		"temperatureEnabled":         "b",
		"temperatureLowThreshold":    "n",
		"temperatureHighThreshold":   "n",
		"humidityLowThreshold":       "n",
		"humidityHighThreshold":      "n",
		"humidityEnabled":            "b",
		"waterDetectedEnabled":       "b",
		"waterDetected":              "b",
		"waterDetectedAt":            "s",
		"waterDetectedAt_Last":       "s",
		"alarmTriggeredAt":           "s",
	},

	"sensor_protect_entry": {
		"isOpened":                 "b",
		"mountType":                "s",
		"openStatusChangedAt":      "s",
		"openStatusChangedAt_Last": "s",
		"alarmTriggeredAt":         "s",
	},

	"sensor_protect_motion": {
		"motionEnabled":              "b",
		"motionSensitivity":          "n",
		"motionSensitivityWhenArmed": "n",
		"motionDetected":             "b",
	},

	"sensor_protect_environmental": {
		"temperature":                  "n",
		"humidity":                     "n",
		"temperatureEnabled":           "b",
		"temperatureLowThreshold":      "n",
		"temperatureHighThreshold":     "n",
		"humidityLowThreshold":         "n",
		"humidityHighThreshold":        "n",
		"humidityEnabled":              "b",
		"waterDetectedEnabled":         "b",
		"waterDetectedInternalEnabled": "b",
		"waterDetectedExternalEnabled": "b",
		"waterDetected":                "b",
		"waterDetectedAt":              "s",
		"waterDetectedAt_Last":         "s",
	},

	"sensor_protect_glassbreak": {
		"motionEnabled":                "b",
		"motionSensitivity":            "n",
		"motionSensitivityWhenArmed":   "n",
		"glassBreakEnabled":            "b",
		"glassBreakSensitivity":        "n",
		"glassBreakSensitivityWhenArmed":"n",
		"glassBreakDetected":           "b",
		"glassBreakAt":                 "s",
		"glassBreakAt_Last":            "s",
		"alarmTriggeredAt":             "s",
	},

	"sensor_protect_siren": {
		"sirenActive":            "b",
		"tamperDetected":         "b",
		"tamperingDetectedAt":    "s",
		"tamperingDetectedAt_Last":"s",
		"powerSource":            "s",
	},

	"sensor_protect_smoke_co": {
		"smokeAlarm":              "b",
		"coAlarm":                 "b",
		"smokeValue":              "n",
		"coValue":                 "n",
		"alarmEnabled":            "b",
		"batteryLow":              "b",
		"endOfLife":               "b",
		"smokeSensorFault":        "b",
		"coSensorFault":           "b",
		"tamperDetected":          "b",
		"tamperingDetectedAt":     "s",
		"tamperingDetectedAt_Last":"s",
		"smokeAlarmAt":            "s",
		"smokeAlarmAt_Last":       "s",
		"coAlarmAt":               "s",
		"coAlarmAt_Last":          "s",
		"alarmTriggeredAt":        "s",
	},

	"sensor_protect_keyfob": {
		"buttonLabels":      "s",
		"buttonPressed":     "s",
		"lastButtonPressed": "s",
		"action":            "s",
		"actionAt":          "s",
		"lastAction":        "s",
		"lastActionAt":      "s",
	},

	"sensor_protect_airquality": {
		"aqi":                "n",
		"vapeIndex":          "n",
		"vapeDetected":       "b",
		"co2":                "n",
		"voc":                "n",
		"nox":                "n",
		"tvoc":               "n",
		"pm1p0":              "n",
		"pm2p5":              "n",
		"pm4p0":              "n",
		"pm10p0":             "n",
		"temperature":        "n",
		"humidity":           "n",
		"vapeEnabled":        "b",
		"vapeDetectedAt":     "s",
		"vapeDetectedAt_Last":"s",
	},

	# relay_protect and light_protect skip K_PROTECT_COMMON_STATES and carry their own reduced base here
	"relay_protect": {                    # display = built-in onOffState
		"groupMember":      "s",
		"status":          "s",
		"name":            "s",
		"MAC":             "s",
		"id":              "s",
		"type":            "s",
		"firmwareVersion": "s",
		"isConnected":     "b",
		"isAdopted":       "b",
		"lastSeen":        "s",
		"created":         "s",
		"lastCommand":     "s",
	},

	"superlink_gateway": {
		"ipNumber":        "s",
		"networkMAC":      "s",
		"numberOfSensors": "n",
		"sensorList":      "s",
	},

	"speaker_protect": {
		"volume":        "n",
		"micVolume":     "n",
		"isMicEnabled":  "b",
		"speakerState":  "s",
		"isStreaming":   "b",
	},

	"light_protect": {
		"groupMember":      "s",
		"status":          "s",
		"isConnected":     "b",
		"MAC":             "s",
		"id":              "s",
		"ipNumber":        "s",
		"firmwareVersion": "s",
		"lastSeen":        "s",
		"created":         "s",
		"motionDetected":  "b",
		"lastMotionAt":    "s",
		"lastMotionAt_Last":"s",
		"isDark":          "b",
		"ledLevel":        "i",
		"lightMode":       "s",
		"pirSensitivity":  "i",
		"pirDuration":     "i",
		"luxSensitivity":  "s",
		"isLightForceOn":  "b",
	},

	"relay_protect_input": {
		"groupMember":      "s",
		"MAC":             "s",
		"input1State":     "b",
		"input1At":        "s",
		"input1At_Last":   "s",
		"input1PressType": "s",
		"input2State":     "b",
		"input2At":        "s",
		"input2At_Last":   "s",
		"input2PressType": "s",
		"created":         "s",
	},

	"relay_protect_output2": {            # display = built-in onOffState
		"groupMember":      "s",
		"MAC":         "s",
		"lastCommand": "s",
		"created":     "s",
	},
}


# device types that use the full 12-state COMMON base (relay_protect / light_protect have their own base)
K_PROTECT_USES_COMMON       = _sp("allInOne", "entry", "motion", "environmental", "glassbreak", "siren", "smoke_co", "keyfob", "airquality") | {"superlink_gateway", "speaker_protect"}
# device types whose display state (UiDisplayStateId) is "displayStatus", generated dynamically like any
# other state. relay_protect / relay_protect_output2 are absent: their display is the built-in onOffState.
K_PROTECT_HAS_DISPLAYSTATUS = _sp("allInOne", "entry", "motion", "environmental", "glassbreak", "siren", "smoke_co", "keyfob", "airquality") | {"superlink_gateway", "speaker_protect", "light_protect", "relay_protect_input"}
K_PROTECT_DYNAMIC_TYPES = set(K_PROTECT_TYPE_STATES)


# ==================================================================================================
# device PROPERTIES (pluginProps) - single source of truth for the capability + marker props that were
# previously hidden checkboxes in each device's ConfigUI. deviceProps(deviceTypeId) rebuilds the
# exact prop dict; deviceStartComm enforces it so the tables are authoritative and drift auto-corrects.
# ==================================================================================================

# the props.<marker> flag each device type carries (used by indigo.devices.iter("props.<marker>") filters)
DEVICE_MARKER = {
	"UniFi":                 "isUniFi",
	"Device-AP":             "isAP",
	"camera":                "isCamera",
	"gateway":               "isGateway",
	"neighbor":              "isNeighbor",
	"system_controller":     "isSystemDev",
	"system_protect":        "isSystemDev",
	"camera_protect":        "isProtectCamera",
	"relay_protect":         "isProtectRelay",
	"relay_protect_output2": "isProtectRelay2",
	"relay_protect_input":   "isProtectRelayInput",
	"light_protect":         "isProtectLight",
	"speaker_protect":       "isProtectSpeaker",
	"superlink_gateway":     "isProtectGateway",
}
DEVICE_MARKER.update({"Device-SW-" + n: "isSwitch" for n in ("4","5","6","7","8","9","10","11","12","14","16","18","20","22","24","26","28","30","48","50","52","54")})
DEVICE_MARKER.update({t: "isProtectSensor" for t in _sp("allInOne","entry","motion","environmental","glassbreak","siren","smoke_co","keyfob","airquality")})

# types that carry the full Indigo capability block (SupportsOnState / SupportsSensorValue /
# SupportsStatusRequest / AllowOnStateChange / AllowSensorValueChange); the two below vary per type,
# the other three are always False in that block.
DEVICE_CAP_BLOCK        = set(DEVICE_MARKER) - {"relay_protect_input"}   # every device type except the read-only relay inputs
HAS_SupportsOnState      = DEVICE_CAP_BLOCK - {"sensor_protect_keyfob"}   # everything in the block except the keyfob
HAS_AllowOnStateChange   = {"relay_protect","relay_protect_output2","light_protect"}
HAS_SupportsBatteryLevel = _sp("allInOne","entry","motion","environmental","glassbreak","keyfob","smoke_co")
HAS_SupportsBatteryFalse = _sp("airquality")                         # declares SupportsBatteryLevel = False explicitly

def deviceProps(dt):
	"""Return the exact capability/marker pluginProps dict for a Protect/UniFi device type (or {} if the
	type has none). Mirrors what used to be hidden checkboxes in Devices.xml."""
	p = {}
	if dt in DEVICE_MARKER:            p[DEVICE_MARKER[dt]] = True
	if dt in DEVICE_CAP_BLOCK:
		p["SupportsOnState"]        = dt in HAS_SupportsOnState
		p["SupportsSensorValue"]    = False
		p["SupportsStatusRequest"]  = False
		p["AllowOnStateChange"]     = dt in HAS_AllowOnStateChange
		p["AllowSensorValueChange"] = False
	elif dt == "relay_protect_input":                                # combined inputs device
		p["SupportsOnState"]        = True    # onOffState mirrors the selected input channel (_refreshRelayInputDisplay)
		p["AllowOnStateChange"]     = False   # ... but it is sensor-driven, the user cannot toggle it
	if   dt in HAS_SupportsBatteryLevel: p["SupportsBatteryLevel"] = True
	elif dt in HAS_SupportsBatteryFalse: p["SupportsBatteryLevel"] = False
	return p


# ==================================================================================================
# UniFi / infrastructure device state tables (switches, APs, gateway, cameras, system, neighbor).
# Switches (Device-SW-N) share ONE base + feature layers + N generated port_NN states - see
# getDeviceStateList(). Type codes as above:  s=string  i=integer  n=number  b=bool
# ==================================================================================================

K_UNIFI_COMMON = {          # the 4 states shared by EVERY UniFi device type (created / groupMember are
	"status":           "s",   # common to all but the camera(s), so they stay in the per-type sets below)
	"displayStatus":    "s",
	"MAC":              "s",
	"lastStatusChange": "s",
}

K_UNIFI_SWITCH_BASE = {
	"groupMember":          "s",
	"overHeating":          "s",
	"model":                "s",
	"ipNumber":             "s",
	"created":              "s",
	"hostname":             "s",
	"previousStatusChange": "s",
	"vendor":               "s",
	"nClients":             "s",
	"unifi_id":             "s",
	"upDownSetting":        "s",
	"switchNo":             "s",
	"upSince":              "s",
}
K_UNIFI_SWITCH_TEMP  = ("temperature", "s")   # Device-SW-10 and up
K_UNIFI_SWITCH_FAN   = ("fanLevel", "s")      # Device-SW-12 and up
K_UNIFI_SWITCH_VLAN  = ("vlan", "s")          # Device-SW-52 only
K_UNIFI_PORT_CODE    = "s"                     # port_01..port_NN
K_UNIFI_SWITCH_TYPES = {"Device-SW-%d" % n for n in (4,5,6,7,8,9,10,11,12,14,16,18,20,22,24,26,28,30,48,50,52,54)}

# non-switch infrastructure device types - full per-type state sets
K_UNIFI_TYPE_STATES = {
	"UniFi": {
		"groupMember":            "s",
		"ipNumber":               "s",
		"created":                "s",
		"name":                   "s",
		"vendor":                 "s",
		"previousStatusChange":   "s",
		"lastStatusChangeReason": "s",
		"upDownSetting":          "s",
		"tx_Bytes_Last5Minutes":  "n",
		"rx_Bytes_Last5Minutes":  "n",
		"GHz":                    "s",
		"noiseWiFi":              "s",
		"signalWiFi":             "s",
		"stateWiFi":              "s",
		"signal2NoiseWiFi":       "s",
		"satisfactionWiFi":       "s",
		"channelWiFi":            "s",
		"AP":                     "s",
		"powerMgmtWiFi":          "s",
		"rx_tx_RateWiFi":         "s",
		"SW_Port":                "s",
		"blocked":                "b",
		"useFixedIP":             "b",
		"firstSeen":              "s",
	},
	"Device-AP": {
		"previousStatusChange": "s",
		"groupMember":          "s",
		"model":                "s",
		"ipNumber":             "s",
		"channel_2":            "s",
		"channel_5":            "s",
		"essid_2":              "s",
		"essid_5":              "s",
		"tx_power_2":           "s",
		"tx_power_5":           "s",
		"nClients_2":           "s",
		"nClients_5":           "s",
		"radio_5":              "s",
		"radio_2":              "s",
		"unifi_id":             "s",
		"created":              "s",
		"hostname":             "s",
		"vendor":               "s",
		"upDownSetting":        "s",
		"upSince":              "s",
		"apNo":                 "s",
		"clientList_5GHz":      "s",
		"clientList_2GHz":      "s",
	},
	"gateway": {
		"previousStatusChange":  "s",
		"groupMember":           "s",
		"cpuPercent":            "s",
		"memPercent":            "s",
		"temperature":           "s",
		"temperature_CPU":       "s",
		"temperature_PHY":       "s",
		"temperature_Board_CPU": "s",
		"temperature_Board_PHY": "s",
		"model":                 "s",
		"ipNumber":              "s",
		"gateways":              "s",
		"nameservers":           "s",
		"publicIP":              "s",
		"MAClan":                "s",
		"created":               "s",
		"vendor":                "s",
		"upDownSetting":         "s",
		"upSince":               "s",
		"wan":                   "s",
		"wanPingTime":           "s",
		"wanLatency":            "s",
		"wanDownload":           "s",
		"wanUpload":             "s",
		"wanSpeedTest":          "s",
		"wanUpTime":             "s",
		"MACwan2":               "s",
		"wan2":                  "s",
		"wan2PingTime":          "s",
		"wan2Latency":           "s",
		"wan2Download":          "s",
		"wan2Upload":            "s",
		"wan2SpeedTest":         "s",
		"wan2UpTime":            "s",
		"wan2Gateways":          "s",
		"wan2Nameservers":       "s",
		"wan2PublicIP":          "s",
		"wanSetup":              "s",
		# WAN ethernet link (negotiated speed of the uplink port, from the controller port_table)
		"wanLinkPort":           "s",
		"wanLinkSpeed":          "i",
		"wanLinkSpeedMax":       "i",
		"wanLinkStatus":         "s",
	},
	"neighbor": {
		"groupMember":          "s",
		"channel":              "s",
		"essid":                "s",
		"Signal_at_APs":        "s",
		"model":                "s",
		"adhoc":                "s",
		"created":              "s",
		"previousStatusChange": "s",
		"vendor":               "s",
		"upDownSetting":        "s",
	},
	"camera": {
		"groupMember":      "s",
		"eventNumber":      "s",
		"lastEventStart":   "s",
		"lastEventStop":    "s",
		"lastEventLength":  "n",
		"ip":               "s",
		"nameOnNVR":        "s",
		"uuid":             "s",
		"apiKey":           "s",
		"eventJpeg":        "s",
	},
	"camera_protect": {
		"groupMember":      "s",
		"eventNumber":                     "s",
		"eventStart":                      "s",
		"eventEnd":                        "s",
		"eventType":                       "s",
		"eventLength":                     "n",
		"ip":                              "s",
		"id":                              "s",
		"lcdMessage":                      "s",
		"name":                            "s",
		"type":                            "s",
		"connectedSince":                  "s",
		"lastSeen":                        "s",
		"lastRing":                        "s",
		"wifiSignalStrength":              "s",
		"wifiSignalQuality":               "s",
		"wifiLinkSpeed":                   "s",
		"wifiChannel":                     "s",
		"lastSmartDetectType":             "s",
		"lastSmartDetectConfidence":       "s",
		"lastSmartDetectZone":             "s",
		"lastSmartDetectAt":               "s",
		"firmwareVersion":                 "s",
		"isAdopted":                       "b",
		"isConnected":                     "b",
		"isManaged":                       "b",
		"isLedEnabled":                    "b",
		"isExternalIrEnabled":             "b",
		"icrSensitivity":                  "s",
		"irLedMode":                       "s",
		"irLedLevel":                      "n",
		"isDark":                          "b",
		"isMicEnabled":                    "b",
		"micVolume":                       "n",
		"zoomPosition":                    "n",
		"dZoomCenterX":                    "n",
		"dZoomCenterY":                    "n",
		"hasSpeaker":                      "b",
		"isSpeakerEnabled":                "b",
		"speakerVolume":                   "n",
		"areSystemSoundsEnabled":          "b",
		"motionRecordingMode":             "s",
		"motionMinEventTrigger":           "s",
		"smartDetect":                     "s",
		"motionPostPaddingSecs":           "s",
		"motionPrePaddingSecs":            "s",
		"motionEndEventDelay":             "s",
		"motionSuppressIlluminationSurge": "s",
		"motionAlgorithm":                 "s",
		"motionUseNewAlgorithm":           "s",
		"eventJpeg":                       "s",
		"created":                         "s",
	},
	"system_protect": {
		"groupMember":      "s",
		"ipNumber":         "s",
		"created":          "s",
		"upSince":          "s",
		"disk_total":       "s",
		"disk_used":        "s",
		"disk_free":        "s",
		"memory_total":     "s",
		"memory_used":      "s",
		"memory_free":      "s",
		"numberOfCameras":  "n",
		"lastCameraEvent":  "s",
		"cpu_temp":         "s",
		"cpu_load":         "s",
	},
	"system_controller": {
		"groupMember":      "s",
		"ipNumber":         "s",
		"created":          "s",
		"upSince":          "s",
		"disk_total":       "s",
		"disk_used":        "s",
		"disk_free":        "s",
		"memory_total":     "s",
		"memory_used":      "s",
		"memory_free":      "s",
		"cpu_temp":         "s",
		"cpu_load":         "s",
	},
}
K_UNIFI_DYNAMIC_TYPES = set(K_UNIFI_TYPE_STATES) | K_UNIFI_SWITCH_TYPES

# ---- shared ConfigUI: group-membership fields, injected into every device type by getDeviceConfigUiXml ----
# ---- shared ConfigUI: per-device debug checkbox, injected at the very end of every ConfigUI ----
_DEBUG_FIELD_XML = '<Field id="unifi-sep-debug" type="separator"/><Field id="debugDev" type="checkbox" defaultValue="false"><Label>log debug msg from this device to plugin.log</Label></Field>'

_GROUP_FIELDS_XML = (
	'<Field id="unifi-sep-groups" type="separator"/>'
	'<Field id="Group0" type="checkbox" defaultValue="false"><Label>Member of group0:</Label></Field>'
	'<Field id="Gtext0" type="textfield" defaultValue="0" readOnly="yes"><Label>Name:</Label></Field>'
	'<Field id="Group1" type="checkbox" defaultValue="false"><Label>Member of group1:</Label></Field>'
	'<Field id="Gtext1" type="textfield" defaultValue="1" readOnly="yes"><Label>Name:</Label></Field>'
	'<Field id="Group2" type="checkbox" defaultValue="false"><Label>Member of group2:</Label></Field>'
	'<Field id="Gtext2" type="textfield" defaultValue="2" readOnly="yes"><Label>Name:</Label></Field>'
	'<Field id="Group3" type="checkbox" defaultValue="false"><Label>Member of group3:</Label></Field>'
	'<Field id="Gtext3" type="textfield" defaultValue="3" readOnly="yes"><Label>Name:</Label></Field>'
	'<Field id="Group4" type="checkbox" defaultValue="false"><Label>Member of group4:</Label></Field>'
	'<Field id="Gtext4" type="textfield" defaultValue="4" readOnly="yes"><Label>Name:</Label></Field>'
	'<Field id="Group5" type="checkbox" defaultValue="false"><Label>Member of group5:</Label></Field>'
	'<Field id="Gtext5" type="textfield" defaultValue="5" readOnly="yes"><Label>Name:</Label></Field>'
	'<Field id="Group6" type="checkbox" defaultValue="false"><Label>Member of group6:</Label></Field>'
	'<Field id="Gtext6" type="textfield" defaultValue="6" readOnly="yes"><Label>Name:</Label></Field>'
	'<Field id="Group7" type="checkbox" defaultValue="false"><Label>Member of group7:</Label></Field>'
	'<Field id="Gtext7" type="textfield" defaultValue="7" readOnly="yes"><Label>Name:</Label></Field>'
)


# ---- daily min/max/average and change/trend tracking for numeric sensor states ----
# per deviceTypeId: the base states that can carry the derived states below. adding a state
# here (plus its value write in plugin.py) is all it takes to make it trackable.
K_MINMAX_TRACKED = {
	"sensor_protect_allInOne":      ("temperature", "humidity", "light"),
	"sensor_protect_environmental": ("temperature", "humidity"),
	"sensor_protect_smoke_co":      ("temperature", "humidity"),
	"sensor_protect_airquality":    ("temperature", "humidity", "voc", "co2"),
}
# every base state name that appears in any tracked tuple - quick reject in addToStatesUpdateList
K_MINMAX_ALLKEYS = set()
for _states in K_MINMAX_TRACKED.values():
	K_MINMAX_ALLKEYS.update(_states)

# derived-state suffix groups; two INDEPENDENT groups, each owned by its own checkbox in device config:
#   "minMaxEnable_<state>"  -> Min/Max Today/Yesterday + ..At timestamps + Ave + Measurements
#   "enableChanges_<state>" -> ChangeMinutes../ChangeHours.. and the Trend derived from them
K_MINMAX_SUFFIXES = (
	("_MinToday","n"), ("_MinTodayAt","s"), ("_MaxToday","n"), ("_MaxTodayAt","s"),
	("_MinYesterday","n"), ("_MinYesterdayAt","s"), ("_MaxYesterday","n"), ("_MaxYesterdayAt","s"),
	("_AveToday","n"), ("_AveYesterday","n"), ("_MeasurementsToday","i"), ("_MeasurementsYesterday","i"),
)
K_CHANGES_SUFFIXES = (
	("_ChangeMinutes10","n"), ("_ChangeMinutes20","n"), ("_ChangeHours01","n"), ("_ChangeHours02","n"),
	("_ChangeHours06","n"), ("_ChangeHours12","n"), ("_ChangeHours24","n"), ("_Trend","s"),
)

def _minMaxConfigFieldsXml(typeId):
	"""ConfigUI <Field> block for one device type: per tracked state the two checkboxes
	(min/max/average + change/trend) and the trend menus bound to the changes checkbox."""
	if typeId not in K_MINMAX_TRACKED: return ""
	out = '<Field id="unifi-sep-minmax" type="separator"/>'
	for st in K_MINMAX_TRACKED[typeId]:
		out += '<Field id="minMaxEnable_'+st+'" type="checkbox" defaultValue="false"><Label>Enable '+st+' min/max/average states</Label></Field>'
		out += '<Field id="ignoreZerominMaxEnable_'+st+'" type="checkbox" defaultValue="false" visibleBindingId="minMaxEnable_'+st+'" visibleBindingValue="true"><Label> ... ignore 0</Label></Field>'
		out += '<Field id="enableChanges_'+st+'" type="checkbox" defaultValue="false"><Label>Enable '+st+' change/trend states</Label></Field>'
		out += '<Field id="trendTimeDeltaMin_'+st+'" type="menu" defaultValue="600" visibleBindingId="enableChanges_'+st+'" visibleBindingValue="true"><Label> ... trend min delta time:</Label>'
		out += '<List>'
		out += '<Option value="300"   > 5 minutes</Option>'
		out += '<Option value="600"   > 10 minutes</Option>'
		out += '<Option value="1200"  > 20 minutes</Option>'
		out += '<Option value="3600"  > 1 hour</Option>'
		out += '<Option value="7200"  > 2 hour</Option>'
		out += '<Option value="21600" > 6 hour</Option>'
		out += '<Option value="43200" > 12 hour</Option>'
		out += '<Option value="86400" > 24 hour</Option>'
		out += '</List></Field>'
		out += '<Field id="trendDelta_'+st+'" type="menu" defaultValue="100" visibleBindingId="enableChanges_'+st+'" visibleBindingValue="true"><Label> ... trend min delta value:</Label>'
		out += '<List>'
		out += '<Option value="10"    > 0.1  %</Option>'
		out += '<Option value="25"    > 0.25 %</Option>'
		out += '<Option value="50"    > 0.5 %</Option>'
		out += '<Option value="100"   > 1 %</Option>'
		out += '<Option value="150"   > 1.5 %</Option>'
		out += '<Option value="200"   > 2 %</Option>'
		out += '<Option value="300"   > 3 %</Option>'
		out += '<Option value="500"   > 5 %</Option>'
		out += '<Option value="1000"  > 10 %</Option>'
		out += '</List></Field>'
	return out
