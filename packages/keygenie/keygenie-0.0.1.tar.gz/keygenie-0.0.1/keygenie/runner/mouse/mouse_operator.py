"""鼠标操作类"""

import time
import threading
from typing import Optional, Tuple, Any

import pyautogui
from pynput.keyboard import Key, Listener as Keyboard_Listener

from keygenie.constant import SCREEN_DPI, MOUSE_SCREEN_WIDTH, MOUSE_SCREEN_HEIGHT


class MouseOperator:
    """鼠标操作器，提供安全的鼠标操作功能"""

    # Class-level flag to control playback stop
    _stop_playback = False
    _keyboard_listener = None
    _lock = threading.Lock()

    def __init__(self):
        """Initialize MouseOperator and start ESC key listener"""
        self._start_esc_listener()

    def _start_esc_listener(self) -> None:
        """Start background thread to listen for ESC key"""
        if MouseOperator._keyboard_listener is None:
            MouseOperator._keyboard_listener = Keyboard_Listener(
                on_press=self._on_key_press
            )
            MouseOperator._keyboard_listener.start()

    def _on_key_press(self, key: Any) -> None:
        """Handle key press events, stop playback on ESC"""
        try:
            if key == Key.esc:
                with MouseOperator._lock:
                    MouseOperator._stop_playback = True
        except AttributeError:
            pass

    def _check_stop_condition(self) -> None:
        """Check if playback should stop and raise exception if needed"""
        with MouseOperator._lock:
            if MouseOperator._stop_playback:
                raise KeyboardInterrupt("Playback stopped by user (ESC pressed)")

    def _check_mouse_position(self, x: int, y: int) -> None:
        """Check if mouse is at screen edge and stop playback if so

        Stops if mouse touches ANY edge (left, right, top, or bottom), not just corners.
        """
        edge_threshold = 1  # Consider within 1 pixel of edge as touching edge

        # Check if touching left or right edge
        touching_left_or_right = (
            x <= edge_threshold or x >= MOUSE_SCREEN_WIDTH - edge_threshold
        )
        # Check if touching top or bottom edge
        touching_top_or_bottom = (
            y <= edge_threshold or y >= MOUSE_SCREEN_HEIGHT - edge_threshold
        )

        # Stop if touching any edge (any side)
        if touching_left_or_right or touching_top_or_bottom:
            with MouseOperator._lock:
                MouseOperator._stop_playback = True
            raise KeyboardInterrupt(
                f"Playback stopped: mouse touched screen edge at ({x}, {y})"
            )

    def _safe_move_to(self, x: int, y: int, duration: float = 0.0) -> None:
        """Safely move mouse to position with safety checks"""
        self._check_stop_condition()
        self._check_mouse_position(x, y)
        # For long duration moves, use smaller steps to allow ESC checking
        if duration > 0.1:
            # Get current position before starting move
            current_pos = pyautogui.position()
            current_x, current_y = current_pos.x, current_pos.y
            steps = max(
                10, int(duration * 10)
            )  # At least 10 steps, or 10 steps per second
            step_duration = duration / steps
            dx = (x - current_x) / steps
            dy = (y - current_y) / steps
            for i in range(steps):
                self._check_stop_condition()
                step_x = int(current_x + dx * (i + 1))
                step_y = int(current_y + dy * (i + 1))
                self._check_mouse_position(step_x, step_y)
                pyautogui.moveTo(step_x, step_y, duration=step_duration)
        else:
            pyautogui.moveTo(x, y, duration=duration)

    def drag(
        self,
        from_x: int,
        from_y: int,
        to_x: Optional[int] = None,
        to_y: Optional[int] = None,
        duration: float = 0.5,
        down_sleep: float = 0,
    ) -> None:
        """
        执行拖拽操作

        Args:
            from_x: 起始X坐标（鼠标坐标，逻辑坐标）
            from_y: 起始Y坐标（鼠标坐标，逻辑坐标）
            to_x: 目标X坐标（鼠标坐标，逻辑坐标），如果为None则使用from_x
            to_y: 目标Y坐标（鼠标坐标，逻辑坐标），如果为None则使用from_y
            duration: 移动持续时间（秒）
            down_sleep: 按下鼠标后等待时间（秒）

        Raises:
            KeyboardInterrupt: If ESC is pressed or mouse touches screen edge
        """
        self._check_stop_condition()
        self._check_mouse_position(from_x, from_y)
        if to_x is None:
            to_x = from_x
        if to_y is None:
            to_y = from_y
        self._check_mouse_position(to_x, to_y)
        pyautogui.mouseDown(from_x, from_y)
        pyautogui.sleep(down_sleep)
        self._safe_move_to(to_x, to_y, duration=duration)
        pyautogui.mouseUp(to_x, to_y)

    def safe_click(
        self,
        x: int,
        y: int,
        pixel: Optional[Tuple[int, int, int]] = None,
        tolerance: int = 10,
        before_sleep: float = 0.5,
        after_sleep: float = 0.5,
        max_waiting_time: float = 10,
        **kwargs: Any,
    ) -> None:
        """
        安全点击，会等待指定位置的像素值匹配后再点击

        Args:
            x: 点击X坐标（鼠标坐标，逻辑坐标）
            y: 点击Y坐标（鼠标坐标，逻辑坐标）
            pixel: 期望的RGB像素值，如果提供则等待像素匹配后再点击
            tolerance: 像素匹配的容差值
            before_sleep: 点击前等待时间（秒）
            after_sleep: 点击后等待时间（秒）
            max_waiting_time: 最大等待时间（秒）
            **kwargs: 传递给pyautogui.click的其他参数

        Raises:
            RuntimeError: 如果超过最大等待时间仍未匹配到目标像素值
        """
        self._check_stop_condition()
        self._check_mouse_position(x, y)
        start_time = time.time()
        self._safe_move_to(x, y)

        # pyautogui.pixel需要像素坐标
        x_px = x * SCREEN_DPI
        y_px = y * SCREEN_DPI

        while time.time() - start_time < max_waiting_time:
            self._check_stop_condition()
            if pixel and not pyautogui.pixelMatchesColor(
                x_px, y_px, pixel, tolerance=tolerance
            ):
                pyautogui.sleep(0.2)
                continue
            else:
                self.click(
                    x, y, before_sleep=before_sleep, after_sleep=after_sleep, **kwargs
                )
                return

        current_pixel = pyautogui.pixel(x_px, y_px)
        raise RuntimeError(
            f"waiting time > {max_waiting_time}s, pixel in ({x}, {y}) = {current_pixel} "
            f"does not match target pixel {pixel}."
        )

    def click(
        self,
        x: int,
        y: int,
        before_sleep: float = 0.0,
        after_sleep: float = 0.0,
        **kwargs: Any,
    ) -> None:
        """
        执行点击操作

        Args:
            x: 点击X坐标（鼠标坐标，逻辑坐标）
            y: 点击Y坐标（鼠标坐标，逻辑坐标）
            before_sleep: 点击前等待时间（秒）
            after_sleep: 点击后等待时间（秒）
            **kwargs: 传递给pyautogui.click的其他参数

        Raises:
            KeyboardInterrupt: If ESC is pressed or mouse touches screen edge
        """
        self._check_stop_condition()
        self._check_mouse_position(x, y)
        if before_sleep > 0:
            pyautogui.sleep(before_sleep)
        pyautogui.click(x, y, **kwargs)
        if after_sleep > 0:
            pyautogui.sleep(after_sleep)

    def safe_scroll(self, value: int, after_sleep: float = 1) -> None:
        """
        安全滚动，滚动后等待指定时间

        Args:
            value: 滚动值，正数向上，负数向下
            after_sleep: 滚动后等待时间（秒）

        Raises:
            KeyboardInterrupt: If ESC is pressed
        """
        self._check_stop_condition()
        pyautogui.scroll(value)
        if after_sleep > 0:
            # Check ESC during sleep period
            sleep_interval = 0.1
            elapsed = 0.0
            while elapsed < after_sleep:
                self._check_stop_condition()
                sleep_time = min(sleep_interval, after_sleep - elapsed)
                pyautogui.sleep(sleep_time)
                elapsed += sleep_time
