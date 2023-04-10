import getopt
import sys

from src.sync_client import SyncType
from src.config import Properties
    
if __name__ == '__main__':
    opts,_ = getopt.getopt(sys.argv[1:], "f:",["skill_database_id=","chara_database_id=","support_card_database_id="])
    skill_database_id = None
    chara_database_id = None
    support_card_database_id = None
    for opt,arg in opts:
        if opt == '-f':
            dst = arg
        elif opt == '--skill_database_id':
            skill_database_id = arg
        elif opt == '--chara_database_id':
            chara_database_id = arg
        elif opt == '--support_card_database_id':
            support_card_database_id = arg
    properties = Properties(dst)
    if skill_database_id:
        properties.write_database_id(SyncType.skill.name, skill_database_id)
    if chara_database_id:
        properties.write_database_id(SyncType.character_card.name, chara_database_id)
    if support_card_database_id:
        properties.write_database_id(SyncType.support_card.name, support_card_database_id)
