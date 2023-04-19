import unittest
import sys

sys.path.insert(0,'.')

from src.db import Gamewithdb
from src.model import *

class TestGamewithdb(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.db = Gamewithdb()
    
    def test_get_all_support_card(self):
        card_list = self.db.get_all_support_card_data()
        self.assertGreater(len(card_list), 0, "support card list should not be empty")

if __name__ == '__main__':
    unittest.main()