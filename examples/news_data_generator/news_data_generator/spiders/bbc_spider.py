# -*- coding: utf-8 -*-
"""
   Description :   BBS news crawl
   Author :        xxm
"""
import scrapy
from scrapy.spiders import CrawlSpider
from time import time
from scrapy.loader import ItemLoader
from ..items import BBCItem


class BbcSpider(CrawlSpider):
    name = 'bbc'
    allowed_domains = ['bbc.com']
    start_urls = ['http://www.bbc.com/news/']

    host = 'http://www.bbc.com'
    base_url = start_urls[0]

    crawled_at = int(round(time() * 1000))
    source = 'bbc'

    url_tags = {
        'world/asia/china': 'china',
        'world': 'politics',
        'world/asia': 'asia',
        'world/africa': 'politics',
        'business': 'business',
        'technology': 'tech',
        'science_and_environment': 'tech',
        'entertainment_and_arts': 'entertainment',
        'health': 'health',
        # 'special_reports': 'special',
    }

    def start_requests(self):
        # print(self.settings.attribute.keys())
        # regex = r'world|business|technology|health|science|special'

        for url, tag in self.url_tags.items():
            yield scrapy.Request(self.base_url + url, callback=self.parse_list, meta={'tag': tag})

    def parse_list(self, res):
        tag = res.meta['tag']

        urls = res.xpath('.//a/@href').re(r'/news/.*\d+$')

        if urls is not None:
            for url in urls:
                yield scrapy.Request(url=self.host + url, callback=self.parse_art, meta={'tag': tag})

    def parse_art(self, res):
        page_url = res.url

        # print('pageurl',page_url)
        story_sel = res.xpath('.//div[@class="story-body"]')[0]
        tag = res.meta['tag']
        b = ItemLoader(item=BBCItem(), selector=story_sel)

        b.add_xpath('title', './/h1[@class="story-body__h1"]/text()')
        b.add_xpath(
            'timestamp', './/li[@class="mini-info-list__item"]/div[@data-seconds]/@data-seconds')

        img_urls = story_sel.xpath(
            './/span/img[@class="js-image-replace"]/@src').extract()
        if len(img_urls) == 0:
            img_urls = story_sel.xpath('.//figure/div[@class="player-with-placeholder"]/img/@src').extract_first()
        # b.add_xpath(
        #     'image_urls', './/span/img[@class="js-image-replace"]/@src')
        b.add_value('image_urls', img_urls)

        b.add_xpath(
            'summary', './/p[@class="story-body__introduction"]/text()')

        b.add_xpath('text', './/div[@property="articleBody"]/p/text()')

        b.add_value('url', page_url)
        b.add_value('crawled_at', self.crawled_at)
        b.add_value('source', self.source)

        b.add_value('tag', tag)
        return b.load_item()
