import io
import time

from PIL import Image


def readable_time(ts):
    """将时间戳转换为可读字符串。"""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))


def is_black_screen(img):
    """判断截图是否为黑屏。"""
    gray_img = img.convert("L")
    pixels = list(gray_img.getdata())
    avg_brightness = sum(pixels) / len(pixels)
    return avg_brightness < 10


def time_count(device, overdue_time):
    """测量播放按钮触发到画面出现的时间。"""
    d = device

    preview_area = d.xpath('//*[@resource-id="camera"]')
    play_btn = d.xpath('(//android.widget.Image)[9]')

    preview_area.wait(timeout=10)
    play_btn.wait(timeout=10)

    preview_bounds = preview_area.get().bounds

    start_time = time.time()
    play_btn.click()

    print(f"点击播放时间为：{readable_time(start_time)}")

    cost_time = None
    n = 0
    while overdue_time > 0:
        screenshot_bytes = d.screenshot()
        if isinstance(screenshot_bytes, bytes):
            full_img = Image.open(io.BytesIO(screenshot_bytes))
        else:
            full_img = screenshot_bytes
        preview_img = full_img.crop(preview_bounds)
        n += 1

        if not is_black_screen(preview_img):
            end_time = time.time()
            print(f"第{n}次截图判断：")
            print(f"出图时间为：{readable_time(end_time)}")
            cost_time = end_time - start_time
            break

        print(f"第{n}次截图判断：未出图  {readable_time(time.time())}")
        time.sleep(0.5)
        overdue_time -= 0.5

    return cost_time


def time_statistics(device, count: int, camera_name: str, overdue_time=30):
    """多次执行出图检测并汇总耗时。"""
    d = device
    time_statistic = []

    for i in range(count):
        for _attempt in range(3):
            try:
                d.xpath(f'//*[@text="{camera_name}"]/../following-sibling::*[1]').click()
                print("进入预览界面成功")
                break
            except Exception:
                print("进入预览界面失败")

        time_track = time_count(d, overdue_time)
        if time_track:
            print(f"第{i + 1}次测试耗时：{time_track:.2f}秒")
        else:
            print(f"第{i + 1}次测试耗时：超过{overdue_time}秒未出图")
        time_statistic.append(time_track)
        d.press("back")
        time.sleep(2)

    return time_statistic
