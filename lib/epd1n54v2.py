"""
* | File        :   epd1in54_V2.py
* | Author      :   Waveshare team (Converted to Python)
* | Function    :   1.54inch e-paper V2
* | Info        :
*----------------
* | This version:   V1.0
* | Date        :   2019-06-24 (Converted: 2025)
* | Info        :
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
"""

from time import sleep_ms

# 디스플레이 크기
EPD_WIDTH = 200
EPD_HEIGHT = 200

# waveform full refresh
WF_Full_1IN54 = bytearray([
    0x80, 0x48, 0x40, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x40, 0x48, 0x80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x80, 0x48, 0x40, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x40, 0x48, 0x80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0xA, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x8, 0x1, 0x0, 0x8, 0x1, 0x0, 0x2,
    0xA, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x0, 0x0, 0x0,
    0x22, 0x17, 0x41, 0x0, 0x32, 0x20
])

# waveform partial refresh(fast)
WF_PARTIAL_1IN54_0 = bytearray([
    0x0, 0x40, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x80, 0x80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x40, 0x40, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0xF, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x1, 0x1, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
    0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x0, 0x0, 0x0,
    0x02, 0x17, 0x41, 0xB0, 0x32, 0x28,
])


class EPD:
    """1.54inch e-Paper V2 display driver class"""
    
    def __init__(self, spi, cs, dc, rst, busy):
        """
        Initialize EPD display        
        """
        self.spi = spi
        self.cs = cs
        self.dc = dc
        self.rst = rst
        self.busy = busy
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        self.rst.init(self.rst.OUT, value=0)
        self.busy.init(self.busy.IN)
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
    
    def send_command(self, command):
        self.dc(0)  # LOW
        self.cs(0)
        self.spi.write(command)
        self.cs(1)
    
    def send_data(self, data):
        self.dc(1)  # HIGH
        self.cs(0)
        self.spi.write(data)
        self.cs(1)
    
    def wait_until_idle(self):
        while self.busy.value() == 1:  # LOW: idle, HIGH: busy
            sleep_ms(100)
        sleep_ms(200)
    
    def lut(self, lut_data):
        self.send_command(b'\x32')
        for i in range(153):
            self.send_data(bytearray([lut_data[i]]))
        self.wait_until_idle()
    
    def set_lut(self, lut_data):
        self.lut(lut_data)
        
        self.send_command(b'\x3f')
        self.send_data(bytearray([lut_data[153]]))
        
        self.send_command(b'\x03')
        self.send_data(bytearray([lut_data[154]]))
        
        self.send_command(b'\x04')
        self.send_data(bytearray([lut_data[155]]))
        self.send_data(bytearray([lut_data[156]]))
        self.send_data(bytearray([lut_data[157]]))
        
        self.send_command(b'\x2c')
        self.send_data(bytearray([lut_data[158]]))
    
    def hdir_init(self, partial=False):
        """Initialize display in high direction mode"""
            
        self.reset()
        self.wait_until_idle()

        if not partial:
            self.send_command(b'\x12')  # SWRESET
            self.wait_until_idle()
            
            self.send_command(b'\x01')  # Driver output control
            self.send_data(b'\xC7')
            self.send_data(b'\x00')
            self.send_data(b'\x01')
            
            self.send_command(b'\x11')  # data entry mode
            self.send_data(b'\x01')
            
            self.send_command(b'\x44')  # set Ram-X address start/end position
            self.send_data(b'\x00')
            self.send_data(b'\x18')  # 0x18 -> (24+1)*8=200
            
            self.send_command(b'\x45')  # set Ram-Y address start/end position
            self.send_data(b'\xC7')  # 0xC7 -> (199+1)=200
            self.send_data(b'\x00')
            self.send_data(b'\x00')
            self.send_data(b'\x00')
            
            self.send_command(b'\x3C')  # BorderWaveform
            self.send_data(b'\x01')
            
            self.send_command(b'\x18')
            self.send_data(b'\x80')
            
            self.send_command(b'\x22')  # Load Temperature and waveform setting
            self.send_data(b'\xB1')
            self.send_command(b'\x20')
            
            self.send_command(b'\x4E')  # set RAM x address count to 0
            self.send_data(b'\x00')
            self.send_command(b'\x4F')  # set RAM y address count to 0x199
            self.send_data(b'\xC7')
            self.send_data(b'\x00')
            self.wait_until_idle()
            
            self.set_lut(WF_Full_1IN54)

        else:

            self.set_lut(WF_PARTIAL_1IN54_0)
            
            self.send_command(b'\x37')
            self.send_data(b'\x00')
            self.send_data(b'\x00')
            self.send_data(b'\x00')
            self.send_data(b'\x00')
            self.send_data(b'\x00')
            self.send_data(b'\x40')
            self.send_data(b'\x00')
            self.send_data(b'\x00')
            self.send_data(b'\x00')
            self.send_data(b'\x00')
            
            self.send_command(b'\x3c')  # BorderWavefrom
            self.send_data(b'\x80')
            
            self.send_command(b'\x22')
            self.send_data(b'\xc0')
            self.send_command(b'\x20')
            self.wait_until_idle()

    def init(self, partial=False):
        """Initialize display in low direction mode"""
        
        self.reset()
        self.wait_until_idle()
        
        if not partial:
            self.send_command(b'\x12')  # SWRESET
            self.wait_until_idle()
            
            self.send_command(b'\x01')  # Driver output control
            self.send_data(b'\xC7')
            self.send_data(b'\x00')
            self.send_data(b'\x00')
            
            self.send_command(b'\x11')  # data entry mode
            self.send_data(b'\x03')
            
            self.send_command(b'\x44')
            # x point must be the multiple of 8 or the last 3 bits will be ignored
            self.send_data(bytearray([(0 >> 3) & 0xFF]))
            self.send_data(bytearray([(199 >> 3) & 0xFF]))
            
            self.send_command(b'\x45')
            self.send_data(bytearray([0 & 0xFF]))
            self.send_data(bytearray([(0 >> 8) & 0xFF]))
            self.send_data(bytearray([199 & 0xFF]))
            self.send_data(bytearray([(199 >> 8) & 0xFF]))
            
            self.send_command(b'\x3C')  # BorderWaveform
            self.send_data(b'\x01')
            
            self.send_command(b'\x18')
            self.send_data(b'\x80')
            
            self.send_command(b'\x22')  # Load Temperature and waveform setting
            self.send_data(b'\xB1')
            self.send_command(b'\x20')
            
            self.send_command(b'\x4E')  # set RAM x address count to 0
            self.send_data(b'\x00')
            self.send_command(b'\x4F')  # set RAM y address count to 0x199
            self.send_data(b'\xC7')
            self.send_data(b'\x00')
            self.wait_until_idle()
            
            self.set_lut(WF_Full_1IN54)

        else:

            self.set_lut(WF_PARTIAL_1IN54_0)
            
            self.send_command(b'\x37')
            self.send_data(b'\x00')
            self.send_data(b'\x00')
            self.send_data(b'\x00')
            self.send_data(b'\x00')
            self.send_data(b'\x00')
            self.send_data(b'\x40')
            self.send_data(b'\x00')
            self.send_data(b'\x00')
            self.send_data(b'\x00')
            self.send_data(b'\x00')
            
            self.send_command(b'\x3c')  # BorderWavefrom
            self.send_data(b'\x80')
            
            self.send_command(b'\x22')
            self.send_data(b'\xc0')
            self.send_command(b'\x20')
            self.wait_until_idle()
    
    def reset(self):
        self.rst(1)  # HIGH
        sleep_ms(200)
        self.rst(0)  # LOW - module reset
        sleep_ms(5)
        self.rst(1)  # HIGH
        sleep_ms(200)
    
    def clear(self,color=b'\xff'):
        self.send_command(b'\x24')
        for j in range(self.width // 8 * self.height):
            self.send_data(color)

        # DISPLAY REFRESH
        self.display_frame()
    
    def display(self, frame_buffer):
        self.set_frame_memory(frame_buffer,0,0,self.width,self.height)        
        # DISPLAY REFRESH
        self.display_frame()
    
    def display_part_base_image(self, frame_buffer):
        len=EPD_WIDTH // 8 * EPD_HEIGHT
        if EPD_WIDTH & 7!=0:
            len=len+1
        
        if frame_buffer is not None:
            self.send_command(b'\x24')
            for j in range(len):
                self.send_data(bytearray([frame_buffer[j]]))
        
        # DISPLAY REFRESH
        self.display_part_frame()
    
    def display_part_base_white_image(self):
        len=EPD_WIDTH // 8 * EPD_HEIGHT
        if EPD_WIDTH & 7!=0:
            len=len+1
        
        self.send_command(b'\x24')
        for j in range(len):
            self.send_data(b'\xff')
        
        # DISPLAY REFRESH
        self.display_part_frame()
    
    def display_part(self, frame_buffer):
        len=EPD_WIDTH // 8 * EPD_HEIGHT
        if EPD_WIDTH & 7!=0:
            len=len+1
        
        if frame_buffer is not None:
            self.send_command(b'\x24')
            for j in range(len):
                self.send_data(bytearray([frame_buffer[j]]))
        
        # DISPLAY REFRESH
        self.display_part_frame()
    
    def set_memory_area(self, x_start, y_start, x_end, y_end):
        self.send_command(b'\x44')
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data(bytearray([(x_start >> 3) & 0xFF]))
        self.send_data(bytearray([(x_end >> 3) & 0xFF]))
        
        self.send_command(b'\x45')
        self.send_data(bytearray([y_start & 0xFF]))
        self.send_data(bytearray([(y_start >> 8) & 0xFF]))
        self.send_data(bytearray([y_end & 0xFF]))
        self.send_data(bytearray([(y_end >> 8) & 0xFF]))
    
    def set_memory_pointer(self, x, y):
        self.send_command(b'\x4e')
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data(bytearray([(x >> 3) & 0xFF]))
        
        self.send_command(b'\x4F')
        self.send_data(bytearray([y & 0xFF]))
        self.send_data(bytearray([(y >> 8) & 0xFF]))
        self.wait_until_idle()
    
    def display_frame(self):
        # DISPLAY REFRESH
        self.send_command(b'\x22')
        self.send_data(b'\xc7')
        self.send_command(b'\x20')
        self.wait_until_idle()
    
    def display_part_frame(self):
        self.send_command(b'\x22')
        self.send_data(b'\xcf')
        self.send_command(b'\x20')
        self.wait_until_idle()
    
    def set_frame_memory(self, image_buffer, x, y, image_width, image_height):

        if (image_buffer is None or
                x < 0 or image_width < 0 or
                y < 0 or image_height < 0):
            return
        
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        x &= 0xF8
        image_width &= 0xF8
        
        if x + image_width >= self.width:
            x_end = self.width - 1
        else:
            x_end = x + image_width - 1
        
        if y + image_height >= self.height:
            y_end = self.height - 1
        else:
            y_end = y + image_height - 1
        
        self.set_memory_area(x, y, x_end, y_end)
        self.set_memory_pointer(x, y)
        self.send_command(b'\x24')
        
        # send the image data
        for j in range(y_end - y + 1):
            for i in range((x_end - x + 1) // 8):
                self.send_data(bytearray([image_buffer[i + j * (image_width // 8)]]))
    
    def sleep(self):
        self.send_command(b'\x10')  # enter deep sleep
        self.send_data(b'\x01')
        sleep_ms(200)

