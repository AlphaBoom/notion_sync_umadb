from typing import Optional,Iterable,Union,Dict
from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin,config,Undefined
from enum import Enum

class Mixin(DataClassJsonMixin):
    dataclass_json_config = config(  # type: ignore
        undefined=Undefined.EXCLUDE,
        exclude=lambda f: f is None # type: ignore
    )["dataclasses_json"]

class ColorType(Enum):
    blue = 'blue'
    blue_background = 'blue_background'
    brown = 'brown'
    brown_background = 'brown_background'
    default = 'default'
    gray = 'gray'
    gray_background = 'gray_background'
    green = 'green'
    green_background = 'green_background'
    orange = 'orange'
    orange_background = 'orange_background'
    yellow = 'yellow'
    pink = 'pink'
    pink_background = 'pink_background'
    purple = 'purple'
    purple_background = 'purple_background'
    red = 'red'
    red_background = 'red_background'
    yellow_background = 'yellow_background'


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


class ParentType(Enum):
    DATABASE = 'database_id'
    PAGE = 'page_id'
    WORKSPACE = 'workspace'
    BLOCK = 'block_id'

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
    caption:Iterable[RichText] = None

@dataclass
class Breakcrumb(Mixin):
    pass

@dataclass
class BulletedListItem(Mixin):
    color:str
    rich_text:Iterable[RichText] = None
    children:Iterable['Block'] = None

@dataclass
class Callout(Mixin):
    rich_text:Iterable[RichText] = None
    icon:Optional[Union[Emoji,File]] = None

@dataclass
class Heading1(Mixin):
    rich_text:Iterable[RichText] = None
    color:str = 'default'
    is_toggleable:bool = False

@dataclass
class Heading2(Mixin):
    rich_text:Iterable[RichText] = None
    color:str = 'default'
    is_toggleable:bool = False

@dataclass
class Heading3(Mixin):
    rich_text:Iterable[RichText] = None
    color:str = 'default'
    is_toggleable:bool = False

@dataclass
class Paragraph(Mixin):
    rich_text:Iterable[RichText] = None
    color:str = 'default'
    children:Iterable['Block'] = None

@dataclass
class Block(Mixin):
    object:str = 'block'
    id:str = None
    parent:Parent = None
    created_time:str = None
    created_by:User = None
    last_edited_time:str = None
    last_edited_by:User = None
    archived:bool = None
    has_children:bool = None
    type:str = None
    bookmark:Optional[Bookmark] = None
    breadcrumb:Optional[Breakcrumb] = None
    bulleted_list_item:Optional[BulletedListItem] = None
    callout:Optional[Callout] = None
    heading_1:Optional[Heading1] = None
    heading_2:Optional[Heading2] = None
    heading_3:Optional[Heading3] = None
    paragraph:Optional[Paragraph] = None


class NumberFormat(Enum):
    argentine_peso = 'argentine_peso'
    baht = 'baht'
    number = 'number'
    number_with_commas = 'number_with_commas'


@dataclass
class PropertyNumber(Mixin):
    format:NumberFormat = NumberFormat.number

@dataclass
class Property(Mixin):
    id:str = None
    type:str = None
    title:Iterable[RichText] = None
    rich_text:Iterable[RichText] = None
    number:Optional[Union[PropertyNumber,int]] = None
    select:Optional[Union[Emoji,File]] = None
    multi_select:Iterable[Union[Emoji,File]] = None
    date:Optional[Dict[str,str]] = None
    people:Iterable[User] = None
    files:Iterable[File] = None
    checkbox:bool = None
    url:str = None
    email:str = None
    phone_number:str = None
    formula:Iterable[RichText] = None
    relation:Iterable[Union[Emoji,File]] = None
    rollup:Iterable[RichText] = None
    created_time:str = None
    created_by:User = None
    last_edited_time:str = None
    last_edited_by:User = None

@dataclass
class Database(Mixin):
    object:str
    id:str
    parent:Parent
    url:str
    created_time:str
    created_by:User
    last_edited_time:str
    last_edited_by:User
    title:Iterable[RichText]
    description:Iterable[RichText]
    properties:Dict[str,Property]
    icon:Optional[Union[Emoji,File]] = None
    cover:Optional[File] = None
    archived:bool = False
    is_inline:bool = False

@dataclass
class Page(Mixin):
    object:str
    id:str
    created_time:str
    created_by:User
    last_edited_time:str
    last_edited_by:User
    parent:Parent
    archived:bool
    properties:Dict[str,Property]
    url:str
    icon:Optional[Union[Emoji,File]] = None
    cover:Optional[File] = None

@dataclass
class NotionList(Mixin):
    object:str
    results:Iterable[Page]
    next_cursor:str = None
    has_more:bool = False
