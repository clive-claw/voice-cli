"""Keyboard listener for spacebar hold-to-talk detection."""

import asyncio
from typing import Callable
from pynput import keyboard


class KeyboardListener:
    """Detect spacebar press/release and signal when recording should stop."""

    def __init__(self):
        self._spacebar_pressed = False
        self._spacebar_released = asyncio.Event()
        self._listener = None

    async def wait_for_spacebar_hold(self) -> None:
        """Wait until spacebar is pressed."""
        loop = asyncio.get_event_loop()

        def on_press(key: keyboard.Key) -> None:
            try:
                if key == keyboard.Key.space:
                    self._spacebar_pressed = True
            except AttributeError:
                pass

        # Start listener in executor to avoid blocking
        with keyboard.Listener(on_press=on_press) as listener:
            while not self._spacebar_pressed:
                await asyncio.sleep(0.01)

    async def wait_for_spacebar_release(self) -> None:
        """Wait until spacebar is released."""
        self._spacebar_released.clear()
        loop = asyncio.get_event_loop()

        def on_release(key: keyboard.Key) -> None:
            try:
                if key == keyboard.Key.space:
                    self._spacebar_released.set()
            except AttributeError:
                pass

        # Run listener in executor and wait for release event
        def listen():
            with keyboard.Listener(on_release=on_release) as listener:
                listener.join()

        await loop.run_in_executor(None, listen)
        await self._spacebar_released.wait()

    async def wait_spacebar_cycle(self) -> None:
        """Wait for spacebar press, then release. Returns when spacebar is released."""
        self._spacebar_pressed = False
        self._spacebar_released.clear()
        loop = asyncio.get_event_loop()

        def on_press(key: keyboard.Key) -> None:
            try:
                if key == keyboard.Key.space:
                    self._spacebar_pressed = True
            except AttributeError:
                pass

        def on_release(key: keyboard.Key) -> None:
            try:
                if key == keyboard.Key.space and self._spacebar_pressed:
                    self._spacebar_released.set()
            except AttributeError:
                pass

        def listen():
            with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                # Block until release is detected
                while not self._spacebar_released.is_set():
                    pass

        await loop.run_in_executor(None, listen)
