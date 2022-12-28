import umqtt
import checkNet
import net
import app_fota
from misc import Power


#

PROJECT_NAME = "HR100"
PROJECT_VERSION = "1.0"

FILE_NAME = r'main.py'
DEF_URL = r'114.55.146.238:8000/{}'.format(FILE_NAME)
FILE_DIR_NAME = r'/usr/{}'.format(FILE_NAME)

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
    
print("enter in  old ")
fota = app_fota.new()
print('准备下载...')
fota.download(DEF_URL, FILE_DIR_NAME)
print('下载完成')
fota.set_update_flag()
print('重启升级')
Power.powerRestart()   # 重启模块




