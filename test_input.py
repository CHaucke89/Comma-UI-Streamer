#!/usr/bin/env python3
"""Test script for remote input injection.

Usage:
    python3 test_input.py          # Auto-detect device
    python3 test_input.py /dev/input/event2  # Specify device
"""
import sys
import time
import input_injector

def test_device():
    """Test finding the touch device."""
    print("🔍 Searching for touch device...")
    device = input_injector.get_touch_device()
    if device:
        print(f"✅ Found: {device}")
        return device
    else:
        print("❌ No touch device found")
        print("   Try: ls -la /dev/input/event*")
        return None

def test_click(device, x=640, y=360):
    """Test a single click."""
    print(f"\n👆 Injecting click at ({x}, {y})...")
    result = input_injector.inject_click(device, x, y)
    if result:
        print("✅ Click sent")
        return True
    else:
        print("❌ Click failed")
        return False

def test_drag(device, x1=640, y1=360, x2=800, y2=400):
    """Test a drag gesture."""
    print(f"\n👐 Injecting drag from ({x1},{y1}) to ({x2},{y2})...")
    input_injector.inject_touch_event(device, x1, y1, 100, "down")
    time.sleep(0.1)
    for i in range(5):
        x = int(x1 + (x2 - x1) * (i / 5))
        y = int(y1 + (y2 - y1) * (i / 5))
        input_injector.inject_touch_event(device, x, y, 100, "move")
        time.sleep(0.05)
    input_injector.inject_touch_event(device, x2, y2, 0, "up")
    print("✅ Drag sent")

def main():
    # Determine device
    if len(sys.argv) > 1:
        device = sys.argv[1]
        print(f"Using specified device: {device}")
    else:
        device = test_device()
        if not device:
            sys.exit(1)

    # Menu
    print("\n" + "="*50)
    print("Remote Input Test")
    print("="*50)
    print(f"Device: {device}\n")
    print("Commands:")
    print("  1 - Test click (center screen)")
    print("  2 - Test drag (horizontal)")
    print("  3 - Test rapid clicks")
    print("  4 - Test custom position")
    print("  q - Quit\n")

    while True:
        cmd = input("Enter command: ").strip().lower()

        if cmd == 'q':
            print("Exiting...")
            break
        elif cmd == '1':
            test_click(device, 640, 360)
        elif cmd == '2':
            test_drag(device, 640, 360, 900, 400)
        elif cmd == '3':
            print("\n🔄 Injecting 5 rapid clicks...")
            for i in range(5):
                x = 400 + (i * 50)
                test_click(device, x, 360)
                time.sleep(0.2)
        elif cmd == '4':
            try:
                x = int(input("  X coordinate (0-1280): "))
                y = int(input("  Y coordinate (0-720): "))
                test_click(device, x, y)
            except ValueError:
                print("❌ Invalid coordinates")
        else:
            print("❓ Unknown command")

if __name__ == '__main__':
    main()
