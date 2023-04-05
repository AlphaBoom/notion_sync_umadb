# Notion sync umadb
Sync data from local Umamusume game data to Notion database. Facilitate pointing content to detailed data when writing articles, use offical Notion API.

## 介绍
> 简单使用可以直接通过Notion复制页面[HERE](https://alphaboom.notion.site/Database-c0477472d548448183fe33a621f78257)

将赛马娘相关数据在Notion上同步保存一份，方便在Notion文章中快速关联技能、人物、支援卡等。例如准备大赛马时，可以快速标记需要的的技能或支援卡配置信息等。

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
5. 运行[run_local.py](run_local.py)即可在Notion上建立对应的数据库。可以适当修改该文件的参数，需要注意的参数：
    * local_properties: 该参数内容对应一个配置文件，如果文件不存在，会创建新的数据库。文件存在，则会根据文件信息选择更新已有的数据库或创建数据库
        ```properties
        [database_id]
        #技能数据库
        skill = d60a258b-ede7-4cd7-bdf6-8248bcb88152
        #人物数据库
        character_card = bf1bde80-14b7-4a52-982a-73af2e94a475
        #支援卡数据库
        support_card = 7718ef63-967f-4c87-a7d8-9c99156a3d6a
        ```
## 计划任务
有些效果存在不便，还有些工作需要完成:

- [ ] 对同步攻略站数据方式，增加workflow。通过Github Actions定时人物来保持数据库更新。
- [ ] 增加同步攻略站数据模式(例如Urara win)
- [ ] 支援卡数据缺失事件获取技能列表
- [ ] 标题列人物名称修改为中文
- [x] 上传支援卡数据库
- [x] 上传人物数据库
- [x] 上传技能数据库

## 其他

关于游戏图标获取以及图片上传参考以下目录：[tools/](tools/) 以及 [scripts/](scripts/)
