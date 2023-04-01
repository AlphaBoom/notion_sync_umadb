import os
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor

from src.model import *
from src.db import Umadb
from src.pages.skill_page import SkillDatabasePage, SkillDetailPage


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

    def setup_external_resource_mapping(self, skill_icon_mapping: dict[str,str] = None) -> None:
        self.skill_icon_mapping = skill_icon_mapping

    def _load_local_skill_list(self) -> list:
        db = Umadb(self.dbpath)
        return list(db.get_all_skill_data())

    def _ensure_local_resource_exists(self) -> None:
        pass

    def _ensure_notion_database_exists(self, parent_page_id, title) -> str:
        id = None
        stored_file_name = 'databaseid'
        if os.path.exists(stored_file_name):
            with open(stored_file_name, mode='r') as f:
                id = f.readline()
        if id:
            return id
        else:
            page_database = SkillDatabasePage().createDatabase(title, parent_page_id)
            with open(stored_file_name, mode='w') as f:
                f.write(page_database.id)
            return page_database.id


    def _update_notion_database(self, database_id, skill_list: list[Skill], thread_count) -> None:
        pool = ThreadPoolExecutor(thread_count)
        # check update info
        print(f"start to fetch current skill list from database {database_id}")
        new_skill_list = SkillDatabasePage().filterNewSkill(skill_list, database_id)
        if not new_skill_list:
            print("No new skill to update")
            return
        print(f"local skill count: {len(skill_list)}, new skill count: {len(new_skill_list)}")
        # start update (now just create new page not update)
        detail_page = SkillDetailPage(self.skill_icon_mapping)
        with tqdm(total=len(new_skill_list)) as pbar:
            def callback(future):
                pbar.update(1)
            for i in range(len(new_skill_list)):
                pool.submit(detail_page.createPageInDatabase, database_id, new_skill_list[i]).add_done_callback(callback)
            pool.shutdown()
        if detail_page.failed_count > 0:
            print(f"Failed to create {detail_page.failed_count} pages")

    def start_skill_data_sync(self, database_title, root_page_id, thread_count=1):
        """
        === Parameters ===
        param database_title: title of the database
        param root_page_id: id of the root page
        param thread_count: number of threads to use
        """
        self._ensure_local_resource_exists()
        database_id = self._ensure_notion_database_exists(
            root_page_id, database_title)
        print(f"ensure database {database_title} exists, id: {database_id}")
        skill_list = self._load_local_skill_list()
        self._update_notion_database(database_id, skill_list, thread_count)
