from abc import ABC, abstractmethod
import os
import json
import time

from src.db import *
from src.model import *
from src.config import Properties
from src.utils.net_utils import get_json_from_github_file

class SourceGenerator(ABC):

    def generate_skill_icon_mapping(self):
        return None
    
    def generate_chara_cover_mapping(self):
        return None
    
    def generate_chara_icon_mapping(self):
        return None
    
    def generate_support_card_icon_mapping(self):
        return None
    
    def generate_support_card_cover_mapping(self):
        return None
    
    @abstractmethod
    def get_all_skill(self)->list[Skill]:
        pass
    
    @abstractmethod
    def get_all_character_card(self)->list[CharacterCard]:
        pass
    
    @abstractmethod
    def get_all_support_card(self)->list[SupportCard]:
        pass

class LocalSourceGenerator(SourceGenerator):
    def __init__(self, properties:Properties, gamedatapath:str = None) -> None:
        super().__init__()
        if gamedatapath:
            dbpath = os.path.join(gamedatapath, 'master', 'master.mdb')
        else:
            dbpath = os.path.join(os.path.expanduser(
                '~'), 'AppData', 'LocalLow', 'Cygames', 'umamusume', 'master', 'master.mdb')
        self.db:Umadb = Umadb(dbpath)
        self.p = properties
        self.translate_mapping = None
    
    def _ensure_translate_mapping(self, locale:str):
        if self.translate_mapping:
            return
        target_file = f"output/local_translate_{locale}.json"
        self.translate_mapping = get_json_from_github_file(self.p, target_file, 'wrrwrr111', 'pretty-derby', 'master', f'src/assert/locales/{locale}.json')

    def translate(self, text, locale:str='zh_CN'):
        if not text:
            return None
        self._ensure_translate_mapping(locale)
        return self.translate_mapping.get(text, text)

    def get_all_skill(self)->list[Skill]:
        skill_list = list(self.db.get_all_skill_data())
        for skill in skill_list:
            skill.original_name = skill.name
            skill.name = self.translate(skill.name)
        return skill_list
    
    def _extract_name(self, name:str):
        if name.startswith('['):
            nick_name = name[1:name.index(']')]
            real_name = name[name.index(']') + 1:]
            return nick_name,real_name
        return None,name

    def get_all_character_card(self)->list[CharacterCard]:
        card_list = self.db.get_all_character_card_data()
        for card in card_list:
            card.original_name = card.name
            nick_name,real_name = self._extract_name(card.name)
            nick_name = self.translate(nick_name)
            real_name = self.translate(real_name)
            if nick_name:
                card.name = f"[{nick_name}]{real_name}"
            else:
                card.name = real_name
        return card_list
    
    def get_all_support_card(self)->list[SupportCard]:
        uraradb = Urarawindb(self.p)
        skill_id_mapping = {skill.id : str(skill.db_id) for skill in uraradb.get_all_skill_data() if skill.db_id}
        card_skill_list_mapping = { str(card_u.db_id) : card_u.trainingEventSkill for card_u in uraradb.get_all_support_card_data()}
        for skill_list in card_skill_list_mapping.values():
            if not skill_list:
                continue
            for i in range(len(skill_list)):
                if skill_list[i] in skill_id_mapping:
                    skill_list[i] = skill_id_mapping[skill_list[i]]
                else:
                    print(f"skill {skill_list[i]} not found")
        card_list = self.db.get_all_support_card_data()
        for card in card_list:
            card.original_name = card.name
            nick_name,real_name = self._extract_name(card.name)
            nick_name = self.translate(nick_name)
            real_name = self.translate(real_name)
            if nick_name:
                card.name = f"[{nick_name}]{real_name}"
            else:
                card.name = real_name
            if card.id in card_skill_list_mapping:
                card.event_skill_list = card_skill_list_mapping[card.id]
        return card_list

class UraraWinSourceGenerator(SourceGenerator):
    def get_all_skill(self)->list[Skill]:
        pass
    
    def get_all_character_card(self)->list[CharacterCard]:
        pass
    
    def get_all_support_card(self)->list[SupportCard]:
        pass
    