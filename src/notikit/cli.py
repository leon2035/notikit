"""notikit 命令行接口"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="notikit",
        description="轻量级通知工具 - 从命令行发送多渠道通知",
    )
    parser.add_argument("message", nargs="?", help="要发送的消息内容")
    parser.add_argument(
        "-c", "--channels",
        help="指定发送渠道，逗号分隔（如 lark,bark）",
    )
    parser.add_argument(
        "--config",
        help="指定配置文件路径",
    )
    parser.add_argument(
        "-v", "--version",
        action="store_true",
        help="显示版本号",
    )

    args = parser.parse_args(argv)

    if args.version:
        from importlib.metadata import version
        print(f"notikit {version('notikit')}")
        return

    if not args.message:
        parser.error("请提供消息内容")

    from notikit import Notikit
    from notikit.exceptions import NotikitError

    try:
        config_path = Path(args.config) if args.config else None
        nk = Notikit(config_path=config_path)
        channels = args.channels.split(",") if args.channels else None
        nk.notify(args.message, channels=channels)
    except NotikitError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
