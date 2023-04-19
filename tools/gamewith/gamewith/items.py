# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass


@dataclass
class SkillBrief:
    name: str
    description: str

@dataclass
class SupportCard:
    name: str
    nick_name: str
    rare: str
    card_type: str
    event_skill: list[SkillBrief]
    train_skill: list[SkillBrief]
