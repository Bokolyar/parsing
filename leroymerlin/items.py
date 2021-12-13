# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose

def process_price(value):
    try:
        value = int(value.replace(' ', ''))
    except Exception as e:
        print(e)
    finally:
        return value

def process_photos(value):
    a = value.split('/f_auto')
    b = a[1].split('d_photoiscoming.png')
    c = a[0] + b[1]
    return c


class LeroymerlinItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(process_price))
    url = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field(input_processor=MapCompose(process_photos))
    id = scrapy.Field(output_processor=TakeFirst())
    specs = scrapy.Field()

