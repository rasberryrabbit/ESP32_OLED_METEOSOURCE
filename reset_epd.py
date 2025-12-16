
from machine import Timer, Pin, I2C, RTC, SPI
import micropython, re, time, network, socket, ntptime, configreader, random, ssl, uos
import errno, sys, ubinascii, machine


import epd1n54v2
import framebuf
spi=SPI(2, sck=Pin(18), mosi=Pin(23))
spi.init()
e = epd1n54v2.EPD(spi, cs=Pin(14), dc=Pin(12), rst=Pin(13), busy=Pin(4))
e.init()

dispbuf=bytearray(e.width // 8 * e.height)
disp=framebuf.FrameBuffer(dispbuf, e.width, e.height, framebuf.MONO_HLSB)

e.clear()

#disp.fill(1)
#disp.text('hello world!',30,0,0)
#for i in range(200 // 8):
#    disp.text('%d' % i,0,i*8,0)   
#e.display(dispbuf)