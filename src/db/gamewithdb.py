from dataclasses import dataclass
from dataclasses_json import dataclass_json,Undefined
from typing import Optional


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class GamewithSkill:
    name: str
    description: str

@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class GamewithSupportCard:
    name: str
    nick_name: str
    rare: str
    card_type: Optional[str]
    event_skill: Optional[list[GamewithSkill]]
    train_skill: Optional[list[GamewithSkill]]

class Gamewithdb:

    def __init__(self,dat_path="output/crawled_support_card.dat") -> None:
        self.dat_path = dat_path

    def get_all_support_card_data(self)->list[GamewithSupportCard]:
        with open(self.dat_path,"r",encoding="utf-8") as f:
            ret = []
            for line in f.readlines():
                ret.append(GamewithSupportCard.from_json(line))
            return ret
            