"""
File      :   epd2in13_v4.py
Author    :   Waveshare team
Function  :   2.13inch e-paper V4
Info      :
----------------
This version:   V1.0
Date        :   2023-6-25
Info        :

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documnetation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to  whom the Software is
furished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import time

# Display resolution
EPD_WIDTH = 122
EPD_HEIGHT = 250

# Display modes
FULL = 0
FAST = 1
PART = 2

class EPD:
    def __init__(self, spi, cs, dc, rst, busy):
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
        self.bufwidth = 128 // 8  # 16
        self.bufheight = 63
        self.count = 0

    def send_command(self, command):
        self.dc(0)
        self.cs(0)
        self.spi.write(command)
        self.cs(1)

    def send_data(self, data):
        self.dc(1)
        self.cs(0)
        self.spi.write(data)
        self.cs(1)

    def wait_until_idle(self):
        while True:  # LOW: idle, HIGH: busy
            if self.busy.value() == 0:
                break
            time.sleep_ms(10)

    def set_windows(self, x_start, y_start, x_end, y_end):
        """
        Set the display window
        
        Args:
            x_start: X-axis starting position
            y_start: Y-axis starting position
            x_end: End position of X-axis
            y_end: End position of Y-axis
        """
        self.send_command(bytearray([0x44]))  # SET_RAM_X_ADDRESS_START_END_POSITION
        self.send_data(bytearray([(x_start >> 3) & 0xFF]))
        self.send_data(bytearray([(x_end >> 3) & 0xFF]))

        self.send_command(bytearray([0x45]))  # SET_RAM_Y_ADDRESS_START_END_POSITION
        self.send_data(bytearray([y_start & 0xFF]))
        self.send_data(bytearray([(y_start >> 8) & 0xFF]))
        self.send_data(bytearray([y_end & 0xFF]))
        self.send_data(bytearray([(y_end >> 8) & 0xFF]))

    def set_cursor(self, x_start, y_start):
        """
        Set cursor position
        
        Args:
            x_start: X-axis starting position
            y_start: Y-axis starting position
        """
        self.send_command(bytearray([0x4E]))  # SET_RAM_X_ADDRESS_COUNTER
        self.send_data(bytearray([x_start & 0xFF]))

        self.send_command(bytearray([0x4F]))  # SET_RAM_Y_ADDRESS_COUNTER
        self.send_data(bytearray([y_start & 0xFF]))
        self.send_data(bytearray([(y_start >> 8) & 0xFF]))

    def init(self, mode=FULL):

        self.reset()

        if mode == FULL:
            self.wait_until_idle()
            self.send_command(bytearray([0x12]))  # soft reset
            self.wait_until_idle()

            self.send_command(bytearray([0x01]))  # Driver output control
            self.send_data(bytearray([0xF9]))
            self.send_data(bytearray([0x00]))
            self.send_data(bytearray([0x00]))

            self.send_command(bytearray([0x11]))  # data entry mode
            self.send_data(bytearray([0x03]))

            self.set_windows(0, 0, EPD_WIDTH - 1, EPD_HEIGHT - 1)
            self.set_cursor(0, 0)

            self.send_command(bytearray([0x3C]))  # BorderWavefrom
            self.send_data(bytearray([0x05]))

            self.send_command(bytearray([0x21]))  # Display update control
            self.send_data(bytearray([0x00]))
            self.send_data(bytearray([0x80]))

            self.send_command(bytearray([0x18]))  # Read built-in temperature sensor
            self.send_data(bytearray([0x80]))
            self.wait_until_idle()

        elif mode == FAST:
            self.wait_until_idle()
            self.send_command(bytearray([0x12]))  # soft reset
            self.wait_until_idle()

            self.send_command(bytearray([0x18]))  # Read built-in temperature sensor
            self.send_data(bytearray([0x80]))

            self.send_command(bytearray([0x11]))  # data entry mode
            self.send_data(bytearray([0x03]))

            self.set_windows(0, 0, EPD_WIDTH - 1, EPD_HEIGHT - 1)
            self.set_cursor(0, 0)

            self.send_command(bytearray([0x22]))  # Load temperature value
            self.send_data(bytearray([0xB1]))
            self.send_command(bytearray([0x20]))
            self.wait_until_idle()

            self.send_command(bytearray([0x1A]))  # Write to temperature register
            self.send_data(bytearray([0x64]))
            self.send_data(bytearray([0x00]))

            self.send_command(bytearray([0x22]))  # Load temperature value
            self.send_data(bytearray([0x91]))
            self.send_command(bytearray([0x20]))
            self.wait_until_idle()

        elif mode == PART:
            self.rst(0)
            time.sleep_ms(1)
            self.rst(1)

            self.send_command(bytearray([0x3C]))  # BorderWavefrom
            self.send_data(bytearray([0x80]))

            self.send_command(bytearray([0x01]))  # Driver output control
            self.send_data(bytearray([0xF9]))
            self.send_data(bytearray([0x00]))
            self.send_data(bytearray([0x00]))

            self.send_command(bytearray([0x11]))  # data entry mode
            self.send_data(bytearray([0x03]))

            self.set_windows(0, 0, EPD_WIDTH - 1, EPD_HEIGHT - 1)
            self.set_cursor(0, 0)


    def reset(self):
        """Software reset"""
        self.rst(1)
        time.sleep_ms(20)
        self.rst(0)
        time.sleep_ms(2)
        self.rst(1)
        time.sleep_ms(20)
        self.count = 0

    def clear(self, color=b'\xff'):
        """Clear screen"""
        w = (EPD_WIDTH // 8) if (EPD_WIDTH % 8 == 0) else (EPD_WIDTH // 8 + 1)
        h = EPD_HEIGHT

        self.send_command(bytearray([0x24]))
        for j in range(h):
            for i in range(w):
                self.send_data(color)

        # DISPLAY REFRESH
        self.send_command(bytearray([0x22]))
        self.send_data(bytearray([0xF7]))
        self.send_command(bytearray([0x20]))
        self.wait_until_idle()

    def display(self, frame_buffer):
        """
        Send the image buffer in RAM to e-Paper and display
        
        Args:
            frame_buffer: Image data (bytearray or list)
        """
        w = (EPD_WIDTH // 8) if (EPD_WIDTH % 8 == 0) else (EPD_WIDTH // 8 + 1)
        h = EPD_HEIGHT

        if frame_buffer is not None:
            self.send_command(bytearray([0x24]))
            for j in range(h):
                for i in range(w):
                    self.send_data(frame_buffer[i + j * w])

        # DISPLAY REFRESH
        self.send_command(bytearray([0x22]))
        self.send_data(bytearray([0xF7]))
        self.send_command(bytearray([0x20]))
        self.wait_until_idle()

    def display1(self, frame_buffer):
        """
        Display with chunked buffer (4 parts)
        
        Args:
            frame_buffer: Image data chunk
        """
        if self.count == 0:
            self.send_command(bytearray([0x24]))
            self.count += 1
        elif 0 < self.count < 4:
            self.count += 1

        for i in range(self.bufwidth * self.bufheight):
            self.send_data(frame_buffer[i])

        if self.count == 4:
            self.send_command(bytearray([0x22]))
            self.send_data(bytearray([0xF7]))
            self.send_command(bytearray([0x20]))
            self.wait_until_idle()
            self.count = 0

    def display_fast(self, frame_buffer):
        """
        Send the image buffer in RAM to e-Paper and fast display
        
        Args:
            frame_buffer: Image data
        """
        w = (EPD_WIDTH // 8) if (EPD_WIDTH % 8 == 0) else (EPD_WIDTH // 8 + 1)
        h = EPD_HEIGHT

        if frame_buffer is not None:
            self.send_command(bytearray([0x24]))
            for j in range(h):
                for i in range(w):
                    self.send_data(bytearray([frame_buffer[i + j * w]]))

        # DISPLAY REFRESH
        self.send_command(bytearray([0x22]))
        self.send_data(bytearray([0xC7]))
        self.send_command(bytearray([0x20]))
        self.wait_until_idle()

    def display_part_base_image(self, frame_buffer):
        """
        Refresh a base image
        
        Args:
            frame_buffer: Image data
        """
        w = (EPD_WIDTH // 8) if (EPD_WIDTH % 8 == 0) else (EPD_WIDTH // 8 + 1)
        h = EPD_HEIGHT

        if frame_buffer is not None:
            self.send_command(bytearray([0x24]))
            for j in range(h):
                for i in range(w):
                    self.send_data(bytearray([frame_buffer[i + j * w]]))

            #self.send_command(bytearray([0x26])) #red
            #for j in range(h):
            #    for i in range(w):
            #        self.send_data(bytearray([frame_buffer[i + j * w]]))

        # DISPLAY REFRESH
        self.send_command(bytearray([0x22]))
        self.send_data(bytearray([0xF7]))
        self.send_command(bytearray([0x20]))
        self.wait_until_idle()

    def display_part(self, frame_buffer):
        """
        Send the image buffer in RAM to e-Paper and partial refresh
        
        Args:
            frame_buffer: Image data
        """
        w = (EPD_WIDTH // 8) if (EPD_WIDTH % 8 == 0) else (EPD_WIDTH // 8 + 1)
        h = EPD_HEIGHT

        if frame_buffer is not None:
            self.send_command(bytearray([0x24]))
            for j in range(h):
                for i in range(w):
                    self.send_data(bytearray([frame_buffer[i + j * w]]))

        # DISPLAY REFRESH
        self.send_command(bytearray([0x22]))
        self.send_data(bytearray([0xFF]))
        self.send_command(bytearray([0x20]))
        self.wait_until_idle()

    def clear_part(self, color=b'\xff'):
        """Clear screen (partial refresh)"""
        w = (EPD_WIDTH // 8) if (EPD_WIDTH % 8 == 0) else (EPD_WIDTH // 8 + 1)
        h = EPD_HEIGHT

        self.send_command(bytearray([0x24]))
        for j in range(h):
            for i in range(w):
                self.send_data(color)

        # DISPLAY REFRESH
        self.send_command(bytearray([0x22]))
        self.send_data(bytearray([0x0F]))
        self.send_command(bytearray([0x20]))
        self.wait_until_idle()

    def sleep(self):
        """Enter sleep mode"""
        self.send_command(bytearray([0x10]))  # enter deep sleep
        self.send_data(bytearray([0x01]))
        time.sleep_ms(200)

