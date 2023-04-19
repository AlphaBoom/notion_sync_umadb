import scrapy
from gamewith.items import SupportCard, SkillBrief


class SupportCardSpider(scrapy.Spider):
    name = 'support_card'
    
    def start_requests(self):
        yield scrapy.Request(
            url="https://gamewith.jp/uma-musume/article/show/255035",
            callback=self.support_card_list_parse,
        )

    def support_card_list_parse(self, response):
        items = response.xpath('//*[@id="article-body"]/div[3]/div/table/tr/td[1]/a')
        self.logger.info("拉取到的支援卡数量: %d", len(items))
        urls = [
            (item.xpath("text()").get(), item.xpath("@href").get()) for item in items
        ]
        for name, url in urls:
            yield scrapy.Request(
                url=url, callback=self.support_card_parse, cb_kwargs={"name": name}
            )

    def support_card_parse(self, response, name):
        performance = response.xpath('//*[@id="article-body"]/table[1]')
        rare = performance.xpath("tr[1]/td/span/a/text()").get()
        card_type = performance.xpath("tr[2]/td/span/a/text()").get()
        nick_name = performance.xpath("tr[3]/td/text()").get()
        event_skill_list = response.xpath(
            '//h3[.="育成イベント"]/following-sibling::node()[1]/table/tr'
        )
        event_skill = []
        for event_skill_item in event_skill_list:
            skill_breif = SkillBrief(
                name=event_skill_item.xpath("td[1]/a/text()").get(),
                description=event_skill_item.xpath("td[1]/text()").get(),
            )
            event_skill.append(skill_breif)
        train_skill_list = response.xpath(
            '//h3[.="所持スキル"]/following-sibling::node()[1]/table/tr'
        )
        train_skill = []
        for train_skill_item in train_skill_list:
            skill_breif = SkillBrief(
                name=train_skill_item.xpath("td[1]/a/text()").get(),
                description=train_skill_item.xpath("td[1]/text()").get(),
            )
            train_skill.append(skill_breif)
        return SupportCard(
            name=name,
            nick_name=nick_name,
            rare=rare,
            card_type=card_type,
            event_skill=event_skill,
            train_skill=train_skill,
        )
