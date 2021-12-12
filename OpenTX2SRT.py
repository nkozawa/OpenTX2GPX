import PySimpleGUI as sg
import os
import csv
import datetime
import re

from srtFormat import srtFormat

flds = {}
patDate = re.compile("\d{4}-\d{2}-\d{2}")
patTime = re.compile("\d{2}:\d{2}:\d{2}\.\d+")
logData = []
logDT = []
logSeq =  []
tdtFirst = datetime.date.today()
itemSelectCount = 0

def main():
    sg.theme('SystemDefault')
    crow = []
    ordrow = []

    for i in range(50):
        crow.append([sg.Checkbox('',key='cItem'+str(i),enable_events=True)])

    for i in range(10):
        ordrow.append([sg.Text('',size=(20,1),key='otItem'+str(i)),sg.Button('^',key='bUp'+str(i),enable_events=True),sg.Button('v',key='bDown'+str(i),enable_events=True)])

    layout = [
        [sg.Text('Pathname:'), sg.InputText(key='tPath', enable_events=True), sg.FileBrowse(file_types=(('CSV', '*.CSV'), ('CSV', '*.csv'),))],
        [sg.Text('OpenTX Log:', key='tLog'), sg.Button('Proceed', key='bProc')],
        [sg.Frame('Select(up to 10 items)', [[sg.Column(crow, size=(300,100), scrollable=True)]],key='fSel')],
        [sg.Frame('Order', ordrow)],
        [sg.Frame('Output Format', [[sg.Text('',key='sFormat')]])],
        [sg.Text('Timestamp: YYYY MM DD', size=(21,1), pad=((5,0),(0,0))), sg.InputText(size=(4,1), key='iYYYY', pad=((0,2),(0,0))), sg.InputText(size=(2,1), key='iMM', pad=((0,2),(0,0))), sg.InputText(size=(2,1), key='iDD', pad=((0,10),(0,0))), sg.Text(' HHMMSS', size=(7,1), pad=((5,0),(0,0))), sg.InputText(size=(2,1), key='iHH', pad=((0,2),(0,0))), sg.InputText(size=(2,1), key='iMIN', pad=((0,2),(0,0))), sg.InputText(size=(2,1), key='iSS', pad=((0,2),(0,0))), sg.Button('Update')],
        [sg.Combo((), size=(30, 1), key='cLogSeq')]
    ]

    window = sg.Window('OpenTX2SRT', layout)

    while True:
        event, values = window.read()
        print(event, values)
        if event == sg.WIN_CLOSED:
            break

        elif event == 'tPath':                      # filename process
            print(">"+values['tPath']+"<")
            validLogFile = False
            window['tLog'].update("OpenTX Log: ")
            if (len(values['tPath']) > 0):
                otname = os.path.basename(values['tPath'])
                otext = os.path.splitext(otname)
                print(otext)
                if (otext[1].lower() == '.csv'):
                    print(otname)
                    window['tLog'].update("OpenTX Log: " + otname)
                    validLogFile = True
        elif event == 'bProc':                      # open log file
            if (validLogFile):
                print("opening log file...")
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

    window.close()

def outputFormat(window):
    sFormat = ""
    for i in range(itemSelectCount):
        logHeader = window['otItem'+str(i)].get()
        if (logHeader == 'Date'):
            print(srtFormat['Date'])
            sFormat += logDT[i].strftime(srtFormat['Date']) + ' '
        elif (logHeader == 'Time'):
            sFormat += logDT[i].strftime(srtFormat['Time']) + ' '
        else:
            if (logHeader in srtFormat):
                fmt = srtFormat[logHeader]
            else:
                fmt = '{0}'
            if (fmt == ''):
                sFormat += logData[0][flds[logHeader]] + ' '
            else:
                sFormat += fmt.format(logData[0][flds[logHeader]]) + ' '
    window['sFormat'].update(sFormat)

def itemOrderUp(window,event):
    i = int(event[3:len(event)])
    if (0 < i and i < itemSelectCount):
        temp = window['otItem'+str(i-1)].get()
        window['otItem'+str(i-1)].update(window['otItem'+str(i)].get())
        window['otItem'+str(i)].update(temp)

def itemOrderDown(window,event):
    i = int(event[5:len(event)])
    if (i < itemSelectCount - 1):
        temp = window['otItem'+str(i)].get()
        window['otItem'+str(i)].update(window['otItem'+str(i+1)].get())
        window['otItem'+str(i+1)].update(temp)

def itemSelectEvent(window,event,values):
    global header, itemSelectCount
    i = int(event[5:len(event)])
    print(header[i])
    if (values[event]):
        if (itemSelectCount > 9):
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
        if (hitem == window['otItem'+str(i)].get()):
            print('HIT ' + str(i))
            for j in range(i, itemSelectCount-1):
                window['otItem'+str(j)].update(window['otItem'+str(j+1)].get())
            window['otItem'+str(itemSelectCount-1)].update('')

def itemSelection(window):
    global header

    for i in range(50):
        if (i < len(header)):
            window['cItem'+str(i)].update(text = header[i])
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
    if (len(logSeq) > 1):
        i = 0
        for s in logSeq:
            if (i + 1 < len(logSeq)):
                dur = tdelta2str(logDT[logSeq[i+1]-1] - logDT[s])
            else:
                dur = tdelta2str(logDT[len(logDT)-1] - logDT[s])
            logSeqTD.append(logDT[s].strftime('%Y/%m/%d %H:%M:%S <'+dur+'>'))
            i += 1
        window['cLogSeq'].update(values = logSeqTD)
        window['cLogSeq'].update(str(len(logSeq))+" sessions <"+tdelta2str(totalDuration)+">")
    else:
        window['cLogSeq'].update(logDT[0][0].strftime('%Y/%m/%d %H:%M:%S')+" <"+tdelta2str(totalDuration)+">")

def logMsg(msg):
    #txtMsg.insert(END, msg+"\n")
    #txtMsg.see(END)
    print(msg)

def valErrorMsg(lineNum,hdr,data):
    logMsg("Parse error, Line:"+str(lineNum)+" Field:"+hdr+" Data:"+data)

def openTXLog(logfilename):
#    cleanupUI()
    global header
    date = time = ""
    with open(logfilename, encoding='utf8', newline='') as f:
        openTXLog = csv.reader(f, delimiter=",", doublequote=True, lineterminator="\r\n", quotechar='"', skipinitialspace=True)
        header = next(openTXLog)
        print(header)
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
            if (result is None):
                valErrorMsg(logNum,"Date",date)
                continue
            time = row[flds['Time']]
            result = re.match(patTime,time)
            if (result is None):
                valErrorMsg(logNum,"Time",time)
                continue

            tdt = datetime.datetime.strptime(date+" "+time, '%Y-%m-%d %H:%M:%S.%f')
            if (0 == i):
                tdtFirst = tdt
                logSeq.append(i)
            elif ((tdt - logDT[i - 1]) > tdtDelta60):
                logSeq.append(i)
                print(i)

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