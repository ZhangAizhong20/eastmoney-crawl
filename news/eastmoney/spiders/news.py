import time

import scrapy
from bs4 import BeautifulSoup
from scrapy.http import HtmlResponse
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from scrapy_selenium import SeleniumRequest
from selenium import webdriver
from scrapy import Request
from selenium.webdriver.common.by import By
from scrapy.selector import Selector

from eastmoney.items import News


class NewsSpider(scrapy.Spider):
    name = "news"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        self.keywords = '数字普惠金融'
        # options = Options()
        # options.add_argument('--headless')  # 无头模式
        # options.add_argument('--disable-gpu')  # 禁用GPU加速
        # options.add_argument('--blink-settings=imagesEnabled=false')  # 禁止加载图片
        # self.option = options

    def start_requests(self):
        keywords = self.keywords
        type = 'content'
        url = f'https://so.eastmoney.com/news/s?keyword={keywords}&sort=score&type={type}'
        # chrome_options = Options()
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        yield Request(url=url, callback=self.parse)

    def parse(self, response: HtmlResponse, **kwargs):
        bro = self.driver
        bro.get(url=response.url)
        time.sleep(0.25)
        news_url_lists = []
        for i in range(1, 50):
            try:
                str1 = '下一页'
                ele = bro.find_element('xpath', f'//*[@id="app"]/div[3]/div[1]/div[4]/div/a[@title=\"{str1}\"]')
                ele.click()

                # news_list = #app > div.main.container > div.c_l > div.news_list > div:nth-child(1)
                time.sleep(0.2)
                page_text = bro.page_source
                soup = BeautifulSoup(page_text, 'html.parser')
                news_list = soup.select('#app > div.main.container > div.c_l > div.news_list > div')
                for news in news_list:
                    # news_item = News()
                    url = news.select_one('div.news_item_t > a')['href']
                    news_url_lists.append(url)
                    # print('success'+url)
            except:time.sleep(10)

        for url in news_url_lists:
            yield Request(url=url, callback=self.Fullnews)
        # # print(page_text)

    def Fullnews(self, response: HtmlResponse, **kwargs):

        total_news = News()
        Sel = Selector(response)
        total_news['url'] = response.url
        total_news['title'] = Sel.css('#topbox > div.title::text').extract_first()

        total_news['body'] = '\n'.join(response.xpath("//div[@id='ContentBody']//p").xpath(
            'string(.)').extract()).strip()  # //*[@id="ContentBody"]/p[3]
        total_news['publish_time'] = Sel.css('#topbox > div.tipbox > div.infos > div:nth-child(1)::text').extract_first()

        total_news['source'] = Sel.css('#topbox > div.tipbox > div.infos > div:nth-child(2)::text').extract_first()

        print(total_news['body'])
        yield total_news

