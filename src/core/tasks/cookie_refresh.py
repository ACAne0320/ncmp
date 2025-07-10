import os
from typing import Dict, Optional, Tuple

from ...utils.auth import AuthService
from ...utils.github import GitHubService
from ...utils.logger import Logger
from ...utils.notification import NotificationService


class CookieRefreshTask:
    def __init__(self, logger: Logger, notifier: Optional[NotificationService] = None):
        self.logger = logger
        self.notifier = notifier
        self.auth_service = AuthService(logger)
        self.github_service = GitHubService(logger)
        
    def execute(self) -> bool:
        """执行Cookie刷新任务"""
        try:
            self.logger.info("开始执行Cookie刷新任务")
            
            # 获取登录凭据
            phone = os.environ.get("NETEASE_PHONE")
            password = os.environ.get("NETEASE_PASSWORD")
            md5_password = os.environ.get("NETEASE_MD5_PASSWORD")
            
            if not phone:
                self.logger.error("未设置手机号，无法执行自动登录")
                if self.notifier:
                    self.notifier.send_notification(
                        "网易云音乐合伙人 - 自动登录失败",
                        "未设置手机号，请检查NETEASE_PHONE环境变量"
                    )
                return False
                
            if not md5_password and not password:
                self.logger.error("未设置密码，无法执行自动登录")
                if self.notifier:
                    self.notifier.send_notification(
                        "网易云音乐合伙人 - 自动登录失败",
                        "未设置密码，请检查NETEASE_MD5_PASSWORD或NETEASE_PASSWORD环境变量"
                    )
                return False
                
            # 执行登录，优先使用MD5密码，如果使用明文密码，则自动转换为MD5
            success, cookies = self.auth_service.login(
                phone=phone,
                password=password if not md5_password else None,
                md5_password=md5_password
            )
            
            if not success or not cookies:
                self.logger.error("登录失败，无法获取新的Cookie")
                if self.notifier:
                    self.notifier.send_notification(
                        "网易云音乐合伙人 - 自动登录失败",
                        "登录过程失败，请检查登录凭据是否正确"
                    )
                return False
                
            # 更新GitHub Secrets
            # 这里需要转换Cookie键名，使其与GitHub Actions中使用的名称匹配
            secrets_to_update = {
                "MUSIC_U": cookies.get("Cookie_MUSIC_U", ""),
                "CSRF": cookies.get("Cookie___csrf", "")
            }
            
            update_success = self.github_service.update_cookies(secrets_to_update)
            
            if update_success:
                self.logger.info("成功更新GitHub Secrets中的Cookie")
                if self.notifier:
                    self.notifier.send_notification(
                        "网易云音乐合伙人 - Cookie更新成功",
                        "已成功获取新的Cookie并更新到GitHub Secrets"
                    )
                return True
            else:
                self.logger.error("更新GitHub Secrets失败")
                if self.notifier:
                    self.notifier.send_notification(
                        "网易云音乐合伙人 - Cookie更新失败",
                        "登录成功但更新GitHub Secrets时失败"
                    )
                return False
                
        except Exception as e:
            error_message = f"Cookie刷新任务执行异常: {str(e)}"
            self.logger.error(error_message)
            
            if self.notifier:
                self.notifier.send_notification(
                    "网易云音乐合伙人 - Cookie刷新异常",
                    error_message
                )
                
            return False
