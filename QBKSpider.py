# -*- coding:utf-8 -*-
#dev:python2
import urllib2
import urllib
import re

class spider(object):
    def __init__(self,url):
        try:
            user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
            headers = { 'User-Agent' : user_agent }
            request = urllib2.Request(url,headers=headers)  #urllib2.Request()的功能是构造一个请求信息，返回的req就是一个构造好的请求
            response = urllib2.urlopen(request)    #urllib2.urlopen()的功能是发送刚刚构造好的请求req，并返回一个文件类的对象response，包括了所有的返回信息
            self.html = response.read()
            response.close()
            #print self.html
        except urllib2.URLError, e:
            if hasattr(e,'reason'):
                print e.reason
            if hasattr(e,'code'):
                print e.code
            print 'error.'
    def re_match(self):
        global x
        #'(?<=<div class="author.*?").*?(<img src=".*?\.JPEG").*?(alt=".*?">).*?(<div class="content">.*?</div>)'#此处有个陷阱，<img />标签。
        rex = r'(?<=<div class="author clearfix").*?<img src="(.*?)" alt="(.*?)"(?:</a>|/>|</span>).*?<div class="content">.*?<span>(.*?)</span>.*?</div>'
        pattern = re.compile(rex,re.S)
        items = re.findall(pattern,self.html)
        for i in items:
            #print i[0]
            img_name = './img_save/%s.jpg'%x
            try:
                urllib.urlretrieve(i[0], img_name)
            except:
                print 'bad url .'
            x += 1
            pattern_1 = re.compile(r'<br/>')
            rep_i = re.sub(pattern_1,'\n',i[2])
            print i[1]
            print rep_i
        print index




if __name__ == '__main__':
    #pageindex = raw_input('1,2,3..')
    x = 1
    index = 1
    for i in range(35):
        url = 'http://www.qiushibaike.com/hot/page/'+str(index)
        a = spider(url)
        a.re_match()
        index += 1

