import app_fota
from misc import Power

FILE_NAME = r'HelloWorld.py'
DEF_URL = r'120.197.216.227:6000/{}'.format(FILE_NAME)
FILE_DIR_NAME = r'/usr/{}'.format(FILE_NAME)
FILE_NAME2 = r'测试后缀.txt'
DEF_URL2 = r'120.197.216.227:6000/{}'.format(FILE_NAME2)
FILE_DIR_NAME2 = r'/usr/{}'.format(FILE_NAME2)

if __name__ == '__main__':
    fota = app_fota.new()
    print('准备下载...')
    fota.download(DEF_URL, FILE_DIR_NAME)
    fota.download(DEF_URL2, FILE_DIR_NAME2)
    print('下载完成')
    fota.set_update_flag()
    print('重启升级')
    Power.powerRestart()   # 重启模块

    # 重启模块后，在文件列表里可以看到 '/usr/OTA_APP_HelloWorld_Chic.py 这个文件
