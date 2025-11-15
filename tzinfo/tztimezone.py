import os, sys

if __name__!="__main__":
    i=__file__.rfind("/")
    if i!=-1:
        __path__=__file__[:i+1]
    else:
        __path__=""
else:
    __path__="tzinfo/"
    
def GetTimezone(zone):
    i = zone.find("/")
    if i!=-1:
        conti=zone[:i]
        regi=zone[i+1:]
    else:
        regi=zone
        conti="None"

    tz=None
    
    try:
        f=open("%stz%s.csv" % (__path__,conti),"r")
    except:
        f=open("%stzNone.csv" % __path__,"r")

    line=None

    while True:
        line=f.readline()
        if line:
            line=line[:-1]
            i=line.find(regi)
            if i!=-1:
                i=line.find(",")
                if i!=-1:
                    tz = line[i+1:]
                    break
        else:
            break
    f.close()
    
    if tz:
        hh = int(tz[1:3])
        mm = int(tz[4:6])

        tm = hh + mm/60
        if tz[0]=='-':
            tm=-tm
    else:
        tm=None

    return tm

if __name__=="__main__":
    print(GetTimezone("Asia/Katmandu"))
    