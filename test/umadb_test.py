import unittest
import os
import sys

sys.path.insert(0,'.')

from src.db import Umadb
from src.model import *

class TestUmadb(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        dbpath = os.path.join(os.path.expanduser(
                '~'), 'AppData', 'LocalLow', 'Cygames', 'umamusume', 'master', 'master.mdb')
        self.db:Umadb = Umadb(dbpath)

    def test_skill_type(self):
        skill:Skill = next(self.db.get_all_skill_data())
        self.assertIsInstance(skill.id, str, "skill id should be string")
        self.assertIsInstance(skill.name, str, "skill name should be string")
        self.assertIsInstance(skill.description, str, "skill description should be string")
        self.assertIsInstance(skill.icon_id, str, "skill icon id should be string")
    
    def test_chara_card_type(self):
        card:CharacterCard = self.db.get_all_character_card_data()[0]
        self.assertIsInstance(card.id, str, "card id should be string")
        self.assertIsInstance(card.name, str, "card name should be string")
        self.assertIsInstance(card.bg_id, str, "card bg_id should be string")


if __name__ == '__main__':
    unittest.main()