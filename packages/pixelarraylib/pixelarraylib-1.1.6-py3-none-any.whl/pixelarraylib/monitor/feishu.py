import requests
import json
import asyncio
import csv
import os
from typing import Optional


class Feishu:
    channel_map = {
        "矩阵像素订阅群": "https://open.feishu.cn/open-apis/bot/v2/hook/6e368741-ab2e-46f4-a945-5c1182303f91",
        "devtoolkit服务报警": "https://open.feishu.cn/open-apis/bot/v2/hook/b9e7cfa1-c63f-4a9f-9699-286f7316784b",
        "baymax服务报警": "https://open.feishu.cn/open-apis/bot/v2/hook/5d8d4fa6-67c4-4202-9122-389d1ec2b668",
        "videodriver服务报警": "https://open.feishu.cn/open-apis/bot/v2/hook/5359b92d-02ab-47ca-a617-58b8152eaa2d",
        "arraycut服务报警": "https://open.feishu.cn/open-apis/bot/v2/hook/e610b1e8-f867-4670-8d4d-0553f64884f0",
        "knowledgebase微服务报警": "https://open.feishu.cn/open-apis/bot/v2/hook/5f007914-235a-4287-8349-6c1dd7c70024",
        "llm微服务报警": "https://open.feishu.cn/open-apis/bot/v2/hook/54942aa6-24f1-4851-8fe9-d7c87572d00a",
        "thirdparty微服务报警": "https://open.feishu.cn/open-apis/bot/v2/hook/b1e6237a-1323-4ad9-96f4-d74de5cdc00f",
        "picturebed服务报警": "https://open.feishu.cn/open-apis/bot/v2/hook/d3c2e68c-3ed3-4832-9b66-76db5bd69b42",
        "picturetransform服务报警": "https://open.feishu.cn/open-apis/bot/v2/hook/e975aa0a-acef-4e3f-bee4-6dc507b87ebd",
        "cloudstorage服务报警": "https://open.feishu.cn/open-apis/bot/v2/hook/a632d0bc-e400-40ce-a3bb-1b9b9ee634f4",
        "deployengine服务报警": "https://open.feishu.cn/open-apis/bot/v2/hook/9a347a63-58fb-4e10-9a3d-ff4918ddb3a9",
    }

    def __init__(
        self,
        channel_name,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
    ):
        """
        description:
            初始化飞书告警客户端
        parameters:
            channel_name(str): 飞书频道名称
            app_id(Optional[str]): 应用ID，可选
            app_secret(Optional[str]): 应用密钥，可选
        """
        self.webhook_url = self.channel_map[channel_name]
        self.app_id = app_id
        self.app_secret = app_secret
        self._access_token = None

    def send(self, text):
        """
        description:
            发送文本消息到飞书群
        parameters:
            text(str): 要发送的文本内容
        return:
            success(bool): 发送是否成功
        """
        print(text)
        headers = {"Content-Type": "application/json"}
        data = {"msg_type": "text", "content": {"text": text}}
        response = requests.post(
            self.webhook_url, headers=headers, data=json.dumps(data)
        )
        return bool(
            response
            and response.json().get("StatusCode") == 0
            and response.json().get("StatusMessage") == "success"
        )

    async def send_async(self, text: str):
        """
        description:
            异步发送文本消息到飞书群
        parameters:
            text(str): 要发送的文本内容
        return:
            success(bool): 发送是否成功
        """
        return await asyncio.to_thread(self.send, text)

    def send_markdown(
        self,
        markdown_content: str,
        title: str,
        template: str = "turquoise",
    ):
        """
        description:
            发送Markdown格式的消息到飞书群
        parameters:
            markdown_content(str): Markdown格式的内容
            title(str): 消息标题
            template(str): 卡片模板颜色，默认为"turquoise"
        return:
            success(bool): 发送是否成功
        """
        headers = {"Content-Type": "application/json; charset=utf-8"}
        card = {
            "config": {"wide_screen_mode": True, "enable_forward": True},
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": template,
            },
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": markdown_content}}
            ],
        }
        payload = {"msg_type": "interactive", "card": card}
        resp = requests.post(
            self.webhook_url, headers=headers, data=json.dumps(payload)
        )
        return bool(resp.ok and resp.json().get("StatusCode") == 0)

    async def send_markdown_async(
        self,
        markdown_content: str,
        title: str,
        template: str = "turquoise",
    ):
        """
        description:
            异步发送Markdown格式的消息到飞书群
        parameters:
            markdown_content(str): Markdown格式的内容
            title(str): 消息标题
            template(str): 卡片模板颜色，默认为"turquoise"
        return:
            success(bool): 发送是否成功
        """
        return await asyncio.to_thread(
            self.send_markdown, markdown_content, title, template
        )

    def send_table(
        self,
        headers: list,
        rows: list,
        title: str,
        template: str = "turquoise",
    ):
        """
        description:
            发送表格消息到飞书群
        parameters:
            headers(list): 表头列表
            rows(list): 表格行数据列表
            title(str): 消息标题
            template(str): 卡片模板颜色，默认为"turquoise"
        return:
            success(bool): 发送是否成功
        """
        headers_req = {"Content-Type": "application/json; charset=utf-8"}
        n_cols = len(headers)
        columns = []
        for ci in range(n_cols):
            elements_in_col = []
            # 表头
            elements_in_col.append(
                {
                    "tag": "div",
                    "text": {"tag": "lark_md", "content": f"**{headers[ci]}**"},
                }
            )
            # 每一行的该列内容
            for row in rows:
                cell = row[ci] if ci < len(row) else ""
                elements_in_col.append(
                    {"tag": "div", "text": {"tag": "lark_md", "content": cell}}
                )
            columns.append(
                {
                    "tag": "column",
                    "width": "weighted",
                    "weight": 1,
                    "elements": elements_in_col,
                }
            )

        elements = [{"tag": "column_set", "columns": columns}]

        card = {
            "config": {"wide_screen_mode": True, "enable_forward": True},
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": template,
            },
            "elements": elements,
        }
        payload = {"msg_type": "interactive", "card": card}

        resp = requests.post(
            self.webhook_url, headers=headers_req, data=json.dumps(payload)
        )
        try:
            print("feishu send_table resp:", resp.status_code, resp.json())
        except Exception:
            print("feishu send_table resp:", resp.status_code, resp.text)
        return bool(resp.ok and resp.json().get("StatusCode") == 0)

    async def send_table_async(
        self,
        headers: list[str],
        rows: list[list[str]],
        title: str,
        template: str = "turquoise",
    ):
        """
        description:
            异步发送表格消息到飞书群
        parameters:
            headers(list[str]): 表头列表
            rows(list[list[str]]): 表格行数据列表
            title(str): 消息标题
            template(str): 卡片模板颜色，默认为"turquoise"
        return:
            success(bool): 发送是否成功
        """
        return await asyncio.to_thread(self.send_table, headers, rows, title, template)

    def send_file(
        self,
        file_url: Optional[str] = None,
        title: Optional[str] = None,
        template: str = "turquoise",
    ):
        """
        description:
            发送文件到飞书群
            通过文件下载链接发送包含文件下载按钮的卡片消息
        parameters:
            file_url(str): 文件下载链接（如 OSS 链接），必需参数
            title(str): 消息标题，如果为 None 则使用文件名
            template(str): 卡片模板颜色，默认 "turquoise"
        return:
            bool: 发送是否成功
        """
        if not file_url:
            print("错误：必须提供 file_url（文件下载链接）")
            return False
        headers = {"Content-Type": "application/json; charset=utf-8"}
        markdown_content = f"[点击下载文件]({file_url})"

        card = {
            "config": {"wide_screen_mode": True, "enable_forward": True},
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": template,
            },
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": markdown_content}}
            ],
        }
        payload = {"msg_type": "interactive", "card": card}

        try:
            resp = requests.post(
                self.webhook_url, headers=headers, data=json.dumps(payload)
            )
            if resp.ok:
                result = resp.json()
                return bool(result.get("StatusCode") == 0 or result.get("code") == 0)
            else:
                print(f"发送文件消息失败: {resp.status_code}, {resp.text}")
                return False
        except Exception as e:
            print(f"发送文件消息异常: {e}")
            return False

    async def send_file_async(self, file_url: str, title: str, template: str):
        """
        description:
            异步发送文件到飞书群
        parameters:
            file_url(str): 文件下载链接
            title(str): 消息标题
            template(str): 卡片模板颜色
        return:
            success(bool): 发送是否成功
        """
        return await asyncio.to_thread(self.send_file, file_url, title, template)
