import asyncio
import urllib.parse
import webbrowser
from typing import Dict, Optional, Tuple

from pixelarraythirdparty.client import AsyncClient


class GoogleLogin(AsyncClient):
    """
    Google OAuth2 登录客户端

    使用示例:
    ```
    google = GoogleLogin(api_key="your_api_key")
    user_info, success = await google.login()
    if success:
        access_token = user_info.get("access_token")
        refresh_token = user_info.get("refresh_token")
        
        # 使用refresh_token刷新access_token
        if refresh_token:
            token_data, success = await google.refresh_access_token(refresh_token)
            if success:
                new_access_token = token_data.get("access_token")
    ```
    """

    def __init__(self, api_key: str):
        super().__init__(api_key)

    async def _get_auth_url(self) -> Tuple[Optional[Dict[str, str]], bool]:
        data, success = await self._request(
            "POST", "/api/unified-login/google/auth-url"
        )
        if not success:
            return None, False
        auth_url = data.get("auth_url")
        if not auth_url:
            return None, False
        return data, True

    async def login(self, timeout: int = 180) -> Tuple[Dict, bool]:
        """
        仿 Supabase CLI 的一键登录流程：打开浏览器完成授权，
        终端端轮询等待登录结果

        :param timeout: 等待用户完成授权的超时时间（秒）
        """
        auth_data, success = await self._get_auth_url()
        if not success or not auth_data:
            return {}, False

        auth_url = auth_data.get("auth_url")
        state = auth_data.get("state") or self._extract_state(auth_url)

        if not auth_url or not state:
            return {}, False

        webbrowser.open(auth_url, new=2)

        return await self._wait_for_google_login(state, timeout)

    def _extract_state(self, auth_url: Optional[str]) -> Optional[str]:
        if not auth_url:
            return None
        try:
            parsed = urllib.parse.urlparse(auth_url)
            query = urllib.parse.parse_qs(parsed.query)
            values = query.get("state")
            if values:
                return values[0]
        except Exception:
            return None
        return None

    async def _wait_for_google_login(
        self, state: str, timeout: int
    ) -> Tuple[Dict, bool]:
        interval = 2
        total_checks = max(1, timeout // interval) if timeout > 0 else 1

        for _ in range(total_checks):
            status, response = await self._request_raw(
                "POST",
                "/api/unified-login/google/wait-login",
                json={"state": state},
            )

            if status == 200 and response.get("success") is True:
                return response.get("data", {}), True

            if status in (400, 408):
                break

            await asyncio.sleep(interval)

        return {}, False

    async def refresh_access_token(self, refresh_token: str) -> Tuple[Dict, bool]:
        """
        使用refresh_token刷新access_token
        
        :param refresh_token: Google OAuth refresh_token
        :return: 包含新的access_token和可能的refresh_token的字典，以及是否成功的布尔值
        
        使用示例:
        ```
        google = GoogleLogin(api_key="your_api_key")
        token_data, success = await google.refresh_access_token(refresh_token="your_refresh_token")
        if success:
            new_access_token = token_data.get("access_token")
            new_refresh_token = token_data.get("refresh_token")  # 可能为None
        ```
        """
        data, success = await self._request(
            "POST",
            "/api/unified-login/google/refresh-token",
            json={"refresh_token": refresh_token},
        )
        if not success:
            return {}, False
        return data, True


class WechatLogin(AsyncClient):
    """
    微信 OAuth2 登录客户端
    
    支持两种登录方式：
    - desktop: PC端扫码登录（使用微信开放平台）
    - mobile: 微信公众号OAuth登录（手机端微信内打开）

    使用示例:
    ```
    wechat = WechatLogin(api_key="your_api_key")
    # PC端扫码登录
    user_info, success = await wechat.login(login_type="desktop")
    # 微信公众号登录（手机端）
    user_info, success = await wechat.login(login_type="mobile")
    ```
    """

    def __init__(self, api_key: str):
        super().__init__(api_key)

    async def _get_auth_url(self, login_type: str = "desktop") -> Tuple[Optional[Dict[str, str]], bool]:
        """
        获取微信授权URL
        
        :param login_type: 登录类型，desktop 表示PC端扫码登录，mobile 表示微信公众号登录
        """
        if login_type == "mobile":
            # 微信公众号OAuth登录（手机端）
            endpoint = "/api/unified-login/wechat-official/auth-url"
        else:
            # PC端扫码登录
            endpoint = "/api/unified-login/wechat/auth-url"
        
        data, success = await self._request("POST", endpoint)
        if not success:
            return None, False
        auth_url = data.get("auth_url")
        if not auth_url:
            return None, False
        return data, True

    async def login(self, login_type: str = "desktop", timeout: int = 180) -> Tuple[Dict, bool]:
        """
        仿 Supabase CLI 的一键登录流程：打开浏览器完成授权，
        终端端轮询等待登录结果

        :param login_type: 登录类型，desktop 表示PC端扫码登录，mobile 表示微信公众号登录
        :param timeout: 等待用户完成授权的超时时间（秒）
        
        使用示例:
        ```
        wechat = WechatLogin(api_key="your_api_key")
        # PC端扫码登录
        user_info, success = await wechat.login(login_type="desktop")
        # 微信公众号登录（手机端）
        user_info, success = await wechat.login(login_type="mobile")
        ```
        """
        auth_data, success = await self._get_auth_url(login_type)
        if not success or not auth_data:
            return {}, False

        auth_url = auth_data.get("auth_url")
        state = auth_data.get("state") or self._extract_state(auth_url)

        if not auth_url or not state:
            return {}, False

        webbrowser.open(auth_url, new=2)

        return await self._wait_for_wechat_login(state, timeout, login_type)

    def _extract_state(self, auth_url: Optional[str]) -> Optional[str]:
        if not auth_url:
            return None
        try:
            parsed = urllib.parse.urlparse(auth_url)
            query = urllib.parse.parse_qs(parsed.query)
            values = query.get("state")
            if values:
                return values[0]
        except Exception:
            return None
        return None

    async def _wait_for_wechat_login(
        self, state: str, timeout: int, login_type: str = "desktop"
    ) -> Tuple[Dict, bool]:
        """
        等待微信登录结果
        
        :param state: 登录状态标识
        :param timeout: 超时时间（秒）
        :param login_type: 登录类型，desktop 表示PC端扫码登录，mobile 表示微信公众号登录
        """
        interval = 2
        total_checks = max(1, timeout // interval) if timeout > 0 else 1

        # 根据登录类型选择不同的等待接口
        if login_type == "mobile":
            endpoint = "/api/unified-login/wechat-official/wait-login"
        else:
            endpoint = "/api/unified-login/wechat/wait-login"

        for _ in range(total_checks):
            status, response = await self._request_raw(
                "POST",
                endpoint,
                json={"state": state},
            )

            if status == 200 and response.get("success") is True:
                return response.get("data", {}), True

            if status in (400, 408):
                break

            await asyncio.sleep(interval)

        return {}, False


class GitHubLogin(AsyncClient):
    """
    GitHub OAuth2 登录客户端

    使用示例:
    ```
    github = GitHubLogin(api_key="your_api_key")
    user_info, success = await github.login()
    ```
    """

    def __init__(self, api_key: str):
        super().__init__(api_key)

    async def _get_auth_url(self) -> Tuple[Optional[Dict[str, str]], bool]:
        data, success = await self._request(
            "POST", "/api/unified-login/github/auth-url"
        )
        if not success:
            return None, False
        auth_url = data.get("auth_url")
        if not auth_url:
            return None, False
        return data, True

    async def login(self, timeout: int = 180) -> Tuple[Dict, bool]:
        """
        仿 Supabase CLI 的一键登录流程：打开浏览器完成授权，
        终端端轮询等待登录结果

        :param timeout: 等待用户完成授权的超时时间（秒）
        """
        auth_data, success = await self._get_auth_url()
        if not success or not auth_data:
            return {}, False

        auth_url = auth_data.get("auth_url")
        state = auth_data.get("state") or self._extract_state(auth_url)

        if not auth_url or not state:
            return {}, False

        webbrowser.open(auth_url, new=2)

        return await self._wait_for_github_login(state, timeout)

    def _extract_state(self, auth_url: Optional[str]) -> Optional[str]:
        if not auth_url:
            return None
        try:
            parsed = urllib.parse.urlparse(auth_url)
            query = urllib.parse.parse_qs(parsed.query)
            values = query.get("state")
            if values:
                return values[0]
        except Exception:
            return None
        return None

    async def _wait_for_github_login(
        self, state: str, timeout: int
    ) -> Tuple[Dict, bool]:
        interval = 2
        total_checks = max(1, timeout // interval) if timeout > 0 else 1

        for _ in range(total_checks):
            status, response = await self._request_raw(
                "POST",
                "/api/unified-login/github/wait-login",
                json={"state": state},
            )

            if status == 200 and response.get("success") is True:
                return response.get("data", {}), True

            if status in (400, 408):
                break

            await asyncio.sleep(interval)

        return {}, False


class DouyinLogin(AsyncClient):
    """
    抖音 OAuth2 登录客户端

    使用示例:
    ```
    douyin = DouyinLogin(api_key="your_api_key")
    user_info, success = await douyin.login()
    ```
    """

    def __init__(self, api_key: str):
        super().__init__(api_key)

    async def _get_auth_url(self) -> Tuple[Optional[Dict[str, str]], bool]:
        data, success = await self._request(
            "POST", "/api/unified-login/douyin/auth-url"
        )
        if not success:
            return None, False
        auth_url = data.get("auth_url")
        if not auth_url:
            return None, False
        return data, True

    async def login(self, timeout: int = 180) -> Tuple[Dict, bool]:
        """
        仿 Supabase CLI 的一键登录流程：打开浏览器完成授权，
        终端端轮询等待登录结果

        :param timeout: 等待用户完成授权的超时时间（秒）
        """
        auth_data, success = await self._get_auth_url()
        if not success or not auth_data:
            return {}, False

        auth_url = auth_data.get("auth_url")
        state = auth_data.get("state") or self._extract_state(auth_url)

        if not auth_url or not state:
            return {}, False

        webbrowser.open(auth_url, new=2)

        return await self._wait_for_douyin_login(state, timeout)

    def _extract_state(self, auth_url: Optional[str]) -> Optional[str]:
        if not auth_url:
            return None
        try:
            parsed = urllib.parse.urlparse(auth_url)
            query = urllib.parse.parse_qs(parsed.query)
            values = query.get("state")
            if values:
                return values[0]
        except Exception:
            return None
        return None

    async def _wait_for_douyin_login(
        self, state: str, timeout: int
    ) -> Tuple[Dict, bool]:
        interval = 2
        total_checks = max(1, timeout // interval) if timeout > 0 else 1

        for _ in range(total_checks):
            status, response = await self._request_raw(
                "POST",
                "/api/unified-login/douyin/wait-login",
                json={"state": state},
            )

            if status == 200 and response.get("success") is True:
                return response.get("data", {}), True

            if status in (400, 408):
                break

            await asyncio.sleep(interval)

        return {}, False


class GitLabLogin(AsyncClient):
    """
    GitLab OAuth2 登录客户端

    使用示例:
    ```
    gitlab = GitLabLogin(api_key="your_api_key")
    user_info, success = await gitlab.login()
    ```
    """

    def __init__(self, api_key: str):
        super().__init__(api_key)

    async def _get_auth_url(self) -> Tuple[Optional[Dict[str, str]], bool]:
        data, success = await self._request(
            "POST", "/api/unified-login/gitlab/auth-url"
        )
        if not success:
            return None, False
        auth_url = data.get("auth_url")
        if not auth_url:
            return None, False
        return data, True

    async def login(self, timeout: int = 180) -> Tuple[Dict, bool]:
        """
        仿 Supabase CLI 的一键登录流程：打开浏览器完成授权，
        终端端轮询等待登录结果

        :param timeout: 等待用户完成授权的超时时间（秒）
        """
        auth_data, success = await self._get_auth_url()
        if not success or not auth_data:
            return {}, False

        auth_url = auth_data.get("auth_url")
        state = auth_data.get("state") or self._extract_state(auth_url)

        if not auth_url or not state:
            return {}, False

        webbrowser.open(auth_url, new=2)

        return await self._wait_for_gitlab_login(state, timeout)

    def _extract_state(self, auth_url: Optional[str]) -> Optional[str]:
        if not auth_url:
            return None
        try:
            parsed = urllib.parse.urlparse(auth_url)
            query = urllib.parse.parse_qs(parsed.query)
            values = query.get("state")
            if values:
                return values[0]
        except Exception:
            return None
        return None

    async def _wait_for_gitlab_login(
        self, state: str, timeout: int
    ) -> Tuple[Dict, bool]:
        interval = 2
        total_checks = max(1, timeout // interval) if timeout > 0 else 1

        for _ in range(total_checks):
            status, response = await self._request_raw(
                "POST",
                "/api/unified-login/gitlab/wait-login",
                json={"state": state},
            )

            if status == 200 and response.get("success") is True:
                return response.get("data", {}), True

            if status in (400, 408):
                break

            await asyncio.sleep(interval)

        return {}, False


class SMSLogin(AsyncClient):
    """
    短信验证码登录客户端

    使用示例:
    ```
    sms = SMSLogin(api_key="your_api_key")
    # 发送验证码
    state, success = await sms.send_code(phone="13800138000")
    if success:
        # 验证验证码并登录
        user_info, success = await sms.login(state=state, code="123456")
    ```
    """

    def __init__(self, api_key: str):
        super().__init__(api_key)

    async def send_code(self, phone: str) -> Tuple[Optional[str], bool]:
        """
        发送短信验证码

        :param phone: 手机号码
        :return: (state, success) state用于后续验证验证码
        """
        data, success = await self._request(
            "POST", "/api/unified-login/sms/send-code", json={"phone": phone}
        )
        if not success:
            return None, False
        state = data.get("state")
        if not state:
            return None, False
        return state, True

    async def verify_code(self, state: str, code: str) -> Tuple[Optional[str], bool]:
        """
        验证短信验证码

        :param state: 发送验证码时返回的state
        :param code: 验证码
        :return: (state, success) state用于后续等待登录结果
        """
        data, success = await self._request(
            "POST",
            "/api/unified-login/sms/verify-code",
            json={"state": state, "code": code},
        )
        if not success:
            return None, False
        new_state = data.get("state")
        if not new_state:
            return None, False
        return new_state, True

    async def _wait_for_login(
        self, state: str, timeout: int
    ) -> Tuple[Dict, bool]:
        """
        等待短信登录结果

        :param state: 验证验证码时返回的state
        :param timeout: 超时时间（秒）
        """
        interval = 2
        total_checks = max(1, timeout // interval) if timeout > 0 else 1

        for _ in range(total_checks):
            status, response = await self._request_raw(
                "POST",
                "/api/unified-login/sms/wait-sms-login",
                json={"state": state},
            )

            if status == 200 and response.get("success") is True:
                return response.get("data", {}), True

            if status in (400, 408):
                break

            await asyncio.sleep(interval)

        return {}, False

    async def login(
        self, state: str, code: str, timeout: int = 180
    ) -> Tuple[Dict, bool]:
        """
        验证验证码并等待登录结果

        :param state: 发送验证码时返回的state
        :param code: 验证码
        :param timeout: 等待登录结果的超时时间（秒）
        :return: (用户信息, 是否成功)
        """
        new_state, success = await self.verify_code(state, code)
        if not success or not new_state:
            return {}, False

        return await self._wait_for_login(new_state, timeout)


class EmailLogin(AsyncClient):
    """
    邮箱验证码登录客户端

    使用示例:
    ```
    email = EmailLogin(api_key="your_api_key")
    # 发送验证码
    state, success = await email.send_code(email="user@example.com")
    if success:
        # 验证验证码并登录
        user_info, success = await email.login(state=state, code="123456")
    ```
    """

    def __init__(self, api_key: str):
        super().__init__(api_key)

    async def send_code(self, email: str) -> Tuple[Optional[str], bool]:
        """
        发送邮箱验证码

        :param email: 邮箱地址
        :return: (state, success) state用于后续验证验证码
        """
        data, success = await self._request(
            "POST", "/api/unified-login/email/send-code", json={"email": email}
        )
        if not success:
            return None, False
        state = data.get("state")
        if not state:
            return None, False
        return state, True

    async def verify_code(self, state: str, code: str) -> Tuple[Optional[str], bool]:
        """
        验证邮箱验证码

        :param state: 发送验证码时返回的state
        :param code: 验证码
        :return: (state, success) state用于后续等待登录结果
        """
        data, success = await self._request(
            "POST",
            "/api/unified-login/email/verify-code",
            json={"state": state, "code": code},
        )
        if not success:
            return None, False
        new_state = data.get("state")
        if not new_state:
            return None, False
        return new_state, True

    async def _wait_for_login(
        self, state: str, timeout: int
    ) -> Tuple[Dict, bool]:
        """
        等待邮箱登录结果

        :param state: 验证验证码时返回的state
        :param timeout: 超时时间（秒）
        """
        interval = 2
        total_checks = max(1, timeout // interval) if timeout > 0 else 1

        for _ in range(total_checks):
            status, response = await self._request_raw(
                "POST",
                "/api/unified-login/email/wait-email-login",
                json={"state": state},
            )

            if status == 200 and response.get("success") is True:
                return response.get("data", {}), True

            if status in (400, 408):
                break

            await asyncio.sleep(interval)

        return {}, False

    async def login(
        self, state: str, code: str, timeout: int = 180
    ) -> Tuple[Dict, bool]:
        """
        验证验证码并等待登录结果

        :param state: 发送验证码时返回的state
        :param code: 验证码
        :param timeout: 等待登录结果的超时时间（秒）
        :return: (用户信息, 是否成功)
        """
        new_state, success = await self.verify_code(state, code)
        if not success or not new_state:
            return {}, False

        return await self._wait_for_login(new_state, timeout)
