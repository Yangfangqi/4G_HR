# Copyright (c) Quectel Wireless Solution, Co., Ltd.All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@file      :mqttIot.py
@author    :elian.wang@quectel.com
@brief     :universal mqtt iot inferface
@version   :0.1
@date      :2022-05-18 13:28:53
@copyright :Copyright (c) 2022
"""

import ujson
import utime
import _thread
from umqtt import MQTTClient
from usr.logging import getLogger
from usr.settings import settings


log = getLogger(__name__)

class MqttIot():

    def __init__(self, server, qos, port, clean_session, client_id, username, password, life_time=30, pub_topic=None, sub_topic=None):

        self.conn_type = "mqtt"
        self.__server = server
        self.__qos = qos
        self.__port = port
        self.__mqtt = None
        self.__clean_session = clean_session
        self.__life_time = life_time
        self.__client_id = client_id
        self.__username = username
        self.__password = password

        if pub_topic == None:
            self.pub_topic_dict = {"0": "/python/mqtt/pub"}
        else:
            self.pub_topic_dict = pub_topic
        if sub_topic == None:
            self.sub_topic_dict = {"0": "/python/mqtt/sub"}
        else:
            self.sub_topic_dict = sub_topic

    #订阅主题
    def __subscribe_topic(self):
        #把键值对内容id，topic分别遍历 items将字典变为键值对数组 
        for id, usr_sub_topic in self.sub_topic_dict.items(): 
             self.__mqtt.subscribe(usr_sub_topic, qos=0) 
             

    #订阅回调函数
    def __sub_cb(self, topic, data):
        #解析utf-8格式topic并返回字符串
        topic = topic.decode()
        #解析json格式data并返回字符串
        try:
            data = ujson.loads(data)
        except:
            pass
        log.info("topic: %s, data: %s" % (topic, data))
        '''
        #判断字符串是否以/post_reply为结尾
        if topic.endswith("/post_reply"):
            pass
        #判断字符串是否以/property/set为结尾  #？处理
        elif topic.endswith("/property/set"):
            if data["method"] == "thing.service.property.set":
                # if "Pressure" in data["params"]:
                #     pressure = data["params"].get("Pressure")
                #     log.info("set Pressure : %s" % pressure)
                # if "Temperature" in data["params"]:
                #     temperature = data["params"].get("Temperature")
                #     log.info("set Temperature : %s" % temperature)
                if "Interval" in data["params"]:
                    interval = data["params"].get("Interval")
                    log.info("set Interval : %s" % interval)
                    settings.current_settings["collectCycle"] = interval
                  
                    
        #判断字符串是否以/ota/device/upgrade/为开始  #？处理
        elif topic.startswith("/ota/device/upgrade/"):
            pass
            # print("subscribe /ota/device/upgrade/")
            # self.__put_post_res(data["id"], True if int(data["code"]) == 1000 else False)
            # if int(data["code"]) == 1000:
            #     if data.get("data"):
            #         self.__ota.set_ota_info(data["data"])
            #         self.notifyObservers(self, *("object_model", [("ota_status", (data["data"]["module"], 1, data["data"]["version"]))]))
            #         self.notifyObservers(self, *("ota_plain", [("ota_cfg", data["data"])]))
        
        else:
            log.warning("not match topic")
        ''' 
    
    def __listen(self):
        while True:
            #阻塞等待服务器响应
            self.__mqtt.wait_msg()
            #延时
            utime.sleep_ms(100)

    def __start_listen(self):
        #创建新线程，接收执行函数
        _thread.start_new_thread(self.__listen, ())

    #mqtt 初始化函数：创建、连接、订阅
    def init(self, enforce=False):

        log.debug("[init start] enforce: %s" % enforce)
        if enforce is False and self.__mqtt is not None:
            #输出服务器连接状态
            log.debug("self.get_status(): %s" % self.get_status())
            #如果未连接成功则退出初始化函数
            if self.get_status():
                return True

        #断开与服务器连接
        if self.__mqtt is not None:
            self.close()
        
        #打印信息
        log.debug("__server: %s" % self.__server)
        log.debug("__port: %s" % self.__port)
        log.debug("__client_id: %s" % self.__client_id) 
        log.debug("__username: %s" % self.__username) 
        log.debug("__password: %s" % self.__password)
              
        #构建MQTT连接对象   
        self.__mqtt = MQTTClient(client_id=self.__client_id, server=self.__server, port=self.__port,
                              user=self.__username, password=self.__password, keepalive=self.__life_time, ssl=False)

     
                              
        #与服务器建立连接
        try:
            self.__mqtt.connect(clean_session=self.__clean_session)
        #如果连接有异常则输出异常
        except Exception as e: 
            log.error("mqtt connect error: %s" % e)
         
        #连接没有异常则创建订阅与监听
        else:
            #设置订阅回调函数
            self.__mqtt.set_callback(self.__sub_cb)
            #创建订阅
            self.__subscribe_topic()
            log.debug("mqtt n_subscribe_topic")
            #设置监听
            self.__start_listen()
            log.debug("mqtt start.")
        
        #获取mqtt连额吉状态
        log.debug("self.get_status(): %s" % self.get_status())
        if self.get_status():
            return True
        else:
            return False

    #与服务器断开连接
    def close(self):
        self.__mqtt.disconnect()


    #获取mqtt连接状态 1：连接中 0：连接成功 2：服务器关闭 -1：连接异常
    def get_status(self):
        try:
            return True if self.__mqtt.get_mqttsta() == 0 else False
        except:
            return False
    
    #发布消息
    def through_post_data(self, data, topic_id):
        #获取pub_topic_dict对应的topic_id的键值作为主题，并对应主题发布消息
        try:
            self.__mqtt.publish(self.pub_topic_dict[topic_id], data, self.__qos)
        except Exception:
            log.error("mqtt publish topic %s failed. data: %s" % (self.pub_topic_dict[topic_id], data))
            return False
        else:
            return True

    #发布传感器检测值
    def post_sensor_data(self, press, temp):
        try:
            sensor_data = {"params":{"Pressure":press,"Temperature":temp}}
            log.info(sensor_data)
            log.info(type(sensor_data)) #输出sensor_data变量类型
            data = ujson.dumps(sensor_data)#将字典类型sensor_data数据转化为字符串
            log.info(data)#输出字符串data
            log.info(type(data))#输出data类型            
            self.__mqtt.publish(self.pub_topic_dict["0"], data, self.__qos)#根据键值“0”对应主题发布数据data
        except Exception:
            log.error("mqtt publish topic %s failed. data: %s" % (self.pub_topic_dict["1"], data))
            return False
        else:
            return True

    def ota_request(self):
        pass

    def ota_action(self, action, module=None):
        pass
    
    def device_report(self):
        pass
