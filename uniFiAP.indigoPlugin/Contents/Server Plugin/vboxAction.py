#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# compress vdi diskfile of virtualbox
# Developed by Karl Wachs
# karlwachs@me.com

import subprocess
import time
import json
import sys
try:    
        import indigo 
        logIndigo = True
except: logIndigo = False



vmMachine = "ubuntu"
vboxPath  = "/Applications/VirtualBox.app/Contents/MacOS/"
vmDisk    = "/Volumes/data4TB/Users/karlwachs/VirtualBox VMs/ubuntu/NewVirtualDisk1.vdi" 
action    = ["stop","compress","start"]


indigoDir  = sys.argv[0].split("vboxAction")[0]
if logIndigo: indigo.server.log("\n>>imput:"+ sys.argv[1]+"<<")
else:         print "\n>>imput:"+ sys.argv[1]+"<<"

try:
    xxx = json.loads(sys.argv[1])
    if logIndigo: indigo.server.log("\n>>imput: "+ json.dumps(xxx)+"<<")
    else:         print "\n>>imput: "+ json.dumps(xxx)+"<<"
    try:    action     = xxx["action"]
    except: pass
    try:    vmMachine  = xxx["vmMachine"]
    except: pass
    try:    vboxPath   = xxx["vboxPath"]
    except: pass
    try:    vmDisk     = xxx["vmDisk"]
    except: pass
except: pass


runningVMs = subprocess.Popen(vboxPath+"VBoxManage  list runningvms",stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0] 
if logIndigo:     indigo.server.log("\n>>"+ runningVMs+"<<")
else: print "\n>>"+ runningVMs+"<<"

if "stop" or "compress" in action:
    if runningVMs.find(vmMachine) >-1:
        if logIndigo: indigo.server.log(vmMachine+" stopping vbox ")
        else:         print vmMachine+" stopping vbox "
        subprocess.Popen(vboxPath+"VBoxManage controlvm '"+ vmMachine+"' acpipowerbutton ", shell=True )


if "stop" in action or "compress" :
    vmrunning = 2
    for ii in range(100):
        if vmrunning ==0: break
        if logIndigo: indigo.server.log(vmMachine+" testing if still runing "+ str(vmrunning))
        else:         print vmMachine+" testing if still runing " + str(vmrunning)
        subprocess.Popen(vboxPath+"VBoxManage  list runningvms",stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0]
        if vmrunning == 2 and vmMachine not in subprocess.Popen(vboxPath+"VBoxManage  list runningvms",stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0]:
            vmrunning = 1
        if vmrunning == 1 and  len(subprocess.Popen("ps -ef | grep VBoxManage | grep -v grep",stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0]) < 10:
            break
        time.sleep(10)

if  "compress" in action:
    if logIndigo:  indigo.server.log(vmMachine+" compressing vbox ")
    else:          print vmMachine+" compressing vbox "
    subprocess.Popen(vboxPath+"VBoxManage modifymedium disk  '"+vmDisk+"' --compact", shell=True)

    for ii in range(100):
        if len(subprocess.Popen("ps -ef | grep 'VBoxManage modifymedium disk' | grep -v grep",stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0]) < 10:
            if logIndigo: indigo.server.log(vmMachine+" compressing finished ")
            else:         print vmMachine+" compressing finished "
            break
        time.sleep(10)

runningVMs = subprocess.Popen(vboxPath+"VBoxManage  list runningvms",stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0] 

if "start" in action and vmMachine not in runningVMs:
    if logIndigo: indigo.server.log(vmMachine+" restarting vbox ")
    else:         print vmMachine+" restarting vbox "
    subprocess.Popen(vboxPath+"VBoxManage  startvm '"+vmMachine+"' --type headless &", shell=True)


