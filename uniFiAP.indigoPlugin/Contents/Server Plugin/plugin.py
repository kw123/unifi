#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# uniFi Plugin
# Developed by Karl Wachs
# karlwachs@me.com

import datetime
import simplejson as json
import subprocess
import fcntl
import os
import sys
import pwd
import time
import Queue
import random
import socket
import getNumber as GT
import MAC2Vendor
import threading
import logging
import copy
import json
import requests
import inspect

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

import cProfile
import pstats


"""
good web pages for unifi API
https://ubntwiki.com/products/software/unifi-controller/api
https://github.com/NickWaterton/Unifi-websocket-interface/blob/master/controller.py
https://github.com/Art-of-WiFi/UniFi-API-client

"""

dataVersion = 2.0

## Static parameters, not changed in pgm
_GlobalConst_numberOfAP	 = 5
_GlobalConst_numberOfSW	 = 13

_GlobalConst_numberOfGroups = 20
_GlobalConst_groupList		= [u"Group"+unicode(i) for i in range(_GlobalConst_numberOfGroups)]
_GlobalConst_dTypes			= [u"UniFi",u"gateway",u"DHCP",u"SWITCH",u"Device-AP",u"Device-SW-5",u"Device-SW-8",u"Device-SW-10",u"Device-SW-11",u"Device-SW-18",u"Device-SW-26",u"Device-SW-52",u"neighbor"]
_debugAreas					= [u"Logic",u"Log",u"Dict",u"LogDetails",u"DictDetails",u"ConnectionCMD",u"ConnectionRET",u"Expect",u"ExpectRET",u"Video",u"Fing",u"BC",u"Ping",u"Protect",u"all",u"Special",u"UDM",u"IgnoreMAC",u"DBinfo"]
_numberOfPortsInSwitch		= [5, 8, 10, 11, 18, 26, 52]
################################################################################
# noinspection PyUnresolvedReferences,PySimplifyBooleanCheck,PySimplifyBooleanCheck
class Plugin(indigo.PluginBase):
	####-----------------			  ---------
	def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
		indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)

		#pfmt = logging.Formatter('%(asctime)s.%(msecs)03d\t%(levelname)-12s\t%(name)s.%(funcName)-25s %(msg)s', datefmt='%Y-%m-%d %H:%M:%S')
		#self.plugin_file_handler.setFormatter(pfmt)

		self.pluginShortName 			= u"UniFi"


		self.quitNow					= ""
		self.updateConnectParams		= time.time() - 100
		self.getInstallFolderPath		= indigo.server.getInstallFolderPath()+"/"
		self.indigoPath					= indigo.server.getInstallFolderPath()+"/"
		self.indigoRootPath 			= indigo.server.getInstallFolderPath().split("Indigo")[0]
		self.pathToPlugin 				= self.completePath(os.getcwd())

		major, minor, release 			= map(int, indigo.server.version.split("."))
		self.indigoRelease				= release
		self.indigoVersion 				= float(major)+float(minor)/10.



		self.pluginVersion				= pluginVersion
		self.pluginId					= pluginId
		self.pluginName					= pluginId.split(".")[-1]
		self.myPID						= os.getpid()
		self.pluginState				= u"init"

		self.myPID 						= os.getpid()
		self.MACuserName				= pwd.getpwuid(os.getuid())[0]

		self.MAChome					= os.path.expanduser(u"~")
		self.userIndigoDir				= self.MAChome + "/indigo/"
		self.indigoPreferencesPluginDir = self.getInstallFolderPath+"Preferences/Plugins/"+self.pluginId+"/"
		self.indigoPluginDirOld			= self.userIndigoDir + self.pluginShortName+"/"
		self.PluginLogFile				= indigo.server.getLogsFolderPath(pluginId=self.pluginId) +"/plugin.log"

		formats=	{   logging.THREADDEBUG: "%(asctime)s %(msg)s",
						logging.DEBUG:       "%(asctime)s %(msg)s",
						logging.INFO:        "%(asctime)s %(msg)s",
						logging.WARNING:     "%(asctime)s %(msg)s",
						logging.ERROR:       "%(asctime)s.%(msecs)03d\t%(levelname)-12s\t%(name)s.%(funcName)-25s %(msg)s",
						logging.CRITICAL:    "%(asctime)s.%(msecs)03d\t%(levelname)-12s\t%(name)s.%(funcName)-25s %(msg)s" }

		date_Format = { logging.THREADDEBUG: "%d %H:%M:%S",
						logging.DEBUG:       "%d %H:%M:%S",
						logging.INFO:        "%d %H:%M:%S",
						logging.WARNING:     "%d %H:%M:%S",
						logging.ERROR:       "%Y-%m-%d %H:%M:%S",
						logging.CRITICAL:    "%Y-%m-%d %H:%M:%S" }
		formatter = LevelFormatter(fmt="%(msg)s", datefmt="%Y-%m-%d %H:%M:%S", level_fmts=formats, level_date=date_Format)

		self.plugin_file_handler.setFormatter(formatter)
		self.indiLOG = logging.getLogger("Plugin")  
		self.indiLOG.setLevel(logging.THREADDEBUG)

		self.indigo_log_handler.setLevel(logging.INFO)
		indigo.server.log(u"initializing  ... ")

		indigo.server.log(  u"path To files:          =================")
		indigo.server.log(  u"indigo                  {}".format(self.indigoRootPath))
		indigo.server.log(  u"installFolder           {}".format(self.indigoPath))
		indigo.server.log(  u"plugin.py               {}".format(self.pathToPlugin))
		indigo.server.log(  u"Plugin params           {}".format(self.indigoPreferencesPluginDir))

		self.indiLOG.log( 0,u"logger  enabled for     0 ==> TEST ONLY ")
		self.indiLOG.log( 5,u"logger  enabled for     THREADDEBUG    ==> TEST ONLY ")
		self.indiLOG.log(10,u"logger  enabled for     DEBUG          ==> TEST ONLY ")
		self.indiLOG.log(20,u"logger  enabled for     INFO           ==> TEST ONLY ")
		self.indiLOG.log(30,u"logger  enabled for     WARNING        ==> TEST ONLY ")
		self.indiLOG.log(40,u"logger  enabled for     ERROR          ==> TEST ONLY ")
		self.indiLOG.log(50,u"logger  enabled for     CRITICAL       ==> TEST ONLY ")
		indigo.server.log(  u"check                   {}  <<<<    for detailed logging".format(self.PluginLogFile))
		indigo.server.log(  u"Plugin short Name       {}".format(self.pluginShortName))
		indigo.server.log(  u"my PID                  {}".format(self.myPID))	 
		indigo.server.log(  u"set params for indigo V {}".format(self.indigoVersion))	 


		
####

	####-----------------			  ---------
	def __del__(self):
		indigo.PluginBase.__del__(self)

	###########################		INIT	## START ########################

	####----------------- @ startup set global parameters, create directories etc ---------
	def startup(self):
		if self.pathToPlugin.find(u"/"+self.pluginName+".indigoPlugin/")==-1:
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"The pluginname is not correct, please reinstall or rename")
				self.errorLog(u"It should be   /Libray/....../Plugins/"+self.pluginName+".indigPlugin")
				p=max(0,self.pathToPlugin.find(u"/Contents/Server"))
				self.errorLog(u"It is: "+self.pathToPlugin[:p])
				self.errorLog(u"please check your download folder, delete old *.indigoPlugin files or this will happen again during next update")
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.sleep(100000)
				self.quitNOW="wrong plugin name"
				return

		if not self.checkPluginPath(self.pluginName,  self.pathToPlugin):
			exit()

		if not self.moveToIndigoPrefsDir(self.indigoPluginDirOld, self.indigoPreferencesPluginDir):
			exit()

		self.pythonPath					= u"/usr/bin/python2.6"
		if os.path.isfile(u"/usr/bin/python2.7"):
			self.pythonPath				= u"/usr/bin/python2.7"


		self.checkcProfile()


		self.debugLevel = []
		for d in _debugAreas:
			if self.pluginPrefs.get(u"debug"+d, False): self.debugLevel.append(d)


		self.logFile		 	= ""
		self.logFileActive	 	= self.pluginPrefs.get(u"logFileActive2", u"standard")
		self.maxLogFileSize	 	= 1*1024*1024
		self.lastCheckLogfile	= time.time()
		self.setLogfile(unicode(self.pluginPrefs.get(u"logFileActive2", u"standard")))


		self.varExcludeSQLList = [u"Unifi_New_Device",u"Unifi_With_IPNumber_Change",u"Unifi_With_Status_Change",u"Unifi_Camera_with_Event",u"Unifi_Camera_Event_PathToThumbnail","Unifi_Camera_Event_DateOfThumbNail","Unifi_Camera_Event_Date"]
		#self.varExcludeSQLList = [u"Unifi_New_Device",u"Unifi_With_IPNumber_Change",u"Unifi_With_Status_Change"]

		self.UserID					= {}
		self.PassWd					= {}
		self.connectParamsDefault 	= {}
		self.connectParamsDefault[u"expectCmdFile"]		= {	u"APtail": u"execLog.exp",
															u"GWtail": u"execLog.exp",
															u"UDtail": u"execLog.exp",
															u"SWtail": u"execLog.exp",
															u"VDtail": u"execLogVideo.exp",
															u"GWdict": u"dictLoop.exp",
															u"UDdict": u"dictLoop.exp",
															u"SWdict": u"dictLoop.exp",
															u"APdict": u"dictLoop.exp",
															u"GWctrl": u"simplecmd.exp",
															u"UDctrl": u"simplecmd.exp",
															u"VDdict": u"simplecmd.exp"
														}
		self.connectParamsDefault[u"commandOnServer"]	= {	u"APtail": u"/usr/bin/tail -F /var/log/messages",
															u"GWtail": u"/usr/bin/tail -F /var/log/messages",
															u"UDtail": u"/usr/bin/tail -F /var/log/messages",
															u"SWtail": u"/usr/bin/tail -F /var/log/messages",
															u"VDtail": u"/usr/bin/tail -F /var/lib/unifi-video/logs/motion.log",
															u"VDdict": u"not implemented",
															u"GWdict": u"mca-dump | sed -e 's/^ *//'",
															u"UDdict": u"mca-dump | sed -e 's/^ *//'",
															u"SWdict": u"mca-dump | sed -e 's/^ *//'",
															u"GWctrl": u"mca-ctrl -t dump-cfg | sed -e 's/^ *//'",
															u"UDctrl": u"mca-ctrl -t dump-cfg | sed -e 's/^ *//'",
															u"APdict": u"mca-dump | sed -e 's/^ *//'"
														}
		self.connectParamsDefault[u"enableListener"]	= {	u"APtail": True,
															u"GWtail": True,
															u"UDtail": True,
															u"SWtail": True,
															u"VDtail": True,
															u"VDdict": True,
															u"GWdict": True,
															u"UDdict": True,
															u"SWdict": True,
															u"GWctrl": True,
															u"UDctrl": True,
															u"APdict": True
														}
		self.connectParamsDefault[u"promptOnServer"] 	= {}
		"""
															u"APtail": u"\# ",
															u"GWtail": u":~",
															u"GWctrl": u":~",
															u"UDtail": u"\# ",
															u"UDctrl": u"\# ",
															u"SWtail": u"\# ",
															u"VDtail": u"VirtualBox",
															u"VDdict": u"VirtualBox",
															u"GWdict": u":~",
															u"UDdict": u"\# ",
															u"SWdict": u"\# ",
															u"APdict": u"\# "}
		"""
		self.connectParamsDefault[u"startDictToken"]	= {	u"APtail": u"x",
															u"GWtail": u"x",
															u"UDtail": u"x",
															u"SWtail": u"x",
															u"VDtail": u"x",
															u"GWdict": u"mca-dump | sed -e 's/^ *//'",
															u"UDdict": u"mca-dump | sed -e 's/^ *//'",
															u"SWdict": u"mca-dump | sed -e 's/^ *//'",
															u"APdict": u"mca-dump | sed -e 's/^ *//'"
														}
		self.connectParamsDefault[u"endDictToken"]		= {	u"APtail": u"x",
															u"GWtail": u"x",
															u"UDtail": u"x",
															u"VDtail": u"x",
															u"GWdict": u"xxxThisIsTheEndTokenxxx",
															u"UDdict": u"xxxThisIsTheEndTokenxxx",
															u"SWdict": u"xxxThisIsTheEndTokenxxx",
															u"APdict": u"xxxThisIsTheEndTokenxxx"
														}
		self.connectParamsDefault[u"UserID"]			= {	u"unixDevs": u"",
															u"unixUD":   u"",
															u"unixNVR":  u"",
															u"nvrWeb":   u"",
															u"unixDevs": u"",
															u"unixUD":   u"",
															u"webCTRL":  u""
														}
		self.connectParamsDefault[u"PassWd"]			= {	u"unixDevs": u"",
															u"unixUD":   u"",
															u"unixNVR":  u"",
															u"nvrWeb":   u"",
															u"unixDevs": u"",
															u"unixUD":   u"",
															u"webCTRL":  u""
														}
		self.tryHTTPPorts 		= [u"443",u"8443"]
		self.HTTPretCodes		= { u"200": {u"os":u"unifi_os", u"unifiApiLoginPath":u"/api/auth/login", u"unifiApiWebPage":u"/proxy/network/api/s" },
									u"302": {u"os":u"std",      u"unifiApiLoginPath":u"/api/login",      u"unifiApiWebPage":u"/api/s" }  }
 		self.OKControllerOS = [u"std",u"unifi_os"]

		self.connectParams = copy.copy(self.connectParamsDefault)
		try: 	
			xx = json.loads(self.pluginPrefs.get(u"connectParams",u"{}"))
			if xx != {}:
				self.connectParams = copy.copy(xx)
			for item1 in self.connectParamsDefault:
				if item1 not in self.connectParams:
					self.connectParams[item1] = copy.deepcopy(self.connectParamsDefault[item1])
				else:
					for item2 in self.connectParamsDefault[item1]:
						if item2 not in self.connectParams[item1]:
							self.connectParams[item1][item2] = copy.copy(self.connectParamsDefault[item1][item2])

				if item1 in [u"startDictToken",u"endDictToken"]:
					self.connectParams[item1] = copy.deepcopy(self.connectParamsDefault[item1])
		except:	
			pass

		if self.connectParams[u"UserID"][u"unixDevs"] == "": 	self.connectParams[u"UserID"][u"unixDevs"] = self.pluginPrefs.get(u"unifiUserID","")
		if self.connectParams[u"UserID"][u"unixUD"]   == "": 	self.connectParams[u"UserID"][u"unixUD"]   = self.pluginPrefs.get(u"unifiUserIDUDM","")
		if self.connectParams[u"UserID"][u"unixNVR"]  == "": 	self.connectParams[u"UserID"][u"unixNVR"]  = self.pluginPrefs.get(u"nvrUNIXUserID","")
		if self.connectParams[u"UserID"][u"nvrWeb"]   == "": 	self.connectParams[u"UserID"][u"nvrWeb"]   = self.pluginPrefs.get(u"nvrWebUserID","")
		if self.connectParams[u"PassWd"][u"webCTRL"]  == "": 	self.connectParams[u"PassWd"][u"nvrWeb"]   = self.pluginPrefs.get(u"unifiCONTROLLERUserID","")

		if self.connectParams[u"PassWd"][u"unixDevs"] == "": 	self.connectParams[u"PassWd"][u"unixDevs"] = self.pluginPrefs.get(u"unifiPassWd","")
		if self.connectParams[u"PassWd"][u"unixUD"]   == "": 	self.connectParams[u"PassWd"][u"unixUD"]   = self.pluginPrefs.get(u"unifiPassWdUDM","")
		if self.connectParams[u"PassWd"][u"unixNVR"]  == "": 	self.connectParams[u"PassWd"][u"unixNVR"]  = self.pluginPrefs.get(u"nvrUNIXPassWd","")
		if self.connectParams[u"PassWd"][u"nvrWeb"]   == "": 	self.connectParams[u"PassWd"][u"nvrWeb"]   = self.pluginPrefs.get(u"nvrWebPassWd","")
		if self.connectParams[u"PassWd"][u"webCTRL"]  == "": 	self.connectParams[u"PassWd"][u"nvrWeb"]   = self.pluginPrefs.get(u"unifiCONTROLLERPassWd","")
		##indigo.server.log(u" connectParams:{}".format(self.connectParams))

		self.stop 											= []
		self.PROTECT 										= {}


		self.vboxPath										= self.completePath(self.pluginPrefs.get(u"vboxPath",    		"/Applications/VirtualBox.app/Contents/MacOS/"))
		self.changedImagePath								= self.completePath(self.pluginPrefs.get(u"changedImagePath", 	self.MAChome))
		self.videoPath										= self.completePath(self.pluginPrefs.get(u"videoPath",    		"/Volumes/data4TB/Users/karlwachs/video/"))
		self.unifiNVRSession								= ""
		self.nvrVIDEOapiKey									= self.pluginPrefs.get(u"nvrVIDEOapiKey","")

		self.copyProtectsnapshots							= self.pluginPrefs.get(u"copyProtectsnapshots","on")
		self.refreshProtectCameras							= float(self.pluginPrefs.get(u"refreshProtectCameras",180.))
		self.protecEventSleepTime 							= float(self.pluginPrefs.get(u"protecEventSleepTime",4.))
		self.vmMachine										= self.pluginPrefs.get(u"vmMachine",  "")
		self.vboxPath										= self.completePath(self.pluginPrefs.get(u"vboxPath",    		"/Applications/VirtualBox.app/Contents/MacOS/"))
		self.vmDisk											= self.pluginPrefs.get(u"vmDisk",  								"/Volumes/data4TB/Users/karlwachs/VirtualBox VMs/ubuntu/NewVirtualDisk1.vdi")
		self.mountPathVM									= self.pluginPrefs.get(u"mountPathVM", "/home/yourid/osx")
		self.videoPath										= self.completePath(self.pluginPrefs.get(u"videoPath",    		"/Volumes/data4TB/Users/karlwachs/video/"))
		self.unifiNVRSession								= ""

		self.menuXML										= json.loads(self.pluginPrefs.get(u"menuXML", "{}"))
		self.pluginPrefs[u"menuXML"]						= json.dumps(self.menuXML)
		self.restartRequest									= {}
		self.lastMessageReceivedInListener					= {}
		self.blockAccess 									= []
		self.waitForMAC2vendor 								= False
		self.enableMACtoVENDORlookup						= int(self.pluginPrefs.get(u"enableMACtoVENDORlookup","21"))
		if self.enableMACtoVENDORlookup != "0":
			self.M2V 										= MAC2Vendor.MAP2Vendor(pathToMACFiles=self.indigoPreferencesPluginDir+"mac2Vendor/", refreshFromIeeAfterDays = self.enableMACtoVENDORlookup, myLogger = self.indiLOG.log )
			self.waitForMAC2vendor 							= self.M2V.makeFinalTable()


		self.enableSqlLogging								= self.pluginPrefs.get(u"enableSqlLogging",True)
		self.pluginPrefs[u"createUnifiDevicesCounter"]		= int(self.pluginPrefs.get(u"createUnifiDevicesCounter",0))

		self.lastupdateDevStateswRXTXbytes					= time.time() - 100
		self.updateDescriptions								= self.pluginPrefs.get(u"updateDescriptions", True)
		self.ignoreNeighborForFing							= self.pluginPrefs.get(u"ignoreNeighborForFing", True)
		self.ignoreNewNeighbors								= self.pluginPrefs.get(u"ignoreNewNeighbors", False)
		self.ignoreNewClients								= self.pluginPrefs.get(u"ignoreNewClients", False)
		self.enableFINGSCAN									= self.pluginPrefs.get(u"enableFINGSCAN", False)
		self.count_APDL_inPortCount							= self.pluginPrefs.get(u"count_APDL_inPortCount", "1")
		self.sendUpdateToFingscanList						= {}
		self.enableBroadCastEvents							= self.pluginPrefs.get(u"enableBroadCastEvents", "0")
		self.sendBroadCastEventsList						= []
		self.unifiCloudKeySiteName							= self.pluginPrefs.get(u"unifiCloudKeySiteName", "")
		self.unifiCloudKeyListOfSiteNames					= json.loads(self.pluginPrefs.get(u"unifiCloudKeyListOfSiteNames", "[]"))
		self.unifiCloudKeyIP								= self.pluginPrefs.get(u"unifiCloudKeyIP", "")
		self.csrfToken 										= ""
		self.numberForUDM									= {u"AP":4,u"SW":12}

		self.refreshCallbackMethodAlreadySet 				= u"no" 

		self.unifiControllerOS 								= ""
		self.unifiApiWebPage								= ""
		self.unifiApiLoginPath								= ""
		self.overWriteControllerPort						= self.pluginPrefs.get(u"overWriteControllerPort", "")
		self.lastPortNumber									= ""
		self.unifiCloudKeyPort								= ""
		self.unifiControllerType							= self.pluginPrefs.get(u"unifiControllerType", "std")
		self.unifiCloudKeyMode								= self.pluginPrefs.get(u"unifiCloudKeyMode", "ON")

		if self.unifiControllerType == "off" or self.unifiCloudKeyMode	== "off" or self.connectParams[u"UserID"][u"webCTRL"] == "":
			self.unifiCloudKeyMode = "off"
			self.pluginPrefs[u"unifiCloudKeyMode"] = ""
			self.unifiControllerType = "off"
			self.pluginPrefs[u"unifiControllerType"] = ""
			self.connectParams[u"UserID"][u"nvrWeb"]  = ""

		if self.unifiControllerType.find(u"UDM") > -1:
			self.unifiCloudKeyMode							= self.pluginPrefs.get(u"unifiCloudKeyMode", "ON")
			if self.unifiControllerType.find(u"UDM") > -1:
				self.unifiCloudKeyMode == u"ON"
				self.pluginPrefs[u"unifiCloudKeyMode"] 		= u"ON"

		try:
			self.controllerWebEventReadON 					= int(self.pluginPrefs.get(u"controllerWebEventReadON",u"-1"))
		except:
			self.controllerWebEventReadON  					= -1
		if self.unifiControllerType == u"UDMpro": 
			self.controllerWebEventReadON  					= -1

		self.unifiControllerBackupON						= self.pluginPrefs.get(u"unifiControllerBackupON", False)
		self.ControllerBackupPath							= self.pluginPrefs.get(u"ControllerBackupPath", "")

		try: self.readBuffer								= int(self.pluginPrefs.get(u"readBuffer", 32767))
		except: self.readBuffer								= 32767
		self.lastCheckForCAMERA								= 0
		self.saveCameraEventsLastCheck						= 0
		self.cameraEventWidth								= int(self.pluginPrefs.get(u"cameraEventWidth", "720"))
		self.imageSourceForEvent							= self.pluginPrefs.get(u"imageSourceForEvent", "noImage")
		self.imageSourceForSnapShot							= self.pluginPrefs.get(u"imageSourceForSnapShot", "noImage")

		self.listenStart									= {}
		self.useStrictToLogin								= self.pluginPrefs.get(u"useStrictToLogin", False)
		self.unifiControllerSession							= ""

		self.curlPath										= self.pluginPrefs.get(u"curlPath", "/usr/bin/curl")
		if len(self.curlPath) < 4:
			self.curlPath									= "/usr/bin/curl"
			self.pluginPrefs[u"curlPath"] 					= self.curlPath

		self.requestOrcurl										= self.pluginPrefs.get(u"requestOrcurl", u"curl")

		self.expectPath 									= "/usr/bin/expect"

		self.restartIfNoMessageSeconds						= 130 #int(self.pluginPrefs.get(u"restartIfNoMessageSeconds", 130))
		self.expirationTime									= int(self.pluginPrefs.get(u"expirationTime", 120) )
		self.expTimeMultiplier								= float(self.pluginPrefs.get(u"expTimeMultiplier", 2))

		self.loopSleep										= 5     # float(self.pluginPrefs.get(u"loopSleep", 8))
		self.timeoutDICT									= u"10" #unicode(int(self.pluginPrefs.get(u"timeoutDICT", 10)))
		self.folderNameCreated								= self.pluginPrefs.get(u"folderNameCreated",   "UNIFI_created")
		self.folderNameNeighbors							= self.pluginPrefs.get(u"folderNameNeighbors", "UNIFI_neighbors")
		self.folderNameVariables							= self.pluginPrefs.get(u"folderNameVariables", "UNIFI")
		self.folderNameSystem								= self.pluginPrefs.get(u"folderNameSystem",	   "UNIFI_system")
		self.fixExpirationTime								= self.pluginPrefs.get(u"fixExpirationTime",	True)
		self.MACignorelist									= {}
		self.MACSpecialIgnorelist							= {}
		self.HANDOVER										= {}
		self.lastUnifiCookieCurl							= 0
		self.lastUnifiCookieRequests						= 0
		self.lastNVRCookie									= 0
		self.pendingCommand									= []
		self.groupStatusList								= {"Group"+unicode(i):{"members":{},"allHome":False,"allAway":False,"oneHome":False,"oneAway":False,"nHome":0,"nAway":0} for i in range(_GlobalConst_numberOfGroups )}
		self.groupStatusListALL								= {"nHome":0,"nAway":0,"anyChange":False}

		self.triggerList									= []
		self.statusChanged									= 0
		self.msgListenerActive								= {}

		self.devsEnabled									= {}
		self.debugDevs										= {}
		self.ipNumbersOf									= {}
		self.deviceUp										= {}
		self.numberOfActive									= {}


		self.createEntryInUnifiDevLogActive					= True #self.pluginPrefs.get(u"createEntryInUnifiDevLogActive",	False)
		self.lastcreateEntryInUnifiDevLog 					= time.time()

		self.updateStatesList								= {}
		self.logCount										= {}
		self.ipNumbersOf[u"AP"]								= ["" for nn in range(_GlobalConst_numberOfAP)]
		self.devsEnabled[u"AP"]								= [False for nn in range(_GlobalConst_numberOfAP)]
		self.debugDevs[u"AP"]								= [False for nn in range(_GlobalConst_numberOfAP)]

		self.ipNumbersOf[u"SW"]								= ["" for nn in range(_GlobalConst_numberOfSW)]
		self.devsEnabled[u"SW"]								= [False for nn in range(_GlobalConst_numberOfSW)]
		self.debugDevs[u"SW"]								= [False for nn in range(_GlobalConst_numberOfSW)]


		self.devNeedsUpdate									= []

		self.MACloglist										= {}

		self.readDictEverySeconds							= {}
		self.readDictEverySeconds[u"AP"]					= 60 #unicode(int(self.pluginPrefs.get(u"readDictEverySecondsAP", 60) ))
		self.readDictEverySeconds[u"GW"]					= 60 #unicode(int(self.pluginPrefs.get(u"readDictEverySecondsGW", 120) ))
		self.readDictEverySeconds[u"SW"]					= 60 #unicode(int(self.pluginPrefs.get(u"readDictEverySecondsSW", 120) ))
		self.readDictEverySeconds[u"UD"]					= 60 #unicode(int(self.pluginPrefs.get(u"readDictEverySecondsUD", 60) ))
		self.readDictEverySeconds[u"DB"]					= 40 #unicode(int(self.pluginPrefs.get(u"readDictEverySecondsDB", 40) ))
		self.getcontrollerDBForClientsLast					= 0
		self.devStateChangeList								= {}
		self.deviceUp[u"AP"]								= {}
		self.deviceUp[u"SW"]								= {}
		self.deviceUp[u"GW"]								= {}
		self.deviceUp[u"VD"]								= {}
		self.deviceUp[u"UD"]								= {}
		self.version			 							= self.getParamsFromFile(self.indigoPreferencesPluginDir+"dataVersion", default=0)

		self.restartListenerEvery							= float(self.pluginPrefs.get(u"restartListenerEvery", "999999999"))

		#####  check AP parameters
		self.numberOfActive[u"AP"] =0
		for i in range(_GlobalConst_numberOfAP):
			ip0 											= self.pluginPrefs.get(u"ip"+unicode(i), "")
			ac												= self.pluginPrefs.get(u"ipON"+unicode(i), "")
			deb												= self.pluginPrefs.get(u"debAP"+unicode(i), "")
			if not self.isValidIP(ip0): ac 					= False
			self.deviceUp[u"AP"][ip0] 						= time.time()
			self.ipNumbersOf[u"AP"][i] 						= ip0
			self.debugDevs[u"AP"][i] 						= deb
			if ac:
				self.devsEnabled[u"AP"][i]					= True
				self.numberOfActive[u"AP"] 					+= 1
 
		#####  check switch parameters
		self.numberOfActive[u"SW"]									= 0
		for i in range(_GlobalConst_numberOfSW):
			ip0														= self.pluginPrefs.get(u"ipSW" + unicode(i), "")
			ac														= self.pluginPrefs.get(u"ipSWON" + unicode(i), "")
			deb														= self.pluginPrefs.get(u"debSW"+unicode(i), "")
			if not self.isValidIP(ip0): ac 							= False
			self.deviceUp[u"SW"][ip0] 								= time.time()
			self.ipNumbersOf[u"SW"][i] 								= ip0
			self.debugDevs[u"SW"][i] 								= deb
			if ac:
				self.devsEnabled[u"SW"][i] 							= True
				self.numberOfActive[u"SW"] 							+= 1

		#####  check UGA parameters
		ip0 														= self.pluginPrefs.get(u"ipUGA",  "")
		ac															= self.pluginPrefs.get(u"ipUGAON",False)
		self.debugDevs[u"GW"] 										= self.pluginPrefs.get(u"debGW",False)


		if self.isValidIP(ip0) and ac:
			self.ipNumbersOf[u"GW"] 								= ip0
			self.devsEnabled[u"GW"] 								= True
			self.deviceUp[u"GW"][ip0] 								= time.time()
		else:
			self.ipNumbersOf[u"GW"] 								= ""
			self.devsEnabled[u"GW"]									= False

		self.enablecheckforUnifiSystemDevicesState					= self.pluginPrefs.get(u"enablecheckforUnifiSystemDevicesState","off")

		#####  check DB parameters
		ip0 														= self.pluginPrefs.get(u"unifiCloudKeyIP",  "")
		ac															= self.pluginPrefs.get(u"unifiCloudKeyMode","ON")
		self.getcontrollerDBForClientsPrevious						= time.time() - 10
		self.useDBInfoForWhichDevices								= self.pluginPrefs.get(u"useDBInfoForWhichDevices","all")
		if self.isValidIP(self.unifiCloudKeyIP) and (ac.find("ON") > -1 or ac.find("UDM") or self.useDBInfoForWhichDevices in ["all","perDevice"]):
			self.unifiCloudKeyMode = "ON"
			self.pluginPrefs[u"unifiCloudKeyMode"] = "ON"
			self.devsEnabled[u"DB"] = True
		else:
			self.devsEnabled[u"DB"]	= False

		#####  check UDM parameters
		ip0 														= self.pluginPrefs.get(u"ipUDM",  "")
		ac															= self.pluginPrefs.get(u"ipUDMON",False)
		self.debugDevs[u"UD"] 										= self.pluginPrefs.get(u"debUD",False)
		self.ipNumbersOf[u"UD"] 									= ip0
		self.deviceUp[u"UD"]										= time.time()

		if self.isValidIP(ip0) and ac:
			self.devsEnabled[u"UD"] 								= True
			self.ipNumbersOf[u"SW"][self.numberForUDM[u"SW"]]		= ip0
			self.ipNumbersOf[u"AP"][self.numberForUDM[u"AP"]]		= ip0
			self.ipNumbersOf[u"GW"] 							  	= ip0
			self.devsEnabled[u"SW"][self.numberForUDM[u"SW"]] 		= True
			self.devsEnabled[u"AP"][self.numberForUDM[u"AP"]] 		= True
			self.numberOfActive[u"SW"] 								= max(1,self.numberOfActive[u"SW"] )
			self.numberOfActive[u"AP"] 								= max(1,self.numberOfActive[u"AP"] )
			self.pluginPrefs[u"ipON"] 								= True
			self.pluginPrefs[u"ipSWON"] 							= True
			self.pluginPrefs[u"ip"+unicode(self.numberForUDM[u"AP"])]   = ip0
			self.pluginPrefs[u"ipSW"+unicode(self.numberForUDM[u"SW"])] = ip0
		else:
			self.devsEnabled[u"UD"] = False



		#####  check video parameters
		self.cameraSystem										= self.pluginPrefs.get(u"cameraSystem", "off")

		self.cameras							 				= {}
		self.ipNumbersOf[u"VD"] 								= ""
		self.VIDEOUP											= 0
		self.unifiVIDEONumerOfEvents 							= 0
		if self.cameraSystem == "nvr":
			try:	self.unifiVIDEONumerOfEvents 				= int(self.pluginPrefs.get(u"unifiVIDEONumerOfEvents", 1000))
			except: self.unifiVIDEONumerOfEvents				= 1000
			self.cameras						 				= {}
			self.saveCameraEventsStatus			 				= False

			ip0 												= self.pluginPrefs.get(u"nvrIP", "192.168.1.x")
			self.ipNumbersOf[u"VD"] 							= ip0
			self.VIDEOUP										= 0
			if self.isValidIP(ip0) and self.connectParams[u"UserID"][u"unixNVR"] != "" and self.connectParams[u"PassWd"][u"unixNVR"] != "":
				self.VIDEOUP	 								= time.time()
		elif self.cameraSystem == "protect":
			pass
		else:
			pass

		self.lastCheckForNVR 								= 0

		self.getFolderId()

		self.readSuspend()


		for ll in range(len(self.ipNumbersOf[u"AP"])):
			self.killIfRunning(self.ipNumbersOf[u"AP"][ll],u"")
		for ll in range(len(self.ipNumbersOf[u"SW"])):
			self.killIfRunning(self.ipNumbersOf[u"SW"][ll],u"")
		self.killIfRunning(self.ipNumbersOf[u"GW"], "")


		self.readDataStats()  # must come before other dev/states updates ...

		self.groupStatusINIT()
		self.setGroupStatus(init=True)
		self.readCamerasStats()
		self.readMACdata()
		self.checkDisplayStatus()
		self.getMACloglist()

		self.pluginStartTime 								= time.time()+150


		self.checkforUnifiSystemDevicesState 				= "start"

		self.killIfRunning("", "")

		try: 	os.mkdir(self.indigoPreferencesPluginDir+"backup")
		except: pass

		return

	
	####-----------------	 ---------
	def getMACloglist(self):
		try:
			self.MACloglist= self.getParamsFromFile(self.indigoPreferencesPluginDir+"MACloglist",  default ={})
			if self.MACloglist !={}:
				self.indiLOG.log(10,u"start track-logging for MAC#s {}".format(self.MACloglist) )
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

		return

	####-----------------	 ---------
	def checkDisplayStatus(self):
		try:
			for dev in indigo.devices.iter(self.pluginId):
				if u"displayStatus" not in dev.states: continue

				if u"MAC" in dev.states and dev.deviceTypeId == u"UniFi" and self.testIgnoreMAC(dev.states[u"MAC"], fromSystem="checkDisp"):
					if dev.states[u"displayStatus"].find(u"ignored") ==-1:
						dev.updateStateOnServer("displayStatus",self.padDisplay(u"ignored")+datetime.datetime.now().strftime(u"%m-%d %H:%M:%S"))
						if unicode(dev.displayStateImageSel) !="PowerOff":
							dev.updateStateImageOnServer(indigo.kStateImageSel.PowerOff)
				else:
					self.exeDisplayStatus(dev, dev.states[u"status"], force =False)


				old = dev.states[u"displayStatus"].split(u" ")
				if len(old) ==3:
					new = self.padDisplay(old[0].strip())+dev.states[u"lastStatusChange"][5:]
					if dev.states[u"displayStatus"] != new:
						dev.updateStateOnServer(u"displayStatus",new)
				else:
					dev.updateStateOnServer(u"displayStatus",self.padDisplay(old[0].strip())+dev.states[u"lastStatusChange"][5:])
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))


		return



	####-----------------	 ---------
	def isValidIP(self, ip0):
		if ip0 == u"localhost": 						return True

		ipx = ip0.split(u".")
		if len(ipx) != 4:								return False

		else:
			for ip in ipx:
				try:
					if int(ip) < 0 or  int(ip) > 255: 	return False
				except:
														return False
		return True

	####-----------------	 ---------
	def fixIP(self, ip): # make last number always 3 digits for sorting
		if len(ip) < 7: return ip
		ipx = ip.split(u"/")[0].split(u".")
		ipx[3] = "%03d" % (int(ipx[3]))
		return u".".join(ipx)


	####-----------------	 ---------
	def isValidMAC(self, mac):
		xxx = mac.split(u":")
		if len(xxx) != 6:			return False
		else:
			for xx in xxx:
				if len(xx) != 2: 	return False
				try: 	int(xx, 16)
				except: 			return False
		return True

	####-----------------	 ---------
	def checkMAC(self, MAC):
		if self.isValidMAC(MAC): return MAC
		macs = MAC.split(":")
		for nn in range(len(macs)):
			mac = macs[nn]
			if len(mac) < 2: macs[nn] = u"0" + mac
		return ":".join(macs)

####-------------------------------------------------------------------------####
	def getParamsFromFile(self,newName, oldName="", default ={}): # called from read config for various input files
			out = copy.copy(default)
			if os.path.isfile(newName):
				try:
					f = open(newName, u"r")
					out	 = json.loads(f.read())
					f.close()
					if oldName !="" and os.path.isfile(oldName):
						os.system("rm "+oldName)
				except	Exception, e:
					self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
					out = copy.copy(default)
			else:
				out = copy.copy(default)
			if oldName !="" and os.path.isfile(oldName):
				try:
					f = open(oldName, u"r")
					out	 = json.loads(f.read())
					f.close()
					os.system("rm "+oldName)
				except	Exception, e:
					self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
					out = copy.copy(default)
			return out


####-------------------------------------------------------------------------####
	def writeJson(self, data, fName="", sort = True, doFormat=False ):
		try:

			if format:
				out = json.dumps(data, sort_keys=sort, indent=2)
			else:
				out = json.dumps(data, sort_keys=sort)

			if fName !="":
				f=open(fName,u"w")
				f.write(out)
				f.close()
			return out

		except	Exception, e:
			self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return ""



	####-----------------  update state lists ---------
	def deviceStartComm(self, dev):
		if self.decideMyLog(u"Logic"): self.indiLOG.log(10,u"starting device:  {}  {}  {}".format(dev.name, dev.id), dev.states[u"MAC"])

		if	self.pluginState == "init":
			dev.stateListOrDisplayStateIdChanged()

			if self.version < 2.0:
				props = dev.pluginProps
				self.indiLOG.log(10,u"Checking for deviceType Update: "+ dev.name )
				if u"SupportsOnState" not in props:
					self.indiLOG.log(10,u" processing: "+ dev.name)
					dev = indigo.device.changeDeviceTypeId(dev, dev.deviceTypeId)
					dev.replaceOnServer()
					dev = indigo.devices[dev.id]
					props = dev.pluginProps
					props[u"SupportsSensorValue"] 		= False
					props[u"SupportsOnState"] 			= True
					props[u"AllowSensorValueChange"] 	= False
					props[u"AllowOnStateChange"] 		= False
					props[u"SupportsStatusRequest"] 		= False
					self.indiLOG.log(10,unicode(dev.pluginProps))
					dev.replacePluginPropsOnServer(props)
					dev= indigo.devices[dev.id]
					#self.myLog( text=unicode(dev.pluginProps))
					#self.myLog( text=unicode(dev.states))

					if (dev.states[u"status"].lower()).lower() in [u"up",u"rec",u"ON"]:
						dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOn)
					elif (dev.states[u"status"].lower()).find(u"down")==0:
						dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOff)
					else:
						dev.updateStateImageOnServer(indigo.kStateImageSel.SensorTripped)
					dev.replaceOnServer()
					#dev= indigo.devices[dev.id]
					dev.updateStateOnServer(u"onOffState",value= (dev.states[u"status"].lower()) in[u"up",u"rec",u"ON"], uiValue=dev.states[u"displayStatus"] )
					self.indiLOG.log(10,u"SupportsOnState after replacePluginPropsOnServer")

			isType={u"UniFi":u"isUniFi",u"camera":u"isCamera",u"gateway":u"isGateway",u"Device-SW":u"isSwitch",u"Device-AP":u"isAP",u"neighbor":u"isNeighbor",u"NVR":u"isNVR"}
			props = dev.pluginProps
			devTid = dev.deviceTypeId
			##if dev.name.find(u"SW") > -1: self.myLog( text=u"deviceStartComm checking on "+dev.name+" "+devTid)
			for iT in isType:
				testId = devTid[0:min( len(iT),len(devTid) ) ]
				if iT == testId:
					##if dev.name.find(u"SW") > -1:	self.myLog( text= iT+ u" == "+testId+ " props"+ unicode(props))
					isT = isType[iT]
					if isT not in props or props[isT] != True:
						props[isT] = True
						dev.replacePluginPropsOnServer(props)
						##if dev.name.find(u"SW") > -1:	self.myLog( text= u" updateing")
					break

			if u"enableBroadCastEvents" not in props:
				props = dev.pluginProps
				props[u"enableBroadCastEvents"] = u"0"
				dev.replacePluginPropsOnServer(props)





		elif self.pluginState == u"run":
			self.devNeedsUpdate.append(unicode(dev.id))

		return

	####-----------------	 ---------
	def deviceStopComm(self, dev):
		if	self.pluginState != u"stop":
			self.devNeedsUpdate.append(unicode(dev.id))
			if self.decideMyLog(u"Logic"): self.indiLOG.log(10,u"stopping device:  {}  {}".format(dev.name, dev.id) )

	####-----------------	 ---------
	def didDeviceCommPropertyChange(self, origDev, newDev):
		#if origDev.pluginProps['xxx'] != newDev.pluginProps['address']:
		#	 return True
		return False
	###########################		INIT	## END	 ########################


	####-----------------	 ---------
	def getFolderId(self):

			self.folderNameIDCreated		= 0
			self.folderNameIDSystemID	   = 0
			try:
				self.folderNameIDCreated = indigo.devices.folders.getId(self.folderNameCreated)
			except:
				pass
			if self.folderNameIDCreated ==0:
				try:
					ff = indigo.devices.folder.create(self.folderNameCreated)
					self.folderNameIDCreated = ff.id
				except:
					self.folderNameIDCreated = 0

			try:
				self.folderNameIDSystemID = indigo.devices.folders.getId(self.folderNameSystem)
			except:
				pass
			if self.folderNameIDSystemID ==0:
				try:
					ff = indigo.devices.folder.create(self.folderNameSystem)
					self.folderNameIDSystemID = ff.id
				except:
					self.folderNameIDSystemID = 0

			try:
				self.folderNameIDNeighbors = indigo.devices.folders.getId(self.folderNameNeighbors)
			except:
				pass
			if self.folderNameIDNeighbors ==0:
				try:
					ff = indigo.devices.folder.create(self.folderNameNeighbors)
					self.folderNameIDNeighbors = ff.id
				except:
					self.folderNameIDNeighbors = 0

			try:
				self.folderNameIDVariables = indigo.variables.folders.getId(self.folderNameVariables)
			except:
				pass
			if self.folderNameIDVariables ==0:
				try:
					ff = indigo.variables.folder.create(self.folderNameVariables)
					self.folderNameIDVariables = ff.id
				except:
					self.folderNameIDVariables = 0


			return


	def getMenuActionConfigUiValues(self):
		valuesDict = indigo.Dict()
		errorMsgDict = indigo.Dict()
		valuesDict["caeraSystemType"] = self.xx
		return (valuesDict, errorMsgDict)


	####-----------------	 ---------
	def validateDeviceConfigUi(self, valuesDict, typeId, devId):
		try:
			if self.decideMyLog(u"Logic"): self.indiLOG.log(10,u"Validate Device dict:, devId:{}  vdict:{}".format(devId,valuesDict) )
			self.devNeedsUpdate.append(int(devId))

			dev = indigo.devices[int(devId)]
			if u"groupMember" in dev.states:
				gMembers =""
				for group in  _GlobalConst_groupList:
					if group in valuesDict:
						if unicode(valuesDict[group]).lower() == u"true":
							gMembers += group+","
							self.groupStatusList[group][u"members"][unicode(devId)] = True
					elif unicode(devId) in	self.groupStatusList[group][u"members"]: del self.groupStatusList[group][u"members"][unicode(devId)]
				self.updateDevStateGroupMembers(dev,gMembers)
			return (True, valuesDict)
		except	Exception, e:
			self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		errorDict = valuesDict
		return (False, valuesDict, errorDict)


	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine returns the XML for the PluginConfig.xml by default; you probably don't
	# want to use this unless you have a need to customize the XML (again, uncommon)
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	def xxgetPrefsConfigUiXml(self):
		return super(Plugin, self).getPrefsConfigUiXml()

	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine returns the UI values for the configuration dialog; the default is to
	# simply return the self.pluginPrefs dictionary. It can be used to dynamically set
	# defaults at run time
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	def getPrefsConfigUiValues(self):
		try:
			(valuesDict, errorsDict) = super(Plugin, self).getPrefsConfigUiValues()

			valuesDict[u"unifiUserID"]				= self.connectParams[u"UserID"][u"unixDevs"]
			valuesDict[u"unifiUserIDUDM"]			= self.connectParams[u"UserID"][u"unixUD"]
			valuesDict[u"nvrUNIXUserID"]			= self.connectParams[u"UserID"][u"unixNVR"]
			valuesDict[u"nvrWebUserID"]				= self.connectParams[u"UserID"][u"nvrWeb"]
			valuesDict[u"unifiCONTROLLERUserID"]	= self.connectParams[u"UserID"][u"webCTRL"]

			valuesDict[u"unifiPassWd"]				= self.connectParams[u"PassWd"][u"unixDevs"]
			valuesDict[u"unifiPassWdUDM"]			= self.connectParams[u"PassWd"][u"unixUD"]
			valuesDict[u"nvrUNIXPassWd"]			= self.connectParams[u"PassWd"][u"unixNVR"]
			valuesDict[u"unifiCONTROLLERPassWd"]	= self.connectParams[u"PassWd"][u"webCTRL"]


			valuesDict[u"GWtailEnable"]				= self.connectParams[u"enableListener"][u"GWtail"]
			valuesDict[u"refreshCallbackMethod"]	= "setfilterunifiCloudKeyListOfSiteNames"
			self.refreshCallbackMethodAlreadySet	= "no"

		except	Exception, e:
			self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return (valuesDict, errorsDict)

	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine is called once the user has exited the preferences dialog
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	def closedPrefsConfigUi(self, valuesDict, userCancelled):
		# if the user saved his/her preferences, update our member variables now
		if userCancelled == False:
			pass
		return


	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine is called once the user has exited the preferences dialog
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	####-----------------  set the geneeral config parameters---------
	def validatePrefsConfigUi(self, valuesDict):

		try:
			rebootRequired									= ""
			self.lastUnifiCookieCurl						= 0
			self.lastUnifiCookieRequests					= 0

			self.lastNVRCookie								= 0
			self.checkforUnifiSystemDevicesState			= u"validateConfig"
			self.enableSqlLogging							= valuesDict[u"enableSqlLogging"]
			self.enableFINGSCAN								= valuesDict[u"enableFINGSCAN"]
			self.count_APDL_inPortCount						= valuesDict[u"count_APDL_inPortCount"]

			self.enableBroadCastEvents						= valuesDict[u"enableBroadCastEvents"]
			self.sendBroadCastEventsList					= []
			self.ignoreNewNeighbors							= valuesDict[u"ignoreNewNeighbors"]
			self.ignoreNewClients							= valuesDict[u"ignoreNewClients"]
			#self.loopSleep									= float(valuesDict[u"loopSleep"])
			self.unifiControllerBackupON					= valuesDict[u"unifiControllerBackupON"]
			self.ControllerBackupPath						= valuesDict[u"ControllerBackupPath"]

			self.unifiControllerOS							= ""
			self.copyProtectsnapshots						= valuesDict[u"copyProtectsnapshots"]
			self.refreshProtectCameras						= float(valuesDict[u"refreshProtectCameras"])
			self.protecEventSleepTime						= float(valuesDict[u"protecEventSleepTime"])
		
			self.cameraEventWidth							= int(valuesDict[u"cameraEventWidth"])
			self.imageSourceForEvent						= valuesDict[u"imageSourceForEvent"]
			self.imageSourceForSnapShot						= valuesDict[u"imageSourceForSnapShot"]
			try: self.readBuffer							= int(valuesDict[u"readBuffer"])
			except: self.readBuffer							= 32767


			if self.connectParams[u"UserID"][u"unixDevs"]	!= valuesDict[u"unifiUserID"]:				rebootRequired += u" unifiUserID changed;"
			if self.connectParams[u"PassWd"][u"unixDevs"]	!= valuesDict[u"unifiPassWd"]:				rebootRequired += u" unifiPassWd changed;"
			if self.connectParams[u"UserID"][u"unixUD"] 	!= valuesDict[u"unifiUserIDUDM"]:			rebootRequired += u" unifiUserIDUDM changed;"
			if self.connectParams[u"PassWd"][u"unixUD"] 	!= valuesDict[u"unifiPassWdUDM"]:			rebootRequired += u" unifiPassWdUDM changed;"

			self.connectParams[u"UserID"][u"unixUD"]		= valuesDict[u"unifiUserIDUDM"]
			self.connectParams[u"PassWd"][u"unixUD"]		= valuesDict[u"unifiPassWdUDM"]
			self.useStrictToLogin							= valuesDict[u"useStrictToLogin"]

			self.connectParams[u"UserID"][u"webCTRL"]		= valuesDict[u"unifiCONTROLLERUserID"]
			self.connectParams[u"PassWd"][u"webCTRL"]		= valuesDict[u"unifiCONTROLLERPassWd"]

			self.connectParams[u"UserID"][u"unixDevs"]		= valuesDict[u"unifiUserID"]
			self.connectParams[u"PassWd"][u"unixDevs"]		= valuesDict[u"unifiPassWd"]
			self.restartListenerEvery						= float(valuesDict[u"restartListenerEvery"])


			self.curlPath									= valuesDict[u"curlPath"]
			self.requestOrcurl								= valuesDict[u"requestOrcurl"]


			self.unifiCloudKeyIP							= valuesDict[u"unifiCloudKeyIP"]
			if self.overWriteControllerPort != valuesDict[u"overWriteControllerPort"]:
				rebootRequired								+= u"controller port overwrite changed"
			self.overWriteControllerPort					= valuesDict[u"overWriteControllerPort"]

			self.unifiCloudKeySiteName						= valuesDict[u"unifiCloudKeySiteName"]


			if valuesDict[u"unifiControllerType"] == u"off" or valuesDict[u"unifiCloudKeyMode"] == u"off" or self.connectParams[u"UserID"][u"webCTRL"] == "":
				self.unifiControllerType 					= u"off"
				self.unifiCloudKeySiteName					= u"off"
				self.connectParams[u"UserID"][u"webCTRL"]	= ""
				valuesDict[u"unifiControllerType"]			= u"off"
				valuesDict[u"unifiCloudKeyMode"]			= u"off"
				valuesDict[u"unifiCONTROLLERUserID"]		= ""

			self.unifiControllerType						= valuesDict[u"unifiControllerType"]
			self.unifiCloudKeyMode							= valuesDict[u"unifiCloudKeyMode"]



			if type("") != self.unifiCloudKeySiteName: self.unifiCloudKeySiteName = ""
			if len(self.unifiCloudKeySiteName) < 3: self.unifiCloudKeySiteName = ""
			valuesDict[u"unifiCloudKeySiteName"] = self.unifiCloudKeySiteName



			self.ignoreNeighborForFing						= valuesDict[u"ignoreNeighborForFing"]
			self.updateDescriptions							= valuesDict[u"updateDescriptions"]
			self.folderNameCreated							= valuesDict[u"folderNameCreated"]
			self.folderNameVariables						= valuesDict[u"folderNameVariables"]
			self.folderNameNeighbors						= valuesDict[u"folderNameNeighbors"]
			self.folderNameSystem							= valuesDict[u"folderNameSystem"]
			self.getFolderId()
			if self.enableMACtoVENDORlookup != valuesDict[u"enableMACtoVENDORlookup"] and self.enableMACtoVENDORlookup == u"0":
				rebootRequired							+= u" MACVendor lookup changed; "
			self.enableMACtoVENDORlookup				= valuesDict[u"enableMACtoVENDORlookup"]

			#self.createEntryInUnifiDevLogActive			= valuesDict[u"createEntryInUnifiDevLogActive"]


	#new for UDM (pro)
			if self.unifiControllerType.find(u"UDM") > -1 and  valuesDict[u"unifiControllerType"].find(u"UDM") == -1:
				# make sure the devices are disabled when going from UDM to std. will require to edit config again
				valuesDict[u"ipsw"+unicode(self.numberForUDM[u"SW"])]	= ""
				valuesDict[u"ipSWON"+unicode(self.numberForUDM[u"SW"])]	= False
				valuesDict[u"ip"+unicode(self.numberForUDM[u"SW"])]		= ""
				valuesDict[u"ipON"+unicode(self.numberForUDM[u"SW"])] 	= False
				
				
			if self.unifiControllerType.find(u"UDM") > -1:
				self.unifiCloudKeyMode = u"ON"
				valuesDict[u"unifiCloudKeyMode"] = "ON"
			try: 	self.controllerWebEventReadON		= int(valuesDict[u"controllerWebEventReadON"])
			except: self.controllerWebEventReadON		= -1
			if self.unifiControllerType == "UDMpro":
					self.controllerWebEventReadON		= -1 

			"""
			xx											= unicode(int(valuesDict[u"timeoutDICT"]))
			if xx != self.timeoutDICT:
				rebootRequired	+= " timeoutDICT  changed; "
				self.timeoutDICT						= xx
			"""

			##
			self.debugLevel = []
			for d in _debugAreas:
				if valuesDict[u"debug"+d]: self.debugLevel.append(d)

			if False:
				for TT in[u"AP",u"GW",u"SW"]:
					try:	xx			 = unicode(int(valuesDict[u"readDictEverySeconds"+TT]))
					except: xx			 = u"120"
					if xx != self.readDictEverySeconds[TT]:
						self.readDictEverySeconds[TT]				  = xx
						valuesDict[u"readDictEverySeconds"+TT]		  = xx
						rebootRequired	+= u" readDictEverySeconds  changed; "


			if False:
				try:	xx			 = int(valuesDict[u"restartIfNoMessageSeconds"])
				except: xx			 = 500
				if xx != self.restartIfNoMessageSeconds:
					self.restartIfNoMessageSeconds					 = xx
					valuesDict[u"restartIfNoMessageSeconds"]		 = xx

			try:	self.expirationTime					= int(valuesDict[u"expirationTime"])
			except: self.expirationTime					= 120
			valuesDict[u"expirationTime"]				= self.expirationTime
			try:	self.expTimeMultiplier				= int(valuesDict[u"expTimeMultiplier"])
			except: self.expTimeMultiplier				= 2.
			valuesDict[u"expTimeMultiplier"]			= self.expTimeMultiplier

			self.fixExpirationTime						= valuesDict[u"fixExpirationTime"]

			## AP parameters
			acNew = [False for i in range(_GlobalConst_numberOfAP)]
			ipNew = ["" for i in range(_GlobalConst_numberOfAP)]
			self.numberOfActive[u"AP"] = 0
			for i in range(_GlobalConst_numberOfAP):
				ip0 = valuesDict[u"ip"+unicode(i)]
				ac	= valuesDict[u"ipON"+unicode(i)]
				self.debugDevs[u"AP"][i] = valuesDict[u"debAP"+unicode(i)]
				if not self.isValidIP(ip0): ac = False
				acNew[i]			 = ac
				ipNew[i]			 = ip0
				if ac: 
					acNew[i] = True
					self.numberOfActive[u"AP"] 	+= 1
				if acNew[i] != self.devsEnabled[u"AP"][i]:
					rebootRequired	+= u" enable/disable AP changed; "
				if ipNew[i] != self.ipNumbersOf[u"AP"][i]:
					rebootRequired	+= " Ap ipNumber  changed; "
					self.deviceUp[u"AP"][ipNew[i]] = time.time()
			self.ipNumbersOf[u"AP"] = copy.copy(ipNew)
			self.devsEnabled[u"AP"] = copy.copy(acNew)

			## Switch parameters
			acNew = [False for i in range(_GlobalConst_numberOfSW)]
			ipNew = ["" for i in range(_GlobalConst_numberOfSW)]
			self.numberOfActive[u"SW"] = 0
			for i in range(_GlobalConst_numberOfSW):
				ip0 = valuesDict[u"ipSW"+unicode(i)]
				ac	= valuesDict[u"ipSWON"+unicode(i)]
				self.debugDevs[u"SW"][i] = valuesDict[u"debSW"+unicode(i)]
				if not self.isValidIP(ip0): ac = False
				acNew[i] = ac
				ipNew[i] = ip0
				if ac: 
					acNew[i] = True
					self.numberOfActive[u"SW"] 	+= 1

				if acNew[i] != self.devsEnabled[u"SW"][i]:
					rebootRequired	+= u" enable/disable SW  changed; "
				if ipNew[i] != self.ipNumbersOf[u"SW"][i]:
					rebootRequired	+= u" SW ipNumber   changed; "
					self.deviceUp[u"SW"][ipNew[i]] = time.time()
			self.ipNumbersOf[u"SW"] = copy.copy(ipNew)
			self.devsEnabled[u"SW"]		= copy.copy(acNew)



			## UGA parameters
			ip0			= valuesDict[u"ipUGA"]
			if self.ipNumbersOf[u"GW"] != ip0:
				rebootRequired	+= " GW ipNumber   changed; "

			ac			= valuesDict[u"ipUGAON"]
			if not self.isValidIP(ip0): ac = False
			if self.devsEnabled[u"GW"] != ac:
				rebootRequired	+= u" enable/disable GW  changed; "

			self.devsEnabled[u"GW"]	   	= ac
			self.ipNumbersOf[u"GW"] 	= ip0
			self.debugDevs[u"GW"] 		= valuesDict[u"debGW"]

			if 	self.connectParams[u"enableListener"][u"GWtail"] != valuesDict[u"GWtailEnable"]:
				rebootRequired	+= u" enable/disable GW  changed; "

			self.connectParams[u"enableListener"][u"GWtail"] = valuesDict[u"GWtailEnable"]	


			## UDM parameters
			ip0			= valuesDict[u"ipUDM"]
			if self.ipNumbersOf[u"UD"] != ip0:
				rebootRequired	+= u" UDM ipNumber   changed; "

			ac			= valuesDict[u"ipUDMON"]
			if not self.isValidIP(ip0): ac = False
			if self.devsEnabled[u"UD"] != ac:
				rebootRequired	+= " enable/disable UDM changed; "

			self.devsEnabled[u"UD"]		= ac
			self.ipNumbersOf[u"UD"]		= ip0
			self.debugDevs[u"UD"]		= valuesDict[u"debUD"]
			if self.devsEnabled[u"UD"]:
				self.ipNumbersOf[u"SW"][self.numberForUDM[u"SW"]]		= ip0
				valuesDict[u"ipsw"+unicode(self.numberForUDM[u"SW"])]	= ip0
				valuesDict[u"ipSWON"+unicode(self.numberForUDM[u"SW"])] = True
				self.devsEnabled[u"SW"][self.numberForUDM[u"SW"]]		= True
				self.numberOfActive[u"SW"] 							= max(1,self.numberOfActive[u"SW"] )

				self.ipNumbersOf[u"GW"] 						  		= ip0
				valuesDict[u"ipNumbersOfGW"]						= ip0
				valuesDict[u"ipUGAON"]								= True

				if valuesDict[u"unifiControllerType"] == "UDM": ## only for UDM not for UDM-pro,has no AP
					self.ipNumbersOf[u"AP"][self.numberForUDM[u"AP"]]		= ip0
					valuesDict[u"ip"+unicode(self.numberForUDM[u"AP"])]		= ip0
					valuesDict[u"ipON"+unicode(self.numberForUDM[u"AP"])]	= True
					self.devsEnabled[u"AP"][self.numberForUDM[u"AP"]] 		= True
					self.numberOfActive[u"AP"] 								= max(1,self.numberOfActive[u"AP"] )

				valuesDict[u"ipNumbersOfGW"]								= ip0


			## video parameters
			if self.connectParams[u"UserID"][u"unixNVR"]	!= valuesDict[u"nvrUNIXUserID"]:	  rebootRequired += u" nvrUNIXUserID changed;"
			if self.connectParams[u"PassWd"][u"unixNVR"]	!= valuesDict[u"nvrUNIXPassWd"]:	  rebootRequired += u" nvrUNIXPassWd changed;"

			self.unifiVIDEONumerOfEvents	= int(valuesDict[u"unifiVIDEONumerOfEvents"])
			self.connectParams[u"UserID"][u"unixNVR"]	= valuesDict[u"nvrUNIXUserID"]
			self.connectParams[u"PassWd"][u"unixNVR"]	= valuesDict[u"nvrUNIXPassWd"]
			self.connectParams[u"UserID"][u"nvrWeb"]	= valuesDict[u"nvrWebUserID"]
			self.connectParams[u"PassWd"][u"nvrWeb"]	= valuesDict[u"nvrWebPassWd"]
			self.vmMachine								= valuesDict[u"vmMachine"]
			self.mountPathVM							= valuesDict[u"mountPathVM"]
			self.videoPath								= self.completePath(valuesDict[u"videoPath"])
			self.vboxPath								= self.completePath(valuesDict[u"vboxPath"])
			self.changedImagePath						= self.completePath(valuesDict[u"changedImagePath"])
			self.vmDisk									= valuesDict[u"vmDisk"]
			enableVideoSwitch							= valuesDict[u"cameraSystem"]
			ip0											= valuesDict[u"nvrIP"]


			if self.cameraSystem != enableVideoSwitch:
				rebootRequired	+= u" video enabled/disabled;"

			self.cameraSystem = enableVideoSwitch
			if self.cameraSystem =="nvr":
				self.ipNumbersOf[u"VD"]	= ip0
				if self.ipNumbersOf[u"VD"] != ip0 :
					rebootRequired	+= u" VIDEO ipNumber changed;"
					self.indiLOG.log(10,u"IP# old:{}, new:{}".format(self.ipNumbersOf[u"VD"], ip0) )


			self.enablecheckforUnifiSystemDevicesState = valuesDict["enablecheckforUnifiSystemDevicesState"]

			self.useDBInfoForWhichDevices = valuesDict["useDBInfoForWhichDevices"]
			if self.isValidIP(self.unifiCloudKeyIP) and (self.unifiCloudKeyMode.find("ON") >-1 or self.unifiCloudKeyMode.find("UDM") or self.useDBInfoForWhichDevices in ["all","perDevice"]):
				if self.unifiCloudKeyMode  != "ON":
					self.unifiCloudKeyMode = "ON"
				self.devsEnabled[u"DB"] = True
			else:
				self.devsEnabled[u"DB"]	= False



			if rebootRequired != "":
				self.indiLOG.log(30,u"restart " + rebootRequired)
				self.quitNow = u"config changed"
			self.updateConnectParams  = time.time() - 100
			valuesDict[u"connectParams"] = json.dumps(self.connectParams)

			self.setLogfile(unicode(valuesDict[u"logFileActive2"]),config=True)

			return True, valuesDict
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e) )
			return (False, valuesDict, valuesDict)


	####-----------------  data stats menu items	---------
	def buttonsetConfigToSelectedControllerTypeCALLBACK(self, valuesDict):
		try:
			controllerType = valuesDict[u"unifiControllerType"]
			if   controllerType == "UDM":
				valuesDict[u"unifiCloudKeyMode"] 	= u"ON"
				valuesDict[u"ControllerBackupPath"]	= u"/usr/lib/unifi/data/backup/autobackup"
				valuesDict[u"ipUDMON"]	 			= True

			elif controllerType == "UDMPro":
				valuesDict[u"unifiCloudKeyMode"] 	= u"ON"
				valuesDict[u"ControllerBackupPath"]	= u"/usr/lib/unifi/data/backup/autobackup"
				valuesDict[u"ipUDMON"]	 			= True

			elif controllerType == "off":
				valuesDict[u"unifiCloudKeyMode"] 	= u"off"
				valuesDict[u"ControllerBackupPath"]	= u"/data/unifi/data/backup/autobackup"
				valuesDict[u"ipUDMON"]	 			= False
			else:
				valuesDict[u"unifiCloudKeyMode"] 	= u"ON"
				valuesDict[u"ControllerBackupPath"]	= u"/data/unifi/data/backup/autobackup"
				valuesDict[u"ipUDMON"]	 			= False

			valuesDict[u"unifiCloudKeySiteName"]	= self.unifiCloudKeySiteName

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e) )
		return valuesDict
		



	####-----------------	 ---------
	def completePath(self,inPath):
		if len(inPath) == 0: return ""
		if inPath == " ":	 return ""
		if inPath[-1] !="/": inPath +="/"
		return inPath

	####-----------------	 ---------
	def getNewValusDictField(self,item,	 valuesDict, old, rebootRequired):
		xxx	   = valuesDict[item]
		if xxx != old:
			rebootRequired += " "+item+" changed"
			#indigo.server.log(u" changed: "+item+ u" new: >"+ xxx +u"< old:>"+old+u"<") 
		return	 xxx, rebootRequired

	####-----------------  config setting ---- END   ----------#########

	####-----------------	 ---------
	def getCPU(self,pid):
		ret = subprocess.Popen("ps -ef | grep " + unicode(pid) + " | grep -v grep", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
		lines = ret[0].strip("\n").split("\n")
		for line in lines:
			if len(line) < 100: continue
			items = line.split()
			if items[1] != unicode(pid): continue
			if len(items) < 6: continue
			return (items[6])
		return ""

	####-----------------	 ---------
	def printConfigMenu(self,  valuesDict=None, typeId=""):
		try:
			self.myLog( text=u" ",mType=u" ")
			self.myLog( text=u"UniFi   =============plugin config Parameters========",mType=u" ")

			self.myLog( text=u"debugLevel".ljust(40)						+	unicode(self.debugLevel).ljust(3) )
			self.myLog( text=u"logFile".ljust(40)							+	unicode(self.logFile) )
			self.myLog( text=u"enableFINGSCAN".ljust(40)					+	unicode(self.enableFINGSCAN) )
			self.myLog( text=u"count_APDL_inPortCount".ljust(40)			+	unicode(self.count_APDL_inPortCount) )
			self.myLog( text=u"enableBroadCastEvents".ljust(40)				+	unicode(self.enableBroadCastEvents) )
			self.myLog( text=u"ignoreNeighborForFing".ljust(40)				+	unicode(self.ignoreNeighborForFing))
			self.myLog( text=u"expirationTime - default".ljust(40)			+	unicode(self.expirationTime).ljust(3)+u" [sec]" )
			self.myLog( text=u"sleep in main loop  ".ljust(40)				+	unicode(self.loopSleep).ljust(3)+u" [sec]" )
			self.myLog( text=u"use curl or request".ljust(40)				+	self.requestOrcurl )
			self.myLog( text=u"curl path".ljust(40)							+	self.curlPath )
			self.myLog( text=u"cpu used since restart: ".ljust(40) 			+	self.getCPU(self.myPID) )
			self.myLog( text=u"" ,mType=u" ")
			self.myLog( text=u"====== used in ssh userid@switch-IP, AP-IP, USG-IP to get DB dump and listen to events",mType=u" " )
			self.myLog( text=u"UserID-ssh".ljust(40)						+	self.connectParams[u"UserID"][u"unixDevs"])
			self.myLog( text=u"PassWd-ssh".ljust(40)						+	self.connectParams[u"PassWd"][u"unixDevs"])
			self.myLog( text=u"UserID-ssh-UDM".ljust(40)					+	self.connectParams[u"UserID"][u"unixUD"])
			self.myLog( text=u"PassWd-ssh-UDM".ljust(40)					+	self.connectParams[u"PassWd"][u"unixUD"])
			self.myLog( text=u"read buffer size ".ljust(40)					+	unicode(self.readBuffer) )
			for ipN in self.connectParams[u"promptOnServer"]:
				self.myLog( text=(u"promptOnServer "+ipN).ljust(40)			+	u"'"+self.connectParams[u"promptOnServer"][ipN]+u"'")

			self.myLog( text=u"GW tailCommand".ljust(40)					+	self.connectParams[u"commandOnServer"][u"GWtail"] )
			self.myLog( text=u"GW dictCommand".ljust(40)					+	self.connectParams[u"commandOnServer"][u"GWdict"] )
			self.myLog( text=u"SW tailCommand".ljust(40)					+	self.connectParams[u"commandOnServer"][u"SWtail"] )
			self.myLog( text=u"SW dictCommand".ljust(40)					+	self.connectParams[u"commandOnServer"][u"SWdict"] )
			self.myLog( text=u"AP tailCommand".ljust(40)					+	self.connectParams[u"commandOnServer"][u"APtail"] )
			self.myLog( text=u"AP dictCommand".ljust(40)					+	self.connectParams[u"commandOnServer"][u"APdict"] )
			self.myLog( text=u"UD dictCommand".ljust(40)					+	self.connectParams[u"commandOnServer"][u"UDdict"] )
			self.myLog( text=u"AP enabled:".ljust(40)						+	unicode(self.devsEnabled[u"AP"]).replace("True","T").replace("False","F").replace(" ","").replace("[","").replace("]","") )
			self.myLog( text=u"SW enabled:".ljust(40)						+	unicode(self.devsEnabled[u"SW"]).replace("True","T").replace("False","F").replace(" ","").replace("[","").replace("]","") )
			self.myLog( text=u"GW enabled:".ljust(40)						+	unicode(self.devsEnabled[u"GW"]).replace("True","T").replace("False","F") )
			self.myLog( text=u"controlelr DB read enabled".ljust(40)		+	unicode(self.devsEnabled[u"DB"]).replace("True","T").replace("False","F") )
			self.myLog( text=u"UDM enabled".ljust(40)						+	unicode(self.devsEnabled[u"UD"]).replace("True","T").replace("False","F") )
			self.myLog( text=u"read DB Dict every".ljust(40)				+	unicode(self.readDictEverySeconds).replace("'","").replace("u","").replace(" ","")+u" [sec]" )
			self.myLog( text=u"restart listeners if NoMessage for".ljust(40)+unicode(self.restartIfNoMessageSeconds).ljust(3)+u"[sec]" )
			self.myLog( text=u"force restart of listeners ".ljust(40)+unicode(self.restartListenerEvery).ljust(5)+u"[sec]" )
			self.myLog( text=u"" ,mType=u" ")
			self.myLog( text=u"====== CONTROLLER/UDM WEB ACCESS , set parameters and reporting",mType=u" " )
			self.myLog( text=u"  curl data={WEB-UserID:..,WEB-PassWd:..} https://controllerIP: ..--------------",mType=u" " )
			self.myLog( text=u"Mode: off, ON, UDM, reports only".ljust(40)	+	self.unifiCloudKeyMode )
			self.myLog( text=u"WEB-UserID".ljust(40)						+	self.connectParams[u"UserID"][u"webCTRL"] )
			self.myLog( text=u"WEB-PassWd".ljust(40)						+	self.connectParams[u"PassWd"][u"webCTRL"] )
			self.myLog( text=u"Controller Type (UDM,..,std)".ljust(40)		+	self.unifiControllerType )
			self.myLog( text=u"use strict:true for web login".ljust(40)		+	unicode(self.useStrictToLogin)[0] )
			self.myLog( text=u"Controller port#".ljust(40)					+	self.unifiCloudKeyPort )
			self.myLog( text=u"overWriteControllerPort".ljust(40)			+	self.overWriteControllerPort )
			self.myLog( text=u"Controller site Name".ljust(40)				+	self.unifiCloudKeySiteName )
			self.myLog( text=u"Controller site NameList ".ljust(40)			+	unicode(self.unifiCloudKeyListOfSiteNames) )

			self.myLog( text=u"Controller API WebPage".ljust(40)			+	self.unifiApiWebPage )
			self.myLog( text=u"Controller API login WebPage".ljust(40)		+	self.unifiApiLoginPath )
			#self.myLog( text=u"get blocked client info from Cntr every".ljust(40) +	unicode(self.unifigetBlockedClientsDeltaTime)+u"[sec]" )
			#self.myLog( text=u"get lastseen info from Cntr every".ljust(40) +	unicode(self.unifigetLastSeenDeltaTime)+u"[sec]" )
			self.myLog( text=u"" ,mType=u" ")
			self.myLog( text=u"====== camera NVR stuff ---------------------------",mType=u" " )
			self.myLog( text=u"Camera enabled".ljust(40)					+	self.cameraSystem )
			if self.cameraSystem =="nvr":
				self.myLog( text=u"=  get camera DB config and listen to recording event logs",mType=u" " )
				self.myLog( text=u"  ssh NVR-UNIXUserID@NVR-IP ",mType=u" ")
				self.myLog( text=u"NVR-UNIXUserID".ljust(40)					+	self.connectParams[u"UserID"][u"unixNVR"] )
				self.myLog( text=u"NVR-UNIXpasswd".ljust(40)					+	self.connectParams[u"PassWd"][u"unixNVR"] )
				self.myLog( text=u"VD tailCommand".ljust(40)					+	self.connectParams[u"commandOnServer"][u"VDtail"] )
				self.myLog( text=u"VD dictCommand".ljust(40)					+	self.connectParams[u"commandOnServer"][u"VDdict"] )
				self.myLog( text=u"= getting snapshots and reading and changing parameters",mType=u" " )
				self.myLog( text=u"  curl data={WEB-UserID:..,WEB-PassWd:..} https://NVR-IP#:  ....   for commands and read parameters ",mType=u" " )
				self.myLog( text=u"  requests(http://IP-NVR:7080/api/2.0/snapshot/camera/**camApiKey**?force=true&width=1024&apiKey=nvrAPIkey,stream=True)  for snap shots",mType=u" " )
				self.myLog( text=u"imageSourceForSnapShot".ljust(40)			+	self.imageSourceForSnapShot )
				self.myLog( text=u"imageSourceForEvent".ljust(40)				+	self.imageSourceForEvent )
				self.myLog( text=u"NVR-WEB-UserID".ljust(40)					+	self.connectParams[u"UserID"][u"nvrWeb"] )
				self.myLog( text=u"NVR-WEB-passWd".ljust(40)					+	self.connectParams[u"PassWd"][u"nvrWeb"] )
				self.myLog( text=u"NVR-API Key".ljust(40)						+	self.nvrVIDEOapiKey )
			elif self.cameraSystem =="protect":
				pass
			self.myLog( text=u"",mType=u" ")
			self.myLog( text=u"AP ip#			  enabled / disabled")
			for ll in range(len(self.ipNumbersOf[u"AP"])):
				self.myLog( text=self.ipNumbersOf[u"AP"][ll].ljust(20) 		+	unicode(self.devsEnabled[u"AP"][ll]).replace("True","T").replace("False","F") )


			self.myLog( text=u"SW ip#")
			for ll in range(len(self.ipNumbersOf[u"SW"])):
				self.myLog( text=self.ipNumbersOf[u"SW"][ll].ljust(20) 		+	unicode(self.devsEnabled[u"SW"][ll]).replace("True","T").replace("False","F") )
			self.myLog( text=u"",mType=u" ")
			self.myLog( text=self.ipNumbersOf[u"GW"].ljust(20) 				+	unicode(self.devsEnabled[u"GW"]).replace("True","T").replace("False","F")+"  USG/UGA  gateway/router " )

			self.myLog( text=self.unifiCloudKeyIP.ljust(20) 				+	u"   Controller / cloud Key IP#" )
			self.myLog( text=self.ipNumbersOf[u"VD"].ljust(20)				+	u"   Video NVR-IP#" )
			self.myLog( text=u"----------------------------------------------------",mType=u"  ")

			self.myLog( text=u"")

			self.myLog( text=u"UniFi    =============plugin config Parameters========  END ", mType=u" " )
			self.myLog( text=u" ", mType=u" ")

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e) )

		return


	####-----------------	 ---------
	def printMACs(self,MAC=""):
		try:

			self.myLog( text=u"===== UNIFI device info =========",  mType=u"    " )
			for dev in indigo.devices.iter(self.pluginId):
				if dev.deviceTypeId == u"client":		  continue
				if MAC !="" and dev.states[u"MAC"] != MAC: continue
				self.myLog( text=dev.name+ u"  id: "+unicode(dev.id).ljust(12)+ u"; type:"+ dev.deviceTypeId,	mType=u"device info")
				self.myLog( text=u"props:",	mType=u" --- ")
				props = dev.pluginProps
				for p in props:
					self.myLog( text=unicode(props[p]),	mType=p)

				self.myLog( text=u"states:",	 mType=u" --- ")
				for p in dev.states:
					self.myLog( text=unicode(dev.states[p]), mType=p)

			self.myLog( text=u"counters, timers etc:",  mType=u" --- ")
			if MAC in self.MAC2INDIGO[u"UN"]:
				self.myLog( text=unicode(self.MAC2INDIGO[u"UN"][MAC]), mType=u"UniFi")

			if MAC in self.MAC2INDIGO[u"AP"]:
				self.myLog( text=unicode(self.MAC2INDIGO[u"AP"][MAC]), mType=u"AP")

			if MAC in self.MAC2INDIGO[u"SW"]:
				self.myLog( text=unicode(self.MAC2INDIGO[u"SW"][MAC]), mType=u"SWITCH")

			if MAC in self.MAC2INDIGO[u"GW"]:
				self.myLog( text=unicode(self.MAC2INDIGO[u"GW"][MAC]), mType=u"GATEWAY")

			if MAC in self.MAC2INDIGO[u"NB"]:
				self.myLog( text=unicode(self.MAC2INDIGO[u"NB"][MAC]), mType=u"NEIGHBOR")


			self.myLog( text=u"===== UNIFI device info ========= END ",	mType=u"device info")

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

	####-----------------	 ---------
	def printALLMACs(self):
		try:

			self.myLog( text=u"===== UNIFI device info =========",  mType=u"")

			for dev in indigo.devices.iter(self.pluginId):
				if dev.deviceTypeId == u"client": continue
				self.myLog( text=u"id:      "+unicode(dev.id).ljust(12)+ u";  type:"+ dev.deviceTypeId, mType=dev.name)
				line=u"props: "
				props = dev.pluginProps
				for p in props:
					line+= unicode(p)+u":"+ unicode(props[p])+u";  "
				self.myLog( text=line,  mType=u" ")
				line=u"states: "
				for p in dev.states:
					line += unicode(p) + u":" + unicode(dev.states[p]) + u";  "
				self.myLog( text=line,  mType=u" ")

				self.myLog( text=u"temp data, counters, timer etc", mType=u" ")
			for dd in self.MAC2INDIGO[u"UN"]:
				self.myLog( text=unicode(self.MAC2INDIGO[u"UN"][dd]), mType=u"UNIFI    "+dd)
			for dd in self.MAC2INDIGO[u"AP"]:
				self.myLog( text=unicode(self.MAC2INDIGO[u"AP"][dd]), mType=u"AP        "+dd)
			for dd in self.MAC2INDIGO[u"SW"]:
				self.myLog( text=unicode(self.MAC2INDIGO[u"SW"][dd]), mType=u"SWITCH    "+dd)
			for dd in self.MAC2INDIGO[u"GW"]:
				self.myLog( text=unicode(self.MAC2INDIGO[u"GW"][dd]), mType=u"GATEWAY "+dd)
			for dd in self.MAC2INDIGO[u"NB"]:
				self.myLog( text=unicode(self.MAC2INDIGO[u"NB"][dd]), mType=u"NEIGHB    "+dd)

			self.myLog( text=u"===== UNIFI device info ========= END ", mType=u"")



		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))


	####-----------------     ---------
	def printALLUNIFIsreduced(self):
		try:

			self.myLog( text=u"===== UniFi device info =========",  mType=u"")

			dType ="UniFi"
			line =u"                                 curr.;   exp;  use ping  ; use WOL;     use what 4;       WiFi;WiFi-max;    DHCP;  SW-UPtm; lastStatusChge;                              reason;     member of;"
			self.myLog( text=line,  mType=u" ")
			line =u"id:         MAC#             ;  status; time;    up;  down;   [sec];         Status;     Status;  idle-T; max-AGE;    chged;               ;                          for change;        groups;"
			lineI = []
			lineE = []
			lineD = []
			self.myLog( text=line,  mType=u"dev Name")
			for dev in indigo.devices.iter(u"props.isUniFi"):
				props = dev.pluginProps
				mac = dev.states[u"MAC"]
				if u"useWhatForStatus" in props and props[u"useWhatForStatus"] == u"WiFi": wf = True
				else:																	   wf = False

				if True:											line  = unicode(dev.id).ljust(12)+mac+"; "

				if mac in self.MACignorelist and self.MACignorelist[mac]:
																	line += ("IGNORED").rjust(7)+u"; "
				elif u"status" in dev.states:						line += (dev.states[u"status"]).rjust(7)+u"; "
				else:												line += ("-------").rjust(7)+u"; "

				if u"expirationTime" in props :						line += (unicode(props[u"expirationTime"]).split(".")[0]).rjust(4)+u"; "
				else:												line += " ".ljust(4)+"; "

				if u"usePingUP" in props :							line += (unicode(props[u"usePingUP"])).rjust(5)+u"; "
				else:												line += " ".ljust(5)+"; "

				if u"usePingDOWN" in props :						line += (unicode(props[u"usePingDOWN"])).rjust(5)+u"; "
				else:												line += " ".ljust(5)+"; "

				if u"useWOL" in props :
					if props[u"useWOL"] =="0":
																	line += ("no").ljust(7)+u"; "
					else:
																	line += (unicode(props[u"useWOL"])).rjust(7)+u"; "
				else:												line += "no".ljust(7)+"; "

				if u"useWhatForStatus" in props :					line += (unicode(props[u"useWhatForStatus"])).rjust(14)+u"; "
				else:												line += " ".ljust(14)+"; "

				if u"useWhatForStatusWiFi" in props and wf:			line += (unicode(props[u"useWhatForStatusWiFi"])).rjust(10)+u"; "
				else:												line += " ".ljust(10)+"; "

				if u"idleTimeMaxSecs" in props and wf:				line += (unicode(props[u"idleTimeMaxSecs"])).rjust(7)+u"; "
				else:												line += " ".ljust(7)+"; "

				if u"useAgeforStatusDHCP" in props and not wf:		line += (unicode(props[u"useAgeforStatusDHCP"])).rjust(7)+u"; "
				else:												line += " ".ljust(7)+"; "

				if u"useupTimeforStatusSWITCH" in props and not wf: line += (unicode(props[u"useupTimeforStatusSWITCH"])).rjust(8)+u"; "
				else:												line += " ".ljust(8)+"; "

				if u"lastStatusChange" in dev.states:				line += (unicode(dev.states[u"lastStatusChange"])[5:]).rjust(14)+u"; "
				else:												line += " ".ljust(14)+"; "
				if u"lastStatusChangeReason" in dev.states:			line += (unicode(dev.states[u"lastStatusChangeReason"])[0:35]).rjust(35)+u"; "
				else:												line += " ".ljust(35)+"; "

				if u"groupMember" in dev.states:					line += (  (unicode(dev.states[u"groupMember"]).replace("Group","")).strip(",")	).rjust(13)+u"; "
				else:												line += " ".ljust(13)+"; "

				devName = dev.name
				if len(devName) > 25: devName = devName[:23]+".." # max len of 25 indicate cutoff if > 25 with ..
				if line.find(u"IGNORED;") >-1:
					lineI.append([line,devName])
				elif line.find(u"expired;") >-1:
					lineE.append([line,devName])
				elif line.find(u"down;") >-1:
					lineD.append([line,devName])
				else:
					self.myLog( text=line,  mType=devName)

			if lineD !=[]:
				for xx in lineD:
					self.myLog( text=xx[0], mType=xx[1])
			if lineE !=[]:
				for xx in lineE:
					self.myLog( text=xx[0], mType=xx[1])
			if lineI !=[]:
				for xx in lineI:
					self.myLog( text=xx[0], mType=xx[1])

			self.myLog( text=u"===== UniFi device info ========= END ", mType=u"")



		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))


	####-----------------  printGroups	  ---------
	def printGroups(self):
		try:

			self.myLog( text=u"-------MEMBERS ---------------", mType=u"GROUPS----- ")
			for group in _GlobalConst_groupList:
				xList = "\n            "
				lineNumber =0
				memberNames =[]
				for member in self.groupStatusList[group][u"members"]:
					if len(member) <2: continue
					try:
						ID = int(member)
						dev = indigo.devices[ID]
					except: continue
					memberNames.append(dev.name)

				for member in sorted(memberNames):
					try:
						dev = indigo.devices[member]
						xList += (member+"/"+dev.states[u"status"][0].upper()).ljust(29)+", "
						if len(xList)/180  > lineNumber:
							lineNumber +=1
							xList +=u"\n            "
					except	Exception, e:
						if unicode(e).find(u"None") == -1:
							self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
				if	xList != u"\n             ":
					gName = group
					homeaway =""
					try:
						gg =  indigo.variables["Unifi_Count_"+group+"_name"].value
						if gg.find(u"me to what YOU like") == -1:
							gName = group+"-"+gg
						homeaway += u"    Home: " + indigo.variables["Unifi_Count_"+group+"_Home"].value
						homeaway += u";    away: " + indigo.variables["Unifi_Count_"+group+"_Away"].value
					except: pass
					self.myLog( text=u"members (/Up/Down/Expired/Ignored) "+homeaway+xList.strip(","), mType=gName)
			self.myLog( text=u"-------MEMBERS ----------------- END",mType=u"GROUPS----- ")

			self.myLog( text=u" ", mType=u" ")

			xList = u"-------MEMBERS      ----------------\n          "
			lineNumber =0
			for member in sorted(self.MACignorelist):
				xList += member+", "
				if len(xList)/180  > lineNumber:
					lineNumber +=1
					xList +="\n            "
			self.myLog( text=xList.strip(","), mType=u"IGNORED ----- ")
			self.myLog( text=u"-------MEMBERS  -- -------------- END", mType=u"IGNORED ---")


		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))



	####-----------------  data stats menu items	---------
	def buttonRestartVDListenerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		self.restartRequest[u"VDtail"] = "VD"
		return

	def buttonRestartGWListenerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		self.restartRequest[u"GWtail"] = u"GW"
		self.restartRequest[u"GWdict"] = u"GW"
		self.indiLOG.log(10,u"menu RestartGWListener:{}".format(self.restartRequest))
		return


	def buttonRestartAPListenerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		if valuesDict[u"pickAP"] != u"-1":
			self.restartRequest[u"APtail"] = valuesDict[u"pickAP"]
			self.restartRequest[u"APdict"] = valuesDict[u"pickAP"]
		self.indiLOG.log(10,u"menu RestartAPListener:{}".format(self.restartRequest))
		return

	def buttonRestartSWListenerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		if valuesDict[u"pickSW"] != "-1":
			self.restartRequest[u"SWdict"] = valuesDict[u"pickSW"]
		self.indiLOG.log(10,u"menu RestartSWListener:{}".format(self.restartRequest))
		return

	def buttonResetPromptsCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		self.connectParams[u"promptOnServer"] = {}
		self.pluginPrefs[u"connectParams"] = json.dumps(self.connectParams)
		indigo.server.savePluginPrefs()	
		self.quitNow = u"restart due to prompt settings reset"
		self.indiLOG.log(30,u" reset prompts, initating restart")
		return

	def buttonstopVideoServiceCALLBACKaction (self, valuesDict=None, filter="", typeId="", devId=""):
		self.execVideoAction(" \"service unifi-video stop\"")
		return
	def buttonstopVideoServiceCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		self.execVideoAction(" \"service unifi-video stop\"")
		return

	def buttonstartVideoServiceCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		self.execVideoAction(" \"service unifi-video start\"")
		return
	def buttonstartVideoServiceCALLBACKaction (self, valuesDict=None, filter="", typeId="", devId=""):
		self.execVideoAction(" \"service unifi-video start\"")
		return

	def buttonMountOSXDriveOnVboxCALLBACKaction(self, valuesDict=None, filter="", typeId="", devId=""):
		self.execVideoAction(" \"sudo mount -t vboxsf -o uid=unifi-video,gid=unifi-video video "+self.mountPathVM+"\"")
		return
	def buttonMountOSXDriveOnVboxCALLBACK(self, valuesDict=None, filter="", typeId="", devId="",returnCmd=False):
		return self.execVideoAction(" \"sudo mount -t vboxsf -o uid=unifi-video,gid=unifi-video video "+self.mountPathVM+"\"", returnCmd=returnCmd)

	def execVideoAction(self,cmdIN,returnCmd=False):
		try:
			uType = "VDdict"
			userid, passwd =  self.getUidPasswd(uType,self.ipNumbersOf[u"VD"])
			if userid == "":
				self.indiLOG.log(10,u"CameraInfo  Video Action : userid not set")
				return

			if self.ipNumbersOf[u"VD"] not in self.connectParams[u"promptOnServer"]:
				self.testServerIfOK(self.ipNumbersOf[u"VD"],uType)

			cmd = self.expectPath  +" "
			cmd +=	"'" +  self.pathToPlugin + "videoServerAction.exp' "
			cmd +=	" '" +userid + "' '" + passwd + "' " 
			cmd +=	self.ipNumbersOf[u"VD"] + " " 
			cmd +=	"'"+self.escapeExpect(self.connectParams[u"promptOnServer"][self.ipNumbersOf[u"VD"]])+"' " 
			cmd += cmdIN
			if self.decideMyLog(u"Expect"):  self.indiLOG.log(10,u"CameraInfo "+ cmd)

			if returnCmd: return cmd

			subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		except	Exception, e:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
				self.indiLOG.log(40,u"promptOnServer={}".format(self.connectParams[u"promptOnServer"]))
				self.indiLOG.log(40,u"ipNumbersOf={}".format(self.ipNumbersOf[u"VD"]))
				self.indiLOG.log(40,u"userid:{}, passwd:{}".format(userid, passwd ))

		return

	####-----------------	 ---------
	####-----send commd parameters to cameras through VNR ------
	####-----------------	 ---------
	def buttonSendCommandToNVRLEDCALLBACKaction (self, action1=None, filter="", typeId="", devId=""):
		return self.buttonSendCommandToNVRLEDCALLBACK(valuesDict= action1.props)
	def buttonSendCommandToNVRLEDCALLBACK(self, valuesDict=None, filter="", typeId="", devId="",returnCmd=False):
		self.addToMenuXML(valuesDict)
		valuesDict[u"msg"],x =  self.setupNVRcmd(valuesDict[u"cameraDeviceSelected"],{"enableStatusLed":valuesDict[u"camLED"] == "1"})
		return valuesDict

	####-----------------	 ---------
	def buttonSendCommandToNVRSoundsCALLBACKaction (self, action1=None, filter="", typeId="", devId=""):
		return self.buttonSendCommandToNVRSoundsCALLBACK(valuesDict= action1.props)
	def buttonSendCommandToNVRSoundsCALLBACK(self, valuesDict=None, filter="", typeId="", devId="",returnCmd=False):
		self.addToMenuXML(valuesDict)
		valuesDict[u"msg"],x =  self.setupNVRcmd(valuesDict[u"cameraDeviceSelected"],{"systemSoundsEnabled":valuesDict[u"camSounds"] == "1"} )
		return valuesDict

	####-----------------	 ---------
	def buttonSendCommandToNVRenableSpeakerCALLBACKaction (self, action1=None, filter="", typeId="", devId=""):
		return self.buttonSendCommandToNVRenableSpeakerCALLBACK(valuesDict= action1.props)
	def buttonSendCommandToNVRenableSpeakerCALLBACK(self, valuesDict=None, filter="", typeId="", devId="",returnCmd=False):
		self.addToMenuXML(valuesDict)
		valuesDict[u"msg"],x =  self.setupNVRcmd(valuesDict[u"cameraDeviceSelected"],{"enableSpeaker":valuesDict[u"enableSpeaker"] == "1", "speakerVolume":int(valuesDict[u"enableSpeaker"])} )
		return valuesDict

	####-----------------	 ---------
	def buttonSendCommandToNVRmicVolumeCALLBACKaction (self, action1=None, filter="", typeId="", devId=""):
		return self.buttonSendCommandToNVRmicVolumeCALLBACK(valuesDict= action1.props)
	def buttonSendCommandToNVRmicVolumeCALLBACK(self, valuesDict=None, filter="", typeId="", devId="",returnCmd=False):
		self.addToMenuXML(valuesDict)
		valuesDict[u"msg"] = self.setupNVRcmd(valuesDict[u"cameraDeviceSelected"],{"micVolume":int(valuesDict[u"micVolume"])} )
		return valuesDict

	####-----------------	 ---------
	def buttonSendCommandToNVRRecordCALLBACKaction (self, action1=None, filter="", typeId="", devId=""):
		return self.buttonSendCommandToNVRRecordCALLBACK(valuesDict= action1.props)

	def buttonSendCommandToNVRRecordCALLBACK(self, valuesDict=None, filter="", typeId="", devId="",returnCmd=False):
		self.addToMenuXML(valuesDict)
		if valuesDict[u"postPaddingSecs"] =="-1" and valuesDict[u"prePaddingSecs"] =="-1":
			valuesDict[u"msg"],x =  self.setupNVRcmd(valuesDict[u"cameraDeviceSelected"],
					{"recordingSettings":{"motionRecordEnabled": valuesDict[u"motionRecordEnabled"] == "1","fullTimeRecordEnabled": valuesDict[u"fullTimeRecordEnabled"] == "1", 'channel': valuesDict[u"channel"]}
					} )
		elif valuesDict[u"postPaddingSecs"] !="-1" and valuesDict[u"prePaddingSecs"] !="-1":
			valuesDict[u"msg"],x =  self.setupNVRcmd(valuesDict[u"cameraDeviceSelected"],
					{"recordingSettings":{"motionRecordEnabled": valuesDict[u"motionRecordEnabled"] == "1","fullTimeRecordEnabled": valuesDict[u"fullTimeRecordEnabled"] == "1", 'channel': valuesDict[u"channel"],
					"postPaddingSecs": int(valuesDict[u"postPaddingSecs"]),
					"prePaddingSecs": int(valuesDict[u"prePaddingSecs"]) }
					} )
		elif valuesDict[u"postPaddingSecs"] !="-1":
			valuesDict[u"msg"],x =  self.setupNVRcmd(valuesDict[u"cameraDeviceSelected"],
					{"recordingSettings":{"motionRecordEnabled": valuesDict[u"motionRecordEnabled"] == "1","fullTimeRecordEnabled": valuesDict[u"fullTimeRecordEnabled"] == "1", 'channel': valuesDict[u"channel"],
					"postPaddingSecs": int(valuesDict[u"postPaddingSecs"]) }
					} )
		elif valuesDict[u"prePaddingSecs"] !="-1":
			valuesDict[u"msg"],x =  self.setupNVRcmd(valuesDict[u"cameraDeviceSelected"],
					{"recordingSettings":{"motionRecordEnabled": valuesDict[u"motionRecordEnabled"] == "1","fullTimeRecordEnabled": valuesDict[u"fullTimeRecordEnabled"] == "1", 'channel': valuesDict[u"channel"],
					"prePaddingSecs": int(valuesDict[u"prePaddingSecs"]) }
					} )
		else:
			valuesDict[u"msg"]="bad selection for recording"
		return valuesDict

	####-----------------	 ---------
	def buttonSendCommandToNVRIRCALLBACKaction (self, action1=None, filter="", typeId="", devId=""):
		return self.buttonSendCommandToNVRIRCALLBACK(valuesDict= action1.props)
	def buttonSendCommandToNVRIRCALLBACK(self, valuesDict=None, filter="", typeId="", devId="",returnCmd=False):
		self.addToMenuXML(valuesDict)
		xxx = valuesDict[u"irLedMode"]
		if xxx.find(u"auto") >-1:
			valuesDict[u"msg"],x =  self.setupNVRcmd(valuesDict[u"cameraDeviceSelected"],{"ispSettings":{"enableExternalIr": int(valuesDict[u"enableExternalIr"]),"irLedMode":"auto" }} )
		else:# for manual 0/100/255 level
			xxx = xxx.split("-")
			valuesDict[u"msg"],x =  self.setupNVRcmd(valuesDict[u"cameraDeviceSelected"],{"ispSettings":{"enableExternalIr": int(valuesDict[u"enableExternalIr"]),"irLedMode":xxx[0], "irLedLevel": int(xxx[1])}  } )
		return valuesDict
	####-----------------	 ---------
	def buttonSendCommandToNVRvideostreamingCALLBACKaction (self, action1=None, filter="", typeId="", devId=""):
		return self.buttonSendCommandToNVRIRCALLBACK(valuesDict= action1.props)
	def buttonSendCommandToNVRvideostreamingCALLBACK(self, valuesDict=None, filter="", typeId="", devId="",returnCmd=False):
		self.addToMenuXML(valuesDict)

		# first we need to get the current values
		error, ret = self.setupNVRcmd(valuesDict[u"cameraDeviceSelected"],"", cmdType=u"get")
		if u"channels" not in ret[0] or len(ret[0][u"channels"]) !=3 : # something went wrong
			self.indiLOG.log(40,u"videostreaming error: {}     \n>>{}<<".format(error, ret))
			valuesDict[u"msg"] = error
			return valuesDict

		# modify the required ones
		channels = ret[0][u"channels"]
		channel	 = int(valuesDict[u"channelS"])
		channels[channel][u"isRtmpEnabled"]	 = valuesDict[u"isRtmpEnabled"]  == u"1"
		channels[channel][u"isRtmpsEnabled"] = valuesDict[u"isRtmpsEnabled"] == u"1"
		channels[channel][u"isRtspEnabled"]  = valuesDict[u"isRtspEnabled"]  == u"1"
		# send back
		error, data=  self.setupNVRcmd(valuesDict[u"cameraDeviceSelected"], {u"channels":channels}, cmdType=u"put")
		valuesDict[u"msg"]=error
		return valuesDict

	####-----------------	 ---------
	def buttonSendCommandToNVRgetSnapshotCALLBACKaction (self, action1=None, filter="", typeId="", devId=""):
		return self.buttonSendCommandToNVRgetSnapshotCALLBACK(valuesDict= action1.props)
	def buttonSendCommandToNVRgetSnapshotCALLBACK(self, valuesDict=None, filter="", typeId="", devId="",returnCmd=False):
		self.addToMenuXML(valuesDict)
		if   self.imageSourceForSnapShot == u"imageFromNVR": 	valuesDict[u"msg"] = self.getSnapshotfromNVR(valuesDict[u"cameraDeviceSelected"], valuesDict[u"widthOfImage"], valuesDict[u"fileNameOfImage"] )
		elif self.imageSourceForSnapShot == u"imageFromCamera":	valuesDict[u"msg"] = self.getSnapshotfromCamera(valuesDict[u"cameraDeviceSelected"],                          valuesDict[u"fileNameOfImage"] )
		return valuesDict

	####-----------------	 ---------
	def setupNVRcmd(self, devId, payload,cmdType=u"put"):

		dev = indigo.devices[int(devId)]
		try:
			if not self.isValidIP(self.ipNumbersOf[u"VD"]): return u"error IP",""
			if self.cameraSystem != "nvr":					 	return u"error enabled",""
			if len(self.nvrVIDEOapiKey) < 5:				return u"error apikey",""

			if payload != "":  payload[u'name']= dev.states[u"nameOnNVR"]
			ret = self.executeCMDonNVR(payload, dev.states[u"apiKey"],  cmdType=cmdType)
			self.fillCamerasIntoIndigo(ret, calledFrom=u"setupNVRcmd")
			return "ok",ret
		except	Exception, e:
			self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))



	####-----------------	 ---------
	def executeCMDonNVR(self, data, cameraKey,	cmdType=u"put"):

		try:
			if cameraKey !="":
				url = u"https://"+self.ipNumbersOf[u"VD"]+ u":7443/api/2.0/camera/"+ cameraKey+ u"?apiKey=" + self.nvrVIDEOapiKey

			else:
				url = u"https://"+self.ipNumbersOf[u"VD"]+ u":7443/api/2.0/camera/"+u"?apiKey=" + self.nvrVIDEOapiKey

			if self.requestOrcurl.find(u"curl") > -1:
				cmdL  = self.curlPath+u" --insecure -c /tmp/nvrCookie --data '"+json.dumps({u"username":self.connectParams[u"UserID"][u"nvrWeb"],u"password":self.connectParams[u"PassWd"][u"nvrWeb"]})+u"' 'https://"+self.ipNumbersOf[u"VD"]+u":7443/api/login'"
				if data =={} or data =="": dataDict = u""
				else:					   dataDict = u" --data '"+json.dumps(data)+"' "
				if	 cmdType == u"put":	  cmdTypeUse= u" -X PUT "
				elif cmdType == u"post":  cmdTypeUse= u" -X post "
				elif cmdType == u"get":	  cmdTypeUse= u"     "
				else:					  cmdTypeUse= u" "
				cmdR = self.curlPath+u" --insecure -b /tmp/nvrCookie  --header \"Content-Type: application/json\" "+cmdTypeUse +  dataDict + u"'" +url+ u"'"

				try:
					try:
						if time.time() - self.lastNVRCookie > 100: # re-login every 90 secs
							if self.decideMyLog(u"Video"): self.indiLOG.log(10,u"Video cmd "+ cmdL )
							ret = subprocess.Popen(cmdL, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
							if ret[1].find(u"error") >-1:
								self.indiLOG.log(40,u"error: (wrong UID/passwd, ip number?) ...>>{}<<\n{}<< Video error".format(ret[0], ret[1]))
								return {}
							self.lastNVRCookie =time.time()
					except	Exception, e:
						self.indiLOG.log(40,u"in Line {} has error={}    Video error".format(sys.exc_traceback.tb_lineno, e) )


					try:
						if self.decideMyLog(u"Video"): self.indiLOG.log(10,u"Video {}".format(cmdR) )
						ret = subprocess.Popen(cmdR, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
						ret0 = ret[0].decode(u"utf8")
						ret1 = ret[1].decode(u"utf8")
						try:
							jj = json.loads(ret0)
						except :
							self.indiLOG.log(10,u"UNIFI Video error  executeCMDonNVR has error, no json object returned: {} \n{}".format(ret0, ret1) )
							return []
						if u"rc" in jj[u"meta"] and unicode(jj[u"meta"][u"rc"]).find(u"error")>-1:
							self.indiLOG.log(40,u"error: data:>>{}<<\n>>{}<<\n" +" UNIFI Video error".format(ret0, ret1))
							return []
						elif self.decideMyLog(u"Video"):
							self.indiLOG.log(10,u"UNIFI Video executeCMDonNV- camera Data:\n" +json.dumps(jj[u"data"], sort_keys=True, indent=2) )

						return jj[u"data"]
					except	Exception, e:
						self.indiLOG.log(40,u"in Line {} has error={}  Video error".format(sys.exc_traceback.tb_lineno, e) )
				except	Exception, e:
					self.indiLOG.log(40,u"in Line {} has error={}  Video error".format(sys.exc_traceback.tb_lineno, e))


			#############does not work on OSX  el capitan ssl lib too old  ##########
			elif self.requestOrcurl ==u"requests":
				if self.unifiNVRSession =="" or (time.time() - self.lastNVRCookie) > 300:
					self.unifiNVRSession  = requests.Session()
					urlLogin  = u"https://"+self.ipNumbersOf[u"VD"]+u":7443/api/login"
					dataLogin = json.dumps({u"username":self.connectParams[u"UserID"][u"nvrWeb"],u"password":self.connectParams[u"PassWd"][u"nvrWeb"]})
					resp  = self.unifiNVRSession.post(urlLogin, data = dataLogin, verify=False)
					self.lastNVRCookie =time.time()
					#if self.decideMyLog(u"Video"): self.myLog( text="executeCMDonNVR  cmdType: post ;     urlLogin: "+urlLogin +";  dataLogin: "+ dataLogin+";  resp.text: "+ resp.text+"<<",mType=u"Video")


				if data == {}: dataDict = ""
				else:		   dataDict = json.dumps(data)

				if self.decideMyLog(u"Video"): self.indiLOG.log(10,u"Video executeCMDonNVR  cmdType: "+cmdType+u";  url: "+url +u";  dataDict: "+ dataDict+u"<<")
				try:
						if	 cmdType == u"put":	 resp = self.unifiNVRSession.put(url,data  = dataDict, headers={u'content-type': u'application/json'})
						elif cmdType == u"post": resp = self.unifiNVRSession.post(url,data = dataDict, headers={u'content-type': u'application/json'})
						elif cmdType == u"get":	 resp = self.unifiNVRSession.get(url,data  = dataDict)
						else:					 resp = self.unifiNVRSession.get(url,data  = dataDict)
						response = resp.text.decode(u"utf8")
						jj = json.loads(response)
						if u"rc" in jj[u"meta"] and unicode(jj[u"meta"][u"rc"]).find(u"error") >-1:
							self.indiLOG.log(40,u"executeCMDonNVR requests error: >>{}<<>>{}".format(resp.status_code, response) )
							return []
						elif self.decideMyLog(u"Video"):
							self.indiLOG.log(10,u"Video executeCMDonNVR requests {}".format(response) )
						return jj[u"data"]
				except	Exception, e:
					self.indiLOG.log(40,u"in Line {} has error={}\n resp.status_code >>{}<<  resp.text{}".format(sys.exc_traceback.tb_lineno, e, resp.status_code , response) )


		except	Exception, e:
			self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return []



	####-----------------  VBOX ACTIONS	  ---------
	def execVboxAction(self,action,action2=""):
		testCMD = "ps -ef | grep '/vboxAction.py ' | grep -v grep"
		if len(subprocess.Popen( testCMD, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0]) > 10:
			try:   self.indiLOG.log(10,u"CameraInfo VBOXAction: still runing, not executing: {}  {}".format(action, action2) )
			except:self.indiLOG.log(10,u"CameraInfo VBOXAction: still runing, not executing: ")
			return False
		cmd = self.pythonPath + " \"" + self.pathToPlugin + "vboxAction.py\" '"+action+"'"
		if action2 !="":
			cmd += " '"+action2+"'"
		cmd +=" &"
		if self.decideMyLog(u"Video"): self.indiLOG.log(10,u"CameraInfo  VBOXAction: "+cmd )
		subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		return

	####-----------------  Stop   ---------
	def buttonVboxActionStopCALLBACKaction(self, action1=None, filter="", typeId="", devId=""):
		self.buttonVboxActionStopCALLBACK(valuesDict= action1.props)
	def buttonVboxActionStopCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		cmd = json.dumps({u"action":[u"stop"], u"vmMachine":self.vmMachine, u"vboxPath":self.vboxPath, u"logfile":self.logFile})
		if not self.execVboxAction(cmd): return
		ip = self.ipNumbersOf[u"VD"]
		for dev in indigo.devices.iter(u"props.isUniFi"):
			if ip == dev.states[u"ipNumber"]:
				self.setSuspend(ip,time.time()+1000000000)
				break
		return


	####-----------------  Start	---------
	def buttonVboxActionStartCALLBACKaction(self, action1=None, filter="", typeId="", devId=""):
		self.buttonVboxActionStartCALLBACK(valuesDict= action1.props)
	def buttonVboxActionStartCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		cmd = {"action":["start","mountDisk"], "vmMachine":self.vmMachine, "vboxPath":self.vboxPath, "logfile":self.logFile,"vmDisk":self.vmDisk }
		mountCmd  = self.buttonMountOSXDriveOnVboxCALLBACK(returnCmd=True)
		self.execVboxAction(json.dumps(cmd),action2=json.dumps(mountCmd))
		return

	####-----------------  compress   ---------
	def buttonVboxActionCompressCALLBACKaction(self, action1=None, filter="", typeId="", devId=""):
		self.buttonVboxActionCompressCALLBACK(valuesDict= action1.props)
	def buttonVboxActionCompressCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		cmd = {u"action":[u"stop",u"compress",u"start",u"mountDisk"], u"vmMachine":self.vmMachine, u"vboxPath":self.vboxPath, u"logfile":self.logFile,u"vmDisk":self.vmDisk }
		mountCmd  = self.buttonMountOSXDriveOnVboxCALLBACK(returnCmd=True)
		if not self.execVboxAction(json.dumps(cmd),action2=json.dumps(mountCmd)): return
		ip = self.ipNumbersOf[u"VD"]
		for dev in indigo.devices.iter(u"props.isUniFi"):
			if ip == dev.states[u"ipNumber"]:
				self.setSuspend(ip, time.time()+300.)
				break
		return

	####-----------------  backup	 ---------
	def buttonVboxActionBackupCALLBACKaction(self, action1=None, filter="", typeId="", devId=""):
		self.buttonVboxActionBackupCALLBACK(valuesDict= action1.props)
	def buttonVboxActionBackupCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		cmd = {u"action":[u"stop",u"backup",u"start",u"mountDisk"], u"vmMachine":self.vmMachine, u"vboxPath":self.vboxPath, u"logfile":self.logFile,u"vmDisk":self.vmDisk }
		mountCmd  = self.buttonMountOSXDriveOnVboxCALLBACK(returnCmd=True)
		if not self.execVboxAction(json.dumps(cmd),action2=json.dumps(mountCmd)): return
		ip = self.ipNumbersOf[u"VD"]
		for dev in indigo.devices.iter(u"props.isUniFi"):
			if ip == dev.states[u"ipNumber"]:
				self.setSuspend(ip, time.time()+220.)
				break
		return




	####-----------------  data stats menu items	---------
	def buttonPrintStatsCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		self.buttonPrintTcpipStats()
		self.printUpdateStats()


	####-----------------	 ---------
	def buttonPrintTcpipStats(self):

		if len(self.dataStats[u"tcpip"]) ==0: return
		nMin	= 0
		nSecs	= 0
		totByte = 0
		totMsg	= 0
		totErr	= 0
		totRes	= 0
		totAli	= 0
		out		= ""
		for uType in sorted(self.dataStats[u"tcpip"].keys()):
			for ipNumber in sorted(self.dataStats[u"tcpip"][uType].keys()):
				if nSecs ==0:
					self.myLog( text=u"=== data stats for received messages ====     collection started at {}".format(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(self.dataStats[u"tcpip"][uType][ipNumber][u"startTime"]))), mType=u"data stats === START" )
					self.myLog( text=u"ipNumber            msgcount;     msgBytes;  errCount;  restarts;aliveCount;   msg/min; bytes/min;   err/min; aliveC/min", mType=u"dev type")
				nSecs = time.time() - self.dataStats[u"tcpip"][uType][ipNumber][u"startTime"]
				nMin  = nSecs/60.
				out	 =ipNumber.ljust(18)
				out +=u"{:10d};".format(self.dataStats[u"tcpip"][uType][ipNumber][u"inMessageCount"])
				out +=u"{:13d};".format(self.dataStats[u"tcpip"][uType][ipNumber][u"inMessageBytes"])
				out +=u"{:10d};".format(self.dataStats[u"tcpip"][uType][ipNumber][u"inErrorCount"])
				out +=u"{:10d};".format(self.dataStats[u"tcpip"][uType][ipNumber][u"restarts"])
				out +=u"{:10d};".format(self.dataStats[u"tcpip"][uType][ipNumber][u"aliveTestCount"]) 
				out +=u"{:10.3f};".format(self.dataStats[u"tcpip"][uType][ipNumber][u"inMessageCount"]/nMin) 
				out +=u"{:10.1f};".format(self.dataStats[u"tcpip"][uType][ipNumber][u"inMessageBytes"]/nMin)
				out +=u"{:10.7f};".format(self.dataStats[u"tcpip"][uType][ipNumber][u"inErrorCount"]/nMin)
				out +=u"{:10.3f};".format(self.dataStats[u"tcpip"][uType][ipNumber][u"aliveTestCount"]/nMin) 
				totByte += self.dataStats[u"tcpip"][uType][ipNumber][u"inMessageBytes"]
				totMsg	+= self.dataStats[u"tcpip"][uType][ipNumber][u"inMessageCount"]
				totErr	+= self.dataStats[u"tcpip"][uType][ipNumber][u"inErrorCount"]
				totRes	+= self.dataStats[u"tcpip"][uType][ipNumber][u"restarts"]
				totAli	+= self.dataStats[u"tcpip"][uType][ipNumber][u"aliveTestCount"]

				self.myLog( text=out, mType=u"  {}-{}".format(uType, self.dataStats[u"tcpip"][uType][ipNumber][u"APN"]) )
		self.myLog( text=u"total             {:10d};{:13d};{:10d};{:10d};{:10d};{:10.3f};{:10.1f};{:10.7f};{:11.3f}".format(totMsg, totByte, totErr, totRes, totAli, totMsg/nMin, totByte/nMin, totErr/nMin, totAli/nMin), mType=u"T O T A L S")
		self.myLog( text=u"===  total time measured: {:10.0f}[s] = {:s} ".format(nSecs/(24*60*60) ,time.strftime("%H:%M:%S", time.gmtime(nSecs))), mType=u"data stats === END" )


	####-----------------	 ---------
	def printUpdateStats(self):
		if len(self.dataStats[u"updates"]) ==0: return
		nSecs = max(1,(time.time()-	 self.dataStats[u"updates"][u"startTime"]))
		nMin  = nSecs/60.
		self.myLog( text=u" ", mType=u" " )
		self.myLog( text=u"===  measuring started at: {}" .format(time.strftime("%H:%M:%S",time.localtime(self.dataStats[u"updates"]["startTime"]))), mType=u"indigo update stats === " )
		self.myLog( text=u"updates: {:10d};     updates/sec: {:10.2f};  updates/minute: {:10.2f}".format(self.dataStats[u"updates"][u"devs"],   self.dataStats[u"updates"][u"devs"]  /nMin, self.dataStats[u"updates"][u"devs"]  /nSecs),  mType=u"     device ")
		self.myLog( text=u"updates: {:10d};     updates/sec: {:10.2f};  updates/minute: {:10.2f}".format(self.dataStats[u"updates"][u"states"], self.dataStats[u"updates"][u"states"]/nMin, self.dataStats[u"updates"][u"states"]/nSecs),  mType=u"     states ")
		self.myLog( text=u"===  total time measured: {:10.0f}[s] = {:s}".format(nSecs/(24*60*60), time.strftime("%H:%M:%S", time.gmtime(nSecs))),  mType=u"indigo update stats === END" )
		return


	####-----------------	 ---------
	def addToMenuXML(self, valuesDict):
		if valuesDict:
			for item in valuesDict:
				self.menuXML[item] = copy.copy(valuesDict[item])
			self.pluginPrefs[u"menuXML"]	 = json.dumps(self.menuXML)
		return

	####-----------------	 ---------
	def buttonprintNVRCameraEventsCALLBACK(self,valuesDict, typeId="", devId=""):
		maxEvents= int(valuesDict[u"maxEvents"])
		totEvents= 0
		for MAC in self.cameras:
			totEvents += len(self.cameras[MAC][u"events"])

		self.addToMenuXML(valuesDict)

		out = u"\n======= Camera Events ======"
		out += u"\nDev MAC             dev.id        Name "
		out += u"\n           Ev#    start                   end        dur[secs]\n"
		for MAC in self.cameras:
			out += MAC+u" %11d"%self.cameras[MAC][u"devid"]+u" "+self.cameras[MAC]["cameraName"].ljust(25)+u"  # events total: "+unicode(len(self.cameras[MAC][u"events"]))+"\n"
			evList=[]
			for evNo in self.cameras[MAC]["events"]:
				dateStart = time.strftime(u"%Y-%m-%d %H:%M:%S",time.localtime(self.cameras[MAC][u"events"][evNo][u"start"]))
				dateStop  = time.strftime(u" .. %H:%M:%S",time.localtime(self.cameras[MAC][u"events"][evNo][u"stop"]))
				delta  = self.cameras[MAC][u"events"][evNo][u"stop"]
				delta -= self.cameras[MAC][u"events"][evNo][u"start"]
				evList.append(u"     "+ unicode(evNo).rjust(10)+u"  "+dateStart+dateStop+u"  %8.1f"%delta+"\n")
			evList= sorted(evList, reverse=True)
			count =0
			for o in evList:
				count+=1
				if count > maxEvents: break
				out += o
		out += u"====== Camera Events ======;                         all # events total: " +unicode(totEvents) +"\n"

		self.myLog( text=out, mType=u" " )
		return

	####-----------------	 ---------
	def buttonresetNVRCameraEventsCALLBACK(self,valuesDict, typeId="", devId=""):
		for dev in indigo.devices.iter(u"props.isCamera"):
			dev.updateStateOnServer(u"eventNumber",0)
			self.indiLOG.log(10,u"reset event number for {}".format(dev.name) )
		self.resetCamerasStats()
		self.addToMenuXML(valuesDict)
		return
	####-----------------	 ---------


	####-----------------	 ---------
	def buttonPrintNVRCameraSystemCALLBACK(self,valuesDict, typeId="", devId=""):
		if self.cameraSystem == "nvr":
			self.pendingCommand.append("getNVRCamerasFromMongoDB-print")
		elif self.cameraSystem == "protect":
			self.pendingCommand.append("getProtectamerasInfo-print")

	####-----------------	 ---------
	def buttonrefreshNVRCameraSystemCALLBACK(self,valuesDict, typeId="", devId=""):
		if self.cameraSystem == "nvr":
			self.pendingCommand.append("getConfigFromNVR")
		elif self.cameraSystem == "protect":
			self.pendingCommand.append("getConfigFromProtect")

	####-----------------	 ---------
	def getMongoData(self, cmdstr, uType=u"VDdict"):
		ret =["",""]
		try:
			userid, passwd =  self.getUidPasswd(uType,self.ipNumbersOf[u"VD"])
			if userid == "": return {}

			cmd = self.expectPath  +" "
			cmd += "'" + self.pathToPlugin + self.connectParams[u"expectCmdFile"][uType] + "' " 
			cmd += "'" + userid + "' '"+passwd + "' " 
			cmd += self.ipNumbersOf[u"VD"] + " " 
			cmd += "'" + self.escapeExpect(self.connectParams[u"promptOnServer"][self.ipNumbersOf[u"VD"]]) + "' " 
			cmd += " XXXXsepXXXXX " 
			cmd += cmdstr
			if self.decideMyLog(u"Expect"): self.indiLOG.log(10,u"UNIFI getMongoData cmd " +cmd )
			ret = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
			dbJson, error= self.makeJson(ret[0], "XXXXsepXXXXX")
			if self.decideMyLog(u"Video"): self.indiLOG.log(10,u"UNIFI getMongoData return {}\n{}".format(ret[0], ret[1]) )
			if error !="":
				self.indiLOG.log(40,u"getMongoData camera system (dump, no json conversion)	info:\n>>{}    {}<<\n>>{}".format(error, cmd, ret[0]) )
				return []
			return	dbJson
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
				if self.decideMyLog(u"Video"): self.indiLOG.log(40," getMongoData error: {}\n{}".format(ret[0], ret[1]))
		return []

	####-----------------	 ---------
	def makeJson(self, dumpIN, sep):  ## {} separated by \n
		try:
			out =[]
			temp = u"empty"
			temp2 = u"empty"
			begStr,endStr =u"{","}"
			dump		 = dumpIN.split(sep)
			lDump = len(dump)
			if lDump <3: return "","error len(split):"+unicode(lDump)
			if lDump >3:
				dump = dump[lDump-3:]
			dump  = dump[1].strip("\n").strip("\r")
			s1 = dump.find(begStr)
			dump = dump[s1:]
			s2 = dump.rfind(endStr)
			dump = dump[:s2+1].strip("\n").strip("\r")
			dumpSplit = dump.split("\n")
			for line in dumpSplit:
				if len(line) < 5: continue
				nnn1   = line.find(begStr)
				temp   = line[nnn1:]
				nnn2   = temp.rfind(endStr)
				temp   = temp[0:nnn2+1]
				temp2	= self.replaceFunc(temp).strip()
				if len(temp2) >2:
					try:
						o =json.loads(temp2)
						out.append(o)
					except:
						self.indiLOG.log(40,u"makeJson error , trying to fix:\ntemp2>>>>>"+ unicode(temp2)+"<<<<<\n>>>>"+unicode(dumpIN)+"<<<<<" )
						try:
							o=json.loads(temp2+"}")
							out.append(o)
							self.indiLOG.log(40,u"makeJson error fixed " )
						except	Exception, e:
							self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

			return out, ""
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
				self.indiLOG.log(40,u"makeJson error :\ndump>>>>"+unicode(dumpIN)+"<<<<<" )
		return dump, "error"
	####-----------------	 ---------
	def makeJson2(self, dump, sep):
		try:
			out={}
			begStr,endStr ="{","}"
			dump		 = dump.split(sep)
			if len(dump) !=3: return ""
			dump  = dump[1].replace("\n","").replace("\r","")
			s1 = dump.find(begStr)
			dump = dump[s1:]
			s2 = dump.rfind(endStr)
			out=json.loads(dump[:s2+1])
			return out, ""
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}\nmakeJson2 error :\n>>>>>{}<<<<<".format(sys.exc_traceback.tb_lineno, e, unicode(dump) ) )
		return dump, "error"

	####-----------------	 ---------
	def replaceFunc(self, dump):
		try:
			for ii in range(500):  # remove binData(xxxxx)
				nn = dump.find(u"BinData(")
				if nn ==-1: break
				endst = dump[nn:].find(u")")
				dump = dump[0:nn-1]+'"xxx"'+ dump[nn+endst+1:]

			for kk in range(1000):	# loop over func Names, max 30
				ss = 0
				for ll in range(100): # remove " (xxx) from targest only abc(xx)
					nn = dump[ss:].find(u"(")
					if nn ==-1: break
					if dump[ss+nn-1] != " ":
						nn+=ss
						break
					ss = nn+1


				if nn ==-1: break
				startSt= dump[0:nn].rfind(" ")
				replString= dump[startSt+1:nn+1]
				lenrepString = len(replString)
				for ii in range(100):  # loop of all occurance of func replacements
					nn = dump.find(replString)
					if nn == -1: break
					pp = dump[nn:].find(u")")
					dump = dump[0:nn] + dump[nn+lenrepString:nn+pp] + dump[nn+pp+1:]
			return dump
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return ""

	####-----------------	 ---------
	def buttonZeroStatsCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		self.zeroDataStats()
		return
	####-----------------	 ---------
	def buttonResetStatsCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		self.resetDataStats(calledFrom="buttonResetStatsCALLBACK")
		return

	####-----------------  reboot unifi device	 ---------

	####-----------------	 ---------
	def filterUnifiDevices(self, filter="", valuesDict=None, typeId="", devId=""):
		xlist = []
		for ll in range(_GlobalConst_numberOfAP):
			if self.devsEnabled[u"AP"][ll]:
				xlist.append((self.ipNumbersOf[u"AP"][ll]+"-APdict","AP -"+self.ipNumbersOf[u"AP"][ll]))
		for ll in range(_GlobalConst_numberOfSW):
			if self.devsEnabled[u"SW"][ll]:
				xlist.append((self.ipNumbersOf[u"SW"][ll]+"-SWtail","SW -"+self.ipNumbersOf[u"SW"][ll]))
		if self.devsEnabled[u"GW"]:
				xlist.append((self.ipNumbersOf[u"GW"]+"-GWtail","GW -"+self.ipNumbersOf[u"GW"]))
		return xlist

	####-----------------	 ---------
	def buttonConfirmrebootCALLBACKaction(self, action1=None, filter="", typeId="", devId=""):
		return self.buttonConfirmrebootCALLBACK(valuesDict=action1.props)

	####-----------------	 ---------
	def buttonConfirmrebootCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		ip_type	 =	valuesDict[u"rebootUNIFIdeviceSelected"].split("-")
		ipNumber = ip_type[0]
		dtype	 = ip_type[1] # not used
		uType 	 = "unixDevs"
		cmd = self.expectPath +" "
		cmd+= "'"+self.pathToPlugin + "rebootUNIFIdeviceAP.exp" + "' "
		cmd+= "'"+self.connectParams[u"UserID"][uType] + "' '"+self.connectParams[u"PassWd"][uType] + "' "
		cmd+= ipNumber + " "
		cmd+= "'"+self.escapeExpect(self.connectParams[u"promptOnServer"][ipNumber]) + "' &"
		if self.decideMyLog(u"Expect"): self.indiLOG.log(10,u"REBOOT: "+cmd )
		ret = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
		if self.decideMyLog(u"ExpectRET"): self.indiLOG.log(10,u"REBOOT returned: {}".format(ret) )
		self.addToMenuXML(valuesDict)

		return


	####-----------------  set properties for all devices	---------
	def buttonConfirmSetWifiOptCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		for MAC in self.MAC2INDIGO[u"UN"]:
			try:
				dev = indigo.devices[self.MAC2INDIGO[u"UN"][MAC][u"devId"]]
				props = dev.pluginProps
				self.indiLOG.log(10,u"doing {}".format(dev.name) )
				if props[u"useWhatForStatus"].find(u"WiFi") > -1:
					props[u"useWhatForStatusWiFi"]	= "Optimized"
					props[u"idleTimeMaxSecs"]		= u"30"
					dev.replacePluginPropsOnServer(props)

					dev = indigo.devices[self.MAC2INDIGO[u"UN"][MAC][u"devId"]]
					props = dev.pluginProps
					self.indiLOG.log(10,u"done  {}  {} ".format(dev.name, unicode(props)) )
			except	Exception, e:
					self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		self.printALLUNIFIsreduced()
		return
	####-----------------	 ---------
	def buttonConfirmSetWifiIdleCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		for MAC in self.MAC2INDIGO[u"UN"]:
			try:
				dev = indigo.devices[self.MAC2INDIGO[u"UN"][MAC][u"devId"]]
				props = dev.pluginProps
				if props[u"useWhatForStatus"].find(u"WiFi") > -1:
					props[u"useWhatForStatusWiFi"]	= "IdleTime"
					props[u"idleTimeMaxSecs"]		= u"30"
					dev.replacePluginPropsOnServer(props)
			except:
				pass
		self.printALLUNIFIsreduced()
		return
	####-----------------	 ---------
	def buttonConfirmSetWifiUptimeCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		for MAC in self.MAC2INDIGO[u"UN"]:
			try:
				dev = indigo.devices[self.MAC2INDIGO[u"UN"][MAC][u"devId"]]
				props = dev.pluginProps
				if props[u"useWhatForStatus"].find(u"WiFi") > -1:
					props[u"useWhatForStatusWiFi"]	= u"UpTime"
					dev.replacePluginPropsOnServer(props)
			except:
				pass
		self.printALLUNIFIsreduced()
		return
	####-----------------	 ---------
	def buttonConfirmSetNonWifiOptCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		for MAC in self.MAC2INDIGO[u"UN"]:
			try:
				dev = indigo.devices[self.MAC2INDIGO[u"UN"][MAC][u"devId"]]
				props = dev.pluginProps
				if props[u"useWhatForStatus"].find(u"WiFi") == -1:
					props[u"useWhatForStatus"]			= u"OptDhcpSwitch"
					props[u"useAgeforStatusDHCP"]		= u"60"
					props[u"useupTimeforStatusSWITCH"]	= True
					dev.replacePluginPropsOnServer(props)
			except:
				pass
		self.printALLUNIFIsreduced()
		return
	####-----------------	 ---------
	def buttonConfirmSetNonWifiToSwitchCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		for MAC in self.MAC2INDIGO[u"UN"]:
			try:
				dev = indigo.devices[self.MAC2INDIGO[u"UN"][MAC][u"devId"]]
				props = dev.pluginProps
				if props[u"useWhatForStatus"].find(u"WiFi") == -1:
					props[u"useWhatForStatus"]			= u"SWITCH"
					props[u"useupTimeforStatusSWITCH"]	= True
					dev.replacePluginPropsOnServer(props)
			except:
				pass
		self.printALLUNIFIsreduced()
		return
	def buttonConfirmSetNonWifiToDHCPCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		for MAC in self.MAC2INDIGO[u"UN"]:
			try:
				dev = indigo.devices[self.MAC2INDIGO[u"UN"][MAC][u"devId"]]
				props = dev.pluginProps
				if props[u"useWhatForStatus"].find(u"WiFi") == -1:
					props[u"useWhatForStatus"]			= u"DHCP"
					props[u"useAgeforStatusDHCP"]		= u"60"
					dev.replacePluginPropsOnServer(props)
			except:
				pass
		self.printALLUNIFIsreduced()
		return
	####-----------------	 ---------
	def buttonConfirmSetUsePingUPonCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		for MAC in self.MAC2INDIGO[u"UN"]:
			try:
				dev = indigo.devices[self.MAC2INDIGO[u"UN"][MAC][u"devId"]]
				props = dev.pluginProps
				props[u"usePingUP"]			 = True
				dev.replacePluginPropsOnServer(props)
			except:
				pass
		self.printALLUNIFIsreduced()
		return
	####-----------------	 ---------
	def buttonConfirmSetUsePingUPoffCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		for MAC in self.MAC2INDIGO[u"UN"]:
			try:
				dev = indigo.devices[self.MAC2INDIGO[u"UN"][MAC][u"devId"]]
				props = dev.pluginProps
				props[u"usePingUP"]			 = False
				dev.replacePluginPropsOnServer(props)
			except:
				pass
		self.printALLUNIFIsreduced()
		return
	####-----------------	 ---------
	def buttonConfirmSetUsePingDOWNonCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		for MAC in self.MAC2INDIGO[u"UN"]:
			try:
				dev = indigo.devices[self.MAC2INDIGO[u"UN"][MAC][u"devId"]]
				props = dev.pluginProps
				props[u"usePingDOWN"]		   = True
				dev.replacePluginPropsOnServer(props)
			except:
				pass
		self.printALLUNIFIsreduced()
		return
	####-----------------	 ---------
	def buttonConfirmSetUsePingDOWNoffCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		for MAC in self.MAC2INDIGO[u"UN"]:
			try:
				dev = indigo.devices[self.MAC2INDIGO[u"UN"][MAC][u"devId"]]
				props = dev.pluginProps
				props[u"usePingDOWN"]		   = False
				dev.replacePluginPropsOnServer(props)
			except:
				pass
		self.printALLUNIFIsreduced()
		return
	####-----------------	 ---------
	def buttonConfirmSetExpTimeCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		for MAC in self.MAC2INDIGO[u"UN"]:
			try:
				dev = indigo.devices[self.MAC2INDIGO[u"UN"][MAC][u"devId"]]
				props = dev.pluginProps
				props[u"expirationTime"]			  =int(valuesDict[u"expirationTime"])
				dev.replacePluginPropsOnServer(props)
			except:
				pass
		self.printALLUNIFIsreduced()
		return

	####-----------------	 ---------
	def buttonConfirmSetExpTimeMinCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		for MAC in self.MAC2INDIGO[u"UN"]:
			try:
				dev = indigo.devices[self.MAC2INDIGO[u"UN"][MAC][u"devId"]]
				props = dev.pluginProps
				try:
					if int(props[u"expirationTime"]) < int(valuesDict[u"expirationTime"]):
						props[u"expirationTime"]		= int(valuesDict[u"expirationTime"])
				except:
					props[u"expirationTime"]			= int(valuesDict[u"expirationTime"])
				dev.replacePluginPropsOnServer(props)
			except:
				pass
		self.printALLUNIFIsreduced()
		return


	####-----------------	 ---------
	def inpDummy(self, valuesDict=None, filter="", typeId="", devId=""):
		return valuesDict

	####-----------------  filter	---------

	####-----------------  setconfig default values	---------
	def setfilterunifiCloudKeyListOfSiteNames(self, valuesDict):
		if self.refreshCallbackMethodAlreadySet == u"yes": return 
		valuesDict[u"unifiCloudKeySiteName"] = self.unifiCloudKeySiteName
		self.refreshCallbackMethodAlreadySet = u"yes" # only do it once after called 
		return valuesDict

	####----------------- set unifi controller site ID anmes in dynamic list ---------
	def filterunifiCloudKeyListOfSiteNames(self, filter="", valuesDict=None, typeId="", devId=""):

		xList = [[u"x",u"set to empty = re-read list from controller"]]
		for xx in self.unifiCloudKeyListOfSiteNames:
			xList.append([xx,xx])
		return xList

	####-----------------	 ---------
	def filterWiFiDevice(self, filter="", valuesDict=None, typeId="", devId=""):

		xList = []
		for dev in indigo.devices.iter(u"props.isUniFi"):
			if u"AP" not	 in dev.states:		  continue
			if len(dev.states[u"AP"]) < 5:	  continue
			xList.append([dev.states[u"MAC"].lower(),dev.name+u"--"+ dev.states[u"MAC"] +u"-- AP:"+dev.states[u"AP"]])
		return sorted(xList, key=lambda x: x[1])

	####-----------------	 ---------
	def filterUNIFIsystemDevice(self, filter="", valuesDict=None, typeId="", devId=""):

		xList = []
		for dev in indigo.devices.iter(u"props.isSwitch,props.isGateway,props.isAP"):
			xList.append([dev.states[u"MAC"].lower(),dev.name+"--"+ dev.states[u"MAC"] ])
		return sorted(xList, key=lambda x: x[1])
	####-----------------	 ---------
	def filterCameraDevice(self, filter="", valuesDict=None, typeId="", devId=""):

		xList = []
		if self.cameraSystem == u"nvr":	
			for dev in indigo.devices.iter(u"props.isCamera"):
				xList.append([dev.id,dev.name])
		if self.cameraSystem == u"protect":	
			for dev in indigo.devices.iter(u"props.isProtectCamera"):
				for camId in self.PROTECT:
					if dev.id == self.PROTECT[camId]["devId"]:
						xList.append([dev.id,dev.name])
						break
		return sorted(xList, key=lambda x: x[1])


	####-----------------	 ---------
	def filterUNIFIsystemDeviceSuspend(self, filter="", valuesDict=None, typeId="", devId=""):

		xList = []
		for dev in indigo.devices.iter(u"props.isSwitch,props.isGateway,props.isAP"):
			xList.append([dev.id,dev.name])
		return sorted(xList, key=lambda x: x[1])

	####-----------------	 ---------
	def filterUNIFIsystemDeviceSuspended(self, filter="", valuesDict=None, typeId="", devId=""):

		xList = []
		for dev in indigo.devices.iter(u"props.isSwitch,props.isGateway,props.isAP"):
			xList.append([dev.id,dev.name])
		return sorted(xList, key=lambda x: x[1])

	####-----------------	 ---------
	def filterAPdevices(self, filter="", valuesDict=None, typeId="", devId=""):

		xList = []
		for dev in indigo.devices.iter(u"props.isAP"):
			xList.append([dev.id,dev.name])
		return sorted(xList, key=lambda x: x[1])



	####-----------------	 ---------
	def filterMACNoIgnored(self, filter="", valuesDict=None, typeId="", devId=""):
		xlist = []
		for dev in indigo.devices.iter(self.pluginId):
			if u"MAC" in dev.states:
				if u"displayStatus" in dev.states and   dev.states[u"displayStatus"].find(u"ignored") >-1: continue
				mac = dev.states[u"MAC"]
				if self.isValidMAC(mac):
					xlist.append([mac,dev.states[u"MAC"] + u" - "+dev.name])
				else:
					xlist.append([u"bad mac",u"badMAC#-"+dev.states[u"MAC"] + u" - "+dev.name])
		return sorted(xlist, key=lambda x: x[1])

	####-----------------	 ---------
	def filterMAC(self, filter="", valuesDict=None, typeId="", devId=""):
		xlist = []
		for dev in indigo.devices.iter(self.pluginId):
			if u"MAC" in dev.states:
				mac = dev.states[u"MAC"]
				if self.isValidMAC(mac):
					xlist.append([dev.states[u"MAC"],dev.name+u" - "+dev.states[u"MAC"]])
				else:
					xlist.append([u"bad mac",u"badMAC#-"+dev.name+u" - "+dev.states[u"MAC"]])
		return sorted(xlist, key=lambda x: x[1])

	####-----------------	 ---------
	def filterMACunifiOnly(self, filter="", valuesDict=None, typeId="", devId=""):
		xlist = []
		for dev in indigo.devices.iter(u"props.isUniFi"):
			if u"MAC" in dev.states:
				xlist.append([dev.states[u"MAC"],dev.name+u"--"+dev.states[u"MAC"] ])
		return sorted(xlist, key=lambda x: x[1])

	####-----------------	 ---------
	def filterMACunifiAndCameraOnly(self, filter="", valuesDict=None, typeId="", devId=""):
		xlist = []
		maclist =[]
		for dev in indigo.devices.iter(u"props.isUniFi"):
			if u"MAC" in dev.states:
				if dev.deviceTypeId not in [u"UniFi"] : continue
				if u"status" in dev.states and dev.states[u"status"].find(u"up") >-1:
					xlist.append([dev.states[u"MAC"],dev.name+u"--"+dev.states[u"MAC"] ])
					maclist.append(dev.states[u"MAC"])
		for dev in indigo.devices.iter(u"props.isCamera"):
			if u"MAC" in dev.states:
				if dev.deviceTypeId not in [u"camera"] : continue
				if dev.states[u"MAC"] in maclist: continue
				xlist.append([dev.states[u"MAC"],dev.name+u"--"+dev.states[u"MAC"] ])
		return sorted(xlist, key=lambda x: x[1])

	####-----------------	 ---------
	def filterMACunifiOnlyUP(self, filter="", valuesDict=None, typeId="", devId=""):
		xlist = []
		for dev in indigo.devices.iter(u"props.isUniFi"):
			if u"MAC" in dev.states:
				if u"status" in dev.states and dev.states[u"status"].find(u"up") >-1:
					xlist.append([dev.states[u"MAC"],dev.name+u"--"+dev.states[u"MAC"] ])
		return sorted(xlist, key=lambda x: x[1])

	####-----------------	 ---------
	def filterMAConlyAP(self, filter="", valuesDict=None, typeId="", devId=""):
		xlist = []
		for dev in indigo.devices.iter(u"props.isAP"):
			if u"MAC" in dev.states:
				if u"status" in dev.states and dev.states[u"status"].find(u"up") >-1:
					xlist.append([dev.states[u"MAC"],dev.name+u"--"+dev.states[u"MAC"] ])
		return sorted(xlist, key=lambda x: x[1])


	####-----------------	 ---------
	def filterMACunifiIgnored(self, filter="", valuesDict=None, typeId="", devId=""):
		xlist = []
		for MAC in self.MACignorelist:
				textMAC = MAC
				for dev in indigo.devices.iter(u"props.isUniFi,props.isCamera"):
					if u"MAC" in dev.states and MAC == dev.states[u"MAC"]:
						textMAC = dev.name+" - "+MAC
						break
				xlist.append([MAC,textMAC])
		return sorted(xlist, key=lambda x: x[1])

	####-----------------  logging for specific MAC number	 ---------
	####-----------------	 ---------
	def filterMACspecialUNIgnore(self, filter="", valuesDict=None, typeId="", devId=""):
		xlist = []
		for MAC in self.MACSpecialIgnorelist:
			xlist.append([MAC,MAC])
		return sorted(xlist, key=lambda x: x[1])

	####-----------------  logging for specific MAC number	 ---------



	####-----------------	 ---------
	def buttonConfirmStartLoggingCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		self.MACloglist[valuesDict[u"MACdeviceSelected"]]=True
		self.indiLOG.log(10,u"start track-logging for MAC# {}".format(valuesDict[u"MACdeviceSelected"]) )
		if valuesDict[u"keepMAClogList"] == "1":
			self.writeJson(self.MACloglist, fName=self.indigoPreferencesPluginDir+"MACloglist")
		else:
			self.writeJson({}, fName=self.indigoPreferencesPluginDir+"MACloglist")
		return
	####-----------------	 ---------
	def buttonConfirmStopLoggingCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		self.MACloglist = {}
		self.writeJson({}, fName=self.indigoPreferencesPluginDir+"MACloglist")
		self.indiLOG.log(10,u" stop logging of MAC #s")
		return

	####-----------------  device info	 ---------
	def buttonConfirmPrintMACCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		self.printMACs(MAC=valuesDict[u"MACdeviceSelected"])
		return
	####-----------------	 ---------
	def buttonprintALLMACsCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		self.printALLMACs()
		return
	####-----------------	 ---------
	def printALLUNIFIsreducedMenue(self, valuesDict=None, filter="", typeId="", devId=""):
		self.printALLUNIFIsreduced()
		return
	####-----------------	 ---------




	####-----------------  GROUPS START	   ---------
	####-----------------	 ---------

	def printGroupsCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		self.printGroups()
		return


	####-----------------  add devices to groups  menu	 ---------
	def buttonConfirmAddDevGroupCALLBACK(self, valuesDict=None, typeId="", devId=0):
		try:
			newGroup =	valuesDict[u"addRemoveGroupsWhichGroup"]
			devtypes =	valuesDict[u"addRemoveGroupsWhichDevice"]
			types	 =""; lanWifi=""
			if	 devtypes == "system":	 types ="props.isGateway,props.isSwitch,props.isAP"
			elif devtypes == "neighbor": types ="props.isNeighbor"
			elif devtypes == "LAN":		 types ="props.isUniFi" ; lanWifi ="LAN"
			elif devtypes == "wifi":	 types ="props.isUniFi" ; lanWifi ="wifi"
			if types !="":
				for dev in indigo.devices.iter(types):
					if lanWifi == "wifi" and "AP" in dev.states:
						if ( dev.states[u"AP"] =="" or
							 dev.states[u"signalWiFi"]	  =="" ): continue
					if lanWifi == "LAN" and "AP" in dev.states:
						if not	( dev.states[u"AP"] =="" or
								  dev.states[u"signalWiFi"]	   =="" ): continue
					props = dev.pluginProps
					props[newGroup] = True
					dev.replacePluginPropsOnServer(props)
					gMembers = self.makeGroupMemberstring(props)
					dev = indigo.devices[dev.id]
					self.updateDevStateGroupMembers(dev,gMembers)
				self.statusChanged = 2

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return valuesDict

	####-----------------	  ---------
	def updateDevStateGroupMembers(self,dev,gMembers):
		if dev.states[u"groupMember"] != gMembers:
			dev.updateStateOnServer("groupMember",gMembers)
		return

	####-----------------	  ---------
	def	 makeGroupMemberstring(self,inputDict):
		gMembers=""
		for group in _GlobalConst_groupList:
			if group in inputDict and unicode(inputDict[group]).lower() =="true" :
				gMembers+=group+u","
		return gMembers.strip(",")



	####-----------------  remove devices to groups	 menu	---------
	def buttonConfirmRemDevGroupCALLBACK(self, valuesDict=None, typeId="", devId=0):
		try:
			self.indiLOG.log(10,u" valuesDict "+unicode(_GlobalConst_groupList)+"  "+ unicode(valuesDict))
			newGroup =	valuesDict[u"addRemoveGroupsWhichGroup"]
			devtypes =	valuesDict[u"addRemoveGroupsWhichDevice"]
			types	 =""; lanWifi=""
			if	 devtypes == "system":	 types =",props.isGateway,props.isSwitch,props.isAP"
			elif devtypes == "neighbor": types =",props.isNeighbor"
			elif devtypes == "LAN":		 types =",props.isUniFi" ; lanWifi ="LAN"
			elif devtypes == "wifi":	 types =",props.isUniFi" ; lanWifi ="wifi"
			for dev in indigo.devices.iter(self.pluginId+types):
				if lanWifi == "wifi" and "AP" in dev.states:
					if ( dev.states[u"AP"] =="" or
						 dev.states[u"signalWiFi"]	  =="" ): continue
				if lanWifi == "LAN" and "AP" in dev.states:
					if not	( dev.states[u"AP"] =="" or
							  dev.states[u"signalWiFi"]	   =="" ): continue

				props = dev.pluginProps
				if newGroup in props:
					del props[newGroup]
				dev.replacePluginPropsOnServer(props)
				gMembers = self.makeGroupMemberstring(props)
				self.updateDevStateGroupMembers(dev,gMembers)

			self.statusChanged = 2
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return valuesDict


	####-----------------	 ---------
	def filterGroupNoName(self, valuesDict=None, filter="", typeId="", devId=""):
		xList=[]
		for ii in range(_GlobalConst_numberOfGroups):
			memberMAC = ""
			group = unicode(ii)
			gName = group
			try:
				gg =  indigo.variables["Unifi_Count_Group"+group+"_name"].value
				if gg.find(u"me to what YOU like") == -1:
					gName= group+"-"+gg
			except: pass
			xList.append(["Group"+group, gName])
		return xList
	####-----------------	 ---------
	def filterGroups(self, valuesDict=None, filter="", typeId="", devId=""):

		xList=[]
		for ii in range(_GlobalConst_numberOfGroups):
			members = self.groupStatusList["Group"+unicode(ii)]["members"]
			#self.myLog( text="members: "+unicode(members))
			gName = unicode(ii)
			#try:
			gg =  indigo.variables["Unifi_Count_Group"+gName+"_name"].value
			if gg.find(u"me to what YOU like") == -1:
				gName += "-"+gg[0:20]
			#except: pass
			memberMAC = ""
			nn = 0
			for id in members:
				nn +=1
				if nn > 6:
					memberMAC +="..."
				try:
					dev = indigo.devices[int(id)]
					MAC = dev.states[u"MAC"]
				except	Exception, e:
					self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
					continue
				memberMAC += dev.name[0:10]+";"
			xList.append([unicode(ii), gName+"=="+ memberMAC.strip("; ")])
		#self.myLog( text=unicode(xList))
		return xList

	####-----------------	 ---------
	def buttonConfirmgroupCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		self.selectedGroup		  = valuesDict[u"selectedGroup"]
		return valuesDict

	####-----------------	 ---------
	def filterGroupMembers(self, valuesDict=None, filter="", typeId="", devId=""):
		xList=[]
		try: sg = int(self.selectedGroup)
		except: return xList
		for mm in self.groupStatusList[u"Group"+unicode(sg)][u"members"]:
			#self.myLog( text=unicode(mm))
			try:
				dev = indigo.devices[int(mm)]
			except: continue
			xList.append([mm,dev.name + u"- "+ dev.states[u"MAC"]])
		#self.myLog( text="group members: "+unicode(xList))
		return xList

	####-----------------	 ---------
	def buttonConfirmremoveGroupMemberCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		mm	= valuesDict[u"selectedGroupMemberIndigoIdremove"]
		gpN = u"Group"+unicode(self.selectedGroup)
		try:
			dev = indigo.devices[int(mm)]
		except:
			self.indiLOG.log(30,u" bad dev id: "+unicode(mm) )
			return
		props = dev.pluginProps
		if mm in self.groupStatusList[gpN][u"members"]:
			del self.groupStatusList[gpN][u"members"][mm]
		if gpN in props and props[gpN]:
			props[gpN] = False
			dev.replacePluginPropsOnServer(props)
			gMembers = self.makeGroupMemberstring(props)
			self.updateDevStateGroupMembers(dev,gMembers)
		return valuesDict


	####-----------------	 ---------
	def buttonConfirmremoveALLGroupMembersCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		gpN = u"Group"+unicode(self.selectedGroup)
		self.groupStatusList[gpN][u"members"] ={}
		for dev in indigo.devices.iter(self.pluginId):
			props=dev.pluginProps
			if gpN in props and props[gpN]:
				props[gpN] = False
				gMembers = self.makeGroupMemberstring(props)
				dev.replacePluginPropsOnServer(props)
				gMembers = self.makeGroupMemberstring(props)
				self.updateDevStateGroupMembers(dev,gMembers)

		#self.myLog( text=" after	: "+unicode(self.groupStatusList[gpN]["members"]) )
		#self.myLog( text="        : "+unicode(props) )
		return valuesDict



	####-----------------	 ---------
	def filterDevicesToAddToGroup(self, valuesDict=None, filter="", typeId="", devId=""):
		xList=[]
		try: sg = int(self.selectedGroup)
		except: return xList
		for dev in indigo.devices.iter(u"props.isUniFi"):
			props = dev.pluginProps
			if unicode(dev.id) in  self.groupStatusList[u"Group"+unicode(sg)][u"members"]: continue
			xList.append([unicode(dev.id),dev.name + u"- "+ dev.states[u"MAC"]])
		#self.myLog( text="group members: "+unicode(xList))
		return xList

	####-----------------	 ---------
	def buttonConfirmADDGroupMemberCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		mm	= valuesDict[u"selectedGroupMemberIndigoIdadd"]
		gpN = u"Group"+unicode(self.selectedGroup)
		try:
			dev = indigo.devices[int(mm)]
		except:
			self.indiLOG.log(30,u" bad dev id: "+unicode(mm) )
			return
		props = dev.pluginProps
		#self.myLog( text=" add to	 from group#:"+unicode(self.selectedGroup)+"  member: "+ dev.name+"     "+ dev.states[u"MAC"]+"     "+unicode(props) )
		if mm not in self.groupStatusList[gpN][u"members"]:
			self.groupStatusList[gpN][u"members"][mm]=True
		props[gpN] =True
		dev.replacePluginPropsOnServer(props)
		gMembers = self.makeGroupMemberstring(props)
		self.updateDevStateGroupMembers(dev,gMembers)
		#self.printMACs(dev.states[u"MAC"])
		return valuesDict



	####-----------------  GROUPS END	 ---------
	####-----------------	 ---------


	####-----------------  Ignore special MAC info	 ---------
	def buttonConfirmStartIgnoringSpecialMACCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		MAC = valuesDict[u"MACspecialIgnore"]
		if not self.isValidMAC(MAC):
			valuesDict[u"MSG"] = u"bad MAC.. must be 12:xx:23:xx:45:aa"
			return valuesDict
		self.MACSpecialIgnorelist[valuesDict[u"MACspecialIgnore"]]=1
		self.indiLOG.log(10,u"start ignoring  MAC# "+valuesDict[u"MACspecialIgnore"])
		self.saveMACdata(force=True)
		valuesDict[u"MSG"] = u"ok"
		return valuesDict
	####-----------------  UN- Ignore special MAC info	 ---------
	####----------------- ---------
	def buttonConfirmStopIgnoringSpecialMACCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):

		try: del self.MACSpecialIgnorelist[valuesDict[u"MACspecialUNIgnored"]]
		except: pass
		self.indiLOG.log(10,u" stop ignoring  MAC# " +valuesDict[u"MACspecialUNIgnored"])
		self.saveMACdata(force=True)
		valuesDict[u"MSG"] = u"ok"
		return valuesDict

	####-----------------  Ignore MAC info	 ---------
	def buttonConfirmStartIgnoringCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		self.MACignorelist[valuesDict[u"MACdeviceSelected"]]=1
		self.indiLOG.log(10,u"start ignoring  MAC# "+valuesDict[u"MACdeviceSelected"])
		for dev in indigo.devices.iter(u"props.isUniFi,props.isCamera"):
			if u"MAC" in dev.states	 and dev.states[u"MAC"] == valuesDict[u"MACdeviceSelected"]:
				if u"displayStatus" in dev.states:
					dev.updateStateOnServer(u"displayStatus",self.padDisplay(u"ignored")+datetime.datetime.now().strftime(u"%m-%d %H:%M:%S"))
					dev.updateStateImageOnServer(indigo.kStateImageSel.PowerOff)
				dev.updateStateOnServer(u"status",value= u"ignored", uiValue=self.padDisplay(u"ignored")+datetime.datetime.now().strftime(u"%m-%d %H:%M:%S"))
		valuesDict[u"MSG"] = u"ok"
		self.saveMACdata(force=True)
		return valuesDict
	####-----------------  UN- Ignore MAC info	 ---------
	####-----------------	 ---------
	def buttonConfirmStopIgnoringCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):

		for dev in indigo.devices.iter(u"props.isUniFi,props.isCamera"):
			if u"MAC" in dev.states	 and dev.states[u"MAC"] == valuesDict[u"MACdeviceIgnored"]:
				if u"displayStatus" in dev.states:
					dev.updateStateOnServer(u"displayStatus",self.padDisplay(u"")+datetime.datetime.now().strftime(u"%m-%d %H:%M:%S"))
					dev.updateStateImageOnServer(indigo.kStateImageSel.PowerOff)
				dev.updateStateOnServer(u"status","")
				dev.updateStateOnServer(u"onOffState", value=False, uiValue=self.padDisplay(u"")+datetime.datetime.now().strftime(u"%m-%d %H:%M:%S"))
		try: del self.MACignorelist[valuesDict[u"MACdeviceIgnored"]]
		except: pass
		valuesDict[u"MSG"] = u"ok"
		self.saveMACdata(force=True)
		self.indiLOG.log(10,u" stop ignoring  MAC# " +valuesDict[u"MACdeviceIgnored"])
		return valuesDict



	####-----------------  powercycle switch port	---------
	####-----------------	 ---------
	def filterUnifiSwitchACTION(self, valuesDict=None, filter="", typeId="", devId=""):
		return self.filterUnifiSwitch(valuesDict)

	####-----------------	 ---------
	def filterUnifiSwitch(self, filter="", valuesDict=None, typeId="", devId=""):
		xList = []
		for dev in indigo.devices.iter(u"props.isSwitch"):
			swNo = int(dev.states[u"switchNo"])
			if self.devsEnabled[u"SW"][swNo]:
				xList.append((unicode(swNo)+u"-SWtail-"+unicode(dev.id),unicode(swNo)+"-"+self.ipNumbersOf[u"SW"][swNo]+u"-"+dev.name))
		return xList

	def buttonConfirmSWCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		self.unifiSwitchSelectedID =  valuesDict[u"selectedUnifiSwitch"].split("-")[2]
		return

	####-----------------	 ---------
	def filterUnifiSwitchPort(self, filter="", valuesDict=None, typeId="", devId=""):

		xList = []
		try:	int(self.unifiSwitchSelectedID)
		except: return xList

		dev = indigo.devices[int(self.unifiSwitchSelectedID)]
		snNo = unicode(dev.states[u"switchNo"] )
		for port in range(99):
			if u"port_%02d"%port not in dev.states: continue
			if	dev.states[u"port_%02d"%port].find(u"poe") >-1:
				name  = ""
				if	dev.states[u"port_%02d"%port].find(u"poeX") >-1:
					name = " - empty"
				else:
					name = ""
					for dev2 in indigo.devices.iter(u"props.isUniFi"):
						if u"SW_Port" in dev2.states and len(dev2.states[u"SW_Port"]) > 2:
							if not dev2.enabled: continue
							sw	 = dev2.states[u"SW_Port"].split(":")
							if sw[0] == snNo:
								if sw[1].find(u"poe") >-1 and dev.states[u"status"] != "expired":
									if unicode(port) == sw[1].split("-")[0]:
										name = " - "+dev2.name
										break
								elif dev.states[u"status"] != "expired":
									if unicode(port) == sw[1].split("-")[0]:
										name = " - "+dev2.name
										break
								else:
									if unicode(port) == sw[1].split("-")[0]:
										name = " - "+dev2.name
				xList.append([port,u"port#"+unicode(port)+name])
		return xList

	####-----------------	 ---------
	def filterUnifiClient(self, filter="", valuesDict=None, typeId="", devId=""):

		xList = []
		for dev2 in indigo.devices.iter(u"props.isUniFi"):
			if u"SW_Port" in dev2.states and len(dev2.states[u"SW_Port"]) > 2:
				sw	 = dev2.states[u"SW_Port"].split(":")
				if sw[1].find(u"poe") >-1:
					port = sw[1].split("-")[0]
					xList.append([sw[0]+"-"+port,u"sw"+sw[0]+"-"u"port#"+unicode(port)+" - "+dev2.name])
		xList.sort(key = lambda x: x[1]) 
		return xList


	####-----------------	 ---------
	def buttonConfirmpowerCycleCALLBACKaction(self, action1=None, filter="", typeId="", devId=""):
		return self.buttonConfirmpowerCycleCALLBACK(valuesDict=action1.props)

	####-----------------	 ---------
	def buttonConfirmpowerCycleClientsCALLBACKaction(self, action1=None, filter="", typeId="", devId=""):
		return self.buttonConfirmpowerCycleClientsCALLBACK(valuesDict=action1.props)

	####-----------------	 ---------
	def buttonConfirmpowerCycleCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		onOffCycle	= valuesDict[u"onOffCycle"]
		ip_type		=  valuesDict[u"selectedUnifiSwitch"].split(u"-")
		ipNumber	= self.ipNumbersOf[u"SW"][int(ip_type[0])]
		dtype		= ip_type[1]
		port		= unicode(valuesDict[u"selectedUnifiSwitchPort"])
		cmd 		= self.expectPath +" "
		if onOffCycle == "CYCLE":
			cmd += "'"+self.pathToPlugin + u"cyclePort.exp" + "' "
		elif  onOffCycle =="ON":
			cmd += "'"+self.pathToPlugin + u"onPort.exp" + "' "
		elif  onOffCycle =="OFF":
			cmd += "'"+self.pathToPlugin + u"offPort.exp" + "' "
		cmd += "'"+self.connectParams[u"UserID"][u"unixDevs"] + u"' '"+self.connectParams[u"PassWd"][u"unixDevs"] + u"' "
		cmd += ipNumber + " "
		cmd += port + u" "
		cmd += "'" + self.escapeExpect(self.connectParams[u"promptOnServer"][ipNumber]) +u"' &"
		if self.decideMyLog(u"Expect"): self.indiLOG.log(10,u"RECYCLE: "+cmd )
		ret = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
		if self.decideMyLog(u"ExpectRET"): self.indiLOG.log(10,u"RECYCLE returned: {}".format(ret))
		self.addToMenuXML(valuesDict)
		return valuesDict

	####-----------------	 ---------
	def buttonConfirmpowerCycleClientsCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		ip_type	 =	valuesDict[u"selectedUnifiClientSwitchPort"].split(u"-")
		if len(ip_type) != 2: return valuesDict
		valuesDict[u"selectedUnifiSwitch"]		= ip_type[0]+u"-SWtail"
		valuesDict[u"selectedUnifiSwitchPort"]	= ip_type[1]
		self.buttonConfirmpowerCycleCALLBACK(valuesDict)
		return valuesDict


	####-----------------  suspend / activate unifi devices	   ---------
	def buttonConfirmsuspendCALLBACKaction(self, action1=None, filter="", typeId="", devId=""):
		self.buttonConfirmsuspendCALLBACKbutton(valuesDict=action1.props)

	####-----------------  suspend / activate unifi devices	   ---------
	def buttonConfirmactivateCALLBACKaction(self, action1=None, filter="", typeId="", devId=""):
		self.buttonConfirmactivateCALLBACKbutton(valuesDict=action1.props)

	 ####-----------------	suspend / activate unifi devices	---------
	def buttonConfirmsuspendCALLBACKbutton(self, valuesDict=None, filter="", typeId="", devId=""):
		try:
			ID = int(valuesDict[u"selectedDevice"])
			dev= indigo.devices[ID]
			ip = dev.states[u"ipNumber"]
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			return
		self.indiLOG.log(10,u"suspending Unifi system device {} {} - only in plugin".format(dev.name, ip) )
		self.setSuspend(ip, time.time()+9999999)
		self.exeDisplayStatus(dev,"susp")
		self.addToMenuXML(valuesDict)
		return valuesDict

	def buttonConfirmactivateCALLBACKbutton(self, valuesDict=None, filter="", typeId="", devId=""):
		try:
			ID = int(valuesDict[u"selectedDevice"])
			dev= indigo.devices[ID]
			ip = dev.states[u"ipNumber"]
			try:
				self.delSuspend(ip)
				self.exeDisplayStatus(dev,"up")
				self.indiLOG.log(10,u"reactivating Unifi system device {} {} - only in plugin".format(dev.name, ip) )
			except: pass
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		self.addToMenuXML(valuesDict)
		return valuesDict



	####-----------------  Unifi controller backup  ---------
	def getBackupFilesFromController(self, valuesDict=None, filter="", typeId="", devId=""):
		if not self.unifiControllerBackupON: return 

		cmd = u"cd '"+self.indigoPreferencesPluginDir+"backup';"
		cmd += self.expectPath 
		cmd += " '"+self.pathToPlugin + "controllerbackup.exp' "
		cmd += " '"+self.connectParams[u"UserID"][u"unixDevs"]+"' "
		cmd += " '"+self.connectParams[u"PassWd"][u"unixDevs"]+"' "
		cmd +=     self.unifiCloudKeyIP
		cmd += " '"+self.ControllerBackupPath.rstrip("/")+"'"

		if self.decideMyLog(u"Expect"): self.indiLOG.log(10,u"backup cmd: {}".format(cmd) )

		ret = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()

		if self.decideMyLog(u"ExpectRET"): self.indiLOG.log(10,u"backup cmd returned: {}".format(ret))

		return 


	####-----------------  Unifi api calls	  ---------


######## block / unblock reconnect
	####-----------------	 ---------
	def buttonConfirmReconnectCALLBACKaction(self, action1=None, filter="", typeId="", devId=""):
		return self.buttonConfirmReconnectCALLBACK(valuesDict=action1.props)

	####-----------------	 ---------
	def buttonConfirmReconnectCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		return self.executeCMDOnController(dataSEND={"cmd":"kick-sta","mac":valuesDict[u"selectedDevice"]},pageString=u"/cmd/stamgr",cmdType=u"post")


	####-----------------	 ---------
	def buttonConfirmBlockCALLBACKaction(self, action1=None, filter="", typeId="", devId=""):
		return self.buttonConfirmBlockCALLBACK(valuesDict=action1.props)

	####-----------------	 ---------
	def buttonConfirmBlockCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		ret = self.executeCMDOnController(dataSEND={"cmd":"block-sta","mac":valuesDict[u"selectedDevice"]},pageString=u"/cmd/stamgr",cmdType=u"post")
		self.getcontrollerDBForClientsLast = time.time() - self.readDictEverySeconds[u"DB"]
		return ret


	####-----------------	 ---------
	def buttonConfirmUnBlockCALLBACKaction(self, action1=None, filter="", typeId="", devId=""):
		return self.buttonConfirmUnBlockCALLBACK(valuesDict=action1.props)

	####-----------------	 ---------
	def buttonConfirmUnBlockCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		ret = self.executeCMDOnController(dataSEND={"cmd":"unblock-sta","mac":valuesDict[u"selectedDevice"]}, pageString=u"/cmd/stamgr",cmdType=u"post")
		self.getcontrollerDBForClientsLast = time.time() - self.readDictEverySeconds[u"DB"]
		return ret

######## block / unblock reconnec  end

######## reports for specific stations / devices
	def buttonConfirmGetAPDevInfoFromControllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		for dev in indigo.devices.iter(u"props.isAP"):
			MAC = dev.states[u"MAC"]
			if u"MAClan" in dev.states: 
				props = dev.pluginProps
				if u"useWhichMAC" in props and props[u"useWhichMAC"] == u"MAClan":
					MAC = dev.states[u"MAClan"]
			self.indiLOG.log(10,u"unifi-Report getting _id for AP {}  /stat/device/{}".format(dev.name, MAC) )
			jData = self.executeCMDOnController(dataSEND={}, pageString=u"/stat/device/"+MAC, jsonAction=u"returnData", cmdType=u"get")

			if len(jData) == 0 and self.unifiCloudKeyPort == "": 
				self.indiLOG.log(10,u"unifi-Report:  controller not setup, skipping other querries" )
				break

			for dd in jData:
				if u"_id" not in dd:
					self.indiLOG.log(10,"unifi-Report _id not in data")
					continue
				self.indiLOG.log(10,u"unifi-Report  _id in data:{}".format(dd[u"_id"]) )
				dev.updateStateOnServer(u"ap_id", dd[u"_id"])
				break
		self.addToMenuXML(valuesDict)
		return

	####-----------------	 ---------
	####-----------------	 ---------
	def buttonConfirmPrintDevInfoFromControllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		MAC = valuesDict[u"MACdeviceSelectedsys"]
		for dev in indigo.devices.iter(u"props.isAP,props.isSwitch,props.isGateway"):
			if u"MAC" in dev.states and dev.states[u"MAC"] != MAC: continue
			if u"MAClan" in dev.states and dev.states[u"MAClan"] != MAC:
				props = dev.pluginProps
				if u"useWhichMAC" in props and props[u"useWhichMAC"] == u"MAClan":
					MAC = dev.states[u"MAClan"]
			break	
		self.executeCMDOnController(dataSEND={}, pageString=u"/stat/device/"+MAC, jsonAction=u"print",startText=u"== Unifi Device print: /stat/device/"+MAC+" ==", cmdType=u"get")
		return

	####-----------------	 ---------
	def buttonConfirmPrintClientInfoFromControllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		MAC = valuesDict[u"MACdeviceSelectedclient"]
		self.executeCMDOnController(dataSEND={}, pageString=u"/stat/sta/"+MAC, jsonAction=u"print",startText=u"== Client print: /stat/sta/"+MAC+" ==", cmdType=u"get")
		return

######## reports all devcies
	####-----------------	 ---------
	def buttonConfirmPrintalluserInfoFromControllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		data = self.executeCMDOnController(dataSEND={}, pageString=u"/stat/alluser/", jsonAction=u"returnData", cmdType=u"get")
#		data = self.executeCMDOnController(dataSEND={"type":"all","conn":"all"}, pageString=u"/stat/alluser/", jsonAction=u"returnData", cmdType=u"get")
		self.unifsystemReport3(data, u"== ALL USER report ==")
		self.fillcontrollerDBForClients(data)
		return

	####-----------------	 ---------
	def buttonConfirmPrintuserInfoFromControllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId="", cmdType=u"get"):
		data = self.executeCMDOnController(dataSEND={}, pageString=u"/list/user/", jsonAction=u"returnData", cmdType=cmdType)
		self.unifsystemReport3(data, u"== USER report ==")



	####-----------------print DPI info  ---------
	def buttonConfirmPrintListOfBackupsFromControllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		try:
			data = self.executeCMDOnController(dataSEND={'cmd': 'list-backups'}, pageString=u"cmd/backup", jsonAction=u"returnData", cmdType=u"post")
			if len(data) == 0: 
				self.indiLOG.log(20,"no data returned from backup list")
				return valuesDict
			##[{"controller_name":"192.168.1.2","filename":"autobackup_6.0.43_20210208_0600_1612764000017.unf","type":"primary","version":"6.0.43","time":1612764000017,"datetime":"2021-02-08T06:00:00Z","format":"bson","days":30,"size":25885584},
			out = ""
			for rec in data:
				if out == "": 
					out =  u"\n== UniFi  list of backups on system {}\n".format(rec["controller_name"])
					out += u"fileName ----------------------------------------              size  days  type       version  date\n"
				out += "{:50}".format(rec["filename"]) 
				out += "{:>17,d} ".format(rec["size"]) 
				out += "{:>5}  ".format(rec["days"]) 
				out += "{:11}".format(rec["type"]) 
				out += "{:9}".format(rec["version"]) 
				out += time.strftime(u"%Y-%m-%d %H:%M:%S",time.localtime(rec["time"]/1000.))
				out += "\n"
			self.indiLOG.log(20,out)
		except	Exception, e:
			self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return

	####-----------------print DPI info  ---------
	def buttonConfirmPrintDPIFromControllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		try:
			data = {}
			data["app"] = self.executeCMDOnController(dataSEND={'type': 'by_app'}, pageString=u"stat/sitedpi", jsonAction=u"returnData", cmdType=u"post")
			data["cat"] = self.executeCMDOnController(dataSEND={'type': 'by_cat'}, pageString=u"stat/sitedpi", jsonAction=u"returnData", cmdType=u"post")
			f = open(self.pathToPlugin+"unifi_dpi.json","r")
			catappInfo = json.loads(f.read())
			f.close()
			#self.indiLOG.log(20,u"{}".format(catappInfo))
			#self.indiLOG.log(20,u"{}".format(data["app"]))
			#self.indiLOG.log(20,u"{}".format(data["cat"]))

			out1 = []
			out2 = []
			lastUpdated = ""
			for rr in data["cat"]: 
				if u'last_updated' in rr:
					lastUpdated = rr["last_updated"]
					lastUpdated = time.strftime(u"%Y-%m-%d %H:%M:%S",time.localtime(lastUpdated))
				if  "by_cat" in rr:
					for rec in rr["by_cat"]:
						o   = "{:>7d} ".format(rec["cat"]) 
						nn = unicode(rec["cat"])
						if nn in catappInfo["categories"]:
							o +=  catappInfo["categories"][nn]["name"].ljust(37)
						else:
							o +=  ("??").ljust(37)
						o += "{:>17,d}".format(rec["rx_bytes"]) 
						o += "{:>17,d}".format(rec["tx_bytes"]) 
						out1.append(o)
			for rr in data["app"]: 
				if u'last_updated' in rr:
					lastUpdated = rr["last_updated"]
					lastUpdated = time.strftime(u"%Y-%m-%d %H:%M:%S",time.localtime(lastUpdated))
				if  "by_app" in rr:
					for rec in rr["by_app"]:
						o  = "{:>7d} ".format(rec["app"]) 
						nn = unicode(rec["app"])
						if nn in catappInfo["applications"]:
							o +=  catappInfo["applications"][nn]["name"].ljust(32)
						else:
							o +=  ("??").ljust(32)
						o += "{:>5d}".format(rec["cat"]) 
						o += "{:>17,d}".format(rec["rx_bytes"]) 
						o += "{:>17,d}".format(rec["rx_bytes"]) 
						if "known_clients" in rec:
							o += "{:>9,d}".format(rec["known_clients"]) 
						out2.append(o)

			if out1 !=[] or out2 !=[]:
				out =  u"\n== UniFi  Deep Packet Info report, lastUpdated: {} == \n".format(lastUpdated)
				out =  u"\n== ** cat and app #s from https://ubntwiki.com/products/software/unifi-controller/api/cat_app_json ** \n".format(lastUpdated)
				out += u"   cat# cat Name-----------------------               rx_bytes         tx_Bytes\n"
				out += "\n".join(sorted(out1))
				out += u"\n"
				out += u"   app# app Name-----------------------  cat#         rx_bytes         tx_Bytes #clients\n"
				out += "\n".join(sorted(out2))
				self.indiLOG.log(20,out)
			else:
				self.indiLOG.log(20,"== DPI report empty, no data returned ==")

		except	Exception, e:
			self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return


####   general reports
	####-----------------	 ---------
	def buttonConfirmPrintHealthInfoFromControllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		data = self.executeCMDOnController(dataSEND={}, pageString=u"/stat/health/", jsonAction=u"returnData", cmdType=u"get")
		out = u"== HEALTH report ==\n"
		ii=0
		for item in data:
			ii+=1
			ll =unicode(ii).ljust(3)
			ll+=(item[u"subsystem"]+":").ljust(10)
			ll+=(item[u"status"]+";").ljust(10)
			if u"rx_bytes-r" in item:
				ll+=u"rx_B:"+(unicode(item[u"rx_bytes-r"])+u";").ljust(9)
			if u"tx_bytes-r" in item:
				ll+=u"tx_B:"+(unicode(item[u"tx_bytes-r"])+u";").ljust(9)

			for item2 in item:
				if item2 ==u"subsystem":  continue
				if item2 ==u"status":	  continue
				if item2 ==u"tx_bytes-r": continue
				if item2 ==u"rx_bytes-r": continue
				ll+=unicode(item2)+u":"+unicode(item[item2])+u";    "
			out+=ll+(u"\n")
		self.indiLOG.log(10,u"unifi-Report ")
		self.indiLOG.log(10,u"unifi-Report  "+out)
		return

	####-----------------	 ---------
	def buttonConfirmPrintPortForWardInfoFromControllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		data =self.executeCMDOnController(dataSEND={}, pageString=u"/stat/portforward/", jsonAction=u"returnData", cmdType=u"get")
		out = u"== PortForward report ==\n"
		out += u"##".ljust(4) + u"name".ljust(20) + u"protocol".ljust(10) + u"source".ljust(16)	+ u"fwd_port".rjust(9)+ u"dst_port".rjust(9)+ " fwd_ip".ljust(17)+ "rx_bytes".rjust(12)+ "rx_packets".rjust(12)+"\n"
		ii = 0
		for item in data:
			ii+=1
			ll = unicode(ii).ljust(4)
			ll+= item[u"name"].ljust(20)
			ll+= item[u"proto"].ljust(10)
			ll+= item[u"src"].ljust(16)
			ll+= item[u"fwd_port"].rjust(9)
			ll+= item[u"dst_port"].rjust(9)
			ll+= (" "+item[u"fwd"]).ljust(17)
			ll+= unicode(item[u"rx_bytes"]).rjust(12)
			ll+= unicode(item[u"rx_packets"]).rjust(12)
			out+=ll+("\n")
		self.indiLOG.log(10,u"unifi-Report ")
		self.indiLOG.log(10,u"unifi-Report  "+out)
		return


	####-----------------	 ---------
	def buttonConfirmPrintSessionInfoFromControllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		toT		= int(time.time()+100)
		fromT 	= toT - 30000
		data = self.executeCMDOnController(dataSEND={}, pageString=u"/stat/session?type=all&start={:d}&end={:d}".format(fromT,toT), jsonAction=u"returnData", cmdType=u"get")
		out = u"\n"
		ii = 0
		for xxx in data:
			ii += 1
			out += u"== Session report ==  #{}, client: mac={} - {}\n".format(ii, xxx[u"mac"], unicode(xxx[u"hostname"]))
			for item in  [u"ip",u"is_wired",u"is_guest",u"rx_bytes",u"tx_bytes",u"ap_mac"]:
				out += (unicode(item)+u":").ljust(35)+unicode(xxx[item])+"\n"
			out += (u"Accociated:").ljust(35)+u"{} minutes ago\n".format(int(time.time()-xxx[u"assoc_time"])/60)
			out += (u"Duration:").ljust(35)+u"{} [secs]\n".format(xxx[u"duration"])
		self.indiLOG.log(10,u"unifi-Report ")
		self.indiLOG.log(10,u"unifi-Report  "+out)
		return


	####-----------------	 ---------
	def buttonConfirmPrintAlarmInfoFromControllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		data = self.executeCMDOnController(dataSEND={}, pageString=u"/list/alarm/", jsonAction=u"returnData", cmdType=u"get")
		self.unifsystemReport1(data, True, u"    ==AlarmReport==", limit=99999)
		self.addToMenuXML(valuesDict)
		return

		out = "\n"
		ii = 0
		for xxx in data:
			ii += 1
			out += u"== Wifi Config report == SSID #{}, {}\n".format(ii, xxx[u"name"])
			for item in xxx:
				if item != u"name":
					out += (unicode(item)+u":").ljust(35)+unicode(xxx[item])+u"\n"
		self.indiLOG.log(10,u"unifi-Report ")
		self.indiLOG.log(10,u"unifi-Report  "+out)
		return


	####-----------------	 ---------
	def buttonConfirmPrintWifiConfigInfoFromControllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		data = self.executeCMDOnController(dataSEND={}, pageString=u"/rest/wlanconf", jsonAction=u"returnData", cmdType=u"get")
		out = "\n"
		ii = 0
		for xxx in data:
			ii += 1
			out += u"== Wifi Config report == # {}; SSID= {}\n".format(ii, xxx[u"name"])
			for item in xxx:
				if item not in [u"name",u"site_id",u"x_iapp_key",u"_id",u"wlangroup_id"]:
					out += (unicode(item)+u":").ljust(35)+unicode(xxx[item])+u"\n"
		self.indiLOG.log(10,u"unifi-Report ")
		self.indiLOG.log(10,u"unifi-Report  "+out)
		return


	####-----------------	 ---------
	def buttonConfirmPrintWifiChannelInfoFromControllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		data =self.executeCMDOnController(dataSEND={}, pageString=u"/stat/current-channel", jsonAction=u"returnData", cmdType=u"get")
		out = u"== Wifi Channel report ==\n"
		for xxx in data:
			for item in [u"code",u"key",u"name"]:
					out += (unicode(item)+u":").ljust(25)+unicode(xxx[item])+u"\n"
			for item in xxx:
				if item not in [u"code",u"key",u"name"]:
					out += (unicode(item)+u":").ljust(25)+unicode(xxx[item])+u"\n"
		self.indiLOG.log(10,u"unifi-Report ")
		self.indiLOG.log(10,u"unifi-Report  "+out)
		return



	####-----------------	 ---------
	def buttonConfirmPrintEventInfoFromControllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):

		limit = 100
		if u"PrintEventInfoMaxEvents" in valuesDict:
			try:	limit = int(valuesDict[u"PrintEventInfoMaxEvents"])
			except: pass

		PrintEventInfoLoginEvents = False
		if u"PrintEventInfoLoginEvents" in valuesDict:
			try:	PrintEventInfoLoginEvents = valuesDict[u"PrintEventInfoLoginEvents"]
			except: pass


		if PrintEventInfoLoginEvents:
			ltype = u"WITH"
			useLimit = limit
		else:
			ltype = u"Skipping"
			useLimit = 5*limit
		data = self.executeCMDOnController(dataSEND={"_sort":"+time", "_limit":useLimit}, pageString=u"/stat/event/", jsonAction=u"returnData", cmdType=u"put")
		self.unifsystemReport1(data, False, u"     ==EVENTs ..;  last {} events ;     -- {} login events ==".format(limit, ltype), limit, PrintEventInfoLoginEvents=PrintEventInfoLoginEvents)
		self.addToMenuXML(valuesDict)

		return

	####-----------------	 ---------
	def updateDevStateswRXTXbytes(self):
		try:
			if time.time() - self.lastupdateDevStateswRXTXbytes < 200: return 
			self.lastupdateDevStateswRXTXbytes = time.time()
			en = int( time.time()  ) * 1000
			st = en - 300*1000
			data = self.executeCMDOnController(dataSEND={u"attrs": [u"tx_bytes", u"rx_bytes", u"time"], u"start": st, u"end": en}, pageString=u"/stat/report/5minutes.user", jsonAction=u"returnData", cmdType=u"post")

			if len(data) == 0: return
			MACbytes 	= {}
			tNow 		= int(time.time()*1000)
			anyUpdate 	= False
			maxDT 		= 0
			oneBad 		= False
			for rec in data:
				#{"rx_bytes":1090.4761904761904,"tx_bytes":1428.904761904762,"time":1613157900000,"user":"b8:27:eb:c8:c7:ab","o":"user","oid":"b8:27:eb:c8:c7:ab"},
				if "user" not in rec or "time" not in rec or "tx_bytes" not in rec: 
					if not oneBad: self.indiLOG.log(10,"updateDevStateswRXTXbytes user/time/rx tx_bytes   not in rec:{}".format(rec))
					oneBad = True
					continue

				maxDT = max( maxDT, tNow - rec[u"time"] )
				if tNow - rec[u"time"] > 605*1000: 
					if not oneBad: self.indiLOG.log(10,"updateDevStateswRXTXbytes bad time tNow:{}; recT:{}; dt:{}; rec:{}".format(tNow, rec[u"time"],  tNow - rec[u"time"], rec))
					oneBad = True
					continue 
				try: 	
					## rx and tx are flipped in response 
					MACbytes[rec[u"user"]] = {u"txBytes":int(rec[u"rx_bytes"]),u"rxBytes":int(rec[u"tx_bytes"])}
				except: 
					if not oneBad: self.indiLOG.log(10,u"updateDevStateswRXTXbytes  bad data rec:{}".format(rec))
					oneBad = True
					continue

			if oneBad and self.decideMyLog(u"Special"): 
				self.indiLOG.log(10,u"updateDevStateswRXTXbytes,  data:{}".format(data))
				self.indiLOG.log(10,u"updateDevStateswRXTXbytes, maxDT:{}  MACBYTES:{}".format(maxDT/1000, MACbytes))

			for dev in indigo.devices.iter(u"props.isUniFi"):
				if not dev.enabled: continue
				mac = dev.address
				if u"rx_Bytes_Last5Minutes" in dev.states:
					if mac in MACbytes:
						tx =  MACbytes[mac][u"txBytes"]
						rx =  MACbytes[mac][u"rxBytes"]
					else:
						tx =  0
						rx =  0

					if dev.states[u"rx_Bytes_Last5Minutes"] != rx:
						anyUpdate = True
						self.addToStatesUpdateList(dev.id, u"rx_Bytes_Last5Minutes", rx)
					if dev.states[u"tx_Bytes_Last5Minutes"] != tx:
						anyUpdate = True
						self.addToStatesUpdateList(dev.id, u"tx_Bytes_Last5Minutes", tx)

			if anyUpdate:
				self.executeUpdateStatesList()

		except	Exception, e:
			self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return


	####-----------------	 ---------
	def buttonConfirmPrint7DaysWiFiInfoFromControllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):

		en = int( time.time() - (time.time() % 3600 ) ) * 1000
		st = en - 3600*1000*12*7 # 7 days
		data = self.executeCMDOnController(dataSEND={u"attrs": [u"rx_bytes", u"tx_bytes", u"num_sta", u"time"], u"start": st, u"end": en}, pageString=u"/stat/report/daily.ap", jsonAction=u"returnData", cmdType=u"post")
		self.printWifiStatReport(data, u"==  days WiFi-AP stat report ==")


	####-----------------	 ---------
	def buttonConfirmPrint48HoursWiFiInfoFromControllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):

		en = int( time.time() - (time.time() % 3600) ) * 1000
		st = en - 3600*1000*48 # 
		data = self.executeCMDOnController(dataSEND={u"attrs": [u"rx_bytes", u"tx_bytes", u"num_sta", u"time"], u"start": st, u"end": en}, pageString=u"/stat/report/hourly.ap", jsonAction=u"returnData", cmdType=u"post")
		self.printWifiStatReport(data, u"==  hours WiFi-AP stat report ==")

	####-----------------	 ---------
	def buttonConfirmPrint5MinutesWiFiInfoFromControllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):

		en = int( time.time()  ) * 1000
		st = en - 3600*1000*4 #  4 hours
		data = self.executeCMDOnController(dataSEND={u"attrs": [u"rx_bytes", u"tx_bytes", u"num_sta", u"time"], u"start": st, u"end": en}, pageString=u"/stat/report/5minutes.ap", jsonAction=u"returnData", cmdType=u"post")
		self.printWifiStatReport(data, u"==  minutes WiFi-AP stat report ==")
		return


	####-----------------	 ---------
	def printWifiStatReport(self, data, headLine):
		out = headLine+"\n"
		out+= u"##".ljust(4)
		out+= u"timeStamp".ljust(21)
		out+= u"num_sta".rjust(8)
		out+= u"rxBytes".rjust(17)
		out+= u"txBytes".rjust(17)
		out+= u"\n"
		ii=0
		lastap = ""
		for item in data:
			ii+=1
			if lastap != item[u"ap"]:
				out+= u"AP MAC #:"+item[u"ap"]+u"\n"
			lastap = item[u"ap"]

			ll =unicode(ii).ljust(4)
			if u"time" in item:
				ll+= time.strftime(u"%Y-%m-%d %H:%M:%S",time.localtime(item[u"time"]/1000)).ljust(21)
			else:				  ll+= (u" ").ljust(21)

			if u"num_sta" in item:
				ll+= unicode(item[u"num_sta"]).rjust(8)
			else:				  ll+= (" ").rjust(8)

			if u"rx_bytes" in item:
				ll+= (u"{0:,d}".format(int(item[u"rx_bytes"]))).rjust(17)
			else:				  ll+= (u" ").rjust(17)
			if u"tx_bytes" in item:
				ll+= (u"{0:,d}".format(int(item[u"tx_bytes"]))).rjust(17)
			else:				  ll+= (u" ").rjust(17)

			out+=ll+(u"\n")
		self.indiLOG.log(10,u"unifi-Report ")
		self.indiLOG.log(10,u"unifi-Report  "+out)
		return


	####-----------------	 ---------
	def buttonConfirmPrint5MinutesWanInfoFromControllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		en = int( time.time()  ) * 1000
		st = en - 3600 *1000*4 # 4 hours 
		data = self.executeCMDOnController(dataSEND={u"attrs": [u"bytes",u"wan-tx_bytes",u"wan-rx_bytes",u"wan-tx_bytes", u"num_sta", u"wlan-num_sta", u"lan-num_sta", u"time"], u"start": st, u"end": en}, pageString=u"/stat/report/5minutes.site", jsonAction=u"returnData", cmdType=u"post")
		self.unifsystemReport2(data,u"== 5 minutes WAN report ==")
		return

	####-----------------	 ---------
	def buttonConfirmPrint48HoursWanInfoFromControllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		en = int( time.time() - (time.time() % 3600) ) * 1000
		st = en - 2*86400*1000 # 2 days
		data = self.executeCMDOnController(dataSEND={u"attrs": [u"bytes",u"wan-tx_bytes",u"wan-rx_bytes",u"wan-tx_bytes", u"num_sta", u"wlan-num_sta", u"lan-num_sta", u"time"], u"start": st, u"end": en}, pageString=u"/stat/report/hourly.site", jsonAction=u"returnData", cmdType=u"post")
		self.unifsystemReport2(data,u"==  HOUR WAN report ==")
		return

	####-----------------	 ---------
	def buttonConfirmPrint7DaysWanInfoFromControllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		en = int( time.time() - (time.time() % 3600) ) * 1000
		st = en - 7*86400 *1000  # 7 days
		data = self.executeCMDOnController(dataSEND={u"attrs": [u"bytes",u"wan-tx_bytes",u"wan-rx_bytes",u"wan-tx_bytes", u"num_sta", u"wlan-num_sta", u"lan-num_sta", u"time"], u"start": st, u"end": en}, pageString=u"/stat/report/daily.site", jsonAction=u"returnData", cmdType=u"post")
		self.unifsystemReport2(data,u"==  DAY WAN report ==")
		return


	####-----------------	 ---------
	def buttonConfirmPrintWlanConfInfoFromControllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		data = self.executeCMDOnController(dataSEND={}, pageString=u"list/wlanconf", jsonAction=u"returnData", cmdType=u"get")
		out = u"==WLan Report =="+u"\n"
		out+= u" ".ljust(4+20+6+20)+u"bc_filter...".ljust(6+15) +u"dtim .......".ljust(8+3+3)+u"MAC_filter ........".ljust(6+20+8)+u" ".ljust(15+8)+u"wpa......".ljust(6+6)+u"\n"
		out+= u"##".ljust(4)
		out+= u"name".ljust(20)
		out+= u"passphrase".ljust(20)
		out+= u"enble".ljust(6)
		out+= u"enble".ljust(6)
		out+= u"list".ljust(15)
		out+= u"mode".ljust(8)
		out+= u"na".ljust(3)
		out+= u"ng".ljust(3)
		out+= u"enble".ljust(6)
		out+= u"list".ljust(20)
		out+= u"policy".ljust(8)
		out+= u"schedule".ljust(15)
		out+= u"secrty".ljust(8)
		out+= u"enc".ljust(6)
		out+= u"mode".ljust(6)
		out+= u"\n"
		ii=0
		for item in data:
			ii+=1
			ll =unicode(ii).ljust(4)
			if u"name" in item:
				ll+= unicode(item[u"name"]).ljust(20)
			else:
				ll+= (u" ").ljust(20)

			if u"x_passphrase" in item:
				ll+= unicode(item[u"x_passphrase"]).ljust(20)
			else:
				ll+= (u" ").ljust(16)

			if u"enabled" in item:
				ll+= unicode(item[u"enabled"]).ljust(6)
			else:				  ll+= (u" ").ljust(6)

			if u"bc_filter_enabled" in item:
				ll+= unicode(item[u"bc_filter_enabled"]).ljust(6)
			else:				 ll+= (u" ").ljust(6)

			if u"bc_filter_list" in item:
				ll+= unicode(item[u"bc_filter_list"]).ljust(15)
			else:				 ll+= (u" ").ljust(15)

			if u"dtim_mode" in item:
				ll+= unicode(item[u"dtim_mode"]).ljust(8)
			else:				 ll+= (u" ").ljust(8)

			if u"dtim_na" in item:
				ll+= unicode(item[u"dtim_na"]).ljust(3)
			else:				 ll+= (u" ").ljust(3)

			if u"dtim_ng" in item:
				ll+= unicode(item[u"dtim_ng"]).ljust(3)
			else:				 ll+= (u" ").ljust(3)

			if u"mac_filter_enabled" in item:
				ll+= unicode(item[u"mac_filter_enabled"]).ljust(6)
			else:				 ll+= (u" ").ljust(6)

			if u"mac_filter_list" in item:
				ll+= unicode(item[u"mac_filter_list"]).ljust(20)
			else:				 ll+= (u" ").ljust(20)

			if u"mac_filter_policy" in item:
				ll+= unicode(item[u"mac_filter_policy"]).ljust(8)
			else:				 ll+= (u" ").ljust(8)

			if u"schedule" in item:
				ll+= unicode(item[u"schedule"]).ljust(15)
			else:				 ll+= (u" ").ljust(15)

			if u"security" in item:
				ll+= unicode(item[u"security"]).ljust(8)
			else:				 ll+= (u" ").ljust(8)

			if u"wpa_enc" in item:
				ll+= unicode(item[u"wpa_enc"]).ljust(6)
			else:				 ll+= (u" ").ljust(6)

			if u"wpa_mode" in item:
				ll+= unicode(item[u"wpa_mode"]).ljust(6)
			else:				 ll+= (u" ").ljust(6)


			out+=ll+("\n")
		self.indiLOG.log(10,u"unifi-Report ")
		self.indiLOG.log(10,u"unifi-Report  "+out)
		return


	####-----------------	 ---------
	def unifsystemReport1(self, data, useName, start, limit, PrintEventInfoLoginEvents=False):
		out =start+"\n"
		if useName:
			out+= u"##### datetime------".ljust(21+6) + u"name---".ljust(30) + u"subsystem--".ljust(12) + u"key--------".ljust(30)    + u"msg-----".ljust(50)+u"\n"
		else:
			out+= u"##### datetime------".ljust(21+6)                        + u"subsystem--".ljust(12) + u"key--------".ljust(30)    + u"msg-----".ljust(50)+u"\n"
		nn = 0
		for item in data:
			if not PrintEventInfoLoginEvents and item[u"msg"].find(u"log in from ")> -1: continue
			nn+=1
			if nn > limit: break
			## convert from UTC to local datetime string
			dd = datetime.datetime.strptime(item[u"datetime"],u"%Y-%m-%dT%H:%M:%SZ")
			xx = (dd - datetime.datetime(1970,1,1)).total_seconds()
			ll = unicode(nn).ljust(6)
			ll += time.strftime(u"%Y-%m-%d %H:%M:%S",time.localtime(xx)).ljust(21)
			if useName:
				found = False
				for	 xx in [u"ap_name",u"gw_name",u"sw_name",u"ap_name"]:
					if xx in item:
						ll+= item[xx].ljust(30)
						found = True
						break
				if not found:
						ll+= " ".ljust(30)
			ll +=item[u"subsystem"].ljust(12) + item[u"key"].ljust(30) + item[u"msg"].ljust(50)
			out+= ll.replace(u"\n","")+u"\n"
		self.indiLOG.log(10,u"unifi-Report ")
		self.indiLOG.log(10,u"unifi-Report  "+out)
		return

	####-----------------	 ---------
	def unifsystemReport2(self,data, start):
		out = start+u"\n"
		out+= u"##".ljust(4)
		out+= u"timeStamp".ljust(21)
		out+= u"lanNumSta".ljust(11)
		out+= u"num_sta".ljust(11)
		out+= u"wlanNumSta".ljust(11)
		out+= u"rx-WanBytes".rjust(20)
		out+= u"tx-WanBytes".rjust(20)
		out+= u"\n"
		ii=0
		for item in data:
			ii+=1
			ll =unicode(ii).ljust(4)
			if u"time" in item:
				ll+= time.strftime(u"%Y-%m-%d %H:%M:%S",time.localtime(item[u"time"]/1000)).ljust(21)
			else:
				ll+= (" ").ljust(21)

			if u"lan-num_sta" in item:
				ll+= unicode(item[u"lan-num_sta"]).ljust(11)
			else:
				ll+= (" ").ljust(10)

			if u"num_sta" in item:
				ll+= unicode(item[u"num_sta"]).ljust(11)
			else:
				ll+= (" ").ljust(11)

			if u"wlan-num_sta" in item:
				ll+= unicode(item[u"wlan-num_sta"]).ljust(11)
			else:
				ll+= (" ").ljust(11)

			if u"wan-rx_bytes" in item:
				ll+= (u"{0:,d}".format(int(item[u"wan-rx_bytes"]))).rjust(20)
			else:
				ll+= (u" ").ljust(20)

			if u"wan-tx_bytes" in item:
				ll+= (u"{0:,d}".format(int(item[u"wan-tx_bytes"]))).rjust(20)
			else:
				ll+= (" ").ljust(20)

			for item2 in item:
				if item2 == u"lan-num_sta":		continue
				if item2 == u"wlan-num_sta":	continue
				if item2 == u"num_sta":			continue
				if item2 == u"wan-rx_bytes":	continue
				if item2 == u"wan-tx_bytes":	continue
				if item2 == u"time":			continue
				if item2 == u"oid":				continue
				if item2 == u"site":			continue
				if item2 == u"o":				continue
				ll+= "  "+ unicode(item2)+u":"+unicode(item[item2])+u";...."

			out+=ll+(u"\n")
		self.indiLOG.log(10,u"unifi-Report ")
		self.indiLOG.log(10,u"unifi-Report  "+out)
		return

	####-----------------	 ---------
	def unifsystemReport3(self,data, start):
		out =start+"\n"
		out+= u"##".ljust(4) + u"mac".ljust(18)
		out+= u"hostname".ljust(21) + u"name".ljust(21)
		out+= u"first_seen".ljust(21)+ "ulast_seen".ljust(21)
		out+= u"vendor".ljust(10)
		out+= u"fixedIP".ljust(16)
		out+= u"us_f-ip".ljust(8)
		out+= u"wired".ljust(6)
		out+= u"blckd".ljust(6)
		out+= u"guest".ljust(6)
		out+= u"durationMin".rjust(12)
		out+= u"rx_KBytes".rjust(16)
		out+= u"rx_Packets".rjust(15)
		out+= u"rx_KBytes".rjust(16)
		out+= u"tx_Packets".rjust(15)
		out+=u"\n"
		ii=0
		for item in data:
			ii+=1
			ll =unicode(ii).ljust(4)
			if u"mac" in item:
				ll+= item[u"mac"].ljust(18)
			else:
				ll+= (" ").ljust(18)

			if u"hostname" in item:
				ll+= (item[u"hostname"][0:20]).ljust(21)
			else:
				ll+= (" ").ljust(21)

			if u"name" in item:
				ll+= (item[u"name"][0:20]).ljust(21)
			else:
				ll+= (" ").ljust(21)

			if u"first_seen" in item:
				ll+= time.strftime(u"%Y-%m-%d %H:%M:%S",time.localtime(item[u"first_seen"])).ljust(21)
			else:
				ll+= (" ").ljust(21)

			if u"last_seen" in item:
				ll+= time.strftime(u"%Y-%m-%d %H:%M:%S",time.localtime(item[u"last_seen"])).ljust(21)
			else:
				ll+= (u" ").ljust(21)

			if u"oui" in item:
				ll+= (item[u"oui"][0:20]).ljust(10)
			else:
				ll+= (u" ").ljust(10)

			if u"fixed_ip" in item:
				ll+= (item[u"fixed_ip"]).ljust(16)
			else:
				ll+= (u" ").ljust(16)

			if u"use_fixedip" in item:
				ll+= unicode(item[u"use_fixedip"]).ljust(8)
			else:
				ll+= (" ").ljust(8)

			if u"is_wired" in item:
				ll+= unicode(item[u"is_wired"]).ljust(6)
			else:
				ll+= (" ").ljust(6)

			if u"blocked" in item:
				ll+= unicode(item[u"blocked"]).ljust(6)
			else:
				ll+= (" ").ljust(6)

			if u"is_guest" in item:
				ll+= unicode(item[u"is_guest"]).ljust(6)
			else:
				ll+= (u" ").ljust(6)

			if u"duration" in item:
				ll+= (u"{0:,d}".format(int(item[u"duration"])/60)).rjust(12)
			else:
				ll+= (u" ").rjust(12)

			if u"rx_bytes" in item:
				ll+= (u"{0:,d}".format(int(item[u"rx_bytes"]/1024.))).rjust(16)
			else:
				ll+= (u" ").rjust(16)

			if u"rx_packets" in item:
				ll+= (u"{0:,d}".format(int(item[u"rx_packets"]))).rjust(15)
			else:
				ll+= (u" ").rjust(15)

			if u"tx_bytes" in item:
				ll+= (u"{0:,d}".format(int(item[u"tx_bytes"]/1024.))).rjust(16)
			else:
				ll+= (u" ").rjust(16)

			if u"tx_packets" in item:
				ll+= (u"{0:,d}".format(int(item[u"tx_packets"]))).rjust(15)
			else:
				ll+= (u" ").ljust(15)

			for item2 in item:
				if item2 ==u"hostname":	   continue
				if item2 ==u"mac":			continue
				if item2 ==u"first_seen":	continue
				if item2 ==u"last_seen":	continue
				if item2 ==u"site_id":	   	continue
				if item2 ==u"_id":		   	continue
				if item2 ==u"network_id":   continue
				if item2 ==u"usergroup_id": continue
				if item2 ==u"noted":		continue
				if item2 ==u"name":			continue
				if item2 ==u"is_wired":		continue
				if item2 ==u"oui":			continue
				if item2 ==u"blocked":		continue
				if item2 ==u"fixed_ip":		continue
				if item2 ==u"use_fixedip":	continue
				if item2 ==u"is_guest":		continue
				if item2 ==u"duration":		continue
				if item2 ==u"rx_bytes":		continue
				if item2 ==u"tx_bytes":		continue
				if item2 =="tx_packets":	continue
				if item2 ==u"rx_packets":   continue
				ll+=unicode(item2)+u":"+unicode(item[item2])+u";...."
			out+=ll+(u"\n")


		self.indiLOG.log(10,u"unifi-Report ")
		self.indiLOG.log(10,u"unifi-Report  "+out)
		return


######## reports end



######## actions and menu set leds on /off
	####-----------------	 ---------
	def buttonConfirmAPledONControllerCALLBACKaction(self, action1=None, filter="", typeId="", devId=""):
		return self.buttonConfirmAPledONControllerCALLBACK(valuesDict=action1.props)
	####-----------------	 ---------
	def buttonConfirmAPledONControllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		self.executeCMDOnController(dataSEND={"led_enabled":True}, pageString=u"/set/setting/mgmt", cmdType=u"post")
		return

	####-----------------	 ---------
	def buttonConfirmAPledOFFControllerCALLBACKaction(self, action1=None, filter="", typeId="", devId=""):
		return self.buttonConfirmAPledOFFControllerCALLBACK(valuesDict=action1.props)
	####-----------------	 ---------
	def buttonConfirmAPledOFFControllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		self.executeCMDOnController(dataSEND={"led_enabled":False}, pageString=u"/set/setting/mgmt", cmdType=u"post")
		return

	####-----------------	 ---------
	def buttonConfirmAPxledONControllerCALLBACKaction(self, action1=None, filter="", typeId="", devId=""):
		return self.buttonConfirmAPxledONControllerCALLBACK(valuesDict=action1.props)
	####-----------------	 ---------
	def buttonConfirmAPxledONControllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		self.executeCMDOnController(dataSEND={"cmd":"set-locate","mac":valuesDict[u"selectedAPDevice"]}, pageString=u"/cmd/devmgr", cmdType=u"post")
		return valuesDict

	####-----------------	 ---------
	def buttonConfirmAPxledOFFControllerCALLBACKaction(self, action1=None, filter="", typeId="", devId=""):
		return self.buttonConfirmAPxledOFFControllerCALLBACK(valuesDict=action1.props)
	####-----------------	 ---------
	def buttonConfirmAPxledOFFControllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		self.executeCMDOnController(dataSEND={"cmd":"unset-locate","mac":valuesDict[u"selectedAPDevice"]}, pageString=u"/cmd/devmgr", cmdType=u"post")
		return valuesDict

######## actions and menu set dev on /off
	####-----------------	 ---------
	def buttonConfirmEnableAPConllerCALLBACKaction(self, action1=None, filter="", typeId="", devId=""):
		self.execDisableAP(action1.props,False)
	def buttonConfirmEnableAPConllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		self.execDisableAP(valuesDict, False)
		return valuesDict

	####-----------------	 ---------
	def buttonConfirmDisableAPConllerCALLBACKaction(self, action1=None, filter="", typeId="", devId=""):
		self.execDisableAP(action1.props, True)
	def buttonConfirmDisableAPConllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		self.execDisableAP(valuesDict, True)
		return valuesDict

	def execDisableAP(self, valuesDict, disable): #( true if disable )
		dev = indigo.devices[int(valuesDict[u"apDeviceSelected"])]
		ID = dev.states[u"ap_id"]
		ip = dev.states[u"ipNumber"]
		if disable: self.setSuspend(ip, time.time() + 99999999)
		else	  : self.delSuspend(ip)
		valuesDict[u"MSG"] = u"command send"
		self.executeCMDOnController(dataSEND={u"disabled":disable}, pageString=u"/rest/device/"+ID, cmdType=u"put", cmdTypeForce=True)
		return valuesDict

######## actions and menu restart unifi devices
	####-----------------	 ---------
	def buttonConfirmRestartUnifiDeviceConllerCALLBACKaction(self, action1=None, filter="", typeId="", devId=""):
		self.buttonConfirmRestartUnifiDeviceConllerCALLBACK(action1.props,False)

	def buttonConfirmRestartUnifiDeviceConllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		mac = valuesDict[u"selectedUnifiDevice"]
		if not self.isValidMAC(mac): 
			valuesDict[u"MSG"] = u"no valid mac given:{}".format(mac)
			return valuesDict
		valuesDict["MSG"] = u"restart command send to:{}".format(mac)
		self.executeCMDOnController(dataSEND={'cmd':'restart','mac':mac}, pageString=u"/cmd/devmgr", cmdType=u"post", cmdTypeForce=True)
		return valuesDict


######## actions and menu provision unifi devices
	####-----------------	 ---------
	def buttonConfirmProvisionUnifiDeviceConllerCALLBACKaction(self, action1=None, filter="", typeId="", devId=""):
		self.buttonConfirmProvisionUnifiDeviceConllerCALLBACK(action1.props,False)

	def buttonConfirmProvisionUnifiDeviceConllerCALLBACK(self, valuesDict=None, filter="", typeId="", devId=""):
		mac = valuesDict[u"selectedUnifiDeviceProvision"]
		if not self.isValidMAC(mac): 
			valuesDict[u"MSG"] = u"no valid mac given:{}".format(mac)
			return valuesDict
		valuesDict["MSG"] = u"Provision command send to:{}".format(mac)
		dataDict = {'cmd':'force-provision','mac':mac}
		page = "/cmd/devmgr"
		indigo.server.log(" page:{}; dict:{}".format(page, dataDict))
		self.executeCMDOnController(dataSEND=dataDict, pageString=page, cmdType=u"post", cmdTypeForce=True, repeatIfFailed=False)
		return valuesDict






######## set defaults for action and menu screens
	#/////////////////////////////////////////////////////////////////////////////////////
	# Actions Configuration
	#/////////////////////////////////////////////////////////////////////////////////////
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine returns the actions for the plugin; you normally don't need to
	# override this as the base class returns the actions from the Actions.xml file
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	def getActionsDict(self):
		return super(Plugin, self).getActionsDict()

	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine obtains the callback method to execute when the action executes; it
	# normally just returns the action callback specified in the Actions.xml file
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	def getActionCallbackMethod(self, typeId):
		return super(Plugin, self).getActionCallbackMethod(typeId)

	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine returns the configuration XML for the given action; normally this is
	# pulled from the Actions.xml file definition and you need not override it
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	def getActionConfigUiXml(self, typeId, devId):
		return super(Plugin, self).getActionConfigUiXml(typeId, devId)

	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine returns the UI values for the action configuration screen prior to it
	# being shown to the user
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	####-----------------	 ---------
	def getActionConfigUiValues(self, pluginProps, typeId, devId):
		#self.myLog( text=unicode(pluginProps)+"  typeId;"+unicode(typeId)+"  devId:"+unicode(devId))
		if u"fileNameOfImage" in pluginProps:
			if len(self.changedImagePath) > 5:
				pluginProps[u"fileNameOfImage"] = self.changedImagePath+u"nameofCamera.jpeg"
			else:
				pluginProps[u"fileNameOfImage"] = self.indigoPreferencesPluginDir+u"nameofCamera.jpeg"
		return super(Plugin, self).getActionConfigUiValues(pluginProps, typeId, devId)


	#/////////////////////////////////////////////////////////////////////////////////////
	# Menu Item Configuration
	#/////////////////////////////////////////////////////////////////////////////////////
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine returns the menu items for the plugin; you normally don't need to
	# override this as the base class returns the menu items from the MenuItems.xml file
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	def getMenuItemsList(self):
		return super(Plugin, self).getMenuItemsList()

	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine returns the configuration XML for the given menu item; normally this is
	# pulled from the MenuItems.xml file definition and you need not override it
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	def getMenuActionConfigUiXml(self, menuId):
		return super(Plugin, self).getMenuActionConfigUiXml(menuId)

	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine returns the initial values for the menu action config dialog, if you
	# need to set them prior to the GUI showing
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	####-----------------	 ---------
	def getMenuActionConfigUiValues(self, menuId):
		valuesDict = indigo.Dict()
		if menuId == u"CameraActions" and (u"fileNameOfImage" not in self.menuXML or len(self.menuXML[u"fileNameOfImage"]) <10 ):
			if len(self.changedImagePath) > 5:
				self.menuXML[u"fileNameOfImage"] = self.changedImagePath+u"nameofCamera.jpeg"
			else:
				self.menuXML[u"fileNameOfImage"] = u"/tmp/nameofCamera.jpeg"
		self.menuXML[u"snapShotTextMethod"] = self.imageSourceForSnapShot

		for item in self.menuXML:
			valuesDict[item] = self.menuXML[item]
		errorsDict = indigo.Dict()
		return (valuesDict, errorsDict)



########  check if we have new unifi system devces, if yes: litt basic variables and request a reboot
	####-----------------	 ---------
	def checkForNewUnifiSystemDevices(self):
		try:
			if not self.enablecheckforUnifiSystemDevicesState : return
			if self.checkforUnifiSystemDevicesState == "": return
			self.checkforUnifiSystemDevicesState  = ""
			if self.unifiCloudKeyMode != "ON"			: return
			newDeviceFound =[]

			deviceDict =		self.executeCMDOnController( pageString=u"/stat/device/", jsonAction=u"returnData", cmdType=u"get")
			if deviceDict =={}: return
			devType =""
			for item in deviceDict:
				ipNumber = ""
				MAC		 = ""
				if u"type"   not in item: continue
				uType	 = item[u"type"]

				if uType == "ugw":
					if u"network_table" in item:
						#self.myLog( text=u"network_table:"+json.dumps(item["network_table"], sort_keys=True, indent=2)	,mType=u"test" )
						for nwt in item[u"network_table"]:
							if u"mac" in nwt and u"ip"  in nwt and u"name" in nwt and nwt[u"name"].lower() == u"lan":
								ipNumber = nwt[u"ip"]
								MAC		 = nwt[u"mac"]
								break

				#### do nto handle UDM type devices (yet)
				elif uType.find(u"udm"):
					continue

				else:
					if u"mac" in item and u"ip" in item:
						ipNumber = item[u"ip"]
						MAC		 = item[u"mac"]

				if MAC == "" or ipNumber == "":
					#self.myLog( text=unicode(item),mType=u"test" )
					continue

				found = False
				name = "--"

				for dev in indigo.devices.iter(u"props.isAP,props.isSwitch,props.isGateway"):
					#self.myLog( text= dev.name ,mType=u"test" )
					if u"MAClan" in dev.states and dev.states[u"MAClan"] == MAC:
						found = True
						name = dev.name
						break
					if u"MAC" in dev.states and dev.states[u"MAC"] == MAC:
						found = True
						name = dev.name
						break
						## found devce no action

				if not found:

					if uType.find(u"uap") >-1:
						for i in range(len(self.ipNumbersOf[u"AP"])):
							if	not self.isValidIP(self.ipNumbersOf[u"AP"][i]):
								newDeviceFound.append(u"uap:	 , new {}     existing: {}".format(ipNumber, self.ipNumbersOf[u"AP"][i]) )
								self.ipNumbersOf[u"AP"][i]						= ipNumber
								self.pluginPrefs[u"ip"+unicode(i)]			= ipNumber
								self.pluginPrefs[u"ipON"+unicode(i)]		= True
								self.checkforUnifiSystemDevicesState		= u"reboot"
								newDeviceFound.append(u"uap: "+unicode(i)+", "+ipNumber)
								break
							else:
								if self.ipNumbersOf[u"AP"][i]	 == ipNumber:
									if not self.devsEnabled[u"AP"][i]: break # we know this one but it is disabled on purpose
									newDeviceFound.append(u"uap:	 , new {}     existing: {}".format(ipNumber, self.ipNumbersOf[u"AP"][i] ) )
									self.ipNumbersOf[u"AP"][i]					= ipNumber
									#self.devsEnabled[u"AP"][i]						= True # will be enabled after restart
									self.pluginPrefs[u"ipON"+unicode(i)]	= True
									self.checkforUnifiSystemDevicesState	= u"reboot"
									newDeviceFound.append(u"uap: "+unicode(i)+u", "+ipNumber)
									break

					elif uType.find(u"usw") >-1:
						for i in range(len(self.ipNumbersOf[u"SW"])):
							if	not self.isValidIP(self.ipNumbersOf[u"SW"][i] ):
								newDeviceFound.append("usw:	 , new {}     existing: {}".format(ipNumber, self.ipNumbersOf[u"SW"][i]) )
								self.ipNumbersOf[u"SW"][i]						= ipNumber
								self.pluginPrefs[u"ipSW"+unicode(i)]		= ipNumber
								self.pluginPrefs[u"ipSWON"+unicode(i)]		= True
								self.checkforUnifiSystemDevicesState		= u"reboot"
								break
							else:
								if self.ipNumbersOf[u"SW"][i] == ipNumber:
									if not self.devsEnabled[u"SW"][i]: break # we know this one but it is disabled on purpose
									newDeviceFound.append(u"usw:	 , new {}     existing: {}".format(ipNumber, self.ipNumbersOf[u"SW"][i]) )
									self.ipNumbersOf[u"SW"][i]					= ipNumber
									#self.devsEnabled[u"SW"][i]						= True # will be enabled after restart
									self.pluginPrefs[u"ipSWON"+unicode(i)]	= True
									self.checkforUnifiSystemDevicesState	= u"reboot"
									break

					elif uType.find(u"ugw") >-1:
							#### "ip" in the dict is the ip number of the wan connection NOT the inernal IP for the gateway !!
							#### using 2 other places instead to get the LAN IP
							if	not self.isValidIP(self.ipNumbersOf[u"GW"]):
								newDeviceFound.append(u"ugw:	 , new {}     existing: {}".format(ipNumber, self.ipNumbersOf[u"GW"]) )
								self.ipNumbersOf[u"GW"]							= ipNumber
								self.pluginPrefs[u"ipUGA"]					= ipNumber
								self.pluginPrefs[u"ipUGAON"]				= True
								self.checkforUnifiSystemDevicesState		= u"reboot"
							else:
								if not self.devsEnabled[u"GW"]: break # we know this one but it is disabled on purpose
								if self.ipNumbersOf[u"GW"] != ipNumber:
									newDeviceFound.append(u"ugw:	 , new {}     existing: {}".format(ipNumber, self.ipNumbersOf[u"GW"]) )
									self.ipNumbersOf[u"GW"]						= ipNumber
									self.pluginPrefs[u"ipUGA"]				= ipNumber
									self.pluginPrefs[u"ipUGAON"]			= True
									self.checkforUnifiSystemDevicesState	= u"reboot"
								else:
									newDeviceFound.append(u"ugw:	 , new {}     existing: {}".format(ipNumber, self.devsEnabled[u"GW"]) )
									self.pluginPrefs[u"ipUGAON"]			= True
									self.checkforUnifiSystemDevicesState	= "reboot"

			if self.checkforUnifiSystemDevicesState =="reboot":
				try:
					self.pluginPrefs[u"createUnifiDevicesCounter"] = int(self.pluginPrefs[u"createUnifiDevicesCounter"] ) +1
					if int(self.pluginPrefs[u"createUnifiDevicesCounter"] ) > 1: # allow only 1 unsucessful try, then wait 10 minutes
						self.checkforUnifiSystemDevicesState		   = ""
					else:
						self.indiLOG.log(10,u"Connection   reboot required due to new UNIFI system device found:{}".format(newDeviceFound))
				except:
						self.checkforUnifiSystemDevicesState		   = ""
			try:	indigo.server.savePluginPrefs()
			except: pass

			if self.checkforUnifiSystemDevicesState =="":
				self.pluginPrefs[u"createUnifiDevicesCounter"] = 0

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}   Connection".format(sys.exc_traceback.tb_lineno, e))

		return




	####-----------------	 --------- This one is not working .. disabled in menu
	def executeMCAconfigDumpOnGW(self, valuesDict={},typeId="" ):
		keepList=[u"vpn",u"port-forward",u"service:radius-server",u"service:dhcp-server"]
		jsonAction=u"print"
		ret =[]
		if self.connectParams[u"commandOnServer"][u"GWctrl"].find(u"off") == 0: return valuesDict
		try:
			cmd = self.expectPath +" "
			cmd += "'"+self.pathToPlugin + self.connectParams[u"expectCmdFile"][u"GWctrl"] + "' " 
			cmd += "'"+self.connectParams[u"UserID"][u"unixDevs"]+ "' '"+self.connectParams[u"PassWd"][u"unixDevs"]+ "' " 
			cmd += self.ipNumbersOf[u"GW"] + " " 
			cmd += "'"+self.connectParams[u"promptOnServer"][self.ipNumbersOf[u"GW"]] + "' " 
			cmd += " XXXXsepXXXXX " + " " 
			cmd += "\""+self.escapeExpect(self.connectParams[u"promptOnServer"][self.ipNumbersOf[u"GW"]])+"\""

			if self.decideMyLog(u"Expect"): self.indiLOG.log(10,u" UGA EXPECT CMD: "+ unicode(cmd))
			ret = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
			if self.decideMyLog(u"ExpectRET"): self.indiLOG.log(10,"returned from expect-command: {}".format(ret[0]))
			dbJson, error= self.makeJson2(ret[0], u"XXXXsepXXXXX")
			if jsonAction == u"print":
				for xx in keepList:
					if xx.find(u":") >-1:
						yy = xx.split(":")
						if yy[0] in dbJson and yy[1] in dbJson[yy[0]]:
							short = dbJson[yy[0]][yy[1]]
							if yy[1] ==u"dhcp-server":
								for z in short:
									if z ==u"shared-network-name":
										for zz in short[z]:
											#self.myLog( text=" in "+zz)
											for zzz in short[z][zz]: # net_LAN_192.168.1.0-24"
												if zzz ==u"subnet":
													for zzzz in short[z][zz][zzz]:	# "192.168.1.0/24"
														for zzzzz in short[z][zz][zzz][zzzz]:
															if zzzzz ==u"static-mapping":
																s0 = short[z][zz][zzz][zzzz][zzzzz]
																## need to sort
																u =[]
																v =[]
																for t in s0:
																	u.append((s0[t][u"mac-address"],s0[t][u"ip-address"]))
																	v.append((self.fixIP(s0[t][u"ip-address"]),s0[t][u"ip-address"],s0[t][u"mac-address"]))

																sortMacKey = sorted(u)
																sortIPKey  = sorted(v)
																out = u"     static DHCP mappings:\n"
																for m in range(len(sortMacKey)):
																	out += sortMacKey[m][0]+" --> "+ sortMacKey[m][1].ljust(20)+u"        " +sortIPKey[m][1].ljust(18)+u"--> "+ sortIPKey[m][2]+u"\n"
																self.myLog( text= out, mType=u"==== UGA-setup ====")
							else:
								self.myLog( text=u"    " +xx+u":\n"+json.dumps(short,sort_keys=True,indent=2), mType=u"==== UGA-setup ====")
						else:
							self.myLog( text=xx+u" not in json returned from UGA ", mType=u"UGA-setup")
					else:
						if xx in dbJson:
							self.myLog( text=u"    " +xx+":\n"+json.dumps(dbJson[xx],sort_keys=True,indent=2), mType=u"==== UGA-setup ====")
						else:
							self.myLog( text=xx+u" not in json returned from UGA ", mType=u"==== UGA-setup ====")
			else:
				return valuesDict


		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}\n system info:\n>>{}<<".format(sys.exc_traceback.tb_lineno, e, unicode(ret)[0:100]) )
		return valuesDict



	####-----------------	 ---------
	def getunifiOSAndPort(self):
		try:
			ret 			= ""
			for ii in range(3):
				# get port and which unifi os:
				if self.unifiControllerOS != "" and (
					self.unifiCloudKeyPort in self.tryHTTPPorts or (
						self.unifiCloudKeyPort == self.overWriteControllerPort and self.overWriteControllerPort !=""
					) 
				) : return True
				if self.overWriteControllerPort != "":
					tryport = [self.overWriteControllerPort]
				else:
					if self.lastPortNumber != "":
						tryport = [self.lastPortNumber] + self.tryHTTPPorts
					else:
						tryport = self.tryHTTPPorts
				self.indiLOG.log(10,u"getunifiOSAndPort existing  os>{}< .. ip#>{}< .. trying ports>{}<".format( self.unifiControllerOS, self.unifiCloudKeyIP, tryport ) )
				self.executeCMDOnControllerReset(calledFrom="getunifiOSAndPort")

				for port in tryport:
					# this cmd will return http code only (I= header only, -s = silent -o send std to null, -w print http reply code)
					# curl --insecure  -I -s -o /dev/null -w "%{http_code}" 'https://192.168.1.2:8443'
					cmdOS = self.curlPath+u" --insecure  -I -s -o /dev/null -w \"%{http_code}\" 'https://"+self.unifiCloudKeyIP+u":"+port+u"'"
					ret = subprocess.Popen(cmdOS, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0]
					if self.decideMyLog(u"ConnectionCMD"): self.indiLOG.log(10,u"getunifiOSAndPort trying port#:>{}< gives ret code:{}".format(cmdOS, ret) )
					if ret in self.HTTPretCodes: 
						self.unifiCloudKeyPort = port
						self.lastPortNumber	   = port
						self.unifiControllerOS = self.HTTPretCodes[ret][u"os"]
						self.unifiApiLoginPath = self.HTTPretCodes[ret][u"unifiApiLoginPath"]
						self.unifiApiWebPage   = self.HTTPretCodes[ret][u"unifiApiWebPage"]
						self.indiLOG.log(10,u"getunifiOSAndPort found  OS:{}, port#:{} using ip#:{}".format(self.unifiControllerOS, port, self.unifiCloudKeyIP) )
						return True
					else:
						self.indiLOG.log(10,u"getunifiOSAndPort trying port:{}, wrong ret code from curl test>{}< expecting {} ".format(port, ret, self.HTTPretCodes) )

				self.sleep(1)
				
			if self.unifiControllerOS == "": 
				self.indiLOG.log(30,u"getunifiOSAndPort bad return from unifi controller {}, no os and / port found, tried ports:{}".format(self.unifiCloudKeyIP, tryport) )

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e) )
				self.indiLOG.log(40,u"getunifiOSAndPort ret:\n>>{}<<".format(unicode(ret)[0:100]) )
		return False


	####-----------------	 ---------
	def executeCMDOnControllerReset(self, wait=False, calledFrom=""):
		try:
			if calledFrom != "":
				if self.decideMyLog(u"Protect"): self.indiLOG.log(10,u"executeCMDOnControllerReset called from:{}".format(calledFrom) )
			if self.unifiControllerSession != "":
				try: self.unifiControllerSession.close()
				except: pass
			self.unifiControllerSession = ""
			self.unifiControllerOS = ""
			self.lastUnifiCookieRequests = 0.
			self.lastUnifiCookieCurl = 0	
			if wait: self.sleep(0.5)	
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e) )


	####-----------------	 ---------
	def setunifiCloudKeySiteName(self, method="response", cookies="", headers="" ):
		try:
			if method == "response":
				# curl --insecure -b /tmp/unifiCookie 'https://192.168.1.2:443/proxy/network/api/self/sites'
				urlSite	= "https://"+self.unifiCloudKeyIP+":"+self.unifiCloudKeyPort+"/proxy/network/api/self/sites"
				textRET	= self.unifiControllerSession.get(urlSite,   cookies=cookies, headers=headers, verify=False).text
				 # should get: {"meta":{"rc":"ok"},"data":[{"_id":"5750f2ade4b04dab3d3d0d4f","name":"default","desc":"stanford","attr_hidden_id":"default","attr_no_delete":true,"role":"admin","role_hotspot":false}]}
			elif method == "curlPath":
				# curl --insecure -b /tmp/unifiCookie 'https://192.168.1.2:443/api/self/sites'
				cmdSite  = self.curlPath+u" --insecure -b /tmp/unifiCookie 'https://"+self.unifiCloudKeyIP+":"+self.unifiCloudKeyPort+"/api/self/sites'"
				ret = subprocess.Popen(cmdSite, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
				textRET	= ret[0].decode(u"utf8")
				ret1 	= ret[1].decode(u"utf8")
				 # should get: {"meta":{"rc":"ok"},"data":[{"_id":"5750f2ade4b04dab3d3d0d4f","name":"default","desc":"stanford","attr_hidden_id":"default","attr_no_delete":true,"role":"admin","role_hotspot":false}]}
			else:
				return False

			try:
				dictRET = json.loads(textRET)
			except :
				self.indiLOG.log(40,u"setunifiCloudKeySiteName for {} has error, getting site ID, no json object returned: >>{}<<".format(self.unifiCloudKeyIP, textRET))
				self.executeCMDOnControllerReset(wait=True, calledFrom="setunifiCloudKeySiteName1")
				return False
		
			oneFound = False
			if u"meta" in dictRET and u"rc" in dictRET[u"meta"] and dictRET[u"meta"][u"rc"] == u"ok" and u"data" in dictRET:
				if len(dictRET[u"data"]) >0:
					for site in dictRET[u"data"]:
						if u"name" in site:
							if not oneFound: 
								self.unifiCloudKeyListOfSiteNames = []
								oneFound = True
							if site[u"name"] not in self.unifiCloudKeyListOfSiteNames:
								self.unifiCloudKeyListOfSiteNames.append(site[u"name"])

					if self.unifiCloudKeyListOfSiteNames != []:
						self.unifiCloudKeySiteName = self.unifiCloudKeyListOfSiteNames[0]
						self.pluginPrefs[u"unifiCloudKeySiteName"] = self.unifiCloudKeySiteName 

				self.indiLOG.log(20,u"setunifiCloudKeySiteNamer setting site id name to >>{}<<, list of Names found:{}<".format(self.unifiCloudKeySiteName , self.unifiCloudKeyListOfSiteNames))
				self.pluginPrefs[u"unifiCloudKeyListOfSiteNames"] = json.dumps(self.unifiCloudKeyListOfSiteNames)
				return True

			self.indiLOG.log(20,u"setunifiCloudKeySiteName  id  not found ret:>>{}<<".format(textRET))
			self.executeCMDOnControllerReset(wait=True,  calledFrom="setunifiCloudKeySiteName2")
			return False

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"setunifiCloudKeySiteName: " )
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e) )
		self.executeCMDOnControllerReset(wait=True,  calledFrom="setunifiCloudKeySiteName3")
		return False



	####-----------------	 ---------
	def executeCMDOnController(self, dataSEND={}, pageString=u"",jsonAction=u"returnData", startText="", cmdType=u"put", cmdTypeForce = False, repeatIfFailed=True, raw=False, protect=False, ignore40x=False):

		try:
			if self.unifiControllerType == u"off": 					return []
			if self.unifiCloudKeyMode   == u"off":					return []
			if not self.isValidIP(self.unifiCloudKeyIP): 			return []
			if len(self.connectParams[u"UserID"][u"webCTRL"]) < 2: 	return []
			if self.unifiCloudKeyMode.find(u"ON") == -1 and self.unifiCloudKeyMode != u"UDM": return []

			for iii in range(2):
				if not repeatIfFailed and iii > 0: return []
				if iii == 1: self.sleep(0.2)

				# get port and which unifi os:
				if not self.getunifiOSAndPort(): 
					self.executeCMDOnControllerReset(wait=False)
					return []
				if self.unifiControllerOS not in self.OKControllerOS:
					if self.decideMyLog(u"ConnectionCMD"): self.indiLOG.log(10,u"unifiControllerOS not set : {}".format(self.unifiControllerOS) )
					return []

				# now execute commands
				#### use curl 
				useCurl = self.requestOrcurl.find(u"curl") > -1 and self.unifiControllerOS == u"std"

				if useCurl:
					#cmdL  = curl  --insecure -c /tmp/unifiCookie -H "Content-Type: application/json"  --data '{"username":"karlwachs","password":"457654aA.unifi"}' https://192.168.1.2:8443/api/login
					#cmdL  = self.curlPath+" --insecure -c /tmp/unifiCookie --data '"                                      +json.dumps({"username":self.connectParams[u"UserID"]["webCTRL"],"password":self.connectParams[u"PassWd"]["webCTRL"]})+"' 'https://"+self.unifiCloudKeyIP+":"+self.unifiCloudKeyPort+"/api/login'"
					cmdLogin  = self.curlPath+u" --max-time 10 --insecure -c /tmp/unifiCookie -H \"Content-Type: application/json\" --data '"+json.dumps({u"username":self.connectParams[u"UserID"][u"webCTRL"],u"password":self.connectParams[u"PassWd"][u"webCTRL"],u"strict":self.useStrictToLogin})+u"' 'https://"+self.unifiCloudKeyIP+u":"+self.unifiCloudKeyPort+self.unifiApiLoginPath+u"'"
					if dataSEND =={}: 	dataSendSTR = ""
					else:		 		dataSendSTR = u" --data '"+json.dumps(dataSEND)+"' "
					if	 cmdType == u"put":	 						cmdTypeUse= u" -X PUT "
					elif cmdType == u"post":	  					cmdTypeUse= u" -X POST "
					elif cmdType == u"get":	  						cmdTypeUse= u" " # 
					else:					 						cmdTypeUse= u" ";	cmdType = u"get"
					if not cmdTypeForce: cmdTypeUse = u" "
					if self.unifiControllerType.find(u"UDM") >-1 and cmdType == u"get":	cmdTypeUse = u" " 



					if self.decideMyLog(u"ConnectionCMD"): self.indiLOG.log(10,u"executeCMDOnController: {}".format(cmdLogin) )
					try:
						if time.time() - self.lastUnifiCookieCurl > 100: # re-login every 90 secs
							ret = subprocess.Popen(cmdLogin, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
							respText = ret[0]
							errText  = ret[1]
							try: loginDict = json.loads(respText)
							except:
								if iii == 0:
									self.indiLOG.log(40,u"UNIFI executeCMDOnController error no json object: (wrong UID/passwd, ip number?{}) ...>>{}<<\n{}".format(self.unifiCloudKeyIP,respText,errText))
									self.executeCMDOnControllerReset(wait=True)
								continue
							if   ( u"meta" not in loginDict or  loginDict[u"meta"][u"rc"] != u"ok"):
								if iii == 0:
									self.indiLOG.log(40,u"UNIFI executeCMDOnController  login cmd:{}\ngives  error: {}\n {}".format(cmdLogin, respText,errText) )
								self.executeCMDOnControllerReset(wait=True)
								continue
							if self.decideMyLog(u"ConnectionRET"):	 self.indiLOG.log(10,u"Connection-{}: {}".format(self.unifiCloudKeyIP,respText) )
							self.lastUnifiCookieCurl = time.time()


						if self.unifiCloudKeySiteName == "":
							if not self.setunifiCloudKeySiteName(method = "curlPath"): continue

						#cmdDATA  = curl  --insecure -b /tmp/unifiCookie' --data '{"within":999,"_limit":1000}' https://192.168.1.2:8443/api/s/default/stat/event
						cmdDATA  = self.curlPath+u" --max-time 10 --insecure -b /tmp/unifiCookie " +dataSendSTR+cmdTypeUse+ u" 'https://"+self.unifiCloudKeyIP+":"+self.unifiCloudKeyPort+self.unifiApiWebPage+"/"+self.unifiCloudKeySiteName+u"/"+pageString.strip("/")+u"'"

						if self.decideMyLog(u"ConnectionCMD"):	self.indiLOG.log(10,u"Connection: {}".format(cmdDATA) )
						if startText != "":					 	self.indiLOG.log(10,u"Connection: {}".format(startText) )
						try:
							ret = subprocess.Popen(cmdDATA, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
							respText = ret[0]#.decode(u"utf8")
							errText  = ret[1]#.decode(u"utf8")
							try:
								dictRET = json.loads(respText)
							except:
								if iii > 0:
									self.indiLOG.log(30,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
									self.indiLOG.log(40,u"UNIFI executeCMDOnController to {} curl errortext:{}".format(self.unifiCloudKeyIP, errText))
									self.printHttpError(unicode(e), respText, iii)
								self.executeCMDOnControllerReset(wait=True, calledFrom="executeCMDOnController-curl json")
								continue

							if dictRET[u"meta"][u"rc"] != u"ok":
								if iii == 0:
									self.indiLOG.log(40,u" Connection error: >>{}<<\n{}".format(self.unifiCloudKeyIP, respText, errText))
								self.executeCMDOnControllerReset(wait=True, calledFrom="executeCMDOnController-curl dict not ok")
								continue

							if self.decideMyLog(u"ConnectionRET"):
									self.indiLOG.log(10,u"Connection to {}: returns >>{}<<".format(self.unifiCloudKeyIP, respText) )

							if  jsonAction == u"print":
								self.indiLOG.log(10,u" Connection to:{} info\n{}".format(self.unifiCloudKeyIP, json.dumps(dictRET["data"],sort_keys=True, indent=2)))
								return []

							if  jsonAction == u"returnData":
								#self.writeJson(dictRET["data"], fName=self.indigoPreferencesPluginDir+"dict-Controller-"+pageString.replace("/","_").replace(" ","-").replace(":","=").strip("_")+".txt", sort=True, doFormat=True )
								return dictRET[u"data"]
							if  jsonAction == u"protect":
								#self.writeJson(dictRET["data"], fName=self.indigoPreferencesPluginDir+"dict-Controller-"+pageString.replace("/","_").replace(" ","-").replace(":","=").strip("_")+".txt", sort=True, doFormat=True )
								return dictRET

							return []

						except	Exception, e:
							self.indiLOG.log(40,u"Connection: in Line {} has error={}   Connection".format(sys.exc_traceback.tb_lineno, e) )
					except	Exception, e:
						self.indiLOG.log(40,u"Connection: in Line {} has error={}   Connection".format(sys.exc_traceback.tb_lineno, e) )


				############# does not work on OSX	el capitan ssl lib too old	##########
				if not useCurl:

					if self.unifiControllerSession == "" or (time.time() - self.lastUnifiCookieRequests) > 80: # every 80 secs token cert
						if self.unifiControllerSession != "":
							try: 	self.unifiControllerSession.close()
							except: pass
							self.unifiControllerSession = ""

						if self.unifiControllerSession == "":
							self.unifiControllerSession	 = requests.Session()

						url = "https://"+self.unifiCloudKeyIP+":"+self.unifiCloudKeyPort+self.unifiApiLoginPath
						loginHeaders = {"Accept": "application/json", "Content-Type": "application/json", "referer": "/login"}
						dataLogin = json.dumps({"username":self.connectParams[u"UserID"][u"webCTRL"],"password":self.connectParams[u"PassWd"][u"webCTRL"]}) #  , "strict":self.useStrictToLogin})
						if self.decideMyLog(u"ConnectionCMD"): self.indiLOG.log(10,u"Connection: requests login url:{};\ndataLogin:{};\nloginHeaders:{};".format(url, dataLogin, loginHeaders) )

						resp  = self.unifiControllerSession.post(url,  headers=loginHeaders, data = dataLogin, timeout=(2.,4.), verify=False)
						if self.decideMyLog(u"ConnectionRET"): self.indiLOG.log(10,u"Connection: requests login code:{}; ret-Text:\n {} ...".format(resp.status_code, resp.text) )

						try: loginDict = json.loads(resp.text)
						except	Exception, e:
							self.indiLOG.log(40,u"Connection: in Line {} has error={}   ".format(sys.exc_traceback.tb_lineno, e) )
							self.indiLOG.log(40,u"UNIFI executeCMDOnController error no json object: (wrong UID/passwd, ip number?{}) ...>>{}<<".format(self.unifiCloudKeyIP, resp.text))
							self.executeCMDOnControllerReset(wait=True, calledFrom="executeCMDOnController-login json")
							continue

						if  resp.status_code != requests.codes.ok:
							self.indiLOG.log(40,u"UNIFI executeCMDOnController  login url:{}\ngives, ok not found or status_code:{} not in [{}]\n  error: {}\n".format(url,resp.status_code, requests.codes.ok, resp.text[0:300]) )
							self.executeCMDOnControllerReset(wait=True, calledFrom="executeCMDOnController-login ret code not ok")
							continue
						if 'X-CSRF-Token' in resp.headers:
							self.csrfToken = resp.headers['X-CSRF-Token']
				

						self.lastUnifiCookieRequests = time.time()
		
					if self.unifiControllerSession == "": 
						self.executeCMDOnControllerReset(wait=False, calledFrom="executeCMDOnController-unifiControllerSession = blank")
						if self.decideMyLog(u"Protect"): self.indiLOG.log(10,u"Connection: session =blank, continue ")
						continue

					headers = {"Accept": "application/json", "Content-Type": "application/json"}
					if self.csrfToken != "":
						headers['X-CSRF-Token'] = self.csrfToken


					cookies_dict = requests.utils.dict_from_cookiejar(self.unifiControllerSession.cookies)
					if self.unifiControllerOS == "unifi_os":
						cookies = {"TOKEN": cookies_dict.get('TOKEN')}
					else:
						cookies = {"unifises": cookies_dict.get('unifises'), "csrf_token": cookies_dict.get('csrf_token')}


					if self.unifiCloudKeySiteName == "":
						if not self.setunifiCloudKeySiteName(method="response", cookies=cookies, headers=headers ): continue
				
						
					if protect:
						url = "https://"+self.unifiCloudKeyIP+":"+self.unifiCloudKeyPort+"/proxy/protect/"+pageString.strip("/")
					else:
						url = "https://"+self.unifiCloudKeyIP+":"+self.unifiCloudKeyPort+self.unifiApiWebPage+"/"+self.unifiCloudKeySiteName+"/"+pageString.strip("/")

					if self.decideMyLog(u"ConnectionCMD"):	self.indiLOG.log(10,u"Connection: requests:{};\nheader:{};\ndataSEND:{};\ncookies:{};\ncmdType:{}".format(url, headers, dataSEND, cookies,cmdType) )
					if startText !="":						self.indiLOG.log(10,u"Connection: requests: startText{},".format(startText) )
					try:
							retCode			= ""
							respText 		= ""
							dictRET			= ""
							rawData			= ""
							if raw:	
								setStream	= True
							else:
								setStream	= False
							timeused		= 0

							if	 cmdType == "put":	resp = self.unifiControllerSession.put(url,  	json=dataSEND,		cookies=cookies, headers=headers, allow_redirects=False, verify=False, timeout=(3.,10.), stream=setStream)
							elif cmdType == "post":	resp = self.unifiControllerSession.post(url, 	json=dataSEND,		cookies=cookies, headers=headers, allow_redirects=False, verify=False, timeout=(3.,10.), stream=setStream)
							elif cmdType == "get":	
								if dataSEND == {}:
													resp =	self.unifiControllerSession.get(url,						cookies=cookies, headers=headers, allow_redirects=False, verify=False, timeout=(3.,10.), stream=setStream)
								else:
									if protect: # get protect needs params= not json=
													resp =	self.unifiControllerSession.get(url, 	params=dataSEND,	cookies=cookies, headers=headers, verify=False, timeout=(3.,10.), stream=setStream)
													if setStream: 
														rawData = resp.raw.read()
														#self.indiLOG.log(10,u"executeCMDOnController protect  url:{} params:{}; stream:{}, len(resp.raw.read):{}".format(url, dataSEND, setStream, len(rawData) ))
									else:
													resp =	self.unifiControllerSession.get(url, 	json=dataSEND,		cookies=cookies, headers=headers, allow_redirects=False, verify=False, timeout=(3.,10.), stream=setStream)

							elif cmdType == "patch":resp = self.unifiControllerSession.patch(url,	json=dataSEND,		cookies=cookies, headers=headers, allow_redirects=False, verify=False, timeout=(3.,10.), stream=setStream)
							else:					resp = self.unifiControllerSession.put(url,   	json=dataSEND,		cookies=cookies, headers=headers, allow_redirects=False, verify=False, timeout=(3.,10.), stream=setStream)
								
							try:
								retCode		= copy.copy(resp.status_code )
								respText 	= copy.copy(resp.text)
								retStatus	= resp.status_code
								##respText 	= respText.decode("utf8")
								timeused 	= resp.elapsed.total_seconds()	
								if self.decideMyLog(u"ConnectionRET"):	
									self.indiLOG.log(10,u"executeCMDOnController retCode:{}, time used:{}; cont length:{} os:{}; cmdType:{}, url:{}\n>>>{}<<<".format(retCode, timeused, len(respText), self.unifiControllerOS, cmdType, url, respText))
								headers 	= copy.copy(resp.headers)

								if not raw:
									dictRET	= json.loads(respText)

								resp.close()
								
							except	Exception, e:
								if iii > 0:
									errText = unicode(e)
									self.indiLOG.log(30,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
									self.indiLOG.log(20,u"executeCMDOnController has error, retCode:{}, time used:{}; cont length:{} os:{}; cmdType:{}, url:{}".format(retCode, timeused, len(respText), self.unifiControllerOS, cmdType, url))
									self.printHttpError(errText, respText)
								self.executeCMDOnControllerReset(wait=True, calledFrom="executeCMDOnController-exception after json/decode ..")
								try: resp.close()
								except: pass
								continue
 
							if protect:
								if retCode != requests.codes.ok:
									if iii == 1 and (not ignore40x or unicode(retCode).find("40") !=0):
										self.indiLOG.log(40,u"error:>> url:{}, resp code:{}".format(url, retCode))
									if (not ignore40x or unicode(retCode).find("40") !=0): self.executeCMDOnControllerReset(wait=True, calledFrom="executeCMDOnController-retcode not ok")
									continue
							else:
								if dictRET["meta"]["rc"] != "ok":
									if iii == 1 and (not ignore40x or unicode(retCode).find("40") !=0):
										self.indiLOG.log(40,u"error:>> url:{}, resp:{}".format(url, respText[0:100]))
									if  (not ignore40x or unicode(retCode).find("40") !=0): self.executeCMDOnControllerReset(wait=True, calledFrom="executeCMDOnController-dict ret not ok")
									continue

							self.lastUnifiCookieRequests = time.time()

							if 'X-CSRF-Token' in headers:
								self.csrfToken = headers['X-CSRF-Token']

							if  jsonAction == u"print":
								self.indiLOG.log(10,u"Reconnect: executeCMDOnController info\n{}".format(json.dumps(dictRET["data"], sort_keys=True, indent=2)) )
								return dictRET["data"]

							if raw:								return rawData
							elif jsonAction == "returnData":	return dictRET["data"]
							elif jsonAction == "protect":		return dictRET
							else:								return []

					except	Exception, e:
						self.indiLOG.log(40,u"in Line {} has error={}   Connection".format(sys.exc_traceback.tb_lineno, e) )

				## we get here when not successful
				self.executeCMDOnControllerReset(wait=True, calledFrom="executeCMDOnController-end-error")

			return []

		except	Exception, e:
			self.indiLOG.log(40,u"in Line {} has error={}   Connection".format(sys.exc_traceback.tb_lineno, e))

		self.executeCMDOnControllerReset(wait=False, calledFrom="executeCMDOnController-exception")
		return []



	####-----------------	   ---------
	def printHttpError(self, errtext, respText):
		try:
			detected = False
			test =[["error=Expecting object","( char ",")"],["ordinal not in range"," in position ",":"]]
			for tt in test:
				if  errtext.find(tt[0]) > -1: #  eg Expecting object: line 1 column 65733 (char 65732)
					try: 
						cpos = errtext.find(tt[1])
						if  cpos > 2: 
							charpos = errtext[cpos+len(tt[1]):]
							charpos = int(charpos.split(tt[2])[0])
							cp = max(0,charpos-10)
							self.indiLOG.log(20,u"executeCMDOnController   bad char >>{}<<;  @{} in\n {}...{}".format(respText[cp:cp+20], charpos, respText[0:200], respText[-200:]))
							detected = True
					except: pass

			if not detected:
				self.indiLOG.log(20,u"executeCMDOnController  resp:>>{}  ...  {}<<<".format(respText[0:200], respText[-200:]) )

		except	Exception, e:
			self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return


	####-----------------	   ---------
	def getSnapshotfromCamera(self, indigoCameraId, fileName):
		try:
			dev		= indigo.devices[int(indigoCameraId)]
			cmdR	= self.curlPath +" 'http://"+dev.states[u"ip"] +"/snap.jpeg' > "+ fileName
			if self.decideMyLog(u"Video"): self.indiLOG.log(10,u"Video: getSnapshotfromNVR with: {}".format(cmdR) )
			ret 	= subprocess.Popen(cmdR, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
			if self.decideMyLog(u"Video"): self.indiLOG.log(10,u"Video: getSnapshotfromCamera response: {}".format(ret))
			return "ok"
		except	Exception, e:
			self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			return "error:"+unicode(e)
		return " error"


	####-----------------	   ---------
	def getSnapshotfromNVR(self, indigoCameraId, width, fileName):

		try:
			camApiKey = indigo.devices[int(indigoCameraId)].states[u"apiKey"]
			url			= "http://"+self.ipNumbersOf[u"VD"] +":7080/api/2.0/snapshot/camera/"+camApiKey+"?force=true&width="+unicode(width)+"&apiKey="+self.nvrVIDEOapiKey
			if self.requestOrcurl.find(u"curl") > -1:
				cmdR	= self.curlPath+" -o '" + fileName +"'  '"+ url+"'"
				try:
					if self.decideMyLog(u"Video"): self.indiLOG.log(10,u"Video: {}".format(cmdR) )
					ret = subprocess.Popen(cmdR, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[1]
					try:
						fs1	 = ""
						fs	 = 0
						fs0	 = ""
						unit = ""
						if ret.find(u"\r")> -1: ret = ret.split("\r")
						else:                  ret = ret.split("\n")
						fs0  = ret[-1] # last line
						fs1  = fs0.split()[-1] # last number
						unit = fs1[-1] # last char
						fs  = int(fs1.strip("k").strip("m").strip("M"))
					except: fs = 0
					if fs == 0:
						self.indiLOG.log(40,u"getSnapshotfromNVR has error, no file returned,  Video error: \n{}\n{}".format(ret[1], cmdR))
						return "error, no file returned"
					return "ok, bytes transfered: {}{}".format(fs, unit)
				except	Exception, e:
					self.indiLOG.log(40,u"in Line {} has error={}  Video error".format(sys.exc_traceback.tb_lineno, e))
				return "error:"+unicode(e)

			else:
				session = requests.Session()

				if self.decideMyLog(u"Video"): self.indiLOG.log(10,u"Video: getSnapshotfromNVR login with: {}".format(url) )

				resp	= session.get(url, stream=True)
				if self.decideMyLog(u"Video"): self.indiLOG.log(10,u"Video: getSnapshotfromNVR response {}[kB]: {}; ".format(len(resp.content)/1024, resp.status_code) )
				if unicode(resp.status_code) == "200":
					f = open(fileName,"wb")
					f.write(resp.content)
					f.close()
					unit=""
					try:
						ll = int(len(resp.content))
						if ll > 1024:
							ll /=1024
							unit="k"
							if ll > 1024:
								ll /=1024
								unit="M"
					except: ll = ""
					return "ok, bytes transfered: "+ unicode(ll)+unit
				return "error "+unicode(resp.status_code)
		except	Exception, e:
			self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return "error:"+unicode(e)



	####-----------------	   ---------
	def groupStatusINIT(self):
		for group in  _GlobalConst_groupList:
			for tType in ["Home","Away","lastChange","name"]:
				varName="Unifi_Count_"+group+"_"+tType
				if varName not in self.varExcludeSQLList: self.varExcludeSQLList.append(varName)
				try:
					var = indigo.variables[varName]
				except:
					if varName.find(u"name")>-1: indigo.variable.create(varName,group+" change me to what YOU like",folder=self.folderNameIDVariables)
					else:						indigo.variable.create(varName,"0",folder=self.folderNameIDVariables)

		for tType in ["Home","Away","lastChange"]:
			varName="Unifi_Count_ALL_"+tType
			if self.enableSqlLogging:
				if varName not in self.varExcludeSQLList: self.varExcludeSQLList.append(varName)
			try:
				var = indigo.variables[varName]
			except:
				indigo.variable.create(varName,"0",folder=self.folderNameIDVariables)

		try:	indigo.variable.create("Unifi_With_Status_Change",value="", folder=self.folderNameIDVariables)
		except: pass
		try:	indigo.variable.create("Unifi_With_IPNumber_Change",value="", folder=self.folderNameIDVariables)
		except: pass
		try:	indigo.variable.create("Unifi_New_Device",value="", folder=self.folderNameIDVariables)
		except: pass

	####-----------------	   ---------
	def setGroupStatus(self, init=False):
		self.statusChanged = 0
		try:

			triggerGroup= {}
			for group in self.groupStatusList:
				triggerGroup[group]={"allHome":False,"allWay":False,"oneHome":False,"oneAway":False}

			for group in  _GlobalConst_groupList:
				self.groupStatusList[group]["nAway"] = 0
				self.groupStatusList[group]["nHome"] = 0
			self.groupStatusListALL["nHome"] = 0
			self.groupStatusListALL["nAway"] = 0

			okList =[]


			for dev in indigo.devices.iter(self.pluginId):
				if u"groupMember" not in dev.states: continue

				if dev.states[u"status"]=="up":
					self.groupStatusListALL["nHome"]	 +=1
				else:
					self.groupStatusListALL["nAway"]	 +=1

				if dev.states[u"groupMember"] == "": continue
				if not dev.enabled:	 continue
				okList.append(unicode(dev.id))
				props= dev.pluginProps
				gMembers = (dev.states[u"groupMember"].strip(",")).split(",")
				for group in _GlobalConst_groupList:
					if group in gMembers:
						self.groupStatusList[group]["members"][unicode(dev.id)] = True
						if dev.states[u"status"]=="up":
							if self.groupStatusList[group]["oneHome"] =="0":
								triggerGroup[group]["oneHome"] = True
								self.groupStatusList[group]["oneHome"]	 = "1"
							self.groupStatusList[group]["nHome"]	 +=1
						else:
							if self.groupStatusList[group]["oneAway"] =="0":
								triggerGroup[group]["oneAway"] = True
							self.groupStatusList[group]["oneAway"]	 = "1"
							self.groupStatusList[group]["nAway"]	 +=1

			for group in  _GlobalConst_groupList:
				removeList=[]
				for member in self.groupStatusList[group]["members"]:
					if member not in okList:
						removeList.append(member)
				for member in  removeList:
					del self.groupStatusList[group]["members"][member]


			for group in  _GlobalConst_groupList:
				if self.groupStatusList[group]["nAway"] == len(self.groupStatusList[group]["members"]):
					if self.groupStatusList[group]["allAway"] =="0":
						triggerGroup[group]["allAway"] = True
					self.groupStatusList[group]["allAway"]	 = "1"
					self.groupStatusList[group]["oneHome"]	 = "0"
				else:
					self.groupStatusList[group]["allAway"]	 = "0"

				if self.groupStatusList[group]["nHome"] == len(self.groupStatusList[group]["members"]):
					if self.groupStatusList[group]["allHome"] =="0":
						triggerGroup[group]["allHome"] = True
					self.groupStatusList[group]["allHome"]	 = "1"
					self.groupStatusList[group]["oneAway"]	 = "0"
				else:
					self.groupStatusList[group]["allHome"]	 = "0"


			# now extra variables
			for group in  _GlobalConst_groupList:
				if	not init:
					#try:
						varName="Unifi_Count_"+group+"_"
						varHomeV = indigo.variables[varName+"Home"].value
						varAwayV = indigo.variables[varName+"Away"].value
						if	varHomeV != unicode(self.groupStatusList[group]["nHome"]) or varAwayV != unicode(self.groupStatusList[group]["nAway"]) or len(indigo.variables["Unifi_Count_"+group+"_lastChange"].value) == 0 :
								indigo.variable.updateValue(u"Unifi_Count_"+group+"_lastChange", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
					#except:pass

				for tType in ["Home","Away"]:
					varName="Unifi_Count_"+group+"_"+tType
					gName="n"+tType
					try:
						var = indigo.variables[varName]
					except:
						indigo.variable.create(varName,"0",folder=self.folderNameIDVariables)
						var = indigo.variables[varName]
					if var.value !=	 unicode(self.groupStatusList[group][gName]):
						indigo.variable.updateValue(varName,unicode(self.groupStatusList[group][gName]))


			if	not init:
				try:
					varName="Unifi_Count_ALL_"
					varHomeV = indigo.variables[varName+"Home"].value
					varAwayV = indigo.variables[varName+"Away"].value
					if varHomeV != unicode(self.groupStatusListALL["nHome"]) or varAwayV != unicode(self.groupStatusListALL["nAway"]) or len(indigo.variables["Unifi_Count_ALL_lastChange"].value) == 0:
						indigo.variable.updateValue(u"Unifi_Count_ALL_lastChange", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
				except:
					self.groupStatusINIT()

			for tType in ["Home","Away"]:
				varName="Unifi_Count_ALL_"+tType
				gName="n"+tType
				try:
					var = indigo.variables[varName]
				except:
					indigo.variable.create(varName,"0",folder=self.folderNameIDVariables)
					var = indigo.variables[varName]
				if var.value != unicode(self.groupStatusListALL[gName]):
					indigo.variable.updateValue(varName,unicode(self.groupStatusListALL[gName]))

			#for group in  self.groupStatusList:
			#	 self.myLog( text=group+"  "+ unicode( self.groupStatusList[group]))
			#self.myLog( text="trigger list "+ unicode( self.triggerList))


			if	not init  and len(self.triggerList) > 0:
				for group in triggerGroup:
					for tType in triggerGroup[group]:
						#self.myLog( text=group+"-"+tType+"  trigger:"+unicode(triggerGroup[group][tType]))
						if triggerGroup[group][tType]:
							self.triggerEvent(group+"_"+tType)

		except	Exception, e:
			self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

		return

######################################################################################
	# Indigo Trigger Start/Stop
######################################################################################

	####-----------------	 ---------
	def triggerStartProcessing(self, trigger):
#		self.myLog( text=u"BeaconData",u"<<-- entering triggerStartProcessing: %s (%d)" % (trigger.name, trigger.id) )iDeviceHomeDistance
		self.triggerList.append(trigger.id)
#		self.myLog( text=u"BeaconData",u"exiting triggerStartProcessing -->>")

	####-----------------	 ---------
	def triggerStopProcessing(self, trigger):
#		self.myLog( text=u"BeaconData",u"<<-- entering triggerStopProcessing: %s (%d)" % (trigger.name, trigger.id))
		if trigger.id in self.triggerList:
#			self.myLog( text=u"BeaconData",u"TRIGGER FOUND")
			self.triggerList.remove(trigger.id)
#		self.myLog( text=u"BeaconData", u"exiting triggerStopProcessing -->>")

	#def triggerUpdated(self, origDev, newDev):
	#	self.logger.log(4, u"<<-- entering triggerUpdated: %s" % origdev.name)
	#	self.triggerStopProcessing(origDev)
	#	self.triggerStartProcessing(newDev)


######################################################################################
	# Indigo Trigger Firing
######################################################################################

	####-----------------	 ---------
	def triggerEvent(self, eventId):
		#self.myLog( text=u"<<-- entering triggerEvent: %s " % eventId)
		for trigId in self.triggerList:
			trigger = indigo.triggers[trigId]
			#self.myLog( text=u"<<-- trigger "+ unicode(trigger)+"  eventId:"+ eventId)
			if trigger.pluginTypeId == eventId:
				#self.myLog( text=u"<<-- trigger exec")
				indigo.trigger.execute(trigger)
		return




	####-----------------setup empty dicts for pointers	 type, mac --> indigop and indigo --> mac,	type ---------
	def setUpDownStateValue(self, dev):
		update=False
		try:
			upDown = ""
			props=dev.pluginProps
			if u"expirationTime" not in props:
				props[u"expirationTime"] = self.expirationTime
				update=True
			if u"useWhatForStatus" in props:
				if props[u"useWhatForStatus"].find(u"WiFi") > -1:
					if u"useWhatForStatusWiFi" in props:
						if props[u"useWhatForStatusWiFi"] != "" and props[u"useWhatForStatusWiFi"] != u"Expiration":
							if props[u"useWhatForStatusWiFi"]in [u"IdleTime",u"Optimized",u"FastDown"]:
								if u"idleTimeMaxSecs" not in props:
									props[u"idleTimeMaxSecs"]= u"10"
									update=True
								upDown = u"WiFi" + "/" + props[u"useWhatForStatusWiFi"]+u"-idle:"+props[u"idleTimeMaxSecs"]
							else:
								upDown = u"WiFi" + "/" + props[u"useWhatForStatusWiFi"]
						else:
							upDown =  u"Wifi"
					else:
						upDown =  u"Wifi"

				elif props[u"useWhatForStatus"].find(u"DHCP") > -1:
					if u"useAgeforStatusDHCP" in props and	props[u"useAgeforStatusDHCP"] != "" and props[u"useAgeforStatusDHCP"] != u"-1":
						upDown = u"DHCP" + "-age:" + props[u"useAgeforStatusDHCP"]
					else:
						upDown = u"DHCP"

				elif props[u"useWhatForStatus"] == u"OptDhcpSwitch":
					upDown ="OPT: "
					if u"useAgeforStatusDHCP" in props and	props[u"useAgeforStatusDHCP"] != "" and props[u"useAgeforStatusDHCP"] != u"-1":
						upDown += u"DHCP" + "-age:" + props[u"useAgeforStatusDHCP"]+"  "
					else:
						upDown += u"DHCP "

					if u"useupTimesforStatusSWITCH" in props and props[u"useupTimeforStatusSWITCH"]:
							upDown += u"SWITCH" + u"/upTime-notchgd"
					else:
							upDown += u"SWITCH"

				elif props[u"useWhatForStatus"] == u"SWITCH":
					if u"useupTimesforStatusSWITCH" in props and props[u"useupTimeforStatusSWITCH"]:
							upDown += u"SWITCH" + u"/upTime-notchgd"
					else:
							upDown += u"SWITCH"

				upDown +=  u"-exp:"+ unicode(self.getexpT(props)).split(".")[0]
				self.addToStatesUpdateList(dev.id,u"upDownSetting", upDown)

			if u"expirationTime" not in props:
				props[u"expirationTime"] = self.expirationTime
				update=True

			if u"AP" in dev.states:
				if dev.states[u"AP"].find(u"-") == -1 :
					newAP= dev.states[u"AP"]+"-"
					dev.updateStateOnServer(u"AP",newAP)


		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		if update:
			dev.replacePluginPropsOnServer(props)
		return


	####-----------------setup empty dicts for pointers	 type, mac --> indigop and indigo --> mac,	type ---------
	def setupStructures(self, xType, dev, MAC, init=False):
		devIds =""
		try:

			devIds = unicode(dev.id)
			if devIds not in self.xTypeMac:
				self.xTypeMac[devIds] = {"xType":"", "MAC":""}
			self.xTypeMac[devIds]["xType"]	= xType
			self.xTypeMac[devIds][u"MAC"]	= MAC

			if xType not in self.MAC2INDIGO:
				self.MAC2INDIGO[xType]={}

			if MAC not in self.MAC2INDIGO[xType]:
			   self.MAC2INDIGO[xType][MAC] = {}

			self.MAC2INDIGO[xType][MAC][u"devId"] = dev.id
			if u"ipNumber" in dev.states:
				self.MAC2INDIGO[xType][MAC][u"ipNumber"] = dev.states[u"ipNumber"]

			try:	self.MAC2INDIGO[xType][MAC][u"lastUp"] == float(self.MAC2INDIGO[xType][MAC][u"lastUp"])
			except: self.MAC2INDIGO[xType][MAC][u"lastUp"] = 0.


			if u"last_seen" 	not in self.MAC2INDIGO[xType][MAC]:	self.MAC2INDIGO[xType][MAC][u"last_seen"] 		= -1
			if u"use_fixedip" 	not in self.MAC2INDIGO[xType][MAC]:	self.MAC2INDIGO[xType][MAC][u"use_fixedip"] 	= False
			if u"blocked" 		not in self.MAC2INDIGO[xType][MAC]:	self.MAC2INDIGO[xType][MAC][u"blocked"] 		= False
			if u"lastAPMessage" not in self.MAC2INDIGO[xType][MAC]:	self.MAC2INDIGO[xType][MAC][u"lastAPMessage"] 	= 0

		except	Exception, e:
			self.indiLOG.log(40,u"in Line {} has error={}\n{}    {}     {}   {}".format(sys.exc_traceback.tb_lineno, e, unicode(xType), devIds, unicode(MAC), unicode(self.MAC2INDIGO)) )
			time.sleep(300)

		if xType ==u"UN":
				self.MAC2INDIGO[xType][MAC][u"AP"]			   = dev.states[u"AP"].split("-")[0]
				self.MAC2INDIGO[xType][MAC][u"lastWOL"]		   = 0.

				for item in [u"inListWiFi",u"inListDHCP",]:
					if item not in self.MAC2INDIGO[xType][MAC]:
							self.MAC2INDIGO[xType][MAC][item] = False
				for item in [u"GHz",u"idleTimeWiFi",u"upTimeWifi",u"upTimeDHCP"]:
					if item not in self.MAC2INDIGO[xType][MAC]:
							self.MAC2INDIGO[xType][MAC][item] = ""

				for ii in range(_GlobalConst_numberOfSW):
					for item in [u"inListSWITCH_"]:
						if item+unicode(ii) not in self.MAC2INDIGO[xType][MAC]:
							self.MAC2INDIGO[xType][MAC][item+unicode(ii)] = -1
					for item in [u"ageSWITCH_",u"upTimeSWITCH_"]:
						if item+unicode(ii) not in self.MAC2INDIGO[xType][MAC]:
							self.MAC2INDIGO[xType][MAC][item+unicode(ii)] = ""


		if xType ==u"SW":
			if u"ports" not in self.MAC2INDIGO[xType][MAC]:
				self.MAC2INDIGO[xType][MAC][u"ports"] = {}
			if u"upTime" not in self.MAC2INDIGO[xType][MAC]:
				self.MAC2INDIGO[xType][MAC][u"upTime"] = ""

		elif xType ==u"AP":
			self.MAC2INDIGO[xType][MAC][u"apNo"] = dev.states[u"apNo"]

		elif xType ==u"GW":
			pass

		elif xType ==u"NB":
			if u"age" not in self.MAC2INDIGO[xType][MAC]:
				self.MAC2INDIGO[xType][MAC][u"age"] = ""



	###########################	   MAIN LOOP  ############################
	####-----------------init  main loop ---------
	def fixBeforeRunConcurrentThread(self):

		nowDT = datetime.datetime.now()
		self.lastMinute		= nowDT.minute
		self.lastHour		= nowDT.hour
		self.logQueue		= Queue.Queue()
		self.logQueueDict	= Queue.Queue()
		self.apDict			= {}
		self.countLoop		= 0
		self.upDownTimers	= {}
		self.xTypeMac		= {}
		self.broadcastIP	= "9.9.9.255"

		self.writeJson(dataVersion, fName=self.indigoPreferencesPluginDir + "dataVersion")

		self.buttonConfirmGetAPDevInfoFromControllerCALLBACK()

		try: 	indigo.variable.delete(u"Unifi_Camera_with_Event")
		except: pass
		indigo.variable.create(u"Unifi_Camera_with_Event", value ="", folder=self.folderNameIDVariables)

		try: 	indigo.variable.delete(u"Unifi_Camera_Event_PathToThumbnail")
		except: pass
		indigo.variable.create(u"Unifi_Camera_Event_PathToThumbnail", value ="", folder=self.folderNameIDVariables)

		try: 	indigo.variable.delete(u"Unifi_Camera_Event_DateOfThumbNail")
		except: pass
		indigo.variable.create(u"Unifi_Camera_Event_DateOfThumbNail", value ="", folder=self.folderNameIDVariables)

		try: 	indigo.variable.delete(u"Unifi_Camera_Event_Date")
		except: pass
		indigo.variable.create(u"Unifi_Camera_Event_Date", value ="", folder=self.folderNameIDVariables)

		## if video enabled
		if self.cameraSystem == "nvr" and self.vmMachine !="":
			self.buttonVboxActionStartCALLBACK()

######## this for fixing the change from mac to MAC in states
		self.indiLOG.log(10,u"..getting vendor names for MAC#s")
		self.MacToNamesOK = True
		if self.enableMACtoVENDORlookup:
			self.indiLOG.log(10,u"..getting missing vendor names for MAC #")
		self.MAC2INDIGO = {}
		self.readMACdata()

		self.indiLOG.log(10,u"..setup dicts  ..")
		delDEV = {}
		for dev in indigo.devices.iter(self.pluginId):
			if dev.deviceTypeId in[u"client",u"camera","NVR-video","NVR"]: continue
			if u"status" not in dev.states:
				self.indiLOG.log(10,u"{} has no status".format(dev.name))
				continue
			else:
				if u"onOffState" in dev.states and  ( (dev.states[u"status"] in ["up","rec","ON"]) != dev.states[u"onOffState"] ):
							dev.updateStateOnServer("onOffState", value= dev.states[u"status"] in ["up","rec","ON"], uiValue=dev.states[u"displayStatus"])

			props= dev.pluginProps
			goodDevice = True
			devId = unicode(dev.id)

			if u"MAC" in dev.states:
				MAC = dev.states[u"MAC"]
				if dev.states[u"MAC"] == "":
					if dev.address != "":
						try:
							self.addToStatesUpdateList(dev.id,u"MAC", dev.address)
							MAC = dev.address
						except:
							goodDevice = False
							self.indiLOG.log(10,u"{} no MAC # deleting".format(dev.name))
							delDEV[devId]=True
							continue
				if dev.address != MAC:
					props[u"address"] = MAC
					dev.replacePluginPropsOnServer(props)

			if self.MacToNamesOK and u"vendor" in dev.states:
				if (dev.states[u"vendor"] == "" or dev.states[u"vendor"].find(u"<html>") >-1 ) and goodDevice:
					vendor = self.getVendortName(MAC)
					if vendor != "":
						self.addToStatesUpdateList(dev.id,u"vendor", vendor)
					if	dev.states[u"vendor"].find(u"<html>") >-1   and	 vendor =="" :
						self.addToStatesUpdateList(dev.id,u"vendor", "")


			if dev.deviceTypeId == u"UniFi":
				#self.myLog( text=u" adding to MAC2INDIGO " + MAC)
				self.setupStructures(u"UN", dev, MAC)


			if dev.deviceTypeId == "Device-AP":
				self.setupStructures(u"AP", dev, MAC)

			if dev.deviceTypeId.find(u"Device-SW")>-1:
				self.setupStructures(u"SW", dev, MAC)

			if dev.deviceTypeId == u"neighbor":
				self.setupStructures(u"NB", dev, MAC)

			if dev.deviceTypeId == u"gateway":
				self.setupStructures(u"GW", dev, MAC)

			if "isProtectCamera" not in props:
				self.setImageAndStatus(dev, dev.states[u"status"], force=True)

			if u"created" in dev.states and dev.states[u"created"] == "":
				self.addToStatesUpdateList(dev.id,u"created", nowDT.strftime(u"%Y-%m-%d %H:%M:%S"))


			self.setUpDownStateValue(dev)

			self.executeUpdateStatesList()

		for devid in delDEV:
			 sself.indiLOG.log(10,u" deleting , bad mac "+ devid )
			 indigo.device.delete[int(devid)]



		## remove old non exiting MAC / indigo devices
		for xType in self.MAC2INDIGO:
			if u"" in self.MAC2INDIGO[xType]:
				del self.MAC2INDIGO[xType][""]
			delXXX = {}
			for MAC in self.MAC2INDIGO[xType]:
				if len(MAC) < 16:
					delXXX[MAC] = True
					continue
				try: indigo.devices[self.MAC2INDIGO[xType][MAC][u"devId"]]
				except	Exception, e:
					self.indiLOG.log(10,u"removing indigo id: "+ unicode(self.MAC2INDIGO[xType][MAC][u"devId"])+"  from internal list" )
					time.sleep(1)
					delXXX[MAC] = True
			for MAC in delXXX:
				del self.MAC2INDIGO[xType][MAC]
			# some cleanup it is now upTime xxx  not uptime xxx
			for MAC in self.MAC2INDIGO[xType]:
				delXXX={}
				for yy in self.MAC2INDIGO[xType][MAC]:
					if yy.find(u"uptime") >-1:
						delXXX[yy]=True
				for yy in delXXX:
					del self.MAC2INDIGO[xType][MAC][yy]
		delXXX = {}

		for devId  in self.xTypeMac:
			try:	 dev = indigo.devices[int(devId)]
			except	Exception, e:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
				if unicode(e).find(u"timeout") >-1:
					self.sleep(20)
					return False
				delXXX[devId]=True
			MAC =  self.xTypeMac[devId][u"MAC"]


			if self.xTypeMac[devId]["xType"]=="SW":
				ipN = dev.states[u"ipNumber"]
				sw	= dev.states[u"switchNo"]
				try:
					sw = int(sw)
					if ipN != self.ipNumbersOf[u"SW"][sw]:
						dev.updateStateOnServer("ipNumber",self.ipNumbersOf[u"SW"][sw])
				except:
					if self.isValidIP(ipN):
						for ii in range(len(self.ipNumbersOf[u"SW"])):
							if self.ipNumbersOf[u"SW"][ii] == ipN:
								dev.updateStateOnServer("apNo",ii)
								break


			if self.xTypeMac[devId]["xType"]=="AP":
				ipN = dev.states[u"ipNumber"]
				sw	= dev.states[u"apNo"]
				try:
					sw = int(sw)
					if ipN != self.ipNumbersOf[u"AP"][sw]:
						dev.updateStateOnServer("ipNumber",self.ipNumbersOf[u"AP"][sw])
				except:
					if self.isValidIP(ipN):
						for ii in range(len(self.ipNumbersOf[u"AP"])):
							if self.ipNumbersOf[u"AP"][ii] == ipN:
								dev.updateStateOnServer("apNo",ii)
								break



		for devId in delXXX:
			del self.xTypeMac[devId]
		delXXX = {}

		self.saveMACdata()

		self.lastSecCheck	= time.time()

		self.readupDownTimers()
		self.saveupDownTimers()

		##start accepting staus = DOWN in 30secs
		self.pluginStartTime = time.time() +30

		self.pluginState   = "run"



		if self.cameraSystem == "nvr":

			self.indiLOG.log(10,u"..setup NVR -1 getNVRIntoIndigo")
			self.testServerIfOK(self.ipNumbersOf[u"VD"], "VDdict")
			self.getNVRIntoIndigo(force= True)
			self.indiLOG.log(10,u"..setup NVR -2 getNVRCamerastoIndigo")
			self.getNVRCamerastoIndigo(force=True)
			self.indiLOG.log(10,u"..setup NVR -3 saveCameraEventsStatus")
			self.saveCameraEventsStatus=True; self.saveCamerasStats(force=False)


				### start video logfile listening
			self.trVDLog = ""
			self.indiLOG.log(10,u"..starting threads for VIDEO NVR log event capture")
			self.trVDLog  = threading.Thread(name=u'getMessages-VD-log', target=self.getMessages, args=(self.ipNumbersOf[u"VD"],0,u"VDtail",500,))
			self.trVDLog.start()
			self.sleep(0.2)

		self.lastRefreshProtect  = 0

		self.getProtectIntoIndigo()
		self.protectThread = {u"thread":"", u"status":""}
		if self.cameraSystem == u"protect":
			self.protectThread[u"status"]  = u"run"
			self.protectThread[u"thread"]  = threading.Thread(name=u'get-protectevents', target=self.getProtectEvents)
			self.protectThread[u"thread"].start()



		self.getcontrollerDBForClients()

		self.consumeDataThread = {u"log":{},u"dict":{}}
		self.consumeDataThread[u"log"][u"status"]  = u"run"
		self.consumeDataThread[u"log"][u"thread"]  = threading.Thread(name=u'comsumeLogData', target=self.comsumeLogData)
		self.consumeDataThread[u"log"][u"thread"].start()
		self.consumeDataThread[u"dict"][u"status"] = u"run"
		self.consumeDataThread[u"dict"][u"thread"] = threading.Thread(name=u'comsumeDictData', target=self.comsumeDictData)
		self.consumeDataThread[u"dict"][u"thread"].start()

		try:
			self.trAPLog  = {}
			self.trAPDict = {}
			nsleep= 1
			if self.numberOfActive[u"AP"] > 0:
				self.indiLOG.log(10,u"..starting threads for {} APs,  {} sec apart (MSG-log and db-DICT)".format(self.numberOfActive[u"AP"],nsleep) )
				for ll in range(_GlobalConst_numberOfAP):
					if self.devsEnabled[u"AP"][ll]:
						if (self.unifiControllerType == "UDM" or self.controllerWebEventReadON > 0) and ll == self.numberForUDM[u"AP"]: continue
						ipn = self.ipNumbersOf[u"AP"][ll]
						self.broadcastIP = ipn
						if self.decideMyLog(u"Logic"): self.indiLOG.log(10,u"START: AP Thread # {}   {}".format(ll, ipn) )
						if self.connectParams[u"commandOnServer"][u"APtail"].find(u"off") ==-1: 
							self.trAPLog[unicode(ll)] = threading.Thread(name=u'getMessages-AP-log-'+unicode(ll), target=self.getMessages, args=(ipn,ll,u"APtail",float(self.readDictEverySeconds[u"AP"])*2,))
							self.trAPLog[unicode(ll)].start()
							self.sleep(nsleep)
						self.trAPDict[unicode(ll)] = threading.Thread(name=u'getMessages-AP-dict-'+unicode(ll), target=self.getMessages, args=(ipn,ll,u"APdict",float(self.readDictEverySeconds[u"AP"])*2,))
						self.trAPDict[unicode(ll)].start()
						self.sleep(nsleep)


		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.quitNow = u"stop"
			self.stop = copy.copy(self.ipNumbersOf[u"AP"])
			return False



		if self.devsEnabled[u"GW"] and not self.devsEnabled[u"UD"]:
			self.indiLOG.log(10,u"..starting threads for GW (MSG-log and db-DICT)")
			self.broadcastIP = self.ipNumbersOf[u"GW"]
			if self.connectParams[u"enableListener"][u"GWtail"]: 
				self.trGWLog  = threading.Thread(name=u'getMessages-UGA-log', target=self.getMessages, args=(self.ipNumbersOf[u"GW"],0,u"GWtail",float(self.readDictEverySeconds[u"GW"])*2,))
				self.trGWLog.start()
				self.sleep(1)
			self.trGWDict = threading.Thread(name=u'getMessages-UGA-dict', target=self.getMessages, args=(self.ipNumbersOf[u"GW"],0,u"GWdict",float(self.readDictEverySeconds[u"GW"])*2,))
			self.trGWDict.start()


		### for UDM devices..
		#1. get mca dump dict   
		if self.devsEnabled[u"UD"]:
			self.indiLOG.log(10,u"..starting threads for UDM  (db-DICT)")
			self.broadcastIP = self.ipNumbersOf[u"UD"]
			self.trUDDict = threading.Thread(name=u'getMessages-UDM-dict', target=self.getMessages, args=(self.ipNumbersOf[u"GW"],0,u"UDdict",float(self.readDictEverySeconds[u"UD"])*2,))
			self.trUDDict.start()
			# 2.  this  runs every xx secs  http get data 
			try:
				self.trWebApiEventlog  = ""
				if self.controllerWebEventReadON > 0:
					self.trWebApiEventlog = threading.Thread(name=u'controllerWebApilogForUDM', target=self.controllerWebApilogForUDM, args=(0, ))
					self.trWebApiEventlog.start()
			except	Exception, e:
				if unicode(e).find(u"None") == -1:
					self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
				self.quitNow = u"stop"
				self.stop = copy.copy(self.ipNumbersOf[u"SW"])
				return False



		try:
			self.trSWLog = {}
			self.trSWDict = {}
			if self.numberOfActive[u"SW"] > 0:
				minCheck = float(self.readDictEverySeconds[u"SW"])*2.
				if self.numberOfActive[u"SW"] > 1:
					minCheck = 2.* float(self.readDictEverySeconds[u"SW"]) / self.numberOfActive[u"SW"]
				else:
					minCheck = 2.* float(self.readDictEverySeconds[u"SW"])
				self.indiLOG.log(10,u"..starting threads for {} SWs {} sec apart (db-DICT only)".format(self.numberOfActive[u"SW"],nsleep) )
				for ll in range(_GlobalConst_numberOfSW):
					if self.devsEnabled[u"SW"][ll]:
						self.sleep(1.)
						if self.unifiControllerType.find(u"UDM") > -1 and ll == self.numberForUDM[u"SW"]: continue
						ipn = self.ipNumbersOf[u"SW"][ll]
						if self.decideMyLog(u"Logic"): self.indiLOG.log(10,u"START SW Thread tr # {}  uDM#:{}  {}".format(ll, self.numberForUDM[u"SW"], ipn, self.unifiControllerType))
	 #					 self.trSWLog[unicode(ll)] = threading.Thread(name='self.getMessages', target=self.getMessages, args=(ipn, ll, "SWtail",float(self.readDictEverySeconds[u"SW"]*2,))
	 #					 self.trSWLog[unicode(ll)].start()
						self.trSWDict[unicode(ll)] = threading.Thread(name=u'getMessages-SW-Dict', target=self.getMessages, args=(ipn, ll, u"SWdict",minCheck,))
						self.trSWDict[unicode(ll)].start()

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.quitNow = u"stop"
			return False


		try:
			ip = self.broadcastIP.split(".")
			self.broadcastIP = ip[0]+"."+ip[1]+"."+ip[2]+".255"
		except:
			pass
		
		self.indiLOG.log(10,u"..starting threads finished" )


		return True




	###########################	   cProfile stuff   ############################ START
	####-----------------  ---------
	def getcProfileVariable(self):

		try:
			if self.timeTrVarName in indigo.variables:
				xx = (indigo.variables[self.timeTrVarName].value).strip().lower().split("-")
				if len(xx) ==1:
					cmd = xx[0]
					pri = ""
				elif len(xx) == 2:
					cmd = xx[0]
					pri = xx[1]
				else:
					cmd = "off"
					pri  = ""
				self.timeTrackWaitTime = 20
				return cmd, pri
		except	Exception, e:
			pass

		self.timeTrackWaitTime = 60
		return "off",""

	####-----------------            ---------
	def printcProfileStats(self,pri=""):
		try:
			if pri !="": pick = pri
			else:		 pick = 'cumtime'
			outFile		= self.indigoPreferencesPluginDir+"timeStats"
			indigo.server.log(" print time track stats to: {}.dump / txt  with option:{} ".format(outFile, pick) )
			self.pr.dump_stats(outFile+".dump")
			sys.stdout 	= open(outFile+".txt", "w")
			stats 		= pstats.Stats(outFile+".dump")
			stats.strip_dirs()
			stats.sort_stats(pick)
			stats.print_stats()
			sys.stdout = sys.__stdout__
		except: pass
		"""
		'calls'			call count
		'cumtime'		cumulative time
		'file'			file name
		'filename'		file name
		'module'		file name
		'pcalls'		primitive call count
		'line'			line number
		'name'			function name
		'nfl'			name/file/line
		'stdname'		standard name
		'time'			internal time
		"""

	####-----------------            ---------
	def checkcProfile(self):
		try:
			if time.time() - self.lastTimegetcProfileVariable < self.timeTrackWaitTime:
				return
		except:
			self.cProfileVariableLoaded = 0
			self.do_cProfile  			= u"x"
			self.timeTrVarName 			= u"enableTimeTracking_"+self.pluginShortName
			indigo.server.log(u"testing if variable {} is == on/off/print-option to enable/end/print time tracking of all functions and methods (option:'',calls,cumtime,pcalls,time)".format(self.timeTrVarName))

		self.lastTimegetcProfileVariable = time.time()

		cmd, pri = self.getcProfileVariable()
		if self.do_cProfile != cmd:
			if cmd == "on":
				if  self.cProfileVariableLoaded ==0:
					indigo.server.log(u"======>>>>   loading cProfile & pstats libs for time tracking;  starting w cProfile ")
					self.pr = cProfile.Profile()
					self.pr.enable()
					self.cProfileVariableLoaded = 2
				elif  self.cProfileVariableLoaded >1:
					self.quitNow = " restart due to change  ON  requested for print cProfile timers"
			elif cmd == u"off" and self.cProfileVariableLoaded >0:
					self.pr.disable()
					self.quitNow = u" restart due to  OFF  request for print cProfile timers "
		if cmd == u"print"  and self.cProfileVariableLoaded >0:
				self.pr.disable()
				self.printcProfileStats(pri=pri)
				self.pr.enable()
				indigo.variable.updateValue(self.timeTrVarName,"done")

		self.do_cProfile = cmd
		return

	####-----------------            ---------
	def checkcProfileEND(self):
		if self.do_cProfile in[u"on",u"print"] and self.cProfileVariableLoaded >0:
			self.printcProfileStats(pri="")
		return
	###########################	   cProfile stuff   ############################ END

	####-----------------	 ---------
	def setSqlLoggerIgnoreStatesAndVariables(self):
		try:
			if self.indigoVersion <  7.4:                             return 
			if self.indigoVersion == 7.4 and self.indigoRelease == 0: return 
			#tt = ["beacon",              "rPI","rPI-Sensor","BLEconnect","sensor"]
			if not self.enableSqlLogging: 
				for v in self.varExcludeSQLList:
					try:
						if v not in indigo.variables: continue
						var = indigo.variables[v]
						sp = var.sharedProps
						if u"sqlLoggerIgnoreChanges" not in sp  or sp[u"sqlLoggerIgnoreChanges"] != u"true":
							continue
						outONV += var.name+u"; "
						sp[u"sqlLoggerIgnoreChanges"] = u""
						var.replaceSharedPropsOnServer(sp)
					except: pass
				return 


			outOffV = ""
			for v in self.varExcludeSQLList:
					var = indigo.variables[v]
					sp = var.sharedProps
					#self.indiLOG.log(30,u"setting /testing off: Var: {} sharedProps:{}".format(var.name, sp) )
					if u"sqlLoggerIgnoreChanges" in sp and sp["sqlLoggerIgnoreChanges"] == "true": 
						continue
					#self.indiLOG.log(30,u"====set to off ")
					outOffV += var.name+u"; "
					sp["sqlLoggerIgnoreChanges"] = "true"
					var.replaceSharedPropsOnServer(sp)

			if len(outOffV) > 0: 
				self.indiLOG.log(10,u" \n")
				self.indiLOG.log(10,u"switching off SQL logging for variables\n :{}".format(outOffV) )
				self.indiLOG.log(10,u"switching off SQL logging for variables END\n")
		except Exception, e:
			self.indiLOG.log(40, u"error in  Line# {} ;  error={}".format(sys.exc_traceback.tb_lineno, e))

		return 



####-----------------   main loop          ---------
	def runConcurrentThread(self):
		### self.indiLOG.log(50,u"CLASS: Plugin")


		if not self.fixBeforeRunConcurrentThread():
			self.indiLOG.log(40,u"..error in startup")
			self.sleep(10)
			return

		self.setSqlLoggerIgnoreStatesAndVariables()

		self.indiLOG.log(10,u"runConcurrentThread.....")

		self.dorunConcurrentThread()
		self.checkcProfileEND()

		self.sleep(1)
		if self.quitNow !="":
			indigo.server.log( u"runConcurrentThread stopping plugin due to:  ::::: {} :::::".format(self.quitNow))
			serverPlugin = indigo.server.getPlugin(self.pluginId)
			serverPlugin.restart(waitUntilDone=False)
		return

####-----------------   main loop            ---------
	def dorunConcurrentThread(self):

		indigo.server.log(u" start   runConcurrentThread, initializing loop settings and threads ..")


		indigo.server.savePluginPrefs()
		self.lastDayCheck		= -1
		self.lastHourCheck		= datetime.datetime.now().hour
		self.lastMinuteCheck	= datetime.datetime.now().minute
		self.lastMinute10Check	= datetime.datetime.now().minute/10
		self.pluginStartTime 	= time.time()
		self.indiLOG.log(20,u"initialized ... looping")
		indigo.server.savePluginPrefs()	
		self.lastcreateEntryInUnifiDevLog = time.time() 

		try:
			while True:
				#self.indiLOG.log(10,u"looping, quitNow= >>{}<<".format(self.quitNow ) )
				sl = max(1., self.loopSleep / 10. )
				sli = int(self.loopSleep / sl)
				for ii in range(sli):
					if self.quitNow != "": break
					self.sleep(sl)

				if self.quitNow != "": break


				if time.time() - self.updateConnectParams > 0 :
					self.updateConnectParams  = time.time() + 100
					#self.indiLOG.log(10,u"saving updated connect parameters from config")
					self.pluginPrefs[u"connectParams"] = json.dumps(self.connectParams)
					indigo.server.savePluginPrefs()	
	 
				self.countLoop += 1
				ret = self.doTheLoop()
				if ret != "ok":
					self.indiLOG.log(10,u"LOOP   return break: >>{}<<".format(ret) )
					break
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

		self.postLoop()

		return


	###########################	   exec the loop  ############################
	####-----------------	 ---------
	def doTheLoop(self):

		if self.checkforUnifiSystemDevicesState == "validateConfig" or \
		  (self.checkforUnifiSystemDevicesState == "start" and (time.time() - self.pluginStartTime) > 30):
			self.checkForNewUnifiSystemDevices()
			if self.checkforUnifiSystemDevicesState == "reboot":
				self.quitNow ="new devices"
				self.checkforUnifiSystemDevicesState =""
				return "new Devices"

		if self.pendingCommand != []:
			if u"getNVRCamerasFromMongoDB-print" in self.pendingCommand: self.getNVRCamerasFromMongoDB(doPrint = True, action=["system","cameras"])
			if u"getNVRCamerastoIndigo"	 in self.pendingCommand: self.getNVRCamerastoIndigo(force = True)
			if u"getConfigFromNVR"		 in self.pendingCommand: self.getNVRIntoIndigo(force = True); self.getNVRCamerastoIndigo(force = True)
			if u"saveCamerasStats"		 in self.pendingCommand: self.saveCameraEventsStatus = True;  self.saveCamerasStats(force = True)
			self.pendingCommand =[]

		if self.quitNow != "": return "break"

		self.getNVRCamerastoIndigo(periodCheck = True)
		self.saveCamerasStats()
		self.saveDataStats()
		self.saveMACdata()

		if self.quitNow != "": return "break"

		part = u"main"+unicode(random.random()); self.blockAccess.append(part)
		for ii in range(90):
			if len(self.blockAccess) == 0 or self.blockAccess[0] == part: break # "my turn?
			self.sleep(0.1)
		if ii >= 89: self.blockAccess = [] # for safety if too long reset list

		## check for expirations etc

		self.checkOnChanges()
		self.executeUpdateStatesList()

		if self.quitNow != "": return "break"

		self.periodCheck()
		self.executeUpdateStatesList()
		self.sendUpdatetoFingscanNOW()
		if	 self.statusChanged ==1:  self.setGroupStatus()
		elif self.statusChanged ==2:  self.setGroupStatus(init=True)

		if self.quitNow != "": return "break"


		if len(self.devNeedsUpdate) > 0:
			for devId in self.devNeedsUpdate:
				try:
					self.setUpDownStateValue(indigo.devices[devId])
				except:
					pass
			self.devNeedsUpdate = []
			self.saveupDownTimers()
			self.setGroupStatus(init=True)

		self.executeUpdateStatesList()
		if len(self.sendBroadCastEventsList) >0: self.sendBroadCastNOW()

		if len(self.blockAccess)>0:	 del self.blockAccess[0]



		if self.lastMinuteCheck != datetime.datetime.now().minute:
			self.lastMinuteCheck = datetime.datetime.now().minute
			self.statusChanged = max(1,self.statusChanged)

			if self.quitNow != "": return "break"

			self.getUDMpro_sensors()

			if datetime.datetime.now().minute%5 == 0: 
				self.updateDevStateswRXTXbytes()

			if self.quitNow != "": return "break"

			if self.cameraSystem == "nvr" and self.vmMachine !="":
				if u"VDtail" in self.msgListenerActive and time.time() - self.msgListenerActive["VDtail"] > 600: # no recordings etc for 10 minutes, reissue mount command
					self.msgListenerActive["VDtail"] = time.time()
					self.buttonVboxActionStartCALLBACK()

			if self.lastMinute10Check != (datetime.datetime.now().minute)/10:
				self.lastMinute10Check = datetime.datetime.now().minute/10
				self.checkforUnifiSystemDevicesState = "10minutes"
				self.checkForNewUnifiSystemDevices()
				self.checkInListSwitch()

				if self.checkforUnifiSystemDevicesState == "reboot":
					self.quitNow ="new devices"
					self.checkforUnifiSystemDevicesState = ""
					return "new devices"


				if self.lastHourCheck != datetime.datetime.now().hour:
					self.lastHourCheck = datetime.datetime.now().hour

					if self.quitNow != "": return "break"

					self.saveupDownTimers()
					if self.lastHourCheck ==1: # recycle at midnight
						try:
							try:	indigo.variable.create("Unifi_With_Status_Change",value="", folder=self.folderNameIDVariables)
							except: pass
						except:		pass

					if self.lastDayCheck != datetime.datetime.now().day:
						self.lastDayCheck = datetime.datetime.now().day
						self.getBackupFilesFromController()

		return "ok"

	###########################	   after the loop  ############################
	####-----------------	 ---------
	def postLoop(self):

		self.pluginState   = "stop"
		indigo.server.savePluginPrefs()	

		if self.quitNow == "": self.quitNow = u" restart / stop requested "
		if self.quitNow == u"config changed":
			self.resetDataStats(calledFrom="postLoop")
		self.pluginPrefs[u"connectParams"] = json.dumps(self.connectParams)

		self.consumeDataThread[u"log"][u"status"]  = u"stop"
		self.consumeDataThread[u"dict"][u"status"] = u"stop"

		if True:
			for ll in range(len(self.devsEnabled[u"SW"])):
				try: 	self.trSWLog[unicode(ll)].join()
				except: pass
				try: 	self.trSWDict[unicode(ll)].join()
				except: pass
			for ll in range(len(self.devsEnabled[u"AP"])):
				try: 	self.trAPLog[unicode(ll)].join()
				except: pass
				try: 	self.trAPDict[unicode(ll)].join()
				except: pass

		try: 	self.trGWLog.join()
		except: pass
		try: 	self.trGWDict.join()
		except: pass
		try: 	self.trVDLog.join()
		except: pass

		## kill all expect "uniFi" programs
		self.killIfRunning("", "")

		self.saveupDownTimers()
		return 



	####-----------------	 ---------
	def saveupDownTimers(self):
		try:
			f = open(self.indigoPreferencesPluginDir+"upDownTimers","w")
			f.write(json.dumps(self.upDownTimers))
			f.close()
		except	Exception, e:
			self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

	####-----------------	 ---------
	def readupDownTimers(self):
		try:
			f = open(self.indigoPreferencesPluginDir+"upDownTimers","r")
			self.upDownTimers = json.loads(f.read())
			f.close()
		except:
			self.upDownTimers ={}
			try:
				f.close()
			except:
				pass

	####-----------------	 ---------
	def checkOnChanges(self):
		xType	= u"UN"
		try:
			if self.upDownTimers =={}: return
			deldev={}

			for devid in self.upDownTimers:
				try:
					dev= indigo.devices[int(devid)]
				except	Exception, e:
					if unicode(e).find(u"timeout waiting") > -1:
						self.indiLOG.log(40,u"in Line {} has error={}\ncommunication to indigo is interrupted".format(sys.exc_traceback.tb_lineno, e))
						return
					if unicode(e).find(u"not found in database") >-1:
						deldev[devid] =[-1,u"dev w devID:{} does not exist".format(devid)]
						continue
					self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
					return

				props=dev.pluginProps
				expT = self.getexpT(props)
				dt	= time.time() - expT
				dtDOWN = time.time() -	self.upDownTimers[devid][u"down"]
				dtUP   = time.time() -	self.upDownTimers[devid][u"up"]

				if dev.states[u"status"] != u"up": newStat = u"down"
				else:							   newStat = u"up"
				MAC = dev.states[u"MAC"]
				if self.upDownTimers[devid][u"down"] > 10.:
					if dtDOWN < 2: continue # ignore and up-> in the last 2 secs to avoid constant up-down-up
					if self.doubleCheckWithPing(newStat,dev.states[u"ipNumber"], props,dev.states[u"MAC"],"Logic", "checkOnChanges", "CHAN-WiF-Pg","UN") ==0:
							deldev[devid] = [MAC,"[down]>10 ping check"]
							continue
					if u"useWhatForStatusWiFi" in props and props[u"useWhatForStatusWiFi"] in [u"FastDown",u"Optimized"]:
						if dtDOWN > 10. and dev.states[u"status"] == u"up":
							self.setImageAndStatus(dev, u"down", ts=dt - 0.1, fing=True, level=1, text1= u"{:30s}  status was up  changed period WiFi, expT={:4.1f};  dt={:4.1f}".format(dev.name, expT, dt), iType=u"CHAN-WiFi",reason="FastDown")
							self.MAC2INDIGO[xType][dev.states[u"MAC"]][u"lastUp"] = time.time() - expT
							deldev[devid] = [MAC,"[down]>10 and fastD or optimized"]
							continue
					if dtDOWN >4:
						deldev[devid] = [MAC,u"[down]>10 and dtDown>4"]
				if self.upDownTimers[devid][u"up"] > 10.:
					if dtUP < 2: continue # ingnore and up-> in the last 2 secs to avoid constant up-down-up
					deldev[devid] = [MAC,"[up]>10 and tt-[up]>2"]
				if self.upDownTimers[devid][u"down"] == 0. and self.upDownTimers[devid][u"up"] == 0.:
					deldev[devid] = [MAC,"[down]==0 and [up]==0"]

			for devId in deldev:
				dd = deldev[devId]
				if self.decideMyLog(u"Logic", MAC=dd[0]): self.indiLOG.log(10,u"ChkOnChang del upDownTimers[{}],reason:{}".format(dd[0], dd[1]) )
				del self.upDownTimers[devId]

		except	Exception, e:
			self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

		return


	####-----------------	 ---------
	def getexpT(self, props):
		try:
			expT = self.expirationTime
			if u"expirationTime" in props and props[u"expirationTime"] != u"-1":
				try:
					expT = float(props[u"expirationTime"])
				except	Exception, e:
					self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
					self.indiLOG.log(40,u"props /expirationTime={}".format(props[u"expirationTime"]))
		except	Exception, e:
			self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return expT

		####-----------------  check things every minute / xx minute / hour once a day ..  ---------



	####-----------------	 ---------
	def getUDMpro_sensors(self):
		try:
			if True or self.unifiControllerType.find(u"UDM") == -1: return 

			cmd =  self.expectPath 
			cmd += " '"+self.pathToPlugin + "UDM-pro-sensors.exp' "
			cmd += " '"+self.connectParams[u"UserID"][u"unixUD"]+"' "
			cmd += " '"+self.connectParams[u"PassWd"][u"unixUD"]+"' "
			cmd +=      self.unifiCloudKeyIP
			cmd += " '"+self.escapeExpect(self.connectParams[u"promptOnServer"][self.unifiCloudKeyIP])+"' "

			if self.decideMyLog(u"UDM"): self.indiLOG.log(10,u"getUDMpro_sensors: get sensorValues from UDMpro w cmd: {}".format(cmd) )

			ret = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()

			data0 = ret[0].split("\n")
			nextItem = ""
			temperature = ""
			temperature_Board_CPU = ""
			temperature_Board_PHY = ""
			if self.decideMyLog(u"UDM") or self.decideMyLog(u"ExpectRET"): self.indiLOG.log(10,u"getUDMpro_sensors returned list: {}".format(data0) )
			for dd in data0:
				if dd.find(u":") == -1: continue
				nn = dd.strip().split(":")
				if nn[0] == "temp2_input":
					t2 	= round(float(nn[1]),1)
				elif nn[0] == "temp1_input":
					t1			= round(float(nn[1]),1)
				elif nn[0] == "temp3_input":
					t3 	= round(float(nn[1]),1)
 
			if self.decideMyLog(u"UDM"): self.indiLOG.log(10,u"getUDMpro_sensors: temp values found:  1:{}, 2:{}, 3:{}".format(t1, t2, t3) )
			found = False			
			for dev in indigo.devices.iter(u"props.isGateway"):
				if self.decideMyLog(u"UDM"): self.indiLOG.log(10,u"getUDMpro_sensors: adding temperature states to device:  {}-{}".format(dev.id, dev.name) )
				if dev.states[u"temperature"] 			!= t1 and t1 != "": 		  self.addToStatesUpdateList(dev.id,u"temperature", t1)
				if dev.states[u"temperature_Board_CPU"] != t2 and t2 != "": self.addToStatesUpdateList(dev.id,u"temperature_Board_CPU", t2)
				if dev.states[u"temperature_Board_PHY"] != t3 and t3 != "": self.addToStatesUpdateList(dev.id,u"temperature_Board_PHY", t3)
				self.executeUpdateStatesList()
				found = True			
				break
			if not found:
				if self.decideMyLog(u"UDM"): self.indiLOG.log(10,u"getUDMpro_sensors: not UDM-GW device setup in indigo" )


		except	Exception, e:
			self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

		return


	####-----------------	 ---------
	def periodCheck(self):
		try:

			if	self.countLoop < 10:					return
			if time.time() - self.pluginStartTime < 70: return
			changed = False

			if self.countLoop%2000 == 0: self.setSqlLoggerIgnoreStatesAndVariables()

			self.checkcProfile()

			self.getNVRIntoIndigo()
			self.getNVRCamerastoIndigo(periodCheck = True)

			self.getProtectIntoIndigo()

			self.saveCamerasStats()
			self.saveDataStats()
			self.saveMACdata()
			self.createEntryInUnifiDevLog()
			self.getcontrollerDBForClients()

			for dev in indigo.devices.iter(self.pluginId):

				try:
					if dev.deviceTypeId == u"camera_protect": continue
					if dev.deviceTypeId == u"camera": continue
					if dev.deviceTypeId == u"NVR": continue
					if u"MAC" not in dev.states: continue

					props = dev.pluginProps
					devid = unicode(dev.id)

					MAC		= dev.states[u"MAC"]
					if dev.deviceTypeId == u"UniFi" and self.testIgnoreMAC(MAC, fromSystem=u"periodCheck") : continue

					if unicode(devid) not in self.xTypeMac:
						if dev.deviceTypeId == u"UniFi":
							self.setupStructures(u"UN", dev, MAC)
						if dev.deviceTypeId == "Device-AP":
							self.setupStructures(u"AP", dev, MAC)
						if dev.deviceTypeId.find(u"Device-SW")>-1:
							self.setupStructures(u"SW", dev, MAC)
						if dev.deviceTypeId == u"neighbor":
							self.setupStructures(u"NB", dev, MAC)
						if dev.deviceTypeId == u"gateway":
							self.setupStructures(u"GW", dev, MAC)
					xType	= self.xTypeMac[devid]["xType"]

					expT= self.getexpT(props)
					try:
						lastUpTT   = self.MAC2INDIGO[xType][MAC][u"lastUp"]
					except:
						lastUpTT = time.time()
					lastUpTTFastDown = lastUpTT

					if dev.deviceTypeId == u"UniFi":
						ipN = dev.states[u"ipNumber"]

						# check for supended status, if sup : set, if back reset susp status
						if ipN in self.suspendedUnifiSystemDevicesIP:
							## check if we need to reset suspend after 300 secs
							if (time.time() - self.suspendedUnifiSystemDevicesIP[ipN] >10 and self.checkPing(ipN,nPings=2,countPings =2, waitForPing=0.5, calledFrom=u"PeriodCheck") == 0) :
									self.delSuspend(ipN)
									lastUpTT = time.time()
									self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
									self.indiLOG.log(10,u"{} is back from suspended status".format(dev.name))
							else:
								if dev.states[u"status"] != u"susp":
									self.setImageAndStatus(dev, u"susp", oldStatus=dev.states[u"status"],ts=time.time(), fing=False, level=1, text1= u"{:30s}  status :{:10s};  set to suspend".format(dev.name, status), iType=u"PER-susp",reason=u"Period Check susp "+status)
									self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
									changed = True
								continue

						if self.useDBInfoForWhichDevices == "all" or (self.useDBInfoForWhichDevices == "perDevice" and u"useDBInfoForDownCheck" in props and props[u"useDBInfoForDownCheck"] == u"useDBInfo"):
							if time.time() -  self.MAC2INDIGO[xType][MAC][u"last_seen"] < max(99., expT):
								if self.MAC2INDIGO[xType][MAC][u"last_seen"]  > lastUpTT:
									if self.decideMyLog(u"DBinfo", MAC=MAC): self.indiLOG.log(10,u"overwriting lastUP w info from controllerdb {} {:28s}  lastTT:{:.0f},   new lastTT:{:.0f}".format(MAC, dev.name,  time.time() - lastUpTT, time.time() - self.MAC2INDIGO[xType][MAC][u"last_seen"] ))
									lastUpTT = self.MAC2INDIGO[xType][MAC][u"last_seen"]
						if self.decideMyLog(u"DBinfo", MAC=MAC): 
							self.indiLOG.log(10,u"checking    lastUP w info from controllerdb {} {:28s}  lastTT:{:.0f},  lastTT-db:{:.0f}".format(MAC, dev.name,  time.time() - lastUpTT, time.time() - self.MAC2INDIGO[xType][MAC][u"last_seen"] ))

						dt = time.time() - lastUpTT

						if u"useWhatForStatus" in props:
							if props[u"useWhatForStatus"].find(u"WiFi") > -1:
								suffixN = u"WiFi"

								######### do WOL / ping	  START ########################
								if u"useWOL" in props and props[u"useWOL"] !=u"0":
									if u"lastWOL" not in self.MAC2INDIGO[xType][MAC]:
										self.MAC2INDIGO[xType][MAC][u"lastWOL"]	= 0.
									if time.time() - self.MAC2INDIGO[xType][MAC][u"lastWOL"] > float(props[u"useWOL"]):
										if dt < expT:	# if UP do minimal broadcast
											waitBeforePing = 0 # do a quick ping
											waitForPing	   = 1 # mSecs =  do not wait
											nBC			   = 1 # # of broadcasts
											nPings		   = 0
											waitAfterPing  = 0.0
										elif dt < 2*expT:			# if down wait between BC and ping,	 wait for ping to answer and do 2 BC
											waitBeforePing = 0.3 # secs
											waitForPing	   = 500 # msecs
											waitAfterPing  = 0.3
											nBC			   = 2
											nPings		   = 2
										else:					   # expired, do a quick bc
											waitBeforePing = 0.0 # secs
											waitForPing	   = 10 # msecs
											nBC			   = 1
											nPings		   = 0
											waitAfterPing  = 0.0
										if self.sendWakewOnLanAndPing( MAC, ipN, nBC=nBC, waitForPing=waitForPing, countPings=1, waitAfterPing=waitAfterPing, waitBeforePing=waitBeforePing, nPings=nPings, calledFrom=u"periodCheck") ==0:
											lastUpTT = time.time()
											lastUpTTFastDown = time.time()
											self.MAC2INDIGO[xType][MAC][u"lastUp"] = lastUpTT
										self.MAC2INDIGO[xType][MAC]["lastWOL"]	= time.time()
								######### do WOL / ping	  END  ########################
								dt = time.time() - lastUpTT

								if u"useWhatForStatusWiFi" not in props or	(u"useWhatForStatusWiFi" in props and props[u"useWhatForStatusWiFi"] != u"FastDown"):

									if (devid in self.upDownTimers	and time.time() -  self.upDownTimers[devid][u"down"] > expT ) or (dt > 1 * expT) :
										if	  dt <						 1 * expT: status = u"up"
										elif  dt <	self.expTimeMultiplier * expT: status = u"down"
										else :				  status = u"expired"
										if not self.expTimerSettingsOK("AP",MAC, dev): continue

										if status != u"up":
											if dev.states[u"status"] == u"up":
												if self.doubleCheckWithPing(status,dev.states[u"ipNumber"], props,dev.states[u"MAC"],u"Logic", u"Period check-WiFi", u"chk-Time",xType) ==0:
													status	= u"up"
													self.setImageAndStatus(dev, "up", oldStatus=dev.states[u"status"],ts=time.time(), fing=False, level=1, text1=  u"{:30s} status {:10s};   set to UP,  reset by ping ".format(dev.name, status), iType=u"PER-AP-Wi-0",reason=u"Period Check Wifi "+status)
													changed = True
													continue
												else:
													self.setImageAndStatus(dev, status, oldStatus=dev.states[u"status"],ts=time.time(), fing=True, level=1, text1= u"{:30s} status {:10s}; changed period WiFi, expT={:4.1f}     dt={:4.1f}".format(dev.name, status, expT, dt), iType=u"PER-AP-Wi-1",reason=u"Period Check Wifi "+status)
													changed = True
													continue

											if dev.states[u"status"] == u"down" and status !=u"down": # to expired
													self.setImageAndStatus(dev, status, oldStatus=dev.states[u"status"],ts=time.time(), fing=True, level=1, text1= u"{:30s} status {:10s}; changed period WiFi, expT={:4.1f}     dt={:4.1f}".format(dev.name, status, expT, dt), iType=u"PER-AP-Wi-1",reason=u"Period Check Wifi "+status)
													changed = True
													continue

										else:
											if dev.states[u"status"] != status:
												if self.doubleCheckWithPing(status,dev.states[u"ipNumber"], props,dev.states[u"MAC"],u"Logic", u"Period check-WiFi", u"chk-Time",xType) !=0:
													pass
												else:
													changed = True
													status = u"up"
													self.setImageAndStatus(dev, status, oldStatus=dev.states[u"status"],ts=time.time(), fing=True, level=1, text1= u"{:30s} status {:10s}; changed period WiFi, expT={:4.1f}     dt={:4.1f}".format(dev.name, status, expT, dt), iType=u"PER-AP-Wi-1",reason=u"Period Check Wifi "+status)
												continue


								elif  (u"useWhatForStatusWiFi" in props and props[u"useWhatForStatusWiFi"] == u"FastDown") and dev.states[u"status"] == u"down" and (time.time() - lastUpTTFastDown > self.expTimeMultiplier * expT):
										if not self.expTimerSettingsOK("AP",MAC, dev): continue
										status = u"expired"
										changed = True
										#self.myLog( text=u" period "+ dev.name+u" changed: old status: "+dev.states[u"status"]+u"; new  "+status)
										self.setImageAndStatus(dev, status, oldStatus=dev.states[u"status"],ts=time.time(), fing=True, level=1, text1=u"{:30s} status {:10s}; changed period WiFi, expT={:4.1f}     dt={:4.1f}".format(dev.name, status, expT, dt), iType=u"PER-AP-Wi-2",reason=u"Period Check Wifi "+status)


							elif props[u"useWhatForStatus"] ==u"SWITCH":
								suffixN = u"SWITCH"
								dt = time.time() - lastUpTT
								if	 dt <  1 * expT:  status = u"up"
								elif dt <  2 * expT:  status = u"down"
								else :				  status = u"expired"
								if not self.expTimerSettingsOK("SW",MAC, dev): continue
								if dev.states[u"status"] != status:
									if status =="down" and self.doubleCheckWithPing(status,dev.states[u"ipNumber"], props,dev.states[u"MAC"],u"Logic", u"Period check-SWITCH", u"chk-Time",xType) ==0:
										status = u"up"
									if dev.states[u"status"] != status:
										changed = True
										self.setImageAndStatus(dev, status,oldStatus=dev.states[u"status"], ts=time.time(), fing=True, level=1, text1= u"{:30s} status {:10s}; changed period SWITCH, expT={:4.1f}     dt={:4.1f}".format(dev.name, status, expT, dt), iType=u"PER-SW-0",reason=u"Period Check SWITCH "+status)



							elif props[u"useWhatForStatus"].find(u"DHCP") > -1:
								suffixN = u"DHCP"
								dt = time.time() - lastUpTT
								if	 dt <  						1 * expT:  status = u"up"
								elif dt <  self.expTimeMultiplier * expT:  status = u"down"
								else :				  status = u"expired"
								if not self.expTimerSettingsOK("GW",MAC, dev): continue
								if dev.states[u"status"] != status:
									if status == "down" and self.doubleCheckWithPing(status,dev.states[u"ipNumber"], props,dev.states[u"MAC"],u"Logic", u"Period check-DHCP", u"chk-Time",xType) ==0:
										status = u"up"
									if dev.states[u"status"] != status:
										changed = True
										self.setImageAndStatus(dev, status,oldStatus=dev.states[u"status"], ts=time.time(), fing=True, level=1, text1= u"{:30s} status {:10s}; changed period DHCP, expT={:4.1f}     dt= {:4.1f}".format(dev.name, status, expT, dt), iType=u"PER-DHCP-0",reason=u"Period Check DHCP "+status)


							else:
								dt = time.time() - lastUpTT
								if	 dt <  						1 * expT:  status = u"up"
								elif dt <  self.expTimeMultiplier * expT:  status = u"down"
								else			   :  status = u"expired"
								if dev.states[u"status"] != status:
									if status =="down" and self.doubleCheckWithPing(status,dev.states[u"ipNumber"], props,dev.states[u"MAC"],u"Logic", u"Period check-default", u"chk-Time",xType) ==0:
										status = u"up"
									if dev.states[u"status"] != status:
										changed = True
										self.setImageAndStatus(dev, status,oldStatus=dev.states[u"status"], ts=time.time(), fing=True, level=1, text1= u"{:30s} status {:10s}; changed period regular expiration, expT{:4.1f}     dt={:4.1f}  useWhatForStatus else{}".format(dev.name, status, expT, dt,props[u"useWhatForStatus"]) , iType=u"PER-expire",reason=u"Period Check")
						continue


					elif dev.deviceTypeId == u"Device-AP":
						try:
							ipN = dev.states[u"ipNumber"]
							if ipN not in self.deviceUp[u"AP"]:
								continue
								#ipN = self.ipNumbersOf[u"AP"][int(dev.states[u"apNo"])]
								#dev.updateStateOnServer(u"ipNumber", ipN )
							if ipN in self.suspendedUnifiSystemDevicesIP:
								status = u"susp"
								self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
								dt	=99
								expT=999
							else:
								dt = time.time() - self.deviceUp[u"AP"][dev.states[u"ipNumber"]]
								if	 dt <  						1 * expT:  status = u"up"
								elif dt <  self.expTimeMultiplier * expT:  status = u"down"
								else :				  status = u"expired"
							if dev.states[u"status"] != status:
								if status =="down" and self.doubleCheckWithPing(status,dev.states[u"ipNumber"], props,dev.states[u"MAC"],u"Logic", u"Period check-dev-AP", "chk-Time",xType) ==0:
									status = u"up"
								if dev.states[u"status"] != status:
									changed = True
									self.setImageAndStatus(dev,status,oldStatus=dev.states[u"status"],ts=time.time(), fing=True, level=1, text1= u"{:30s} status {:10s}; changed period, expT={:4.1f}     dt= {:4.1f}".format(dev.name, status, expT, dt), reason=u"Period Check", iType=u"PER-DEV-AP")
						except	Exception, e:
							if unicode(e).find(u"None") == -1:
								self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
							continue

					elif dev.deviceTypeId.find(u"Device-SW") >-1:
						try:
							ipN = dev.states[u"ipNumber"]
							if ipN not in self.deviceUp[u"SW"]:
								ipN = self.ipNumbersOf[u"SW"][int(dev.states[u"switchNo"])]
								dev.updateStateOnServer(u"ipNumber", ipN )
							if ipN in self.suspendedUnifiSystemDevicesIP:
								self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
								status = u"susp"
								dt =99
								expT=999
							else:

								dt = time.time() - self.deviceUp[u"SW"][ipN]
								if	 dt < 						1 * expT: status = u"up"
								elif dt < self.expTimeMultiplier  * expT: status = u"down"
								else:				status = u"expired"
							if dev.states[u"status"] != status:
								if status ==u"down" and self.doubleCheckWithPing(status,dev.states[u"ipNumber"], props,dev.states[u"MAC"],u"Logic", u"Period check-dev-SW", u"chk-Time",xType) ==0:
									status = u"up"
								if dev.states[u"status"] != status:
									changed = True
									self.setImageAndStatus(dev,status,oldStatus=dev.states[u"status"],ts=time.time(), fing=True, level=1, text1=u"{:30s} status {:10s}; changed period, expT={:4.1f}     dt= {:4.1f}".format(dev.name, status, expT, dt),reason=u"Period Check", iType=u"PER-DEV-SW")
						except	Exception, e:
							if unicode(e).find(u"None") == -1:
								self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
							continue


					elif dev.deviceTypeId == u"neighbor":
						try:
							dt = time.time() - lastUpTT
							if	 dt < 						1 * expT: status = u"up"
							elif dt < self.expTimeMultiplier  * expT: status = u"down"
							else:				status = u"expired"
							if dev.states[u"status"] != status:
									changed=True
									self.setImageAndStatus(dev,status,oldStatus=dev.states[u"status"],ts=time.time(), fing=self.ignoreNeighborForFing, level=1, text1=u"{:30s} status {:10s}; changed period, expT={:4.1f}     dt= {:4.1f}".format(dev.name, status, expT, dt),reason=u"Period Check other", iType=u"PER-DEV-NB")
						except	Exception, e:
							if unicode(e).find(u"None") == -1:
								self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
							continue
					else:
						try:
							dt = time.time() - lastUpTT
							if dt < 1 * expT:	status = u"up"
							elif dt < 2 * expT: status = u"down"
							else:				status = u"expired"
							if dev.states[u"status"] != status:
								if status =="down" and self.doubleCheckWithPing(status,dev.states[u"ipNumber"], props,dev.states[u"MAC"],u"Logic", u"Period check-def", u"chk-Time",xType) ==0:
									status = u"up"
								if dev.states[u"status"] != status:
									changed=True
									self.setImageAndStatus(dev,status, oldStatus=dev.states[u"status"],ts=time.time(), fing=True, level=1, text1=u"{:30s} status {:10s}; changed period, expT={:4.1f}     dt= {:4.1f}  devtype else:{}".format(dev.name, status, expT, dt,dev.deviceTypeId),reason=u"Period Check other", iType=u"PER-DEV-exp")

						except:
							continue

					self.lastSecCheck = time.time()
				except	Exception, e:
					if unicode(e).find(u"None") == -1:
						self.indiLOG.log(40,u"in Line {} has error={}\nlooking at device:  {}".format(sys.exc_traceback.tb_lineno, e, dev.name))


		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return	changed





	###########################	   UTILITIES  #### START #################

	### reset exp timer if it is shorter than the device exp time
	####-----------------	 ---------
	def expTimerSettingsOK(self, xType, MAC,	dev):
		try:
			if not self.fixExpirationTime: 		return True
			props = dev.pluginProps
			if u"expirationTime" not in props:	return True

			if float(self.readDictEverySeconds[xType]) <  float(props[u"expirationTime"]): return True
			newExptime	= float(self.readDictEverySeconds[xType])+10
			self.indiLOG.log(10,u"checking expiration timer settings {} updating exptime for {} to {} as it is shorter than reading dicts: {}+10".format(MAC, dev.name, newExptime, self.readDictEverySeconds[xType]))
			props[u"expirationTime"] = newExptime
			dev.replacePluginPropsOnServer(props)
			return False

		except	Exception, e:
			self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return True

	###	 kill expect pids if running
	####-----------------	 ---------
	def killIfRunning(self,ipNumber,expectPGM):
		cmd = "ps -ef | grep '/uniFiAP.' | grep "+self.expectPath+" | grep -v grep"
		if  expectPGM !="":		cmd += " | grep '" + expectPGM + "' "
		if  ipNumber != "":		cmd += " | grep '" + ipNumber  + " ' "  # add space at end of ip# for search string

		if self.decideMyLog(u"Expect"): self.indiLOG.log(10,u"killing request, get list with: "+cmd)
		ret = subprocess.Popen( cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0]

		if len(ret) < 5:
			return

		lines = ret.split("\n")
		for line in lines:
			if len(line) < 5:
				continue

			items = line.split()
			if len(items) < 5:
				continue

			pid = items[1]
			try:
				if int(pid) < 100: continue # don't mess with any system processes
				ret = subprocess.Popen("/bin/kill -9  " + pid, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
				if self.decideMyLog(u"Expect"): self.indiLOG.log(10,u"killing expect "+expectPGM+" w ip# " +ipNumber +"    "  +pid+":\n"+line )
			except:
				pass

		return

	####-----------------	 ---------
	def killPidIfRunning(self,pid):
		cmd = "ps -ef | grep '/uniFiAP.' | grep "+self.expectPath+" | grep "+unicode(pid)+" | grep -v grep"

		if self.decideMyLog(u"Expect"): self.indiLOG.log(10,u"killing request,  for pid: "+unicode(pid))
		ret = subprocess.Popen( cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0]

		if len(ret) < 5:
			return

		lines = ret.split("\n")
		for line in lines:
			if len(line) < 5:
				continue

			items = line.split()
			if len(items) < 5:
				continue

			pidInLine = items[1]
			try:
				if int(pidInLine) != int(pid): continue # don't mess with any system processes
				ret = subprocess.Popen("/bin/kill -9  " + pidInLine, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
				if self.decideMyLog(u"Expect"): self.indiLOG.log(10,u"killing expect "  +pidInLine+":\n"+line )
			except:
				pass
			break

		return

	### test if AP are up, first ping then check if expect is running
	####-----------------	 ---------
	def testAPandPing(self,ipNumber, cType):
		try:
			if self.decideMyLog(u"Expect"): self.indiLOG.log(10,u"CONNtest  testing if {} {} {} is running ".format(ipNumber, self.expectPath,self.connectParams[u"expectCmdFile"][cType]))
			if os.path.isfile(self.pathToPlugin +self.connectParams[u"expectCmdFile"][cType]):
				if self.decideMyLog(u"Expect"): self.indiLOG.log(10,u"CONNtest {} exists, now doing ping" .format(self.connectParams[u"expectCmdFile"][cType]))
			if self.checkPing(ipNumber, nPings=2, waitForPing=1000, calledFrom=u"testAPandPing", verbose=True) !=0:
				if self.decideMyLog(u"Expect"): self.indiLOG.log(10,u"CONNtest  ping not returned" )
				return False

			cmd = "ps -ef | grep " +self.connectParams[u"expectCmdFile"][cType]+ "| grep " + ipNumber + " | grep "+self.expectPath+" | grep -v grep"
			if self.decideMyLog(u"Expect"): self.indiLOG.log(10,u"CONNtest  check if pgm is running {}".format(cmd) )
			ret = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[0]
			if self.decideMyLog(u"ExpectRET"): self.indiLOG.log(10,"returned from expect-command: {}".format(ret[0]))
			if len(ret) < 5: return False
			lines = ret.split("\n")
			for line in lines:
				if len(line) < 5:
					continue

				##self.myLog( text=line )
				items = line.split()
				if len(items) < 5:
					continue

				if self.decideMyLog(u"Expect"): self.indiLOG.log(10,u"CONNtest  expect is running" )
				return True

			if self.decideMyLog(u"Expect"): self.indiLOG.log(10,u"CONNtest  {}    {}is NOT running".format(cType, ipNumber) )
			return False
		except	Exception, e:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))




	####-----------------	 --------- 
	### init,save,write data stats for receiving messages
	def addTypeToDataStats(self,ipNumber, apN, uType):
		try:
			if uType not in self.dataStats[u"tcpip"]:
				self.dataStats[u"tcpip"][uType]={}
			if ipNumber not in self.dataStats[u"tcpip"][uType]:
				self.dataStats[u"tcpip"][uType][ipNumber]={u"inMessageCount":0,u"inMessageBytes":0,u"inErrorCount":0,u"restarts":0,u"inErrorTime":0,u"startTime":time.time(),u"APN":unicode(apN), u"aliveTestCount":0}
			if u"inErrorTime" not in self.dataStats[u"tcpip"][uType][ipNumber]:
				self.dataStats[u"tcpip"][uType][ipNumber][u"inErrorTime"] = 0
		except	Exception, e:
			self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
	####-----------------	 ---------
	def zeroDataStats(self):
		for uType in self.dataStats[u"tcpip"]:
			for ipNumber in self.dataStats[u"tcpip"][uType]:
				self.dataStats[u"tcpip"][uType][ipNumber][u"inMessageCount"]	= 0
				self.dataStats[u"tcpip"][uType][ipNumber][u"inMessageBytes"]	= 0
				self.dataStats[u"tcpip"][uType][ipNumber][u"aliveTestCount"]	= 0
				self.dataStats[u"tcpip"][uType][ipNumber][u"inErrorCount"]		= 0
				self.dataStats[u"tcpip"][uType][ipNumber][u"restarts"]			= 0
				self.dataStats[u"tcpip"][uType][ipNumber][u"startTime"]			= time.time()
				self.dataStats[u"tcpip"][uType][ipNumber][u"inErrorTime"]		= 0
		self.dataStats[u"updates"]={u"devs":0,u"states":0,u"startTime":time.time()}
	####-----------------	 ---------
	def resetDataStats(self, calledFrom=""):
		indigo.server.log(u" resetDataStats called from {}".format(calledFrom) )
		self.dataStats={u"tcpip":{},u"updates":{u"devs":0,u"states":0,u"startTime":time.time()}}
		self.saveDataStats()

	####-----------------	 ---------
	def saveDataStats(self):
		if time.time() - 60	 < self.lastSaveDataStats: return
		self.lastSaveDataStats = time.time()
		self.writeJson(self.dataStats, fName=self.indigoPreferencesPluginDir+"dataStats", sort=False, doFormat=True )

	####-----------------	 ---------
	def readDataStats(self):
		self.lastSaveDataStats	= time.time() -60
		try:
			f=open(self.indigoPreferencesPluginDir+"dataStats","r")
			self.dataStats = json.loads(f.read())
			f.close()
			if u"tcpip" not in self.dataStats:
				self.resetDataStats( calledFrom="readDataStats 1")
			return
		except: pass

		self.resetDataStats( calledFrom="readDataStats 2")
		return
	### init,save,write data stats for receiving messages
	####-----------------	 --------- END


	####------ camera  ---	-------START
	def resetCamerasStats(self):
		self.cameras={}
		self.saveCameraEventsStatus = True
		self.saveCameraEventsLastCheck = 0
		self.saveCamerasStats()

	####-----------------	 ---------
	def saveCamerasStats(self,force=False):
		if	not self.saveCameraEventsStatus: return

		if self.saveCameraEventsStatus == True:
			self.saveCameraEventsLastCheck = 0

		# check if we have deleted devices in cameras
		if time.time() - self.saveCameraEventsLastCheck > 500 or force:

			cameraMacList ={}
			for dev in indigo.devices.iter(u"props.isCamera"):
				cameraMacList[dev.states[u"MAC"]] = dev.id

			delList ={}
			for MAC in self.cameras:
				if MAC not in cameraMacList:
					delList[MAC]=True
			for MAC in delList:
				self.cameras[MAC][u"devid"]=-1

			self.saveCameraEventsLastCheck = time.time()

		# save cameras to disk
		self.writeJson( self.cameras, fName=self.indigoPreferencesPluginDir+"CamerasStats",  sort=True, doFormat=True )
		self.saveCameraEventsStatus = False

	####-----------------	 ---------
	def readCamerasStats(self):
		try:
			f=open(self.indigoPreferencesPluginDir+"CamerasStats","r")
			self.cameras = json.loads(f.read())
			f.close()
			self.saveCameraEventsStatus = True
			self.saveCamerasStats()
			return
		except: pass

		self.resetCamerasStats()
		return


	####-----------------	 ---------
	def getIfinDict(self,inDict, inText, default=""):
		if inText not in inDict: return default
		return inDict[inText]

	####------ camera PROTEC ---	-------END

	####------ camera NVR ---	-------START

	####-----------------	 ---------
	def getNVRCamerastoIndigo(self, force = False, periodCheck = False):
		try:
			if periodCheck: test = 300
			else:			test = 30
			if time.time() - self.lastCheckForCAMERA < test and not force: return
			self.lastCheckForCAMERA = time.time()
			timeElapsed = time.time()
			if self.cameraSystem != "nvr":					return
			if not self.isValidIP(self.ipNumbersOf[u"VD"]): return
			info = self.getNVRCamerasFromMongoDB(action=["cameras"])
			if len(info) < 1:
				self.sleep(1)
				info = self.getNVRCamerasFromMongoDB(action=["cameras"])

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

	####-----------------	 ---------
	def getNVRIntoIndigo(self,force= False):
		try:
			if time.time() - self.lastCheckForNVR < 451 and not force: return
			self.lastCheckForNVR = time.time()
			if not self.isValidIP(self.ipNumbersOf[u"VD"]): return
			if self.cameraSystem != "nvr":			   		return


			info =self.getNVRCamerasFromMongoDB( action=["system"])

			if len(info["NVR"]) < 2:
				for dev in indigo.devices.iter(u"props.isNVR"):
					self.updateStatewCheck(dev,u"status", u"down")
					self.executeUpdateStatesList()
					break
				return

			NVR = info["NVR"]
			ipNumber =""
			UnifiDevice = ""
			UnifiMAC	= ""
			UnifiName	= ""
			memoryUsed	= ""
			dirName		= ""
			diskUsed	= ""
			diskFree	= ""
			rtmpsPort	= "off"
			rtspPort	= "off"
			rtmpPort	= "off"
			diskUsed	= ""
			diskAvail	= ""
			diskUsed	= ""
			cpuLoad		= ""
			apiKey		= ""
			apiAccess	= False
			upSince		= ""
			MAC			= ""


			if u"host"				in NVR:								  ipNumber			= NVR[u"host"]
			if u"uptime"			in NVR:								  upSince			= time.strftime( u'%Y-%m-%d %H:%M:%S', time.localtime(float(NVR[u"uptime"])/1000) )

			if u"systemInfo"	   in NVR:
				if u"nics"		   in NVR["systemInfo"]:
					for nic		   in NVR["systemInfo"]["nics"]:
						if u"ip"	   in nic:							  ipNumber			= nic["ip"]
						if u"mac"   in nic:								  MAC				= nic[u"mac"].lower()
				if u"memory"	 in NVR["systemInfo"]:
						if u"total" in NVR["systemInfo"]["memory"]:		  memoryUsed		= "%d/%d"%( float(NVR[u"systemInfo"]["memory"]["used"])/(1024*1024), float(NVR["systemInfo"]["memory"]["total"])/(1024*1024) )+"[GB]"
				if u"cpuLoad"	 in NVR["systemInfo"]:					  cpuLoad			= "%.1f"%( float(NVR[u"systemInfo"]["cpuLoad"]))+"[%]"
				if u"disk"		 in NVR["systemInfo"]:
						if u"dirName"	 in NVR["systemInfo"]["disk"]:	  dirName			= NVR["systemInfo"]["disk"]["dirName"]
						if u"availKb"	 in NVR["systemInfo"]["disk"]:	  diskAvail			= "%d"%( float(NVR["systemInfo"]["disk"]["availKb"])/(1024*1024) )+"[GB]"
						if u"usedKb"		 in NVR["systemInfo"]["disk"]:diskUsed			= "%d/%d"%( float(NVR["systemInfo"]["disk"]["usedKb"])/(1024*1024) , float(NVR["systemInfo"]["disk"]["totalKb"])/(1024*1024) )	+"[GB]"

			if"livePortSettings"		 in NVR:
				if u"rtmpEnabled"		 in NVR["livePortSettings"]:
						if NVR["livePortSettings"]["rtmpEnabled"]:		  rtmpPort			=  unicode( NVR[u"livePortSettings"]["rtmpPort"] )
				if u"rtmpsEnabled"		  in NVR["livePortSettings"]:
						if NVR["livePortSettings"]["rtmpsEnabled"]:		  rtmpsPort			=  unicode( NVR[u"livePortSettings"]["rtmpsPort"] )
				if u"rtspEnabled"		 in NVR["livePortSettings"]:
						if NVR["livePortSettings"]["rtspEnabled"]:		  rtspPort			=  unicode( NVR["livePortSettings"]["rtspPort"] )

			users = info["users"]

			for _id in users:
				if users[_id]["userName"] == self.connectParams[u"UserID"]["nvrWeb"]:
					if u"apiKey" in users[_id] and "enableApiAccess" in users[_id]:
						if users[_id]["enableApiAccess"] :
							apiKey		= users[_id]["apiKey"]
							apiAccess 	= users[_id]["enableApiAccess"]


			UnifiName	= ipNumber
			for dev in indigo.devices.iter(u"props.isUniFi"):
				if dev.states[u"ipNumber"] == ipNumber and MAC == dev.states[u"MAC"]:
					UnifiName	= dev.name
					break


			dev = ""
			for dd in indigo.devices.iter(u"props.isNVR"):
				dev = dd
				break

			if dev =="":
				if UnifiName != "": useName= UnifiName
				elif UnifiMAC !="": useName= UnifiMAC
				else:				useName= ipNumber+unicode(int(time.time()))

				dev = indigo.device.create(
					protocol =		 indigo.kProtocol.Plugin,
					address =		 UnifiMAC,
					name =			 "NVR_" + useName,
					description =	 self.fixIP(ipNumber),
					pluginId =		 self.pluginId,
					deviceTypeId =	 "NVR",
					folder =		 self.folderNameIDSystemID,
					props =			 {"isNVR":True})

			self.updateStatewCheck(dev,"status",		"up")
			self.updateStatewCheck(dev,"ipNumber",		ipNumber)
			self.updateStatewCheck(dev,"memoryUsed",	memoryUsed)
			self.updateStatewCheck(dev,"dirName",		dirName)
			self.updateStatewCheck(dev,"diskUsed",		diskUsed)
			self.updateStatewCheck(dev,"diskAvail",		diskAvail)
			self.updateStatewCheck(dev,"rtmpPort",		rtmpPort)
			self.updateStatewCheck(dev,"rtmpsPort",		rtmpsPort)
			self.updateStatewCheck(dev,"rtspPort",		rtspPort)
			self.updateStatewCheck(dev,"cpuLoad",		cpuLoad)
			self.updateStatewCheck(dev,"apiKey",		apiKey)
			self.updateStatewCheck(dev,"apiAccess",		apiAccess)
			self.updateStatewCheck(dev,"upSince",		upSince)

			self.pluginPrefs["nvrVIDEOapiKey"]		  	= apiKey
			self.nvrVIDEOapiKey						  	= apiKey

			self.executeUpdateStatesList()

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))


	####-----------------	 ---------
	def fillCamerasIntoIndigo(self,camJson, calledFrom=""):
		try:
			## self.myLog( text=u"fillCamerasIntoIndigo called from: "+calledFrom)
			if len(camJson) < 1: return
			saveCam= False
			for cam2 in camJson:
				if u"mac" in cam2:
					c = cam2[u"mac"]
					MAC = c[0:2]+":"+c[2:4]+":"+c[4:6]+":"+c[6:8]+":"+c[8:10]+":"+c[10:12]
					MAC = MAC.lower()

					skip = ""
					if self.testIgnoreMAC(MAC, fromSystem="fillCam"):
						skip = "MAC in ignored List"
					else:
						if u"authStatus" in cam2 and cam2["authStatus"] != "AUTHENTICATED":
							skip += "authStatus: !=AUTHENTICATED;"
						if u"managed" in cam2 and not cam2["managed"]:
							skip += " .. != managed;"
						if u"deleted" in cam2 and  cam2["deleted"]:
							skip += " deleted"
						if skip !="":
							if self.decideMyLog(u"Video"): self.indiLOG.log(10,u"skipping camera with MAC # "+MAC +"; because : "+ skip)
					if skip !="":
						continue

					found = False
					for cam in self.cameras:
						if MAC == cam:
							self.cameras[MAC]["uuid"]		= cam2["uuid"]
							self.cameras[MAC]["ip"]			= cam2["host"]
							self.cameras[MAC]["apiKey"]		= cam2["_id"]
							self.cameras[MAC]["nameOnNVR"]	= cam2[u"name"]
							found = True
							break
					if not found:
						saveCam = True
						self.cameras[MAC]= {"nameOnNVR":cam2[u"name"], u"events":{}, u"eventsLast":{u"start":0,u"stop":0},u"devid":-1, u"uuid":cam2[u"uuid"], "ip":cam2[u"host"], u"apiKey":cam2[u"_id"]}

					devFound = False
					if u"devid" in self.cameras[MAC]:
						try:
							dev = indigo.devices[self.cameras[MAC][u"devid"]]
							devFound = True
						except: pass

					if	not devFound:
						for dev in indigo.devices.iter(u"props.isCamera"):
							if u"MAC" not in dev.states:	   continue
							if dev.states[u"MAC"] == MAC:
								devFound = True
								break
					if not devFound:
						try:
							dev = indigo.device.create(
								protocol		=indigo.kProtocol.Plugin,
								address			=MAC,
								name 			= "Camera_"+self.cameras[MAC]["nameOnNVR"]+"_"+MAC ,
								description		="",
								pluginId		=self.pluginId,
								deviceTypeId	=u"camera",
								props			={"isCamera":True},
								folder			=self.folderNameIDSystemID
								)
							indigo.variable.updateValue(u"Unifi_New_Device",u"{}/{}/{}".format(dev.name, MAC, cam2["host"]) )
						except	Exception, e:
							if unicode(e).find(u"NameNotUniqueError") >-1:
								dev 				= indigo.devices["Camera_"+self.cameras[MAC]["nameOnNVR"]+"_"+MAC]
								props 				= dev.pluginProps
								props[u"isCamera"] 	= True
								dev.replacePluginPropsOnServer()
								dev 				= indigo.devices[dev.id]
							else:
								if unicode(e).find(u"None") == -1:
									self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
								continue
					saveCam or self.updateStatewCheck(dev,u"MAC",			MAC)
					saveCam or self.updateStatewCheck(dev,u"apiKey",		self.cameras[MAC]["apiKey"])
					saveCam or self.updateStatewCheck(dev,u"uuid",		 	self.cameras[MAC]["uuid"])
					saveCam or self.updateStatewCheck(dev,u"ip",			self.cameras[MAC]["ip"])
					saveCam or self.updateStatewCheck(dev,u"nameOnNVR",	 	self.cameras[MAC]["nameOnNVR"])
					saveCam or self.updateStatewCheck(dev,u"eventNumber",	 -1,					check="", NotEq=True)
					saveCam or self.updateStatewCheck(dev,u"status",		"ON",					check="", NotEq=True)
					self.executeUpdateStatesList()
					if not devFound:
						dev = indigo.devices[dev.id]

			if saveCam:
				self.pendingCommand.append("saveCamerasStats")


		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))



	####-----------------	 ---------
	def getNVRCamerasFromMongoDB(self, doPrint = False, action=[]):
		try:
			timeElapsed = time.time()
			info	= {u"users":{}, u"cameras":[], u"NVR":{}}
			USERs	= []
			ACCOUNTs= []
			cmdstr	= ["\"mongo 127.0.0.1:7441/av --quiet --eval  'db.", ".find().forEach(printjsononeline)'  | sed 's/^\s*//' \"" ]

			#self.indiLOG.log(10," into getNVRCamerasFromMongoDB action :{}".format(action))
			if u"system" in action:
				USERs			= self.getMongoData(cmdstr[0]+u"user"   +cmdstr[1])
				ACCOUNTs		= self.getMongoData(cmdstr[0]+u"account"+cmdstr[1])

				if len(USERs)>0 and len(ACCOUNTs) >0:
					for account in ACCOUNTs:
						##self.myLog( text="getNVRCamerasFromMongoDB account dict: "+unicode(account))
						if u"_id" in account and u"username" in account and u"name" in account:
							ID =  account[u"_id"]
							info[u"users"][ID] ={u"userName":account[u"username"], u"name":account[u"name"]}
							for user in USERs:
								##self.myLog( text="getNVRCamerasFromMongoDB user dict: "+unicode(user))
								if u"accountId" in user and ID == user[u"accountId"]:
									##self.myLog( text="getNVRCamerasFromMongoDB accountId ok and id found:"+ID)
									if u"apiKey" in user and u"enableApiAccess" in user:
										##self.myLog( text="getNVRCamerasFromMongoDB apiKey found <<"+ user["apiKey"]+"<<    enableApiAccess>>"+unicode(user["enableApiAccess"]))
										info[u"users"][ID][u"apiKey"]			= user[u"apiKey"]
										info[u"users"][ID][u"enableApiAccess"]	= user[u"enableApiAccess"]
									else:
										if u"enableApiAccess" in user and user[u"enableApiAccess"]: # its enabled, but no api key
											self.indiLOG.log(40,u"getNVRCamerasFromMongoDB camera users   bad enableApiAccess / apiKey info for id:{}\n{} UNIFI error".format(ID, USERs))
										else:
											if self.decideMyLog(u"Video"): self.indiLOG.log(10,u"UNIFI error  getNVRCamerasFromMongoDB camera users   enableApiAccess disabled info for id:{}\n{}".format(ID, USERs))
						else:
										self.indiLOG.log(40,u"getNVRCamerasFromMongoDB camera ACCOUNT bad _id / username / name info:\n{}".format(ACCOUNTs))

				server = self.getMongoData(cmdstr[0]+u"server" +cmdstr[1])
				if len(server) >0:
					info[u"NVR"]		= server[0]

			#self.indiLOG.log(10," into getNVRCamerasFromMongoDB info :{}".format(info))
			if u"cameras" in action:
				info[u"cameras"]	 = self.executeCMDonNVR( {}, "",  cmdType=u"get")
				if len(info[u"cameras"]) <1:
					info[u"cameras"] = self.getMongoData(cmdstr[0]+u"camera" +cmdstr[1])
				if len(info[u"cameras"]) >0: self.fillCamerasIntoIndigo(info[u"cameras"], calledFrom=u"getNVRCamerasFromMongoDB")


			##self.myLog( text=unicode(info))

			if doPrint:
				self.printNVRCameras(info)
			return info


		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return {}

	####-----------------	 ---------
	def printNVRCameras(self, info):
		keepList = [u"name",u"uuid",u"host",u"model",u"_id",u"firmwareVersion",u"systemInfo",u"mac",u"controllerHostAddress",u"controllerHostPort",u"deviceSettings",u"networkStatus",u"status",u"analyticsSettings",u"channels",u"ispSettings" ]
		out = u""
		try:
			if u"NVR" in info:
				self.myLog( text=u"--====================++++++++++++++++++++++++++++++++++++++++====================--",mType=u"System info-NVR:")
				for key in info[u"NVR"]:
					self.myLog( text=unicode(info[u"NVR"][key]),mType=u"  "+key )

				self.myLog( text=u"---====================++++++++++++++++++++++++++++++++++++++++====================--", mType=u"== System info- users:")
			if u"users" in info:
				nn = 0
				for user in info[u"users"]:
					out = ""
					for item in ["name","apiKey","enableApiAccess"] :
						out+=(item+":"+unicode(info["users"][user][item])+"; ").ljust(30)
					self.myLog( text=out.strip("; "),mType= (info[u"users"][user][u"userName"]).ljust(18)+u" # "+ unicode(nn))
					nn+=1


			if u"cameras" in info:
				self.myLog( text=u"---====================++++++++++++++++++++++++++++++++++++++++====================--", mType=u"== System info- cameras:")
				for camera in info[u"cameras"]:
					self.myLog( text=u"--===============--" , mType=camera[u"name"])
					for item in camera:
						if item ==u"name": continue
						if item in keepList or keepList == [u"*"]:
							if item == u"channels":
								nn = 0
								for channel in camera[item]:
									out = (u"bitrates: "+unicode(channel[u"minBitrate"])+".."+unicode(channel[u"maxBitrate"])) .ljust(30)
									for	 prop in [u"enabled",u"isRtmpsEnabled",u"isRtspEnabled"]:
										if prop in channel:
											out+= prop+u": "+unicode(channel[prop])+u";  "
									out = out.strip(";....")
									self.myLog( text=out, mType=u"              channel#"+unicode(nn) )
									nn+=1
							elif item == "status":
								status = camera[item]
								out = ""
								for	 prop in [u"remotePort",u"remoteHost"]:
									if prop in status:
										out+= prop+":"+unicode(status[prop])+u"; "
								out = out.strip("; ")
								self.myLog( text=out, mType=u"              status" )
								for nn in range(len(status[u"recordingStatus"])):
									out	 =	(u"motionRecordingEnabled: "+unicode(status[u"recordingStatus"][unicode(nn)][u"motionRecordingEnabled"])).ljust(30)
									out += u"; fullTimeRecordingEnabled: "+unicode(status[u"recordingStatus"][unicode(nn)][u"fullTimeRecordingEnabled"])
									self.myLog( text=out, mType=u"           recordingSt:#"+unicode(nn) )
							else:
								self.myLog( text=(item+":").ljust(25)+json.dumps(camera[item]) )

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}\n printNVRCameras system info:\n{}".format(sys.exc_traceback.tb_lineno, e, json.dumps(out,sort_keys=True, indent=2)) )
		return



	####------ camera NVR ----------END



	####-----------------	 ---------
	def updateStatewCheck(self,dev, state , value, check = "", NotEq = False):
		if state not in dev.states:		   return False
		if NotEq:
			if dev.states[state] != check: return False
		else:
			if state == check:			   return False
		if dev.states[state]  ==  value:   return False
		self.addToStatesUpdateList(dev.id,state,  value )
		return True




	####-----------------	 -----------
	### ----------- save read MAC2INDIGO
	def saveMACdata(self, force=False):
		if not force and  (time.time() - 20 < self.lastSaveMAC2INDIGO): return
		self.lastSaveMAC2INDIGO = time.time()
		self.writeJson(self.MAC2INDIGO, fName=self.indigoPreferencesPluginDir+"MAC2INDIGO", doFormat=True )
		self.writeJson(self.MACignorelist, fName=self.indigoPreferencesPluginDir+"MACignorelist", doFormat=True )
		self.writeJson(self.MACSpecialIgnorelist, fName=self.indigoPreferencesPluginDir+"MACSpecialIgnorelist", doFormat=True )

	####-----------------	 ---------
	def readMACdata(self):
		self.lastSaveMAC2INDIGO	 = time.time() -21
		try:
			f=open(self.indigoPreferencesPluginDir+"MAC2INDIGO","r")
			self.MAC2INDIGO= json.loads(f.read())
			f.close()
		except:
			self.MAC2INDIGO= {"UN":{},u"GW":{},u"SW":{},u"AP":{},u"NB":{}}
		try:
			f=open(self.indigoPreferencesPluginDir+"MACignorelist","r")
			self.MACignorelist= json.loads(f.read())
			f.close()
		except:
			self.MACignorelist ={}
		try:
			f=open(self.indigoPreferencesPluginDir+"MACSpecialIgnorelist","r")
			self.MACSpecialIgnorelist= json.loads(f.read())
			f.close()
		except:
			self.MACSpecialIgnorelist ={}
		return
	### ----------- save read MAC2INDIGO
	####-----------------	 -----------   END


	####-----------------	 -----------   START
	### ----------- manage suspend status
	def setSuspend(self,ip,tt):
		self.suspendedUnifiSystemDevicesIP[ip] = tt
		self.writeSuspend()
	####-----------------	 ---------
	def delSuspend(self,ip):
		if ip in self.suspendedUnifiSystemDevicesIP:
			del self.suspendedUnifiSystemDevicesIP[ip]
			self.writeSuspend()
	####-----------------	 ---------
	def writeSuspend(self):
		try:
			self.writeJson(self.suspendedUnifiSystemDevicesIP, fName=self.indigoPreferencesPluginDir+"suspended", sort=False, doFormat=False)
		except: pass
	####-----------------	 ---------
	def readSuspend(self):
		self.suspendedUnifiSystemDevicesIP={}
		try:
			f=open(self.indigoPreferencesPluginDir+"suspended","r")
			self.suspendedUnifiSystemDevicesIP = json.loads(f.read())
			f.close()
		except: pass
	### ----------- manage suspend status
	####-----------------	 -----------   END



	### here we do the work, setup the logfiles listening and read the logfiles and check if everything is running

	### UDM log tracking
	####-----------------	 ---------
	def controllerWebApilogForUDM(self, dummy):

		try:
			lastRecordTime	= 0
			lastRead   		= 0
			self.indiLOG.log(10,u"ctlWebUDM: launching web log get for runs every {} secs".format(self.controllerWebEventReadON) )
			nRecordsToRetriveDefault 	= 25
			lastRecIds					= []
			thisRecIds					= []
			lastRecIdFound				= False
			lastTimeStamp				= time.time() - 500
			while self.pluginState != "stop":
				time.sleep(0.5)
				try:
					nrec = nRecordsToRetriveDefault
					if len(thisRecIds) > 0: 
						nrec = int( float(nRecordsToRetriveDefault * self.controllerWebEventReadON) / 30.)
					eventLogList 		= self.executeCMDOnController(dataSEND={"_sort":"+time", "_limit":min(500,max(10,nrec))}, pageString=u"/stat/event/", jsonAction=u"returnData", cmdType=u"post")
					#eventLogList 		= self.executeCMDOnController(dataSEND={}, pageString=u"/stat/event/", jsonAction=u"returnData", cmdType=u"get") 
					thisRecIds			= []
					# test if we have overlap. if not read 3 times the data 
					for logEntry in eventLogList:
						thisRecIds.append(logEntry["_id"])
						if lastRecIds !=[] and logEntry["_id"] in lastRecIds: 
							lastRecIdFound = True

					if not lastRecIdFound and lastRecIds !=[]:
						eventLogList 		= self.executeCMDOnController(dataSEND={"_sort":"+time", "_limit":min(500,max(10,nrec*3))}, pageString=u"/stat/event/", jsonAction=u"returnData", cmdType=u"post")
						thisRecIds			= []
						for logEntry in eventLogList:
							thisRecIds.append(logEntry["_id"])

					lastRead 			= time.time()
					ii = 0
					for logEntry in eventLogList[::-1]:
						ii +=1
						recId = logEntry["_id"]
						# do not reprocess old records
						if recId in lastRecIds: 										continue
						## filter out non AP info entries
						if u"time" not in logEntry: 									continue 
						# the time stamp from UFNI is in msecs, convert to float secs
						logEntry["time"] /= 1000. 
						# skip already processed records
						if logEntry["time"] < lastTimeStamp:							continue
						lastTimeStamp = logEntry["time"] 
						# remove junk
						if u"key" not in logEntry: 										continue
						if logEntry["key"].lower().find(u"login") >-1:					continue
						if u"user" not in logEntry: 									continue
						#
						MAC = logEntry["user"]
						if self.decideMyLog(u"UDM", MAC=MAC): self.indiLOG.log(10,u"ctlWebUDM  {}, rec#{} of {} recs; logEntry:{}".format(MAC, ii, len(thisRecIds), logEntry))

						# now we should have an ok event record
						apN 			= self.numberForUDM[u"AP"]
						ipNumberAP		= self.ipNumbersOf[u"AP"][apN]
						MAC_AP_Active 	= ""
						MAC_AP_from 	= ""

						# check if we have AP info, if not skip record
						if u"ap" in logEntry: 
							fromTo = ""
							MAC_AP_Active = logEntry[u"ap"]
							self.createAPdeviceIfNeededForUDM(MAC_AP_Active, logEntry,   fromTo)
							if self.MAC2INDIGO[u"AP"][MAC_AP_Active][u"ipNumber"] == "":
								self.indiLOG.log(10,u"ctlWebUDM  ap-mac:{}  MAC2INDIGO: has empty ipNumber, logEntry:{}".format(MAC_AP_Active, logEntry))
								continue
							#if self.MAC2INDIGO[u"AP"][MAC_AP_Active][u"ipNumber"] != self.ipNumbersOf[u"AP"][self.numberForUDM[u"AP"]]: continue  # ignore non UDM log entries 
						if u"ap_from" in logEntry: 
							fromTo = "_from"
							MAC_AP_from	= logEntry[u"ap"+fromTo]
							self.createAPdeviceIfNeededForUDM(MAC_AP_from, logEntry,   fromTo)
							if self.MAC2INDIGO[u"AP"][MAC_AP_from][u"ipNumber"] == "":
								self.indiLOG.log(10,u"ctlWebUDM  ap-mac:{}  MAC2INDIGO: has empty ipNumber, logEntry:{}".format(MAC_AP_from, logEntry))
								continue
							logEntry[u"IP_from"]	= self.MAC2INDIGO[u"AP"][MAC_AP_from][u"ipNumber"]
						if u"ap_to" in logEntry: 
							fromTo = "_to"
							MAC_AP_Active = logEntry[u"ap"+fromTo]
							self.createAPdeviceIfNeededForUDM(MAC_AP_Active, logEntry, fromTo)
							if self.MAC2INDIGO[u"AP"][MAC_AP_Active][u"ipNumber"] == "":
								self.indiLOG.log(10,u"ctlWebUDM  ap-mac:{}  MAC2INDIGO: has empty ipNumber, logEntry:{}".format(MAC_AP_Active, logEntry))
								continue
							logEntry[u"IP_to"] 	= self.MAC2INDIGO[u"AP"][MAC_AP_Active][u"ipNumber"]

						# for no ap log entry check if it about an existing devices, if yes: assign to UDM
						if MAC_AP_Active == "":
							if MAC in self.MAC2INDIGO[u"UN"]:
								for MACap in self.MAC2INDIGO[u"AP"]:
									if int(self.MAC2INDIGO[u"AP"][MACap][u"apNo"]) == int(self.numberForUDM[u"AP"]):
										MAC_AP_Active = MACap
										break
										# skip this event, not about existing wifi devices ...
						logEntry[u"MAC_AP_Active"] = MAC_AP_Active

						if MAC_AP_Active == "":
							if self.decideMyLog(u"UDM", MAC=MAC): self.indiLOG.log(10,u"ctlWebUDM  {}  ignoring: no 'ap': ..  given, logEntry:{}".format(MAC, logEntry))
							continue

						else:
							ipNumberAP = self.MAC2INDIGO[u"AP"][MAC_AP_Active][u"ipNumber"]
							for nn in range(_GlobalConst_numberOfAP):
								if ipNumberAP == self.ipNumbersOf[u"AP"][nn]: 
									apN	= nn
									break

						self.doAPmessages([logEntry], ipNumberAP, apN, webApiLog=True)
					lastRecIds = copy.copy(thisRecIds)
				except	Exception, e:
					self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
				for ii in range(100):
					if not lastRecIdFound: break
					if self.pluginState == "stop": break
					time.sleep(1)
					if time.time() - lastRead > self.controllerWebEventReadON: break
			self.indiLOG.log(10,u"ctlWebUDM: exiting plugin state = stop" )
		except	Exception, e:
			self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return 


	####----------------- thsi is for UDM devices only	 ---------
	def createAPdeviceIfNeededForUDM(self, MAC, line, fromTo):
		if MAC == "": 									return False
		if MAC in self.MAC2INDIGO[u"AP"]:				return True
		if self.unifiControllerType.find(u"UDM") == -1: 	return False

		self.indiLOG.log(30,u"==> new UDM device to be created, mac :{}  not in self.MAC2INDIGO[AP]{} ".format(MAC, self.MAC2INDIGO[u"AP"]))

		hostname	= "-UDM-AP"
		model		= "UDM-AP"
		tx_power	= "-99"
		GHz			= "2"
		essid		= ""
		channel		= ""
		radio 		= ""
		nClients	= ""
		devName		= "UDM-AP"
		xType		= "AP"
		isType 		= "isAP"
		if u"radio"+fromTo in line: radio = line[u"radio"+fromTo]
		if u"essid"+fromTo in line: essid = line[u"ssid"+fromTo]
		if u"channel"+fromTo in line: 
			if int(line[u"channel"+fromTo]) > 11: GHz = "5"
			else: 								 GHz = "2"
			channel = line[u"channel"+fromTo]
		try:
			ipNDevice = self.ipNumbersOf[u"AP"][self.numberForUDM[u"AP"]]
			dev = indigo.device.create(
				protocol		= indigo.kProtocol.Plugin,
				address 		= MAC,
				name 			= devName+"_" + MAC,
				description		= self.fixIP(ipNDevice) + hostname,
				pluginId 		= self.pluginId,
				deviceTypeId	= "Device-AP",
				folder			= self.folderNameIDCreated,
				props			= {u"useWhatForStatus":"",isType:True})
			self.setupStructures("AP", dev, MAC)
			self.setupBasicDeviceStates(dev, MAC, "AP", ipNDevice,"", "", u" status up            AP WEB  new AP", u"STATUS-AP")
			self.addToStatesUpdateList(dev.id,u"essid_" + GHz, essid)
			self.addToStatesUpdateList(dev.id,u"channel_" + GHz, channel)
			self.addToStatesUpdateList(dev.id,u"MAC", MAC)
			self.addToStatesUpdateList(dev.id,u"hostname", hostname)
			self.addToStatesUpdateList(dev.id,u"nClients_" + GHz, nClients)
			self.addToStatesUpdateList(dev.id,u"radio_" + GHz, radio)
			self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
			self.addToStatesUpdateList(dev.id,u"model", model)
			self.addToStatesUpdateList(dev.id,u"tx_power_" + GHz, tx_power)
			self.executeUpdateStatesList()
			indigo.variable.updateValue(u"Unifi_New_Device", u"{}/{}/{}".format(dev.name, MAC, ipNDevice) )
			dev = indigo.devices[dev.id]
			self.setupStructures(xType, dev, MAC)
			return True

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return False


	####-----------------	 ---------
	def getcontrollerDBForClients(self):
		try:
			if not self.devsEnabled[u"DB"]:																	return 
			if time.time() - self.getcontrollerDBForClientsLast < float(self.readDictEverySeconds[u"DB"]):	return 

			if self.decideMyLog(u"DBinfo"): self.indiLOG.log(10,u"getcontrollerDBForClients: start, read every:{}".format(self.readDictEverySeconds[u"DB"]))
			dataDict = self.executeCMDOnController(pageString=u"/stat/sta/", cmdType=u"get")
			if self.decideMyLog(u"DBinfo"): self.indiLOG.log(10,u"getcontrollerDBForClients: \n{} ...".format(unicode(dataDict)[0:500]) )

			self.fillcontrollerDBForClients(dataDict)
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

	####-----------------	 ---------
	def fillcontrollerDBForClients(self, dataDict):
		try:
			if len(dataDict) == 0: 
				self.getcontrollerDBForClientsLast = time.time() 
				return 

			xType = u"UN"
			macsFound = []
			anyChange = 0 
			secChange = 0 
			nClients = 0.
			for client in dataDict:
				if len(client) == 0: 					continue
				if u"mac" not in client: 				continue
				MAC = client[u"mac"]
				if MAC not in self.MAC2INDIGO[xType]: 	continue
				macsFound.append(MAC)
				nClients +=1.
				if u"first_seen" in client:
					try: 	self.MAC2INDIGO[xType][MAC][u"first_seen"]	= datetime.datetime.fromtimestamp(client[u"first_seen"]).strftime(u"%Y-%m-%d %H:%M:%S")
					except: pass

				if u"use_fixedip" in client:
					self.MAC2INDIGO[xType][MAC][u"use_fixedip"]	= client[u"use_fixedip"]
				else:
					self.MAC2INDIGO[xType][MAC][u"use_fixedip"] = False

				#self.myLog( text=unicode(client)[0:100])
				if u"blocked" in client:
					self.MAC2INDIGO[xType][MAC][u"blocked"] = client[u"blocked"]
				else:
					self.MAC2INDIGO[xType][MAC][u"blocked"] = False


				previousSeen = self.MAC2INDIGO[xType][MAC][u"last_seen"]
				if  u"last_seen" in client: 
					lastSeen = float(client[u"last_seen"])
					if previousSeen != lastSeen: 
						anyChange += 1.
						secChange += lastSeen - previousSeen
					self.MAC2INDIGO[xType][MAC][u"last_seen"] = lastSeen
				else:
					self.MAC2INDIGO[xType][MAC][u"last_seen"] = -1
					lastSeen = -1

				#if self.decideMyLog(u"DBinfo", MAC=MAC): self.indiLOG.log(10,u"controlDB  {:15s}      client:{}".format(MAC, client) )
				if self.decideMyLog(u"DBinfo", MAC=MAC): self.indiLOG.log(10,u"controlDB  {:15s}      delta delta(now-previous):{:9.0f}, dt lastseen{:9.0f} lastSeen:{:9.0f}".format(MAC, lastSeen - previousSeen, time.time()-lastSeen, lastSeen) )


			for MAC in self.MAC2INDIGO[xType]:
				if MAC not in macsFound: 
					if self.MAC2INDIGO[xType][MAC][u"last_seen"] > 0:
						self.MAC2INDIGO[xType][MAC][u"last_seen"] = -1
					continue

				try: 
					changed = False
					dev = indigo.devices[self.MAC2INDIGO[u"UN"][MAC][u"devId"]]
					if self.decideMyLog(u"DBinfo", MAC=MAC): 
							self.indiLOG.log(10,u"controlDB  {:15s}  {:15s} {:32s};   delta lastUp:{:9.0f}, lastSeen-DB:{:9.0f}*{:9.0f}*{:9.0f}".format(
							 MAC, dev.states["ipNumber"], dev.name, 
							time.time() - self.MAC2INDIGO[xType][MAC][u"lastUp"],
							self.MAC2INDIGO[xType][MAC][u"last_seen"] - self.MAC2INDIGO[xType][MAC][u"lastUp"],
							time.time() - self.MAC2INDIGO[xType][MAC][u"last_seen"],
							self.MAC2INDIGO[xType][MAC][u"last_seen"]	
						) )

					if u"first_seen" in self.MAC2INDIGO[u"UN"][MAC]:
						if u"firstSeen" in dev.states and dev.states[u"firstSeen"] != self.MAC2INDIGO[u"UN"][MAC][u"first_seen"]:
							changed = True
							self.addToStatesUpdateList(dev.id,u"firstSeen",  self.MAC2INDIGO[u"UN"][MAC][u"first_seen"])

					if u"use_fixedip" in self.MAC2INDIGO[u"UN"][MAC]:
						if u"useFixedIP" in dev.states and dev.states[u"useFixedIP"] != self.MAC2INDIGO[u"UN"][MAC][u"use_fixedip"]:
							changed = True
							self.addToStatesUpdateList(dev.id,u"useFixedIP",  self.MAC2INDIGO[u"UN"][MAC][u"use_fixedip"])

					if u"blocked" in dev.states:
						if dev.states[u"blocked"] != self.MAC2INDIGO[u"UN"][MAC]["blocked"]:
							changed = True
							self.addToStatesUpdateList(dev.id,u"blocked",  self.MAC2INDIGO[u"UN"][MAC][u"blocked"])
					if changed:
						self.executeUpdateStatesList()

				except	Exception, e:
					if unicode(e).find(u"None") == -1:
						self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
						if unicode(e).find(u"timeout waiting for response")>-1:
							self.getcontrollerDBForClientsLast = time.time()
							nextCheck = self.getcontrollerDBForClientsLast + float(self.readDictEverySeconds[u"DB"])
							return 

			## try to sync w controller update, repeat faster if no change
			#dt = time.time() - self.getcontrollerDBForClientsPrevious
			### logic here.. to complicated, just take fixed delta 
			self.getcontrollerDBForClientsLast = time.time()
			nextCheck = self.getcontrollerDBForClientsLast + float(self.readDictEverySeconds[u"DB"])
			#if self.decideMyLog(u"DBinfo") or True: self.indiLOG.log(10,u"controlDB anyChange:{}/{} ave:{}; lastdt:{:.0f}; next check in {:.0f}[secs]".format(anyChange, nClients,secChange/max(1,nClients), dt,  nextCheck - time.time() ) )
			self.getcontrollerDBForClientsPrevious = time.time()

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return 


	### here we do the work, setup the logfiles listening and read the logfiles and check if everything is running, if not restart
	####-----------------	 ---------
	def getMessages(self, ipNumber, apN, uType, repeatRead):

		apnS = unicode(apN)
		self.addTypeToDataStats(ipNumber, apnS, uType)
		self.msgListenerActive[uType] = time.time() - 200
		try:
			startErrorCount 			= 0
			unifiDeviceType 			= uType[0:2]
			combinedLines				= ""
			lastTestServer				= time.time()
			msgSleep					= 1
			restartCount				= -1
			lastMSG						= ""
			aliveReceivedTime			= -1
			goodDataReceivedTime		= -1
			ListenProcessFileHandle		= ""
			lastRestartCheck			= time.time()
			newDataStartTime			= time.time()
			newlinesFromServer			= ""
			if repeatRead < 0:
				minWaitbeforeRestart 	= 9999999999999999
			else:
				minWaitbeforeRestart	= 130. #max(float(self.restartIfNoMessageSeconds), float(repeatRead) )
			lastOkRestart				= time.time()

			self.sleep(max(0.5,min(6,float(apN)/2.)))

			self.testServerIfOK(ipNumber,uType)
			if uType.find("tail") > -1:
				self.lastMessageReceivedInListener[ipNumber] = time.time()
			lastOkRestart				= time.time()

			printNow = False
			lastPrintCheck = time.time() -5
			dateStamp = []
			spDebug = False
			consumeDataTime = 0
			while True:
				if printNow:
					self.indiLOG.log(10,u"checkIfRestartNeeded: 0. after while True   datetimestamps:{}".format(unicode(dateStamp).replace(" ","").replace("'","").replace("u","")))

				if spDebug and self.decideMyLog(u"Special"): 
					dateStamp.append([datetime.datetime.now().strftime(u"%M:%S.%f")[0:7]])
					if len(dateStamp) > 4:
						dateStamp.pop(0)
					if  (time.time()-lastPrintCheck > 5) and consumeDataTime < -1: 
						lastPrintCheck = time.time()
						printNow = True
					else:
						printNow = False


				if self.pluginState == "stop" or not self.connectParams[u"enableListener"][uType]: 
					try:	self.killPidIfRunning(ListenProcessFileHandle.pid)
					except:	pass
					break

					## should we stop?, is our IP number listed?
				if ipNumber in self.stop:
					self.indiLOG.log(10,uType+ "getMessage: stop = True for ip# {}".format(ipNumber) )
					self.stop.remove(ipNumber)
					return

				if ipNumber in self.suspendedUnifiSystemDevicesIP:
					self.sleep(20)
					continue

				self.sleep(min(15, msgSleep))

				if printNow: 
					self.indiLOG.log(10,u"checkIfRestartNeeded: 1. after sleep  {}-{}-{}; rC={}; msgSleep:{:.1f}; lastRestartCheck:{:.1f}; dT:{:.1f}, min wait:{:.1f}, check?:{:.1f}, T/F:{}".format(uType, ipNumber, apnS, restartCount, msgSleep, time.time()-lastRestartCheck, time.time() - goodDataReceivedTime, minWaitbeforeRestart,(time.time() - goodDataReceivedTime), (time.time() - goodDataReceivedTime) > minWaitbeforeRestart) )

				retCode, startErrorCount, ListenProcessFileHandle, goodDataReceivedTime, aliveReceivedTime, combinedLines, lastRestartCheck, lastOkRestart = \
					self.checkIfRestartNeeded( 
						goodDataReceivedTime, aliveReceivedTime, startErrorCount, combinedLines, minWaitbeforeRestart, msgSleep, lastRestartCheck, restartCount, uType, ipNumber, apnS, lastMSG, ListenProcessFileHandle, lastOkRestart
					)

				if spDebug and self.decideMyLog(u"Special")  and uType.find("dict") ==-1 and ipNumber == "192.168.1.5": dateStamp[-1].append(datetime.datetime.now().strftime(u"%S.%f")[0:4])
				if printNow:
					self.indiLOG.log(10,u"checkIfRestartNeeded: 2. after checkIfRestartNeeded")

				if retCode == 2: continue

				if spDebug and self.decideMyLog(u"Special")  and uType.find("dict") ==-1 and ipNumber == "192.168.1.5": dateStamp[-1].append(datetime.datetime.now().strftime(u"%S.%f")[0:4])
				if printNow:
					self.indiLOG.log(10,u"checkIfRestartNeeded: 3. after retCode == 2: continue ")
				## here we actually read the stuff
				goodDataReceivedTime, aliveReceivedTime, newlinesFromServer, msgSleep, newDataStartTime = self.readFromUnifiBox( goodDataReceivedTime, aliveReceivedTime, ListenProcessFileHandle, uType, ipNumber, msgSleep, newlinesFromServer, newDataStartTime)
				if newlinesFromServer == "": continue

				if spDebug and self.decideMyLog(u"Special")  and uType.find("dict") ==-1 and ipNumber == "192.168.1.5": dateStamp[-1].append(datetime.datetime.now().strftime(u"%S.%f")[0:4])
				if printNow:
					self.indiLOG.log(10,u"checkIfRestartNeeded: 4. after readFromUnifiBox")
				# command from plugin
				if self.pluginState == "stop": 
					try:	self.killPidIfRunning(ListenProcessFileHandle.pid)
					except:	pass
					return

				goodDataReceivedTime = self.checkIfErrorReceived( goodDataReceivedTime, newlinesFromServer, uType, ipNumber)
				if goodDataReceivedTime == 1: continue

				if spDebug and self.decideMyLog(u"Special")  and uType.find("dict") ==-1 and ipNumber == "192.168.1.5": dateStamp[-1].append(datetime.datetime.now().strftime(u"%S.%f")[0:4])
				if printNow:
					self.indiLOG.log(10,u"checkIfRestartNeeded: 5. after checkIfErrorReceived")

				######### for tail logfile
				consumeDataTime = time.time()
				if uType.find(u"tail") > -1:
					goodDataReceivedTime, lastMSG = self.checkAndPrepTail(newlinesFromServer, goodDataReceivedTime, ipNumber, uType, unifiDeviceType, apN)

					######### for Dicts
				else:
					goodDataReceivedTime, combinedLines, lastMSG = self.checkAndPrepDict( newlinesFromServer, goodDataReceivedTime, combinedLines, ipNumber, uType, unifiDeviceType, minWaitbeforeRestart, apN, newDataStartTime)
				consumeDataTime -= time.time()
				if consumeDataTime < -1:
					if  self.decideMyLog(u"Special"): 
						self.indiLOG.log(10,u"getMessages: consume data needed > 10 secc;  {}-{}-{}; DT:{:.1f}[sec] len(MSG):{:} lastMSG:{:}".format(uType, ipNumber, apnS,-consumeDataTime,len(lastMSG), lastMSG[-100:].replace("\r","")) )
					msgSleep = 0

				if spDebug and self.decideMyLog(u"Special")  and uType.find("dict") ==-1 and ipNumber == "192.168.1.5": dateStamp[-1].append(datetime.datetime.now().strftime(u"%S.%f")[0:4])
				if printNow:
					self.indiLOG.log(10,u"checkIfRestartNeeded: 6. after checkAndPrepTail")

				if self.statusChanged > 0:
					self.setGroupStatus()

				if spDebug and self.decideMyLog(u"Special")  and uType.find("dict") ==-1 and ipNumber == "192.168.1.5": dateStamp[-1].append(datetime.datetime.now().strftime(u"%S.%f")[0:4])
				if printNow:
					self.indiLOG.log(10,u"checkIfRestartNeeded: 7. after sendBroadCastNOW")

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		self.indiLOG.log(30,u"getMessages: stopping listener process for :{} - {}".format(uType, ipNumber )  )
		return



	####-----------------	 ---------
	def checkIfRestartNeeded(self, goodDataReceivedTime, aliveReceivedTime, startErrorCount, combinedLines, minWaitbeforeRestart, msgSleep, lastRestartCheck, restartCount, uType, ipNumber, apnS, lastMSG, ListenProcessFileHandle, lastOkRestart):
		try:
			retCode = 0
			if False and self.decideMyLog(u"Special"): self.indiLOG.log(10,u"checkIfRestartNeeded: {}-{}-{}; rC={}; msgSleep:{:.1f}; lastRestartCheck:{:.1f}; dT:{:.1f}, min wait:{:.1f}, check?:{:.1f}, T/F:{}".format(uType, ipNumber, apnS, restartCount, msgSleep, time.time()-lastRestartCheck, time.time() - goodDataReceivedTime, minWaitbeforeRestart,(time.time() - goodDataReceivedTime), (time.time() - goodDataReceivedTime) > minWaitbeforeRestart) )
			lastRestartCheck = time.time()
			if len(self.restartRequest) > 0:
				if uType in self.restartRequest:
					if self.restartRequest[uType] == apnS:
						self.indiLOG.log(10,u"getMessages: {}    restart requested by menue ".format(self.restartRequest) )
						goodDataReceivedTime	= -1
						del self.restartRequest[uType]

			forcedRestart  = time.time() - lastOkRestart 
			restartTimeout = time.time() - goodDataReceivedTime

			if restartTimeout < minWaitbeforeRestart and goodDataReceivedTime > 0 and forcedRestart < self.restartListenerEvery: 
				# nothing to do
				return retCode, startErrorCount, ListenProcessFileHandle, goodDataReceivedTime, aliveReceivedTime, combinedLines, lastRestartCheck, lastOkRestart

			## ned to restart, eitehr new or launch command, or no messages for xx secs
			if goodDataReceivedTime < 0:# at startup
				self.indiLOG.log(10,u"getMessages: launching listener for: {} / {}".format(uType, ipNumber) )

			## no messages for xx secs:
			else:
				if forcedRestart > self.restartListenerEvery:
					logLevel = 10
					restartCount = 0
				else:
					if   restartCount > 6:	logLevel = 30; restartCount = 0
					elif restartCount > 2:	logLevel = 20
					else:				  	logLevel = 10
					restartCount += 1

				lsm = lastMSG.replace("\n","")
				self.indiLOG.log(logLevel,u"getMessages: relaunching {} / {} / {}:  timeSinceLastRestart {:.0f} > forcedRestart:{:.0f} [sec]  ;  without message:{:.1f}[sec], limitforRestart:{:.1f}[sec], restartCount:{:},  len(msg):{:}; lastMSG:{:}<<".format(self.connectParams[u"expectCmdFile"][uType], uType, ipNumber, forcedRestart, self.restartListenerEvery, restartTimeout, minWaitbeforeRestart, restartCount, len(lsm), lsm[-100:].replace("\r","") )  )

				self.dataStats[u"tcpip"][uType][ipNumber][u"restarts"] += 1

				if restartCount in [3,5,7]:
					self.connectParams[u"promptOnServer"][ipNumber] = ""

				
			if ListenProcessFileHandle != "": 
				self.killPidIfRunning(ListenProcessFileHandle.pid)


			if not self.testServerIfOK(ipNumber,uType):
				self.indiLOG.log(40,u"getMessages: (1 - test connect)  error for {}, ip#: {}, prompt:'{}'; wrong ip/ password or system down or ssh timed out or ..? ".format(uType, ipNumber, self.connectParams[u"promptOnServer"][ipNumber]) )
				self.msgListenerActive[uType] = 0
				retCode = 2
				combinedLines = ""
				time.sleep(15)
				return retCode, startErrorCount, ListenProcessFileHandle, goodDataReceivedTime, aliveReceivedTime, combinedLines, lastRestartCheck, lastOkRestart

			if uType=="VDtail":
				self.setAccessToLog(ipNumber,uType)

			ListenProcessFileHandle, startError = self.startConnect(ipNumber,uType)
			combinedLines = ""
			if self.decideMyLog(u"Expect"):
				try: 	pid = ListenProcessFileHandle.pid
				except:	pid = "not defined"
				self.indiLOG.log(10,u"getMessages: ListenProcess started for uType: {};  ip: {}, prompt:'{}', pid:{}".format(uType, ipNumber, self.connectParams[u"promptOnServer"][ipNumber], pid) )


			if startError != "":
				startErrorCount +=1
				if startErrorCount%10 == 0:
					self.indiLOG.log(40,u"getMessages: connect start connect error in listener {}, to  @ {}  ::::{}::::".format(uType, ipNumber, startError) )
				retCode = 2
				self.sleep(15)
				return retCode, startErrorCount, ListenProcessFileHandle, goodDataReceivedTime, aliveReceivedTime, combinedLines, lastRestartCheck, lastOkRestart

			self.msgListenerActive[uType]	= time.time()
			goodDataReceivedTime 			= time.time()
			aliveReceivedTime 	 			= time.time()
			lastOkRestart					= time.time()

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
				combinedLines 	= ""
				retCode 		= 2
				self.sleep(15)

		return retCode, startErrorCount, ListenProcessFileHandle, goodDataReceivedTime, aliveReceivedTime, combinedLines, lastRestartCheck, lastOkRestart


	####-----------------	 ---------
	def readFromUnifiBox(self, goodDataReceivedTime, aliveReceivedTime, ListenProcessFileHandle, uType, ipNumber, msgSleep, lastLine, newDataStartTime):
		try:
			try:
				if ListenProcessFileHandle == "": 
					self.indiLOG.log(20,"readFromUnifiBox: read handle not defined for {}-{}, sleeping 15 secs ".format(uType, ipNumber))
					newlinesFromServer		= ""
					goodDataReceivedTime	= 1 # this forces a restart of the listener
					msgSleep				= 15
					self.sleep(10)
					return goodDataReceivedTime, aliveReceivedTime, newlinesFromServer, msgSleep, newDataStartTime

				newlinesFromServer = ""
				lfs = ""
				lfs = os.read(ListenProcessFileHandle.stdout.fileno(),self.readBuffer).decode(u"utf8") 
				newlinesFromServer = unicode(lfs) 
				if newlinesFromServer != "":
					aliveReceivedTime = time.time()
				msgSleep = 0.2 # fast read to follow, if data 
				if lastLine == "" and  newlinesFromServer != "": newDataStartTime = time.time()
			except	Exception, e:
				if uType.find("dict") >-1:	msgSleep += .4 # nothing new, can wait, dicts come every 60 secs 
				else:						msgSleep  = 0.4 # this is for tail 
				msgSleep = min(msgSleep,4)
				if unicode(e).find(u"[Errno 35]") == -1:	 # "Errno 35" is the normal response if no data, if other error stop and restart
					if unicode(e).find(u"None") == -1:
						out = u"os.read(ListenProcessFileHandle.stdout.fileno())  in Line {} has error={}\n ip:{}  type: {}".format(sys.exc_traceback.tb_lineno, e, ipNumber,uType )
						try: out+= u"fileNo: {}".format(ListenProcessFileHandle.stdout.fileno() )
						except: pass
						if unicode(e).find(u"[Errno 22]") > -1:  # "Errno 22" is  general read error "wrong parameter"
							out+= u"\n ..      try lowering/increasing read buffer parameter in config" 
							self.indiLOG.log(30,out)
						else:
							self.indiLOG.log(40,out)
							self.indiLOG.log(40,lfs)
					goodDataReceivedTime = 1 # this forces a restart of the listener
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

		return goodDataReceivedTime, aliveReceivedTime, newlinesFromServer, msgSleep, newDataStartTime

	####-----------------	 ---------
	def checkIfErrorReceived(self, goodDataReceivedTime, newlinesFromServer, uType, ipNumber):
		try:
			if newlinesFromServer != "":
				self.dataStats[u"tcpip"][uType][ipNumber][u"inMessageCount"] += 1
				self.dataStats[u"tcpip"][uType][ipNumber][u"inMessageBytes"] += len(newlinesFromServer)
				## any error messages from OSX?
				pos1 = newlinesFromServer.find(u"closed by remote host")
				pos2 = newlinesFromServer.find(u"Killed by signal")
				pos3 = newlinesFromServer.find(u"Killed -9")
				if (  pos1 >- 1 or pos2 >- 1 or pos3 > -1):
					self.indiLOG.log(             30,u"getMessage: {} {} returning: ".format(uType, ipNumber)  )
					if pos1 >-1: self.indiLOG.log(30,u"...{}".format(newlinesFromServer[max(0,pos1 - 100):pos1 + 100]) )
					if pos2 >-1: self.indiLOG.log(30,u"...{}".format(newlinesFromServer[max(0,pos2 - 100):pos2 + 100]) )
					if pos3 >-1: self.indiLOG.log(30,u"...{}".format(newlinesFromServer[max(0,pos3 - 100):pos3 + 100]) )
					self.indiLOG.log(             30,u"...: {} we should restart listener on server ".format(uType) )
					goodDataReceivedTime = 1#
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return goodDataReceivedTime

	####-----------------	 ---------
	def checkAndPrepTail(self, newlinesFromServer, goodDataReceivedTime, ipNumber, uType, unifiDeviceType, apN):
		try:
			lastMSG = newlinesFromServer
			## fill the queue and send to the method that uses it
			if		unifiDeviceType == "AP":
				self.deviceUp[u"AP"][ipNumber] = time.time()
			elif	unifiDeviceType == "GW":
				self.deviceUp[u"GW"][ipNumber] = time.time()
			elif	unifiDeviceType == "VD":
				self.deviceUp[u"VD"][ipNumber] = time.time()
			self.msgListenerActive[uType]  = time.time()

			if time.time() > self.lastMessageReceivedInListener[ipNumber]: 
				self.lastMessageReceivedInListener[ipNumber] = time.time()

			# we accept any message as good data 
			goodDataReceivedTime = time.time()

			if newlinesFromServer.find(u"ThisIsTheAliveTestFromUnifiToPlugin") > -1:
				self.dataStats[u"tcpip"][uType][ipNumber][u"aliveTestCount"] += 1
				if self.decideMyLog(u"ExpectRET"): self.indiLOG.log(10,u"getMessage: {} {} ThisIsTheAliveTestFromUnifiToPlugin received ".format(uType, ipNumber))
			else:
				self.logQueue.put((newlinesFromServer,ipNumber,apN, uType,unifiDeviceType))

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
				self.indiLOG.log(30,u"checkAndPrepDict: error for {} - {}".format(uType, ipNumber )  )
		return goodDataReceivedTime, lastMSG


	####-----------------	 ---------
	def checkAndPrepDict(self, newlinesFromServer, goodDataReceivedTime, combinedLines, ipNumber, uType, unifiDeviceType, minWaitbeforeRestart, apN, newDataStartTime):
		try:
			combinedLines += newlinesFromServer
			lastMSG = combinedLines
			ppp = combinedLines.split(self.connectParams[u"startDictToken"][uType])
			if False and self.decideMyLog(u"Special"): 
				ll = 70
				out =  unicode(combinedLines[0:ll]).replace("\n","").replace("\r","")
				ll = max(5, min(70, len(combinedLines) - len(out)))
				out += " -.-.- "
 				out +=	unicode(combinedLines[-ll:]).replace("\n","").replace("\r","")
				self.indiLOG.log(10,u"::::::{}-{}data read from Unifi Dev len(split):{};combinedLines:{}; splitting:>>{}<< startDict:\ndata={}<<<<".format(ipNumber, uType, len(ppp), len(combinedLines), self.connectParams[u"startDictToken"][uType], out) )

			if len(ppp) == 2:
				endTokenPos = ppp[1].find(self.connectParams[u"endDictToken"][uType])
				if False and self.decideMyLog(u"Special"): self.indiLOG.log(10,u"...1::{} found endDictToken:{} @ pos:{} ".format( ipNumber, self.connectParams[u"endDictToken"][uType], endTokenPos ) )
				if endTokenPos >-1:
					dictData = ppp[1].lstrip("\r\n")
					if False and self.decideMyLog(u"Special"): self.indiLOG.log(10,u"getMessages check dict:{}; endPos found @ pos:{}, len(data):{}, collect time = {:.1f}, ending with:{:}".format( ipNumber, endTokenPos,len(dictData), time.time() - newDataStartTime, dictData[-100:].replace("\n","").replace("\r","") ) )
					try:
						dictData = dictData[0:endTokenPos]
						## remove last line
						if dictData[-1] !="}":
							ppp = dictData.rfind("}")
							dictData = dictData[0:ppp+1]
						theDict= json.loads(dictData)
						if	  unifiDeviceType == "AP":
							self.deviceUp[u"AP"][ipNumber]	= time.time()
						elif  unifiDeviceType == "SW":
							self.deviceUp[u"SW"][ipNumber]	= time.time()
						elif  unifiDeviceType == "GW":
							self.deviceUp[u"GW"][ipNumber]	= time.time()
						elif  unifiDeviceType == "UD":
							self.deviceUp[u"SW"][ipNumber]	= time.time()
							self.deviceUp[u"UD"]			= time.time()
							self.deviceUp[u"GW"][ipNumber]	= time.time()

						if False and self.decideMyLog(u"Special"): self.indiLOG.log(10,u"...2::{} theDict: {} -.-.- {}<<<<".format( ipNumber, dictData[0:40].replace("\n","").replace("\r","") ,  dictData[-90:].replace("\n","").replace("\r","") ) )
						combinedLines = ""
						self.logQueueDict.put((theDict, ipNumber, apN, uType, unifiDeviceType))
						goodDataReceivedTime = time.time()
						self.dataStats[u"tcpip"][uType][ipNumber][u"inErrorTime"] -= 30

					except	Exception, e:
						if unicode(e).find(u"None") == -1:
							errText = u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e)
							pingTest = self.testAPandPing(ipNumber,uType) 
							okTest = self.testServerIfOK(ipNumber,uType) 
							retryPeriod = float(self.readDictEverySeconds[uType[0:2]]) + 10.
							if True or time.time() - self.dataStats[u"tcpip"][uType][ipNumber][u"inErrorTime"] < retryPeriod or not pingTest or not okTest:
								msgF = combinedLines.replace("\r","").replace("\n","")
								self.indiLOG.log(40,errText)
								self.indiLOG.log(20,u"checkAndPrepDict JSON len:{}; {}...\n...  {}".format(len(combinedLines),msgF[0:100], msgF[-40:]) )
								self.indiLOG.log(20,u".... in receiving DICTs for {}-{};  for details check unifi logfile  at: {} ".format(uType, ipNumber, self.logFile ))
								self.indiLOG.log(10,u".... ping test:  {}".format(" ok " if pingTest  else " bad") )
								self.indiLOG.log(10,u".... ssh test:   {}".format(" ok " if okTest else " bad") )
								self.indiLOG.log(10,u".... uid/passwd:>{}<".format(self.getUidPasswd(uType, ipNumber)) )
							else:
								self.indiLOG.log(10,u"getMessage, error reading dict >{}-{}<, not complete? len(data){}, endTokenPos:{}; error:{} ---- retrying".format(uType, ipNumber, len(dictData), endTokenPos, e) )

							self.dataStats[u"tcpip"][uType][ipNumber][u"inErrorCount"]+=1
							self.dataStats[u"tcpip"][uType][ipNumber][u"inErrorTime"] = time.time()
							goodDataReceivedTime = time.time() - minWaitbeforeRestart*0.95
					combinedLines = ""
			else:
				combinedLines = ""

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
				self.indiLOG.log(30,u"checkAndPrepDict: error for {} - {}".format(uType, ipNumber )  )
				goodDataReceivedTime = 1
				combinedLines = ""
		return goodDataReceivedTime, combinedLines, lastMSG


	### start the expect command to get the logfile
	####-----------------	 ---------
	def startConnect(self, ipNumber, uType):
		try:
			userid, passwd = self.getUidPasswd(uType,ipNumber)
			if userid =="": return

			if self.decideMyLog(u"Expect"): self.indiLOG.log(10,u"startConnect: with IP: {:<15};   uType: {};   UID/PWD: {}/{}".format(ipNumber, uType, userid, passwd) )

			if ipNumber not in self.listenStart:
				self.listenStart[ipNumber] = {}
			self.listenStart[ipNumber][uType] = time.time()
			if self.connectParams[u"commandOnServer"][uType].find(u"off") == 0: return "",""

			TT= uType[0:2]
			for ii in range(20):
				if uType.find(u"dict")>-1:
					cmd  = self.expectPath + " '" 
					cmd += self.pathToPlugin + self.connectParams[u"expectCmdFile"][uType] + "' "
					cmd += "'"+userid + "' '"+passwd + "' " 
					cmd += ipNumber + " " 
					cmd += "'"+self.escapeExpect(self.connectParams[u"promptOnServer"][ipNumber]) + "' " 
					cmd += self.connectParams[u"endDictToken"][uType]+ " " 
					cmd += unicode(self.readDictEverySeconds[TT])+ " " 
					cmd += unicode(self.timeoutDICT)
					cmd += " \""+self.connectParams[u"commandOnServer"][uType]+"\" "
					if uType.find(u"AP") >-1:
						cmd += " /var/log/messages"
					else:
						 cmd += "  doNotSendAliveMessage"

				else:
					cmd = self.expectPath + " '" 
					cmd +=  self.pathToPlugin +self.connectParams[u"expectCmdFile"][uType] + "' "
					cmd += "'"+userid + "' '"+passwd + "' "
					cmd += ipNumber + " "
					cmd += "'"+self.escapeExpect(self.connectParams[u"promptOnServer"][ipNumber])+"' " 
					cmd += " \""+self.connectParams[u"commandOnServer"][uType]+"\" "

				if self.decideMyLog(u"Expect"): self.indiLOG.log(10,u"startConnect: cmd {}".format(cmd) )
				ListenProcessFileHandle = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
				##pid = ListenProcessFileHandle.pid
				##self.myLog( text=u" pid= " + unicode(pid) )
				msg = unicode(ListenProcessFileHandle.stderr)
				if msg.find(u"open file") == -1:	# try this again
					self.indiLOG.log(40,u"uType {}; IP#: {}; error connecting {}".formaat(uType, ipNumber, msg) )
					self.sleep(20)
					continue

				# set the O_NONBLOCK flag of ListenProcessFileHandle.stdout file descriptor:
				flags = fcntl.fcntl(ListenProcessFileHandle.stdout, fcntl.F_GETFL)  # get current p.stdout flags
				fcntl.fcntl(ListenProcessFileHandle.stdout, fcntl.F_SETFL, flags | os.O_NONBLOCK)

				return ListenProcessFileHandle, ""
			self.sleep(0.1)
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"startConnect: in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			return "", "error "+ unicode(e)
		self.indiLOG.log(40,u"startConnect timeout, not able to  connect after 20 tries ")
		return "","error connecting"



	####-----------------	 ---------
	def createEntryInUnifiDevLog(self):
		try:
			if not self.createEntryInUnifiDevLogActive: return 
			if time.time() - self.lastcreateEntryInUnifiDevLog < 12: return 
			self.lastcreateEntryInUnifiDevLog = time.time()
			doTestIflastMsg = 80 # do a test if last msg from listener is > xx sec ago 
			#if self.decideMyLog(u"Special"):self.indiLOG.log(10,u"createEntryInUnifiDevLog: testing if we should do test ok, now:{}; lastmsgs:\n{}".format(time.time(), self.lastMessageReceivedInListener ))

			if self.devsEnabled[u"GW"] and not self.devsEnabled[u"UD"]:
				ipN = self.ipNumbersOf[u"GW"]
				if ipN in self.lastMessageReceivedInListener and  time.time() - self.lastMessageReceivedInListener[ipN] > doTestIflastMsg: 
					self.testServerIfOK( ipN, u"GW", batch=True)

			for aa in [u"AP",u"SW"]:
				if self.numberOfActive[aa] > 0:
					for ll in range(len(self.devsEnabled[aa])):
						if self.devsEnabled[aa][ll]:
							if (self.unifiControllerType == "UDM" or self.controllerWebEventReadON > 0) and ll == self.numberForUDM[aa]: continue
							ipN = self.ipNumbersOf[aa][ll]
							if ipN in self.lastMessageReceivedInListener  and  time.time() - self.lastMessageReceivedInListener[ipN] > doTestIflastMsg: 
								self.testServerIfOK( ipN, aa, batch=True)
	
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"startConnect: in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return 



	####-----------------	 ---------
	def testServerIfOK(self, ipNumber, uType, batch=False):
		try:
			userid, passwd = self.getUidPasswd(uType,ipNumber)
			if userid == u"": 
				self.indiLOG.log(40,u"testServerIf ssh connection OK: userid>>{}<<, passwd>>{}<<  wrong for {}-{}".format(userid, passwd, uType, ipNumber) )
				return False

			cmd = self.expectPath+ " '" + self.pathToPlugin +"test.exp' '" + userid + "' '" + passwd + "' " + ipNumber


			if ipNumber in self.lastMessageReceivedInListener: self.lastMessageReceivedInListener[ipNumber] = time.time()

			if batch:
				#if self.decideMyLog(u"Special"): self.indiLOG.log(10,u"testServer ssh to {}-{} to create log entry using:{}".format(uType, ipNumber, cmd) )
				if self.decideMyLog(u"Expect"): self.indiLOG.log(10,u"testServerIfOK: batch {}".format(cmd) )
				subprocess.Popen(cmd+" &", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
				return 

			if self.decideMyLog(u"Expect"): self.indiLOG.log(10,u"testServerIfOK: {}".format(cmd) )
			ret = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
			xx = ret[0].replace("\r","")
			if self.decideMyLog(u"ExpectRET"): self.indiLOG.log(10,"returned from expect-command: {}".format(xx))

			## check if we need to fix unknown host in .ssh/known_hosts
			if len(ret[1]) > 0:
				self.indiLOG.log(40,u"testServerIf ssh connection to server failed, cmd: {}".format(cmd) )
				ret1, ok = self.fixHostsFile(ret,ipNumber)
				if not ok: 
					self.indiLOG.log(40,u"testServerIfOK failed, will retry ")
					ret = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
					xx = ret[0].replace("\r","")

			test = xx.lower()
			tags = [u"welcome",u"unifi",u"debian",u"edge",u"busybox",u"ubiquiti",u"ubnt",u"login"]
			loggedIn = False
			for tag in tags:
				if tag in test: 
					loggedIn = True
					break
			if loggedIn:
				nPrompt = 3
				if ipNumber in self.connectParams[u"promptOnServer"]:
					if self.connectParams[u"promptOnServer"][ipNumber]  == xx[-nPrompt:]: 
						return True
					else:
						self.indiLOG.log(10,u"testServerIfOK: =========== {}; prompt not found or reset by restart;  old:'{}', new candidate:'{}'".format(ipNumber, self.escapeExpect(self.connectParams[u"promptOnServer"][ipNumber]),  xx[-nPrompt:]) )
						pass
				else:
					self.connectParams[u"promptOnServer"][ipNumber] = ""
					self.indiLOG.log(10,u"testServerIfOK: =========== ipNumber:{} not in connectParams".format(ipNumber) )

				prompt= xx[-nPrompt:]
				# remove new line from prompts would screw up expect, does not like newline in variables ...
				newL = prompt.find("\n")
				if newL == -1: 
					newL = prompt.find("\r")

				if   newL	== 0: 				prompt = prompt[1:]
				elif newL	== len(prompt)-1:	prompt = prompt[:-1]
				nPrompt = len(prompt)
				self.indiLOG.log(10,u"testServerIfOK: =========== for {}  ssh response, setting promp to:'{}' using last {} chars in ...{}<<<< ".format(ipNumber,  prompt, nPrompt,   xx[-20:]) )


				self.connectParams[u"promptOnServer"][ipNumber] = prompt
				
				self.pluginPrefs[u"connectParams"] = json.dumps(self.connectParams)

				self.indiLOG.log(10,u"testServerIfOK: =========== known prompts: \n{}".format(self.connectParams[u"promptOnServer"]))
				return True

			self.indiLOG.log(10,u"testServerIfOK: ==========={}  ssh response, tags {} not found : ==> \n{}".format(ipNumber, tags, xx) )
			return False
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"testServerIfOK in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return False

####-------------------------------------------------------------------------####
	def fixHostsFile(self, ret, ipNumber):
		try:
			if ret[0].find(u".ssh/known_hosts:") > -1:
				if (subprocess.Popen(u"/usr/bin/csrutil status" , shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].find(u"enabled")) >-1:
					self.indiLOG.log(40,u'ERROR can not update hosts known_hosts file,    "/usr/bin/csrutil status" shows system enabled SIP; please edit manually with \n"nano {}/.ssh/known_hosts"\n and delete line starting with {}'.format(self.MAChome, ipNumber) )
					self.indiLOG.log(40,u"trying to fix from within plugin, if it happens again you need to do it manually")
					try:
						f = open(self.MAChome+u'/.ssh/known_hosts',u"r")
						lines = f.readlines()
						f.close()
						f = open(self.MAChome+u'/.ssh/known_hosts',u"w")
						for line in lines:
							if line.find(ipNumber) >-1: continue
							if len(line) < 10: continue
							f.write(line+u"\n")
						f.close()
					except Exception, e:
						self.indiLOG.log(40,u"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

					return [u"",""], False

				fix1 = ret[0].split(u"Offending RSA key in ")
				if len(fix1) > 1:
					fix2 = fix1[1].split(u"\n")[0].strip(u"\n").strip(u"\n")
					fix3 = fix2.split(u":")
					if len(fix3) > 1:
						fixcode = u"/usr/bin/perl -pi -e 's/\Q$_// if ($. == " + fix3[1] + ");' " + fix3[0]
						self.indiLOG.log(40, u"wrong RSA key, trying to fix with: {}".format(fixcode) )
						p = subprocess.Popen(fixcode, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
						ret = p.communicate()
 
		except Exception, e:
			self.indiLOG.log(40,u"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return ret, True


	####-----------------	 ---------
	def setAccessToLog(self, ipNumber, uType):
		try:
			userid, passwd = self.getUidPasswd(uType,ipNumber)
			if userid =="": return False

			cmd = self.expectPath +" '" + self.pathToPlugin +"setaccessToLog.exp' '" + userid + "' '" + passwd + "' " + ipNumber + " '" +self.escapeExpect(self.connectParams[u"promptOnServer"][ipNumber])+"' "
			#if self.decideMyLog(u"Expect"): 
			if self.decideMyLog(u"Expect"): self.indiLOG.log(10,cmd)
			ret = (subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate())
			if self.decideMyLog(u"ExpectRET"): self.indiLOG.log(10,"returned from expect-command: {}".format(ret[0]))
			test = ret[0].lower()
			tags = [u"welcome",u"unifi",u"debian",u"edge",u"busybox",u"ubiquiti",u"ubnt",u"login"]
			for tag in tags:
				if tag in test:	 return True
			self.indiLOG.log(10,u"\n==========={}  ssh response, tags {} not found : ==> {}".format(ipNumber, tags, test) )
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"setAccessToLog in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return False

	####-----------------	 ---------
	def getUidPasswd(self, uType, ipNumber):

		try:
			if uType.find(u"VD") > -1:
				userid = self.connectParams[u"UserID"][u"unixNVR"]
				passwd = self.connectParams[u"PassWd"][u"unixNVR"]

			else:
				if self.unifiControllerType.find(u"UDM") > -1 and (
					( uType.find(u"AP") > -1 and ipNumber == self.ipNumbersOf[u"AP"][self.numberForUDM[u"AP"]]) or
					( uType.find(u"SW") > -1 and ipNumber == self.ipNumbersOf[u"SW"][self.numberForUDM[u"SW"]]) or
					( uType.find(u"UD") > -1 ) or
					( uType.find(u"GW") > -1 and ipNumber == self.ipNumbersOf[u"GW"]) ):
					userid = self.connectParams[u"UserID"][u"unixUD"]
					passwd = self.connectParams[u"PassWd"][u"unixUD"]
				else:	
					userid = self.connectParams[u"UserID"][u"unixDevs"]
					passwd = self.connectParams[u"PassWd"][u"unixDevs"]

			if userid == u"" or passwd == u"":
				self.indiLOG.log(10,u"Connection: {} login disabled, userid is empty".format(uType) )
			return userid, passwd
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"setAccessToLog in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return "",""



	####-----------------	 ---------
	def comsumeLogData(self):# , startTime):
		self.sleep(1)
		self.indiLOG.log(10,u"comsumeLogData:  process starting")
		nextItem = ""
		lines	 = ""
		ipNumber = ""
		while True:
			try:
				if self.pluginState == "stop" or self.consumeDataThread[u"log"][u"status"] == u"stop": 
					self.indiLOG.log(30,u"comsumeLogData: stopping process due to stop request")
					return  
				self.sleep(0.1)
				consumedTimeQueue = time.time()
				while not self.logQueue.empty():
					if self.pluginState == "stop" or self.consumeDataThread[u"log"][u"status"] == u"stop": 
						self.indiLOG.log(30,u"comsumeLogData:  stopping process due to stop request")
						return 

					nextItem = self.logQueue.get()

					lines			= nextItem[0].split("\r\n")
					ipNumber		= nextItem[1]
					apN				= nextItem[2]
					try: 	apNint	= int(nextItem[2])
					except: apNint	= -1
					uType			= nextItem[3]
					xType			= nextItem[4]

					## update device-ap with new timestamp, it is up
					if self.decideMyLog(u"Log"): self.indiLOG.log(10,u"MS-------  {:13s}#{}   {}  {} .. {}".format(ipNumber, apN, uType, xType, unicode(nextItem[0])[0:100]) )

					if ( (uType.find(u"SW") > -1 and apNint >= 0 and apNint < len(self.debugDevs[u"SW"]) and self.debugDevs[u"SW"][apNint]) or
						 (uType.find(u"AP") > -1 and apNint >= 0 and apNint < len(self.debugDevs[u"AP"]) and self.debugDevs[u"AP"][apNint]) or 
						 (uType.find(u"GW") > -1  and self.debugDevs[u"GW"]) ): 
						self.indiLOG.log(10,u"DEVdebug   {} dev #:{:2d} uType:{}, xType{}, logmessage:\n{}".format(ipNumber, apNint, uType, xType, "\n".join(lines)) )

					### update lastup for unifi devices
					if xType in self.MAC2INDIGO:
						for MAC in self.MAC2INDIGO[xType]:
							if xType == u"UN" and self.testIgnoreMAC(MAC, fromSystem="log"): continue
							if ipNumber == self.MAC2INDIGO[xType][MAC][u"ipNumber"]:
								self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
								break

					consumedTime = time.time()

					if	 uType == "APtail":
						self.doAPmessages(lines, ipNumber, apN)
					elif uType == "GWtail":
						self.doGWmessages(lines, ipNumber, apN)
					elif uType == "SWtail":
						self.doSWmessages(lines, ipNumber, apN)
					elif uType == "VDtail":
						self.doVDmessages()
					consumedTime -= time.time()
					if consumedTime < -3.0: logLevel = 20
					else:					logLevel = 10
					if logLevel == 20 or (self.decideMyLog(u"Special") and consumedTime < -0.4) :
						self.indiLOG.log(logLevel,u"comsumeLogData    excessive time consumed:{:.1f}[secs]; {:}; len:{:},  lines:{:}".format(-consumedTime, ipNumber, len(lines), unicode(lines)[0:100]) )

					self.logQueue.task_done()

				#self.logQueue.task_done()
					if len(self.sendUpdateToFingscanList) > 0: self.sendUpdatetoFingscanNOW()
					if len(self.sendBroadCastEventsList)  > 0: self.sendBroadCastNOW()

				consumedTimeQueue -= time.time()
				if consumedTimeQueue < -5.0: logLevel = 20
				else:						 logLevel = 10
				if logLevel == 20 or (self.decideMyLog(u"Special") and consumedTimeQueue < -0.6) :
					self.indiLOG.log(logLevel,u"comsumeLogData  T excessive time consumed:{:.1f}[secs]; {:}; len:{:},  lines:{:}".format(-consumedTimeQueue, ipNumber, len(lines), unicode(lines)[0:100]) )


			except	Exception, e:
				if unicode(e).find(u"None") == -1:
					self.indiLOG.log(40,u"updateIndigoWithLogData in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		self.indiLOG.log(30,u"comsumeLogData:  stopping process (3)")
		return 




	###########################################
	####------ camera PROTEC ---	-------START
	###########################################
	def getProtectIntoIndigo(self):
		try:
			if self.cameraSystem != u"protect":										return
			if time.time() - self.lastRefreshProtect < self.refreshProtectCameras: 	return
			elapsedTime 	= time.time()
			systemInfoProtect = self.executeCMDOnController(dataSEND={}, pageString=u"api/bootstrap/", jsonAction=u"protect", cmdType=u"get", protect=True)
			if False and self.decideMyLog(u"Protect"): self.indiLOG.log(10,u"getProtectIntoIndigo: *********   elapsed time (1):{:.1f}".format(time.time() - elapsedTime))

			if len(systemInfoProtect) == 0: 
				self.lastRefreshProtect  = time.time() - self.refreshProtectCameras +2
				return
			if u"cameras" not in systemInfoProtect:
				self.lastRefreshProtect  = time.time() - self.refreshProtectCameras +2
				return

			mapSensToLevel ={"":"", 0:u"low", 1:u"med", 2:u"high"}
			lD = len(self.PROTECT)
			# clean up device listed in PROTECT, but not in indigo, only check at beginning and every 5 minutes
			if lD == 0 or time.time() - self.lastRefreshProtect > 300 or self.lastRefreshProtect ==0:
				devList = {}
				MAClist = {}
				for dev in indigo.devices.iter(u"props.isProtectCamera"):
					cameraId = dev.states[u"id"]
					if dev.states[u"MAC"] in MAClist:
						self.indiLOG.log(30,u"getProtectIntoIndigo: duplicated MAC number:{} in indigo devices, please delete one : {}, currently ignoring: [{},{}]  ".format(dev.states[u"MAC"], MAClist[dev.states[u"MAC"]],  dev.id, dev.name ))
						continue
					MAClist[dev.states[u"MAC"]] = [dev.id, dev.name]
					if dev.states[u"id"] not in self.PROTECT:
						self.PROTECT[cameraId] = {u"events":{}, u"devId":dev.id, u"devName":dev.name, u"MAC":dev.states[u"MAC"], "lastUpdate":time.time()}
					devList[cameraId] = 1
					# clean up wrong status afetr strtup
					if lD == 0:
						if dev.states[u"status"] in [u"event",u"motion",u"ring","person","vehicle"]:
							#self.indiLOG.log(30,u"getProtectIntoIndigo: fixing status for:{}".format(dev.name ))
							self.addToStatesUpdateList(dev.id, u"status", u"CONNECTED")
							dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOn)
							self.executeUpdateStatesList()

				delList = {}
				for cameraId in self.PROTECT:
					if cameraId not in devList:
						delList[cameraId] = 1

				for cameraId in delList:
					del self.PROTECT[cameraId]
			
				if lD == 0 and self.decideMyLog(u"Protect"):
					self.indiLOG.log(10,u"getProtectIntoIndigo: starting with dev list: {}".format(self.PROTECT))

			for camera in systemInfoProtect[u"cameras"]:
				try:
					states = {}
					MAC 										= self.getIfinDict(camera,u"mac",default=u"00:00:00:00:00:00")
					states[u"MAC"] 								= MAC[0:2]+u":"+MAC[2:4]+u":"+MAC[4:6]+u":"+MAC[6:8]+u":"+MAC[8:10]+u":"+MAC[10:12]
					states[u"id"] 								= self.getIfinDict(camera,u"id",default=u"0")
					states[u"name"] 							= self.getIfinDict(camera,u"name")
					states[u"ip"]		 						= self.getIfinDict(camera,u"host")
					states[u"status"] 							= self.getIfinDict(camera,u"state")
					states[u"type"] 							= self.getIfinDict(camera,u"type")
					states[u"firmwareVersion"] 					= self.getIfinDict(camera,u"firmwareVersion")
					states[u"isAdopted"] 						= self.getIfinDict(camera,u"isAdopted", default=False)
					states[u"isConnected"] 						= self.getIfinDict(camera,u"isConnected", default=False)
					states[u"isManaged"] 						= self.getIfinDict(camera,u"isManaged", default=False)
					states[u"isDark"] 							= self.getIfinDict(camera,u"isDark", default=False)
					states[u"hasSpeaker"] 						= self.getIfinDict(camera,u"hasSpeaker", default=False)
					states[u"isSpeakerEnabled"] 				= self.getIfinDict(camera[u"speakerSettings"],u"isEnabled", default=False)
					states[u"isExternalIrEnabled"] 				= self.getIfinDict(camera[u"ispSettings"],u"isExternalIrEnabled", default=False)
					states[u"irLedMode"] 						= self.getIfinDict(camera[u"ispSettings"],u"irLedMode")
					states[u"irLedLevel"] 						= self.getIfinDict(camera[u"ispSettings"],u"irLedLevel")
					states[u"icrSensitivity"] 					= mapSensToLevel[self.getIfinDict(camera[u"ispSettings"],u"icrSensitivity")]
					states[u"isLedEnabled"] 					= self.getIfinDict(camera[u"ledSettings"],u"isEnabled")
					states[u"speakerVolume"] 					= int(self.getIfinDict(camera[u"speakerSettings"],u"volume", default=100))
					states[u"areSystemSoundsEnabled"] 			= self.getIfinDict(camera[u"speakerSettings"],u"areSystemSoundsEnabled", default=False)
					states[u"micVolume"] 						= int(self.getIfinDict(camera,u"micVolume", default=100))
					states[u"modelKey"] 						= self.getIfinDict(camera,u"modelKey")
					states[u"motionRecordingMode"] 				= self.getIfinDict(camera[u"recordingSettings"], u"mode")
					states[u"motionMinEventTrigger"] 			= self.getIfinDict(camera[u"recordingSettings"], u"minMotionEventTrigger")
					states[u"motionSuppressIlluminationSurge"] 	= self.getIfinDict(camera[u"recordingSettings"], u"suppressIlluminationSurge")
					states[u"motionUseNewAlgorithm"] 			= self.getIfinDict(camera[u"recordingSettings"], u"useNewMotionAlgorithm")
					states[u"motionAlgorithm"] 					= self.getIfinDict(camera[u"recordingSettings"], u"motionAlgorithm", default="-")
					states[u"motionEndEventDelay"] 				= float(self.getIfinDict(camera[u"recordingSettings"], u"endMotionEventDelay"))/1000.
					states[u"motionPostPaddingSecs"] 			= float(self.getIfinDict(camera[u"recordingSettings"], u"postPaddingSecs"))
					states[u"motionPrePaddingSecs"] 			= float(self.getIfinDict(camera[u"recordingSettings"], u"prePaddingSecs"))
					states[u"lastSeen"] 		= datetime.datetime.fromtimestamp(camera[u"lastSeen"]/1000.).strftime(u"%Y-%m-%d %H:%M:%S")
					states[u"lastRing"] 		= datetime.datetime.fromtimestamp(camera[u"lastRing"]/1000.).strftime(u"%Y-%m-%d %H:%M:%S")
					states[u"connectedSince"] 	= datetime.datetime.fromtimestamp(camera[u"connectedSince"]/1000.).strftime(u"%Y-%m-%d %H:%M:%S")
					#self.indiLOG.log(10,u"camid {}  states {}".format( states[u"id"] , states))
					devId = -1
					dev = ""
					if states[u"id"] not in self.PROTECT:
						try:
							devName = "Camera_Protect_"+states[u"name"] +"_"+MAC 
							dev = indigo.device.create(
								protocol		=indigo.kProtocol.Plugin,
								address			= states[u"MAC"],
								name 			= devName,
								description		="",
								pluginId		=self.pluginId,
								deviceTypeId	="camera_protect",
								props			={u"isProtectCamera":True, u"eventThumbnailOn":True, u"eventHeatmapOn":False, u"thumbnailwh":u"640/480", u"heatmapwh":u"320/240"
												, u"SupportsOnState":True, u"SupportsSensorValue":False , u"SupportsStatusRequest":False, u"AllowOnStateChange":False, u"AllowSensorValueChange":False
												},
								folder			=self.folderNameIDCreated,
								)
							devId = dev.id
							self.PROTECT[states[u"id"]] = {u"events":{}, u"devId":devId, u"devName":dev.name, u"MAC":states[u"MAC"] , "lastUpdate":time.time()}
						except	Exception, e:
							errtext = unicode(e)
							if errtext.find(u"None") == -1:
								self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, errtext))
								if "NameNotUniqueError" in errtext:
									self.indiLOG.log(20,u"error with : {}  will try to update the camera id in indigo device and continue, if the error percist, please delete device, will be re-created".format( devName ))
									dev = indigo.devices[devName]
									devId = dev.id
									self.PROTECT[states[u"id"]][u"devId"] = devId
								else:
									self.indiLOG.log(20,u"unknown error- please restart plugin, dev : {} / {}   internal list:{}".format( devName , states[u"id"], self.PROTECT))
									continue
							else:
								self.sleep(0.1)
								continue
					else:
						devId = self.PROTECT[states[u"id"]][u"devId"]
						dev = indigo.devices[devId]
					if devId ==-1:
						self.indiLOG.log(40,u"dev not found ")
						continue

					self.PROTECT[states[u"id"]][u"lastUpdate"] = time.time()

					if dev != "":
						for state in states:
							#self.indiLOG.log(10,u"checking dev {} state:{} := {}".format(dev.name, state, states[state]))
							if dev.states[state] != states[state]:
								self.addToStatesUpdateList(devId, state, states[state])

					else:
						try:
							dev = indigo.devices[devId]
							devId = dev.id
						except	Exception, e:
							if unicode(e).find(u"None") == -1:
								self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
								if unicode(e).find(u"timeout waiting") == -1: 
									if states[u"id"] in self.PROTECT:
										self.indiLOG.log(30,u" due to error removing cameraId: {}  from internal list:{}".format(states[u"id"], self.PROTECT[states[u"id"]]))
										del self.PROTECT[states[u"id"]]
								continue


				except	Exception, e:
					if unicode(e).find(u"None") == -1:
						self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

				# cleanup old devices not used
			if time.time() - self.lastRefreshProtect < 300:
				delList = {}
				for cameraId in self.PROTECT:
					delEvents = {}
					for eventID in self.PROTECT[cameraId][u"events"]:
						if ( time.time() - self.PROTECT[cameraId][u"events"][eventID][u"eventStart"] > 100 and 
							  self.PROTECT[cameraId][u"events"][eventID][u"eventEnd"]  == 0 ): delEvents[eventID] = 1

					for eventID in delEvents:
						del self.PROTECT[cameraId][u"events"][eventID]

					if self.PROTECT[cameraId][u"lastUpdate"] > 24*3600: # we have received no update in > 24 hour 
						try: 	dev = indigo.devices[self.PROTECT[states[u"id"]][u"devId"]]
						except:	delList[cameraId] =1

				for cameraId in delList:
					self.indiLOG.log(30,u"removing cameraId: {} from internal list:{} ,after > 24 hours w not activity and indigo dev does not exists either".format(cameraId, self.PROTECT[states[u"id"]]))
					del self.PROTECT[cameraId]

			self.executeUpdateStatesList()
			self.lastRefreshProtect  = time.time()
			#self.indiLOG.log(10,u"getProtectIntoIndigo: *********   elapsed time (2):{:.1f}".format(time.time() - elapsedTime))
	
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return



	####-----------------	 ---------
	####----- thread to get new events ever x secs   ------
	####-----------------	 ---------
	def getProtectEvents(self):# , startTime):
		self.indiLOG.log(10,u"getProtectEvents:  process starting")
		lastGetEvent = time.time()
		lastId = ""
		self.lastEvCheck = time.time()
		lastEvent = {}
		self.lastThumbnailTime = 0
		while True:
			try:
				refreshCameras = False
				if self.pluginState == u"stop" or self.protectThread[u"status"] == u"stop": 
					self.indiLOG.log(30,u"getProtectEvents: stopping process due to stop request")
					return  
				self.sleep(0.2)
				if self.PROTECT == {}: continue
				if time.time() - lastGetEvent < self.protecEventSleepTime: continue
				lastGetEvent	= time.time()

				endTime 		= int(time.time() * 1000)
				dataDict 		= {u"end": str(endTime+20), u"start": str( endTime - int(max(1,self.protecEventSleepTime)) *1000)}
				events = self.executeCMDOnController(dataSEND=dataDict, pageString=u"api/events/", jsonAction=u"protect", cmdType=u"get", protect=True)
				if False and self.decideMyLog(u"Protect"):  self.indiLOG.log(10,u"getProtectEvents: *********   get events elapsed time (1):{:.2f}, len(events):{} ".format(time.time() - elapsedTime, len(events) ))
				

				if not self.checkIfEmptyEventCleanup(events): 
					checkIds = self.loopThroughEvents(events)
				else:
					checkIds = {}

				self.getProtectEventPicsAndupdateDevices(checkIds)

				self.executeUpdateStatesList()

				if False and self.decideMyLog(u"Protect"): self.indiLOG.log(10,u"getProtectEvents: elapsed time (2):{:.1f}".format(time.time() - lastGetEvent))
					

			except	Exception, e:
				if unicode(e).find(u"None") == -1:
					self.indiLOG.log(40,u"getProtectEvents in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
					self.sleep(10)
		self.indiLOG.log(30,u"comsumeLogData:  stopping process (3)")
		return 

	####-----------------	 ---------
	####-----loop through new evenst and check if any new, changes  ------
	####-----------------	 ---------

	def loopThroughEvents(self, events):
		try:
			checkIds = {}
			if events == []: return checkIds 
			for event in events:
				dev = ""
				# first check if everything is here 
				if u"modelKey"				not in event: continue
				if event["modelKey"] != u"event": 		  continue
				if u"camera"				not in event: continue
				if u"id"					not in event: continue
				if u"start"					not in event: continue
				if u"end"					not in event: continue
				if u"thumbnail"				not in event: continue
				if u"type"					not in event: continue
				if u"smartDetectEvents"		not in event: continue
				if u"smartDetectTypes"		not in event: continue
				# ignore old events  !
				if time.time() - event[u"start"]/1000. > 60: continue  # ignore old events 

				## we have a complete event 

				newId = event[u"id"]

				updateDev = False
				cameraId = event[u"camera"]
				if cameraId not in self.PROTECT:
					self.lastRefreshProtect = time.time() - self.refreshProtectCameras + 2 
					continue

				debug = False
				#if cameraId == "604b049d0206a503e700d760":	debug = True

				#### ignore repeat event info ### start
				if self.PROTECT[cameraId][u"events"] != {}:
					if newId in self.PROTECT[cameraId][u"events"]:
						double = True
						for xx in event:
							if xx not in self.PROTECT[cameraId][u"events"][newId]["rawEvent"]:
								double = False
								break
							if  event[xx] != self.PROTECT[cameraId][u"events"][newId]["rawEvent"][xx]:
								double = False
								break
						if not double:
							self.PROTECT[cameraId][u"events"][newId]["rawEvent"] = copy.deepcopy(event)
					else:
						double = False

					if double: 
						if self.decideMyLog(u"Protect"):  
							#self.indiLOG.log(10,u"getProtectEvents: camID:{}, evId:{}; skipping = repeat event".format(cameraId, newId) )
							pass
						continue

				#### ignore repeat event info ### END

				if  debug or  self.decideMyLog(u"Protect"):
					xxx = copy.deepcopy(event)
					del xxx["camera"]
					del xxx["id"]
					self.indiLOG.log(10,u"getProtectEvents: camID:{}, evId:{}; event {}".format(cameraId, newId, xxx))

				smartDetect = ""

				## for the time being ignore list of smart detect events. this is a list of events to follow in the next event listings, we willl deal with them then
				if False and event[u"smartDetectEvents"] != []:
					if  debug or  self.decideMyLog(u"Protect"): self.indiLOG.log(10,u"getProtectEvents: camID:{}, evId:{}; skipping type:{}; smart:{}".format(cameraId, newId, event[u"type"], event[u"smartDetectEvents"]))
					continue


				## new event?
				if newId not in self.PROTECT[cameraId][u"events"]:
					self.PROTECT[cameraId][u"events"][newId] =  {u"eventStart":0, u"eventEnd":0, u"ringTime":0, u"eventType":"", u"thumbnailLastCopyTime": time.time() + 50, u"thumbnailCopied": False, u"status": "","rawEvent":copy.deepcopy(event)}
					if dev == "":
						dev = indigo.devices[self.PROTECT[cameraId][u"devId"]]
					if  debug or  self.decideMyLog(u"Protect"): self.indiLOG.log(10,u"getProtectEvents: camID:{}, evId:{}; {}: new event; type:{}".format(cameraId, newId, self.PROTECT[cameraId]["devName"], event[u"type"]))
					self.PROTECT[cameraId][u"events"][newId][u"eventStart"] 			= event[u"start"]/1000.
					self.PROTECT[cameraId][u"events"][newId][u"eventEnd"]    			= 0
					if self.copyProtectsnapshots == "on" or (self.copyProtectsnapshots == u"selectedByDevice" and "eventThumbnailOn" in props and props["eventThumbnailOn"] ):
						self.PROTECT[cameraId][u"events"][newId][u"thumbnailLastCopyTime"] 	= time.time() + 15 # try to get thumbnail in the next 15 secs
					else:
						self.PROTECT[cameraId][u"events"][newId][u"thumbnailLastCopyTime"] 	= time.time()      # no thumbnails to be copied

					self.PROTECT[cameraId][u"events"][newId][u"eventType"]				= event[u"type"]
					if event[u"type"] == u"ring": 
						self.PROTECT[cameraId][u"events"][newId][u"ringTime"] 			= event[u"start"]/1000.
					updateDev = True
					indigo.variable.updateValue(u"Unifi_Camera_with_Event", self.PROTECT[cameraId]["devName"])
					indigo.variable.updateValue(u"Unifi_Camera_Event_Date", datetime.datetime.now().strftime(u"%Y-%m-%d %H:%M:%S"))
					checkIds[newId] = cameraId
				

				if event[u"smartDetectEvents"] !=[]:
					for evID in event[u"smartDetectEvents"]:
						if evID in self.PROTECT[cameraId][u"events"]:
							checkIds[evID] = cameraId
							self.PROTECT[cameraId][u"events"][evID][u"eventEnd"] = time.time()
					if self.PROTECT[cameraId][u"events"][newId][u"eventEnd"] != 0:  self.PROTECT[cameraId][u"events"][newId][u"eventEnd"] = time.time()
					checkIds[newId] = cameraId

				# event ended, can be the same event as the start event ie rings?
				if self.PROTECT[cameraId][u"events"][newId][u"eventEnd"] < self.PROTECT[cameraId][u"events"][newId][u"eventStart"] and event[u"end"] is not None:
					if self.decideMyLog(u"Protect"): self.indiLOG.log(10,u"getProtectEvents: camID:{}, evId:{}; event ended devid:{}".format(cameraId, newId, self.PROTECT[cameraId][u"devId"]))
					self.PROTECT[cameraId][u"events"][newId][u"eventEnd"] = event[u"end"]/1000.
					checkIds[newId] = cameraId

				# other vent types?
				if event[u"type"] == u"disconnected":
					self.PROTECT[cameraId][u"events"][newId][u"eventStart"]  = event[u"start"]/1000.
					self.PROTECT[cameraId][u"events"][newId][u"eventEnd"]    = event[u"start"]/1000.+1
					checkIds[newId] = cameraId
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"getProtectEvents in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return checkIds


	####-----------------	 ---------
	####-----called to check if old events need to be expired / deleted ------
	####-----------------	 ---------
	def checkIfEmptyEventCleanup (self, events):
		try:
			if events != []: return False
			if time.time() - self.lastEvCheck < 10: return True
			self.lastEvCheck = time.time()

			# close old not updated status
			for cameraId in self.PROTECT:
				rmEvent ={}
				if self.PROTECT[cameraId]["devId"] < 1: continue

				for evId in self.PROTECT[cameraId][u"events"]:
					testEV = self.PROTECT[cameraId][u"events"][evId]
					if testEV[u"eventStart"]  == 0: 				continue
					if time.time() - testEV[u"eventStart"] < 40: 	continue # look only at older events 
					if testEV[u"eventType"]  == u"ring" and self.PROTECT[cameraId][u"events"][evId][u"status"] == "ring":
						dev = indigo.devices[self.PROTECT[cameraId]["devId"]]
						if dev.states["status"] == u"ring":
							if self.decideMyLog(u"Protect"): self.indiLOG.log(10,u"getProtectEvents: setting status to CONNECTED for expired ring event {}".format(self.PROTECT[cameraId][u"devName"], testEV[u"thumbnailCopied"]) )
							dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOn)
							self.addToStatesUpdateList(dev.id, u"status", u"CONNECTED")
							rmEvent[evId] = 1

					elif testEV[u"eventEnd"] == 0:
						dev = indigo.devices[self.PROTECT[cameraId]["devId"]]
						if dev.states[u"status"] == testEV[u"status"]:
							dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOn)
							if self.decideMyLog(u"Protect"): self.indiLOG.log(10,u"getProtectEvents: setting status to CONNECTED for expired not ended event {}, Thumbnailcopied:{}".format(self.PROTECT[cameraId][u"devName"], testEV[u"thumbnailCopied"]) )
							self.addToStatesUpdateList(dev.id, u"status", u"CONNECTED")
							rmEvent[evId] = 1

					if time.time() - testEV[u"eventStart"]  > 60: # remove rest of events from list after 1 minutes
						if self.decideMyLog(u"Protect"): self.indiLOG.log(10,u"getProtectEvents: removing old {}- event:{}, Thumbnailcopied:{}".format(self.PROTECT[cameraId][u"devName"], evId, testEV[u"thumbnailCopied"]) )
						rmEvent[evId] = 1

				for evId in rmEvent:
					del self.PROTECT[cameraId][u"events"][evId]
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"getProtectEvents in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return True


	####-----------------	 ---------
	####-----get thumbnails and update dev states ------
	####-----------------	 ---------
	def getProtectEventPicsAndupdateDevices (self, checkIds):
		try:
			if time.time() - self.lastThumbnailTime < 2 and checkIds == {}: return
			self.lastThumbnailTime = time.time() 
			debug = False
			# have to wait until end of event to get the thumbnail
			for cameraId in self.PROTECT:
				for evID in self.PROTECT[cameraId][u"events"]:
					#if self.decideMyLog(u"Protect"): self.indiLOG.log(10,u"getProtectEvents: camID:{}, evId:{}; evids check :{} eventEnd:{}; copied:{}".format(cameraId, newId, evID, self.PROTECT[cameraId][u"events"][evID][u"eventEnd"], self.PROTECT[cameraId][u"events"][evID][u"thumbnailLastCopyTime"]))
					if self.PROTECT[cameraId][u"events"][evID][u"eventEnd"] >0 or time.time() - self.PROTECT[cameraId][u"events"][evID][u"eventStart"] > 1.5:
						if time.time() - self.PROTECT[cameraId][u"events"][evID][u"thumbnailLastCopyTime"] < 0:
							checkIds[evID] = cameraId

			if False and self.decideMyLog(u"Protect"): self.indiLOG.log(10,u"getProtectEvents: check :{}".format(checkIds))
			for evID in checkIds:
				cameraId 	= checkIds[evID]
				protectEV 	= self.PROTECT[cameraId][u"events"][evID]
				smartDetect	= ""
				dev 		= ""
				eventJpeg	= ""
				status		= protectEV[u"eventType"]
				if protectEV["rawEvent"][u"smartDetectTypes"] != []:
					smartDetect = ",".join(protectEV["rawEvent"][u"smartDetectTypes"]).strip(",")
					if debug or self.decideMyLog(u"Protect"):  self.indiLOG.log(10,u"getProtectEvents: camID:{}, evId:{}; smartDetect-{} --> {}".format(cameraId, evID, protectEV["rawEvent"][u"smartDetectTypes"], smartDetect) )
					status = smartDetect

				if not protectEV[u"thumbnailCopied"] and ( time.time()-protectEV[u"thumbnailLastCopyTime"] < 0 and  protectEV["rawEvent"][u"thumbnail"] is not None and (time.time() - protectEV[u"eventStart"] > 5 or protectEV[u"eventEnd"] >0)):

					###  copy thumbnail to local indigo disk -----
					if self.PROTECT[cameraId][u"devId"] > 0:
						dev = indigo.devices[self.PROTECT[cameraId][u"devId"]]
						props = dev.pluginProps
						if u"eventThumbnailOn" in props and props[u"eventThumbnailOn"]:
							wh = props[u"thumbnailwh"].split("/")
							params = {"accessKey": "", "h": wh[1], "w": wh[0],}
							data = self.executeCMDOnController(dataSEND=params, pageString=u"api/thumbnails/{}".format(protectEV["rawEvent"][u"thumbnail"]), jsonAction=u"protect", cmdType=u"get", protect=True, raw=True, ignore40x=True)
							if  debug or self.decideMyLog(u"Protect"): self.indiLOG.log(10,u"getProtectEvents: camID:{}, evId:{}; getting thumbnail, datalen:{}; thumbnail: {}; devId:{}".format(cameraId, evID, len(data),  protectEV["rawEvent"][u"thumbnail"], self.PROTECT[cameraId][u"devId"]))
							if len(data) > 0:
								eventJpeg = self.changedImagePath.rstrip("/")+u"/"+dev.name+"_"+status+"_thumbnail.jpeg"
								f = open(eventJpeg,"wb")
								f.write(data)
								f.close()
								protectEV[u"thumbnailLastCopyTime"] = time.time()
								protectEV[u"thumbnailCopied"] = True
								indigo.variable.updateValue(u"Unifi_Camera_Event_PathToThumbnail", eventJpeg)
								indigo.variable.updateValue(u"Unifi_Camera_Event_DateOfThumbNail", datetime.datetime.now().strftime(u"%Y-%m-%d %H:%M:%S") )
	
							if protectEV[u"eventEnd"] == 0:  protectEV[u"eventEnd"] = time.time()

							## only do heatmaps when thumbnail is enabled too
							if False and u"eventHeatmapOn" in props and props[u"eventHeatmapOn"]:
								wh = props[u"heatmapwh"].split("/")
								params = {"accessKey": "", "h": wh[1], "w": wh[0],}
								data = self.executeCMDOnController(dataSEND=params, pageString=u"api/heatmaps/{}".format(protectEV["rawEvent"][u"heatmap"]), jsonAction=u"protect", cmdType=u"get", protect=True, raw=True, ignore40x=True)
								if len(data) > 0:
									f = open(self.changedImagePath.rstrip("/")+u"/"+dev.name+"_"+status+"_heatmap.jpeg","wb")
									f.write(data)
									f.close()


				status = protectEV[u"eventType"]
				if smartDetect != "":
					status = smartDetect

				if True:
					try:
						if dev == "":
							dev = indigo.devices[self.PROTECT[cameraId][u"devId"]]

						if protectEV[u"eventStart"] != 0: 
							evStart = datetime.datetime.fromtimestamp(protectEV[u"eventStart"]).strftime(u"%Y-%m-%d %H:%M:%S")
							if dev.states[u"eventStart"] != evStart:
								dev.updateStateImageOnServer(indigo.kStateImageSel.SensorTripped)
								self.addToStatesUpdateList(dev.id,u"eventStart", evStart)
								protectEV[u"status"] = status
								rgStart = datetime.datetime.fromtimestamp(protectEV[u"ringTime"]).strftime(u"%Y-%m-%d %H:%M:%S")
								if protectEV[u"ringTime"] != 0 and  rgStart != dev.states[u"lastRing"]:
									self.addToStatesUpdateList(dev.id,u"lastRing", rgStart)
									if self.decideMyLog(u"Protect"): self.indiLOG.log(10,u"getProtectEvents: camID:{}, evId:{}; setting status to ring, ".format(cameraId, evID))

								if status != dev.states[u"status"]: self.addToStatesUpdateList(dev.id, u"status", status)
								protectEV[u"status"] = status

								try: evN = int(dev.states[u"eventNumber"])
								except: evN = 0
								self.addToStatesUpdateList(dev.id,u"eventNumber", evN+1 )

					
						if protectEV[u"eventEnd"] != 0 and status != u"ring": 
							evEnd = datetime.datetime.fromtimestamp(protectEV[u"eventEnd"]).strftime(u"%Y-%m-%d %H:%M:%S")
							if dev.states[u"eventEnd"] != evEnd:
								if self.decideMyLog(u"Protect"): self.indiLOG.log(10,u"getProtectEvents: camID:{}, evId:{}; setting status to CONNECT, ".format(cameraId, evID))
								self.addToStatesUpdateList(dev.id, u"eventEnd", evEnd)
								dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOn)
								self.addToStatesUpdateList(dev.id, u"status", u"CONNECTED")
								protectEV[u"status"] = u"CONNECTED"

						dt = int(max(-1,protectEV[u"eventEnd"] - protectEV[u"eventStart"]))
						if dev.states[u"eventLength"] != dt:
							self.addToStatesUpdateList(dev.id, u"eventLength", dt )

						if eventJpeg != "" and eventJpeg != dev.states[u"eventJpeg"]:
							self.addToStatesUpdateList(dev.id, u"eventJpeg", eventJpeg )

						if protectEV[u"eventType"]  not in [u"", dev.states[u"eventType"]]:
							self.addToStatesUpdateList(dev.id, u"eventType", protectEV[u"eventType"] )

						if smartDetect != dev.states[u"smartDetect"]:
							self.addToStatesUpdateList(dev.id, u"smartDetect", smartDetect )

					except	Exception, e:
						if unicode(e).find(u"None") == -1:
							self.indiLOG.log(40,u"getProtectEvents in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"getProtectEvents in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return 


	####-----------------	 ---------
	####-----send commd parameters to cameras through protect ------
	####-----------------	 ---------
	def buttonSendCommandToProtectLEDCALLBACKaction (self, action1=None, filter="", typeId="", devId=""):
		return self.buttonSendCommandToProtectLEDCALLBACK(valuesDict= action1.props)
	def buttonSendCommandToProtectLEDCALLBACK(self, valuesDict=None, filter="", typeId="", devId="",returnCmd=False):
		try:
			area = u"ledSettings"
			payload ={area:{}}
			if valuesDict[u"blinkRate"]			!= u"-1": payload[area][u"blinkRate"] 		= int(valuesDict[u"blinkRate"])
			if valuesDict[u"camLEDenabled"]		!= u"-1": payload[area][u"isEnabled"] 		= valuesDict[u"camLEDenabled"] == "1"
			data = self.setupProtectcmd( valuesDict[u"cameraDeviceSelected"], payload)
			ok = True
			if area not in data: ok = False
			else:
				for xx in data[area]:
					if data[area][xx] != payload[area][x]: 
						ok = False
						break

			valuesDict[u"msg"] =  u"ok"  if ok else  u"error"
			if self.decideMyLog(u"Protect"): self.indiLOG.log(10,u"setupProtectcmd returned data: {} ".format(data[area]))
			self.addToMenuXML(valuesDict)
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"updateIndigoWithLogData in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return valuesDict


	####-----------------	 ---------
	def buttonSendCommandToProtectenableSpeakerCALLBACKaction (self, action1=None, filter="", typeId="", devId=""):
		return self.buttonSendCommandToProtectenableSpeakerCALLBACK(valuesDict= action1.props)
	def buttonSendCommandToProtectenableSpeakerCALLBACK(self, valuesDict=None, filter="", typeId="", devId="",returnCmd=False):
		self.addToMenuXML(valuesDict)
		try:
			"""
			"speakerSettings": {
				"areSystemSoundsEnabled": true, 
				"isEnabled": true, 
				"volume": 100
			}
			"""
			area = u"speakerSettings"
			payload ={area:{}}
			if valuesDict[u"areSystemSoundsEnabled"]	!= u"-1": payload[area][u"areSystemSoundsEnabled"] 	= valuesDict[u"areSystemSoundsEnabled"] == "1"
			if valuesDict[u"isEnabled"] 				!= u"-1": payload[area][u"isEnabled"] 				= valuesDict[u"isEnabled"] == "1"
			if valuesDict[u"volume"] 					!= u"-1": payload[area][u"volume"] 					= int(valuesDict[u"volume"])
			data = self.setupProtectcmd( valuesDict[u"cameraDeviceSelected"], payload)
			ok = True
			if area not in data: ok = False
			else:
				for xx in payload[area]:
					if data[area][xx] != payload[area][x]: 
						ok = False
						break

			valuesDict[u"msg"] =  u"ok"  if ok else  u"error"
			if self.decideMyLog(u"Protect"): self.indiLOG.log(10,u"setupProtectcmd returned data: {} ".format(data[area]))
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"updateIndigoWithLogData in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return valuesDict

	####-----------------	 ---------
	def buttonSendCommandToProtectmicVolumeCALLBACKaction (self, action1=None, filter="", typeId="", devId=""):
		return self.buttonSendCommandToProtectmicVolumeCALLBACK(valuesDict= action1.props)
	def buttonSendCommandToProtectmicVolumeCALLBACK(self, valuesDict=None, filter="", typeId="", devId="",returnCmd=False):
		try:
			self.addToMenuXML(valuesDict)
			if valuesDict[u"micVolume"] == u"-1":	return valuesDict
			area = u"micVolume"
			payload ={area:int(valuesDict[area])}
			data = self.setupProtectcmd(valuesDict[u"cameraDeviceSelected"],payload )
			ok = True
			if area not in data: ok = False
			if self.decideMyLog(u"Protect"): self.indiLOG.log(10,u"setupProtectcmd returned data: {} ".format(data[area]))
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"updateIndigoWithLogData in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return valuesDict

	####-----------------	 ---------
	def buttonSendCommandToProtectRecordCALLBACKaction (self, action1=None, filter="", typeId="", devId=""):
		return self.buttonSendCommandToProtectRecordCALLBACK(valuesDict= action1.props)

	def buttonSendCommandToProtectRecordCALLBACK(self, valuesDict=None, filter="", typeId="", devId="",returnCmd=False):
		try:
			"""
		  "recordingSettings": {
			"enablePirTimelapse": false, 
			"endMotionEventDelay": 3000, 
			"geofencing": "off", 
			"minMotionEventTrigger": 2000, 
			"mode": "motion", 				never, motion, always, smartDetect
			"motionAlgorithm": "stable", 
			"postPaddingSecs": 10, 
			"prePaddingSecs": 5, 
			"suppressIlluminationSurge": false, 
			"useNewMotionAlgorithm": false
		  }, 
			 {u'suppressIlluminationSurge': False, u'postPaddingSecs': 10, u'geofencing': u'off', u'motionAlgorithm': u'stable', u'prePaddingSecs': 1, u'enablePirTimelapse': False, u'minMotionEventTrigger': 0, u'mode': u'motion', u'useNewMotionAlgorithm': False, u'endMotionEventDelay': 3000} 
			"""
			area = u"recordingSettings"
			payload ={area:{}}
			if valuesDict[u"prePaddingSecs"] 				!= u"-1":	payload[area][u"prePaddingSecs"] 			= int(valuesDict[u"prePaddingSecs"])
			if valuesDict[u"postPaddingSecs"] 				!= u"-1":	payload[area][u"postPaddingSecs"] 			= int(valuesDict[u"postPaddingSecs"])
			if valuesDict[u"minMotionEventTrigger"] 		!= u"-1":	payload[area][u"minMotionEventTrigger"] 		= int(valuesDict[u"minMotionEventTrigger"])
			if valuesDict[u"motionRecordEnabledProtect"] 	!= u"-1":	payload[area][u"mode"] 						= valuesDict[u"motionRecordEnabledProtect"]
			if valuesDict[u"suppressIlluminationSurge"] 	!= u"-1":	payload[area][u"suppressIlluminationSurge"]	= valuesDict[u"suppressIlluminationSurge"]
			if valuesDict[u"useNewMotionAlgorithm"] 		!= u"-1":	payload[area][u"useNewMotionAlgorithm"] 		= valuesDict[u"useNewMotionAlgorithm"]
			if valuesDict[u"motionAlgorithm"] 				!= u"-1":	payload[area][u"motionAlgorithm"] 			= valuesDict[u"motionAlgorithm"]
			if valuesDict[u"endMotionEventDelay"] 			!= u"-1":	payload[area][u"endMotionEventDelay"] 		= valuesDict[u"endMotionEventDelay"]
			data = self.setupProtectcmd( valuesDict[u"cameraDeviceSelected"], payload)
			ok = True
			if area not in data: ok = False
			else:
				for xx in payload[area]:
					if data[area][xx] != payload[area][xx]: 
						ok = False
						break

			valuesDict[u"msg"] =  u"ok"  if ok else  u"error"
			if self.decideMyLog(u"Protect"): self.indiLOG.log(10,u"setupProtectcmd returned data: {} ".format(data[area]))

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"updateIndigoWithLogData in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		self.addToMenuXML(valuesDict)
		return valuesDict

	####-----------------	 ---------
	def buttonSendCommandToProtectIRCALLBACKaction (self, action1=None, filter="", typeId="", devId=""):
		return self.buttonSendCommandToProtectIRCALLBACK(valuesDict= action1.props)
	def buttonSendCommandToProtectIRCALLBACK(self, valuesDict=None, filter="", typeId="", devId="",returnCmd=False):
		try:
			"""
		  "ispSettings": {
			"aeMode": "auto", 
			"brightness": 50, 
			"contrast": 50, 
			"dZoomCenterX": 50, 
			"dZoomCenterY": 50, 
			"dZoomScale": 0, 
			"dZoomStreamId": 4, 
			"denoise": 50, 
			"focusMode": "ztrig", 
			"focusPosition": 0, 
			"hue": 50, 
			"icrSensitivity": 0, 
			"irLedLevel": 255, 
			"irLedMode": "auto", autoFilterOnly, on off
			"is3dnrEnabled": true, 
			"isAggressiveAntiFlickerEnabled": false, 
			"isAutoRotateEnabled": false, 
			"isExternalIrEnabled": false, 
			"isFlippedHorizontal": false, 
			"isFlippedVertical": false, 
			"isLdcEnabled": true, 
			"isPauseMotionEnabled": false, 
			"saturation": 50, 
			"sharpness": 50, 
			"touchFocusX": 0, 
			"touchFocusY": 0, 
			"wdr": 1, 
			"zoomPosition": 0
		  }, 


	09 11:37:20 setupProtectcmd  {'ispSettings': {'icrSensitivity': 1, 'irLedMode': u'autoFilterOnly', 'irLedLevel': 100}} , devid:1965914261, name:Camera_Protect_Reserve-UVC G3  Flex_7483C23FD3E5; id:603fe05602f2a503e70003f4
	09 11:37:20 setupProtectcmd returned data: {u'icrSensitivity': 1, u'sharpness': 50, u'isPauseMotionEnabled': False, u'isLdcEnabled': True, u'zoomPosition': 0, u'touchFocusX': 0, u'touchFocusY': 0, u'isAggressiveAntiFlickerEnabled': False, u'is3dnrEnabled': True, u'isExternalIrEnabled': False, u'denoise': 50, u'dZoomStreamId': 4, u'irLedLevel': 100, u'aeMode': u'auto', u'contrast': 50, u'dZoomScale': 0, u'hue': 50, u'saturation': 50, u'isFlippedHorizontal': False, u'focusPosition': 0, u'isAutoRotateEnabled': True, u'irLedMode': u'autoFilterOnly', u'focusMode': u'ztrig', u'isFlippedVertical': False, u'brightness': 50, u'wdr': 1, u'dZoomCenterX': 50, u'dZoomCenterY': 50} 
			"""

			area = u"ispSettings"
			payload ={area:{}}
			if valuesDict[u"irLedMode"] 		!= "-1":	payload[area][u"irLedMode"] 			= valuesDict[u"irLedMode"]
			if valuesDict[u"icrSensitivity"] 	!= "-1":	payload[area][u"icrSensitivity"] 	= int(valuesDict[u"icrSensitivity"])
			if valuesDict[u"irLedLevel"] 		!= "-1":	payload[area][u"irLedLevel"] 		= int(valuesDict[u"irLedLevel"])
			data = self.setupProtectcmd( valuesDict[u"cameraDeviceSelected"], payload)
			ok = True
			if area not in data: ok = False
			else:
				for xx in payload[area]:
					if data[area][xx] != payload[area][x]: 
						ok = False
						break

			valuesDict[u"msg"] =  u"ok"  if ok else  u"error"
			if self.decideMyLog(u"Protect"): self.indiLOG.log(10,u"setupProtectcmd returned data: {} ".format(data[area]))

			self.addToMenuXML(valuesDict)
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"updateIndigoWithLogData in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return valuesDict

####-----------------	 ---------
	def buttonrefreshProtectCameraSystemCALLBACK(self, valuesDict=None, filter="", typeId="", devId="",returnCmd=False):
		self.addToMenuXML(valuesDict)
		self.refreshProtectCameras = 0
		return valuesDict

	####-----------------	 ---------
	def buttonSendCommandToProtectgetSnapshotCALLBACKaction (self, action1=None, filter="", typeId="", devId=""):
		return self.buttonSendCommandToProtectgetSnapshotCALLBACK(valuesDict= action1.props)
	def buttonSendCommandToProtectgetSnapshotCALLBACK(self, valuesDict=None, filter="", typeId="", devId="",returnCmd=False):
		try:
			camId = valuesDict[u"cameraDeviceSelected"]
			wh = valuesDict[u"whofImage"].split("/")
			fName = valuesDict[u"fileNameOfImage"] 
			dev = indigo.devices[int(camId)]
			self.indiLOG.log(10,u"getSnapshot  dev {};  vd:{} ".format(dev.name, valuesDict))

			params = {
					u"accessKey": "",
					u"h": wh[1],
					u"ts": str(int(time.time())*1000),
					u"force": u"true",
					u"w": wh[0],
			}

			data = self.executeCMDOnController(dataSEND=params, pageString=u"api/cameras/{}/snapshot".format(dev.states[u"id"]), jsonAction=u"protect", protect=True, cmdType="get", raw=True)
			self.addToMenuXML(valuesDict)

			if len(data) < 10:
				self.indiLOG.log(10,u"getSnapshot  no data returned data length {} ".format(len(data)))
				return valuesDict
			if self.decideMyLog(u"Protect"): self.indiLOG.log(10,u"getSnapshot  writing data to {};  length {} ".format(fName, len(data)))
			f = open(fName,"wb")
			f.write(data)
			f.close()
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"updateIndigoWithLogData in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return valuesDict


	####-----------------	 ---------
	def setupProtectcmd(self, devId, payload,cmdType="patch"):

		dev = indigo.devices[int(devId)]
		try:
			if self.cameraSystem != u"protect":				return u"error protect not enabled"
			if self.decideMyLog(u"Protect"): self.indiLOG.log(10,u"setupProtectcmd  {} , devid:{}, name:{}; id:{}".format(payload, dev.id, dev.name, dev.states[u"id"]))
					
			data = self.executeCMDOnController(dataSEND=payload, pageString=u"cameras/{}".format(dev.states[u"id"]), jsonAction=u"protect", protect=True, cmdType=cmdType)
			self.lastRefreshProtect = time.time() - self.refreshProtectCameras +1
			return data
		except	Exception, e:
			self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))



	####-----------------  printGroups	  ---------
	def buttonConfirmPrintProtectDeviceInfoCALLBACK(self, valuesDict, typeId):
		try:
			self.lastRefreshProtect = 0
			self.getProtectIntoIndigo()
			#                1         2         3         4         5         6         7         8         9         10        11        12        13        14        15        16
			#       1234567891123456789212345678931234567894123456789512345678961234567897123456789812345678991234567890123456789012345678901234567890123456789012345678901234567890
			out  =u"Protect Camera devices      START =============================================================================================================================  \n"
			out +=u"                                                                                   ThumbNail     HeatMap       Device        Events----------------------------------- is   Volume- ir-LED----------------- stat  \n"
			out +=u"DevName---------------------- MAC#------------- ip#----------- DevType--- FWV----- On-resolutn   On-resolutn   lastSeen----- last-motion-- lastRing----- ---#of Mode   dark mic spk En  Sens Mode       Lvl LED  \n"
			mapTFtoenDis 	= {"":u"?", True:u"ena", False:u"dis"}
			mapTFtoNight 	= {"":u"?", True:u"Nite", False:u"Day"}
			mapirMode 		= {"":u"?", u"auto":u"auto", u"on":u"on", u"off":u"off", u"autoFilterOnly":u"a-Filt-Onl"}
			for dev in indigo.devices.iter(u"props.isProtectCamera"):
				props = dev.pluginProps
				cameraId = dev.states[u"id"] 
				out+= u"{:30s}".format(dev.name[:30])
				out+= u"{:18s}".format(dev.states[u"MAC"])
				out+= u"{:15s}".format(dev.states[u"ip"])
				out+= u"{:11s}".format(dev.states[u"type"][4:])
				out+= u"{:9s}".format(dev.states[u"firmwareVersion"])
				out+= u"{:3s}".format(mapTFtoenDis[props[u"eventThumbnailOn"]])
				out+= u"-{:10s}".format(props[u"thumbnailwh"])
				out+= u"{:3s}".format(mapTFtoenDis[props[u"eventHeatmapOn"]])
				out+= u"-{:10s}".format(props[u"heatmapwh"])
				out+= u"{:14s}".format(dev.states[u"lastSeen"][6:])
				out+= u"{:14s}".format(dev.states[u"eventStart"][6:])
				out+= u"{:13s}".format(dev.states[u"lastRing"][6:])
				out+= u"{:7d} ".format(dev.states[u"eventNumber"])
				out+= u"{:7s}".format(dev.states[u"motionRecordingMode"])
				out+= u"{:4s}".format(mapTFtoNight[dev.states[u"isDark"]])
				out+= u"{:4d}".format(dev.states[u"micVolume"])
				out+= u"{:4d}".format(dev.states[u"speakerVolume"])
				out+= u" {:4s}".format(mapTFtoenDis[dev.states[u"isExternalIrEnabled"]])
				out+= u"{:5}".format(dev.states[u"icrSensitivity"])
				out+= u"{:11s}".format(mapirMode[dev.states[u"irLedMode"]])
				out+= u"{:3d}".format(dev.states[u"irLedLevel"])
				out+= u" {:3}".format(mapTFtoenDis[dev.states[u"isLedEnabled"]])
				out +=u"  \n"
			out +=u"                                                                     =============================================================================================================================  \n"  
			out +=u"  \n"
			out+= u"================= INSTALL HELP =====================================  \n"
			out+= u"To setup: select the querry every time parametes etc  \n"
			out+= u"Currently the protect system must be on the same hardware as the controller eg cloudkey 2, UMDpro.    \n"
			out+= u"Once started the plugin will query(http) protect and will get all cameras installed and create the appropritate indigo devices    \n"
			out+= u"It then will query(http) the protect system for new events every x secs  \n"
			out+= u"The events can be of type Motion/Person/Vehicle/Ring. One physical ring can create several events  \n"
			out+= u"eg motion+person+ring in differnt sequences depending on how a person approaches the doorbell  \n"
			out+= u"Then for each event the variables  \n"
			out+= u"- Unifi_Camera_with_Event  \n"
			out+= u"- Unifi_Camera_Event_PathToThumbnail  \n"
			out+= u"- Unifi_Camera_Event_DateOfThumbNail  \n"
			out+= u"- Unifi_Camera_Event_Date  \n"
			out+= u"are updated as they come in. The event date is the first variable tio be updated, some of the other images can take several seconds to be produced.  \n"
			out+= u"You can trigger on any of these variables or on the device states: lastRing or eventStart. eventEnd is set when the event is over. In most cases the thumbnail should be ready.  \n"
			out+= u"  \n"
			out+= u"In menu / CAMERA - protect Info ...  \n"
			out+= u"you can print camera info to the logfile and  get a snap shot and set several parameetrs on the caameras  \n"
			out+= u"in actions you can setup most of the config as as well as get snapshots  \n"
			out +=u"  \n"
			out +=u"   uniFiAP                         Protect Camera devices      END   =============================================================================================================================  \n"  

			self.indiLOG.log(20,out)

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

	###########################################
	####------ camera PROTEC ---	-------END
	###########################################


	####-----------------	 ---------
	def doVDmessages(self, lines, ipNumber,apN ):

		part="doVDmessages"+unicode(random.random()); self.blockAccess.append(part)
		for ii in range(90):
				if len(self.blockAccess) == 0 or self.blockAccess[0] == part: break # my turn?
				self.sleep(0.1)
		if ii >= 89: self.blockAccess = [] # for safety if too long reset list

		dateUTC = datetime.datetime.utcnow().strftime("%Y%m%d")
		## self.myLog( text="utc time: " + dateUTC, mType = "MS-VD----")
		uType = "VDtail"

		try:
			for line in lines:
				if len(line) < 10: continue
				##if self.decideMyLog(u"Video"):	 self.myLog( text="msg: "+line,mType = "MS-VD----")
				#self.myLog( text=ipNumber+"     "+ line, mType = "MS-VD----")
				## this is an event tring:
				# logversion 1:
				###1524837857.747 2018-04-27 09:04:17.747/CDT: INFO   Camera[F09FC2C1967B] type:start event:105 clock:58199223 (UVC G3 Micro) in ApplicationEvtBus-15
				###1524837862.647 2018-04-27 09:04:22.647/CDT: INFO   Camera[F09FC2C1967B] type:stop event:105 clock:58204145 (UVC G3 Micro) in ApplicationEvtBus-18
				## new format logVersion 2:
				#1561518324.741 2019-06-25 22:05:24.741/CDT: INFO   [uv.analytics.motion] [AnalyticsService] [FCECDA1F1532|LivingRoom-Window-Flex] MotionEvent type:start event:1049 clock:111842854 in AnalyticsEvtBus-0

				itemsRaw = (line.strip()).split(" INFO ")
				if len(itemsRaw) < 2:
					#self.myLog( text=" INFO not found ",mType = "MS-VD----")
					continue


				try: timeSt= float(itemsRaw[0].split()[0])
				except:
					if self.decideMyLog(u"Video"):  self.indiLOG.log(10,u"MS-VD----  bad float")
					continue

				items= itemsRaw[1].strip().split()
				if len(items) < 5:
					self.indiLOG.log(10,u"MS-VD----  less than 5 items, line: "+line)
					continue

				logVersion = 0
				if items[0].find(u"Camera[") >-1: 			logVersion = 1
				elif itemsRaw[1].find(u"MotionEvent") >-1:	logVersion = 2
				else:
					if self.decideMyLog(u"Video"): self.indiLOG.log(10,u"MS-VD----  no Camera, line: {}".format(line) )
					continue

				if logVersion == 1:
					#Camera[F09FC2C1967B]
					c = items[0].split("[")[1].strip("]").lower()
					# clock:58199223 (UVC G3 Micro) in 
					cameraName	 = " ".join(items[4:]).split("(")[1].split(")")[0].strip()
				if logVersion == 2:
					# [mac|name]
					# [FCECDA1F1532|LivingRoom-Window-Flex] 
					xx = items[2].split("|")
					cameraName = xx[1].strip("]")
					c = xx[0].strip("[").lower()

				if len(c) < 12:
					if self.decideMyLog(u"Video"): self.indiLOG.log(10,u"MS-VD----  bad data, line: {}".format(line) )
					continue

				MAC = c[0:2]+":"+c[2:4]+":"+c[4:6]+":"+c[6:8]+":"+c[8:10]+":"+c[10:12]

				if self.testIgnoreMAC(MAC, fromSystem="doVDmsg"): continue

				evType = itemsRaw[1].split("type:")
				if len(evType) !=2: 
					if self.decideMyLog(u"Video"): self.indiLOG.log(10,u"MS-VD----   no    type, line: {}".format(line) )
					continue
				evType = evType[1].split()[0]

				if evType not in [u"start",u"stop"]:
					if self.decideMyLog(u"Video"): self.indiLOG.log(10,u"MS-VD----  bad eventType {}".format(evType) )
					continue


				event = itemsRaw[1].split(u"event:")
				if len(event) !=2: 
					if self.decideMyLog(u"Video"): self.indiLOG.log(10,u"MS-VD----   no    event, line: {}".format(line) )
					continue
				evNo = int(event[1].split()[0])


				if self.decideMyLog(u"Video"): self.indiLOG.log(10,u"MS-VD----  parsed items: #{:5d}  {}    {:13.1f}  {} {}".format(evNo, evType, timeSt, MAC, cameraName) )


				if MAC not in self.cameras:
					 self.cameras[MAC] = {"cameraName":cameraName,"events":{},"eventsLast":{"start":0,"stop":0},"devid":-1,"uuid":"", "ip":"", "apiKey":""}

				if evNo not in	self.cameras[MAC][u"events"]:
					self.cameras[MAC][u"events"][evNo] = {u"start":0,u"stop":0}


				if len(self.cameras[MAC][u"events"]) > self.unifiVIDEONumerOfEvents:
					delEvents={}
					for ev in self.cameras[MAC][u"events"]:
						try:
							if int(evNo) - int(ev) > self.unifiVIDEONumerOfEvents:
								delEvents[ev]=True
						except:
							self.indiLOG.log(40,u"doVDmessages error in ev# {};	  evNo {};	 maxNumberOfEvents: {}\n to fix:  try to rest event count ".format(ev, evNo, self.unifiVIDEONumerOfEvents) )



					if len(delEvents) >0:
						if self.decideMyLog(u"Video"): self.indiLOG.log(10,u"MS-VD----  {} number of events > {}; deleting {} events".format(cameraName, self.unifiVIDEONumerOfEvents, len(delEvents)) )
						for ev in delEvents:
							del	 self.cameras[MAC][u"events"][ev]

				self.cameras[MAC][u"events"][evNo][evType]  = timeSt
				##if self.decideMyLog(u"Video"): self.myLog( text=unicode(self.cameras[MAC]) , mType = "MS-VD----")


				devFound = False
				if u"devid" in self.cameras[MAC]:
					try:
						dev = indigo.devices[self.cameras[MAC][u"devid"]]
						devFound = True
					except: pass
				if	not devFound:
					for dev in indigo.devices.iter(u"props.isCamera"):
						if u"MAC" not in dev.states:	   continue
						#self.myLog( text=" testing "+ dev.name+"  "+ dev.states[u"MAC"] +"    " + MAC)
						if dev.states[u"MAC"] == MAC:
							devFound = True
							#self.myLog( text="           ... found")
							break

				if not devFound:
					try:
						dev = indigo.device.create(
							protocol		=indigo.kProtocol.Plugin,
							address			=MAC,
							name 			= "Camera_"+cameraName+"_"+MAC ,
							description		="",
							pluginId		=self.pluginId,
							deviceTypeId	="camera",
							props			={"isCamera":True},
							folder			=self.folderNameIDCreated,
							)
						dev.updateStateOnServer("MAC", MAC)
						dev.updateStateOnServer("eventNumber", -1)
						props = dev.pluginProps
						props[u"isCamera"] = True
						dev.replacePluginPropsOnServer()
						dev = indigo.devices[dev.id]
						self.saveCameraEventsStatus = True
					except	Exception, e:
							if unicode(e).find(u"None") == -1:
								self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
							if u"NameNotUniqueError" in unicode(e):
								dev = indigo.devices[u"Camera_"+cameraName+"_"+MAC]
								self.indiLOG.log(10,u"states  "+ unicode(dev.states))
								dev.updateStateOnServer("MAC", MAC)
								dev.updateStateOnServer("eventNumber", -1)
								props = dev.pluginProps
								props[u"isCamera"] = True
								dev.replacePluginPropsOnServer()
								dev = indigo.devices[dev.id]

							continue
					indigo.variable.updateValue(u"Unifi_New_Device", u"{}/{}".format(dev.name, MAC) )
					self.pendingCommand.append("getConfigFromNVR")

				self.cameras[MAC][u"devid"] = dev.id

				##if self.decideMyLog(u"Video"): self.myLog( text=ipNumber+"    listenStart: "+ unicode(self.listenStart), mType = "MS-VD----")
				if dev.states[u"eventNumber"] > evNo or ( self.cameras[MAC][u"events"][evNo][evType] <= self.cameras[MAC][u"eventsLast"][evType]) :
					try:
						if time.time() - self.listenStart[ipNumber][uType] > 30:
							self.indiLOG.log(10,u"MS-VD----  "+"rejected event number "+ unicode(evNo)+" resetting event No ; time after listener lauch: %5.1f"%(time.time() - self.listenStart[ipNumber][uType]))
							self.addToStatesUpdateList(dev.id,u"eventNumber", evNo)
					except	Exception, e:
							self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
							self.indiLOG.log(40,u"rejected event dump  "+ipNumber+"    " + unicode(self.listenStart))
							self.addToStatesUpdateList(dev.id,u"eventNumber", evNo)


				if self.decideMyLog(u"Video"): self.indiLOG.log(10,u"MS-VD----  "+"event # "+ unicode(evNo)+" accepted ; delta T from listener lauch: %5.1f"%(time.time() - self.listenStart[ipNumber][uType]))
				dateStr = time.strftime(u"%Y-%m-%d %H:%M:%S",time.localtime(timeSt))
				if evType == "start":
					self.addToStatesUpdateList(dev.id,u"lastEventStart", dateStr )
					self.addToStatesUpdateList(dev.id,u"status", "REC")
					if self.imageSourceForEvent == "imageFromNVR":
						if dev.states[u"eventJpeg"] != self.changedImagePath+dev.name+".jpg": # update only if new
							self.addToStatesUpdateList(dev.id,"eventJpeg",self.changedImagePath+dev.name+"_event.jpg")
						self.getSnapshotfromNVR(dev.id, self.cameraEventWidth, self.changedImagePath+dev.name+"_event.jpg")
					if self.imageSourceForEvent == "imageFromCamera":
						if dev.states[u"eventJpeg"] != self.changedImagePath+dev.name+".jpg": # update only if new
							self.addToStatesUpdateList(dev.id,"eventJpeg",self.changedImagePath+dev.name+"_event.jpg")
						self.getSnapshotfromCamera(dev.id, self.changedImagePath+dev.name+"_event.jpg")

				elif evType == "stop":
					self.addToStatesUpdateList(dev.id,u"lastEventStop", dateStr )
					self.addToStatesUpdateList(dev.id,u"status", "off" )
					evLength  = float(self.cameras[MAC][u"events"][evNo][u"stop"]) - float(self.cameras[MAC][u"events"][evNo][u"start"])
					self.addToStatesUpdateList(dev.id,u"lastEventLength", int(evLength))

					try:
						if self.imageSourceForEvent == "imageFromDirectory":
							if dev.states[u"uuid"] !="":
								year = dateUTC[0:4]
								mm	 = dateUTC[4:6]
								dd	 = dateUTC[6:8]

								fromDir	   = self.videoPath+dev.states[u"uuid"]+"/"+year+"/"+mm+"/"+dd+"/meta/"
								toDir	   = self.changedImagePath
								last	   = 0.
								newestFile = ""
								filesInDir = ""

								if not os.path.isdir(fromDir):
										if not os.path.isdir(self.videoPath+dev.states[u"uuid"]):						os.mkdir(self.videoPath+dev.states[u"uuid"])
										if not os.path.isdir(self.videoPath+dev.states[u"uuid"]+"/"+year):				os.mkdir(self.videoPath+dev.states[u"uuid"]+"/"+year)
										if not os.path.isdir(self.videoPath+dev.states[u"uuid"]+"/"+year+"/"+mm):		os.mkdir(self.videoPath+dev.states[u"uuid"]+"/"+year+"/"+mm)
										if not os.path.isdir(self.videoPath+dev.states[u"uuid"]+"/"+year+"/"+mm+"/"+dd): os.mkdir(self.videoPath+dev.states[u"uuid"]+"/"+year+"/"+mm+"/"+dd)
										if not os.path.isdir(fromDir):													os.mkdir(fromDir)

								for testFile in os.listdir(fromDir):
									if testFile.find(u".jpg") == -1: continue
									timeStampOfFile = os.path.getmtime(os.path.join(fromDir, testFile))
									if	timeStampOfFile > last:
										last = timeStampOfFile
										newestFile = testFile
								if newestFile =="":
									if self.decideMyLog(u"Video"): self.indiLOG.log(10,u"MS-VD-EV-  {}  no file found".format(dev.name))
									continue

								if dev.states[u"eventJpeg"] != fromDir+newestFile: # update only if new
									self.addToStatesUpdateList(dev.id,"eventJpeg",fromDir+newestFile)
									if os.path.isdir(toDir): # copy to destination directory
										if os.path.isfile(fromDir+newestFile):
											cmd = "cp '"+fromDir+newestFile+"' '"+toDir+dev.name+"_event.jpg' &"
											if self.decideMyLog(u"Video"): self.indiLOG.log(10,u"MS-VD-EV-  copy event file: {}".format(cmd))
											subprocess.Popen(cmd,shell=True)
									else:
										if self.decideMyLog(u"Video"): self.indiLOG.log(10,u"MS-VD-EV-  "+u"path "+ self.changedImagePath+u"     does not exist.. no event files copied")

					except	Exception, e:
							if unicode(e).find(u"None") == -1:
								self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

				self.cameras[MAC][u"eventsLast"] = copy.copy(self.cameras[MAC][u"events"][evNo])
				self.addToStatesUpdateList(dev.id,u"eventNumber", int(evNo) )
				self.executeUpdateStatesList()

		except	Exception, e:
				if unicode(e).find(u"None") == -1:
					self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

		if len(self.blockAccess)>0:	 del self.blockAccess[0]
		return



	####-----------------	 ---------
	def doGWmessages(self, lines,ipNumber,apN):
		try:
			devType	 = u"UniFi"
			isType	 = u"isUniFi"
			devName	 = u"UniFi"
			suffixN	 = u"DHCP"
			xType	 = u"UN"

			part="doGWmessages"+unicode(random.random()); self.blockAccess.append(part)
			for ii in range(90):
				if len(self.blockAccess) == 0 or self.blockAccess[0] == part: break # my turn?
				self.sleep(0.1)
			if ii >= 89: self.blockAccess = [] # for safety if too long reset list

# looking for dhcp refresh requests
#  Oct 26 22:20:00 GW sudo:		root : TTY=unknown ; PWD=/ ; USER=root ; COMMAND=/bin/sh -c echo -e '192.168.1.180\t iPhone.localdomain\t #on-dhcp-event 18:65:90:6a:b9:c' >> /etc/hosts

			tag = "TTY=unknown ; PWD=/ ; USER=root ; COMMAND=/bin/sh -c echo -e '"
			for line in lines:
				if len(line) < 10: continue
				if line.find(tag) ==-1: continue
				if self.decideMyLog(u"LogDetails"): self.indiLOG.log(10,u"MS-GW---   "+line )
				items	= line .split(tag)
				if len(items) !=2: continue
				items	= items[1].split("' >> /etc/hosts")
				if len(items) != 2: continue
				items	= items[0].split("\\t")
				if len(items) != 3: continue
				ip		= items[0]
				name	= items[1]
				items	= items[2].split()
				if len(items) != 2: continue

				MAC = self.checkMAC(items[1])# fix a bug in hosts file
				if self.testIgnoreMAC(MAC, fromSystem="GW-msg"): continue

				new = True
				if MAC in self.MAC2INDIGO[xType]:
					try:
						dev = indigo.devices[self.MAC2INDIGO[xType][MAC][u"devId"]]
						if dev.deviceTypeId != devType: 1/0
						new = False
					except:
						if self.decideMyLog(u"LogDetails", MAC=MAC): self.indiLOG.log(10,MAC + "  " + unicode(self.MAC2INDIGO[xType][MAC][u"devId"]) + " wrong " + devType)
						for dev in indigo.devices.iter(u"props."+isType):
							if u"MAC" not in dev.states: continue
							if dev.states[u"MAC"] != MAC: continue
							self.MAC2INDIGO[xType][MAC]={}
							self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
							self.MAC2INDIGO[xType][MAC][u"devId"] = dev.id
							new = False
							break
						del self.MAC2INDIGO[xType][MAC]
				if not new:
					props=dev.pluginProps
					new = False
					if dev.states[u"ipNumber"] != ip:
						self.addToStatesUpdateList(dev.id,u"ipNumber", ip)
					## if a device asks for dhcp extension, it must be alive,  good for everyone..
					if True: #  Always true, if active request to renew DHCP, must be present  "useWhatForStatus" in props and props[u"useWhatForStatus"].find(u"DHCP") >-1:
						if dev.states[u"status"] != u"up":
							self.setImageAndStatus(dev, u"up",oldStatus= dev.states[u"status"],ts=time.time(), level=1, text1=  dev.name.ljust(30) +u"  status up        GW-DHCP renew request", iType=u"STATUS-DHCP",reason=u"MS-DHCP "+u"up")
						else:
							if self.decideMyLog(u"LogDetails", MAC=MAC): self.indiLOG.log(10,u"MS-GW-DHCP {} restarting expTimer due to DHCP renew request from device".format(MAC) )
						self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()

					#break

				if new and not self.ignoreNewClients:
					try:
						dev = indigo.device.create(
							protocol		=indigo.kProtocol.Plugin,
							address			=MAC,
							name			=devName+"_" + MAC,
							description		=self.fixIP(ip),
							pluginId		=self.pluginId,
							deviceTypeId	=devType,
							folder			=self.folderNameIDCreated,
							props			={u"useWhatForStatus":"DHCP","useAgeforStatusDHCP":"-1",isType:True})
					except	Exception, e:
						if unicode(e).find(u"None") == -1:
							self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
						continue
					self.setupStructures(xType, dev, MAC)
					self.setupBasicDeviceStates(dev, MAC, "UN", "", "", "", u" status up       GW msg new device", "STATUS-DHCP")
					self.executeUpdateStatesList()
					dev = indigo.devices[dev.id]
					self.setupStructures(xType, dev, MAC)
					indigo.variable.updateValue(u"Unifi_New_Device",u"{}/{}/{}".format(dev.name, MAC, ip) )

			self.executeUpdateStatesList()
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

		self.executeUpdateStatesList()

		if len(self.blockAccess)>0:	 del self.blockAccess[0]


		return


	####-----------------	 ---------
	def doSWmessages(self, lines, ipNumber,apN ):
		return

		part="doSWmessages"+unicode(random.random()); self.blockAccess.append(part)
		for ii in range(90):
				if len(self.blockAccess) == 0 or self.blockAccess[0] == part: break # my turn?
				self.sleep(0.1)
		if ii >= 89: self.blockAccess = [] # for safety if too long reset list

		try:
			for line in lines:
				if len(line) < 2: continue
				if self.decideMyLog(u"Log"): self.indiLOG.log(10,u"MS-SW---   "+ipNumber+"    " + line)


		except	Exception, e:
				if unicode(e).find(u"None") == -1:
					self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

		if len(self.blockAccess)>0:	 del self.blockAccess[0]
		return


	####-----------------	 ---------
	def doAPmessages(self, lines, ipNumberAP, apN, webApiLog=False):

		try:
			part="doAPmessages"+unicode(random.random()); self.blockAccess.append(part)
			for ii in range(90):
					if len(self.blockAccess) ==0 or self.blockAccess[0]==part:
						break
					self.sleep(0.1)
			if ii >= 89: self.blockAccess = [] # for safety if too long reset list

			devType = "UniFi"
			isType	= "isUniFi"
			devName = "UniFi"
			suffixN	 = "WiFi"
			xType	=  u"UN"


			for line in lines:
				MAC = ""
				GHz = ""
				up = False
				token = ""
				if webApiLog: # message from UDM re-packaged as AP message
					MAC = line[u"user"]
					up = True
					token = "steady"
					if line[u"key"].lower().find(u"disconnected") >-1:
						token = "DISCONNECTED"
						up = False
					if line[u"key"].lower().find(u"disassociated") >-1:
						token = "DISCONNECTED"
						up = False

					#### roaming:::::
					elif line[u"key"].lower().find(u"roam") >-1:
						if  "IP_to" in line and "IP_from" in line:
							if line[u"IP_to"] !="" and line[u"IP_from"] !="":
								self.HANDOVER[MAC] = {"tt":line[u"time"],"ipNumberNew": line[u"IP_to"], "ipNumberOld": line[u"IP_from"]}
								token = "roam"
							else:
								if self.decideMyLog(u"UDM", MAC=MAC):self.indiLOG.log(10,u"MS-AP-WB-E {} roam data wrong (IP_from/to empty) event:{}; ".format(MAC, line))
						elif  "channel_from" in line or "channel_to" in line: # this is just change of channel, no real roaming to other AP
							pass 
						else:
							if self.decideMyLog(u"UDM", MAC=MAC):self.indiLOG.log(10,u"MS-AP-WB-E {} roam data wrong (IP_from/to missing) event:{}; ".format(MAC, line))

					else:
						pass

					GHz = "2"
					if u"channel"    in line and int(line[u"channel"])    >= 12:	GHz = "5"
					if u"channel_to" in line and int(line[u"channel_to"]) >= 12:	GHz = "5"
					timeOfMSG = line[u"time"]
					if self.decideMyLog(u"UDM", MAC=MAC):self.indiLOG.log(10,u"MS-AP-WB-0 {};  ipNumberAP:{};  GHz:{}; up:{} token:{}, dTime:{:.1f}; api-event:{}; ".format( MAC, ipNumberAP, GHz, up, token, time.time()-timeOfMSG, line))

				else: # regular ap message
					if len(line) < 2: continue
					tags = line.split()
					MAC = ""

					ll = line.find(u"[HANDOVER]") + 10 +1 ## len of [HANDOVER] + one space
					if ll  > 30:
						if ll+17  >=  len(line):	 					 continue  # 17 = len of MAC address
						lin2 = line.split("[HANDOVER]")[1]
						tags = lin2.split()
						if len(tags) !=5: 								 continue
						MAC = tags[0]
						if not self.isValidMAC(MAC):					 continue
						if self.testIgnoreMAC(MAC, fromSystem="AP-msg"): continue

						ipNumber = tags[4]	# new IP number of target AP
						self.HANDOVER[MAC] = {"tt":time.time(),"ipNumberNew":ipNumber, "ipNumberOld":tags[2]}
							### handle this: [HANDOVER]
							#13:40:42 AP----	  -192.168.1.4	Apr 16 13:40:41 4-kons daemon.notice hostapd: ath0: IEEE 802.11 UBNT-ROAM.get-sta-data for 18:65:90:6a:b9:0c
							#13:40:42 AP----	  -192.168.1.4	Apr 16 13:40:41 4-kons user.info kernel: [92232.074000] ubnt_roam [BASIC]:[HANDOVER] 18:65:90:6a:b9:0c from 192.168.1.4 to 192.168.1.5
							#13:40:42 AP----	  -192.168.1.4	Apr 16 13:40:41 4-kons daemon.notice hostapd: ath0: IEEE 802.11 UBNT-ROAM.sta-leave: 18:65:90:6a:b9:0c
							#13:40:42 AP----	  -192.168.1.4	Apr 16 13:40:41 4-kons daemon.info hostapd: ath0: STA 18:65:90:6a:b9:0c IEEE 802.11: disassociated
							#13:40:42 MS-AP-WiFi -	AP message received 18:65:90:6a:b9:0c  UniFi-iphone7-karl;	old/new associated 192.168.1.4/192.168.1.4
							#13:40:42 MS-AP-WiFi - 18:65:90:6a:b9:0c UniFi-iphone7-karl				check timer,  down token: disassociated time.time() -upt 1492368042.1

					###	 add test for :
					# 13:22:58 AP----	   -192.168.1.4	 Apr 15 13:22:57 4-kons user.info kernel: [ 4766.438000] ubnt_roam [BASIC]:Presence at AP 192.168.1.5 verified for 18:65:90:6a:b9:0c
					elif line.find(u"Presence at AP") > -1 and line.find(u"verified for") > -1:
						MAC = tags[-1]
						if not self.isValidMAC(MAC):					 continue
						ipNumberAP = tags[-4]

					elif line.find(u"EVENT_STA_JOIN ") > -1 and line.find(u"verified for") > -1:
							ipNumberAP = tags[-4]

					else:
						try:
							ll = tags.index("STA")
							if ll+1 >=	len(tags):				 		continue
							MAC = tags[ll + 1]
							if not self.isValidMAC(MAC):
								continue
							if	line.find(u"Authenticating") > 10:
								continue
							if	line.find(u"STA Leave!!") != -1 :
								continue
							if	line.find(u"STA enter") != -1:
								continue
						except Exception, e:
							if unicode(e).find(u"not in list") >-1: 		continue
							self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
							continue

					up = True
					token = ""
					if line.lower().find(u"disassociated") > -1:
						token = "disassociated"
						up = False
					elif line.lower().find(u"disconnected") > -1:
						token = "DISCONNECTED"
						up = False
					elif line.find(u" sta_stats") > -1:
						token = "sta_stats"
						up = False
					if line.find(u"ath0:") > -1: GHz = "5"
					if line.find(u"ath1:") > -1: GHz = "2"
					timeOfMSG = time.time()

					if self.decideMyLog(u"LogDetails", MAC=MAC):self.indiLOG.log(10,u"MS-AP-WF-0 {:13s}#{}; {};  GHz:{}; up:{} token:{}, log-event:{}".format( ipNumberAP,apN, MAC , GHz, up, token, line))

				if self.testIgnoreMAC(MAC, fromSystem="AP-msg"): continue


				if MAC != "":

					if MAC in self.HANDOVER:
						if time.time() - self.HANDOVER[MAC][u"tt"] <1.3: # protect for 1+ secs when in handover mode
							ipNumber = self.HANDOVER[MAC][u"ipNumberNew"]
							up = True
						else:
							del self.HANDOVER[MAC]

					new = True
					if MAC in self.MAC2INDIGO[xType]:
						try:
							dev = indigo.devices[self.MAC2INDIGO[xType][MAC][u"devId"]]
							new = False
						except:
							if self.decideMyLog(u""): self.indiLOG.log(10,u"{}     {} wrong {}".format(MAC, self.MAC2INDIGO[xType][MAC][u"devId"], devType) )
							for dev in indigo.devices.iter(u"props."+isType):
								if u"MAC" not in dev.states:		 continue
								if dev.states[u"MAC"] != MAC:	 continue
								self.MAC2INDIGO[xType][MAC]={}
								self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
								self.MAC2INDIGO[xType][MAC][u"devId"] = dev.id
								self.MAC2INDIGO[xType][MAC][u"lastAPMessage"] = timeOfMSG
								new = False
								break

					if not new:
						props =	 dev.pluginProps
						devId = unicode(dev.id)
						if devId not in self.upDownTimers:
							self.upDownTimers[devId] = {u"down": 0, u"up": 0}

						if u"lastAPMessage" not in self.MAC2INDIGO[xType][MAC]: self.MAC2INDIGO[xType][MAC][u"lastAPMessage"] = 0
						if timeOfMSG - self.MAC2INDIGO[xType][MAC][u"lastAPMessage"] < -2: 
							if self.decideMyLog(u"LogDetails", MAC=MAC): self.indiLOG.log(10,u"MS-AP-WF-1 ..ignore msg, older than last AP message; lastMSG:{:.1f}, thisMSG:{:.1f}".format(self.MAC2INDIGO[xType][MAC][u"lastAPMessage"],timeOfMSG ) )
							continue

						oldIP = dev.states[u"AP"]
						if ipNumberAP != "" and ipNumberAP != oldIP.split(u"-")[0]:
							if up:
								self.addToStatesUpdateList(dev.id,u"AP", ipNumberAP+u"-#"+unicode(apN))
							else:
								if self.decideMyLog(u"LogDetails", MAC=MAC): self.indiLOG.log(10,u"MS-AP-WF-2  .. old->new associated AP {}->{}-{} not setting to down, as associated to old AP".format( oldIP, ipNumberAP, apN))
								continue


						if u"useWhatForStatus" in props and props[u"useWhatForStatus"].find(u"WiFi") > -1:

							if self.decideMyLog(u"LogDetails", MAC=MAC): self.indiLOG.log(10,u"MS-AP-WF-3  .. old->new associated {}->{}#{}".format( oldIP, ipNumberAP, apN) )

							if up: # is up now
								self.MAC2INDIGO[xType][MAC][u"idleTime" + suffixN] = 0
								self.upDownTimers[devId][u"down"] = 0
								self.upDownTimers[devId][u"up"] = time.time()
								if dev.states[u"status"] != u"up":
									if self.decideMyLog(u"LogDetails", MAC=MAC): self.indiLOG.log(10,u"MS-AP-WF-4  .. ipNumberAP:{} 'setting state to UP' from:{}".format( ipNumberAP, dev.states[u"status"]))
									self.setImageAndStatus(dev, "up",oldStatus= dev.states[u"status"], ts=time.time(), level=1, text1= u"{:30s} status up  AP message received >{}<".format(dev.name,ipNumberAP), iType=u"MS-AP-WF-4 ",reason=u"MSG WiFi "+u"up")
								if self.decideMyLog(u"Logic", MAC=MAC): self.indiLOG.log(10,u"MS-AP-WF-R   ==> restart exptimer use AP log-msg, exp-time left:{:5.1f}".format(self.getexpT(props) -(time.time()-self.MAC2INDIGO[xType][MAC][u"lastUp"]) ))
								self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()

							else: # is down now
								try:
									if devId not in self.upDownTimers:
										self.upDownTimers[devId] = {u"down": 0, u"up": 0}

									if ipNumberAP == "" or ipNumberAP == oldIP.split(u"-")[0]: # only if its on the same current AP
										dt = (time.time() - self.upDownTimers[devId][u"up"])

										if u"useWhatForStatusWiFi" in props and props[u"useWhatForStatusWiFi"] in [u"FastDown",u"Optimized"]:
											if self.decideMyLog(u"LogDetails", MAC=MAC): self.indiLOG.log(10,u"MS-AP-WF-5  .. checking timer,   token:down;  tt-uptDelay:{:4.1f}".format(dt) )
											if dt > 5.0 and (props[u"useWhatForStatusWiFi"] == "FastDown" or (time.time() - self.MAC2INDIGO[xType][MAC][u"lastUp"]) > self.getexpT(props) ):
												if dev.states[u"status"] == u"up":
													#self.myLog( text=u" apmsg dw "+ dev.name+u" changed: old status: "+dev.states[u"status"]+u"; new	down")
													if props[u"useWhatForStatusWiFi"] == u"FastDown":  # in fast down set it down right now
														self.setImageAndStatus(dev, u"down",oldStatus=u"up", ts=time.time(), level=1, text1=MAC +u", "+ dev.name.ljust(30)+u" status down    AP message received fast down-", iType=u"MS-AP-WF-5 ",reason=u"MSG FAST down")
														self.upDownTimers[devId][u"down"] = time.time()
													else:  # in optimized give it 3 more secs
														self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time() - self.getexpT(props) + 3
														self.upDownTimers[devId][u"down"] = time.time() + 3
													self.upDownTimers[devId][u"up"]	  = 0.

										elif dt > 2.:
											if self.decideMyLog(u"LogDetails", MAC=MAC): self.indiLOG.log(10,u"MS-AP-WF-6  .. ipNumberAP:{} 'delay settings updown timer < 2; set uptimer =0, downtimer =tt'".format( ipNumberAP))
											self.upDownTimers[devId][u"down"] =	 time.time()  # this is a down message
											self.upDownTimers[devId][u"up"]	  = 0.
								except	Exception, e:
									if unicode(e).find(u"None") == -1:
										self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))


						if self.updateDescriptions:
							if dev.description.find(u"=WiFi")==-1 and  len(dev.description) >2:
								dev.description = dev.description+u"=WiFi"
								dev.replaceOnServer()


					if new and not self.ignoreNewClients:
						try:

							dev = indigo.device.create(
								protocol		=indigo.kProtocol.Plugin,
								address			=MAC,
								name			=devName+"_" + MAC,
								description		="",
								pluginId		=self.pluginId,
								deviceTypeId	=devType,
								folder			=self.folderNameIDCreated,
								props			={u"useWhatForStatus":"WiFi","useWhatForStatusWiFi":"Expiration",isType:True})
						except Exception, e:
							if unicode(e).find(u"None") == -1:
								self.indiLOG.log(40,u"in Line {} has error={}   trying to create: {}_{}".format(sys.exc_traceback.tb_lineno, e, devName,MAC) )
							continue
						self.setupStructures(xType, dev, MAC)
						self.addToStatesUpdateList(dev.id,u"AP", ipNumberAP+"-#"+unicode(apN))
						self.MAC2INDIGO[xType][MAC][u"idleTime" + suffixN] = 0
						if unicode(dev.id) in self.upDownTimers:
							del self.upDownTimers[unicode(dev.id)]
						self.setupBasicDeviceStates(dev, MAC,  "UN", "", "", "", "    " +MAC+u" status up   AP msg new device", "MS-AP-WF-6 ")
						indigo.variable.updateValue(u"Unifi_New_Device",u"{}{}".format(dev.name, MAC) )
						self.executeUpdateStatesList()
						dev = indigo.devices[dev.id]
						self.setupStructures(xType, dev, MAC)
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

		self.executeUpdateStatesList()

		if len(self.blockAccess)>0:	 del self.blockAccess[0]

		return

	####-----------------	 ---------
	### double check up/down with ping
	####-----------------	 ---------
	def doubleCheckWithPing(self,newStatus, ipNumber, props,MAC,debLevel, section, theType,xType):

		if ("usePingUP" in props and props[u"usePingUP"] and newStatus =="up" ) or ( "usePingDOWN" in props and props[u"usePingDOWN"] and newStatus !="up") :
			if self.checkPing(ipNumber, nPings=1, waitForPing=500, calledFrom="doubleCheckWithPing") !=0:
				if self.decideMyLog(debLevel, MAC=MAC): self.indiLOG.log(10,theType+"  "+u" "+MAC+" "+section+" , status changed - not up , ping test failed" )
				return 1
			else:
				if self.decideMyLog(debLevel, MAC=MAC): self.indiLOG.log(10,theType+"  "+u" "+MAC+" "+section+" , status changed - not up , ping test OK" )
				if xType in self.MAC2INDIGO:
					self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
				return 0
		return -1


	####-----------------	 ---------
	### for the dict,
	####-----------------	 ---------
	def comsumeDictData(self):#, startTime):
		self.sleep(1)
		self.indiLOG.log(10,u"comsumeDictData: process starting")
		nextItem = "     "
		while True:
			try:
				if self.pluginState == "stop" or self.consumeDataThread[u"dict"][u"status"] == u"stop": 
					self.indiLOG.log(30,u"comsumeDictData: stopping process due to stop request")
					return 
				consumedTimeQueue = time.time()
				self.sleep(0.1)
				while not self.logQueueDict.empty():
					if self.pluginState == "stop" or self.consumeDataThread[u"dict"][u"status"] == u"stop": 
						self.indiLOG.log(30,u"comsumeDictData: stopping process due to stop request")
						return 

					nextItem = self.logQueueDict.get()
					consumedTime = time.time()
					self.updateIndigoWithDictData( nextItem[0], nextItem[1], nextItem[2], nextItem[3], nextItem[4] )
					consumedTime -= time.time()

					if consumedTime < -3.0:	logLevel = 20
					else:					logLevel = 10
					if logLevel == 20 or (self.decideMyLog(u"Special")  and consumedTime < -.4):
						self.indiLOG.log(logLevel,u"comsumeDictData   excessive time consumed:{:.1f}; {:}-{:}-{:} len:{:},  next:{:}".format(-consumedTime, nextItem[1], nextItem[2], nextItem[3], len(nextItem[0]), unicode(nextItem[0])[0:100] ) )

					self.logQueueDict.task_done()

					if len(self.sendUpdateToFingscanList) > 0: self.sendUpdatetoFingscanNOW()
					if len(self.sendBroadCastEventsList)  > 0: self.sendBroadCastNOW()

				consumedTimeQueue -= time.time()
				if consumedTimeQueue < -5.0:	logLevel = 20
				else:							logLevel = 10
				if logLevel == 20  or (self.decideMyLog(u"Special")  and consumedTimeQueue < -.6):
					self.indiLOG.log(logLevel,u"comsumeDictData T excessive time consumed:{:.1f}; {:}-{:}-{:} len:{:},  next:{:}".format(-consumedTimeQueue, nextItem[1], nextItem[2], nextItem[3], len(nextItem[0]),  unicode(nextItem[0])[0:100]) )
	
			except	Exception, e:
				if unicode(e).find(u"None") == -1:
					self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		self.indiLOG.log(30,u"comsumeDictData: stopping process (3)")
		return 



	####-----------------	 ---------
	def updateIndigoWithDictData(self, apDict, ipNumber, apNumb, uType, unifiDeviceType):

		try:
			#if self.decideMyLog(u"Special"): self.indiLOG.log(10,u"updateIndigoWithDictData apDict[0:100]:{}, ipNumber:{}, apNumb:{}, uType:{}, unifiDeviceType:{}".format(unicode(apDict)[0:100], ipNumber, apNumb, uType, unifiDeviceType ) )

			if len(apDict) < 1: return
			self.manageLogfile(apDict, apNumb, unifiDeviceType)

			apNumbSW = apNumb
			apNumbAP = apNumb
			try:	apNint	= int(apNumb)
			except: apNint	= -1
			doSW 	 = False
			doAP 	 = False
			doGW 	 = False
			#######  if this is a UDM device set AP, SW GW to tru
			if unifiDeviceType == "UD" and self.unifiControllerType.find(u"UDM") > -1:
				doSW 	 = True
				doGW 	 = True
				doAP 	 = True
				apNumbSW = self.numberForUDM[u"SW"]
				apNumbAP = self.numberForUDM[u"AP"]


			if ( (uType.find(u"SW") > -1 and apNumb >= 0 and apNumb < len(self.debugDevs[u"SW"]) and self.debugDevs[u"SW"][apNumbSW]) or
			     (uType.find(u"AP") > -1 and apNumb >= 0 and apNumb < len(self.debugDevs[u"AP"]) and self.debugDevs[u"AP"][apNumbAP]) or
				 (uType.find(u"GW") > -1 and self.debugDevs[u"GW"]) or
				  self.decideMyLog(u"Dict") ): 
				dd = unicode(apDict)
				self.indiLOG.log(10,u"DEVdebug   {} dev #sw:{},ap:{}, uType:{}, unifiDeviceType:{}; dictmessage:\n{} ..\n{}".format(ipNumber, apNumbSW, apNumbAP, uType, unifiDeviceType, dd[:50], dd[-50:] ) )


			if self.decideMyLog(u"UDM"):  self.indiLOG.log(10,u"updDict  ipNumber:{};  apNumb:{};  uType:{};  unifiDeviceType:{};  doGW:{}; ".format(ipNumber,  apNumb, uType, unifiDeviceType, doGW) )
			if unifiDeviceType == "GW" or doGW:
				if self.decideMyLog(u"UDM"):  self.indiLOG.log(10,u"updDict  dict:\n{}".format(apDict) )
				self.doGatewaydictSELF(apDict, ipNumber)
				if self.unifiControllerType.find(u"UDM") >-1: 
					self.doGWDvi_stats(apDict, ipNumber)
				else:
					self.doGWHost_table(apDict, ipNumber)



			if unifiDeviceType == "SW" or doSW:
				if(	"mac"		  in apDict and 
				  	u"port_table" in apDict and
				 	u"hostname"	  in apDict and
				  	u"ip"		  in apDict ):

					MACSW = apDict[u"mac"]
					hostname = apDict[u"hostname"].strip()
					ipNDevice = apDict[u"ip"]

					#################  update SWs themselves
					self.doSWdictSELF(apDict, apNumbSW, ipNDevice, MACSW, hostname, ipNumber)

					#################  now update the devices on switch
					self.doSWITCHdictClients(apDict, apNumbSW, ipNDevice, MACSW, hostname, ipNumber)
				else:
					pass
##					self.indiLOG.log(10,u"DICTDATA    rejected .. mac, port_table, hostname ip not in dict ..{}".format(apDict))


			if unifiDeviceType == "AP" or doAP:
				if(	"mac"		 in apDict and
					u"vap_table" in apDict and
					u"ip"		 in apDict):

					MACAP		 = apDict[u"mac"]
					hostname = apDict[u"hostname"].strip()
					ipNDevice= apDict[u"ip"]

					clientHostnames ={"2":"","5":""}
					for jj in range(len(apDict[u"vap_table"])):
						if u"usage" in apDict[u"vap_table"][jj]: #skip if not wireless
							if apDict[u"vap_table"][jj][u"usage"] == "downlink": continue
							if apDict[u"vap_table"][jj][u"usage"] == "uplink":	continue

						channel = unicode(apDict[u"vap_table"][jj][u"channel"])
						if int(channel) >= 12:
							GHz = "5"
						else:
							GHz = "2"
						if u"sta_table" in apDict[u"vap_table"][jj] and apDict[u"vap_table"][jj][u"sta_table"] !=[]:
							clientHostnames[GHz] = self.doWiFiCLIENTSdict(apDict[u"vap_table"][jj][u"sta_table"], GHz, ipNDevice, apNumbAP, ipNumber)

						#################  update APs themselves
					self.doAPdictsSELF(apDict, apNumbAP, ipNDevice, MACAP, hostname, ipNumber, clientHostnames)


					############  update neighbors
					if u"radio_table" in	 apDict:
						self.doNeighborsdict(apDict[u"radio_table"], apNumbAP, ipNumber)
				else:
					pass
###					self.indiLOG.log(10,u"DICTDATA    rejected .. mac, vap_table,  ip not in dict ..{}".format(apDict))


		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))


		return


	#################  update APs
	####-----------------	 ---------
	def checkInListSwitch(self):

		xType = u"UN"
		ignore ={}
		try:
			for dev in indigo.devices.iter(u"props.isSwitch"):
				nn  = int(dev.states[u"switchNo"])
				if not self.devsEnabled[u"SW"][nn]:
					ignore[u"inListSwitch_"+unicode(nn)] = -1
				if  not self.isValidIP(self.ipNumbersOf[u"SW"][nn]):
					ignore[u"inListSwitch_"+unicode(nn)] = -1

			for nn in range(_GlobalConst_numberOfSW):
				if not self.devsEnabled[u"SW"][nn]:
					ignore[u"inListSwitch_"+unicode(nn)] = -1
				if  not self.isValidIP(self.ipNumbersOf[u"SW"][nn]):
					ignore[u"inListSwitch_"+unicode(nn)] = -1

			if not self.devsEnabled[u"GW"]:
				ignore[u"inListDHCP"] = 0
				ignore[u"upTimeDHCP"] = ""
			if  not self.isValidIP(self.ipNumbersOf[u"GW"]):
				ignore[u"inListDHCP"] = 0
				ignore[u"upTimeDHCP"] = ""

			save = False
			if len(ignore) > 0:
				for MAC in self.MAC2INDIGO[xType]:
					for xx in ignore:
						if xx in self.MAC2INDIGO[xType][MAC]:
							if self.MAC2INDIGO[xType][MAC][xx] != ignore[xx]:
								self.MAC2INDIGO[xType][MAC][xx]  = ignore[xx]
								save = True
						else:
								self.MAC2INDIGO[xType][MAC][xx]  = ignore[xx]
								save = True
				if save:
					self.saveMACdata()

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return


	####-----------------	 ---------
	#################  update APs
	####-----------------	 ---------
	def doInList(self,suffixN,	wifiIPAP=""):


		suffix = suffixN.split("_")[0]
		try:
			## now check if device is not in dict, if not ==> initiate status --> down
			xType = u"UN"
			delMAC={}
			for MAC in self.MAC2INDIGO[xType]:
				if self.MAC2INDIGO[xType][MAC][u"inList"+suffixN]  == -1: continue	# do not test
				if self.MAC2INDIGO[xType][MAC][u"inList"+suffixN]  ==  1: continue	# is here
				try:
					devId = self.MAC2INDIGO[xType][MAC][u"devId"]
					dev	  = indigo.devices[devId]
					aW	  = dev.states[u"AP"]
					if wifiIPAP =="" or aW == wifiIPAP:
						self.MAC2INDIGO[xType][MAC][u"inList"+suffixN] = 0
					if wifiIPAP !="" and aW != wifiIPAP:											 continue
					if dev.states[u"status"] != "up":											 continue

					props= dev.pluginProps
					if u"useWhatForStatus" not in props or props[u"useWhatForStatus"].find(suffix) == -1:	 continue
				except	Exception, e:
					if unicode(e).find(u"timeout waiting") > -1:
						self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
						self.indiLOG.log(40,u"communication to indigo is interrupted")
						return
					self.indiLOG.log(40,u"in Line {} has error={}  just deleted?.. then ignore message".format(sys.exc_traceback.tb_lineno, e) )
					self.indiLOG.log(40,u"deleting device from internal lists -- MAC:"+ MAC+";  devId:"+unicode(devId))
					delMAC[MAC]=1
					continue

				try:
					lastUpTT   = self.MAC2INDIGO[xType][MAC][u"lastUp"]
				except:
					lastUpTT = time.time() - 1000


				expT = self.getexpT(props)# this should be much faster than normal expiration
				if wifiIPAP !="" : expTUse  = max(expT/2.,10) # only for non wifi devices
				else:			   expTUse  = expT
				dt = time.time() - lastUpTT
				if dt < 						1 * expT:
					status = "up"
				elif dt < self.expTimeMultiplier  * expT:
					status = "down"
				else:
					status = "expired"


				if dev.states[u"status"] != status and status !="up":
					if u"usePingUP" in props and props[u"usePingUP"]	and status !="up" and self.sendWakewOnLanAndPing(MAC,dev.states[u"ipNumber"], props=props, nPings=1, calledFrom="inList") == 0:
							if self.decideMyLog(u"Logic", MAC=MAC): self.indiLOG.log(10,u"List-"+suffix+u"    " +dev.states[u"MAC"]+" check, status changed - not up , ping test ok resetting to up" )
							self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
							continue

					# self.myLog( text=" 4 " +dev.name + " set to "+ status)
					#self.myLog( text=u" inList "+ dev.name+u" changed: old status: "+dev.states[u"status"]+u"; new  "+status)
					self.setImageAndStatus(dev, status,oldStatus=dev.states[u"status"], ts=time.time(), level=1, text1= dev.name.ljust(30) + u" in list status " + status.ljust(10) + " "+suffixN+"     dt= %5.1f" % dt + ";  expT= %5.1f" % expT+ "  wifi:" +wifiIPAP, iType=u"STATUS-"+suffix,reason=u"NotInList "+suffixN+u" "+wifiIPAP+u" "+status)
	   #self.executeUpdateStatesList()

			for MAC in delMAC:
				del	 self.MAC2INDIGO[xType][MAC]

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return




	####-----------------	 ---------
	#### this does the unifswitch attached devices
	####-----------------	 ---------
	def doSWITCHdictClients(self, apDict, swNumb, ipNDevice, MACSW, hostnameSW, ipNumber):



		part="doSWITCHdict"+unicode(random.random()); self.blockAccess.append(part)
		for ii in range(90):
				if len(self.blockAccess) ==0 or self.blockAccess[0]==part:	break
				self.sleep(0.1)
		if ii >= 89: self.blockAccess = [] # for safety if too long reset list


		try:

			devType = "UniFi"
			isType	= "isUniFi"
			devName = "UniFi"
			suffix	= "SWITCH"
			xType	= u"UN"

			portTable = apDict[u"port_table"]


			UDMswitch = False
			useIP = ipNumber
			if self.unifiControllerType.find(u"UDM") > -1 and swNumb == self.numberForUDM[u"SW"]:
				UDMswitch = True
				if self.decideMyLog(u"UDM"):  self.indiLOG.log(10,u"DC-SW-UDM  using UDM mode  for  IP#Dict:{}  ip#proc#{} ".format(ipNDevice, ipNumber) )


			if useIP not in self.deviceUp[u"SW"]:
				if len(self.blockAccess) >0: del self.blockAccess[0]
				return

			switchNumber = -1
			for ii in range(_GlobalConst_numberOfSW):
				if not self.devsEnabled[u"SW"][ii]:				continue
				if useIP != self.ipNumbersOf[u"SW"][ii]: 	continue
				switchNumber = ii
				break

			if switchNumber < 0:
				if len(self.blockAccess)>0:	 del self.blockAccess[0]
				return

			swN		= unicode(switchNumber)
			suffixN = suffix+u"_"+swN


			for MAC in self.MAC2INDIGO[xType]:
				if len(MAC) < 16:
					self.MAC2INDIGO[xType][MAC][u"inList"+suffixN] = -1	 # was not here
					continue
				try:
					if u"inList"+suffixN not in self.MAC2INDIGO[xType][MAC]:
						self.indiLOG.log(40,u"error in doSWITCHdictClients: mac:{}  inList{} not in NMAC2INDIGO:{}".format(MAC,suffix,  self.MAC2INDIGO[xType][MAC]))
						continue
					if self.MAC2INDIGO[xType][MAC][u"inList"+suffixN]  > 0:	 # was here was here , need to test
						self.MAC2INDIGO[xType][MAC][u"inList"+suffixN] = 0
				except:
						self.indiLOG.log(40,u"error in doSWITCHdictClients: mac:{}  MAC2INDIGO:{}".format(MAC, self.MAC2INDIGO[xType][MAC]))
						return
				else:
					self.MAC2INDIGO[xType][MAC][u"inList"+suffixN] = -1	 # was not here


			for port in portTable:

				##self.myLog( text="port # "+ unicode(ii)+unicode(portTable[0:100])
				portN = unicode(port[u"port_idx"])
				if u"mac_table" not in port: continue
				macTable =	port[u"mac_table"]
				if macTable == []:	continue
				if u"port_idx" in port:
					portN = unicode(port[u"port_idx"])
				else:
					portN = ""
				isUpLink = False
				isDownLink = False

				if u"is_uplink"	  in port and port[u"is_uplink"]:			isUpLink   = True
				elif u"lldp_table" in port and len(port[u"lldp_table"]) > 0:	isDownLink = True

				#if isUpLink:		   continue
				#if isDownLink:		   continue

				for switchDevices in macTable:
					MAC = switchDevices[u"mac"]
					if self.testIgnoreMAC(MAC, fromSystem="SW-Dict"): continue

					if u"vlan" in switchDevices:		vlan	   = switchDevices[u"vlan"]
					else: vlan = ""

					if u"age" in switchDevices:		age	   = switchDevices[u"age"]
					else: age = ""

					if u"ip" in switchDevices:
													ip	   = switchDevices[u"ip"]
													try:	self.MAC2INDIGO[xType][MAC][u"ipNumber"] = ip
													except: continue
					else:							ip = ""

					if u"uptime" in switchDevices:	newUp  = unicode(switchDevices[u"uptime"])
					else: newUp = ""

					nameSW = "empty"
					if u"hostname" in switchDevices: nameSW = unicode(switchDevices[u"hostname"]).strip()
					if nameSW == "?":    nameSW = "empty"
					if len(nameSW) == 0: nameSW = "empty"

					ipx = self.fixIP(ip)
					new = True
					if MAC in self.MAC2INDIGO[xType]:
						try:
							dev = indigo.devices[self.MAC2INDIGO[xType][MAC][u"devId"]]
							if dev.deviceTypeId != devType: 1 / 0
							self.MAC2INDIGO[xType][MAC][u"inList"+suffixN] = 1 # is here
							new = False
						except:
							if self.decideMyLog(u"Logic", MAC=MAC): self.indiLOG.log(10, "{}     {} wrong {}".format(MAC, self.MAC2INDIGO[xType][MAC][u"devId"], devType))
							for dev in indigo.devices.iter(u"props."+isType):
								if u"MAC" not in dev.states:			continue
								if dev.states[u"MAC"] != MAC:		continue
								self.setupStructures(xType, dev, MAC, init=False)
								self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
								self.MAC2INDIGO[xType][MAC][u"inList"+suffixN] = 1
								new = False
								break

					if not new:

						self.MAC2INDIGO[xType][MAC][u"inList"+suffixN] = 1
						if self.decideMyLog(u"Dict", MAC=MAC): self.indiLOG.log(10,u"DC-SW-00   {:15s}  {}; {}; IP:{}; AGE:{}; newUp:{}; hostN:{}".format(useIP, MAC, dev.name, ip, age, newUp, nameSW))

						if not ( isUpLink or isDownLink ): # this is not for up or downlink 
							poe = ""
							if MACSW in self.MAC2INDIGO[u"SW"]:  # do we know the switch
								if portN in self.MAC2INDIGO[u"SW"][MACSW][u"ports"]: # is the port in the switch
									if  "nClients" in self.MAC2INDIGO[u"SW"][MACSW][u"ports"][portN] and  self.MAC2INDIGO[u"SW"][MACSW][u"ports"][portN][u"nClients"] == 1: 
										if u"poe" in self.MAC2INDIGO[u"SW"][MACSW][u"ports"][portN] and self.MAC2INDIGO[u"SW"][MACSW][u"ports"][portN][u"poe"]  != "": # if empty dont add "-"
											poe = u"-"+self.MAC2INDIGO[u"SW"][MACSW][u"ports"][portN][u"poe"]
										if len(dev.states[u"AP"]) > 5: # fix if direct connect and poe is one can not have wifi for this MAC, must be ethernet, set wifi to "-"
											self.addToStatesUpdateList(dev.id,u"AP", "-")

							newPort = swN+":"+portN+poe
							#self.indiLOG.log(10,u"portInfo   MACSW: "+MACSW +"   hostnameSW:"+hostnameSW+"  "+useIP +" "+ MAC+"  portN:"+portN+" MACSW-poe:"+ self.MAC2INDIGO[u"SW"][MACSW][u"ports"][portN][u"poe"]+"; nameSW:"+unicode(nameSW)+"  poe:"+poe+"  newPort:"+newPort)

							if dev.states[u"SW_Port"] != newPort:
								self.addToStatesUpdateList(dev.id,u"SW_Port", newPort)


						props=dev.pluginProps

						newd = False
						devidd = unicode(dev.id)
						if ip != "":
							if dev.states[u"ipNumber"] != ip:
								self.addToStatesUpdateList(dev.id,u"ipNumber", ip)
							self.MAC2INDIGO[xType][MAC][u"ipNumber"] = ip
						self.MAC2INDIGO[xType][MAC][u"age"+suffixN] = age
						if dev.states[u"name"] != nameSW and nameSW !="empty":
							self.addToStatesUpdateList(dev.id,u"name", nameSW)

						if u"vlan" in dev.states and dev.states[u"vlan"] != vlan:
							self.addToStatesUpdateList(dev.id,u"vlan", vlan)


						newStatus = "up"
						oldStatus = dev.states[u"status"]
						oldUp	  = self.MAC2INDIGO[xType][MAC][u"upTime" + suffixN]
						self.MAC2INDIGO[xType][MAC][u"upTime" + suffixN] = unicode(newUp)
						if u"useWhatForStatus" in props and props[u"useWhatForStatus"] in [u"SWITCH","OptDhcpSwitch"]:
							if self.decideMyLog(u"Dict", MAC=MAC): self.indiLOG.log(10,u"DC-SW-0    {:15s} {} {}; oldStatus:{}; IP:{}; AGE:{}; newUp:{}; oldUp:{} hostN:{}".format(useIP, MAC, dev.name, oldStatus, ip, age, newUp, oldUp, nameSW))
							if oldUp ==	 newUp and oldStatus =="up":
								if u"useupTimeforStatusSWITCH" in props and props[u"useupTimeforStatusSWITCH"] :
									if u"usePingDOWN" in props and props[u"usePingDOWN"]	and self.sendWakewOnLanAndPing(MAC,dev.states[u"ipNumber"], props=props, calledFrom ="doSWITCHdictClients") == 0:
										if self.decideMyLog(u"DictDetails", MAC=MAC): self.indiLOG.log(10,u"DC-SW-1    {} reset timer for status up  notuptime const	but answers ping".format(MAC))
										self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
									else:
										if self.decideMyLog(u"DictDetails", MAC=MAC): self.indiLOG.log(10,u"DC-SW-2    {} SW DICT network_table , Uptime not changed, continue expiration timer".format(MAC))
								else: # will only expired if not in list anymore
									if u"usePingDOWN" in props and props[u"usePingDOWN"]	 and status !="up" and self.sendWakewOnLanAndPing(MAC,dev.states[u"ipNumber"], props=props, calledFrom ="doSWITCHdictClients") != 0:
										if self.decideMyLog(u"DictDetails", MAC=MAC): self.indiLOG.log(10,u"DC-SW-3    {} SW DICT network_table , but does not answer ping, continue expiration timer".format(MAC))
									else:
										if self.decideMyLog(u"DictDetails", MAC=MAC): self.indiLOG.log(10,u"DC-SW-4    {} reset timer for status up     answers ping in  DHCP list".format(MAC))
										self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()


							if oldUp != newUp:
								if u"usePingUP" in props and props[u"usePingUP"] and self.sendWakewOnLanAndPing(MAC,dev.states[u"ipNumber"], props=props, calledFrom ="doSWITCHdictClients") != 0:
									if self.decideMyLog(u"Dict", MAC=MAC): self.indiLOG.log(10,u"DC-SW-5    {} SW DICT network_table , but does not answer ping, continue expiration timer".format(MAC))
								else:
									self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
									if self.decideMyLog(u"Dict", MAC=MAC): self.indiLOG.log(10,u"DC-SW-0    {} SW DICT network_tablerestart exp timer ".format(MAC))

						if self.updateDescriptions:
							oldIPX = dev.description.split("-")
							if ipx !="" and (oldIPX[0] != ipx or ( (dev.description != ipx + "-" + nameSW or len(dev.description) < 5) and nameSW !="empty"  and  (dev.description).find(u"=WiFi") ==-1 )) :
								if oldIPX[0] != ipx and oldIPX[0] !="":
									indigo.variable.updateValue(u"Unifi_With_IPNumber_Change",u"{}/{}/{}/{}".format(dev.name, dev.states[u"MAC"], oldIPX[0], ipx) )
								dev.description = ipx + "-" + nameSW
								if self.decideMyLog(u"DictDetails", MAC=MAC): self.indiLOG.log(10,u"DC-SW-7    updating description for {}  to....{}".format(dev.name, dev.description) )
								dev.replaceOnServer()

						#break

					if new and not self.ignoreNewClients:
						try:
							dev = indigo.device.create(
								protocol		=indigo.kProtocol.Plugin,
								address			=MAC,
								name			=devName+ "_" + MAC,
								description		=ipx + "-" + nameSW,
								pluginId		=self.pluginId,
								deviceTypeId	=devType,
								folder			=self.folderNameIDCreated,
								props			={u"useWhatForStatus":"SWITCH","useupTimeforStatusSWITCH":"",isType:True})

						except	Exception, e:
							if unicode(e).find(u"None") == -1:
								self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
							continue

						self.setupStructures(xType, dev, MAC)
						self.addToStatesUpdateList(dev.id,u"SW_Port", "")
						self.MAC2INDIGO[xType][MAC][u"age"+suffixN] = age
						self.MAC2INDIGO[xType][MAC][u"upTime"+suffixN] = newUp
						self.setupBasicDeviceStates(dev, MAC, xType, ip, "", "", u" status up          SWITCH DICT new Device", "STATUS-SW")
						self.MAC2INDIGO[xType][MAC][u"inList"+suffixN] = 1
						indigo.variable.updateValue(u"Unifi_New_Device",u"{}/{}/{}".format(dev.name, MAC, ipx) )
						self.executeUpdateStatesList()
						dev = indigo.devices[dev.id]
						self.setupStructures(xType, dev, MAC)

			self.doInList(suffixN)
			self.executeUpdateStatesList()



		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

		#if time.time()-waitT > 0.001: #self.myLog( text=unicode(self.blockAccess).ljust(28)+part.ljust(18)+"    exectime> %6.3f"%(time.time()-waitT)+ " @ "+datetime.datetime.now().strftime("%M:%S.%f")[:-3])
		if len(self.blockAccess)>0:	 del self.blockAccess[0]

		return

	####-----------------	 ---------
	def doGWHost_table(self, gwDict, ipNumber):

		part="doGWHost_table"+unicode(random.random()); self.blockAccess.append(part)
		for ii in range(90):
				if len(self.blockAccess) == 0 or self.blockAccess[0] == part: break # my turn?
				self.sleep(0.1)
		if ii >= 89: self.blockAccess = [] # for safety if too long reset list


		try:
			devType = u"UniFi"
			isType	= "isUniFi"
			devName = u"UniFi"
			suffixN = u"DHCP"
			xType	= u"UN"

			###########	 do DHCP devices

			if u"network_table" not in gwDict:
				if self.decideMyLog(u"Logic"): self.indiLOG.log(10,u"DC-DHCP-E0 network_table not in dict {}".format(gwDict[0:100]) )
				return


			host_table = ""
			for item  in gwDict[u"network_table"]:
				if u"host_table" not in item: continue
				host_table = item[u"host_table"]
				break
			if host_table == "":
				if u"host_table" not in gwDict[u"network_table"]:
					if self.decideMyLog(u"Logic"): self.indiLOG.log(10,u"DC-DHCP-E1 no DHCP in gwateway ?.. skipping info ".format(gwDict[u"network_table"][0:100]) )
					return # DHCP not enabled on gateway, no info from GW available

			if u"connect_request_ip" in gwDict:
				ipNumber = gwDict[u"connect_request_ip"]
			else:
				ipNumber = "            "
			##self.myLog( text=" GW dict: lan0" + unicode(lan0)[:100])

			for MAC in self.MAC2INDIGO[xType]:
				self.MAC2INDIGO[xType][MAC][u"inList"+suffixN] = 0

			if self.decideMyLog(u"DictDetails", MAC=MAC): self.indiLOG.log(10,u"DC-DHCP-0  host_table len:{}     {}".format( len(host_table), host_table[0:100]) )
			if len(host_table) > 0:
				for item in host_table:

					##self.myLog( text=" nn: "+ unicode(nn)+"; lan: "+ unicode(lan)[0:200] )


					if u"ip" in item:  ip = item[u"ip"]
					else:			  ip = ""
					MAC					 = item[u"mac"]
					if self.testIgnoreMAC(MAC, fromSystem="GW-Dict"): continue
					age					 = item[u"age"]
					uptime				 = item[u"uptime"]
					new					 = True
					#self.myLog( text=" GW dict: network_table" + unicode(host_table)[:100])
					if MAC in self.MAC2INDIGO[xType]:
						try:
							dev = indigo.devices[self.MAC2INDIGO[xType][MAC][u"devId"]]
							if dev.deviceTypeId != devType: 1 / 0
							# self.myLog( text=MAC+" "+ dev.name)
							new = False
							self.MAC2INDIGO[xType][MAC][u"inList" + suffixN] = 1
						except:
							if self.decideMyLog(u"Logic", MAC=MAC): self.indiLOG.log(10,u"DC-DHCP-E1 {}  {} wrong {}".format(MAC, self.MAC2INDIGO[xType][MAC], devType) )
							for dev in indigo.devices.iter(u"props."+isType):
								if u"MAC" not in dev.states: continue
								if dev.states[u"MAC"] != MAC: continue
								self.setupStructures(xType, dev, MAC, init=False)
								self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
								self.MAC2INDIGO[xType][MAC][u"inList" + suffixN] = 1
								new = False
								break

					if not new:
							if self.decideMyLog(u"DictDetails", MAC=MAC): self.indiLOG.log(10,u"DC-DHCP-1  {:15s}  {}; {}; ip:{}; age:{}; uptime:{}".format(ipNumber, MAC, dev.name,ip, age, uptime))

							self.MAC2INDIGO[xType][MAC][u"inList"+suffixN] = True

							props = dev.pluginProps
							new = False
							if MAC != dev.states[u"MAC"]:
								self.addToStatesUpdateList(dev.id,u"MAC", MAC)
							if ip != "":
								if ip != dev.states[u"ipNumber"]:
									self.addToStatesUpdateList(dev.id,u"ipNumber", ip)
								self.MAC2INDIGO[xType][MAC][u"ipNumber"] = ip

							newStatus = "up"
							if u"useWhatForStatus" in props and props[u"useWhatForStatus"] in [u"DHCP",u"OptDhcpSwitch",u"WiFi,DHCP"]:

								if u"useAgeforStatusDHCP" in props and props[u"useAgeforStatusDHCP"] != u"-1"     and float(age) > float( props[u"useAgeforStatusDHCP"]):
										if dev.states[u"status"] == "up":
											if u"usePingDOWN" in props and props[u"usePingDOWN"] and self.sendWakewOnLanAndPing(MAC,dev.states[u"ipNumber"], props=props, calledFrom =u"doGWHost_table") == 0:  # did  answer
												if self.decideMyLog(u"DictDetails", MAC=MAC): self.indiLOG.log(10,u"    {} restart exptimer DICT network_table AGE>max:{}, but answers ping, exp-time left:{:5.1f}".format(MAC, props[u"useAgeforStatusDHCP"], self.getexpT(props) -(time.time()-self.MAC2INDIGO[xType][MAC][u"lastUp"]) ))
												self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
												newStatus = u"up"
											else:
												if self.decideMyLog(u"DictDetails", MAC=MAC): self.indiLOG.log(10,u"    {} set timer for status down GW DICT network_table AGE>max:{}".format(MAC, props[u"useAgeforStatusDHCP"]))
												newStatus = u"startDown"

								else: # good data, should be up
									if u"usePingUP" in props and props[u"usePingUP"] and dev.states[u"status"] == u"up" and self.sendWakewOnLanAndPing(MAC,dev.states[u"ipNumber"], props=props, calledFrom =u"doGWHost_table") == 1:	# did not answer
											self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time() - self.getexpT(props) # down immediately
											self.setImageAndStatus(dev, "down",oldStatus=dev.states[u"status"], ts=time.time(), level=1, text1= dev.name.ljust(30) + u"set timer for status down    ping does not answer", iType=u"DC-DHCP-4  ",reason=u"DICT "+suffixN+u" up")
											newStatus = u"down"
									elif dev.states[u"status"] != u"up":
											self.setImageAndStatus(dev, u"up",oldStatus=dev.states[u"status"], ts=time.time(), level=1, text1= dev.name.ljust(30) + u" status up   GW DICT network_table", iType=u"DC-DHCP-4  ",reason=u"DICT "+suffixN+u" up")
											newStatus = u"up"

								if newStatus == u"up":
									self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()

							self.MAC2INDIGO[xType][MAC][u"age"+suffixN]		= age
							self.MAC2INDIGO[xType][MAC][u"upTime"+suffixN]	= uptime

							if self.updateDescriptions:
								oldIPX = dev.description.split("-")
								ipx = self.fixIP(ip)
								if ipx != "" and oldIPX[0] != ipx and oldIPX[0] != u"":
									indigo.variable.updateValue(u"Unifi_With_IPNumber_Change", u"{}/{}/{}/{}".format(dev.name, dev.states[u"MAC"], oldIPX[0], ipx) )
									oldIPX[0] = ipx
									dev.description = u"-".join(oldIPX)
									if self.decideMyLog(u"DictDetails", MAC=MAC): self.indiLOG.log(10,u"updating description for {}  to....{}".format(dev.name, dev.description) )
									dev.replaceOnServer()


					if new and not self.ignoreNewClients:
						try:
							dev = indigo.device.create(
								protocol		=indigo.kProtocol.Plugin,
								address			=MAC,
								name			=devName + u"_" + MAC,
								description		=self.fixIP(ip),
								pluginId		=self.pluginId,
								deviceTypeId	=devType,
								folder			=self.folderNameIDCreated,
								props			={ "useWhatForStatus":"DHCP","useAgeforStatusDHCP": "-1","useWhatForStatusWiFi":"", isType:True})
						except	Exception, e:
							if unicode(e).find(u"None") == -1:
								self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
							continue

						self.setupStructures(xType, dev, MAC)
						self.MAC2INDIGO[xType][MAC][u"age"+suffixN]			= age
						self.MAC2INDIGO[xType][MAC][u"upTime"+suffixN]		= uptime
						self.MAC2INDIGO[xType][MAC][u"inList"+suffixN]		= True
						self.setupBasicDeviceStates(dev, MAC, xType, ip, "", "", u" status up    GW DICT  new device","DC-DHCP-3   ")
						self.executeUpdateStatesList()
						dev = indigo.devices[dev.id]
						self.setupStructures(xType, dev, MAC)
						indigo.variable.updateValue(u"Unifi_New_Device",u"{}/{}".format(dev.name, MAC) )



			## now check if device is not in dict, if not ==> initiate status --> down
			self.doInList(suffixN)
			self.executeUpdateStatesList()


		except	Exception, e:
					if unicode(e).find(u"None") == -1:
						self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		if len(self.blockAccess)>0:	 del self.blockAccess[0]
		return


	####-----------------	 ---------
	def doGWDvi_stats(self, gwDict, ipNumber):

		part="doGWDvi_stats"+unicode(random.random()); self.blockAccess.append(part)
		for ii in range(90):
				if len(self.blockAccess) == 0 or self.blockAccess[0] == part: break # my turn?
				self.sleep(0.1)
		if ii >= 89: self.blockAccess = [] # for safety if too long reset list


		try:
			devType = u"UniFi"
			isType	= u"isUniFi"
			devName = u"UniFi"
			suffixN = u"DHCP"
			xType	= u"UN"

			###########	 do DHCP devices

			### UDM does not have DHCP info use DPI info, cretae an artificial age # by adding rx tx packets
			if self.unifiControllerType.find(u"UDM") > -1: key = "dpi_stats"
			else:										   key = "dpi-stats"
			if key not in gwDict or gwDict[key] == []: 
				if False and self.decideMyLog(u"UDM"):  self.indiLOG.log(10,u"DC-DPI   dpi-stats not in dict or empty " )
				return 
			dpi_table =[]
			xx = {}
			for dd in gwDict:
				if len(dd) < 1: continue
				if u"ip" not in dd: 		
					#if self.decideMyLog(u"UDM"):  self.indiLOG.log(10,u"DC-DPI    \"ip\" not in gWDict" )
					continue
				if type(dd) != type({}): 
					#if self.decideMyLog(u"UDM"):  self.indiLOG.log(10,u"DC-DPI     dict in gwDict :".format(gwDict) )
					continue
				xx = {u"age": 99999999999,
					  u"authorized": False,
					  u"ip": dd[u"ip"],
					  u"mac": dd[u"mac"],
					  u"tx_bytes": 0,
					  u"tx_packets": 0,
					  u"uptime": 0}
				for yy in gwDict[key][u"stats"]:
					xx[u"rx_packets"] += yy[u"rx_packets"]
					xx[u"tx_packets"] += yy[u"tx_packets"]
				if xx[u"rx_packets"]  + xx[u"tx_packets"]  > 0:
					xx[u"age"] 	 = 0
					xx[u"uptime"] = int(time.time()*1000 - float(gwDict[u"initialized"]))
					dpi_table.append(xx)

			for item in dpi_table:
					if u"ip" in item: ip = item[u"ip"]
					else:			  ip = ""
					MAC					 = item[u"mac"]
					if self.testIgnoreMAC(MAC, fromSystem="GW-Dict"): continue
					age					 = item[u"age"]
					uptime				 = item[u"uptime"]
					new					 = True
					#self.myLog( text=" GW dict: network_table" + unicode(host_table)[:100])
					if MAC in self.MAC2INDIGO[xType]:
						try:
							dev = indigo.devices[self.MAC2INDIGO[xType][MAC][u"devId"]]
							if dev.deviceTypeId != devType: 1 / 0
							# self.myLog( text=MAC+" "+ dev.name)
							new = False
							self.MAC2INDIGO[xType][MAC][u"inList" + suffixN] = 1
						except:
							if self.decideMyLog(u"Logic", MAC=MAC): self.indiLOG.log(10,u"DC-DPI-E1  {}     {} wrong devType:{}".format(MAC, self.MAC2INDIGO[xType][MAC], devType) )
							for dev in indigo.devices.iter(u"props."+isType):
								if u"MAC" not in dev.states: continue
								if dev.states[u"MAC"] != MAC: continue
								self.setupStructures(xType, dev, MAC, init=False)
								self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
								self.MAC2INDIGO[xType][MAC][u"inList" + suffixN] = 1
								new = False
								break

					if not new:
							if self.decideMyLog(u"DictDetails", MAC=MAC): self.indiLOG.log(10,u"DC-DPI-1  {} {}  {} ip:{} age:{} uptime:{}".format(ipNumber, MAC, dev.name, ip, age, uptime))

							self.MAC2INDIGO[xType][MAC][u"inList"+suffixN] = True

							props = dev.pluginProps
							new = False
							if MAC != dev.states[u"MAC"]:
								self.addToStatesUpdateList(dev.id,u"MAC", MAC)
							if ip != "":
								if ip != dev.states[u"ipNumber"]:
									self.addToStatesUpdateList(dev.id,u"ipNumber", ip)
								self.MAC2INDIGO[xType][MAC][u"ipNumber"] = ip

							newStatus = u"up"
							if u"useWhatForStatus" in props and props[u"useWhatForStatus"] in ["DHCP",u"OptDhcpSwitch",u"WiFi,DHCP"]:

								if u"useAgeforStatusDHCP" in props and props[u"useAgeforStatusDHCP"] != u"-1"     and float(age) > float( props[u"useAgeforStatusDHCP"]):
										if dev.states[u"status"] == u"up":
											if u"usePingDOWN" in props and props[u"usePingDOWN"] and self.sendWakewOnLanAndPing(MAC,dev.states[u"ipNumber"], props=props, calledFrom = u"doGWHost_table") == 0:  # did  answer
												if self.decideMyLog(u"DictDetails", MAC=MAC): self.indiLOG.log(10,u"DC-DPI-2   {} ==> restart exptimer DICT network_table AGE>max, but answers ping {}, exp-time left:{:5.1f}".format(MAC,props[u"useAgeforStatusDHCP"], self.getexpT(props) -(time.time()-self.MAC2INDIGO[xType][MAC][u"lastUp"])))
												self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
												newStatus = "up"
											else:
												if self.decideMyLog(u"DictDetails", MAC=MAC): self.indiLOG.log(10,u"DC-DPI-3   {} set timer for status down GW DICT network_table AGE>max:" .format(MAC,props[u"useAgeforStatusDHCP"]))
												newStatus = "startDown"

								else: # good data, should be up
									if u"usePingUP" in props and props[u"usePingUP"] and dev.states[u"status"] == u"up" and self.sendWakewOnLanAndPing(MAC,dev.states[u"ipNumber"], props=props, calledFrom =u"doGWHost_table") == 1:	# did not answer
											self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time() - self.getexpT(props) # down immediately
											self.setImageAndStatus(dev, "down",oldStatus=dev.states[u"status"], ts=time.time(), level=1, text1= dev.name.ljust(30) + u"set timer for status down    ping does not answer", iType=u"DC-DHCP-4  ",reason=u"DICT "+suffixN+u" up")
											newStatus = "down"
									elif dev.states[u"status"] != u"up":
											self.setImageAndStatus(dev, u"up",oldStatus=dev.states[u"status"], ts=time.time(), level=1, text1= dev.name.ljust(30) + u" status up  	GW DICT network_table", iType=u"DC-DHCP-4  ",reason=u"DICT "+suffixN+u" up")
											newStatus = u"up"

								if newStatus == u"up":
									self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()

							self.MAC2INDIGO[xType][MAC][u"age"+suffixN]		= age
							self.MAC2INDIGO[xType][MAC][u"upTime"+suffixN]	= uptime

							if self.updateDescriptions:
								oldIPX = dev.description.split("-")
								ipx = self.fixIP(ip)
								if ipx!="" and oldIPX[0] != ipx and oldIPX[0] !="":
									indigo.variable.updateValue(u"Unifi_With_IPNumber_Change",u"{}/{}/{}/{}".format(dev.name, dev.states[u"MAC"], oldIPX[0], ipx) )
									oldIPX[0] = ipx
									dev.description = "-".join(oldIPX)
									if self.decideMyLog(u"DictDetails", MAC=MAC): self.indiLOG.log(10,u"DC-DPI-4   updating description for {}  to: {}".format(dev.name, dev.description) )
									dev.replaceOnServer()


					if new and not self.ignoreNewClients:
						try:
							dev = indigo.device.create(
								protocol		=indigo.kProtocol.Plugin,
								address			=MAC,
								name			=devName + "_" + MAC,
								description		=self.fixIP(ip),
								pluginId		=self.pluginId,
								deviceTypeId	=devType,
								folder			=self.folderNameIDCreated,
								props			={ "useWhatForStatus":"DHCP","useAgeforStatusDHCP": "-1","useWhatForStatusWiFi":"", isType:True})
						except	Exception, e:
							if unicode(e).find(u"None") == -1:
								self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
							continue

						self.setupStructures(xType, dev, MAC)
						self.MAC2INDIGO[xType][MAC][u"age"+suffixN]			= age
						self.MAC2INDIGO[xType][MAC][u"upTime"+suffixN]		= uptime
						self.MAC2INDIGO[xType][MAC][u"inList"+suffixN]		= True
						self.setupBasicDeviceStates(dev, MAC, xType, ip, "", "", u" status u         GW DICT  new device","DC-DPI-3   ")
						self.executeUpdateStatesList()
						dev = indigo.devices[dev.id]
						self.setupStructures(xType, dev, MAC)
						indigo.variable.updateValue(u"Unifi_New_Device",u"{}/{}".format(dev.name, MAC) )



			## now check if device is not in dict, if not ==> initiate status --> down
			self.doInList(suffixN)
			self.executeUpdateStatesList()


		except	Exception, e:
					if unicode(e).find(u"None") == -1:
						self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		if len(self.blockAccess)>0:	 del self.blockAccess[0]
		return




	####-----------------	 ---------
	def doWiFiCLIENTSdict(self,adDict, GHz, ipNDevice, apN, ipNumber):
		try:
	
			part="doWiFiCLIENTSdict"+unicode(random.random()); self.blockAccess.append(part)
			for ii in range(90):
					if len(self.blockAccess) == 0 or self.blockAccess[0] == part: break # my turn?
					self.sleep(0.1)
			if ii >= 89: self.blockAccess = [] # for safety if too long reset list

			if len(adDict) == 0:
				if len(self.blockAccess)>0:	 del self.blockAccess[0]
				return

			if self.decideMyLog(u"Dict") or self.debugDevs[u"AP"][int(apN)]: self.indiLOG.log(10,u"DC-WF-00   {:13s}#{} ... vap_table..[sta_table]: {}".format(ipNumber,apN, adDict) )

			try:
				devType = u"UniFi"
				isType	= u"isUniFi"
				devName = u"UniFi"
				suffixN = u"WiFi"
				xType	= u"UN"
				clientHostNames = ""
				#self.myLog( text=u"DictDetails", ipNDevice + " GHz" +GHz, mType=u"DICT-WiFi")
				for MAC in self.MAC2INDIGO[xType]:
					if u"AP" not in self.MAC2INDIGO[xType][MAC]:
						self.indiLOG.log(30,u"DC-WF-ER   {} # type:{} is not properly defined, please check config  and fix, then restart plugin".format(MAC, xType) )
						continue
					if self.MAC2INDIGO[xType][MAC][u"AP"]  != ipNumber: continue
					if self.MAC2INDIGO[xType][MAC][u"GHz"] != GHz:		continue
					self.MAC2INDIGO[xType][MAC][u"inList"+suffixN] = 0


				for ii in range(len(adDict)):

					new				= True
					if u"mac" not in adDict[ii] : continue
					MAC				= adDict[ii][u"mac"]
					if self.testIgnoreMAC(MAC, fromSystem="WF-Dict"): continue
					if u"ip" not in adDict[ii]: continue
					ip				= adDict[ii][u"ip"]
					txRate			= unicode(adDict[ii][u"tx_rate"])
					rxRate			= unicode(adDict[ii][u"rx_rate"])
					rxtx			= rxRate+"/"+txRate+" [Kb]"
					signal			= unicode(adDict[ii][u"signal"])
					noise			= unicode(adDict[ii][u"noise"])
					idletime		= unicode(adDict[ii][u"idletime"])
					try:state		= format(int(adDict[ii][u"state"]), '08b')	## not in controller
					except: state	= ""
					newUpTime		= unicode(adDict[ii][u"uptime"])
					try:
						nameCl		= adDict[ii][u"hostname"].strip()
					except:
						nameCl		= ""
					if nameCl !="": clientHostNames += nameCl+u"; "
					powerMgmt = unicode(adDict[ii][u"state_pwrmgt"])
					ipx = self.fixIP(ip)
					#if	 MAC == "54:9f:13:3f:95:25":
					#self.myLog( text=u"DictDetails", ipNDevice+" checking MAC in dict "+MAC	 ,mType=u"DICT-WiFi")

					if MAC in self.MAC2INDIGO[xType]:
						try:
							dev = indigo.devices[self.MAC2INDIGO[xType][MAC][u"devId"]]
							if dev.deviceTypeId != devType: 1/0
							#self.myLog( text=MAC+" "+ dev.name)
							new = False
							self.MAC2INDIGO[xType][MAC][u"AP"]		   		 = ipNumber
							self.MAC2INDIGO[xType][MAC][u"inList" + suffixN] = 1
							self.MAC2INDIGO[xType][MAC][u"GHz"]		   		 = GHz
						except:
							if self.decideMyLog(u"Logic", MAC=MAC): self.indiLOG.log(10,u"{}; {} has wrong devType:{}".format(MAC, self.MAC2INDIGO[xType][MAC], devType) )
							for dev in indigo.devices.iter(u"props."+isType):
								if u"MAC" not in dev.states: continue
								if dev.states[u"MAC"] != MAC: continue
								self.setupStructures(xType, dev, MAC, init=False)
								self.MAC2INDIGO[xType][MAC][u"lastUp"] 			 =  time.time()
								self.MAC2INDIGO[xType][MAC][u"GHz"] 			 = GHz
								self.MAC2INDIGO[xType][MAC][u"AP"] 				 = ipNumber
								self.MAC2INDIGO[xType][MAC][u"inList" + suffixN] = 1
								new = False
								break
					else:
						pass


					if not new:
							props=dev.pluginProps
							devidd = unicode(dev.id)

							oldAssociated =	 dev.states[u"AP"].split("#")[0]
							newAssociated =	 ipNumber
							try:	 oldIdle =	int(self.MAC2INDIGO[xType][MAC][u"idleTime" + suffixN])
							except:	 oldIdle = 0

							# this is for the case when device switches betwen APs and the old one is still sending.. ignore that one
							if dev.states[u"AP"].split("-")[0] != ipNumber:
								try:
									if oldIdle < 600 and int(idletime) > oldIdle: 
										if self.decideMyLog(u"DictDetails", MAC=MAC) or self.decideMyLog(u"Logic") or self.debugDevs[u"AP"](int[apN]):
											self.indiLOG.log(10,u"DC-WF-old  {:15s} oldAP:{}; {};  idletime old:{}/new:{} reject entry, still managed by old AP, not switched yet.. expired?".format(ipNumber, dev.states[u"AP"], MAC, oldIdle, idletime ))
										continue # oldIdle < 600 is to catch expired devices
								except:
									pass

							if dev.states[u"AP"] != ipNumber+"-#"+unicode(apN):
								self.addToStatesUpdateList(dev.id,u"AP", ipNumber+"-#"+unicode(apN))

							self.MAC2INDIGO[xType][MAC][u"inList"+suffixN] = 1

							if ip != "":
								if dev.states[u"ipNumber"] != ip:
									self.addToStatesUpdateList(dev.id,u"ipNumber", ip)
								self.MAC2INDIGO[xType][MAC][u"ipNumber"] = ip

							if dev.states[u"name"] != nameCl and nameCl !="":
								self.addToStatesUpdateList(dev.id,u"name", nameCl)

							if dev.states[u"GHz"] != GHz:
								self.addToStatesUpdateList(dev.id,u"GHz", GHz)

							if dev.states[u"powerMgmt"+suffixN] != powerMgmt:
								self.addToStatesUpdateList(dev.id,u"powerMgmt"+suffixN, powerMgmt)

							if dev.states[u"rx_tx_Rate"+suffixN] != rxtx:
								self.addToStatesUpdateList(dev.id,u"rx_tx_Rate"+suffixN, rxtx)

							if dev.states[u"noise"+suffixN] != noise:
								uD = True
								try:
									if abs(int(dev.states[u"noise"+suffixN])- int(noise)) < 3:
										uD=	 False
								except: pass
								if uD: self.addToStatesUpdateList(dev.id,u"noise"+suffixN, noise)

							if dev.states[u"signal"+suffixN] != signal:
								uD = True
								try:
									if abs(int(dev.states[u"signal"+suffixN])- int(signal)) < 3:
										uD=	 False
								except: pass
								if uD: self.addToStatesUpdateList(dev.id,u"signal"+suffixN, signal)

							try:	oldUpTime = unicode(int(self.MAC2INDIGO[xType][MAC][u"upTime"+suffixN]))
							except: oldUpTime = "0"
							self.MAC2INDIGO[xType][MAC][u"upTime"+suffixN] = newUpTime

							if dev.states[u"state" + suffixN] != state:
								self.addToStatesUpdateList(dev.id,u"state" + suffixN, state)

							if dev.states[u"AP"].split("-")[0] != ipNumber:
								self.addToStatesUpdateList(dev.id,u"AP", ipNumber+"-#"+unicode(apN) )

							if idletime != "":
								self.MAC2INDIGO[xType][MAC][u"idleTime" + suffixN] =  idletime

							oldStatus = dev.states[u"status"]

							if self.updateDescriptions:
								oldIPX = dev.description.split("-")
								if oldIPX[0] != ipx or (dev.description != ipx + "-" + nameCl+"=WiFi" or len(dev.description) < 5):
									if oldIPX[0] != ipx and oldIPX[0] !="":
										indigo.variable.updateValue(u"Unifi_With_IPNumber_Change",u"{}/{}/{}/{}".format(dev.name, dev.states[u"MAC"], oldIPX[0], ipx) )
									if len(oldIPX) < 2:
										oldIPX.append(nameCl.strip("-"))
									elif len(oldIPX) == 2 and oldIPX[1] == "":
										if nameCl != "":
											oldIPX[1] = nameCl.strip("-")
									oldIPX[0] = ipx
									newDescr = "-".join(oldIPX)
									if (dev.description).find(u"=WiFi")==-1:
										dev.description = newDescr+"=WiFi"
									else:
										dev.description = newDescr
									dev.replaceOnServer()

							expTime = self.getexpT(props)
							if self.decideMyLog(u"DictDetails", MAC=MAC) or self.decideMyLog(u"Logic") or self.debugDevs[u"AP"][int(apN)]:
								self.indiLOG.log(10,u"DC-WF-01   {:15s}  {}; {}; ip:{}; GHz:{}; txRate:{}; rxR:{}; new-oldUPtime:{}-{}; idletime:{}; signal:{}; hostN:{}; powerMgmt:{}; old/new assoc {}/{}; curr status:{}".format(ipNumber, MAC, dev.name, ip, GHz, txRate, rxRate,  newUpTime, oldUpTime, idletime, signal, nameCl, powerMgmt, oldAssociated.split("-")[0], newAssociated, dev.states[u"status"]))


							# check what is used to determine up / down, make WiFi a priority
							if ( "useWhatForStatus" not in	props ) or ( "useWhatForStatus" in props and props[u"useWhatForStatus"].find(u"WiFi") == -1 ):
								try:
									if time.time() - time.mktime(datetime.datetime.strptime(dev.states[u"created"], "%Y-%m-%d %H:%M:%S").timetuple()) <	 60:
										props = dev.pluginProps
										props[u"useWhatForStatus"]		= "WiFi,DHCP"
										props[u"useWhatForStatusWiFi"]	= "Optimized"
										dev.replacePluginPropsOnServer(props)
										props = dev.pluginProps
								except:
									self.addToStatesUpdateList(dev.id,u"created", datetime.datetime.now().strftime(u"%Y-%m-%d %H:%M:%S"))
									props = dev.pluginProps
									props[u"useWhatForStatus"]		= "WiFi,DHCP"
									props[u"useWhatForStatusWiFi"]	= "Optimized"
									dev.replacePluginPropsOnServer(props)
									props = dev.pluginProps

							if u"useWhatForStatus" in props and props[u"useWhatForStatus"].find(u"WiFi") > -1:

								if u"useWhatForStatusWiFi" not in props or ("useWhatForStatusWiFi" in props and	props[u"useWhatForStatusWiFi"] !="FastDown"):

									try:	 newUpTime = int(newUpTime)
									except:	 newUpTime = int(oldUpTime)
									try:
										idleTimeMaxSecs	 = float(props[u"idleTimeMaxSecs"])
									except:
										idleTimeMaxSecs = 5

									if u"useWhatForStatusWiFi" in props and ( props[u"useWhatForStatusWiFi"] == "Optimized"):
										if self.decideMyLog(u"DictDetails", MAC=MAC) or self.decideMyLog(u"Logic", MAC=MAC): self.indiLOG.log(10,u"DC-WF-o1   {:15s}  {}; .. using optimized for status; idle uptimes {} < {} or uptime (new){} != {}(Old)" .format(ipNumber, MAC, idletime, idleTimeMaxSecs, newUpTime, oldUpTime))

										if oldStatus == "up":
											if (  float(newUpTime) != float(oldUpTime)	) or  ( float(idletime)  < idleTimeMaxSecs ):
													if self.decideMyLog(u"DictDetails", MAC=MAC): self.indiLOG.log(10,u"DC-WF-o2R  {:15s}  {}; ==> restart exptimer use idleTime, exp-time left:{:5.1f}".format(ipNumber, MAC, expTime -(time.time()-self.MAC2INDIGO[xType][MAC][u"lastUp"])))
													self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
											else:
												if ( oldAssociated.split("-")[0] != newAssociated ): # ignore new AP
													if self.decideMyLog(u"Logic", MAC=MAC): self.indiLOG.log(10,u"DC-WF-o3R  {:15s}  {}; ==> restart exptimer, associated to new AP:{} from:{}, exp-time left:{:5.1f}".format(ipNumber, MAC, oldAssociated, newAssociated, expTime -(time.time()-self.MAC2INDIGO[xType][MAC][u"lastUp"])) )
													self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
												else: # same old
													if self.decideMyLog(u"DictDetails", MAC=MAC): self.indiLOG.log(10,u"DC-WF-o4DN {:15s}  {}; set timer to expire in 10 secs use idleTime/uptime".format(ipNumber, MAC))
													self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()- expTime + 10

										else: # old = down
											if ( float(newUpTime) != float(oldUpTime) ) or (  float(idletime) <= idleTimeMaxSecs ):
												if self.decideMyLog(u"DictDetails", MAC=MAC): self.indiLOG.log(10,u"DC-WF-o5   {:15s}  {}; status Down->up; ==> restart exptimer, use idleTime/uptime, exp-time left:{:5.1f}".format(ipNumber, MAC, expTime -(time.time()-self.MAC2INDIGO[xType][MAC][u"lastUp"]) ))
												self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
												self.setImageAndStatus(dev, "up",oldStatus=oldStatus,ts=time.time(),reason=u"DICT "+suffixN+u" "+ipNumber+u" up Optimized")
											else:
												if ( oldAssociated.split("-")[0] != newAssociated ): # ignore new AP
													if self.decideMyLog(u"Logic", MAC=MAC): self.indiLOG.log(10,u"DC-WF-o6R  {:15s}  {}; ==> restart exptimer, status up new AP; use idleTime/uptime, exp-time left:{:5.1f}".format(ipNumber, MAC, expTime -(time.time()-self.MAC2INDIGO[xType][MAC][u"lastUp"])))
													self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()


									elif u"useWhatForStatusWiFi" in props and (props[u"useWhatForStatusWiFi"] =="IdleTime" ):
										if self.decideMyLog(u"DictDetails", MAC=MAC) or self.decideMyLog(u"Logic", MAC=MAC): self.indiLOG.log(10,u"DC-WF-i0-  {:15s}  {};.  IdleTime..  checking IdleTime {} < {}  old/new associated {}/{}".format(ipNumber, MAC,idletime, idleTimeMaxSecs, oldAssociated.split("-")[0], newAssociated)) 
					
										if float(idletime)	> idleTimeMaxSecs and oldStatus == "up":
											if ( oldAssociated.split("-")[0] == newAssociated ):
												if u"usePingDOWN" in props and props[u"usePingDOWN"] and self.sendWakewOnLanAndPing(MAC,dev.states[u"ipNumber"], props=props, calledFrom ="doWiFiCLIENTSdict") ==0:
														if self.decideMyLog(u"DictDetails"): self.indiLOG.log(10,u"DC-WF-i1R  {:15s}  {}; reset exptimer, ping was test up, exp-time left:{:5.1f}".format(ipNumber, MAC, expTime -(time.time()-self.MAC2INDIGO[xType][MAC][u"lastUp"])) )
														self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
												else:
													if self.decideMyLog(u"DictDetails", MAC=MAC): self.indiLOG.log(10,u"DC-WF-i2DN {:15s}  {}; status down in 10 secs".format(ipNumber, MAC))
													self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()- expTime + 10
											else:
												if self.decideMyLog(u"DictDetails", MAC=MAC): self.indiLOG.log(10,u"DC-WF-i3R  {:15s}  {}; status up new AP use IdleTime, exp-time left:{:5.1f}".format(ipNumber, MAC, expTime -(time.time()-self.MAC2INDIGO[xType][MAC][u"lastUp"])))
												self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()

										elif float(idletime)  <= idleTimeMaxSecs:
											if self.decideMyLog(u"DictDetails", MAC=MAC): self.indiLOG.log(10,u"DC-WF-i4R  {:15s}  {}; ==> restart exptimer, use IdleTime, exp-time left:{:5.1f}".format(ipNumber, MAC, expTime -(time.time()-self.MAC2INDIGO[xType][MAC][u"lastUp"])))
											self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
											if oldStatus != "up":
												self.setImageAndStatus(dev, "up",oldStatus=oldStatus,ts=time.time(),reason=u"DICT "+ipNumber+u" "+suffixN+u" up IdleTime")
												if self.decideMyLog(u"Logic", MAC=MAC): self.indiLOG.log(10,u"DC-WF-i5R  {:15s}  {}; status up, use IdleTime".format(ipNumber, MAC))


									elif u"useWhatForStatusWiFi" in props and (props[u"useWhatForStatusWiFi"] == "UpTime" ):
										if self.decideMyLog(u"DictDetails", MAC=MAC) or self.decideMyLog(u"Logic", MAC=MAC): self.indiLOG.log(10,u"DC-WF-U1   .. using  UpTime for status" )
										if newUpTime == oldUpTime and oldStatus == "up":
											if u"usePingUP" in props and props[u"usePingUP"] and self.sendWakewOnLanAndPing(MAC,dev.states[u"ipNumber"], props=props, calledFrom ="doWiFiCLIENTSdict") == 0:
													if self.decideMyLog(u"DictDetails", MAC=MAC):self.indiLOG.log(10,u"DC-WF-u2   {:15s}   {}; ==> restart exptimer, ping test ok, exp-time left:{:5.1f}".format(ipNumber, MAC, expTime -(time.time()-self.MAC2INDIGO[xType][MAC][u"lastUp"])) )
													self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
											else:
												if self.decideMyLog(u"DictDetails", MAC=MAC): self.indiLOG.log(10,u"DC-WF-u3DN {:15s}  {}; let timer expire, Uptime is not changed".format(ipNumber, MAC) )

										elif newUpTime != oldUpTime and oldStatus != u"up":
											self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
											self.setImageAndStatus(dev, u"up",oldStatus=oldStatus, ts=time.time(), level=1, text1=dev.name.ljust(30) + " "+MAC+u" status up  WiFi DICT Uptime",iType=u"DC-WF-U2",reason=u"DICT "+ipNumber+u" "+suffixN+u" up time")

										elif oldStatus == u"up":
											if self.decideMyLog(u"DictDetails", MAC=MAC): self.indiLOG.log(10,u"DC-WF-u4   {:15s}  {}; ==> restart exptimer, normal extension, exp-time left:{:5.1f}".format(ipNumber, MAC, expTime -(time.time()-self.MAC2INDIGO[xType][MAC][u"lastUp"])))
											self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()


									else:
										self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
										if oldStatus != "up":
											self.setImageAndStatus(dev, "up", oldStatus=oldStatus,level=1, text1=dev.name.ljust(30) + " "+MAC+u" status up    WiFi DICT general", iType=u"DC-WF-UE   ",reason=u"DICT "+suffixN+u" "+ipNumber+u" up else")
								continue

								#break

					if new and not self.ignoreNewClients:
						try:
							dev = indigo.device.create(
								protocol		=indigo.kProtocol.Plugin,
								address			=MAC,
								name=			devName + u"_" + MAC,
								description		=ipx + u"-" + nameCl+"=Wifi",
								pluginId		=self.pluginId,
								deviceTypeId	=devType,
								folder			=self.folderNameIDCreated,
								props			={u"useWhatForStatus":u"WiFi,DHCP", u"useWhatForStatusWiFi":u"Expiration",isType:True})
						except	Exception, e:
							if unicode(e).find(u"None") == -1:
								self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
							try:
								devName += u"_"+( unicode(time.time() - int(time.time())) ).split(".")[1] # create random name
								self.indiLOG.log(30,u"trying again to create device with different name "+devName)
								dev = indigo.device.create(
									protocol		=indigo.kProtocol.Plugin,
									address			=MAC,
									name			=devName + u"_" + MAC,
									description		=ipx + u"-" + nameCl+"=Wifi",
									pluginId		=self.pluginId,
									deviceTypeId	=devType,
									folder			=self.folderNameIDCreated,
									props			={u"useWhatForStatus":u"WiFi,DHCP", u"useWhatForStatusWiFi":u"Expiration",isType:True})
							except	Exception, e:
								if unicode(e).find(u"None") == -1:
									self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
								continue


						self.setupStructures(xType, dev, MAC)
						self.setupBasicDeviceStates(dev, MAC, xType, ip, ipNumber, "", u" status up   new Device", "DC-AP-WF-f ")
						self.addToStatesUpdateList(dev.id,u"AP", ipNumber+"-#"+unicode(apN))
						self.addToStatesUpdateList(dev.id,u"powerMgmt"+suffixN, powerMgmt)
						self.addToStatesUpdateList(dev.id,u"name", nameCl)
						self.addToStatesUpdateList(dev.id,u"rx_tx_Rate" + suffixN, rxtx)
						self.addToStatesUpdateList(dev.id,u"signal" + suffixN, signal)
						self.addToStatesUpdateList(dev.id,u"noise" + suffixN, noise)
						self.MAC2INDIGO[xType][MAC][u"idleTime" + suffixN] = idletime
						self.MAC2INDIGO[xType][MAC][u"inList"+suffixN] = 1
						self.addToStatesUpdateList(dev.id,u"state"+suffixN, state)
						self.MAC2INDIGO[xType][MAC][u"upTime"+suffixN] = newUpTime
						self.executeUpdateStatesList()
						dev = indigo.devices[dev.id]
						self.setupStructures(xType, dev, MAC)
						indigo.variable.updateValue(u"Unifi_New_Device", u"{}/{}/{}".format(dev.name, MAC, ipx) )

					self.executeUpdateStatesList()

				self.doInList(suffixN,wifiIPAP=ipNumber)
				self.executeUpdateStatesList()

			except	Exception, e:
				if unicode(e).find(u"None") == -1:
					self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

			#if time.time()-waitT > 0.001: #self.myLog( text=unicode(self.blockAccess).ljust(28)+part.ljust(18)+"    exectime> %6.3f"%(time.time()-waitT)+ " @ "+datetime.datetime.now().strftime("%M:%S.%f")[:-3])
			if len(self.blockAccess)>0:	 del self.blockAccess[0]
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
					self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return 	clientHostNames




	####-----------------	 ---------
	## AP devices themselves  DICT
	####-----------------	 ---------
	def doAPdictsSELF(self,apDict, apNumb, ipNDevice, MAC, hostname, ipNumber, clientHostNames):

		part="doAPdictsSELF"+unicode(random.random()); self.blockAccess.append(part)
		for ii in range(90):
				if len(self.blockAccess) == 0 or self.blockAccess[0] == part: break # my turn?
				self.sleep(0.1)
		if ii >= 89: self.blockAccess = [] # for safety if too long reset list

		if u"model_display" in apDict:  model = (apDict[u"model_display"])
		else:
			self.indiLOG.log(30,u"model_display not in dict doAPdicts")
			model = ""


		devType ="Device-AP"
		isType	= "isAP"
		devName = "AP"
		xType	= "AP"
		try:


			for GHz in [u"2",u"5"]:
				nClients = 0
				essid	  = ""
				radio	  = ""
				tx_power  = ""
				for jj in range(len(apDict[u"vap_table"])):
					shortC	= apDict[u"vap_table"][jj]
					if u"usage" in shortC: #skip if not wireless
						if shortC[u"usage"] == u"downlink": continue
						if shortC[u"usage"] == u"uplink":	  continue
					channel = shortC[u"channel"]
					if not( GHz == u"2" and channel < 14 or GHz == u"5" and channel > 13): continue 
					nClients += shortC[u"num_sta"]
					essid	  += unicode(shortC[u"essid"]) + "; "
					radio	  =  unicode(shortC[u"radio"])
					tx_power  =  unicode(shortC[u"tx_power"])
					#if self.decideMyLog(u"Special"): self.indiLOG.log(10,u"doAPdictsSELF {} - GHz:{}, sta:{}, essid:{}, radio:{}, tx:{}".format(MAC, GHz, nClients, essid, radio, tx_power)  )

					new = True
					if MAC in self.MAC2INDIGO[xType]:
						try:
							dev = indigo.devices[self.MAC2INDIGO[xType][MAC][u"devId"]]
							if dev.deviceTypeId != devType: 1 / 0
							#self.myLog( text=MAC + " " + dev.name)
							new = False
						except:
							if self.decideMyLog(u"Logic"): self.indiLOG.log(10, u"{}  {} wrong {}".format(MAC, self.MAC2INDIGO[xType][MAC], devType) )
							for dev in indigo.devices.iter(u"props."+isType):
								if u"MAC" not in dev.states: continue
								if dev.states[u"MAC"] != MAC: continue
								self.MAC2INDIGO[xType][MAC][u"devId"] = dev.id
								new = False
								break
					if not new:
							if self.decideMyLog(u"DictDetails", MAC=MAC): self.indiLOG.log(10,u"DC-AP---   {} hostname:{} MAC:{}; GHz:{}; essid:{}; channel:{}; nClients:{}; tx_power:{}; radio:{}".format(ipNumber, hostname, MAC, GHz, essid, channel, nClients, tx_power, radio))
							if u"uptime" in apDict and apDict[u"uptime"] !="":
								if u"upSince" in dev.states:
									self.addToStatesUpdateList(dev.id,u"upSince", time.strftime("%Y-%d-%m %H:%M:%S", time.localtime(time.time() - apDict[u"uptime"])) )
							if tx_power != dev.states[u"tx_power_" + GHz]:
								self.addToStatesUpdateList(dev.id,u"tx_power_" + GHz, tx_power)
							if unicode(channel) != dev.states[u"channel_" + GHz]:
								self.addToStatesUpdateList(dev.id,u"channel_" + GHz, unicode(channel) )
							if essid.strip("; ") != dev.states[u"essid_" + GHz]:
								self.addToStatesUpdateList(dev.id,u"essid_" + GHz, essid.strip("; "))
							if unicode(nClients) != dev.states[u"nClients_" + GHz]:
								self.addToStatesUpdateList(dev.id,u"nClients_" + GHz, unicode(nClients) )
							if radio != dev.states[u"radio_" + GHz]:
								self.addToStatesUpdateList(dev.id,u"radio_" + GHz, radio)
							self.MAC2INDIGO[xType][MAC][u"ipNumber"] = ipNumber
							if ipNumber != dev.states[u"ipNumber"]:
								self.addToStatesUpdateList(dev.id,u"ipNumber", ipNumber)
							if hostname != dev.states[u"hostname"]:
								self.addToStatesUpdateList(dev.id,u"hostname", hostname)
							if dev.states[u"status"] != "up":
								self.setImageAndStatus(dev, "up", oldStatus=dev.states[u"status"],ts=time.time(),  level=1, text1=dev.name.ljust(30) + u" status up            AP    DICT", reason=u"AP DICT", iType=u"STATUS-AP")
							self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
							if dev.states[u"model"] != model and model != u"":
								self.addToStatesUpdateList(dev.id,u"model", model)
							if dev.states[u"apNo"] != apNumb:
								self.addToStatesUpdateList(dev.id,u"apNo", apNumb)

							self.setStatusUpForSelfUnifiDev(MAC)


					if new:
						try:
							dev = indigo.device.create(
								protocol		=indigo.kProtocol.Plugin,
								address			=MAC,
								name			=devName + u"_" + MAC,
								description		=self.fixIP(ipNumber) + u"-" + hostname,
								pluginId		=self.pluginId,
								deviceTypeId	=devType,
								folder			=self.folderNameIDCreated,
								props			={u"useWhatForStatus":"",isType:True})
							self.setupStructures(xType, dev, MAC)
							self.setupBasicDeviceStates(dev, MAC, u"AP", ipNumber,"", "", u" status up            AP DICT  new AP", u"STATUS-AP")
							self.addToStatesUpdateList(dev.id,u"essid_" + GHz, essid)
							self.addToStatesUpdateList(dev.id,u"channel_" + GHz, channel)
							self.addToStatesUpdateList(dev.id,u"MAC", MAC)
							self.addToStatesUpdateList(dev.id,u"hostname", hostname)
							self.addToStatesUpdateList(dev.id,u"nClients_" + GHz, unicode(nClients) )
							self.addToStatesUpdateList(dev.id,u"radio_" + GHz, radio)
							self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
							self.addToStatesUpdateList(dev.id,u"model", model)
							self.addToStatesUpdateList(dev.id,u"tx_power_" + GHz, tx_power)
							dev = indigo.devices[dev.id]
							self.setupStructures(xType, dev, MAC)
							self.buttonConfirmGetAPDevInfoFromControllerCALLBACK()
							indigo.variable.updateValue(u"Unifi_New_Device", u"{}/{}/{}".format(dev.name, MAC, ipNumber) )
						except	Exception, e:
						  if unicode(e).find(u"None") == -1:
								self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))


					self.addToStatesUpdateList(dev.id,u"clientList_"+GHz+"GHz", clientHostNames[GHz].strip("; "))

			self.executeUpdateStatesList()

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

		#if time.time()-waitT > 0.001: #self.myLog( text=unicode(self.blockAccess).ljust(28)+part.ljust(18)+"    exectime> %6.3f"%(time.time()-waitT)+ " @ "+datetime.datetime.now().strftime("%M:%S.%f")[:-3])
		if len(self.blockAccess)>0:	 del self.blockAccess[0]
		return




	####-----------------	 ---------
	def doGatewaydictSELF(self, gwDict, ipNumber):

		part="doGatewaydict"+unicode(random.random()); self.blockAccess.append(part)
		for ii in range(90):
				if len(self.blockAccess) == 0 or self.blockAccess[0] == part: break # my turn?
				self.sleep(0.1)
		if ii >= 89: self.blockAccess = [] # for safety if too long reset list

		try:

			devType  = u"gateway"
			devName  = u"gateway"
			isType	 = u"isGateway"
			xType	 = u"GW"
			suffixN	 = u"DHCP"
			##########	do gateway params  ###
			#self.myLog( text=" GW dict if_table:"+json.dumps(gwDict, sort_keys=True, indent=2 ) )


			#  get lan info ------
			ipNDevice	= ""
			MAClan		= ""
			lan			= {}
			model		= ""
			cpuPercent	= ""
			memPercent	= ""
			temperature = ""
			temperature_Board_CPU 	= ""
			temperature_Board_PHY 	= ""
			temperature_CPU 		= ""
			temperature_PHY 		= ""

			publicIP	= ""
			wan			= {}
			MAC			= ""
			gateways	= ""
			wanUP		= False
			wanPingTime = ""
			wanSpeedTest= ""
			wanLatency	= ""
			wanDownload = ""
			wanUpload	= ""
			nameservers = "-"
			wanRunDate	= ""
			wanUpTime	= ""
			gateways	= "-"

			publicIP2	= ""
			wan2		= {}
			MACwan2		= ""
			gateways2	= "-"
			wan2UP		= False
			wan2PingTime = ""
			wan2SpeedTest= ""
			wan2Latency	= ""
			wan2Download = ""
			wan2Upload	= ""
			nameservers2 = "-"
			wan2RunDate	= ""
			wan2UpTime	= ""
			gateways2	= "-"

			wanSetup	= u"wan1 only"


			if self.decideMyLog(u"UDM"):  self.indiLOG.log(10,u"doGw     unifiControllerType:{}; if.. find UDM >-1:{}".format(self.unifiControllerType, self.unifiControllerType.find(u"UDM") > -1) )

			if self.unifiControllerType.find(u"UDM") > -1:   

				if u"if_table" not in gwDict: 
					if self.decideMyLog(u"UDM"): self.indiLOG.log(10,u"doGw     UDM gateway \"if_table\" not in gwDict")
					return

				if u"ip" in gwDict:	   
					publicIP	   = gwDict[u"ip"].split(u"/")[0]
				else:
					if self.decideMyLog(u"UDM"): self.indiLOG.log(10,u"doGw    UDM gateway no public IP number found: \"ip\" not in gwDict")
					return 

				nameList = {}
				for table in gwDict[u"if_table"]:
					if u"name" in table: 
						nameList[table[u"name"]] = ""
						if u"mac" in table:
							nameList[table[u"name"]] = table[u"mac"]

				for ethName in nameList:
					for table in gwDict[u"port_table"]:
						if ethName in table:
							if u"mac" in table: 
								nameList[ethName] = mac


				###  wan default
				#  udm-pro
				#   wan  = eth8
				#   wan2 = eth9
				# udm has no second wan on the dedicated Unifi lte modem allows inetrnet backup 
				#   not supported yet , only use wan not wan2
				wan = {}
				for table in gwDict[u"if_table"]:
					if self.unifiControllerType == u"UDM":
						if table[u"ip"] == publicIP:
							wan = table
							if u"speedtest-status" in table:
								wan[u"latency"] 		= table[u"speedtest-status"][u"latency"]
								wan[u"xput_down"] 		= table[u"speedtest-status"][u"xput_download"]
								wan[u"xput_up"] 		= table[u"speedtest-status"][u"xput_upload"]
								wan[u"speedtest_ping"] 	= table[u"speedtest-status"][u"status_ping"]
							if u"name" in table:
								if table[u"name"] in nameList:
									wan[u"mac"] =  nameList[table[u"name"]]
							break

					else:
						if table[u"name"] == u"eth8":
							wan = table
							if u"speedtest-status" in table:
								wan[u"latency"] 		= table[u"speedtest-status"][u"latency"]
								wan[u"xput_down"] 		= table[u"speedtest-status"][u"xput_download"]
								wan[u"xput_up"] 		= table[u"speedtest-status"][u"xput_upload"]
								wan[u"speedtest_ping"] 	= table[u"speedtest-status"][u"status_ping"]
							if u"name" in table:
								if table[u"name"] in nameList:
									wan[u"mac"] =  nameList[table[u"name"]]
							break


				wan2 = {}
				if self.unifiControllerType != u"UDM": # for UDM pro only
					for table in gwDict[u"if_table"]:
						if table[u"name"] == u"eth9":
							wan2 = table
							if u"speedtest-status" in table:
								wan2[u"latency"] 			= table[u"speedtest-status"][u"latency"]
								wan2[u"xput_down"] 			= table[u"speedtest-status"][u"xput_download"]
								wan2[u"xput_up"] 			= table[u"speedtest-status"][u"xput_upload"]
								wan2[u"speedtest_ping"] 	= table[u"speedtest-status"][u"status_ping"]
							if u"name" in table:
								if table[u"name"] in nameList:
									wan2[u"mac"] =  nameList[table[u"name"]]
							break


				lan = {}
				for table in gwDict[u"if_table"]:
					if u"ip" not in table: continue
					if table[u"ip"] == ipNumber:
						lan = table
						if u"name" in table:
							if table[u"name"] in nameList:
								wan[u"mac"] =  nameList[table[u"name"]]
						break

				if lan == {} or wan == {}: 
					if self.decideMyLog(u"UDM"): self.indiLOG.log(10,u"doGw    UDM gateway nameList:{};  ip:{}; wan:{} / lan:{};  not found in \"if_table\"".format(ipNumber, nameList, lan, wan) )
					return 

				ipNDevice = ipNumber

				if self.decideMyLog(u"UDM"): self.indiLOG.log(10,u"doGw    UDM gateway ip:{}; nameList:{}\nwan:{}\nlan:{}".format(ipNumber, lan, wan, nameList) )


			else: # non UDM type 
				if u"if_table"			  not in gwDict: 
					return
				if	  u"config_port_table"	  in gwDict: table = u"config_port_table"
				elif  u"config_network_ports"  in gwDict: table = u"config_network_ports"
				else:									 
					return

				if u"connect_request_ip" in gwDict:
					ipNDevice = self.fixIP(gwDict[u"connect_request_ip"])
				if ipNDevice == "": 
					return

				if table == "config_network_ports":
						if u"LAN" in gwDict[table]:
							ifnameLAN = gwDict[table][u"LAN"]
							for xx in range(len(gwDict[u"if_table"])):
								if u"name" in gwDict[u"if_table"][xx] and gwDict[u"if_table"][xx][u"name"] == ifnameLAN:
									lan = gwDict[u"if_table"][xx]
						if u"WAN" in gwDict[table]:
							ifnameWAN = gwDict[table][u"WAN"]
							for xx in range(len(gwDict[u"if_table"])):
								if u"name" in gwDict[u"if_table"][xx] and gwDict[u"if_table"][xx][u"name"] == ifnameWAN:
									wan = gwDict[u"if_table"][xx]
						if u"WAN2" in gwDict[table]:
							ifnameWAN2 = gwDict[table][u"WAN2"]
							for xx in range(len(gwDict[u"if_table"])):
								if u"name" in gwDict[u"if_table"][xx] and gwDict[u"if_table"][xx][u"name"] == ifnameWAN2:
									wan2 = gwDict[u"if_table"][xx]

				elif table == "config_port_table":
					for xx in range(len(gwDict[table])):
						if u"name" in gwDict[table][xx] and gwDict[table][xx][u"name"].lower() == "lan":
							ifnameLAN = gwDict[table][xx][u"ifname"]
							if u"name" in gwDict[u"if_table"][xx] and gwDict[u"if_table"][xx][u"name"] == ifnameLAN:
								lan = gwDict[u"if_table"][xx]
						if u"name" in gwDict[table][xx] and gwDict[table][xx][u"name"].lower() =="wan":
							ifnameWAN = gwDict[table][xx][u"ifname"]
							if u"name" in gwDict[u"if_table"][xx] and gwDict[u"if_table"][xx][u"name"] == ifnameWAN:
								wan = gwDict[u"if_table"][xx]
						if u"name" in gwDict[table][xx] and gwDict[table][xx][u"name"].lower() =="wan2":
							ifnameWAN2 = gwDict[table][xx][u"ifname"]
							if u"name" in gwDict[u"if_table"][xx] and gwDict[u"if_table"][xx][u"name"] == ifnameWAN2:
								wan2 = gwDict[u"if_table"][xx]



			if u"model_display" 	in gwDict:						model		= gwDict[u"model_display"]
			else:
				self.indiLOG.log(10,u"model_display not in dict doGatewaydict")

			if u"uptime" in wan2:								wan2UpTime = self.convertTimedeltaToDaysHoursMin(wan2[u"uptime"])
			if u"uptime" in wan:									wanUpTime  = self.convertTimedeltaToDaysHoursMin(wan[u"uptime"])

			if u"gateways" 		in wan:							gateways		= "-".join(wan[u"gateways"])
			if u"gateways" 		in wan2:						gateways2		= "-".join(wan2[u"gateways"])
			if u"nameservers" 	in wan:							nameservers		= "-".join(wan[u"nameservers"])
			if u"nameservers" 	in wan2:						nameservers2	= "-".join(wan2[u"nameservers"])
			if u"mac" 			in wan:							MAC				= wan[u"mac"]
			if u"mac" 			in wan2:						MACwan2			= wan2[u"mac"]


			if u"up" in wan:									wanUP  = wan[u"up"]
			if u"up" in wan2:									wan2UP = wan2[u"up"]

			if   not wanUP and wan2UP: 							wanSetup = "failover"
			elif not wanUP and not wan2UP: 						wanSetup = "wan down"
			elif wanUP     and wan2UP: 							wanSetup = "load balancing"
			else: 												wanSetup = "wan1 only"

			if   "ip" in wan  and wan[u"ip"]  != "" and wanUP: 	publicIP  = wan[u"ip"].split("/")[0]
			elif u"ip" in wan2 and wan2[u"ip"] != "" and wan2UP:	publicIP2 = wan2[u"ip"].split("/")[0]


			#if self.decideMyLog(u"Special"): self.indiLOG.log(10,u"gw dict parameters wan:{}, wan2:{}, macwan:{}, macwan2:{}, publicIP:{}, publicIP2:{}".format(wan,wan2,MAC,MACwan2,publicIP,publicIP2))

			if u"mac" in lan:				MAClan			= lan[u"mac"]
			if u"system-stats" in gwDict:
				sysStats = gwDict[u"system-stats"]
				if u"cpu" in sysStats:	 cpuPercent = sysStats[u"cpu"]
				if u"mem" in sysStats:	 memPercent = sysStats[u"mem"]
				for xx in [u"temps"]:
					if xx in sysStats:
						if len(sysStats[xx]) > 0:
							if type(sysStats[xx]) == type({}):
								try:
									for key, value in sysStats[xx].iteritems():
										if   key == u"Board (CPU)": temperature_Board_CPU 	= GT.getNumber(value)
										elif key == u"Board (PHY)":	temperature_Board_PHY 	= GT.getNumber(value)
										elif key == u"CPU": 		temperature_CPU 		= GT.getNumber(value)
										elif key == u"PHY": 		temperature_PHY 		= GT.getNumber(value)
									#self.myLog( text="doGatewaydictSELF sysStats[temp]ok : "+temperature)
								except:
									self.indiLOG.log(30,u"doGatewaydictSELF sysStats[temp]err : "+unicode(sysStats[xx]))
							else:
								temperature	 = GT.getNumber(sysStats[xx])
								#self.myLog( text="doGatewaydictSELF sysStats: empty "+unicode(sysStats))
			for xx in [u"temperatures"]:
					if xx in gwDict:
						if len(gwDict[xx]) > 0:
							if type(gwDict[xx]) == type([]):
								try:
									for yy in gwDict[xx]:
										if u"name" in yy: 
											if yy[u"name"] == u"Local": 	temperature		 	= GT.getNumber(yy[u"value"])
											if yy[u"name"] == u"PHY":  	temperature_Board_PHY 	= GT.getNumber(yy[u"value"])
											if yy[u"name"] == u"CPU": 	temperature_Board_CPU 	= GT.getNumber(yy[u"value"])
									#self.myLog( text="doGatewaydictSELF sysStats[temp]ok : "+temperature)
								except:
									self.indiLOG.log(30,u"doGatewaydictSELF temperatures[temp]err : "+unicode(gwDict[xx]))
								#self.myLog( text="doGatewaydictSELF sysStats: empty "+unicode(sysStats))

			if u"speedtest_lastrun" in wan and wan[u"speedtest_lastrun"] !=0:
											wanSpeedTest	= datetime.datetime.fromtimestamp(float(wan[u"speedtest_lastrun"])).strftime(u"%Y-%m-%d %H:%M:%S")
			if u"speedtest_lastrun" in wan2 and wan2[u"speedtest_lastrun"] !=0:
											wan2SpeedTest	= datetime.datetime.fromtimestamp(float(wan2[u"speedtest_lastrun"])).strftime(u"%Y-%m-%d %H:%M:%S")
			if u"speedtest_ping" in wan:	wanPingTime		= u"%4.1f" % wan[u"speedtest_ping"] + u"[ms]"
			if u"latency" in wan:			wanLatency		= u"%4.1f" % wan[u"latency"] + u"[ms]"
			if u"xput_down" in wan:			wanDownload		= u"%4.1f" % wan[u"xput_down"] + u"[Mb/S]"
			if u"xput_up" in wan:			wanUpload		= u"%4.1f" % wan[u"xput_up"] + u"[Mb/S]"

			if u"speedtest_ping" in wan2:	wan2PingTime	= u"%4.1f" % wan2[u"speedtest_ping"] + u"[ms]"
			if u"latency" in wan2:			wan2Latency		= u"%4.1f" % wan2[u"latency"] + u"[ms]"
			if u"xput_down" in wan2:		wan2Download	= u"%4.1f" % wan2[u"xput_down"] + u"[Mb/S]"
			if u"xput_up" in wan2:			wan2Upload		= u"%4.1f" % wan2[u"xput_up"] + u"[Mb/S]"


			if self.decideMyLog(u"UDM"): self.indiLOG.log(10,u"UDM gateway   MAC:{} -MAClan{}".format(MAC,MAClan))

			isNew = True

			if MAC in self.MAC2INDIGO[xType]:
				try:
					dev = indigo.devices[self.MAC2INDIGO[xType][MAC][u"devId"]]
					if dev.deviceTypeId != devType: 1 / 0
					#self.myLog( text=MAC + " " + dev.name)
					isNew = False
				except:
					if self.decideMyLog(u"Logic", MAC=MAC): self.indiLOG.log(10,u"{}     {} wrong {}" .format(MAC, self.MAC2INDIGO[xType][MAC], devType) )
					for dev in indigo.devices.iter(u"props."+isType):
						if u"MAC" not in dev.states:			continue
						if dev.states[u"MAC"] != MAC:		continue
						self.MAC2INDIGO[xType][MAC][u"devId"] = dev.id
						isNew = False
						break


			if isNew:
				try:
					dev = indigo.device.create(
						protocol		= indigo.kProtocol.Plugin,
						address 		= MAC,
						name 			= devName+"_" + MAC,
						description 	= self.fixIP(ipNDevice),
						pluginId 		= self.pluginId,
						deviceTypeId 	= devType,
						folder 			= self.folderNameIDCreated,
						props 			= {u"useWhatForStatus":"",isType:True, u"failoverSettings":"copypublicIP", "useWhichMAC":"MAClan","enableBroadCastEvents":"0"})
					self.setupStructures(xType, dev, MAC)
					self.setupBasicDeviceStates(dev, MAC, xType, ipNDevice, "", "", u" status up         GW DICT new gateway if_table", u"STATUS-GW")
					self.executeUpdateStatesList()
					dev = indigo.devices[dev.id]
					self.setupStructures(xType, dev, MAC)
					self.executeUpdateStatesList()
					self.setUpDownStateValue(dev)
					dev = indigo.devices[dev.id]
					indigo.variable.updateValue(u"Unifi_New_Device", u"{}/{}/{}".format(dev.name, MAC, ipNDevice) )
					if self.decideMyLog(u"Dict", MAC=MAC): self.indiLOG.log(10,u"DC-GW-1--- {}  ip:{}  {}  new device".format(MAC, ipNDevice, dev.name) )
					isNew = False #  fill the rest in next section
				except	Exception, e:
					if unicode(e).find(u"None") == -1:
						self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

			if not isNew:
				if u"uptime" in gwDict and gwDict[u"uptime"] != "" and u"upSince" in dev.states:				self.addToStatesUpdateList(dev.id,u"upSince",time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()-gwDict[u"uptime"])) )
				props = dev.pluginProps
				if wanSetup == "failover": 
					if u"failoverSettings" in props and props[u"failoverSettings"] == "copypublicIP":
						publicIP = publicIP2 
						gateways = gateways2 
						nameservers = nameservers2 


				self.MAC2INDIGO[xType][MAC][u"ipNumber"] = ipNDevice
				self.MAC2INDIGO[xType][MAC][u"lastUp"] 	 = time.time()

				if dev.states[u"wanSetup"] 				!= wanSetup: 											self.addToStatesUpdateList(dev.id,u"wanSetup", wanSetup)
				if dev.states[u"MAClan"] 				!= MAClan:												self.addToStatesUpdateList(dev.id,u"MAClan", MAClan)
				if dev.states[u"ipNumber"] 				!= ipNDevice: 											self.addToStatesUpdateList(dev.id,u"ipNumber", ipNDevice)
				if dev.states[u"model"] 				!= model and model != "":								self.addToStatesUpdateList(dev.id,u"model", model)
				if dev.states[u"memPercent"] 			!= cpuPercent and memPercent != "":						self.addToStatesUpdateList(dev.id,u"memPercent", memPercent)
				if dev.states[u"cpuPercent"] 			!= cpuPercent and cpuPercent != "":						self.addToStatesUpdateList(dev.id,u"cpuPercent", cpuPercent)
				if dev.states[u"temperature"] 			!= temperature and temperature != "": 					self.addToStatesUpdateList(dev.id,u"temperature", temperature)
				if dev.states[u"temperature_Board_CPU"]	!= temperature_Board_CPU and temperature_Board_CPU != "": self.addToStatesUpdateList(dev.id,u"temperature_Board_CPU", temperature_Board_CPU)
				if dev.states[u"temperature_Board_PHY"]	!= temperature_Board_PHY and temperature_Board_PHY != "": self.addToStatesUpdateList(dev.id,u"temperature_Board_PHY", temperature_Board_PHY)
				if dev.states[u"temperature_CPU"]		!= temperature_CPU 		 and temperature_CPU != "":		self.addToStatesUpdateList(dev.id,u"temperature_CPU", temperature_CPU)
				if dev.states[u"temperature_PHY"]		!= temperature_PHY 		 and temperature_PHY != "":		self.addToStatesUpdateList(dev.id,u"temperature_PHY", temperature_PHY)

				if dev.states[u"wan"] 					!= wanUP:												self.addToStatesUpdateList(dev.id,u"wan", "up" if wanUP else "down")	
				if dev.states[u"MAC"] 					!= MAC:													self.addToStatesUpdateList(dev.id,u"MAC", MAC)
				if dev.states[u"nameservers"]			!= nameservers:											self.addToStatesUpdateList(dev.id,u"nameservers", nameservers)
				if dev.states[u"gateways"] 				!= gateways:											self.addToStatesUpdateList(dev.id,u"gateways", gateways)
				if dev.states[u"publicIP"] 				!= publicIP:											self.addToStatesUpdateList(dev.id,u"publicIP", publicIP)
				if dev.states[u"wanPingTime"] 			!= wanPingTime: 										self.addToStatesUpdateList(dev.id,u"wanPingTime", wanPingTime)
				if dev.states[u"wanLatency"] 			!= wanLatency: 											self.addToStatesUpdateList(dev.id,u"wanLatency", wanLatency)
				if dev.states[u"wanUpload"] 			!= wanUpload:											self.addToStatesUpdateList(dev.id,u"wanUpload", wanUpload)
				if dev.states[u"wanSpeedTest"] 			!= wanSpeedTest:										self.addToStatesUpdateList(dev.id,u"wanSpeedTest", wanSpeedTest)
				if dev.states[u"wanDownload"] 			!= wanDownload:											self.addToStatesUpdateList(dev.id,u"wanDownload", wanDownload)
				if dev.states[u"wanUpTime"] 			!= wanUpTime: 											self.addToStatesUpdateList(dev.id,u"wanUpTime", wanUpTime)

				if dev.states[u"wan2"] 					!= wan2UP:												self.addToStatesUpdateList(dev.id,u"wan2", "up" if wan2UP else "down")
				if dev.states[u"MACwan2"] 				!= MACwan2:												self.addToStatesUpdateList(dev.id,u"MACwan2", MACwan2)
				if dev.states[u"wan2Nameservers"]		!= nameservers2:										self.addToStatesUpdateList(dev.id,u"wan2Nameservers", nameservers2)
				if dev.states[u"wan2Gateways"] 			!= gateways2:											self.addToStatesUpdateList(dev.id,u"wan2Gateways", gateways2)
				if dev.states[u"wan2PublicIP"] 			!= publicIP2:											self.addToStatesUpdateList(dev.id,u"wan2PublicIP", publicIP2)
				if dev.states[u"wan2PingTime"] 			!= wan2PingTime: 										self.addToStatesUpdateList(dev.id,u"wan2PingTime", wan2PingTime)
				if dev.states[u"wan2Latency"] 			!= wan2Latency:											self.addToStatesUpdateList(dev.id,u"wan2Latency", wan2Latency)
				if dev.states[u"wan2Upload"] 			!= wan2Upload:											self.addToStatesUpdateList(dev.id,u"wan2Upload", wan2Upload)
				if dev.states[u"wan2SpeedTest"] 		!= wan2SpeedTest:										self.addToStatesUpdateList(dev.id,u"wan2SpeedTest", wan2SpeedTest)
				if dev.states[u"wan2Download"] 			!= wan2Download:										self.addToStatesUpdateList(dev.id,u"wan2Download", wan2Download)
				if dev.states[u"wan2UpTime"] 			!= wan2UpTime: 											self.addToStatesUpdateList(dev.id,u"wan2UpTime", wan2UpTime)

				if dev.states[u"status"] 				!= "up":												self.setImageAndStatus(dev, "up",oldStatus=dev.states[u"status"], ts=time.time(), level=1, text1=dev.name.ljust(30) + u" status up   GW DICT if_table", reason="gateway DICT", iType=u"STATUS-GW")


				if self.decideMyLog(u"Dict", MAC=MAC) or self.decideMyLog(u"UDM"): self.indiLOG.log(10,u"DC-GW-1--  {}     ip:{}    {}   new GW data".format(MAC,ipNDevice, dev.name))

				self.setStatusUpForSelfUnifiDev(MAC)

		except	Exception, e:
			self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

		#if time.time()-waitT > 0.001: #self.myLog( text=unicode(self.blockAccess).ljust(28)+part.ljust(18)+"    exectime> %6.3f"%(time.time()-waitT)+ " @ "+datetime.datetime.now().strftime("%M:%S.%f")[:-3])
		if len(self.blockAccess)>0:	 del self.blockAccess[0]
		return


	####-----------------	 ---------
	def convertTimedeltaToDaysHoursMin(self,uptime):
		try:
			ret = ""
			uptime = float(uptime)
			xx = unicode(datetime.timedelta(seconds=uptime)).replace(" days","").replace(" day","").split(",")
			if len(xx) ==2:
				ret = xx[0]+"d "
				yy = xx[1].split(":")
				if len(yy) >1:
					ret += yy[0]+"h " +yy[1]+"m"
			if len(xx) ==1:
				yy = xx[0].split(":")
				if len(yy) >1:
					ret += yy[0]+"h " +yy[1]+"m"
			return ret
		except: pass


	####-----------------	 ---------
	def doNeighborsdict(self,apDict,apNumb, ipNumber):
		part="doNeighborsdict"+unicode(random.random()); self.blockAccess.append(part)
		for ii in range(90):
				if len(self.blockAccess) == 0 or self.blockAccess[0] == part: break # my turn?
				self.sleep(0.1)
		if ii >= 89: self.blockAccess = [] # for safety if too long reset list

		try:
			devType =u"neighbor"
			devName =u"neighbor"
			isType  = "isNeighbor"
			xType   = u"NB"
			for kk in range(len(apDict)):

				shortR = apDict[kk][u"scan_table"]
				for shortC in shortR:
					MAC = unicode(shortC[u"bssid"])
					channel = unicode(shortC[u"channel"])
					essid = unicode(shortC[u"essid"])
					age = unicode(shortC[u"age"])
					adhoc = unicode(shortC[u"is_adhoc"])
					try:
						rssi = unicode(shortC[u"rssi"])
					except:
						rssi = ""
					if u"model_display" in shortC:  model = (shortC[u"model_display"])
					else:
						model = ""

					new = True
					if int(channel) >= 36:
						GHz = u"5"
					else:
						GHz = u"2"
					if MAC in self.MAC2INDIGO[xType]:
						try:
							dev = indigo.devices[self.MAC2INDIGO[xType][MAC][u"devId"]]
							if dev.deviceTypeId != devType: 1 / 0
							new = False
						except:
							if self.decideMyLog(u"Logic", MAC=MAC): self.indiLOG.log(10,MAC + u"     " + unicode(self.MAC2INDIGO[xType][MAC]) + u" wrong " + devType)
							for dev in indigo.devices.iter(u"props."+isType):
								if u"MAC" not in dev.states: continue
								if dev.states[u"MAC"] != MAC: continue
								self.setupStructures(xType, dev, MAC, init=False)
								new = False
								break
					if not new:
							self.MAC2INDIGO[xType][MAC][u"ipNumber"] = ipNumber
							if self.decideMyLog(u"DictDetails", MAC=MAC): self.indiLOG.log(10,u"DC-NB-0-   "+ipNumber+ u" MAC: " + MAC + u" GHz:" + GHz + u"     essid:" + essid + u" channel:" + channel )
							if MAC != dev.states[u"MAC"]:
								self.addToStatesUpdateList(dev.id,u"MAC", MAC)
							if essid != dev.states[u"essid"]:
								self.addToStatesUpdateList(dev.id,u"essid", essid)
							if channel != dev.states[u"channel"]:
								self.addToStatesUpdateList(dev.id,u"channel", channel)
							if channel != dev.states[u"adhoc"]:
								self.addToStatesUpdateList(dev.id,u"adhoc", adhoc)

							signalOLD = [" " for iii in range(_GlobalConst_numberOfAP)]
							signalNEW = copy.copy(signalOLD)
							if rssi != "":
								signalOLD = dev.states[u"Signal_at_APs"].split(u"[")[0].split("/")
								if len(signalOLD) == _GlobalConst_numberOfAP:
									signalNEW = copy.copy(signalOLD)
									signalNEW[apNumb] = unicode(int(-90 + float(rssi) / 99. * 40.))
							if signalNEW != signalOLD or dev.states[u"Signal_at_APs"] == "":
								self.addToStatesUpdateList(dev.id,u"Signal_at_APs", "/".join(signalNEW) + "[dBm]")

							if model != dev.states[u"model"] and model != "":
								self.addToStatesUpdateList(dev.id,u"model", model)
							self.MAC2INDIGO[xType][MAC][u"age"] = age
							self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
							self.setImageAndStatus(dev, "up",oldStatus=dev.states[u"status"], ts=time.time(), level=1, text1=dev.name.ljust(30) + u" status up           neighbor DICT ", reason="neighbor DICT", iType=u"DC-NB-1   ")
							if self.updateDescriptions	and dev.description != "Channel= " + channel.rjust(2).replace(" ", "0") + " - SID= " + essid:
								dev.description = "Channel= " + channel.rjust(2).replace(" ", "0") + " - SID= " + essid
								dev.replaceOnServer()


					if new and not self.ignoreNewNeighbors:
						self.indiLOG.log(10,u"new: neighbor  " +MAC)
						try:
							dev = indigo.device.create(
								protocol		=indigo.kProtocol.Plugin,
								address			=MAC,
								name			=devName + "_" + MAC,
								description		="Channel= " + channel.rjust(2).replace(" ", "0") + " - SID= " + essid,
								pluginId		=self.pluginId,
								deviceTypeId	=devType,
								folder			=self.folderNameNeighbors,
								props			={u"useWhatForStatus":"",isType:True})
						except	Exception, e:
							if unicode(e).find(u"None") == -1:
								self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
							continue

						self.setupStructures(xType, dev, MAC)
						self.addToStatesUpdateList(dev.id,u"channel", channel)
						signalNEW = [" " for iii in range(_GlobalConst_numberOfAP)]
						if rssi != "":
							signalNEW[apNumb] = unicode(int(-90 + float(rssi) / 99. * 40.))
						self.addToStatesUpdateList(dev.id,u"Signal_at_APs", "/".join(signalNEW) + "[dBm]")
						self.addToStatesUpdateList(dev.id,u"essid", essid)
						self.addToStatesUpdateList(dev.id,u"model", model)
						self.MAC2INDIGO[xType][MAC][u"age"] = age
						self.addToStatesUpdateList(dev.id,u"adhoc", adhoc)
						self.setupBasicDeviceStates(dev, MAC, xType, "", "", "", u" status up        neighbor DICT new neighbor", "DC-NB-2   ")
						self.executeUpdateStatesList()
						indigo.variable.updateValue(u"Unifi_New_Device", u"{}".format(dev.name) )
						dev = indigo.devices[dev.id]
						self.setupStructures(xType, dev, MAC)
				self.executeUpdateStatesList()

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

		#if time.time()-waitT > 0.001: #self.myLog( text=unicode(self.blockAccess).ljust(28)+part.ljust(18)+"    exectime> %6.3f"%(time.time()-waitT)+ " @ "+datetime.datetime.now().strftime("%M:%S.%f")[:-3])
		if len(self.blockAccess)>0:	 del self.blockAccess[0]
		return


	####-----------------	 ---------
	#### this does the unifswitch device itself
	####-----------------	 ---------
	def doSWdictSELF(self, theDict, apNumb, ipNDevice, MAC, hostname, ipNumber):

		part="doSWdictSELF"+unicode(random.random()); self.blockAccess.append(part)
		for ii in range(90):
				if len(self.blockAccess) == 0 or self.blockAccess[0] == part: break # my turn?
				self.sleep(0.1)
		if ii >= 89: self.blockAccess = [] # for safety if too long reset list

		if u"model_display" in theDict:	model = (theDict[u"model_display"])
		else:
			self.indiLOG.log(30,u"model_display not in dict doSWdictSELF")
			model = ""


		devName = u"SW"
		xType	= u"SW"
		isType	= "isSwitch"

		try:
			fanLevel	= ""
			if u"fan_level" in theDict:
				fanLevel = unicode(theDict[u"fan_level"])

			temperature = ""
			if u"general_temperature" in theDict:
				if unicode(theDict[u"general_temperature"]) !="0":
					temperature = GT.getNumber(theDict[u"general_temperature"])
			if u"overheating" in theDict:	overHeating	= theDict[u"overheating"]# not in UDM
			else:							overHeating = False
			uptime			= unicode(theDict[u"uptime"])
			portTable		= theDict[u"port_table"]
			nports			= len(portTable)
			nClients		= 0

			if nports not in _numberOfPortsInSwitch:
				for nn in _numberOfPortsInSwitch:
					if nports < nn:
						nports = nn
					if MAC not in self.MAC2INDIGO[xType]:
						self.indiLOG.log(30,u"switch device model {} not support: please contact author. This has {} ports; supported are {}   ports only - remember there are extra ports for fiber cables , using next highest..".format(model, nports, _numberOfPortsInSwitch))

			if nports > _numberOfPortsInSwitch[-1]: return


			devType = u"Device-SW-" + unicode(nports)
			new = True

			if MAC in self.MAC2INDIGO[xType]:
				try:
					dev = indigo.devices[self.MAC2INDIGO[xType][MAC][u"devId"]]
					if dev.deviceTypeId != devType: raise error
					new = False
				except:
					if self.decideMyLog(u"Logic", MAC=MAC): self.indiLOG.log(10,u"{}   {}   wrong  {}".format(MAC, self.MAC2INDIGO[xType][MAC], devType) )
					for dev in indigo.devices.iter(u"props."+isType):
						if u"MAC" not in dev.states: continue
						if dev.states[u"MAC"] != MAC: continue
						self.MAC2INDIGO[xType][MAC][u"devId"] = dev.id
						new = False
						break

			UDMswitch = False
			useIP = ipNumber
			if self.unifiControllerType.find(u"UDM") > -1 and apNumb == self.numberForUDM[u"SW"]:
				if self.decideMyLog(u"UDM"):  self.indiLOG.log(10,u"DC-SW-UDM  using UDM mode  for  {}; IP process:{}; #Dict{}".format(MAC, ipNumber, ipNDevice ) )



			if not new:
					if self.decideMyLog(u"DictDetails", MAC=MAC):  self.indiLOG.log(10,u"DC-SW-0    {}/{};   SW  hostname:{}; MAC:{}".format(ipNumber, ipNDevice, hostname, MAC) )
					self.MAC2INDIGO[xType][MAC][u"ipNumber"] = ipNumber

					if u"uptime" in theDict and theDict[u"uptime"] !="":
						if u"upSince" in dev.states:
							self.addToStatesUpdateList(dev.id,u"upSince", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()-theDict[u"uptime"])) )

					ports = {}
					if dev.states[u"switchNo"] != apNumb:
						self.addToStatesUpdateList(dev.id,u"switchNo", apNumb)

					if u"ports" not in self.MAC2INDIGO[xType][MAC]:
						self.MAC2INDIGO[xType][MAC][u"ports"]={}
					self.MAC2INDIGO[xType][MAC][u"nPorts"] = len(portTable)

					for port in portTable:

						if u"port_idx" not in port: continue
						ID = port[u"port_idx"]
						idS = "%02d" % ID  # state name

						if unicode(ID) not in self.MAC2INDIGO[xType][MAC][u"ports"]:
							self.MAC2INDIGO[xType][MAC][u"ports"][unicode(ID)] = {u"rxLast": 0, u"txLast": 0, u"timeLast": 0,u"poe":"",u"fullDuplex":"",u"link":"",u"nClients":0}
						portsMAC = self.MAC2INDIGO[xType][MAC][u"ports"][unicode(ID)]
						if portsMAC[u"timeLast"] != 0.:
							try:
								dt = max(5, time.time() - portsMAC[u"timeLast"]) * 1000
								rxRate = "%1d" % ((port[u"tx_bytes"] - portsMAC[u"txLast"]) / dt + 0.5)
								txRate = "%1d" % ((port[u"rx_bytes"] - portsMAC[u"rxLast"]) / dt + 0.5)
							except	Exception, e:
								if unicode(e).find(u"None") == -1:
									self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
							###self.myLog( text=u"rxRate: " + unicode(rxRate)+	 u"     txRate: " + unicode(txRate))
							try:
								errors = unicode(port[u"tx_dropped"] + port[u"tx_errors"] + port[u"rx_errors"] + port[u"rx_dropped"])
							except:
								errors = u"?"
							if port[u"full_duplex"]:
								fullDuplex = u"FD"
							else:
								fullDuplex = u"HD"
							portsMAC["fullDuplex"] = fullDuplex+u"-" + (unicode(port[u"speed"]))

							nDevices = 0
							if u"mac_table" in port:
								nDevices = len(port[u"mac_table"])
							portsMAC["nClients"] = nDevices
							ppp = u"#C: " + "%02d" % nDevices # of clients


							SWP = ""
							if u"is_uplink"  in port and port["is_uplink"]:
								SWP = "UL"
								ppp += ";"+SWP


							### check if another unifi switch or gw is attached to THIS port , add SW:# or GW:0to the port string
							if SWP == "" and u"lldp_table"  in port and len(port["lldp_table"]) >0:
								lldp_table = port[u"lldp_table"][0]
								if u"lldp_chassis_id" in lldp_table and u"lldp_port_id" in lldp_table and u"lldp_system_name" in lldp_table:
									try:
										LinkName = 			lldp_table[u"lldp_system_name"].lower()
										macUPdowndevice = 	lldp_table[u"lldp_chassis_id"].lower()
										portID = 			lldp_table[u"lldp_port_id"].lower()

										if	SWP == "" and macUPdowndevice in self.MAC2INDIGO[u"GW"]:
											ppp += ";GW"
											SWP  = "GW"

										if	SWP == "" and macUPdowndevice in self.MAC2INDIGO[u"AP"]:
											ppp += ";AP"
											SWP  = "AP"

										if	SWP == "" and "gatew" in LinkName or "udm" in LinkName and LinkName.find(u"switch") ==-1:
											ppp += ";GW"
											SWP  = "GW"

										if  SWP == "" and macUPdowndevice in self.MAC2INDIGO[xType]:
											try:	portNatSW = ",P:"+portID.split("/")
											except: portNatSW = ""
											SWP = "DL"
											devIdOfSwitch = self.MAC2INDIGO[u"SW"][macUPdowndevice][u"devId"]
											ppp+= ";"+SWP+":"+ unicode(indigo.devices[devIdOfSwitch].states[u"switchNo"])+portNatSW

										if  SWP == "" and "switch" in LinkName:
											ppp += ";DL"
											SWP = "DL"

									except	Exception, e:
											self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

							portsMAC["link"] = SWP

							if self.count_APDL_inPortCount == "0":
								dontCountIf = ["UL","GW","AP","DL"]
							else:
								dontCountIf = ["UL","GW"]

							if SWP not in dontCountIf: 
								nClients += nDevices
							if SWP == "":
								ppp += "; "

							poe = ""
							if u"poe_enable" in port:
								if port[u"poe_enable"]:
									if (u"poe_good" in port and port[u"poe_good"])	:
										poe="poe1"
									elif (u"poe_mode" in port and port[u"poe_mode"] == "passthrough") :
										poe="poeP"
									else:
										poe="poe0"
								else:
										poe="poeX"
							portsMAC["poe"] = poe

							if poe != "":
								ppp += ";"+poe
							else:
								ppp += "; "

							if u"port_" + idS in dev.states:
								if nDevices > 0:
									ppp += u";" + fullDuplex + u"-" + (unicode(port[u"speed"]))
									ppp += u"; err:" + errors
									ppp += u"; rx-tx[kb/s]:" + rxRate + "-" + txRate
								else:
									ppp += "; ; ;"

								if ppp != dev.states[u"port_" + idS]:
									self.addToStatesUpdateList(dev.id,u"port_" + idS, ppp)




						portsMAC[u"txLast"]	   = port[u"tx_bytes"]
						portsMAC[u"rxLast"]	   = port[u"rx_bytes"]
						portsMAC[u"timeLast"]  = time.time()

					if model != dev.states[u"model"] and model !="":
						self.addToStatesUpdateList(dev.id,u"model", model)
					if uptime != self.MAC2INDIGO[xType][MAC][u"upTime"]:
						self.MAC2INDIGO[xType][MAC][u"upTime"] =uptime
					if temperature !="" and "temperature" in dev.states and  temperature != dev.states[u"temperature"]:
						self.addToStatesUpdateList(dev.id,u"temperature", temperature)
					if u"overHeating" in dev.states and overHeating != dev.states[u"overHeating"]:
							self.addToStatesUpdateList(dev.id,u"overHeating", overHeating)
					if useIP != dev.states[u"ipNumber"]:
						self.addToStatesUpdateList(dev.id,u"ipNumber", useIP)
					if hostname != dev.states[u"hostname"]:
						self.addToStatesUpdateList(dev.id,u"hostname", hostname)
					if dev.states[u"status"] != u"up":
						self.setImageAndStatus(dev, u"up",oldStatus=dev.states[u"status"], ts=time.time(), level=1, text1=dev.name.ljust(30) + u" status up            SW    DICT", reason="switch DICT", iType=u"STATUS-SW")
					self.MAC2INDIGO[xType][MAC][u"lastUp"] = time.time()
					if u"fanLevel" in dev.states and  fanLevel != "" and fanLevel != dev.states[u"fanLevel"]:
						self.addToStatesUpdateList(dev.id,u"fanLevel", fanLevel)

					if u"nClients" in dev.states and  nClients != "" and nClients != dev.states[u"nClients"]:
						self.addToStatesUpdateList(dev.id,u"nClients", nClients)


					if self.updateDescriptions:
						ipx = self.fixIP(useIP)
						oldIPX = dev.description.split("-")
						if oldIPX[0] != ipx or ( (dev.description != ipx + "-" + hostname) or len(dev.description) < 5):
							if oldIPX[0] != ipx and oldIPX[0] !="":
								indigo.variable.updateValue(u"Unifi_With_IPNumber_Change", u"{}/{}/{}/{}".format(dev.name, dev.states[u"MAC"], oldIPX[0], ipx) )
							if len(oldIPX) < 2:
								oldIPX.append(hostname.strip("-"))
							elif len(oldIPX) == 2 and oldIPX[1] == "":
								if hostname != "":
									oldIPX[1] = hostname.strip("-")
							oldIPX[0] = ipx
							newDescr = "-".join(oldIPX)
							dev.description = newDescr
							dev.replaceOnServer()


					self.setStatusUpForSelfUnifiDev(MAC)
					#break

			if new:
				newName = devName+u"_" + MAC
				self.indiLOG.log(30,u"creatung new unifi switch device:{};  MAC:{};  IP#in dict:{}; ip# proc:{}; Model:{}; devType:{};  nports:{}".format(newName, MAC, ipNDevice, ipNumber, model, devType, nports) )
				try:
					dev = indigo.device.create(
						protocol 		= indigo.kProtocol.Plugin,
						address 		= MAC,
						name 			= newName,
						description 	= self.fixIP(useIP) + "-" + hostname,
						pluginId 		= self.pluginId,
						deviceTypeId 	= devType,
						folder 			= self.folderNameIDCreated,
						props 			= {u"useWhatForStatus":"",isType:True})
					self.setupStructures(xType, dev, MAC)
					self.MAC2INDIGO[xType][MAC][u"upTime"] = uptime
					self.addToStatesUpdateList(dev.id,u"model", model)
					if temperature != "" and "temperature" in dev.states and  temperature != dev.states[u"temperature"]:
						self.addToStatesUpdateList(dev.id,u"temperature", temperature)
					self.addToStatesUpdateList(dev.id,u"overHeating", overHeating)
					self.addToStatesUpdateList(dev.id,u"hostname", hostname)
					self.addToStatesUpdateList(dev.id,u"switchNo", apNumb)
					self.setupBasicDeviceStates(dev, MAC, xType, useIP, "", "", u" status up     SW DICT  new SWITCH", "STATUS-SW")
					indigo.variable.updateValue(u"Unifi_New_Device", u"{}/{}/{}".format(dev.name, MAC, useIP) )
					dev = indigo.devices[dev.id]
					self.setupStructures(xType, dev, MAC)
				except	Exception, e:
					if unicode(e).find(u"None") == -1:
						self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
						self.indiLOG.log(40,u"     for mac#"+MAC+";  hostname: "+ hostname)
						self.indiLOG.log(40,u"MAC2INDIGO: "+unicode(self.MAC2INDIGO[xType]))

			self.executeUpdateStatesList()

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

		#if time.time()-waitT > 0.001: #self.myLog( text=unicode(self.blockAccess).ljust(28)+part.ljust(18)+"    exectime> %6.3f"%(time.time()-waitT)+ " @ "+datetime.datetime.now().strftime("%M:%S.%f")[:-3])
		if len(self.blockAccess)>0:	 del self.blockAccess[0]

		return

	####----------------- if FINGSCAN is enabled send update signal	 ---------
	def setStatusUpForSelfUnifiDev(self, MAC):
		try:

			if MAC in self.MAC2INDIGO[u"UN"]:
				self.MAC2INDIGO[u"UN"][MAC][u"lastUp"] = time.time()+20
				devidUN = self.MAC2INDIGO[u"UN"][MAC][u"devId"]
				try:
					devUN = indigo.devices[devidUN]
					if devUN.states[u"status"] !=u"up":
						self.addToStatesUpdateList(devidUN,u"status", u"up")
						self.addToStatesUpdateList(devidUN,u"lastStatusChangeReason", u"switch message")
						if self.decideMyLog(u"Logic", MAC=MAC) :  self.indiLOG.log(10,u"updateself setStatusUpForSelfUnifiDev:      updating status to up MAC:" + MAC+"  "+devUN.name+"  was: "+ devUN.states[u"status"] )
					if unicode(devUN.displayStateImageSel) !="SensorOn":
						devUN.updateStateImageOnServer(indigo.kStateImageSel.SensorOn)
				except:pass

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return

	####----------------- if FINGSCAN is enabled send update signal	 ---------
	def sendUpdatetoFingscanNOW(self, force=False):
		try:
			x = ""
			if not self.enableFINGSCAN:
				self.sendUpdateToFingscanList ={}
				return x
			if self.sendUpdateToFingscanList =={} and not force:
				return x
			if self.countLoop < 10:
				self.sendUpdateToFingscanList ={}
				return x  ## only after stable ops for 10 loops ~ 20 secs

			plug = indigo.server.getPlugin("com.karlwachs.fingscan")
			if not plug.isEnabled():
				self.sendUpdateToFingscanList ={}
				return x

			if not force:
				localF = copy.copy(self.sendUpdateToFingscanList)
				for devid in localF:
					if devid !="":
							dev= indigo.devices[int(devid)]
							if dev.deviceTypeId != u"neighbor" or ( dev.deviceTypeId == u"neighbor" and not self.ignoreNeighborForFing) :
								try:
									if self.decideMyLog(u"Fing"): self.indiLOG.log(10,u"FINGSC---   "+u"updating fingscan with " + dev.name + u" = " + dev.states[u"status"])
									plug.executeAction(u"unifiUpdate", props={u"deviceId": [devid]})
									self.fingscanTryAgain = False
								except	Exception, e:
									if unicode(e).find(u"None") == -1:
										self.indiLOG.log(40,u"in Line {} has error={}   finscan update failed".format(sys.exc_traceback.tb_lineno, e) )
									self.fingscanTryAgain = True

			else:
				devIds	  = []
				devNames  = []
				devValues = {}
				stringToPrint = u"\n"
				for dev in indigo.devices.iter(self.pluginId):
					if dev.deviceTypeId == u"client": continue
					devIds.append(unicode(dev.id))
					stringToPrint += dev.name + u"= " + dev.states[u"status"] + u"\n"

				if devIds != []:
					for i in range(3):
						if self.decideMyLog(u"Fing"): self.indiLOG.log(10,u"FINGSC---   "+u"updating fingscan try# " + unicode(i + 1) + u";     with " + stringToPrint )
						plug.executeAction(u"unifiUpdate", props={u"deviceId": devIds})
						self.fingscanTryAgain = False
						break

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			else:
				x = "break"
		self.sendUpdateToFingscanList ={}
		return x

	####----------------- if FINGSCAN is enabled send update signal	 ---------
	def sendBroadCastNOW(self):
		try:
			x = ""
			if	self.enableBroadCastEvents =="0":
				self.sendBroadCastEventsList = []
				return x
			if self.sendBroadCastEventsList == []:
				return x
			if self.countLoop < 10:
				self.sendBroadCastEventsList = []
				return x  ## only after stable ops for 10 loops ~ 20 secs

			msg = copy.copy(self.sendBroadCastEventsList)
			self.sendBroadCastEventsList = []
			if len(msg) >0:
				msg ={"pluginId":self.pluginId,"data":msg}
				try:
					if self.decideMyLog(u"BC"): self.indiLOG.log(10,u"BroadCast-   "+u"updating BC with " + unicode(msg) )
					indigo.server.broadcastToSubscribers(u"deviceStatusChanged", json.dumps(msg))
				except	Exception, e:
					if unicode(e).find(u"None") == -1:
						self.indiLOG.log(40,u"in Line {} has error={}   finscan update failed".format(sys.exc_traceback.tb_lineno, e) )

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			else:
				x = "break"
		return x

	####-----------------	 ---------
	def setupBasicDeviceStates(self, dev, MAC, devType, ip, ipNDevice, GHz, text1, type):
		try:
			self.addToStatesUpdateList(dev.id,u"created", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
			self.addToStatesUpdateList(dev.id,u"MAC", MAC)
			self.MAC2INDIGO[devType][MAC][u"lastUp"] = time.time()
			if ip !="":
				self.addToStatesUpdateList(dev.id,u"ipNumber", ip)

			self.setImageAndStatus(dev, "up",oldStatus=dev.states[u"status"], ts=time.time(), level=1, text1=dev.name.ljust(30) + text1, iType=type,reason="initialsetup")
			vendor = self.getVendortName(MAC)
			if vendor != "":
					self.addToStatesUpdateList(dev.id,u"vendor", vendor)
					self.moveToUnifiSystem(dev, vendor)
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return

	####-----------------	 ---------
	def testIgnoreMAC(self, MAC,  fromSystem="") :
		ignore = False
		#self.myLog( text=u"testIgnoreMAC testing: MAC "+MAC+";  called from: "+fromSystem )
		if MAC in self.MACignorelist:
			if self.decideMyLog(u"IgnoreMAC"):  self.indiLOG.log(10,u"{:10}: ignore list.. ignore MAC:{}".format(fromSystem, MAC))
			return True

		if len(self.MACSpecialIgnorelist) == 0:
			return False

		MACSplit = (MAC.lower()).split(":")
		for MACsp in self.MACSpecialIgnorelist:
			MACSPSplit = (MACsp.lower()).split(":")
			ignore = True
			for nn  in range(6):
				if MACSPSplit[nn] !="xx" and MACSPSplit[nn] != MACSplit[nn]:
					ignore = False
					break
			if ignore:
				if self.decideMyLog(u"IgnoreMAC"):  self.indiLOG.log(10,u"{:10}: ignore list.. ignore MAC:{};  is member of ignore list:{}" .format(fromSystem, MAC, MACsp))
				return True
		return False

	####-----------------	 ---------
	def moveToUnifiSystem(self,dev,vendor):
		try:
			if vendor.upper().find(u"UBIQUIT") >-1:
				indigo.device.moveToFolder(dev.id, value=self.folderNameIDSystemID)
				self.indiLOG.log(10,u"moving "+dev.name+u";  to folderID: "+ unicode(self.folderNameIDSystemID))
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return

	####-----------------	 ---------
	def getVendortName(self,MAC):
		if self.enableMACtoVENDORlookup !="0" and not self.waitForMAC2vendor:
			self.waitForMAC2vendor = self.M2V.makeFinalTable()

		return	self.M2V.getVendorOfMAC(MAC)


	####-----------------	 ---------
	def setImageAndStatus(self, dev, newStatus, oldStatus=u"123abc123abcxxx", ts="", level=1, text1="", iType=u"", force=False, fing=True,reason=u""):
		try:
			if unicode(dev.id) not in self.xTypeMac: 
				self.indiLOG.log(10,u"STAT-Chng  {} not properly setup,  missing in xTypeMac".format(dev.name.ljust(20)) )
				return 

			MAC	  =	 self.xTypeMac[unicode(dev.id)][u"MAC"]
			if self.testIgnoreMAC(MAC, fromSystem="set-image"): return 

			if  self.decideMyLog(u"", MAC=MAC): self.indiLOG.log(10,u"STAT-Chang {} data in: newSt:{}; oldStIn:{}; oldDevSt:{}".format(MAC, newStatus, oldStatus, dev.states[u"status"]))
			if oldStatus == u"123abc123abc":
				oldStatus = dev.states[u"status"]

			try:	xType = self.xTypeMac[unicode(dev.id)]["xType"]
			except: 
				self.indiLOG.log(10,u"STAT-Chang error for devId:{} xType bad:{}".format(dev.id, self.xTypeMac[unicode(dev.id)]))
				return

			if oldStatus != newStatus or force:

				if oldStatus != newStatus:
					if fing and oldStatus != u"123abc123abcxxx":
						self.sendUpdateToFingscanList[unicode(dev.id)] = unicode(dev.id)
					self.addToStatesUpdateList(dev.id,u"status", newStatus)

					if u"lastStatusChangeReason" in dev.states and reason != u"":
						self.addToStatesUpdateList(dev.id,u"lastStatusChangeReason", reason)
					if self.decideMyLog(u"Logic", MAC=MAC): self.indiLOG.log(10,u"STAT-Chang {} st changed  {}->{}; {}".format(dev.states[u"MAC"], dev.states[u"status"], newStatus, text1))

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

		return

	####-----------------	 ---------
	#### wake on lan and pings	START
	####-----------------	 ---------
	def sendWakewOnLanAndPing(self, MAC,IPNumber, nBC=2, waitForPing=500, countPings=1, waitBeforePing=0.5, waitAfterPing=0.5, nPings =1, calledFrom="", props=""):
		try:
			doWOL = True
			if props != "" and "useWOL" in props and props[u"useWOL"] =="0": doWOL = False
			if doWOL:
				self.sendWakewOnLan(MAC, calledFrom=calledFrom)
				if nBC ==2:
					self.sleep(0.05)
					self.sendWakewOnLan(MAC, calledFrom=calledFrom)
				self.sleep(waitBeforePing)
			return self.checkPing(IPNumber, waitForPing=waitForPing, countPings=countPings, nPings=nPings, waitAfterPing=waitAfterPing, calledFrom=calledFrom)
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}  called from: {} ".format(sys.exc_traceback.tb_lineno, e, calledFrom) )
		return

	####-----------------	 ---------
	def checkPing(self, IPnumber , waitForPing=100, countPings=1,nPings=1, waitAfterPing=0.5, calledFrom="",verbose=False):
		try:
			Wait = ""
			if waitForPing != "":
				Wait = "-W "+ unicode(waitForPing)
			Count = "-c 1"

			if countPings != "":
				Count = "-c "+unicode(countPings)

			if nPings == 1 :
				waitAfterPing = 0.

			retCode =1
			for nn in range(nPings):
				retCode = subprocess.call('/sbin/ping -o '+Wait+' '+Count+' -q '+IPnumber+' >/dev/null',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE) # "call" will wait until its done and deliver retcode 0 or >0
				if self.decideMyLog(u"Ping"):  self.indiLOG.log(10,calledFrom+" "+u"ping resp:{}  :{}".format(IPnumber,retCode))
				if retCode ==0:  return 0
				if nn != nPings-1: self.sleep(waitAfterPing)
			if retCode !=0 and verbose:  self.indiLOG.log(10,u"ping to:{}, dev not responding".format(IPnumber))
			return retCode
		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.indiLOG.log(40,u"in Line {} has error={}  called from: {} ".format(sys.exc_traceback.tb_lineno, e, calledFrom) )
		return

	####-----------------	 ---------
	def sendWakewOnLan(self, MAC, calledFrom=""):
		if self.broadcastIP !="9.9.9.255":
			data = ''.join(['FF' * 6, (MAC.upper()).replace(':', '') * 16])
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
			sock.sendto(data.decode("hex"), (self.broadcastIP, 9))
			if self.decideMyLog(u"Ping"):  self.indiLOG.log(10,calledFrom+" "+u"sendWakewOnLan for "+MAC+";    called from "+calledFrom+";  bc ip: "+self.broadcastIP)
		return

	####-----------------	 ---------
	#### wake on lan and pings	END
	####-----------------	 ---------


	####-----------------	 ---------
	def manageLogfile(self, apDict, apNumb,unifiDeviceType):
		try:
				name = self.indigoPreferencesPluginDir + u"dict-"+unifiDeviceType+u"#" + unicode(apNumb)
				self.writeJson( apDict, fName=name+".txt", sort=False, doFormat=True )
		except	Exception, e:
				if unicode(e).find(u"None") == -1:
					self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return


	####-----------------	 ---------
	def exeDisplayStatus(self, dev, status, force=True):
		if status.lower() in [u"up",u"on",u"connected"] :
			dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOn)
		elif status.lower() in [u"down",u"off",u"adopting",u"offline"]:
			dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOff)
		elif status.lower()  in [u"expired",u"rec",u"event",u"motion",u"ring",u"person",u"vehicle"]:
			dev.updateStateImageOnServer(indigo.kStateImageSel.SensorTripped)
		elif status.lower()  in [u"susp"] :
			dev.updateStateImageOnServer(indigo.kStateImageSel.PowerOff)
		elif status == u"" :
			dev.updateStateImageOnServer(indigo.kStateImageSel.SensorTripped)
		if force or status == "":
			dev.updateStateOnServer(u"displayStatus",self.padDisplay(status)+datetime.datetime.now().strftime(u"%m-%d %H:%M:%S"))
			dev.updateStateOnServer(u"status",status)
			dev.updateStateOnServer(u"onOffState",value= dev.states[u"status"].lower() in [u"up",u"rec",u"on",u"connected"], uiValue= dev.states[u"displayStatus"])
		return


	####-----------------	 ---------
	def addToStatesUpdateList(self,devid, key, value):
		try:
			devId = unicode(devid)
			### no down during startup .. 100 secs
			if key == "status" and value.lower() not in[u"up", u"connected", u"event", u"rec", u"motion", u"vehicle", u"person"]:
			   if time.time() - self.pluginStartTime <0:
					#self.indiLOG.log(10,u"in addToStatesUpdateList reject update at startup for devId:{} key:{}; value:{}".format(devid, key, value ) )
					return

			local = copy.deepcopy(self.devStateChangeList)
			if devId not in local:
				local[devId]={}
			if key in local[devId]:
				if value != local[devId][key]:
					local[devId][key] = {}
			local[devId][key] = value
			self.devStateChangeList = copy.deepcopy(local)

		except	Exception, e:
			if len(unicode(e))	> 5 :
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return




	####-----------------	 ---------
	def executeUpdateStatesList(self):
		devId = ""
		key = ""
		local = ""
		try:
			if len(self.devStateChangeList) ==0: return
			local = copy.deepcopy(self.devStateChangeList)
			self.devStateChangeList ={}
			changedOnly = {}
			trigList=[]
			for devId in  local:
				try: int(devId)
				except: continue
				if len( local[devId]) > 0:
					dev =indigo.devices[int(devId)]
					for key in local[devId]:
						value = local[devId][key]
						if unicode(value) != unicode(dev.states[key]):
							if devId not in changedOnly: changedOnly[devId]=[]
							changedOnly[devId].append({u"key":key,u"value":value})
							if key == u"status":
								#self.indiLOG.log(10,u"in executeUpdateStatesList dev {} key:{}; value:{}".format(dev.name, key, value ) )
								ts = datetime.datetime.now().strftime(u"%Y-%m-%d %H:%M:%S")
								changedOnly[devId].append({u"key":u"lastStatusChange", u"value":ts})
								changedOnly[devId].append({u"key":u"displayStatus",	   u"value":self.padDisplay(value)+ts[5:] } )
								changedOnly[devId].append({u"key":u"onOffState",	   u"value":value in ["up","rec","ON"],   u"uiValue":self.padDisplay(value)+ts[5:] } )
								self.exeDisplayStatus(dev, value, force=False)

								self.statusChanged = max(1,self.statusChanged)
								trigList.append(dev.name)
								val = unicode(value).lower()
								if self.enableBroadCastEvents !="0" and val in ["up","down","expired","rec","ON", u"event"]:
									props = dev.pluginProps
									if	self.enableBroadCastEvents == "all" or	("enableBroadCastEvents" in props and props[u"enableBroadCastEvents"] == "1" ):
										msg = {"action":"event", "id":unicode(dev.id), "name":dev.name, "state":"status", "valueForON":"up", "newValue":val}
										if self.decideMyLog(u"BC"):	self.indiLOG.log(10,u"BroadCast "+dev.name+" " +unicode(msg))
										self.sendBroadCastEventsList.append(msg)



					if devId in changedOnly and changedOnly[devId] !=[]:

						self.dataStats[u"updates"][u"devs"]	  +=1
						self.dataStats[u"updates"][u"states"] +=len(changedOnly)
						if self.indigoVersion >6:
							try:
								dev.updateStatesOnServer(changedOnly[devId])
							except	Exception, e:
								self.indiLOG.log(40,u"in Line {} has error={} \n devId:{};     changedOnlyDict:{}".format(sys.exc_traceback.tb_lineno, e, devId , changedOnly[devId] ) )
						else:
							for uu in changedOnly[devId]:
								dev.updateStateOnServer(uu[u"key"],uu[u"value"])

			if len(trigList) >0:
				for devName	 in trigList:
					indigo.variable.updateValue(u"Unifi_With_Status_Change",devName)
				self.triggerEvent(u"someStatusHasChanged")
		except	Exception, e:
			if len(unicode(e))	> 5 :
				self.indiLOG.log(40,u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
				try:
					self.indiLOG.log(40,"{}     {}  {};  devStateChangeList:\n{}".format(dev.name, devId , key, local) )
				except:pass
		if len(self.sendBroadCastEventsList) >0: self.sendBroadCastNOW()
		return

	####-----------------	 ---------
	def padDisplay(self,status):
		if	 status == u"up":		 return status.ljust(11)
		elif status == u"expired":	 return status.ljust(8)
		elif status == u"down":		 return status.ljust(9)
		elif status == u"susp":		 return status.ljust(9)
		elif status == u"changed":	 return status.ljust(8)
		elif status == u"double":	 return status.ljust(8)
		elif status == u"ignored":	 return status.ljust(8)
		elif status == u"off":		 return status.ljust(11)
		elif status == u"REC":		 return status.ljust(9)
		elif status == u"ON":		 return status.ljust(10)
		else:						 return status.ljust(10)
		return

	####-----------------	 ---------
	def escapeExpect(self, inString):
		return inString.replace("#","\\#")


	########################################
	# General Action callback
	######################
	def actionControlUniversal(self, action, dev):
		###### BEEP ######
		if action.deviceAction == indigo.kUniversalAction.Beep:
			# Beep the hardware module (dev) here:
			# ** IMPLEMENT ME **
			indigo.server.log(u"sent \"{}\" beep request not implemented".format(dev.name) )

		###### STATUS REQUEST ######
		elif action.deviceAction == indigo.kUniversalAction.RequestStatus:
			# Query hardware module (dev) for its current status here:
			# ** IMPLEMENT ME **
			indigo.server.log(u"sent \"{}\" status request not implemented".format(dev.name) )
		return

	####-----------------
	########################################
	# Sensor Action callback
	######################
	def actionControlSensor(self, action, dev):
		###### TURN ON ######
		if action.sensorAction == indigo.kSensorAction.TurnOn:
			self.setImageAndStatus(dev, "up",oldStatus=dev.states[u"status"], ts=time.time(), iType=u"actionControlSensor",reason=u"TurnOn")

		###### TURN OFF ######
		elif action.sensorAction == indigo.kSensorAction.TurnOff:
			self.setImageAndStatus(dev, "up",oldStatus=dev.states[u"status"], ts=time.time(), iType=u"actionControlSensor",reason=u"TurnOff")

		###### TOGGLE ######
		elif action.sensorAction == indigo.kSensorAction.Toggle:
			if dev.onState:
				self.setImageAndStatus(dev, "up",oldStatus=dev.states[u"status"], ts=time.time(), iType=u"actionControlSensor",reason=u"toggle")
			else:
				self.setImageAndStatus(dev, "up",oldStatus=dev.states[u"status"], ts=time.time(), iType=u"actionControlSensor",reason=u"toggle")

		self.executeUpdateStatesList()
		return

########################################
########################################
####----checkPluginPath----
########################################
########################################
	####------ --------
	def checkPluginPath(self, pluginName, pathToPlugin):

		if self.pathToPlugin.find(u"/" + self.pluginName + ".indigoPlugin/") == -1:
			self.errorLog(u"--------------------------------------------------------------------------------------------------------------")
			self.errorLog(u"The pluginName is not correct, please reinstall or rename")
			self.errorLog(u"It should be   /Libray/....../Plugins/" + pluginName + ".indigoPlugin")
			p = max(0, pathToPlugin.find(u"/Contents/Server"))
			self.errorLog(u"It is: " + pathToPlugin[:p])
			self.errorLog(u"please check your download folder, delete old *.indigoPlugin files or this will happen again during next update")
			self.errorLog(u"---------------------------------------------------------------------------------------------------------------")
			self.sleep(100)
			return False
		return True

########################################
########################################
####----move files to ...indigo x.y/Preferences/Plugins/< pluginID >.----
########################################
########################################
	####------ --------
	def moveToIndigoPrefsDir(self, fromPath, toPath):
		if os.path.isdir(toPath): 		
			return True
		indigo.server.log(u"--------------------------------------------------------------------------------------------------------------")
		indigo.server.log("creating plugin prefs directory ")
		os.mkdir(toPath)
		if not os.path.isdir(toPath): 	
			self.errorLog("| preference directory can not be created. stopping plugin:  "+ toPath)
			self.errorLog(u"--------------------------------------------------------------------------------------------------------------")
			self.sleep(100)
			return False
		indigo.server.log("| preference directory created;  all config.. files will be here: "+ toPath)
			
		if not os.path.isdir(fromPath): 
			indigo.server.log(u"--------------------------------------------------------------------------------------------------------------")
			return True
		cmd = "cp -R '"+ fromPath+"'  '"+ toPath+"'"
		os.system(cmd )
		self.sleep(1)
		indigo.server.log("| plugin files moved:  "+ cmd)
		indigo.server.log("| please delete old files")
		indigo.server.log(u"--------------------------------------------------------------------------------------------------------------")
		return True


########################################
########################################
####-----------------  logging ---------
########################################
########################################

	####----------------- ---------
	def setLogfile(self, lgFile, config=False):
		self.logFileActive =lgFile
		if   self.logFileActive =="standard":	self.logFile = ""
		elif self.logFileActive =="indigo":		self.logFile = self.indigoPath.split("Plugins/")[0]+"Logs/"+self.pluginId+"/plugin.log"
		else:									self.logFile = self.indigoPreferencesPluginDir +"plugin.log"
		self.myLog( text="myLogSet setting parameters -- logFileActive= {}; logFile= {};  debugLevel= {}".format(self.logFileActive, self.logFile, self.debugLevel), destination="standard")
		if config:
			self.myLog( text="... debug enabled for GW-dev:{}, AP-dev:{}, SW-dev:{}".format( unicode(self.debugDevs[u"GW"]).replace("True","T").replace("False","F"), unicode(self.debugDevs[u"AP"]).replace("True","T").replace("False","F"), unicode(self.debugDevs[u"SW"]).replace("True","T").replace("False","F")), destination="standard")
		return



			
			
	####-----------------	 ---------
	def decideMyLog(self, msgLevel, MAC=""):
		try:
			if MAC != "" and MAC in self.MACloglist:				return True
			if msgLevel	 == u"all" or u"all" in self.debugLevel:	return True
			if msgLevel	 == ""  and u"all" not in self.debugLevel:	return False
			if msgLevel in self.debugLevel:							return True

		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				indigo.server.log( u"decideMyLog in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return False

	####-----------------  print to logfile or indigo log  ---------
	def myLog(self,	 text="", mType=u"", errorType="", showDate=True, destination=""):
		   
	
		try:
			if	self.logFileActive =="standard" or destination.find(u"standard") >-1:
				if errorType == u"smallErr":
					self.errorLog(u"------------------------------------------------------------------------------")
					self.errorLog(text)
					self.errorLog(u"------------------------------------------------------------------------------")

				elif errorType == u"bigErr":
					self.errorLog(u"==================================================================================")
					self.errorLog(text)
					self.errorLog(u"==================================================================================")

				elif mType == "":
					indigo.server.log(text)
				else:
					indigo.server.log(text, type=mType)


			if	self.logFileActive !="standard":

				ts =""
				try:
					if len(self.logFile) < 3: return # not properly defined
					f =	 open(self.logFile,"a")
				except	Exception, e:
					indigo.server.log(u"in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
					try:
						f.close()
					except:
						pass
					return

				if errorType == u"smallErr":
					if showDate: ts = datetime.datetime.now().strftime(u"%H:%M:%S")
					f.write(u"----------------------------------------------------------------------------------\n")
					f.write((ts+u" ".ljust(12)+u"-"+text+u"\n").encode(u"utf8"))
					f.write(u"----------------------------------------------------------------------------------\n")
					f.close()
					return

				if errorType == u"bigErr":
					if showDate: ts = datetime.datetime.now().strftime(u"%H:%M:%S")
					ts = datetime.datetime.now().strftime(u"%H:%M:%S")
					f.write(u"==================================================================================\n")
					f.write((ts+u" "+u" ".ljust(12)+u"-"+text+u"\n").encode(u"utf8"))
					f.write(u"==================================================================================\n")
					f.close()
					return

				if showDate: ts = datetime.datetime.now().strftime(u"%H:%M:%S")
				if mType == u"":
					f.write((ts+u" " +u" ".ljust(25)  +u"-" + text + u"\n").encode(u"utf8"))
				else:
					f.write((ts+u" " +mType.ljust(25) +u"-" + text + u"\n").encode(u"utf8"))
				### print calling function 
				#f.write(u"_getframe:   1:" +sys._getframe(1).f_code.co_name+"   called from:"+sys._getframe(2).f_code.co_name+" @ line# %d"%(sys._getframe(1).f_lineno) ) # +"    trace# "+unicode(sys._getframe(1).f_trace)+"\n" )
				f.close()
				return


		except	Exception, e:
			if unicode(e).find(u"None") == -1:
				self.errorLog(u"myLog in Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
				indigo.server.log(text)
				try: f.close()
				except: pass
		return

####-----------------  valiable formatter for differnt log levels ---------
# call with: 
# formatter = LevelFormatter(fmt='<default log format>', level_fmts={logging.INFO: '<format string for info>'})
# handler.setFormatter(formatter)
class LevelFormatter(logging.Formatter):
	def __init__(self, fmt=None, datefmt=None, level_fmts={}, level_date={}):
		self._level_formatters = {}
		self._level_date_format = {}
		for level, format in level_fmts.items():
			# Could optionally support level names too
			self._level_formatters[level] = logging.Formatter(fmt=format, datefmt=level_date[level])
		# self._fmt will be the default format
		super(LevelFormatter, self).__init__(fmt=fmt, datefmt=datefmt)
		return

	def format(self, record):
		if record.levelno in self._level_formatters:
			return self._level_formatters[record.levelno].format(record)

		return super(LevelFormatter, self).format(record)

