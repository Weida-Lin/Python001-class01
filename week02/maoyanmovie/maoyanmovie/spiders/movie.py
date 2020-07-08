import scrapy
import time
from scrapy.selector import Selector
from maoyanmovie.items import MaoyanmovieItem


class MovieSpider(scrapy.Spider):
    name = 'movie'
    allowed_domains = ['maoyan.com']
    start_urls = ['https://maoyan.com/films?showType=3']
    custom_settings = {
    	'ITEM_PIPELINES': {
   	    'maoyanmovie.pipelines.MaoyanmoviePipeline': 300,
    	}
    }

    def parse(self, response):
        movies = Selector(response=response).xpath(
            '//div[@class="channel-detail movie-item-title"]')
        for movie in movies:
            item = MaoyanmovieItem()
            title = movie.xpath('./a/text()')
            linkpart = movie.xpath('./a/@href')
            item['title'] = title.extract_first().strip()
            item['link'] = 'https://maoyan.com' + \
                linkpart.extract_first().strip()
            # print(item['title'])
            # print(item['link'])
            yield scrapy.Request(url=item['link'], meta={'item': item}, callback=self.parsedetail)

    def parsedetail(self, response):
        item = response.meta['item']
        detail = Selector(response=response).xpath(
            '//div[@class="movie-brief-container"]/ul/li')
        item['genre'] = detail[0].xpath('./a/text()').extract()
        dateandplace = detail[2].xpath('./text()').extract_first()
        try:
            item['date'] = dateandplace[0:10]
        except TypeError:
            item['date'] = None
        '''
        print(item['title'])
        print(item['genre'])
        print(item['date'])
        '''
        time.sleep(2)
        yield item
