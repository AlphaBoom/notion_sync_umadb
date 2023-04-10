from typing import Callable
import traceback
from abc import ABC,abstractmethod

from src.model import *
from src.notion import *

class DatabasePage(ABC):

    @abstractmethod
    def createDatabase(self, database_name, parent_page_id: str)->Database:
        pass
    
    @abstractmethod
    def updateDatabase(self, database_name, database_id)->Database:
        pass
    
    def getPageDictInNotionDatabase(self, database_id: str) -> dict[str, Page]:
        pages = self.getAllPageInNotionDatabase(database_id)
        page_dict = {}
        for page in pages:
            id = page.properties['id'].rich_text[0].text.content
            page_dict[id] = page
        return page_dict

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
                page_list.append(Page.from_dict(page))
            if not notion_list.has_more:
                break
        return page_list


_METHOD_UPDATE = 1
_METHOD_ADD = 2
_METHOD_REMOVE = 3

class DetailPage:

    def getFileInMapping(self, id, mapping:StrMapping) -> File:
        if mapping is not None:
            file = File(
                type=FileType.external,
                external=ExternalFile(url=mapping.get(id))
            )
            if file.external.url:
                return file
            else:
                print(f"file key:{id} not found.")

    def updatePageAndBlocks(self, properties:list[Property], page:Page, new_blocks:list[Block], icon_file=None, cover_file=None):
        updatePage(UpdatePageRequest(
                page_id=page.id,
                properties=properties,
                icon=icon_file,
                cover=cover_file,
            ))
        self._checkAndUpdateBlocks(page, new_blocks)
    
    def _getAllBlocksInPage(self, page:Page)->list[Block]:
        blocks = []
        start_cursor = None
        while True:
            notion_list = retrieveBlockChildren(
                page.id, start_cursor=start_cursor, page_size=100)
            if not notion_list:
                break
            start_cursor = notion_list.next_cursor
            for block in notion_list.results:
                blocks.append(Block.from_dict(block))
            if not notion_list.has_more:
                break
        return blocks
    
    def _checkAndUpdateBlocks(self, page:Page, new_blocks:list[Block]):
        blocks = self._getAllBlocksInPage(page)
        require_update_blocks = self._checkRequireUpdateBlocks(blocks, new_blocks)
        if require_update_blocks:
            # simple delete all blocks and append new blocks
            for block in blocks:
                deleteBlock(block.id)
            appendBlockChildren(page.id, new_blocks)

    def _checkRequireUpdateBlocks(self, blocks:list[Block], new_blocks:list[Block])->list[tuple[int, Block]]:
        index = 0
        length = len(blocks)
        index_new = 0
        length_new = len(new_blocks)
        ret = []
        while index < length or index_new < length_new:
            block = blocks[index] if index < length else None
            new_block = new_blocks[index_new] if index_new < length_new else None
            if block is None:
                ret.append((_METHOD_ADD, new_block))
                index_new += 1
            elif new_block is None:
                ret.append((_METHOD_REMOVE, block))
                index += 1
            elif self._is_block_euqal(block, new_block):
                index += 1
                index_new += 1
            elif block.type == self._get_local_block_type(new_block):
                ret.append((_METHOD_UPDATE, new_block))
                index += 1
                index_new += 1
            else:
                ret.append((_METHOD_REMOVE, block))
                ret.append((_METHOD_ADD, new_block))
                index += 1
                index_new += 1
        return ret
    
    def _get_local_block_type(self, block:Block):
        if block.type:
            return block.type
        elif block.heading_1:
            return 'heading_1'
        elif block.heading_2:
            return 'heading_2'
        elif block.heading_3:
            return 'heading_3'
        elif block.paragraph:
            return 'paragraph'
        elif block.numbered_list_item:
            return 'numbered_list_item'
        elif block.bulleted_list_item:
            return 'bulleted_list_item'
        else:
            return block.type
    
    def _is_block_euqal(self, block:Block, new_block:Block)->bool:
        if block.type == self._get_local_block_type(new_block):
            if block.type in ('heading_1','heading_2','heading_3','paragraph','numbered_list_item', 'bulleted_list_item'):
                rich_text = getattr(block, block.type).rich_text
                rich_text_new = getattr(new_block, block.type).rich_text
                if len(rich_text) == len(rich_text_new):
                    for i in range(len(rich_text)):
                        if rich_text[i].text.content != rich_text_new[i].text.content:
                            return False
                    return True
        return False
