from enum import Enum

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

class FileType(Enum):
    external = 'external'
    file = 'file'

class ParentType(Enum):
    DATABASE = 'database_id'
    PAGE = 'page_id'
    WORKSPACE = 'workspace'
    BLOCK = 'block_id'

class RichTextType(Enum):
    text = 'text'
    mention = 'mention'
    equation = 'equation'

class MentionType(Enum):
    date = 'date'
    databse = 'database'
    link_preview = 'link_preview'
    page = 'page'
    user = 'user'

class NumberFormat(Enum):
    argentine_peso = 'argentine_peso'
    baht = 'baht'
    number = 'number'
    number_with_commas = 'number_with_commas'
    percent = 'percent'