import hashlib
import hmac
import json
import time
import requests
import base64
import urllib.parse


class WebHookUtil:

    @staticmethod
    def send(url, data, secret=None):
        """
        发送Webhook请求

        Args:
            url (str): Webhook地址
            data (dict): 发送的数据
            secret (str, optional): 签名密钥

        Returns:
            dict: 响应结果
        """
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'WebHookUtil/1.0'
        }

        # 如果提供了secret，则添加签名
        if secret:
            timestamp = str(int(time.time() * 1000))
            string_to_sign = timestamp + "\n" + secret
            hmac_code = hmac.new(
                secret.encode('utf-8'),
                string_to_sign.encode('utf-8'),
                hashlib.sha256
            ).digest()
            sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

            # 将签名参数添加到URL中而不是请求头
            separator = '&' if '?' in url else '?'
            url_with_sign = f"{url}{separator}timestamp={timestamp}&sign={sign}"
        else:
            url_with_sign = url

        response = requests.post(url_with_sign, headers=headers, data=json.dumps(data), timeout=30)
        response.raise_for_status()

    @staticmethod
    def send_text(url, content, secret=None):
        """
        发送文本消息

        Args:
            url (str): Webhook地址
            content (str): 消息内容
            secret (str, optional): 签名密钥

        Returns:
            dict: 响应结果
        """
        WebHookUtil.send(url, {"msgtype": "text", "text": {"content": content}}, secret)

    @staticmethod
    def send_markdown(url, title, text, secret=None):
        """
        发送Markdown消息

        Args:
            url (str): Webhook地址
            title (str): 消息标题
            text (str): 消息文本
            secret (str, optional): 签名密钥

        Returns:
            dict: 响应结果
        """
        WebHookUtil.send(url, {"msgtype": "markdown", "markdown": {"title": title, "text": text}}, secret)

    @staticmethod
    def send_link(url, title, text, link, secret=None):
        """
        发送链接消息

        Args:
            url (str): Webhook地址
            title (str): 消息标题
            text (str): 消息文本
            link (str): 消息链接
            secret (str, optional): 签名密钥

        Returns:
            dict: 响应结果
        """
        WebHookUtil.send(url, {"msgtype": "link", "link": {"title": title, "text": text}, "messageUrl": link}, secret)

    @staticmethod
    def send_image(url, image_base64, secret=None):
        """
        发送图片消息

        Args:
            url (str): Webhook地址
            image_base64 (str): 图片
            secret (str, optional): 签名密钥

        Returns:
            dict: 响应结果
        """
        WebHookUtil.send(url, {"msgtype": "image", "image": {"base64": image_base64}}, secret)
