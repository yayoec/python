# -*- coding: utf-8 -*-

import urllib
import urllib2
import logging
import simplejson

def encode_get_args(args):
    def _to_quoted_utf8(s):
        if not isinstance(s, basestring):
            s = str(s)
        if isinstance(s, unicode):
            s = s.encode('utf-8')
        return urllib.quote(s)
    return '&'.join([ '='.join([item[0], _to_quoted_utf8(item[1])]) for item in args.items()])

def encode_post_args(args):
    return simplejson.dumps(args)

def decode_response(body):
    data = simplejson.loads(body)
    return data

class RestRequest(object):
    url = ''
    debug = False
    request_timeout = 3 # seconds
    error_description_func = None

    def __init__(self, host=None, method=None, **kwargs):
        self.__dict__['_properties'] = {}
        if host:
            self._host = host
        self._method = method
        self._response = None
        self._curry = {}
        self._kwargs = kwargs

    def __setattr__(self, attr, value):
        if attr not in ['_properties', '_host', '_method', '_response', '_curry', '_user_id', '_client', '_kwargs']:
            if attr in self._curry:
                self._properties[attr] = self._curry[attr][1](value)
            else:
                self._properties[attr] = value
        else:
            self.__dict__[attr] = value

    def __getattr__(self, attr):
        if attr not in ['_properties', '_host', '_method', '_response', '_curry', '_user_id', '_client', '_kwargs']:
            value = self._properties.get(attr, None)
            if attr in self._curry:
                return self._curry[attr][0](value)
            else:
                return value
        else:
            return self.__dict__.get(attr, None)

    def get_url(self):
        if self.url.startswith('/'):
            url = self.url[1:]
        return '%s/%s'%(self._host, url)

    def fetch(self):
        raise NotImplemented

    def get_validated_args(self):
        return self._properties
    
    def _format_response(self, response, format='json'):

        try:
            body = response.read()
            if self.debug:
                print 'response :', body
            if format == 'json':
                self._response = decode_response(body)
            elif format == 'raw':
                self._response = {'ok': True, 'data': body, 'reason': ''}
            return self.data()
        except Exception, e:
            logging.error('rest %s request exception, exception: %s'%(self.get_url(), e))

    def data(self):
        if self._response:
            return self._response['data']

    def ok(self):
        if self._response:
            return self._response['ok']

    def reason(self):
        if self._response:
            reason = self._response['reason']
            if reason:
                if self.error_description_func:
                    try:
                        return self.error_description_func(reason)
                    except:
                        logging.error('rest %s get invalid error code, response: %s'%(self.get_url(), self._response))
                        return u'系统无法识别的错误。'
                else:
                    return reason
            return ''

    def reason_code(self):
        return self._response.get('reason', 0)


class RestGetRequest(RestRequest):

    def __init__(self, host=None, **kwargs):
        RestRequest.__init__(self, host=None, method='GET', **kwargs)

    def fetch(self, url=None, format='json', timeout=None):
        if not timeout:
            timeout = self.request_timeout
        if not url:
            url = self.get_url()
        if self.debug:
            print "request url ", self._method, ": ", url, self.get_validated_args()
        body = encode_get_args(self.get_validated_args())
        if body:
            url += '?%s' % body

        response = urllib2.urlopen(url, timeout=timeout)
        return self._format_response(response, format=format)

class RestPostRequest(RestRequest):

    def __init__(self, host=None, **kwargs):
        RestRequest.__init__(self, host=None, method='POST', **kwargs)

    def fetch(self, url=None, format='json', timeout=None):
        if not timeout:
            timeout = self.request_timeout
        if not url:
            url = self.get_url()
        if self.debug:
            print "request url ", self._method, ": ", url, self.get_validated_args()
        body = encode_post_args(self.get_validated_args())
        req = urllib2.Request(url, body)
        req.add_header('Content-Type', 'application/json')
        response = urllib2.urlopen(req, timeout=timeout)
        return self._format_response(response, format=format)
