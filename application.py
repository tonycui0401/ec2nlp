# coding=utf8
#!/usr/bin/env python
from tika import parser
from collections import Counter
import pkuseg
import scrapy
from scrapy.crawler import CrawlerProcess
from items import HudongItem
from six.moves import urllib
import os
from flask import Flask, request, render_template, url_for, redirect
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
import subprocess
import json
import numpy as np
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# Pokemons =["Pikachu", "Charizard", "Squirtle", "Jigglypuff",  
#            "Bulbasaur", "Gengar", "Charmander", "Mew", "Lugia", "Gyarados"] 
# # print a nice greeting.
# def say_hello(username = "World"):
#     return '<p>Hello %s!</p>\n' % username

# def fileFrontPage():
#     return render_template('fileform.html')

# some bits of text for the page.
header_text = '''
    <html>\n<head> <title>EB Flask Test</title> </head>\n<body>'''
instructions = '''
    <p><em>Hint</em>: This is a RESTful web service! Append a username
    to the URL (for example: <code>/Thelonious</code>) to say hello to
    someone specific.</p>\n'''
home_link = '<p><a href="/">Back</a></p>\n'
footer_text = '</body>\n</html>'

# EB looks for an 'application' callable by default.
application = Flask(__name__)

split_sign = '##'  # 定义分隔符
filename = 'example.ppt'



# filename = os.path.join('result.json')
# with open(filename) as blog_file:
#     data = json.load(blog_file)
#     data = np.array(data)
#     for i in data.flat:
#        dictvalue.append(i['title'])
#         # print(i)

# print (dictvalue)

class HudongSpider(scrapy.Spider):
    name = "hudong"  # 爬虫启动命令：scrapy crawl hudong -o items.json -s FEED_EXPORT_ENCODING=UTF-8

    allowed_domains = ["http://www.baike.com"]  # 声明地址域

    #   file_object = open('merge_table3.txt','r').read()
    words = ['气缸', '气缸体', '活塞', '间隙', '直径']

    start_urls = []
    count = 0

    #   start_urls.append('http://www.baike.com/wiki/小米%5B农作物%5D')
    #   start_urls.append('http://www.baike.com/wiki/苹果%5B果实%5D')
    #   start_urls.append('http://www.baike.com/wiki/李%5B蔷薇科李属植物%5D')

    # 本处是用于构造原始json
    for i in words:  ##生成url列表
        cur = "http://www.baike.com/wiki/"
        cur = cur + str(i)
        start_urls.append(cur)

    #       count += 1
    #       #print(cur)
    #       if count > 1000:
    #           break

    def parse(self, response):
        # div限定范围
        main_div = response.xpath('//div[@class="w-990"]')

        title = response.url.split('/')[-1]  # 通过截取url获取title
        title = urllib.parse.unquote(title)
        if title.find('isFrom=intoDoc') != -1:
            title = 'error'

        url = response.url  # url直接得到
        url = urllib.parse.unquote(url)

        img = ""  # 爬取图片url
        for p in main_div.xpath('.//div[@class="r w-300"]/div[@class="doc-img"]/a/img/@src'):
            img = p.extract().strip()

        openTypeList = ""  # 爬取开放域标签
        flag = 0  # flag用于分隔符处理（第一个词前面不插入分隔符）
        for p in main_div.xpath('.//div[@class="l w-640"]/div[@class="place"]/p[@id="openCatp"]/a/@title'):
            if flag == 1:
                openTypeList += split_sign
            openTypeList += p.extract().strip()
            flag = 1

        detail = ""  # 详细信息
        detail_xpath = main_div.xpath('.//div[@class="l w-640"]/div[@class="information"]/div[@class="summary"]/p')
        if len(detail_xpath) > 0:
            detail = detail_xpath.xpath('string(.)').extract()[0].strip()

        if detail == "":  # 可能没有
            detail_xpath = main_div.xpath('.//div[@class="l w-640"]/div[@id="content"]')
            if len(detail_xpath) > 0:
                detail = detail_xpath.xpath('string(.)').extract()[0].strip()

        flag = 0
        baseInfoKeyList = ""  # 基本信息的key值
        for p in main_div.xpath(
                './/div[@class="l w-640"]/div[@name="datamodule"]/div[@class="module zoom"]/table//strong/text()'):
            if flag == 1:
                baseInfoKeyList += split_sign
            baseInfoKeyList += p.extract().strip()
            flag = 1

        ## 继续调xpath！！！！！！！！！！！！！
        flag = 0
        baseInfoValueList = ""  # 基本信息的value值
        base_xpath = main_div.xpath('.//div[@class="l w-640"]/div[@name="datamodule"]/div[@class="module zoom"]/table')
        for p in base_xpath.xpath('.//span'):
            if flag == 1:
                baseInfoValueList += split_sign
            all_text = p.xpath('string(.)').extract()[0].strip()
            baseInfoValueList += all_text
            flag = 1

        item = HudongItem()
        item['title'] = title
        item['url'] = url
        item['image'] = img
        item['openTypeList'] = openTypeList
        item['detail'] = detail
        item['baseInfoKeyList'] = baseInfoKeyList
        item['baseInfoValueList'] = baseInfoValueList

        yield item
# process = CrawlerProcess()
# process = CrawlerProcess({
#     'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
#     'FEED_FORMAT': 'json',
#     'FEED_URI': 'result.json',
#     'FEED_EXPORT_ENCODING': 'UTF-8'
# })

# add a rule for the index page.
@application.route("/")
def fileFrontPage():
    return render_template('fileform.html')

@application.route("/handleUpload", methods=['POST'])
def handleFileUpload():
    if 'photo' in request.files:
        photo = request.files['photo']
        if photo.filename != '':            
            photo.save(os.path.join(photo.filename))
            os.remove("result.json")
            file = photo.filename
            parsed = parser.from_file(photo.filename)
            seg = pkuseg.pkuseg(postag=True)
            text = seg.cut(parsed["content"])
            spider_name = "hudong"
            subprocess.check_output(['python3', 'extracter.py', photo.filename])
            # with open("result.json") as items_file:
            #     return items_file.decode('utf-8')..read()
            # print(text)
            # run_spider()
            # process.crawl(HudongSpider, file)
            # process.start(stop_after_crawl=False)
            # process.stop()
            # def search(runner, keyword):
            #   return runner.crawl(HudongSpider, keyword)
            # runner = CrawlerProcess()
            # search(runner, file)
            # runner.start()
            # print(file)
            # run_spider()
            # def _crawl(result, spider):
            #     deferred = process.crawl(spider)
            #     deferred.addCallback(_crawl, spider)
            #     return deferred
            # _crawl(None, HudongSpider)

            # runner = CrawlerRunner()
            # runner.crawl(HudongSpider)
            # d = runner.join()
            # d.addBoth(lambda _: reactor.stop())
            # reactor.run()

            # process.crawl(HudongSpider)
            # process.start() # the script will block here until the crawling is finished
    return redirect(url_for('users'))

@application.route('/users/')
def users():
    filename = os.path.join('result.json')
    with open(filename) as blog_file:
        dictvalue = []
        dictvalueEx = []
        images= []
        data = json.load(blog_file)
        data = np.array(data)
        for i in data.flat:
           dictvalue.append(i['title'])
           dictvalueEx.append(i['detail'])
           images.append(i['image'])
    # print (data)
    return render_template('users.html', len = len(dictvalue), Pokemons = dictvalue, PokemonsEx = dictvalueEx, Images = images)

# if __name__ == '__main__':
#     app.run()

# add a rule when the page is accessed with a name appended to the site
# URL.
# application.add_url_rule('/<username>', 'hello', (lambda username:
#     header_text + say_hello(username) + home_link + footer_text))

# @app.route("/")
# def fileFrontPage():
#     return render_template('fileform.html')


# run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.debug = True
    application.run()