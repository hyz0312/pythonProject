class Spider_item(object):

    def __init__(self):

    #     # self.id = 0  # id，自动生成，不用给
    #     #self.create_time = ''

        self.fid = ""  # 招中标类型，[num]
        self.title = ""  # 标题
        self.source = ""  # 信息来源
        self.notice_time = ""  # r1
        self.special = ""  # platform_id_招标编号 / platform_id_每个详情页唯一标识
        self.platform_id = 5226

        self.content = ""  # 正文
        self.text = ""  # 关键字
        self.annex = "" # 附件链接，并以,分割多个

        self.region = ""  # 地区
        self.trade = ""  # 行业
        self.uid = 20  # 20
        self.local = ""  # ‘’
        self.sync = 0  # 0
