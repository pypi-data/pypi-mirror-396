"""
Upload (上传) 模块

提供图片上传功能。

Example:
    ```python
    from x_dm_python.upload import UploadClient

    client = UploadClient(cookies)

    with open("image.jpg", "rb") as f:
        image_bytes = f.read()

    result = await client.image(image_bytes, "dm_image")
    if result.success:
        print(f"Media ID: {result.media_id_string}")

    # 批量上传获取多个 media_id
    result = await client.image_multiple_times(image_bytes, "dm_image", 3)
    print(f"Media IDs: {result.media_ids}")
    ```
"""

from ..x_dm_python import upload as _upload

UploadClient = _upload.UploadClient
UploadResult = _upload.UploadResult
BatchUploadResult = _upload.BatchUploadResult

__all__ = [
    "UploadClient",
    "UploadResult",
    "BatchUploadResult",
]
