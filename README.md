# Notion sync umadb
Sync data from local Umamusume game data to Notion database. Facilitate pointing content to detailed data when writing articles, use offical Notion API.

## 为什么做这个
方便在Notion文章中快速关联技能，例如准备大赛马的技能和支援卡配置
![](https://res.cloudinary.com/djdwogbsk/image/upload/v1680314691/image_3_orjdto.png)

## 使用说明

1. 使用Python3运行，依赖信息在[requirements.txt](requirements.txt)
2. 到[Notion integrations](https://www.notion.so/my-integrations)创建一个应用，记下APIKEY
3. Notion上建一个Page，并在这个Page上关联2.创建的应用，之后记录这个页面的ID。
    页面ID可以通过copy当前页面的链接获得，链接尾的字符串就是id。之后需要根据8-4-4-4-12的方式加入中线即可.
    ```Plain text
    0dfc38fea6f24fc4beba4985b7206031
    ------
    0dfc38fe-a6f2-4fc4b-eba4-985b7206031
    ```
4. 本地创建`.env`文件把相关信息填入
    ```Plain text
    NOTION_API_KEY=""
    ROOT_PAGE_ID=""
    ```

## 关于资源图标和上传图片

获取游戏图标使用了UnityPy，上传图片使用了Cloudinary