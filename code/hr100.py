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
@file      :dtu.py
@author    :elian.wang@quectel.com
@brief     :dtu main function
@version   :0.1
@date      :2022-05-18 09:12:37
@copyright :Copyright (c) 2022
"""

import sim, dataCall, net, modem, utime, _thread
import urandom
import checkNet
import utime
from misc import Power
from machine import Pin  # 导入Pin模块
from usr.mqttIot import MqttIot
from usr.logging import getLogger
from usr.common import Singleton
import umqtt

#引入setings实例对象
from usr.settings import settings
#引入变量
from usr.settings import PROJECT_NAME, PROJECT_VERSION, DEVICE_FIRMWARE_NAME, DEVICE_FIRMWARE_VERSION

from usr.sensor import Sensor


#引脚输出低电平
LED_B = Pin(Pin.GPIO32, Pin.OUT, Pin.PULL_DISABLE, 0)  # GPIO32配置成输出模式，默认输出0
LED_G = Pin(Pin.GPIO33, Pin.OUT, Pin.PULL_DISABLE, 0)  # GPIO33配置成输出模式，默认输出0

#获取log对象
log = getLogger(__name__)

#全局变量 mqtt_iot
global mqtt_iot


def cloud_init(data):
    protocol = data.get("protocol").lower() #将键值转换为小写
    if protocol == "mqtt":
        global mqtt_iot  #声明全局变量以在函数内部修改全局变量值
        #创建mqtt对象
        mqtt_iot = MqttIot(data.get("url", None),
                            int(data.get("qos", 0)),
                            int(data.get("port", 1883)),
                            int(data.get("cleanSession", 1)),
                            data.get("clientID"),
                            data.get("username"),
                            data.get("passwd"),
                            int(data.get("keep_alive", 0)),
                            data.get("publish"),
                            data.get("subscribe")
                            )

        mqtt_iot.init(enforce=True)
        return True
        
    else:
        log.error("no mqtt conf!")
        return False


def run():
    LED_G.write(1)
    # log.info("PROJECT_NAME: %s, PROJECT_VERSION: %s" % (PROJECT_NAME, PROJECT_VERSION))
    # log.info("DEVICE_FIRMWARE_NAME: %s, DEVICE_FIRMWARE_VERSION: %s" % (DEVICE_FIRMWARE_NAME, DEVICE_FIRMWARE_VERSION))

    #创建checkNeck对象
    checknet = checkNet.CheckNetwork(PROJECT_NAME, PROJECT_VERSION)
    #开机打印信息：打印用户项目名称，用户项目版本号
    checknet.poweron_print_once()

    print("enter in new ")

   
    #等待网络就绪
    try:
        checknet.wait_network_connected()
    except BaseException:
        print('Not Net, Resatrting...')
        utime.sleep_ms(200)
        #模块重启
        Power.powerRestart()


    #mqtt连接、订阅初始化
    cloud_init(settings.current_settings.get("conf"))
    global mqtt_iot
    #传感器初始化
    sensor = Sensor()

    while True:
        #获取传感器检测值
        pressure, temperature = sensor.read_press_temp()
        #发布传感器采集数据
        mqtt_iot.post_sensor_data(pressure, temperature)
        utime.sleep(settings.current_settings.get("collectCycle"))


#运行本函数
if __name__ == "__main__":
    run()

