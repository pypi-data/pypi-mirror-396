"""
x_dm_python - Twitter API Python 绑定类型存根

此文件为 PyCharm/VSCode 等 IDE 提供精确的类型提示
"""
from typing import Optional, Any

__version__: str

# ============================================================
# 主客户端类
# ============================================================

class Twitter:
    """
    Twitter 客户端

    统一入口，通过子模块属性访问各功能模块。

    Example:
        ```python
        from x_dm_python import Twitter

        client = Twitter(cookies, proxy_url="http://proxy:8080")

        # 访问 DM 模块
        result = await client.dm.send_message("123", "Hello")

        # 访问 Upload 模块
        result = await client.upload.image(image_bytes, "dm_image")

        # 访问 User 模块
        result = await client.user.get_profile("elonmusk")

        # 访问 Inbox 模块
        result = await client.inbox.get_user_updates()
        ```
    """

    dm: "dm.DMClient"
    upload: "upload.UploadClient"
    inbox: "inbox.InboxClient"
    user: "user.UserClient"

    def __init__(
        self,
        cookies: str,
        proxy_url: Optional[str] = None,
    ) -> None:
        """
        创建 Twitter 客户端

        Args:
            cookies: Twitter 账号的 cookies 字符串，必须包含 ct0, auth_token, twid
            proxy_url: 可选的代理服务器 URL

        Raises:
            RuntimeError: 当 cookies 格式无效或缺少必需字段时
        """
        ...

    def get_cookies(self) -> str:
        """获取当前 cookies 字符串"""
        ...

    def validate_cookies(self) -> bool:
        """验证 cookies 是否有效"""
        ...

    @staticmethod
    async def auth_token_to_cookies(
        auth_token: str,
        proxy_url: Optional[str] = None,
    ) -> "AuthTokenResult":
        """
        将 auth_token 转换为完整的 cookies

        模拟 Chrome 插件的 Token Login 流程，直接带 auth_token 访问
        x.com/home，从响应中收集所有需要的 cookies (ct0, twid)。

        Args:
            auth_token: Twitter 的 auth_token
            proxy_url: 可选的代理服务器 URL

        Returns:
            AuthTokenResult: 包含完整认证信息的结果对象

        Raises:
            RuntimeError: 当 auth_token 无效或转换失败时

        Example:
            ```python
            result = await Twitter.auth_token_to_cookies("your_auth_token")
            print(f"用户 ID: {result.user_id}")
            print(f"完整 cookies: {result.cookies}")

            # 使用返回的 cookies 创建客户端
            client = Twitter(result.cookies)
            ```
        """
        ...

    def __repr__(self) -> str: ...


# ============================================================
# DM 子模块
# ============================================================

class dm:
    """DM (私信) 模块"""

    class DMClient:
        """
        DM 客户端

        提供私信发送功能，支持单条发送和批量并发发送。
        """

        def __init__(
            self,
            cookies: str,
            proxy_url: Optional[str] = None,
        ) -> None: ...

        async def send_message(
            self,
            user_id: str,
            text: str,
            media_id: Optional[str] = None,
        ) -> "dm.DMResult":
            """
            发送单条私信

            Args:
                user_id: 目标用户 ID
                text: 消息内容
                media_id: 可选的媒体 ID
            """
            ...

        async def send_batch(
            self,
            user_ids: list[str],
            text: str,
            client_transaction_ids: Optional[list[str]] = None,
            media_ids: Optional[list[Optional[str]]] = None,
        ) -> "dm.BatchDMResult":
            """批量发送私信（相同内容）"""
            ...

        async def send_batch_with_custom_texts(
            self,
            user_ids: list[str],
            texts: list[str],
            client_transaction_ids: Optional[list[str]] = None,
            media_ids: Optional[list[Optional[str]]] = None,
        ) -> "dm.BatchDMResult":
            """批量发送自定义文案私信"""
            ...

    class DMResult:
        """单条私信发送结果"""
        success: bool
        user_id: str
        message: str
        error_msg: str
        http_status: int
        event_id: Optional[str]
        media_id: Optional[str]

        def __init__(
            self,
            success: bool = False,
            user_id: str = "",
            message: str = "",
            error_msg: str = "",
            http_status: int = 0,
            event_id: Optional[str] = None,
            media_id: Optional[str] = None,
        ) -> None: ...

        def __repr__(self) -> str: ...

    class BatchDMResult:
        """批量私信发送结果"""
        success_count: int
        failure_count: int
        results: list["dm.DMResult"]

        def __init__(
            self,
            success_count: int = 0,
            failure_count: int = 0,
            results: list["dm.DMResult"] = [],
        ) -> None: ...

        def __repr__(self) -> str: ...


# ============================================================
# Upload 子模块
# ============================================================

class upload:
    """Upload (上传) 模块"""

    class UploadClient:
        """
        Upload 客户端

        提供图片上传功能。
        """

        def __init__(
            self,
            cookies: str,
            proxy_url: Optional[str] = None,
        ) -> None: ...

        async def image(
            self,
            image_bytes: bytes,
            media_category: str,
        ) -> "upload.UploadResult":
            """
            上传图片

            Args:
                image_bytes: 图片二进制数据
                media_category: 媒体类别 ("tweet_image", "dm_image", "banner_image")
            """
            ...

        async def image_multiple_times(
            self,
            image_bytes: bytes,
            media_category: str,
            count: int,
        ) -> "upload.BatchUploadResult":
            """批量上传同一张图片多次"""
            ...

    class UploadResult:
        """单次图片上传结果"""
        success: bool
        media_id: Optional[int]
        media_id_string: Optional[str]
        error_msg: str

        def __init__(
            self,
            success: bool = False,
            media_id: Optional[int] = None,
            media_id_string: Optional[str] = None,
            error_msg: str = "",
        ) -> None: ...

        def __repr__(self) -> str: ...

    class BatchUploadResult:
        """批量图片上传结果"""
        success_count: int
        failure_count: int
        media_ids: list[str]
        results: list["upload.UploadResult"]

        def __init__(
            self,
            success_count: int = 0,
            failure_count: int = 0,
            media_ids: list[str] = [],
            results: list["upload.UploadResult"] = [],
        ) -> None: ...

        def __repr__(self) -> str: ...


# ============================================================
# Inbox 子模块
# ============================================================

class inbox:
    """Inbox (收件箱) 模块"""

    class InboxClient:
        """
        Inbox 客户端

        提供收件箱查询功能。
        """

        def __init__(
            self,
            cookies: str,
            proxy_url: Optional[str] = None,
        ) -> None: ...

        async def get_user_updates(
            self,
            active_conversation_id: Optional[str] = None,
            cursor: Optional[str] = None,
        ) -> "inbox.UserUpdatesResult":
            """获取用户消息更新"""
            ...

    class UserUpdatesResult:
        """用户消息更新结果"""
        success: bool
        error_msg: str
        http_status: int
        data_source: Optional[str]
        cursor: Optional[str]
        entry_count: int
        user_count: int

        def get_entries(self) -> list[dict[str, Any]]:
            """获取消息条目列表"""
            ...

        def get_users(self) -> dict[str, dict[str, Any]]:
            """获取用户信息映射"""
            ...

        def __repr__(self) -> str: ...


# ============================================================
# User 子模块
# ============================================================

class user:
    """User (用户) 模块"""

    class UserClient:
        """
        User 客户端

        提供用户资料查询和编辑功能。
        """

        def __init__(
            self,
            cookies: str,
            proxy_url: Optional[str] = None,
        ) -> None: ...

        async def get_profile(self, screen_name: str) -> "user.UserResp":
            """获取用户资料"""
            ...

        async def get_profile_by_id(self, rest_id: str) -> "user.UserResp":
            """通过用户 ID 获取用户资料"""
            ...

        async def get_about_account(self, screen_name: str) -> "user.AboutAccountResult":
            """获取账号详细信息"""
            ...

        async def edit_profile(self, params: "user.EditUserParams") -> "user.EditUserResult":
            """编辑用户资料"""
            ...

        async def change_profile_image(self, media_id: str) -> "user.ChangeProfileImageResult":
            """更换头像"""
            ...

        async def change_background_image(self, media_id: str) -> "user.ChangeBannerResult":
            """更换背景图"""
            ...

    class UserResp:
        """用户资料响应"""
        success: bool
        user_id: Optional[str]
        screen_name: Optional[str]
        name: Optional[str]
        description: Optional[str]
        location: Optional[str]
        url: Optional[str]
        profile_image_url: Optional[str]
        background_image: Optional[str]
        following_count: Optional[int]
        followers_count: Optional[int]
        following: bool
        protected: Optional[bool]
        profile_interstitial_type: Optional[str]
        error_msg: str
        http_status: int

        def __repr__(self) -> str: ...

    class AboutAccountResult:
        """账号详细信息结果"""
        success: bool
        rest_id: Optional[str]
        account_based_in: Optional[str]
        location_accurate: Optional[bool]
        learn_more_url: Optional[str]
        source: Optional[str]
        username_change_count: Optional[str]
        username_last_changed_at_msec: Optional[str]
        is_identity_verified: Optional[bool]
        is_blue_verified: Optional[bool]
        error_msg: str
        http_status: int

        def __repr__(self) -> str: ...

    class EditUserParams:
        """编辑用户资料参数"""
        name: Optional[str]
        description: Optional[str]
        location: Optional[str]
        url: Optional[str]

        def __init__(
            self,
            name: Optional[str] = None,
            description: Optional[str] = None,
            location: Optional[str] = None,
            url: Optional[str] = None,
        ) -> None: ...

        def __repr__(self) -> str: ...

    class EditUserResult:
        """编辑用户资料结果"""
        success: bool
        name: Optional[str]
        description: Optional[str]
        location: Optional[str]
        url: Optional[str]
        error_msg: str
        http_status: int

        def __repr__(self) -> str: ...

    class ChangeProfileImageResult:
        """更换头像结果"""
        success: bool
        profile_image_url: Optional[str]
        error_msg: str
        http_status: int

        def __repr__(self) -> str: ...

    class ChangeBannerResult:
        """更换背景图结果"""
        success: bool
        banner_url: Optional[str]
        error_msg: str
        http_status: int

        def __repr__(self) -> str: ...


# ============================================================
# Auth Token 转换结果
# ============================================================

class AuthTokenResult:
    """
    Auth Token 转换结果

    包含从 auth_token 获取的完整认证信息。
    """
    cookies: str
    """完整的 cookies 字符串"""

    ct0: str
    """CSRF Token (ct0)"""

    user_id: str
    """用户 ID"""

    auth_token: str
    """原始 auth_token"""

    def __repr__(self) -> str: ...

