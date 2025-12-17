import csv
import os
from datetime import datetime
from typing import List, Optional, Union


def format_duration(seconds: Optional[float]) -> str:
    """将秒数格式化为更易读的字符串。"""
    if seconds is None:
        return "不出图"
    if seconds < 0.001:
        return f"{seconds * 1000000:.1f}μs"
    if seconds < 1:
        return f"{seconds * 1000:.2f}ms"
    if seconds < 60:
        return f"{seconds:.2f}s"
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes:.0f}min {remaining_seconds:.1f}s"


def save_time_statistics(
    time_statistics: List[Union[int, float, None]],
    file_path: str,
    format_type: str = "text",
    time_unit: str = "seconds",
    overdue_time: int = 30,
) -> None:
    """保存包含 ``None`` 值的耗时统计结果。"""

    times_in_seconds = []
    for t in time_statistics:
        if t is None:
            times_in_seconds.append(None)
        else:
            if time_unit == "milliseconds":
                times_in_seconds.append(float(t) / 1000)
            else:
                times_in_seconds.append(float(t))

    total_count = len(times_in_seconds)
    none_count = times_in_seconds.count(None)
    valid_count = total_count - none_count
    none_rate = (none_count / total_count) * 100 if total_count > 0 else 0.0

    valid_times = [t for t in times_in_seconds if t is not None]
    avg_time = sum(valid_times) / valid_count if valid_count > 0 else None
    max_time = max(valid_times) if valid_count > 0 else None
    min_time = min(valid_times) if valid_count > 0 else None
    total_valid_time = sum(valid_times) if valid_count > 0 else None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir_name, file_full = os.path.split(file_path)
    file_name, ext = os.path.splitext(file_full)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)

    if format_type == "text" or ext == ".txt":
        new_file_name = f"{file_name}_{timestamp}.txt"
        file_path = os.path.join(dir_name, new_file_name) if dir_name else new_file_name
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("=== 视频出图耗时统计报告 ===\n")
            f.write(f"总测试次数：{total_count} 次\n")
            f.write(f"出图成功次数：{valid_count} 次\n")
            f.write(f"超时{overdue_time}秒不出图次数：{none_count} 次\n")
            f.write(f"超时{overdue_time}秒不出图率：{none_rate:.2f}%\n")

            if valid_count > 0:
                f.write(f"有效耗时总计：{format_duration(total_valid_time)}\n")
                f.write(f"有效耗时平均值：{format_duration(avg_time)}\n")
                f.write(f"有效耗时最大值：{format_duration(max_time)}\n")
                f.write(f"有效耗时最小值：{format_duration(min_time)}\n")
            else:
                f.write("无有效出图耗时数据\n")

            f.write("-" * 50 + "\n")
            f.write("序号\t出图状态\t耗时\t原始值（秒）\n")
            f.write("-" * 50 + "\n")

            for idx, t in enumerate(times_in_seconds, 1):
                status = "成功" if t is not None else f"失败（超时{overdue_time}秒不出图）"
                duration_str = format_duration(t)
                raw_value = f"{t:.6f}" if t is not None else "-"
                f.write(f"{idx}\t{status}\t{duration_str}\t\t{raw_value}\n")

        print(f"纯文本格式统计已保存到：{file_path}")

    elif format_type == "csv" or ext == ".csv":
        new_file_name = f"{file_name}_{timestamp}.csv"
        file_path = os.path.join(dir_name, new_file_name) if dir_name else new_file_name
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["序号", "出图状态", "耗时", "原始值（秒）", "原始值（毫秒）"])

            for idx, t in enumerate(times_in_seconds, 1):
                if t is None:
                    status = f"失败（超时{overdue_time}秒不出图）"
                    duration_str = f"失败（超时{overdue_time}秒不出图）"
                    raw_second = "-"
                    raw_ms = "-"
                else:
                    status = "成功"
                    duration_str = format_duration(t)
                    raw_second = round(t, 6)
                    raw_ms = round(t * 1000, 3)
                writer.writerow([idx, status, duration_str, raw_second, raw_ms])

            writer.writerow([])
            writer.writerow(["统计摘要", "", "", "", ""])
            writer.writerow(["总测试次数", total_count, "", "", ""])
            writer.writerow(["出图成功次数", valid_count, "", "", ""])
            writer.writerow([f"超时{overdue_time}秒不出图次数", none_count, "", "", ""])
            writer.writerow([f"超时{overdue_time}秒不出图率(%)", f"{none_rate:.2f}", "", "", ""])

            if valid_count > 0:
                writer.writerow(["有效耗时总计", format_duration(total_valid_time), "", "", ""])
                writer.writerow(["有效耗时平均值", format_duration(avg_time), "", "", ""])
                writer.writerow(["有效耗时最大值", format_duration(max_time), "", "", ""])
                writer.writerow(["有效耗时最小值", format_duration(min_time), "", "", ""])

        print(f"CSV格式统计已保存到：{file_path}")

    else:
        raise ValueError("format_type 仅支持 'text' 或 'csv'")
