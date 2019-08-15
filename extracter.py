# coding=utf8
#!/usr/bin/env python
from tika import parser
from collections import Counter
import pkuseg
import scrapy
from scrapy.crawler import CrawlerProcess
from items import HudongItem
from six.moves import urllib
import re
import sys

filename = sys.argv[1]


split_sign = '##'  # 定义分隔符
# filename = 'example2.ppt'

class HudongSpider(scrapy.Spider):
    name = "hudong"  # 爬虫启动命令：scrapy crawl hudong -o items.json -s FEED_EXPORT_ENCODING=UTF-8

    allowed_domains = ["http://www.baike.com"]  # 声明地址域

    #   file_object = open('merge_table3.txt','r').read()


    # file_object = open('crawled_leaf_list.txt', 'r', encoding='UTF-8').read()
    # wordList = file_object.split()  # 获取词表
    parsed = parser.from_file(filename)
# print(parsed["metadata"]) #To get the meta data of the file
# print(parsed["content"]) # To get the content of the file

    seg = pkuseg.pkuseg(postag=True)           # 以默认配置加载模型
# text = seg.cut('PowerPoint 演示文稿气缸故障已显现，如何判断气缸是否进入维修程序？课题3 缸体的检测 2提出问题3课时安排 理论1节实训2节1课程引入4教学方法理论引导分组实训互动学习体会手感课题3 缸体的检测重点难点技术标准实训器材教学内容掌握 气缸的圆度、圆柱度 气缸体上平面平面度的 检测方法掌握几个概念掌握刀口尺、塞尺、内径量表的使用方法课题3 缸体的检测重点难点技术标准实训器材教学内容轿车气缸体上平面的平面度误差≯0.12mm主轴承座孔的圆度及圆柱度对于铝合金气缸体不大于0.015mm技术标准:汽油机:圆度 ≯0.05 圆柱度≯ 0.12 柴油机:圆度≯ 0.063 圆柱度≯0.20轿车气缸磨损尺寸与标准尺寸的差值≯0.08mm实训设备与器材缸体及配套活塞1个千分尺与内径量表各1套刀口尺 1把塞尺1把清 洁 总 成气缸体上平面度的检测 职 业 素 质 的 养 成 活塞与气缸配合间隙的检测 气缸磨损程度的检测 教学内容 油污、积炭和水垢衬 垫 材 料轻 微 凸 起螺 丝 孔1.清洗缸体（检测前） 1.清洗缸体 （检验前） 检验前彻底清理气缸体上、下平面及内、外部的油污、积炭和水垢。使用刮刀将气缸体接触表面上所有衬垫材料清除掉，注意不要刮伤表面。消除毛刺并铲平或刮平螺孔周围的轻微凸起。 检查气缸体上的螺丝孔是否有丝扣损坏或滑丝的现象，必要时更换螺栓。 2.气缸体上平面度的检验 外观检验气缸体上平面度检测要领技术标准2.气缸体上平面度的检验 外观检验气缸体上平面度六个位置注意手感误差≯0.12mm检查有无磨损、损伤及裂纹。 [概念一] 用塞尺测量刀口尺与上平面间的间隙，塞入塞尺的最大厚度值就是平面度误差。塞尺拉动时稍有阻力检测要领 牢记部位 体会手感3.气缸磨损程度的检测气缸磨损规律气缸直径的测量圆 柱 度圆 度3.气缸磨损程度的检测气缸磨损规律知识扩展单缸横向大；纵向小整机首尾两缸磨损大3.气缸磨损程度的检测 使用量缸表时应注意 使测杆与气缸轴线保持垂直，以达到测量的准确性。 指针指示到最小读数时，这时才能记录读数， 在上述测量中，其最大、最小读数即为某气缸的最大、最小缸径。 气缸磨损规律知识扩展知识扩展气缸直径的测量检测要领用50 -lOOmm量缸表，分别在横向A和纵向B和上、中、下处测量气缸直径。最大直径部位---第一道活塞环上止点处13.unknown3.气缸磨损程度的检测气缸磨损规律气缸直径的测量知识扩展知识扩展检测要领圆 度知识扩展[概念二] 同一横截面中的最大和最小直 径差值的一半。 圆 度= (D1max - D1min)/2 气缸总体圆度误差：三个圆度中的最大的3.气缸磨损程度的检测气缸磨损规律气缸直径的测量圆 柱 度知识扩展知识扩展检测要领圆 度知识扩展')  # 进行分词
    text = seg.cut(parsed["content"])
# print(text.__class__)
    nouns = []

    for i in text:
       if i[1]== 'n':
   	      nouns.append(i[0])

    words = []

    items = list(Counter(nouns).items())

    for i in items:

       if i[1]>10 and i[0]!='mm':

          words.append(i[0])


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

process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'FEED_FORMAT': 'json',
    'FEED_URI': 'result.json',
    'FEED_EXPORT_ENCODING': 'UTF-8'
})

process.crawl(HudongSpider)
process.start() # the script will block here until the crawling is finished

# parsed = parser.from_file('example.ppt')
# # print(parsed["metadata"]) #To get the meta data of the file
# # print(parsed["content"]) # To get the content of the file

# seg = pkuseg.pkuseg(postag=True)           # 以默认配置加载模型
# # text = seg.cut('PowerPoint 演示文稿气缸故障已显现，如何判断气缸是否进入维修程序？课题3 缸体的检测 2提出问题3课时安排 理论1节实训2节1课程引入4教学方法理论引导分组实训互动学习体会手感课题3 缸体的检测重点难点技术标准实训器材教学内容掌握 气缸的圆度、圆柱度 气缸体上平面平面度的 检测方法掌握几个概念掌握刀口尺、塞尺、内径量表的使用方法课题3 缸体的检测重点难点技术标准实训器材教学内容轿车气缸体上平面的平面度误差≯0.12mm主轴承座孔的圆度及圆柱度对于铝合金气缸体不大于0.015mm技术标准:汽油机:圆度 ≯0.05 圆柱度≯ 0.12 柴油机:圆度≯ 0.063 圆柱度≯0.20轿车气缸磨损尺寸与标准尺寸的差值≯0.08mm实训设备与器材缸体及配套活塞1个千分尺与内径量表各1套刀口尺 1把塞尺1把清 洁 总 成气缸体上平面度的检测 职 业 素 质 的 养 成 活塞与气缸配合间隙的检测 气缸磨损程度的检测 教学内容 油污、积炭和水垢衬 垫 材 料轻 微 凸 起螺 丝 孔1.清洗缸体（检测前） 1.清洗缸体 （检验前） 检验前彻底清理气缸体上、下平面及内、外部的油污、积炭和水垢。使用刮刀将气缸体接触表面上所有衬垫材料清除掉，注意不要刮伤表面。消除毛刺并铲平或刮平螺孔周围的轻微凸起。 检查气缸体上的螺丝孔是否有丝扣损坏或滑丝的现象，必要时更换螺栓。 2.气缸体上平面度的检验 外观检验气缸体上平面度检测要领技术标准2.气缸体上平面度的检验 外观检验气缸体上平面度六个位置注意手感误差≯0.12mm检查有无磨损、损伤及裂纹。 [概念一] 用塞尺测量刀口尺与上平面间的间隙，塞入塞尺的最大厚度值就是平面度误差。塞尺拉动时稍有阻力检测要领 牢记部位 体会手感3.气缸磨损程度的检测气缸磨损规律气缸直径的测量圆 柱 度圆 度3.气缸磨损程度的检测气缸磨损规律知识扩展单缸横向大；纵向小整机首尾两缸磨损大3.气缸磨损程度的检测 使用量缸表时应注意 使测杆与气缸轴线保持垂直，以达到测量的准确性。 指针指示到最小读数时，这时才能记录读数， 在上述测量中，其最大、最小读数即为某气缸的最大、最小缸径。 气缸磨损规律知识扩展知识扩展气缸直径的测量检测要领用50 -lOOmm量缸表，分别在横向A和纵向B和上、中、下处测量气缸直径。最大直径部位---第一道活塞环上止点处13.unknown3.气缸磨损程度的检测气缸磨损规律气缸直径的测量知识扩展知识扩展检测要领圆 度知识扩展[概念二] 同一横截面中的最大和最小直 径差值的一半。 圆 度= (D1max - D1min)/2 气缸总体圆度误差：三个圆度中的最大的3.气缸磨损程度的检测气缸磨损规律气缸直径的测量圆 柱 度知识扩展知识扩展检测要领圆 度知识扩展')  # 进行分词
# text = seg.cut(parsed["content"])
# # print(text.__class__)
# nouns = []

# for i in text:
#    if i[1]== 'n':
#    	  nouns.append(i[0])

# words = []

# items = list(Counter(nouns).items())

# for i in items:

#    if i[1]>10 and i[0]!='mm':

#       words.append(i[0])

# print(words)

# print(list(Counter(nouns).items()))