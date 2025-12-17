import time
import logging

import requests
from flask import current_app, request

from lesscode_flask.model.response_result import ResponseResult
from lesscode_flask.model.user import flask_login
from lesscode_flask.utils.fs_util import fs_webhook
from lesscode_flask.utils.redis.redis_helper import RedisHelper

logger = logging.getLogger(__name__)


class RateLimitHandler:
    """
    限流后的处理函数实现
    """

    def __init__(self, req, delay: float, excess: float):
        """
         初始化
        :param req:
        :param delay: 延迟时间
        :param excess: 超出数量
        """
        self.req = req
        self.delay = delay
        self.excess = excess

    def response_handler(self):
        # 如果配置了飞书 webhook URL，则发送告警通知
        # 收集用户相关信息
        current_user = flask_login.current_user
        fs_oam_service_url = current_app.config.get("FS_OAM_SERVICE_URL")
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        lock_account_url = (
            f"{fs_oam_service_url}/icp/authUser/lock_account?id={current_user.id}"
        )
        logout_url = f"{fs_oam_service_url}/icp/oauth/logout_token?token={token}"

        # 发送 GET 请求到 lock_account_url
        try:
            lock_response = requests.get(lock_account_url, timeout=30)
            logger.info(
                "Lock account request sent, status: %s", lock_response.status_code
            )
        except requests.RequestException as e:
            logger.error("Failed to send lock account request: %s", str(e))

        # 发送 GET 请求到 logout_url
        try:
            logout_response = requests.get(logout_url, timeout=30)
            logger.info("Logout request sent, status: %s", logout_response.status_code)
        except requests.RequestException as e:
            logger.error("Failed to send logout request: %s", str(e))

        limit_fs_webhook_url = current_app.config.get("LIMIT_FS_WEBHOOK_URL")
        # 如果配置了飞书 webhook URL，则发送告警通知
        if limit_fs_webhook_url:
            content = []
            current_user = flask_login.current_user
            # 收集用户相关信息
            content.append(
                {"tag": "text", "text": f"用户名称：{current_user.display_name}\n"}
            )
            phone_no = (
                current_user.phone_no if current_user.phone_no is not None else "-"
            )
            content.append({"tag": "text", "text": f"手机号：{phone_no}\n"})
            content.append({"tag": "text", "text": f"用户IP：{request.remote_addr}\n"})
            content.append({"tag": "text", "text": f"资源地址：{request.path}\n"})
            token = request.headers.get("Authorization", "").replace("Bearer ", "")
            if token:
                FS_OAM_SERVICE_URL = current_app.config.get("FS_OAM_SERVICE_URL")
                content.append({"tag": "text", "text": "运维处理："})
                # lock_account_url = f"{FS_OAM_SERVICE_URL}/icp/authUser/lock_account?id={current_user.id}"
                # url = f"{FS_OAM_SERVICE_URL}/icp/oauth/logout_token?token={token}"
                # content.append({"tag": "a","text": "强制下线","href": f"{url}"})
                # content.append({"tag": "a", "text": "    禁止登录    ", "href": f"{lock_account_url}"})
                ban_ip_url = f"{FS_OAM_SERVICE_URL}/icp/accessLog/ban_ip?ip={request.remote_addr}"
                content.append({"tag": "a", "text": "封禁IP ", "href": f"{ban_ip_url}"})

            # 发送飞书 webhook 告警
            fs_webhook(limit_fs_webhook_url, "触发频率限流告警", content)
        return ResponseResult.fail(
            status_code="403", http_code="403", message="请求过于频繁，请稍后再试！"
        )
