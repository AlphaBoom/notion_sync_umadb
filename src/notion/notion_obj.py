from typing import Optional,Union,Dict
from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin,config,Undefined

from src.notion.noton_enums import *

class Mixin(DataClassJsonMixin):
    dataclass_json_config = config(  # type: ignore
        undefined=Undefined.EXCLUDE,
        exclude=lambda f: f is None # type: ignore
    )["dataclasses_json"]

@dataclass
class Emoji(Mixin):
    emoji:str
    type:str = 'emoji'

@dataclass
class NotionHostedFile(Mixin):
    url:str
    expiry_time:str = None

@dataclass
class ExternalFile(Mixin):
    url:str

@dataclass
class File(Mixin):
    type:str
    file:Optional[NotionHostedFile] = None
    external:Optional[ExternalFile] = None

@dataclass
class User(Mixin):
    object:str
    id:str
    type:Optional[str] = None
    name:Optional[str] = None
    avatar_url:Optional[str] = None

@dataclass
class Parent(Mixin):
    type:ParentType
    database_id:Optional[str] = None
    page_id:Optional[str] = None
    workspace:Optional[bool] = None
    block_id:Optional[str] = None

@dataclass
class Annotation(Mixin):
    bold:bool = False
    italic:bool = False
    strikethrough:bool = False
    underline:bool = False
    code:bool = False
    color:str = 'default'

@dataclass
class Equation(Mixin):
    expression:str

@dataclass
class MentionDatabase(Mixin):
    id:str

@dataclass
class MentionDate(Mixin):
    start:str
    end:str = None

@dataclass
class MentionLinkPreview(Mixin):
    url:str

@dataclass
class MentionPage(Mixin):
    id:str

@dataclass
class MentionTempalteMention(Mixin):
    type:str

@dataclass
class MentionUser(Mixin):
    user:User

@dataclass
class Mention(Mixin):
    type:str
    database:Optional[MentionDatabase] = None
    date:Optional[MentionDate] = None
    link_preview:Optional[MentionLinkPreview] = None
    page:Optional[MentionPage] = None
    template_mention:Optional[MentionTempalteMention] = None
    user:Optional[MentionUser] = None

@dataclass
class Link(Mixin):
    url:str

@dataclass
class Text(Mixin):
    content:str
    link:Optional[Link] = None

@dataclass
class RichText(Mixin):
    type:str = 'text'
    plain_text:str = None
    annotations:Optional[Annotation] = None
    text:Optional[Text] = None
    mention:Optional[Mention] = None
    equation:Optional[Equation] = None
    href:Optional[str] = None


@dataclass
class Bookmark(Mixin):
    url:str
    caption:list[RichText] = None

@dataclass
class Breakcrumb(Mixin):
    pass

@dataclass
class BulletedListItem(Mixin):
    color:str
    rich_text:list[RichText] = None
    children:list['Block'] = None

@dataclass
class Callout(Mixin):
    rich_text:list[RichText] = None
    icon:Optional[Union[Emoji,File]] = None

@dataclass
class Heading1(Mixin):
    rich_text:list[RichText] = None
    color:str = 'default'
    is_toggleable:bool = False

@dataclass
class Heading2(Mixin):
    rich_text:list[RichText] = None
    color:str = 'default'
    is_toggleable:bool = False

@dataclass
class Heading3(Mixin):
    rich_text:list[RichText] = None
    color:str = 'default'
    is_toggleable:bool = False

@dataclass
class Paragraph(Mixin):
    rich_text:list[RichText] = None
    color:str = 'default'
    children:list['Block'] = None

@dataclass
class Table(Mixin):
    table_width:int
    has_column_header:bool
    has_row_header:bool
    children:list['Block'] = None

@dataclass
class TableRow(Mixin):
    cells: list[list[RichText]]

@dataclass
class Block(Mixin):
    object:str = 'block'
    id:str = None
    parent:Parent = None
    created_time:str = None
    created_by:User = None
    last_edited_time:Optional[str] = None
    last_edited_by:Optional[User] = None
    archived:Optional[bool] = None
    has_children:Optional[bool] = None
    type:Optional[str] = None
    bookmark:Optional[Bookmark] = None
    breadcrumb:Optional[Breakcrumb] = None
    bulleted_list_item:Optional[BulletedListItem] = None
    callout:Optional[Callout] = None
    heading_1:Optional[Heading1] = None
    heading_2:Optional[Heading2] = None
    heading_3:Optional[Heading3] = None
    paragraph:Optional[Paragraph] = None
    table:Optional[Table] = None
    table_row:Optional[TableRow] = None
    divider:Optional[dict] = None


@dataclass
class PropertyNumber(Mixin):
    format:NumberFormat = NumberFormat.number

@dataclass
class SelectOptions(Mixin):
    name:str
    color:Optional[ColorType] = None
    id:Optional[int] = None

@dataclass
class PropertySelect(Mixin):
    options:Optional[list[SelectOptions]] = None

@dataclass
class Property(Mixin):
    id:Optional[str] = None
    type:Optional[str] = None
    title:Optional[list[RichText]] = None
    rich_text:Optional[list[RichText]] = None
    number:Optional[Union[PropertyNumber,int]] = None
    select:Optional[PropertySelect] = None
    multi_select:Optional[list[Union[Emoji,File]]] = None
    date:Optional[Dict[str,str]] = None
    people:Optional[list[User]] = None
    files:Optional[list[File]] = None
    checkbox:Optional[bool] = None
    url:Optional[str] = None
    email:Optional[str] = None
    phone_number:Optional[str] = None
    formula:Optional[list[RichText]] = None
    relation:Optional[list[Union[Emoji,File]]] = None
    rollup:Optional[list[RichText]] = None
    created_time:Optional[str] = None
    created_by:Optional[User] = None
    last_edited_time:Optional[str] = None
    last_edited_by:Optional[User] = None

@dataclass
class Database(Mixin):
    object:str
    id:str
    parent:Parent
    url:str
    properties:Dict[str,Property]
    created_time:Optional[str] = None
    created_by:Optional[User] = None
    last_edited_time:Optional[str] = None
    last_edited_by:Optional[User] = None
    title:Optional[list[RichText]] = None
    description:Optional[list[RichText]] = None
    icon:Optional[Union[Emoji,File]] = None
    cover:Optional[File] = None
    archived:bool = False
    is_inline:bool = False

@dataclass
class Page(Mixin):
    object:str
    id:str
    parent:Parent
    properties:Dict[str,Property]
    url:str
    created_time:Optional[str] = None
    created_by:Optional[User] = None
    last_edited_time:Optional[str] = None
    last_edited_by:Optional[User] = None
    archived:bool = False
    icon:Optional[Union[Emoji,File]] = None
    cover:Optional[File] = None

@dataclass
class NotionList(Mixin):
    object:str
    has_more:bool = False
    results:Optional[list[Page]] = None
    next_cursor:Optional[str] = None
