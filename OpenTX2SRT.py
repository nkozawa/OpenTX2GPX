import PySimpleGUI as sg
import os
import csv
import datetime
import re

from srtFormat import srtFormat
version = 'V0.1'
messageLevel = 3

flds = {}
patDate = re.compile("\d{4}-\d{2}-\d{2}")
patTime = re.compile("\d{2}:\d{2}:\d{2}\.\d+")
header = []
logData = []
logDT = []
logSeq =  []
tdtFirst = datetime.date.today()
itemSelectCount = 0
ordLogHNum = []
ordLogFormat = []

def main():
    sg.theme('SystemDefault')
    crow = []
    ordrow = []

    for i in range(50):
        crow.append([sg.Checkbox('',key='cItem'+str(i),enable_events=True)])

    sepvalues = ['""','" "','"  "','" / "','" | "','"\\n"']

    for i in range(10):
        ordrow.append([sg.Text('',size=(20,1),key='otItem'+str(i)),sg.Button('^',key='bUp'+str(i),enable_events=True),sg.Button('v',key='bDown'+str(i),enable_events=True),sg.Combo(sepvalues,default_value='" "',key='ocItem'+str(i),enable_events=True)])

    layout = [
        [sg.Text('Pathname:'), sg.InputText(key='tPath', enable_events=True), sg.FileBrowse(file_types=(('CSV', '*.CSV'), ('CSV', '*.csv'),))],
        [sg.Text('OpenTX Log:', key='tLog'), sg.Button('Proceed', key='bProc')],
        [sg.Frame('Select(up to 10 items)', [[sg.Column(crow, size=(300,100), scrollable=True)]],key='fSel')],
        [sg.Frame('Order', ordrow)],
        [sg.Frame('Output Format', [[sg.Text('',key='sFormat')]])],
        [sg.Text('Timestamp: YYYY MM DD', size=(21,1), pad=((5,0),(0,0))), sg.InputText(size=(4,1), key='iYYYY', pad=((0,2),(0,0))), sg.InputText(size=(2,1), key='iMM', pad=((0,2),(0,0))), sg.InputText(size=(2,1), key='iDD', pad=((0,10),(0,0))), sg.Text(' HHMMSS', size=(7,1), pad=((5,0),(0,0))), sg.InputText(size=(2,1), key='iHH', pad=((0,2),(0,0))), sg.InputText(size=(2,1), key='iMIN', pad=((0,2),(0,0))), sg.InputText(size=(2,1), key='iSS', pad=((0,2),(0,0))), sg.Button('Update')],
        [sg.Combo((), size=(30, 1), key='cLogSeq'), sg.Button('ExportSRT')],
        [sg.Text(version+' by KozakFPV')]
    ]

    window = sg.Window('OpenTX2SRT', layout)

    validLogFile = False
    while True:
        event, values = window.read()
        logMsg(3, str(event)+' '+str(values))
        if event == sg.WIN_CLOSED:
            break

        elif event == 'tPath':                      # filename process
            resetGui(window)
            validLogFile = False
            window['tLog'].update("OpenTX Log: ")
            if (len(values['tPath']) > 0):
                otname = os.path.basename(values['tPath'])
                otext = os.path.splitext(otname)
                if (otext[1].lower() == '.csv'):
                    logMsg(2, otname)
                    window['tLog'].update("OpenTX Log: " + otname)
                    validLogFile = True
        elif event == 'bProc':                      # open log file
            if (validLogFile):
                logMsg(2, "opening log file...")
                openTXLog(values['tPath'])
                itemSelection(window)
                logSeqUpdate(window)
        elif event[0:5] == 'cItem':                 # item selection
            itemSelectEvent(window,event,values)
            window['fSel'].update('Select(up to 10 items) Count:'+str(itemSelectCount))
            outputFormat(window)
        elif event[0:3] == 'bUp':
            itemOrderUp(window,event)
            outputFormat(window)
        elif event[0:5] == 'bDown':
            itemOrderDown(window,event)
            outputFormat(window)
        elif event == 'Update':
            updateDT(window, values)
        elif event == 'ExportSRT':
            exportSRTEvent(window, values)
        elif event[0:6] == 'ocItem':
            outputFormat(window)

    window.close()


def exportSRTEvent(window, values):
    if (len(logSeq) < 1):
        return
    elif (len(logSeq) == 1):
        exportSRT(0, len(logData))
    else:
        c = values['cLogSeq'].split(':')
        ic = int(c[0]) - 1
        if (ic < 0):
            return
        s = logSeq[ic]
        if ((ic >= 0) and (ic + 1) < len(logSeq)):
            e = logSeq[ic + 1]
        else:
            e = len(logData)
        exportSRT(window, s, e)    

def exportSRT(window, s, e):
    fname = sg.popup_get_file('Export SRT', save_as=True, file_types=(('Subscript', '.srt')))
    if fname is None or fname == '':
        return
    fDt = logDT[s]
    prev = '00:00:00,000'
    i = s + 1
    c = 1
    with open(fname,'w') as f:
        while i < e:
            elpsDT = logDT[i] - fDt
            e1 = str(elpsDT).split(':')
            e2 = e1[2].split('.')
            if len(e2) > 1:
                e3 = e2[1][0:3]
            else:
                e3 = '000'
            current = '{0:02d}:{1}:{2},{3}'.format(int(e1[0]),e1[1],e2[0],e3)
            f.write(str(c) + "\n")
            f.write(prev + ' --> ' + current + "\n")
#            print(c)
#            print(prev + ' --> ' + current)
            prev = current
            fmttext = getFormatedText(window,i).split('\\n')
            for ftxt in fmttext:
                f.write(ftxt + "\n")
            f.write("\n")
#            print(getFormatedText(i))
#            print()
            i += 1
            c += 1
    logMsg(1, 'Exported SRT file: '+fname)

def updateDT(window, values):
    sy = values['iYYYY']
    sm = values['iMM']
    sd = values['iDD']
    sh = values['iHH']
    smin = values['iMIN']
    ss = values['iSS']
    if sy.isdecimal() and sm.isdecimal() and sd.isdecimal() and sh.isdecimal() and smin.isdecimal() and ss.isdecimal():
        y = int(sy)
        m = int(sm)
        d = int(sd)
        h = int(sh)
        min = int(smin)
        s = int(ss)
        if 1999 < y and y < 2100 and 0 < m and m < 13 and 0 < d and d < 32 and 0 <= h and h < 24 and 0 <= min and min < 60 and 0 <= s and s < 60: 
            updateTimestamp(window, y, m, d, h, min, s)
            logMsg(2, "Update timestamp")
        else:
            logMsg(1, "Datetime error - no update")

def updateTimestamp(window, y, m, d, h, min, s):
    global tdtFirst
    if (len(logDT) > 0):
        tdtFirst = datetime.datetime(y, m, d, h, min, s)
        dtDiff = tdtFirst - logDT[0]
        i = 0
        while(i < len(logDT)):
            logDT[i] = dtDiff + logDT[i]
            i += 1
        logSeqUpdate(window)
        outputFormat(window)

def resetGui(window):
    global flds, header, logData, logDT, logSeq, itemSelectCount
    for i in range(50):
        window['cItem'+str(i)].update(False, text = '', visible = False)

    for i in range(10):
        window['otItem'+str(i)].update('')

    window['cLogSeq'].update('', values = [])
    window['sFormat'].update('')

    flds = {}
    header = []
    logData = []
    logDT = []
    logSeq =  []
    itemSelectCount = 0
    window['iYYYY'].update(tdtFirst.strftime(""))
    window['iMM'].update(tdtFirst.strftime(""))
    window['iDD'].update(tdtFirst.strftime(""))
    window['iHH'].update(tdtFirst.strftime(""))
    window['iMIN'].update(tdtFirst.strftime(""))
    window['iSS'].update(tdtFirst.strftime(""))


def outputFormat(window):
    global ordLogHNum, ordLogFormat, itemSelectCount
    sFormat = ""
    ordLogHNum = []
    ordLogFormat = []
    for i in range(itemSelectCount):
        logHeader = window['otItem'+str(i)].get()
        ordLogHNum.append(flds[logHeader])
        if logHeader in srtFormat:
            fmt = srtFormat[logHeader]
        else:
            logMsg(1, 'Header item "'+logHeader+" is not found in srtFormat.py")
            fmt = '{0}'
        ordLogFormat.append(fmt)
    window['sFormat'].update(getFormatedText(window,0))


def getFormatedText(window,n):
    global ordLogHNum, ordLogFormat, itemSelectCount
    sFormat = ""
    for i in range(itemSelectCount):
        fmt = ordLogFormat[i]
        sepa = window['ocItem'+str(i)].get()
        sepa = sepa[1:len(sepa)-1]
        if 2 > ordLogHNum[i]:
            sFormat += logDT[n].strftime(fmt) + sepa
        else:
            if fmt == '':
                sFormat += logData[n][ordLogHNum[i]] + sepa
            else:
                sFormat += fmt.format(logData[n][ordLogHNum[i]]) + sepa
    return sFormat

def itemOrderUp(window,event):
    i = int(event[3:len(event)])
    if 0 < i and i < itemSelectCount:
        temp = window['otItem'+str(i-1)].get()
        window['otItem'+str(i-1)].update(window['otItem'+str(i)].get())
        window['otItem'+str(i)].update(temp)

def itemOrderDown(window,event):
    i = int(event[5:len(event)])
    if i < itemSelectCount - 1:
        temp = window['otItem'+str(i)].get()
        window['otItem'+str(i)].update(window['otItem'+str(i+1)].get())
        window['otItem'+str(i+1)].update(temp)

def itemSelectEvent(window,event,values):
    global header, itemSelectCount
    if len(header) == 0:
        window[event].update(False)
        return

    i = int(event[5:len(event)])
    if values[event]:
        if itemSelectCount > 9:
            window[event].update(False)
            return
        window['otItem'+str(itemSelectCount)].update(header[i])
        itemSelectCount += 1
    else:
        itemDeselect(window,values,header[i])
        itemSelectCount -= 1

def itemDeselect(window,values,hitem):
    global itemSelectCount
    for i in range(itemSelectCount):
        if hitem == window['otItem'+str(i)].get():
            for j in range(i, itemSelectCount-1):
                window['otItem'+str(j)].update(window['otItem'+str(j+1)].get())
            window['otItem'+str(itemSelectCount-1)].update('')

def itemSelection(window):
    global header

    for i in range(50):
        if i < len(header):
            window['cItem'+str(i)].update(text = header[i], visible = True)
        else:
            window['cItem'+str(i)].update(visible = False)

def logSeqUpdate(window):
    window['iYYYY'].update(tdtFirst.strftime("%Y"))
    window['iMM'].update(tdtFirst.strftime("%m"))
    window['iDD'].update(tdtFirst.strftime("%d"))
    window['iHH'].update(tdtFirst.strftime("%H"))
    window['iMIN'].update(tdtFirst.strftime("%M"))
    window['iSS'].update(tdtFirst.strftime("%S"))
    logSeqTD = []
    totalDuration = logDT[len(logDT)-1] - logDT[0]
    if len(logSeq) > 1:
        i = 0
        for s in logSeq:
            if i + 1 < len(logSeq):
                dur = tdelta2str(logDT[logSeq[i+1]-1] - logDT[s])
            else:
                dur = tdelta2str(logDT[len(logDT)-1] - logDT[s])
            logSeqTD.append(logDT[s].strftime(str(i+1)+': %Y/%m/%d %H:%M:%S <'+dur+'>'))
            i += 1
        window['cLogSeq'].update(values = logSeqTD)
        window['cLogSeq'].update('0: '+str(len(logSeq))+" sessions <"+tdelta2str(totalDuration)+">")
    else:
        window['cLogSeq'].update(logDT[0][0].strftime('0: %Y/%m/%d %H:%M:%S')+" <"+tdelta2str(totalDuration)+">")

def logMsg(l, msg):
    #txtMsg.insert(END, msg+"\n")
    #txtMsg.see(END)
    if l <= messageLevel:
        print(msg)

def valErrorMsg(lineNum,hdr,data):
    logMsg(1, "Parse error, Line:"+str(lineNum)+" Field:"+hdr+" Data:"+data)

def openTXLog(logfilename):
#    cleanupUI()
    global header
    date = time = ""
    with open(logfilename, encoding='utf8', newline='') as f:
        openTXLog = csv.reader(f, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)

        header = next(openTXLog)
        i = 0
        for hdr in header:
            flds[hdr] = i
            i += 1
        i = logNum = 0
        tdtDelta60 = datetime.timedelta(0,60)

        for row in openTXLog:
            global tdtFirst
            logNum += 1
            # validation process, just skip no valid data
            date = row[flds['Date']]
            result = re.match(patDate,date)
            if result is None:
                valErrorMsg(logNum,"Date",date)
                continue
            time = row[flds['Time']]
            result = re.match(patTime,time)
            if result is None:
                valErrorMsg(logNum,"Time",time)
                continue

            tdt = datetime.datetime.strptime(date+" "+time, '%Y-%m-%d %H:%M:%S.%f')
            if 0 == i:
                tdtFirst = tdt
                logSeq.append(i)
            elif (tdt - logDT[i - 1]) > tdtDelta60:
                logSeq.append(i)

            logData.append(row)
            logDT.append(tdt)
            
            i += 1

def tdelta2str(tdelta):
    sec = tdelta.total_seconds()
    h = sec // 3600
    m = sec % 3600 // 60
    s = sec - h * 3600 - m * 60
    if (h == 0):
        return "%02d:%02d"%(m, s)
    else:
        return "%02d:%02d:%02d"%(h, m, s)


if __name__ == "__main__":
    main()