

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
        f=open("tz%s.csv" % conti,"r")
    except:
        f=open("tzNone.csv","r")

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


# print(GetTimezone("Asia/Kuala_Lumpur"))
