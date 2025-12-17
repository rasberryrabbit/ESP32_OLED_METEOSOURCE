
from machine import Timer, Pin, I2C, RTC, SPI
import micropython, re, time, network, socket, ntptime, configreader, random, ssl, uos
import errno, sys, ubinascii, machine


import epd1n54v2
import framebuf

spi=SPI(2, sck=Pin(18), mosi=Pin(23))
spi.init()
e = epd1n54v2.EPD(spi, cs=Pin(14), dc=Pin(12), rst=Pin(13), busy=Pin(4))
e.partial=False
e.init()

dispbuf=bytearray(e.width // 8 * e.height)
disp=framebuf.FrameBuffer(dispbuf, e.width, e.height, framebuf.MONO_HLSB)

def drawtxt(x,y):
    data=bytearray(8)
    fimg=framebuf.FrameBuffer(data,8,8,framebuf.MONO_HLSB)
    fimg.fill(1)
    fimg.text('A',0,0,0)
    e.set_frame_memory(data,x,y,8,8)
    data=[]
    fimg=None

x=1
def doit():
    # draw image
    global x
    drawtxt(100+x,100)
    e.display_part_frame()
    x=x+1

# draw base image on framebuf
disp.fill(1)
disp.text('hello world!',30,0,0)
for i in range(200 // 8):
    disp.text('%d' % i,0,i*8,0)

# partial has 2 memory page, fill the pages
e.display_part_base_white_image()
e.display_part_base_white_image()

# partial mode
e.init(True)

for i in range(8):
    doit()
