"""
DM (私信) 模块

提供私信发送功能，支持单条发送和批量并发发送。

Example:
    ```python
    from x_dm_python.dm import DMClient

    client = DMClient(cookies)
    result = await client.send_message("123456", "Hello!")

    # 批量发送
    result = await client.send_batch(["123", "456"], "批量消息")
    ```
"""

from ..x_dm_python import dm as _dm

DMClient = _dm.DMClient
DMResult = _dm.DMResult
BatchDMResult = _dm.BatchDMResult

__all__ = [
    "DMClient",
    "DMResult",
    "BatchDMResult",
]
