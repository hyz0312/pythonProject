import time
import requests
from lxml import etree
import re
from lxml.html import fromstring
from lxml.html import _transform_result
import requests
from Crypto import Random
from Crypto.PublicKey import RSA
import base64
from Crypto.Cipher import PKCS1_v1_5
import execjs
import urllib
from bs4 import BeautifulSoup
from w3lib.html import remove_comments
from save_mysql import SaveMysql

"""
var param="pageNo="+hid+"&_ser_p="+encodeURIComponent(encoder.encryptRSA(hid));
hrefurl = "/cms/channel/ccbbidzbgg/1088964.htm"
content_url = "https://ibuy.ccb.com"+hrefurl+param

"""


# todo 下载
def download(url, num):
    num = num
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://ibuy.ccb.com",
        "Referer": "https://ibuy.ccb.com/cms/channel/ccbbidzbgg/index.htm",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.57",
        "sec-ch-ua": "\"Chromium\";v=\"110\", \"Not A(Brand\";v=\"24\", \"Microsoft Edge\";v=\"110\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\""
    }
    url = url
    num = num
    pageNo = num
    # 读取公钥
    key = open('public.pem').read()
    public_key = RSA.importKey(key)
    # 加密
    pk = PKCS1_v1_5.new(public_key)
    encrypt_text = pk.encrypt(str(num).encode())
    # 加密后进行 base64 编码
    result = base64.b64encode(encrypt_text)
    # 转换成字符串
    _ser_p = bytes.decode(result)

    data = {
        "pageNo": num,
        "_ser_p": _ser_p,
        "keyword": "",
        "region": "",
        "beginDate": "",
        "endDate": ""
    }
    response = requests.post(url, headers=headers, data=data)
    print(response.text)
    return response


def parse(response):
    # 解析：
    html = etree.HTML(response.text)
    hid = html.xpath('//div[@class="infolist-main single-main bidlist"]/ul/li/a/@hid')

    hrefurl = html.xpath('//div[@class="infolist-main single-main bidlist"]/ul/li/a/@hrefurl')
    if hid == []:
        hid = html.xpath('//div[@class="infolist-main bidlist"]/ul/li/a/@hid')
        hrefurl = html.xpath('//div[@class="infolist-main bidlist"]/ul/li/a/@hrefurl')

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://ibuy.ccb.com",
        "Referer": "https://ibuy.ccb.com/cms/channel/ccbbidzbgg/index.htm",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.57",
        "sec-ch-ua": "\"Chromium\";v=\"110\", \"Not A(Brand\";v=\"24\", \"Microsoft Edge\";v=\"110\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\""
    }

    # 获取详情页链接：
    for hid in hid:
        # 读取公钥
        key = open('public.pem').read()
        public_key = RSA.importKey(key)

        # 加密
        pk = PKCS1_v1_5.new(public_key)
        encrypt_text = pk.encrypt(hid.encode())

        # 加密后进行 base64 编码
        result = base64.b64encode(encrypt_text)

        # 转换成字符串
        result_str = bytes.decode(result)

        # 把字符串作为 URI 组件进行编码。
        url_code_name = urllib.parse.quote(result_str)

        param = "?pageNo=" + hid + "&_ser_p=" + url_code_name
    for hrefurl in hrefurl:
        content_url = "https://ibuy.ccb.com" + hrefurl + param
        print(content_url)
        res = requests.get(content_url, headers=headers)

        # todo 详情页解析
        html1 = etree.HTML(res.text)
        # 时间处理
        time = str(html1.xpath('//div[@class="article-author"]/em/text()')[0]).replace("\n", "").replace("\t",
                                                                                                         "").replace(
            "发布时间：", "").strip()
        # 标题：
        title = str(html1.xpath('//div[@class="article-content"]/div[1]/text()')[0])
        # 附件地址：
        annex = ""
        annexs = html1.xpath('//div[@class="text"]/div/span/a/@href')
        for annexs in annexs:
            annex += "https://ibuy.ccb.com" + annexs + ","
        # todo 正则匹配到附件最后的逗号
        ann = re.compile(r'(,)\Z')
        # 把匹配到的逗号替换为空，并塞回annex中，完成数据处理
        annex = re.sub(ann, '', annex)

        if "中标" in title:
            fid = 134
        else:
            fid = 133
        print(fid)
        # todo 内容：
        # 1.数据处理，拿到需要解析的html 对content进行数据处理
        table = html1.xpath('/html/body/div[2]/div/div/div[3]')[0]
        # 正则匹配需要替换的标签
        tb_re = re.compile(r'<table.*?>')
        ta_re = re.compile(r'<col .*?>')
        tr_re = re.compile(r'<tr.*?>')
        td_re = re.compile(r'<td.*?>')
        tc_re = re.compile(r'( target=".*?")')
        # 2、逐一删除 元素属性,枕着匹配tanle 等元素属性
        for content in table:
            etree.strip_attributes(content,
                                   ["style", "id", "class", "alt", "data-test", "table", "td", "tr",
                                    "div", "table"])
        # Element对象转成字符串
        content = etree.tostring(table, encoding='utf-8').decode().replace('<div class="main-text">',
                                                                           "").replace("</div>", "").replace("\n",
                                                                                                             "").strip()
        # 替换标签，并塞回原html
        content = re.sub(tb_re, '<table>', content)
        content = re.sub(ta_re, '<col>', content)
        content = re.sub(tr_re, '<tr>', content)
        content = re.sub(td_re, '<td>', content)
        content = re.sub(tc_re, '', content)
        content = " ".join(content.split())

        # 遍历附件拿到附件html并与前面拿到的content拼接成完整的html
        fujian = html1.xpath('/html/body/div[2]/div/div/div[4]')[0]
        for fujians in fujian:
            etree.strip_attributes(fujians,
                                   ["style", "id", "class", "alt", "data-test", "table", "td", "tr",
                                    "div", "table"])
        fujian = etree.tostring(fujian, encoding='utf-8').decode().replace(
            ' class="text" style="font-size: 15px;line-height: 40px;padding-left: 2%;"', "").replace(
            ' class="article-bottom"', "").replace("\n", "").strip()
        fujian = " ".join(fujian.split())
        th = re.compile(r'(<a hid="(.*?)" hrefurl="/(.*?)">)')
        fujian = re.sub(th, '<a>', fujian)
        # fj =re.compile(r'"(.*?)"')
        # print(type(fj))
        fj_html = etree.HTML(fujian)
        #
        fjss = ""
        fj = fj_html.xpath('/html/body//a/@href')
        for fjs in fj:
            fjss = '"' + "https://ibuy.ccb.com" + fjs + '"'
        fj01 = re.compile(r'(".*?")')
        fujian = re.sub(fj01, fjss, fujian)
        print(fujian)
        content = content + fujian

        # todo 获取完整的文件链接
        soup = BeautifulSoup(content, 'lxml')
        soup = soup.find_all('a')
        for sps in soup:
            sps = sps.get("href")
            if sps != None:
                sps = "https://ibuy.ccb.com" + sps
                sps = '"' + sps + '"'
        find = re.compile(r'href="/(.*?)"')
        find = find.sub(f'href={sps}', content)
        # todo 网站唯一标识
        platform_id = 5226
        specials = re.findall("\d+", hrefurl)[0]
        special = str(platform_id) + "_" + str(specials)

        # todo 获取网页全部正文
        element_ = html1.xpath('//div[@class="main-text"]')[0]
        # 获取不同标签下全部内容的方法
        texts = element_.xpath('string(.)')
        # Python3 lxml.etree._ElementUnicodeResult转化为字符串str类型
        text = ""
        for texts in texts:
            text += str(texts)
            text = text.strip()
        text = ",".join(text).replace(",", "")
        text = "".join(text.split())
        region = ""

        region = "全国"
        trade = "中国建设银行"
        # todo 保存 用已经封装好的存储方法执行
        save = SaveMysql()
        save.save_mysql(title, content, text, content_url, annex, time, special, platform_id, fid, region, trade)


if __name__ == '__main__':
    url = ["https://ibuy.ccb.com/cms/channel/ccbbidzbgg/index.htm",
           "https://ibuy.ccb.com/cms/channel/ccbbidzgysgg/index.htm",
           "https://ibuy.ccb.com/cms/channel/ccbbidecgg/index.htm",
           "https://ibuy.ccb.com/cms/channel/ccbbidzbgs/index.htm",
           "https://ibuy.ccb.com/cms/channel/ccbbidzbjggs/index.htm",
           "https://ibuy.ccb.com/cms/channel/ccbgyszj/index.htm",
           "https://ibuy.ccb.com/cms/channel/ccbpurtzgg/index.htm"]

    for num in range(1, 2):
        res = download(url[0], num)
        parse(res)
    for num in range(1, 5):
        res = download(url[1], num)
        parse(res)
    for num in range(1, 5):
        res = download(url[2], num)
        parse(res)
    for num in range(1, 5):
        res = download(url[3], num)
        parse(res)
    for num in range(1, 5):
        res = download(url[4], num)
        parse(res)
    for num in range(1, 2):
        res = download(url[5], num)
        parse(res)
    for num in range(1, 4):
        res = download(url[6], num)
        time.sleep(3)
        parse(res)
