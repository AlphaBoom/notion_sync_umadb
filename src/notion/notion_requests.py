from dataclasses import dataclass

from src.notion.notion_obj import *

@dataclass
class CreatePageRequest(Mixin):
    parent:Parent
    properties:Dict[str,Property]
    children:Iterable[Block] = None
    icon:Optional[Union[Emoji,File]] = None
    cover:Optional[File] = None

@dataclass
class CreateDatabaseRequest(Mixin):
    parent:Parent
    title:Iterable[RichText]
    properties:Dict[str,Property]
    icon:Optional[Union[Emoji,File]] = None
    cover:Optional[File] = None

