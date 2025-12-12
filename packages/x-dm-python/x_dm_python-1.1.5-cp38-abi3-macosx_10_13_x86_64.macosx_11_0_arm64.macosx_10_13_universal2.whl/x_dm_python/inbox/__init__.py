"""
Inbox (收件箱) 模块

提供收件箱查询功能。

Example:
    ```python
    from x_dm_python.inbox import InboxClient

    client = InboxClient(cookies)
    result = await client.get_user_updates()

    if result.success:
        entries = result.get_entries()
        users = result.get_users()
        print(f"获取 {result.entry_count} 条消息，{result.user_count} 个用户")
    ```
"""

from ..x_dm_python import inbox as _inbox

InboxClient = _inbox.InboxClient
UserUpdatesResult = _inbox.UserUpdatesResult

__all__ = [
    "InboxClient",
    "UserUpdatesResult",
]
