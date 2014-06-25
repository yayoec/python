#!/usr/bin/python  
#coding=utf-8
#author Joe
#采集脚本, 模拟登录, 模拟mysql长连接 
import time, socket
import traceback
import urllib, urllib2  
import cookielib
import MySQLdb
import re

socket.setdefaulttimeout(65)

cookiefile = "cookiefile"
cookieJar = cookielib.MozillaCookieJar(cookiefile)
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookieJar));
opener.addheaders.append(('Accept-Language', 'zh-CN,zh;q=0.8,en;q=0.6,th;q=0.4,zh-TW;q=0.2'))
opener.addheaders.append(('Accept', '*/*'))
opener.addheaders.append(('User-Agent', 'Mozilla/5.0 (compatible; MISE 9.0; Windows NT 6.1); Trident/5.0'))
opener.addheaders.append(('Connection', 'Keep-Alive'))

class mysql:
    #模拟持久连接
    def __init__ (self,  
                  host   = '',  
                  user   = '',  
                  passwd = '',  
                  db     = '',  
                  port   = 3306,  
                  charset= 'utf8'  
                  ):  
        self.host   = host  
        self.user   = user  
        self.passwd = passwd  
        self.db     = db  
        self.port   = port  
        self.charset= charset  
        self.conn   = None  
        self._conn()  
  
    def _conn (self):  
        try:  
            self.conn = MySQLdb.Connection(self.host, self.user, self.passwd, self.db, self.port , self.charset)  
            return True  
        except :  
            return False  
  
    def _reConn (self,num = 28800,stime = 15): #重试连接总次数为1天,这里根据实际情况自己设置,如果服务器宕机1天都没发现就......  
        _number = 0  
        _status = True  
        while _status and _number <= num:  
            try:
                self.conn.ping()       #cping 校验连接是否异常  
                _status = False  
            except Exception, e:
                if self._conn()==True: #重新连接,成功退出  
                    _status = False  
                    break  
                _number +=1  
                time.sleep(stime)      #连接不成功,休眠3秒钟,继续循环，知道成功或重试次数结束  
  
    def select (self, sql = '', fetchOne=False):
        try:
            self._reConn()
            self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
            self.cursor.execute (sql)
            result = self.cursor.fetchone() if fetchOne else self.cursor.fetchall() 
            self.cursor.close ()
            return result
        except Exception, e:
            print '-select error-->', str(e) 
            #print "Error %d: %s" % (e.args[0], e.args[1])  
            return False  
  
    def select_limit (self, sql ='',offset = 0, length = 20):  
        sql = '%s limit %d , %d ;' % (sql, offset, length)  
        return self.select(sql)
  
    def query (self, sql = ''):
        try:  
            self._reConn()  
            self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)  
            self.cursor.execute ("set names utf8") #utf8 字符集  
            result = self.cursor.execute (sql)  
            self.conn.commit()  
            self.cursor.close ()  
            return (True,result)  
        except Exception, e:
            print 'e-->', str(e)
            return False  
  
    def close (self):  
        self.conn.close()

def get(url):
    req = urllib2.Request(url)
    #enable cookie
    cookieJar.load()
    response = opener.open(req)  
    cookieJar.save()
    print '-----get------->'
    return response.read()
    
def post(url, data):  
    req = urllib2.Request(url)  
    data = urllib.urlencode(data)
    #enable cookie
    cookieJar.load()
    response = opener.open(req, data)
    cookieJar.save()
    print '---post----'
    return response.read()
    #print response.read().decode('GBK')
    
loginurl = 'xxx'
logindata = {'xxx':'xxx', 'xxx': 'xxx'}
xxReg = r'(?<=<div align="center">)(\d+,)?\d+\.\d+(?=<\/div>)'

def trimComma(s):
    return ''.join(s.split(','))

def main():
    dbhost = '192.168.88.1'; dbuser = 'test'; dbpass = 'test'; dbname = 'test'
    my = mysql(dbhost, dbuser, dbpass, dbname)
    while True:
        res = ''
        if not cookieJar:
            post(loginurl, logindata)
            res = get(gatherurl)
        else:
            for key, cookie in enumerate(cookieJar):
                if cookie.domain == '.xxx' and cookie.name == 'sid':
                    res = get(gatherurl)
                    if res.find('请重新登入') > -1:
                        post(loginurl, logindata)
                        res = get(gatherurl)
        tbody = re.findall(tbodyReg, res)
        tr = re.findall(trReg, tbody[0])
        lentr = len(tr)
        for i in range(lentr):
            line = re.sub(r'<td [^>]*?>|\s|<!--[^>]*?-->|<span[^>]*?>', '', tr[i]).split('</td>')
            [xx, xx, xx, xxx, xx, tmp1, tmp2, tmp3] = map(trimComma, line)
        time.sleep(60)

if __name__ == '__main__':  
    main()
