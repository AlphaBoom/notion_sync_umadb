from typing import Callable
import traceback

from src.model import *
from src.notion import *

class DatabasePage:
    
    def getIdSetInNotionDatabase(self, database_id: str) -> set[int]:
        pages = self.getAllPageInNotionDatabase(database_id)
        id_set = set()
        for page in pages:
            id_set.add(int(page.properties['id'].number))
        return id_set

    def getAllPageInNotionDatabase(self, database_id: str) -> list[Page]:
        page_list = []
        start_cursor = None
        while True:
            notion_list = queryDatabase(
                database_id, start_cursor=start_cursor, page_size=100)
            if not notion_list:
                break
            start_cursor = notion_list.next_cursor
            for page in notion_list.results:
                page_list.append(page)
            if not notion_list.has_more:
                break
        return page_list