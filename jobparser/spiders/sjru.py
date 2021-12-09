import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://russia.superjob.ru/vakansii/sistemnyj-administrator.html']


    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@rel='next']/@href").get()
        if next_page:
            # next_page = 'https://superjob.ru/' + next_page
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//div[@class='f-test-search-result-item']//a[contains(@class, 'icMQ_ _6AfZ9')]/@href").getall()
        for link in links:
            # link = 'https://superjob.ru/' + link
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.xpath("//h1/text()").get()
        salary = response.xpath("//div[@class='_3MVeX']//span[contains(@class, '_2Wp8I')]//text()").getall()
        url = response.url

        yield JobparserItem(name=name, salary=salary, url=url)
