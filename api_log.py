# coding=utf8
'''
Created on 2012-11-30
接口请求日志
@author: nic
'''

import os, fcntl, time, simplejson
from urllib2 import urlparse

class ApiDiskLog(object):
    '接口请求日志'
    def __init__(self, server_name, project_name, log_dir='/tmp', ignore_url=[], log_format='comma'):
        self.server_name = server_name
        self.project_name = project_name
        self.log_dir = log_dir
        self.ignore_url = ignore_url
        self.log_format = log_format
        
    def write(self, url, start_time, end_time, ok, reason):
        '''
        @param url: 这个url必须是完整的http请求地址如：  http://127.0.0.1:8080/xxx/?sdfa=fas
        @param ok: boolean -> True or False
        @param reason: 错误原因，字符串，不能包含英文逗号','
        '''
        process_time = int((end_time - start_time) * 1000) # 毫秒
        
        urlps = urlparse.urlparse(url)
        host = '%s%s' %(urlps.hostname, (':%s' %urlps.port) if urlps.port else '')
        url = urlps.path or '/'
        
        for iu in self.ignore_url:
            if url.startswith(iu):
                return
        ok = ok and 1 or 0 # and 'true' or 'false'
        if self.log_format == 'comma':
            msg = '%s,%s,%s,%s,%s,%s,%s,%s' %(self.server_name, self.project_name, host, url, process_time, ok, int(start_time), reason)
            
        elif self.log_format == 'json':
            msg = { 'server_name': self.server_name, 'project_name': self.project_name, 
                    'host': host,
                    'url': url, 'create_time': int(start_time), 'process_time': process_time,
                    'ok': ok, 'reason': reason}
            msg = simplejson.dumps(msg)
        self.write_log(msg)
        
    def write_log(self, msg):
        log_file_name = 'apilog_%s_%s.log' %(self.server_name.lower(), self.project_name.lower())
        abs_path = os.path.join(self.log_dir, log_file_name) 
        abs_dir = os.path.split(abs_path)[0]
        # 确保路径可写
        if not os.path.isdir(abs_dir):
            os.mkdir(abs_dir)

        # 写入消息的json字符串
        for i in range(10):
            try:
                f = open(abs_path, 'a')
                fcntl.lockf(f, fcntl.LOCK_EX)
                f.write('%s\n'%msg)
                fcntl.lockf(f, fcntl.LOCK_UN)
                f.close()
                break
            except:
                import traceback; traceback.print_exc()
                time.sleep(0.0001)
        
    