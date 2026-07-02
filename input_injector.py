"""Inject touch events into /dev/input/ for remote control."""
import struct
import time
import os

# Event codes from linux/input-event-codes.h
EV_ABS = 3
EV_SYN = 0
ABS_X = 0
ABS_Y = 1
ABS_PRESSURE = 24
ABS_MT_POSITION_X = 53
ABS_MT_POSITION_Y = 54
ABS_MT_TRACKING_ID = 57
ABS_MT_PRESSURE = 58
SYN_REPORT = 0
SYN_MT_REPORT = 2

BTN_TOUCH = 330


def get_touch_device():
    """Find the touch device. Try common paths first."""
    candidates = [
        "/dev/input/event0",
        "/dev/input/event1",
        "/dev/input/event2",
        "/dev/input/event3",
        "/dev/input/event4",
        "/dev/input/event5",
    ]

    for path in candidates:
        if os.path.exists(path):
            try:
                # Try to open it
                open(path, 'wb').close()
                return path
            except PermissionError:
                continue

    return None


def inject_touch_event(device_path, x, y, pressure=100, action="move"):
    """
    Inject a touch event into /dev/input/.

    Args:
        device_path: Path to input device (e.g., /dev/input/event0)
        x, y: Absolute coordinates
        pressure: Touch pressure (0-255)
        action: "down", "move", or "up"
    """
    if not device_path or not os.path.exists(device_path):
        return False

    try:
        with open(device_path, 'wb') as f:
            now = time.time()
            sec = int(now)
            usec = int((now - sec) * 1000000)

            # Multi-touch event sequence
            events = []

            if action == "down":
                # Start touch: set tracking ID and position
                events.extend([
                    (EV_ABS, ABS_MT_TRACKING_ID, 0),
                    (EV_ABS, ABS_MT_POSITION_X, x),
                    (EV_ABS, ABS_MT_POSITION_Y, y),
                    (EV_ABS, ABS_MT_PRESSURE, pressure),
                    (EV_SYN, SYN_MT_REPORT, 0),
                    (EV_SYN, SYN_REPORT, 0),
                ])
            elif action == "move":
                # Update position
                events.extend([
                    (EV_ABS, ABS_MT_POSITION_X, x),
                    (EV_ABS, ABS_MT_POSITION_Y, y),
                    (EV_ABS, ABS_MT_PRESSURE, pressure),
                    (EV_SYN, SYN_MT_REPORT, 0),
                    (EV_SYN, SYN_REPORT, 0),
                ])
            elif action == "up":
                # End touch: clear tracking ID
                events.extend([
                    (EV_ABS, ABS_MT_TRACKING_ID, -1),
                    (EV_SYN, SYN_MT_REPORT, 0),
                    (EV_SYN, SYN_REPORT, 0),
                ])

            for type_, code, value in events:
                # struct: timeval (sec, usec) + type + code + value
                event = struct.pack('llHHI', sec, usec, type_, code, value)
                f.write(event)

        return True
    except Exception as e:
        print(f"Failed to inject event: {e}")
        return False


def inject_click(device_path, x, y):
    """Inject a click event (down + up)."""
    inject_touch_event(device_path, x, y, pressure=100, action="down")
    time.sleep(0.05)
    inject_touch_event(device_path, x, y, pressure=0, action="up")
