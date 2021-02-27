#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# start/stop/backup/compress vdi diskfile of virtualbox
# Developed by Karl Wachs
# karlwachs@me.com

import subprocess
import time
import datetime
import json
import sys
import os
global logfile

### ------------------------ ###
def toLog(text):
    global logfile, mypid
    if logfile !="":
        try:
            f=open(logfile,"a")
            f.write(datetime.datetime.now().strftime("%H:%M:%S")+" vboxaction (pid# "+mypid+"): ---- "+text+"\n")
            f.close()
        except: 
            print text
    else:
        print text
  
### ------------------------ ###
def testIfAlreadyRunning():
    global mypid
    cmd= "ps -ef | grep /vboxAction.py | grep -v grep"
    ret = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()[0]
    lines=ret.split("\n")
    for line in lines:
        if len(line) < 10: continue
        testPid = line.split()[1]
        if  testPid != mypid:
            toLog("previous task still running: \n>>>>"+line+"<<<<\n") 
            toLog("--exit--")
            exit() 
    return "0"


mypid = str(os.getpid())
  
    
vmMachine = "ubuntu"
vboxPath  = "/Applications/VirtualBox.app/Contents/MacOS/"
vmDisk    = "/Volumes/data4TB/Users/karlwachs/VirtualBox VMs/ubuntu/NewVirtualDisk1.vdi" 
action    = [] # ["stop","compress","start","backup","mountDisk"]
logfile   = ""

pathToPlugin = sys.argv[0].split("/vboxAction.py")[0]

try:
    xxx = json.loads(sys.argv[1])
    try:    action     = xxx["action"]
    except: pass
    try:    vmMachine  = xxx["vmMachine"]
    except: pass
    try:    vboxPath   = xxx["vboxPath"]
    except: pass
    try:    vmDisk     = xxx["vmDisk"]
    except: pass
    try:    logfile     = xxx["logfile"]
    except: pass
    try:    mountCmd     = json.loads(sys.argv[2])
    except: pass
except: pass
toLog("  imput: "+ json.dumps(xxx))


pid = testIfAlreadyRunning()

runningVMs = subprocess.Popen(vboxPath+"VBoxManage  list runningvms",stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0] 
toLog("VBOX running: >>"+ runningVMs.strip("\n")+"<<")

if "stop"  in action:
    if runningVMs.find(vmMachine) >-1:
        toLog(vmMachine+" stopping vbox with acpipowerbutton")
        subprocess.Popen(vboxPath+"VBoxManage controlvm '"+ vmMachine+"' acpipowerbutton ", shell=True )

    vmrunning = 2
    for ii in range(100):
        if vmrunning ==0: break
        toLog(vmMachine+" testing if still running "+ str(vmrunning))
        runningVMs = subprocess.Popen(vboxPath+"VBoxManage  list runningvms",stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0]
        if vmrunning == 2 and vmMachine not in runningVMs:
            vmrunning = 1
        if vmrunning == 1 and  len(subprocess.Popen("ps -ef | grep VBoxManage | grep -v grep",stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0]) < 10:
            break
        time.sleep(10)

if  "compress" in action:
    toLog(vmMachine+" compressing VM disk: "+vboxPath+"VBoxManage modifymedium disk  '"+vmDisk+"' --compact",)
    subprocess.Popen("'"+vboxPath+"VBoxManage' modifymedium disk  '"+vmDisk+"' --compact", shell=True)

    for ii in range(100):
        if len(subprocess.Popen("ps -ef | grep 'VBoxManage modifymedium disk' | grep -v grep",stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0]) < 10:
            toLog(vmMachine+" compressing finished ")
            break
        time.sleep(10)


if  "backup" in action:
    toLog(vmMachine+" backup VM disk   cp '"+vmDisk+"'  '"+vmDisk+"-backup'")
    subprocess.Popen("cp '"+vmDisk+"'  '"+vmDisk+"-backup'", shell=True)

    for ii in range(100):
        if len(subprocess.Popen("ps -ef | grep 'cp ' | grep '"+vmDisk+"-backup' | grep -v grep | grep -v 'vboxAction.py'",stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0]) < 10:
            toLog( vmMachine+" backup finished, now compressing file")
            cmd = "rm '"+vmDisk+"-backup.zip' ; /usr/bin/zip '"+vmDisk+"-backup.zip'  '"+vmDisk+"-backup'  && rm '"+vmDisk+"-backup'  &"
            toLog(vmMachine+" "+cmd)
            subprocess.Popen(cmd ,stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            break
        time.sleep(10)




if "start" in action: 
    for ii in range(3):
        runningVMs = subprocess.Popen(vboxPath+"VBoxManage  list runningvms",stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0]
        if  vmMachine not in runningVMs:
            toLog(vmMachine+" restarting vbox "+vboxPath+"VBoxManage  startvm '"+vmMachine+"' --type headless &")
            subprocess.Popen("'"+vboxPath+"VBoxManage'  startvm '"+vmMachine+"' --type headless &", shell=True)
            time.sleep(20)
    time.sleep(25) # keep "vboxAction.py active for some seconds to enbale tests if still running.. to give vbox time to start

if "mountDisk" in action: 
    time.sleep(20)
    cmd = mountCmd
    toLog(vmMachine+" mount command "+cmd)
    subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

toLog("--finished--")

