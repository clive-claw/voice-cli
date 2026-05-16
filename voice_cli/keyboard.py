"""Keyboard listener for spacebar hold-to-talk detection."""

import asyncio
from pynput import keyboard


class KeyboardListener:
    """Detect spacebar press/release and signal when recording should stop."""

    def __init__(self):
        self._spacebar_pressed = False
        self._spacebar_released = None
        self._listener = None

    async def wait_for_spacebar_hold(self) -> None:
        """Wait until spacebar is pressed."""
        self._spacebar_pressed = False
        loop = asyncio.get_event_loop()

        def on_press(key):
            try:
                if key == keyboard.Key.space:
                    self._spacebar_pressed = True
                    return False  # Stop listener
            except AttributeError:
                pass

        def start_listener():
            with keyboard.Listener(on_press=on_press) as listener:
                listener.join()

        await loop.run_in_executor(None, start_listener)

    async def wait_for_spacebar_release(self) -> None:
        """Wait until spacebar is released."""
        loop = asyncio.get_event_loop()
        released = asyncio.Event()

        def on_release(key):
            try:
                if key == keyboard.Key.space:
                    loop.call_soon_threadsafe(released.set)
                    return False  # Stop listener
            except AttributeError:
                pass

        def start_listener():
            with keyboard.Listener(on_release=on_release) as listener:
                listener.join()

        # Start listener in executor
        await loop.run_in_executor(None, start_listener)
        # Wait for release signal
        await released.wait()
