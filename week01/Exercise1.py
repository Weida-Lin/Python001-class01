import requests
from bs4 import BeautifulSoup as bs
import pandas as pd

movie_name = []
movie_genre = []
movie_date = []
urls = []

#电影列表，提取电影名称与电影详情页面的超链接
user_agent1 = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'

header1 = {
    'user-agent':user_agent1,
    'Accept': "*/*",
    'Accept-Encoding': 'gazip, deflate, br',
    'Accept-Language': 'en-AU,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,la;q=0.6',
    'Content-Type': 'text/plain',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site'
    }
	
starturl = 'https://maoyan.com/films?showType=3'

response = requests.get(starturl,headers=header1)
bs_info = bs(response.text, 'html.parser')

for tags in bs_info.find_all('div', attrs={'class': 'channel-detail movie-item-title'}):
	for atag in tags.find_all('a',):
        movie_name.append(atag.text)
        urls.append('https://maoyan.com'+atag.get('href'))


#电影详情页面,提取电影种类与上映时间
user_agent2 = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0'

header2 = {
    'user-agent':user_agent2,
    'Accept': "*/*",
    'Accept-Encoding': 'gazip, deflate, br',
    'Accept-Language': 'en-AU,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,la;q=0.6',
    'Content-Type': 'text/plain',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'cross-site'
    }

for url in urls[:10]:
    detail_page = requests.get(url, headers=header2)
    bs_info = bs(detail_page.text, 'html.parser')
    genre = ''
    divtag = bs_info.find('div', attrs={'class': 'movie-brief-container'})
    for i, value in enumerate(divtag.find_all('li',)):
        #提取第一个<li>标签的类型信息
		if i == 0:
            for atag in value.find_all('a',):
                genre += atag.text
            movie_genre.append(genre)
		#提取第三个<li>标签的日期信息
        if i == 2:
            movie_date.append(value.text[:10])


#将提取到的信息整合为csv文件
movie_data = {
    'name' : movie_name[:10],
    'genre' : movie_genre,
    'date'  : movie_date
}

movies = pd.DataFrame(data = movie_data)
#用utf-8保存为csv会乱码，于是用gbk
movies.to_csv('movies.csv', encoding='gbk')