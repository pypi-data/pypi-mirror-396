"""屏幕DPI和尺寸相关常量"""

import os
import tempfile

import pyautogui


def _get_screen_info() -> tuple[int, int, int, int, int]:
    """
    获取屏幕信息

    通过比较鼠标可点击点的分辨率和显示器实际分辨率来计算DPI。
    pyautogui.size()返回的是鼠标可以点击的点的分辨率（逻辑坐标），
    而screenshot返回的是显示器的实际分辨率（物理像素）。

    Returns:
        tuple: (DPI, 鼠标坐标宽度, 鼠标坐标高度, 显示器像素宽度, 显示器像素高度)

    Raises:
        AssertionError: 如果水平和垂直方向的DPI不一致
    """
    mouse_screen_w, mouse_screen_h = (
        pyautogui.size()
    )  # pyautogui.size()是鼠标可以点击的点的分辨率（逻辑坐标）
    with tempfile.TemporaryDirectory() as tmpdir:
        screenshot_img = pyautogui.screenshot(
            os.path.join(tmpdir, "all_screen.png")
        )  # screenshot 是显示器的分辨率（物理像素）
        display_pixel_w = screenshot_img.size[0]
        display_pixel_h = screenshot_img.size[1]
        screen_dpi_w = int(display_pixel_w / mouse_screen_w)
        screen_dpi_h = int(display_pixel_h / mouse_screen_h)
        assert screen_dpi_w == screen_dpi_h, "水平和垂直方向的DPI不一致"
        screen_dpi = screen_dpi_w  # 一般mac上这个值是2
    return screen_dpi, mouse_screen_w, mouse_screen_h, display_pixel_w, display_pixel_h


# 全局常量：屏幕DPI值（一般mac上这个值是2）
SCREEN_DPI: int
# 全局常量：鼠标坐标空间的宽度（逻辑坐标）
MOUSE_SCREEN_WIDTH: int
# 全局常量：鼠标坐标空间的高度（逻辑坐标）
MOUSE_SCREEN_HEIGHT: int
# 全局常量：显示器物理像素宽度
DISPLAY_PIXEL_WIDTH: int
# 全局常量：显示器物理像素高度
DISPLAY_PIXEL_HEIGHT: int

(
    SCREEN_DPI,
    MOUSE_SCREEN_WIDTH,
    MOUSE_SCREEN_HEIGHT,
    DISPLAY_PIXEL_WIDTH,
    DISPLAY_PIXEL_HEIGHT,
) = _get_screen_info()
