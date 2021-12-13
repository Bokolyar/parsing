import scrapy
from scrapy.http import HtmlResponse
from leroymerlin.items import LeroymerlinItem
from scrapy.loader import ItemLoader


class LmerlinSpider(scrapy.Spider):
    name = 'lmerlin'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self):
        super().__init__()
        self.start_urls = ['https://leroymerlin.ru/offer/novogodniy-dekor/']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//div[@view-type='primary']//a[@rel='next']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//a[@slot='name']")
        for link in links:
            yield response.follow(link, callback=self.parse_ads)

    def parse_ads(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroymerlinItem(), response=response)

        loader.add_xpath('name', "//h1/text()")  # "//img[@slot='thumbs-tail']"
        loader.add_xpath('photos', "//img[@slot='thumbs']/@src")
        loader.add_xpath('price', "//uc-pdp-price-view[@class='primary-price']/span[@slot='price']/text()")
        loader.add_value('url', response.url)
        loader.add_xpath('id', "//span[@slot='article']/@content")
        loader.add_xpath('specs', "//section[@id='nav-characteristics']//div[@class='def-list__group']")
        yield loader.load_item()

