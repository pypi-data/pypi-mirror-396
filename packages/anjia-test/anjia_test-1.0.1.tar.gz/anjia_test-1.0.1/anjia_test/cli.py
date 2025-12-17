from __future__ import annotations

import argparse
import os

import uiautomator2 as u2

from .utils.time_count import time_statistics
from .utils.time_statistic import save_time_statistics
from .utils.notify_wx import send_wecom_text_for_file


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="anjia-test",
        description="出图耗时统计脚本",
        epilog="示例：anjia-test -c 10 -n '单目摄像头A' -t 30 -f csv -o result/test.txt -w <wecom_webhook>",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-c", "--count", type=int, default=1, help="测试次数")
    parser.add_argument("-n", "--camera_name", type=str, help="摄像头名称")
    parser.add_argument("-t", "--overdue_time", type=int, default=30, help="超时时间")
    parser.add_argument("-f", "--file_format", type=str, default="text", help="文件格式,支持text,csv")
    parser.add_argument("-o", "--output_path", type=str, help="输出路径")
    parser.add_argument("-w", "--wx_webhook", type=str, help="微信webhook地址")
    parser.add_argument("-q", "--quite", action="store_true", help="是否静默模式")
    parser.add_argument("-s", "--serial", type=str, help="设备序列号")
    return parser.parse_args()


def main() -> None:
    args = get_args()

    if args.serial:
        d = u2.connect(args.serial)
    else:
        d = u2.connect()

    count = args.count
    if args.camera_name is None:
        try:
            camera_name = d.xpath("(//android.view.View)[19]/*[1]").get_text()
            print(f"获取第一个摄像头名称成功：{camera_name}")
        except Exception:
            raise RuntimeError("获取摄像头名称失败，请通过 -n/--camera_name 手动输入")
    else:
        camera_name = args.camera_name

    overdue_time = args.overdue_time
    file_format = args.file_format

    if args.output_path is None:
        output_path = f"result/{camera_name}_time_statistics.txt"
    else:
        output_path = args.output_path

    time_data = time_statistics(device=d, count=count, camera_name=camera_name, overdue_time=overdue_time)
    save_time_statistics(
        time_statistics=time_data,
        file_path=output_path,
        format_type=file_format,
        overdue_time=overdue_time,
    )

    webhook = os.getenv("WX_WEBHOOK_URL") or args.wx_webhook
    if webhook and args.quite:
        send_wecom_text_for_file(webhook_url=webhook, file_path=output_path)


if __name__ == "__main__":
    main()
