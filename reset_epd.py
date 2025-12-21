
from machine import Timer, Pin, I2C, RTC, SPI
import micropython, re, time, network, socket, ntptime, configreader, random, ssl, uos
import errno, sys, ubinascii, machine


import epd1n54v2
import framebuf

if uos.uname().machine.find("C3")>-1:
    spi=SPI(1)
    spi.init(sck=Pin(4),mosi=Pin(6),miso=None)
    e = epd1n54v2.EPD(spi, cs=Pin(20), dc=Pin(3), rst=Pin(2), busy=Pin(1))
    e.init()
else:
    spi=SPI(2, sck=Pin(14), mosi=Pin(13))
    spi.init()
    e = epd1n54v2.EPD(spi, cs=Pin(18), dc=Pin(33), rst=Pin(23), busy=Pin(4))
    e.init()


dispbuf=bytearray(e.width // 8 * e.height)
disp=framebuf.FrameBuffer(dispbuf, e.width, e.height, framebuf.MONO_HLSB)

disp.fill(1)
e.display_part_base_image(dispbuf)
e.display_part_base_image(dispbuf)


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
    drawtxt(100+x*8,100)
    e.display_part_frame()
    x=x+1

# partial mode
e.init(True)

