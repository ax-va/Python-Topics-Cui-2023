import re

from typing import Any, Dict
import scrapy
from scrapy import Selector, Request
from scrapy.http.response import Response

WIKIPEDIA_DOMAIN = "en.wikipedia.org"
BASE_URL = "https://" + WIKIPEDIA_DOMAIN
NOBEL_WINNERS_BY_COUNTRY_URL = BASE_URL + "/wiki/List_of_Nobel_laureates_by_country"


class NobelWinnerItem(scrapy.Item):
    """
    Contains the fields for the scraped data.

    Installed Pillow is required.
    """
    name = scrapy.Field()
    link = scrapy.Field()
    image_urls = scrapy.Field()
    image_paths = scrapy.Field()
    images = scrapy.Field()  # full information about images


class NobelWinnersSpiderForPhotos(scrapy.Spider):
    """
    Scrapes the Nobel-winners data.

    Installed Pillow is required.
    """
    name = 'Nobel_winners_with_photos'
    allowed_domains = [WIKIPEDIA_DOMAIN]
    start_urls = [NOBEL_WINNERS_BY_COUNTRY_URL]
    custom_settings = {
        'ITEM_PIPELINES': {
            'nobel_winners.pipelines.NobelPhotosPipeline': 300,
        },
        'IMAGES_STORE': '/home/delorian/PycharmProjects/Python-Topics-Cui-2023/topics/scrapy-projects/nobel_winners/images',
    }

    def parse(self, response: Response, **kwargs: Any) -> Request:
        country_item_list = response.xpath('//ol[1]/../h3')
        for country_item in country_item_list:
            winner_item_list = country_item.xpath('following-sibling::ol[1]/li')
            for winner_item in winner_item_list:
                text = ' '.join(winner_item.xpath('descendant-or-self::text()').extract())
                winner_data = {
                    'name': text.split(',')[0].replace('*', '').strip(),
                    'link': BASE_URL + winner_item.xpath('a/@href').extract()[0],
                }
                request = scrapy.Request(  # Make a request to the winner’s biography page
                    winner_data['link'],
                    callback=self.parse_biographical_page,  # Set the callback function to handle the response
                    dont_filter=True
                )
                request.meta['item'] = NobelWinnerItem(**winner_data)
                yield request

    def parse_biographical_page(self, response: Response) -> Request:
        """
        Handles the callback from the biography-link request.
        """
        item = response.meta['item']
        img_src_list = response.xpath('//table[contains(@class,"infobox")]//img/@src')
        if img_src_list:
            item['image_urls'] = ['https:' + img_src_list[0].extract()]
        yield item

