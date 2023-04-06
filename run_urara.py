import os
from dotenv import load_dotenv

load_dotenv()
notion_api_key = os.getenv("NOTION_API_KEY")
root_page_id = os.getenv("ROOT_PAGE_ID")
opts = {
    "--notion_api_key": f'"{notion_api_key}"',
    "--root_page_id": f'"{root_page_id}"',
    "--local_properties": '"urarawin.properties"',
    "--generator": '"urarawin"',
    "--update_mode": '"insert"',
    "--skill_database_title": '"赛马娘技能数据库"',
    "--skill_sync_thread_count": 5,
    "--chara_database_title": '"赛马娘角色数据库"',
    "--chara_sync_thread_count": 3,
    "--support_card_database_title": '"赛马娘支援卡数据库"',
    "--support_card_sync_thread_count": 3,
}
command_line = "python main.py"
for opt, arg in opts.items():
    command_line += f" {opt} {arg}"
os.system(command_line)