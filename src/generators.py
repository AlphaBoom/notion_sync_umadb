from abc import ABC, abstractmethod
import os

from src.db import *
from src.model import *
from src.config import Properties
from src.translators import UraraWinTranslator,TrainersLegendTranslator


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
    def get_all_skill(self) -> list[Skill]:
        pass

    @abstractmethod
    def get_all_character_card(self) -> list[CharacterCard]:
        pass

    @abstractmethod
    def get_all_support_card(self) -> list[SupportCard]:
        pass


class LocalSourceGenerator(SourceGenerator):
    def __init__(self, properties: Properties, gamedatapath: str = None) -> None:
        super().__init__()
        if gamedatapath:
            dbpath = os.path.join(gamedatapath, 'master', 'master.mdb')
        else:
            dbpath = os.path.join(os.path.expanduser(
                '~'), 'AppData', 'LocalLow', 'Cygames', 'umamusume', 'master', 'master.mdb')
        self.db: Umadb = Umadb(dbpath)
        self.p = properties
        self.translator = TrainersLegendTranslator(properties)

    def get_all_skill(self) -> list[Skill]:
        skill_list = list(self.db.get_all_skill_data())
        for skill in skill_list:
            skill.original_name = skill.name
        return [self.translator.translate_skill(skill) for skill in skill_list]

    def get_all_character_card(self) -> list[CharacterCard]:
        card_list = self.db.get_all_character_card_data()
        for card in card_list:
            card.original_name = card.name
        return [self.translator.translate_chara_card(card) for card in card_list]

    def get_all_support_card(self) -> list[SupportCard]:
        uraradb = Urarawindb(self.p)
        skill_id_mapping = {skill.id: str(
            skill.db_id) for skill in uraradb.get_all_skill_data() if skill.db_id}
        card_skill_list_mapping = {str(
            card_u.db_id): card_u.trainingEventSkill for card_u in uraradb.get_all_support_card_data()}
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
            if card.id in card_skill_list_mapping:
                card.event_skill_list = card_skill_list_mapping[card.id]
        return [self.translator.translate_support_card(card) for card in card_list]


class UraraWinSourceGenerator(SourceGenerator):
    def __init__(self, properties: Properties) -> None:
        self.translator = UraraWinTranslator(properties)
        self.db = Urarawindb(properties)
        self.skill_list_u: list[UraraSkill] = self.db.get_all_skill_data()
        self.chara_card_list_u: list[UraraCharaCard] = self.db.get_all_chara_card_data(
        )
        self.support_card_list_u: list[UraraSupportCard] = self.db.get_all_support_card_data(
        )

    def _format_img_url(self, url: str):
        if not url:
            return None
        if url.startswith('http'):
            return url
        # just use github raw url, urara win use vercel to host image, not sure use github raw url to render is fast enough
        return f"https://raw.githubusercontent.com/wrrwrr111/pretty-derby/master/public/{url}"

    def generate_skill_icon_mapping(self):
        return {skill.id: self._format_img_url(skill.imgUrl) for skill in self.skill_list_u if skill.imgUrl}

    def generate_chara_icon_mapping(self):
        return {card.id: self._format_img_url(card.imgUrl) for card in self.chara_card_list_u if card.imgUrl}

    def generate_chara_cover_mapping(self):
        # not provide chara cover just return None, no cover is tolerable
        return None

    def generate_support_card_icon_mapping(self):
        # not provide icon use cover instead
        return self.generate_support_card_cover_mapping()

    def generate_support_card_cover_mapping(self):
        return {card.id: self._format_img_url(card.imgUrl) for card in self.support_card_list_u if card.imgUrl}

    def _skill_ability_to_effect(self, ability: UraraSkillAbility) -> SkillEffect:
        return SkillEffect(type=ability.type, value=ability.value, target_type=ability.target_type, target_value=ability.target_value)

    def get_all_skill(self) -> list[Skill]:
        ret = []
        for skill_u in self.skill_list_u:
            id = skill_u.id
            original_name = skill_u.name
            if skill_u.rarity:
                rarity = skill_u.rarity
                if rarity == 1:
                    rarity = SkillRarity.Normal
                elif rarity == 2:
                    rarity = SkillRarity.Rare
                elif 3 <= rarity <= 5:
                    rarity = SkillRarity.Unique
                elif rarity == 6:
                    rarity = SkillRarity.Upgrade
                else:
                    rarity = SkillRarity.Normal
            else:
                rare = skill_u.rare
                if rare == '固有':
                    rarity = SkillRarity.Unique
                elif rare == 'ノーマル':
                    rarity = SkillRarity.Normal
                elif rare == 'レア':
                    rarity = SkillRarity.Rare
                elif rare == 'アップグレード':
                    rarity = SkillRarity.Upgrade
                else:
                    rarity = SkillRarity.Normal
            skill_data_list = []
            # skill 1
            if skill_u.condition:
                skill_data = SkillData(precondition="", condition=skill_u.condition, duration=skill_u.ability_time or 0, cooldown=skill_u.cooldown or 0)
                skill_data.effectList = []
                if skill_u.ability:
                    for ability in skill_u.ability:
                        skill_data.effectList.append(
                            self._skill_ability_to_effect(ability))
                skill_data_list.append(skill_data)
            # skill 2
            if skill_u.condition2:
                skill_data = SkillData(precondition="", condition=skill_u.condition2)
                skill_data.effectList = []
                if skill_u.ability2:
                    for ability in skill_u.ability2:
                        skill_data.effectList.append(
                            self._skill_ability_to_effect(ability))
                skill_data_list.append(skill_data)
            skill = Skill(id, skill_u.name, skill_u.describe, id, id,
                       rarity, skill_data_list, original_name)
            ret.append(self.translator.translate_skill(skill))
        return ret

    def _convert_grow(self, grow: str):
        if not grow:
            return 0
        return int(grow.strip("+%"))

    def _convert_proper(self, proper: str):
        if not proper:
            return 1
        return 72 - ord(proper)

    def get_all_character_card(self) -> list[CharacterCard]:
        ret = []
        for card_u in self.chara_card_list_u:
            original_name = f"[{card_u.name}]{card_u.charaName}"
            name = original_name
            id = card_u.id
            speed_grow = self._convert_grow(card_u.speedGrow)
            power_grow = self._convert_grow(card_u.powerGrow)
            stamina_grow = self._convert_grow(card_u.staminaGrow)
            guts_grow = self._convert_grow(card_u.gutsGrow)
            wiz_grow = self._convert_grow(card_u.wisdomGrow)
            talentInfo = Talent(speed_grow, stamina_grow,
                                power_grow, guts_grow, wiz_grow)
            proper_set = {}
            proper_set[3] = Proper(
                self._convert_proper(card_u.shortDistance),
                self._convert_proper(card_u.mile),
                self._convert_proper(card_u.mediumDistance),
                self._convert_proper(card_u.longDistance),
                self._convert_proper(card_u.escape),
                self._convert_proper(card_u.leading),
                self._convert_proper(card_u.insert),
                self._convert_proper(card_u.tracking),
                self._convert_proper(card_u.grass),
                self._convert_proper(card_u.dirt),
            )
            rarity_skill_set = {}
            if card_u.uniqueSkillList:
                rarity_skill_set[3] = [id for id in card_u.uniqueSkillList]
            available_skill_set = {}
            if card_u.initialSkillList:
                available_skill_set[1] = [id for id in card_u.skillList]
            if card_u.awakeningSkillist:
                available_skill_set[3] = [
                    id for id in card_u.awakeningSkillist]
            card = CharacterCard(id, name, "", talentInfo, proper_set=proper_set, rairty_skill_set=rarity_skill_set,
                              available_skill_set=available_skill_set, original_name=original_name)
            ret.append(self.translator.translate_chara_card(card))
        return ret

    def get_all_support_card(self) -> list[SupportCard]:
        ret = []
        for card_u in self.support_card_list_u:
            original_name = f"[{card_u.name}]{card_u.charaName}"
            name = original_name
            id = card_u.id
            if card_u.rare == 'SSR':
                rarity = SupportCardRarity.SSR
            elif card_u.rare == 'SR':
                rarity = SupportCardRarity.SR
            else:
                rarity = SupportCardRarity.R
            type = card_u.type or "スピード"
            if type == "スピード":
                type = SupportCardType.Speed
            elif type == "パワー":
                type = SupportCardType.Power
            elif type == "根性":
                type = SupportCardType.Guts
            elif type == "賢さ":
                type = SupportCardType.Wiz
            elif type == "スタミナ":
                type = SupportCardType.Stamina
            elif type == "友人":
                type = SupportCardType.Friend
            elif type == "チーム":
                type = SupportCardType.Team
            else:
                type = SupportCardType.Team
            train_skill_list = []
            if card_u.trainingEventSkill and card_u.skillList:
                train_skill_list = [
                    id for id in card_u.skillList if id not in card_u.trainingEventSkill]
            card = SupportCard(id, name, rarity, type, event_skill_list=card_u.trainingEventSkill,
                            train_skill_list=train_skill_list, original_name=original_name)
            ret.append(self.translator.translate_support_card(card))
        return ret
