import sqlite3
from typing import Generator

from src.model import SkillData,SkillEffect,Skill

_TABLE_SKILL_DATA = 'skill_data'
_TABLE_TEXT_DATA = 'text_data'

class Umadb:
    def __init__(self, dbpath:str) -> None:
        self.dbpath = dbpath
    
    def __enter__(self) -> sqlite3.Connection:
        self.conn = sqlite3.connect(self.dbpath)
        return self.conn
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.conn.close()
    
    def create_table(self, table_name:str, columns:dict) -> None:
        with self as conn:
            cursor = conn.cursor()
            cursor.execute(f'CREATE TABLE {table_name} ({", ".join([f"{key} {value}" for key, value in columns.items()])})')
            conn.commit()
    
    def insert(self, table_name:str, values:dict) -> None:
        with self as conn:
            cursor = conn.cursor()
            cursor.execute(f'INSERT INTO {table_name} ({", ".join(values.keys())}) VALUES ({", ".join(["?" for _ in values.values()])})', tuple(values.values()))
            conn.commit()
    
    def select(self, table_name:str, columns:tuple, where:dict=None) -> list:
        with self as conn:
            cursor = conn.cursor()
            if where is None:
                cursor.execute(f'SELECT {", ".join(columns)} FROM {table_name}')
            else:
                cursor.execute(f'SELECT {", ".join(columns)} FROM {table_name} WHERE {where["column"]} = ?', (where["value"],))
            return cursor.fetchall()
    
    def update(self, table_name:str, values:dict, where:dict) -> None:
        with self as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE {table_name} SET {", ".join([f"{key} = ?" for key in values.keys()])} WHERE {where["column"]} = ?', tuple(values.values()) + (where["value"],))
            conn.commit()
    
    def delete(self, table_name:str, where:dict) -> None:
        with self as conn:
            cursor = conn.cursor()
            cursor.execute(f'DELETE FROM {table_name} WHERE {where["column"]} = ?', (where["value"],))
            conn.commit()
    
    def drop_table(self, table_name:str) -> None:
        with self as conn:
            cursor = conn.cursor()
            cursor.execute(f'DROP TABLE {table_name}')
            conn.commit()

    def _create_skill_effect(self, row:tuple, start) -> SkillEffect:
        return 
    
    def get_all_skill_data(self) -> Generator[SkillData,None,None]:
        with self as conn:
            cursor = conn.cursor()
            _text = _TABLE_TEXT_DATA
            _skill = _TABLE_SKILL_DATA
            cursor.execute(
                f'SELECT {_text}.[text], {_text}.category, {_skill}.* FROM {_text} INNER JOIN {_skill} \
                    ON {_text}.[index] = {_skill}.id WHERE {_text}.category IN (47,48) ORDER BY {_skill}.id, {_text}.category')
            while (row := cursor.fetchone()) is not None:
                description = cursor.fetchone()[0]
                skillDataList = []
                for i in range(2):
                    left = 15 + i*26
                    if not row[left + 1]:
                        break
                    effectList = []
                    for i in range(3):
                        start = 20+i*7
                        if row[start] != 0:
                            effectList.append(SkillEffect(*row[start:start + 7]))
                    skillDataList.append(SkillData(*row[left:left+5], effectList))
                yield Skill(row[2], row[0], description,row[-7], skillDataList)


    
    