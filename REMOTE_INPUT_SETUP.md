# Remote UI Input Setup

This guide explains how to set up remote interactivity for your streamed openpilot UI.

## Architecture

The system works in two parts:

1. **HTTP Server** (port 8082 default) - Streams video and telemetry
2. **WebSocket Server** (port 8083 default) - Accepts input events from the browser

When you interact with the browser UI (clicks, touches), the JavaScript sends events via WebSocket to the device, where they're injected as `/dev/input/` touch events.

## Installation

### 1. Install Python dependencies on the device

You need the `websockets` library for WebSocket support:

```bash
pip install websockets
```

If you can't install system-wide, you can install locally:
```bash
pip install --user websockets
```

### 2. Files included

- **`ui_stream.py`** - Updated with WebSocket server and input handler
- **`input_injector.py`** - Handles `/dev/input/` event injection
- **`stream_patch.py`** - Patches application.py (unchanged, but documents the integration)

## Usage

The system starts automatically when you launch openpilot with `STREAM=1`:

```bash
STREAM=1 python application.py
```

This will start both:
- HTTP server on `http://device:8082`
- WebSocket server on `ws://device:8083`

### Connect from Browser

Open `http://<device-ip>:8082` in your browser. The browser will:
1. Stream the openpilot UI in real-time
2. Automatically connect to the WebSocket server
3. Send your touches/clicks to the device

## Interaction Methods

### Touchscreen / Mobile
- **Tap** to click a button
- **Drag** to interact with sliders or draggable elements
- **Swipe** is treated as touch movement

### Mouse / Desktop
- **Click** to tap
- **Drag** while holding the mouse button to drag on screen

## Input Coordinate Mapping

The browser automatically:
1. Detects where you click/touch relative to the displayed image
2. Normalizes to percentage coordinates (0-100%)
3. Sends to the device

The device then scales these back to the actual touchscreen resolution (default 1280x720, configurable in the browser event handler).

## Troubleshooting

### WebSocket connection fails

1. Check if the device is listening:
   ```bash
   netstat -tlnp | grep :8083
   ```

2. Check firewall rules (port 8083 must be accessible from the browser)

3. Look for errors in the application output

### Inputs don't work

1. Verify the touch device was detected:
   ```bash
   ls -la /dev/input/event*
   ```

2. Check permissions - you may need to run as root or in the right group:
   ```bash
   sudo python application.py  # or adjust group permissions
   ```

3. Verify the correct device path in the logs:
   ```
   [ui_stream] Touch device: /dev/input/event0
   ```

4. Test direct input injection:
   ```python
   import input_injector
   device = input_injector.get_touch_device()
   input_injector.inject_click(device, 640, 360)
   ```

## Customization

### Change ports

In `stream_patch.py` or where you call `ui_stream.start()`:

```python
ui_stream.start(port=8082, ws_port=8083)
```

### Disable WebSocket (fallback to HTTP-only)

```python
ui_stream.start(port=8082, ws_port=False)
```

### Adjust touch resolution

In the browser, edit the `sendInput` function to match your device's resolution:

```javascript
width: 1920,  // change from 1280
height: 1080,  // change from 720
```

## Technical Details

### Input Event Format (JSON)

The browser sends events in this format:

```json
{
  "action": "down",  // "down", "move", or "up"
  "x": 50.0,  // percentage (0-100)
  "y": 50.0,  // percentage (0-100)
  "pressure": 100,  // 0-255
  "normalized": true,
  "width": 1280,
  "height": 720
}
```

### Touch Event Sequence

A typical touch interaction sends:
1. `"action": "down"` - Finger touches screen
2. `"action": "move"` - (Optional) Finger moves across screen
3. `"action": "up"` - Finger lifts off screen

### Device Detection

The input injector searches for touch devices in this order:
- `/dev/input/event0` through `/dev/input/event5`

If your device is at a different path, modify `input_injector.get_touch_device()`.

## Performance Notes

- WebSocket messages are sent immediately on touch/mouse events
- Typical latency: 10-50ms depending on network
- No frame buffering needed - events are instant
- Safe for local network use (same WiFi)

## Security Considerations

⚠️ **Important**: This server accepts input from any client that can reach port 8083. In untrusted networks:

- Run on localhost only: modify `0.0.0.0` to `127.0.0.1` in the bind address
- Use a firewall to restrict access
- Consider adding authentication before deploying on public networks

## Future Enhancements

Possible improvements:
- Keyboard input support (for text entry)
- Gesture recognition (two-finger pinch, etc.)
- Pressure sensitivity for analog inputs
- Input rate limiting for safety
