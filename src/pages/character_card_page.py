from src.pages.common_page import *


class CharacterCardDatabasePage(DatabasePage):

    def createPropertiesForPage(id, name, talent_speed, talent_stamina, talent_power, talent_guts, talent_wiz):
        return {
            "角色名称": Property(
                title=[RichText(text=Text(content=name))]
            ),
            "速度成长率": Property(
                number=talent_speed/100
            ),
            "耐力成长率": Property(
                number=talent_stamina/100
            ),
            "力量成长率": Property(
                number=talent_power/100
            ),
            "根性成长率": Property(
                number=talent_guts/100
            ),
            "智力成长率": Property(
                number=talent_wiz/100
            ),
            "id": Property(
                rich_text=[RichText(text=Text(content=id))]
            ),
        }

    def __init__(self) -> None:
        super().__init__()
        self._properties = {
            '角色名称': Property(title={}),
            '速度成长率': Property(number=PropertyNumber(format=NumberFormat.percent)),
            '耐力成长率': Property(number=PropertyNumber(format=NumberFormat.percent)),
            '力量成长率': Property(number=PropertyNumber(format=NumberFormat.percent)),
            '根性成长率': Property(number=PropertyNumber(format=NumberFormat.percent)),
            '智力成长率': Property(number=PropertyNumber(format=NumberFormat.percent)),
            'id': Property(rich_text={}),
        }

    def createDatabase(self, database_name, parent_page_id: str) -> Database:
        return createDatabase(CreateDatabaseRequest(
            parent=Parent(type=ParentType.PAGE, page_id=parent_page_id),
            title=[RichText(text=Text(content=database_name))],
            properties=self._properties
        ))
    
    def filterNewCard(self, card_list: list[CharacterCard], database_id: str) -> list[CharacterCard]:
        id_set = self.getIdSetInNotionDatabase(database_id)
        return list(filter(lambda card: card.id not in id_set, card_list))


_proper_color_mapping = {
    8: ColorType.yellow,
    7: ColorType.orange,
    6: ColorType.pink,
    5: ColorType.green,
    4: ColorType.purple,
    3: ColorType.blue,
    2: ColorType.gray,
    1: ColorType.default
}
_proper_alphabet_mapping = {
    8: 'S',
    7: 'A',
    6: 'B',
    5: 'C',
    4: 'D',
    3: 'E',
    2: 'F',
    1: 'G'
}


class CharacterCardDetailPage:

    def __init__(self, cover_mapping=None, icon_mapping=None, local_skill_info=None) -> None:
        self.failed_count = 0
        self.cover_mapping = cover_mapping
        self.icon_mapping = icon_mapping
        self.local_skill_info = local_skill_info

    def createPageInDatabase(self, database_id, card: CharacterCard, skill_page_mapping: StrMapping, missmatch: Callable[[str], str]):
        icon_file = None
        if self.icon_mapping is not None:
            icon_file = File(
                type=FileType.external,
                external=ExternalFile(url=self.icon_mapping.get(card.id))
            )
            if not icon_file.external.url:
                icon_file = None
                print(f"Icon for {card.name}:({card.id}) not found.")
        cover_file = None
        if self.cover_mapping is not None:
            cover_file = File(
                type=FileType.external,
                external=ExternalFile(url=self.cover_mapping.get(card.id))
            )
            if not cover_file.external.url:
                cover_file = None
                print(f"Cover for {card.name}:({card.id}) not found.")
        try:
            children_list = self._createPageDetail(
                card, skill_page_mapping, missmatch)
            createPage(CreatePageRequest(
                parent=Parent(type=ParentType.DATABASE,
                              database_id=database_id),
                properties=CharacterCardDatabasePage.createPropertiesForPage(
                    card.id, card.name, *card.talent_info),
                children=children_list,
                icon=icon_file,
                cover=cover_file,
            ))
        except Exception as e:
            traceback.print_exc()
            self.failed_count += 1

    def _createPageDetail(self, card: CharacterCard, skill_page_mapping: StrMapping, mismatch: Callable[[str], str]) -> List[Block]:
        block_list = []
        block_list.extend(self._createStatusTable(card))
        block_list.extend(self._createGroundProperTable(card))
        block_list.extend(self._createDistanceProperTable(card))
        block_list.extend(self._createRunningStyleProperTable(card))
        block_list.extend(self._createInstristicSkillInfo(
            card, skill_page_mapping, mismatch))
        block_list.extend(self._createUpgradeSkillInfo(
            card, skill_page_mapping, mismatch))
        block_list.extend(self._createSkillInfo(
            card, skill_page_mapping, mismatch))
        return block_list

    def _createStatusTable(self, card: CharacterCard) -> List[Block]:
        column_count = 6
        ret = []
        ret.append(Block(heading_2=Heading2(
            rich_text=[RichText(text=Text(content="基础状态"))])))
        if card.original_name:
            ret.append(Block(
                paragraph=Paragraph(rich_text=[
                    RichText(text=Text(content="原名："), annotations=Annotation(
                        bold=True, color=ColorType.purple)),
                    RichText(text=Text(content=card.original_name)),
                ])
            ))
        table_rows = []
        table_rows.append(Block(table_row=TableRow(cells=[
            [RichText(text=Text(content="Rank"))],
            [RichText(text=Text(content="速度"))],
            [RichText(text=Text(content="耐力"))],
            [RichText(text=Text(content="力量"))],
            [RichText(text=Text(content="根性"))],
            [RichText(text=Text(content="智力"))],
        ])))
        for rank, status in card.status_set.items():
            table_rows.append(Block(table_row=TableRow(cells=[
                [RichText(text=Text(content=f"Lv.{rank}"))],
                [RichText(text=Text(content=str(status.speed)))],
                [RichText(text=Text(content=str(status.stamina)))],
                [RichText(text=Text(content=str(status.power)))],
                [RichText(text=Text(content=str(status.guts)))],
                [RichText(text=Text(content=str(status.wiz)))],
            ])))
        ret.append(Block(table=Table(table_width=column_count,
                   has_column_header=True, has_row_header=True, children=table_rows)))
        ret.append(Block(divider={}))
        return ret

    def _createGroundProperTable(self, card: CharacterCard) -> List[Block]:
        ret = []
        ret.append(Block(heading_2=Heading2(
            rich_text=[RichText(text=Text(content="场地适性"))])))
        if card.proper_set:
            column_count = 2
            proper = list(card.proper_set.values())[0]
            table_rows = []
            table_rows.append(Block(table_row=TableRow(cells=[
                [RichText(text=Text(content="芝"))],
                [RichText(text=Text(content="ダート"))],
            ])))
            table_rows.append(Block(table_row=TableRow(cells=[
                [RichText(text=Text(content=_proper_alphabet_mapping[proper.turf]),
                          annotations=Annotation(color=_proper_color_mapping[proper.turf]))],
                [RichText(text=Text(content=_proper_alphabet_mapping[proper.dirt]),
                          annotations=Annotation(color=_proper_color_mapping[proper.dirt]))],
            ])))
            ret.append(Block(table=Table(table_width=column_count,
                                         has_column_header=True, has_row_header=False, children=table_rows)))
        ret.append(Block(divider={}))
        return ret

    def _createDistanceProperTable(self, card: CharacterCard) -> List[Block]:
        ret = []
        ret.append(Block(heading_2=Heading2(
            rich_text=[RichText(text=Text(content="距离适性"))])))
        if card.proper_set:
            column_count = 4
            proper = list(card.proper_set.values())[0]
            table_rows = []
            table_rows.append(Block(table_row=TableRow(cells=[
                [RichText(text=Text(content="短距離"))],
                [RichText(text=Text(content="マイル"))],
                [RichText(text=Text(content="中距離"))],
                [RichText(text=Text(content="長距離"))],
            ])))
            table_rows.append(Block(table_row=TableRow(cells=[
                [RichText(text=Text(content=_proper_alphabet_mapping[proper.short]),
                          annotations=Annotation(color=_proper_color_mapping[proper.short]))],
                [RichText(text=Text(content=_proper_alphabet_mapping[proper.mile]),
                          annotations=Annotation(color=_proper_color_mapping[proper.mile]))],
                [RichText(text=Text(content=_proper_alphabet_mapping[proper.middle]),
                          annotations=Annotation(color=_proper_color_mapping[proper.middle]))],
                [RichText(text=Text(content=_proper_alphabet_mapping[proper.long]),
                          annotations=Annotation(color=_proper_color_mapping[proper.long]))],
            ])))
            ret.append(Block(table=Table(table_width=column_count,
                                         has_column_header=True, has_row_header=False, children=table_rows)))
        ret.append(Block(divider={}))
        return ret

    def _createRunningStyleProperTable(self, card: CharacterCard) -> List[Block]:
        ret = []
        ret.append(Block(heading_2=Heading2(
            rich_text=[RichText(text=Text(content="跑法适性"))])))
        if card.proper_set:
            column_count = 4
            proper = list(card.proper_set.values())[0]
            table_rows = []
            table_rows.append(Block(table_row=TableRow(cells=[
                [RichText(text=Text(content="逃げ"))],
                [RichText(text=Text(content="先行"))],
                [RichText(text=Text(content="差し"))],
                [RichText(text=Text(content="追込"))],
            ])))
            table_rows.append(Block(table_row=TableRow(cells=[
                [RichText(text=Text(content=_proper_alphabet_mapping[proper.nige]),
                          annotations=Annotation(color=_proper_color_mapping[proper.nige]))],
                [RichText(text=Text(content=_proper_alphabet_mapping[proper.senko]),
                          annotations=Annotation(color=_proper_color_mapping[proper.senko]))],
                [RichText(text=Text(content=_proper_alphabet_mapping[proper.sashi]),
                          annotations=Annotation(color=_proper_color_mapping[proper.sashi]))],
                [RichText(text=Text(content=_proper_alphabet_mapping[proper.oikomi]),
                          annotations=Annotation(color=_proper_color_mapping[proper.oikomi]))],
            ])))
            ret.append(Block(table=Table(table_width=column_count,
                                         has_column_header=True, has_row_header=False, children=table_rows)))
        ret.append(Block(divider={}))
        return ret

    def _getSkillPageId(self, skill_id: int, skill_page_mapping: StrMapping, mismatch: Callable[[str], str]) -> str:
        if skill_id in skill_page_mapping:
            return skill_page_mapping[skill_id]
        return mismatch(skill_id)

    def _createInstristicSkillInfo(self, card: CharacterCard, skill_page_mapping: StrMapping, mismatch: Callable[[str], str]) -> List[Block]:
        ret = []
        ret.append(Block(heading_2=Heading2(
            rich_text=[RichText(text=Text("固有技能"))])))
        if not card.rairty_skill_set:
            ret.append(Block(divider={}))
            return ret
        skill_id = list(card.rairty_skill_set.values())[0][0]
        page_id = self._getSkillPageId(skill_id, skill_page_mapping, mismatch)
        if page_id == None:
            if skill_id in self.local_skill_info:
                print(f"Skill {skill_id} not found from cloud, using local skill info")
                skill = self.local_skill_info[skill_id]
                ret.append(Block(paragraph=Paragraph(
                    rich_text=[RichText(text=Text(skill.name))])))
            else:
                print(f"Skill {skill_id} not found ,neither local and cloud ")
        else:
            ret.append(Block(paragraph=Paragraph(rich_text=[RichText(
                type=RichTextType.mention, mention=Mention(type=MentionType.page, page=MentionPage(id=page_id)))])))
        ret.append(Block(divider={}))
        return ret

    def _createUpgradeSkillInfo(self, card: CharacterCard, skill_page_mapping: StrMapping, mismatch: Callable[[str], str]) -> List[Block]:
        ret = []
        ret.append(Block(heading_2=Heading2(
            rich_text=[RichText(text=Text("进化技能"))])))
        if not card.upgrade_skill_set:
            ret.append(Block(divider={}))
            return ret
        skill_list = []
        for skill_id_array in card.upgrade_skill_set.values():
            for skill_id in skill_id_array:
                page_id = self._getSkillPageId(
                    skill_id, skill_page_mapping, mismatch)
                if page_id == None:
                    if skill_id in self.local_skill_info:
                        print(f"Skill {skill_id} not found from cloud, using local sill info")
                        skill = self.local_skill_info[skill_id]
                        skill_list.append(
                            RichText(text=Text(content=skill.name)))
                    else:
                        print(f"Skill {skill_id} not found ,neither local and cloud")
                else:
                    skill_list.append(RichText(type=RichTextType.mention, mention=Mention(
                        type=MentionType.page, page=MentionPage(id=page_id))))
                skill_list.append(RichText(text=Text(content="  ")))
        ret.append(Block(paragraph=Paragraph(rich_text=skill_list)))
        ret.append(Block(divider={}))
        return ret

    def _createSkillInfo(self, card: CharacterCard, skill_page_mapping: StrMapping, mismatch: Callable[[str], str]) -> List[Block]:
        ret = []
        ret.append(Block(heading_2=Heading2(
            rich_text=[RichText(text=Text("技能"))])))
        if not card.available_skill_set:
            ret.append(Block(divider={}))
            return ret
        skill_list = []
        for skill_id_array in card.available_skill_set.values():
            for skill_id in skill_id_array:
                page_id = self._getSkillPageId(
                    skill_id, skill_page_mapping, mismatch)
                if page_id == None:
                    if skill_id in self.local_skill_info:
                        print(f"Skill {skill_id} not found from cloud, using local sill info")
                        skill = self.local_skill_info[skill_id]
                        skill_list.append(
                            RichText(text=Text(content=skill.name)))
                    else:
                        print(f"Skill {skill_id} not found ,neither local and cloud")
                else:
                    skill_list.append(RichText(type=RichTextType.mention, mention=Mention(
                        type=MentionType.page, page=MentionPage(id=page_id))))
                skill_list.append(RichText(text=Text(content="  ")))
        ret.append(Block(paragraph=Paragraph(rich_text=skill_list)))
        return ret
