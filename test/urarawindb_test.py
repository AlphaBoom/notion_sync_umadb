import unittest
import os
import sys

sys.path.insert(0,'.')

from src.db import Urarawindb
from src.model import *
from src.config import Properties


class TestUrarawindb(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.db = Urarawindb(Properties("local.properties"))

    def test_get_all_skill(self):
        skill_list = self.db.get_all_skill_data()
        self.assertGreater(len(skill_list), 0, "skill list should not be empty")
    
    def test_get_all_support_card(self):
        card_list = self.db.get_all_support_card_data()
        self.assertGreater(len(card_list), 0, "support card list should not be empty")
    
    def test_get_all_chara_card(self):
        card_list = self.db.get_all_chara_card_data()
        self.assertGreater(len(card_list), 0, "chara card list should not be empty")

if __name__ == '__main__':
    unittest.main()