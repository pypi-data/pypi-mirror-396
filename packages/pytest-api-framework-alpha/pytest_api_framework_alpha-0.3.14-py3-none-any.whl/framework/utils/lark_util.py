import base64
import hmac
import hashlib
import time
from datetime import datetime

import json
import requests


class LarkUtil:
    def __init__(self, webhook: dict):
        self.webhook = webhook
        self.url = self.webhook.get("url")
        self.secret = self.webhook.get("secret")
        self.at_ids = self.webhook.get("open_ids") or None
        self.headers = {"Content-Type": "application/json"}

    @staticmethod
    def gen_sign(timestamp, secret):
        """生成HMAC签名"""
        # 拼接timestamp和secret
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
        # 对结果进行base64处理
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return sign

    def send_text(self, text: str, at_ids: list[str] = None):
        data = {
            "msg_type": "text",
            "content": {"text": text},
        }
        if at_ids:
            data["at"] = {"open_ids": at_ids}
        if self.secret:
            timestamp = str(int(time.time()))
            data["sign"] = LarkUtil.gen_sign(timestamp, self.secret)
            data["timestamp"] = timestamp

        return requests.post(self.url, data=json.dumps(data), headers=self.headers)

    def send_markdown(self, title: str, markdown_text: str, at_ids: list[str] = None):
        """发送 Markdown 消息"""

        data = {
            "msg_type": "interactive",
            "card": {
                "header": {
                    "template": "blue",
                    "title": {"tag": "plain_text", "content": title}
                },
                "elements": [
                    {
                        "tag": "markdown",
                        "content": markdown_text
                    }
                ]
            }
        }
        if at_ids:
            data["at"] = {"open_ids": at_ids}
        if self.secret:
            timestamp = str(int(time.time()))
            data["sign"] = LarkUtil.gen_sign(timestamp, self.secret)
            data["timestamp"] = timestamp
        return requests.post(self.url, headers=self.headers, data=json.dumps(data))

    def send_test_report(self, total: int, passed: int, failed: int, skipped: int, report_url: str = None,
                         job_name: str = None, env=None):
        """自动化测试结果消息（Markdown）"""
        try:
            pass_rate = round(passed / (total - skipped) * 100, 2)
        except ZeroDivisionError:
            pass_rate = 0
        markdown = f"""**执行环境：** {env}
**执行完成时间：** {datetime.now().strftime("%Y-%m-%d %X")}
**执行用例总数：** {total}
**通过用例数：** {passed}
**失败用例数：** {failed}
**跳过用例数：** {skipped}
**用例通过率：** {pass_rate}%
            """
        if report_url:
            markdown += f"\n**测试报告：** [点击查看测试报告]({report_url})"
        title = f"【自动化测试结果】-{job_name} " if job_name else "【自动化测试结果】"
        return self.send_markdown(title, markdown)