# OpenTX2GPX - Convert OpenTX Log which containes GPS data to GPX file
# Author: KozakFPV  
# Copyright (C) 2021 by Nobumichi Kozawa

version = "1.1"

from tkinter import *
from tkinter import filedialog
from tkinter import ttk
#from tkinter import messagebox
import os
import csv
import gpxpy
import gpxpy.gpx
import re
import datetime

flds = {'Date':-1,'Time':-1, 'GPS':-1, 'GSpd(kmh)':-1,'Alt(m)':-1,'Sats':-1}
patDate = re.compile("\d{4}-\d{2}-\d{2}")
patTime = re.compile("\d{2}:\d{2}:\d{2}\.\d+")
patGPS = re.compile("-?\d+\.\d+ -?\d+\.\d+")
patGSpd = re.compile("\d+\.\d+")
patAlt = re.compile("-?\d+")
patSats = re.compile("\d+")
gpsData = []
logSeq =  []
csvFilename = ""

root = Tk()
frame = ttk.Frame(root, padding=10)
lOpenTXLog = ttk.Label(frame, text="OpenTX Log: ")
fMsg = ttk.Frame(frame, padding=10)
txtMsg = Text(fMsg, height=15, width=80)
fLogseq = ttk.Frame(frame)
cboxLogseq = ttk.Combobox(fLogseq, state='readonly', width=27)

rbVar = StringVar()

svYYYY = StringVar()
svMM = StringVar()
svDD = StringVar()
svHr = StringVar()
svMin = StringVar()
svSec = StringVar()
heightOffset = IntVar()

def main():
    style = ttk.Style()
# comment out following line because 'alt' does not work with MacOS Venture and works with default theme well
#    style.theme_use('alt')  # to avoid MacOS Dark mode issue with default ttk thema 'aqua'
    root.title('OpenTX2GPX')
    frame.pack()

    btn = ttk.Button(
        frame, text='OpenTX Log', width=15,
        command=bOpenClicked)
    btn.pack()

    lOpenTXLog.pack(anchor=W)

    fHO = ttk.Frame(frame)
    fHO.pack(anchor=W)

    lMM = ttk.Label(fHO, text="Height offset: ")
    lMM.pack(side=LEFT)
    eMM = ttk.Entry(fHO, textvariable=heightOffset, width=5)
    eMM.pack(side=LEFT)

    fDT = ttk.Frame(frame)
    fDT.pack(anchor=W)

    lDT = ttk.Label(fDT, text="Timestamp: YYYY")
    lDT.pack(side=LEFT)

    eYYYY = ttk.Entry(fDT, textvariable=svYYYY, width=4)
    eYYYY.pack(side=LEFT)
    lMM = ttk.Label(fDT, text=" MM")
    lMM.pack(side=LEFT)
    eMM = ttk.Entry(fDT, textvariable=svMM, width=2)
    eMM.pack(side=LEFT)
    lDD = ttk.Label(fDT, text=" DD")
    lDD.pack(side=LEFT)
    eDD = ttk.Entry(fDT, textvariable=svDD, width=2)
    eDD.pack(side=LEFT)
    lHr = ttk.Label(fDT, text=" / HH")
    lHr.pack(side=LEFT)
    eHr = ttk.Entry(fDT, textvariable=svHr, width=2)
    eHr.pack(side=LEFT)
    lMin = ttk.Label(fDT, text=" MM")
    lMin.pack(side=LEFT)
    eMin = ttk.Entry(fDT, textvariable=svMin, width=2)
    eMin.pack(side=LEFT)
    lSec = ttk.Label(fDT, text=" SS")
    lSec.pack(side=LEFT)
    eSec = ttk.Entry(fDT, textvariable=svSec, width=2)
    eSec.pack(side=LEFT)


    bDT = ttk.Button(fDT, text="Update", command=bDTClicked)
    bDT.pack()
    
    cboxLogseq.pack(side=LEFT)
    rbVar.set("1.1")
    rb1 = ttk.Radiobutton(fLogseq, text="GPX1.0",value="1.0",variable=rbVar)
    rb2 = ttk.Radiobutton(fLogseq, text="GPX1.1",value="1.1",variable=rbVar)
    rb1.pack(side=LEFT)
    rb2.pack(side=LEFT)
    bExportGPX = ttk.Button(fLogseq, text="Export GPX", command=bExportGPXClicked)
    bExportGPX.pack(side=LEFT)
    fLogseq.pack(anchor=W)

    lMsg = ttk.Label(frame,text="Messages:")
    lMsg.pack(anchor=W)
    fMsg.pack(anchor=W)
    txtMsg.grid(row=0,column=0,sticky=(N, W, S, E))
    scrollbar = ttk.Scrollbar(
    fMsg,
    orient=VERTICAL,
    command=txtMsg.yview)
    scrollbar.grid(row=0,column=1,sticky=(N, S))
    txtMsg['yscrollcommand'] = scrollbar.set

    lAuthor = ttk.Label(frame, text="V"+str(version)+" by KozakFPV")
    lAuthor.pack(anchor=E)

    root.mainloop()

def bOpenClicked():
    global csvFilename
    csvFile = filedialog.askopenfile(filetypes=[('CSV','*.csv'),('CSV','*.CSV')],title="Select OpenTX Log")
    if (csvFile is not None):
        csvFilename = os.path.basename(csvFile.name)
        lOpenTXLog['text'] = "OpenTX Log: " + csvFilename
        logMsg("OpenTX Log: "+csvFilename)
        openTXLog(csvFile)

def openFileDialogGPX():
    global csvFilename
    cfname = os.path.splitext(csvFilename)
    gpxFile = filedialog.asksaveasfilename(defaultextension="gpx",initialfile=cfname[0])
    return gpxFile

def bDTClicked():
    y = int(svYYYY.get())
    m = int(svMM.get())
    d = int(svDD.get())
    h = int(svHr.get())
    min = int(svMin.get())
    s = int(svSec.get())
    if (1999 < y and y < 2100 and 0 < m and m < 13 and 0 < d and d < 32 and 0 <= h and h < 24 and 0 <= min and min < 60 and 0 <= s and s < 60): 
        updateTimestamp(y, m, d, h, min, s)
        logMsg("Update timestamp")
    else:
        logMsg("Datetime error - no update")

def bExportGPXClicked():
    if (len(logSeq) == 1):
        exportGPX(0, len(gpsData))
    else:
        c = cboxLogseq.current()
        if (c < 0):
            return
        s = logSeq[c]
        if ((c >= 0) and (c + 1) < len(logSeq)):
            e = logSeq[c + 1]
        else:
            e = len(gpsData)
        exportGPX(s, e)    

def logMsg(msg):
    txtMsg.insert(END, msg+"\n")
    txtMsg.see(END)

def valErrorMsg(lineNum,hdr,data):
    logMsg("Parse error, Line:"+str(lineNum)+" Field:"+hdr+" Data:"+data)

def cleanupUI():
    gpsData.clear()
    logSeq.clear()
    svYYYY.set("")
    svMM.set("")
    svDD.set("")
    svHr.set("")
    svMin.set("")
    svSec.set("")
    cboxLogseq['values'] = []
    cboxLogseq.set("")

# End of GUI part

def openTXLog(csvf):
    cleanupUI()
    date = time = ""
    openTXLog = csv.reader(csvf, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
    header = next(openTXLog)
    i = 0
    for hdr in header:
        for fl in flds.keys():
            if (hdr == fl):
                flds[fl] = i
        i += 1
    i = logNum = 0
    tdtDelta60 = datetime.timedelta(0,60)

    for row in openTXLog:
        logNum += 1
        # validation process, just skip no valid data
        date = row[flds['Date']]
        result = re.match(patDate,date)
        if (result is None):
            valErrorMsg(logNum,"Date",date)
            continue
        time = row[flds['Time']]
        result = re.match(patTime,time)
        if (result is None):
            valErrorMsg(logNum,"Time",time)
            continue
        gps = row[flds['GPS']]
        result = re.match(patGPS,gps)
        if (result is None):
            valErrorMsg(logNum,"GPS",gps)
            continue
        spd = row[flds['GSpd(kmh)']]
        result = re.match(patGSpd,spd)
        if (result is None):
            valErrorMsg(logNum,"GSpd(kmh)",spd)
            continue
        alt = row[flds['Alt(m)']]
        result = re.match(patAlt,alt)
        if (result is None):
            valErrorMsg(logNum,"Alt(m)",alt)
            continue
        sats = row[flds['Sats']]
        result = re.match(patSats,sats)
        if (result is None):
            valErrorMsg(logNum,"Sats",sats)
            continue
        # end of validation process

        tdt = datetime.datetime.strptime(date+" "+time, '%Y-%m-%d %H:%M:%S.%f')
        if (0 == i):
            tdtFirst = tdt
            logSeq.append(i)
        #elif (1 == i):
        #    tdtInterval = tdt - tdtFirst       #may not use this
        elif ((tdt - gpsData[i - 1][0]) > tdtDelta60):
            logSeq.append(i)

        gps = row[flds['GPS']].split()
        glon = gps.pop()
        glat = gps.pop()
        gpsData.append([tdt,glon,glat,spd,alt,sats])

        svYYYY.set(tdtFirst.strftime("%Y"))
        svMM.set(tdtFirst.strftime("%m"))
        svDD.set(tdtFirst.strftime("%d"))
        svHr.set(tdtFirst.strftime("%H"))
        svMin.set(tdtFirst.strftime("%M"))
        svSec.set(tdtFirst.strftime("%S"))

        i += 1
        logSeqUpdate()

def logSeqUpdate():
    cboxLogseq['values'] = []
    cboxLogseq.set("")
    logSeqTD = []
    totalDuration = gpsData[len(gpsData)-1][0] - gpsData[0][0]
    if (len(logSeq) > 1):
        i = 0
        for s in logSeq:
            if (i + 1 < len(logSeq)):
                dur = tdelta2str(gpsData[logSeq[i+1]-1][0] - gpsData[s][0])
            else:
                dur = tdelta2str(gpsData[len(gpsData)-1][0] - gpsData[s][0])
            logSeqTD.append(gpsData[s][0].strftime('%Y/%m/%d %H:%M:%S <'+dur+'>'))
            i += 1
        cboxLogseq['values'] = logSeqTD
        cboxLogseq.set(str(len(logSeq))+" sessions <"+tdelta2str(totalDuration)+">")
    else:
        cboxLogseq.set(gpsData[0][0].strftime('%Y/%m/%d %H:%M:%S')+" <"+tdelta2str(totalDuration)+">")

def tdelta2str(tdelta):
    sec = tdelta.total_seconds()
    h = sec // 3600
    m = sec % 3600 // 60
    s = sec - h * 3600 - m * 60
    if (h == 0):
        return "%02d:%02d"%(m, s)
    else:
        return "%02d:%02d:%02d"%(h, m, s)

def updateTimestamp(y, m, d, h, min, s):
    if (len(gpsData) > 0):
        dt = datetime.datetime(y, m, d, h, min, s)
        dtDiff = dt - gpsData[0][0]
        i = 0
        while(i < len(gpsData)):
            gpsData[i][0] = dtDiff + gpsData[i][0]
            i += 1
        logSeqUpdate()

def exportGPX(s, e):
    gpx = gpxpy.gpx.GPX()
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    i = s
    while(i < e):
        lon = gpsData[i][1]
        lat = gpsData[i][2]
        alt = gpsData[i][4]
        if (heightOffset.get() > 0):
            alt = str(int(alt) + heightOffset.get())
        gtp = gpxpy.gpx.GPXTrackPoint(lat, lon, alt)
        gtp.time = gpsData[i][0]
        speed = float(gpsData[i][3]) * 1000 / 3600
        gtp.speed = speed
        gtp.satellites = gpsData[i][5]
        #gtp.extensions = {'speed':speed}
        gpx_segment.points.append(gtp)
        i += 1

    gpxFilename = openFileDialogGPX()
    if (gpxFilename != ""):
        with open(gpxFilename, "w") as f:
            f.write(gpx.to_xml(version=rbVar.get()))

if __name__ == "__main__":
    main()