from src.model import *
from src.notion import *


def _createTitleProperty(text: str) -> Property:
    return Property(
        title=[RichText(text=Text(content=text))]
    )


def _createRichTextProperty(text: str) -> Property:
    return Property(
        rich_text=[RichText(text=Text(content=text))]
    )


def _createNumberProperty(number: int) -> Property:
    return Property(
        number=number
    )


class SkillDatabasePage:

    def createPropertiesForPage(skill_id, skill_name, skill_description, skill_condition, skill_duration, skill_cooldown, skill_type, skill_value):
        return {
            "技能名称": _createTitleProperty(skill_name),
            "技能描述": _createRichTextProperty(skill_description),
            "技能条件": _createRichTextProperty(skill_condition),
            "技能类型": _createRichTextProperty(skill_type),
            "技能数值": _createRichTextProperty(skill_value),
            "技能持续时间": _createNumberProperty(skill_duration),
            "技能冷却时间": _createNumberProperty(skill_cooldown),
            "id": _createNumberProperty(skill_id),
        }

    def __init__(self) -> None:
        self._properties = {
            '技能名称': Property(title={}),
            '技能描述': Property(rich_text={}),
            '技能条件': Property(rich_text={}),
            '技能持续时间': Property(number=PropertyNumber(format=NumberFormat.number)),
            '技能冷却时间': Property(number=PropertyNumber(format=NumberFormat.number)),
            '技能类型': Property(rich_text={}),
            '技能数值': Property(rich_text={}),
            'id': Property(number=PropertyNumber(format=NumberFormat.number)),
        }

    def createDatabase(self, database_name, parent_page_id: str) -> Database:
        return createDatabase(self._generateCreateDatabaseRequest(database_name, parent_page_id))
    
    def filterNewSkill(self, skill_list: list[Skill], database_id: str) -> list[Skill]:
        id_set = self._getallSkillIdInDatabase(database_id)
        return list(filter(lambda skill: int(skill.id) not in id_set, skill_list))
    
    def _getallSkillIdInDatabase(self, database_id: str) -> set[int]:
        id_set = set()
        start_cursor = None
        while True:
            notion_list  = queryDatabase(database_id,start_cursor=start_cursor, page_size=100)
            if not notion_list:
                break
            if not notion_list.has_more:
                break
            start_cursor = notion_list.next_cursor
            for page in notion_list.results:
                id_set.add(int(page['properties']['id']['number']))
        return id_set

    def _generateCreateDatabaseRequest(self, database_name, parent_page_id: str) -> CreateDatabaseRequest:
        return CreateDatabaseRequest(
            parent=Parent(type=ParentType.PAGE, page_id=parent_page_id),
            title=[RichText(text=Text(content=database_name))],
            properties=self._properties
        )


class SkillDetailPage:

    def __init__(self, skill_icon_mapping=None) -> None:
        self.failed_count = 0
        self.skill_icon_mapping = skill_icon_mapping

    def createPageInDatabase(self, database_id, skill: Skill) -> None:
        skill_name = skill.name
        skill_description = skill.description
        if skill.dataList:
            skill_condition = skill.dataList[0].condition
            skill_duration = skill.dataList[0].duration/10000
            skill_cooldown = skill.dataList[0].cooldown/10000
            _skill_type = skill.dataList[0].effectList[0].type
            skill_type = self._skillEffectTypeFormat(_skill_type)
            _value = skill.dataList[0].effectList[0].value
            skill_value = self._skillEffectValueFormat(_skill_type, _value)
        else:
            skill_condition = "None"
            skill_duration = -1
            skill_cooldown = -1
            skill_type = "None"
            skill_value = "None"
        icon_file = None
        if self.skill_icon_mapping:
            icon_url = self.skill_icon_mapping.get(str(skill.icon_id))
            if icon_url:
                icon_file = File(
                    type='external', external=ExternalFile(url=icon_url))
        children_list = self._createPageDetail(skill)
        try:
            createPage(CreatePageRequest(
                parent=Parent(type=ParentType.DATABASE,
                              database_id=database_id),
                properties=SkillDatabasePage
                .createPropertiesForPage(skill.id, skill_name, skill_description,
                                         skill_condition, skill_duration, skill_cooldown,
                                         skill_type, skill_value),
                children=children_list,
                icon=icon_file
            ))
        except Exception as e:
            print(e)
            self.failed_count += 1

    def _skillDurationFormat(self, time: int) -> str:
        if time < 0:
            return "None"
        else:
            return f"{time/10000} s"

    def _skillEffectTypeFormat(self, skill_type: int) -> str:
        return SkillType(skill_type).name

    def _skillEffectValueFormat(self, skill_type: int, value: int) -> str:
        _skill_type = SkillType(skill_type)
        if _skill_type in (SkillType.Speed, SkillType.Stamina, SkillType.Power, SkillType.Guts, SkillType.Wiz):
            return str(value)
        elif _skill_type in (SkillType.CurrentSpeed, SkillType.CurrentSpeedWithNaturalDeceleration, SkillType.TargetSpeed):
            return f"{value/10000} m/s"
        elif _skill_type in (SkillType.Accel,):
            return f"{value/10000} m/s^2"
        elif _skill_type in (SkillType.HpDecRate, SkillType.HpRate):
            return f"{value/100} %"
        else:
            return str(value)

    def _createPageDetail(self, skill: Skill) -> Iterable[Block]:
        result = []
        result.append(Block(
            heading_2=Heading2(rich_text=[RichText(text=Text(content="基本信息"))])
        ))
        result.append(Block(
            paragraph=Paragraph(rich_text=[
                RichText(text=Text(content="技能名称："), annotations=Annotation(
                    bold=True, color=ColorType.purple)),
                RichText(text=Text(content=skill.name)),
            ])
        ))
        result.append(Block(
            paragraph=Paragraph(rich_text=[
                RichText(text=Text(content="技能描述："), annotations=Annotation(
                    bold=True, color=ColorType.purple)),
                RichText(text=Text(content=skill.description)),
            ])
        ))
        result.append(Block(
            heading_2=Heading2(rich_text=[RichText(text=Text(content="发动条件"))])
        ))
        result.append(Block(
            paragraph=Paragraph(rich_text=[
                RichText(text=Text(content="前置条件："), annotations=Annotation(
                    bold=True, color=ColorType.purple)),
                RichText(text=Text(content=skill.dataList[0].precondition)),
            ])
        ))
        result.append(Block(
            paragraph=Paragraph(rich_text=[
                RichText(text=Text(content="发动条件："), annotations=Annotation(
                    bold=True, color=ColorType.purple)),
                RichText(text=Text(content=skill.dataList[0].condition)),
            ])
        ))
        result.append(Block(
            heading_3=Heading3(rich_text=[RichText(text=Text(content="效果信息"))])
        ))
        for effect in skill.dataList[0].effectList:
            result.append(Block(
                paragraph=Paragraph(rich_text=[
                    RichText(text=Text(content=self._skillEffectTypeFormat(effect.type) + "："), annotations=Annotation(
                        bold=True, color=ColorType.purple)),
                    RichText(text=Text(content=self._skillEffectValueFormat(
                        effect.type, effect.value))),
                ])
            ))
        result.append(Block(
            paragraph=Paragraph(rich_text=[
                RichText(text=Text(content="持续时间："), annotations=Annotation(
                    bold=True, color=ColorType.purple)),
                RichText(text=Text(content=self._skillDurationFormat(
                    skill.dataList[0].duration))),
            ])))
        result.append(Block(
            paragraph=Paragraph(rich_text=[
                RichText(text=Text(content="冷却时间："), annotations=Annotation(
                    bold=True, color=ColorType.purple)),
                RichText(text=Text(content=self._skillDurationFormat(
                    skill.dataList[0].cooldown))),
            ])))
        if len(skill.dataList) > 1:
            result.append(Block(
                heading_2=Heading2(
                    rich_text=[RichText(text=Text(content="发动条件2"))])
            ))
            result.append(Block(
                paragraph=Paragraph(rich_text=[
                    RichText(text=Text(content="前置条件："), annotations=Annotation(
                        bold=True, color=ColorType.purple)),
                    RichText(
                        text=Text(content=skill.dataList[0].precondition)),
                ])
            ))
            result.append(Block(
                paragraph=Paragraph(rich_text=[
                    RichText(text=Text(content="发动条件："), annotations=Annotation(
                        bold=True, color=ColorType.purple)),
                    RichText(text=Text(content=skill.dataList[0].condition)),
                ])
            ))
            result.append(Block(
                heading_3=Heading3(
                    rich_text=[RichText(text=Text(content="效果信息"))])
            ))
            for effect in skill.dataList[0].effectList:
                result.append(Block(
                    paragraph=Paragraph(rich_text=[
                        RichText(text=Text(content=self._skillEffectTypeFormat(effect.type) + "：", annotations=Annotation(
                            bold=True, color=ColorType.purple))),
                        RichText(text=Text(content=self._skillEffectValueFormat(
                            effect.type, effect.value))),
                    ])
                ))
            result.append(Block(
                paragraph=Paragraph(rich_text=[
                    RichText(text=Text(content="持续时间："), annotations=Annotation(
                        bold=True, color=ColorType.purple)),
                    RichText(text=Text(content=self._skillDurationFormat(
                        skill.dataList[0].duration))),
                ])))
            result.append(Block(
                paragraph=Paragraph(rich_text=[
                    RichText(text=Text(content="冷却时间："), annotations=Annotation(
                        bold=True, color=ColorType.purple)),
                    RichText(text=Text(content=self._skillDurationFormat(
                        skill.dataList[0].cooldown))),
                ])))
        result.append(Block(
            heading_2=Heading2(rich_text=[RichText(text=Text(content="其他信息"))])
        ))
        return result