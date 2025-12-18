""" main. py """

use_epd=False
use_debug=False
bcol=0
wcol=1

from machine import Timer, Pin, I2C, RTC, SPI
import micropython, re, time, network, socket, ntptime, configreader, random, ssl, uos
import errno, sys, ubinascii, machine
#import framebuf2 as framebuf
import framebuf
if use_debug:
    from uio import StringIO
micropython.alloc_emergency_exception_buf(100)
import vga2_8x8 as font1
from tzinfo import tztimezone

class ConfigError(RuntimeError):
    pass

def epochtotime(ept, offset):
    return time.gmtime(ept-946684800+offset)

def fileexists(fn):
    try:
        f=open(fn,'r')
        f.close()
        return True
    except:
        return False

# display and timer init
if uos.uname().machine.find("C3")>-1:
    if not use_epd:
        i2c=I2C(0, scl=Pin(9),sda=Pin(8) )
    else:
        import epd1n54v2
        spi=SPI(1)
        spi.init(sck=Pin(4),mosi=Pin(6),miso=None)
        e = epd1n54v2.EPD(spi, cs=Pin(20), dc=Pin(3), rst=Pin(2), busy=Pin(1))
        e.init()
    Pin_setup = Pin(10, Pin.IN, Pin.PULL_UP)
    # id 0 or 2
    tmUpdate = Timer(1)
    modelc3 = True
else:
    # not tested.
    if not use_epd:
        i2c=I2C(0, scl=Pin(22),sda=Pin(21))
    else:
        import epd1n54v2
        spi=SPI(2, sck=Pin(18), mosi=Pin(23))
        spi.init()
        e = epd1n54v2.EPD(spi, cs=Pin(14), dc=Pin(12), rst=Pin(13), busy=Pin(4))
        e.init()
    Pin_setup = Pin(5, Pin.IN, Pin.PULL_UP)
    tmUpdate = Timer(1)
    modelc3 = False  

# unique id
uid = machine.unique_id()
esp_id = ubinascii.hexlify(uid).decode()

if not use_epd:
    iconpath='i32/'
    tempsen_int=5
    import sh1106
    disp=sh1106.SH1106_I2C(128,64,i2c,None,0x3c,rotate=180)
    disp.fill(bcol)
    disp.show()
    disp.contrast(0x5f)
else:
    iconpath='i48/'
    tempsen_int=60
    bcol=1
    wcol=0
    dispbuf=bytearray(200 * 100 // 8)
    disp=framebuf.FrameBuffer(dispbuf, 200, 100, framebuf.MONO_HLSB)
    disp.fill(bcol)
    e.display_part_base_white_image()
    e.display_part_base_white_image()
    e.init(True)
    
def disp_show(bidx,update):
    if not use_epd:
        disp.show()
    else:
        if bidx!=0:
            e.set_frame_memory(dispbuf,0,100,200,100)
        else:
            e.set_frame_memory(dispbuf,0,0,200,100)
        #disp.fill(bcol)
        #e.set_frame_memory(dispbuf,0,100,200,100)
        if update:
            e.display_part_frame()
        
 
# read config
needconfig=False
if not Pin_setup.value():
    print('config')
    needconfig=True

config=configreader.ConfigReader()
if fileexists('config.txt'):
    config.read('config.txt')
else:
    needconfig=True
    print('config.txt is missing.')

try:
    ssid=config.option['ssid']
    passw=config.option['pass']
    lat=config.option['lat']
    lon=config.option['lon']
    key=config.option['key']
    tmzone=config.option['timezone']
except:
    ssid=""
    passw=""
    lat=""
    lon=""
    key=""
    tmzone=""
    
try:
    tzone=float(tmzone)
except:
    tzone=9.0

ctimeoffset=int(tzone*3600)

try:
    stimeout=config.option['timeout']
    ctimeout=int(stimeout)
except:
    ctimeout=20

try:
    tempsensor=config.option['tempsensor']
except:
    tempsensor='0'

try:
    timeint=config.option['interval']
    tminterval=int(timeint)
except:
    tminterval=600


if key=='' or ssid=='':
    print('Missing info in config.txt.')
    needconfig=True
#print(config.option)

if tempsensor=='1':
    import onewire, ds18x20
    if uos.uname().machine.find("C3")>-1:
        ds_sen = ds18x20.DS18X20(onewire.OneWire(Pin(0)))
    else:
        ds_sen = ds18x20.DS18X20(onewire.OneWire(Pin(32)))
    roms = ds_sen.scan()
    print('DS18x20 :', roms)

# wifi connection
delaych=['/','-','\\','|']
ignlist={}
if needconfig:
    wlan = network.WLAN(network.AP_IF)
    wlan.active(False)
    time.sleep(0.5)
    wlan.active(True)
    if modelc3:
        wlan.config(txpower=10.0) # 8.5
    wlan.config(ssid="weather_%s" %esp_id,password="")
else:
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    time.sleep(0.5)
    wlan.active(True)
    if modelc3:
        wlan.config(txpower=10.0) # 8.5

def tryconnect(dispid):
    global ssid, passw, ignlist

    wlan.disconnect()
    while wlan.isconnected():
        pass
    if not wlan.isconnected():
      disp.text('Connect',0,0,wcol)
      disp.text(ssid,0,8,wcol)
      disp_show(0,True)
      print('Connect %s' % (ssid))
      wlan.connect(ssid,passw)
      trycounter=0
      while not wlan.isconnected():
          trycounter+=1
          if trycounter>60:
              ignlist[ssid]=1
              # connect to open wifi
              wl=wlan.scan()
              ap_count=0
              for wap in wl:
                  if ignlist[wap[0]]!=1 and wap[4]==0:
                      ap_count+=1
                      ssid=wap[0]
                      passw=''
                      wlan.connect(ssid,passw)
                      trycounter=0
                      disp.text('Connect ',0,0,wcol)
                      if dispid:
                          disp.text(ssid,0,8,wcol)
                      print('Connect %s' % (ssid))
                      break
              # reset ignore list
              if ap_count==0:
                  ignlist={}
                  trycounter=0
                  time.sleep(30)
                  ssid=config.option['ssid']
                  passw=config.option['pass']
                  wlan.connect(ssid,passw)
                  disp.text('ReConnect ',0,0,wcol)
                  if dispid:
                      disp.text(ssid,0,8,wcol)
                  print('ReConnect %s' % (ssid))
          disp.fill_rect(120,0,9,8,bcol)
          disp.text(delaych[trycounter % 4],120,0,wcol)
          disp_show(0,True)
          time.sleep_ms(1000)
    print('network config:',wlan.ifconfig())
    
if not needconfig:
    tryconnect(True)

def synctime():
    counter=0
    while True:
        try:
            ntptime.settime()
            break
        except Exception as e:
            print(str(e))
            print("sync time")
            disp.fill_rect(120,0,9,8,bcol)
            disp.text(delaych[counter % 4],120,0,wcol)
            disp_show(0,True)
            counter+=1
        time.sleep(1)

# ntp time
rtc=RTC()
if not needconfig:
    synctime()
    print(time.localtime(time.time()+int(tzone*3600)))

# open weather
class MeteoSource:
    ContLen=-1
    last_remain=b''
    timeoffset=ctimeoffset
    to_send=b''
    imgoffset=0
    firststamp=0
    error_count=0
    weinfo=[]
    lsinfo=[]
    lastsynctime=0
    errno=0
    errmsg=''
    
    def __init__(self,lat,lon,key):
        self.last_remain=b''
        self.lastsynctime=0
        self.to_send=b'GET /api/v1/free/point?lat=%s&lon=%s&sections=hourly&timezone=Auto&language=en&units=metric&key=%s HTTP/1.1\r\nHost: www.meteosource.com\r\nConnection: keep-alive\r\nAccept: */*\r\n\r\n' % (lat,lon,key)
    
    def GetInfo(self):
        self.errno=0
        self.errmsg=''
        while True:
            y=time.localtime(time.time()+self.timeoffset)
            if y[0]>2000:
                break
            disp.text('wait sync',0,0)
            print('wait sync')
            synctime()
            time.sleep_ms(1000)

        if self.lastsynctime==0:
            self.lastsynctime=time.time()
        else:
            if time.time()-self.lastsynctime>=1296000:
                try:
                    ntptime.settime()
                    self.lastsynctime=time.time()
                except Exception as e:
                    pass
        sock=None
        sslsock=None
        try:
            saddr=socket.getaddrinfo('www.meteosource.com',443)[0][-1]
            sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(ctimeout)
            sock.connect(saddr)
            context=ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            sslsock=context.wrap_socket(sock)

            self.last_remain=b''
            self.ContLen=-1
            self.imageoffset=0
            self.firststamp=time.time()+self.timeoffset
            self.weinfo=[]
            sslsock.write(self.to_send)
            while True:
                data=sslsock.read(1024)
                if data:
                   # check header
                   if self.ContLen==-1:
                       i=data.decode().find('\r\n\r\n')
                       if i!=-1:
                           i+=4
                           s=re.search("Content\-Length:\s+(\d+)",data)
                           if s:
                               self.ContLen=int(s.group(1))
                           else:
                               self.ContLen=16384
                           data=data[i:]
                   # process body
                   ilen=len(data)
                   self.ContLen-=ilen
                   if self.ContLen<=0:
                       break
                   data=self.last_remain+data
                   self.last_remain=b''
                   if self.imgoffset>4:
                       data=b''
                       break
                   spos=0
                   epos=0
                   # timezone
                   tzi=re.search("timezone\":\"([^\",]+)",data)
                   if tzi:
                       stimezone=tzi.group(1)
                       if stimezone:
                           #print(stimezone)
                           try:
                               tz=tztimezone.GetTimezone(stimezone.decode('utf-8'))
                           except:
                               tz=None

                           if tz:
                               #print(tz)
                               self.timeoffset=int(float(tz)*3600)

                   while True:
                       spos=data.decode().find("{\"date\":")
                       epos=data.decode().find("}}")
                       if epos!=-1:
                           epos+=2
                       if spos!=-1 and epos!=-1 and epos>spos:
                           # date
                           sdayw=re.search("\"date\":\"([^\"]+)",data)
                           if sdayw:
                               dayw=sdayw.group(1)
                               sd=re.search("(\d+)-(\d+)-(\d+)T(\d+):(\d+):(\d+)",dayw)
                               if sd:
                                   t=(int(sd.group(1)),int(sd.group(2)),int(sd.group(3)),int(sd.group(4)),int(sd.group(5)),int(sd.group(6)),0,0,0)
                                   dayww=time.mktime(t)
                               else:
                                   dayww=time.time()+self.timeoffset
                           else:
                               dayw=""
                               dayww=0
                           # weather
                           sweath=re.search("\"weather\":\"([^\"]+)",data)
                           if sweath:
                               weath=sweath.group(1)
                           else:
                               weath=""
                           # icon
                           sicon=re.search("\"icon\":(\d+)",data)
                           if sicon:
                               weicon=sicon.group(1).decode()+".pbm"
                           else:
                               weicon="1.pbm"
                           ssum=re.search("\"summary\":\"([^\"]+)",data)
                           if ssum:
                               summary=ssum.group(1)
                           else:
                               summary=""
                           # temp
                           stemp=re.search("temperature\":([0-9\.\-]+)",data)
                           if stemp:
                               ttemp=float(stemp.group(1))
                           else:
                               ttemp=0.0
                           # wind
                           swind=re.search("\"wind\":\{\"speed\":([0-9\.]+),\"dir\":\"([^\"]+)",data)
                           if swind:
                               windspd=float(swind.group(1))
                               winddir=swind.group(2)
                           else:
                               windspd=0.0
                               winddir=""
                           # cloud
                           scloud=re.search("\"cloud_cover\":{\"total\":(\d+)",data)
                           if scloud:
                               cloud=int(scloud.group(1))
                           else:
                               cloud=0
                           # precipitation
                           srain=re.search("\"precipitation\":{\"total\":([0-9\.]+)",data)
                           if srain:
                               rain=float(srain.group(1))
                           else:
                               rain=0.0
                           # info array
                           if dayww>self.firststamp:
                               self.weinfo.append([dayw,dayww,weath,weicon,summary,ttemp,windspd,winddir,cloud,rain])
                               self.imgoffset+=1
                           data=data[epos:]
                           if self.imgoffset>4:
                               break
                       else:
                           self.last_remain=data
                           break
                # no data
                else:
                    break

        except Exception as e:
            if use_debug:
                s = StringIO()
                sys.print_exception(e, s)
                tracestr = s.getvalue()
                s.close()
                print(tracestr)
            else:
                self.errno = e.errno
                self.errmsg = str(e)
                print(self.errmsg)

        if sslsock:
            sslsock.close()
        if sock:
            sock.close()
        if self.imgoffset>2:
            self.error_count=0
            return True
        else:
            self.error_count+=1
            return False

winfo=MeteoSource(lat,lon,key)

def drawvline(x,y,h):
    for yi in range(random.randint(0,1),h,2):
        disp.pixel(x,y+yi,wcol)

def drawtemp(x,y,t):
    disp.text('T',x,y,wcol)
    if t>0:
        disp.text('%4.1f' % (t),x+10,y,wcol)
    else:
        disp.fill_rect(x+8,y,4*8+2,8,wcol)
        disp.hline(x+8,y+4,3,bcol)
        disp.text('%4.1f' % (-t),x+10,y,bcol)

def drawpop(x,y,pop):
    xp=int(pop*100)
    disp.fill_rect(x-1,y,4*8+2,8,wcol)
    disp.text('%3d%%' % (xp),x,y,bcol)
    
def drawrain(x,y,rain):
    disp.fill_rect(x-1,y,4*8+2,8,wcol)
    disp.text('%4.2f' % (rain),x,y,bcol)
    
def drawwind(x,y,wind):
    disp.text('W',x,y,wcol)
    if wind>=7.0:
        disp.fill_rect(x+9,y,4*8+2,8,wcol)
        disp.text('%4.1f' % (wind),x+10,y,bcol)        
    else:
        disp.text('%4.1f' % (wind),x+10,y,wcol)
    
def loadpbm(x,y,fname):
    f=open(fname,'rb')
    f.readline()
    f.readline()
    f.readline()
    data=bytearray(f.read())
    f.close()
    if not use_epd:
        for i, v in enumerate(data):
            data[i]=~v
        fimg=framebuf.FrameBuffer(data,32,32,framebuf.MONO_HLSB)
    else:
        fimg=framebuf.FrameBuffer(data,48,48,framebuf.MONO_HLSB)
    disp.blit(fimg,x,y)
    data=[]
    fimg=None
   
def displayinfo(sidx):
    #[dayw,dayww,weath,weicon,summary,ttemp,windspd,winddir,cloud,rain]
    i=0
    idx=0
    if not use_epd:
        px=random.randint(0,2)
    else:
        px=0
    disp.fill(bcol)
    if winfo.imgoffset>4:
        for wi in winfo.weinfo:
            if idx<sidx:
                idx+=1
                continue
            if fileexists(iconpath+wi[3]):
                if use_epd:
                    loadpbm(px+152,i,iconpath+wi[3])
                else:
                    loadpbm(px+90,i,iconpath+wi[3])
            else:
                print('error',iconpath+wi[3])
            dt=time.localtime(wi[1])
            if not use_epd:
                disp.text('%s' % (wi[2].decode()[:11]),px+0,i,wcol)
            else:
                disp.text('%s' % (wi[2].decode()[:19]),px+0,i,wcol)
            drawtemp(px+0,i+8,wi[5])
            drawwind(px+0,i+16,wi[6])
            disp.text('  %s' % (wi[7].decode()),px+0,i+24,wcol)
            if wi[8]>0:
                disp.text(' %3d%%' % (wi[8]), px+50, i+8,wcol)
            if wi[9]>0:
                drawrain(px+50,i+16,wi[9])
            if not use_epd:
                disp.text('%2d:00' % (dt[3]),px+50,i+24,wcol)
            else:
                disp.text('%2d:00' % (dt[3]),px+0,i+32,wcol)
            drawvline(px+45,i+8,24)
            if use_epd:
                i+=48
            else:
                i+=32
            # append valid info
            if idx==0:
                winfo.lsinfo=[]
            winfo.lsinfo.append(wi)
            if idx % 2==1:
                break
            idx+=1
    else:
        # display last valid information
        for wi in winfo.lsinfo:
            if fileexists(iconpath+wi[3]):
                if use_epd:
                    loadpbm(px+152,i,iconpath+wi[3])
                else:
                    loadpbm(px+90,i,iconpath+wi[3])
            else:
                print('error',iconpath+wi[3])
            dt=time.localtime(wi[1])
            if idx==0:
                disp.text('Error : %d' % (winfo.errno),px+0,i,wcol)
            else:
                if not use_epd:
                    disp.text('%s' % (wi[2].decode()[:11]),px+0,i,wcol)
                else:
                    disp.text('%s' % (wi[2].decode()[:19]),px+0,i,wcol)
            drawtemp(px+0,i+8,wi[5])
            drawwind(px+0,i+16,wi[6])
            disp.text('  %s' % (wi[7].decode()),px+0,i+24,wcol)
            if wi[8]>0:
                disp.text(' %3d%%' % (wi[8]), px+50, i+8,wcol)
            if wi[9]>0:
                drawrain(px+50,i+16,wi[9])
            if not use_epd:
                disp.text('%2d:00' % (dt[3]),px+50,i+24,wcol)
            else:
                disp.text('%2d:00' % (dt[3]),px+0,i+32,wcol)
            drawvline(px+45,i+8,24)
            if use_epd:
                i+=48
            else:
                i+=32
            if idx==1:
                break
            idx+=1
    if not use_epd:
        disp_show(0,True)
    
timeoff=0
showuvi=0
timeupd=tminterval
ds_readcnt=2

def cbUpdate(t):
    global timeoff
    global timeupd
    global ds_readcnt
    
    timeupd+=1
    ds_readcnt+=1
    if timeupd>tminterval:
        tmUpdate.deinit()
        timeupd=0
        print("cbUpdate")
        try:
            lcnt=0
            winfo.imgoffset=0
            while not winfo.GetInfo():
                lcnt=lcnt+1
                if lcnt>2:
                    break
                if winfo.errno==113 or winfo.errno==116:
                    winfo.error_count=0
                    winfo.imgoffset=0
                    time.sleep(2)
                else:
                    if winfo.error_count>3:
                        winfo.error_count=0
                        wlan.disconnect()
                        tryconnect(True)
                    break

            if winfo.imgoffset>4:
                displayinfo(0)
                if use_epd:
                    disp_show(0,False)
                    displayinfo(2)
                    disp_show(1,True)
                print('ok')

        except Exception as e:
            if use_debug:
                s = StringIO()
                sys.print_exception(e, s)
                tracestr = s.getvalue()
                s.close()
                print("cbUpdate : ")
                print(tracestr)
            else:
                winfo.errno = e.errno
                winfo.errmsg = str(e)
                print(winfo.errmsg)

        tmUpdate.init(period=1000, mode=Timer.PERIODIC, callback=cbUpdate)
    else:
        if not use_epd:
            displayinfo(0)
        # draw local temp
        if tempsensor=='1':
            if timeupd % tempsen_int==0:
                ds_sen.convert_temp()
                ds_readcnt=0
            else:
                if ds_readcnt==1:
                    dstemp=85.0
                    for rom in roms:
                        dstemp=ds_sen.read_temp(rom)
                    if dstemp!=85.0:
                        if use_epd:
                            displayinfo(0)
                            disp_show(0,False)
                            displayinfo(2)
                            ds_readcnt=0 # update once
                            disp.fill_rect(0,0,19*8,8,bcol)
                            drawtemp(0,40,dstemp)
                        else:
                            disp.fill_rect(0,0,11*8+2,8,bcol)
                            drawtemp(random.randint(0,2),0,dstemp)
                        disp_show(1,True)

        # Night mode
        if not use_epd:
            rt=time.localtime(time.time()+winfo.timeoffset)
            if rt[3]>20 or rt[3]<7:
                if timeoff>=5:
                    timeoff=0
                    disp.contrast(0)
            else:
                if timeoff>=5:
                    timeoff=0
                    disp.contrast(0x5f)
                elif timeoff==3:
                    disp.contrast(0)
        timeoff+=1

# start timer
if not needconfig:
    cbUpdate(0)
else:
    # Webserver
    from micropyserver import MicroPyServer
    import utils
    server = MicroPyServer()

    # webserver
    configpara = {"ssid":ssid,"pass":passw,"latitude":lat,"longitude":lon,"key":key,"timezone":tmzone,"timeout":str(ctimeout),"tempsensor":tempsensor,"interval":str(tminterval)}

    def webconfigshow(request):
        # head
        f=open("webconfig_head.txt","r")
        s=f.read()
        f.close()
        server.send(s)
        # input
        f=open("webconfig_input.txt","r")
        s=f.read()
        f.close()
        for k,v in configpara.items():
            if k=="pass" or k=="key":
                v=""
            res=s
            res=res.replace("{%key}",k)
            res=res.replace("{%value}",v)
            server.send(res)
        # tail
        f=open("webconfig_tail.txt","r")
        s=f.read()
        f.close()
        server.send(s)
        
    def save_config():
        f=open("config.txt","w")
        for k,v in configpara.items():
            if k=="latitude" or k=="longitude":
                k=k[:3]
            f.write(k)
            f.write('=')
            f.write(str(v))
            f.write("\n")
        f.close()
        
    def webconfigsubmit(request):
        params = utils.get_request_query_params(request)
        for k,v in params.items():
            if k in configpara:
                v=v.replace('+',' ')
                if k=='interval' or k=='timeout':
                    if v and v!="":
                        if k=='interval' and int(v)<300:
                            v="300"
                        configpara[k]=int(v)
                else:
                    if v and v!="":
                        configpara[k]=v
        save_config()
        server.send("<html><body>ok<br/>Reboot needed</body></html>")
        
    def webconfigstop(request):
        server.send("<html><body>server stopped</body></html>")
        server.stop()

    server.add_route("/", webconfigshow)
    server.add_route("/action_config", webconfigsubmit)
    server.add_route("/stop", webconfigstop)
    server.start()
