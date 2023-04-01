from src.sync_client import SyncClient
from dotenv import load_dotenv
import os
import json

def get_skill_icon_mapping():
    if os.path.exists("output/skill_icon_mapping.json"):
        with open("output/skill_icon_mapping.json", "r") as f:
             local_dict = json.load(f)
             return { k.rsplit('_',1)[-1] : v for k,v in local_dict.items()}

if __name__ == '__main__':
    load_dotenv()
    client = SyncClient()
    client.setup_external_resource_mapping(skill_icon_mapping=get_skill_icon_mapping())
    # 考虑Notion的限制thread_count不要设置太大
    # 重复执行可能会导致有重复项，Notion Query可能有最大900条数据的限制，所以超过部分的数据重复无法检测
    client.start_skill_data_sync("赛马娘技能数据库",os.getenv("ROOT_PAGE_ID"), thread_count=5)