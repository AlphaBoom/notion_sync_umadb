from tqdm import tqdm
from typing import Callable
from concurrent.futures import ThreadPoolExecutor
import threading
from enum import Enum
import os

from src.config import Properties
from src.model import *
from src.notion import Database
from src.pages.skill_page import SkillDatabasePage, SkillDetailPage
from src.pages.character_card_page import CharacterCardDatabasePage, CharacterCardDetailPage
from src.pages.support_card_page import SupportCardDatabasePage,SupportCardDetailPage
from src.utils.file_utils import read_id_list, write_id_list
from src.generators import SourceGenerator

_DEFAULT_MODE = "insert"
_FULL_UPDATE_MODE = "full"

SKILL_FAILED_PERSIST_PATH = "skill_failed_persist.txt"
CHARA_FAILED_PERSIST_PATH = "chara_failed_persist.txt"
SUPPORT_CARD_FAILED_PERSIST_PATH = "support_card_failed_persist.txt"

class SyncType(Enum):
    skill = 1
    character_card = 2
    support_card = 3

def _create_database(type:SyncType, database_name, parent_page_id: str) -> Database:
    if type == SyncType.skill:
        return SkillDatabasePage().createDatabase(database_name, parent_page_id)
    elif type == SyncType.character_card:
        return CharacterCardDatabasePage().createDatabase(database_name, parent_page_id)
    elif type == SyncType.support_card:
        return SupportCardDatabasePage().createDatabase(database_name, parent_page_id)
    else:
        raise NotImplementedError

def _update_database(type:SyncType, database_name, database_id:str) -> Database:
    if type == SyncType.skill:
        return SkillDatabasePage().updateDatabase(database_name, database_id)
    elif type == SyncType.character_card:
        return CharacterCardDatabasePage().updateDatabase(database_name, database_id)
    elif type == SyncType.support_card:
        return SupportCardDatabasePage().updateDatabase(database_name, database_id)
    else:
        raise NotImplementedError

class SyncClient:

    def __init__(self, properties:Properties, generator:SourceGenerator, update_mode:str) -> None:
        """
        === Parameters ===
        param gamedatapath: path to the game data
        param gameinstalledpath: path to the game installed directory
        """
        self.skill_icon_mapping:StrMapping = None
        self.chara_cover_mapping:StrMapping = None
        self.chara_icon_mapping:StrMapping = None
        self.support_card_cover_mapping:StrMapping = None
        self.support_card_icon_mapping:StrMapping = None
        self._skill_page_mapping = None
        self.update_mode = update_mode
        self.source:SourceGenerator = generator
        self.p = properties
        self.failed_retry_count = 0
        self.failed_update_id_set = set()

    def setup_external_resource_mapping(self, skill_icon_mapping:StrMapping = None, 
                                        chara_cover_mapping:StrMapping = None, 
                                        chara_icon_mapping:StrMapping = None,
                                        support_card_icon_mapping:StrMapping = None,
                                        support_card_cover_mapping:StrMapping = None) -> None:
        self.skill_icon_mapping = skill_icon_mapping
        self.chara_cover_mapping = chara_cover_mapping
        self.chara_icon_mapping = chara_icon_mapping
        self.support_card_icon_mapping = support_card_icon_mapping
        self.support_card_cover_mapping = support_card_cover_mapping

    def _ensure_notion_database_exists(self, parent_page_id, title, type:SyncType) -> str:
        id = self.p.read_database_id(type.name)
        if id:
            if self.update_mode == _FULL_UPDATE_MODE:
                _update_database(type, title, id)
            return id
        else:
            page_database = _create_database(type, title, parent_page_id)
            self.p.write_database_id(type.name, page_database.id)
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
    
    def _load_local_skill_list(self) -> list[Skill]:
        return self.source.get_all_skill()
    
    def _retry_check(self, failed_count, func, *args):
        if failed_count > 0 and self.failed_retry_count < 2:
            self.failed_retry_count += 1
            print(f"have {failed_count} failed pages, retry {self.failed_retry_count} times")
            try:
                func(*args)
            except Exception as e:
                print(f"retry failed: {e}")
                self._retry_check(failed_count, func, *args)
        else:
            self.failed_retry_count = 0
    
    def _update_precheck(self, in_cloud_list, persist_file_path=None)->list:
        if persist_file_path:
            stored_list = read_id_list(persist_file_path)
            if stored_list:
                self.failed_update_id_set = set(stored_list)
        if self.failed_update_id_set:
            return list(filter(lambda resource: resource[0].id in self.failed_update_id_set, in_cloud_list))
        else:
            return in_cloud_list

    def _update_postcheck(self, update_failed_id_set , persist_file_path=None):
        if update_failed_id_set:
            print(f"Failed to update {len(update_failed_id_set)} pages")
            self.failed_update_id_set = update_failed_id_set
            if persist_file_path:
                write_id_list(persist_file_path, self.failed_update_id_set)
        else:
            self.failed_update_id_set.clear()
            if persist_file_path:
                if os.path.exists(persist_file_path):
                    os.remove(persist_file_path)

    def _update_skill_database(self, database_id, skill_list: list[Skill], thread_count, attentive_check, persist_file_path=None) -> None:
        # check update info
        record_file_path = f"{SyncType.skill.name}_update_{database_id}.record"
        database_page = SkillDatabasePage()
        new_skill_list,in_cloud_list = database_page.filterNewSkill(skill_list, database_id)
        record_set = set(read_id_list(record_file_path) or [])
        for skill, page in in_cloud_list:
            record_set.add(skill.id)
        new_skill_list = list(filter(lambda skill: skill.id not in record_set, new_skill_list))
        detail_page = SkillDetailPage(self.skill_icon_mapping)
        def end_callback():
            if detail_page.failed_count > 0:
                print(f"Failed to create {detail_page.failed_count} pages")
        if new_skill_list:
            # add new page in database
            print(f"local skill count: {len(skill_list)}, new skill count: {len(new_skill_list)}")
            if attentive_check and len(in_cloud_list) >= 900:
                # if cloud size is too large, use single filter query to check skill whether or not in database
                temp_list = []
                origin_count = len(new_skill_list)
                validate_count_from_filter_query = 0
                for skill in new_skill_list:
                    page = None
                    try:
                        page = database_page.getPageInNotionDatabase(database_id, skill.id)
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
            self._run_in_multi_thread(thread_count, len(new_skill_list), end_callback, detail_page.createPageInDatabase, lambda i: (database_id, new_skill_list[i]))
        elif self.update_mode == _DEFAULT_MODE:
            print("no skill need to update, skip")
        if self.update_mode == _FULL_UPDATE_MODE and in_cloud_list:
            # update existed page
            print("update existed skill page...")
            in_cloud_list = self._update_precheck(in_cloud_list, persist_file_path)
            self._run_in_multi_thread(thread_count, len(in_cloud_list), lambda: None, detail_page.updatePageInDatabase, lambda i: (in_cloud_list[i][1], in_cloud_list[i][0]))
            self._update_postcheck(detail_page.failed_update_id_set, persist_file_path=SKILL_FAILED_PERSIST_PATH)
        self._retry_check(detail_page.failed_count, self._update_skill_database, database_id, skill_list, thread_count, attentive_check)

    def start_skill_data_sync(self, database_title, root_page_id, thread_count=1, attentive_check=False, persist_file_path=None):
        """
        === Parameters ===
        param database_title: title of the database
        param root_page_id: id of the root page
        param thread_count: number of threads to use
        param attentive_check: if true, will use single filter query to check skill whether or not in database
        """
        print("start sync skill data...")
        database_id = self._ensure_notion_database_exists(root_page_id, database_title, SyncType.skill)
        skill_list = self._load_local_skill_list()
        self._update_skill_database(database_id, skill_list, thread_count, attentive_check, persist_file_path)
    
    def _load_local_character_card_list(self) -> list[CharacterCard]:
        return self.source.get_all_character_card()

    def _generate_local_skill_mapping(self) -> tuple[StrMapping,Callable[[str], str]]:
        if self._skill_page_mapping:
            return self._skill_page_mapping
        skill_database_id = self.p.read_database_id(SyncType.skill.name)
        if not skill_database_id:
            print("require sync skill database first")
            return None
        print("fetch current skill database info...")
        skill_database_page = SkillDatabasePage()
        skill_pages = skill_database_page.getAllPageInNotionDatabase(skill_database_id)
        skill_page_mapping = {page.properties['id'].rich_text[0].plain_text : page.id for page in skill_pages}
        lock = threading.Lock()
        def mismatch_callback(skill_id:int)->str:
            page_id = None
            page = skill_database_page.getPageInNotionDatabase(skill_database_id, skill_id)
            if page:
                page_id = page.id
            print(f"skill id ({skill_id}) not found in notion database, send single query request to get skill id in notion database, result:{page_id}")
            with lock:
                if skill_id not in skill_page_mapping:
                    skill_page_mapping[skill_id] = page_id
            return page_id
        self._skill_page_mapping = (skill_page_mapping, mismatch_callback)
        return self._skill_page_mapping

    def start_character_card_data_sync(self, database_title, root_page_id, thread_count=1, persist_file_path=None):
        """
        === Parameters ===
        param database_title: title of the database
        param root_page_id: id of the root page
        param thread_count: number of threads to use
        """
        print("start sync character card data...")
        database_id = self._ensure_notion_database_exists(root_page_id, database_title, SyncType.character_card)
        card_list, in_cloud_list = CharacterCardDatabasePage().filterNewCard(self._load_local_character_card_list(), database_id)
        if self.update_mode == _DEFAULT_MODE and not card_list:
            print("No character card require update, skip.")
            return
        skill_page_mapping, mismatch_callback = self._generate_local_skill_mapping()
        local_skill_list = self._load_local_skill_list()
        local_skill_mapping = {skill.id : skill for skill in local_skill_list}
        detail_page = CharacterCardDetailPage(self.chara_cover_mapping, self.chara_icon_mapping, local_skill_mapping)
        def end_callback():
            if detail_page.failed_count > 0:
                print(f"Failed to create {detail_page.failed_count} pages")
        if card_list:
            self._run_in_multi_thread(thread_count, len(card_list), end_callback, detail_page.createPageInDatabase, 
                                  lambda i: (database_id, card_list[i], skill_page_mapping, mismatch_callback))
        if self.update_mode == _FULL_UPDATE_MODE and in_cloud_list:
            # update existed page
            print("update existed chara page...")
            in_cloud_list = self._update_precheck(in_cloud_list, persist_file_path)
            self._run_in_multi_thread(thread_count, len(in_cloud_list), lambda: None, detail_page.updatePageInDatabase, lambda i: (in_cloud_list[i][1], in_cloud_list[i][0],skill_page_mapping, mismatch_callback))
            self._update_postcheck(detail_page.failed_update_id_set, persist_file_path=CHARA_FAILED_PERSIST_PATH)
        self._retry_check(detail_page.failed_count, self.start_character_card_data_sync, database_title, root_page_id, thread_count)
    
    def _load_local_support_card_list(self) -> list[SupportCard]:
        return self.source.get_all_support_card()
    
    def start_support_card_data_sync(self, database_title, root_page_id, thread_count=1, persist_file_path=None):
        """
        === Parameters ===
        param database_title: title of the database
        param root_page_id: id of the root page
        param thread_count: number of threads to use
        """
        print("start sync support card data...")
        database_id = self._ensure_notion_database_exists(root_page_id, database_title, SyncType.support_card)
        card_list, in_cloud_list = SupportCardDatabasePage().filterNewCard(self._load_local_support_card_list(), database_id)
        if self.update_mode == _DEFAULT_MODE and not card_list:
            print("No support card require update, skip.")
            return
        skill_page_mapping, mismatch_callback = self._generate_local_skill_mapping()
        detail_page = SupportCardDetailPage(self.support_card_cover_mapping, self.support_card_icon_mapping)
        def end_callback():
            if detail_page.failed_count > 0:
                print(f"Failed to create {detail_page.failed_count} pages")
        if card_list:
            self._run_in_multi_thread(thread_count, len(card_list), end_callback, detail_page.createPageInDatabase, 
                                  lambda i: (database_id, card_list[i], skill_page_mapping, mismatch_callback))
        if self.update_mode == _FULL_UPDATE_MODE and in_cloud_list:
            # update existed page
            print("update existed support card page...")
            in_cloud_list = self._update_precheck(in_cloud_list, persist_file_path)
            self._run_in_multi_thread(thread_count, len(in_cloud_list), lambda: None, detail_page.updatePageInDatabase, lambda i: (in_cloud_list[i][1], in_cloud_list[i][0],skill_page_mapping, mismatch_callback))
            self._update_postcheck(detail_page.failed_update_id_set, persist_file_path=SUPPORT_CARD_FAILED_PERSIST_PATH)
        self._retry_check(detail_page.failed_count, self.start_support_card_data_sync, database_title, root_page_id, thread_count)