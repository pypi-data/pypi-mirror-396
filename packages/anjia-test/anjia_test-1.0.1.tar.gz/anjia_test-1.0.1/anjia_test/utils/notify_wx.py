"""企微机器人 webhook 通知工具。"""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, Optional

import requests


logger = logging.getLogger(__name__)


class WeComNotifier:
    """简单封装企业微信机器人 webhook 接口。

    Args:
        webhook_url (str): 企业微信机器人 webhook 地址。
        timeout (float, optional): 请求超时时间，单位秒，默认 5。
    """

    def __init__(self, webhook_url: str, timeout: float = 5.0) -> None:
        self.webhook_url = webhook_url
        self.timeout = timeout

    def _post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """发送 POST 请求并返回响应 JSON。"""

        logger.debug("发送企微通知: %s", payload)
        resp = requests.post(self.webhook_url, json=payload, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        if data.get("errcode") != 0:
            logger.error("企微通知失败: %s", data)
            raise RuntimeError(f"WeCom webhook error: {data}")
        logger.info("企微通知成功: %s", data)
        return data

    def send_text(
        self,
        content: str,
        mentioned_user_ids: Optional[Iterable[str]] = None,
        mentioned_mobile_list: Optional[Iterable[str]] = None,
    ) -> Dict[str, Any]:
        """发送文本通知。"""

        payload = {
            "msgtype": "text",
            "text": {
                "content": content,
                "mentioned_list": list(mentioned_user_ids or []),
                "mentioned_mobile_list": list(mentioned_mobile_list or []),
            },
        }
        return self._post(payload)

    def send_markdown(self, content: str) -> Dict[str, Any]:
        """发送 Markdown 通知。"""

        payload = {
            "msgtype": "markdown",
            "markdown": {"content": content},
        }
        return self._post(payload)


def read_txt_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def send_wecom_text_for_file(
    webhook_url: str,
    file_path: str,
    mentioned_user_ids: Optional[Iterable[str]] = None,
    mentioned_mobile_list: Optional[Iterable[str]] = None,
    timeout: float = 5.0,
) -> Dict[str, Any]:
    """便捷函数：发送文本通知。"""

    notifier = WeComNotifier(webhook_url=webhook_url, timeout=timeout)
    return notifier.send_text(
        read_txt_file(file_path),
        mentioned_user_ids=mentioned_user_ids,
        mentioned_mobile_list=mentioned_mobile_list,
    )


def send_wecom_text(
    webhook_url: str,
    content: str,
    mentioned_user_ids: Optional[Iterable[str]] = None,
    mentioned_mobile_list: Optional[Iterable[str]] = None,
    timeout: float = 5.0,
) -> Dict[str, Any]:
    """便捷函数：发送文本通知。"""

    notifier = WeComNotifier(webhook_url=webhook_url, timeout=timeout)
    return notifier.send_text(
        content,
        mentioned_user_ids=mentioned_user_ids,
        mentioned_mobile_list=mentioned_mobile_list,
    )


def send_wecom_markdown(
    webhook_url: str,
    content: str,
    timeout: float = 5.0,
) -> Dict[str, Any]:
    """便捷函数：发送 Markdown 通知。"""

    notifier = WeComNotifier(webhook_url=webhook_url, timeout=timeout)
    return notifier.send_markdown(content)


if __name__ == "__main__":
    demo_webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY"

    try:
        send_wecom_text(
            webhook_url=demo_webhook,
            content="测试通知：实时预览出图统计任务完成",
            mentioned_user_ids=["@all"],
        )
    except Exception as exc:
        logger.error("文本通知发送失败: %s", exc)
