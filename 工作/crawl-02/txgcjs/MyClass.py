# encoding=utf-8
import re
import sys
import logging
import getpass
import pymysql
from bs4 import BeautifulSoup
from items import Spider_item
from config import mysql_local



class MyLog(object):
    # 类MyLog的构造函数
    def __init__(self):
        self.user = getpass.getuser()
        self.logger = logging.getLogger(self.user)
        self.logger.setLevel(logging.DEBUG)
        # 日志文件名
        self.logFile = sys.argv[0][0:-3] + '.log'                           # print(sys.argv[0])   代表文件名 输出 mylog.py
        self.formatter = logging.Formatter('%(asctime)-12s %(levelname)-8s %(name)-10s %(message)-12s\r\n')

        # 日志显示到屏幕上并输出到日志文件内
        # 输出到日志文件
        self.logHand = logging.FileHandler(self.logFile, encoding='utf8')
        self.logHand.setFormatter(self.formatter)
        self.logHand.setLevel(logging.DEBUG)

        # 输出到屏幕
        self.logHandSt = logging.StreamHandler()
        self.logHandSt.setFormatter(self.formatter)
        self.logHandSt.setLevel(logging.DEBUG)

        # 添加两个Handler
        self.logger.addHandler(self.logHand)
        self.logger.addHandler(self.logHandSt)

    # 日志的5个级别对应以下的5个函数
    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)



class Contentre():
    def cont(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        for tag in soup.findAll(True):                                      # find_all(True) 来获取所有的 content的HTML 标签
            attrs = dict(tag.attrs)                                         # dict(tag.attrs) 将标签的所有属性展开成一个字典
            for attr in attrs:                                              # 遍历所有属性
                if attr != "href" or attr != "src":                         # 如果这个属性名不是 "href"
                    del tag[attr]                                           # del tag[attr] 将这个标签的属性删除掉

        no_attr_html = str(soup)                                            # 将修改后的 BeautifulSoup 对象转换为字符串
        return no_attr_html



class SaveMysql():
    def save_mysql(self, title, content, text, content_url, annex, time, special, platform_id, fid, region, trade,
                   exist_num):
        # todo 存储：

        uid = 20
        sync = 0

        local = ""
        it = Spider_item()
        it.fid = fid
        it.uid = uid
        it.title = title
        it.content = content
        it.region = region
        it.trade = trade
        it.text = text
        it.source = content_url
        it.annex = annex
        it.notice_time = time
        it.local = local
        it.special = special
        it.platform_id = platform_id
        it.sync = sync

        if exist_num == 0:
            conn = pymysql.Connect(**mysql_local)                                  # 连接mysql信息(连接信息存储在config.py中)
            cursor = conn.cursor()                                                 # 游标
            keys = ', '.join(it.__dict__.keys())                                   # 封装成一个字典
            sql = 'INSERT INTO {bids}({keys}) VALUES {values}'.format(bids='bids', keys=keys,
                                                                      values=tuple(it.__dict__.values()))
            cursor.execute(sql)
            conn.commit()


# class htmls():
#     # def divs_hl(self):
#     #     divs_html = ''
#     #     my_list = ["<div><div><label>招标人:</label>", "<div><div><label>项目编号:</label>",
#     #                "<div><div><label>项目类型:</label>"]
#     #     for i in range(0, 6):
#     #         if i == 0:
#     #             # 创建一个div元素
#     #             div = '<div>' + '<div>' + str({i}) + '</div>' + '</div>' + my_list[0]
#     #         else:
#     #             div = div + '</div>' + '</div>' + my_list[1]
#     #             if i == 2:
#     #                 div = div + my_list[2]
#     #         if i > 2:
#     #             div = '<span>' + str({i}) + '</span>'
#     #         # 将新的div元素添加到原有的字符串中
#     #         divs_html += div
#     #
#     #     divs_html = '<form>' + divs_html + '</div>' + '</div>' + '</div>' + '</div>'
#     #     return divs_html
#     # def divs_hls(self):
#     #     my_list = ["<div><div><label>标段编号:</label>","<div><div><label>中标人:</label>", "<div><div><label>中标份额:</label>",
#     #                "<div><div><label>标段名称:</label", "<div><div><label>中标价格:</label>","<div><div><label>中标日期:</label>"]
#     #     divs_htmls = ""
#     #     n = 0
#     #     for m in range(0, 7):
#     #         try:
#     #             if m == 0:
#     #                 div = '<div><div><div><div>' + str({m}) + '</div>' + '</div>' + my_list[n]
#     #             else:
#     #                 div = '<div><div>' + str({m}) + '</div></div></div></div>' + my_list[n + 1]
#     #                 n += 1
#     #                 print(m)
#     #             divs_htmls += div
#     #             divs_htmls = '<span>' + divs_htmls + '<div><div>'+str({6})+'</div></div>'+ '</div></div></div></div>' + '</span>'
#     #
#     #         except Exception as e:
#     #             continue
#     #
#     #     return divs_htmls
#
#     pass