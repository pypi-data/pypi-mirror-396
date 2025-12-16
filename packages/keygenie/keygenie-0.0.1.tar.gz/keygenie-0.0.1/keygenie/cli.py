"""命令行接口模块"""

import sys
import argparse
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from keygenie.recoder import MainRecorder


def generate_markdown(
    md_file: Path,
    code_lines: List[str],
    screenshot_map: Dict[str, str],
    screenshots_dir_name: str,
) -> None:
    """
    生成包含代码块和截图的Markdown文件

    Args:
        md_file: Markdown文件路径
        code_lines: 代码行列表
        screenshot_map: 代码行到截图文件名的映射
        screenshots_dir_name: 截图目录名称
    """
    with open(md_file, "w", encoding="utf-8") as f:
        for line in code_lines:
            # 处理多行import语句
            if "\n" in line:
                # 这是import块，在markdown中跳过
                continue

            if not line.strip():
                continue

            # 检查这一行是否有截图
            line_stripped = line.strip()
            screenshot_filename = screenshot_map.get(line_stripped)
            if screenshot_filename:
                # 这是点击操作，添加截图
                screenshot_path = f"{screenshots_dir_name}/{screenshot_filename}"
                f.write(f"![]({screenshot_path})\n\n")
                f.write("```python\n")
                f.write(f"{line_stripped}\n")
                f.write("```\n\n")
                f.write("---\n")
            else:
                # 普通代码行
                f.write("```python\n")
                f.write(f"{line_stripped}\n")
                f.write("```\n\n")
                f.write("---\n")


def _reset_recorder(
    recorder: MainRecorder, screenshots_dir: Path, tolerance: int
) -> None:
    """
    重置录制器状态（用于新的录制会话）

    由于MainRecorder是单例，需要手动更新属性以支持新的录制会话。

    Args:
        recorder: 录制器实例
        screenshots_dir: 截图目录路径
        tolerance: 像素匹配容差值
    """
    recorder.screenshots_dir = str(screenshots_dir)
    recorder.tolerance = tolerance
    recorder.print_line_list = []
    recorder.screenshot_map = {}
    recorder.screenshot_counter = 0
    recorder.char_buffer = ""
    recorder.last_char_time = 0


def record_command(args: argparse.Namespace) -> int:
    """
    处理 kg record 命令

    Args:
        args: 命令行参数

    Returns:
        退出码，0表示成功
    """
    # 获取录制目录，默认为 ./keygenie_records
    record_dir = (
        Path(args.directory) if args.directory else Path.cwd() / "keygenie_records"
    )
    record_dir.mkdir(parents=True, exist_ok=True)

    # 创建时间戳子目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = record_dir / timestamp
    session_dir.mkdir(parents=True, exist_ok=True)

    # 创建截图目录
    screenshots_dir = session_dir / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    print(f"Recording session started. Session directory: {session_dir}")
    print("Press Ctrl+C or press 'q' to finish recording...")

    # 开始录制
    recorder = MainRecorder(
        tolerance=args.tolerance,
        screenshots_dir=str(screenshots_dir),
    )
    # 为新录制会话重置状态
    _reset_recorder(recorder, screenshots_dir, args.tolerance)

    try:
        code_lines = recorder.start_listen()
    except KeyboardInterrupt:
        print("\nRecording interrupted by user.")
        code_lines = recorder.print_line_list
    except Exception as e:
        print(f"\nRecording stopped: {e}")
        code_lines = recorder.print_line_list

    # 将代码写入Python文件
    python_file = session_dir / "record.py"
    with open(python_file, "w", encoding="utf-8") as f:
        for line in code_lines:
            f.write(line + "\n")

    # 生成Markdown文件
    md_file = session_dir / "record.md"
    generate_markdown(
        md_file, code_lines, recorder.screenshot_map, screenshots_dir.name
    )

    print(f"\nRecording saved to: {python_file}")
    print(f"Markdown file saved to: {md_file}")
    return 0


def _find_latest_record_file(record_dir: Path) -> Optional[Path]:
    """
    Find the most recent record.py file in the record directory

    Uses directory name timestamp (YYYYMMDD_HHMMSS) to determine the latest recording.

    Args:
        record_dir: Directory containing recording sessions

    Returns:
        Path to the most recent record.py file, or None if not found
    """
    if not record_dir.exists():
        return None

    record_files = []
    for session_dir in record_dir.iterdir():
        if session_dir.is_dir():
            record_file = session_dir / "record.py"
            if record_file.exists():
                # Try to parse timestamp from directory name (YYYYMMDD_HHMMSS)
                try:
                    timestamp = datetime.strptime(session_dir.name, "%Y%m%d_%H%M%S")
                    record_files.append((timestamp, record_file))
                except ValueError:
                    # If directory name is not in expected format, use modification time as fallback
                    record_files.append(
                        (
                            datetime.fromtimestamp(record_file.stat().st_mtime),
                            record_file,
                        )
                    )

    if not record_files:
        return None

    # Sort by timestamp (most recent first) and return the first one
    record_files.sort(reverse=True, key=lambda x: x[0])
    return record_files[0][1]


def replay_command(args: argparse.Namespace) -> int:
    """
    Handle kg replay command

    Args:
        args: Command line arguments

    Returns:
        Exit code, 0 for success
    """
    if args.file:
        # Use provided file path
        python_file = Path(args.file)
        if not python_file.exists():
            print(f"Error: File not found: {python_file}")
            return 1
        if not python_file.is_file():
            print(f"Error: Not a file: {python_file}")
            return 1
    else:
        # Find the latest record.py file
        record_dir = (
            Path(args.directory) if args.directory else Path.cwd() / "keygenie_records"
        )
        python_file = _find_latest_record_file(record_dir)
        if python_file is None:
            print(f"Error: No record.py file found in {record_dir}")
            print("Please run 'kg record' first or specify a file path.")
            return 1
        print(f"Found latest recording: {python_file}")

    # Execute the Python file
    print(f"Replaying: {python_file}")
    print("Press ESC or move mouse to screen edge to stop playback...")

    try:
        result = subprocess.run(
            [sys.executable, str(python_file)],
            check=False,
        )
        return result.returncode
    except KeyboardInterrupt:
        print("\nPlayback interrupted by user.")
        return 130  # Standard exit code for Ctrl+C
    except Exception as e:
        print(f"Error executing file: {e}")
        return 1


def main() -> int:
    """
    主函数，解析命令行参数并执行相应命令

    Returns:
        退出码，0表示成功，1表示失败
    """
    parser = argparse.ArgumentParser(
        prog="kg", description="KeyGenie CLI - Mouse and Keyboard Recorder"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # record命令
    record_parser = subparsers.add_parser(
        "record", help="Start recording mouse and keyboard actions"
    )
    record_parser.add_argument(
        "-d",
        "--directory",
        type=str,
        default=None,
        help="Directory to save recordings (default: ./keygenie_records)",
    )
    record_parser.add_argument(
        "-t",
        "--tolerance",
        type=int,
        default=10,
        help="Pixel matching tolerance for safe_click (default: 10, set to 0 to disable)",
    )

    # replay command
    replay_parser = subparsers.add_parser(
        "replay", help="Replay recorded mouse and keyboard actions"
    )
    replay_parser.add_argument(
        "file",
        nargs="?",
        type=str,
        default=None,
        help="Path to Python file to replay (default: latest record.py)",
    )
    replay_parser.add_argument(
        "-d",
        "--directory",
        type=str,
        default=None,
        help="Directory to search for recordings (default: ./keygenie_records)",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "record":
        return record_command(args)
    elif args.command == "replay":
        return replay_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
