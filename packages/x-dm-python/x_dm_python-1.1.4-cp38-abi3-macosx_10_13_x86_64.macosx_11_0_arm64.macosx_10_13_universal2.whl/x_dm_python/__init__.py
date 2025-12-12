"""
x_dm_python - Twitter API Python 绑定

模块化设计，支持两种 API 风格：

## 风格 1: 子模块属性访问（推荐）
```python
from x_dm_python import Twitter

client = Twitter(cookies)
result = await client.dm.send_message("123", "Hello")
result = await client.user.get_profile("elonmusk")
result = await client.upload.image(image_bytes, "dm_image")
result = await client.inbox.get_user_updates()
```

## 风格 2: 独立客户端导入
```python
from x_dm_python.dm import DMClient
from x_dm_python.user import UserClient
from x_dm_python.upload import UploadClient
from x_dm_python.inbox import InboxClient

dm_client = DMClient(cookies)
result = await dm_client.send_message("123", "Hello")
```

## 模块列表

- `dm`: 私信发送模块
- `upload`: 图片上传模块
- `inbox`: 收件箱查询模块
- `user`: 用户资料模块
"""

from .x_dm_python import (
    Twitter,
    __version__,
)

# 导入子模块
from . import dm
from . import upload
from . import inbox
from . import user
from . import posts

__all__ = [
    # 主客户端
    "Twitter",
    "__version__",
    # 子模块
    "dm",
    "upload",
    "inbox",
    "user",
    "posts",
]
