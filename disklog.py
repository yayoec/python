# -*- coding: utf-8 -*-

import time
import os, sys
import logging
import fcntl
import simplejson

class DocTypeRequiredError(Exception):
    pass

class ReservedAttributeError(Exception):
    pass

class JsonDiskLogger():

    def __init__(self, log_dir, server_name, project_name, retry_count=3):
        self.log_dir = log_dir
        self.server_name = server_name
        self.project_name = project_name
        self.retry_count = retry_count

    def write_disklog(self, msg):
        if 'doc_type' not in msg:
            raise DocTypeRequiredError
        for reserved_word in ['server_name', 'project_name']:
            if reserved_word in msg:
                raise ReservedAttributeError

        msg['server_name'] = self.server_name
        msg['project_name'] = self.project_name
        if 'create_time' not in msg:
            msg['create_time'] = int(time.time())

        doc_type = msg['doc_type']
        log_file_name = '%s/%s_%s_%s.log'%(doc_type, doc_type.lower(), 
                                        self.server_name.lower(),
                                        self.project_name.lower())
        abs_path = os.path.join(self.log_dir, log_file_name)
        abs_dir = os.path.split(abs_path)[0]
        if not os.path.isdir(abs_dir):
            os.mkdir(abs_dir)

        for i in range(self.retry_count):
            try:
                f = open(abs_path, 'a')
                fcntl.lockf(f, fcntl.LOCK_EX)
                f.write('%s\n'%simplejson.dumps(msg))
                fcntl.lockf(f, fcntl.LOCK_UN)
                f.close()
                break
            except:
                import traceback; traceback.print_exc()
                time.sleep(0.0001)
    
class JsonDiskLoggerNew():
    """write everyday's log in seperate files
    """

    def __init__(self, log_dir, server_name, project_name, retry_count=3):
        self.log_dir = log_dir
        self.server_name = server_name
        self.project_name = project_name
        self.retry_count = retry_count

    def write_disklog(self, msg):
        if 'doc_type' not in msg:
            raise DocTypeRequiredError
        for reserved_word in ['server_name', 'project_name']:
            if reserved_word in msg:
                raise ReservedAttributeError

        msg['server_name'] = self.server_name
        msg['project_name'] = self.project_name
        if 'create_time' not in msg:
            msg['create_time'] = int(time.time())

        doc_type = msg['doc_type']
        log_file_name = '%s/%s_%s_%s_%s.log'%(doc_type, doc_type.lower(), 
                                        self.server_name.lower(),
                                        self.project_name.lower(),
                                        time.strftime('%Y%m%d'))
        abs_path = os.path.join(self.log_dir, log_file_name)
        self._write_msg(abs_path, msg)

    def _write_msg(self, abs_path, msg):
        abs_dir = os.path.split(abs_path)[0]
        
        if not os.path.isdir(abs_dir):
            os.mkdir(abs_dir)

        try:
            f = open(abs_path, 'a')
            f.write('%s\n'%simplejson.dumps(msg))
            f.close()
        except:
            import traceback; traceback.print_exc()
            logging.exception("save msg error ,msg:%s" % msg)

