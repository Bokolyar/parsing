# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os

import scrapy
# from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from lxml import html


class LeroymerlinPipeline:
    def process_item(self, item, spider):
        item['specs'] = self.process_specs(item['specs'])
        return item

    def process_specs(self, specs):
        specs_dict = {}
        for item in specs:
            dom = html.fromstring(item)
            key = dom.xpath("//dt[@class='def-list__term']/text()")[0]
            value = dom.xpath("//dd[@class='def-list__definition']/text()")[0].strip()
            specs_dict[key] = value
        return specs_dict


class LeroymerlinPhotos(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        path = f"./photos/full/{item['id']}"
        itemphotos = []
        for itm in results:
            if itm[0]:
                if not os.path.isdir(path):
                    os.mkdir(path)
                old_path = itm[1]['path']
                new_path = path + '/' + old_path.split('/')[1]
                os.replace('./photos/' + old_path, new_path)
                itm[1]['path'] = new_path[9:]
                itemphotos.append(itm[1])
        item['photos'] = itemphotos
        return item
