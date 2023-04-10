import os
import json
import getopt
import sys
from typing import Callable

from src.sync_client import SyncClient
from src.config import Properties

def get_mapping(file, fallback:Callable):
    if not file:
        return fallback()
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)

def print_help():
    print("""main.py
      --root_page_id <root_page_id> 
      --notion_api_key <notion_api_key>
      --local_properties <local_properties> properties file to store notion database id.
      --generator <generator_name> The following generators are supported:
        - local (default): use data from umamusume DMM client database(like master.mdb).
        - urarawin : use data from urara-win. This can be used on github workflow.
      --update_mode <update_mode> The following update modes are supported:
        - insert (default): just insert new data to Notion database, do not update existing data.
        - full : update all data in Notion database.
      --skill_database_title <skill_database_title>
      --skill_sync_thread_count <skill_sync_thread_count>
      --skill_icon_mapping <skill_icon_mapping> 
      --chara_database_title <chara_database_title>
      --chara_sync_thread_count <chara_sync_thread_count>
      --chara_cover_mapping <chara_cover_mapping> 
      --chara_icon_mapping <chara_icon_mapping> 
      --support_card_database_title <support_card_databse_title>
      --support_card_sync_thread_count <support_card_sync_thread_count>
      --support_card_icon_mapping <support_card_icon_mapping> 
      --support_card_cover_mapping <support_card_cover_mapping>
    """)
available_generators = ("local","urarawin")
available_update_modes = ("insert","full")

if __name__ == '__main__':
    try:
        opts,_ = getopt.getopt(sys.argv[1:], "h", 
                               ["help","root_page_id=","notion_api_key=","local_properties=",   
                                "generator=","update_mode=",
                                "skill_database_title=","skill_sync_thread_count=","skill_icon_mapping=",
                                "chara_database_title=","chara_sync_thread_count=","chara_cover_mapping=","chara_icon_mapping=",
                                "support_card_database_title=","support_card_sync_thread_count=","support_card_icon_mapping=","support_card_cover_mapping="])
    except getopt.GetoptError as e:
        print(e)
        print_help()
        sys.exit(2)
    skill_icon_mapping_file = None
    chara_cover_mapping_file = None
    chara_icon_mapping_file = None
    support_card_icon_mapping_file = None
    support_card_cover_mapping_file = None
    skill_sync_thread_count = 5
    chara_sync_thread_count = 3
    support_card_sync_thread_count = 3
    skill_database_title = None
    chara_database_title = None
    support_card_database_title = None
    generator_name = "lcoal"
    update_mode = "insert"
    properties_file = "local.properties"
    for opt,arg in opts:
        if opt in ("-h","--help"):
            print_help()
            sys.exit()
        elif opt == "--root_page_id":
            os.environ["ROOT_PAGE_ID"] = arg
        elif opt == "--notion_api_key":
            os.environ["NOTION_API_KEY"] = arg
        elif opt == "--local_properties":
            properties_file = arg
        elif opt == "--generator":
            if arg not in available_generators:
                print(f"generator {arg} is not supported")
                sys.exit(2)
            generator_name = arg
        elif opt == "--update_mode":
            if arg not in available_update_modes:
                print(f"update_mode {arg} is not supported")
                sys.exit(2)
            update_mode = arg
        elif opt == "--skill_database_title":
            skill_database_title = arg
        elif opt == "--skill_sync_thread_count":
            skill_sync_thread_count = int(arg)
        elif opt == "--skill_icon_mapping":
            skill_icon_mapping_file = arg
        elif opt == "--chara_database_title":
            chara_database_title = arg
        elif opt == "--chara_sync_thread_count":
            chara_sync_thread_count = int(arg)
        elif opt == "--chara_cover_mapping":
            chara_cover_mapping_file = arg
        elif opt == "--chara_icon_mapping":
            chara_icon_mapping_file = arg
        elif opt == "--support_card_database_title":
            support_card_database_title = arg
        elif opt == "--support_card_sync_thread_count":
            support_card_sync_thread_count = int(arg)
        elif opt == "--support_card_icon_mapping":
            support_card_icon_mapping_file = arg
        elif opt == "--support_card_cover_mapping":
            support_card_cover_mapping_file = arg
    
    properties = Properties(properties_file)

    if generator_name == "urarawin":
        from src.generators import UraraWinSourceGenerator
        source = UraraWinSourceGenerator(properties)
    else:
        from src.generators import LocalSourceGenerator
        source = LocalSourceGenerator(properties)
    
    client = SyncClient(properties, source, update_mode)
    client.setup_external_resource_mapping(skill_icon_mapping=get_mapping(skill_icon_mapping_file, source.generate_skill_icon_mapping), 
                                           chara_icon_mapping=get_mapping(chara_icon_mapping_file, source.generate_chara_icon_mapping),
                                           chara_cover_mapping=get_mapping(chara_cover_mapping_file, source.generate_chara_cover_mapping),
                                           support_card_icon_mapping=get_mapping(support_card_icon_mapping_file, source.generate_support_card_icon_mapping),
                                           support_card_cover_mapping=get_mapping(support_card_cover_mapping_file, source.generate_support_card_cover_mapping))
    root_page_id = os.getenv("ROOT_PAGE_ID")
    if skill_database_title:
        client.start_skill_data_sync(skill_database_title,root_page_id, thread_count=skill_sync_thread_count)
    if chara_database_title:
        client.start_character_card_data_sync(chara_database_title,root_page_id, thread_count=chara_sync_thread_count)
    if support_card_database_title:
        client.start_support_card_data_sync(support_card_database_title,root_page_id, thread_count=support_card_sync_thread_count)