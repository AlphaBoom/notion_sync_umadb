from abc import ABC, abstractmethod
import os
from src.db import Umadb

from src.model import *

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
    def __init__(self, gamedatapath:str = None) -> None:
        super().__init__()
        if gamedatapath:
            dbpath = os.path.join(gamedatapath, 'master', 'master.mdb')
        else:
            dbpath = os.path.join(os.path.expanduser(
                '~'), 'AppData', 'LocalLow', 'Cygames', 'umamusume', 'master', 'master.mdb')
        self.db:Umadb = Umadb(dbpath)

    def get_all_skill(self)->list[Skill]:
        return list(self.db.get_all_skill_data())
    
    def get_all_character_card(self)->list[CharacterCard]:
        return self.db.get_all_character_card_data()
    
    def get_all_support_card(self)->list[SupportCard]:
        return self.db.get_all_support_card_data()

class UraraWinSourceGenerator(SourceGenerator):
    def get_all_skill(self)->list[Skill]:
        pass
    
    def get_all_character_card(self)->list[CharacterCard]:
        pass
    
    def get_all_support_card(self)->list[SupportCard]:
        pass
    