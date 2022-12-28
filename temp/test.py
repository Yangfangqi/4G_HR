import umqtt
import checkNet
import net


PROJECT_NAME = "HR100"
PROJECT_VERSION = "1.0"


print(net.csqQueryPoll())

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

print("success connect")

global mqtt_iot 
mqtt_iot=umqtt.MQTTClient("GID_EC800M@@@001", "mqtt-cn-zpr2zg1er01.mqtt.aliyuncs.com", port=1883, user="Signature|LTAI5tE84GMytUDjtdzpyPuS|mqtt-cn-zpr2zg1er01", password="GfCVKpPvjKTVumR6uO1lUCCxuhQ=", keepalive=0, ssl=False, ssl_params={},reconn=True,version=4)
a=mqtt_iot.connect(clean_session=True) 
print(a)
mqtt_iot.publish("EC800-TEST-001","hello", retain=False, qos=0)