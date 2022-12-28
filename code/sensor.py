import log
import utime
from machine import I2C

# Register address
NSA2862_SET_REG = 0x30
NSA2862_DATA_REG = 0x06

# Work mode
NSA2862_MODE_CONTINUE = 0x03
NSA2862_DATA_LENGHT = 0x06

# Bind it to the external interrupt pin。
class Sensor(object):
    i2c_dev = None #I2C对象
    address = None #从设备地址
    int_pin = None 
    dev_log = None #log对象


    #类初始化
    def __init__(self, slave_address = 0x6d):
        self.dev_log = log.getLogger("I2C") #创建log对象
        self.address = slave_address #配置从设备地址
        self.i2c_dev = I2C(I2C.I2C0, I2C.STANDARD_MODE) #创建I2C对象
        self.sensor_init() #传感器初始化
        utime.sleep_ms(100) 
        pass

    #读传感器指定地址、长度数据
    def read_data(self, regaddr, datalen, debug=False):
        r_data = [0x00 for _ in range(datalen)]
        r_data = bytearray(r_data)
        reg_addres = bytearray([regaddr])
        self.i2c_dev.read(self.address, reg_addres, 1, r_data, datalen, 1)
        ret_data = list(r_data)
        if debug is True:
            self.dev_log.debug(" read 0x{0:02x} 0x{1:02x} 0x{2:02x} from 0x{3:02x}".format(ret_data[0], ret_data[1], ret_data[2], regaddr))
        return ret_data

    #写传感器指定地址数据
    def write_data(self, regaddr, data, debug=False):
        w_data = bytearray([regaddr, data])
        # Temporarily put the address to be transmitted in the data bit
        self.i2c_dev.write(self.address, bytearray(0x00), 0, bytearray(w_data), len(w_data))
        if debug is True:
            self.dev_log.debug(" write 0x{0:02x} to 0x{1:02x}".format(data, regaddr))

    #传感器复位
    def sensor_reset(self):
        pass

    #传感器初始化
    def sensor_init(self):
        #复位
        self.sensor_reset()  # 1. Reset the device; 2. Initialize the sensor
        #配置持续工作
        self.write_data(NSA2862_SET_REG, NSA2862_MODE_CONTINUE)

    #读取压力、温度值
    def read_press_temp(self):
        #读取压力、温度原始值
        r_data = self.read_data(NSA2862_DATA_REG, NSA2862_DATA_LENGHT)
        #处理压力值
        pressure = (r_data[0] << 16) | (
                r_data[1] << 8) | (r_data[2] )
        if (pressure&0x800000)==0x800000:
            pressure=~pressure
            pressure=pressure+1
            pressure*=-1
        pressure=pressure/8388608 -0.1 
        pressure=3125*pressure
        #打印压力值
        self.dev_log.info("current pressure is {}Kpa".format(pressure))
        #处理温度值
        temperature = (r_data[3] << 16) | (
                r_data[4] << 8) | r_data[5]
        if temperature<8388608:
            temperature=temperature/65536+25
        else :
            temperature=(temperature-16777216)/65536 +25
        #打印温度处理值
        self.dev_log.info("current temperature is {}°C".format(temperature))
        return pressure, temperature

#测试Sensor类
if __name__ == "__main__":
    log.basicConfig(level=log.DEBUG)  # Set log output level
    sensor = Sensor()
    while True:
        sensor.read_press_temp()
        utime.sleep(1)
