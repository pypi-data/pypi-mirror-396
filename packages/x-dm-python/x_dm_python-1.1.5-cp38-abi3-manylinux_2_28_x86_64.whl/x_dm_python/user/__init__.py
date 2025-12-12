"""
User (用户) 模块

提供用户资料查询和编辑功能。

Example:
    ```python
    from x_dm_python.user import UserClient, EditUserParams

    client = UserClient(cookies)

    # 获取用户资料
    result = await client.get_profile("elonmusk")
    if result.success:
        print(f"用户: {result.name}, 粉丝: {result.followers_count}")

    # 编辑资料
    params = EditUserParams(name="New Name", description="Updated bio")
    result = await client.edit_profile(params)

    # 更换头像
    upload_result = await upload_client.image(image_bytes, "banner_image")
    if upload_result.success:
        result = await client.change_profile_image(upload_result.media_id_string)
    ```
"""

from ..x_dm_python import user as _user

UserClient = _user.UserClient
UserResp = _user.UserResp
AboutAccountResult = _user.AboutAccountResult
EditUserParams = _user.EditUserParams
EditUserResult = _user.EditUserResult
ChangeProfileImageResult = _user.ChangeProfileImageResult
ChangeBannerResult = _user.ChangeBannerResult

__all__ = [
    "UserClient",
    "UserResp",
    "AboutAccountResult",
    "EditUserParams",
    "EditUserResult",
    "ChangeProfileImageResult",
    "ChangeBannerResult",
]
