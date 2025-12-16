"""主录制器模块，用于记录鼠标和键盘操作"""

import time
import sys
import os
import warnings
import math
import platform
from typing import Optional, Tuple, Dict, List, Any

from pynput.mouse import Listener as Mouse_Listener, Button
from pynput.keyboard import Key, Listener as Keyboard_Listener
import pyautogui
from PIL import Image, ImageDraw

from keygenie.constant import (
    SCREEN_DPI,
    MOUSE_SCREEN_WIDTH,
    MOUSE_SCREEN_HEIGHT,
    DISPLAY_PIXEL_WIDTH,
    DISPLAY_PIXEL_HEIGHT,
)
from keygenie.utils.decorator import singleton

# todo 已知bug1：启动时偶发会有个KeyError: 'CFMachPortCreateRunLoopSource'，会导致键盘记录不了，如遇到，重新试着开几次
# todo bug2: 退出程序的话在项目目录下保存一个临时图片，好像是pyautogui.pixel的问题


@singleton
class MainRecorder:
    """
    主录制器类，单例模式

    用于记录鼠标和键盘操作，并生成对应的Python代码。
    支持截图功能，可以在点击位置保存截图。
    """

    def __init__(
        self,
        tolerance: int = 10,
        screenshots_dir: Optional[str] = None,
        screenshot_size: int = -1,
    ) -> None:
        """
        初始化录制器

        Args:
            tolerance: 像素匹配容差值，>0时使用safe_click，=0时使用普通click
            screenshots_dir: 截图保存目录
            screenshot_size: 截图大小，-1表示全屏截图
        """
        self.tolerance = tolerance  # 像素匹配容差值
        self.screenshots_dir = screenshots_dir  # 截图保存目录
        assert (
            screenshot_size == -1 or screenshot_size > 0
        ), "screenshot_size must be -1 (full screen) or > 0"
        self.screenshot_size = screenshot_size  # 截图大小
        self.screenshot_counter = 0  # 截图文件名计数器
        self.screenshot_map: Dict[str, str] = {}  # 代码行到截图路径的映射

        # 键盘映射表，根据平台动态设置
        if platform.system() == "Darwin":  # macOS
            self.key_map: Dict[Key, str] = {
                Key.cmd: "command",
                Key.cmd_r: "command",
                Key.alt: "option",
                Key.alt_r: "option",
                Key.shift_r: "shift",
            }
        else:  # Linux/Windows
            self.key_map: Dict[Key, str] = {
                Key.cmd: "ctrl",
                Key.cmd_r: "ctrl",
                Key.alt: "alt",
                Key.alt_r: "alt",
                Key.shift_r: "shift",
            }
        self.key_stack: List[Any] = []  # 当前按下的键栈
        self.max_key_stack: List[Any] = []  # 最大键栈（用于记录组合键）
        self.last_char_time: float = 0  # 上次字符输入时间
        self.char_buffer: str = ""  # 字符缓冲区，用于累积连续字符输入

        self.total_scroll = 0  # 累计滚动值

        self.pressed_xy: Tuple[int, int] = (0, 0)  # 按下鼠标时的坐标
        self.pressed_button: Optional[Button] = None  # 按下时的鼠标按钮类型
        self.pixel_before_press: Tuple[int, int, int] = (0, 0, 0)  # 按下前的像素值
        self.screenshot_filename_on_press: Optional[str] = (
            None  # 按下时保存的截图文件名
        )

        self.last_click_print: Optional[str] = None  # 上次点击的代码行
        self.last_click_print_time: float = time.time()  # 上次点击的时间

        self.print_line_list: List[str] = []  # 生成的代码行列表

    def start_listen(self) -> List[str]:
        """
        开始监听鼠标和键盘事件

        启动鼠标和键盘监听线程，记录用户操作并生成对应的Python代码。

        Returns:
            生成的代码行列表
        """
        try:
            print("###start###")
            # 添加导入语句
            self.print_line_list.append(
                """import pyautogui\n
from keygenie.runner.mouse.mouse_operator import MouseOperator\n
mouse_operator = MouseOperator()\n
"""
            )

            # 启动鼠标监听线程
            mouse_listen_thread = Mouse_Listener(
                on_click=self.on_click, on_scroll=self.on_scroll
            )
            mouse_listen_thread.start()

            # 启动键盘监听线程
            keyboard_listen_thread = Keyboard_Listener(
                on_press=self.on_key_press, on_release=self.on_key_release
            )
            keyboard_listen_thread.start()
            keyboard_listen_thread.join()
        except Exception:
            # 录制停止时打印代码（例如用户按'q'或Ctrl+C）
            # 输出剩余的字符缓冲区
            if self.char_buffer:
                self.print_line_list.append(f'pyautogui.write("{self.char_buffer}")')
                self.char_buffer = ""
            _ = [print(line) for line in self.print_line_list]
        finally:
            # 输出剩余的字符缓冲区
            if self.char_buffer:
                self.print_line_list.append(f'pyautogui.write("{self.char_buffer}")')
                self.char_buffer = ""
            # 始终返回代码列表
            return self.print_line_list

    def on_click(self, x: float, y: float, button: Any, is_press: bool) -> None:
        """
        鼠标点击事件处理

        Args:
            x: 鼠标X坐标（鼠标坐标，逻辑坐标）
            y: 鼠标Y坐标（鼠标坐标，逻辑坐标）
            button: 鼠标按钮
            is_press: 是否为按下事件（True为按下，False为释放）
        """
        x_mouse = round(x)
        y_mouse = round(y)

        if is_press:
            # 记录按下时的坐标和按钮类型
            self.pressed_xy = (x_mouse, y_mouse)
            self.pressed_button = button
            # 先截图，然后从截图中读取像素值，确保像素值和截图完全一致
            screenshot_filename, pixel_value = self.save_click_screenshot(
                x_mouse, y_mouse
            )
            self.screenshot_filename_on_press = screenshot_filename
            # 如果成功获取像素值，保存它
            if pixel_value is not None:
                self.pixel_before_press = pixel_value
            else:
                # 如果从截图中读取失败，回退到使用pyautogui.pixel（需要像素坐标）
                self.pixel_before_press = pyautogui.pixel(
                    x_mouse * SCREEN_DPI, y_mouse * SCREEN_DPI
                )
        else:
            # 处理释放事件
            if x_mouse == self.pressed_xy[0] and y_mouse == self.pressed_xy[1]:
                # 点击（按下和释放在同一位置）
                # 使用按下时保存的截图
                screenshot_filename = getattr(
                    self, "screenshot_filename_on_press", None
                )
                now_click_print = self._generate_click_code(
                    x_mouse, y_mouse, self.pressed_button
                )
                self._handle_single_click(
                    x_mouse,
                    y_mouse,
                    now_click_print,
                    screenshot_filename,
                    self.pressed_button,
                )
            else:
                # 拖拽（按下和释放在不同位置）
                drag_code_line = (
                    f"mouse_operator.drag({self.pressed_xy[0]}, {self.pressed_xy[1]}, "
                    f"to_x={x_mouse}, to_y={y_mouse})"
                )
                # 保存拖拽截图
                screenshot_filename = self.save_drag_screenshot(
                    self.pressed_xy[0],
                    self.pressed_xy[1],
                    x_mouse,
                    y_mouse,
                )
                self.print_line_list.append(drag_code_line)
                # 存储截图信息
                if screenshot_filename:
                    self.screenshot_map[drag_code_line] = screenshot_filename

    def on_key_press(self, key: Any) -> None:
        """
        键盘按下事件处理

        Args:
            key: 按下的键
        """
        try:
            self.key_stack.append(key.char)
        except AttributeError:
            self.key_stack.append(key)
        self.max_key_stack = self.key_stack.copy()

    def on_key_release(self, key: Any) -> None:
        """
        键盘释放事件处理

        当所有键都释放时，生成热键代码或字符输入代码。

        Args:
            key: 释放的键
        """
        if self.key_stack:
            self.key_stack.pop()
        if not self.key_stack and self.max_key_stack:
            self._handle_key_input()

    def on_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        """
        鼠标滚动事件处理

        Args:
            x: 鼠标X坐标
            y: 鼠标Y坐标
            dx: 水平滚动值
            dy: 垂直滚动值
        """
        if dx != 0:
            print("dx = ", dx)
        if dy != 0:
            print("dy = ", dy)

        self._handle_scroll_axis(dx)
        self._handle_scroll_axis(dy)

    def _is_modifier_key(self, key: Any) -> bool:
        """
        判断是否是修饰键（ctrl、alt、shift、cmd等）

        Args:
            key: 键对象或字符串

        Returns:
            如果是修饰键返回True，否则返回False
        """
        if isinstance(key, str):
            return False
        modifier_keys = {
            Key.ctrl,
            Key.ctrl_l,
            Key.ctrl_r,
            Key.alt,
            Key.alt_l,
            Key.alt_r,
            Key.shift,
            Key.shift_l,
            Key.shift_r,
            Key.cmd,
            Key.cmd_l,
            Key.cmd_r,
        }
        return key in modifier_keys

    def _handle_key_input(self) -> None:
        """
        处理键盘输入，区分单个字符输入和组合键
        """
        # 检查是否有修饰键
        has_modifier = any(self._is_modifier_key(key) for key in self.max_key_stack)

        if has_modifier:
            # 有修饰键，使用热键方式
            self.print_hot_key()
        else:
            # 没有修饰键，检查是否是单个字符
            if len(self.max_key_stack) == 1:
                key = self.max_key_stack[0]
                if isinstance(key, str) and len(key) == 1:
                    # 单个字符，累积到缓冲区
                    current_time = time.time()
                    # 如果距离上次输入超过0.3秒，输出之前的缓冲区内容
                    if current_time - self.last_char_time > 0.3 and self.char_buffer:
                        self.print_line_list.append(
                            f'pyautogui.write("{self.char_buffer}")'
                        )
                        self.char_buffer = ""
                    # 添加到缓冲区
                    self.char_buffer += key
                    self.last_char_time = current_time
                else:
                    # 特殊键（如回车、退格等），先输出缓冲区，再输出特殊键
                    if self.char_buffer:
                        self.print_line_list.append(
                            f'pyautogui.write("{self.char_buffer}")'
                        )
                        self.char_buffer = ""
                    # 处理特殊键
                    key_name = self._format_key_name(key)
                    if key_name == "enter":
                        self.print_line_list.append("pyautogui.press('enter')")
                    elif key_name == "backspace":
                        self.print_line_list.append("pyautogui.press('backspace')")
                    elif key_name == "tab":
                        self.print_line_list.append("pyautogui.press('tab')")
                    elif key_name == "space":
                        # 空格当作普通字符处理
                        current_time = time.time()
                        if (
                            current_time - self.last_char_time > 0.3
                            and self.char_buffer
                        ):
                            self.print_line_list.append(
                                f'pyautogui.write("{self.char_buffer}")'
                            )
                            self.char_buffer = ""
                        self.char_buffer += " "
                        self.last_char_time = current_time
                    else:
                        # 其他特殊键，使用press
                        self.print_line_list.append(f"pyautogui.press('{key_name}')")
            else:
                # 多个键但没有修饰键，可能是快速按键，使用热键方式
                self.print_hot_key()

    def print_hot_key(self) -> None:
        """
        打印热键组合代码

        将当前按下的键组合转换为pyautogui.hotkey()调用代码。
        如果检测到'q'键，会抛出KeyError来结束录制。

        Raises:
            KeyError: 如果检测到'q'键，用于结束录制
        """
        # 先输出字符缓冲区
        if self.char_buffer:
            self.print_line_list.append(f'pyautogui.write("{self.char_buffer}")')
            self.char_buffer = ""

        key_list = [self._format_key_name(item) for item in self.max_key_stack]
        print_str = "".join([f"'{key}', " for key in key_list])

        if "q" in print_str:
            raise KeyError("Finish.")

        self.print_line_list.append(f"pyautogui.hotkey({print_str[:-2]})")

    def save_click_screenshot(
        self, x_mouse: int, y_mouse: int
    ) -> Tuple[Optional[str], Optional[Tuple[int, int, int]]]:
        """
        保存点击位置的截图，并从截图中读取像素值

        如果screenshot_size为-1，则捕获整个屏幕。
        否则，捕获以点击位置为中心的screenshot_size x screenshot_size的正方形区域。

        Args:
            x_mouse: 点击X坐标（鼠标坐标，逻辑坐标）
            y_mouse: 点击Y坐标（鼠标坐标，逻辑坐标）

        Returns:
            (截图文件名, 像素值RGB元组)，如果保存失败则返回(None, None)
        """
        if not self.screenshots_dir:
            return None, None

        try:
            # 验证坐标并准备截图目录
            if not self._validate_and_prepare_screenshot_region(x_mouse, y_mouse):
                return None, None

            # 计算截图区域（返回逻辑坐标，因为pyautogui.screenshot使用逻辑坐标）
            left_mouse, top_mouse, width_mouse, height_mouse = (
                self._calculate_screenshot_region(x_mouse, y_mouse)
            )

            # 捕获截图（先截图，确保像素值从截图中读取）
            screenshot = self._capture_screenshot(
                left_mouse, top_mouse, width_mouse, height_mouse
            )
            if screenshot is None:
                return None, None

            # 从截图中读取像素值（确保像素值和截图完全一致）
            relative_x = x_mouse - left_mouse
            relative_y = y_mouse - top_mouse
            # 确保坐标在截图范围内
            if (
                relative_x < 0
                or relative_y < 0
                or relative_x >= width_mouse
                or relative_y >= height_mouse
            ):
                pixel_value = None
            else:
                pixel_value = screenshot.getpixel((relative_x, relative_y))

            # 在截图上绘制点击位置标记（使用逻辑坐标）
            self._draw_click_marker(screenshot, x_mouse, y_mouse, left_mouse, top_mouse)

            # 保存截图
            screenshot_filename = (
                f"click_local_screen_shot{self.screenshot_counter + 1}.png"
            )
            saved_filename = self._save_screenshot(screenshot, screenshot_filename)
            return saved_filename, pixel_value
        except Exception:
            # 静默失败，避免中断录制
            # 调试时可以取消注释以下行：
            # print(f"Failed to save screenshot at ({x_mouse}, {y_mouse}): {e}")
            return None, None

    def save_drag_screenshot(
        self, from_x_mouse: int, from_y_mouse: int, to_x_mouse: int, to_y_mouse: int
    ) -> Optional[str]:
        """
        保存拖拽操作的截图（包含箭头标记）

        Args:
            from_x_mouse: 起始X坐标（鼠标坐标，逻辑坐标）
            from_y_mouse: 起始Y坐标（鼠标坐标，逻辑坐标）
            to_x_mouse: 目标X坐标（鼠标坐标，逻辑坐标）
            to_y_mouse: 目标Y坐标（鼠标坐标，逻辑坐标）

        Returns:
            截图文件名，如果保存失败则返回None
        """
        if not self.screenshots_dir:
            return None

        try:
            # 验证坐标并准备截图目录
            if not self._validate_and_prepare_screenshot_region(
                from_x_mouse, from_y_mouse
            ):
                return None

            # 计算截图区域
            if self.screenshot_size == -1:
                # 全屏截图
                left_mouse = 0
                top_mouse = 0
                width_mouse = MOUSE_SCREEN_WIDTH
                height_mouse = MOUSE_SCREEN_HEIGHT
            else:
                # 计算包含起点和终点的区域（逻辑坐标）
                min_x_mouse = min(from_x_mouse, to_x_mouse)
                max_x_mouse = max(from_x_mouse, to_x_mouse)
                min_y_mouse = min(from_y_mouse, to_y_mouse)
                max_y_mouse = max(from_y_mouse, to_y_mouse)

                # 添加边距（逻辑坐标）
                padding_mouse = 50
                left_mouse = max(0, min_x_mouse - padding_mouse)
                top_mouse = max(0, min_y_mouse - padding_mouse)
                right_mouse = min(MOUSE_SCREEN_WIDTH, max_x_mouse + padding_mouse)
                bottom_mouse = min(MOUSE_SCREEN_HEIGHT, max_y_mouse + padding_mouse)

                width_mouse = right_mouse - left_mouse
                height_mouse = bottom_mouse - top_mouse

                # 验证区域有效性
                if width_mouse <= 0 or height_mouse <= 0:
                    return None

            # 捕获截图
            screenshot = self._capture_screenshot(
                left_mouse, top_mouse, width_mouse, height_mouse
            )
            if screenshot is None:
                return None

            # 在截图上绘制箭头（使用逻辑坐标）
            self._draw_arrow(
                screenshot,
                from_x_mouse,
                from_y_mouse,
                to_x_mouse,
                to_y_mouse,
                left_mouse,
                top_mouse,
            )

            # 保存截图
            screenshot_filename = f"drag_screen_shot{self.screenshot_counter + 1}.png"
            return self._save_screenshot(screenshot, screenshot_filename)
        except Exception:
            # 静默失败，避免中断录制
            return None

    # ========== 私有方法 ==========

    def _capture_screenshot(
        self, left_mouse: int, top_mouse: int, width_mouse: int, height_mouse: int
    ) -> Optional[Image.Image]:
        """
        捕获截图区域

        Args:
            left_mouse: 左边界（逻辑坐标）
            top_mouse: 上边界（逻辑坐标）
            width_mouse: 宽度（逻辑坐标）
            height_mouse: 高度（逻辑坐标）

        Returns:
            截图图像，如果失败则返回None
        """
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning)
                return pyautogui.screenshot(
                    region=(left_mouse, top_mouse, width_mouse, height_mouse)
                )
        except Exception:
            return None

    def _save_screenshot(self, screenshot: Image.Image, filename: str) -> Optional[str]:
        """
        保存截图到文件

        Args:
            screenshot: 截图图像
            filename: 文件名

        Returns:
            截图文件名，如果保存失败则返回None
        """
        try:
            self.screenshot_counter += 1
            screenshot_path = os.path.join(self.screenshots_dir, filename)
            screenshot.save(screenshot_path)
            return filename
        except Exception:
            return None

    def _calculate_screenshot_region(
        self,
        click_x_mouse: int,
        click_y_mouse: int,
    ) -> Tuple[int, int, int, int]:
        """
        计算截图区域坐标（逻辑坐标）

        Args:
            click_x_mouse: 点击位置的X坐标（鼠标坐标，逻辑坐标）
            click_y_mouse: 点击位置的Y坐标（鼠标坐标，逻辑坐标）

        Returns:
            截图区域 (left, top, width, height)，单位为逻辑坐标
        """
        # 如果截图大小为-1，捕获整个屏幕
        if self.screenshot_size == -1:
            return (0, 0, MOUSE_SCREEN_WIDTH, MOUSE_SCREEN_HEIGHT)

        # 计算以点击位置为中心的正方形区域（逻辑坐标）
        desired_size_mouse = self.screenshot_size

        # 计算理想位置（以点击点为中心）
        ideal_left_mouse = click_x_mouse - desired_size_mouse // 2
        ideal_top_mouse = click_y_mouse - desired_size_mouse // 2

        # 调整位置和大小，确保不超出屏幕边界
        left_mouse = max(
            0, min(ideal_left_mouse, MOUSE_SCREEN_WIDTH - desired_size_mouse)
        )
        top_mouse = max(
            0, min(ideal_top_mouse, MOUSE_SCREEN_HEIGHT - desired_size_mouse)
        )
        width_mouse = min(desired_size_mouse, MOUSE_SCREEN_WIDTH - left_mouse)
        height_mouse = min(desired_size_mouse, MOUSE_SCREEN_HEIGHT - top_mouse)

        return (left_mouse, top_mouse, width_mouse, height_mouse)

    def _validate_and_prepare_screenshot_region(
        self, x_mouse: int, y_mouse: int
    ) -> bool:
        """
        验证坐标并准备截图目录

        Args:
            x_mouse: X坐标（鼠标坐标，逻辑坐标）
            y_mouse: Y坐标（鼠标坐标，逻辑坐标）

        Returns:
            如果坐标有效返回True，否则返回False
        """
        # 早期检查：如果位置超出屏幕边界，跳过截图
        if (
            x_mouse < 0
            or y_mouse < 0
            or x_mouse >= MOUSE_SCREEN_WIDTH
            or y_mouse >= MOUSE_SCREEN_HEIGHT
        ):
            return False

        # 确保截图目录存在
        if self.screenshots_dir:
            os.makedirs(self.screenshots_dir, exist_ok=True)

        return True

    def _draw_click_marker(
        self,
        screenshot: Image.Image,
        click_x_mouse: int,
        click_y_mouse: int,
        left_mouse: int,
        top_mouse: int,
    ) -> None:
        """
        在截图上绘制点击位置标记（红色圆圈，包含内外两层）

        Args:
            screenshot: 截图图像
            click_x_mouse: 点击位置的X坐标（逻辑坐标）
            click_y_mouse: 点击位置的Y坐标（逻辑坐标）
            left_mouse: 截图区域的左边界（逻辑坐标）
            top_mouse: 截图区域的上边界（逻辑坐标）
        """
        # 计算点击位置相对于截图的位置（逻辑坐标）
        relative_x = click_x_mouse - left_mouse
        relative_y = click_y_mouse - top_mouse

        # 在截图上绘制红色圆圈
        draw = ImageDraw.Draw(screenshot)

        # 外层大圆
        outer_radius = 20
        outer_bbox = [
            relative_x - outer_radius,
            relative_y - outer_radius,
            relative_x + outer_radius,
            relative_y + outer_radius,
        ]
        draw.ellipse(outer_bbox, outline="red", width=2)

        # 内层小圆
        inner_radius = 5
        inner_bbox = [
            relative_x - inner_radius,
            relative_y - inner_radius,
            relative_x + inner_radius,
            relative_y + inner_radius,
        ]
        draw.ellipse(inner_bbox, outline="red", width=2)

    def _draw_arrow(
        self,
        screenshot: Image.Image,
        start_x_mouse: int,
        start_y_mouse: int,
        end_x_mouse: int,
        end_y_mouse: int,
        left_mouse: int,
        top_mouse: int,
    ) -> None:
        """
        在截图上绘制箭头（从起点到终点）

        Args:
            screenshot: 截图图像
            start_x_mouse: 起点X坐标（逻辑坐标）
            start_y_mouse: 起点Y坐标（逻辑坐标）
            end_x_mouse: 终点X坐标（逻辑坐标）
            end_y_mouse: 终点Y坐标（逻辑坐标）
            left_mouse: 截图区域的左边界（逻辑坐标）
            top_mouse: 截图区域的上边界（逻辑坐标）
        """
        draw = ImageDraw.Draw(screenshot)

        # 计算相对于截图的位置（逻辑坐标）
        start_rel_x = start_x_mouse - left_mouse
        start_rel_y = start_y_mouse - top_mouse
        end_rel_x = end_x_mouse - left_mouse
        end_rel_y = end_y_mouse - top_mouse

        # 绘制箭头线
        draw.line(
            [(start_rel_x, start_rel_y), (end_rel_x, end_rel_y)],
            fill="red",
            width=3,
        )

        # 计算箭头角度
        angle = math.atan2(end_rel_y - start_rel_y, end_rel_x - start_rel_x)
        arrow_length = 15  # 箭头长度
        arrow_angle = math.pi / 6  # 箭头角度（30度）

        # 计算箭头两个点的位置
        arrow_x1 = end_rel_x - arrow_length * math.cos(angle - arrow_angle)
        arrow_y1 = end_rel_y - arrow_length * math.sin(angle - arrow_angle)
        arrow_x2 = end_rel_x - arrow_length * math.cos(angle + arrow_angle)
        arrow_y2 = end_rel_y - arrow_length * math.sin(angle + arrow_angle)

        # 绘制箭头
        draw.line([(end_rel_x, end_rel_y), (arrow_x1, arrow_y1)], fill="red", width=3)
        draw.line([(end_rel_x, end_rel_y), (arrow_x2, arrow_y2)], fill="red", width=3)

        # 在起点和终点画圆圈标记
        circle_radius = 5
        # 起点圆圈
        start_bbox = [
            start_rel_x - circle_radius,
            start_rel_y - circle_radius,
            start_rel_x + circle_radius,
            start_rel_y + circle_radius,
        ]
        draw.ellipse(start_bbox, outline="red", width=2)
        # 终点圆圈
        end_bbox = [
            end_rel_x - circle_radius,
            end_rel_y - circle_radius,
            end_rel_x + circle_radius,
            end_rel_y + circle_radius,
        ]
        draw.ellipse(end_bbox, outline="red", width=2)

    def _format_key_name(self, key: Any) -> str:
        """
        格式化键名为字符串

        Args:
            key: 键对象或字符串

        Returns:
            格式化后的键名
        """
        if isinstance(key, str):
            return key
        try:
            return self.key_map[key]
        except KeyError:
            # 'Key.backspace' 如果不在self.key_map里，那就用backspace
            return str(key)[4:]

    def _handle_scroll_axis(self, scroll_value: int) -> None:
        """
        处理单个轴的滚动值

        Args:
            scroll_value: 滚动值
        """
        if scroll_value != 0:
            self.total_scroll = self.total_scroll + scroll_value
        else:
            if self.total_scroll != 0:
                self.print_line_list.append(
                    f"mouse_operator.safe_scroll({self.total_scroll})"
                )
            self.total_scroll = 0

    def _generate_click_code(
        self, x_mouse: int, y_mouse: int, button: Optional[Button] = None
    ) -> str:
        """
        生成点击代码行

        Args:
            x_mouse: 点击X坐标（鼠标坐标，逻辑坐标）
            y_mouse: 点击Y坐标（鼠标坐标，逻辑坐标）
            button: 鼠标按钮类型，None表示左键

        Returns:
            生成的代码行字符串
        """
        # 确定按钮类型
        if button == Button.right:
            click_method = "pyautogui.rightClick"
        elif button == Button.middle:
            click_method = "pyautogui.middleClick"
        else:
            # 左键或None
            if self.tolerance > 0:
                pixel = self.pixel_before_press
                return (
                    f"mouse_operator.safe_click({x_mouse}, {y_mouse}, "
                    f"pixel=({pixel[0]}, {pixel[1]}, {pixel[2]}), tolerance={self.tolerance})"
                )
            else:
                click_method = "pyautogui.click"

        return f"{click_method}({x_mouse}, {y_mouse})"

    def _handle_single_click(
        self,
        x_mouse: int,
        y_mouse: int,
        now_click_print: str,
        screenshot_filename: Optional[str],
        button: Optional[Button] = None,
    ) -> None:
        """
        处理单击事件

        Args:
            x_mouse: 点击X坐标（鼠标坐标，逻辑坐标）
            y_mouse: 点击Y坐标（鼠标坐标，逻辑坐标）
            now_click_print: 当前点击的代码行
            screenshot_filename: 截图文件名
            button: 鼠标按钮类型，None表示左键
        """
        now_click_print_time = time.time()

        # 如果距离上次点击时间超过0.5秒，直接添加
        if now_click_print_time - self.last_click_print_time > 0.5:
            self.print_line_list.append(now_click_print)
            if screenshot_filename:
                self.screenshot_map[now_click_print] = screenshot_filename
        else:
            # 如果距离上次点击时间很短，检查是否是双击（仅左键支持双击）
            if now_click_print == self.last_click_print and button in (
                None,
                Button.left,
            ):
                # 移除之前的点击，添加双击
                prev_line = self.print_line_list.pop()
                if prev_line in self.screenshot_map:
                    del self.screenshot_map[prev_line]
                double_click_line = f"pyautogui.doubleClick({x_mouse}, {y_mouse})"
                self.print_line_list.append(double_click_line)
                if screenshot_filename:
                    self.screenshot_map[double_click_line] = screenshot_filename
            else:
                # 不同的点击位置或非左键，正常添加
                self.print_line_list.append(now_click_print)
                if screenshot_filename:
                    self.screenshot_map[now_click_print] = screenshot_filename

        self.last_click_print_time = time.time()
        self.last_click_print = now_click_print


if __name__ == "__main__":
    result = MainRecorder().start_listen()
    # print(result)
