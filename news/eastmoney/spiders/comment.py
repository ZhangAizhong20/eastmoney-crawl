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
from eastmoney.items import Comment



class commentSpider(scrapy.Spider):
    name = 'comment'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        chrome_options = webdriver.ChromeOptions()
        # self.title = '大学搜题酱'
        # prefs = {"profile.managed_default_content_settings.images": 2}
        # chrome_options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(chrome_options=chrome_options)

    def start_requests(self):
        dic = {'快答案': 'https://appgallery.huawei.com/app/C102759767',
               "上学吧找答案": 'https://appgallery.huawei.com/app/C100092693',
               '火星搜题': 'https://appgallery.huawei.com/app/C103805631',
               "大学搜题王": 'https://appgallery.huawei.com/app/C104604599',
               '大学搜题酱':'https://appgallery.huawei.com/app/C102506411'
               }
        for title,url in dic.items():
            # url = 'https://appgallery.huawei.com/app/C102506411'
            yield Request(url=url,cb_kwargs={'title':title})


    def parse(self, response,**kwargs):
        title = kwargs['title']
        Sel1 = Selector(response)
        name = Sel1.css(
            'body > div > div.box > div > div.componentContainer > div:nth-child(1) > div > div.center_info > div.title::text').extract_first()
        download_time = Sel1.css(
            'body > div > div.box > div > div.componentContainer > div:nth-child(1) > div > div.center_info > div.center_info_bottom > div.downloads > span::text').extract_first()
        score = Sel1.css('body > div > div.box > div > div.componentContainer > div:nth-child(1) > div > div.center_info > div.center_info_bottom > div.downloads > span')
        print(score)
        name = str(name)
        bro = self.driver
        bro.get(url=response.url)
        time.sleep(0.5)
        bro.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.1)


        download_time = str(download_time)
        score = str(score)
        # / html / body / div / div[2] / div / div[3] / div[4] / div / div[1] / div[2]
        ele = bro.find_element('css selector', 'body > div > div.box > div > div.componentContainer > div:nth-child(4) > div > div.header > div.more')
        ele.click()
        time.sleep(0.5)
        for i in range(20):
            time.sleep(0.05)
            bro.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        page_text_comment = bro.page_source
        soup = BeautifulSoup(page_text_comment, 'html.parser')
        comment_list = soup.select('body > div > div.box > div > div.componentContainer > div.CommentList > div.listContainer > div')
        for comment in comment_list:
            # print("one")
            # print(comment)
            try:
                com = Comment()
                com['publish_time'] = comment.select_one('div.right > div.part_top > div > div.deviceName > div').text #body > div > div.box > div > div.componentContainer > div.CommentList > div.listContainer > div:nth-child(4) > div.right > div.part_top > div > div.deviceName > div
                com['device'] = comment.select_one('div.right > div.part_top > div > div.deviceName > span').text
                com['text'] = comment.select_one('div.right > div.part_middle').text
                secore_items = comment.select('div.right > div.part_bottom > div.newStarBox.starBox > img')
                current_socre = 5

                for img in secore_items:
                    img_type = img['src']
                    if "3ZnPg" in img_type:
                        current_socre -= 1
                com['score'] = current_socre
                com['title'] = title

                yield com
            except: pass






