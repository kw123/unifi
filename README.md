# uniFiAP — Indigo Plugin

Integrates a UniFi network installation with the [Indigo](https://www.indigodomo.com) home-automation platform. Monitors UniFi access points, switches, gateways, cameras, and UniFi Protect sensors/relays; exposes device states as Indigo sensor/relay devices; and provides actions for controlling ports, cameras, clients, and relay outputs.

Plugin ID: `com.karlwachs.uniFiAP`  
Version: 2026.57.446  
Indigo Server API: 3.0

---

## Requirements

- Indigo 2022.1 or later
- UniFi Network controller (self-hosted or UDM/UDM-Pro)
- UniFi Protect (optional — for cameras and USL sensors/relays)
- SSH access enabled on switches for port power-cycle actions
- Python 3 (bundled with Indigo)

---

## Device Types

### Network Infrastructure

- **UniFi (generic)** — catch-all UniFi device; reports status, firmware, MAC, IP, uptime
- **Access Point (Device-AP)** — per-AP device with signal stats, client counts, uptime, LED state, radio band info
- **Switch (Device-SW-4 through Device-SW-54)** — per-port PoE/power state, traffic counters, uptime; variants for 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 48, 50, 52 and 54-port models. The port states (`port_01`…`port_NN`) and the size-dependent extras (temperature on 10-port and up, fan level on 12 and up, VLAN on 52 and up) are generated per model, so adding a new switch size needs no per-port editing
- **Gateway** — WAN/LAN stats, uptime, CPU/memory, DHCP leases. With the WAN link watch switched on (plugin config, off by default) it also reports the negotiated speed of the WAN port: `wanLinkSpeed` (Mbit as an integer, so it can be used in triggers and plotted), `wanLinkSpeedMax` (what the port itself can do), `wanLinkPort` (e.g. `Port 5 / eth4 (2500 Mbit)`) and `wanLinkStatus` (`ok 1000 Mbit` / `DEGRADED 100 of 1000 Mbit` / `link down` / `no uplink port` / `off` when the watch is disabled) — see [WAN Port Link Speed Watch](#wan-port-link-speed-watch)
- **Neighbor** — neighboring UniFi devices discovered by the controller
- **SuperLink Gateway** — dedicated device for the UniFi SuperLink gateway
- **Controller System** — overall controller health and version info
- **Protect System** — UniFi Protect NVR/application status and version; CPU temperature/load, memory, and disk usage update live from the Protect WebSocket (no SSH poll needed)

> **Note:** every device type in this plugin is created automatically by the plugin itself — none of them can be added manually via Indigo's "New Device" dialog. Switches and APs, in particular, can either be created automatically by enabling **Auto-detect** in the plugin configuration's Switch/AP sections (the plugin reads the controller's device list and creates matching devices itself), or — when auto-detect is off — by entering the switch/AP IP addresses in the plugin configuration's per-slot fields, after which the plugin creates and matches the device the next time it reads the controller. See [Plugin Configuration](#plugin-configuration) below.

### Cameras

- **Camera (Protect)** — camera connected via UniFi Protect; reports connection state, recording mode, firmware, and Protect-specific stats. WiFi cameras additionally report `wifiSignalStrength` (dBm), `wifiSignalQuality` (%), `wifiLinkSpeed` (Mbps), and `wifiChannel`. Smart detections fill `lastSmartDetectType` (person/vehicle/…), `lastSmartDetectConfidence` (%), `lastSmartDetectZone`, and `lastSmartDetectAt`
- **Camera (legacy)** — camera managed directly by the network controller

### UniFi Protect Sensors (USL family)

Each sensor device reports `status`, `isConnected`, `isAdopted`, `MAC`, `firmwareVersion`, `lastSeen`, `created`, and sensor-specific states. The device-state column in Indigo shows the `displayStatus` text with a change-stamped timestamp, e.g. `21.5ºC  26-07-03 11:42:00`, `GLASS BREAK!  26-07-03 …`, `open  26-07-03 …` — the trailing date-time updates only when the state actually changes, not on every poll:

- **All-In-One Sensor (UP-Sense)** — motion, contact, temperature, humidity, ambient light (`light` state), battery, `sensorButtonPressedAt` / `sensorButtonPressedAt_Last` (datetime of last/previous function-button press). Water leak: `waterDetected`, `waterDetectedAt`, `waterDetectedAt_Last`, `waterDetectedEnabled`. When leak detection is enabled (exclusive mode on this sensor) the device behaves like a water sensor: onOffState on = wet, display shows dry/LEAK!
- **Entry Sensor (USL-Entry)** — door/window contact open/closed state, battery
- **Motion Sensor (USL-Motion)** — motion detected state, battery
- **Environmental Sensor (USL-Environmental)** — temperature, humidity, battery, `sensorButtonPressedAt`. Water leak: `waterDetected` + timestamps (combined — Protect does not report which probe fired) and per-probe enable flags `waterDetectedInternalEnabled` (built-in contacts) / `waterDetectedExternalEnabled` (wired probe)
- **Glass Break Sensor (USL-Glassbreak)** — glass break detection (`glassBreakAt` / `glassBreakAt_Last`), battery, `sensorButtonPressedAt`
- **Remote Key Fob (USL-Fob)** — button press events (`buttonPressed` always as "number/name", e.g. `2/night`; display selectable as names or numbers, Auto follows the Protect "Button Labels" setting), battery
- **Smoke / CO Alarm (sensor_protect_smoke_co)** — `smokeAlarm`, `coAlarm`, `smokeValue`, `coValue`, `alarmEnabled`, `batteryLow`, `endOfLife`, sensor-fault and tamper states + alarm-onset timestamps; onOffState/display trip on smoke or CO (`SMOKE+CO!` / `SMOKE!` / `CO!` / `ok`). Future CO-only models (UP-CO / USL-CO variants) map onto this same type
- **Vape / Air Quality (UP-AirQuality)** — `aqi`, `vapeIndex`/`vapeDetected`, `co2`, `voc`/`nox`/`tvoc`, `pm1`/`pm2.5`/`pm4`/`pm10`, temperature, humidity; PoE powered; display selectable (AQI / vape / CO2 / temp+humidity)

#### On/Off State of the Boolean Sensors

For the sensors that trip — Entry, Motion, Glass Break, Siren, Smoke/CO and the vape detection of the Air Quality sensor — `onOffState` is **on when the sensor is tripped** (door open, motion, glass break, siren active, alarm, vape) and off when it is idle. Two independent options on the device's Edit Device dialog change that:

- **What to show in device display → `… (onOffState inverted)`** — inverts `onOffState`: on = idle, e.g. on = door **closed** for an Entry sensor. The `onOffState` text then reads the inverted word too. Entry sensors that were set to the earlier entry-only option keep working without being re-saved
- **Icon colour** — `red / green` (default: red = tripped, green = idle) or `green / red`. Independent of the option above, so wording and icon colour can be inverted separately

`onOffState`, its text and the icon are updated straight from the live Protect WebSocket message, not only on the next poll, so an open/close shows up immediately. The word pair and trigger state of each type are defined once in `kSensorOnOff` in `plugin.py`.

#### Min/Max/Average and Change/Trend States

The numeric sensor states can optionally keep their own history (same scheme as the homematic and piBeacon plugins). Tracked are `temperature` and `humidity` on the All-In-One, Environmental and Smoke/CO sensors, `light` on the All-In-One, and `temperature`, `humidity`, `voc` and `co2` on the Air Quality sensor. Each tracked state has **two independent checkboxes** on the device's own Edit Device dialog, both off by default — nothing changes for an existing device until one is ticked:

- **Enable `<state>` min/max/average states** — adds `_MinToday`/`_MaxToday` and `_MinYesterday`/`_MaxYesterday` with matching `…At` timestamps, `_AveToday`/`_AveYesterday`, and the `_MeasurementsToday`/`_MeasurementsYesterday` counters. A sub-option *ignore 0* drops zero readings
- **Enable `<state>` change/trend states** — adds `_ChangeMinutes10`/`_ChangeMinutes20` and `_ChangeHours01`/`02`/`06`/`12`/`24` (the difference between now and that long ago) plus a `_Trend` state shown as arrows: `^` to `^^^^` rising, `v` to `vvvv` falling, `==` flat. Two menus set the time window the trend looks back over and the percentage step it reacts to

The daily average is **time-weighted**: a reading counts by how long it stayed valid, not by how often it arrived, so a chatty sensor does not outweigh quiet periods. History and accumulators persist in `changedValues.json` in the prefs dir (written every 10 minutes and at plugin stop) and roll over at midnight. The derived states are generated per device from `deviceTables.py` (`K_MINMAX_TRACKED` plus the suffix tables), so tracking another state is one table entry.

### Protect Relay (USL-Relay)

The relay creates three Indigo devices:

- **Protect Relay (relay_protect)** — parent device for output 1; states include `onOffState`, `lastCommand`, `status`, `isConnected`, `MAC`, `id`, `firmwareVersion`, `btSignal`, `lastSeen`, `created`
- **Protect Relay Output 2 (relay_protect_output2)** — independent on/off control for output 2; states include `onOffState`, `lastCommand`, `MAC`, `created` (only the parent device carries `status`)
- **Protect Relay Inputs (relay_protect_input)** — ONE combined device for both dry-contact inputs: `input1State`/`input2State`, per-channel `input1At`/`input2At` (+ `_Last`) and `input1PressType`/`input2PressType`, plus `sensorButtonPressedAt`. A device setting selects which channel drives `onOffState`/display (shown as e.g. `in1:ON  26-07-03 …`)

#### Relay Input Behaviour

Input events are delivered exclusively via the UniFi Protect WebSocket (`sensorButtonPressed`). Each press sets the channel's `input{n}State` to `true`, records the press type (`press`, `longPress`, or `doublePress`) in `input{n}PressType`, and stores a timestamp in `input{n}At` (previous press in `input{n}At_Last`). The state automatically resets to `false` after ~3 seconds, creating a clean on→off pulse suitable for Indigo triggers.

#### Relay Output Behaviour

Outputs are controlled via the UniFi Protect Integration API (`/proxy/protect/integration/v1/relays`). On success, `onOffState` is updated and `lastCommand` is set to e.g. `on sent 2026-07-03 17:42:11`. The timestamp is captured immediately before the API call so it reflects when the command was sent, not when the response arrived.

### FloodLight (UP FloodLight)

- **Protect FloodLight (light_protect)** — Indigo **dimmer** device: the six LED levels map proportionally onto the percent scale (level×100/6 → 17/33/50/67/83/100 %, 0 = off; any percent set rounds to the nearest level, Brighten/Dim steps one level). `onOffState`/`brightnessLevel` follow the physical light (`isLightOn`, including motion-triggered activations); Turn On/Off/Set Brightness control the light via the internal Protect API (`lightOnSettings.isLedForceOn` / `lightDeviceSettings.ledLevel`; off releases it back to its configured mode). States: `motionDetected` (live PIR — usable as an Indigo motion trigger even when the light mode is off), `lastMotionAt`/`_Last`, `isDark`, `ledLevel` (1–6), `lightMode` (off/motion/always), `pirSensitivity`/`pirDuration`/`luxSensitivity`, `isLightForceOn`, plus connection/firmware/ip/lastSeen. Also controllable via the "FLOODLIGHT Protect set light ON / off" action and menu item

### Siren

- **Protect Siren (USL-Siren)** — siren/alarm device; on/off state and volume level

---

## Plugin Configuration

Open the plugin's configuration dialog from Indigo's Plugins menu.

### Quick Setup

The fastest way to configure the plugin: open the **QUICK SETUP** section at the top of the dialog, pick what your controller device has built in from one menu —

- controller hosted on Mac/rPi (no Protect, no events)
- CloudKey (controller only, no built-in switch/AP)
- controller w. built-in switch / w. built-in switch + AP
- UDM-Pro / UCG (built-in gateway + switch) / UDM (gateway + switch + AP)

— enter the few required parameters (controller IP, web login, SSH login, UDM unix login, and optionally Protect IP/login/API key with *with cameras* / *with sensors* checkboxes), then press **execute**. This fills in all the regular configuration sections below; nothing is saved until you press SAVE, so everything can be reviewed and adjusted first. Notes:

- The menu describes **only the controller box itself**. External switches/APs are found by auto-detect and are never changed by the wizard; the controller's own built-in switch/AP use the reserved slots SW#13/AP#20, filled automatically
- The wizard resets on every dialog open and prefills its fields from the current settings, so nothing has to be retyped; the result line shows how many parameters actually changed (details in the Indigo log)
- *with cameras* / *with sensors* map to the prefs `protectCreateCameras` / `protectCreateSensors` (both default on) which gate the creation of **new** Protect camera resp. sensor/relay/speaker/SuperLink devices — existing devices keep updating either way

### Key settings

- **Controller address and credentials** — IP/hostname, username, password for the UniFi Network controller
- **Switch / AP auto-detect** — optional, off by default, found in the Switch and AP sections respectively. When on, the plugin reads the controller's device list and automatically creates and fills in the matching Indigo switch/AP devices, instead of requiring the IP to be entered manually in a slot below. When off, switches/APs must be added by entering their IP in a free slot in the Switch/AP section (the device itself is still created automatically the next time the controller is read — manual creation via Indigo's "New Device" dialog is not available for these types). Either way, already-configured devices keep being matched and updated automatically. A small number of switch/AP slots are reserved internally for UDM-integrated controllers and are never used by auto-detect or available for manual entry
- **Protect API key** — X-API-KEY for the UniFi Protect Integration API (required for relay control)
- **Poll intervals** — how often to refresh AP, switch, gateway, camera, and sensor states
- **WebSocket** — the plugin maintains a persistent WebSocket connection to UniFi Protect for real-time sensor and relay-input events
- **Controller event tracking** — opens a second WebSocket to the Network controller's event stream (client connect/disconnect/roam, security alerts, admin actions). Buffers the last 500 events, enables the live monitor and print-events menu. Can be toggled at runtime without a plugin restart
- **Use controller WS events for client presence detection** — optional (visible only when event tracking is on): feeds controller WiFi events into client presence tracking instead of the SSH log listener. WARNING: adds roughly 10 seconds of latency vs the SSH listener; only useful when direct SSH access to the APs is unavailable. Changing this setting restarts the plugin
- **Debug areas** — individual checkboxes to enable verbose logging per subsystem (AP, Switch, Gateway, Protect, WebSocket, etc.). Two of them append raw controller resp. Protect WebSocket events to `EVENTS-controllerWS.json` / `EVENTS-protectWS.json` in the prefs dir (both off by default). The files start with `[` and every line ends with `,` — append `]` to get valid JSON. At 50 MB the oldest half is dropped automatically. Per-device debug logging (and, for switches, the mini-switch/no-SSH override) is configured on the individual switch/AP device's own Edit Device dialog, not here — see below
- **SSH settings** — credentials and port for switch port power-cycle actions that use SSH
- **WAN port link speed watch** *(Gateway section, off by default)* — watches the negotiated ethernet speed of the gateway's WAN port and optionally resets it when it drops; see [WAN Port Link Speed Watch](#wan-port-link-speed-watch) below

### Event log when the UniFi gateway is away

When the gateway or controller goes away — typically its automatic update or nightly jobs around 03:30 — every listener, login and WebSocket path would log its own error. Instead:

- The **first** warning or error from the UniFi connection code is shown in the Indigo event log with `[UniFi connection messages muted for 5 min]` appended, and further connection messages are kept out of the event log for 5 minutes. Other messages (sensor events, leak warnings, …) are not affected, and the plugin's own log file still gets everything
- When listener data from that IP arrives again the plugin logs `UniFi <ip> recovered after <n> min, <n> connection messages muted` and ends the mute. If the device is still down after 5 minutes, the next error is shown and mutes again. Devices without an SSH listener (e.g. a separate Protect controller) get no recovered line — their mute simply runs out
- A single `closed by remote host` (restart code 1) is logged at debug level only; a second one from the same device within 10 minutes is logged normally
- The listener restart messages log only the first 150 characters of the data received, with its total length, instead of the whole device dict
- The `reflector` messages in the same time window come from Indigo itself, not from this plugin

---

### WAN Port Link Speed Watch

Some modems renegotiate the WAN link at a lower speed after a link flap (typically 1000 → 100 Mbit) and stay there until the port is reset. This watch, in the plugin configuration's **Gateway** section and off by default, makes that visible.

- The negotiated speed is read from the controller's own `port_table` on every gateway dict read — **no SSH, no extra polling, no launchd job**. The WAN port is identified by its `is_uplink` flag, so no interface name has to be entered and it works on any gateway model regardless of which `ethN` carries the WAN
- **Expected minimum WAN link speed** (default 1000 Mbit) — the speed below which the link counts as degraded. Pick what the ISP link actually runs at, not what the port could do: `auto` compares against the port's own maximum (derived from its media type, e.g. `2.5GE` → 2500), which on a 2.5GE WAN port feeding a 1 Gbit modem is a permanent false alarm. A degraded link is logged as a warning at most once an hour, so a port that stays degraded does not flood the log
- **Renegotiate the port automatically when degraded** (off by default, with a minimum retry interval, default 15 min) — SSHes to the gateway and resets the WAN port with `ethtool -r <if>`, falling back to `ip link set <if> down; sleep 5; up`. It uses the plugin's existing expect script and the unix SSH credentials already configured for the UniFi devices, so nothing has to be installed on the gateway and no SSH key has to be deployed (a key in `authorized_keys` would be lost on a firmware update). **CAREFUL: this interrupts the internet connection for a few seconds.** Without it, a degraded link is only reported in the device states and the log
- Debug area **(4.4)** traces the whole `port_table` per read (ifname / name / `is_uplink` / up / media / speed / duplex, so a missing or wrong `is_uplink` flag is visible), the speed comparison and its verdict, the auto-fix cooldown, and the renegotiation command with its output — the last without having to switch on the noisy general Expect areas
- The port can also be reset by hand at any time, independent of the watch, via the menu item or the action (below)

> **Not yet verified on real hardware:** whether UCG/UDM firmware actually ships `ethtool`, and whether a software port reset is equivalent to physically unplugging the cable for 10 s (which is the workaround known to work). The monitoring half needs no SSH at all and is safe to switch on by itself; the auto-fix is deliberately off by default until that is confirmed. A link that degrades every couple of days is usually a marginal cable pair (100 Mbit needs only 2 of the 4) or an EEE negotiation problem — a new Cat6 cable and disabling EEE on the modem are the real fixes; this watch is monitoring plus a workaround.

---

### Per-device settings

**Every** device's own Edit Device dialog (not the plugin configuration) offers:

- **Member of group0…7** — group membership, with the group names shown next to each checkbox (names are set in the plugin configuration). Group membership drives the home/away presence groups and is reflected in the device's `groupMember` state. Child devices without an up/down status (relay inputs/outputs) can be members but are not counted for presence
- **log debug msg from this device to plugin.log** — enables verbose logging for just this one device, in every processing area that handles it (dict reads, status logic, controller info, …)

Switch and AP devices additionally have:
- **Mini-switch (no SSH) override** *(switches only)* — `Auto` (default) follows the controller's own report of whether the switch supports SSH; `Force: Mini-switch (no SSH)` and `Force: Regular switch (SSH-capable)` override that detection for this device. The dialog also shows a read-only label with the currently auto-detected status, so it's easy to tell what `Auto` is currently resolving to before overriding it. Mini/flex switches that don't support SSH get their port and client data from the controller's own API instead of an SSH session; this is normally detected automatically and the override is rarely needed

The boolean Protect sensors additionally have the inverted-onOffState display option and the icon colour menu described under [On/Off State of the Boolean Sensors](#onoff-state-of-the-boolean-sensors).

Every device with statistics states also has **statistics states into the SQL logger** — `default (as set in plugin config)` / `not written` / `written`. Statistics states are the min / max / average today / yesterday (+ `…At`), measurement counters, today / yesterday / day-x, this / last week, month, year and switch-point states. They are added to or taken out of the device's `sqlLoggerIgnoreStates`; other entries there stay untouched. The plugin-wide default is the checkbox **do not write statistics states into the SQL logger** in the plugin configuration (off by default, i.e. no change).

The Protect sensors with numeric states (All-In-One, Environmental, Smoke/CO, Air Quality) additionally have the per-state min/max/average and change/trend checkboxes described under [Min/Max/Average and Change/Trend States](#minmaxaverage-and-changetrend-states).

---

## Actions

### Camera Actions

- **LED set ON/OFF** — turn the camera LED on or off
- **Speaker volume** — set the camera speaker volume (0–100)
- **IR ON/OFF** — enable or disable infrared night vision
- **Set Contrast / Brightness / Saturation / Sharpness / Hue** — adjust image settings
- **Mic volume** — set microphone sensitivity
- **Record ON/OFF** — start or stop recording
- **Get Snapshot** — fetch a still image from the camera
- **General command** — send an arbitrary camera command
- **Pan/Tilt command** — PTZ pan and tilt
- **Zoom command** — PTZ zoom
- **Pan/Tilt/Zoom to preset** — move to a named PTZ preset position

### Network Client Actions

- **Power-cycle a switch port (SSH)** — cycle PoE power on a specific switch port using SSH
- **Power-cycle a switch port (controller)** — same via the controller API
- **Reconnect a WiFi client** — kick a client off the network so it reconnects
- **Block a client** — block a MAC address at the controller
- **Unblock a client** — remove a MAC block

### AP / Device Actions

- **Disable a UniFi AP** — take an AP offline
- **Enable a UniFi AP** — bring an AP back online
- **Reboot a UniFi device** — send a reboot command
- **LED: switch all AP LEDs on** — turn on LEDs for all access points
- **LED: switch all AP LEDs off** — turn off LEDs for all access points
- **LED: blink one AP LED on/off** — blink a specific AP's LED

### Gateway Actions

- **GATEWAY renegotiate WAN port link** — reset/renegotiate the gateway's WAN (uplink) port over SSH (`ethtool -r`, falling back to `ip link` down/up), independent of the WAN link watch option. Interrupts the internet connection for a few seconds

### Relay Actions

- **RELAY Protect set output 1/2** — set a relay output to on or off

### Suspend/Activate

- **Suspend a system device** — mark a device as suspended in the plugin (plugin takes no further action for it)
- **Unsuspend a system device** — return it to normal polling

---

## Menu Items

Available under Plugins → uniFiAP:

- **Print parameters to log** — dump current plugin configuration values to the Indigo log
- **Print & get info from controller DB / UGA** — query and print raw controller database records
- **Print communication and processing stats** — show timing and throughput metrics
- **Track info for specific MAC** — log all activity for a given MAC address
- **(Un)Ignore clients** — add or remove clients from the ignore list
- **Reset SSH known-hosts file** — clear the SSH known-hosts cache
- **Listeners — Manage** — configure event listeners
- **GATEWAY … renegotiate WAN port** — reset the gateway's WAN (uplink) port by hand; menu version of the action above
- **Groups — Manage device types / individual devices** — assign devices to polling groups
- **Protect — Info, settings, actions** — Protect-specific diagnostics and commands
- **Protect cameras — send test commands** — send test commands to Protect cameras
- **Copy controller backup files** — copy controller backups to the Indigo preferences directory
- **Set all UniFi device props** — bulk-update plugin properties across devices
- **Power-cycle a switch port** — interactive menu version of the port-cycle action
- **Reconnect a WiFi client** — menu version of the kick action
- **(Un)Block a client** — menu version of the block/unblock action
- **Enable/disable/reboot a UniFi device** — menu version of the device control action
- **Suspend/Activate a system device** — menu version of the suspend action
- **Set AP LEDs on/off** — menu version of the LED action

---

## State Lifecycle Notes

- **`lastSeen`** — updated every poll cycle from the controller; reflects the controller's own last-seen timestamp, not the plugin's
- **`isConnected`** — USL-Relay uses Bluetooth; Protect may return `null` for this field. The plugin treats `null` as `true` (connected) since adoption implies connectivity for Bluetooth devices
- **`input{n}At` / `input{n}At_Last`** — the relay inputs device records the timestamp of the most recent press per channel, and the previous one in `_Last`
- **`wanLink*`** — the four gateway WAN states always exist (state existence is keyed on `deviceTypeId` only), but they are only filled while the WAN link watch is enabled; with it off `wanLinkStatus` reads `off`. When on they refresh on every gateway dict read, straight from the controller's `port_table`
- **`lastCommand`** — relay output devices only; format `"on sent YYYY-MM-DD HH:MM:SS"` or `"off sent …"`
- **`created`** — set once when the device is created and then kept. Protect sensors, relays (and their input/output devices), SuperLink gateways and speakers used to rewrite it on every poll; devices created before that fix keep the time of their last poll before it
- **`memory_free` / `memory_used` / `cpu_temp` / `cpu_load`** (`Unifi_System_Protect`, `Unifi_System_Controller`) — only written when the value really moved, so they do not update on every read: memory by more than 10 %, `cpu_temp` by 3 ºC or more, `cpu_load` by 5 points or more. Only the numbers are compared (`62ºC` from SSH and `62.5` from the WebSocket count as the same); a non-numeric value is always written. The limits are `kSmallChangeFraction` / `kSmallChangeSteps` at the top of `plugin.py`

### WiFi Client Signal States (UniFi devices)

Read from the AP's per-client station table every dict poll cycle:

- **`signalWiFi`** — absolute received signal strength in dBm (e.g. `-41`); closer to 0 is stronger, below about -75 dBm connections get flaky
- **`noiseWiFi`** — noise floor in dBm (typically around `-95`)
- **`signal2NoiseWiFi`** — signal-to-noise ratio in dB (Ubiquiti calls this "rssi"): `signalWiFi - noiseWiFi`. Higher is better: above 25 dB solid, 15–25 dB usable, below 15 dB problems. Usually the most meaningful quality number since it accounts for the local noise floor
- **`satisfactionWiFi`** — UniFi's own 0–100 connection quality score for the client
- **`channelWiFi`** — actual WiFi channel the client is on (e.g. `11`, `44`)
- **`stateWiFi`** — the AP driver's per-station flags as an 8-bit binary string (e.g. `00011111`, bit 0 rightmost). Bit meanings (Atheros/madwifi node flags, not officially documented by Ubiquiti):
  - bit 0 (0x01) — authenticated
  - bit 1 (0x02) — QoS/WMM negotiated
  - bit 2 (0x04) — ERP / 802.11g protection (set on 2.4 GHz clients only)
  - bit 3 (0x08) — U-APSD power-save capable
  - bit 4 (0x10) — power management currently active (client is dozing; matches the AP's `state_pwrmgt` field)
  - Example: `00011111` = authenticated 2.4 GHz client with WMM, currently power-saving (typical IoT device napping between beacons)

---

## Architecture Notes

- **Device definitions are generated, not hand-written.** `deviceTables.py` is the single source of truth for every device type:
  - **States** — `getDeviceStateList()` builds each device's state list at runtime from `deviceTypeId`-keyed tables (a shared common set + named layers + a per-type set). All `<States>` blocks in `Devices.xml` are empty. Existence is keyed on `deviceTypeId` only — known at plugin start, before any controller/Protect data is read — so a device's states are correct from the first call and never fluctuate with what a poll happens to contain
  - **Properties** — the Indigo capability flags (`SupportsOnState`, `SupportsSensorValue`, `AllowOnStateChange`, `SupportsBatteryLevel`) and the `is*` type markers come from `deviceProps()`, injected when a device is created and enforced at device start
  - **ConfigUI** — the group-membership fields and the per-device debug checkbox are appended by a `getDeviceConfigUiXml()` override, so they exist on every device without being repeated per type; only genuinely type-specific fields live in `Devices.xml`
  - Adding a state, a capability or a whole new switch size is therefore a small edit in one data file
- Communication with the UniFi Network controller uses the controller's REST API (cookie-based session auth)
- Communication with UniFi Protect uses two paths:
  - REST Integration API (`/proxy/protect/integration/v1/`) with X-API-KEY for read and write operations
  - WebSocket (`/proxy/protect/ws/updates`) for real-time events (sensor triggers, relay inputs, camera motion)
- An optional second WebSocket connects to the Network controller's event stream (`/proxy/network/wss/s/default/events`). It powers:
  - the live event monitor and print-events menu (last 500 events buffered)
  - security alerts (IPS/IDS, threats) logged as Indigo warnings with source IP, country, and signature
  - instant `blocked` state updates plus an audit log line when an admin blocks/unblocks a client
  - optional client presence detection (`EVT_WU_Connected`/`Disconnected`/`Roam`) as a replacement for the SSH log listener — slower by ~10 s, intended for setups without AP SSH access
- The gateway WAN link speed needs no transport of its own: the controller's `port_table` already carries the negotiated speed of every port including the uplink, so the watch is four state comparisons on a dict the plugin reads anyway. SSH is used only for the optional remediation
- Per-device polling runs on background threads; one thread per controller IP and device type
- Relay input events do not use polling — they arrive exclusively via WebSocket
- Sensor button presses arrive on two WebSocket paths (a `sensorButtonPressed` event and a `functionButtonPressedAt` field in sensor updates) — both update the `sensorButtonPressed` state
- Delayed state resets (e.g. relay input auto-off after 3 s) are handled by a dedicated daemon thread checking a time-stamped action queue every 0.5 s

---

## File Layout

```
uniFiAP.indigoPlugin/
  Contents/
    Info.plist                  plugin metadata and version
    Server Plugin/
      plugin.py                 main plugin code
      deviceTables.py           device states, properties and shared ConfigUI (single source of truth)
      statsSqlIgnore.py         keeps statistics states out of the SQL logger (sqlLoggerIgnoreStates)
      Devices.xml               device type definitions
      Actions.xml               action definitions
      MenuItems.xml             menu item definitions
      Events.xml                event definitions
      PluginConfig.xml          plugin preferences UI
      MAC2Vendor.py             MAC-to-vendor lookup
      *.exp                     expect scripts for SSH operations
      unifi_dpi.json            DPI application ID map
```
