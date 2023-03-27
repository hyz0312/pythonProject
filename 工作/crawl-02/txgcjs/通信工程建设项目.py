import re
import json
import base64
import logging
import pymysql
import ddddocr
import retrying
import openpyxl
import requests
from lxml import etree
from tenacity import retry
from bs4 import BeautifulSoup
from config import mysql_local
from lxml.html import fromstring
from w3lib.html import remove_comments
from lxml.html import _transform_result
from MyClass import MyLog,Contentre,SaveMysql

@retry
def dowmload_zb1(headers, url, urls, i, num):
    headers = headers
    # todo 处理验证码：
    url = url
    response = requests.post(url, headers=headers)
    urls = urls
    num = num
    token = response.json()['token']                                                            # 处理翻页token
    img = response.json()['img']                                                                # 获取验证码图片
    image = "data:image/jpeg;base64," + str(img)                                                # base64加密后的图片链接
    page_content = base64.b64decode(img)                                                        # 将data:image/jpg;base64格式的数据转化为图片
    file_path = './code.jpg'
    with open(file_path, 'wb') as img:
        img.write(page_content)

    # todo 识别验证码（它会在其所装饰的函数运行过程抛出错误时不停地重试下去）
    ocr = ddddocr.DdddOcr()
    with open('./code.jpg', 'rb') as f:
        img_bytes = f.read()
    rese = ocr.classification(img_bytes)
    print(rese)
    data = {
        "resource": "",
        "page": num,
        "limit": 15,
        "totalSize": 0,
        "bulletinTitle": "",
        "issueDate": "",
        "status": "11",
        "bulletinType": str(i),
        "unitRestrict": [],
        "supervisorName": [],
        "nationFlag": None,
        "bidType": None,
        "bidSubtype": None,
        "fileBuyBeginTime": "",
        "fileBuyEndTime": "",
        "occupationBeginDate": "",
        "occupationEndDate": "",
        "issueDates": [],
        "gatewayFlag": 0,
        # code 为获取的图片识别的内容
        "code": rese,
        "token": token,
        "expire": 10,

    }
    if i == "11" or i == "12":
        data = {
            "totalSize": 0,
            "page": num,
            "limit": 15,
            "publicityTitle": "",
            "publishTime": "",
            "occupationBeginDate": "",
            "occupationEndDate": "",
            "publicityType": str(i),
            "bidderName": "",
            "datetime": "",
            "supervisorName": [],
            "nationFlag": None,
            "bidType": None,
            "bidSubtype": None,
            "unitRestrict": [],
            "gatewaySize": 0,
            "code": rese,
            "token": token
        }
    data = json.dumps(data, separators=(',', ':'))
    res = requests.post(urls, headers=headers, data=data)
    # todo 重试
    if res.json()['code'] == 500:
        num = num
        raise Exception("开始重试")
    return res


def parse(res, headers):
    try:
        conn = pymysql.Connect(**mysql_local)
        cursor = conn.cursor()

        content_url = "https://txzbqy.miit.gov.cn/#/gateway/inviteDetail"
        headers = headers
        title_list = res.json()['page']['list']
        for title_list in title_list:
            if 'bulletinTitle' in title_list:
                title = title_list['bulletinTitle']
                time = title_list['issueDate']
                fid = 133
                content = title_list['bulletinComment']
            else:

                fid = 134
                title = title_list['publicityTitle']
                time = title_list['publishTime']
                content = title_list['publicityComment']
                time = title_list['publishTime']

            region = "全国"
            trade = "通信工程建设项目"
            platform_id = 8500
            special = str(platform_id) + "_" + title_list['uuid']
            # 消重
            sql = """SELECT special FROM bids WHERE special = %s limit 1 ;"""
            exist_num = cursor.execute(sql, special)
            conn.commit()

            # todo 处理带附件的网页
            fileId = title_list['fileId']                                                       # 获取fileid对应的是获取文件连接钥匙的data值
            annex_key_url = "https://txzbqy.miit.gov.cn/zbtb/zwzt/file/getFileByKeys"           # 请求钥匙链接获取keyNum为附件下载地址data里的md5Paths
            data = f'["{fileId}"]'.encode('unicode_escape')
            res_annex_key = requests.post(annex_key_url, headers=headers, data=data)
            keyNums = res_annex_key.json()['files']
            if keyNums != []:
                keyNum = keyNums[0]['keyNum']
                annex_url = "https://txzbqy.miit.gov.cn/zbtb/zwzt/file/getAccessToken"          # 请求附件下载地址，并把上面拿到的keynum的值传入到data当中
                data = {
                    "userId": "-1",
                    "md5Paths": keyNum
                }
                data = json.dumps(data, separators=(',', ':'))
                res_annex = requests.post(annex_url, headers=headers, data=data)
                res_annex_cont = res_annex.json()['accessToken'][0]

                annex = "https://file.miit.gov.cn/file/download?&t=" + res_annex_cont           # 获取accessToken的值并拼接成完整的附件url
            else:
                annex = ""

            # todo 调用封装好的数据处理方法
            con = Contentre()
            no_attr_html = con.cont(content).replace("xa0","")
            print(no_attr_html)
            # todo 获取网页全部正文

            html = etree.HTML(no_attr_html)
            element_ = html.xpath('/html/body')
            text = ""
            for element_ in element_:
                element_ = element_.xpath('string(.)')
                text += str(element_)
                text = text.strip()
            text = ",".join(text).replace(",", "")
            text = "".join(text.split())

            # todo 保存 用已经封装好的存储方法执行
            save = SaveMysql()
            save.save_mysql(title, no_attr_html, text, content_url,
                            annex, time, special,
                            platform_id, fid, region, trade, exist_num)
    except Exception as e:
        mylog = MyLog()
        mylog.error(e)
@retry
def download_zzb2(num,headers):
    try:
        conn = pymysql.Connect(**mysql_local)
        cursor = conn.cursor()

        headers = headers
        url = "https://txzbqy.miit.gov.cn/zbtb/gateway/gatewayExpert/getBidInformationList"
        fid = 134
        region = "全国"
        trade = "通信工程建设项目"
        num = num
        data = {
            "totalSize": 0,
            "page": num,
            "limit": 15,
            "bidProjectName": "",
            "supervisorName": [],
            "occupationBeginDate": "",
            "occupationEndDate": "",
            "nationFlag": None,
            "bidType": None,
            "bidSubtype": None,
            "acceptanceBidder": "",
            "unitRestrict": [],
            "bidAcceptanceNotificaiton": [],
            "flag": 2,
            "isPublic": "0"
        }
        data = json.dumps(data, separators=(',', ':'))
        response = requests.post(url, headers=headers, data=data)
        # 获取详情页需要的data
        con_data = response.json()['page']['list']
        print(con_data)
        for con_data in con_data:
            # 获取详情页链接
            html = "</div><!----></div></div></div><!----></div></div></div></div></span></form>"
            headers_c = headers
            content_url = "https://txzbqy.miit.gov.cn/zbtb/gateway/gatewayExpert/getAchieveDetail"
            response = requests.post(content_url, headers=headers_c, json=con_data)                   # 当为json'数据用json=处理
            list_cont = response.json()

            xq_title = '''<form><div><div>{0}</div></div>
                                         <div><div><div><label>招标人:</label><div><div>{1}</div></div></div></div>
                                         <div><div><label>项目编号:</label><div><div>{2}</div></div></div></div>
                                         <div><div><label>项目类型:</label><div><div><span>{3}</span><span>{4}</span><span>{5}</span>
                                         </div></div></div></div></div>'''
            xq_fl = '''<span><div><div><div><div>{0}</div>
                                   <div><div><div><label>标段编号:</label><div><div>{1}</div></div></div></div>
                                   <div><div><label>中标人:</label><div><div>{2}</div></div></div></div>
                                   <div><div><label>中标份额:</label><div><div>{3}</div></div></div></div></div></div></div>
                                   <div><div><div><div><div><label>标段名称:</label><div><div>{4}</div></div></div></div>
                                   <div><div><label>中标价格:</label><div><div>{5}</div></div></div></div>
                                   <div><div><label>中标日期:</label><div><div>{6}</div></div></div></div></div></div></div></div></span>'''

            xqy_info = list_cont['bidRecordTEntity']
            xq_info_title = xq_title.format(xqy_info['bidProjectName'] + '中标信息',
                                            xqy_info['fundResource'], xqy_info['bidProjectCode'],
                                            xqy_info['nationFlag'], '-' + xqy_info['bidType'],
                                            '-' + xqy_info['bidSubtype'],
                                            )
            # </form>

            for zbdata in xqy_info['zbData']:
                xq_info_fl = xq_fl.format(zbdata['bidPackageName'], zbdata['bidPackageCode'],
                                          zbdata['acceptanceBidder'], zbdata['bidShare'],
                                          zbdata['bidProjectName'], zbdata['winningPrice'],
                                          zbdata['bidAcceptanceNotificaiton'], )

                xq_info_title = xq_info_title + xq_info_fl
                time = zbdata['bidAcceptanceNotificaiton']

            content = xq_info_title + '</form>'
            content = content.replace('\n', '').replace(' ', '')
            print(content)
            title = xqy_info['bidProjectName']
            # todo 获取网页全部正文
            html = etree.HTML(content)
            element_ = html.xpath('/html/body')
            text = ""
            for element_ in element_:
                element_ = element_.xpath('string(.)')
                text += str(element_)
                text = text.strip()
            text = ",".join(text).replace(",", "")
            text = "".join(text.split())
            annex = ""
            platform_id = 8500
            special = str(platform_id) + "_" + xqy_info['uuid']
            # 消重
            sql = """SELECT special FROM bids WHERE special = %s limit 1 ;"""
            exist_num = cursor.execute(sql, special)

            # todo 保存 用已经封装好的存储方法执行
            save = SaveMysql()
            save.save_mysql(title, content, text, content_url, annex, time, special, platform_id, fid, region, trade,
                            exist_num)
    except Exception as e:
        mylog = MyLog()
        mylog.error(e)

if __name__ == '__main__':
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Length": "0",
        "Origin": "https://txzbqy.miit.gov.cn",
        "Pragma": "no-cache",
        "Referer": "https://txzbqy.miit.gov.cn/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0.1; Nexus 5 Build/MMB29K) tuhuAndroid 5.24.6',
        'content-type': 'application/json',
        "sec-ch-ua": "\"Chromium\";v=\"110\", \"Not A(Brand\";v=\"24\", \"Microsoft Edge\";v=\"110\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\""
    }
    url = "https://txzbqy.miit.gov.cn/zbtb/opinion/captcha"
    urls = "https://txzbqy.miit.gov.cn/zbtb/gateway/gatewayPublicity/bidBulletinList"
    urlss = "https://txzbqy.miit.gov.cn/zbtb/gateway/gatewayPublicity/bidPublicityList"
    i = ["21", "22", "23", "11", "12"]


    for l in i:
        print(l)
        for num in range(1, 2):
            if l == "21" or l == "22" or l == "23":
                res = dowmload_zb1(headers, url, urls, l, num)
                parse(res, headers)
            else:
                res = dowmload_zb1(headers, url, urlss, l, num)
                parse(res, headers)

    for num in range(1, 2):
        download_zzb2(num, headers)