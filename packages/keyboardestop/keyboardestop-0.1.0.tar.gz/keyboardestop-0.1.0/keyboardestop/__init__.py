
"""
keyboardestop.py — reusable emergency stop helpers for CoDrone EDU (or any drone object)

Usage (minimal):
    from codrone_edu.drone import Drone
    import keyboardestop as kes

    drone = Drone()
    drone.pair("COM4")
    kes.install(drone)  # Ctrl+C will call drone.emergency_stop() and exit (by default)

    # -- Your mission code --
    drone.takeoff()
    drone.hover(5.0)
    drone.land()

Alternative: keep process alive after Ctrl+C
    kes.install(drone, exit_on_interrupt=False)

Optional: use as a context manager
    with kes.EmergencyStopGuard(drone):
        # mission code here

Optional: add a background 'q' listener (for testing or extra manual kill)
    kes.enable_q_listener(drone, key='q', exit_on_q=False)

Notes:
- This module does not redefine your Drone class. Pass in your SDK instance.
- By default, Ctrl+C triggers emergency_stop and exits quickly to avoid continuing control code.
- Safe to call install() once; subsequent calls are ignored unless you uninstall().
"""

import signal
import sys
import atexit
import threading
from typing import Optional, Callable

__all__ = [
    'install', 'uninstall', 'safe_stop', 'EmergencyStopGuard', 'enable_q_listener'
]

# Internal state
_drone = None
_installed = False
_prev_sigint_handler = None
_lock = threading.Lock()
_q_thread = None


def _call_emergency_stop(drone_obj):
    """Call the SDK's emergency stop method if present, with robust error handling."""
    if drone_obj is None:
        return
    try:
        # CoDrone EDU uses emergency_stop()
        if hasattr(drone_obj, 'emergency_stop') and callable(getattr(drone_obj, 'emergency_stop')):
            drone_obj.emergency_stop()
        else:
            # Fallback name if different SDKs are used
            if hasattr(drone_obj, 'emergencystop') and callable(getattr(drone_obj, 'emergencystop')):
                drone_obj.emergencystop()
            else:
                print('[keyboardestop] Warning: drone has no emergency stop method.', file=sys.stderr)
        print('[keyboardestop] Emergency stop sent.')
    except Exception as e:
        print(f"[keyboardestop] Emergency stop failed: {e}", file=sys.stderr)


def safe_stop():
    """Public helper to trigger emergency stop once, if a drone is installed."""
    with _lock:
        _call_emergency_stop(_drone)


def install(drone, exit_on_interrupt: bool = True):
    """
    Install Ctrl+C (SIGINT) handler that calls drone.emergency_stop().

    Args:
        drone: Your SDK drone instance (e.g., codrone_edu.drone.Drone).
        exit_on_interrupt: If True, call sys.exit(1) after stopping to terminate immediately.
    """
    global _drone, _installed, _prev_sigint_handler
    with _lock:
        if _installed:
            # Already installed; do nothing
            return
        _drone = drone
        _installed = True
        _prev_sigint_handler = signal.getsignal(signal.SIGINT)

        def on_sigint(signum, frame):
            # Ctrl + C pressed
            _call_emergency_stop(_drone)
            if exit_on_interrupt:
                # Exit immediately to avoid continuing control code
                try:
                    sys.exit(1)
                except SystemExit:
                    raise
            # If not exiting, return control to Python (KeyboardInterrupt may surface elsewhere)

        signal.signal(signal.SIGINT, on_sigint)
        atexit.register(safe_stop)
        print('[keyboardestop] SIGINT handler installed.')


def uninstall():
    """Remove the installed SIGINT handler and atexit hook. Does not change any drone state."""
    global _installed, _drone, _prev_sigint_handler
    with _lock:
        if not _installed:
            return
        try:
            if _prev_sigint_handler is not None:
                signal.signal(signal.SIGINT, _prev_sigint_handler)
            else:
                signal.signal(signal.SIGINT, signal.SIG_DFL)
        except Exception:
            pass
        _installed = False
        _drone = None
        print('[keyboardestop] SIGINT handler uninstalled.')


class EmergencyStopGuard:
    """
    Context manager ensuring emergency stop on any exit path.

    Usage:
        with EmergencyStopGuard(drone):
            # mission code
    """
    def __init__(self, drone):
        self.drone = drone

    def __enter__(self):
        return self.drone

    def __exit__(self, exc_type, exc, tb):
        try:
            _call_emergency_stop(self.drone)
        finally:
            # Propagate exceptions (including KeyboardInterrupt)
            return False


def enable_q_listener(drone, key: str = 'q', exit_on_q: bool = False):
    """
    Start a background daemon thread that listens for the given key and triggers emergency stop.
    Works on Windows (msvcrt) and POSIX (termios + select) terminals.

    Args:
        drone: Your drone instance.
        key: Single character to trigger stop (default 'q').
        exit_on_q: If True, call sys.exit(1) after stopping.
    """
    global _q_thread
    with _lock:
        if _q_thread and _q_thread.is_alive():
            return _q_thread

        def on_q():
            _call_emergency_stop(drone)
            if exit_on_q:
                try:
                    sys.exit(1)
                except SystemExit:
                    raise

        def listener_windows():
            import msvcrt, time
            print(f"[keyboardestop] Press '{key}' to emergency stop. (Windows)")
            while True:
                if msvcrt.kbhit():
                    ch = msvcrt.getch()
                    s = (ch.decode('utf-8', errors='ignore') if isinstance(ch, bytes) else str(ch)).lower()
                    if s == key:
                        on_q()
                time.sleep(0.01)

        def listener_posix():
            import tty, termios, select, time
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            print(f"[keyboardestop] Press '{key}' to emergency stop. (POSIX)")
            try:
                tty.setcbreak(fd)
                while True:
                    rlist, _, _ = select.select([sys.stdin], [], [], 0.05)
                    if rlist:
                        ch = sys.stdin.read(1).lower()
                        if ch == key:
                            on_q()
                    time.sleep(0.01)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)

        target = listener_windows if sys.platform.startswith('win') else listener_posix
        _q_thread = threading.Thread(target=target, daemon=True)
        _q_thread.start()
        return _q_thread
