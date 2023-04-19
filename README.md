# Notion sync umadb
Sync data from local Umamusume game data to Notion database. Facilitate pointing content to detailed data when writing articles, use offical Notion API.

## 介绍
> 简单使用可以直接通过Notion复制页面[HERE](https://alphaboom.notion.site/Database-c0477472d548448183fe33a621f78257)

将赛马娘相关数据在Notion上同步保存一份，方便在Notion文章中快速关联技能、人物、支援卡等。例如准备大赛马时，可以快速标记需要的技能或支援卡配置信息等。

![](https://res.cloudinary.com/djdwogbsk/image/upload/v1680314691/image_3_orjdto.png)

## 使用说明

1. 使用pipenv安装依赖,在项目根目录执行：
    ```cmd
    pipenv install --dev
    ```
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
## 更新数据库

在游戏更新加入新卡时需要更新数据库，目前支持两种数据源

### 本地数据源

数据来源于DMM客户端，需要本地生成新数据然后再执行上传操作

### UraraWin数据源

可以借助Github WorkFlow自动更新数据，操作步骤如下：
1. Fork该项目
2. 在项目settings->Secrets and variables -> Actions中创建两个Repository Secrets
    ```properties
    # Notion申请的API KEY
    NOTION_API_KEY= 
    # 需要创建数据库的根页面
    ROOT_PAGE_ID=
    ```
3. 到Github Actions 中选择`Create database use urarawin data `然后执行，该任务执行完成后会创建数据库。之后需要记录生成好的Database id用于后续更新使用，这个id可以在Notion上获取，也可以在刚刚创建数据库的工作流的输出信息里看到，查看`check created database id`里面会有如下内容：
    ```properties
    [database_id]
    skill = 58b7e69d-f3cc-4c57-9dde-14efa2da1ce1
    character_card = c37ea0dc-795d-49bd-8a56-130539117177
    support_card = fc4540b7-08f7-4917-b33a-d14f2f2bf323
    ```
4. 在项目settings->Secrets and variables -> Actions中，这次选择Variables。创建3个Repository variable
    ```properties
    # 技能数据库id
    SKILL_DATABASE_ID=
    # 角色数据库id
    CHARA_DATABASE_ID=
    # 支援卡数据库id
    SUPPORT_CARD_DATABASE_ID=
    ```
默认更新计划是在周3和周6的5:30进行(0时区时间)。

## 其他

### 资源获取

关于游戏图标获取以及图片上传参考以下目录：[tools/](tools/) 以及 [scripts/](scripts/)

### 全量更新

默认只会在当前数据库基础上创建新页面，如果需要更新已有的页面可以设置更新模式为Full，如果使用GithubAction可以使用Full(Force) update database的工作流。全量更新运行耗时很长，如果当前没有大量文章关联到数据库，建议使用创建新的数据库的方式。
