from faker import Faker

from .Utils import json_util, trans_data_to_url_util, time_stamp_util, get_now_time_util, to_encrypt_util, \
    http_client_util, string_coding_util, get_cookies_util, logger_util, get_ip_by_url_util, send_robot_msg_util, \
    send_mail_util, xml_to_dict_util, random_string_util, telnet_util, format_quot_str_util, dict_to_xml_util


class Tool(object):
    def __init__(self, faker_lang='zh_CN'):
        self.faker_data = Faker(faker_lang)  # 随机假数据
        self.ding_talk_token = ''  # 钉钉机器人token
        self.ding_talk_sign_key = ''  # 钉钉机器人签名密钥
        self.feishu_token = ''  # 飞书机器人token
        self.feishu_sign_key = ''  # 飞书机器人签名密钥
        self.qy_wechat_token = ''  # 企业微信机器人token
        self.mail_from_user = ''  # 邮件发送者账号
        self.mail_from_user_pwd = ''  # 邮件发送者密码
        self.mail_from_user_host = ''  # 邮件发送者host

    # 记录日志
    @staticmethod
    def logger(msg):
        logger_util(msg)

    # 获取cookies
    @staticmethod
    def get_cookies(url, data, method='GET', headers=None):
        return get_cookies_util(url, data, method, headers)

    # url编码
    @staticmethod
    def url_encode(url):
        return string_coding_util(url, 'url_encode')

    # url解码
    @staticmethod
    def url_decode(url):
        return string_coding_util(url, 'url_decode')

    # base64编码
    @staticmethod
    def base_64_encode(pre_str):
        return string_coding_util(pre_str, 'base_64_encode')

    # 解析读取json
    @staticmethod
    def json_loads(json_str):
        return json_util(json_str, 'json_load', indent=None)

    # 转成json
    @staticmethod
    def json_dumps(dict_str, **kwargs):
        return json_util(dict_str, 'json_dump', **kwargs)

    # 将参数转成链接（针对于get请求）
    @staticmethod
    def trans_data_to_url(url, data):
        return trans_data_to_url_util(url, data)

    # 获取当前时间戳
    @staticmethod
    def time_stamp(time_stamp='s'):
        return time_stamp_util(time_stamp)

    @staticmethod
    def time_stamp_to_date(time_stamp, date_type='-'):
        return get_now_time_util(date_type, time_stamp)

    @staticmethod
    def date_to_time_stamp(time_stamp, date_type='-'):
        return get_now_time_util(date_type, time_stamp, True)

    # 获取当前的时间
    @staticmethod
    def get_now_time(date_type='-'):
        return get_now_time_util(date_type, 'now')

    # sha256加密
    @staticmethod
    def to_sha_256(pre_str):
        return to_encrypt_util(pre_str, 'sha_256')

    # md5加密
    @staticmethod
    def to_md5(pre_str, salt=''):
        return to_encrypt_util(pre_str, 'md5', sign_key=salt)

    # hmac256加密
    @staticmethod
    def to_hmac_256(pre_str, sign_key):
        return to_encrypt_util(pre_str, 'hmac_256', sign_key)

    # 随机UA信息
    def random_ua(self, b_type=''):
        if b_type == 'chrome':
            return self.faker_data.chrome()
        elif b_type == 'firefox':
            return self.faker_data.firefox()
        elif b_type == 'ie':
            return self.faker_data.internet_explorer()
        elif b_type == 'opera':
            return self.faker_data.opera()
        elif b_type == 'safari':
            return self.faker_data.safari()
        else:
            return self.faker_data.user_agent()

    # 随机位数数字
    def random_number(self, n):
        return str(self.faker_data.random_number(n)).zfill(n)

    # 随机手机号
    def random_phone(self):
        return str(self.faker_data.phone_number())

    # 随机身份证号
    def random_ssn(self):
        return str(self.faker_data.ssn())

    # 随机姓名
    def random_name(self):
        return self.faker_data.name()

    # 随机位数字符串
    @staticmethod
    def random_string(n):
        return random_string_util(n)

    # http请求
    @staticmethod
    def http_client(url, method='GET', data=None, **kwargs):
        return http_client_util(url, method, data, **kwargs)

    # 通过链接获取ip
    @staticmethod
    def get_ip_by_url(url):
        return get_ip_by_url_util(url)

    # 发送钉钉机器人消息
    def send_ding_talk_msg(self, msg, at_all=None):
        if at_all is None:
            at_all = []
        send_robot_msg_util(msg, 'dingding', sign_key=self.ding_talk_sign_key,
                            token=self.ding_talk_token, at_all=at_all)

    # 发送企业微信机器人消息
    def send_qy_wechat_msg(self, msg, at_all=None):
        if at_all is None:
            at_all = []
        send_robot_msg_util(msg, 'qy_wechat', token=self.qy_wechat_token, at_all=at_all)

    # 发送飞书机器人消息
    def send_feishu_msg(self, msg, at_all=None):
        if at_all is None:
            at_all = []
        send_robot_msg_util(msg, 'feishu', sign_key=self.feishu_sign_key,
                            token=self.feishu_token, at_all=at_all)

    # 发送邮件消息
    def send_mail_msg(self, to_user, title, content):
        send_mail_util(self.mail_from_user, self.mail_from_user_pwd, self.mail_from_user_host, to_user, title, content)

    # 将xml转成字典
    @staticmethod
    def xml_to_dict(p_xml):
        return xml_to_dict_util(p_xml)

    @staticmethod
    def dict_to_xml(data, cdata=False):
        return dict_to_xml_util(data, cdata)

    # ================dubbo接口相关==========================
    @staticmethod
    def dubbo_args(*args):
        return str(','.join([format_quot_str_util(i, double_quot=True) for i in args]))

    @staticmethod
    def invoke_dubbo(host, port, service, method, args):
        final_args = (f'({args})', '()')[args is None]
        command_str = f'invoke {service}.{method}{final_args}'
        return telnet_util(host, port, command_str, 'dubbo>'), command_str
