import threading, queue, time, os, pickle, pymongo
from selenium import webdriver
import logging
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from huya.spiders.config import USER_PROFILE, HUYA_CONFIG

MONGODB_CONFIG = {
    'host': '127.0.0.1',
    'port': 27017,
    'db_name': 'huya',
    'user_name': None,
    'password': None
}

HOME_PAGE = 'https://www.huya.com/g'
BASE_URL_FOR_ROOM = 'https://www.huya.com/'

logging.basicConfig(level=logging.INFO,
                    # filename='./huya/log/in_room.log',
                    filename='../log/in_room.log',
                    datefmt='%Y/%m/%d %H:%M:%S',
                    format='%%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(module)s - %(message)s')

class conphantomjs:
    jiange = 0.00001  # 开启phantomjs间隔
    timeout = 20  # 设置phantomjs超时时间
    # path = "D:\python27\Scripts\phantomjs.exe"  ##phantomjs路径
    # service_args = ['--load-images=no', '--disk-cache=yes']  ##参数设置

    def __init__(self, name):
        self.logger = logging.getLogger(__name__)
        self.logger.info('Initialing...')
        huya_config = HUYA_CONFIG()
        self.huya_config = huya_config.get_huya_config()
        self.interval_time = self.huya_config['interval_time']  # 开启phantomjs间隔
        self.phantomjs_max = self.huya_config['phantomjs']  # 同时开启phantomjs个数
        self.phantomjs_timeout = self.huya_config['phantomjs_timeout']  # 设置phantomjs超时时间

        self.conn = pymongo.MongoClient(MONGODB_CONFIG['host'], MONGODB_CONFIG['port'])
        self.db = self.conn[MONGODB_CONFIG['db_name']]
        self.q_phantomjs = queue.Queue()  # 存放phantomjs进程队列

        user_profile = USER_PROFILE(name)
        self.user_info = user_profile.get_user_profile()
        self.user_name = self.user_info['user_name']
        self.user_pw = self.user_info['user_pw']
        self.msg = self.user_info['msg']

    def load_pickle(self, name):
        self.logger.info('loading pickle %s' % name)
        with open('../cookies/{user_name}.pkl'.format(user_name=self.user_name), 'rb')as fp:
            try:
                n = pickle.load(fp)
            except EOFError:
                return None

            for i in range(0, len(n)):
                if n[i]['name'] == name:
                    return n[i]['value']

    def set_cookies(self, browser):
        print('setting cookies, user name: %s' % self.user_name)
        self.logger.info('setting cookies, user name: %s' % self.user_name)
        try:
            browser.add_cookie({'name': 'Hm_lvt_51700b6c722f5bb4cf39906a596ea41f',
                                'value': self.load_pickle('Hm_lvt_51700b6c722f5bb4cf39906a596ea41f')})  #
            browser.add_cookie({'name': 'h_pr', 'value': '1'})  #
            browser.add_cookie({'name': 'udb_passdata', 'value': self.load_pickle('udb_passdata')})
            browser.add_cookie({'name': 'yyuid', 'value': self.load_pickle('yyuid')})  #
            browser.add_cookie({'name': '__yaoldyyuid', 'value': self.load_pickle('__yaoldyyuid')})  #
            browser.add_cookie({'name': 'username', 'value': self.load_pickle('username')})  #
            browser.add_cookie({'name': 'password', 'value': self.load_pickle('password')})  #
            browser.add_cookie({'name': 'udboauthtmptokensec', 'value': ''})
            browser.add_cookie({'name': 'osinfo', 'value': self.load_pickle('osinfo')})  #
            browser.add_cookie({'name': 'udb_l',
                                'value': self.load_pickle('osinfo')})
            browser.add_cookie({'name': 'udb_n',
                                'value': self.load_pickle('udb_n')})
            browser.add_cookie({'name': 'udb_c',
                                'value': self.load_pickle('udb_c')})
            browser.add_cookie({'name': 'udb_oar',
                                'value': self.load_pickle('udb_oar')})
            browser.add_cookie({'name': 'Hm_lpvt_51700b6c722f5bb4cf39906a596ea41f',
                                'value': self.load_pickle('Hm_lpvt_51700b6c722f5bb4cf39906a596ea41f')})  #
            browser.add_cookie({'name': '_yasids', 'value': self.load_pickle('_yasids')})  #
            browser.add_cookie({'name': 'udboauthtmptoken',
                                'value': self.load_pickle('udboauthtmptoken')})
            browser.add_cookie({'name': 'PHPSESSID', 'value': self.load_pickle('PHPSESSID')})  #
            browser.add_cookie({'name': '__yamid_tt1', 'value': self.load_pickle('__yamid_tt1')})  #
            browser.add_cookie({'name': '__yamid_new', 'value': self.load_pickle('__yamid_new')})  #
            browser.add_cookie({'name': '__yasmid', 'value': self.load_pickle('__yasmid')})  #
            # print('__yasmid:' + self.load_pickle('__yasmid'))

            # browser.add_cookie({'name': 'Hm_lvt_51700b6c722f5bb4cf39906a596ea41f', 'value': '1531028179'})  #
            # browser.add_cookie({'name': 'h_pr', 'value': '1'})  #
            # browser.add_cookie({'name': 'udb_passdata', 'value': '1'})
            # browser.add_cookie({'name': 'yyuid', 'value': '2232479408'})  #
            # browser.add_cookie({'name': '__yaoldyyuid', 'value': '2232479408'})  #
            # browser.add_cookie({'name': 'username', 'value': '2232684128yy'})  #
            # browser.add_cookie({'name': 'password', 'value': 'A9634A21DF0E39C5A66CBB439F50083824BDDAA8'})  #
            # browser.add_cookie({'name': 'udboauthtmptokensec', 'value': ''})
            # browser.add_cookie({'name': 'osinfo', 'value': '6FAF261D7FC94FC7846263C27AEF48DAAFC48AB5'})  #
            # browser.add_cookie({'name': 'udb_l',
            #                     'value': 'DAAyMjMyNjg0MTI4eXkjo0FbCXQAutSAfXqOdpd2YWU2sau7G4fvxTnMlsAYzMX0VxMwDmQrujgKEH7K7kS42BGtVrXEN1TWjl3ukLgL3FYIRJr-ofsGfQj0Bb_4oTp8aHewX8c6x3eSLfMu5soIYKzyoI3Bx8e-AmbVfHhiOLLAU8R_cQvy7MYAAAAAAwAAAAAAAAANADExMy42NS43MC4xNDEEADUyMTY='})
            # browser.add_cookie({'name': 'udb_n',
            #                     'value': '4c51af117380196a141bd2ee9959ee6050666e9c0ce89c244c4b84f935c4f49db47605b825e9dc3dd6e345aee5bb4e34'})
            # browser.add_cookie({'name': 'udb_c',
            #                     'value': 'AMCBJFBqAAJgAOHw8IXq2Q9YoW2ezq7V93WDV15YkmTzW-Pub9MCCrwFbpzPhRs6Xvu9x4324wWN0xSy_ikPetIY-Bik78kkOcgHKG5jZvksVQ37k904NW5JJoHeu5XIjpJ94ULjb__EWg=='})
            # browser.add_cookie({'name': 'udb_oar',
            #                     'value': '579498B14DC3339CFD8499CB2976D2D704734D2A310E4CF12EA7C39E26D08672D2D3CFCB1FAAF4851FA52491CDEE6E5A7D10066793AE039EAD20CE8653B9135791423C07C1092830196E9363A35CA987CDD0BD3F0FB95AA85D75F0A6F2B7BC3CB005E30F97352189BFCCE51697069F79EBBC4D2A32DF700621710E5D5879322D6AB2A5169EF7A1667750515AE5AD3E3CD19DB56D84823CD2CE6A4FBF5E722162D2D8B2B0C4B25546E86779EFAE3328A8ECE706E0729E71F21EA6022A6791EFDA3E6198378AC1E739A61C3686C0CDED3064BA5BB85C6087539F60465AF76497DF0499DD86D035678FC671116A71BDC5F6EBA3846933BB647E614EE1F8131B1AAF6F039D51C7092CFC1E0B496A2856B286DEEAA3FF271C8769D2DA84F3632160C4B896F232EC809FB959349A0263EB2F016A3C42089C474D9E51A8345788833FC5'})
            # browser.add_cookie({'name': 'Hm_lpvt_51700b6c722f5bb4cf39906a596ea41f', 'value': '1531028323'})  #
            # browser.add_cookie({'name': '_yasids', 'value': '__rootsid%3DC80E111C01000001A74710001F6A1A95'})  #
            # browser.add_cookie({'name': 'udboauthtmptoken',
            #                     'value': '17da3796d54dbcd5604e5f9d6b967f579d99d77f19cbf230a035cafba28975ff24705436408366aec1984877140969f7c3a272d5f1119a2db5b7dcee611777b3'})
            # browser.add_cookie({'name': 'PHPSESSID', 'value': 'ir0o747nlljg41gmqjg8j35tu3'})  #
            # browser.add_cookie({'name': '__yamid_tt1', 'value': '0.5740688303946497'})  #
            # browser.add_cookie({'name': '__yamid_new', 'value': 'C80E111ABEF000015D7E1980D7D01BCD'})  #
            # browser.add_cookie({'name': '__yasmid', 'value': '0.5740688303946497'})  #
            # browser.add_cookie({'name': 'h_unt', 'value': load_cookie(n, 'h_unt')})  # no need
        except EOFError:  # 捕获异常EOFError 后返回None
            print('EOFError')
            self.logger.error('Fail to get cookies', exc_info=True)

    # def save_cookies(self):
    #     chromedriver = "C:\Program Files\Google\Chrome\Application\chromedriver.exe"
    #     os.environ["webdriver.chrome.driver"] = chromedriver
    #     option = webdriver.ChromeOptions()
        # driver = webdriver.Chrome(chromedriver, chrome_options=option)
        # driver.maximize_window()
        # driver.get(HOME_PAGE)
        # self.login(driver)
        # self.logger.info('saving cookies, user name: %s' % self.user_name)
        # print(driver.get_cookies())
        # pickle.dump(driver.get_cookies(), open("../cookies/{user_name}.pkl".format(user_name=self.user_name), "wb"))

    def access(self):
        chromedriver = "C:\Program Files\Google\Chrome\Application\chromedriver.exe"
        os.environ["webdriver.chrome.driver"] = chromedriver
        option = webdriver.ChromeOptions()
        driver = webdriver.Chrome(chromedriver, chrome_options=option)

        # driver = webdriver.PhantomJS()  # service_args=service_args # service_args.append('--load-image=no')
        # driver.set_page_load_timeout(self.phantomjs_timeout)  ##设置超时时间
        # driver.implicitly_wait(self.phantomjs_timeout)  # 设置超时时间

        driver.maximize_window()
        driver.get(HOME_PAGE)
        self._login(driver)
        self.saveCookies(driver)

    def _login(self, driver):
        self.logger.info('logging, user name: %s' % self.user_name)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'nav-login'))).click()
        WebDriverWait(driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//*[@id='udbsdk_frm_normal']")))
        time.sleep(0.5)
        ele = driver.find_element_by_xpath("//*[@id='m_commonLogin']/div[1]/span/input")
        ele.send_keys(self.user_name)
        ele = driver.find_element_by_xpath("//*[@id='m_commonLogin']/div[2]/span/input")
        ele.send_keys(self.user_pw)
        time.sleep(0.5)
        driver.find_element_by_xpath("//*[@id='m_commonLogin']/div[5]/a[1]").click()
        time.sleep(1)

    def saveCookies(self, driver):
        self.logger.info('saving cookies, user name: %s' % self.user_name)
        print(driver.get_cookies())
        pickle.dump(driver.get_cookies(), open("../cookies/{user_name}.pkl".format(user_name=self.user_name), "wb"))

    def open_url_with_cookies(self, driver, url):
        self.logger.info('opening url: %s' % url)
        driver.maximize_window()
        driver.get(url)
        yy_user_name = self.load_pickle('username')
        print('user name get from cookies: ' + yy_user_name)
        yy_user_name_get_from_web = ''
        print('yy user name get from web: ' + driver.find_element_by_xpath("//span[@id='login-username']").text)
        try:
            yy_user_name_get_from_web = driver.find_element_by_xpath("//span[@id='login-username']").text
        except Exception:
            print("issue_1")
        finally:
            if yy_user_name_get_from_web != yy_user_name:
                self.set_cookies(driver)
                time.sleep(0.3)
                driver.refresh()
            else:
                print('still online, no need to set cookies')

    def getbody(self, url):
        """利用phantomjs获取网站源码以及url"""
        d = self.q_phantomjs.get()
        print('room: ' + url)
        print('driver id: ' + str(d))
        try:
            if os.path.exists('../cookies/{user_name}.pkl'.format(user_name=self.user_name)):
                self.logger.info('cookie found...')
                self.open_url_with_cookies(d, url)
            time.sleep(0.3)

        except Exception:
            print("163 Phantomjs Open url Error")
            self.logger.info("Phantomjs Open url Error")
        self.send_msg(d, self.msg)
        self.q_phantomjs.put(d)

    def open_phantomjs(self):
        """多线程开启phantomjs进程"""
        def open_threading():
            # service_args = []
            # service_args.append('--disk-cache=yes')
            # service_args.append('--ignore-ssl-errors=true')
            # d = webdriver.PhantomJS(service_args=service_args)  # service_args=conphantomjs.service_args
            # d = webdriver.PhantomJS() # service_args=service_args # service_args.append('--load-image=no')
            # d.set_page_load_timeout(self.phantomjs_timeout)  ##设置超时时间
            # d.implicitly_wait(self.phantomjs_timeout)  # 设置超时时间

            chromedriver = "C:\Program Files\Google\Chrome\Application\chromedriver.exe"
            os.environ["webdriver.chrome.driver"] = chromedriver
            option = webdriver.ChromeOptions()
            d = webdriver.Chrome(chromedriver, chrome_options=option)
            d.maximize_window()
            self.q_phantomjs.put(d)  # 将phantomjs进程存入队列

        th = []
        for i in range(int(self.phantomjs_max)):
            t = threading.Thread(target=open_threading)
            th.append(t)
        for i in th:
            i.start()
            time.sleep(float(self.interval_time)) # conphantomjs.jiange)  # 设置开启的时间间隔
        for i in th:
            i.join()

    def close_phantomjs(self):
        """多线程关闭phantomjs对象"""
        th = []

        def close_threading():
            d = self.q_phantomjs.get()
            d.quit()

        for i in range(self.q_phantomjs.qsize()):
            t = threading.Thread(target=close_threading)
            th.append(t)
        for i in th:
            i.start()
        for i in th:
            i.join()

    @staticmethod
    def send_msg(driver, msg):
        msg_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='pub_msg_input']")))
        #     msg_input = self.driver.find_element_by_xpath("//*[@id='pub_msg_input']")
        msg_input.send_keys(msg)
        # time.sleep(2)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, 'msg_send_bt'))).click()
        # d.find_element_by_xpath("//*[@id='msg_send_bt']").click()
        # self.driver.find_element_by_id('msg_send_bt').click()
        time.sleep(0.5)
        print('Message 1 sent!')

    def main(self):
        # 1. check cookies exist or not. if not, give cookies
        if not os.path.exists('../cookies/{user_name}.pkl'.format(user_name=self.user_name)):
            self.access()

        # 2. run open_phantomjs, create the process of phantomjs
        self.open_phantomjs()
        print("phantomjs num is ", self.q_phantomjs.qsize())

        urls = []
        count = self.db['rooms'].count()
        if count == 0:
            print("no url...")
            self.logger.info("no urls...")
            return

        rooms = self.db['rooms'].find({})
        no = 0
        for r in rooms:
            no += 1
            if no == 10:
                urls.append(r['room'])
                no = 0
            th = []
            for i in urls:
                i = BASE_URL_FOR_ROOM + i
                t = threading.Thread(target=self.getbody, args=(i,))
                th.append(t)
            for i in th:
                i.start()
            for i in th:
                i.join()
            urls = []

        self.close_phantomjs()
        print("phantomjs num is ", self.q_phantomjs.qsize())


if __name__ == "__main__":
    cur = conphantomjs('13250219510')
    cur.main()

    '''
        用法：
        1.实例化类
        2.运行open_phantomjs 开启phantomjs进程
        3.运行getbody函数，传入url
        4.运行close_phantomjs 关闭phantomjs进程
        '''
    # cur = conphantomjs()
    # conphantomjs.phantomjs_max = 10
    # cur.open_phantomjs()
    # print("phantomjs num is ", cur.q_phantomjs.qsize())
    #
    # urls = []
    # count = cur.db['rooms'].count()
    # for e in range(0, count // 10 + 1):
    #     print('---------------%d' % e)
    #     res = cur.db['rooms'].find({'_id': {'$gte': 10 * e, '$lt': 10 * (e + 1)}})
    #     for k in res:
    #         urls.append(k['room'])
    #     print(urls)
    #     print('---------------')
    # urls = ["http://www.baidu.com"] * 50
    #     th = []
    #     for i in urls:
    #         i = 'https://www.huya.com/' + i
    #         t = threading.Thread(target=cur.getbody, args=(i,))
    #         th.append(t)
    #     for i in th:
    #         i.start()
    #     for i in th:
    #         i.join()
    #     urls = []
    #
    # cur.close_phantomjs()
    # print("phantomjs num is ", cur.q_phantomjs.qsize())

    # url_list = ["http://www.baidu.com"] * 50
    # th = []
    # for i in url_list:
    #     t = threading.Thread(target=cur.getbody, args=(i,))
    #     th.append(t)
    # for i in th:
    #     i.start()
    # for i in th:
    #     i.join()
    # cur.close_phantomjs()
    # print("phantomjs num is ", cur.q_phantomjs.qsize())

    # https://lgn.yy.com/lgn/oauth/authorize.do?oauth_token=b7e2debe51603ff22075819a5ca17e828810b7de69530da6d59a35a5cb78b5139b85cd08af12b31ec50608b67fa24628&denyCallbackURL=&regCallbackURL=https://www.huya.com/udb_web/udbport2.php?do=callback&UIStyle=xelogin&rdm=0.14674353878945112
