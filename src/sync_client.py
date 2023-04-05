from tqdm import tqdm
from typing import Callable
from concurrent.futures import ThreadPoolExecutor
import threading
from enum import Enum

from src.config import Properties
from src.model import *
from src.notion import Database
from src.pages.skill_page import SkillDatabasePage, SkillDetailPage
from src.pages.character_card_page import CharacterCardDatabasePage, CharacterCardDetailPage
from src.pages.support_card_page import SupportCardDatabasePage,SupportCardDetailPage
from src.utils.file_utils import read_id_list, write_id_list
from src.generators import SourceGenerator

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
            func(*args)
        else:
            self.failed_retry_count = 0

    def _update_skill_database(self, database_id, skill_list: list[Skill], thread_count, attentive_check) -> None:
        # check update info
        record_file_path = f"{SyncType.skill.name}_update_{database_id}.record"
        database_page = SkillDatabasePage()
        new_skill_list,id_set_in_cloud = database_page.filterNewSkill(skill_list, database_id)
        record_set = set(read_id_list(record_file_path) or [])
        for id_in_cloud in id_set_in_cloud:
            record_set.add(id_in_cloud)
        new_skill_list = list(filter(lambda skill: skill.id not in record_set, new_skill_list))
        if not new_skill_list:
            print("No skill require update, skip.")
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
        # start update (now just create new page not update)
        detail_page = SkillDetailPage(self.skill_icon_mapping)
        def end_callback():
            if detail_page.failed_count > 0:
                print(f"Failed to create {detail_page.failed_count} pages")
        self._run_in_multi_thread(thread_count, len(new_skill_list), end_callback, detail_page.createPageInDatabase, lambda i: (database_id, new_skill_list[i]))
        self._retry_check(detail_page.failed_count, self._update_skill_database, database_id, skill_list, thread_count, attentive_check)

    def start_skill_data_sync(self, database_title, root_page_id, thread_count=1, attentive_check=False):
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
        self._update_skill_database(database_id, skill_list, thread_count, attentive_check)
    
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

    def start_character_card_data_sync(self, database_title, root_page_id, thread_count=1):
        """
        === Parameters ===
        param database_title: title of the database
        param root_page_id: id of the root page
        param thread_count: number of threads to use
        """
        print("start sync character card data...")
        database_id = self._ensure_notion_database_exists(root_page_id, database_title, SyncType.character_card)
        card_list = CharacterCardDatabasePage().filterNewCard(self._load_local_character_card_list(), database_id)
        if not card_list:
            print("No character card require update, skip.")
            return
        skill_page_mapping, mismatch_callback = self._generate_local_skill_mapping()
        local_skill_list = self._load_local_skill_list()
        local_skill_mapping = {skill.id : skill for skill in local_skill_list}
        detail_page = CharacterCardDetailPage(self.chara_cover_mapping, self.chara_icon_mapping, local_skill_mapping)
        def end_callback():
            if detail_page.failed_count > 0:
                print(f"Failed to create {detail_page.failed_count} pages")
        self._run_in_multi_thread(thread_count, len(card_list), end_callback, detail_page.createPageInDatabase, 
                                  lambda i: (database_id, card_list[i], skill_page_mapping, mismatch_callback))
        self._retry_check(detail_page.failed_count, self.start_character_card_data_sync, database_title, root_page_id, thread_count)
    
    def _load_local_support_card_list(self) -> list[SupportCard]:
        return self.source.get_all_support_card()
    
    def start_support_card_data_sync(self, database_title, root_page_id, thread_count=1):
        """
        === Parameters ===
        param database_title: title of the database
        param root_page_id: id of the root page
        param thread_count: number of threads to use
        """
        print("start sync support card data...")
        database_id = self._ensure_notion_database_exists(root_page_id, database_title, SyncType.support_card)
        card_list = SupportCardDatabasePage().filterNewCard(self._load_local_support_card_list(), database_id)
        if not card_list:
            print("No support card require update, skip.")
            return
        skill_page_mapping, mismatch_callback = self._generate_local_skill_mapping()
        detail_page = SupportCardDetailPage(self.support_card_cover_mapping, self.support_card_icon_mapping)
        def end_callback():
            if detail_page.failed_count > 0:
                print(f"Failed to create {detail_page.failed_count} pages")
        self._run_in_multi_thread(thread_count, len(card_list), end_callback, detail_page.createPageInDatabase, 
                                  lambda i: (database_id, card_list[i], skill_page_mapping, mismatch_callback))
        self._retry_check(detail_page.failed_count, self.start_support_card_data_sync, database_title, root_page_id, thread_count)