import smbus
import time

class LCD1602:
    def __init__(self, i2c_addr=0x27, i2c_bus=1):
        # Thiết lập I2C
        self.bus = smbus.SMBus(i2c_bus)
        self.address = i2c_addr
        
        # Các hằng số lệnh LCD
        self.LCD_CHR = 1  # Chế độ cho ký tự
        self.LCD_CMD = 0  # Chế độ cho lệnh

        # Địa chỉ các dòng trên LCD
        self.LCD_LINE_1 = 0x80  # Dòng 1
        self.LCD_LINE_2 = 0xC0  # Dòng 2

        # Chuỗi khởi tạo LCD
        self.lcd_init()
    
    def lcd_init(self):
        # Chuỗi khởi tạo LCD
        self.lcd_write(0x33, self.LCD_CMD)  # 110011 Khởi tạo
        self.lcd_write(0x32, self.LCD_CMD)  # 110010 Khởi tạo
        self.lcd_write(0x06, self.LCD_CMD)  # Chuyển hướng con trỏ
        self.lcd_write(0x0C, self.LCD_CMD)  # Tắt con trỏ
        self.lcd_write(0x28, self.LCD_CMD)  # Màn hình 2 dòng
        self.lcd_write(0x01, self.LCD_CMD)  # Xóa màn hình

    def lcd_write(self, bits, mode):
        # Gửi dữ liệu đến LCD qua I2C (chế độ 4-bit)
        high_bits = mode | (bits & 0xF0) | 0x08  # Bật đèn nền
        low_bits = mode | ((bits << 4) & 0xF0) | 0x08  # Bật đèn nền
        self.bus.write_byte(self.address, high_bits)
        self.lcd_toggle_enable(high_bits)
        self.bus.write_byte(self.address, low_bits)
        self.lcd_toggle_enable(low_bits)

    def lcd_toggle_enable(self, bits):
        # Chuyển đổi tín hiệu enable để lưu dữ liệu
        time.sleep(0.0005)
        self.bus.write_byte(self.address, (bits | 0x04))  # Set bit Enable
        time.sleep(0.0005)
        self.bus.write_byte(self.address, (bits & ~0x04))  # Clear bit Enable
        time.sleep(0.0005)

    def clear(self):
        self.lcd_write(0x01, self.LCD_CMD)  # Xóa màn hình

    def write_string(self, message, line=1):
        # Ghi một chuỗi vào LCD
        if line == 1:
            self.lcd_write(self.LCD_LINE_1, self.LCD_CMD)
        elif line == 2:
            self.lcd_write(self.LCD_LINE_2, self.LCD_CMD)
        for char in message:
            self.lcd_write(ord(char), self.LCD_CHR)

    def close(self):
        # Xóa màn hình và tắt đèn nền
        self.clear()
