""" main. py """

from machine import Timer, Pin, I2C, SoftI2C, RTC
import micropython, re, time, network, socket, ntptime, configreader, sh1106, random, framebuf, ssl
micropython.alloc_emergency_exception_buf(100)
import vga1_8x8 as font1

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

# display
i2c=SoftI2C(scl=Pin(4),sda=Pin(5))
disp=sh1106.SH1106_I2C(128,64,i2c,None,0x3c,rotate=180)
disp.fill(0)
disp.show()
disp.contrast(0x5f)

# read config       
config=configreader.ConfigReader()
if fileexists('config.txt'):
    config.read('config.txt')
else:
    print('config.txt is missing. Writing sample.')
    f=open('config.txt','w')
    f.write('ssid=\n')
    f.write('pass=\n')
    f.write('lat=\n')
    f.write('lon=\n')
    f.write('key=\n')
    f.write('timezone=\n')
    f.close()
    raise ConfigError
    
ssid=config.option['ssid']
passw=config.option['pass']
lat=config.option['lat']
lon=config.option['lon']
key=config.option['key']
tmzone=config.option['timezone']
if tmzone=='':
    tzone=9
else:
    tzone=int(tmzone)
ctimeoffset=tzone*3600

if key=='':
    print('Missing info in config.txt.')
    raise ConfigError
#print(config.option)

delaych=['/','-','\\','|']
# wifi connection
ignlist={}
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

def tryconnect(dispid):
    global ssid, passw, ignlist
    wlan.disconnect()
    while wlan.isconnected():
        pass
    if not wlan.isconnected():
      disp.text('Connect',0,0)
      disp.text(ssid,0,8)
      disp.show()
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
                      disp.text('Connect ',0,0)
                      if dispid:
                          disp.text(ssid,0,8)
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
                  disp.text('ReConnect ',0,0)
                  if dispid:
                      disp.text(ssid,0,8)
                  print('ReConnect %s' % (ssid))
          disp.fill_rect(120,0,9,8,0)
          disp.text(delaych[trycounter % 4],120,0)
          disp.show()
          time.sleep_ms(500)
    print('network config:',wlan.ifconfig())
    
tryconnect(True)

def synctime():
    counter=0
    while True:
        try:
            ntptime.settime()
            break
        except Exception as e:
            print(e)
            print("sync time")
            disp.fill_rect(120,0,9,8,0)
            disp.text(delaych[counter % 4],120,0)
            disp.show()
            counter+=1
        time.sleep(1)

# ntp time
rtc=RTC()
synctime()
print(time.localtime(time.time()+tzone*3600))

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
    lastsynctime=0
    
    def __init__(self,lat,lon,key):
        self.last_remain=b''
        self.lastsynctime=0
        self.to_send=b'GET /api/v1/free/point?lat=%s&lon=%s&sections=hourly&timezone=Auto&language=en&units=metric&key=%s HTTP/1.1\r\nHost: www.meteosource.com\r\nConnection: keep-alive\r\nAccept: */*\r\n\r\n' % (lat,lon,key)
    
    def GetInfo(self):
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
        try:
            sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            saddr=socket.getaddrinfo('www.meteosource.com',443)[0][-1]
            sock.connect(saddr)
            # https
            sslsock=ssl.wrap_socket(sock)
            
            self.last_remain=b''
            self.ContLen=-1
            self.imageoffset=0
            self.firststamp=0
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
                               self.ContLen=8192
                           data=data[i:]
                   # process body
                   ilen=len(data)
                   self.ContLen-=ilen
                   if self.ContLen<=0:
                       break
                   data=self.last_remain+data
                   self.last_remain=b''
                   if self.imgoffset>2:
                       data=b''
                       break
                   spos=0
                   epos=0
                   # timezone
                   tzi=re.search("timezone\":\s+?([^,]+),",data)
                   if tzi:
                       stimezone=tzi.group(1)
                       #self.timeoffset=0
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
                           if self.firststamp==0:
                               self.firststamp=dayww
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
                           if self.firststamp<=dayww:
                               self.weinfo.append([dayw,dayww,weath,weicon,summary,ttemp,windspd,winddir,cloud,rain])
                               self.imgoffset+=1
                           data=data[epos:]
                           if self.imgoffset>2:
                               break
                       else:
                           self.last_remain=data
                           break
                # no data
                else:
                    break
            sock.close()
        except Exception as e:
            print(e)
            print(" parser")
        if self.imgoffset>2:
            self.error_count=0
            return True
        else:
            self.error_count+=1
            return False

winfo=MeteoSource(lat,lon,key)

def drawvline(x,y,h):
    for yi in range(random.randint(0,1),h,2):
        disp.pixel(x,y+yi,1)

def drawtemp(x,y,t):
    disp.text('T',x,y)
    if t>0:
        disp.text('%4.1f' % (t),x+10,y)
    else:
        disp.fill_rect(x+8,y,4*8+2,8,1)
        disp.hline(x+8,y+4,3,0)
        disp.text('%4.1f' % (-t),x+10,y,0)
    
def drawpop(x,y,pop):
    xp=int(pop*100)
    disp.fill_rect(x-1,y,4*8+2,8,1)
    disp.text('%3d%%' % (xp),x,y,0)
    
def drawrain(x,y,rain):
    disp.fill_rect(x-1,y,4*8+2,8,1)
    disp.text('%4.2f' % (rain),x,y,0)
    
def drawwind(x,y,wind):
    disp.text('W',x,y)
    disp.text('%4.1f' % (wind),x+10,y)
    
def loadpbm(x,y,fname):
    f=open(fname,'rb')
    f.readline()
    f.readline()
    f.readline()
    data=bytearray(f.read())
    f.close()
    for i, v in enumerate(data):
        data[i]=~v
    fimg=framebuf.FrameBuffer(data,32,32,framebuf.MONO_HLSB)
    disp.blit(fimg,x,y)

def displayinfo(bpop):
    #[dayw,dayww,weath,weicon,summary,ttemp,windspd,winddir,cloud,rain]
    i=0
    idx=0
    px=random.randint(0,2)
    disp.fill(0)
    for wi in winfo.weinfo:
        if idx>0:
            if fileexists(wi[3]):
                loadpbm(px+90,i,wi[3])
            else:
                print('error',wi[3])
            dt=time.localtime(wi[1])
            disp.text('%s' % (wi[2].decode()),px+0,i)
            drawtemp(px+0,i+8,wi[5])
            drawwind(px+0,i+16,wi[6])
            disp.text('  %s' % (wi[7].decode()),px+0,i+24)
            if wi[8]>0:
                disp.text(' %3d%%' % (wi[8]), px+50, i+8)
            if wi[9]>0:
                drawrain(px+50,i+16,wi[9])
            disp.text('%2d:00' % (dt[3]),px+50,i+24)
            drawvline(px+45,i+8,24)
            i+=32
        idx+=1
    disp.show()
    
tmTime=Timer(0)
# update every 5 minutes
tmUpdate = Timer(1)

timeoff=0
showuvi=0

def cbTime(t):
    global timeoff
    displayinfo(True)
    # Night mode
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
       
def cbUpdate(t):
    tmTime.deinit()
    tmUpdate.deinit()
    try:
        winfo.imgoffset=0
        if winfo.GetInfo():
            #print(winfo.weinfo)
            displayinfo(True)
            print('ok')
        else:
            if winfo.error_count>3:
                winfo.error_count=0
                wlan.disconnect()
                tryconnect(True)
    except Exception as e:
        print(e)
        print(" Update")
    tmTime.init(period=1000, mode=Timer.PERIODIC, callback=cbTime)
    tmUpdate.init(period=300000, mode=Timer.PERIODIC, callback=cbUpdate)

        
cbUpdate(0)