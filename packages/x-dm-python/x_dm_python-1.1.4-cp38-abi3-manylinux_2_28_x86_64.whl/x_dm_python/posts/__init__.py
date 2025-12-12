"""
Posts (帖子) 模块

提供帖子相关操作，包括发帖、删帖、点赞、转发等。

Example:
    ```python
    from x_dm_python.posts import PostsClient, CreateTweetParams

    client = PostsClient(cookies)

    # 发帖
    result = await client.create_tweet(text="Hello World!")

    # 带图片发帖
    result = await client.create_tweet(
        text="Check this out!",
        media_ids=["12345"]
    )

    # 点赞
    result = await client.favorite_tweet("1234567890")

    # 转发
    result = await client.create_retweet("1234567890")

    # 获取帖子列表
    result = await client.get_tweets("44196397")
    for tweet in result.tweets:
        print(tweet.text)
    ```
"""

from ..x_dm_python import posts as _posts

# 客户端
PostsClient = _posts.PostsClient

# 参数类型
CreateTweetParams = _posts.CreateTweetParams

# 结果类型
TweetResult = _posts.TweetResult
DeleteTweetResult = _posts.DeleteTweetResult
LikeResult = _posts.LikeResult
RetweetResult = _posts.RetweetResult
TweetInfo = _posts.TweetInfo
GetTweetsResult = _posts.GetTweetsResult
GetLikesResult = _posts.GetLikesResult

__all__ = [
    # 客户端
    "PostsClient",
    # 参数类型
    "CreateTweetParams",
    # 结果类型
    "TweetResult",
    "DeleteTweetResult",
    "LikeResult",
    "RetweetResult",
    "TweetInfo",
    "GetTweetsResult",
    "GetLikesResult",
]
