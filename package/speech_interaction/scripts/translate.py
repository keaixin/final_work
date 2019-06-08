#! /usr/bin/env python
# -*- coding: utf-8 -*-

import httplib
import md5
import urllib
import random
import json
import rospy
from std_msgs.msg import String

class translate():
    def __init__(self):
        self.sub_tuling_topic_name = rospy.get_param("sub_tuling_topic_name","/tuling_response")
        self.pub_translate_result = rospy.get_param("pub_translate_result","/tuling_translate_result")
        rospy.Subscriber(self.sub_tuling_topic_name, String, self.translatecallback)
        self.pub_result=rospy.Publisher(self.pub_translate_result,String, queue_size=1)
    def translatecallback(self, msg):

        appid = '20190525000301673'
        secretKey = 'VpuVs8uIEbH8obiDEgMW' 

        httpClient = None
        myurl = '/api/trans/vip/translate'
        q = str(msg.data)
        fromLang = 'zh'
        toLang = 'en'
        salt = random.randint(32768, 65536)

        sign = appid+q+str(salt)+secretKey
        m1 = md5.new()
        m1.update(sign)
        sign = m1.hexdigest()#做MD5得到32位小写的sign
        myurl = myurl+'?appid='+appid+'&q='+urllib.quote(q)+'&from='+fromLang+'&to='+toLang+'&salt='+str(salt)+'&sign='+sign

        try:
            httpClient = httplib.HTTPConnection('api.fanyi.baidu.com')
            httpClient.request('GET', myurl)

            #response是HTTPResponse对象
            response = httpClient.getresponse()
            res = response.read()
            res2 = json.loads(res)
            src = urllib.unquote(res2["trans_result"][0]["src"])
            print ("src: %s"%src)
            dst = str(res2["trans_result"][0]["dst"])
            print ("dst: %s"%dst)
            self.pub_result.publish(dst)

        except Exception, e:
            print e

        finally:
            if httpClient:
                httpClient.close()

if __name__ == '__main__':
    rospy.init_node('translate')
    trans = translate()
    rospy.spin()        