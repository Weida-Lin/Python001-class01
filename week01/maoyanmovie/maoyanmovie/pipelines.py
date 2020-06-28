# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pandas as pd 

class MaoyanmoviePipeline:
    def process_item(self, item, spider):
		title = item['title']
		genre = item['genre']
		date = item['date']
		movie_data = {'title' : title, 'genre' : genre, 'date'  : date}
		movies = pd.DataFrame(data = movie_data)
		movies.to_csv('movies2.csv', encoding='utf8')

		return item
	
