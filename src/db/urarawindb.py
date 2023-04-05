
from dataclasses import dataclass
from dataclasses_json import dataclass_json,Undefined
from typing import Optional

from src.config import Properties
from src.utils.net_utils import get_json_from_github_file
from src.model import *

_db_file_path = "output/urarawindb.json"

@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class UraraSupportCard:
    gwId: str
    id: str
    charaName: str
    imgUrl: str
    rare: str
    name: str
    type: Optional[str] = None
    db_id: Optional[int] = None
    rarity: Optional[int] = None
    skillList: Optional[list[str]] = None
    unique_effect: Optional[dict[str,int]] = None
    trainingEventSkill: Optional[list[str]] = None
    eventList: Optional[list[str]] = None

@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class UraraSkill:
    name:str
    imgUrl:str
    rare:str
    id:str
    db_id:Optional[int] = None
    icon_id:Optional[int] = None
    ability_time:Optional[int] = None
    cooldown:Optional[int] = None
    need_skill_point:Optional[int] = None
    grade_value:Optional[int] = None
    rarity:Optional[int] = None
    condition:Optional[str] = None
    condition2:Optional[str] = None
    ability_value:Optional[int] = None
    describe:Optional[str] = None

class Urarawindb:

    def __init__(self, properties:Properties):
        self.p = properties
        self.db = None

    def _ensure_db_available(self):
        if self.db:
            return
        self.db = get_json_from_github_file(self.p, _db_file_path, 'wrrwrr111', 'pretty-derby', 'master', 'src/assert/db.json')
    
    def get_all_skill_data(self)->list[UraraSkill]:
        self._ensure_db_available()
        return UraraSkill.schema().load(self.db['skills'], many=True)

    def get_all_support_card_data(self)->list[UraraSupportCard]:
        self._ensure_db_available()
        return UraraSupportCard.schema().load(self.db['supports'], many=True)
        