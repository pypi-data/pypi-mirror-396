摄像头小程序实时预览出图时间统计工具

本项目用于测试摄像头小程序实时预览出图时间，并将每次测试的结果（含不出图的情况）汇总成友好的报表和明细列表，便于后续分析。

## 功能概览

1. **自动化触发播放/出图**：利用 `uiautomator2` 控制设备进入指定摄像头预览并点击播放按钮。
2. **黑屏检测**：通过裁剪预览区域并计算平均亮度，判断是否真正出图。
3. **耗时统计**：多次执行测试，将成功与失败（不出图）记录到列表。
4. **结果导出**：以文本或 CSV 形式保存统计结果，包含平均值、最大/最小值、不出图率等指标。

## 目录结构

```
anjia_test/
├── anjia_test/               # 可发布的 Python 包（导入名：anjia_test）
│   ├── __init__.py
│   ├── cli.py                # 命令行入口：anjia-test
│   └── utils/
│       ├── notify_wx.py
│       ├── time_count.py
│       └── time_statistic.py
├── requirements.txt          # 依赖包
├── pyproject.toml            # 打包/发布配置
└── README.md
```

## 环境要求

- Python 3.9+
- 已开启调试模式并能通过 USB/Wi-Fi 连接的安卓设备
- 电脑端安装了与设备匹配的 ADB 驱动

## 安装依赖

```bash
pip install -r requirements.txt
```

## 快速开始

1. **连接设备**：确保安卓设备与电脑连接，`uiautomator2` 能够正常识别。
2. **安装（开发模式）**：
   ```bash
   pip install -e .
   ```
3. **启动命令行工具**：
   ```bash
   anjia-test -c 10 -n "单目摄像头A" -t 30 -f csv -o result/test.txt -w "<wecom_webhook>"
   ```
4. **查看输出**：程序会在控制台打印每次测试的耗时，并在 `result/` 目录下生成带时间戳的统计文件（文本或 CSV）。

## 自定义用法

- 调整测试次数或最大等待时间：
  ```python
  from anjia_test import time_statistics, save_time_statistics
  import uiautomator2 as u2
  
  d = u2.connect()
  time_data = time_statistics(device=d, count=5, camera_name="单目摄像头A", overdue_time=30)
  save_time_statistics(time_statistics=time_data, file_path="result/test.txt", format_type="csv", overdue_time=30)
  ```
- 若原始耗时单位为毫秒，可在 `save_time_statistics` 中指定 `time_unit="milliseconds"`，函数会自动转换为秒并保持统计正确。

## 输出示例

生成的文本报告包含：
- 总测试次数、成功次数、不出图次数、不出图率
- 有效耗时的总计、平均值、最大值、最小值
- 每次测试的状态与原始耗时值

CSV 文件在上述内容外，还会追加原始秒值和毫秒值，方便进一步分析。

---
如需扩展更多指标（例如失败截图保存、AI 识别等），可基于 `utils/time_count.py` 与 `utils/time_statistic.py` 进行定制。
