from dataclasses import dataclass
from typing import List
from enum import Enum

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
    CurrentSpeed = 21
    CurrentSpeedWithNaturalDeceleration = 22
    TargetSpeed = 27
    LaneMoveSpeed = 28
    TemptationPer = 29
    PushPer = 30
    Accel = 31
    TargetLane = 35
    ActivateRandomNormalAndRareSkill = 36
    ActivateRandomRareSkill = 37


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
