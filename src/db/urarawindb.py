
from dataclasses import dataclass
from dataclasses_json import dataclass_json,Undefined
from typing import Optional

from src.config import Properties
from src.utils.net_utils import get_json_from_github_file
from src.model import *

_DB_FILE_PATH = "output/urarawindb.json"

@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class UraraSupportCard:
    gwId: str
    id: str
    charaName: str
    rare: str
    name: str
    imgUrl: Optional[str] = None
    type: Optional[str] = None
    db_id: Optional[int] = None
    rarity: Optional[int] = None
    skillList: Optional[list[str]] = None
    unique_effect: Optional[dict[str,int]] = None
    trainingEventSkill: Optional[list[str]] = None
    eventList: Optional[list[str]] = None

@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class UraraSkillAbility:
    type:int
    value:int
    target_type:int
    target_value:int

@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class UraraSkill:
    name:str
    rare:str
    id:str
    imgUrl:Optional[str] = None
    db_id:Optional[int] = None
    icon_id:Optional[int] = None
    ability_time:Optional[int] = None
    cooldown:Optional[int] = None
    need_skill_point:Optional[int] = None
    grade_value:Optional[int] = None
    rarity:Optional[int] = None
    condition:Optional[str] = None
    condition2:Optional[str] = None
    ability:Optional[list[UraraSkillAbility]] = None
    ability2:Optional[list[UraraSkillAbility]] = None
    ability_value:Optional[int] = None
    describe:Optional[str] = None

@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class UraraCharaCard:
    id:str
    gwId:str
    rare:str
    name:str
    charaName:str
    grass:str
    dirt:str
    shortDistance:str
    mile:str
    mediumDistance:str
    longDistance:str
    escape:str
    leading:str
    insert:str
    tracking:str
    default_rarity:Optional[int] = None
    imgUrl:Optional[str] = None
    speedGrow:Optional[str] = None
    staminaGrow:Optional[str] = None
    powerGrow:Optional[str] = None
    gutsGrow:Optional[str] = None
    wisdomGrow:Optional[str] = None
    db_id:Optional[int] = None
    hideEvent:Optional[list[str]] = None
    uniqueSkillList:Optional[list[str]] = None
    initialSkillList:Optional[list[str]] = None
    awakeningSkillist:Optional[list[str]] = None
    skillList:Optional[list[str]] = None
    eventList:Optional[list[str]] = None
    eventList0:Optional[list[str]] = None
    eventList1:Optional[list[str]] = None
    eventList2:Optional[list[str]] = None
    eventList3:Optional[list[str]] = None
    eventList4:Optional[list[str]] = None
    raceList:Optional[dict[str,dict[str,str]]] = None


class Urarawindb:

    def __init__(self, properties:Properties):
        self.p = properties
        self.db = None

    def _ensure_db_available(self):
        if self.db:
            return
        self.db = get_json_from_github_file(self.p, _DB_FILE_PATH, 'wrrwrr111', 'pretty-derby', 'master', 'src/assert/db.json')
    
    def get_all_skill_data(self)->list[UraraSkill]:
        self._ensure_db_available()
        return UraraSkill.schema().load(self.db['skills'], many=True)

    def get_all_support_card_data(self)->list[UraraSupportCard]:
        self._ensure_db_available()
        return UraraSupportCard.schema().load(self.db['supports'], many=True)

    def get_all_chara_card_data(self)->list[UraraCharaCard]:
        self._ensure_db_available()
        return UraraCharaCard.schema().load(self.db['players'], many=True)
        