学习笔记


爬虫流程
1.requests：获取网页内容
	import requests

	user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
	
	#尽可能模拟用户浏览器
	header = {'user-agent':user_agent}

	myurl = 'https://movie.douban.com/top250'

	#向服务器请求或查询一些资源并得到从服务器返回的响应
	response = requests.get(myurl,headers=header)

	#网页源代码
	print(response.text)
	#网页的状态码
	print(f'返回码是: {response.status_code}')
	'''
	HTTP 状态码（响应代码）
	1XX		信息响应
	2XX		成功响应
	3XX		重定向
	4XX		客户端响应
	5XX		服务段响应
	'''
	
2.BeautifulSoup：解析网页，提取网页特定内容
	from bs4 import BeautifulSoup as bs

	bs_info = bs(response.text, 'html.parser')

	# Python 中使用 for in 形式的循环,Python使用缩进来做语句块分隔
	for tags in bs_info.find_all('div', attrs={'class': 'hd'}):
		for atag in tags.find_all('a'):
			print(atag.get('href'))
			# 获取所有链接
			print(atag.find('span').text)
			# 获取电影名字


3.lxml.etree: 也是解析网页，提取网页特定内容，效率比BeautifulSoup高
	import lxml.etree
	
	# xml化处理
	selector = lxml.etree.HTML(response.text)

	# 电影名称
	film_name = selector.xpath('//*[@id="content"]/h1/span[1]/text()')#提取标签里面的内容
	print(f'电影名称: {film_name}')

	
4.pandas: 把信息进行保存
	import pandas as pd

	movie1 = pd.DataFrame(data = mylist)#传入一个字典参数

	# windows需要使用gbk字符集
	movie1.to_csv('./movie1.csv', encoding='utf8', index=False, header=False)
	

爬虫框架：Scrapy
	核心组件
	Engine（引擎）：“大脑”，指挥其他组件协同工作
	Scheduler（调度器）：接收引擎发过来的请求，按照先后顺序，压入队列中，同时去除重复的请求
	Downloader（下载器）：用于下载网页内容，并返回给爬虫
	Spiders（爬虫）：用于从特定网页提取需要的信息，及所谓的实体（Item）。用户也可以从中提取出链接，让Scrapy继续抓取下个页面
	Item Pipelines(项目管道)：负责处理爬虫从网页抽出的实体。主要功能是持久化实体、验证实体的有效性、清除不需要的信息等
	Downloader Middlewares（下载器中间件）
	Spider Middlewares（爬虫中间件）
	
	Spiders组件可包含多个spider,一个spider对于一个域名
	1）运行爬虫时需指定域名，Engine根据域名找到相应的spider，
	2）Spiders组件会向Scheduler发起一个请求，
	3）Scheduler自动去重，之后根据请求的先后顺序将请求发给Engine,
	4）Engine再找到Downloader,Downloader向Internet发起请求并接收请求的返回信息，
	5）返回信息又回到Engine，（Engine与Downloader之间有下载器中间件，在发起下载和下载结束后做中间处理）
	6）Engine又会把返回信息交给Spiders，（Engine与Spiders之间有爬虫中间件）
	7）这时Spiders可以通过Item Pipeline将数据保存或者再次将要请求的页面传给Engine,Engine在传给Scheduler,重复刚才的步骤。
	
	一般只需编写Spiders和Item Pipelines。
	
	#安装scrapy
	pip install scrapy
	#创建项目目录
	scrapy startproject projectname
	#进入项目目录
	cd projectname
	#生成spider(爬虫逻辑)
	scrapy genspider spidername domainname
	#运行spider
	scrapy crawl spidername
	
	
	spider实例：
	# -*- coding: utf-8 -*-
	import scrapy
	from bs4 import BeautifulSoup
	from doubanmovie.items import DoubanmovieItem


	class DoubanSpider(scrapy.Spider):
		# 定义爬虫名称
		name = 'douban'
		allowed_domains = ['movie.douban.com']
		# 起始URL列表
		start_urls = ['https://movie.douban.com/top250']

		#   注释默认的parse函数
		#   def parse(self, response):
		#        pass


		# 爬虫启动时，引擎自动调用该方法，并且只会被调用一次，用于生成初始的请求对象（Request）。
		# start_requests()方法读取start_urls列表中的URL并生成Request对象，发送给引擎。
		# 引擎再指挥其他组件向网站服务器发送请求，下载网页
		def start_requests(self):
			for i in range(0, 10):
				url = f'https://movie.douban.com/top250?start={i*25}'
				yield scrapy.Request(url=url, callback=self.parse)
				# url 请求访问的网址
				# callback 回调函数，引擎回将下载好的页面(Response对象)发给该方法，执行数据解析
				# 这里可以使用callback指定新的函数，不是用parse作为默认的回调参数

		# 解析函数
		def parse(self, response):
			soup = BeautifulSoup(response.text, 'html.parser')
			title_list = soup.find_all('div', attrs={'class': 'hd'})
			#for i in range(len(title_list)):
			# 在Python中应该这样写
			for i in title_list:
				# 在items.py定义
				item = DoubanmovieItem()
				title = i.find('a').find('span').text
				link = i.find('a').get('href')
				item['title'] = title
				item['link'] = link
				yield scrapy.Request(url=link, meta={'item': item}, callback=self.parse2)

		# 解析具体页面
		def parse2(self, response):
			item = response.meta['item']
			soup = BeautifulSoup(response.text, 'html.parser')
			content = soup.find('div', attrs={'class': 'related-info'}).get_text().strip()
			item['content'] = content
			#将item传给pipeline
			yield item
			
		
	items.py实例：
	import scrapy
	
	class DoubanmovieItem(scrapy.Item):
		# define the fields for your item here like:
		# name = scrapy.Field()

		# 注释原有的pass
		# pass
		title = scrapy.Field()
		link = scrapy.Field()
	
	
	pipelins.py实例：
	# -*- coding: utf-8 -*-

	# Define your item pipelines here
	#
	# Don't forget to add your pipeline to the ITEM_PIPELINES setting
	# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


	# 注册到settings.py文件的ITEM_PIPELINES中，激活组件
	class DoubanmoviePipeline:
	#    def process_item(self, item, spider):
	#        return item

    # 每一个item管道组件都会调用该方法，并且必须返回一个item对象实例或raise DropItem异常
    def process_item(self, item, spider):
        title = item['title']
        link = item['link']
        content = item['content']
        output = f'|{title}|\t|{link}|\t|{content}|\n\n'
        with open('./doubanmovie.txt', 'a+', encoding='utf-8') as article:
            article.write(output)
        #一定要return item
		return item
	
	
	利用Scrapy Xpath代替BeautifulSoup实例（效率比BeautifulSoup高）：
	# -*- coding: utf-8 -*-
	import scrapy
	from doubanmovie.items import DoubanmovieItem
	# from bs4 import BeautifulSoup
	from scrapy.selector import Selector


	class DoubanSpider(scrapy.Spider):
		# 定义爬虫名称
		name = 'douban'
		allowed_domains = ['movie.douban.com']
		# 起始URL列表
		start_urls = ['https://movie.douban.com/top250']

		#   注释默认的parse函数
		#   def parse(self, response):
		#        pass


		# 爬虫启动时，引擎自动调用该方法，并且只会被调用一次，用于生成初始的请求对象（Request）。
		# start_requests()方法读取start_urls列表中的URL并生成Request对象，发送给引擎。
		# 引擎再指挥其他组件向网站服务器发送请求，下载网页
		def start_requests(self):
			# for i in range(0, 10):
				i=0
				url = f'https://movie.douban.com/top250?start={i*25}'
				#dont_filter 设置为 True，是用来解除去重功能。Scrapy 自带 url 去重功能，第二次请求之前会将已发送的请求自动进行过滤处理。所以将 dont_filter 设置为 True 起到的作用是解除去重功能，一旦设置成重 True，将不会去重，直接发送请求。
				yield scrapy.Request(url=url, callback=self.parse, dont_filter=False)
				# url 请求访问的网址
				# callback 回调函数，引擎回将下载好的页面(Response对象)发给该方法，执行数据解析
				# 这里可以使用callback指定新的函数，不是用parse作为默认的回调参数

		# 解析函数
		def parse(self, response):
			# 打印网页的url
			print(response.url)
			# 打印网页的内容
			# print(response.text)

			# soup = BeautifulSoup(response.text, 'html.parser')
			# title_list = soup.find_all('div', attrs={'class': 'hd'})
			movies = Selector(response=response).xpath('//div[@class="hd"]')
			for movie in movies:
			#     title = i.find('a').find('span',).text
			#     link = i.find('a').get('href')
				# 路径使用 / .  .. 不同的含义　
				title = movie.xpath('./a/span/text()')
				link = movie.xpath('./a/@href')
				print('-----------')
				print(title)
				print(link)
				print('-----------')
				print(title.extract())
				print(link.extract())
				print(title.extract_first())
				print(link.extract_first())
				print(title.extract_first().strip())
				print(link.extract_first().strip())
	

	调试Xpath的方法：
	1）利用浏览器开发者工具，Ctrl+False
	2）利用终端进行一些输出
	