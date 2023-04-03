import os
from tqdm import tqdm
from typing import Callable
from concurrent.futures import ThreadPoolExecutor
import threading
from enum import Enum

from src.config import read_database_id,write_database_id
from src.model import *
from src.notion import Database
from src.db import Umadb
from src.pages.skill_page import SkillDatabasePage, SkillDetailPage
from src.pages.character_card_page import CharacterCardDatabasePage, CharacterCardDetailPage
from src.utils.file_utils import read_id_list, write_id_list

class SyncType(Enum):
    skill = 1
    character_card = 2
    support_card = 3

def _create_database(type:SyncType, database_name, parent_page_id: str) -> Database:
    if type == SyncType.skill:
        return SkillDatabasePage().createDatabase(database_name, parent_page_id)
    elif type == SyncType.character_card:
        return CharacterCardDatabasePage().createDatabase(database_name, parent_page_id)
    else:
        raise NotImplementedError

class SyncClient:

    def __init__(self, gamedatapath: str = None, gameinstalledpath: str = None) -> None:
        """
        === Parameters ===
        param gamedatapath: path to the game data
        param gameinstalledpath: path to the game installed directory
        """
        if gamedatapath:
            self.dbpath = os.path.join(gamedatapath, 'master', 'master.mdb')
        else:
            self.dbpath = os.path.join(os.path.expanduser(
                '~'), 'AppData', 'LocalLow', 'Cygames', 'umamusume', 'master', 'master.mdb')
        self.skill_icon_mapping = None
        self.chara_cover_mapping = None
        self.chara_icon_mapping = None
        self.umadb = Umadb(self.dbpath)

    def setup_external_resource_mapping(self, skill_icon_mapping: dict[str,str] = None, 
                                        chara_cover_mapping:dict[str, str] = None, 
                                        chara_icon_mapping:dict[str,str]=None) -> None:
        self.skill_icon_mapping = skill_icon_mapping
        self.chara_cover_mapping = chara_cover_mapping
        self.chara_icon_mapping = chara_icon_mapping

    def _ensure_notion_database_exists(self, parent_page_id, title, type:SyncType) -> str:
        id = read_database_id(type.name)
        if id:
            return id
        else:
            page_database = _create_database(type, title, parent_page_id)
            write_database_id(type.name, page_database.id)
            return page_database.id
    
    def _run_in_multi_thread(self, thread_count,size, endfunc, func, genfunc: Callable[[int], tuple]):
        pool = ThreadPoolExecutor(thread_count)
        with tqdm(total=size) as pbar:
            def callback(future):
                pbar.update(1)
            for i in range(size):
                pool.submit(func, *genfunc(i)).add_done_callback(callback)
            pool.shutdown()
        endfunc()
    
    def _load_local_skill_list(self) -> list:
        return list(self.umadb.get_all_skill_data())

    def _update_skill_database(self, database_id, skill_list: list[Skill], thread_count, attentive_check) -> None:
        # check update info
        print(f"start to fetch current skill list from database {database_id}")
        record_file_path = f"{SyncType.skill.name}_update_{database_id}.record"
        database_page = SkillDatabasePage()
        new_skill_list,id_set_in_cloud = database_page.filterNewSkill(skill_list, database_id)
        record_set = set(read_id_list(record_file_path) or [])
        for id_in_cloud in id_set_in_cloud:
            record_set.add(id_in_cloud)
        new_skill_list = list(filter(lambda skill: skill.id not in record_set, new_skill_list))
        if not new_skill_list:
            print("No new skill to update")
            return
        print(f"local skill count: {len(skill_list)}, new skill count: {len(new_skill_list)}")
        if attentive_check and len(id_set_in_cloud) >= 900:
            # if cloud size is too large, use single filter query to check skill whether or not in database
            temp_list = []
            origin_count = len(new_skill_list)
            validate_count_from_filter_query = 0
            for skill in new_skill_list:
                page = None
                try:
                    page = database_page.getSkillPageInNotionDatabase(database_id, skill.id)
                except Exception as e:
                    print(f"Failed to get skill page for skill {skill.id}, error: {e}")
                if not page:
                    print(f"Skill {skill.id} not in notion database, add to new skill list")
                    temp_list.append(skill)
                else:
                    print(f"Skill {skill.id} already in notion database, skip")
                    record_set.add(skill.id)
                    write_id_list(record_file_path, [skill.id], append=True)
                    validate_count_from_filter_query += 1
            new_skill_list = temp_list
            if validate_count_from_filter_query > 0:
                write_id_list(record_file_path, record_set)
            print(f"Origin new skill count {origin_count}, single filter query validate count: {validate_count_from_filter_query}.")
        # start update (now just create new page not update)
        detail_page = SkillDetailPage(self.skill_icon_mapping)
        def end_callback():
            if detail_page.failed_count > 0:
                print(f"Failed to create {detail_page.failed_count} pages")
        self._run_in_multi_thread(thread_count, len(new_skill_list), end_callback, detail_page.createPageInDatabase, lambda i: (database_id, new_skill_list[i]))

    def start_skill_data_sync(self, database_title, root_page_id, thread_count=1, attentive_check=False):
        """
        === Parameters ===
        param database_title: title of the database
        param root_page_id: id of the root page
        param thread_count: number of threads to use
        param attentive_check: if true, will use single filter query to check skill whether or not in database
        """
        database_id = self._ensure_notion_database_exists(root_page_id, database_title, SyncType.skill)
        print(f"ensure database {database_title} exists, id: {database_id}")
        skill_list = self._load_local_skill_list()
        self._update_skill_database(database_id, skill_list, thread_count, attentive_check)
    
    def _load_local_character_card_list(self) -> list[CharacterCard]:
        return list(self.umadb.get_all_character_card_data())

    def start_character_card_data_sync(self, database_title, root_page_id, thread_count=1):
        database_id = self._ensure_notion_database_exists(root_page_id, database_title, SyncType.character_card)
        card_list = self._load_local_character_card_list()
        skill_database_id = read_database_id(SyncType.skill.name)
        if not skill_database_id:
            print("require sync skill database first")
            return
        print("fetch current skill database info...")
        skill_database_page = SkillDatabasePage()
        skill_pages = skill_database_page.getAllSkillPageInNotionDatabase(skill_database_id)
        skill_page_mapping = {page.properties['id'].number : page.id for page in skill_pages}
        local_skill_list = self._load_local_skill_list()
        local_skill_mapping = {skill.id : skill for skill in local_skill_list}
        lock = threading.Lock()
        def mismatch_callback(skill_id:int)->str:
            page_id = None
            page = skill_database_page.getSkillPageInNotionDatabase(skill_database_id, skill_id)
            if page:
                page_id = page.id
            print(f"skill id ({skill_id}) not found in notion database, send single query request to get skill id in notion database, result:{page_id}")
            with lock:
                if skill_id not in skill_page_mapping:
                    skill_page_mapping[skill_id] = page_id
            return page_id
        detail_page = CharacterCardDetailPage(self.chara_cover_mapping, self.chara_icon_mapping, local_skill_mapping)
        def end_callback():
            if detail_page.failed_count > 0:
                print(f"Failed to create {detail_page.failed_count} pages")
        self._run_in_multi_thread(thread_count, len(card_list), end_callback, detail_page.createPageInDatabase, lambda i: (database_id, card_list[i], skill_page_mapping, mismatch_callback))
