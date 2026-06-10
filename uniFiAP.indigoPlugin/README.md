# uniFiAP — Indigo Plugin

Integrates a UniFi network installation with the [Indigo](https://www.indigodomo.com) home-automation platform. Monitors UniFi access points, switches, gateways, cameras, and UniFi Protect sensors/relays; exposes device states as Indigo sensor/relay devices; and provides actions for controlling ports, cameras, clients, and relay outputs.

Plugin ID: `com.karlwachs.uniFiAP`  
Version: 2026.50.436  
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
- **Switch (Device-SW-4 through Device-SW-52)** — per-port PoE/power state, traffic counters, uptime; variants for 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 18, 26, and 52-port models
- **Gateway** — WAN/LAN stats, uptime, CPU/memory, DHCP leases
- **Neighbor** — neighboring UniFi devices discovered by the controller
- **SuperLink Gateway** — dedicated device for the UniFi SuperLink gateway
- **Controller System** — overall controller health and version info
- **Protect System** — UniFi Protect NVR/application status and version; CPU temperature/load, memory, and disk usage update live from the Protect WebSocket (no SSH poll needed)

### Cameras

- **Camera (Protect)** — camera connected via UniFi Protect; reports connection state, recording mode, firmware, and Protect-specific stats. WiFi cameras additionally report `wifiSignalStrength` (dBm), `wifiSignalQuality` (%), `wifiLinkSpeed` (Mbps), and `wifiChannel`. Smart detections fill `lastSmartDetectType` (person/vehicle/…), `lastSmartDetectConfidence` (%), `lastSmartDetectZone`, and `lastSmartDetectAt`
- **Camera (legacy)** — camera managed directly by the network controller

### UniFi Protect Sensors (USL family)

Each sensor device reports `status`, `isConnected`, `isAdopted`, `MAC`, `firmwareVersion`, `lastSeen`, `created`, and sensor-specific states. The device-state column in Indigo shows the `displayStatus` text (e.g. 21.5ºC, GLASS BREAK!, OPEN):

- **All-In-One Sensor (UP-Sense)** — motion, contact, temperature, humidity, ambient light (`light` state), battery, `sensorButtonPressedAt` / `sensorButtonPressedAt_Last` (datetime of last/previous function-button press). Water leak: `waterDetected`, `waterDetectedAt`, `waterDetectedAt_Last`, `waterDetectedEnabled`. When leak detection is enabled (exclusive mode on this sensor) the device behaves like a water sensor: onOffState on = wet, display shows dry/LEAK!
- **Entry Sensor (USL-Entry)** — door/window contact open/closed state, battery
- **Motion Sensor (USL-Motion)** — motion detected state, battery
- **Environmental Sensor (USL-Environmental)** — temperature, humidity, battery, `sensorButtonPressedAt`. Water leak: `waterDetected` + timestamps (combined — Protect does not report which probe fired) and per-probe enable flags `waterDetectedInternalEnabled` (built-in contacts) / `waterDetectedExternalEnabled` (wired probe)
- **Glass Break Sensor (USL-Glassbreak)** — glass break detection (`glassBreakAt` / `glassBreakAt_Last`), battery, `sensorButtonPressedAt`
- **Remote Key Fob (USL-Fob)** — button press events, battery

### Protect Relay (USL-Relay)

The relay creates four Indigo devices:

- **Protect Relay (relay_protect)** — parent device for output 1; states include `onOffState`, `lastCommand`, `status`, `isConnected`, `MAC`, `id`, `firmwareVersion`, `btSignal`, `lastSeen`, `created`
- **Protect Relay Output 2 (relay_protect_output2)** — independent on/off control for output 2; states include `onOffState`, `lastCommand`, `MAC`, `created` (only the parent device carries `status`)
- **Protect Relay Input 1 (relay_protect_input1)** — dry-contact input 1; states include `onOffState`, `pressType`, `onAt`, `onAt_Last`, `MAC`, `created`
- **Protect Relay Input 2 (relay_protect_input2)** — dry-contact input 2; same states as input 1

#### Relay Input Behaviour

Input events are delivered exclusively via the UniFi Protect WebSocket (`sensorButtonPressed`). Each press sets `onOffState` to `true`, records the press type (`press`, `longPress`, or `doublePress`) in the `pressType` state, and stores a timestamp in `onAt`. The state automatically resets to `false` after ~3 seconds, creating a clean on→off pulse suitable for Indigo triggers. The `pressType` state can be used to differentiate trigger conditions.

#### Relay Output Behaviour

Outputs are controlled via the UniFi Protect Integration API (`/proxy/protect/integration/v1/relays`). On success, `onOffState` is updated and `lastCommand` is set to e.g. `on sent 2026-06-08 17:42:11`. The timestamp is captured immediately before the API call so it reflects when the command was sent, not when the response arrived.

### Siren

- **Protect Siren (USL-Siren)** — siren/alarm device; on/off state and volume level

---

## Plugin Configuration

Open the plugin's configuration dialog from Indigo's Plugins menu. Key settings:

- **Controller address and credentials** — IP/hostname, username, password for the UniFi Network controller
- **Protect API key** — X-API-KEY for the UniFi Protect Integration API (required for relay control)
- **Poll intervals** — how often to refresh AP, switch, gateway, camera, and sensor states
- **WebSocket** — the plugin maintains a persistent WebSocket connection to UniFi Protect for real-time sensor and relay-input events
- **Controller event tracking** — opens a second WebSocket to the Network controller's event stream (client connect/disconnect/roam, security alerts, admin actions). Buffers the last 500 events, enables the live monitor and print-events menu. Can be toggled at runtime without a plugin restart
- **Use controller WS events for client presence detection** — optional (visible only when event tracking is on): feeds controller WiFi events into client presence tracking instead of the SSH log listener. WARNING: adds roughly 10 seconds of latency vs the SSH listener; only useful when direct SSH access to the APs is unavailable. Changing this setting restarts the plugin
- **Debug areas** — individual checkboxes to enable verbose logging per subsystem (AP, Switch, Gateway, Protect, WebSocket, etc.). One of them appends raw controller WebSocket events to `EVENTS-controllerWS.json` in the prefs dir; Protect WebSocket events are always logged to `EVENTS-protectWS.json` (no option — active whenever Protect is enabled). The files start with `[` and every line ends with `,` — append `]` to get valid JSON. At 50 MB the oldest half is dropped automatically
- **SSH settings** — credentials and port for switch port power-cycle actions that use SSH

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
- **`onAt` / `onAt_Last`** — relay inputs record the timestamp of the most recent press in `onAt` and the previous one in `onAt_Last`
- **`lastCommand`** — relay output devices only; format `"on sent YYYY-MM-DD HH:MM:SS"` or `"off sent …"`

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

- Communication with the UniFi Network controller uses the controller's REST API (cookie-based session auth)
- Communication with UniFi Protect uses two paths:
  - REST Integration API (`/proxy/protect/integration/v1/`) with X-API-KEY for read and write operations
  - WebSocket (`/proxy/protect/ws/updates`) for real-time events (sensor triggers, relay inputs, camera motion)
- An optional second WebSocket connects to the Network controller's event stream (`/proxy/network/wss/s/default/events`). It powers:
  - the live event monitor and print-events menu (last 500 events buffered)
  - security alerts (IPS/IDS, threats) logged as Indigo warnings with source IP, country, and signature
  - instant `blocked` state updates plus an audit log line when an admin blocks/unblocks a client
  - optional client presence detection (`EVT_WU_Connected`/`Disconnected`/`Roam`) as a replacement for the SSH log listener — slower by ~10 s, intended for setups without AP SSH access
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
      Devices.xml               device type definitions
      Actions.xml               action definitions
      MenuItems.xml             menu item definitions
      Events.xml                event definitions
      PluginConfig.xml          plugin preferences UI
      MAC2Vendor.py             MAC-to-vendor lookup
      *.exp                     expect scripts for SSH operations
      unifi_dpi.json            DPI application ID map
```
