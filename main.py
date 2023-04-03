from src.sync_client import SyncClient
from dotenv import load_dotenv
import os
import json

def get_skill_icon_mapping():
    """
    use tools/extract_skill_icon.py to generate icon resources, then use tools/upload_image_tocloudinary.py to generate mapping
    """
    if os.path.exists("output/skill_icon_mapping.json"):
        with open("output/skill_icon_mapping.json", "r") as f:
             local_dict = json.load(f)
             return { int(k.rsplit('_',1)[-1]) : v for k,v in local_dict.items()}

def get_chara_cover_mapping():
    """
    use tools/extract_chara_icon.py to generate icon resources, then use tools/upload_image_tocloudinary.py to generate mapping
    """
    if os.path.exists("output/chara_cover_mapping.json"):
        with open("output/chara_cover_mapping.json", "r") as f:
             local_dict = json.load(f)
             return { int(k.rsplit('_',1)[-1]) : v for k,v in local_dict.items()}

def get_chara_icon_mapping():
    """
    use tools/extract_chara_icon.py to generate icon resources, then use tools/upload_image_tocloudinary.py to generate mapping
    """
    if os.path.exists("output/chara_icon_mapping.json"):
        with open("output/chara_icon_mapping.json", "r") as f:
             local_dict = json.load(f)
             return { int(k.rsplit('_',1)[-1]) : v for k,v in local_dict.items()}

def get_support_card_icon_mapping():
    """
    use tools/extract_support_card_icon.py to generate icon resources, then use tools/upload_image_tocloudinary.py to generate mapping
    """
    if os.path.exists("output/supportcard_icon_mapping.json"):
        with open("output/supportcard_icon_mapping.json", "r") as f:
             local_dict = json.load(f)
             return { int(k.rsplit('_',1)[-1]) : v for k,v in local_dict.items()}

def get_support_card_cover_mapping():
    """
    use tools/extract_support_card_icon.py to generate icon resources, then use tools/upload_image_tocloudinary.py to generate mapping
    """
    if os.path.exists("output/supportcard_cover_mapping.json"):
        with open("output/supportcard_cover_mapping.json", "r") as f:
             local_dict = json.load(f)
             return { int(k.rsplit('_',1)[-1]) : v for k,v in local_dict.items()}

if __name__ == '__main__':
    load_dotenv()
    client = SyncClient()
    client.setup_external_resource_mapping(skill_icon_mapping=get_skill_icon_mapping(), 
                                           chara_cover_mapping=get_chara_cover_mapping(), 
                                           chara_icon_mapping=get_chara_icon_mapping(),
                                           support_card_icon_mapping=get_support_card_icon_mapping(),
                                           support_card_cover_mapping=get_support_card_cover_mapping())
    #考虑Notion的请求限制thread_count不要设置太大
    client.start_skill_data_sync("赛马娘技能数据库",os.getenv("ROOT_PAGE_ID"), thread_count=5)
    client.start_character_card_data_sync("赛马娘角色数据库",os.getenv("ROOT_PAGE_ID"), thread_count=3)
    client.start_support_card_data_sync("赛马娘支援卡数据库",os.getenv("ROOT_PAGE_ID"), thread_count=3)