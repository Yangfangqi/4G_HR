import app_fota
from misc import Power

FILE_NAME = r'sensor.py'
DEF_URL = r'192.168.0.143:8000/{}'.format(FILE_NAME)
FILE_DIR_NAME = r'Users/30459/Desktop/updata'.format(FILE_NAME)

if __name__ == '__main__':

    print("enter in  old ")
    fota = app_fota.new()
    print('准备下载...')
    fota.download(DEF_URL, FILE_DIR_NAME)
    print('下载完成')
    fota.set_update_flag()
    print('重启升级')
    Power.powerRestart()   # 重启模块

    # 重启模块后，在文件列表里可以看到 '/usr/OTA_APP_HelloWorld_Chic.py 这个文件


