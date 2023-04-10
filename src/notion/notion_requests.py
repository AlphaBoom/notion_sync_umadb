from dataclasses import dataclass

from src.notion.notion_obj import *

@dataclass
class CreatePageRequest(Mixin):
    parent:Parent
    properties:Dict[str,Property]
    children:list[Block] = None
    icon:Optional[Union[Emoji,File]] = None
    cover:Optional[File] = None

@dataclass
class CreateDatabaseRequest(Mixin):
    parent:Parent
    title:list[RichText]
    properties:Dict[str,Property]
    icon:Optional[Union[Emoji,File]] = None
    cover:Optional[File] = None

@dataclass
class UpdatePageRequest(Mixin):
    properties:Dict[str,Property]
    page_id:Optional[str] = None
    icon:Optional[Union[Emoji,File]] = None
    cover:Optional[File] = None

@dataclass
class UpdateDatabaseRequest(Mixin):
    database_id:Optional[str]
    title:list[RichText]
    properties:Dict[str,Property]
    icon:Optional[Union[Emoji,File]] = None
    cover:Optional[File] = None

@dataclass
class UpdateBlockRequest(Mixin):
    block_id:str
    block:Block

@dataclass
class AppendBlockRequest(Mixin):
    children:list[Block]

