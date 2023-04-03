from dataclasses import dataclass,field
from typing import List
from enum import Enum
from collections import namedtuple

Talent = namedtuple('Talent', 'speed stamina power guts wiz')
Proper = namedtuple('Proper', 'short mile middle long nige senko sashi oikomi turf dirt')
Status = namedtuple('Status', 'speed stamina power guts wiz')
EffectTable = namedtuple('EffectTable', 'init limit_lv5 limit_lv10 limit_lv15 limit_lv20 limit_lv30 limit_lv35 limit_lv40 limit_lv45 limit_lv50')
UniqueEffect = namedtuple('UniqueEffect', 'lv type_0 value_0 value_0_1 value_0_2 value_0_3 value_0_4 type_1 value_1 value_1_1 value_1_2 value_1_3 value_1_4')


class SkillType(Enum):
    Speed = 1
    Stamina = 2
    Power = 3
    Guts = 4
    Wiz = 5
    RunningStyleExOonige = 6
    HpDecRate = 7
    VisibleDistance = 8
    HpRate = 9
    StartDash = 10
    ForceOvertakeIn = 11
    ForceOvertakeOut = 12
    TemptationEndTime = 13
    StartDelayFix = 14
    NOUSE_13 = 15
    NOUSE_14 = 16
    NOUSE = 17
    NOUSE_3 = 18
    NOUSE_21 = 19
    NOUSE_8 = 20
    CurrentSpeed = 21
    CurrentSpeedWithNaturalDeceleration = 22
    NOUSE_2 = 23
    NOUSE_4 = 24
    NOUSE_7 = 25
    NOUSE_5 = 26
    TargetSpeed = 27
    LaneMoveSpeed = 28
    TemptationPer = 29
    PushPer = 30
    Accel = 31
    AllStatus = 32
    NOUSE_10 = 33
    NOUSE_20 = 34
    TargetLane = 35
    ActivateRandomNormalAndRareSkill = 36
    ActivateRandomRareSkill = 37
    NOUSE_17 = 38
    NOUSE_18 = 39
    ChallengeMatchBonus_Old = 501
    ChallengeMatchBonusStatus = 502
    ChallengeMatchBonusMotivation = 503

class SupportCardEffectType(Enum):
    NONE = 0
    SpecialTagEffectUp = 1
    MotivationUp = 2
    TrainningSpeedUp = 3
    TrainningStaminaUp = 4
    TrainningPowerUp = 5
    TrainningGutsUp = 6
    TrainningWizUp = 7
    TrainningEffectUp = 8
    InitialSpeedUp = 9
    InitalStaminaUp = 10
    InitialPowerUp = 11
    InitialGutsUp = 12
    InitialWizUp = 13
    InitalEvaluationUp = 14
    RaceStatusUp = 15
    RaceFanUp = 16
    SkillTipsLvUp = 17
    SkillTipsEventRateUp = 18
    GoodTrainingRateUp = 19
    SpeedLimitUp = 20
    StaminaLimitUp = 21
    PowerLimitUp = 22
    GutzLimitUp = 23
    WizLimitUp = 24
    EventRecoveryAmountUp = 25
    EventEffetcUp = 26
    TrainningFailureRateDown = 27
    TrainningHPConsumptionDown = 28
    MinigameEffectUP = 29
    SkillPointBonus = 30
    WizRecoverUp = 31 

class SupportCardRarity(Enum):
    R = 1
    SR = 2
    SSR = 3

class SupportCardType(Enum):
    Speed = 1
    Stamina = 2
    Power = 3
    Guts = 4
    Wiz = 5
    Friend = 6
    Team = 7

@dataclass
class SkillEffect:
    type: int = 0
    value_type: int = 0
    additional_active_type: int = 0
    ability_value_level_usage: int = 0
    value: int = 0
    target_type: int = 0
    target_value: int = 0


@dataclass
class SkillData:
    precondition: str = None
    condition: str = None
    duration: int = 0
    duration_usage: int = 0
    cooldown: int = 0
    effectList: List[SkillEffect] = None


@dataclass
class Skill:
    id: int
    name: str
    description: str
    icon_id: int
    dataList: List[SkillData]


@dataclass
class CharacterCard:
    id: int
    name: str
    bg_id: int
    talent_info: Talent
    proper_set: dict[int,Proper] = field(default_factory=dict)
    status_set: dict[int,Status] = field(default_factory=dict)
    available_skill_set: dict[int,List[int]] = None
    rairty_skill_set: dict[int,List[int]] = field(default_factory=dict)


@dataclass
class SupportCard:
    id: int
    name: str
    rarity:SupportCardRarity
    type:SupportCardType
    event_skill_list:list[int] = None
    train_skill_list:list[int] = None
    unique_effect:UniqueEffect = None
    effect_table_set:dict[SupportCardEffectType, EffectTable] = None
