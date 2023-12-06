#! /Library/Frameworks/Python.framework/Versions/Current/bin/python3
# -*- coding: utf-8 -*-
####################
# uniFi Plugin
# Developed by Karl Wachs
# karlwachs@me.com

import datetime
try:
	import json
except:
	import simplejson as json
import subprocess
import fcntl
import os 
import sys
import pwd
import time
import traceback
import platform
import struct
import codecs

try:
	import queue as queue
	from queue import PriorityQueue
	queueOrQueue = "queue"
except:
	import Queue as queue
	from Queue import PriorityQueue
	queueOrQueue = "Queue"

import random
import socket
import getNumber as GT
import MAC2Vendor
import threading
import logging
import copy
import requests
import inspect
from checkIndigoPluginName import checkIndigoPluginName 

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

import cProfile
import pstats


try:
	unicode("x")
except:
	unicode = str

######### set new  pluginconfig defaults
# this needs to be updated for each new property added to pluginProps. 
# indigo ignores the defaults of new properties after first load of the plugin 
kDefaultPluginPrefs = {
	"MSG":										"please enter values",
	"updateDescriptions":						True,
	"expirationTime":							"120",
	"fixExpirationTime":						True,
	"expTimeMultiplier":						"2",
	"launchWaitSeconds":						"1.13",
	"ignoreNewClients":							False,
	"ignoreNewNeighbors":						False,
	"ignoreNeighborForFing":					True,
	"enableBroadCastEvents":					"0",
	"enableFINGSCAN":							False,
	"enableSqlLogging":							True,
	"enableMACtoVENDORlookup":					"21",
	"requestOrcurl":							"requests",
	"curlPath":									"/usr/bin/curl",
	"folderNameCreated":						"UNIFI_created",
	"folderNameSystem":							"UNIFI_system",
	"folderNameNeighbors":						"UNIFI_neighbors",
	"folderNameVariables":						"UNIFI",
	"Group0":									"Group0",
	"Group1":									"Group1",
	"Group2":									"Group2",
	"Group3":									"Group3",
	"Group4":									"Group4",
	"Group5":									"Group5",
	"Group6":									"Group6",
	"Group7":									"Group7",
	"unifiCONTROLLERUserID":					"",
	"unifiCONTROLLERPassWd":					"",
	"unifiUserID":								"",
	"unifiPassWd":								"",
	"unifiUserIDUDM":							"",
	"unifiPassWdUDM":							"",
	"useStrictToLogin":							False,
	"unifiControllerType":						"std",
	"unifiCloudKeyMode":						"ONreportsOnly",
	"useDBInfoForWhichDevices":					"all",
	"unifiCloudKeyIP":							"192.168.1.x",
	"refreshCallbackMethod":					"no",
	"unifiCloudKeySiteName":					"",
	"overWriteControllerPort":					"443",
	"unifControllerCheckPortNumber"				"0"
	"unifiControllerBackupON":					True,
	"ControllerBackupPath":						"/data/autobackup",
	"infoLabelbackup1":							"/usr/lib/unifi/data/backup/autobackup",
	"infoLabelbackup2":							"/data/unifi/data/backup/autobackup",
	"infoLabelbackup2a":						"/data/autobackup",
	"infoLabelbackup3":							"/Preferences/Plugins/com.karlwachs.uniFiAP/backup",
	"ipUDMON":									False,
	"ipUDM":									"192.168.1.x",
	"debUD":									False,
	"apON":										True,
	"ipON0":									False,
	"ip0":										"192.168.1.x",
	"debAP0":									False,
	"ipON1":									False,
	"ip1":										"192.168.1.x",
	"debAP1":									False,
	"ipON2":									False,
	"ip2":										"192.168.1.x",
	"debAP2":									False,
	"ipON3":									False,
	"ip3":										"192.168.1.x",
	"debAP3":									False,
	"ipON4":									False,
	"ip4":										"192.168.1.x",
	"debAP4":									False,
	"ipON5":									False,
	"ip5":										"192.168.1.x",
	"debAP5":									False,
	"ipON6":									False,
	"ip6":										"192.168.1.x",
	"debAP6":									False,
	"ipON7":									False,
	"ip7":										"192.168.1.x",
	"debAP7":									False,
	"ipON8":									False,
	"ip8":										"192.168.1.x",
	"debAP8":									False,
	"ipON9":									False,
	"ip9":										"192.168.1.x",
	"debAP9":									False,
	"ipON10":									False,
	"ip10":										"192.168.1.x",
	"debAP10":									False,
	"ipON11":									False,
	"ip11":										"192.168.1.x",
	"debAP11":									False,
	"ipON12":									False,
	"ip12":										"192.168.1.x",
	"debAP12":									False,
	"ipON13":									False,
	"ip13":										"192.168.1.x",
	"debAP13":									False,
	"ipON14":									False,
	"ip14":										"192.168.1.x",
	"debAP14":									False,
	"ipON15":									False,
	"ip15":										"192.168.1.x",
	"debAP15":									False,
	"ipON16":									False,
	"ip16":										"192.168.1.x",
	"debAP16":									False,
	"ipON17":									False,
	"ip17":										"192.168.1.x",
	"debAP17":									False,
	"ipON18":									False,
	"ip18":										"192.168.1.x",
	"debAP18":									False,
	"ipON19":									False,
	"ip19":										"192.168.1.x",
	"debAP19":									False,
	"ipUGAON":									False,
	"GWtailEnable":								False,
	"ipUGA":									"192.168.1.1",
	"debGW":									False,
	"count_APDL_inPortCount":					"1",
	"ipSWON0":									False,
	"ipSW0":									"192.168.1.x",
	"debSW0":									False,
	"ipSWON1":									False,
	"ipSW1":									"192.168.1.x",
	"debSW1":									False,
	"ipSWON2":									False,
	"ipSW2":									"192.168.1.x",
	"debSW2":									False,
	"ipSWON3":									False,
	"ipSW3":									"192.168.1.x",
	"debSW3":									False,
	"ipSWON4":									False,
	"ipSW4":									"192.168.1.x",
	"debSW4":									False,
	"ipSWON5":									False,
	"ipSW5":									"192.168.1.x",
	"debSW5":									False,
	"ipSWON6":									False,
	"ipSW6":									"192.168.1.x",
	"debSW6":									False,
	"ipSWON7":									False,
	"ipSW7":									"192.168.1.x",
	"debSW7":									False,
	"ipSWON8":									False,
	"ipSW8":									"192.168.1.x",
	"debSW8":									False,
	"ipSWON9":									False,
	"ipSW9":									"192.168.1.x",
	"debSW9":									False,
	"ipSWON10":									False,
	"ipSW10":									"192.168.1.x",
	"debSW10":									False,
	"ipSWON11":									False,
	"ipSW11":									"192.168.1.x",
	"debSW11":									False,
	"ipSWON12":									False,
	"ipSW12":									"192.168.1.x",
	"debSW12":									False,
	"cameraSystem":								"off",
	"protecEventSleepTime":						2,
	"refreshProtectCameras":					60,
	"copyProtectsnapshots":						"no",
	"changedImagePath":							"/Users/YOURID/.....",
	"debugLogic":								False,
	"debugLog":									False,
	"debugLogDetails":							False,
	"debugDict":								False,
	"debugDictDetails":							False,
	"debugConnectionCMD":						False,
	"debugConnectionRET":						False,
	"debugExpect":								False,
	"debugExpectRET":							False,
	"debugVideo":								False,
	"debugFing":								False,
	"debugBC":									False,
	"debugPing":								False,
	"debugUDM":									False,
	"debugIgnoreMAC":							False,
	"debugDBinfo":								False,
	"debugProtect":								False,
	"debugProtDetails":							False,
	"debugProtEvents":							False,
	"debugSpecial":								False,
	"debugDictFile":							False,
	"debugall":									False,
	"showLoginTest":							True,
	"do_cProfile":								"on/off/print",
	"rebootUnifiDeviceOnError":					True,
	"restartListenerEvery":						"999999999",
	"maxConsumedTimeQueueForWarning":			"10",
	"maxConsumedTimeForWarning":				"15",
	"hostFileCheck":							"no",
	"requestTimeout":							"10",
	"checkForNewUnifiSystemDevicesEvery":		"10",
	"readBuffer":								"16384" 
}

"""
good web pages for unifi API
https://ubntwiki.com/products/software/unifi-controller/api
https://github.com/NickWaterton/Unifi-websocket-interface/blob/master/controller.py
https://github.com/Art-of-WiFi/UniFi-API-client

"""

dataVersion = 2.0

## Static parameters, not changed in pgm
_GlobalConst_numberOfAP	 = 20
_GlobalConst_numberOfSW	 = 13

_GlobalConst_numberOfGroups = 8
_GlobalConst_groupList		= ["Group{}".format(i) for i in range(_GlobalConst_numberOfGroups)]
_GlobalConst_dTypes			= ["UniFi","gateway","DHCP","SWITCH","Device-AP","Device-SW-4","Device-SW-5","Device-SW-6","Device-SW-7","Device-SW-8","Device-SW-10","Device-SW-11","Device-SW-12","Device-SW-14","Device-SW-16","Device-SW-18","Device-SW-26","Device-SW-52","neighbor"]
_debugAreas					= ["Logic","Log","Dict","LogDetails","DictDetails","ConnectionCMD","ConnectionRET","Expect","ExpectRET","Video","Fing","BC","Ping","Protect","ProtDetails","ProtEvents","all","Special","UDM","IgnoreMAC","DBinfo","DictFile","UpdateStates"]
_numberOfPortsInSwitch		= [4, 5, 7, 8, 10, 11, 12, 16, 18, 26, 52]
################################################################################
# noinspection PyUnresolvedReferences,PySimplifyBooleanCheck,PySimplifyBooleanCheck
class Plugin(indigo.PluginBase):
	####-----------------			  ---------
	def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
		indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)

	
		self.pluginShortName 			= "UniFi"
		self.quitNOW					= ""
		self.delayedAction				={}
		self.updateConnectParams		= time.time() - 100
###############  common for all plugins ############
		self.getInstallFolderPath		= indigo.server.getInstallFolderPath()+"/"
		self.indigoPath					= indigo.server.getInstallFolderPath()+"/"
		self.indigoRootPath 			= indigo.server.getInstallFolderPath().split("Indigo")[0]
		self.pathToPlugin 				= self.completePath(os.getcwd())

		major, minor, release 			= map(int, indigo.server.version.split("."))
		self.indigoVersion 				= float(major)+float(minor)/10.
		self.indigoRelease 				= release

		self.pluginVersion				= pluginVersion
		self.pluginId					= pluginId
		self.pluginName					= pluginId.split(".")[-1]
		self.myPID						= os.getpid()
		self.pluginState				= "init"

		self.myPID 						= os.getpid()
		self.MACuserName				= pwd.getpwuid(os.getuid())[0]

		self.MAChome					= os.path.expanduser("~")
		self.userIndigoDir				= self.MAChome + "/indigo/"
		self.indigoPreferencesPluginDir = self.getInstallFolderPath+"Preferences/Plugins/"+self.pluginId+"/"
		self.indigoPluginDirOld			= self.userIndigoDir + self.pluginShortName+"/"
		self.PluginLogFile				= indigo.server.getLogsFolderPath(pluginId=self.pluginId) +"/plugin.log"
		self.showLoginTest 				= pluginPrefs.get('showLoginTest',True)

		formats=	{   logging.THREADDEBUG: "%(asctime)s %(msg)s",
						logging.DEBUG:       "%(asctime)s %(msg)s",
						logging.INFO:        "%(asctime)s %(msg)s",
						logging.WARNING:     "%(asctime)s %(msg)s",
						logging.ERROR:       "%(asctime)s.%(msecs)03d\t%(levelname)-12s\t%(name)s.%(funcName)-25s %(msg)s",
						logging.CRITICAL:    "%(asctime)s.%(msecs)03d\t%(levelname)-12s\t%(name)s.%(funcName)-25s %(msg)s" }

		date_Format = { logging.THREADDEBUG: "%Y-%m-%d %H:%M:%S",		# 5
						logging.DEBUG:       "%Y-%m-%d %H:%M:%S",		# 10
						logging.INFO:        "%Y-%m-%d %H:%M:%S",		# 20
						logging.WARNING:     "%Y-%m-%d %H:%M:%S",		# 30
						logging.ERROR:       "%Y-%m-%d %H:%M:%S",		# 40
						logging.CRITICAL:    "%Y-%m-%d %H:%M:%S" }		# 50
		formatter = LevelFormatter(fmt="%(msg)s", datefmt="%Y-%m-%d %H:%M:%S", level_fmts=formats, level_date=date_Format)

		self.plugin_file_handler.setFormatter(formatter)
		self.indiLOG = logging.getLogger("Plugin")  
		self.indiLOG.setLevel(logging.THREADDEBUG)

		self.indigo_log_handler.setLevel(logging.INFO)

		self.indiLOG.log(20,"initializing  ...")
		self.indiLOG.log(20,"path To files:          =================")
		self.indiLOG.log(10,"indigo                  {}".format(self.indigoRootPath))
		self.indiLOG.log(10,"installFolder           {}".format(self.indigoPath))
		self.indiLOG.log(10,"plugin.py               {}".format(self.pathToPlugin))
		self.indiLOG.log(10,"indigo                  {}".format(self.indigoRootPath))
		self.indiLOG.log(20,"detailed logging        {}".format(self.PluginLogFile))
		if self.showLoginTest:
			self.indiLOG.log(20,"testing logging levels, for info only: ")
			self.indiLOG.log( 0,"logger  enabled for     0 ==> TEST ONLY ")
			self.indiLOG.log( 5,"logger  enabled for     THREADDEBUG    ==> TEST ONLY ")
			self.indiLOG.log(10,"logger  enabled for     DEBUG          ==> TEST ONLY ")
			self.indiLOG.log(20,"logger  enabled for     INFO           ==> TEST ONLY ")
			self.indiLOG.log(30,"logger  enabled for     WARNING        ==> TEST ONLY ")
			self.indiLOG.log(40,"logger  enabled for     ERROR          ==> TEST ONLY ")
			self.indiLOG.log(50,"logger  enabled for     CRITICAL       ==> TEST ONLY ")
			self.indiLOG.log(10,"Plugin short Name       {}".format(self.pluginShortName))
		self.indiLOG.log(10,"my PID                  {}".format(self.myPID))	 
		self.indiLOG.log(10,"Achitecture             {}".format(platform.platform()))	 
		self.indiLOG.log(10,"OS                      {}".format(platform.mac_ver()[0]))	 
		self.indiLOG.log(10,"indigo V                {}".format(indigo.server.version))	 
		self.indiLOG.log(10,"python V                {}.{}.{}".format(sys.version_info[0], sys.version_info[1] , sys.version_info[2]))	 

		self.pythonPath = ""
		if sys.version_info[0] >2:
			if os.path.isfile("/Library/Frameworks/Python.framework/Versions/Current/bin/python3"):
				self.pythonPath				= "/Library/Frameworks/Python.framework/Versions/Current/bin/python3"
		else:
			if os.path.isfile("/usr/local/bin/python"):
				self.pythonPath				= "/usr/local/bin/python"
			elif os.path.isfile("/usr/bin/python2.7"):
				self.pythonPath				= "/usr/bin/python2.7"
		if self.pythonPath == "":
				self.indiLOG.log(40,"FATAL error:  none of python versions 2.7 3.x is installed  ==>  stopping {}".format(self.pluginId))
				self.quitNOW = "none of python versions 2.7 3.x is installed "
				exit()
		self.indiLOG.log(20,"using '{}' for utily programs".format(self.pythonPath))

###############  END common for all plugins ############

		return
		
####

	####-----------------			  ---------
	def __del__(self):
		indigo.PluginBase.__del__(self)

	###########################		INIT	## START ########################

	####----------------- @ startup set global parameters, create directories etc ---------
	def startup(self):
		if not checkIndigoPluginName(self, indigo): 
			exit() 

		try:

			self.checkcProfile()



			if not os.path.isdir(self.indigoPreferencesPluginDir):
				self.indiLOG.log(20, " creating plugin prefs directory:{}".format(self.indigoPreferencesPluginDir))
				os.mkdir(self.indigoPreferencesPluginDir)

			self.varExcludeSQLList = ["Unifi_New_Device","Unifi_With_IPNumber_Change","Unifi_With_Status_Change","Unifi_Camera_with_Event","Unifi_Camera_Event_PathToThumbnail","Unifi_Camera_Event_DateOfThumbNail","Unifi_Camera_Event_Date"]
			#self.varExcludeSQLList = ["Unifi_New_Device","Unifi_With_IPNumber_Change","Unifi_With_Status_Change"]

			self.triggerList									= []
			self.statusChanged									= 0
			self.msgListenerActive								= {}



			self.UserID					= {}
			self.PassWd					= {}
			self.connectParamsDefault 	= {}
			self.connectParamsDefault["expectRestart"]		= {	"APtail": "restart.exp",
																"GWtail": "restart.exp",
																"UDtail": "restart.exp",
																"SWtail": "restart.exp",
																"VDtail": "restart.exp",
																"GWdict": "restart.exp",
																"UDdict": "restart.exp",
																"SWdict": "restart.exp",
																"APdict": "restart.exp",
																"GWctrl": "restart.exp",
																"UDctrl": "restart.exp",
																"VDdict": "restart.exp"
															}
			self.connectParamsDefault["expectCmdFile"]		= {	"APtail": "execLog.exp",
																"GWtail": "execLog.exp",
																"UDtail": "execLog.exp",
																"SWtail": "execLog.exp",
																"VDtail": "execLogVideo.exp",
																"GWdict": "dictLoop.exp",
																"UDdict": "dictLoop.exp",
																"SWdict": "dictLoop.exp",
																"APdict": "dictLoop.exp",
																"GWctrl": "simplecmd.exp",
																"UDctrl": "simplecmd.exp",
																"VDdict": "simplecmd.exp"
															}
			self.connectParamsDefault["commandOnServer"]	= {	"APtail": "/usr/bin/tail -F /var/log/messages",
																"GWtail": "/usr/bin/tail -F /var/log/messages",
																"UDtail": "/usr/bin/tail -F /var/log/messages",
																"SWtail": "/usr/bin/tail -F /var/log/messages",
																"VDtail": "/usr/bin/tail -F /var/lib/unifi-video/logs/motion.log",
																"VDdict": "not implemented",
																"GWdict": "mca-ctrl -t dump | sed -e 's/^ *//'",
																"UDdict": "mca-ctrl -t dump | sed -e 's/^ *//'",
																"SWdict": "mca-ctrl -t dump | sed -e 's/^ *//'",
																"GWctrl": "mca-ctrl -t dump-cfg | sed -e 's/^ *//'",
																"UDctrl": "mca-ctrl -t dump-cfg | sed -e 's/^ *//'",
																"APdict": "mca-ctrl -t dump | sed -e 's/^ *//'"
															}
			self.connectParamsDefault["enableListener"]	= {	"APtail": True,
																"GWtail": True,
																"UDtail": True,
																"SWtail": True,
																"VDtail": True,
																"VDdict": True,
																"GWdict": True,
																"UDdict": True,
																"SWdict": True,
																"GWctrl": True,
																"UDctrl": True,
																"APdict": True
															}
			self.connectParamsDefault["promptOnServer"] 	= {}
			"""
																"APtail": "\# ",
																"GWtail": ":~",
																"GWctrl": ":~",
																"UDtail": "\# ",
																"UDctrl": "\# ",
																"SWtail": "\# ",
																"VDtail": "VirtualBox",
																"VDdict": "VirtualBox",
																"GWdict": ":~",
																"UDdict": "\# ",
																"SWdict": "\# ",
																"APdict": "\# "}
			"""
			self.connectParamsDefault["startDictToken"]	= {	"APtail": "x",
																"GWtail": "x",
																"UDtail": "x",
																"SWtail": "x",
																"VDtail": "x",
																"GWdict": self.connectParamsDefault["commandOnServer"]["GWdict"],
																"UDdict": self.connectParamsDefault["commandOnServer"]["UDdict"],
																"SWdict": self.connectParamsDefault["commandOnServer"]["SWdict"],
																"APdict": self.connectParamsDefault["commandOnServer"]["GWdict"]
															}
			self.connectParamsDefault["endDictToken"]		= {	"APtail": "x",
																"GWtail": "x",
																"UDtail": "x",
																"VDtail": "x",
																"GWdict": "xxxThisIsTheEndTokenxxx",
																"UDdict": "xxxThisIsTheEndTokenxxx",
																"SWdict": "xxxThisIsTheEndTokenxxx",
																"APdict": "xxxThisIsTheEndTokenxxx"
															}
			self.connectParamsDefault["UserID"]			= {	"unixDevs": "",
																"unixUD":   "",
																"unixNVR":  "",
																"nvrWeb":   "",
																"webCTRL":  ""
															}
			self.connectParamsDefault["PassWd"]			= {	"unixDevs": "",
																"unixUD":   "",
																"unixNVR":  "",
																"nvrWeb":   "",
																"webCTRL":  ""
															}
			self.tryHTTPPorts 		= ["443","8443"]
			self.HTTPretCodes		= { "200": {"os":"unifi_os", "unifiApiLoginPath":"/api/auth/login", "unifiApiWebPage":"/proxy/network/api/s" },
										"302": {"os":"std",      "unifiApiLoginPath":"/api/login",      "unifiApiWebPage":"/api/s" }  }
			self.OKControllerOS = ["std","unifi_os"]


			self.connectParams = copy.copy(self.connectParamsDefault)
			useDefault = ["endDictToken", "startDictToken", "commandOnServer", "expectCmdFile", "expectRestart"]

			try: 	
					xx = json.loads(self.pluginPrefs.get("connectParams","{}"))
					if xx != {}:
						self.connectParams = copy.deepcopy(xx)
					for item1 in self.connectParamsDefault:
						if item1 in useDefault:
							self.connectParams[item1] = copy.deepcopy(self.connectParamsDefault[item1])
							continue

						if item1 not in self.connectParams:
							self.connectParams[item1] = copy.deepcopy(self.connectParamsDefault[item1])
						else:
							for item2 in self.connectParamsDefault[item1]:
								if item2 not in self.connectParams[item1]:
									self.connectParams[item1][item2] = copy.copy(self.connectParamsDefault[item1][item2])

			except:	
				pass

			if self.connectParams["UserID"]["unixDevs"] == "": 	self.connectParams["UserID"]["unixDevs"] = self.pluginPrefs.get("unifiUserID","")
			if self.connectParams["UserID"]["unixUD"]   == "": 	self.connectParams["UserID"]["unixUD"]   = self.pluginPrefs.get("unifiUserIDUDM","")
			if self.connectParams["UserID"]["unixNVR"]  == "": 	self.connectParams["UserID"]["unixNVR"]  = self.pluginPrefs.get("nvrUNIXUserID","")
			if self.connectParams["UserID"]["nvrWeb"]   == "": 	self.connectParams["UserID"]["nvrWeb"]   = self.pluginPrefs.get("nvrWebUserID","")
			if self.connectParams["PassWd"]["webCTRL"]  == "": 	self.connectParams["PassWd"]["nvrWeb"]   = self.pluginPrefs.get("unifiCONTROLLERUserID","")

			if self.connectParams["PassWd"]["unixDevs"] == "": 	self.connectParams["PassWd"]["unixDevs"] = self.pluginPrefs.get("unifiPassWd","")
			if self.connectParams["PassWd"]["unixUD"]   == "": 	self.connectParams["PassWd"]["unixUD"]   = self.pluginPrefs.get("unifiPassWdUDM","")
			if self.connectParams["PassWd"]["unixNVR"]  == "": 	self.connectParams["PassWd"]["unixNVR"]  = self.pluginPrefs.get("nvrUNIXPassWd","")
			if self.connectParams["PassWd"]["nvrWeb"]   == "": 	self.connectParams["PassWd"]["nvrWeb"]   = self.pluginPrefs.get("nvrWebPassWd","")
			if self.connectParams["PassWd"]["webCTRL"]  == "": 	self.connectParams["PassWd"]["nvrWeb"]   = self.pluginPrefs.get("unifiCONTROLLERPassWd","")
			##indigo.server.log(" connectParams:{}".format(self.connectParams))

			self.stop 											= []
			self.PROTECT 										= {}
			self.failedControllerLoginCount 					= 0
			self.failedControllerLoginCountMax					= 30
			self.checkForNewUnifiSystemDevicesEvery				= int(self.pluginPrefs.get("checkForNewUnifiSystemDevicesEvery","10"))
			self.launchWaitSeconds								= float(self.pluginPrefs.get("launchWaitSeconds","1.13"))
			self.vboxPath										= self.completePath(self.pluginPrefs.get("vboxPath",    		"/Applications/VirtualBox.app/Contents/MacOS/"))
			self.changedImagePath								= self.completePath(self.pluginPrefs.get("changedImagePath", 	self.MAChome))
			self.videoPath										= self.completePath(self.pluginPrefs.get("videoPath",    		"/Volumes/data4TB/Users/karlwachs/video/"))
			self.unifiNVRSession								= ""
			self.nvrVIDEOapiKey									= self.pluginPrefs.get("nvrVIDEOapiKey","")

			self.copyProtectsnapshots							= self.pluginPrefs.get("copyProtectsnapshots","on")
			self.refreshProtectCameras							= float(self.pluginPrefs.get("refreshProtectCameras",180.))
			self.protecEventSleepTime 							= float(self.pluginPrefs.get("protecEventSleepTime",4.))
			self.vmMachine										= self.pluginPrefs.get("vmMachine",  "")
			self.vboxPath										= self.completePath(self.pluginPrefs.get("vboxPath",    		"/Applications/VirtualBox.app/Contents/MacOS/"))
			self.vmDisk											= self.pluginPrefs.get("vmDisk",  								"/Volumes/data4TB/Users/karlwachs/VirtualBox VMs/ubuntu/NewVirtualDisk1.vdi")
			self.mountPathVM									= self.pluginPrefs.get("mountPathVM", "/home/yourid/osx")
			self.videoPath										= self.completePath(self.pluginPrefs.get("videoPath",    		"/Volumes/data4TB/Users/karlwachs/video/"))

			self.menuXML										= json.loads(self.pluginPrefs.get("menuXML", "{}"))
			self.pluginPrefs["menuXML"]							= json.dumps(self.menuXML)
			self.restartRequest									= {}
			self.lastMessageReceivedInListener					= {}
			self.waitForMAC2vendor 								= False
			self.enableMACtoVENDORlookup						= int(self.pluginPrefs.get("enableMACtoVENDORlookup","21"))
			if self.enableMACtoVENDORlookup != "0":
				self.M2V 										= MAC2Vendor.MAP2Vendor(pathToMACFiles=self.indigoPreferencesPluginDir+"mac2Vendor/", refreshFromIeeAfterDays = self.enableMACtoVENDORlookup, myLogger = self.indiLOG.log)
				self.waitForMAC2vendor 							= self.M2V.makeFinalTable()


			self.enableSqlLogging								= self.pluginPrefs.get("enableSqlLogging",True)
			self.pluginPrefs["createUnifiDevicesCounter"]		= int(self.pluginPrefs.get("createUnifiDevicesCounter",0))

			self.lastupdateDevStateswRXTXbytes					= time.time() - 100
			self.updateDescriptions								= self.pluginPrefs.get("updateDescriptions", True)
			self.ignoreNeighborForFing							= self.pluginPrefs.get("ignoreNeighborForFing", True)
			self.ignoreNewNeighbors								= self.pluginPrefs.get("ignoreNewNeighbors", False)
			self.ignoreNewClients								= self.pluginPrefs.get("ignoreNewClients", False)
			self.enableFINGSCAN									= self.pluginPrefs.get("enableFINGSCAN", False)
			self.count_APDL_inPortCount							= self.pluginPrefs.get("count_APDL_inPortCount", "1")
			self.sendUpdateToFingscanList						= {}
			self.enableBroadCastEvents							= self.pluginPrefs.get("enableBroadCastEvents", "0")
			self.sendBroadCastEventsList						= []
			self.unifiCloudKeyListOfSiteNames					= json.loads(self.pluginPrefs.get("unifiCloudKeyListOfSiteNames", "[]"))
			self.unifiCloudKeyIP								= self.pluginPrefs.get("unifiCloudKeyIP", "")
			self.csrfToken 										= ""
			self.numberForUDM									= {"AP":4,"SW":12}

			self.rebootUnifiDeviceOnError						= self.pluginPrefs.get("rebootUnifiDeviceOnError", True)


			self.refreshCallbackMethodAlreadySet 				= "no" 

			self.unifiControllerOS 								= ""
			self.unifiApiWebPage								= ""
			self.unifiApiLoginPath								= ""
			self.unifControllerCheckPortNumber					= self.pluginPrefs.get("unifControllerCheckPortNumber", "0") 
			self.overWriteControllerPort						= self.pluginPrefs.get("overWriteControllerPort", "443")
			self.lastPortNumber									= ""
			self.unifiCloudKeyPort								= ""
			self.unifiControllerType							= self.pluginPrefs.get("unifiControllerType", "std")
			self.unifiCloudKeyMode								= self.pluginPrefs.get("unifiCloudKeyMode", "ON")
			self.unifiCloudKeySiteName							= self.pluginPrefs.get("unifiCloudKeySiteName", "default")
			self.requestTimeout									= max(1., float(self.pluginPrefs.get("requestTimeout", 10.)))
			self.unifiCloudKeySiteNameGetNew 					= False
			self.unifiCloudKeyMode								= self.pluginPrefs.get("unifiCloudKeyMode", "ONreportsOnly")



			if self.unifiControllerType == "off" or self.unifiCloudKeyMode	== "off" or self.connectParams["UserID"]["webCTRL"] == "":
				self.unifiCloudKeyMode = "off"
				self.pluginPrefs["unifiCloudKeyMode"] = "off"
				self.unifiControllerType = "off"
				self.pluginPrefs["unifiControllerType"] = ""
				self.connectParams["UserID"]["nvrWeb"]  = ""

			if self.unifiControllerType.find("UDM") > -1:
				if self.unifiControllerType.find("UDM") > -1:
					self.unifiCloudKeyMode = "ON"
					self.pluginPrefs["unifiCloudKeyMode"] 		= "ON"

			try:
				self.controllerWebEventReadON 					= int(self.pluginPrefs.get("controllerWebEventReadON","-1"))
			except:
				self.controllerWebEventReadON  					= -1
			if self.unifiControllerType == "UDMpro": 
				self.controllerWebEventReadON  					= -1

			self.unifiControllerBackupON						= self.pluginPrefs.get("unifiControllerBackupON", False)
			self.ControllerBackupPath							= self.pluginPrefs.get("ControllerBackupPath", "")

			try: self.readBuffer								= int(self.pluginPrefs.get("readBuffer", "16384"))
			except: self.readBuffer								= 16384
			self.maxConsumedTimeQueueForWarning					= float(self.pluginPrefs.get("maxConsumedTimeQueueForWarning", "5"))
			self.maxConsumedTimeForWarning						= float(self.pluginPrefs.get("maxConsumedTimeForWarning", "3"))


			self.lastCheckForCAMERA								= 0
			self.saveCameraEventsLastCheck						= 0
			self.cameraEventWidth								= int(self.pluginPrefs.get("cameraEventWidth", "720"))
			self.imageSourceForEvent							= self.pluginPrefs.get("imageSourceForEvent", "noImage")
			self.imageSourceForSnapShot							= self.pluginPrefs.get("imageSourceForSnapShot", "unoImage")

			self.listenStart									= {}
			self.useStrictToLogin								= self.pluginPrefs.get("useStrictToLogin", False)
			self.unifiControllerSession							= ""

			self.curlPath										= self.pluginPrefs.get("curlPath", "/usr/bin/curl")
			if len(self.curlPath) < 4:
				self.curlPath									= "/usr/bin/curl"
				self.pluginPrefs["curlPath"] 					= self.curlPath

			self.requestOrcurl									= self.pluginPrefs.get("requestOrcurl", "curl")

			self.expectPath 									= "/usr/bin/expect"

			self.restartIfNoMessageSeconds						= 130 #int(self.pluginPrefs.get("restartIfNoMessageSeconds", 130))
			self.expirationTime									= int(self.pluginPrefs.get("expirationTime", 120) )
			self.expTimeMultiplier								= float(self.pluginPrefs.get("expTimeMultiplier", 2))

	
			self.loopSleep										= 5     # float(self.pluginPrefs.get("loopSleep", 8))
			self.timeoutDICT									= "15"
			#self.timeoutDICT									= "{}".format(int(self.pluginPrefs.get("timeoutDICT", "15")))
			self.folderNameCreated								= self.pluginPrefs.get("folderNameCreated",   "UNIFI_created")
			self.folderNameNeighbors							= self.pluginPrefs.get("folderNameNeighbors", "UNIFI_neighbors")
			self.folderNameVariables							= self.pluginPrefs.get("folderNameVariables", "UNIFI")
			self.folderNameSystem								= self.pluginPrefs.get("folderNameSystem",	  "UNIFI_system")
			self.fixExpirationTime								= self.pluginPrefs.get("fixExpirationTime",	True)
			self.MACignorelist									= {}
			self.MACSpecialIgnorelist							= {}
			self.HANDOVER										= {}
			self.lastUnifiCookieCurl							= 0
			self.lastUnifiCookieRequests						= 0
			self.lastNVRCookie									= 0
			self.pendingCommand									= []
			self.groupNames										= []
			for groupNo in range(_GlobalConst_numberOfGroups):
				self.groupNames.append(self.pluginPrefs.get("Group{}".format(groupNo), "Group".format(groupNo)))

			self.groupStatusList								= [{"members":{},"allHome":False,"allAway":False,"oneHome":False,"oneAway":False,"nHome":0,"nAway":0} for i in range(_GlobalConst_numberOfGroups )]
			self.groupStatusListALL								= {"nHome":0,"nAway":0,"anyChange":False}


			self.createEntryInUnifiDevLogActive					= True #self.pluginPrefs.get("createEntryInUnifiDevLogActive",	False)
			self.lastcreateEntryInUnifiDevLog 					= time.time()

			self.devsEnabled									= {}
			self.debugDevs										= {}
			self.ipNumbersOf									= {}
			self.deviceUp										= {}
			self.numberOfActive									= {}
			self.debugDevs										= {}

			self.updateStatesList								= {}
			self.logCount										= {}
			self.ipNumbersOf["AP"]								= ["" for nn in range(_GlobalConst_numberOfAP)]
			self.devsEnabled["AP"]								= [False for nn in range(_GlobalConst_numberOfAP)]
			self.debugDevs["AP"]								= [False for nn in range(_GlobalConst_numberOfAP)]

			self.ipNumbersOf["SW"]								= ["" for nn in range(_GlobalConst_numberOfSW)]
			self.devsEnabled["SW"]								= [False for nn in range(_GlobalConst_numberOfSW)]
			self.debugDevs["SW"]								= [False for nn in range(_GlobalConst_numberOfSW)]
			self.isMiniSwitch									= [False for nn in range(_GlobalConst_numberOfSW)]


			self.devNeedsUpdate									= {}

			self.MACloglist										= {}

			self.readDictEverySeconds							= {}
			self.readDictEverySeconds["AP"]						= 65
			self.readDictEverySeconds["GW"]						= 65
			self.readDictEverySeconds["SW"]						= 65
			self.readDictEverySeconds["UD"]						= 65
			self.readDictEverySeconds["DB"]						= 45
			self.getcontrollerDBForClientsLast					= 0
			self.lastResetUnifiDevice							= {}
			self.devStateChangeList								= {}
			self.deviceUp["AP"]									= {}
			self.deviceUp["SW"]									= {}
			self.deviceUp["GW"]									= {}
			self.deviceUp["VD"]									= {}
			self.deviceUp["UD"]									= {}
			self.version			 							= self.getParamsFromFile(self.indigoPreferencesPluginDir+"dataVersion", default=0)

			self.restartListenerEvery							= float(self.pluginPrefs.get("restartListenerEvery", "999999999"))


			#####  check AP parameters
			self.numberOfActive["AP"] =0
			for i in range(_GlobalConst_numberOfAP):
				ip0 											= self.pluginPrefs.get("ip{}".format(i), "")
				ac												= self.pluginPrefs.get("ipON{}".format(i), "")
				deb												= self.pluginPrefs.get("debAP{}".format(i), "")
				if not self.isValidIP(ip0): ac 					= False
				self.deviceUp["AP"][ip0] 						= time.time()
				self.ipNumbersOf["AP"][i] 						= ip0
				self.debugDevs["AP"][i] 						= deb
				if ac:
					self.devsEnabled["AP"][i]					= True
					self.numberOfActive["AP"] 					+= 1
 
			#####  check switch parameters
			self.numberOfActive["SW"]									= 0
			for i in range(_GlobalConst_numberOfSW):
				self.isMiniSwitch[i]									= self.pluginPrefs.get("isMini{}".format(i),False)
				ip0														= self.pluginPrefs.get("ipSW{}".format(i), "")
				ac														= self.pluginPrefs.get("ipSWON{}".format(i), "")
				deb														= self.pluginPrefs.get("debSW{}".format(i), "")
				if not self.isValidIP(ip0): ac 							= False
				self.deviceUp["SW"][ip0] 								= time.time()
				self.ipNumbersOf["SW"][i] 								= ip0
				self.debugDevs["SW"][i] 								= deb
				if ac:
					self.devsEnabled["SW"][i] 							= True
					self.numberOfActive["SW"] 							+= 1

			#####  check UGA parameters
			ip0 														= self.pluginPrefs.get("ipUGA",  "")
			ac															= self.pluginPrefs.get("ipUGAON",False)
			self.debugDevs["GW"] 										= [self.pluginPrefs.get("debGW",False)]


			if self.isValidIP(ip0) and ac:
				self.ipNumbersOf["GW"] 									= ip0
				self.devsEnabled["GW"] 									= True
				self.deviceUp["GW"][ip0] 								= time.time()
			else:
				self.ipNumbersOf["GW"] 									= ""
				self.devsEnabled["GW"]									= False


			#####  check DB parameters
			ip0 														= self.pluginPrefs.get("unifiCloudKeyIP",  "")
			ac															= self.pluginPrefs.get("unifiCloudKeyMode","ON")
			self.useDBInfoForWhichDevices								= self.pluginPrefs.get("useDBInfoForWhichDevices","all")
			if self.isValidIP(self.unifiCloudKeyIP) and (ac.find("ON") > -1 or ac.find("UDM") or self.useDBInfoForWhichDevices in ["all","perDevice"]):
				self.devsEnabled["DB"] = True
			else:
				self.devsEnabled["DB"]	= False

			#####  check UDM parameters
			ip0 														= self.pluginPrefs.get("ipUDM",  "")
			ac															= self.pluginPrefs.get("ipUDMON",False)
			self.debugDevs["UD"] 										= [self.pluginPrefs.get("debUD",False)]
			self.ipNumbersOf["UD"] 										= ip0
			self.deviceUp["UD"]											= time.time()

			if self.isValidIP(ip0) and ac:
				self.devsEnabled["UD"] 									= True
				self.ipNumbersOf["SW"][self.numberForUDM["SW"]]			= ip0
				self.ipNumbersOf["AP"][self.numberForUDM["AP"]]			= ip0
				self.ipNumbersOf["GW"] 							  		= ip0
				self.devsEnabled["SW"][self.numberForUDM["SW"]] 		= True
				self.devsEnabled["AP"][self.numberForUDM["AP"]] 		= True
				self.numberOfActive["SW"] 								= max(1,self.numberOfActive["SW"] )
				self.numberOfActive["AP"] 								= max(1,self.numberOfActive["AP"] )
				self.pluginPrefs["ipON"] 								= True
				self.pluginPrefs["ipSWON"] 								= True
				self.pluginPrefs["ip{}".format(self.numberForUDM["AP"])]   = ip0
				self.pluginPrefs["ipSW{}".format(self.numberForUDM["SW"])] = ip0
			else:
				self.devsEnabled["UD"] = False

			self.setDebugFromPrefs(self.pluginPrefs)



			#####  check video parameters
			self.cameraSystem										= self.pluginPrefs.get("cameraSystem", "off")
			if self.cameraSystem =="nvr": self.cameraSystem = "off"

			self.cameras							 				= {}
			self.ipNumbersOf["VD"] 									= ""
			self.VIDEOUP											= 0
			self.unifiVIDEONumerOfEvents 							= 0
			if self.cameraSystem == "nvr":
				try:	self.unifiVIDEONumerOfEvents 				= int(self.pluginPrefs.get("unifiVIDEONumerOfEvents", 1000))
				except: self.unifiVIDEONumerOfEvents				= 1000
				self.cameras						 				= {}
				self.saveCameraEventsStatus			 				= False

				ip0 												= self.pluginPrefs.get("nvrIP", "192.168.1.x")
				self.ipNumbersOf["VD"] 								= ip0
				self.VIDEOUP										= 0
				if self.isValidIP(ip0) and self.connectParams["UserID"]["unixNVR"] != "" and self.connectParams["PassWd"]["unixNVR"] != "":
					self.VIDEOUP	 								= time.time()
			elif self.cameraSystem == "protect":
				pass
			else:
				pass

			self.lastCheckForNVR 									= 0

			self.getFolderId()

			self.readSuspend()


			for ll in range(len(self.ipNumbersOf["AP"])):
				self.killIfRunning(self.ipNumbersOf["AP"][ll],"")
			for ll in range(len(self.ipNumbersOf["SW"])):
				self.killIfRunning(self.ipNumbersOf["SW"][ll],"")
			self.killIfRunning(self.ipNumbersOf["GW"], "")


			self.readDataStats()  # must come before other dev/states updates ...

			self.groupStatusINIT()
			self.setGroupStatus(init=True)
			self.readCamerasStats()
			self.readMACdata()
			self.checkDisplayStatus()
			self.getMACloglist()

			self.pluginStartTime 								= time.time()+150


			self.checkforUnifiSystemDevicesState 				= "start at {}".format(datetime.datetime.now().strftime("%m-%d %H:%M:%S"))

			self.killIfRunning("", "")

			try: 	os.mkdir(self.indigoPreferencesPluginDir+"backup")
			except: pass


		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
			exit(0)


		return

	
	####-----------------	 ---------
	def getMACloglist(self):
		try:
			self.MACloglist= self.getParamsFromFile(self.indigoPreferencesPluginDir+"MACloglist",  default ={})
			if self.MACloglist !={}:
				self.indiLOG.log(10,"start track-logging for MAC#s {}".format(self.MACloglist) )
		except	Exception as e:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		return

	####-----------------	 ---------
	def checkDisplayStatus(self):
		try:
			for dev in indigo.devices.iter(self.pluginId):
				if "displayStatus" not in dev.states: continue

				if "MAC" in dev.states and dev.deviceTypeId == "UniFi" and self.testIgnoreMAC(dev.states["MAC"], fromSystem="checkDisp"):
					if dev.states["displayStatus"].find("ignored") ==-1:
						dev.updateStateOnServer("displayStatus",self.padDisplay("ignored")+datetime.datetime.now().strftime("%m-%d %H:%M:%S"))
						if "{}".format(dev.displayStateImageSel) !="PowerOff":
							dev.updateStateImageOnServer(indigo.kStateImageSel.PowerOff)
				else:
					self.exeDisplayStatus(dev, dev.states["status"], force =False)


				old = dev.states["displayStatus"].split(" ")
				if len(old) ==3:
					new = self.padDisplay(old[0].strip())+dev.states["lastStatusChange"]
					if dev.states["displayStatus"] != new:
						dev.updateStateOnServer("displayStatus",new)
				else:
					dev.updateStateOnServer("displayStatus",self.padDisplay(old[0].strip())+dev.states["lastStatusChange"])
		except	Exception as e:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)


		return


	####-----------------	 ---------
	def setDebugFromPrefs(self, theDict, writeToLog=True):
		self.debugLevel = []
		try:
			for d in _debugAreas:
				if theDict.get("debug"+d, False): self.debugLevel.append(d)
			self.showLoginTest = self.pluginPrefs.get("showLoginTest", True)
			if writeToLog: self.indiLOG.log(20,"debug areas: {} ".format(self.debugLevel))
			out = ""
			for utype in self.debugDevs:
				out1 = ""
				for devn in range(len(self.debugDevs[utype])):
					if self.debugDevs[utype][devn]:
						out1 += "#{};".format(devn)
				if len(out1) > 1:
					out +=  "{}:{}".format(utype, out1)

			if writeToLog: self.indiLOG.log(20,"debug tracking unifi system devs:{} ".format(out))
		except	Exception as e:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)




	####-----------------	 ---------
	def isValidIP(self, ip0):
		if ip0 == "localhost": 						return True

		ipx = ip0.split(".")
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
		ipx = ip.split("/")[0].split(".")
		ipx[3] = "{:03d}".format(int(ipx[3]))
		return ".".join(ipx)


	####-----------------	 ---------
	def isValidMAC(self, mac):
		xxx = mac.split(":")
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
			if len(mac) < 2: macs[nn] = "0" + mac
		return ":".join(macs)

####-------------------------------------------------------------------------####
	def getParamsFromFile(self,newName, oldName="", default ={}): # called from read config for various input files
			out = copy.copy(default)
			if os.path.isfile(newName):
				try:
					f = self.openEncoding(newName, "r")
					out	 = json.loads(f.read())
					f.close()
					if oldName !="" and os.path.isfile(oldName):
						os.system("rm "+oldName)
				except	Exception as e:
					if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
					out = copy.copy(default)
			else:
				out = copy.copy(default)
			if oldName !="" and os.path.isfile(oldName):
				try:
					f = self.openEncoding(oldName, "r")
					out	 = json.loads(f.read())
					f.close()
					os.system("rm "+oldName)
				except	Exception as e:
					if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
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
				f = self.openEncoding(fName,"w")
				f.write(out)
				f.close()
			return out

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return ""



	####-----------------  update state lists ---------
	def deviceStartComm(self, dev):
		if self.decideMyLog("Logic"): self.indiLOG.log(10,"starting device:  {}  {}  {}".format(dev.name, dev.id, dev.states["MAC"]))

		if	self.pluginState == "init":
			dev.stateListOrDisplayStateIdChanged()

			if self.version < 2.0:
				props = dev.pluginProps
				self.indiLOG.log(10,"Checking for deviceType Update: "+ dev.name )
				if "SupportsOnState" not in props:
					self.indiLOG.log(10," processing: "+ dev.name)
					dev = indigo.device.changeDeviceTypeId(dev, dev.deviceTypeId)
					dev.replaceOnServer()
					dev = indigo.devices[dev.id]
					props = dev.pluginProps
					props["SupportsSensorValue"] 		= False
					props["SupportsOnState"] 			= True
					props["AllowSensorValueChange"] 	= False
					props["AllowOnStateChange"] 		= False
					props["SupportsStatusRequest"] 		= False
					self.indiLOG.log(10, "{}".format(dev.pluginProps))
					dev.replacePluginPropsOnServer(props)
					dev= indigo.devices[dev.id]

					if (dev.states["status"].lower()).lower() in ["up","rec","ON"]:
						dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOn)
					elif (dev.states["status"].lower()).find("down")==0:
						dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOff)
					else:
						dev.updateStateImageOnServer(indigo.kStateImageSel.SensorTripped)
					dev.replaceOnServer()
					#dev= indigo.devices[dev.id]
					dev.updateStateOnServer("onOffState",value=(dev.states["status"].lower()) in["up","rec","ON"], uiValue=dev.states["displayStatus"] )
					self.indiLOG.log(10,"SupportsOnState after replacePluginPropsOnServer")

			isType={"UniFi":"isUniFi","camera":"isCamera","gateway":"isGateway","Device-SW":"isSwitch","Device-AP":"isAP","neighbor":"isNeighbor","NVR":"isNVR"}
			props = dev.pluginProps
			devTid = dev.deviceTypeId
			for iT in isType:
				testId = devTid[0:min( len(iT),len(devTid) ) ]
				if iT == testId:
					isT = isType[iT]
					if isT not in props or props[isT] != True:
						props[isT] = True
						dev.replacePluginPropsOnServer(props)
					break

			if "enableBroadCastEvents" not in props:
				props = dev.pluginProps
				props["enableBroadCastEvents"] = "0"
				dev.replacePluginPropsOnServer(props)


		elif self.pluginState == "run":
			self.devNeedsUpdate[dev.id] = True

		return

	####-----------------	 ---------
	def deviceStopComm(self, dev):
		if	self.pluginState != "stop":
			self.devNeedsUpdate[dev.id] = True
			if self.decideMyLog("Logic"): self.indiLOG.log(10,"stopping device:  {}  {}".format(dev.name, dev.id) )

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



	###########################		DEVICE	#################################
####-------------------------------------------------------------------------####
	def getDeviceConfigUiValues(self, pluginProps, typeId, devId):
		try:
			theDictList =  super(Plugin, self).getDeviceConfigUiValues(pluginProps, typeId, devId)
			for groupNo in range(_GlobalConst_numberOfGroups):
				theDictList[0]["Gtext{}".format(groupNo)] =  self.groupNames[groupNo]
			return theDictList
		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		return super(Plugin, self).getDeviceConfigUiValues(pluginProps, typeId, devId)


	####-----------------	 ---------
	def validateDeviceConfigUi(self, valuesDict=None, typeId="", devId=0):
		try:
			if self.decideMyLog("Logic"): self.indiLOG.log(10,"Validate Device dict:, devId:{}  vdict:{}".format(devId,valuesDict) )
			self.devNeedsUpdate[int(devId)] = True

			dev = indigo.devices[int(devId)]
			if "groupMember" in dev.states:
				gMembers =""
				for groupNo in range(_GlobalConst_numberOfGroups):
					if "Group{}".format(groupNo) in valuesDict:
						if valuesDict["Group{}".format(groupNo)]:
							gMembers += self.groupNames[groupNo]+","
							self.groupStatusList[groupNo]["members"]["{}".format(devId)] = True

						elif "{}".format(devId) in	self.groupStatusList[groupNo]["members"]: 
							del self.groupStatusList[groupNo]["members"]["{}".format(devId)]

					elif "{}".format(devId) in	self.groupStatusList[groupNo]["members"]: 
						del self.groupStatusList[groupNo]["members"]["{}".format(devId)]
				if gMembers != "":
					if devId not in self.delayedAction:
						self.delayedAction[devId] = []
					self.delayedAction[devId].append({"action":"updateState", "state":"groupMember", "value":gMembers})
			return (True, valuesDict)
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		errorDict = valuesDict
		return (False, valuesDict, errorDict)


	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine returns the XML for the PluginConfig.xml by default; you probably don't
	# want to use this unless you have a need to customize the XML (again, uncommon)
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	def xxgetPrefsConfigUiXml(self):
		return super(Plugin, self).getPrefsConfigUiXml()



	####-----------------  setconfig default values	---------
	def setfilterunifiCloudKeyListOfSiteNames(self, valuesDict):

		# not set yet, for future use
		if self.refreshCallbackMethodAlreadySet == "yes": return valuesDict 

		if valuesDict["unifiControllerType"] == "hosted":
			valuesDict["overWriteControllerPort"]	 = "8443"
			valuesDict["unifiCloudKeySiteName"]		 = "default"

		controllerType = valuesDict["unifiControllerType"]
		if   controllerType == "UDM":
			valuesDict["ControllerBackupPath"]		= kDefaultPluginPrefs.get("infoLabelbackup1","/usr/lib/unifi/data/backup/autobackup")
			valuesDict["ipUDMON"]	 				= True

		elif controllerType == "UDMPro":
			valuesDict["ControllerBackupPath"]		= kDefaultPluginPrefs.get("infoLabelbackup1","/usr/lib/unifi/data/backup/autobackup")
			valuesDict["ipUDMON"]	 				= True

		elif controllerType == "std":
			valuesDict["ControllerBackupPath"]		= kDefaultPluginPrefs.get("infoLabelbackup2a","")
			valuesDict["ipUDMON"]	 				= False

		elif controllerType == "off":
			valuesDict["unifiCloudKeyMode"] 		= "off"
			valuesDict["ControllerBackupPath"]		= kDefaultPluginPrefs.get("infoLabelbackup2","/data/unifi/data/backup/autobackup")
			valuesDict["ipUDMON"]	 				= False

		else:
			pass

		valuesDict["unifiCloudKeySiteName"]	= self.unifiCloudKeySiteName

		#self.refreshCallbackMethodAlreadySet = "yes" # only do it once after called 
		return valuesDict

	####----------------- set unifi controller site ID anmes in dynamic list ---------
	def filterunifiCloudKeyListOfSiteNames(self, filter="", valuesDict=None, typeId="", targetId=""):

		xList = [["x","set to empty = re-read list from controller"]]
		for xx in self.unifiCloudKeyListOfSiteNames:
			xList.append([xx,xx])
		xList.append(["set","overwrite in next field"])
		return xList


	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine returns the UI values for the configuration dialog; the default is to
	# simply return the self.pluginPrefs dictionary. It can be used to dynamically set
	# defaults at run time
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	def getPrefsConfigUiValues(self):
		try:
			(valuesDict, errorsDict) = super(Plugin, self).getPrefsConfigUiValues()

			valuesDict["unifiUserID"]				= self.connectParams["UserID"]["unixDevs"]
			valuesDict["unifiUserIDUDM"]			= self.connectParams["UserID"]["unixUD"]
			valuesDict["nvrUNIXUserID"]			= self.connectParams["UserID"]["unixNVR"]
			valuesDict["nvrWebUserID"]				= self.connectParams["UserID"]["nvrWeb"]
			valuesDict["unifiCONTROLLERUserID"]	= self.connectParams["UserID"]["webCTRL"]

			valuesDict["unifiPassWd"]				= self.connectParams["PassWd"]["unixDevs"]
			valuesDict["unifiPassWdUDM"]			= self.connectParams["PassWd"]["unixUD"]
			valuesDict["nvrUNIXPassWd"]			= self.connectParams["PassWd"]["unixNVR"]
			valuesDict["unifiCONTROLLERPassWd"]	= self.connectParams["PassWd"]["webCTRL"]


			valuesDict["GWtailEnable"]				= self.connectParams["enableListener"]["GWtail"]
			valuesDict["refreshCallbackMethod"]	= "setfilterunifiCloudKeyListOfSiteNames"
			valuesDict["unifiCloudKeySiteName"]	= self.unifiCloudKeySiteName
			valuesDict["unifControllerCheckPortNumber"] = self.unifControllerCheckPortNumber
			#self.refreshCallbackMethodAlreadySet	= "yes"

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return (valuesDict, errorsDict)

	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	# This routine is called once the user has exited the preferences dialog
	#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
	def closedPrefsConfigUi(self, valuesDict , userCancelled):
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
			valuesDict["MSG"]								= "ok"
			rebootRequired									= ""
			self.lastUnifiCookieCurl						= 0
			self.lastUnifiCookieRequests					= 0

			self.lastNVRCookie								= 0
			self.checkforUnifiSystemDevicesState			= "validate config"
			self.enableSqlLogging							= valuesDict["enableSqlLogging"]
			self.enableFINGSCAN								= valuesDict["enableFINGSCAN"]
			self.count_APDL_inPortCount						= valuesDict["count_APDL_inPortCount"]

			self.enableBroadCastEvents						= valuesDict["enableBroadCastEvents"]
			self.sendBroadCastEventsList					= []
			self.ignoreNewNeighbors							= valuesDict["ignoreNewNeighbors"]
			self.ignoreNewClients							= valuesDict["ignoreNewClients"]
			#self.loopSleep									= float(valuesDict["loopSleep"])
			self.unifiControllerBackupON					= valuesDict["unifiControllerBackupON"]
			self.ControllerBackupPath						= valuesDict["ControllerBackupPath"]

			self.unifiControllerOS							= "" # force initialization of connection
			self.copyProtectsnapshots						= valuesDict["copyProtectsnapshots"]
			self.refreshProtectCameras						= float(valuesDict["refreshProtectCameras"])
			self.protecEventSleepTime						= float(valuesDict["protecEventSleepTime"])
			self.unifControllerCheckPortNumber				= valuesDict["unifControllerCheckPortNumber"] 
			self.requestTimeout								= max(1., float(valuesDict["requestTimeout"]))


			try: self.readBuffer							= int(valuesDict["readBuffer"])
			except: self.readBuffer							= 32767

			try:	self.maxConsumedTimeQueueForWarning		= float(valuesDict["maxConsumedTimeQueueForWarning"])
			except:	self.maxConsumedTimeQueueForWarning		= 5.
			valuesDict["maxConsumedTimeQueueForWarning"]	= self.maxConsumedTimeQueueForWarning

			try:	self.maxConsumedTimeForWarning			= float(valuesDict["maxConsumedTimeForWarning"])
			except:	self.maxConsumedTimeForWarning			= 3.
			valuesDict["maxConsumedTimeForWarning"]		= self.maxConsumedTimeForWarning

			if self.launchWaitSeconds != float(valuesDict["launchWaitSeconds"]):
				rebootRequired +="launchWaitSeconds changed "
			self.launchWaitSeconds							= float(valuesDict["launchWaitSeconds"])

			self.rebootUnifiDeviceOnError					= valuesDict["rebootUnifiDeviceOnError"]

			if self.connectParams["UserID"]["unixDevs"]	!= valuesDict["unifiUserID"]:				rebootRequired += " unifiUserID changed;"
			if self.connectParams["PassWd"]["unixDevs"]	!= valuesDict["unifiPassWd"]:				rebootRequired += " unifiPassWd changed;"
			if self.connectParams["UserID"]["unixUD"] 	!= valuesDict["unifiUserIDUDM"]:			rebootRequired += " unifiUserIDUDM changed;"
			if self.connectParams["PassWd"]["unixUD"] 	!= valuesDict["unifiPassWdUDM"]:			rebootRequired += " unifiPassWdUDM changed;"

			self.connectParams["UserID"]["unixUD"]		= valuesDict["unifiUserIDUDM"]
			self.connectParams["PassWd"]["unixUD"]		= valuesDict["unifiPassWdUDM"]
			self.useStrictToLogin							= valuesDict["useStrictToLogin"]

			self.connectParams["UserID"]["webCTRL"]		= valuesDict["unifiCONTROLLERUserID"]
			self.connectParams["PassWd"]["webCTRL"]		= valuesDict["unifiCONTROLLERPassWd"]

			self.connectParams["UserID"]["unixDevs"]		= valuesDict["unifiUserID"]
			self.connectParams["PassWd"]["unixDevs"]		= valuesDict["unifiPassWd"]

			self.restartListenerEvery = float(valuesDict["restartListenerEvery"])

			self.curlPath									= valuesDict["curlPath"]
			self.requestOrcurl								= valuesDict["requestOrcurl"]


			self.unifiCloudKeyIP							= valuesDict["unifiCloudKeyIP"]
			if self.overWriteControllerPort != valuesDict["overWriteControllerPort"]:
				rebootRequired								+= "controller port overwrite changed"
			self.overWriteControllerPort					= valuesDict["overWriteControllerPort"]


			#self.indiLOG.log(10,"unifiCloudKeySiteName old:>{}<   new:>{}<, types:{}  {}".format(self.unifiCloudKeySiteName, valuesDict["unifiCloudKeySiteName"], type(" ") , type(valuesDict["unifiCloudKeySiteName"]) ) )
			if type(" ") != type(valuesDict["unifiCloudKeySiteName"]): valuesDict["unifiCloudKeySiteName"] = ""
			#self.indiLOG.log(10,"unifiCloudKeySiteName old:>{}<   new:>{}<".format(self.unifiCloudKeySiteName, valuesDict["unifiCloudKeySiteName"] ) )
			if len(valuesDict["unifiCloudKeySiteName"]) < 3: 
				valuesDict["unifiCloudKeySiteName"] = ""
			if self.unifiCloudKeySiteName != valuesDict["unifiCloudKeySiteName"]:
				self.indiLOG.log(20,"setting unifiCloudKeySiteName from:>{}<   to:>{}<".format(self.unifiCloudKeySiteName, valuesDict["unifiCloudKeySiteName"] ) )
				self.executeCMDOnControllerReset()
			self.unifiCloudKeySiteName = valuesDict["unifiCloudKeySiteName"] 

			valuesDict["unifiCloudKeySiteNameFreeText"] = ""

			if valuesDict["unifiControllerType"] == "off" or valuesDict["unifiCloudKeyMode"] == "off" or self.connectParams["UserID"]["webCTRL"] == "":
				self.unifiControllerType 					= "off"
				self.unifiCloudKeySiteName					= "off"
				self.connectParams["UserID"]["webCTRL"]		= ""
				valuesDict["unifiControllerType"]			= "off"
				valuesDict["unifiCloudKeyMode"]				= "off"
				valuesDict["unifiCONTROLLERUserID"]			= ""

			self.unifiControllerType						= valuesDict["unifiControllerType"]
			self.unifiCloudKeyMode							= valuesDict["unifiCloudKeyMode"]


			self.ignoreNeighborForFing						= valuesDict["ignoreNeighborForFing"]
			self.updateDescriptions							= valuesDict["updateDescriptions"]
			self.folderNameCreated							= valuesDict["folderNameCreated"]
			self.folderNameVariables						= valuesDict["folderNameVariables"]
			self.folderNameNeighbors						= valuesDict["folderNameNeighbors"]
			self.folderNameSystem							= valuesDict["folderNameSystem"]
			self.getFolderId()
			if self.enableMACtoVENDORlookup != valuesDict["enableMACtoVENDORlookup"] and self.enableMACtoVENDORlookup == "0":
				rebootRequired							+= " MACVendor lookup changed; "
			self.enableMACtoVENDORlookup				= valuesDict["enableMACtoVENDORlookup"]


			for groupNo in range(_GlobalConst_numberOfGroups):
				self.groupNames[groupNo] = valuesDict["Group{}".format(groupNo)]


	#new for UDM (pro)
			if self.unifiControllerType.find("UDM") > -1 and  valuesDict["unifiControllerType"].find("UDM") == -1:
				# make sure the devices are disabled when going from UDM to std. will require to edit config again
				valuesDict["ipsw{}".format(self.numberForUDM["SW"])]	= ""
				valuesDict["ipSWON{}".format(self.numberForUDM["SW"])]	= False
				valuesDict["ip{}".format(self.numberForUDM["SW"])]		= ""
				valuesDict["ipON{}".format(self.numberForUDM["SW"])] 	= False

			try: 	self.controllerWebEventReadON		= int(valuesDict["controllerWebEventReadON"])
			except: self.controllerWebEventReadON		= -1
			if self.unifiControllerType == "UDMpro":
					self.controllerWebEventReadON		= -1 

			"""
			xx											= "{}".format(int(valuesDict["timeoutDICT"]))
			if xx != self.timeoutDICT:
				rebootRequired	+= " timeoutDICT  changed; "
				self.timeoutDICT						= xx
			"""

			##

			if False:
				for TT in["AP","GW","SW"]:
					try:	xx			 = "{}".format(int(valuesDict["readDictEverySeconds"+TT]))
					except: xx			 = "120"
					if xx != self.readDictEverySeconds[TT]:
						self.readDictEverySeconds[TT]				  = xx
						valuesDict["readDictEverySeconds"+TT]		  = xx
						rebootRequired	+= " readDictEverySeconds  changed; "


			if False:
				try:	xx			 = int(valuesDict["restartIfNoMessageSeconds"])
				except: xx			 = 500
				if xx != self.restartIfNoMessageSeconds:
					self.restartIfNoMessageSeconds					 = xx
					valuesDict["restartIfNoMessageSeconds"]		 = xx

			try:	self.expirationTime					= int(valuesDict["expirationTime"])
			except: self.expirationTime					= 120
			valuesDict["expirationTime"]				= self.expirationTime
			try:	self.expTimeMultiplier				= int(valuesDict["expTimeMultiplier"])
			except: self.expTimeMultiplier				= 2.
			valuesDict["expTimeMultiplier"]			= self.expTimeMultiplier

			self.fixExpirationTime						= valuesDict["fixExpirationTime"]

			## AP parameters
			acNew = [False for i in range(_GlobalConst_numberOfAP)]
			ipNew = ["" for i in range(_GlobalConst_numberOfAP)]
			self.numberOfActive["AP"] = 0
			for i in range(_GlobalConst_numberOfAP):
				ip0 = valuesDict["ip{}".format(i)]
				ac	= valuesDict["ipON{}".format(i)]
				self.debugDevs["AP"][i] = valuesDict["debAP{}".format(i)]
				if not self.isValidIP(ip0): ac = False
				acNew[i]			 = ac
				ipNew[i]			 = ip0
				if ac: 
					acNew[i] = True
					self.numberOfActive["AP"] 	+= 1
				if acNew[i] != self.devsEnabled["AP"][i]:
					rebootRequired	+= " enable/disable AP changed; "
				if ipNew[i] != self.ipNumbersOf["AP"][i]:
					rebootRequired	+= " Ap ipNumber  changed; "
					self.deviceUp["AP"][ipNew[i]] = time.time()
			self.ipNumbersOf["AP"] = copy.copy(ipNew)
			self.devsEnabled["AP"] = copy.copy(acNew)

			## Switch parameters
			acNew = [False for i in range(_GlobalConst_numberOfSW)]
			ipNew = ["" for i in range(_GlobalConst_numberOfSW)]
			self.numberOfActive["SW"] = 0
			for i in range(_GlobalConst_numberOfSW):
				if self.isMiniSwitch[i] != valuesDict["isMini{}".format(i)]: rebootRequired	+= " SW type changed: {} vs {}".format(self.isMiniSwitch[i], valuesDict["isMini{}".format(i)])
				self.isMiniSwitch[i] = valuesDict["isMini{}".format(i)]
				ip0 = valuesDict["ipSW{}".format(i)]
				ac	= valuesDict["ipSWON{}".format(i)]
				self.debugDevs["SW"][i] = valuesDict["debSW{}".format(i)]
				if not self.isValidIP(ip0): ac = False
				acNew[i] = ac
				ipNew[i] = ip0
				if ac: 
					acNew[i] = True
					self.numberOfActive["SW"] 	+= 1

				if acNew[i] != self.devsEnabled["SW"][i]:
					rebootRequired	+= " enable/disable SW  changed; "
				if ipNew[i] != self.ipNumbersOf["SW"][i]:
					rebootRequired	+= " SW ipNumber   changed; "
					self.deviceUp["SW"][ipNew[i]] = time.time()
			self.ipNumbersOf["SW"] = copy.copy(ipNew)
			self.devsEnabled["SW"] = copy.copy(acNew)



			## UGA parameters
			ip0			= valuesDict["ipUGA"]
			if self.ipNumbersOf["GW"] != ip0:
				rebootRequired	+= " GW ipNumber   changed; "

			ac			= valuesDict["ipUGAON"]
			if not self.isValidIP(ip0): ac = False
			if self.devsEnabled["GW"] != ac:
				rebootRequired	+= " enable/disable GW  changed; "

			self.devsEnabled["GW"]	   	= ac
			self.ipNumbersOf["GW"] 		= ip0
			self.debugDevs["GW"][0]		= valuesDict["debGW"]

			if 	self.connectParams["enableListener"]["GWtail"] != valuesDict["GWtailEnable"]:
				rebootRequired	+= " enable/disable GW  changed; "

			self.connectParams["enableListener"]["GWtail"] = valuesDict["GWtailEnable"]	


			## UDM parameters
			ip0			= valuesDict["ipUDM"]
			if self.ipNumbersOf["UD"] != ip0:
				rebootRequired	+= " UDM ipNumber   changed; "

			ac			= valuesDict["ipUDMON"]
			if not self.isValidIP(ip0): ac = False
			if self.devsEnabled["UD"] != ac:
				rebootRequired	+= " enable/disable UDM changed; "

			self.devsEnabled["UD"]		= ac
			self.ipNumbersOf["UD"]		= ip0
			self.debugDevs["UD"][0]		= valuesDict["debUD"]
			if self.devsEnabled["UD"]:
				self.ipNumbersOf["SW"][self.numberForUDM["SW"]]		= ip0
				valuesDict["ipsw{}".format(self.numberForUDM["SW"])]	= ip0
				valuesDict["ipSWON{}".format(self.numberForUDM["SW"])] = True
				self.devsEnabled["SW"][self.numberForUDM["SW"]]		= True
				self.numberOfActive["SW"] 							= max(1,self.numberOfActive["SW"] )

				self.ipNumbersOf["GW"] 						  		= ip0
				valuesDict["ipNumbersOfGW"]						= ip0
				valuesDict["ipUGAON"]								= True

				if valuesDict["unifiControllerType"] == "UDM": ## only for UDM not for UDM-pro,has no AP
					self.ipNumbersOf["AP"][self.numberForUDM["AP"]]		= ip0
					valuesDict["ip{}".format(self.numberForUDM["AP"])]		= ip0
					valuesDict["ipON{}".format(self.numberForUDM["AP"])]	= True
					self.devsEnabled["AP"][self.numberForUDM["AP"]] 		= True
					self.numberOfActive["AP"] 								= max(1,self.numberOfActive["AP"] )

				valuesDict["ipNumbersOfGW"]								= ip0

			"""
			## video parameters
			if self.connectParams["UserID"]["unixNVR"]	!= valuesDict["nvrUNIXUserID"]:	  rebootRequired += " nvrUNIXUserID changed;"
			if self.connectParams["PassWd"]["unixNVR"]	!= valuesDict["nvrUNIXPassWd"]:	  rebootRequired += " nvrUNIXPassWd changed;"

			self.unifiVIDEONumerOfEvents	= int(valuesDict["unifiVIDEONumerOfEvents"])
			self.connectParams["UserID"]["unixNVR"]	= valuesDict["nvrUNIXUserID"]
			self.connectParams["PassWd"]["unixNVR"]	= valuesDict["nvrUNIXPassWd"]
			self.connectParams["UserID"]["nvrWeb"]	= valuesDict["nvrWebUserID"]
			self.connectParams["PassWd"]["nvrWeb"]	= valuesDict["nvrWebPassWd"]
			self.vmMachine								= valuesDict["vmMachine"]
			self.mountPathVM							= valuesDict["mountPathVM"]
			self.videoPath								= self.completePath(valuesDict["videoPath"])
			self.vboxPath								= self.completePath(valuesDict["vboxPath"])
			self.changedImagePath						= self.completePath(valuesDict["changedImagePath"])
			self.vmDisk									= valuesDict["vmDisk"]
			enableVideoSwitch							= valuesDict["cameraSystem"]
			ip0											= valuesDict["nvrIP"]


			self.cameraSystem = enableVideoSwitch
			if self.cameraSystem =="nvr":
				self.ipNumbersOf["VD"]	= ip0
				if self.ipNumbersOf["VD"] != ip0 :
					rebootRequired	+= " VIDEO ipNumber changed;"
					self.indiLOG.log(10,"IP# old:{}, new:{}".format(self.ipNumbersOf["VD"], ip0) )

			"""


			if self.cameraSystem != valuesDict["cameraSystem"]:
				rebootRequired	+= " video enabled/disabled;"
				self.cameraSystem = valuesDict["cameraSystem"]

			self.checkForNewUnifiSystemDevicesEvery = int(valuesDict["checkForNewUnifiSystemDevicesEvery"])

			self.useDBInfoForWhichDevices = valuesDict["useDBInfoForWhichDevices"]
			if self.isValidIP(self.unifiCloudKeyIP) and (self.unifiCloudKeyMode.find("ON") >-1 or self.unifiCloudKeyMode.find("UDM") > -1 or self.useDBInfoForWhichDevices in ["all","perDevice"]):
				if self.unifiCloudKeyMode  != "ON":
					self.unifiCloudKeyMode = "ON"
				self.devsEnabled["DB"] = True
			else:
				self.devsEnabled["DB"]	= False



			if rebootRequired != "":
				self.indiLOG.log(30,"restart " + rebootRequired)
				self.quitNOW = "config changed"
			self.updateConnectParams  = time.time() - 100
			valuesDict["connectParams"] = json.dumps(self.connectParams)

			self.groupStatusINIT()

			self.setDebugFromPrefs(valuesDict)
			return True, valuesDict

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
			errorDict = indigo.Dict()
			errorDict["MSG"] = "error please check indigo eventlog"
			return (False, errorDict, valuesDict)





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
			#indigo.server.log(" changed: "+item+ " new: >"+ xxx +"< old:>"+old+"<") 
		return	 xxx, rebootRequired

	####-----------------  config setting ---- END   ----------#########

	####-----------------	 ---------
	def getCPU(self,pid):
		ret, err = self.readPopen("ps -ef | grep {}".format(pid) + " | grep -v grep")
		lines = ret.strip("\n").split("\n")
		for line in lines:
			if len(line) < 100: continue
			items = line.split()
			if items[1] != "{}".format(pid): continue
			if len(items) < 6: continue
			return (items[6])
		return ""

	def replaceTrueFalse(self,inString):
		outString = "{}".format(inString)
		try:
			outString = outString.replace("True","T").replace("False","F").replace(" ","").replace("[","").replace("]","").replace("{","").replace("}","").replace("(","").replace(")","")
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return outString
	####-----------------	 ---------
	def printConfigMenu(self,  valuesDict=None, typeId=""):
		try:
			out = "\n"
			out += "\n "
			out += "\nUniFi   =============plugin config Parameters========"

			out += "\ndebugAreas".ljust(40)								+	"{}".format(self.debugLevel)
			out += "\nlogFile".ljust(40)								+	self.PluginLogFile
			out += "\nenableFINGSCAN".ljust(40)							+	"{}".format(self.enableFINGSCAN)[0]
			out += "\ncheckForNewUnifiSystemDevicesEvery".ljust(40)		+	"{} minutes".format(self.checkForNewUnifiSystemDevicesEvery)
			out += "\ncount_APDL_inPortCount".ljust(40)					+	"{}".format(self.count_APDL_inPortCount == "1")[0]
			out += "\nenableBroadCastEvents".ljust(40)					+	"{}".format(self.enableBroadCastEvents == "1")[0]
			out += "\nignoreNeighborForFing".ljust(40)					+	"{}".format(self.ignoreNeighborForFing)[0]
			out += "\nexpirationTime - default".ljust(40)				+	"{:.0f} [sec]".format(self.expirationTime)
			out += "\nsleep in main loop  ".ljust(40)					+	"{:.0f} [sec]".format(self.loopSleep)
			out += "\nuse curl or request".ljust(40)					+	self.requestOrcurl
			out += "\ncurl path".ljust(40)								+	self.curlPath
			out += "\ncurl/requests timeout".ljust(40)					+	"{:.0f} [sec]".format(self.requestTimeout)
			out += "\ncpu used since restart: ".ljust(40) 				+	self.getCPU(self.myPID)
			out += "\n" 
			out += "\n====== used in ssh userid@switch-IP, AP-IP, USG-IP to get DB dump and listen to events"
			out += "\nUserID-ssh".ljust(40)								+	self.connectParams["UserID"]["unixDevs"]
			out += "\nPassWd-ssh".ljust(40)								+	self.connectParams["PassWd"]["unixDevs"]
			out += "\nUserID-ssh-UDM".ljust(40)							+	self.connectParams["UserID"]["unixUD"]
			out += "\nPassWd-ssh-UDM".ljust(40)							+	self.connectParams["PassWd"]["unixUD"]
			out += "\nread buffer size ".ljust(40)						+	"{:.0f}".format(self.readBuffer)
			for ipN in self.connectParams["promptOnServer"]:
				out += ("\npromptOnServer "+ipN).ljust(40)				+	"'"+self.connectParams["promptOnServer"][ipN]+"'"

			out += "\nGW tailCommand".ljust(40)							+	self.connectParams["commandOnServer"]["GWtail"]
			out += "\nGW dictCommand".ljust(40)							+	self.connectParams["commandOnServer"]["GWdict"]
			out += "\nSW tailCommand".ljust(40)							+	self.connectParams["commandOnServer"]["SWtail"]
			out += "\nSW dictCommand".ljust(40)							+	self.connectParams["commandOnServer"]["SWdict"]
			out += "\nAP tailCommand".ljust(40)							+	self.connectParams["commandOnServer"]["APtail"]
			out += "\nAP dictCommand".ljust(40)							+	self.connectParams["commandOnServer"]["APdict"]
			out += "\nUD dictCommand".ljust(40)							+	self.connectParams["commandOnServer"]["UDdict"]
			out += "\nAP enabled:".ljust(40)							+	self.replaceTrueFalse(self.devsEnabled["AP"])
			out += "\nSW enabled:".ljust(40)							+	self.replaceTrueFalse(self.devsEnabled["SW"])
			out += "\nGW enabled:".ljust(40)							+	self.replaceTrueFalse(self.devsEnabled["GW"])
			out += "\ncontrolelr DB read enabled".ljust(40)				+	self.replaceTrueFalse(self.devsEnabled["DB"])
			out += "\nUDM enabled".ljust(40)							+	self.replaceTrueFalse(self.devsEnabled["UD"])
			out += "\nread DB Dict every".ljust(40)						+	"{}".format(self.readDictEverySeconds).replace("'","").replace("u","").replace(" ","")+" [sec]"
			out += "\nrestart listeners if NoMessage for".ljust(40)		+	"{:.0f} [sec]".format(self.restartIfNoMessageSeconds)
			out += "\nforce restart of listeners ".ljust(40)			+	"{:.0f} [sec]".format(self.restartListenerEvery)
			out += "\nmax Consumed Time For Warning".ljust(40)			+	"{:.0f} [sec]".format(self.maxConsumedTimeForWarning)
			out += "\nmax Consumed Time Queue For Warning".ljust(40)	+	"{:.0f} [sec]".format(self.maxConsumedTimeQueueForWarning)
			out += "\nwait time betwen lauch of listeners".ljust(40)	+	"{:.2f} [sec]".format(self.launchWaitSeconds)

			out += "\n"
			out += "\n====== CONTROLLER/UDM WEB ACCESS , set parameters and reporting"
			out += "\n  curl data={WEB-UserID:..,WEB-PassWd:..} https://controllerIP: ..--------------"
			out += "\nMode: off, ON, UDM, reports only".ljust(40)		+	self.unifiCloudKeyMode 
			out += "\nWEB-UserID".ljust(40)								+	self.connectParams["UserID"]["webCTRL"]
			out += "\nWEB-PassWd".ljust(40)								+	self.connectParams["PassWd"]["webCTRL"]
			out += "\nController Type (UDM,..,std)".ljust(40)			+	self.unifiControllerType 
			out += "\nuse strict:true for web login".ljust(40)			+	"{}".format(self.useStrictToLogin)[0] 
			out += "\nController port#".ljust(40)						+	self.unifiCloudKeyPort 
			out += "\noverWriteControllerPort".ljust(40)				+	self.overWriteControllerPort 
			out += "\nController site Name".ljust(40)					+	self.unifiCloudKeySiteName 
			out += "\nController site NameList ".ljust(40)				+	"{}".format(self.unifiCloudKeyListOfSiteNames)

			out += "\nController API WebPage".ljust(40)					+	self.unifiApiWebPage 
			out += "\nController API login WebPage".ljust(40)			+	self.unifiApiLoginPath
			out += "\n"
			if self.cameraSystem == "nvr":
				out += "\n====== camera NVR stuff ---------------------------"
				out += "\nCamera enabled".ljust(40)						+	self.cameraSystem 
				out += "\n=  get camera DB config and listen to recording event logs"
				out += "\n  ssh NVR-UNIXUserID@NVR-IP "
				out += "\nNVR-UNIXUserID".ljust(40)						+	self.connectParams["UserID"]["unixNVR"]
				out += "\nNVR-UNIXpasswd".ljust(40)						+	self.connectParams["PassWd"]["unixNVR"] 
				out += "\nVD tailCommand".ljust(40)						+	self.connectParams["commandOnServer"]["VDtail"]
				out += "\nVD dictCommand".ljust(40)						+	self.connectParams["commandOnServer"]["VDdict"] 
				out += "\n= getting snapshots and reading and changing parameters"
				out += "\n  curl data={WEB-UserID:..,WEB-PassWd:..} https://NVR-IP#:  ....   for commands and read parameters "
				out += "\n  requests(http://IP-NVR:7080/api/2.0/snapshot/camera/**camApiKey**?force=true&width=1024&apiKey=nvrAPIkey,stream=True)  for snap shots"
				out += "\nimageSourceForSnapShot".ljust(40)				+	self.imageSourceForSnapShot
				out += "\nimageSourceForEvent".ljust(40)				+	self.imageSourceForEvent 
				out += "\nNVR-WEB-UserID".ljust(40)						+	self.connectParams["UserID"]["nvrWeb"]
				out += "\nNVR-WEB-passWd".ljust(40)						+	self.connectParams["PassWd"]["nvrWeb"]
				out += "\nNVR-API Key".ljust(40)						+	self.nvrVIDEOapiKey
				out += "\nVideo NVR-IP#".ljust(40)						+	self.ipNumbersOf["VD"]
			elif self.cameraSystem == "protect":
				pass
			out += "\n"
			out += "\n" + "#   AP ip#".ljust(20)  						+	"enabled / disabled / is mini switch "
			for ll in range(len(self.ipNumbersOf["AP"])):
				out += "\n{:2} ".format(ll) + self.ipNumbersOf["AP"][ll].ljust(20) 	+		"{:1}".format(self.devsEnabled["AP"][ll])

			out += "\n" + "#   SW ip#"
			for ll in range(len(self.ipNumbersOf["SW"])):
				out += "\n{:2} ".format(ll) + self.ipNumbersOf["SW"][ll].ljust(20) 	+		"{:1}, {:1}".format(self.devsEnabled["SW"][ll], self.isMiniSwitch[ll])

			out += "\n" + "  USG/UGA  gateway/router"
			out += "\n  " + self.ipNumbersOf["GW"].ljust(20) 			+		"{}".format(self.devsEnabled["GW"])[0]

			out += "\n" + "  Controller / cloud Key IP#"
			out += "\n  " + self.unifiCloudKeyIP.ljust(20) 				
			out += "\n" + "--------------------------"
			out += "\n"

			out += "\nUniFi    =============plugin config Parameters========  END "
			out += "\n "

			self.indiLOG.log(20,out)
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return


	####-----------------	 ---------
	def printMACs(self,MAC=""):
		try:

			out = "\n ===== UNIFI device info ========="
			for dev in indigo.devices.iter(self.pluginId):
				if dev.deviceTypeId == "client":		  continue
				if MAC !="" and dev.states["MAC"] != MAC: continue
				out += "\ndevice info         {}  id: {:<12d}; type:{:}".format(dev.name, dev.id, dev.deviceTypeId)
				out += "\n   props:"
				props = dev.pluginProps
				for p in props:
					out += "\n                    {}: {}".format(p, props[p])

				out += "\n    states:"
				for p in dev.states:
					out += "\n                    {}: {}".format(p, dev.states[p])

			out += "\n    counters, timers etc:"
			if MAC in self.MAC2INDIGO["UN"]:
				out += "\nUniFi                {}".format(self.MAC2INDIGO["UN"][MAC])

			if MAC in self.MAC2INDIGO["AP"]:
				out += "\nAP                   {}".format(self.MAC2INDIGO["AP"][MAC])

			if MAC in self.MAC2INDIGO["SW"]:
				out += "\nSWITCH               {}".format(self.MAC2INDIGO["SW"][MAC])

			if MAC in self.MAC2INDIGO["GW"]:
				out += "\nGATEWAY              {}".format(self.MAC2INDIGO["GW"][MAC])

			if MAC in self.MAC2INDIGO["NB"]:
				out += "\nNEIGHBOR             {}".format(self.MAC2INDIGO["NB"][MAC])


			out += "\ndevice info              ===== UNIFI device info ========= END "

			self.indiLOG.log(20,out)
		except	Exception as e:
			if "{}".format(e).find("None") == -1:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

	####-----------------	 ---------
	def printALLMACs(self):
		try:
			out = "\n         ===== UNIFI device info ========="

			for dev in indigo.devices.iter(self.pluginId):
				if dev.deviceTypeId == "client": continue
				out += "\n{:20s} id:{:12d};  type:{:s}".format(dev.name, dev.id, dev.deviceTypeId)
				line="props: "
				props = dev.pluginProps
				for p in props:
					line+= "{}:{}; ".format(p, props[p])
				out += "\n                     {}".format(line)
				line="states: "
				for p in dev.states:
					line += "{}:{};  ".format(p, dev.states[p])
				out += "\n                     {}".format(line)

				out += "\n======Temp data, counters, timer etc======="

			for dd in self.MAC2INDIGO["UN"]:
				out += "\nUNIFI   {}          {}".format(dd, self.MAC2INDIGO["UN"][dd])
			for dd in self.MAC2INDIGO["AP"]:
				out += "\AP       {}          {}".format(dd, self.MAC2INDIGO["AP"][dd])
			for dd in self.MAC2INDIGO["SW"]:
				out += "\SWITCH   {}          {}".format(dd, self.MAC2INDIGO["SW"][dd])
			for dd in self.MAC2INDIGO["GW"]:
				out += "\GATEWAY  {}          {}".format(dd, self.MAC2INDIGO["GW"][dd])
			for dd in self.MAC2INDIGO["NB"]:
				out += "\nNB      {}          {}".format(dd, self.MAC2INDIGO["NB"][dd])

			out += "\n                        ===== UNIFI device info ========= END "

			self.indiLOG.log(20,out)


		except	Exception as e:
			if "{}".format(e).find("None") == -1:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)



	####-----------------     ---------
	def printALLUNIFIsreduced(self):
		try:

			lineI = []
			lineE = []
			lineD = []
			out = "\n"
			dType ="UniFi"
			out +="\n ===== UniFi device info =========                              curr.;  exp;   use ping  ; use WOL;     use what 4;       WiFi;WiFi-max;    DHCP;  SW-UPtm; lastStatusChge;                              reason;     member of;"
			out +="\ndev Name                       id:         MAC#             ;  status; time;   up;   down;   [sec];         Status;     Status;  idle-T; max-AGE;    chged;               ;                          for change;        groups;"
			for dev in indigo.devices.iter("props.isUniFi"):
				line = ""
				props = dev.pluginProps
				mac = dev.states["MAC"]
				if "useWhatForStatus" in props and props["useWhatForStatus"] == "WiFi": wf = True
				else:																	   wf = False

				if True:											line  = "{}".format(dev.id).ljust(12)+mac+"; "

				if mac in self.MACignorelist and self.MACignorelist[mac]:
																	line += ("IGNORED").rjust(7)+"; "
				elif "status" in dev.states:						line += (dev.states["status"]).rjust(7)+"; "
				else:												line += ("-------").rjust(7)+"; "

				if "expirationTime" in props :						line += ("{}".format(props["expirationTime"]).split(".")[0]).rjust(4)+"; "
				else:												line += " ".ljust(4)+"; "

				if "usePingUP" in props :							line += ("{}".format(props["usePingUP"])).rjust(5)+"; "
				else:												line += " ".ljust(5)+"; "

				if "usePingDOWN" in props :						line += ("{}".format(props["usePingDOWN"])).rjust(5)+"; "
				else:												line += " ".ljust(5)+"; "

				if "useWOL" in props :
					if props["useWOL"] =="0":
																	line += ("no").ljust(7)+"; "
					else:
																	line += ("{}".format(props["useWOL"])).rjust(7)+"; "
				else:												line += "no".ljust(7)+"; "

				if "useWhatForStatus" in props :					line += ("{}".format(props["useWhatForStatus"])).rjust(14)+"; "
				else:												line += " ".ljust(14)+"; "

				if "useWhatForStatusWiFi" in props and wf:			line += ("{}".format(props["useWhatForStatusWiFi"])).rjust(10)+"; "
				else:												line += " ".ljust(10)+"; "

				if "idleTimeMaxSecs" in props and wf:				line += ("{}".format(props["idleTimeMaxSecs"])).rjust(7)+"; "
				else:												line += " ".ljust(7)+"; "

				if "useAgeforStatusDHCP" in props and not wf:		line += ("{}".format(props["useAgeforStatusDHCP"])).rjust(7)+"; "
				else:												line += " ".ljust(7)+"; "

				if "useupTimeforStatusSWITCH" in props and not wf: line += ("{}".format(props["useupTimeforStatusSWITCH"])).rjust(8)+"; "
				else:												line += " ".ljust(8)+"; "

				if "lastStatusChange" in dev.states:				line += ("{}".format(dev.states["lastStatusChange"])[5:]).rjust(14)+"; "
				else:												line += " ".ljust(14)+"; "
				if "lastStatusChangeReason" in dev.states:			line += ("{}".format(dev.states["lastStatusChangeReason"])[0:35]).rjust(35)+"; "
				else:												line += " ".ljust(35)+"; "

				if "groupMember" in dev.states:					line += (  ("{}".format(dev.states["groupMember"]).replace("Group","")).strip(",")	).rjust(13)+"; "
				else:												line += " ".ljust(13)+"; "

				devName = dev.name
				if len(devName) > 28: devName = devName[:28]+".." # max len of 30indicate cutoff if > 28 with ..
				if line.find("IGNORED;") >-1:
					lineI.append([line,devName])
				elif line.find("expired;") >-1:
					lineE.append([line,devName])
				elif line.find("down;") >-1:
					lineD.append([line,devName])
				else:
					out+= "\n{:30s} {}".format(devName, line)

			if lineD !=[]:
				for xx in lineD:
					out+= "\n{:30s} {}".format(xx[1],xx[0])
			if lineE !=[]:
				for xx in lineE:
					out+= "\n{:30s} {}".format(xx[1],xx[0])
			if lineI !=[]:
				for xx in lineI:
					out+= "\n{:30s} {}".format(xx[1],xx[0])

			out+= "\n            ===== UniFi device info ========= END "

			self.indiLOG.log(20,out)


		except	Exception as e:
			if "{}".format(e).find("None") == -1:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)


	####-----------------  printGroups	  ---------
	def printGroups(self):
		try:
			out = "\nGROUPS-----           -------MEMBERS ( status = /Up/ Down/ Expired/ Ignored) ----"
			for groupNo in range(_GlobalConst_numberOfGroups):
				indent = "\n            "
				xList =  ""
				memberNames = []
				for member in self.groupStatusList[groupNo]["members"]:
					if len(member) <2: continue
					try:
						ID = int(member)
						dev = indigo.devices[ID]
					except: continue
					memberNames.append(dev.name)

				newLine = indent
				for member in sorted(memberNames):
					try:
						dev = indigo.devices[member]
						newLine += "{:30s}/{}; ".format(member, dev.states["status"][0].upper())
						if len(newLine) > 180:
							xList += newLine
							newLine = indent
					except	Exception as e:
						if "{}".format(e).find("None") == -1:
							if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
				if	newLine != indent:
					xList += newLine

				if	xList != indent:
					gName = self.groupNames[groupNo]
					homeaway = ""
					try:
						homeaway +=  "   Home: " + indigo.variables["Unifi_Count_"+gName+"_Home"].value
						homeaway += ";   away: " + indigo.variables["Unifi_Count_"+gName+"_Away"].value
					except: pass
					out += "\n {:15s} {} ".format(gName, homeaway+xList.strip(","))
			out += "\nGROUPS-----   -------MEMBERS --------------- END"

			out += "\n"


			xList = "\n-------MEMBERS   ---------------- MAC# \n "
			lineNumber =0
			for member in sorted(self.MACignorelist):
				xList += member+", "
				if len(xList)/180  > lineNumber:
					lineNumber +=1
					xList +="\n "
			out += "\nIGNORED -----                    {}".format(xList.strip(","))
			out += "\nIGNORED -----   -------MEMBERS  ----------------- END\n"
			self.indiLOG.log(20, out )

		except	Exception as e:
			if "{}".format(e).find("None") == -1:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)




####-------------------------------------------------------------------------####
	def resetHostsFileCALLBACKmenu(self, valuesDict=None, typeId="", devId=0):
		if valuesDict is None: valuesDict = {}
		fn = "{}/.ssh/known_hosts".format(self.MAChome)

		if os.path.isfile(fn):
			os.remove(fn)

		if not os.path.isfile(fn):
			valuesDict["MSG"] = "{} file deleted".format(fn)
			self.indiLOG.log(30,"ssh known hosts file deleted:{}".format(fn))

		else:
			valuesDict["MSG"] = "ERROR {} file NOT deleted".format(fn)
			self.indiLOG.log(30,"Error ssh known hosts file  NOT deleted:{}".format(fn))

		return valuesDict


####-------------------------------------------------------------------------####
	def resetHostsFileOnlyUnifiCALLBACKmenu(self, valuesDict=None, typeId="", devId=0):
		if valuesDict is None: valuesDict = {}
		fn = "{}/.ssh/known_hosts".format(self.MAChome)
		removed = ""

		ipList = self.ipNumbersOf["AP"] + self.ipNumbersOf["SW"] + [self.ipNumbersOf["GW"] ] +[self.ipNumbersOf["UD"]]
		if os.path.isfile(fn):
			try:
				for ipN in ipList:
					if  self.isValidIP(ipN):
						f = open(fn, "r")
						lines  = f.readlines()
						f.close()

						f = open(fn, "w")
						for line in lines:
							if len(line) < 10: continue
							if line.find(ipN) >-1:
								self.indiLOG.log(30,"ssh known_hosts: removed line:{}".format(line.strip("\n")))
								continue
							f.write(line.strip("\n")+"\n")
						f.close()

			except	Exception as e:
				if "{}".format(e).find("None") == -1:
					if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)


		valuesDict["MSG"] = "rmved IPNs entries, see logfile"

		return valuesDict



	####-----------------  data stats menu items	---------
	def buttonRestartVDListenerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		self.restartRequest["VDtail"] = "VD"
		return valuesDict

	def buttonRestartGWListenerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		self.restartRequest["GWtail"] = "GW"
		self.restartRequest["GWdict"] = "GW"
		self.indiLOG.log(10,"menu RestartGWListener:{}".format(self.restartRequest))
		return valuesDict


	def buttonRestartAPListenerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		if valuesDict["pickAP"] != "-1":
			self.restartRequest["APtail"] = valuesDict["pickAP"]
			self.restartRequest["APdict"] = valuesDict["pickAP"]
		self.indiLOG.log(10,"menu RestartAPListener:{}".format(self.restartRequest))
		return valuesDict


	def buttonRestartAPProcessCALLBACK(self, valuesDict=None, typeId="", devId=""):
		if valuesDict["pickAP"] != "-1":
			self.restartRequest["APtail"] = valuesDict["pickAP"] + "-restart"
			self.restartRequest["APdict"] = valuesDict["pickAP"] + "-restart"
		self.indiLOG.log(10,"menu Restart AP :{}".format(self.restartRequest))
		return valuesDict

	def buttonRestartSWListenerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		if valuesDict["pickSW"] != "-1":
			self.restartRequest["SWdict"] = valuesDict["pickSW"]
		self.indiLOG.log(10,"menu Restart SW Listener:{}".format(self.restartRequest))
		return valuesDict

	def buttonRestartSWProcessCALLBACK(self, valuesDict=None, typeId="", devId=""):
		if valuesDict["pickAP"] != "-1":
			self.restartRequest["APtail"] = valuesDict["pickAP"] + "-restart"
			self.restartRequest["APdict"] = valuesDict["pickAP"] + "-restart"
		self.indiLOG.log(10,"menu Restart SW :{}".format(self.restartRequest))
		return valuesDict

	def buttonResetPromptsCALLBACK(self, valuesDict=None, typeId="", devId=""):
		self.connectParams["promptOnServer"] = {}
		self.pluginPrefs["connectParams"] = json.dumps(self.connectParams)
		indigo.server.savePluginPrefs()	
		self.quitNOW = "restart due to prompt settings reset"
		self.indiLOG.log(30," reset prompts, initating restart")
		return valuesDict

	def buttonstopVideoServiceCALLBACKaction(self, valuesDict):
		return
		self.execVideoAction(" \"service unifi-video stop\"")
		return valuesDict

	def buttonstopVideoServiceCALLBACK(self, valuesDict=None, typeId="", devId=""):
		return
		self.execVideoAction(" \"service unifi-video stop\"")
		return valuesDict

	def buttonstartVideoServiceCALLBACK(self, valuesDict=None, typeId="", devId=""):
		return
		self.execVideoAction(" \"service unifi-video start\"")
		return valuesDict
	def buttonstartVideoServiceCALLBACKaction(self, valuesDict):
		return
		self.execVideoAction(" \"service unifi-video start\"")
		return valuesDict

	def buttonMountOSXDriveOnVboxCALLBACKaction(self, valuesDict):
		return
		self.execVideoAction(" \"sudo mount -t vboxsf -o uid=unifi-video,gid=unifi-video video "+self.mountPathVM+"\"")
		return valuesDict

	def buttonMountOSXDriveOnVboxCALLBACK(self, valuesDict=None, typeId="", devId="",returnCmd=False):
		return
		self.execVideoAction(" \"sudo mount -t vboxsf -o uid=unifi-video,gid=unifi-video video "+self.mountPathVM+"\"", returnCmd=returnCmd)
		return valuesDict

	def execVideoAction(self,cmdIN,returnCmd=False):
		return
		try:
			uType = "VDdict"
			userid, passwd =  self.getUidPasswd(uType,self.ipNumbersOf["VD"])
			if userid == "":
				self.indiLOG.log(10,"CameraInfo  Video Action : userid not set")
				return ""

			if self.ipNumbersOf["VD"] not in self.connectParams["promptOnServer"]:
				self.testServerIfOK(self.ipNumbersOf["VD"],uType)

			cmd = self.expectPath  +" "
			cmd +=	"'" +  self.pathToPlugin + "videoServerAction.exp' "
			cmd +=	" '" +userid + "' '" + passwd + "' " 
			cmd +=	self.ipNumbersOf["VD"] + " " 
			cmd +=	"'"+self.escapeExpect(self.connectParams["promptOnServer"][self.ipNumbersOf["VD"]])+"' " 
			cmd += cmdIN
			if self.decideMyLog("Expect"):  self.indiLOG.log(10,"CameraInfo "+ cmd)
			cmd +=  self.getHostFileCheck()

			if returnCmd: return cmd

			ret, err = self.readPopen(cmd)

		except	Exception as e:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
				self.indiLOG.log(40,"promptOnServer={}".format(self.connectParams["promptOnServer"]))
				self.indiLOG.log(40,"ipNumbersOf={}".format(self.ipNumbersOf["VD"]))
				self.indiLOG.log(40,"userid:{}, passwd:{}".format(userid, passwd ))

		return ""

	####-----------------	 ---------
	####-----send commd parameters to cameras through VNR ------
	####-----------------	 ---------
	def buttonSendCommandToNVRLEDCALLBACKaction (self, action1=None):
		return
		return self.buttonSendCommandToNVRLEDCALLBACK(valuesDict= action1.props)
	def buttonSendCommandToNVRLEDCALLBACK(self, valuesDict=None, typeId="", devId="",returnCmd=False):
		return
		self.addToMenuXML(valuesDict)
		valuesDict["MSG"],x =  self.setupNVRcmd(valuesDict["cameraDeviceSelected"],{"enableStatusLed":valuesDict["camLED"] == "1"})
		return valuesDict

	####-----------------	 ---------
	def buttonSendCommandToNVRSoundsCALLBACKaction (self, action1=None):
		return
		return self.buttonSendCommandToNVRSoundsCALLBACK(valuesDict= action1.props)
	def buttonSendCommandToNVRSoundsCALLBACK(self, valuesDict=None, typeId="", devId="",returnCmd=False):
		return
		self.addToMenuXML(valuesDict)
		valuesDict["MSG"],x =  self.setupNVRcmd(valuesDict["cameraDeviceSelected"],{"systemSoundsEnabled":valuesDict["camSounds"] == "1"} )
		return valuesDict

	####-----------------	 ---------
	def buttonSendCommandToNVRenableSpeakerCALLBACKaction (self, action1=None):
		return
		return self.buttonSendCommandToNVRenableSpeakerCALLBACK(valuesDict= action1.props)
	def buttonSendCommandToNVRenableSpeakerCALLBACK(self, valuesDict=None, typeId="", devId="",returnCmd=False):
		return
		self.addToMenuXML(valuesDict)
		valuesDict["MSG"],x =  self.setupNVRcmd(valuesDict["cameraDeviceSelected"],{"enableSpeaker":valuesDict["enableSpeaker"] == "1", "speakerVolume":int(valuesDict["enableSpeaker"])} )
		return valuesDict

	####-----------------	 ---------
	def buttonSendCommandToNVRmicVolumeCALLBACKaction (self, action1=None):
		return
		return self.buttonSendCommandToNVRmicVolumeCALLBACK(valuesDict= action1.props)
	def buttonSendCommandToNVRmicVolumeCALLBACK(self, valuesDict=None, typeId="", devId="",returnCmd=False):
		return
		self.addToMenuXML(valuesDict)
		valuesDict["MSG"] = self.setupNVRcmd(valuesDict["cameraDeviceSelected"],{"micVolume":int(valuesDict["micVolume"])} )
		return valuesDict

	####-----------------	 ---------
	def buttonSendCommandToNVRRecordCALLBACKaction (self, action1=None):
		return self.buttonSendCommandToNVRRecordCALLBACK(valuesDict= action1.props)

	def buttonSendCommandToNVRRecordCALLBACK(self, valuesDict=None, typeId="", devId="",returnCmd=False):
		return
		self.addToMenuXML(valuesDict)
		if valuesDict["postPaddingSecs"] =="-1" and valuesDict["prePaddingSecs"] =="-1":
			valuesDict["MSG"],x =  self.setupNVRcmd(valuesDict["cameraDeviceSelected"],
					{"recordingSettings":{"motionRecordEnabled": valuesDict["motionRecordEnabled"] == "1","fullTimeRecordEnabled": valuesDict["fullTimeRecordEnabled"] == "1", 'channel': valuesDict["channel"]}
					} )
		elif valuesDict["postPaddingSecs"] !="-1" and valuesDict["prePaddingSecs"] !="-1":
			valuesDict["MSG"],x =  self.setupNVRcmd(valuesDict["cameraDeviceSelected"],
					{"recordingSettings":{"motionRecordEnabled": valuesDict["motionRecordEnabled"] == "1","fullTimeRecordEnabled": valuesDict["fullTimeRecordEnabled"] == "1", 'channel': valuesDict["channel"],
					"postPaddingSecs": int(valuesDict["postPaddingSecs"]),
					"prePaddingSecs": int(valuesDict["prePaddingSecs"]) }
					} )
		elif valuesDict["postPaddingSecs"] !="-1":
			valuesDict["MSG"],x =  self.setupNVRcmd(valuesDict["cameraDeviceSelected"],
					{"recordingSettings":{"motionRecordEnabled": valuesDict["motionRecordEnabled"] == "1","fullTimeRecordEnabled": valuesDict["fullTimeRecordEnabled"] == "1", 'channel': valuesDict["channel"],
					"postPaddingSecs": int(valuesDict["postPaddingSecs"]) }
					} )
		elif valuesDict["prePaddingSecs"] !="-1":
			valuesDict["MSG"],x =  self.setupNVRcmd(valuesDict["cameraDeviceSelected"],
					{"recordingSettings":{"motionRecordEnabled": valuesDict["motionRecordEnabled"] == "1","fullTimeRecordEnabled": valuesDict["fullTimeRecordEnabled"] == "1", 'channel': valuesDict["channel"],
					"prePaddingSecs": int(valuesDict["prePaddingSecs"]) }
					} )
		else:
			valuesDict["MSG"]="bad selection for recording"
		return valuesDict

	####-----------------	 ---------
	def buttonSendCommandToNVRIRCALLBACKaction (self, action1=None):
		return
		return self.buttonSendCommandToNVRIRCALLBACK(valuesDict= action1.props)
	def buttonSendCommandToNVRIRCALLBACK(self, valuesDict=None, typeId="", devId="",returnCmd=False):
		return
		self.addToMenuXML(valuesDict)
		xxx = valuesDict["irLedMode"]
		if xxx.find("auto") >-1:
			valuesDict["MSG"],x =  self.setupNVRcmd(valuesDict["cameraDeviceSelected"],{"ispSettings":{"enableExternalIr": int(valuesDict["enableExternalIr"]),"irLedMode":"auto" }} )
		else:# for manual 0/100/255 level
			xxx = xxx.split("-")
			valuesDict["MSG"],x =  self.setupNVRcmd(valuesDict["cameraDeviceSelected"],{"ispSettings":{"enableExternalIr": int(valuesDict["enableExternalIr"]),"irLedMode":xxx[0], "irLedLevel": int(xxx[1])}  } )
		return valuesDict
	####-----------------	 ---------
	def buttonSendCommandToNVRvideostreamingCALLBACKaction (self, action1=None):
		return
		return self.buttonSendCommandToNVRIRCALLBACK(valuesDict= action1.props)
	def buttonSendCommandToNVRvideostreamingCALLBACK(self, valuesDict=None, typeId="", devId="",returnCmd=False):
		return
		self.addToMenuXML(valuesDict)

		# first we need to get the current values
		error, ret = self.setupNVRcmd(valuesDict["cameraDeviceSelected"],"", cmdType="get")
		if "channels" not in ret[0] or len(ret[0]["channels"]) !=3 : # something went wrong
			self.indiLOG.log(40,"videostreaming error: {}     \n>>{}<<".format(error, ret))
			valuesDict["MSG"] = error
			return valuesDict

		# modify the required ones
		channels = ret[0]["channels"]
		channel	 = int(valuesDict["channelS"])
		channels[channel]["isRtmpEnabled"]	 = valuesDict["isRtmpEnabled"]  == "1"
		channels[channel]["isRtmpsEnabled"] = valuesDict["isRtmpsEnabled"] == "1"
		channels[channel]["isRtspEnabled"]  = valuesDict["isRtspEnabled"]  == "1"
		# send back
		error, data=  self.setupNVRcmd(valuesDict["cameraDeviceSelected"], {"channels":channels}, cmdType="put")
		valuesDict["MSG"]=error
		return valuesDict

	####-----------------	 ---------
	def buttonSendCommandToNVRgetSnapshotCALLBACKaction (self, action1=None):
		return
		return self.buttonSendCommandToNVRgetSnapshotCALLBACK(valuesDict= action1.props)
	def buttonSendCommandToNVRgetSnapshotCALLBACK(self, valuesDict=None, typeId="", devId="",returnCmd=False):
		return
		self.addToMenuXML(valuesDict)
		if   self.imageSourceForSnapShot == "imageFromNVR": 	valuesDict["MSG"] = self.getSnapshotfromNVR(valuesDict["cameraDeviceSelected"], valuesDict["widthOfImage"], valuesDict["fileNameOfImage"] )
		elif self.imageSourceForSnapShot == "imageFromCamera":	valuesDict["MSG"] = self.getSnapshotfromCamera(valuesDict["cameraDeviceSelected"],                          valuesDict["fileNameOfImage"] )
		return valuesDict

	####-----------------	 ---------
	def setupNVRcmd(self, devId, payload,cmdType="put"):
		return

		dev = indigo.devices[int(devId)]
		try:
			if not self.isValidIP(self.ipNumbersOf["VD"]): return "error IP",""
			if self.cameraSystem != "nvr":					 	return "error enabled",""
			if len(self.nvrVIDEOapiKey) < 5:				return "error apikey",""

			if payload != "":  payload['name']= dev.states["nameOnNVR"]
			ret = self.executeCMDonNVR(payload, dev.states["apiKey"],  cmdType=cmdType)
			self.fillCamerasIntoIndigo(ret, calledFrom="setupNVRcmd")
			return "ok",ret
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)



	####-----------------	 ---------
	def executeCMDonNVR(self, data, cameraKey,	cmdType="put"):
		return

		try:
			if cameraKey !="":
				url = "https://"+self.ipNumbersOf["VD"]+ ":7443/api/2.0/camera/"+ cameraKey+ "?apiKey=" + self.nvrVIDEOapiKey

			else:
				url = "https://"+self.ipNumbersOf["VD"]+ ":7443/api/2.0/camera/"+"?apiKey=" + self.nvrVIDEOapiKey

			if self.requestOrcurl.find("curl") > -1:
				cmdL  = self.curlPath+" --max-time {:.0f}".format(self.requestTimeout)+" --insecure -c /tmp/nvrCookie --data '"+json.dumps({"username":self.connectParams["UserID"]["nvrWeb"],"password":self.connectParams["PassWd"]["nvrWeb"]})+"' 'https://"+self.ipNumbersOf["VD"]+":7443/api/login'"
				if data =={} or data =="": dataDict = ""
				else:					   dataDict = " --data '"+json.dumps(data)+"' "
				if	 cmdType == "put":	  cmdTypeUse= " -X PUT "
				elif cmdType == "post":  cmdTypeUse= " -X post "
				elif cmdType == "get":	  cmdTypeUse= "     "
				else:					  cmdTypeUse= " "
				cmdR = self.curlPath+" --max-time {:.0f}".format(self.requestTimeout)+" --insecure -b /tmp/nvrCookie  --header \"Content-Type: application/json\" "+cmdTypeUse +  dataDict + "'" +url+ "'"

				try:
					try:
						if time.time() - self.lastNVRCookie > 100: # re-login every 90 secs
							if self.decideMyLog("Video"): self.indiLOG.log(10,"Video cmd "+ cmdL )
							ret, err = self.readPopen(cmdL)

							if err.find("error") >-1:
								self.indiLOG.log(40,"error: (wrong UID/passwd, ip number?) ...>>{}<<\n{}<< Video error".format(ret, err))
								return {}
							self.lastNVRCookie =time.time()
					except	Exception as e:
						if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)


					try:
						if self.decideMyLog("Video"): self.indiLOG.log(10,"Video {}".format(cmdR) )
						ret, err = self.readPopen(cmdR)
						try:
							jj = json.loads(ret)
						except :
							self.indiLOG.log(10,"UNIFI Video error  executeCMDonNVR has error, no json object returned: {} \n{}".format(ret, err) )
							return []
						if "rc" in jj["meta"] and "{}".format(jj["meta"]["rc"]).find("error")>-1:
							self.indiLOG.log(40,"error: data:>>{}<<\n>>{}<<\n" +" UNIFI Video error".format(ret, err))
							return []
						elif self.decideMyLog("Video"):
							self.indiLOG.log(10,"UNIFI Video executeCMDonNV- camera Data:\n" +json.dumps(jj["data"], sort_keys=True, indent=2) )

						return jj["data"]
					except	Exception as e:
						if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
				except	Exception as e:
					if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)


			#############does not work on OSX  el capitan ssl lib too old  ##########
			elif self.requestOrcurl =="requests":
				if self.unifiNVRSession =="" or (time.time() - self.lastNVRCookie) > 300:
					self.unifiNVRSession  = requests.Session()
					urlLogin  = "https://"+self.ipNumbersOf["VD"]+":7443/api/login"
					dataLogin = json.dumps({"username":self.connectParams["UserID"]["nvrWeb"],"password":self.connectParams["PassWd"]["nvrWeb"]})
					resp  = self.unifiNVRSession.post(urlLogin, data = dataLogin, verify=False)
					self.lastNVRCookie =time.time()


				if data == {}: dataDict = ""
				else:		   dataDict = json.dumps(data)

				if self.decideMyLog("Video"): self.indiLOG.log(10,"Video executeCMDonNVR  cmdType: "+cmdType+";  url: "+url +";  dataDict: "+ dataDict+"<<")
				try:
						if	 cmdType == "put":	 resp = self.unifiNVRSession.put(url,data  = dataDict, headers={'content-type': 'application/json'})
						elif cmdType == "post": resp = self.unifiNVRSession.post(url,data = dataDict, headers={'content-type': 'application/json'})
						elif cmdType == "get":	 resp = self.unifiNVRSession.get(url,data  = dataDict)
						else:					 resp = self.unifiNVRSession.get(url,data  = dataDict)
						response = resp.text.decode("utf8")
						jj = json.loads(response)
						if "rc" in jj["meta"] and "{}".format(jj["meta"]["rc"]).find("error") >-1:
							self.indiLOG.log(40,"executeCMDonNVR requests error: >>{}<<>>{}".format(resp.status_code, response) )
							return []
						elif self.decideMyLog("Video"):
							self.indiLOG.log(10,"Video executeCMDonNVR requests {}".format(response) )
						return jj["data"]
				except	Exception as e:
					if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)


		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return []



	####-----------------  VBOX ACTIONS	  ---------
	def execVboxAction(self,action,action2=""):
		return
		testCMD = "ps -ef | grep '/vboxAction.py ' | grep -v grep"
		ret, err = self.readPopen(testCMD)

		if len(ret) > 10:
			try:   self.indiLOG.log(10,"CameraInfo VBOXAction: still runing, not executing: {}  {}".format(action, action2) )
			except:self.indiLOG.log(10,"CameraInfo VBOXAction: still runing, not executing: ")
			return False
		cmd = self.pythonPath + " \"" + self.pathToPlugin + "vboxAction.py\" '"+action+"'"
		if action2 !="":
			cmd += " '"+action2+"'"
		cmd +=" &"
		if self.decideMyLog("Video"): self.indiLOG.log(10,"CameraInfo  VBOXAction: "+cmd )
		ret, err = self.readPopen(cmd)
		return

	####-----------------  Stop   ---------
	def buttonVboxActionStopCALLBACKaction(self, action1=None):
		return
		self.buttonVboxActionStopCALLBACK(valuesDict= action1.props)
	def buttonVboxActionStopCALLBACK(self, valuesDict=None, typeId="", devId=""):
		return
		cmd = json.dumps({"action":["stop"], "vmMachine":self.vmMachine, "vboxPath":self.vboxPath, "logfile":self.PluginLogFile})
		if not self.execVboxAction(cmd): return
		ip = self.ipNumbersOf["VD"]
		for dev in indigo.devices.iter("props.isUniFi"):
			if ip == dev.states["ipNumber"]:
				self.setSuspend(ip,time.time()+1000000000)
				break
		return valuesDict


	####-----------------  Start	---------
	def buttonVboxActionStartCALLBACKaction(self, action1=None):
		return
		self.buttonVboxActionStartCALLBACK(valuesDict= action1.props)
	def buttonVboxActionStartCALLBACK(self, valuesDict=None, typeId="", devId=""):
		return
		cmd = {"action":["start","mountDisk"], "vmMachine":self.vmMachine, "vboxPath":self.vboxPath, "logfile":self.PluginLogFile,"vmDisk":self.vmDisk }
		mountCmd  = self.buttonMountOSXDriveOnVboxCALLBACK(returnCmd=True)
		self.execVboxAction(json.dumps(cmd),action2=json.dumps(mountCmd))
		return valuesDict

	####-----------------  compress   ---------
	def buttonVboxActionCompressCALLBACKaction(self, action1=None):
		return
		self.buttonVboxActionCompressCALLBACK(valuesDict= action1.props)
	def buttonVboxActionCompressCALLBACK(self, valuesDict=None, typeId="", devId=""):
		return
		cmd = {"action":["stop","compress","start","mountDisk"], "vmMachine":self.vmMachine, "vboxPath":self.vboxPath, "logfile":self.PluginLogFile,"vmDisk":self.vmDisk }
		mountCmd  = self.buttonMountOSXDriveOnVboxCALLBACK(returnCmd=True)
		if not self.execVboxAction(json.dumps(cmd),action2=json.dumps(mountCmd)): return
		ip = self.ipNumbersOf["VD"]
		for dev in indigo.devices.iter("props.isUniFi"):
			if ip == dev.states["ipNumber"]:
				self.setSuspend(ip, time.time()+300.)
				break
		return valuesDict

	####-----------------  backup	 ---------
	def buttonVboxActionBackupCALLBACKaction(self, action1=None):
		return
		self.buttonVboxActionBackupCALLBACK(valuesDict= action1.props)
	def buttonVboxActionBackupCALLBACK(self, valuesDict=None, typeId="", devId=""):
		return
		cmd = {"action":["stop","backup","start","mountDisk"], "vmMachine":self.vmMachine, "vboxPath":self.vboxPath, "logfile":self.PluginLogFile,"vmDisk":self.vmDisk }
		mountCmd  = self.buttonMountOSXDriveOnVboxCALLBACK(returnCmd=True)
		if not self.execVboxAction(json.dumps(cmd),action2=json.dumps(mountCmd)): return
		ip = self.ipNumbersOf["VD"]
		for dev in indigo.devices.iter("props.isUniFi"):
			if ip == dev.states["ipNumber"]:
				self.setSuspend(ip, time.time()+220.)
				break
		return valuesDict


	####-----------------  	---------
	def checkIfPrintProcessingTime(self):
		if "today" 		not in self.waitTimes: return 
		if "lastPrint"	not in self.waitTimes["today"]: return 

		if time.time() - self.waitTimes["today"]["lastPrint"] > 6*60*60:
			self.buttonPrintWaitStatsCALLBACK(hourlyReport=True)
			self.waitTimes["today"]["lastPrint"] = time.time() 

		#reset at midnight
		if  datetime.datetime.now().hour == 0 and  datetime.datetime.now().minute == 0:
			if time.time() - self.waitTimes["today"]["startTime"] > 65:
				self.buttonZeroWaitStatsCALLBACK()


	####-----------------  ---------
	def buttonZeroWaitStatsCALLBACK(self, valuesDict=None, typeId="", devId=""):
		self.waitTimes["yesterday"] = copy.copy(self.waitTimes["today"] ) 
		self.waitTimes["today"] = {}
		self.saveDataStats(force=True)
		return valuesDict


	####-----------------  data stats menu items	---------
	def buttonPrintWaitStatsCALLBACK(self, valuesDict=None, typeId="", devId="",hourlyReport= False):
		try:
			if "yesterday" not in self.waitTimes: return 
			trailer  = "================================================ END ================================================"
			out = "\n"
			for dd in ["today", "yesterday"]:
				if dd not in self.waitTimes:				continue
				if "startDate" not in self.waitTimes[dd]:	continue
				if self.waitTimes[dd]["startDate"] == "":	continue
				out += "Wait times[secs] during processing of incoming data,  from {} to {} - {}\n".format(self.waitTimes[dd]["startDate"], self.waitTimes[dd]["endDate"], dd)
				for waitORbusy in ["Waiting", "Blocking"]:
					ytag = waitORbusy+"Pgm"
					out += "Pgm Module {:8}--- nMeasuremts  Tot{:4}Time  Ave{:4}   >.1  >.5   >1   >3   >6  >12  >20  maxWait\n".format(waitORbusy,waitORbusy[:4],waitORbusy[:4])
					for tag in sorted(self.waitTimes[dd][ytag]):
						if tag == "---TOTAL----": continue
						xx = self.waitTimes[dd][ytag][tag]
						avWait = xx["tot"] / max(1, xx["n"])
						out += "{:21s}  {:11}{:13.3f}  {:7.3f} {:5}{:5}{:5}{:5}{:5}{:5}{:5} {:8.1f}\n".format(tag, xx["n"], xx["tot"], avWait, xx[".1"], xx[".5"], xx["1"], xx["3"], xx["6"], xx["12"],xx["20"], xx["max"]  )

					tag = "---TOTAL----"
					xx = self.waitTimes[dd][ytag][tag]
					avWait = xx["tot"] / max(1, xx["n"])
					out += "{:21s}  {:11}{:13.3f}  {:7.3f} {:5}{:5}{:5}{:5}{:5}{:5}{:5} {:8.1f}\n".format(tag, xx["n"], xx["tot"], avWait, xx[".1"], xx[".5"], xx["1"], xx["3"], xx["6"], xx["12"],xx["20"], xx["max"]  )
				out += "N-pgms Blocking > 1={}, max blocking pgms={} (several pgms waiting in sequence)\n\n".format(self.waitTimes[dd]["QlenGT1"], self.waitTimes[dd]["QlenMax"] )

			if hourlyReport:
				self.indiLOG.log(10, out+trailer)
			else:
				self.indiLOG.log(20, out+trailer)

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		return valuesDict


	####-----------------  data stats menu items	---------
	def buttonPrintStatsCALLBACK(self, valuesDict=None, typeId="", devId=""):
		self.buttonPrintTcpipStats()
		self.printUpdateStats()
		valuesDict["MSG"] = "check logfile for output"
		return valuesDict


	####-----------------	 ---------
	def buttonPrintTcpipStats(self):

		try:
			if len(self.dataStats["tcpip"]) == 0: return
			nMin	= 0
			nSecs	= 0
			totByte = 0
			totMsg	= 0
			totErr	= 0
			totRes	= 0
			totAli	= 0
			out		= ""
			out = "\n"
			for uType in sorted(self.dataStats["tcpip"].keys()):
				for ipNumber in sorted(self.dataStats["tcpip"][uType].keys()):
					if nSecs ==0:
						out += "\n=== data stats for received messages ====     collection started at {}".format( time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.dataStats["tcpip"][uType][ipNumber]["startTime"])) )
						out += "\ndev type         ipNumber            msgcount;     msgBytes;  errCount;  restarts;aliveCount;   msg/min; bytes/min;   err/min; aliveC/min"
					nSecs = time.time() - self.dataStats["tcpip"][uType][ipNumber]["startTime"]
					nMin  = nSecs/60.
					outx = ipNumber.ljust(18)
					outx += "{:10d};".format(self.dataStats["tcpip"][uType][ipNumber]["inMessageCount"])
					outx += "{:13d};".format(self.dataStats["tcpip"][uType][ipNumber]["inMessageBytes"])
					outx += "{:10d};".format(self.dataStats["tcpip"][uType][ipNumber]["inErrorCount"])
					outx += "{:10d};".format(self.dataStats["tcpip"][uType][ipNumber]["restarts"])
					outx += "{:10d};".format(self.dataStats["tcpip"][uType][ipNumber]["aliveTestCount"]) 
					outx += "{:10.3f};".format(self.dataStats["tcpip"][uType][ipNumber]["inMessageCount"]/nMin) 
					outx += "{:10.1f};".format(self.dataStats["tcpip"][uType][ipNumber]["inMessageBytes"]/nMin)
					outx += "{:10.7f};".format(self.dataStats["tcpip"][uType][ipNumber]["inErrorCount"]/nMin)
					outx += "{:10.3f};".format(self.dataStats["tcpip"][uType][ipNumber]["aliveTestCount"]/nMin) 
					totByte += self.dataStats["tcpip"][uType][ipNumber]["inMessageBytes"]
					totMsg	+= self.dataStats["tcpip"][uType][ipNumber]["inMessageCount"]
					totErr	+= self.dataStats["tcpip"][uType][ipNumber]["inErrorCount"]
					totRes	+= self.dataStats["tcpip"][uType][ipNumber]["restarts"]
					totAli	+= self.dataStats["tcpip"][uType][ipNumber]["aliveTestCount"]

					out += "\n  {}-{:4s}    {}".format(uType, self.dataStats["tcpip"][uType][ipNumber]["APN"], outx)
			out += "\nT O T A L S            total       {:10d};{:13d};{:10d};{:10d};{:10d};{:10.3f};{:10.1f};{:10.7f};{:10.3f}".format(totMsg, totByte, totErr, totRes, totAli, totMsg/nMin, totByte/nMin, totErr/nMin, totAli/nMin)
			out += "\ndata stats === END===  total time measured: {:10.0f}[s] = {:s} ".format( nSecs/(24*60*60) ,time.strftime("%H:%M:%S", time.gmtime(nSecs)) ) 
			self.indiLOG.log(20, out )
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return


	####-----------------	 ---------
	def printUpdateStats(self):
		try:
			if len(self.dataStats["updates"]) == 0: return
			nSecs = max(1,(time.time()-	 self.dataStats["updates"]["startTime"]))
			nMin  = nSecs/60.
			out = "\n"
			out +="\nindigo update stats === ===  measuring started at: {}" .format( time.strftime("%H:%M:%S",time.localtime(self.dataStats["updates"]["startTime"])) )
			out +="\n     device updates:         {:10d};     updates/sec: {:10.2f};  updates/minute: {:10.2f}".format( self.dataStats["updates"]["devs"],   self.dataStats["updates"]["devs"]  /nMin, self.dataStats["updates"]["devs"]  /nSecs )
			out +="\n     device updates:         {:10d};     updates/sec: {:10.2f};  updates/minute: {:10.2f}".format( self.dataStats["updates"]["states"], self.dataStats["updates"]["states"]/nMin, self.dataStats["updates"]["states"]/nSecs )
			out +="\nindigo update stats === END===  total time measured: {:10.0f}[s] = {:s}".format( nSecs/(24*60*60), time.strftime("%H:%M:%S", time.gmtime(nSecs)) )
			self.indiLOG.log(20,out)
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return


	####-----------------	 ---------
	def addToMenuXML(self, valuesDict):
		if valuesDict:
			for item in valuesDict:
				self.menuXML[item] = copy.copy(valuesDict[item])
			self.pluginPrefs["menuXML"]	 = json.dumps(self.menuXML)
		return

	####-----------------	 ---------
	def buttonprintNVRCameraEventsCALLBACK(self,valuesDict, typeId="", devId=""):
		maxEvents= int(valuesDict["maxEvents"])
		totEvents= 0
		for MAC in self.cameras:
			totEvents += len(self.cameras[MAC]["events"])

		self.addToMenuXML(valuesDict)

		out = "\n======= Camera Events ======"
		out += "\nDev MAC             dev.id        Name "
		out += "\n           Ev#    start                   end        dur[secs]\n"
		for MAC in self.cameras:
			out += MAC+" {:11d} {}  # events total: {}\n".format(self.cameras[MAC]["devid"], self.cameras[MAC]["cameraName"].ljust(25), len(self.cameras[MAC]["events"]))
			evList=[]
			for evNo in self.cameras[MAC]["events"]:
				dateStart = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(self.cameras[MAC]["events"][evNo]["start"]))
				dateStop  = time.strftime(" .. %H:%M:%S",time.localtime(self.cameras[MAC]["events"][evNo]["stop"]))
				delta  = self.cameras[MAC]["events"][evNo]["stop"]
				delta -= self.cameras[MAC]["events"][evNo]["start"]
				evList.append("     {}".format(evNo).rjust(10)+"  {:}  {:8.1f}\n".format(dateStart+dateStop, delta))
			evList= sorted(evList, reverse=True)
			count =0
			for o in evList:
				count+=1
				if count > maxEvents: break
				out += o
		out += "====== Camera Events ======;                         all # events total: " +"{}".format(totEvents) +"\n"

		self.indiLOG.log(20,out )
		return valuesDict

	####-----------------	 ---------
	def buttonresetNVRCameraEventsCALLBACK(self,valuesDict, typeId="", devId=""):
		for dev in indigo.devices.iter("props.isCamera"):
			dev.updateStateOnServer("eventNumber",0)
			self.indiLOG.log(10,"reset event number for {}".format(dev.name) )
		self.resetCamerasStats()
		self.addToMenuXML(valuesDict)
		return valuesDict
	####-----------------	 ---------


	####-----------------	 ---------
	def buttonPrintNVRCameraSystemCALLBACK(self,valuesDict, typeId="", devId=""):
		if self.cameraSystem == "nvr":
			self.pendingCommand.append("getNVRCamerasFromMongoDB-print")
		elif self.cameraSystem == "protect":
			self.pendingCommand.append("getProtectamerasInfo-print")
		return valuesDict

	####-----------------	 ---------
	def buttonrefreshNVRCameraSystemCALLBACK(self,valuesDict, typeId="", devId=""):
		if self.cameraSystem == "nvr":
			self.pendingCommand.append("getConfigFromNVR")
		elif self.cameraSystem == "protect":
			self.pendingCommand.append("getConfigFromProtect")
		return valuesDict

	####-----------------	 ---------
	def getMongoData(self, cmdstr, uType="VDdict"):
		ret =["",""]
		try:
			userid, passwd =  self.getUidPasswd(uType,self.ipNumbersOf["VD"])
			if userid == "": return {}

			cmd = self.expectPath  +" "
			cmd += "'" + self.pathToPlugin + self.connectParams["expectCmdFile"][uType] + "' " 
			cmd += "'" + userid + "' '"+passwd + "' " 
			cmd += self.ipNumbersOf["VD"] + " " 
			cmd += "'" + self.escapeExpect(self.connectParams["promptOnServer"][self.ipNumbersOf["VD"]]) + "' " 
			cmd += " XXXXsepXXXXX " 
			cmd += cmdstr
			cmd +=  self.getHostFileCheck()

			if self.decideMyLog("Expect"): self.indiLOG.log(10,"UNIFI getMongoData cmd " +cmd )
			ret, err = self.readPopen(cmd)
			dbJson, error= self.makeJson(ret, "XXXXsepXXXXX")
			if self.decideMyLog("Video"): self.indiLOG.log(10,"UNIFI getMongoData return {}\n{}".format(ret, err) )
			if error !="":
				self.indiLOG.log(40,"getMongoData camera system (dump, no json conversion)	info:\n>>{}    {}<<\n>>{}".format(error, cmd, ret) )
				return []
			return	dbJson
		except	Exception as e:
			if "{}".format(e).find("None") == -1:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
				if self.decideMyLog("Video"): self.indiLOG.log(40," getMongoData error: {}\n{}".format(ret[0], ret[1]))
		return []

	####-----------------	 ---------
	def makeJson(self, dumpIN, sep):  ## {} separated by \n
		try:
			out =[]
			temp = "empty"
			temp2 = "empty"
			begStr,endStr ="{","}"
			dump		 = dumpIN.split(sep)
			lDump = len(dump)
			if lDump <3: return "","error len(split):{}".format(lDump)
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
						self.indiLOG.log(40,"makeJson error , trying to fix:\ntemp2>>>>>{}".format(temp2)+"<<<<<\n>>>>{}".format(dumpIN)+"<<<<<" )
						try:
							o=json.loads(temp2+"}")
							out.append(o)
							self.indiLOG.log(40,"makeJson error fixed " )
						except	Exception as e:
							if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

			return out, ""
		except	Exception as e:
			if "{}".format(e).find("None") == -1:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
				self.indiLOG.log(40,"makeJson error :\ndump>>>>{}".format(dumpIN)+"<<<<<" )
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
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

	####-----------------	 ---------
	def replaceFunc(self, dump):
		try:
			for ii in range(500):  # remove binData(xxxxx)
				nn = dump.find("BinData(")
				if nn ==-1: break
				endst = dump[nn:].find(")")
				dump = dump[0:nn-1]+'"xxx"'+ dump[nn+endst+1:]

			for kk in range(1000):	# loop over func Names, max 30
				ss = 0
				for ll in range(100): # remove " (xxx) from targest only abc(xx)
					nn = dump[ss:].find("(")
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
					pp = dump[nn:].find(")")
					dump = dump[0:nn] + dump[nn+lenrepString:nn+pp] + dump[nn+pp+1:]
			return dump
		except	Exception as e:
			if "{}".format(e).find("None") == -1:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return ""

	####-----------------	 ---------
	def buttonZeroStatsCALLBACK(self, valuesDict=None, typeId="", devId=""):
		self.zeroDataStats()
		return valuesDict
	####-----------------	 ---------
	def buttonResetStatsCALLBACK(self, valuesDict=None, typeId="", devId=""):
		self.resetDataStats(calledFrom="buttonResetStatsCALLBACK")
		return valuesDict

	####-----------------  reboot unifi device	 ---------

	####-----------------	 ---------
	def filterUnifiDevices(self, filter="", valuesDict=None, typeId="", targetId=""):
		xlist = []
		for ll in range(_GlobalConst_numberOfAP):
			if self.devsEnabled["AP"][ll]:
				xlist.append((self.ipNumbersOf["AP"][ll]+"-APdict","AP -"+self.ipNumbersOf["AP"][ll]))
		for ll in range(_GlobalConst_numberOfSW):
			if self.devsEnabled["SW"][ll]:
				xlist.append((self.ipNumbersOf["SW"][ll]+"-SWtail","SW -"+self.ipNumbersOf["SW"][ll]))
		if self.devsEnabled["GW"]:
				xlist.append((self.ipNumbersOf["GW"]+"-GWtail","GW -"+self.ipNumbersOf["GW"]))
		return xlist

	####-----------------	 ---------
	def buttonConfirmrebootCALLBACKaction(self, action1=None):
		return self.buttonConfirmrebootCALLBACK(valuesDict=action1.props)

	####-----------------	 ---------
	def buttonConfirmrebootCALLBACK(self, valuesDict=None, typeId="", devId=""):
		ip_type	 =	valuesDict["rebootUNIFIdeviceSelected"].split("-")
		ipNumber = ip_type[0]
		dtype	 = ip_type[1] # not used
		uType 	 = "unixDevs"
		cmd = self.expectPath +" "
		cmd+= "'"+self.pathToPlugin + "rebootUNIFIdeviceAP.exp" + "' "
		cmd+= "'"+self.connectParams["UserID"][uType] + "' '"+self.connectParams["PassWd"][uType] + "' "
		cmd+= ipNumber + " "
		cmd+= "'"+self.escapeExpect(self.connectParams["promptOnServer"][ipNumber]) + "' "
		cmd +=  self.getHostFileCheck()
		cmd +=   " &"
		if self.decideMyLog("Expect"): self.indiLOG.log(10,"REBOOT: "+cmd )
		ret, err = self.readPopen(cmd)
		if self.decideMyLog("ExpectRET"): self.indiLOG.log(10,"REBOOT returned: {}-{}".format(ret, err) )
		self.addToMenuXML(valuesDict)

		return valuesDict


	####-----------------  set properties for all devices	---------
	def buttonConfirmSetWifiOptCALLBACK(self, valuesDict=None, typeId="", devId=""):
		for MAC in self.MAC2INDIGO["UN"]:
			try:
				dev = indigo.devices[self.MAC2INDIGO["UN"][MAC]["devId"]]
				props = dev.pluginProps
				self.indiLOG.log(10,"doing {}".format(dev.name) )
				if props["useWhatForStatus"].find("WiFi") > -1:
					props["useWhatForStatusWiFi"]	= "Optimized"
					props["idleTimeMaxSecs"]		= "30"
					dev.replacePluginPropsOnServer(props)

					dev = indigo.devices[self.MAC2INDIGO["UN"][MAC]["devId"]]
					props = dev.pluginProps
					self.indiLOG.log(10,"done  {}  {} ".format(dev.name, "{}".format(props)) )
			except	Exception as e:
					if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		self.printALLUNIFIsreduced()
		return valuesDict
	####-----------------	 ---------
	def buttonConfirmSetWifiIdleCALLBACK(self, valuesDict=None, typeId="", devId=""):
		for MAC in self.MAC2INDIGO["UN"]:
			try:
				dev = indigo.devices[self.MAC2INDIGO["UN"][MAC]["devId"]]
				props = dev.pluginProps
				if props["useWhatForStatus"].find("WiFi") > -1:
					props["useWhatForStatusWiFi"]	= "IdleTime"
					props["idleTimeMaxSecs"]		= "30"
					dev.replacePluginPropsOnServer(props)
			except:
				pass
		self.printALLUNIFIsreduced()
		return valuesDict
	####-----------------	 ---------
	def buttonConfirmSetWifiUptimeCALLBACK(self, valuesDict=None, typeId="", devId=""):
		for MAC in self.MAC2INDIGO["UN"]:
			try:
				dev = indigo.devices[self.MAC2INDIGO["UN"][MAC]["devId"]]
				props = dev.pluginProps
				if props["useWhatForStatus"].find("WiFi") > -1:
					props["useWhatForStatusWiFi"]	= "UpTime"
					dev.replacePluginPropsOnServer(props)
			except:
				pass
		self.printALLUNIFIsreduced()
		return valuesDict
	####-----------------	 ---------
	def buttonConfirmSetNonWifiOptCALLBACK(self, valuesDict=None, typeId="", devId=""):
		for MAC in self.MAC2INDIGO["UN"]:
			try:
				dev = indigo.devices[self.MAC2INDIGO["UN"][MAC]["devId"]]
				props = dev.pluginProps
				if props["useWhatForStatus"].find("WiFi") == -1:
					props["useWhatForStatus"]			= "OptDhcpSwitch"
					props["useAgeforStatusDHCP"]		= "60"
					props["useupTimeforStatusSWITCH"]	= True
					dev.replacePluginPropsOnServer(props)
			except:
				pass
		self.printALLUNIFIsreduced()
		return valuesDict
	####-----------------	 ---------
	def buttonConfirmSetNonWifiToSwitchCALLBACK(self, valuesDict=None, typeId="", devId=""):
		for MAC in self.MAC2INDIGO["UN"]:
			try:
				dev = indigo.devices[self.MAC2INDIGO["UN"][MAC]["devId"]]
				props = dev.pluginProps
				if props["useWhatForStatus"].find("WiFi") == -1:
					props["useWhatForStatus"]			= "SWITCH"
					props["useupTimeforStatusSWITCH"]	= True
					dev.replacePluginPropsOnServer(props)
			except:
				pass
		self.printALLUNIFIsreduced()
		return valuesDict

	####-----------------	 ---------
	def buttonConfirmSetNonWifiToDHCPCALLBACK(self, valuesDict=None, typeId="", devId=""):
		for MAC in self.MAC2INDIGO["UN"]:
			try:
				dev = indigo.devices[self.MAC2INDIGO["UN"][MAC]["devId"]]
				props = dev.pluginProps
				if props["useWhatForStatus"].find("WiFi") == -1:
					props["useWhatForStatus"]			= "DHCP"
					props["useAgeforStatusDHCP"]		= "60"
					dev.replacePluginPropsOnServer(props)
			except:
				pass
		self.printALLUNIFIsreduced()
		return valuesDict

	####-----------------	 ---------
	def buttonConfirmSetUsePingUPonCALLBACK(self, valuesDict=None, typeId="", devId=""):
		for MAC in self.MAC2INDIGO["UN"]:
			try:
				dev = indigo.devices[self.MAC2INDIGO["UN"][MAC]["devId"]]
				props = dev.pluginProps
				props["usePingUP"]			 = True
				dev.replacePluginPropsOnServer(props)
			except:
				pass
		self.printALLUNIFIsreduced()
		return valuesDict

	####-----------------	 ---------
	def buttonConfirmSetUsePingUPoffCALLBACK(self, valuesDict=None, typeId="", devId=""):
		for MAC in self.MAC2INDIGO["UN"]:
			try:
				dev = indigo.devices[self.MAC2INDIGO["UN"][MAC]["devId"]]
				props = dev.pluginProps
				props["usePingUP"]			 = False
				dev.replacePluginPropsOnServer(props)
			except:
				pass
		self.printALLUNIFIsreduced()
		return valuesDict

	####-----------------	 ---------
	def buttonConfirmSetUsePingDOWNonCALLBACK(self, valuesDict=None, typeId="", devId=""):
		for MAC in self.MAC2INDIGO["UN"]:
			try:
				dev = indigo.devices[self.MAC2INDIGO["UN"][MAC]["devId"]]
				props = dev.pluginProps
				props["usePingDOWN"]		   = True
				dev.replacePluginPropsOnServer(props)
			except:
				pass
		self.printALLUNIFIsreduced()
		return valuesDict

	####-----------------	 ---------
	def buttonConfirmSetUsePingDOWNoffCALLBACK(self, valuesDict=None, typeId="", devId=""):
		for MAC in self.MAC2INDIGO["UN"]:
			try:
				dev = indigo.devices[self.MAC2INDIGO["UN"][MAC]["devId"]]
				props = dev.pluginProps
				props["usePingDOWN"]		   = False
				dev.replacePluginPropsOnServer(props)
			except:
				pass
		self.printALLUNIFIsreduced()
		return valuesDict

	####-----------------	 ---------
	def buttonConfirmSetExpTimeCALLBACK(self, valuesDict=None, typeId="", devId=""):
		for MAC in self.MAC2INDIGO["UN"]:
			try:
				dev = indigo.devices[self.MAC2INDIGO["UN"][MAC]["devId"]]
				props = dev.pluginProps
				props["expirationTime"]			  =int(valuesDict["expirationTime"])
				dev.replacePluginPropsOnServer(props)
			except:
				pass
		self.printALLUNIFIsreduced()
		return valuesDict

	####-----------------	 ---------
	def buttonConfirmSetExpTimeMinCALLBACK(self, valuesDict=None, typeId="", devId=""):
		for MAC in self.MAC2INDIGO["UN"]:
			try:
				dev = indigo.devices[self.MAC2INDIGO["UN"][MAC]["devId"]]
				props = dev.pluginProps
				try:
					if int(props["expirationTime"]) < int(valuesDict["expirationTime"]):
						props["expirationTime"]		= int(valuesDict["expirationTime"])
				except:
					props["expirationTime"]			= int(valuesDict["expirationTime"])
				dev.replacePluginPropsOnServer(props)
			except:
				pass
		self.printALLUNIFIsreduced()
		return valuesDict


	####-----------------	 ---------
	def inpDummy(self, valuesDict=None, typeId="", devId=""):
		return valuesDict

	####-----------------  filter	---------


	####-----------------	 ---------
	def filterWiFiDevice(self, filter="", valuesDict=None, typeId="", targetId=""):

		xList = []
		for dev in indigo.devices.iter("props.isUniFi"):
			if "AP" not	 in dev.states:		  continue
			if len(dev.states["AP"]) < 5:	  continue
			xList.append([dev.states["MAC"].lower(),dev.name+"--"+ dev.states["MAC"] +"-- AP:"+dev.states["AP"]])
		return sorted(xList, key=lambda x: x[1])

	####-----------------	 ---------
	def filterUNIFIsystemDevice(self, filter="", valuesDict=None, typeId="", targetId=""):

		xList = []
		for dev in indigo.devices.iter("props.isSwitch,props.isGateway,props.isAP"):
			xList.append([dev.states["MAC"].lower(),dev.name+"--"+ dev.states["MAC"] ])
		return sorted(xList, key=lambda x: x[1])
	####-----------------	 ---------
	def filterCameraDevice(self, filter="", valuesDict=None, typeId="", targetId=""):

		xList = []
		if self.cameraSystem == "nvr":	
			for dev in indigo.devices.iter("props.isCamera"):
				xList.append([dev.id,dev.name])
		if self.cameraSystem == "protect":	
			for dev in indigo.devices.iter("props.isProtectCamera"):
				for camId in self.PROTECT:
					if dev.id == self.PROTECT[camId]["devId"]:
						xList.append([dev.id,dev.name])
						break
		return sorted(xList, key=lambda x: x[1])


	####-----------------	 ---------
	def filterUNIFIsystemDeviceSuspend(self, filter="", valuesDict=None, typeId="", targetId=""):

		xList = []
		for dev in indigo.devices.iter("props.isSwitch,props.isGateway,props.isAP"):
			xList.append([dev.id,dev.name])
		return sorted(xList, key=lambda x: x[1])

	####-----------------	 ---------
	def filterUNIFIsystemDeviceSuspended(self, filter="", valuesDict=None, typeId="", targetId=""):

		xList = []
		for dev in indigo.devices.iter("props.isSwitch,props.isGateway,props.isAP"):
			xList.append([dev.id,dev.name])
		return sorted(xList, key=lambda x: x[1])

	####-----------------	 ---------
	def filterAPdevices(self, filter="", valuesDict=None, typeId="", targetId=""):

		xList = []
		for dev in indigo.devices.iter("props.isAP"):
			xList.append([dev.id,dev.name])
		return sorted(xList, key=lambda x: x[1])



	####-----------------	 ---------
	def filterMACNoIgnored(self, filter="", valuesDict=None, typeId="", targetId=""):
		xlist = []
		for dev in indigo.devices.iter(self.pluginId):
			if "MAC" in dev.states:
				if "displayStatus" in dev.states and   dev.states["displayStatus"].find("ignored") >-1: continue
				mac = dev.states["MAC"]
				if self.isValidMAC(mac):
					xlist.append([mac,dev.states["MAC"] + " - "+dev.name])
				else:
					xlist.append(["bad mac","badMAC#-"+dev.states["MAC"] + " - "+dev.name])
		return sorted(xlist, key=lambda x: x[1])

	####-----------------	 ---------
	def filterMAC(self, filter="", valuesDict=None, typeId="", targetId=""):
		xlist = []
		for dev in indigo.devices.iter(self.pluginId):
			if "MAC" in dev.states:
				mac = dev.states["MAC"]
				if len(mac) < 5: continue
				if self.isValidMAC(mac):
					xlist.append([dev.states["MAC"],dev.name+" - "+dev.states["MAC"]])
				else:
					xlist.append(["bad mac","badMAC#-"+dev.name+" - "+dev.states["MAC"]])
		return sorted(xlist, key=lambda x: x[1])

	####-----------------	 ---------
	def filterMACunifiOnly(self, filter="", valuesDict=None, typeId="", targetId=""):
		xlist = []
		for dev in indigo.devices.iter("props.isUniFi"):
			if "MAC" in dev.states:
				if len(dev.states["MAC"]) < 5: continue
				xlist.append([dev.states["MAC"],dev.name+"--"+dev.states["MAC"] ])
		return sorted(xlist, key=lambda x: x[1])

	####-----------------	 ---------
	def filterMACunifiAndCameraOnly(self, filter="", valuesDict=None, typeId="", targetId=""):
		xlist = []
		for dev in indigo.devices.iter("props.isUniFi"):
			if "MAC" in dev.states:
				if dev.deviceTypeId not in ["UniFi"] : continue
				if len(dev.states["MAC"]) < 5: continue
				if "status" in dev.states and dev.states["status"].find("up") >-1:
					xlist.append([dev.states["MAC"],dev.name+"--"+dev.states["MAC"] ])

		for dev in indigo.devices.iter("props.isCamera"):
			if "MAC" in dev.states:
				if dev.deviceTypeId not in ["camera"] : continue
				if dev.states["MAC"] in maclist: continue
				if len(dev.states["MAC"]) < 5: continue
				xlist.append([dev.states["MAC"],dev.name+"--"+dev.states["MAC"] ])

		self.indiLOG.log(20,f"filterMACunifiAndCameraOnly, xlist: {xlist:}")
		return sorted(xlist, key=lambda x: x[1])

	####-----------------	 ---------
	def filterMACunifiOnlyUP(self, filter="", valuesDict=None, typeId="", targetId=""):
		xlist = []
		for dev in indigo.devices.iter("props.isUniFi"):
			if "MAC" in dev.states:
				if "status" in dev.states and dev.states["status"].find("up") > -1:
					useMe = True
					for dev2 in indigo.devices.iter("props.isSwitch,props.isGateway,props.isAP,props.isCamera,props.isProtectCamera,props.NVR,props.isNeighbor"):
						if dev2.deviceTypeId == "UniFi": continue
						if dev2.id == dev.id: continue
						if dev2.states.get("MAC","y") == dev.states["MAC"]:
							useMe = False
							break
					if useMe:
						if len(dev.states["MAC"]) < 5: continue
						xlist.append([dev.states["MAC"],dev.name+"--"+dev.states["MAC"] ])

		return sorted(xlist, key=lambda x: x[1])

	####-----------------	 ---------
	def filterMAConlyAP(self, filter="", valuesDict=None, typeId="", targetId=""):
		xlist = []
		for dev in indigo.devices.iter("props.isAP"):
			if "MAC" in dev.states:
				if len(dev.states["MAC"]) < 5: continue
				if "status" in dev.states and dev.states["status"].find("up") >-1:
					xlist.append([dev.states["MAC"],dev.name+"--"+dev.states["MAC"] ])
		return sorted(xlist, key=lambda x: x[1])


	####-----------------	 ---------
	def filterMACunifiIgnored(self, filter="", valuesDict=None, typeId="", targetId=""):
		xlist = []
		for MAC in self.MACignorelist:
				if len(MAC) < 5: continue
				textMAC = MAC
				for dev in indigo.devices.iter("props.isUniFi,props.isCamera"):
					if "MAC" in dev.states and MAC == dev.states["MAC"]:
						textMAC = dev.name+" - "+MAC
						break
				xlist.append([MAC,textMAC])

		self.indiLOG.log(20,f"filterMACunifiIgnored, xlist: {xlist:}")
		return sorted(xlist, key=lambda x: x[1])

	####-----------------  logging for specific MAC number	 ---------
	####-----------------	 ---------
	def filterMACspecialUNIgnore(self, filter="", valuesDict=None, typeId="", targetId=""):
		xlist = []
		for MAC in self.MACSpecialIgnorelist:
			if len(dev.states["MAC"]) < 5: continue
			xlist.append([MAC,MAC])
		return sorted(xlist, key=lambda x: x[1])

	####-----------------  logging for specific MAC number	 ---------



	####-----------------	 ---------
	def buttonConfirmStartLoggingCALLBACK(self, valuesDict=None, typeId="", devId=""):
		self.MACloglist[valuesDict["MACdeviceSelected"]]=True
		self.indiLOG.log(10,"start track-logging for MAC# {}".format(valuesDict["MACdeviceSelected"]) )
		if valuesDict["keepMAClogList"] == "1":
			self.writeJson(self.MACloglist, fName=self.indigoPreferencesPluginDir+"MACloglist")
		else:
			self.writeJson({}, fName=self.indigoPreferencesPluginDir+"MACloglist")
		return valuesDict

	####-----------------	 ---------
	def buttonConfirmStopLoggingCALLBACK(self, valuesDict=None, typeId="", devId=""):
		self.MACloglist = {}
		self.writeJson({}, fName=self.indigoPreferencesPluginDir+"MACloglist")
		self.indiLOG.log(10," stop logging of MAC #s")
		return valuesDict

	####-----------------  device info	 ---------
	def buttonConfirmPrintMACCALLBACK(self, valuesDict=None, typeId="", devId=""):
		self.printMACs(MAC=valuesDict["MACdeviceSelected"])
		return valuesDict
	####-----------------	 ---------
	def buttonprintALLMACsCALLBACK(self, valuesDict=None, typeId="", devId=""):
		self.printALLMACs()
		return valuesDict
	####-----------------	 ---------
	def printALLUNIFIsreducedMenue(self, valuesDict=None, typeId="", devId=""):
		self.printALLUNIFIsreduced()
		return valuesDict
	####-----------------	 ---------




	####-----------------  GROUPS START	   ---------
	####-----------------	 ---------

	def printGroupsCALLBACK(self, valuesDict=None, typeId="", devId=""):
		self.printGroups()
		return valuesDict


	####-----------------  add devices to groups  menu	 ---------
	def buttonConfirmAddDevGroupCALLBACK(self, valuesDict=None, typeId="", devId=0):
		try:
			newGroup =	valuesDict["addRemoveGroupsWhichGroup"]
			devtypes =	valuesDict["addRemoveGroupsWhichDevice"]
			types	 =""; lanWifi = ""
			if	 devtypes == "system":	 types ="props.isGateway,props.isSwitch,props.isAP"
			elif devtypes == "neighbor": types ="props.isNeighbor"
			elif devtypes == "LAN":		 types ="props.isUniFi" ; lanWifi ="LAN"
			elif devtypes == "wifi":	 types ="props.isUniFi" ; lanWifi ="wifi"
			if types !="":
				for dev in indigo.devices.iter(types):
					if lanWifi == "wifi" and "AP" in dev.states:
						if ( dev.states["AP"] == "" or
							 dev.states["signalWiFi"]		== "" ): continue
					if lanWifi == "LAN" and "AP" in dev.states:
						if not	( dev.states["AP"] =="" or
								  dev.states["signalWiFi"]	== "" ): continue
					props = dev.pluginProps
					props[newGroup] = True
					gMembers = self.makeGroupMemberstring(props)
					self.updateDevStateGroupMembers(dev, gMembers)
					dev.replacePluginPropsOnServer(props)
				self.statusChanged = 1

		except	Exception as e:
			if "{}".format(e).find("None") == -1:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return valuesDict

	####-----------------	  ---------
	def updateDevStateGroupMembers(self, dev, gMembers, delay=False):
		if dev.states["groupMember"] != gMembers:
			if delay:
				self.addToStatesUpdateList(dev.id,"groupMember", gMembers)
			else:
				dev.updateStateOnServer("groupMember", gMembers)
		return

	####-----------------	  ---------
	def makeGroupMemberstring(self, inputDict):
		gMembers = ""
		for groupNo in range(_GlobalConst_numberOfGroups):
			group = "Group{}".format(groupNo)
			if group in inputDict and inputDict[group]:
				gMembers += self.groupNames[groupNo]+","
		return gMembers.strip(",")



	####-----------------  remove devices to groups	 menu	---------
	def buttonConfirmRemDevGroupCALLBACK(self, valuesDict=None, typeId="", devId=0):
		try:
			newGroup =	valuesDict["addRemoveGroupsWhichGroup"]
			devtypes =	valuesDict["addRemoveGroupsWhichDevice"]
			types	 = ""; lanWifi=""
			if	 devtypes == "system":	 types =",props.isGateway,props.isSwitch,props.isAP"
			elif devtypes == "neighbor": types =",props.isNeighbor"
			elif devtypes == "LAN":		 types =",props.isUniFi" ; lanWifi = "LAN"
			elif devtypes == "wifi":	 types =",props.isUniFi" ; lanWifi = "wifi"
			for dev in indigo.devices.iter(self.pluginId+types):
				if lanWifi == "wifi" and "AP" in dev.states:
					if ( dev.states["AP"] =="" or
						 dev.states["signalWiFi"]	  =="" ): continue
				if lanWifi == "LAN" and "AP" in dev.states:
					if not	( dev.states["AP"] == "" or
							  dev.states["signalWiFi"]	   =="" ): continue

				props = dev.pluginProps
				if newGroup in props:
					del props[newGroup]
				dev.replacePluginPropsOnServer(props)
				gMembers = self.makeGroupMemberstring(props)
				self.updateDevStateGroupMembers(dev, gMembers)

			self.statusChanged = 1
		except	Exception as e:
			if "{}".format(e).find("None") == -1:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return valuesDict


	####-----------------	 ---------
	def filterGroupNoName(self, filter="", valuesDict=None, typeId="", targetId=""):
		try:
			xList=[]
			for groupNo in range(_GlobalConst_numberOfGroups):
				members = self.groupStatusList[groupNo]["members"]
				gName = self.groupNames[groupNo] 
				xList.append(["Group{}".format(groupNo), gName])
		except	Exception as e:
			if "{}".format(e).find("None") == -1:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return xList
	####-----------------	 ---------
	def filterGroups(self, filter="", valuesDict=None, typeId="", targetId=""):
		try:
			xList=[]
			for groupNo in range(_GlobalConst_numberOfGroups):
				members = self.groupStatusList[groupNo]["members"]
				gName = self.groupNames[groupNo] 
				#try:
				#except: pass
				memberMAC = ""
				nn = 0
				for id in members:
					nn +=1
					if nn < 6:
						try:
							memberMAC = indigo.devices[int(id)].states["MAC"]
						except	Exception as e:
							if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
							continue
						memberMAC += memberMAC+";"
					elif nn == 6:
						memberMAC +="..."
				xList.append(["{}".format(groupNo), "{}= {}".format(gName, memberMAC.strip("; "))])
		except	Exception as e:
			if "{}".format(e).find("None") == -1:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return xList

	####-----------------	 ---------
	def buttonConfirmgroupCALLBACK(self, valuesDict=None, typeId="", devId=""):
		self.selectedGroup		  = int(valuesDict["selectedGroup"])
		return valuesDict

	####-----------------	 ---------
	def filterGroupMembers(self, filter="", valuesDict=None, typeId="", targetId=""):
		try:
			xList=[]
			try: groupNo = int(self.selectedGroup)
			except: return xList
			for memberDevID in self.groupStatusList[groupNo]["members"]:
				try:
					dev = indigo.devices[int(memberDevID)]
				except: continue
				xList.append([memberDevID,dev.name + "- "+ dev.states["MAC"]])
		except	Exception as e:
			if "{}".format(e).find("None") == -1:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return xList

	####-----------------	 ---------
	def buttonConfirmremoveGroupMemberCALLBACK(self, valuesDict=None, typeId="", devId=""):
		devIdOfGroupMember	= valuesDict["selectedGroupMemberIndigoIdremove"]
		try: groupNo = int(self.selectedGroup)
		except: return valuesDict
		groupPropsName = "Group{}".format(groupNo)
		try:
			dev = indigo.devices[int(devIdOfGroupMember)]
		except:
			self.indiLOG.log(30," bad dev id: {}".format(devIdOfGroupMember) )
			return
		props = dev.pluginProps
		if devIdOfGroupMember in self.groupStatusList[groupNo]["members"]:
			del self.groupStatusList[groupNo]["members"][devIdOfGroupMember]
		if groupPropsName in props and props[groupPropsName]:
			props[groupPropsName] = False
			gMembers = self.makeGroupMemberstring(props)
			self.updateDevStateGroupMembers(dev, gMembers)
			dev.replacePluginPropsOnServer(props)
		return valuesDict


	####-----------------	 ---------
	def buttonConfirmremoveALLGroupMembersCALLBACK(self, valuesDict=None, typeId="", devId=""):
		try: groupNo = int(self.selectedGroup)
		except: return valuesDict
		groupPropsName = "Group".format(groupNo)
		self.indiLOG.log(20," groupStatusList:{} removing all members".format(self.groupStatusList)  )
		self.groupStatusList[groupNo]["members"] = {}
		for dev in indigo.devices.iter(self.pluginId):
			props=dev.pluginProps
			if groupPropsName in props and props[groupPropsName]:
				props[groupPropsName] = False
				gMembers = self.makeGroupMemberstring(props)
				gMembers = self.makeGroupMemberstring(props)
				self.updateDevStateGroupMembers(dev, gMembers)
				dev.replacePluginPropsOnServer(props)

		return valuesDict



	####-----------------	 ---------
	def filterDevicesToAddToGroup(self, filter="", valuesDict=None, typeId="", targetId=""):
		try:
			xList=[]
			try: groupNo = int(self.selectedGroup)
			except: return xList
			for dev in indigo.devices.iter("props.isUniFi"):
				props = dev.pluginProps
				if "{}".format(dev.id) in  self.groupStatusList[groupNo]["members"]: continue
				xList.append(["{}".format(dev.id), dev.name + "- "+ dev.states["MAC"]])
		except	Exception as e:
			if "{}".format(e).find("None") == -1:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return xList

	####-----------------	 ---------
	def buttonConfirmADDGroupMemberCALLBACK(self, valuesDict=None, typeId="", targetId=""):
		devIdOfGroupMember	= valuesDict["selectedGroupMemberIndigoIdadd"]
		try: groupNo = int(self.selectedGroup)
		except: return valuesDict
		try:
			dev = indigo.devices[int(devIdOfGroupMember)]
		except:
			self.indiLOG.log(30," bad dev id: {}".format(devIdOfGroupMember) )
			return
		props = dev.pluginProps
		if devIdOfGroupMember not in self.groupStatusList[groupNo]["members"]:
			self.groupStatusList[groupNo]["members"][devIdOfGroupMember] = True
		props["Group{}".format(groupNo)] = True
		gMembers = self.makeGroupMemberstring(props)
		self.updateDevStateGroupMembers(dev, gMembers)
		dev.replacePluginPropsOnServer(props)
		return valuesDict



	####-----------------  GROUPS END	 ---------
	####-----------------	 ---------


	####-----------------  Ignore special MAC info	 ---------
	def buttonConfirmStartIgnoringSpecialMACCALLBACK(self, valuesDict=None, typeId="", devId=""):
		MAC = valuesDict["MACspecialIgnore"]
		if not self.isValidMAC(MAC):
			valuesDict["MSG"] = "bad MAC.. must be 12:xx:23:xx:45:aa"
			return valuesDict
		self.MACSpecialIgnorelist[valuesDict["MACspecialIgnore"]]=1
		self.indiLOG.log(10,"start ignoring  MAC# "+valuesDict["MACspecialIgnore"])
		self.saveMACdata(force=True)
		valuesDict["MSG"] = "ok"
		return valuesDict
	####-----------------  UN- Ignore special MAC info	 ---------
	####----------------- ---------
	def buttonConfirmStopIgnoringSpecialMACCALLBACK(self, valuesDict=None, typeId="", devId=""):

		try: del self.MACSpecialIgnorelist[valuesDict["MACspecialUNIgnored"]]
		except: pass
		self.indiLOG.log(10," stop ignoring  MAC# " +valuesDict["MACspecialUNIgnored"])
		self.saveMACdata(force=True)
		valuesDict["MSG"] = "ok"
		return valuesDict

	####-----------------  Ignore MAC info	 ---------
	def buttonConfirmStartIgnoringCALLBACK(self, valuesDict=None, typeId="", devId=""):
		self.MACignorelist[valuesDict["MACdeviceSelected"]]=1
		self.indiLOG.log(10,"start ignoring  MAC# "+valuesDict["MACdeviceSelected"])
		for dev in indigo.devices.iter("props.isUniFi,props.isCamera"):
			if "MAC" in dev.states	 and dev.states["MAC"] == valuesDict["MACdeviceSelected"]:
				if "displayStatus" in dev.states:
					dev.updateStateOnServer("displayStatus",self.padDisplay("ignored")+datetime.datetime.now().strftime("%m-%d %H:%M:%S"))
					dev.updateStateImageOnServer(indigo.kStateImageSel.PowerOff)
				dev.updateStateOnServer("status",value= "ignored", uiValue=self.padDisplay("ignored")+datetime.datetime.now().strftime("%m-%d %H:%M:%S"))
		valuesDict["MSG"] = "ok"
		self.saveMACdata(force=True)
		return valuesDict
	####-----------------  UN- Ignore MAC info  ---------
	####-----------------	 ---------
	def buttonConfirmStopIgnoringCALLBACK(self, valuesDict=None, typeId="", devId=""):

		for dev in indigo.devices.iter("props.isUniFi,props.isCamera"):
			if "MAC" in dev.states	 and dev.states["MAC"] == valuesDict["MACdeviceIgnored"]:
				if "displayStatus" in dev.states:
					dev.updateStateOnServer("displayStatus",self.padDisplay("")+datetime.datetime.now().strftime("%m-%d %H:%M:%S"))
					dev.updateStateImageOnServer(indigo.kStateImageSel.PowerOff)
				dev.updateStateOnServer("status","")
				dev.updateStateOnServer("onOffState", value=False, uiValue=self.padDisplay("")+datetime.datetime.now().strftime("%m-%d %H:%M:%S"))
		try: del self.MACignorelist[valuesDict["MACdeviceIgnored"]]
		except: pass
		valuesDict["MSG"] = "ok"
		self.saveMACdata(force=True)
		self.indiLOG.log(10," stop ignoring  MAC# " +valuesDict["MACdeviceIgnored"])
		return valuesDict



	####-----------------  powercycle switch port	---------
	####-----------------	 ---------
	def filterUnifiSwitchACTION(self, filter="", valuesDict=None, typeId="", targetId=""):
		return self.filterUnifiSwitch(valuesDict)

	####-----------------	 ---------
	def filterUnifiSwitch(self, filter="", valuesDict=None, typeId="", targetId=""):
		xList = []
		for dev in indigo.devices.iter("props.isSwitch"):
			swNo = int(dev.states["switchNo"])
			if self.devsEnabled["SW"][swNo]:
				xList.append(("{}".format(swNo)+"-SWtail-{}".format(dev.id), "{}".format(swNo)+"-"+self.ipNumbersOf["SW"][swNo]+"-"+dev.name))
		return xList

	def buttonConfirmSWCALLBACK(self, valuesDict=None, typeId="", targetId=""):
		self.unifiSwitchSelectedID =  valuesDict["selectedUnifiSwitch"].split("-")[2]
		return valuesDict

	####-----------------	 ---------
	def filterUnifiSwitchPort(self, filter="", valuesDict=None, typeId="", targetId=""):

		xList = []
		try:	int(self.unifiSwitchSelectedID)
		except: return xList

		dev = indigo.devices[int(self.unifiSwitchSelectedID)]
		snNo = "{}".format(dev.states["switchNo"] )
		for port in range(99):
			ppp = "port_{:02d}".format(port) 
			if ppp not in dev.states: continue
			if	dev.states[ppp].find("poe") >-1:
				name  = ""
				if	dev.states[ppp].find("poeX") >-1:
					name = " - empty"
				else:
					name = ""
					for dev2 in indigo.devices.iter("props.isUniFi"):
						if "SW_Port" in dev2.states and len(dev2.states["SW_Port"]) > 2:
							if not dev2.enabled: continue
							sw	 = dev2.states["SW_Port"].split(":")
							if sw[0] == snNo:
								if sw[1].find("poe") > -1 and dev.states["status"] != "expired":
									if "{}".format(port) == sw[1].split("-")[0]:
										name = " - {}".format(dev2.name)
										break
								elif dev.states["status"] != "expired":
									if "{}".format(port) == sw[1].split("-")[0]:
										name = " - {}".format(dev2.name)
										break
								else:
									if "{}".format(port) == sw[1].split("-")[0]:
										name = " - {}".format(dev2.name)
				xList.append([port,"port#{}{}".format(port, name)])
		return xList

	####-----------------	 ---------
	def filterUnifiClient(self, filter="", valuesDict=None, typeId="", targetId=""):

		xList = []
		for dev2 in indigo.devices.iter("props.isUniFi"):
			if "SW_Port" in dev2.states and len(dev2.states["SW_Port"]) > 2:
				sw	 = dev2.states["SW_Port"].split(":")
				if sw[1].find("poe") >-1:
					port = sw[1].split("-")[0]
					xList.append([sw[0]+"-"+port,"sw{}-port#{} - {}".format(sw[0], port, dev2.name)])
		xList.sort(key = lambda x: x[1]) 
		return xList


	####-----------------	 ---------
	def buttonConfirmpowerCycleCALLBACKaction(self, action1=None):
		return self.buttonConfirmpowerCycleCALLBACK(valuesDict=action1.props)

	####-----------------	 ---------
	def buttonConfirmpowerCycleClientsCALLBACKaction(self, action1=None):
		return self.buttonConfirmpowerCycleClientsCALLBACK(valuesDict=action1.props)

	####-----------------	 ---------
	def buttonConfirmpowerCycleCALLBACK(self, valuesDict=None, typeId="", devId=""):
		onOffCycle	= valuesDict["onOffCycle"]
		ip_type		=  valuesDict["selectedUnifiSwitch"].split("-")
		ipNumber	= self.ipNumbersOf["SW"][int(ip_type[0])]
		dtype		= ip_type[1]
		port		= "{}".format(valuesDict["selectedUnifiSwitchPort"])
		cmd 		= self.expectPath +" "
		if onOffCycle == "CYCLE":
			cmd += "'"+self.pathToPlugin + "cyclePort.exp" + "' "
		elif  onOffCycle =="ON":
			cmd += "'"+self.pathToPlugin + "onPort.exp" + "' "
		elif  onOffCycle =="OFF":
			cmd += "'"+self.pathToPlugin + "offPort.exp" + "' "
		cmd += "'"+self.connectParams["UserID"]["unixDevs"] + "' '"+self.connectParams["PassWd"]["unixDevs"] + "' "
		cmd += ipNumber + " "
		cmd += port + " "
		cmd += "'" + self.escapeExpect(self.connectParams["promptOnServer"][ipNumber]) +"' "
		cmd +=  self.getHostFileCheck()
		cmd +=   " &"
		if self.decideMyLog("Expect"): self.indiLOG.log(10,"RECYCLE: "+cmd )
		ret, err = self.readPopen(cmd)
		if self.decideMyLog("ExpectRET"): self.indiLOG.log(10,"RECYCLE returned: {}-{}".format(ret, err))
		self.addToMenuXML(valuesDict)
		return valuesDict

	####-----------------	 ---------
	def buttonConfirmpowerCycleClientsCALLBACK(self, valuesDict=None, typeId="", devId=""):
		ip_type	 =	valuesDict["selectedUnifiClientSwitchPort"].split("-")
		if len(ip_type) != 2: return valuesDict
		valuesDict["selectedUnifiSwitch"]		= ip_type[0]+"-SWtail"
		valuesDict["selectedUnifiSwitchPort"]	= ip_type[1]
		self.buttonConfirmpowerCycleCALLBACK(valuesDict)
		return valuesDict


	####-----------------  suspend / activate unifi devices	   ---------
	def buttonConfirmsuspendCALLBACKaction(self, action1=None):
		self.buttonConfirmsuspendCALLBACKbutton(valuesDict=action1.props)

	####-----------------  suspend / activate unifi devices	   ---------
	def buttonConfirmactivateCALLBACKaction(self, action1=None):
		self.buttonConfirmactivateCALLBACKbutton(valuesDict=action1.props)


	####-----------------	suspend / activate unifi devices	---------
	def buttonConfirmsuspendCALLBACKbutton(self, valuesDict=None, typeId="", devId=""):
		try:
			ID = int(valuesDict["selectedDevice"])
			dev= indigo.devices[ID]
			ip = dev.states["ipNumber"]
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
			return
		self.indiLOG.log(10,"suspending Unifi system device {} {} - only in plugin".format(dev.name, ip) )
		self.setSuspend(ip, time.time()+9999999)
		self.exeDisplayStatus(dev,"susp")
		self.addToMenuXML(valuesDict)
		return valuesDict

	def buttonConfirmactivateCALLBACKbutton(self, valuesDict=None, typeId="", devId=""):
		try:
			ID = int(valuesDict["selectedDevice"])
			dev= indigo.devices[ID]
			ip = dev.states["ipNumber"]
			try:
				self.delSuspend(ip)
				self.exeDisplayStatus(dev,"up")
				self.indiLOG.log(10,"reactivating Unifi system device {} {} - only in plugin".format(dev.name, ip) )
			except: pass
		except	Exception as e:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		self.addToMenuXML(valuesDict)
		return valuesDict



	####-----------------  Unifi controller backup  ---------
	def getBackupFilesFromController(self, valuesDict=None, typeId="", devId=""):
		if not self.unifiControllerBackupON: return 

		cmd = "cd '"+self.indigoPreferencesPluginDir+"backup';"
		cmd += self.expectPath 
		cmd += " '"+self.pathToPlugin + "controllerbackup.exp' "
		cmd += " '"+self.connectParams["UserID"]["unixDevs"]+"' "
		cmd += " '"+self.connectParams["PassWd"]["unixDevs"]+"' "
		cmd +=     self.unifiCloudKeyIP
		cmd += " '"+self.ControllerBackupPath.rstrip("/")+"'"
		cmd +=  self.getHostFileCheck()

		if self.decideMyLog("Expect"): self.indiLOG.log(10,"backup cmd: {}".format(cmd) )

		ret, err = self.readPopen(cmd)

		if self.decideMyLog("ExpectRET"): self.indiLOG.log(10,"backup cmd returned: {}-{}".format(ret, err))

		return 


	####-----------------  Unifi api calls	  ---------


######## block / unblock reconnect
	####-----------------	 ---------
	def buttonConfirmReconnectCALLBACKaction(self, action1=None):
		return self.buttonConfirmReconnectCALLBACK(valuesDict=action1.props)

	####-----------------	 ---------
	def buttonConfirmReconnectCALLBACK(self, valuesDict=None, typeId="", devId=""):
		ret = self.executeCMDOnController(dataSEND={"cmd":"kick-sta","mac":valuesDict["selectedDevice"]},pageString="/cmd/stamgr",cmdType="post")
		self.indiLOG.log(10,"reconnect cmd: return  {}".format(ret) )
		valuesDict["MSG"] = "command send"
		return valuesDict

	####-----------------	 ---------
	def buttonConfirmBlockCALLBACKaction(self, action1=None):
		return self.buttonConfirmBlockCALLBACK(valuesDict=action1.props)

	####-----------------	 ---------
	def buttonConfirmBlockCALLBACK(self, valuesDict=None, typeId="", devId=""):
		ret = self.executeCMDOnController(dataSEND={"cmd":"block-sta","mac":valuesDict["selectedDevice"]},pageString="/cmd/stamgr",cmdType="post")
		self.getcontrollerDBForClientsLast = time.time() - self.readDictEverySeconds["DB"]
		valuesDict["MSG"] = "error"
		for rr in ret:
			if "blocked" in rr: 
				self.indiLOG.log(20,"MAC#: {} {}".format(valuesDict["selectedDevice"], "blocked" if rr["blocked"] else "not executed") )
				valuesDict["MSG"] = "{} {}".format(valuesDict["selectedDevice"], "blocked" if rr["blocked"] else "not executed")
		return valuesDict


	####-----------------	 ---------
	def buttonConfirmUnBlockCALLBACKaction(self, action1=None):
		return self.buttonConfirmUnBlockCALLBACK(valuesDict=action1.props)

	####-----------------	 ---------
	def buttonConfirmUnBlockCALLBACK(self, valuesDict=None, typeId="", devId=""):
		ret = self.executeCMDOnController(dataSEND={"cmd":"unblock-sta","mac":valuesDict["selectedDevice"]}, pageString="/cmd/stamgr",cmdType="post")
		self.getcontrollerDBForClientsLast = time.time() - self.readDictEverySeconds["DB"]
		valuesDict["MSG"] = "error"
		for rr in ret:
			if len(rr) ==0: continue
			if "blocked" in rr: 
				self.indiLOG.log(20,"MAC#:{} {}".format(valuesDict["selectedDevice"],"un-blocked" if not rr["blocked"] else "not executed") )
				valuesDict["MSG"] = "{} {}".format(valuesDict["selectedDevice"], "un-blocked" if not rr["blocked"] else "not executed")
		return valuesDict

######## block / unblock reconnec  end

######## reports for specific stations / devices
	def buttonConfirmGetAPDevInfoFromControllerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		valuesDict["MSG"] = ""
		for dev in indigo.devices.iter("props.isAP"):
			MAC = dev.states["MAC"]
			if "MAClan" in dev.states: 
				props = dev.pluginProps
				if "useWhichMAC" in props and props["useWhichMAC"] == "MAClan":
					MAC = dev.states["MAClan"]
			self.indiLOG.log(10,"unifi-Report getting _id for AP {}  /stat/device/{}".format(dev.name, MAC) )
			jData = self.executeCMDOnController(dataSEND={}, pageString="/stat/device/"+MAC, jsonAction="returnData", cmdType="get")

			if len(jData) == 0 and self.unifiCloudKeyPort == "": 
				self.indiLOG.log(10,"unifi-Report:  controller not setup, skipping other querries" )
				break

			for dd in jData:
				if "_id" not in dd:
					self.indiLOG.log(10,"unifi-Report _id not in data")
					continue
				self.indiLOG.log(10,"unifi-Report  _id in data:{}".format(dd["_id"]) )
				dev.updateStateOnServer("ap_id", dd["_id"])
				break
		self.addToMenuXML(valuesDict)
		return valuesDict

	####-----------------	 ---------
	####-----------------	 ---------
	def buttonConfirmPrintDevInfoFromControllerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		MAC = valuesDict["MACdeviceSelectedsys"]
		for dev in indigo.devices.iter("props.isAP,props.isSwitch,props.isGateway"):
			if "MAC" in dev.states and dev.states["MAC"] != MAC: continue
			if "MAClan" in dev.states and dev.states["MAClan"] != MAC:
				props = dev.pluginProps
				if "useWhichMAC" in props and props["useWhichMAC"] == "MAClan":
					MAC = dev.states["MAClan"]
			break	
		self.executeCMDOnController(dataSEND={}, pageString="/stat/device/"+MAC, jsonAction="print",startText="== Unifi Device print: /stat/device/"+MAC+" ==", cmdType="get")
		return valuesDict

	####-----------------	 ---------
	def buttonConfirmPrintClientInfoFromControllerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		MAC = valuesDict["MACdeviceSelectedclient"]
		self.executeCMDOnController(dataSEND={}, pageString="/stat/sta/"+MAC, jsonAction="print",startText="== Client print: /stat/sta/"+MAC+" ==", cmdType="get")
		return valuesDict

######## reports all devcies
	####-----------------	 ---------
	def buttonConfirmPrintalluserInfoFromControllerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		data = self.executeCMDOnController(dataSEND={}, pageString="/stat/alluser/", jsonAction="returnData", cmdType="get")
#		data = self.executeCMDOnController(dataSEND={"type":"all","conn":"all"}, pageString="/stat/alluser/", jsonAction="returnData", cmdType="get")
		self.unifsystemReport3(data, "== ALL USER report ==")
		self.fillcontrollerDBForClients(data)
		return valuesDict

	####-----------------	 ---------
	def buttonConfirmPrintuserInfoFromControllerCALLBACK(self, valuesDict=None, typeId="", devId="", cmdType="get"):
		data = self.executeCMDOnController(dataSEND={}, pageString="/list/user/", jsonAction="returnData", cmdType=cmdType)
		self.unifsystemReport3(data, "== USER report ==")
		return valuesDict



	####-----------------print DPI info  ---------
	def buttonConfirmPrintListOfBackupsFromControllerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		try:
			data = self.executeCMDOnController(dataSEND={'cmd': 'list-backups'}, pageString="cmd/backup", jsonAction="returnData", cmdType="post")
			if len(data) == 0: 
				self.indiLOG.log(20,"no data returned from backup list")
				return valuesDict
			##[{"controller_name":"192.168.1.2","filename":"autobackup_6.0.43_20210208_0600_1612764000017.unf","type":"primary","version":"6.0.43","time":1612764000017,"datetime":"2021-02-08T06:00:00Z","format":"bson","days":30,"size":25885584},
			out = ""
			for rec in data:
				if out == "": 
					out =  "\n== UniFi  list of backups on system {}\n".format(rec["controller_name"])
					out += "fileName ----------------------------------------              size  days  type       version  date\n"
				out += "{:50}".format(rec["filename"]) 
				out += "{:>17,d} ".format(rec["size"]) 
				out += "{:>5}  ".format(rec["days"]) 
				out += "{:11}".format(rec["type"]) 
				out += "{:9}".format(rec["version"]) 
				out += time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(rec["time"]/1000.))
				out += "\n"
			self.indiLOG.log(20,out)
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return valuesDict

	####-----------------print DPI info  ---------
	def buttonConfirmPrintDPIFromControllerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		try:
			data = {}
			data["app"] = self.executeCMDOnController(dataSEND={'type': 'by_app'}, pageString="stat/sitedpi", jsonAction="returnData", cmdType="post")
			data["cat"] = self.executeCMDOnController(dataSEND={'type': 'by_cat'}, pageString="stat/sitedpi", jsonAction="returnData", cmdType="post")
			f = self.openEncoding(self.pathToPlugin+"unifi_dpi.json","r")
			catappInfo = json.loads(f.read())
			f.close()
			#self.indiLOG.log(20,"{}".format(catappInfo))
			#self.indiLOG.log(20,"{}".format(data["app"]))
			#self.indiLOG.log(20,"{}".format(data["cat"]))

			out1 = []
			out2 = []
			lastUpdated = ""
			for rr in data["cat"]: 
				if 'last_updated' in rr:
					lastUpdated = rr["last_updated"]
					lastUpdated = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(lastUpdated))
				if  "by_cat" in rr:
					for rec in rr["by_cat"]:
						o   = "{:>7d} ".format(rec["cat"]) 
						nn = "{}".format(rec["cat"])
						if nn in catappInfo["categories"]:
							o +=  catappInfo["categories"][nn]["name"].ljust(37)
						else:
							o +=  ("??").ljust(37)
						o += "{:>17,d}".format(rec["rx_bytes"]) 
						o += "{:>17,d}".format(rec["tx_bytes"]) 
						out1.append(o)
			for rr in data["app"]: 
				if 'last_updated' in rr:
					lastUpdated = rr["last_updated"]
					lastUpdated = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(lastUpdated))
				if  "by_app" in rr:
					for rec in rr["by_app"]:
						o  = "{:>7d} ".format(rec["app"]) 
						nn = "{}".format(rec["app"])
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
				out =  "\n== UniFi  Deep Packet Info report, lastUpdated: {} == \n".format(lastUpdated)
				out =  "\n== ** cat and app #s from https://ubntwiki.com/products/software/unifi-controller/api/cat_app_json ** \n".format(lastUpdated)
				out += "   cat# cat Name-----------------------               rx_bytes         tx_Bytes\n"
				out += "\n".join(sorted(out1))
				out += "\n"
				out += "   app# app Name-----------------------  cat#         rx_bytes         tx_Bytes #clients\n"
				out += "\n".join(sorted(out2))
				self.indiLOG.log(20,out)
			else:
				self.indiLOG.log(20,"== DPI report empty, no data returned ==")

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return valuesDict


####   general reports
	####-----------------	 ---------
	def buttonConfirmPrintHealthInfoFromControllerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		data = self.executeCMDOnController(dataSEND={}, pageString="/stat/health/", jsonAction="returnData", cmdType="get")
		out = "== HEALTH report ==\n"
		ii=0
		for item in data:
			ii+=1
			ll = "{}".format(ii).ljust(3)
			ll+=(item["subsystem"]+":").ljust(10)
			ll+=(item["status"]+";").ljust(10)
			if "rx_bytes-r" in item:
				ll+="rx_B:"+("{}".format(item["rx_bytes-r"])+";").ljust(9)
			if "tx_bytes-r" in item:
				ll+="tx_B:"+("{}".format(item["tx_bytes-r"])+";").ljust(9)

			for item2 in item:
				if item2 =="subsystem":  continue
				if item2 =="status":	  continue
				if item2 =="tx_bytes-r": continue
				if item2 =="rx_bytes-r": continue
				ll+= "{}".format(item2)+":{}".format(item[item2])+";    "
			out+=ll+("\n")
		self.indiLOG.log(20,"unifi-Report ")
		self.indiLOG.log(20,"unifi-Report  "+out)
		return valuesDict

	####-----------------	 ---------
	def buttonConfirmPrintPortForWardInfoFromControllerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		data =self.executeCMDOnController(dataSEND={}, pageString="/stat/portforward/", jsonAction="returnData", cmdType="get")
		out = "== PortForward report ==\n"
		out += "##".ljust(4) + "name".ljust(20) + "protocol".ljust(10) + "source".ljust(16)	+ "fwd_port".rjust(9)+ "dst_port".rjust(9)+ " fwd_ip".ljust(17)+ "rx_bytes".rjust(12)+ "rx_packets".rjust(12)+"\n"
		ii = 0
		for item in data:
			ii+=1
			ll = "{}".format(ii).ljust(4)
			ll+= item["name"].ljust(20)
			ll+= item["proto"].ljust(10)
			ll+= item["src"].ljust(16)
			ll+= item["fwd_port"].rjust(9)
			ll+= item["dst_port"].rjust(9)
			ll+= (" "+item["fwd"]).ljust(17)
			ll+= "{}".format(item["rx_bytes"]).rjust(12)
			ll+= "{}".format(item["rx_packets"]).rjust(12)
			out+=ll+("\n")
		self.indiLOG.log(20,"unifi-Report ")
		self.indiLOG.log(20,"unifi-Report  "+out)
		return valuesDict


	####-----------------	 ---------
	def buttonConfirmPrintSessionInfoFromControllerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		toT		= int(time.time()+100)
		fromT 	= toT - 30000
		data = self.executeCMDOnController(dataSEND={}, pageString="/stat/session?type=all&start={:d}&end={:d}".format(fromT,toT), jsonAction="returnData", cmdType="get")
		out = "\n"
		ii = 0
		for xxx in data:
			ii += 1
			out += "== Session report ==  #{}, client: mac={} - {}\n".format(ii, xxx["mac"], xxx["hostname"])
			for item in  ["ip","is_wired","is_guest","rx_bytes","tx_bytes","ap_mac"]:
				if item in xxx:
					out += "{:35s}:{}\n".format(item, xxx[item])
				else:
					out += "{:35s}: empty\n".format(item)

			out += ("Accociated:").ljust(35)+"{} minutes ago\n".format(int(time.time()-xxx["assoc_time"])/60)
			out += ("Duration:").ljust(35)+"{} [secs]\n".format(xxx["duration"])
		self.indiLOG.log(20,"unifi-Report ")
		self.indiLOG.log(20,"unifi-Report  "+out)
		return valuesDict


	####-----------------	 ---------
	def buttonConfirmPrintAlarmInfoFromControllerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		data = self.executeCMDOnController(dataSEND={}, pageString="/list/alarm/", jsonAction="returnData", cmdType="get")
		self.unifsystemReport1(data, True, "    ==AlarmReport==", limit=99999)
		self.addToMenuXML(valuesDict)
		return valuesDict



	####-----------------	 ---------
	def buttonConfirmPrintWifiConfigInfoFromControllerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		data = self.executeCMDOnController(dataSEND={}, pageString="/rest/wlanconf", jsonAction="returnData", cmdType="get")
		out = "\n"
		ii = 0
		for xxx in data:
			ii += 1
			out += "== Wifi Config report == # {}; SSID= {}\n".format(ii, xxx["name"])
			for item in xxx:
				if item not in ["name","site_id","x_iapp_key","_id","wlangroup_id"]:
					out += ("{}".format(item)+":").ljust(35)+"{}".format(xxx[item])+"\n"
		self.indiLOG.log(20,"unifi-Report ")
		self.indiLOG.log(20,"unifi-Report  "+out)
		return valuesDict


	####-----------------	 ---------
	def buttonConfirmPrintWifiChannelInfoFromControllerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		data =self.executeCMDOnController(dataSEND={}, pageString="/stat/current-channel", jsonAction="returnData", cmdType="get")
		out = "== Wifi Channel report ==\n"
		for xxx in data:
			for item in ["code","key","name"]:
					out += ("{}".format(item)+":").ljust(25)+"{}".format(xxx[item])+"\n"
			for item in xxx:
				if item not in ["code","key","name"]:
					out += ("{}".format(item)+":").ljust(25)+"{}".format(xxx[item])+"\n"
		self.indiLOG.log(20,"unifi-Report ")
		self.indiLOG.log(20,"unifi-Report  "+out)
		return valuesDict



	####-----------------	 ---------
	def buttonConfirmPrintEventInfoFromControllerCALLBACK(self, valuesDict=None, typeId="", devId=""):

		limit = 100
		if "PrintEventInfoMaxEvents" in valuesDict:
			try:	limit = int(valuesDict["PrintEventInfoMaxEvents"])
			except: pass

		PrintEventInfoLoginEvents = False
		if "PrintEventInfoLoginEvents" in valuesDict:
			try:	PrintEventInfoLoginEvents = valuesDict["PrintEventInfoLoginEvents"]
			except: pass


		if PrintEventInfoLoginEvents:
			ltype = "WITH"
			useLimit = limit
		else:
			ltype = "Skipping"
			useLimit = 5*limit
		data = self.executeCMDOnController(dataSEND={"_sort":"+time", "_limit":useLimit}, pageString="/stat/event/", jsonAction="returnData", cmdType="put")
		self.unifsystemReport1(data, False, "     ==EVENTs ..;  last {} events ;     -- {} login events ==".format(limit, ltype), limit, PrintEventInfoLoginEvents=PrintEventInfoLoginEvents)
		self.addToMenuXML(valuesDict)

		return valuesDict

	####-----------------	 ---------
	def updateDevStateswRXTXbytes(self):
		try:
			if time.time() - self.lastupdateDevStateswRXTXbytes < 200: return 
			self.lastupdateDevStateswRXTXbytes = time.time()
			en = int( time.time()  ) * 1000
			st = en - 300*1000
			data = self.executeCMDOnController(dataSEND={"attrs": ["tx_bytes", "rx_bytes", "time"], "start": st, "end": en}, pageString="/stat/report/5minutes.user", jsonAction="returnData", cmdType="post")

			if len(data) == 0: return
			MACbytes 	= {}
			tNow 		= int(time.time()*1000)
			anyUpdate 	= False
			maxDT 		= 0
			oneBad 		= False
			for rec in data:
				#{"rx_bytes":1090.4761904761904,"tx_bytes":1428.904761904762,"time":1613157900000,"user":"b8:27:eb:c8:c7:ab","o":"user","oid":"b8:27:eb:c8:c7:ab"},
				if "user" not in rec or "time" not in rec or "tx_bytes" not in rec: 
					#if not oneBad: self.indiLOG.log(10,"updateDevStateswRXTXbytes user/time/rx tx_bytes   not in rec:{}".format(rec))
					oneBad = True
					continue

				maxDT = max( maxDT, tNow - rec["time"] )
				if tNow - rec["time"] > 605*1000: 
					if not oneBad: self.indiLOG.log(10,"updateDevStateswRXTXbytes bad time tNow:{}; recT:{}; dt:{}; rec:{}".format(tNow, rec["time"],  tNow - rec["time"], rec))
					oneBad = True
					continue 
				try: 	
					## rx and tx are flipped in response 
					MACbytes[rec["user"]] = {"txBytes":int(rec["rx_bytes"]),"rxBytes":int(rec["tx_bytes"])}
				except: 
					if not oneBad: self.indiLOG.log(10,"updateDevStateswRXTXbytes  bad data rec:{}".format(rec))
					oneBad = True
					continue

			if oneBad and self.decideMyLog("Special"): 
				self.indiLOG.log(10,"updateDevStateswRXTXbytes,  data:{}".format(data))
				self.indiLOG.log(10,"updateDevStateswRXTXbytes, maxDT:{}  MACBYTES:{}".format(maxDT/1000, MACbytes))

			for dev in indigo.devices.iter("props.isUniFi"):
				if not dev.enabled: continue
				mac = dev.address
				if "rx_Bytes_Last5Minutes" in dev.states:
					if mac in MACbytes:
						tx =  MACbytes[mac]["txBytes"]
						rx =  MACbytes[mac]["rxBytes"]
					else:
						tx =  0
						rx =  0

					if dev.states["rx_Bytes_Last5Minutes"] != rx:
						anyUpdate = True
						self.addToStatesUpdateList(dev.id, "rx_Bytes_Last5Minutes", rx)
					if dev.states["tx_Bytes_Last5Minutes"] != tx:
						anyUpdate = True
						self.addToStatesUpdateList(dev.id, "tx_Bytes_Last5Minutes", tx)

			if anyUpdate:
				self.executeUpdateStatesList()

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return


	####-----------------	 ---------
	def buttonConfirmPrint7DaysWiFiInfoFromControllerCALLBACK(self, valuesDict=None, typeId="", devId=""):

		en = int( time.time() - (time.time() % 3600 ) ) * 1000
		st = en - 3600*1000*12*7 # 7 days
		data = self.executeCMDOnController(dataSEND={"attrs": ["rx_bytes", "tx_bytes", "num_sta", "time"], "start": st, "end": en}, pageString="/stat/report/daily.ap", jsonAction="returnData", cmdType="post")
		self.printWifiStatReport(data, "==  days WiFi-AP stat report ==")
		return valuesDict


	####-----------------	 ---------
	def buttonConfirmPrint48HoursWiFiInfoFromControllerCALLBACK(self, valuesDict=None, typeId="", devId=""):

		en = int( time.time() - (time.time() % 3600) ) * 1000
		st = en - 3600*1000*48 # 
		data = self.executeCMDOnController(dataSEND={"attrs": ["rx_bytes", "tx_bytes", "num_sta", "time"], "start": st, "end": en}, pageString="/stat/report/hourly.ap", jsonAction="returnData", cmdType="post")
		self.printWifiStatReport(data, "==  hours WiFi-AP stat report ==")
		return valuesDict

	####-----------------	 ---------
	def buttonConfirmPrint5MinutesWiFiInfoFromControllerCALLBACK(self, valuesDict=None, typeId="", devId=""):

		en = int( time.time()  ) * 1000
		st = en - 3600*1000*4 #  4 hours
		data = self.executeCMDOnController(dataSEND={"attrs": ["rx_bytes", "tx_bytes", "num_sta", "time"], "start": st, "end": en}, pageString="/stat/report/5minutes.ap", jsonAction="returnData", cmdType="post")
		self.printWifiStatReport(data, "==  minutes WiFi-AP stat report ==")
		return valuesDict


	####-----------------	 ---------
	def printWifiStatReport(self, data, headLine):
		out = headLine+"\n"
		out+= "##".ljust(4)
		out+= "timeStamp".ljust(21)
		out+= "num_sta".rjust(8)
		out+= "rxBytes".rjust(17)
		out+= "txBytes".rjust(17)
		out+= "\n"
		ii=0
		lastap = ""
		for item in data:
			ii+=1
			if lastap != item["ap"]:
				out+= "AP MAC #:"+item["ap"]+"\n"
			lastap = item["ap"]

			ll = "{}".format(ii).ljust(4)
			if "time" in item:
				ll+= time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(item["time"]/1000)).ljust(21)
			else:				  ll+= (" ").ljust(21)

			if "num_sta" in item:
				ll+= "{}".format(item["num_sta"]).rjust(8)
			else:				  ll+= (" ").rjust(8)

			if "rx_bytes" in item:
				ll+= ("{0:,d}".format(int(item["rx_bytes"]))).rjust(17)
			else:				  ll+= (" ").rjust(17)
			if "tx_bytes" in item:
				ll+= ("{0:,d}".format(int(item["tx_bytes"]))).rjust(17)
			else:				  ll+= (" ").rjust(17)

			out+=ll+("\n")
		self.indiLOG.log(20,"unifi-Report ")
		self.indiLOG.log(20,"unifi-Report  "+out)
		return


	####-----------------	 ---------
	def buttonConfirmPrint5MinutesWanInfoFromControllerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		en = int( time.time()  ) * 1000
		st = en - 3600 *1000*4 # 4 hours 
		data = self.executeCMDOnController(dataSEND={"attrs": ["bytes","wan-tx_bytes","wan-rx_bytes","wan-tx_bytes", "num_sta", "wlan-num_sta", "lan-num_sta", "time"], "start": st, "end": en}, pageString="/stat/report/5minutes.site", jsonAction="returnData", cmdType="post")
		self.unifsystemReport2(data,"== 5 minutes WAN report ==")
		return valuesDict

	####-----------------	 ---------
	def buttonConfirmPrint48HoursWanInfoFromControllerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		en = int( time.time() - (time.time() % 3600) ) * 1000
		st = en - 2*86400*1000 # 2 days
		data = self.executeCMDOnController(dataSEND={"attrs": ["bytes","wan-tx_bytes","wan-rx_bytes","wan-tx_bytes", "num_sta", "wlan-num_sta", "lan-num_sta", "time"], "start": st, "end": en}, pageString="/stat/report/hourly.site", jsonAction="returnData", cmdType="post")
		self.unifsystemReport2(data,"==  HOUR WAN report ==")
		return valuesDict

	####-----------------	 ---------
	def buttonConfirmPrint7DaysWanInfoFromControllerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		en = int( time.time() - (time.time() % 3600) ) * 1000
		st = en - 7*86400 *1000  # 7 days
		data = self.executeCMDOnController(dataSEND={"attrs": ["bytes","wan-tx_bytes","wan-rx_bytes","wan-tx_bytes", "num_sta", "wlan-num_sta", "lan-num_sta", "time"], "start": st, "end": en}, pageString="/stat/report/daily.site", jsonAction="returnData", cmdType="post")
		self.unifsystemReport2(data,"==  DAY WAN report ==")
		return valuesDict


	####-----------------	 ---------
	def buttonConfirmPrintWlanConfInfoFromControllerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		data = self.executeCMDOnController(dataSEND={}, pageString="list/wlanconf", jsonAction="returnData", cmdType="get")
		out = "==WLan Report =="+"\n"
		out+= " ".ljust(4+20+6+20)+"bc_filter...".ljust(6+15) +"dtim .......".ljust(8+3+3)+"MAC_filter ........".ljust(6+20+8)+" ".ljust(15+8)+"wpa......".ljust(6+6)+"\n"
		out+= "##".ljust(4)
		out+= "name".ljust(20)
		out+= "passphrase".ljust(20)
		out+= "enble".ljust(6)
		out+= "enble".ljust(6)
		out+= "list".ljust(15)
		out+= "mode".ljust(8)
		out+= "na".ljust(3)
		out+= "ng".ljust(3)
		out+= "enble".ljust(6)
		out+= "list".ljust(20)
		out+= "policy".ljust(8)
		out+= "schedule".ljust(15)
		out+= "secrty".ljust(8)
		out+= "enc".ljust(6)
		out+= "mode".ljust(6)
		out+= "\n"
		ii=0
		for item in data:
			ii+=1
			ll = "{}".format(ii).ljust(4)
			if "name" in item:
				ll+= "{}".format(item["name"]).ljust(20)
			else:
				ll+= (" ").ljust(20)

			if "x_passphrase" in item:
				ll+= "{}".format(item["x_passphrase"]).ljust(20)
			else:
				ll+= (" ").ljust(16)

			if "enabled" in item:
				ll+= "{}".format(item["enabled"]).ljust(6)
			else:				  ll+= (" ").ljust(6)

			if "bc_filter_enabled" in item:
				ll+= "{}".format(item["bc_filter_enabled"]).ljust(6)
			else:				 ll+= (" ").ljust(6)

			if "bc_filter_list" in item:
				ll+= "{}".format(item["bc_filter_list"]).ljust(15)
			else:				 ll+= (" ").ljust(15)

			if "dtim_mode" in item:
				ll+= "{}".format(item["dtim_mode"]).ljust(8)
			else:				 ll+= (" ").ljust(8)

			if "dtim_na" in item:
				ll+= "{}".format(item["dtim_na"]).ljust(3)
			else:				 ll+= (" ").ljust(3)

			if "dtim_ng" in item:
				ll+= "{}".format(item["dtim_ng"]).ljust(3)
			else:				 ll+= (" ").ljust(3)

			if "mac_filter_enabled" in item:
				ll+= "{}".format(item["mac_filter_enabled"]).ljust(6)
			else:				 ll+= (" ").ljust(6)

			if "mac_filter_list" in item:
				ll+= "{}".format(item["mac_filter_list"]).ljust(20)
			else:				 ll+= (" ").ljust(20)

			if "mac_filter_policy" in item:
				ll+= "{}".format(item["mac_filter_policy"]).ljust(8)
			else:				 ll+= (" ").ljust(8)

			if "schedule" in item:
				ll+= "{}".format(item["schedule"]).ljust(15)
			else:				 ll+= (" ").ljust(15)

			if "security" in item:
				ll+= "{}".format(item["security"]).ljust(8)
			else:				 ll+= (" ").ljust(8)

			if "wpa_enc" in item:
				ll+= "{}".format(item["wpa_enc"]).ljust(6)
			else:				 ll+= (" ").ljust(6)

			if "wpa_mode" in item:
				ll+= "{}".format(item["wpa_mode"]).ljust(6)
			else:				 ll+= (" ").ljust(6)


			out+=ll+("\n")
		self.indiLOG.log(20,"unifi-Report ")
		self.indiLOG.log(20,"unifi-Report  "+out)
		return valuesDict


	####-----------------	 ---------
	def unifsystemReport1(self, data, useName, start, limit, PrintEventInfoLoginEvents=False):
		out =start+"\n"
		if useName:
			out+= "##### datetime------".ljust(21+6) + "name---".ljust(30) + "subsystem--".ljust(12) + "key--------".ljust(30)    + "msg-----".ljust(50)+"\n"
		else:
			out+= "##### datetime------".ljust(21+6)                        + "subsystem--".ljust(12) + "key--------".ljust(30)    + "msg-----".ljust(50)+"\n"
		nn = 0
		for item in data:
			if not PrintEventInfoLoginEvents and item["msg"].find("log in from ")> -1: continue
			nn+=1
			if nn > limit: break
			## convert from UTC to local datetime string
			dd = datetime.datetime.strptime(item["datetime"],"%Y-%m-%dT%H:%M:%SZ")
			xx = (dd - datetime.datetime(1970,1,1)).total_seconds()
			ll = "{}".format(nn).ljust(6)
			ll += time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(xx)).ljust(21)
			if useName:
				found = False
				for	 xx in ["ap_name","gw_name","sw_name","ap_name"]:
					if xx in item:
						ll+= item[xx].ljust(30)
						found = True
						break
				if not found:
						ll+= " ".ljust(30)
			ll +=item["subsystem"].ljust(12) + item["key"].ljust(30) + item["msg"].ljust(50)
			out+= ll.replace("\n","")+"\n"
		self.indiLOG.log(20,"unifi-Report ")
		self.indiLOG.log(20,"unifi-Report  "+out)
		return 

	####-----------------	 ---------
	def unifsystemReport2(self,data, start):
		out = start+"\n"
		out+= "##".ljust(4)
		out+= "timeStamp".ljust(21)
		out+= "lanNumSta".ljust(11)
		out+= "num_sta".ljust(11)
		out+= "wlanNumSta".ljust(11)
		out+= "rx-WanBytes".rjust(20)
		out+= "tx-WanBytes".rjust(20)
		out+= "\n"
		ii=0
		for item in data:
			ii+=1
			ll = "{}".format(ii).ljust(4)
			if "time" in item:
				ll+= time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(item["time"]/1000)).ljust(21)
			else:
				ll+= (" ").ljust(21)

			if "lan-num_sta" in item:
				ll+= "{}".format(item["lan-num_sta"]).ljust(11)
			else:
				ll+= (" ").ljust(10)

			if "num_sta" in item:
				ll+= "{}".format(item["num_sta"]).ljust(11)
			else:
				ll+= (" ").ljust(11)

			if "wlan-num_sta" in item:
				ll+= "{}".format(item["wlan-num_sta"]).ljust(11)
			else:
				ll+= (" ").ljust(11)

			if "wan-rx_bytes" in item:
				ll+= ("{0:,d}".format(int(item["wan-rx_bytes"]))).rjust(20)
			else:
				ll+= (" ").ljust(20)

			if "wan-tx_bytes" in item:
				ll+= ("{0:,d}".format(int(item["wan-tx_bytes"]))).rjust(20)
			else:
				ll+= (" ").ljust(20)

			for item2 in item:
				if item2 == "lan-num_sta":		continue
				if item2 == "wlan-num_sta":	continue
				if item2 == "num_sta":			continue
				if item2 == "wan-rx_bytes":	continue
				if item2 == "wan-tx_bytes":	continue
				if item2 == "time":			continue
				if item2 == "oid":				continue
				if item2 == "site":			continue
				if item2 == "o":				continue
				ll+= "  {}".format(item2)+":{}".format(item[item2])+";...."

			out+=ll+("\n")
		self.indiLOG.log(20,"unifi-Report ")
		self.indiLOG.log(20,"unifi-Report  "+out)
		return

	####-----------------	 ---------
	def unifsystemReport3(self,data, start):
		out =start+"\n"
		out+= "##".ljust(4) + "mac".ljust(18)
		out+= "hostname".ljust(21) + "name".ljust(21)
		out+= "first_seen".ljust(21)+ "ulast_seen".ljust(21)
		out+= "vendor".ljust(10)
		out+= "fixedIP".ljust(16)
		out+= "us_f-ip".ljust(8)
		out+= "wired".ljust(6)
		out+= "blckd".ljust(6)
		out+= "guest".ljust(6)
		out+= "durationMin".rjust(12)
		out+= "rx_KBytes".rjust(16)
		out+= "rx_Packets".rjust(15)
		out+= "rx_KBytes".rjust(16)
		out+= "tx_Packets".rjust(15)
		out+="\n"
		ii=0
		for item in data:
			ii+=1
			ll = "{}".format(ii).ljust(4)
			if "mac" in item:
				ll+= item["mac"].ljust(18)
			else:
				ll+= (" ").ljust(18)

			if "hostname" in item:
				ll+= (item["hostname"][0:20]).ljust(21)
			else:
				ll+= (" ").ljust(21)

			if "name" in item:
				ll+= (item["name"][0:20]).ljust(21)
			else:
				ll+= (" ").ljust(21)

			if "first_seen" in item:
				ll+= time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(item["first_seen"])).ljust(21)
			else:
				ll+= (" ").ljust(21)

			if "last_seen" in item:
				ll+= time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(item["last_seen"])).ljust(21)
			else:
				ll+= (" ").ljust(21)

			if "oui" in item:
				ll+= (item["oui"][0:20]).ljust(10)
			else:
				ll+= (" ").ljust(10)

			if "fixed_ip" in item:
				ll+= (item["fixed_ip"]).ljust(16)
			else:
				ll+= (" ").ljust(16)

			if "use_fixedip" in item:
				ll+= "{}".format(item["use_fixedip"]).ljust(8)
			else:
				ll+= (" ").ljust(8)

			if "is_wired" in item:
				ll+= "{}".format(item["is_wired"]).ljust(6)
			else:
				ll+= (" ").ljust(6)

			if "blocked" in item:
				ll+= "{}".format(item["blocked"]).ljust(6)
			else:
				ll+= (" ").ljust(6)

			if "is_guest" in item:
				ll+= "{}".format(item["is_guest"]).ljust(6)
			else:
				ll+= (" ").ljust(6)

			if "duration" in item:
				ll+= ("{0:,d}".format(int(item["duration"])/60)).rjust(12)
			else:
				ll+= (" ").rjust(12)

			if "rx_bytes" in item:
				ll+= ("{0:,d}".format(int(item["rx_bytes"]/1024.))).rjust(16)
			else:
				ll+= (" ").rjust(16)

			if "rx_packets" in item:
				ll+= ("{0:,d}".format(int(item["rx_packets"]))).rjust(15)
			else:
				ll+= (" ").rjust(15)

			if "tx_bytes" in item:
				ll+= ("{0:,d}".format(int(item["tx_bytes"]/1024.))).rjust(16)
			else:
				ll+= (" ").rjust(16)

			if "tx_packets" in item:
				ll+= ("{0:,d}".format(int(item["tx_packets"]))).rjust(15)
			else:
				ll+= (" ").ljust(15)

			for item2 in item:
				if item2 =="hostname":	   continue
				if item2 =="mac":			continue
				if item2 =="first_seen":	continue
				if item2 =="last_seen":	continue
				if item2 =="site_id":	   	continue
				if item2 =="_id":		   	continue
				if item2 =="network_id":   continue
				if item2 =="usergroup_id": continue
				if item2 =="noted":		continue
				if item2 =="name":			continue
				if item2 =="is_wired":		continue
				if item2 =="oui":			continue
				if item2 =="blocked":		continue
				if item2 =="fixed_ip":		continue
				if item2 =="use_fixedip":	continue
				if item2 =="is_guest":		continue
				if item2 =="duration":		continue
				if item2 =="rx_bytes":		continue
				if item2 =="tx_bytes":		continue
				if item2 =="tx_packets":	continue
				if item2 =="rx_packets":   continue
				ll+= "{}".format(item2)+":{}".format(item[item2])+";...."
			out+=ll+("\n")


		self.indiLOG.log(20,"unifi-Report ")
		self.indiLOG.log(20,"unifi-Report  "+out)
		return


######## reports end



######## actions and menu set leds on /off
	####-----------------	 ---------
	def buttonConfirmAPledONControllerCALLBACKaction(self, action1=None):
		return self.buttonConfirmAPledONControllerCALLBACK(valuesDict=action1.props)
	####-----------------	 ---------
	def buttonConfirmAPledONControllerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		ret = self.executeCMDOnController(dataSEND={"led_enabled":True}, pageString="/set/setting/mgmt", cmdType="post")
		for rr in ret:
			if len(rr) ==0: continue
			if "led_enabled" in rr: 
				self.indiLOG.log(10, "LED cmd ret:{}".format(rr) )
				valuesDict["MSG"] = "LED cmd enabled:{}".format(rr["led_enabled"])
		return valuesDict

	####-----------------	 ---------
	def buttonConfirmAPledOFFControllerCALLBACKaction(self, action1=None):
		return self.buttonConfirmAPledOFFControllerCALLBACK(valuesDict=action1.props)
	####-----------------	 ---------
	def buttonConfirmAPledOFFControllerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		ret = self.executeCMDOnController(dataSEND={"led_enabled":False}, pageString="/set/setting/mgmt", cmdType="post")
		for rr in ret:
			if len(rr) ==0: continue
			if "led_enabled" in rr: 
				self.indiLOG.log(10, "LED cmd ret:{}".format(rr) )
				valuesDict["MSG"] = "LED cmd enabled:{}".format(rr["led_enabled"])
		return valuesDict

	####-----------------	 ---------
	def buttonConfirmAPxledONControllerCALLBACKaction(self, action1=None):
		return self.buttonConfirmAPxledONControllerCALLBACK(valuesDict=action1.props)
	####-----------------	 ---------
	def buttonConfirmAPxledONControllerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		ret = self.executeCMDOnController(dataSEND={"cmd":"set-locate","mac":valuesDict["selectedAPDevice"]}, pageString="/cmd/devmgr", cmdType="post")
		valuesDict["MSG"] = "command send"
		self.indiLOG.log(10,"set-locate cmd: return  {}".format(ret) )
		return valuesDict

	####-----------------	 ---------
	def buttonConfirmAPxledOFFControllerCALLBACKaction(self, action1=None):
		return self.buttonConfirmAPxledOFFControllerCALLBACK(valuesDict=action1.props)
	####-----------------	 ---------
	def buttonConfirmAPxledOFFControllerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		ret = self.executeCMDOnController(dataSEND={"cmd":"unset-locate","mac":valuesDict["selectedAPDevice"]}, pageString="/cmd/devmgr", cmdType="post")
		valuesDict["MSG"] = "command send"
		self.indiLOG.log(10,"unset-locate cmd: return  {}".format(ret) )
		return valuesDict

######## actions and menu set dev on /off
	####-----------------	 ---------
	def buttonConfirmEnableAPConllerCALLBACKaction(self, action1=None):
		self.execDisableAP(action1.props,False)
	def buttonConfirmEnableAPConllerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		ret = self.execDisableAP(valuesDict, False)
		return valuesDict

	####-----------------	 ---------
	def buttonConfirmDisableAPConllerCALLBACKaction(self, action1=None):
		self.execDisableAP(action1.props, True)
	def buttonConfirmDisableAPConllerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		ret = self.execDisableAP(valuesDict, True)
		return valuesDict

	def execDisableAP(self, valuesDict , disable): #( true if disable )
		dev = indigo.devices[int(valuesDict["apDeviceSelected"])]
		ID = dev.states["ap_id"]
		ip = dev.states["ipNumber"]
		if disable: self.setSuspend(ip, time.time() + 99999999)
		else	  : self.delSuspend(ip)
		valuesDict["MSG"] = "command send"
		ret = self.executeCMDOnController(dataSEND={"disabled":disable}, pageString="/rest/device/"+ID, cmdType="put", cmdTypeForce=True)
		for rr in ret:
			if len(rr) ==0: continue
			if "disabled" in rr: 
				self.indiLOG.log(10, "enable ret:{}".format(rr) )
				valuesDict["MSG"] = "enabled:{}".format(not rr["disabled"])
		self.indiLOG.log(10,"execDisableAP cmd: return  {}".format(ret) )
		return ret

######## actions and menu restart unifi devices
	####-----------------	 ---------
	def buttonConfirmRestartUnifiDeviceConllerCALLBACKaction(self, action1=None):
		self.buttonConfirmRestartUnifiDeviceConllerCALLBACK(action1.props)

	def buttonConfirmRestartUnifiDeviceConllerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		mac = valuesDict["selectedUnifiDevice"]
		if not self.isValidMAC(mac): 
			valuesDict["MSG"] = "no valid mac given:{}".format(mac)
			return valuesDict
		valuesDict["MSG"] = "restart command send to:{}".format(mac)
		ret = self.executeCMDOnController(dataSEND={'cmd':'restart','mac':mac}, pageString="/cmd/devmgr", cmdType="post", cmdTypeForce=True)
		self.indiLOG.log(10,"restart cmd: return  {}".format(ret) )
		return valuesDict


######## actions and menu provision unifi devices
	####-----------------	 ---------
	def buttonConfirmProvisionUnifiDeviceConllerCALLBACKaction(self, action1=None):
		self.buttonConfirmProvisionUnifiDeviceConllerCALLBACK(action1.props)

	def buttonConfirmProvisionUnifiDeviceConllerCALLBACK(self, valuesDict=None, typeId="", devId=""):
		mac = valuesDict["selectedUnifiDeviceProvision"]
		if not self.isValidMAC(mac): 
			valuesDict["MSG"] = "no valid mac given:{}".format(mac)
			return valuesDict
		valuesDict["MSG"] = "Provision command send to:{}".format(mac)
		dataDict = {'cmd':'force-provision','mac':mac}
		page = "/cmd/devmgr"
		ret = self.executeCMDOnController(dataSEND=dataDict, pageString=page, cmdType="post", cmdTypeForce=True, repeatIfFailed=False)
		self.indiLOG.log(20,"provision cmd: return  {}".format(ret) )
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
		if "fileNameOfImage" in pluginProps:
			if len(self.changedImagePath) > 5:
				pluginProps["fileNameOfImage"] = self.changedImagePath+"nameofCamera.jpeg"
			else:
				pluginProps["fileNameOfImage"] = self.indigoPreferencesPluginDir+"nameofCamera.jpeg"
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
		self.menuXML ={}
		if menuId == "CameraActions" and ("fileNameOfImage" not in self.menuXML or len(self.menuXML["fileNameOfImage"]) <10 ):
			if len(self.changedImagePath) > 5:
				self.menuXML["fileNameOfImage"] = self.changedImagePath+"nameofCamera.jpeg"
			else:
				self.menuXML["fileNameOfImage"] = "/tmp/nameofCamera.jpeg"
		self.menuXML["snapShotTextMethod"] = self.imageSourceForSnapShot
		self.menuXML["fileNameOfImage"] = self.completePath(self.changedImagePath)+"snapshot.jpeg"
		self.menuXML["MSG"] = ""
		

		for item in self.menuXML:
			valuesDict[item] = self.menuXML[item]
		errorsDict = indigo.Dict()
		#self.indiLOG.log(20,"getMenuActionConfigUiValues - menuId:{}".format(menuId))
		return (valuesDict, errorsDict)



########  check if we have new unifi system devces, if yes: litt basic variables and request a reboot
	####-----------------	 ---------
	def checkForNewUnifiSystemDevices(self):
		try:
			if self.checkForNewUnifiSystemDevicesEvery == 0:	 	return
			if self.checkforUnifiSystemDevicesState == "": 			return
			if self.checkforUnifiSystemDevicesState == "reboot": 	return
			if self.unifiCloudKeyMode != "ON":			 		
				self.checkforUnifiSystemDevicesState  = ""
				return

			self.indiLOG.log(10,"checkForNewUnifiSystemDevices   due to: {}".format(self.checkforUnifiSystemDevicesState))
			self.checkforUnifiSystemDevicesState  = ""

			newDeviceFound = []

			deviceDict =		self.executeCMDOnController( pageString="/stat/device/", jsonAction="returnData", cmdType="get")
			if self.decideMyLog("DictFile"): 
				self.writeJson( deviceDict, fName="{}dict-Controller.json".format(self.indigoPreferencesPluginDir), sort=False, doFormat=True )

			if deviceDict == []: return

			devType =""
			counter = 0
			for device in deviceDict:
				counter +=1
				ipNumber = ""
				MAC		 = ""
				if "type"   not in device: continue
				uType	 = device["type"]
				uModel	 = device.get("model","")

				if uType == "ugw":
					if "network_table" in device:
						for nwt in device["network_table"]:
							if "mac" in nwt and "ip"  in nwt and "name" in nwt and nwt["name"].lower() == "lan":
								ipNumber = nwt["ip"]
								MAC		 = nwt["mac"]
								break

				#### do not handle UDM type devices (yet)
				elif uType.find("udm") > -1:
					continue

				else:
					if "mac" in device and "ip" in device:
						ipNumber = device["ip"]
						MAC		 = device["mac"]

				if MAC == "" or ipNumber == "":
					continue

				found = False
				name = "--"

				for dev in indigo.devices.iter("props.isAP,props.isSwitch,props.isGateway"):
					if "MAClan" in dev.states and dev.states["MAClan"] == MAC:
						found = True
						name = dev.name
						break
					if "MAC" in dev.states and dev.states["MAC"] == MAC:
						found = True
						name = dev.name
						break
						## found devce no action



				if uType.find("usw") > -1: # check for miniswitches, they can not be ssh-ed, only info is in controller db
					for i in range(len(self.ipNumbersOf["SW"])):
						if not self.isMiniSwitch[i]: 						continue 
						if ipNumber != self.ipNumbersOf["SW"][i]: 			continue
						if not self.isValidIP(self.ipNumbersOf["SW"][i]): 	continue
						self.doMimiTypeSwitchesWithControllerData(device, i, found)
						break


				if not found:

					if uType.find("uap") >-1:
						for i in range(len(self.ipNumbersOf["AP"])):
							if	not self.isValidIP(self.ipNumbersOf["AP"][i]):
								newDeviceFound.append("uap: , new {}     existing: {}".format(ipNumber, self.ipNumbersOf["AP"][i]) )
								self.ipNumbersOf["AP"][i]					= ipNumber
								self.pluginPrefs["ip{}".format(i)]			= ipNumber
								self.pluginPrefs["ipON{}".format(i)]		= True
								self.checkforUnifiSystemDevicesState		= "reboot"
								newDeviceFound.append("uap: {}".format(i)+", "+ipNumber)
								break
							else:
								if self.ipNumbersOf["AP"][i]	 == ipNumber:
									if not self.devsEnabled["AP"][i]: break # we know this one but it is disabled on purpose
									newDeviceFound.append("uap: , new {}     existing: {}".format(ipNumber, self.ipNumbersOf["AP"][i] ) )
									self.ipNumbersOf["AP"][i]				= ipNumber
									#self.devsEnabled["AP"][i]						= True # will be enabled after restart
									self.pluginPrefs["ipON{}".format(i)]	= True
									self.checkforUnifiSystemDevicesState	= "reboot"
									newDeviceFound.append("uap: {}".format(i)+", "+ipNumber)
									break

					elif uType.find("usw") >-1:
						for i in range(len(self.ipNumbersOf["SW"])):
							self.isMiniSwitch[i] = uModel.find("MINI") > -1	

							if	not self.isValidIP(self.ipNumbersOf["SW"][i] ):
								newDeviceFound.append("usw: , new {}     existing: {}, isMiniSw?:{}".format(ipNumber, self.ipNumbersOf["SW"][i], self.isMiniSwitch[i]  ))
								self.ipNumbersOf["SW"][i]					= ipNumber
								self.pluginPrefs["ipSW{}".format(i)]		= ipNumber
								self.pluginPrefs["ipSWON{}".format(i)]		= True
								self.pluginPrefs["isMini{}".format(i)]		= self.isMiniSwitch[i] 
								self.checkforUnifiSystemDevicesState		= "reboot"
								break
							else:
								if self.ipNumbersOf["SW"][i] == ipNumber:
									if not self.devsEnabled["SW"][i]: break # we know this one but it is disabled on purpose
									newDeviceFound.append("usw: , new {}     existing: {}, isMiniSw?:{}".format(ipNumber, self.ipNumbersOf["SW"][i], self.isMiniSwitch[i]  ))
									self.ipNumbersOf["SW"][i]				= ipNumber
									#self.devsEnabled["SW"][i]						= True # will be enabled after restart
									self.pluginPrefs["ipSWON{}".format(i)]	= True
									self.checkforUnifiSystemDevicesState	= "reboot"
									self.pluginPrefs["isMini{}".format(i)]	= self.isMiniSwitch[i] 
									break

					elif uType.find("ugw") >-1:
							#### "ip" in the dict is the ip number of the wan connection NOT the inernal IP for the gateway !!
							#### using 2 other places instead to get the LAN IP
							if	not self.isValidIP(self.ipNumbersOf["GW"]):
								newDeviceFound.append("ugw: , new {}     existing: {}".format(ipNumber, self.ipNumbersOf["GW"]) )
								self.ipNumbersOf["GW"]						= ipNumber
								self.pluginPrefs["ipUGA"]					= ipNumber
								self.pluginPrefs["ipUGAON"]					= True
								self.checkforUnifiSystemDevicesState		= "reboot"
							else:
								if not self.devsEnabled["GW"]: break # we know this one but it is disabled on purpose
								if self.ipNumbersOf["GW"] != ipNumber:
									newDeviceFound.append("ugw: , new {}     existing: {}".format(ipNumber, self.ipNumbersOf["GW"]) )
									self.ipNumbersOf["GW"]					= ipNumber
									self.pluginPrefs["ipUGA"]				= ipNumber
									self.pluginPrefs["ipUGAON"]			= True
									self.checkforUnifiSystemDevicesState	= "reboot"
								else:
									newDeviceFound.append("ugw:	 , new {}     existing: {}".format(ipNumber, self.devsEnabled["GW"]) )
									self.pluginPrefs["ipUGAON"]			= True
									self.checkforUnifiSystemDevicesState	= "reboot"

			if self.checkforUnifiSystemDevicesState == "reboot":
				try:
					self.pluginPrefs["createUnifiDevicesCounter"] = int(self.pluginPrefs["createUnifiDevicesCounter"] ) +1
					if int(self.pluginPrefs["createUnifiDevicesCounter"] ) > 1: # allow only 1 unsucessful try, then wait 10 minutes
						self.checkforUnifiSystemDevicesState		   = ""
					else:
						self.indiLOG.log(30,"Connection   reboot required due to new UNIFI system device found:{}".format(newDeviceFound))
				except:
						self.checkforUnifiSystemDevicesState		   = ""
			try:	indigo.server.savePluginPrefs()
			except: pass

			if self.checkforUnifiSystemDevicesState =="":
				self.pluginPrefs["createUnifiDevicesCounter"] = 0

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		return




	####-----------------	 --------- This one is not working .. disabled in menu
	def executeMCAconfigDumpOnGW(self, valuesDict=None,typeId="" ):
		keepList=["vpn","port-forward","service:radius-server","service:dhcp-server"]
		jsonAction="print"
		ret =[]
		if self.connectParams["commandOnServer"]["GWctrl"].find("off") == 0: return valuesDict
		try:
			cmd = self.expectPath +" "
			cmd += "'"+self.pathToPlugin + self.connectParams["expectCmdFile"]["GWctrl"] + "' " 
			cmd += "'"+self.connectParams["UserID"]["unixDevs"]+ "' '"+self.connectParams["PassWd"]["unixDevs"]+ "' " 
			cmd += self.ipNumbersOf["GW"] + " " 
			cmd += "'"+self.connectParams["promptOnServer"][self.ipNumbersOf["GW"]] + "' " 
			cmd += " XXXXsepXXXXX " + " " 
			cmd += "\""+self.escapeExpect(self.connectParams["promptOnServer"][self.ipNumbersOf["GW"]])+"\""
			cmd +=  self.getHostFileCheck()

			if self.decideMyLog("Expect"): self.indiLOG.log(10," UGA EXPECT CMD: {}".format(cmd))
			ret, err = self.readPopen(cmd)
			if self.decideMyLog("ExpectRET"): self.indiLOG.log(10,"returned from expect-command: {}".format(ret))
			dbJson, error= self.makeJson2(ret, "XXXXsepXXXXX")
			outLine = ""
			if jsonAction == "print":
				for xx in keepList:
					if xx.find(":") >-1:
						yy = xx.split(":")
						if yy[0] in dbJson and yy[1] in dbJson[yy[0]]:
							short = dbJson[yy[0]][yy[1]]
							if yy[1] =="dhcp-server":
								for z in short:
									if z =="shared-network-name":
										for zz in short[z]:
											for zzz in short[z][zz]: # net_LAN_192.168.1.0-24"
												if zzz =="subnet":
													for zzzz in short[z][zz][zzz]:	# "192.168.1.0/24"
														for zzzzz in short[z][zz][zzz][zzzz]:
															if zzzzz =="static-mapping":
																s0 = short[z][zz][zzz][zzzz][zzzzz]
																## need to sort
																u =[]
																v =[]
																for t in s0:
																	u.append((s0[t]["mac-address"],s0[t]["ip-address"]))
																	v.append((self.fixIP(s0[t]["ip-address"]),s0[t]["ip-address"],s0[t]["mac-address"]))

																sortMacKey = sorted(u)
																sortIPKey  = sorted(v)
																out = "     static DHCP mappings:\n"
																for m in range(len(sortMacKey)):
																	out += sortMacKey[m][0]+" --> "+ sortMacKey[m][1].ljust(20)+"        " +sortIPKey[m][1].ljust(18)+"--> "+ sortIPKey[m][2]+"\n"
																outLine += "\n==== UGA-setup ==== {}".format(out)
							else:
								outLine += "\n==== UGA-setup ====     {}:\n{}".format(xx,json.dumps(short,sort_keys=True,indent=2))
						else:
							outLine += "\n==== UGA-setup ==== {} not in json returned from UGA".format(xx)
					else:
						if xx in dbJson:
							outLine += "\n==== UGA-setup ====     {}:\n{}".format(xx,json.dumps(dbJson[xx],sort_keys=True,indent=2))
						else:
							outLine += "\n==== UGA-setup ====  not in json returned from UGA"
				self.indiLOG.log(20,outLine)
			else:
				return valuesDict


		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return valuesDict



	####-----------------	 ---------
	def getunifiOSAndPort(self):
		try:
			if self.overWriteControllerPort != "":
				if self.unifControllerCheckPortNumber == "0": 
					respCode = "200"
					self.unifiControllerOS = self.HTTPretCodes[respCode]["os"]
					self.unifiApiLoginPath = self.HTTPretCodes[respCode]["unifiApiLoginPath"]
					self.unifiApiWebPage   = self.HTTPretCodes[respCode]["unifiApiWebPage"]
					self.unifiCloudKeyPort = self.overWriteControllerPort
					self.lastPortNumber	   = self.overWriteControllerPort
					return True

				else:
					if self.unifiControllerOS != "" and self.lastPortNumber	!= "": 
						return True

					cmd = "https://{}:{}".format(self.unifiCloudKeyIP, self.overWriteControllerPort)
					if self.decideMyLog("ConnectionCMD"): self.indiLOG.log(20,"getunifiOSAndPort cmd:{}".format(cmd) )
					resp = requests.head(cmd, verify=False, timeout=self.requestTimeout)

				respCode = str(resp.status_code)
				if respCode in ["200", "302"]:
					if self.decideMyLog("ConnectionCMD"): self.indiLOG.log(20,"getunifiOSAndPort sucess: {}:{} ==>  osCode:{}, OS:{}".format(self.unifiCloudKeyIP,self.overWriteControllerPort, respCode, self.HTTPretCodes[respCode]["os"]))
					self.unifiControllerOS = self.HTTPretCodes[respCode]["os"]
					self.unifiApiLoginPath = self.HTTPretCodes[respCode]["unifiApiLoginPath"]
					self.unifiApiWebPage   = self.HTTPretCodes[respCode]["unifiApiWebPage"]
					self.unifiCloudKeyPort = self.overWriteControllerPort
					self.lastPortNumber	   = self.overWriteControllerPort
					return True

				self.indiLOG.log(40,"getunifiOSAndPort {}: no contact to controller using overWriteControllerPort".format(self.unifiCloudKeyIP, self.overWriteControllerPort))
				return False


			if self.unifiControllerType == "hosted":
				ret = "302"
				if self.unifiApiLoginPath  == "" or self.unifiApiWebPage == "" or  self.unifiControllerOS == "": logmsg = True
				else: logmsg = False
				self.unifiCloudKeyPort = self.overWriteControllerPort
				self.unifiControllerOS = self.HTTPretCodes[ret]["os"]
				self.unifiApiLoginPath = self.HTTPretCodes[ret]["unifiApiLoginPath"]
				self.unifiApiWebPage   = self.HTTPretCodes[ret]["unifiApiWebPage"]
				if logmsg:
					self.indiLOG.log(10,"getunifiOSAndPort setting OS:{}, port#:{} using ip#:{}, loginpath:{}, wepAPipAge:{}".format(self.unifiControllerOS, self.unifiCloudKeyPort, self.unifiCloudKeyIP, self.unifiApiLoginPath, self.unifiApiWebPage) )
				return True				

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
				self.indiLOG.log(10,"getunifiOSAndPort existing  os>{}< .. ip#>{}< .. trying ports>{}<".format( self.unifiControllerOS, self.unifiCloudKeyIP, tryport ) )
				self.executeCMDOnControllerReset(calledFrom="getunifiOSAndPort")

				for port in tryport:
					# this cmd will return http code only (I= header only, -s = silent -o send std to null, -w print http reply code)
					# curl --insecure  -I -s -o /dev/null -w "%{http_code}" 'https://192.168.1.2:8443'
					cmdOS = self.curlPath+" --max-time {:.0f}".format(self.requestTimeout)+" --insecure  -I -s -o /dev/null -w \"%{http_code}\" 'https://"+self.unifiCloudKeyIP+":"+port+"'"
					ret, err = self.readPopen(cmdOS)
					if self.decideMyLog("ConnectionCMD"): self.indiLOG.log(10,"getunifiOSAndPort trying port#:>{}< gives ret code:{}".format(cmdOS, ret) )
					if ret in self.HTTPretCodes: 
						self.unifiCloudKeyPort = port
						self.lastPortNumber	   = port
						self.unifiControllerOS = self.HTTPretCodes[ret]["os"]
						self.unifiApiLoginPath = self.HTTPretCodes[ret]["unifiApiLoginPath"]
						self.unifiApiWebPage   = self.HTTPretCodes[ret]["unifiApiWebPage"]
						self.indiLOG.log(10,"getunifiOSAndPort found  OS:{}, port#:{} using ip#:{}".format(self.unifiControllerOS, port, self.unifiCloudKeyIP) )
						return True
					else:
						self.indiLOG.log(10,"getunifiOSAndPort trying port:{}, wrong ret code from curl test>{}< expecting {}, for contoller os >= 6.5.55 set port to 443 and checkcontroller port to OFF".format(port, ret, self.HTTPretCodes) )

				self.sleep(1)
				
			if self.unifiControllerOS == "": 
				self.indiLOG.log(30,"getunifiOSAndPort bad return from unifi controller {}, no os and / port found, tried ports:{}".format(self.unifiCloudKeyIP, tryport) )

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
			self.indiLOG.log(40,"getunifiOSAndPort ret:\n>>{}<<".format("{}".format(ret)[0:100]) )
		return False


	####-----------------	 ---------
	def executeCMDOnControllerReset(self, wait=False, calledFrom=""):
		try:
			if calledFrom != "":
				if self.decideMyLog("Protect"): self.indiLOG.log(10,"executeCMDOnControllerReset called from:{}".format(calledFrom) )
			if self.unifiControllerSession != "":
				try: self.unifiControllerSession.close()
				except: pass
			self.unifiControllerSession = ""
			self.unifiControllerOS = ""
			self.lastUnifiCookieRequests = 0.
			self.lastUnifiCookieCurl = 0	
			self.unifiCloudKeySiteNameGetNew = True
			if wait: self.sleep(2.0)	
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)


	####-----------------	 ---------
	def setunifiCloudKeySiteName(self, method="response", cookies="", headers="" ):
		try:
			if self.unifiControllerType == "hosted":
				self.indiLOG.log(10,"setunifiCloudKeySiteName set site name to default")
				self.unifiCloudKeySiteName = "default"
				return True

			elif method == "response":
				urlSite	= "https://"+self.unifiCloudKeyIP+":"+self.unifiCloudKeyPort+"/proxy/network/api/self/sites"
				ret	= self.unifiControllerSession.get(urlSite, cookies=cookies,  headers=headers, timeout=self.requestTimeout, verify=False).text
				# should get: {"meta":{"rc":"ok"},"data":[{"_id":"5750f2ade4b04dab3d3d0d4f","name":"default","desc":"stanford","attr_hidden_id":"default","attr_no_delete":true,"role":"admin","role_hotspot":false}]}

			elif method == "curl":
				cmdSite  = self.curlPath+" --max-time {:.0f}".format(self.requestTimeout)+" --insecure  'https://"+self.unifiCloudKeyIP+":"+self.unifiCloudKeyPort+"/api/self/sites'"
				#cmdSite  = self.curlPath+" --max-time {:.0f}".format(self.requestTimeout)+" 'https://"+self.unifiCloudKeyIP+":"+self.unifiCloudKeyPort+"/api/self/sites'"
				if self.decideMyLog("ConnectionCMD"):self.indiLOG.log(10,"setunifiCloudKeySiteName cmd:{}".format(cmdSite))
				ret, err = self.readPopen(cmdSite)
				# should get: {"meta":{"rc":"ok"},"data":[{"_id":"5750f2ade4b04dab3d3d0d4f","name":"default","desc":"stanford","attr_hidden_id":"default","attr_no_delete":true,"role":"admin","role_hotspot":false}]}

			else:
				return False

			if self.decideMyLog("ConnectionRET"):self.indiLOG.log(10,"setunifiCloudKeySiteName ret text:{}".format("{}".format(ret)))

			try:
				dictRET = json.loads(ret)
			except :
				self.indiLOG.log(30,"setunifiCloudKeySiteName for {} has error, getting site ID, no json object returned: >>{}<<".format(self.unifiCloudKeyIP, "{}".format(ret)))
				self.executeCMDOnControllerReset(wait=True, calledFrom="setunifiCloudKeySiteName1")
				return False
		
				
			oneFound = False
			if "meta" in dictRET and "rc" in dictRET["meta"] and dictRET["meta"]["rc"] == "ok" and "data" in dictRET:
				if len(dictRET["data"]) >0:
					for site in dictRET["data"]:
						if "name" in site:
							if not oneFound: 
								self.unifiCloudKeyListOfSiteNames = []
								oneFound = True
							if site["name"] not in self.unifiCloudKeyListOfSiteNames:
								self.unifiCloudKeyListOfSiteNames.append(site["name"])

					if self.unifiCloudKeyListOfSiteNames != []:
						if self.unifiCloudKeySiteName not in self.unifiCloudKeyListOfSiteNames:
							if self.unifiCloudKeySiteName =="":
								self.indiLOG.log(20,"setunifiCloudKeySiteName setting site id name to >>{}<<, was empty, available list:{}".format(self.unifiCloudKeyListOfSiteNames[0],  self.unifiCloudKeyListOfSiteNames))
							else:
								self.indiLOG.log(20,"setunifiCloudKeySiteName overwriting site id name with >>{}<<, was {}, available list:{}".format(self.unifiCloudKeyListOfSiteNames[0], self.unifiCloudKeySiteName,  self.unifiCloudKeyListOfSiteNames))
							self.unifiCloudKeySiteName = self.unifiCloudKeyListOfSiteNames[0]
						self.pluginPrefs["unifiCloudKeySiteName"] = self.unifiCloudKeySiteName 
						self.pluginPrefs["unifiCloudKeyListOfSiteNames"] = json.dumps(self.unifiCloudKeyListOfSiteNames)
						return True
					else:
						self.indiLOG.log(20,"setunifiCloudKeySiteName setting site id name returned empty")
						return False


			self.indiLOG.log(20,"setunifiCloudKeySiteName  id  not found ret:>>{}<<".format(ret))
			self.executeCMDOnControllerReset(wait=True,  calledFrom="setunifiCloudKeySiteName2")
			return False

		except	Exception as e:
			self.indiLOG.log(40,"setunifiCloudKeySiteName: " )
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		self.executeCMDOnControllerReset(wait=True,  calledFrom="setunifiCloudKeySiteName3")
		return False



	####-----------------	 ---------
	def executeCMDOnController(self, dataSEND={}, pageString="",jsonAction="returnData", startText="", cmdType="put", cmdTypeForce = False, repeatIfFailed=True, raw=False, protect=False, ignore40x=False):

		try:
			if self.unifiControllerType == "off": 					return []
			if self.unifiCloudKeyMode   == "off":					return []
			if not self.isValidIP(self.unifiCloudKeyIP): 			return []
			if len(self.connectParams["UserID"]["webCTRL"]) < 2: 	return []
			if self.unifiCloudKeyMode.find("ON") == -1 and self.unifiCloudKeyMode != "UDM": return []

			for iii in range(2):
				if not repeatIfFailed and iii > 0: return []
				if iii == 1: self.sleep(0.2)

				# get port and which unifi os:
				if not self.getunifiOSAndPort(): 
					self.executeCMDOnControllerReset(wait=False)
					return []
				if self.unifiControllerOS not in self.OKControllerOS:
					if self.decideMyLog("ConnectionCMD"): self.indiLOG.log(10,"unifiControllerOS not set : {}".format(self.unifiControllerOS) )
					return []

				# now execute commands
				#### use curl if ...
				useCurl = self.requestOrcurl.find("curl") > -1 and self.unifiControllerOS == "std"

				if useCurl:
					#cmdL  = curl  --insecure -c /tmp/unifiCookie -H "Content-Type: application/json"  --data '{"username":"karlwachs","password":"457654aA.unifi"}' https://192.168.1.2:8443/api/login
					#cmdL  = self.curlPath+" --max-time {:.0f}".format(self.requestTimeout)+" --insecure -c /tmp/unifiCookie --data '"                                      +json.dumps({"username":self.connectParams["UserID"]["webCTRL"],"password":self.connectParams["PassWd"]["webCTRL"]})+"' 'https://"+self.unifiCloudKeyIP+":"+self.unifiCloudKeyPort+"/api/login'"
					cmdLogin  = self.curlPath+" --max-time {:.0f}".format(self.requestTimeout)+" --max-time {:.0f}".format(self.requestTimeout)+" --insecure -c /tmp/unifiCookie -H \"Content-Type: application/json\" --data '"+json.dumps({"username":self.connectParams["UserID"]["webCTRL"],"password":self.connectParams["PassWd"]["webCTRL"],"strict":self.useStrictToLogin})+"' 'https://"+self.unifiCloudKeyIP+":"+self.unifiCloudKeyPort+self.unifiApiLoginPath+"'"
					if dataSEND =={}: 	dataSendSTR = ""
					else:		 		dataSendSTR = " --data '"+json.dumps(dataSEND)+"' "
					if	 cmdType == "put":	 						cmdTypeUse= " -X PUT "
					elif cmdType == "post":	  					cmdTypeUse= " -X POST "
					elif cmdType == "get":	  						cmdTypeUse= " " # 
					else:					 						cmdTypeUse= " ";	cmdType = "get"
					if not cmdTypeForce: cmdTypeUse = " "
					if self.unifiControllerType.find("UDM") >-1 and cmdType == "get":	cmdTypeUse = " " 



					if self.decideMyLog("ConnectionCMD"): self.indiLOG.log(10,"executeCMDOnController: {}".format(cmdLogin) )
					try:
						if time.time() - self.lastUnifiCookieCurl > 100: # re-login every 90 secs
							respText, errText = self.readPopen(cmdLogin)
							try: loginDict = json.loads(respText)
							except:
								if iii == 0:
									self.indiLOG.log(40,"UNIFI executeCMDOnController error no json object: (wrong UID/passwd, ip number?{}) ...>>{}<<\n{}".format(self.unifiCloudKeyIP,respText,errText))
									self.executeCMDOnControllerReset(wait=True)
								continue
							if   ( "meta" not in loginDict or  loginDict["meta"]["rc"] != "ok"):
								if iii == 0:
									self.indiLOG.log(40,"UNIFI executeCMDOnController  login cmd:{}\ngives  error: {}\n {}".format(cmdLogin, respText,errText) )
								self.executeCMDOnControllerReset(wait=True)
								continue
							if self.decideMyLog("ConnectionRET"):	 self.indiLOG.log(10,"Connection-{}: {}".format(self.unifiCloudKeyIP,respText) )
							self.lastUnifiCookieCurl = time.time()



						if self.unifiCloudKeySiteName == "" or self.unifiCloudKeySiteNameGetNew:
							if not self.setunifiCloudKeySiteName(method="curl"): continue

						if self.unifiCloudKeySiteName == "": continue
						self.unifiCloudKeySiteNameGetNew = False


						if self.unifiCloudKeySiteName == "":
							if not self.setunifiCloudKeySiteName(method = "curl"): continue

						#cmdDATA  = curl  --insecure -b /tmp/unifiCookie' --data '{"within":999,"_limit":1000}' https://192.168.1.2:8443/api/s/default/stat/event
						cmdDATA  = self.curlPath+" --max-time {:.0f}".format(self.requestTimeout)+" --insecure -b /tmp/unifiCookie " +dataSendSTR+cmdTypeUse+ " 'https://"+self.unifiCloudKeyIP+":"+self.unifiCloudKeyPort+self.unifiApiWebPage+"/"+self.unifiCloudKeySiteName+"/"+pageString.strip("/")+"'"

						if self.decideMyLog("ConnectionCMD"):	self.indiLOG.log(10,"Connection: {}".format(cmdDATA) )
						if startText != "":					 	self.indiLOG.log(10,"Connection: {}".format(startText) )
						try:
							ret = subprocess.Popen(cmdDATA, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
							respText = ret[0]#.decode("utf8")
							errText  = ret[1]#.decode("utf8")
							try:
								dictRET = json.loads(respText)
							except:
								if iii > 0:
									if "{}".format(e).find("None") == -1: 
										self.indiLOG.log(30,"", exc_info=True)
										self.indiLOG.log(30,"UNIFI executeCMDOnController to {} curl errortext:{}".format(self.unifiCloudKeyIP, errText))
										self.printHttpError("{}".format(e), respText, ind=iii)
									self.executeCMDOnControllerReset(wait=True, calledFrom="executeCMDOnController-curl json")
								continue

							if dictRET["meta"]["rc"] != "ok":
								if iii == 0:
									self.indiLOG.log(40," Connection error: >>{}<<\n{}".format(self.unifiCloudKeyIP, respText, errText))
								self.executeCMDOnControllerReset(wait=True, calledFrom="executeCMDOnController-curl dict not ok")
								continue

							if self.decideMyLog("ConnectionRET"):
									self.indiLOG.log(10,"Connection to {}: returns >>{}<<".format(self.unifiCloudKeyIP, respText) )

							if  jsonAction == "print":
								self.indiLOG.log(10," Connection to:{} info\n{}".format(self.unifiCloudKeyIP, json.dumps(dictRET["data"],sort_keys=True, indent=2)))
								return []

							if  jsonAction == "returnData":
								#self.writeJson(dictRET["data"], fName=self.indigoPreferencesPluginDir+"dict-Controller-"+pageString.replace("/","_").replace(" ","-").replace(":","=").strip("_")+".txt", sort=True, doFormat=True )
								return dictRET["data"]
							if  jsonAction == "protect":
								#self.writeJson(dictRET["data"], fName=self.indigoPreferencesPluginDir+"dict-Controller-"+pageString.replace("/","_").replace(" ","-").replace(":","=").strip("_")+".txt", sort=True, doFormat=True )
								return dictRET

							return []

						except	Exception as e:
							if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
					except	Exception as e:
						if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)


				############# does not work on OSX	el capitan ssl lib too old	##########
				if not useCurl:

					if self.unifiControllerSession == "" or (time.time() - self.lastUnifiCookieRequests) > 99: # every 99 secs token cert
						if self.unifiControllerSession != "":
							try: 	self.unifiControllerSession.close()
							except: pass
							self.unifiControllerSession = ""

						if self.unifiControllerSession == "":
							self.unifiControllerSession	 = requests.Session()

						url = "https://"+self.unifiCloudKeyIP+":"+self.unifiCloudKeyPort+self.unifiApiLoginPath
						loginHeaders = {"Accept": "application/json", "Content-Type": "application/json", "referer": "/login"}
						dataLogin = json.dumps({"username":self.connectParams["UserID"]["webCTRL"],"password":self.connectParams["PassWd"]["webCTRL"]}) #  , "strict":self.useStrictToLogin})
						if self.decideMyLog("ConnectionCMD"): self.indiLOG.log(10,"Connection: requests login url:{};\ndataLogin:{};\nloginHeaders:{};".format(url, dataLogin, loginHeaders) )

						resp  = self.unifiControllerSession.post(url,  headers=loginHeaders, data = dataLogin, timeout=self.requestTimeout, verify=False)
						if self.decideMyLog("ConnectionRET"): self.indiLOG.log(10,"Connection: requests login code:{}; ret-Text:\n {} ...".format(resp.status_code, resp.text) )

						try: loginDict = json.loads(resp.text)
						except	Exception as e:
							if "{}".format(e).find("timed out") > -1:
									self.indiLOG.log(40," read timed out to {}".format(url))
									continue
							else:
								if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

							self.indiLOG.log(30,"UNIFI executeCMDOnController error no json object: (wrong UID/passwd, ip number?{}) ...>>{}<<".format(self.unifiCloudKeyIP, resp.text))
							self.executeCMDOnControllerReset(wait=True, calledFrom="executeCMDOnController-login json")
							continue

						if  resp.status_code != requests.codes.ok:
							self.failedControllerLoginCount += 1 
							self.indiLOG.log(30,"UNIFI executeCMDOnController  LOGIN failed ({} times), will try again; url:{}, >>ok<< not found,  or status_code:{} not in >>{}<<\n  error: >>{}<<\n".format(self.failedControllerLoginCount , url,resp.status_code, requests.codes.ok, resp.text[0:300]) )
							self.executeCMDOnControllerReset(wait=True, calledFrom="executeCMDOnController-login ret code not ok")
							self.sleep(2)
							if self.failedControllerLoginCount > self.failedControllerLoginCountMax: 		
								self.quitNOW = "restart due to failed Controller Login count  > {}".format(self.failedControllerLoginCount )
								return []
								
							continue
						if 'X-CSRF-Token' in resp.headers:
							self.csrfToken = resp.headers['X-CSRF-Token']
				

						self.lastUnifiCookieRequests = time.time()
		
					if self.unifiControllerSession == "": 
						self.executeCMDOnControllerReset(wait=False, calledFrom="executeCMDOnController-unifiControllerSession = blank")
						if self.decideMyLog("Protect"): self.indiLOG.log(10,"Connection: session =blank, continue ")
						continue

					headers = {"Accept": "application/json", "Content-Type": "application/json"}
					if self.csrfToken != "":
						headers['X-CSRF-Token'] = self.csrfToken


					cookies_dict = requests.utils.dict_from_cookiejar(self.unifiControllerSession.cookies)
					if self.unifiControllerOS == "unifi_os":
						cookies = {"TOKEN": cookies_dict.get('TOKEN')}
					else:
						cookies = {"unifises": cookies_dict.get('unifises'), "csrf_token": cookies_dict.get('csrf_token')}
					if self.decideMyLog("ConnectionCMD"):	self.indiLOG.log(10,"Connection: unifiControllerOS:{}, unifiControllerSession>>>{}<<<".format(self.unifiControllerOS, str(self.unifiControllerSession)) )


					if self.unifiCloudKeySiteName == "" or self.unifiCloudKeySiteNameGetNew:
						if not self.setunifiCloudKeySiteName(method="response", cookies=cookies, headers=headers ): continue

					if self.unifiCloudKeySiteName == "": continue
					self.unifiCloudKeySiteNameGetNew = False

					if self.failedControllerLoginCount  > 0:
						self.indiLOG.log(30,"UNIFI executeCMDOnController  LOGIN fixed after #{} tries ".format(self.failedControllerLoginCount ) )
					self.failedControllerLoginCount = 0
				
					if protect:
						url = "https://"+self.unifiCloudKeyIP+":"+self.unifiCloudKeyPort+"/proxy/protect/"+pageString.strip("/")
					else:
						url = "https://"+self.unifiCloudKeyIP+":"+self.unifiCloudKeyPort+self.unifiApiWebPage+"/"+self.unifiCloudKeySiteName+"/"+pageString.strip("/")

					if self.decideMyLog("ConnectionCMD"):	self.indiLOG.log(10,"Connection: requests:{};\nheader:{};\ndataSEND:{};\ncookies:{};\ncmdType:{}".format(url, headers, dataSEND, cookies,cmdType) )
					if startText !="":						self.indiLOG.log(10,"Connection: requests: startText{},".format(startText) )
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

							try:
								if	 cmdType == "put":	resp = self.unifiControllerSession.put(url,  	json=dataSEND,		cookies=cookies, headers=headers, allow_redirects=False, verify=False, timeout=self.requestTimeout, stream=setStream)
								elif cmdType == "post":	resp = self.unifiControllerSession.post(url, 	json=dataSEND,		cookies=cookies, headers=headers, allow_redirects=False, verify=False, timeout=self.requestTimeout, stream=setStream)
								elif cmdType == "get":	
									if dataSEND == {}:
														resp =	self.unifiControllerSession.get(url,						cookies=cookies, headers=headers, allow_redirects=False, verify=False, timeout=self.requestTimeout, stream=setStream)
									else:
										if protect: # get protect needs params= not json=
														resp =	self.unifiControllerSession.get(url, 	params=dataSEND,	cookies=cookies, headers=headers, verify=False, timeout=self.requestTimeout, stream=setStream)
														if setStream: 
															rawData = resp.raw.read()
															#self.indiLOG.log(10,"executeCMDOnController protect  url:{} params:{}; stream:{}, len(resp.raw.read):{}".format(url, dataSEND, setStream, len(rawData) ))
										else:
														resp =	self.unifiControllerSession.get(url, 	json=dataSEND,		cookies=cookies, headers=headers, allow_redirects=False, verify=False, timeout=self.requestTimeout, stream=setStream)

								elif cmdType == "patch":resp = self.unifiControllerSession.patch(url,	json=dataSEND,		cookies=cookies, headers=headers, allow_redirects=False, verify=False, timeout=self.requestTimeout, stream=setStream)
								else:					resp = self.unifiControllerSession.put(url,   	json=dataSEND,		cookies=cookies, headers=headers, allow_redirects=False, verify=False, timeout=self.requestTimeout, stream=setStream)
								
							except	Exception as e:
								if "{}".format(e).find("timed out") > -1:
									self.indiLOG.log(40," read timed out to {}".format(url))
									continue
				
								if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
								continue

							try:
								retCode		= copy.copy(resp.status_code )
								respText 	= copy.copy(resp.text)
								retStatus	= resp.status_code
								##respText 	= respText.decode("utf8")
								timeused 	= resp.elapsed.total_seconds()	
								if self.decideMyLog("ConnectionRET"):	
									self.indiLOG.log(10,"executeCMDOnController retCode:{}, time used:{}; cont length:{} os:{}; cmdType:{}, url:{}\n>>>{}<<<".format(retCode, timeused, len(respText), self.unifiControllerOS, cmdType, url, respText))
								headers 	= copy.copy(resp.headers)

								if not raw:
									dictRET	= json.loads(respText)

								resp.close()
								
							except	Exception as e:
								if iii > 0:
									errText = "{}".format(e)
									if "{}".format(e).find("None") == -1: 
										self.indiLOG.log(30,"", exc_info=True)
										self.indiLOG.log(20,"executeCMDOnController has error, retCode:{}, time used:{}; cont length:{} os:{}; cmdType:{}, url:{}".format(retCode, timeused, len(respText), self.unifiControllerOS, cmdType, url))
										self.printHttpError(errText, respText)
								self.executeCMDOnControllerReset(wait=True, calledFrom="executeCMDOnController-exception after json/decode ..")
								try: resp.close()
								except: pass
								continue
 
							if protect:
								if retCode != requests.codes.ok:
									if iii == 1 and (not ignore40x or "{}".format(retCode).find("40") !=0):
										self.indiLOG.log(40,"error:>> url:{}, resp code:{}".format(url, retCode))
									if (not ignore40x or "{}".format(retCode).find("40") !=0): self.executeCMDOnControllerReset(wait=True, calledFrom="executeCMDOnController-retcode not ok")
									continue
							else:
								if dictRET["meta"]["rc"] != "ok":
									if iii == 1 and (not ignore40x or "{}".format(retCode).find("40") !=0):
										self.indiLOG.log(40,"error:>> url:{}, resp:{}".format(url, respText[0:100]))
									if  (not ignore40x or "{}".format(retCode).find("40") !=0): self.executeCMDOnControllerReset(wait=True, calledFrom="executeCMDOnController-dict ret not ok")
									continue

							self.lastUnifiCookieRequests = time.time()

							if 'X-CSRF-Token' in headers:
								self.csrfToken = headers['X-CSRF-Token']

							if  jsonAction == "print":
								self.indiLOG.log(10,"Reconnect: executeCMDOnController info\n{}".format(json.dumps(dictRET["data"], sort_keys=True, indent=2)) )
								return dictRET["data"]

							if raw:								return rawData
							elif jsonAction == "returnData":	return dictRET["data"]
							elif jsonAction == "protect":		return dictRET
							else:								return []

					except	Exception as e:
						if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

				## we get here when not successful
				self.executeCMDOnControllerReset(wait=True, calledFrom="executeCMDOnController-end-error")

			return []

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		self.executeCMDOnControllerReset(wait=False, calledFrom="executeCMDOnController-exception")
		return []



	####-----------------	   ---------
	def printHttpError(self, errtext, respText, ind=0):
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
							self.indiLOG.log(20,"executeCMDOnController Ind:{}  bad char >>{}<<;  @{} in\n {}...{}".format(ind, respText[cp:cp+20], charpos, respText[0:200], respText[-200:]))
							detected = True
					except: pass

			if not detected:
				self.indiLOG.log(20,"executeCMDOnController  resp:>>{}  ...  {}<<<".format(respText[0:200], respText[-200:]) )

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return


	####-----------------	   ---------
	def getSnapshotfromCamera(self, indigoCameraId, fileName):
		try:
			dev		= indigo.devices[int(indigoCameraId)]
			cmdR	= self.curlPath+" --max-time {:.0f}".format(self.requestTimeout) +" 'http://"+dev.states["ip"] +"/snap.jpeg' > "+ fileName
			if self.decideMyLog("Video"): self.indiLOG.log(10,"Video: getSnapshotfromNVR with: {}".format(cmdR) )
			respText, errText = self.readPopen(cmdR)
			if self.decideMyLog("Video"): self.indiLOG.log(10,"Video: getSnapshotfromCamera response: {}".format(respText))
			return "ok"
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
			return "error:{}".format(e)
		return " error"


	####-----------------	   ---------
	def getSnapshotfromNVR(self, indigoCameraId, width, fileName):

		try:
			camApiKey = indigo.devices[int(indigoCameraId)].states["apiKey"]
			url			= "http://"+self.ipNumbersOf["VD"] +":7080/api/2.0/snapshot/camera/"+camApiKey+"?force=true&width={}".format(width)+"&apiKey="+self.nvrVIDEOapiKey
			if self.requestOrcurl.find("curl") > -1:
				cmdR	= self.curlPath+" --max-time {:.0f}".format(self.requestTimeout)+" -o '" + fileName +"'  '"+ url+"'"
				try:
					if self.decideMyLog("Video"): self.indiLOG.log(10,"Video: {}".format(cmdR) )
					ret = subprocess.Popen(cmdR, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()[1]
					try:
						fs1	 = ""
						fs	 = 0
						fs0	 = ""
						unit = ""
						if ret.find("\r")> -1: ret = ret.split("\r")
						else:                  ret = ret.split("\n")
						fs0  = ret[-1] # last line
						fs1  = fs0.split()[-1] # last number
						unit = fs1[-1] # last char
						fs  = int(fs1.strip("k").strip("m").strip("M"))
					except: fs = 0
					if fs == 0:
						self.indiLOG.log(40,"getSnapshotfromNVR has error, no file returned,  Video error: \n{}\n{}".format(ret[1], cmdR))
						return "error, no file returned"
					return "ok, bytes transfered: {}{}".format(fs, unit)
				except	Exception as e:
					if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
				return "error:{}".format(e)

			else:
				session = requests.Session()

				if self.decideMyLog("Video"): self.indiLOG.log(10,"Video: getSnapshotfromNVR login with: {}".format(url) )

				resp	= session.get(url, stream=True)
				if self.decideMyLog("Video"): self.indiLOG.log(10,"Video: getSnapshotfromNVR response {}[kB]: {}; ".format(len(resp.content)/1024, resp.status_code) )
				if "{}".format(resp.status_code) == "200":
					f = self.openEncoding(fileName,"wb")
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
					return "ok, bytes transfered: {} {}".format(ll, unit)
				return "error {}".format(resp.status_code)
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return "error:{}".format(e)



	####-----------------	   ---------
	def groupStatusINIT(self):
		for gNumber in  range(_GlobalConst_numberOfGroups):
			varN = "Unifi_Count_{}_".format(self.groupNames[gNumber])
			for tType in ["Home","Away","lastChange"]:
				varName = varN+tType
				if varName not in self.varExcludeSQLList: self.varExcludeSQLList.append(varName)
				try:
					var = indigo.variables[varName]
				except:
					indigo.variable.create(varName,"0",folder=self.folderNameIDVariables)

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


			for groupNo in range(_GlobalConst_numberOfGroups):
				self.groupStatusList[groupNo]["nAway"] = 0
				self.groupStatusList[groupNo]["nHome"] = 0
			self.groupStatusListALL["nHome"] = 0
			self.groupStatusListALL["nAway"] = 0

			okList = {}


			for dev in indigo.devices.iter(self.pluginId):
				if "groupMember" not in dev.states: continue

				if dev.states["status"] == "up":
					self.groupStatusListALL["nHome"]	 +=1
				else:
					self.groupStatusListALL["nAway"]	 +=1

				if dev.states["groupMember"] == "": continue
				if not dev.enabled:	 continue
				okList["{}".format(dev.id)] = True
				props= dev.pluginProps
				gNames = (dev.states["groupMember"].strip(",")).split(",")
				for groupName in gNames:
					if groupName == "": continue
					if groupName in self.groupNames:
						groupNo = self.groupNames.index(groupName)
						self.groupStatusList[groupNo]["members"]["{}".format(dev.id)] = True
						if dev.states["status"] == "up":
							if self.groupStatusList[groupNo]["oneHome"] == "0":
								self.groupStatusList[groupNo]["oneHome"]	= "1"
							self.groupStatusList[groupNo]["nHome"]	 	+=1
						else:
							if self.groupStatusList[groupNo]["oneAway"] == "0":
								self.groupStatusList[groupNo]["oneAway"]	= "1"
							self.groupStatusList[groupNo]["nAway"]	 	+=1

			for groupNo in  range(_GlobalConst_numberOfGroups):
				removeList=[]
				for member in self.groupStatusList[groupNo]["members"]:
					if member not in okList:
						removeList.append(member)
				for member in  removeList:
					self.indiLOG.log(20,"removing from group#:{}  memberId:{}".format(groupNo, member))
					del self.groupStatusList[groupNo]["members"][member]


			for groupNo in  range(_GlobalConst_numberOfGroups):
				if self.groupStatusList[groupNo]["nAway"] == len(self.groupStatusList[groupNo]["members"]):
					if self.groupStatusList[groupNo]["allAway"] == "0":
						self.groupStatusList[groupNo]["allAway"]	 = "1"
					self.groupStatusList[groupNo]["oneHome"]	 = "0"
				else:
					self.groupStatusList[groupNo]["allAway"]	 = "0"

				if self.groupStatusList[groupNo]["nHome"] == len(self.groupStatusList[groupNo]["members"]):
					if self.groupStatusList[groupNo]["allHome"] == "0":
						self.groupStatusList[groupNo]["allHome"]	 = "1"
					self.groupStatusList[groupNo]["oneAway"]	 = "0"
				else:
					self.groupStatusList[groupNo]["allHome"]	 = "0"


			# now variables
			for groupNo in  range(_GlobalConst_numberOfGroups):
				varN = "Unifi_Count_{}_".format(self.groupNames[groupNo])
				if	not init:
					try:
						varName = varN 
						varHomeV = indigo.variables[varName+"Home"].value
						varAwayV = indigo.variables[varName+"Away"].value
						if	varHomeV != "{}".format(self.groupStatusList[groupNo]["nHome"]) or varAwayV != "{}".format(self.groupStatusList[groupNo]["nAway"]) or len(indigo.variables[varName+"lastChange"].value) == 0 :
								indigo.variable.updateValue(varName+"lastChange", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
					except:
						self.groupStatusINIT()

				for tType in ["Home","Away"]:
					varName = varN + tType
					gName = "n"+tType
					try:
						var = indigo.variables[varName]
					except:
						indigo.variable.create(varName,"0",folder=self.folderNameIDVariables)
						var = indigo.variables[varName]
					if var.value !=	 "{}".format(self.groupStatusList[groupNo][gName]):
						indigo.variable.updateValue(varName, "{}".format(self.groupStatusList[groupNo][gName]))


			if	not init:
				varName = "Unifi_Count_ALL_"
				try:
					varHomeV = indigo.variables[varName+"Home"].value
					varAwayV = indigo.variables[varName+"Away"].value
					if varHomeV != "{}".format(self.groupStatusListALL["nHome"]) or varAwayV != "{}".format(self.groupStatusListALL["nAway"]) or len(indigo.variables["Unifi_Count_ALL_lastChange"].value) == 0:
						indigo.variable.updateValue("Unifi_Count_ALL_lastChange", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
				except:
					self.groupStatusINIT()

			for tType in ["Home","Away"]:
				varName = "Unifi_Count_ALL_"+tType
				gName = "n"+tType
				try:
					var = indigo.variables[varName]
				except:
					indigo.variable.create(varName,"0",folder=self.folderNameIDVariables)
					var = indigo.variables[varName]
				if var.value != "{}".format(self.groupStatusListALL[gName]):
					indigo.variable.updateValue(varName, "{}".format(self.groupStatusListALL[gName]))



		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		return

######################################################################################
	# Indigo Trigger Start/Stop
######################################################################################

	####-----------------	 ---------
	def triggerStartProcessing(self, trigger):
		self.triggerList.append(trigger.id)

	####-----------------	 ---------
	def triggerStopProcessing(self, trigger):
		if trigger.id in self.triggerList:
			self.triggerList.remove(trigger.id)

	#def triggerUpdated(self, origDev, newDev):
	#	self.triggerStopProcessing(origDev)
	#	self.triggerStartProcessing(newDev)


######################################################################################
	# Indigo Trigger Firing
######################################################################################

	####-----------------	 ---------
	def triggerEvent(self, eventId):
		for trigId in self.triggerList:
			trigger = indigo.triggers[trigId]
			if trigger.pluginTypeId == eventId:
				indigo.trigger.execute(trigger)
		return




	####-----------------setup empty dicts for pointers	 type, mac --> indigop and indigo --> mac,	type ---------
	def setUpDownStateValue(self, dev):
		update=False
		try:
			upDown = ""
			props=dev.pluginProps
			if "expirationTime" not in props:
				props["expirationTime"] = self.expirationTime
				update=True
			if "useWhatForStatus" in props:
				if props["useWhatForStatus"].find("WiFi") > -1:
					if "useWhatForStatusWiFi" in props:
						if props["useWhatForStatusWiFi"] != "" and props["useWhatForStatusWiFi"] != "Expiration":
							if props["useWhatForStatusWiFi"]in ["IdleTime","Optimized","FastDown"]:
								if "idleTimeMaxSecs" not in props:
									props["idleTimeMaxSecs"]= "10"
									update=True
								upDown = "WiFi" + "/" + props["useWhatForStatusWiFi"]+"-idle:"+props["idleTimeMaxSecs"]
							else:
								upDown = "WiFi" + "/" + props["useWhatForStatusWiFi"]
						else:
							upDown =  "Wifi"
					else:
						upDown =  "Wifi"

				elif props["useWhatForStatus"].find("DHCP") > -1:
					if "useAgeforStatusDHCP" in props and	props["useAgeforStatusDHCP"] != "" and props["useAgeforStatusDHCP"] != "-1":
						upDown = "DHCP" + "-age:" + props["useAgeforStatusDHCP"]
					else:
						upDown = "DHCP"

				elif props["useWhatForStatus"] == "OptDhcpSwitch":
					upDown ="OPT: "
					if "useAgeforStatusDHCP" in props and	props["useAgeforStatusDHCP"] != "" and props["useAgeforStatusDHCP"] != "-1":
						upDown += "DHCP" + "-age:" + props["useAgeforStatusDHCP"]+"  "
					else:
						upDown += "DHCP "

					if "useupTimesforStatusSWITCH" in props and props["useupTimeforStatusSWITCH"]:
							upDown += "SWITCH" + "/upTime-notchgd"
					else:
							upDown += "SWITCH"

				elif props["useWhatForStatus"] == "SWITCH":
					if "useupTimesforStatusSWITCH" in props and props["useupTimeforStatusSWITCH"]:
							upDown += "SWITCH" + "/upTime-notchgd"
					else:
							upDown += "SWITCH"

				upDown +=  "-exp:{}".format(self.getexpT(props)).split(".")[0]
				self.addToStatesUpdateList(dev.id,"upDownSetting", upDown)

			if "expirationTime" not in props:
				props["expirationTime"] = self.expirationTime
				update=True

			if "AP" in dev.states:
				if dev.states["AP"].find("-") == -1 :
					newAP= dev.states["AP"]+"-"
					dev.updateStateOnServer("AP",newAP)


		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		if update:
			dev.replacePluginPropsOnServer(props)
		return


	####-----------------setup empty dicts for pointers	 type, mac --> indigop and indigo --> mac,	type ---------
	def setupStructures(self, xType, dev, MAC, init=False):
		devIds =""
		try:

			devIds = "{}".format(dev.id)
			if devIds not in self.xTypeMac:
				self.xTypeMac[devIds] = {"xType":"", "MAC":""}
			self.xTypeMac[devIds]["xType"]	= xType
			self.xTypeMac[devIds]["MAC"]	= MAC

			if xType not in self.MAC2INDIGO:
				self.MAC2INDIGO[xType]={}

			if MAC not in self.MAC2INDIGO[xType]:
				self.MAC2INDIGO[xType][MAC] = {}

			self.MAC2INDIGO[xType][MAC]["devId"] = dev.id
			if "ipNumber" in dev.states:
				self.MAC2INDIGO[xType][MAC]["ipNumber"] = dev.states["ipNumber"]

			try:	self.MAC2INDIGO[xType][MAC]["lastUp"] == float(self.MAC2INDIGO[xType][MAC]["lastUp"])
			except: self.MAC2INDIGO[xType][MAC]["lastUp"] = 0.


			if "last_seen" 	not in self.MAC2INDIGO[xType][MAC]:	self.MAC2INDIGO[xType][MAC]["last_seen"] 		= -1
			if "use_fixedip" 	not in self.MAC2INDIGO[xType][MAC]:	self.MAC2INDIGO[xType][MAC]["use_fixedip"] 	= False
			if "blocked" 		not in self.MAC2INDIGO[xType][MAC]:	self.MAC2INDIGO[xType][MAC]["blocked"] 		= False
			if "lastAPMessage" not in self.MAC2INDIGO[xType][MAC]:	self.MAC2INDIGO[xType][MAC]["lastAPMessage"] 	= 0

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
			self.indiLOG.log(40," {}   {}   {}   {}".format( "{}".format(xType), devIds, "{}".format(MAC), "{}".format(self.MAC2INDIGO)) )
			time.sleep(300)

		if xType =="UN":
				self.MAC2INDIGO[xType][MAC]["AP"]			   = dev.states["AP"].split("-")[0]
				self.MAC2INDIGO[xType][MAC]["lastWOL"]		   = 0.

				for item in ["inListWiFi","inListDHCP",]:
					if item not in self.MAC2INDIGO[xType][MAC]:
							self.MAC2INDIGO[xType][MAC][item] = False
				for item in ["GHz","idleTimeWiFi","upTimeWifi","upTimeDHCP"]:
					if item not in self.MAC2INDIGO[xType][MAC]:
							self.MAC2INDIGO[xType][MAC][item] = ""

				for ii in range(_GlobalConst_numberOfSW):
					for item in ["inListSWITCH_"]:
						if item+"{}".format(ii) not in self.MAC2INDIGO[xType][MAC]:
							self.MAC2INDIGO[xType][MAC][item+"{}".format(ii)] = -1
					for item in ["ageSWITCH_","upTimeSWITCH_"]:
						if item+"{}".format(ii) not in self.MAC2INDIGO[xType][MAC]:
							self.MAC2INDIGO[xType][MAC][item+"{}".format(ii)] = ""


		if xType =="SW":
			if "ports" not in self.MAC2INDIGO[xType][MAC]:
				self.MAC2INDIGO[xType][MAC]["ports"] = {}
			if "upTime" not in self.MAC2INDIGO[xType][MAC]:
				self.MAC2INDIGO[xType][MAC]["upTime"] = ""

		elif xType =="AP":
			self.MAC2INDIGO[xType][MAC]["apNo"] = dev.states["apNo"]

		elif xType =="GW":
			pass

		elif xType =="NB":
			if "age" not in self.MAC2INDIGO[xType][MAC]:
				self.MAC2INDIGO[xType][MAC]["age"] = ""



	####-----------------init  main loop ---------
	def setupCameraVariables(self):
		try:
			if self.cameraSystem == "protect":
				if False and not self.enableSqlLogging:
					try: 	indigo.variable.delete("Unifi_Camera_with_Event")
					except: pass
					try: 	indigo.variable.delete("Unifi_Camera_Event_PathToThumbnail")
					except: pass
					try: 	indigo.variable.delete("Unifi_Camera_Event_DateOfThumbNail")
					except: pass
					try: 	indigo.variable.delete("Unifi_Camera_Event_Date")
					except: pass
		
				try: 	indigo.variable.create("Unifi_Camera_Event_Date", value ="", folder=self.folderNameIDVariables)
				except: pass
				try: 	indigo.variable.create("Unifi_Camera_with_Event", value ="", folder=self.folderNameIDVariables)
				except: pass
				try: 	indigo.variable.create("Unifi_Camera_Event_PathToThumbnail", value ="", folder=self.folderNameIDVariables)
				except: pass
				try: 	indigo.variable.create("Unifi_Camera_Event_DateOfThumbNail", value ="", folder=self.folderNameIDVariables)
				except: pass
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return


	###########################	   MAIN LOOP  ############################
	####-----------------init  main loop ---------
	def fixBeforeRunConcurrentThread(self):

		nowDT = datetime.datetime.now()
		self.lastMinute		= nowDT.minute
		self.lastHour		= nowDT.hour
		self.logQueue		= queue.Queue()
		self.logQueueDict	= queue.Queue()
		self.blockWaitQueue	= PriorityQueue()
		self.apDict			= {}
		self.countLoop		= 0
		self.upDownTimers	= {}
		self.xTypeMac		= {}
		self.broadcastIP	= "9.9.9.255"

		self.writeJson(dataVersion, fName=self.indigoPreferencesPluginDir + "dataVersion")


		self.buttonConfirmGetAPDevInfoFromControllerCALLBACK({})

		## if video enabled
		if self.cameraSystem == "nvr" and self.vmMachine !="":
			self.buttonVboxActionStartCALLBACK()

######## this for fixing the change from mac to MAC in states
		self.indiLOG.log(10,"..getting vendor names for MAC#s")
		self.MacToNamesOK = True
		if self.enableMACtoVENDORlookup:
			self.indiLOG.log(10,"..getting missing vendor names for MAC #")
		self.MAC2INDIGO = {}
		self.readMACdata()

		self.indiLOG.log(10,"..setup dicts  ..")
		delDEV = {}
		for dev in indigo.devices.iter(self.pluginId):
			if dev.deviceTypeId in["client","camera","NVR-video","NVR"]: continue
			if "status" not in dev.states:
				self.indiLOG.log(10,"{} has no status".format(dev.name))
				continue
			else:
				if "onOffState" in dev.states and  ( (dev.states["status"] in ["up","rec","ON"]) != dev.states["onOffState"] ):
							dev.updateStateOnServer("onOffState", value= dev.states["status"] in ["up","rec","ON"], uiValue=dev.states["displayStatus"])

			props= dev.pluginProps
			goodDevice = True
			devId = "{}".format(dev.id)

			if "MAC" in dev.states:
				MAC = dev.states["MAC"]
				if dev.states["MAC"] == "":
					if dev.address != "":
						try:
							self.addToStatesUpdateList(dev.id,"MAC", dev.address)
							MAC = dev.address
						except:
							goodDevice = False
							self.indiLOG.log(10,"{} no MAC # deleting".format(dev.name))
							delDEV[devId]=True
							continue
				if dev.address != MAC:
					props["address"] = MAC
					dev.replacePluginPropsOnServer(props)

			if self.MacToNamesOK and "vendor" in dev.states:
				if (dev.states["vendor"] == "" or dev.states["vendor"].find("<html>") >-1 ) and goodDevice:
					vendor = self.getVendortName(MAC)
					if vendor != "":
						self.addToStatesUpdateList(dev.id,"vendor", vendor)
					if	dev.states["vendor"].find("<html>") >-1   and	 vendor =="" :
						self.addToStatesUpdateList(dev.id,"vendor", "")


			if dev.deviceTypeId == "UniFi":
				self.setupStructures("UN", dev, MAC)


			if dev.deviceTypeId == "Device-AP":
				self.setupStructures("AP", dev, MAC)

			if dev.deviceTypeId.find("Device-SW")>-1:
				self.setupStructures("SW", dev, MAC)

			if dev.deviceTypeId == "neighbor":
				self.setupStructures("NB", dev, MAC)

			if dev.deviceTypeId == "gateway":
				self.setupStructures("GW", dev, MAC)

			if "isProtectCamera" not in props:
				self.setImageAndStatus(dev, dev.states["status"], force=True)

			if "created" in dev.states and dev.states["created"] == "":
				self.addToStatesUpdateList(dev.id,"created", nowDT.strftime("%Y-%m-%d %H:%M:%S"))


			self.setUpDownStateValue(dev)

			self.executeUpdateStatesList()

		for devid in delDEV:
			self.indiLOG.log(10," deleting , bad mac "+ devid )
			indigo.device.delete(int(devid))



		## remove old non exiting MAC / indigo devices
		for xType in self.MAC2INDIGO:
			if "" in self.MAC2INDIGO[xType]:
				del self.MAC2INDIGO[xType][""]
			delXXX = {}
			for MAC in self.MAC2INDIGO[xType]:
				if len(MAC) < 16:
					delXXX[MAC] = True
					continue
				try: indigo.devices[self.MAC2INDIGO[xType][MAC]["devId"]]
				except	Exception as e:
					self.indiLOG.log(10,"removing indigo dev.id: {} from internal list, does not exist as an indigo device".format(self.MAC2INDIGO[xType][MAC]["devId"]))
					time.sleep(1)
					delXXX[MAC] = True
			for MAC in delXXX:
				del self.MAC2INDIGO[xType][MAC]
			# some cleanup it is now upTime xxx  not uptime xxx
			for MAC in self.MAC2INDIGO[xType]:
				delXXX={}
				for yy in self.MAC2INDIGO[xType][MAC]:
					if yy.find("uptime") >-1:
						delXXX[yy]=True
				for yy in delXXX:
					del self.MAC2INDIGO[xType][MAC][yy]
		delXXX = {}

		for devId  in self.xTypeMac:
			try:	 dev = indigo.devices[int(devId)]
			except	Exception as e:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
				if "{}".format(e).find("timeout") >-1:
					self.sleep(20)
					return False
				delXXX[devId]=True
			MAC =  self.xTypeMac[devId]["MAC"]


			if self.xTypeMac[devId]["xType"]=="SW":
				ipN = dev.states["ipNumber"]
				sw	= dev.states["switchNo"]
				try:
					sw = int(sw)
					if ipN != self.ipNumbersOf["SW"][sw]:
						dev.updateStateOnServer("ipNumber",self.ipNumbersOf["SW"][sw])
				except:
					if self.isValidIP(ipN):
						for ii in range(len(self.ipNumbersOf["SW"])):
							if self.ipNumbersOf["SW"][ii] == ipN:
								dev.updateStateOnServer("apNo",ii)
								break


			if self.xTypeMac[devId]["xType"]=="AP":
				ipN = dev.states["ipNumber"]
				sw	= dev.states["apNo"]
				try:
					sw = int(sw)
					if ipN != self.ipNumbersOf["AP"][sw]:
						dev.updateStateOnServer("ipNumber",self.ipNumbersOf["AP"][sw])
				except:
					if self.isValidIP(ipN):
						for ii in range(len(self.ipNumbersOf["AP"])):
							if self.ipNumbersOf["AP"][ii] == ipN:
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

		waitBeforeStart = 1
		addtoWait = self.launchWaitSeconds  # make sure not all listeners start at the same time 

		self.consumeDataThread = {"log":{},"dict":{}}
		self.consumeDataThread["log"]["status"]  = "run"
		self.consumeDataThread["log"]["thread"]  = threading.Thread(name='comsumeLogData', target=self.comsumeLogData)
		self.consumeDataThread["log"]["thread"].start()
		self.consumeDataThread["dict"]["status"] = "run"
		self.consumeDataThread["dict"]["thread"] = threading.Thread(name='comsumeDictData', target=self.comsumeDictData)
		self.consumeDataThread["dict"]["thread"].start()



		if self.cameraSystem == "nvr":

			self.indiLOG.log(10,"..setup NVR -1 getNVRIntoIndigo")
			self.testServerIfOK(self.ipNumbersOf["VD"], "VDdict")
			self.getNVRIntoIndigo(force= True)
			self.indiLOG.log(10,"..setup NVR -2 getNVRCamerastoIndigo")
			self.getNVRCamerastoIndigo(force=True)
			self.indiLOG.log(10,"..setup NVR -3 saveCameraEventsStatus")
			self.saveCameraEventsStatus=True; self.saveCamerasStats(force=False)

				### start video logfile listening
			waitBeforeStart += addtoWait
			self.trVDLog = ""
			self.indiLOG.log(10,"..starting threads for VIDEO NVR log event capture")
			self.trVDLog  = threading.Thread(name='getMessages-VD-log', target=self.getMessages, args=(self.ipNumbersOf["VD"],0,"VDtail",waitBeforeStart,))
			self.trVDLog.start()
			self.sleep(addtoWait)

		self.lastRefreshProtect  = 0

		self.setupCameraVariables()
		self.getProtectIntoIndigo()
		self.protectThread = {"thread":"", "status":""}

		if self.cameraSystem == "protect":
			self.protectThread["status"]  = "run"
			self.protectThread["thread"]  = threading.Thread(name='get-protectevents', target=self.getProtectEvents)
			self.protectThread["thread"].start()
			self.sleep(addtoWait)



		self.getcontrollerDBForClients()

		try:
			self.trAPLog  = {}
			self.trAPDict = {}
			if self.numberOfActive["AP"] > 0:
				self.indiLOG.log(10,"..starting threads for {} APs,  (MSG-log and db-DICT)".format(self.numberOfActive["AP"]) )
				for ll in range(_GlobalConst_numberOfAP):
					if self.devsEnabled["AP"][ll]:
						if (self.unifiControllerType == "UDM" or self.controllerWebEventReadON > 0) and ll == self.numberForUDM["AP"]: continue
						ipn = self.ipNumbersOf["AP"][ll]
						self.broadcastIP = ipn
						if self.decideMyLog("Logic"): self.indiLOG.log(10,"START: AP Thread # {}   {}".format(ll, ipn) )
						if self.connectParams["commandOnServer"]["APtail"].find("off") ==-1: 
							waitBeforeStart +=addtoWait
							self.trAPLog["{}".format(ll)] = threading.Thread(name='getMessages-AP-log-'+"{}".format(ll), target=self.getMessages, args=(ipn,ll,"APtail",waitBeforeStart,))
							self.trAPLog["{}".format(ll)].start()
						waitBeforeStart +=addtoWait
						self.trAPDict["{}".format(ll)] = threading.Thread(name='getMessages-AP-dict-'+"{}".format(ll), target=self.getMessages, args=(ipn,ll,"APdict",waitBeforeStart,))
						self.trAPDict["{}".format(ll)].start()


		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
			self.quitNOW = "stop"
			self.stop = copy.copy(self.ipNumbersOf["AP"])
			return False



		if self.devsEnabled["GW"] and not self.devsEnabled["UD"]:
			self.indiLOG.log(10,"..starting threads for GW (MSG-log and db-DICT)")
			self.broadcastIP = self.ipNumbersOf["GW"]
			if self.connectParams["enableListener"]["GWtail"]: 
				waitBeforeStart +=addtoWait
				self.trGWLog  = threading.Thread(name='getMessages-UGA-log', target=self.getMessages, args=(self.ipNumbersOf["GW"],0,"GWtail",waitBeforeStart,))
				self.trGWLog.start()
			waitBeforeStart +=addtoWait
			self.trGWDict = threading.Thread(name='getMessages-UGA-dict', target=self.getMessages, args=(self.ipNumbersOf["GW"],0,"GWdict",waitBeforeStart,))
			self.trGWDict.start()


		### for UDM devices..
		#1. get mca dump dict   
		if self.devsEnabled["UD"]:
			self.indiLOG.log(10,"..starting threads for UDM  (db-DICT)")
			self.broadcastIP = self.ipNumbersOf["UD"]
			waitBeforeStart +=addtoWait
			self.trUDDict = threading.Thread(name='getMessages-UDM-dict', target=self.getMessages, args=(self.ipNumbersOf["GW"],0,"UDdict",waitBeforeStart,))
			self.trUDDict.start()
			# 2.  this  runs every xx secs  http get data 
			try:
				self.trWebApiEventlog  = ""
				if self.controllerWebEventReadON > 0:
					waitBeforeStart +=addtoWait
					self.trWebApiEventlog = threading.Thread(name='controllerWebApilogForUDM', target=self.controllerWebApilogForUDM, args=(waitBeforeStart, ))
					self.trWebApiEventlog.start()
			except	Exception as e:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
				self.quitNOW = "stop"
				self.stop = copy.copy(self.ipNumbersOf["SW"])
				return False


		try:
			self.trSWLog = {}
			self.trSWDict = {}
			if self.numberOfActive["SW"] > 0:
				self.indiLOG.log(10,"..starting threads for {} SWs (db-DICT only)".format(self.numberOfActive["SW"]) )
				for ll in range(_GlobalConst_numberOfSW):
					if self.devsEnabled["SW"][ll]:
						if self.isMiniSwitch[ll]: continue
						if self.unifiControllerType.find("UDM") > -1 and ll == self.numberForUDM["SW"]: continue
						ipn = self.ipNumbersOf["SW"][ll]
						if self.decideMyLog("Logic"): self.indiLOG.log(10,"START SW Thread tr # {}  uDM#:{}  {}".format(ll, self.numberForUDM["SW"], ipn, self.unifiControllerType))
	 					#					 self.trSWLog["{}".format(ll)] = threading.Thread(name='self.getMessages', target=self.getMessages, args=(ipn, ll, "SWtail",float(self.readDictEverySeconds["SW"]*2,))
	 					#					 self.trSWLog["{}".format(ll)].start()
						waitBeforeStart += addtoWait
						self.trSWDict["{}".format(ll)] = threading.Thread(name='getMessages-SW-Dict', target=self.getMessages, args=(ipn, ll, "SWdict",waitBeforeStart,))
						self.trSWDict["{}".format(ll)].start()

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
			self.quitNOW = "stop"
			return False


		try:
			ip = self.broadcastIP.split(".")
			self.broadcastIP = ip[0]+"."+ip[1]+"."+ip[2]+".255"
		except:
			pass
		
		self.indiLOG.log(10,"..starting threads finished" )


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
		except	Exception as e:
			pass

		self.timeTrackWaitTime = 60
		return "off",""

	####-----------------            ---------
	def printcProfileStats(self,pri=""):
		try:
			if pri !="": pick = pri
			else:		 pick = 'cumtime'
			outFile		= self.indigoPreferencesPluginDir+"timeStats"
			self.indiLOG.log(10," print time track stats to: {}.dump / txt  with option:{} ".format(outFile, pick) )
			self.pr.dump_stats(outFile+".dump")
			sys.stdout 	= self.openEncoding(outFile+".txt", "w")
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
			self.do_cProfile  			= "x"
			self.timeTrVarName 			= "enableTimeTracking_"+self.pluginShortName
			self.indiLOG.log(10,"testing if variable {} is == on/off/print-option to enable/end/print time tracking of all functions and methods (option:'',calls,cumtime,pcalls,time)".format(self.timeTrVarName))

		self.lastTimegetcProfileVariable = time.time()

		cmd, pri = self.getcProfileVariable()
		if self.do_cProfile != cmd:
			if cmd == "on":
				if  self.cProfileVariableLoaded ==0:
					self.indiLOG.log(10,"======>>>>   loading cProfile & pstats libs for time tracking;  starting w cProfile ")
					self.pr = cProfile.Profile()
					self.pr.enable()
					self.cProfileVariableLoaded = 2
				elif  self.cProfileVariableLoaded >1:
					self.quitNOW = " restart due to change  ON  requested for print cProfile timers"
			elif cmd == "off" and self.cProfileVariableLoaded >0:
					self.pr.disable()
					self.quitNOW = " restart due to  OFF  request for print cProfile timers "
		if cmd == "print"  and self.cProfileVariableLoaded >0:
				self.pr.disable()
				self.printcProfileStats(pri=pri)
				self.pr.enable()
				indigo.variable.updateValue(self.timeTrVarName,"done")

		self.do_cProfile = cmd
		return

	####-----------------            ---------
	def checkcProfileEND(self):
		if self.do_cProfile in["on","print"] and self.cProfileVariableLoaded >0:
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
						if "sqlLoggerIgnoreChanges" not in sp  or sp["sqlLoggerIgnoreChanges"] != "true":
							continue
						outONV += var.name+"; "
						sp["sqlLoggerIgnoreChanges"] = ""
						var.replaceSharedPropsOnServer(sp)
					except: pass
				return 


			outOffV = ""
			for v in self.varExcludeSQLList:
				if v in indigo.variables:
					var = indigo.variables[v]
					sp = var.sharedProps
					#self.indiLOG.log(30,"setting /testing off: Var: {} sharedProps:{}".format(var.name, sp) )
					if "sqlLoggerIgnoreChanges" in sp and sp["sqlLoggerIgnoreChanges"] == "true": 
						continue
					#self.indiLOG.log(30,"====set to off ")
					outOffV += var.name+"; "
					sp["sqlLoggerIgnoreChanges"] = "true"
					var.replaceSharedPropsOnServer(sp)

			if len(outOffV) > 0: 
				self.indiLOG.log(10," \n")
				self.indiLOG.log(10,"switching off SQL logging for variables\n :{}".format(outOffV) )
				self.indiLOG.log(10,"switching off SQL logging for variables END\n")
		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		return 



####-----------------   main loop          ---------
	def runConcurrentThread(self):
		### self.indiLOG.log(50,"CLASS: Plugin")


		if not self.fixBeforeRunConcurrentThread():
			self.indiLOG.log(40,"..error in startup")
			self.sleep(10)
			return

		self.setSqlLoggerIgnoreStatesAndVariables()

		self.indiLOG.log(10,"runConcurrentThread.....")

		self.dorunConcurrentThread()
		self.checkcProfileEND()

		self.sleep(1)
		if self.quitNOW !="":
			self.indiLOG.log(20, "runConcurrentThread stopping plugin due to:  ::::: {} :::::".format(self.quitNOW))
			serverPlugin = indigo.server.getPlugin(self.pluginId)
			serverPlugin.restart(waitUntilDone=False)
		return

####-----------------   main loop            ---------
	def dorunConcurrentThread(self):

		self.indiLOG.log(10," start   runConcurrentThread, initializing loop settings and threads ..")


		indigo.server.savePluginPrefs()
		self.lastDayCheck				= -1
		self.lastHourCheck				= datetime.datetime.now().hour
		self.lastMinuteCheck			= datetime.datetime.now().minute
		self.lastMinuteNewUnifiCheck	= int(datetime.datetime.now().minute)//self.checkForNewUnifiSystemDevicesEvery
		self.pluginStartTime 			= time.time()
		self.indiLOG.log(20,"initialized ... looping")
		indigo.server.savePluginPrefs()	
		self.lastcreateEntryInUnifiDevLog = time.time() 

		try:
			while True:
				sl = max(1., self.loopSleep / 10. )
				sli = int(self.loopSleep / sl)
				for ii in range(sli):
					if self.quitNOW != "": 
						break
					self.sleep(sl)

				if self.quitNOW != "": 
					break


				if time.time() - self.updateConnectParams > 0 :
					self.updateConnectParams  = time.time() + 100
					#self.indiLOG.log(10,"saving updated connect parameters from config")
					self.pluginPrefs["connectParams"] = json.dumps(self.connectParams)
					indigo.server.savePluginPrefs()	
	 
				self.countLoop += 1
				ret = self.doTheLoop()
				if ret != "ok":
					self.indiLOG.log(20,"LOOP   return break: >>{}<<".format(ret) )
					break
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		self.indiLOG.log(20,"after loop , quitNow= >>{}<<".format(self.quitNOW ) )

		self.postLoop()

		return


	###########################	   exec the loop  ############################
	####-----------------	 ---------
	def doTheLoop(self):

		if self.checkforUnifiSystemDevicesState == "validate config" or \
		  (self.checkforUnifiSystemDevicesState == "start" and (time.time() - self.pluginStartTime) > 30):
			self.checkForNewUnifiSystemDevices()
			if self.checkforUnifiSystemDevicesState == "reboot":
				self.quitNOW ="new devices at startup / validate config"
				self.checkforUnifiSystemDevicesState =""
				return "new Devices found"

		if self.pendingCommand != []:
			if "getNVRCamerasFromMongoDB-print" in self.pendingCommand: self.getNVRCamerasFromMongoDB(doPrint = True, action=["system","cameras"])
			if "getNVRCamerastoIndigo"	 in self.pendingCommand: self.getNVRCamerastoIndigo(force = True)
			if "getConfigFromNVR"		 in self.pendingCommand: self.getNVRIntoIndigo(force = True); self.getNVRCamerastoIndigo(force = True)
			if "saveCamerasStats"		 in self.pendingCommand: self.saveCameraEventsStatus = True;  self.saveCamerasStats(force = True)
			self.pendingCommand =[]

		if self.quitNOW != "": return "break"

		self.getNVRCamerastoIndigo(periodCheck = True)
		self.saveCamerasStats()
		self.saveDataStats()
		self.saveMACdata()

		if self.quitNOW != "": return "break"

		self.setBlockAccess("main")

		## check for expirations etc

		self.checkOnChanges()
		self.checkOnDelayedActions()
		self.executeUpdateStatesList()

		if self.quitNOW != "": return "break"

		self.periodCheck()
		self.executeUpdateStatesList()
		self.sendUpdatetoFingscanNOW()
		if	 self.statusChanged == 1:  self.setGroupStatus()
		elif self.statusChanged == 2:  self.setGroupStatus(init=True)

		if self.quitNOW != "": return "break"

		self.checkOnDevNeedsUpdate()

		self.executeUpdateStatesList()
		if len(self.sendBroadCastEventsList) >0: self.sendBroadCastNOW()

		self.unsetBlockAccess("main")

		if self.lastMinuteCheck != datetime.datetime.now().minute:
			self.lastMinuteCheck = datetime.datetime.now().minute
			self.statusChanged = max(1,self.statusChanged)

			if self.quitNOW != "": return "break"

			self.getUDMpro_sensors()

			if datetime.datetime.now().minute%5 == 0: 
				self.updateDevStateswRXTXbytes()

			if self.quitNOW != "": return "break"

			if self.cameraSystem == "nvr" and self.vmMachine !="":
				if "VDtail" in self.msgListenerActive and time.time() - self.msgListenerActive["VDtail"] > 600: # no recordings etc for 10 minutes, reissue mount command
					self.msgListenerActive["VDtail"] = time.time()
					self.buttonVboxActionStartCALLBACK()

			if self.lastMinuteNewUnifiCheck != int((datetime.datetime.now().minute)//self.checkForNewUnifiSystemDevicesEvery):
				self.lastMinuteNewUnifiCheck = int((datetime.datetime.now().minute)//self.checkForNewUnifiSystemDevicesEvery)
				self.checkforUnifiSystemDevicesState = "check every {} minutes,  at minute:{}".format(self.checkForNewUnifiSystemDevicesEvery, datetime.datetime.now().minute)
				self.checkForNewUnifiSystemDevices()
				self.checkInListSwitch()

				if self.checkforUnifiSystemDevicesState == "reboot":
					self.quitNOW ="new devices found"
					self.checkforUnifiSystemDevicesState = ""
					return "new devices"


				if self.lastHourCheck != datetime.datetime.now().hour:
					self.lastHourCheck = datetime.datetime.now().hour

					if self.quitNOW != "": return "break"

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

		if self.quitNOW == "config changed":
			self.resetDataStats(calledFrom="postLoop")
		if self.quitNOW == "": self.quitNOW = " restart / stop requested "
		self.pluginPrefs["connectParams"] = json.dumps(self.connectParams)

		self.consumeDataThread["log"]["status"]  = "stop"
		self.consumeDataThread["dict"]["status"] = "stop"

		if True:
			for ll in range(len(self.devsEnabled["SW"])):
				try: 	self.trSWLog["{}".format(ll)].join()
				except: pass
				try: 	self.trSWDict["{}".format(ll)].join()
				except: pass
			for ll in range(len(self.devsEnabled["AP"])):
				try: 	self.trAPLog["{}".format(ll)].join()
				except: pass
				try: 	self.trAPDict["{}".format(ll)].join()
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
	def checkOnDelayedActions(self):
		try:
			if self.delayedAction == {}: return 
			for devId in self.delayedAction:
				for actionDict in self.delayedAction[devId]:
					if actionDict["action"] == "updateState":
						self.addToStatesUpdateList(devId,actionDict["state"], actionDict["value"] )
			self.delayedAction = {}
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return 


	####-----------------	 ---------
	def checkOnDevNeedsUpdate(self):
		try:
			if len(self.devNeedsUpdate) == 0: return 

			for devId in self.devNeedsUpdate:
				if devId not in indigo.devices: 
					self.indiLOG.log(30,"checkOnDevNeedsUpdate: device id not in indigo :{}, skipping, please restart plugin".format(devId))
					continue
				self.setUpDownStateValue(indigo.devices[devId])

			self.devNeedsUpdate = {}
			self.saveupDownTimers()
			self.setGroupStatus(init=True)

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return 

	####-----------------	 ---------
	def saveupDownTimers(self):
		try:
			f = self.openEncoding(self.indigoPreferencesPluginDir+"upDownTimers","w")
			f.write(json.dumps(self.upDownTimers))
			f.close()
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

	####-----------------	 ---------
	def readupDownTimers(self):
		try:
			f = self.openEncoding(self.indigoPreferencesPluginDir+"upDownTimers","r")
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
		xType	= "UN"
		try:
			if self.upDownTimers =={}: return
			deldev={}

			for devid in self.upDownTimers:
				try:
					dev= indigo.devices[int(devid)]
				except	Exception as e:
					if "{}".format(e).find("timeout waiting") > -1:
						if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
						return
					if "{}".format(e).find("not found in database") >-1:
						deldev[devid] =[-1,"dev w devID:{} does not exist".format(devid)]
						continue
					if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
					return

				props=dev.pluginProps
				expT = self.getexpT(props)
				dt	= time.time() - expT
				dtDOWN = time.time() -	self.upDownTimers[devid]["down"]
				dtUP   = time.time() -	self.upDownTimers[devid]["up"]

				if dev.states["status"] != "up": newStat = "down"
				else:							   newStat = "up"
				MAC = dev.states["MAC"]
				if self.upDownTimers[devid]["down"] > 10.:
					if dtDOWN < 2: continue # ignore and up-> in the last 2 secs to avoid constant up-down-up
					if self.doubleCheckWithPing(newStat,dev.states["ipNumber"], props,dev.states["MAC"],"Logic", "checkOnChanges", "CHAN-WiF-Pg","UN") ==0:
							deldev[devid] = [MAC,"[down]>10 ping check"]
							continue
					if "useWhatForStatusWiFi" in props and props["useWhatForStatusWiFi"] in ["FastDown","Optimized"]:
						if dtDOWN > 10. and dev.states["status"] == "up":
							self.setImageAndStatus(dev, "down", ts=dt - 0.1, fing=True, level=1, text1= "{:30s}  status was up  changed period WiFi, expT={:4.1f};  dt={:4.1f}".format(dev.name, expT, dt), iType="CHAN-WiFi",reason="FastDown")
							self.MAC2INDIGO[xType][dev.states["MAC"]]["lastUp"] = time.time() - expT
							deldev[devid] = [MAC,"[down]>10 and fastD or optimized"]
							continue
					if dtDOWN >4:
						deldev[devid] = [MAC,"[down]>10 and dtDown>4"]
				if self.upDownTimers[devid]["up"] > 10.:
					if dtUP < 2: continue # ingnore and up-> in the last 2 secs to avoid constant up-down-up
					deldev[devid] = [MAC,"[up]>10 and tt-[up]>2"]
				if self.upDownTimers[devid]["down"] == 0. and self.upDownTimers[devid]["up"] == 0.:
					deldev[devid] = [MAC,"[down]==0 and [up]==0"]

			for devId in deldev:
				dd = deldev[devId]
				if self.decideMyLog("Logic", MAC=dd[0]): self.indiLOG.log(10,"ChkOnChang del upDownTimers[{}],reason:{}".format(dd[0], dd[1]) )
				del self.upDownTimers[devId]

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		return


	####-----------------	 ---------
	def getexpT(self, props):
		try:
			expT = self.expirationTime
			if "expirationTime" in props and props["expirationTime"] != "-1":
				try:
					expT = float(props["expirationTime"])
				except	Exception as e:
					if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
					self.indiLOG.log(40,"props /expirationTime={}".format(props["expirationTime"]))
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return expT

		####-----------------  check things every minute / xx minute / hour once a day ..  ---------



	####-----------------	 ---------
	def getUDMpro_sensors(self):
		try:
			if True or self.unifiControllerType.find("UDM") == -1: return 

			cmd =  self.expectPath 
			cmd += " '"+self.pathToPlugin + "UDM-pro-sensors.exp' "
			cmd += " '"+self.connectParams["UserID"]["unixUD"]+"' "
			cmd += " '"+self.connectParams["PassWd"]["unixUD"]+"' "
			cmd +=      self.unifiCloudKeyIP
			cmd += " '"+self.escapeExpect(self.connectParams["promptOnServer"][self.unifiCloudKeyIP])+"' "
			cmd +=  self.getHostFileCheck()

			if self.decideMyLog("UDM"): self.indiLOG.log(10,"getUDMpro_sensors: get sensorValues from UDMpro w cmd: {}".format(cmd) )

			ret, err = self.readPopen(cmd)

			data0 = ret.split("\n")
			nextItem = ""
			temperature = ""
			temperature_Board_CPU = ""
			temperature_Board_PHY = ""
			if self.decideMyLog("UDM") or self.decideMyLog("ExpectRET"): self.indiLOG.log(10,"getUDMpro_sensors returned list: {}".format(data0) )
			for dd in data0:
				if dd.find(":") == -1: continue
				nn = dd.strip().split(":")
				if nn[0] == "temp2_input":
					t2 	= round(float(nn[1]),1)
				elif nn[0] == "temp1_input":
					t1			= round(float(nn[1]),1)
				elif nn[0] == "temp3_input":
					t3 	= round(float(nn[1]),1)
 
			if self.decideMyLog("UDM"): self.indiLOG.log(10,"getUDMpro_sensors: temp values found:  1:{}, 2:{}, 3:{}".format(t1, t2, t3) )
			found = False			
			for dev in indigo.devices.iter("props.isGateway"):
				if self.decideMyLog("UDM"): self.indiLOG.log(10,"getUDMpro_sensors: adding temperature states to device:  {}-{}".format(dev.id, dev.name) )
				if dev.states["temperature"] 			!= t1 and t1 != "": 		  self.addToStatesUpdateList(dev.id,"temperature", t1)
				if dev.states["temperature_Board_CPU"] != t2 and t2 != "": self.addToStatesUpdateList(dev.id,"temperature_Board_CPU", t2)
				if dev.states["temperature_Board_PHY"] != t3 and t3 != "": self.addToStatesUpdateList(dev.id,"temperature_Board_PHY", t3)
				self.executeUpdateStatesList()
				found = True			
				break
			if not found:
				if self.decideMyLog("UDM"): self.indiLOG.log(10,"getUDMpro_sensors: not UDM-GW device setup in indigo" )


		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

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


			self.checkIfPrintProcessingTime()


			for dev in indigo.devices.iter(self.pluginId):

				try:
					if dev.deviceTypeId == "camera_protect": continue
					if dev.deviceTypeId == "camera": continue
					if dev.deviceTypeId == "NVR": continue
					if "MAC" not in dev.states: continue

					props = dev.pluginProps
					devid = "{}".format(dev.id)

					MAC		= dev.states["MAC"]
					if dev.deviceTypeId == "UniFi" and self.testIgnoreMAC(MAC, fromSystem="periodCheck") : continue

					if "{}".format(devid) not in self.xTypeMac:
						if dev.deviceTypeId == "UniFi":
							self.setupStructures("UN", dev, MAC)
						if dev.deviceTypeId == "Device-AP":
							self.setupStructures("AP", dev, MAC)
						if dev.deviceTypeId.find("Device-SW")>-1:
							self.setupStructures("SW", dev, MAC)
						if dev.deviceTypeId == "neighbor":
							self.setupStructures("NB", dev, MAC)
						if dev.deviceTypeId == "gateway":
							self.setupStructures("GW", dev, MAC)
					xType	= self.xTypeMac[devid]["xType"]

					expT= self.getexpT(props)
					try:
						lastUpTT   = self.MAC2INDIGO[xType][MAC]["lastUp"]
					except:
						lastUpTT = time.time()
					lastUpTTFastDown = lastUpTT

					if dev.deviceTypeId == "UniFi":
						ipN = dev.states["ipNumber"]

						if MAC not in self.MAC2INDIGO[xType]:
							self.indiLOG.log(10,"{}  xType:{} MAC:{} not in  self.MAC2INDIGO dict, try to restart, delete device and re-create".format(dev.Name, xType, MAC) )
							continue
							
						# check for supended status, if sup : set, if back reset susp status
						if ipN in self.suspendedUnifiSystemDevicesIP:
							## check if we need to reset suspend after 300 secs
							if (time.time() - self.suspendedUnifiSystemDevicesIP[ipN] >10 and self.checkPing(ipN,nPings=2,countPings =2, waitForPing=0.5, calledFrom="PeriodCheck") == 0) :
									self.delSuspend(ipN)
									lastUpTT = time.time()
									self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
									self.indiLOG.log(10,"{} is back from suspended status".format(dev.name))
							else:
								if dev.states["status"] != "susp":
									self.setImageAndStatus(dev, "susp", oldStatus=dev.states["status"],ts=time.time(), fing=False, level=1, text1= "{:30s}  status :{:10s};  set to suspend".format(dev.name, status), iType="PER-susp",reason="Period Check susp "+status)
									self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
									changed = True
								continue

						lastUpTT = self.checkIfControllerDBInfoActive(xType, MAC, props, lastUpTT, expT, dev)

						dt = time.time() - lastUpTT

						if "useWhatForStatus" in props:
							if props["useWhatForStatus"].find("WiFi") > -1:
								suffixN = "WiFi"

								######### do WOL / ping	  START ########################
								if "useWOL" in props and props["useWOL"] !="0":
									if "lastWOL" not in self.MAC2INDIGO[xType][MAC]:
										self.MAC2INDIGO[xType][MAC]["lastWOL"]	= 0.
									if time.time() - self.MAC2INDIGO[xType][MAC]["lastWOL"] > float(props["useWOL"]):
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
										if self.sendWakewOnLanAndPing( MAC, ipN, nBC=nBC, waitForPing=waitForPing, countPings=1, waitAfterPing=waitAfterPing, waitBeforePing=waitBeforePing, nPings=nPings, calledFrom="periodCheck") ==0:
											lastUpTT = time.time()
											lastUpTTFastDown = time.time()
											self.MAC2INDIGO[xType][MAC]["lastUp"] = lastUpTT
										self.MAC2INDIGO[xType][MAC]["lastWOL"]	= time.time()
								######### do WOL / ping	  END  ########################
								dt = time.time() - lastUpTT

								if "useWhatForStatusWiFi" not in props or	("useWhatForStatusWiFi" in props and props["useWhatForStatusWiFi"] != "FastDown"):

									if (devid in self.upDownTimers	and time.time() -  self.upDownTimers[devid]["down"] > expT ) or (dt > 1 * expT) :
										if	  dt <						 1 * expT: status = "up"
										elif  dt <	self.expTimeMultiplier * expT: status = "down"
										else :				  status = "expired"
										if not self.expTimerSettingsOK("AP",MAC, dev): continue

										if status != "up":
											if dev.states["status"] == "up":
												if self.doubleCheckWithPing(status,dev.states["ipNumber"], props,dev.states["MAC"],"Logic", "Period check-WiFi", "chk-Time",xType) ==0:
													status	= "up"
													self.setImageAndStatus(dev, "up", oldStatus=dev.states["status"],ts=time.time(), fing=False, level=1, text1=  "{:30s} status {:10s};   set to UP,  reset by ping ".format(dev.name, status), iType="PER-AP-Wi-0",reason="Period Check Wifi "+status)
													changed = True
													continue
												else:
													self.setImageAndStatus(dev, status, oldStatus=dev.states["status"],ts=time.time(), fing=True, level=1, text1= "{:30s} status {:10s}; changed period WiFi, expT={:4.1f}     dt={:4.1f}".format(dev.name, status, expT, dt), iType="PER-AP-Wi-1",reason="Period Check Wifi "+status)
													changed = True
													continue

											if dev.states["status"] == "down" and status !="down": # to expired
													self.setImageAndStatus(dev, status, oldStatus=dev.states["status"],ts=time.time(), fing=True, level=1, text1= "{:30s} status {:10s}; changed period WiFi, expT={:4.1f}     dt={:4.1f}".format(dev.name, status, expT, dt), iType="PER-AP-Wi-1",reason="Period Check Wifi "+status)
													changed = True
													continue

										else:
											if dev.states["status"] != status:
												if self.doubleCheckWithPing(status,dev.states["ipNumber"], props,dev.states["MAC"],"Logic", "Period check-WiFi", "chk-Time",xType) !=0:
													pass
												else:
													changed = True
													status = "up"
													self.setImageAndStatus(dev, status, oldStatus=dev.states["status"],ts=time.time(), fing=True, level=1, text1= "{:30s} status {:10s}; changed period WiFi, expT={:4.1f}     dt={:4.1f}".format(dev.name, status, expT, dt), iType="PER-AP-Wi-1",reason="Period Check Wifi "+status)
												continue


								elif  ("useWhatForStatusWiFi" in props and props["useWhatForStatusWiFi"] == "FastDown") and dev.states["status"] == "down" and (time.time() - lastUpTTFastDown > self.expTimeMultiplier * expT):
										if not self.expTimerSettingsOK("AP",MAC, dev): continue
										status = "expired"
										changed = True
										self.setImageAndStatus(dev, status, oldStatus=dev.states["status"],ts=time.time(), fing=True, level=1, text1="{:30s} status {:10s}; changed period WiFi, expT={:4.1f}     dt={:4.1f}".format(dev.name, status, expT, dt), iType="PER-AP-Wi-2",reason="Period Check Wifi "+status)


							elif props["useWhatForStatus"] =="SWITCH":
								suffixN = "SWITCH"
								dt = time.time() - lastUpTT
								if	 dt <  1 * expT:  status = "up"
								elif dt <  2 * expT:  status = "down"
								else :				  status = "expired"
								if not self.expTimerSettingsOK("SW",MAC, dev): continue
								if dev.states["status"] != status:
									if status =="down" and self.doubleCheckWithPing(status,dev.states["ipNumber"], props,dev.states["MAC"],"Logic", "Period check-SWITCH", "chk-Time",xType) ==0:
										status = "up"
									if dev.states["status"] != status:
										changed = True
										self.setImageAndStatus(dev, status,oldStatus=dev.states["status"], ts=time.time(), fing=True, level=1, text1= "{:30s} status {:10s}; changed period SWITCH, expT={:4.1f}     dt={:4.1f}".format(dev.name, status, expT, dt), iType="PER-SW-0",reason="Period Check SWITCH "+status)



							elif props["useWhatForStatus"].find("DHCP") > -1:
								suffixN = "DHCP"
								dt = time.time() - lastUpTT
								if	 dt <  						1 * expT:  status = "up"
								elif dt <  self.expTimeMultiplier * expT:  status = "down"
								else :				  status = "expired"
								if not self.expTimerSettingsOK("GW",MAC, dev): continue
								if dev.states["status"] != status:
									if status == "down" and self.doubleCheckWithPing(status,dev.states["ipNumber"], props,dev.states["MAC"],"Logic", "Period check-DHCP", "chk-Time",xType) ==0:
										status = "up"
									if dev.states["status"] != status:
										changed = True
										self.setImageAndStatus(dev, status,oldStatus=dev.states["status"], ts=time.time(), fing=True, level=1, text1= "{:30s} status {:10s}; changed period DHCP, expT={:4.1f}     dt= {:4.1f}".format(dev.name, status, expT, dt), iType="PER-DHCP-0",reason="Period Check DHCP "+status)


							else:
								dt = time.time() - lastUpTT
								if	 dt <  						1 * expT:  status = "up"
								elif dt <  self.expTimeMultiplier * expT:  status = "down"
								else			   :  status = "expired"
								if dev.states["status"] != status:
									if status =="down" and self.doubleCheckWithPing(status,dev.states["ipNumber"], props,dev.states["MAC"],"Logic", "Period check-default", "chk-Time",xType) ==0:
										status = "up"
									if dev.states["status"] != status:
										changed = True
										self.setImageAndStatus(dev, status,oldStatus=dev.states["status"], ts=time.time(), fing=True, level=1, text1= "{:30s} status {:10s}; changed period regular expiration, expT{:4.1f}     dt={:4.1f}  useWhatForStatus else{}".format(dev.name, status, expT, dt,props["useWhatForStatus"]) , iType="PER-expire",reason="Period Check")
						continue


					elif dev.deviceTypeId == "Device-AP":
						try:
							ipN = dev.states["ipNumber"]
							if ipN not in self.deviceUp["AP"]:
								continue
								#ipN = self.ipNumbersOf["AP"][int(dev.states["apNo"])]
								#dev.updateStateOnServer("ipNumber", ipN )
							if ipN in self.suspendedUnifiSystemDevicesIP:
								status = "susp"
								self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
								dt	=99
								expT=999
							else:
								dt = time.time() - self.deviceUp["AP"][dev.states["ipNumber"]]
								if	 dt <  						1 * expT:  status = "up"
								elif dt <  self.expTimeMultiplier * expT:  status = "down"
								else :				  status = "expired"
							if dev.states["status"] != status:
								if status =="down" and self.doubleCheckWithPing(status,dev.states["ipNumber"], props,dev.states["MAC"],"Logic", "Period check-dev-AP", "chk-Time",xType) ==0:
									status = "up"
								if dev.states["status"] != status:
									changed = True
									self.setImageAndStatus(dev,status,oldStatus=dev.states["status"],ts=time.time(), fing=True, level=1, text1= "{:30s} status {:10s}; changed period, expT={:4.1f}     dt= {:4.1f}".format(dev.name, status, expT, dt), reason="Period Check", iType="PER-DEV-AP")
						except	Exception as e:
							if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
							continue

					elif dev.deviceTypeId.find("Device-SW") >-1:
						try:
							ipN = dev.states["ipNumber"]
							if ipN not in self.deviceUp["SW"]:
								ipN = self.ipNumbersOf["SW"][int(dev.states["switchNo"])]
								dev.updateStateOnServer("ipNumber", ipN )
							if ipN in self.suspendedUnifiSystemDevicesIP:
								self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
								status = "susp"
								dt =99
								expT=999
							else:

								dt = time.time() - self.deviceUp["SW"][ipN]
								if	 dt < 						1 * expT: status = "up"
								elif dt < self.expTimeMultiplier  * expT: status = "down"
								else:									  status = "expired"

							if dev.states["status"] != status:
								if status =="down" and self.doubleCheckWithPing(status,dev.states["ipNumber"], props,dev.states["MAC"],"Logic", "Period check-dev-SW", "chk-Time",xType) ==0:
									status = "up"
								if dev.states["status"] != status:
									changed = True
									self.setImageAndStatus(dev,status,oldStatus=dev.states["status"],ts=time.time(), fing=True, level=1, text1="{:30s} status {:10s}; changed period, expT={:4.1f}     dt= {:4.1f}".format(dev.name, status, expT, dt),reason="Period Check", iType="PER-DEV-SW")
						except	Exception as e:
							if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
							continue


					elif dev.deviceTypeId == "neighbor":
						try:
							dt = time.time() - lastUpTT
							if	 dt < 						1 * expT: status = "up"
							elif dt < self.expTimeMultiplier  * expT: status = "down"
							else:				status = "expired"
							if dev.states["status"] != status:
									changed=True
									self.setImageAndStatus(dev,status,oldStatus=dev.states["status"],ts=time.time(), fing=self.ignoreNeighborForFing, level=1, text1="{:30s} status {:10s}; changed period, expT={:4.1f}     dt= {:4.1f}".format(dev.name, status, expT, dt),reason="Period Check other", iType="PER-DEV-NB")
						except	Exception as e:
							if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
							continue
					else:
						try:
							dt = time.time() - lastUpTT
							if dt < 1 * expT:	status = "up"
							elif dt < 2 * expT: status = "down"
							else:				status = "expired"
							if dev.states["status"] != status:
								if status =="down" and self.doubleCheckWithPing(status,dev.states["ipNumber"], props,dev.states["MAC"],"Logic", "Period check-def", "chk-Time",xType) ==0:
									status = "up"
								if dev.states["status"] != status:
									changed=True
									self.setImageAndStatus(dev,status, oldStatus=dev.states["status"],ts=time.time(), fing=True, level=1, text1="{:30s} status {:10s}; changed period, expT={:4.1f}     dt= {:4.1f}  devtype else:{}".format(dev.name, status, expT, dt,dev.deviceTypeId),reason="Period Check other", iType="PER-DEV-exp")

						except:
							continue

					self.lastSecCheck = time.time()
				except	Exception as e:
					if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)


		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return	changed




	########################### #################
	def checkIfControllerDBInfoActive(self, xType, MAC, props, lastUpTT, expT, dev):
		try:
			if self.useDBInfoForWhichDevices == "all" or (self.useDBInfoForWhichDevices == "perDevice" and "useDBInfoForDownCheck" in props and props["useDBInfoForDownCheck"] == "useDBInfo"):
				if time.time() -  self.MAC2INDIGO[xType][MAC]["last_seen"] < max(99., expT):
					if self.MAC2INDIGO[xType][MAC]["last_seen"]  > lastUpTT:
						if self.decideMyLog("DBinfo", MAC=MAC): self.indiLOG.log(10,"overwriting lastUP w info from controllerdb {} {:28s}  lastTT:{:.0f},   new lastTT:{:.0f}".format(MAC, dev.name,  time.time() - lastUpTT, time.time() - self.MAC2INDIGO[xType][MAC]["last_seen"] ))
						lastUpTT = self.MAC2INDIGO[xType][MAC]["last_seen"]
			if self.decideMyLog("DBinfo", MAC=MAC): 
				self.indiLOG.log(10,"checking    lastUP w info from controllerdb {} {:28s}  lastTT:{:.0f},  lastTT-db:{:.0f}".format(MAC, dev.name,  time.time() - lastUpTT, time.time() - self.MAC2INDIGO[xType][MAC]["last_seen"] ))

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return lastUpTT


	###########################	   UTILITIES  #### START #################

	### reset exp timer if it is shorter than the device exp time
	####-----------------	 ---------
	def expTimerSettingsOK(self, xType, MAC,	dev):
		try:
			if not self.fixExpirationTime: 		return True
			props = dev.pluginProps
			if "expirationTime" not in props:	return True

			if float(self.readDictEverySeconds[xType]) <  float(props["expirationTime"]): return True
			newExptime	= float(self.readDictEverySeconds[xType])+10
			self.indiLOG.log(10,"checking expiration timer settings {} updating exptime for {} to {} as it is shorter than reading dicts: {}+10".format(MAC, dev.name, newExptime, self.readDictEverySeconds[xType]))
			props["expirationTime"] = newExptime
			dev.replacePluginPropsOnServer(props)
			return False

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return True

	###	 kill expect pids if running
	####-----------------	 ---------
	def killIfRunning(self,ipNumber,expectPGM):
		cmd = "ps -ef | grep '/uniFiAP.' | grep "+self.expectPath+" | grep -v grep"
		if  expectPGM !="":		cmd += " | grep '" + expectPGM + "' "
		if  ipNumber != "":		cmd += " | grep '" + ipNumber  + " ' "  # add space at end of ip# for search string

		if self.decideMyLog("Expect"): self.indiLOG.log(10,"killing request, get list with: "+cmd)
		ret, err = self.readPopen(cmd)

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
				ret, err = self.readPopen("/bin/kill -9  " + pid)
				if self.decideMyLog("Expect"): self.indiLOG.log(10,"killing expect "+expectPGM+" w ip# " +ipNumber +"    "  +pid+":\n"+line )
			except:
				pass

		return

	####-----------------	 ---------
	def killPidIfRunning(self,pid):
		cmd = "ps -ef | grep '/uniFiAP.' | grep "+self.expectPath+" | grep {}".format(pid)+" | grep -v grep"

		if self.decideMyLog("Expect"): self.indiLOG.log(10,"killing request,  for pid: {}".format(pid))
		ret, err = self.readPopen(cmd)

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
				ret, err = self.readPopen("/bin/kill -9  " + pidInLine)
				if self.decideMyLog("Expect"): self.indiLOG.log(10,"killing expect "  +pidInLine+":\n"+line )
			except:
				pass
			break

		return

	### test if AP are up, first ping then check if expect is running
	####-----------------	 ---------
	def testAPandPing(self,ipNumber, cType):
		try:
			if self.decideMyLog("Expect"): self.indiLOG.log(10,"CONNtest  testing if {} {} {} is running ".format(ipNumber, self.expectPath,self.connectParams["expectCmdFile"][cType]))
			if os.path.isfile(self.pathToPlugin +self.connectParams["expectCmdFile"][cType]):
				if self.decideMyLog("Expect"): self.indiLOG.log(10,"CONNtest {} exists, now doing ping" .format(self.connectParams["expectCmdFile"][cType]))
			if self.checkPing(ipNumber, nPings=2, waitForPing=1000, calledFrom="testAPandPing", verbose=True) !=0:
				if self.decideMyLog("Expect"): self.indiLOG.log(10,"CONNtest  ping not returned" )
				return False

			cmd = "ps -ef | grep " +self.connectParams["expectCmdFile"][cType]+ "| grep " + ipNumber + " | grep "+self.expectPath+" | grep -v grep"
			if self.decideMyLog("Expect"): self.indiLOG.log(10,"CONNtest  check if pgm is running {}".format(cmd) )
			ret, err = self.readPopen(cmd)
			if self.decideMyLog("ExpectRET"): self.indiLOG.log(10,"returned from expect-command: {}".format(ret[0]))
			if len(ret) < 5: return False
			lines = ret.split("\n")
			for line in lines:
				if len(line) < 5:
					continue

				items = line.split()
				if len(items) < 5:
					continue

				if self.decideMyLog("Expect"): self.indiLOG.log(10,"CONNtest  expect is running" )
				return True

			if self.decideMyLog("Expect"): self.indiLOG.log(10,"CONNtest  {}    {}is NOT running".format(cType, ipNumber) )
			return False
		except	Exception as e:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)


	### test if AP are up, first ping then check if expect is running
	####-----------------	 ---------
	def resetUnifiDevice(self,ipNumber, uType):
		try:
			userid, passwd = self.getUidPasswd(uType,ipNumber)
			if userid == "": return
			self.indiLOG.log(10,"resetUnifiDevice  {}-{};  requested".format(uType, ipNumber) )
			if ipNumber in self.lastResetUnifiDevice:
				if time.time() - self.lastResetUnifiDevice[ipNumber] < 180: return  # only reset devices every 50 secs not more often..
			self.lastResetUnifiDevice[ipNumber]  = time.time()
			cmd  = self.expectPath + " '" 
			cmd += self.pathToPlugin + self.connectParams["expectRestart"][uType] + "' "
			cmd += "'"+userid + "' '"+passwd + "' " 
			cmd += ipNumber + " " 
			cmd += "'"+self.escapeExpect(self.connectParams["promptOnServer"][ipNumber]) + "' "  
			cmd +=  self.getHostFileCheck()
			ret, err = self.readPopen(cmd)
			self.indiLOG.log(10,"resetUnifiDevice  {}-{};  cmd:{}    return:{}".format(uType, ipNumber, cmd, ret) )
			return False
		except	Exception as e:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)




	####-----------------	 --------- 
	### init,save,write data stats for receiving messages
	def addTypeToDataStats(self,ipNumber, apN, uType):
		try:
			if uType not in self.dataStats["tcpip"]:
				self.dataStats["tcpip"][uType]={}
			if ipNumber not in self.dataStats["tcpip"][uType]:
				self.dataStats["tcpip"][uType][ipNumber]={"inMessageCount":0,"inMessageBytes":0,"inErrorCount":0,"restarts":0,"inErrorTime":0,"startTime":time.time(),"APN":"{}".format(apN), "aliveTestCount":0}
			if "inErrorTime" not in self.dataStats["tcpip"][uType][ipNumber]:
				self.dataStats["tcpip"][uType][ipNumber]["inErrorTime"] = 0
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
	####-----------------	 ---------
	def zeroDataStats(self):
		for uType in self.dataStats["tcpip"]:
			for ipNumber in self.dataStats["tcpip"][uType]:
				self.dataStats["tcpip"][uType][ipNumber]["inMessageCount"]	= 0
				self.dataStats["tcpip"][uType][ipNumber]["inMessageBytes"]	= 0
				self.dataStats["tcpip"][uType][ipNumber]["aliveTestCount"]	= 0
				self.dataStats["tcpip"][uType][ipNumber]["inErrorCount"]		= 0
				self.dataStats["tcpip"][uType][ipNumber]["restarts"]			= 0
				self.dataStats["tcpip"][uType][ipNumber]["startTime"]			= time.time()
				self.dataStats["tcpip"][uType][ipNumber]["inErrorTime"]		= 0
		self.dataStats["updates"]={"devs":0,"states":0,"startTime":time.time()}
	####-----------------	 ---------
	def resetDataStats(self, calledFrom=""):
		indigo.server.log(" resetDataStats called from {}".format(calledFrom) )
		self.dataStats={"tcpip":{},"updates":{"devs":0,"states":0,"startTime":time.time()}}
		self.saveDataStats()

	####-----------------	 ---------
	def saveDataStats(self, force = False):
		if time.time() - 60	 < self.lastSaveDataStats and not force: return
		self.lastSaveDataStats = time.time()
		self.writeJson(self.dataStats, fName=self.indigoPreferencesPluginDir+"dataStats", sort=False, doFormat=True )
		self.writeJson(self.waitTimes, fName=self.indigoPreferencesPluginDir+"waitTimes", sort=True, doFormat=True )


	####-----------------	 ---------
	def readDataStats(self):
		self.lastSaveDataStats	= time.time() - 60
		self.waitTimes = {}
		self.dataStats = {}

		try:
			f = self.openEncoding(self.indigoPreferencesPluginDir+"waitTimes","r")
			self.waitTimes = json.loads(f.read())
			f.close()
		except: pass

		try:
			f = self.openEncoding(self.indigoPreferencesPluginDir+"dataStats","r")
			self.dataStats = json.loads(f.read())
			f.close()
			if "tcpip" not in self.dataStats:
				self.resetDataStats( calledFrom="readDataStats 1")
			return 
		except: 
			self.resetDataStats( calledFrom="readDataStats 2")

		return
	### init,save,write data stats for receiving messages
	####-----------------	 --------- END


	####------ camera  ---	-------START
	def resetCamerasStats(self):
		return
		self.cameras={}
		self.saveCameraEventsStatus = True
		self.saveCameraEventsLastCheck = 0
		self.saveCamerasStats()

	####-----------------	 ---------
	def saveCamerasStats(self,force=False):
		return
		if	not self.saveCameraEventsStatus: return

		if self.saveCameraEventsStatus == True:
			self.saveCameraEventsLastCheck = 0

		# check if we have deleted devices in cameras
		if time.time() - self.saveCameraEventsLastCheck > 500 or force:

			cameraMacList ={}
			for dev in indigo.devices.iter("props.isCamera"):
				cameraMacList[dev.states["MAC"]] = dev.id

			delList ={}
			for MAC in self.cameras:
				if MAC not in cameraMacList:
					delList[MAC]=True
			for MAC in delList:
				self.cameras[MAC]["devid"]=-1

			self.saveCameraEventsLastCheck = time.time()

		# save cameras to disk
		self.writeJson( self.cameras, fName=self.indigoPreferencesPluginDir+"CamerasStats",  sort=True, doFormat=True )
		self.saveCameraEventsStatus = False

	####-----------------	 ---------
	def readCamerasStats(self):
		return
		try:
			f = self.openEncoding(self.indigoPreferencesPluginDir+"CamerasStats","r")
			self.cameras = json.loads(f.read())
			f.close()
			self.saveCameraEventsStatus = True
			self.saveCamerasStats()
			return
		except: pass

		self.resetCamerasStats()
		return

	####------ camera PROTEC ---	-------END

	####------ camera NVR ---	-------START

	####-----------------	 ---------
	def getNVRCamerastoIndigo(self, force = False, periodCheck = False):
		return
		try:
			if periodCheck: test = 300
			else:			test = 30
			if time.time() - self.lastCheckForCAMERA < test and not force: return
			self.lastCheckForCAMERA = time.time()
			timeElapsed = time.time()
			if self.cameraSystem != "nvr":					return
			if not self.isValidIP(self.ipNumbersOf["VD"]): return
			info = self.getNVRCamerasFromMongoDB(action=["cameras"])
			if len(info) < 1:
				self.sleep(1)
				info = self.getNVRCamerasFromMongoDB(action=["cameras"])

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

	####-----------------	 ---------
	def getNVRIntoIndigo(self,force= False):
		return
		try:
			if time.time() - self.lastCheckForNVR < 451 and not force: return
			self.lastCheckForNVR = time.time()
			if not self.isValidIP(self.ipNumbersOf["VD"]): return
			if self.cameraSystem != "nvr":			   		return


			info =self.getNVRCamerasFromMongoDB( action=["system"])

			if len(info["NVR"]) < 2:
				for dev in indigo.devices.iter("props.isNVR"):
					self.updateStatewCheck(dev,"status", "down")
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


			if "host"				in NVR:								  ipNumber			= NVR["host"]
			if "uptime"			in NVR:								  upSince			= time.strftime( '%Y-%m-%d %H:%M:%S', time.localtime(float(NVR["uptime"])/1000) )

			if "systemInfo"	   in NVR:
				if "nics"		   in NVR["systemInfo"]:
					for nic		   in NVR["systemInfo"]["nics"]:
						if "ip"	   in nic:							  ipNumber			= nic["ip"]
						if "mac"   in nic:								  MAC				= nic["mac"].lower()
				if "memory"	 in NVR["systemInfo"]:
						if "total" in NVR["systemInfo"]["memory"]:		  memoryUsed		= "%d/%d"%( float(NVR["systemInfo"]["memory"]["used"])/(1024*1024), float(NVR["systemInfo"]["memory"]["total"])/(1024*1024) )+"[GB]"
				if "cpuLoad"	 in NVR["systemInfo"]:					  cpuLoad			= "%.1f"%( float(NVR["systemInfo"]["cpuLoad"]))+"[%]"
				if "disk"		 in NVR["systemInfo"]:
						if "dirName"	 in NVR["systemInfo"]["disk"]:	  dirName			= NVR["systemInfo"]["disk"]["dirName"]
						if "availKb"	 in NVR["systemInfo"]["disk"]:	  diskAvail			= "%d"%( float(NVR["systemInfo"]["disk"]["availKb"])/(1024*1024) )+"[GB]"
						if "usedKb"		 in NVR["systemInfo"]["disk"]:diskUsed			= "%d/%d"%( float(NVR["systemInfo"]["disk"]["usedKb"])/(1024*1024) , float(NVR["systemInfo"]["disk"]["totalKb"])/(1024*1024) )	+"[GB]"

			if"livePortSettings"		 in NVR:
				if "rtmpEnabled"		 in NVR["livePortSettings"]:
						if NVR["livePortSettings"]["rtmpEnabled"]:		  rtmpPort			=  "{}".format( NVR["livePortSettings"]["rtmpPort"] )
				if "rtmpsEnabled"		  in NVR["livePortSettings"]:
						if NVR["livePortSettings"]["rtmpsEnabled"]:		  rtmpsPort			=  "{}".format( NVR["livePortSettings"]["rtmpsPort"] )
				if "rtspEnabled"		 in NVR["livePortSettings"]:
						if NVR["livePortSettings"]["rtspEnabled"]:		  rtspPort			=  "{}".format( NVR["livePortSettings"]["rtspPort"] )

			users = info["users"]

			for _id in users:
				if users[_id]["userName"] == self.connectParams["UserID"]["nvrWeb"]:
					if "apiKey" in users[_id] and "enableApiAccess" in users[_id]:
						if users[_id]["enableApiAccess"] :
							apiKey		= users[_id]["apiKey"]
							apiAccess 	= users[_id]["enableApiAccess"]


			UnifiName	= ipNumber
			for dev in indigo.devices.iter("props.isUniFi"):
				if dev.states["ipNumber"] == ipNumber and MAC == dev.states["MAC"]:
					UnifiName	= dev.name
					break


			dev = ""
			for dd in indigo.devices.iter("props.isNVR"):
				dev = dd
				break

			if dev =="":
				if UnifiName != "": useName= UnifiName
				elif UnifiMAC !="": useName= UnifiMAC
				else:				useName= ipNumber+"{}".format(int(time.time()))

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

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)


	####-----------------	 ---------
	def fillCamerasIntoIndigo(self,camJson, calledFrom=""):
		return
		try:
			if len(camJson) < 1: return
			saveCam= False
			for cam2 in camJson:
				if "mac" in cam2:
					c = cam2["mac"]
					MAC = c[0:2]+":"+c[2:4]+":"+c[4:6]+":"+c[6:8]+":"+c[8:10]+":"+c[10:12]
					MAC = MAC.lower()

					skip = ""
					if self.testIgnoreMAC(MAC, fromSystem="fillCam"):
						skip = "MAC in ignored List"
					else:
						if "authStatus" in cam2 and cam2["authStatus"] != "AUTHENTICATED":
							skip += "authStatus: !=AUTHENTICATED;"
						if "managed" in cam2 and not cam2["managed"]:
							skip += " .. != managed;"
						if "deleted" in cam2 and  cam2["deleted"]:
							skip += " deleted"
						if skip !="":
							if self.decideMyLog("Video"): self.indiLOG.log(10,"skipping camera with MAC # "+MAC +"; because : "+ skip)
					if skip !="":
						continue

					found = False
					for cam in self.cameras:
						if MAC == cam:
							self.cameras[MAC]["uuid"]		= cam2["uuid"]
							self.cameras[MAC]["ip"]			= cam2["host"]
							self.cameras[MAC]["apiKey"]		= cam2["_id"]
							self.cameras[MAC]["nameOnNVR"]	= cam2["name"]
							found = True
							break
					if not found:
						saveCam = True
						self.cameras[MAC]= {"nameOnNVR":cam2["name"], "events":{}, "eventsLast":{"start":0,"stop":0},"devid":-1, "uuid":cam2["uuid"], "ip":cam2["host"], "apiKey":cam2["_id"]}

					devFound = False
					if "devid" in self.cameras[MAC]:
						try:
							dev = indigo.devices[self.cameras[MAC]["devid"]]
							devFound = True
						except: pass

					if	not devFound:
						for dev in indigo.devices.iter("props.isCamera"):
							if "MAC" not in dev.states:	   continue
							if dev.states["MAC"] == MAC:
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
								deviceTypeId	="camera",
								props			={"isCamera":True},
								folder			=self.folderNameIDSystemID
								)
							indigo.variable.updateValue("Unifi_New_Device","{}/{}/{}".format(dev.name, MAC, cam2["host"]) )
						except	Exception as e:
							if "{}".format(e).find("NameNotUniqueError") >-1:
								dev 				= indigo.devices["Camera_"+self.cameras[MAC]["nameOnNVR"]+"_"+MAC]
								props 				= dev.pluginProps
								props["isCamera"] 	= True
								dev.replacePluginPropsOnServer()
								dev 				= indigo.devices[dev.id]
							else:
								if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
								continue
					saveCam or self.updateStatewCheck(dev,"MAC",			MAC)
					saveCam or self.updateStatewCheck(dev,"apiKey",		self.cameras[MAC]["apiKey"])
					saveCam or self.updateStatewCheck(dev,"uuid",		 	self.cameras[MAC]["uuid"])
					saveCam or self.updateStatewCheck(dev,"ip",			self.cameras[MAC]["ip"])
					saveCam or self.updateStatewCheck(dev,"nameOnNVR",	 	self.cameras[MAC]["nameOnNVR"])
					saveCam or self.updateStatewCheck(dev,"eventNumber",	 -1,					check="", NotEq=True)
					saveCam or self.updateStatewCheck(dev,"status",		"ON",					check="", NotEq=True)
					self.executeUpdateStatesList()
					if not devFound:
						dev = indigo.devices[dev.id]

			if saveCam:
				self.pendingCommand.append("saveCamerasStats")


		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)



	####-----------------	 ---------
	def getNVRCamerasFromMongoDB(self, doPrint = False, action=[]):
		return
		try:
			timeElapsed = time.time()
			info	= {"users":{}, "cameras":[], "NVR":{}}
			USERs	= []
			ACCOUNTs= []
			cmdstr	= ["\"mongo 127.0.0.1:7441/av --quiet --eval  'db.", ".find().forEach(printjsononeline)'  | sed 's/^\s*//' \"" ]

			#self.indiLOG.log(10," into getNVRCamerasFromMongoDB action :{}".format(action))
			if "system" in action:
				USERs			= self.getMongoData(cmdstr[0]+"user"   +cmdstr[1])
				ACCOUNTs		= self.getMongoData(cmdstr[0]+"account"+cmdstr[1])

				if len(USERs)>0 and len(ACCOUNTs) >0:
					for account in ACCOUNTs:
						if "_id" in account and "username" in account and "name" in account:
							ID =  account["_id"]
							info["users"][ID] ={"userName":account["username"], "name":account["name"]}
							for user in USERs:
								if "accountId" in user and ID == user["accountId"]:
									if "apiKey" in user and "enableApiAccess" in user:
										info["users"][ID]["apiKey"]			= user["apiKey"]
										info["users"][ID]["enableApiAccess"]	= user["enableApiAccess"]
									else:
										if "enableApiAccess" in user and user["enableApiAccess"]: # its enabled, but no api key
											self.indiLOG.log(40,"getNVRCamerasFromMongoDB camera users   bad enableApiAccess / apiKey info for id:{}\n{} UNIFI error".format(ID, USERs))
										else:
											if self.decideMyLog("Video"): self.indiLOG.log(10,"UNIFI error  getNVRCamerasFromMongoDB camera users   enableApiAccess disabled info for id:{}\n{}".format(ID, USERs))
						else:
										self.indiLOG.log(40,"getNVRCamerasFromMongoDB camera ACCOUNT bad _id / username / name info:\n{}".format(ACCOUNTs))

				server = self.getMongoData(cmdstr[0]+"server" +cmdstr[1])
				if len(server) >0:
					info["NVR"]		= server[0]

			if "cameras" in action:
				info["cameras"]	 = self.executeCMDonNVR( {}, "",  cmdType="get")
				if len(info["cameras"]) <1:
					info["cameras"] = self.getMongoData(cmdstr[0]+"camera" +cmdstr[1])
				if len(info["cameras"]) >0: self.fillCamerasIntoIndigo(info["cameras"], calledFrom="getNVRCamerasFromMongoDB")



			if doPrint:
				self.printNVRCameras(info)
			return info


		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return {}

	####-----------------	 ---------
	def printNVRCameras(self, info):
		return
		keepList = ["name","uuid","host","model","_id","firmwareVersion","systemInfo","mac","controllerHostAddress","controllerHostPort","deviceSettings","networkStatus","status","analyticsSettings","channels","ispSettings" ]
		out = ""
		try:
			outLine = ""
			if "NVR" in info:
				outLine += "\nSystem info-NVR:       --====================++++++++++++++++++++++++++++++++++++++++====================--"
				for key in info["NVR"]:
					outLine += "\n  {:19s}  {:}".format(key, info["NVR"][key])

				outLine += "\n== System info- users: --====================++++++++++++++++++++++++++++++++++++++++====================--"
			if "users" in info:
				nn = 0
				for user in info["users"]:
					out = ""
					for item in ["name","apiKey","enableApiAccess"] :
						out+=(item+":{}".format(info["users"][user][item])+"; ").ljust(30)
					outLine += "\n{} {}".format( (info["users"][user]["userName"]).ljust(18)+" # {}".format(nn), out.strip(";"))
					nn+=1


			if "cameras" in info:
				outLine +=       "\nSystem info- cameras:  --====================++++++++++++++++++++++++++++++++++++++++====================--"
				for camera in info["cameras"]:
					outLine += "\n{:19s}--===============--".format(camera["name"])
					for item in camera:
						if item =="name": continue
						if item in keepList or keepList == ["*"]:
							if item == "channels":
								nn = 0
								for channel in camera[item]:
									out = ("bitrates: {}".format(channel["minBitrate"])+"..{}".format(channel["maxBitrate"])) .ljust(30)
									for	 prop in ["enabled","isRtmpsEnabled","isRtspEnabled"]:
										if prop in channel:
											out+= prop+": {}".format(channel[prop])+";  "
									out = out.strip(";....")
									outLine += "\n{:22s} {:}".format("              channel#{}".format(nn), out)
									nn+=1
							elif item == "status":
								status = camera[item]
								out = ""
								for	 prop in ["remotePort","remoteHost"]:
									if prop in status:
										out+= prop+":{}".format(status[prop])+"; "
								out = out.strip("; ")
								outLine += "\n{:22s} {:}".format("              status{}".format(nn), out)
								for nn in range(len(status["recordingStatus"])):
									out	 =	("motionRecordingEnabled: {}".format(status["recordingStatus"]["{}".format(nn)]["motionRecordingEnabled"])).ljust(30)
									out += "; fullTimeRecordingEnabled: {}".format(status["recordingStatus"]["{}".format(nn)]["fullTimeRecordingEnabled"])
									outLine += "\n{:22s} {:}".format("           recordingSt:#{}".format(nn), out)
							else:
									outLine += "\n{:22s} {:}".format("  ", (item+":").ljust(25)+json.dumps(camera[item]))
			self.indiLOG.log(20,outLine)

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
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
			f = self.openEncoding(self.indigoPreferencesPluginDir+"MAC2INDIGO","r")
			self.MAC2INDIGO= json.loads(f.read())
			f.close()
		except:
			self.MAC2INDIGO= {"UN":{},"GW":{},"SW":{},"AP":{},"NB":{}}
		try:
			f = self.openEncoding(self.indigoPreferencesPluginDir+"MACignorelist","r")
			self.MACignorelist= json.loads(f.read())
			f.close()
		except:
			self.MACignorelist ={}
		try:
			f = self.openEncoding(self.indigoPreferencesPluginDir+"MACSpecialIgnorelist","r")
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
		self.suspendedUnifiSystemDevicesIP = {}
		try:
			f = self.openEncoding(self.indigoPreferencesPluginDir+"suspended", "r", showError=False)
			self.suspendedUnifiSystemDevicesIP = json.loads(f.read())
			f.close()
		except: pass
		self.writeSuspend()
	### ----------- manage suspend status
	####-----------------	 -----------   END



	### here we do the work, setup the logfiles listening and read the logfiles and check if everything is running

	### UDM log tracking
	####-----------------	 ---------
	def controllerWebApilogForUDM(self, waitBeforeStart):

		try:
			lastRecordTime	= 0
			lastRead   		= 0
			time.sleep(min(1,waitBeforeStart))
			self.indiLOG.log(10,"ctlWebUDM: launching web log get for runs every {} secs".format(self.controllerWebEventReadON) )
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
					eventLogList 		= self.executeCMDOnController(dataSEND={"_sort":"+time", "_limit":min(500,max(10,nrec))}, pageString="/stat/event/", jsonAction="returnData", cmdType="post")
					#eventLogList 		= self.executeCMDOnController(dataSEND={}, pageString="/stat/event/", jsonAction="returnData", cmdType="get") 
					thisRecIds			= []
					# test if we have overlap. if not read 3 times the data 
					for logEntry in eventLogList:
						thisRecIds.append(logEntry["_id"])
						if lastRecIds !=[] and logEntry["_id"] in lastRecIds: 
							lastRecIdFound = True

					if not lastRecIdFound and lastRecIds !=[]:
						eventLogList 		= self.executeCMDOnController(dataSEND={"_sort":"+time", "_limit":min(500,max(10,nrec*3))}, pageString="/stat/event/", jsonAction="returnData", cmdType="post")
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
						if "time" not in logEntry: 									continue 
						# the time stamp from UFNI is in msecs, convert to float secs
						logEntry["time"] /= 1000. 
						# skip already processed records
						if logEntry["time"] < lastTimeStamp:							continue
						lastTimeStamp = logEntry["time"] 
						# remove junk
						if "key" not in logEntry: 										continue
						if logEntry["key"].lower().find("login") >-1:					continue
						if "user" not in logEntry: 									continue
						#
						MAC = logEntry["user"]
						if self.decideMyLog("UDM", MAC=MAC): self.indiLOG.log(10,"ctlWebUDM  {}, rec#{} of {} recs; logEntry:{}".format(MAC, ii, len(thisRecIds), logEntry))

						# now we should have an ok event record
						apN 			= self.numberForUDM["AP"]
						ipNumberAP		= self.ipNumbersOf["AP"][apN]
						MAC_AP_Active 	= ""
						MAC_AP_from 	= ""

						# check if we have AP info, if not skip record
						if "ap" in logEntry: 
							fromTo = ""
							MAC_AP_Active = logEntry["ap"]
							self.createAPdeviceIfNeededForUDM(MAC_AP_Active, logEntry,   fromTo)
							if self.MAC2INDIGO["AP"][MAC_AP_Active]["ipNumber"] == "":
								self.indiLOG.log(10,"ctlWebUDM  ap-mac:{}  MAC2INDIGO: has empty ipNumber, logEntry:{}".format(MAC_AP_Active, logEntry))
								continue
							#if self.MAC2INDIGO["AP"][MAC_AP_Active]["ipNumber"] != self.ipNumbersOf["AP"][self.numberForUDM["AP"]]: continue  # ignore non UDM log entries 
						if "ap_from" in logEntry: 
							fromTo = "_from"
							MAC_AP_from	= logEntry["ap"+fromTo]
							self.createAPdeviceIfNeededForUDM(MAC_AP_from, logEntry,   fromTo)
							if self.MAC2INDIGO["AP"][MAC_AP_from]["ipNumber"] == "":
								self.indiLOG.log(10,"ctlWebUDM  ap-mac:{}  MAC2INDIGO: has empty ipNumber, logEntry:{}".format(MAC_AP_from, logEntry))
								continue
							logEntry["IP_from"]	= self.MAC2INDIGO["AP"][MAC_AP_from]["ipNumber"]
						if "ap_to" in logEntry: 
							fromTo = "_to"
							MAC_AP_Active = logEntry["ap"+fromTo]
							self.createAPdeviceIfNeededForUDM(MAC_AP_Active, logEntry, fromTo)
							if self.MAC2INDIGO["AP"][MAC_AP_Active]["ipNumber"] == "":
								self.indiLOG.log(10,"ctlWebUDM  ap-mac:{}  MAC2INDIGO: has empty ipNumber, logEntry:{}".format(MAC_AP_Active, logEntry))
								continue
							logEntry["IP_to"] 	= self.MAC2INDIGO["AP"][MAC_AP_Active]["ipNumber"]

						# for no ap log entry check if it about an existing devices, if yes: assign to UDM
						if MAC_AP_Active == "":
							if MAC in self.MAC2INDIGO["UN"]:
								for MACap in self.MAC2INDIGO["AP"]:
									if int(self.MAC2INDIGO["AP"][MACap]["apNo"]) == int(self.numberForUDM["AP"]):
										MAC_AP_Active = MACap
										break
										# skip this event, not about existing wifi devices ...
						logEntry["MAC_AP_Active"] = MAC_AP_Active

						if MAC_AP_Active == "":
							if self.decideMyLog("UDM", MAC=MAC): self.indiLOG.log(10,"ctlWebUDM  {}  ignoring: no 'ap': ..  given, logEntry:{}".format(MAC, logEntry))
							continue

						else:
							ipNumberAP = self.MAC2INDIGO["AP"][MAC_AP_Active]["ipNumber"]
							for nn in range(_GlobalConst_numberOfAP):
								if ipNumberAP == self.ipNumbersOf["AP"][nn]: 
									apN	= nn
									break

						self.doAPmessages([logEntry], ipNumberAP, apN, webApiLog=True)
					lastRecIds = copy.copy(thisRecIds)
				except	Exception as e:
					if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
				for ii in range(100):
					if not lastRecIdFound: break
					if self.pluginState == "stop": break
					time.sleep(1)
					if time.time() - lastRead > self.controllerWebEventReadON: break
			self.indiLOG.log(10,"ctlWebUDM: exiting plugin state = stop" )
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return 


	####----------------- thsi is for UDM devices only	 ---------
	def createAPdeviceIfNeededForUDM(self, MAC, line, fromTo):
		if MAC == "": 									return False
		if MAC in self.MAC2INDIGO["AP"]:				return True
		if self.unifiControllerType.find("UDM") == -1: 	return False

		self.indiLOG.log(30,"==> new UDM device to be created, mac :{}  not in self.MAC2INDIGO[AP]{} ".format(MAC, self.MAC2INDIGO["AP"]))

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
		if "radio"+fromTo in line: radio = line["radio"+fromTo]
		if "essid"+fromTo in line: essid = line["ssid"+fromTo]
		if "channel"+fromTo in line: 
			if int(line["channel"+fromTo]) > 11: GHz = "5"
			else: 								 GHz = "2"
			channel = line["channel"+fromTo]
		try:
			ipNDevice = self.ipNumbersOf["AP"][self.numberForUDM["AP"]]
			dev = indigo.device.create(
				protocol		= indigo.kProtocol.Plugin,
				address 		= MAC,
				name 			= devName+"_" + MAC,
				description		= self.fixIP(ipNDevice) + hostname,
				pluginId 		= self.pluginId,
				deviceTypeId	= "Device-AP",
				folder			= self.folderNameIDCreated,
				props			= {"useWhatForStatus":"",isType:True})
			self.setupStructures("AP", dev, MAC)
			self.setupBasicDeviceStates(dev, MAC, "AP", ipNDevice,"", "", " status up            AP WEB  new AP", "STATUS-AP")
			self.addToStatesUpdateList(dev.id,"essid_" + GHz, essid)
			self.addToStatesUpdateList(dev.id,"channel_" + GHz, channel)
			self.addToStatesUpdateList(dev.id,"MAC", MAC)
			self.addToStatesUpdateList(dev.id,"hostname", hostname)
			self.addToStatesUpdateList(dev.id,"nClients_" + GHz, nClients)
			self.addToStatesUpdateList(dev.id,"radio_" + GHz, radio)
			self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
			self.addToStatesUpdateList(dev.id,"model", model)
			self.addToStatesUpdateList(dev.id,"tx_power_" + GHz, tx_power)
			self.executeUpdateStatesList()
			indigo.variable.updateValue("Unifi_New_Device", "{}/{}/{}".format(dev.name, MAC, ipNDevice) )
			dev = indigo.devices[dev.id]
			self.setupStructures(xType, dev, MAC)
			return True

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return False


	####-----------------	 ---------
	def getcontrollerDBForClients(self):
		try:
			if not self.devsEnabled["DB"]:																	return 
			if time.time() - self.getcontrollerDBForClientsLast < float(self.readDictEverySeconds["DB"]):	return 
			#if self.decideMyLog("Special"): self.indiLOG.log(10,"getcontrollerDBForClients: start, read every:{}, dt:{}".format(self.readDictEverySeconds["DB"], time.time() - self.getcontrollerDBForClientsLast))

			if self.decideMyLog("DBinfo"): self.indiLOG.log(10,"getcontrollerDBForClients: start, read every:{}".format(self.readDictEverySeconds["DB"]))
			dataDict = self.executeCMDOnController(pageString="/stat/sta/", cmdType="get")
			if self.decideMyLog("DBinfo"): self.indiLOG.log(10,"getcontrollerDBForClients: \n{} ...".format("{}".format(dataDict)[0:500]) )

			self.fillcontrollerDBForClients(dataDict)
		except	Exception as e:
			if "{}".format(e).find("None") == -1:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

	####-----------------	 ---------
	def fillcontrollerDBForClients(self, dataDict):
		try:
			self.getcontrollerDBForClientsLast = time.time() 
			if len(dataDict) == 0: 
				return 

			xType = "UN"
			macsFound = []
			anyChange = 0 
			secChange = 0 
			nClients = 0.
			for client in dataDict:
				if len(client) == 0: 					continue
				if "mac" not in client: 				continue
				MAC = client["mac"]
				if MAC not in self.MAC2INDIGO[xType]: 	continue
				macsFound.append(MAC)
				nClients +=1.
				if "first_seen" in client:
					try: 	self.MAC2INDIGO[xType][MAC]["first_seen"]	= datetime.datetime.fromtimestamp(client["first_seen"]).strftime("%Y-%m-%d %H:%M:%S")
					except: pass

				if "use_fixedip" in client:
					self.MAC2INDIGO[xType][MAC]["use_fixedip"]	= client["use_fixedip"]
				else:
					self.MAC2INDIGO[xType][MAC]["use_fixedip"] = False

				if "blocked" in client:
					self.MAC2INDIGO[xType][MAC]["blocked"] = client["blocked"]
				else:
					self.MAC2INDIGO[xType][MAC]["blocked"] = False


				previousSeen = self.MAC2INDIGO[xType][MAC]["last_seen"]
				if  "last_seen" in client: 
					lastSeen = float(client["last_seen"])
					if previousSeen != lastSeen: 
						anyChange += 1.
						secChange += lastSeen - previousSeen
					self.MAC2INDIGO[xType][MAC]["last_seen"] = lastSeen
				else:
					self.MAC2INDIGO[xType][MAC]["last_seen"] = -1
					lastSeen = -1

				#if self.decideMyLog("DBinfo", MAC=MAC): self.indiLOG.log(10,"controlDB  {:15s}      client:{}".format(MAC, client) )
				if self.decideMyLog("DBinfo", MAC=MAC): self.indiLOG.log(10,"controlDB  {:15s}      delta delta(now-previous):{:9.0f}, dt lastseen{:9.0f} lastSeen:{:9.0f}".format(MAC, lastSeen - previousSeen, time.time()-lastSeen, lastSeen) )


			for MAC in copy.deepcopy(self.MAC2INDIGO[xType]):
				if MAC not in macsFound: 
					if self.MAC2INDIGO[xType][MAC]["last_seen"] > 0:
						self.MAC2INDIGO[xType][MAC]["last_seen"] = -1
					continue

				try: 
					devId =  self.MAC2INDIGO["UN"][MAC]["devId"] 
					if  devId not in indigo.devices:
						self.indiLOG.log(30,f"controlDB  MAC{MAC:} , devId:{devId:} not in indigo devices, removing")
						del self.MAC2INDIGO["UN"][MAC]
						continue
					changed = False
					dev = indigo.devices[self.MAC2INDIGO["UN"][MAC]["devId"]]
					if self.decideMyLog("DBinfo", MAC=MAC): 
							self.indiLOG.log(10,"controlDB  {:15s}  {:15s} {:32s};   delta lastUp:{:9.0f}, lastSeen-DB:{:9.0f}*{:9.0f}*{:9.0f}".format(
							MAC, dev.states["ipNumber"], dev.name, 
							time.time() - self.MAC2INDIGO[xType][MAC]["lastUp"],
							self.MAC2INDIGO[xType][MAC]["last_seen"] - self.MAC2INDIGO[xType][MAC]["lastUp"],
							time.time() - self.MAC2INDIGO[xType][MAC]["last_seen"],
							self.MAC2INDIGO[xType][MAC]["last_seen"]	
						) )

					if "first_seen" in self.MAC2INDIGO["UN"][MAC]:
						if "firstSeen" in dev.states and dev.states["firstSeen"] != self.MAC2INDIGO["UN"][MAC]["first_seen"]:
							changed = True
							self.addToStatesUpdateList(dev.id,"firstSeen",  self.MAC2INDIGO["UN"][MAC]["first_seen"])

					if "use_fixedip" in self.MAC2INDIGO["UN"][MAC]:
						if "useFixedIP" in dev.states and dev.states["useFixedIP"] != self.MAC2INDIGO["UN"][MAC]["use_fixedip"]:
							changed = True
							self.addToStatesUpdateList(dev.id,"useFixedIP",  self.MAC2INDIGO["UN"][MAC]["use_fixedip"])

					if "blocked" in dev.states:
						if dev.states["blocked"] != self.MAC2INDIGO["UN"][MAC]["blocked"]:
							changed = True
							self.addToStatesUpdateList(dev.id,"blocked",  self.MAC2INDIGO["UN"][MAC]["blocked"])
					if changed:
						self.executeUpdateStatesList()

				except	Exception as e:
					if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
					if "{}".format(e).find("timeout waiting for response")>-1:
						self.getcontrollerDBForClientsLast = time.time()
						return 

			self.getcontrollerDBForClientsLast = time.time()

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return 


	### here we do the work, setup the logfiles listening and read the logfiles and check if everything is running, if not restart
	####-----------------	 ---------
	def getMessages(self, ipNumber, apN, uType, waitAtStart):

		apnS = "{}".format(apN)
		self.addTypeToDataStats(ipNumber, apnS, uType)
		self.msgListenerActive[uType] = time.time() - 200
		try:
			self.sleep(max(1.,min(60, waitAtStart )))
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
			minWaitbeforeRestart		= 135. #max(float(self.restartIfNoMessageSeconds), float(repeatRead) )
			lastOkRestart				= time.time()
			restartCode					= 0
			apNint 						= int(apN)
			noDataCounter 				= 0
			noDataCounterMax			= {"tail":100,"dict":30}
			self.testServerIfOK(ipNumber,uType)
			if uType.find("tail") >-1:  useType = "tail"
			else:						useType = "dict"

			if  useType == "tail":
				self.lastMessageReceivedInListener[ipNumber] = time.time()

			self.lastResetUnifiDevice[ipNumber] = time.time()

			consumeDataTime = 0
			while True:

				if self.pluginState == "stop" or not self.connectParams["enableListener"][uType]: 
					try:	self.killPidIfRunning(ListenProcessFileHandle.pid)
					except:	pass
					break

					## should we stop?, is our IP number listed?
				if ipNumber in self.stop:
					self.indiLOG.log(10,"{}  getMessage: stop = True for ip# {}".format(uType, ipNumber) )
					self.stop.remove(ipNumber)
					return

				if ipNumber in self.suspendedUnifiSystemDevicesIP:
					self.sleep(max(1, self.suspendedUnifiSystemDevicesIP[ipNumber]-time.time()))
					goodDataReceivedTime = 1
					continue

				self.sleep(min(15, msgSleep))

				retCode, startErrorCount, ListenProcessFileHandle, goodDataReceivedTime, aliveReceivedTime, combinedLines, lastRestartCheck, lastOkRestart = \
					self.checkIfRestartNeeded( 
						restartCode, goodDataReceivedTime, aliveReceivedTime, startErrorCount, combinedLines, minWaitbeforeRestart, msgSleep, lastRestartCheck, restartCount, uType, ipNumber, apnS, lastMSG, ListenProcessFileHandle, lastOkRestart
					)
				if retCode == 2: continue
				else: 			 restartCode = 0


				## here we actually read the stuff
				goodDataReceivedTime, aliveReceivedTime, newlinesFromServer, msgSleep, newDataStartTime = self.readFromUnifiDevice( goodDataReceivedTime, aliveReceivedTime, ListenProcessFileHandle, uType, ipNumber, msgSleep, newlinesFromServer, newDataStartTime)
				if newlinesFromServer == "": 
					noDataCounter += 1
					if self.debugThisDevices(uType, apNint):
						if noDataCounter % noDataCounterMax[useType] == 0:
							self.indiLOG.log(20,"noDataCounter for: {} {}  = {} tries".format(ipNumber, uType, noDataCounter))
					continue


				if self.debugThisDevices(uType, apNint):
					if noDataCounter >  noDataCounterMax[useType] :
						self.indiLOG.log(20,"noDataCounter for: {} {}  = {} new data received, reset counter".format(ipNumber, uType, noDataCounter))

				noDataCounter = 0 

				if self.pluginState == "stop": 
					try:	self.killPidIfRunning(ListenProcessFileHandle.pid)
					except:	pass
					return

				self.dataStats["tcpip"][uType][ipNumber]["inMessageCount"] += 1
				self.dataStats["tcpip"][uType][ipNumber]["inMessageBytes"] += len(newlinesFromServer)


				if self.debugThisDevices(uType, apNint):
					if len(newlinesFromServer) > 300:
						self.indiLOG.log(10,"getMessages-Data: {}-{} len:{:}, line:{}         ...         {}".format(ipNumber, uType, len(newlinesFromServer), newlinesFromServer[0:200].replace("\n","").replace("\r",""), newlinesFromServer[-200:].replace("\n","").replace("\r","")))
					else:
						self.indiLOG.log(10,"getMessages-Data: {}-{} len:{:}, line:{} ".format(ipNumber, uType, len(newlinesFromServer), newlinesFromServer.replace("\n","").replace("\r","")))

				restartCode = self.checkIfErrorReceived(newlinesFromServer, ipNumber)
				if restartCode > 0: 
					if self.retcodeNotOk(restartCode, goodDataReceivedTime, uType,ipNumber, newlinesFromServer):
						goodDataReceivedTime = 1
						continue


				######### for tail logfile
				consumeDataTime = time.time()
				if useType == "tail":
					restartCode = self.checkIfErrorReceivedTail(newlinesFromServer, ipNumber)
					if self.retcodeNotOk(restartCode, goodDataReceivedTime, uType, ipNumber, newlinesFromServer):
						goodDataReceivedTime = 1

						continue
					goodDataReceivedTime, lastMSG = self.checkAndPrepTail(newlinesFromServer, goodDataReceivedTime, ipNumber, uType, unifiDeviceType, apN)

				######### for Dicts
				elif useType == "dict":
					restartCode = self.checkIfErrorReceivedDict(newlinesFromServer, combinedLines, ipNumber)
					if self.retcodeNotOk(restartCode, goodDataReceivedTime, uType,ipNumber, newlinesFromServer):
						goodDataReceivedTime = 1
						continue
					goodDataReceivedTime, combinedLines, lastMSG = self.checkAndPrepDict( newlinesFromServer, goodDataReceivedTime, combinedLines, ipNumber, uType, unifiDeviceType, minWaitbeforeRestart, apN, newDataStartTime)

				## bad setup is wrong, extit
				else:
					self.indiLOG.log(40,"bad parameters for: {} {}".format(ipNumber, uType))
					return 

				consumeDataTime -= time.time()
				if consumeDataTime < -1:
					msgSleep = 0

				if self.statusChanged > 0:
					self.setGroupStatus()

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		self.indiLOG.log(30,"getMessages: stopping listener process for :{} - {}".format(uType, ipNumber )  )
		return

	####-----------------	 ---------
	def debugThisDevices(self, uType, Nint):
		try:
			ut = uType[0:2]
			if ( (ut == "SW" and Nint >= 0 and Nint < len(self.debugDevs["SW"]) and self.debugDevs["SW"][Nint]) or
				 (ut == "AP" and Nint >= 0 and Nint < len(self.debugDevs["AP"]) and self.debugDevs["AP"][Nint]) or 
				 (ut == "GW" and self.debugDevs["GW"][0]) ): 
				return True
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return False
		
	####-----------------	 ---------
	def retcodeNotOk(self, restartCode, goodDataReceivedTime,  uType, ipNumber, newlinesFromServer):
		try:
			if restartCode > 0: 
				if self.rebootUnifiDeviceOnError:
					self.indiLOG.log(20,"getMessages: code:{:}  need restart of listener and send reboot if code>10- lastDataRceived:{:.1f}; from {:}-{:}  lines:{:}".format(restartCode, time.time()-goodDataReceivedTime, ipNumber, uType, newlinesFromServer.strip("\n")))
					self.suspendedUnifiSystemDevicesIP[ipNumber] = time.time() + 60.
					if restartCode > 10: self.resetUnifiDevice(ipNumber, uType)
					self.sleep(60.)
					try: del self.suspendedUnifiSystemDevicesIP[ipNumber]
					except: pass
					return True

				self.indiLOG.log(20,"getMessages: code:{:} - no reboot issued, blocked by:rebootUnifiDeviceOnError=False, lastDataRceived:{:.1f}; from {:}-{:}  lines:{:}".format(restartCode, time.time()-goodDataReceivedTime, ipNumber, uType, newlinesFromServer.strip("\n")))
			return False

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return False

	####-----------------	 ---------
	def checkIfRestartNeeded(self, restartCode, goodDataReceivedTime, aliveReceivedTime, startErrorCount, combinedLines, minWaitbeforeRestart, msgSleep, lastRestartCheck, restartCount, uType, ipNumber, apnS, lastMSG, ListenProcessFileHandle, lastOkRestart):
		try:
			retCode = 0
			lastRestartCheck = time.time()
			if len(self.restartRequest) > 0:
				#self.indiLOG.log(10,"getMessages: {}-{}-{} #req:{};  restart requested dict:{}".format(ipNumber, uType,apnS, self.restartRequest[uType].split("-")[0], self.restartRequest) )
				if uType in self.restartRequest:
					if self.restartRequest[uType].split("-")[0] == apnS:
						if self.restartRequest[uType].find("reset")  > -1:
							if self.rebootUnifiDeviceOnError:
								self.resetUnifiDevice(ipNumber, uType)
								self.sleep(25) 
						self.indiLOG.log(10,"getMessages: {}    restart requested by menu ".format(self.restartRequest) )
						goodDataReceivedTime = -1
						self.restartRequest = {}

			forcedRestart  = time.time() - lastOkRestart 
			restartTimeout = time.time() - goodDataReceivedTime

			if restartTimeout < minWaitbeforeRestart and goodDataReceivedTime > 0 and forcedRestart < self.restartListenerEvery and restartCode == 0: 
				# nothing to do
				return retCode, startErrorCount, ListenProcessFileHandle, goodDataReceivedTime, aliveReceivedTime, combinedLines, lastRestartCheck, lastOkRestart

			## ned to restart, either new or launch command, or no messages for xx secs
			if goodDataReceivedTime < 0:# at startup
				self.indiLOG.log(10,"getMessages: launching listener for: {} / {}".format(uType, ipNumber) )

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
				self.indiLOG.log(logLevel,"getMessages: relaunching {} / {} / {}: code:{}; timeSinceLastRestart {:.0f} > forcedRestart:{:.0f} [sec]  ;  without message:{:.1f}[sec], limitforRestart:{:.1f}[sec], restartCount:{:},  len(msg):{:}; lastMSG:{:}<<".format(self.connectParams["expectCmdFile"][uType], uType, ipNumber, restartCode, forcedRestart, self.restartListenerEvery, restartTimeout, minWaitbeforeRestart, restartCount, len(lsm), lsm[-100:].replace("\r","") )  )

				self.dataStats["tcpip"][uType][ipNumber]["restarts"] += 1

				if restartCount in [3,5,7]:
					self.connectParams["promptOnServer"][ipNumber] = ""

				
			if ListenProcessFileHandle != "": 
				self.killPidIfRunning(ListenProcessFileHandle.pid)


			if not self.testServerIfOK(ipNumber,uType):
				if ipNumber in self.connectParams["promptOnServer"]:
					prompt = self.connectParams["promptOnServer"][ipNumber]
				else: 
					prompt = "not defined"

				self.indiLOG.log(40,"getMessages: (1 - test connect)  error for {}, ip#: {}, prompt:'{}'; wrong ip/ password or system down or ssh timed out or ..? ".format(uType, ipNumber, prompt) )
			
				self.msgListenerActive[uType] = 0
				retCode = 2
				combinedLines = ""
				time.sleep(15)
				return retCode, startErrorCount, ListenProcessFileHandle, goodDataReceivedTime, aliveReceivedTime, combinedLines, lastRestartCheck, lastOkRestart

			if uType=="VDtail":
				self.setAccessToLog(ipNumber,uType)

			ListenProcessFileHandle, startError = self.startConnect(ipNumber,uType)
			combinedLines = ""
			if self.decideMyLog("Expect"):
				try: 	pid = ListenProcessFileHandle.pid
				except:	pid = "not defined"
				self.indiLOG.log(10,"getMessages: ListenProcess started for uType: {};  ip: {}, prompt:'{}', pid:{}".format(uType, ipNumber, self.connectParams["promptOnServer"][ipNumber], pid) )


			if startError != "":
				startErrorCount +=1
				if startErrorCount%3== 0:
					self.indiLOG.log(40,"getMessages: connect start connect error in listener {}, to  @ {}  ::::{}::::".format(uType, ipNumber, startError) )
				retCode = 2
				self.sleep(15)
				return retCode, startErrorCount, ListenProcessFileHandle, goodDataReceivedTime, aliveReceivedTime, combinedLines, lastRestartCheck, lastOkRestart

			self.msgListenerActive[uType]	= time.time()
			goodDataReceivedTime 			= time.time()
			aliveReceivedTime 	 			= time.time()
			lastOkRestart					= time.time()

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
			combinedLines 	= ""
			retCode 		= 2
			self.sleep(15)

		return retCode, startErrorCount, ListenProcessFileHandle, goodDataReceivedTime, aliveReceivedTime, combinedLines, lastRestartCheck, lastOkRestart


	####-----------------	 ---------
	def readFromUnifiDevice(self, goodDataReceivedTime, aliveReceivedTime, ListenProcessFileHandle, uType, ipNumber, msgSleep, lastLine, newDataStartTime):
		try:
			try:
				if ListenProcessFileHandle == "": 
					self.indiLOG.log(20,"readFromUnifiDevice: read handle not defined for {}-{}, sleeping 15 secs ".format(uType, ipNumber))
					newlinesFromServer		= ""
					goodDataReceivedTime	= 1 # this forces a restart of the listener
					msgSleep				= 15
					self.sleep(10)
					return goodDataReceivedTime, aliveReceivedTime, newlinesFromServer, msgSleep, newDataStartTime

				newlinesFromServer = ""
				lfs = ""
				lfs = os.read(ListenProcessFileHandle.stdout.fileno(),self.readBuffer).decode("utf8") 
				newlinesFromServer = "{}".format(lfs) 
				if newlinesFromServer != "":
					aliveReceivedTime = time.time()

				msgSleep = 0.2 # fast read to follow, if data 
				if lastLine == "" and  newlinesFromServer != "": 
					newDataStartTime = time.time()

			except	Exception as e:
				if uType.find("dict") >-1:	msgSleep = 2 # nothing new, can wait, dicts come every 60 secs 
				else:						msgSleep = 0.4 # this is for tail 

				if "{}".format(e).find("[Errno 35]") == -1:	 # "Errno 35" is the normal response if no data, if other error stop and restart
					if "{}".format(e).find("None") == -1:
						out = "os.read(ListenProcessFileHandle.stdout.fileno())  in Line {} has error={}\n ip:{}  type: {}".format(sys.exc_info()[2].tb_lineno, e, ipNumber,uType )
						try: out+= "fileNo: {}".format(ListenProcessFileHandle.stdout.fileno() )
						except: pass
						if "{}".format(e).find("[Errno 22]") > -1:  # "Errno 22" is  general read error "wrong parameter"
							out+= "\n ..      try lowering/increasing read buffer parameter in config" 
							self.indiLOG.log(30,out)
						else:
							self.indiLOG.log(40,out)
							self.indiLOG.log(40,lfs)
					goodDataReceivedTime = 1 # this forces a restart of the listener
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		return goodDataReceivedTime, aliveReceivedTime, newlinesFromServer, msgSleep, newDataStartTime

	####-----------------	 ---------
	def checkIfErrorReceived(self, newlinesFromServer, ipNumber):
		try:
			retCode = 0
			## any error messages from OSX 
			if newlinesFromServer.find("closed by remote host") > -1:											retCode = 1
			elif newlinesFromServer.find("Killed by signal") > -1:												retCode = 2
			elif newlinesFromServer.find("Killed -9") > -1:														retCode = 3
			#elif newlinesFromServer.find("Broken pipe") > -1:													retCode = 4 # only shows AFTER  reboot finished
			elif newlinesFromServer.find("[reboot] reboot") > -1:												retCode = 5
			return retCode

		except	Exception as e:
			if "{}".format(e).find("None")== -1: self.indiLOG.log(40,"", exc_info=True)
		return retCode


	####-----------------	 ---------
	def checkIfErrorReceivedDict(self, newlinesFromServer, combinedLines, ipNumber):
		try:
			retCode = 0
			## any error messages from UNIFI device
			if newlinesFromServer.find("mca-ctrl: error")> -1:													retCode = 11 #mca-ctrl: error while loading shared libraries: libubus.so: cannot ope...
			elif len(newlinesFromServer) < 200 and len(combinedLines) < 500:
				pos6 = newlinesFromServer.find("xxxThisIsTheEndTokenxxx255")
				if pos6 > -1 and pos6 < 100: 																	retCode = 12 

			return retCode

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return retCode

	####-----------------	 ---------
	def checkIfErrorReceivedTail(self, newlinesFromServer, ipNumber):
		try:
			retCode = 0
			## any error messages from UNIFI device
			if newlinesFromServer.find("user.notice syswrapper: [state is locked] waiting for lock") > -1:		retCode = 21
			return retCode

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return retCode

	####-----------------	 ---------
	def checkAndPrepTail(self, newlinesFromServer, goodDataReceivedTime, ipNumber, uType, unifiDeviceType, apN):
		try:
			lastMSG = newlinesFromServer
			## fill the queue and send to the method that uses it
			if		unifiDeviceType == "AP":
				self.deviceUp["AP"][ipNumber] = time.time()
			elif	unifiDeviceType == "GW":
				self.deviceUp["GW"][ipNumber] = time.time()
			elif	unifiDeviceType == "VD":
				self.deviceUp["VD"][ipNumber] = time.time()
			self.msgListenerActive[uType]  = time.time()

			if time.time() > self.lastMessageReceivedInListener[ipNumber]: 
				self.lastMessageReceivedInListener[ipNumber] = time.time()

			# we accept any message as good data 
			goodDataReceivedTime = time.time()

			if newlinesFromServer.find("ThisIsTheAliveTestFromUnifiToPlugin") > -1:
				self.dataStats["tcpip"][uType][ipNumber]["aliveTestCount"] += 1
				if self.decideMyLog("ExpectRET"): self.indiLOG.log(10,"getMessage: {} {} ThisIsTheAliveTestFromUnifiToPlugin received ".format(uType, ipNumber))
			else:
				self.logQueue.put((newlinesFromServer,ipNumber,apN, uType,unifiDeviceType))

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
			self.indiLOG.log(30,"checkAndPrepTail: error for {} - {}".format(uType, ipNumber )  )
		return goodDataReceivedTime, lastMSG


	####-----------------	 ---------
	def checkAndPrepDict(self, newlinesFromServer, goodDataReceivedTime, combinedLines, ipNumber, uType, unifiDeviceType, minWaitbeforeRestart, apN, newDataStartTime):
		try:
			combinedLines += newlinesFromServer
			lastMSG = combinedLines
			ppp = combinedLines.split(self.connectParams["startDictToken"][uType])
			if self.debugThisDevices(uType, apN):
					self.indiLOG.log(10,"checkAndPrepDict:  {}/{} , check ==2?:{} into check 1 startDictToken:'{:}' , inputlines:{} first 100 ".format(uType, ipNumber, len(ppp), self.connectParams["startDictToken"][uType], combinedLines[0:100]))

			if len(ppp) == 2:
				endTokenPos = ppp[1].find(self.connectParams["endDictToken"][uType])
				if self.debugThisDevices(uType, apN):
					self.indiLOG.log(10,"checkAndPrepDict:  {}/{} ,  into check endTokenPos:{}, endDictToken {:}' ".format(uType, ipNumber, endTokenPos, self.connectParams["endDictToken"][uType]))
				if endTokenPos > -1:
					if self.debugThisDevices(uType, apN):
						self.indiLOG.log(10,"checkAndPrepDict:  {}/{} , raw data:{} 0:200".format(uType, ipNumber,  ppp[1][0:200]))

					dictData = ppp[1].lstrip("\r\n")
					try:
						dictData = dictData[0:endTokenPos]
						## remove last line
						if dictData[-1] !="}":
							ppp = dictData.rfind("}")
							dictData = dictData[0:ppp+1]
						theDict= json.loads(dictData)
						if	  unifiDeviceType == "AP":
							self.deviceUp["AP"][ipNumber]	= time.time()
						elif  unifiDeviceType == "SW":
							self.deviceUp["SW"][ipNumber]	= time.time()
						elif  unifiDeviceType == "GW":
							self.deviceUp["GW"][ipNumber]	= time.time()
						elif  unifiDeviceType == "UD":
							self.deviceUp["SW"][ipNumber]	= time.time()
							self.deviceUp["UD"]				= time.time()
							self.deviceUp["GW"][ipNumber]	= time.time()

						combinedLines = ""
						self.logQueueDict.put((theDict, ipNumber, apN, uType, unifiDeviceType))
						goodDataReceivedTime = time.time()
						self.dataStats["tcpip"][uType][ipNumber]["inErrorTime"] -= 30

					except	Exception as e:
							if "{}".format(e).find("None") == -1: self.indiLOG.log(30,"{}; checkAndPrepDict: bad/incomplete data receivced from {}/{} @ line#,Module,Statement:{}, \nraw data:{}".format(e, uType, ipNumber,  traceback.extract_tb(sys.exc_info()[2])[-1][1:], ppp))
							pingTest = self.testAPandPing(ipNumber,uType) 
							okTest = self.testServerIfOK(ipNumber,uType) 
							retryPeriod = float(self.readDictEverySeconds[uType[0:2]]) + 10.
							if time.time() - self.dataStats["tcpip"][uType][ipNumber]["inErrorTime"] < retryPeriod or not pingTest or not okTest:
								msgF = combinedLines.replace("\r","").replace("\n","")
								self.indiLOG.log(20,"checkAndPrepDict JSON len:{}; {}...\n...  {}".format(len(combinedLines),msgF[0:100], msgF[-40:]) )
								self.indiLOG.log(20,".... in receiving DICTs for {}-{};  for details check unifi logfile  at: {} ".format(uType, ipNumber, self.PluginLogFile ))
								self.indiLOG.log(10,".... ping test:  {}".format(" ok " if pingTest  else " bad") )
								self.indiLOG.log(10,".... ssh test:   {}".format(" ok " if okTest else " bad") )
								self.indiLOG.log(10,".... uid/passwd:>{}<".format(self.getUidPasswd(uType, ipNumber)) )
							else:
								self.indiLOG.log(20,"getMessage, error reading dict >{}-{}<, not complete? len(data){}, endTokenPos:{}; error:{} ---- retrying".format(uType, ipNumber, len(dictData), endTokenPos, e) )

							self.dataStats["tcpip"][uType][ipNumber]["inErrorCount"]+=1
							self.dataStats["tcpip"][uType][ipNumber]["inErrorTime"] = time.time()
							goodDataReceivedTime = time.time() - minWaitbeforeRestart*0.95
					combinedLines = ""
			else:
				combinedLines = ""

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
			self.indiLOG.log(30,"checkAndPrepDict: error for {} - {}".format(uType, ipNumber )  )
			goodDataReceivedTime = 1
			combinedLines = ""
		return goodDataReceivedTime, combinedLines, lastMSG


	### start the expect command to get the logfile
	####-----------------	 ---------
	def startConnect(self, ipNumber, uType):
		try:
			userid, passwd = self.getUidPasswd(uType,ipNumber)
			if userid =="": return

			if self.decideMyLog("Expect"): self.indiLOG.log(10,"startConnect: with IP: {:<15};   uType: {};   UID/PWD: {}/{}".format(ipNumber, uType, userid, passwd) )

			if ipNumber not in self.listenStart:
				self.listenStart[ipNumber] = {}
			self.listenStart[ipNumber][uType] = time.time()
			if self.connectParams["commandOnServer"][uType].find("off") == 0: return "",""

			TT= uType[0:2]
			for ii in range(20):
				if uType.find("dict") > -1:
					cmd  = self.expectPath + " '" 
					cmd += self.pathToPlugin + self.connectParams["expectCmdFile"][uType] + "' "
					cmd += "'"+userid + "' '"+passwd + "' " 
					cmd += ipNumber + " " 
					cmd += "'"+self.escapeExpect(self.connectParams["promptOnServer"][ipNumber]) + "' " 
					cmd += self.connectParams["endDictToken"][uType]+ " " 
					cmd += "{}".format(self.readDictEverySeconds[TT])+ " " 
					cmd += "{}".format(self.timeoutDICT)
					cmd += " \""+self.connectParams["commandOnServer"][uType]+"\" "
					if uType.find("AP") > -1:
						cmd += " /var/log/messages"
					else:
						cmd += "  doNotSendAliveMessage"

				else:
					cmd = self.expectPath + " '" 
					cmd +=  self.pathToPlugin +self.connectParams["expectCmdFile"][uType] + "' "
					cmd += "'"+userid + "' '"+passwd + "' "
					cmd += ipNumber + " "
					cmd += "'"+self.escapeExpect(self.connectParams["promptOnServer"][ipNumber])+"' " 
					cmd += " \""+self.connectParams["commandOnServer"][uType]+"\" "

				cmd +=  self.getHostFileCheck()
				if self.decideMyLog("Expect"): self.indiLOG.log(20,"startConnect: cmd {}".format(cmd) )
				ListenProcessFileHandle = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
				##pid = ListenProcessFileHandle.pid
				msg = "{}".format(ListenProcessFileHandle.stderr)
				if msg.find("open file") == -1 and msg.find("io.BufferedReader") == -1:	# try this again
					self.indiLOG.log(40,"startConnect {}; IP#: {}; error connecting {}".format(uType, ipNumber, msg) )
					self.sleep(20)
					continue

				# set the O_NONBLOCK flag of ListenProcessFileHandle.stdout file descriptor:
				flags = fcntl.fcntl(ListenProcessFileHandle.stdout, fcntl.F_GETFL)  # get current p.stdout flags
				fcntl.fcntl(ListenProcessFileHandle.stdout, fcntl.F_SETFL, flags | os.O_NONBLOCK)

				return ListenProcessFileHandle, ""
			self.sleep(0.1)
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
			return "", "error {}".format(e)
		self.indiLOG.log(40,"startConnect timeout, not able to  connect after 20 tries ")
		return "","error connecting"



	####-----------------	 ---------
	def createEntryInUnifiDevLog(self):
		try:
			if not self.createEntryInUnifiDevLogActive: return 
			if time.time() - self.lastcreateEntryInUnifiDevLog < 12: return 
			self.lastcreateEntryInUnifiDevLog = time.time()
			doTestIflastMsg = 80 # do a test if last msg from listener is > xx sec ago 
			#if self.decideMyLog("Special"):self.indiLOG.log(10,"createEntryInUnifiDevLog: testing if we should do test ok, now:{}; lastmsgs:\n{}".format(time.time(), self.lastMessageReceivedInListener ))

			if self.devsEnabled["GW"] and not self.devsEnabled["UD"]:
				ipN = self.ipNumbersOf["GW"]
				if ipN in self.lastMessageReceivedInListener and  time.time() - self.lastMessageReceivedInListener[ipN] > doTestIflastMsg: 
					self.testServerIfOK( ipN, "GW", batch=True)

			for aa in ["AP","SW"]:
				if self.numberOfActive[aa] > 0:
					for ll in range(len(self.devsEnabled[aa])):
						if self.devsEnabled[aa][ll]:
							if (self.unifiControllerType == "UDM" or self.controllerWebEventReadON > 0) and ll == self.numberForUDM[aa]: continue
							ipN = self.ipNumbersOf[aa][ll]
							if ipN in self.lastMessageReceivedInListener  and  time.time() - self.lastMessageReceivedInListener[ipN] > doTestIflastMsg: 
								self.testServerIfOK( ipN, aa, batch=True)
	
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return 



	####-----------------	 ---------
	def testServerIfOK(self, ipNumber, uType, batch=False):
		try:
			userid, passwd = self.getUidPasswd(uType,ipNumber)
			if userid == "": 
				self.indiLOG.log(40,"testServerIf ssh connection OK: userid>>{}<<, passwd>>{}<<  wrong for {}-{}".format(userid, passwd, uType, ipNumber) )
				return False

			cmd = self.expectPath+ " '" + self.pathToPlugin +"test.exp' '" + userid + "' '" + passwd + "' " + ipNumber 
			cmd+= self.getHostFileCheck()


			if ipNumber in self.lastMessageReceivedInListener: self.lastMessageReceivedInListener[ipNumber] = time.time()

			if batch:
				#if self.decideMyLog("Special"): self.indiLOG.log(10,"testServer ssh to {}-{} to create log entry using:{}".format(uType, ipNumber, cmd) )
				if self.decideMyLog("Expect"): self.indiLOG.log(10,"testServerIfOK: batch {}".format(cmd) )
				subprocess.Popen(cmd+" &", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
				return 

			if self.decideMyLog("Expect"): self.indiLOG.log(10,"testServerIfOK: {}".format(cmd) )
			ret, err = self.readPopen(cmd)
			xx = ret.replace("\r","")
			if self.decideMyLog("ExpectRET"): self.indiLOG.log(10,"returned from expect-command: {}".format(xx))

			## check if we need to fix unknown host in .ssh/known_hosts
			if len(err) > 0:
				self.indiLOG.log(40,"testServerIf ssh connection to server failed, cmd: {}".format(cmd) )
				retx, ok = self.fixHostsFile(ret,ipNumber)
				if not ok: 
					self.indiLOG.log(40,"testServerIfOK failed, will retry ")
					ret, err = self.readPopen(cmd)
					xx = ret.replace("\r","")

			test = xx.lower()
			tags = ["welcome","unifi","debian","edge","busybox","ubiquiti","ubnt","login"]
			loggedIn = False
			for tag in tags:
				if tag in test: 
					loggedIn = True
					break
			if loggedIn:
				nPrompt = 3
				if ipNumber in self.connectParams["promptOnServer"]:
					if self.connectParams["promptOnServer"][ipNumber]  == xx[-nPrompt:]: 
						return True
					else:
						self.indiLOG.log(10,"testServerIfOK: =========== {}; prompt not found or reset by restart;  old:'{}', new candidate:'{}'".format(ipNumber, self.escapeExpect(self.connectParams["promptOnServer"][ipNumber]),  xx[-nPrompt:]) )
						pass
				else:
					self.connectParams["promptOnServer"][ipNumber] = ""
					self.indiLOG.log(10,"testServerIfOK: =========== ipNumber:{} not in connectParams".format(ipNumber) )

				prompt= xx[-nPrompt:]
				# remove new line from prompts would screw up expect, does not like newline in variables ...
				newL = prompt.find("\n")
				if newL == -1: 
					newL = prompt.find("\r")

				if   newL	== 0: 				prompt = prompt[1:]
				elif newL	== len(prompt)-1:	prompt = prompt[:-1]
				nPrompt = len(prompt)
				self.indiLOG.log(10,"testServerIfOK: =========== for {}  ssh response, setting promp to:'{}' using last {} chars in ...{}<<<< ".format(ipNumber,  prompt, nPrompt,   xx[-20:]) )


				self.connectParams["promptOnServer"][ipNumber] = prompt
				
				self.pluginPrefs["connectParams"] = json.dumps(self.connectParams)

				self.indiLOG.log(10,"testServerIfOK: =========== known prompts: \n{}".format(self.connectParams["promptOnServer"]))
				return True

			self.indiLOG.log(10,"testServerIfOK: ==========={}  ssh response, tags {} not found : ==> \n{}".format(ipNumber, tags, xx) )
			return False
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return False

####-------------------------------------------------------------------------####
	def fixHostsFile(self, ret, ipNumber):
		try:
			if ret.find(".ssh/known_hosts:") > -1:
				ret, err = self.readPopen("/usr/bin/csrutil status" )
				if ret.find("enabled") > -1:
					self.indiLOG.log(40,'ERROR can not update hosts known_hosts file,    "/usr/bin/csrutil status" shows system enabled SIP; please edit manually with \n"nano {}/.ssh/known_hosts"\n and delete line starting with {}'.format(self.MAChome, ipNumber) )
					self.indiLOG.log(40,"trying to fix from within plugin, if it happens again you need to do it manually")
					try:
						f = self.openEncoding(self.MAChome+'/.ssh/known_hosts',"r")
						lines = f.readlines()
						f.close()
						f = self.openEncoding(self.MAChome+'/.ssh/known_hosts',"w")
						for line in lines:
							if line.find(ipNumber) >-1: continue
							if len(line) < 10: continue
							f.write(line+"\n")
						f.close()
					except Exception as e:
						if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

					return ["",""], False

				fix1 = ret.split("Offending RSA key in ")
				if len(fix1) > 1:
					fix2 = fix1[1].split("\n")[0].strip("\n").strip("\n")
					fix3 = fix2.split(":")
					if len(fix3) > 1:
						fixcode = "/usr/bin/perl -pi -e 's/\Q$_// if ($. == " + fix3[1] + ");' " + fix3[0]
						self.indiLOG.log(40, "wrong RSA key, trying to fix with: {}".format(fixcode) )
						ret, err = self.readPopen(fixcode )
 
		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return ret, True


	####-----------------	 ---------
	def setAccessToLog(self, ipNumber, uType):
		try:
			userid, passwd = self.getUidPasswd(uType,ipNumber)
			if userid =="": return False

			cmd = self.expectPath +" '" + self.pathToPlugin +"setaccessToLog.exp' '" + userid + "' '" + passwd + "' " + ipNumber + " '" +self.escapeExpect(self.connectParams["promptOnServer"][ipNumber])+"' "
			cmd +=  self.getHostFileCheck()
			#if self.decideMyLog("Expect"): 
			if self.decideMyLog("Expect"): self.indiLOG.log(10,cmd)
			ret, err = self.readPopen(cmd)
			if self.decideMyLog("ExpectRET"): self.indiLOG.log(10,"returned from expect-command: {}".format(ret))
			test = ret.lower()
			tags = ["welcome","unifi","debian","edge","busybox","ubiquiti","ubnt","login"]
			for tag in tags:
				if tag in test:	 return True
			self.indiLOG.log(10,"\n==========={}  ssh response, tags {} not found : ==> {}".format(ipNumber, tags, test) )
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return False

	####-----------------	 ---------
	def getUidPasswd(self, uType, ipNumber):

		try:
			if uType.find("VD") > -1:
				userid = self.connectParams["UserID"]["unixNVR"]
				passwd = self.connectParams["PassWd"]["unixNVR"]

			else:
				if self.unifiControllerType.find("UDM") > -1 and (
					( uType.find("AP") > -1 and ipNumber == self.ipNumbersOf["AP"][self.numberForUDM["AP"]]) or
					( uType.find("SW") > -1 and ipNumber == self.ipNumbersOf["SW"][self.numberForUDM["SW"]]) or
					( uType.find("UD") > -1 ) or
					( uType.find("GW") > -1 and ipNumber == self.ipNumbersOf["GW"]) ):
					userid = self.connectParams["UserID"]["unixUD"]
					passwd = self.connectParams["PassWd"]["unixUD"]
				else:	
					userid = self.connectParams["UserID"]["unixDevs"]
					passwd = self.connectParams["PassWd"]["unixDevs"]

			if userid == "" or passwd == "":
				self.indiLOG.log(10,"Connection: {} login disabled, userid is empty".format(uType) )
			return userid, passwd
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return "",""



	####-----------------	 ---------
	def comsumeLogData(self):# , startTime):
		self.sleep(1)
		self.indiLOG.log(10,"comsumeLogData:  process starting")
		nextItem = ""
		lines	 = ""
		ipNumber = ""
		while True:
			try:
				if self.pluginState == "stop" or self.consumeDataThread["log"]["status"] == "stop": 
					self.indiLOG.log(30,"comsumeLogData: stopping process due to stop request")
					return  
				self.sleep(0.1)
				consumedTimeQueue = time.time()
				queueItemCount = 0
				while not self.logQueue.empty():
					if self.pluginState == "stop" or self.consumeDataThread["log"]["status"] == "stop": 
						self.indiLOG.log(30,"comsumeLogData:  stopping process due to stop request")
						return 
					queueItemCount += 1

					nextItem = self.logQueue.get()

					lines			= nextItem[0].split("\r\n")
					ipNumber		= nextItem[1]
					apN				= nextItem[2]
					try: 	apNint	= int(nextItem[2])
					except: apNint	= -1
					uType			= nextItem[3]
					xType			= nextItem[4]

					## update device-ap with new timestamp, it is up
					if self.decideMyLog("Log"): self.indiLOG.log(10,"MS-------  {:13s}#{}   {}  {} .. {}".format(ipNumber, apN, uType, xType, "{}".format(nextItem[0])[0:100]) )

					if self.debugThisDevices(uType, apNint):
						self.indiLOG.log(10,"DEVdebug   {} dev #:{:2d} uType:{}, xType{}, logmessage:\n{}".format(ipNumber, apNint, uType, xType, "\n".join(lines)) )

					### update lastup for unifi devices
					if xType in self.MAC2INDIGO:
						for MAC in self.MAC2INDIGO[xType]:
							if xType == "UN" and self.testIgnoreMAC(MAC, fromSystem="log"): continue
							if ipNumber == self.MAC2INDIGO[xType][MAC]["ipNumber"]:
								self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
								break

					consumedTime = time.time()

					if	 uType == "APtail":
						self.doAPmessages(lines, ipNumber, apN)
					elif uType == "GWtail":
						self.doGWmessages(lines, ipNumber, apN)
					elif uType == "SWtail":
						self.doSWmessages(lines, ipNumber, apN)
					elif uType == "VDtail":
						pass# self.doVDmessages()
					consumedTime -= time.time()
					if consumedTime < -self.maxConsumedTimeForWarning:	logLevel = 20
					else:												logLevel = 10
					if logLevel == 20:
						self.indiLOG.log(logLevel,"comsumeLogData        excessive time consumed:{:5.1f}[secs]; {:16}; len:{:},  lines:{:}".format(-consumedTime, ipNumber, len(lines), "{}".format(lines)[0:100]) )

					self.logQueue.task_done()

				#self.logQueue.task_done()
					if len(self.sendUpdateToFingscanList) > 0: self.sendUpdatetoFingscanNOW()
					if len(self.sendBroadCastEventsList)  > 0: self.sendBroadCastNOW()

				consumedTimeQueue -= time.time()
				if consumedTimeQueue < -self.maxConsumedTimeQueueForWarning:	logLevel = 20
				else:															logLevel = 10
				if logLevel == 20:
						self.indiLOG.log(logLevel,"comsumeLogData  Total excessive time consumed:{:5.1f}[secs]; {:16}; items:{:2} len:{:},  lines:{:}".format(-consumedTimeQueue, ipNumber, queueItemCount, len(lines), "{}".format(lines)[0:100]) )


			except	Exception as e:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		self.indiLOG.log(30,"comsumeLogData:  stopping process (3)")
		return 




	###########################################
	####------ camera PROTEC ---	-------START
	###########################################
	def getProtectIntoIndigo(self):
		try:
			if self.cameraSystem != "protect":										return
			if time.time() - self.lastRefreshProtect < self.refreshProtectCameras: 	return
			elapsedTime 	= time.time()
			systemInfoProtect = self.executeCMDOnController(dataSEND={}, pageString="api/bootstrap/", jsonAction="protect", cmdType="get", protect=True)
			if self.decideMyLog("Protect"): self.indiLOG.log(10,"getProtectIntoIndigo: *********   elapsed time (1):{:.1f}, len:{}, cameraInfo:{}".format(time.time() - elapsedTime, len(systemInfoProtect), "cameras" in systemInfoProtect ))

			if len(systemInfoProtect) == 0: 
				self.lastRefreshProtect  = time.time() - self.refreshProtectCameras +2
				return
			if "cameras" not in systemInfoProtect:
				self.lastRefreshProtect  = time.time() - self.refreshProtectCameras +2
				return


			devName = ""
			mapSensToLevel ={"":"", 0:"low", 1:"med", 2:"high"}
			lD = len(self.PROTECT)
			# clean up device listed in PROTECT, but not in indigo, only check at beginning and every 5 minutes
			if lD == 0 or time.time() - self.lastRefreshProtect > 300 or self.lastRefreshProtect ==0:
				devList = {}
				MAClist = {}
				for dev in indigo.devices.iter("props.isProtectCamera"):
					
					cameraId = dev.states.get("id","-1")
					if cameraId == "-1":
						self.indiLOG.log(30,"getProtectIntoIndigo: device :{} is not properly defined as camera, please delete and recreate  ".format(dev.name))
						continue

					if dev.states["MAC"] in MAClist:
						self.indiLOG.log(30,"getProtectIntoIndigo: duplicated MAC number:{} in indigo devices, please delete one : {}, currently ignoring: [{},{}]  ".format(dev.states["MAC"], MAClist[dev.states["MAC"]],  dev.id, dev.name ))
						continue

					MAClist[dev.states["MAC"]] = [dev.id, dev.name]
					if dev.states["id"] not in self.PROTECT:
						self.PROTECT[cameraId] = {"events":{}, "devId":dev.id, "devName":dev.name, "MAC":dev.states["MAC"], "lastUpdate":time.time()}

					devList[cameraId] = 1
					# clean up wrong status afetr strtup
					if lD == 0:
						if dev.states["status"] in ["event","motion","ring","person","vehicle"]:
							#self.indiLOG.log(30,"getProtectIntoIndigo: fixing status for:{}".format(dev.name ))
							self.addToStatesUpdateList(dev.id, "status", "CONNECTED")
							dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOn)
							self.executeUpdateStatesList()

				delList = {}
				for cameraId in self.PROTECT:
					if cameraId not in devList:
						delList[cameraId] = 1

				for cameraId in delList:
					del self.PROTECT[cameraId]
			
				if lD == 0:
					if self.decideMyLog("ProtDetails"): self.indiLOG.log(10,"getProtectIntoIndigo: starting with dev list: {}".format(self.PROTECT))


			for camera in systemInfoProtect["cameras"]:
				try:
					states = {}
					MAC 										= camera.get("mac","00:00:00:00:00:00")
					states["MAC"] 								= MAC[0:2]+":"+MAC[2:4]+":"+MAC[4:6]+":"+MAC[6:8]+":"+MAC[8:10]+":"+MAC[10:12]
					states["id"] 								= camera.get("id","0")
					states["name"] 								= camera.get("name")
					states["ip"]		 						= camera.get("host")
					states["status"] 							= camera.get("state")
					states["type"] 								= camera.get("type")
					states["firmwareVersion"] 					= camera.get("firmwareVersion")
					states["isAdopted"] 						= camera.get("isAdopted",False)
					states["isConnected"] 						= camera.get("isConnected",False)
					states["isManaged"] 						= camera.get("isManaged",False)
					states["isDark"] 							= camera.get("isDark",False)
					states["hasSpeaker"] 						= camera.get("hasSpeaker",False)
					states["modelKey"] 							= camera.get("modelKey")
					states["lcdMessage"] 						= camera["lcdMessage"].get("text")
					states["isSpeakerEnabled"] 					= camera["speakerSettings"].get("isEnabled",False)
					states["isExternalIrEnabled"] 				= camera["ispSettings"].get("isExternalIrEnabled",False)
					states["irLedMode"] 						= camera["ispSettings"].get("irLedMode")
					states["irLedLevel"] 						= camera["ispSettings"].get("irLedLevel")
					states["isLedEnabled"] 						= camera["ledSettings"].get("isEnabled")
					states["motionRecordingMode"] 				= camera["recordingSettings"].get("mode")
					states["motionMinEventTrigger"] 			= camera["recordingSettings"].get("minMotionEventTrigger")
					states["motionSuppressIlluminationSurge"] 	= camera["recordingSettings"].get("suppressIlluminationSurge")
					states["motionUseNewAlgorithm"] 			= camera["recordingSettings"].get("useNewMotionAlgorithm")
					states["motionAlgorithm"] 					= camera["recordingSettings"].get("motionAlgorithm","-")
					states["areSystemSoundsEnabled"] 			= camera["speakerSettings"].get("areSystemSoundsEnabled",False)
					states["speakerVolume"] 					= int(camera["speakerSettings"].get("volume",100))
					states["micVolume"] 						= int(camera.get("micVolume",100))
					states["icrSensitivity"] 					= mapSensToLevel[camera["ispSettings"].get("icrSensitivity")]
					states["motionEndEventDelay"] 				= float(camera["recordingSettings"].get("endMotionEventDelay"))/1000.
					states["motionPostPaddingSecs"] 			= float(camera["recordingSettings"].get( "postPaddingSecs"))
					states["motionPrePaddingSecs"] 				= float(camera["recordingSettings"].get( "prePaddingSecs"))
					# ret might be "None"
					try:	states["lastSeen"] 					= datetime.datetime.fromtimestamp(camera.get("lastSeen",0)/1000.,0).strftime("%Y-%m-%d %H:%M:%S")
					except:	states["lastSeen"] 					= ""
					try:	states["connectedSince"] 			= datetime.datetime.fromtimestamp(camera.get("connectedSince",0)/1000.).strftime("%Y-%m-%d %H:%M:%S")
					except:	states["connectedSince"] 			= ""
					try:	states["lastRing"] 					= datetime.datetime.fromtimestamp(camera.get("lastRing",0)/1000.).strftime("%Y-%m-%d %H:%M:%S")
					except:	states["lastRing"] 					= ""
					devId = -1
					dev = ""
					if states["id"] not in self.PROTECT:
						try:
							devName = "Camera_Protect_"+states["name"] +"_"+MAC 
							dev = indigo.device.create(
								protocol		=indigo.kProtocol.Plugin,
								address			= states["MAC"],
								name 			= devName,
								description		="",
								pluginId		=self.pluginId,
								deviceTypeId	="camera_protect",
								props			={"isProtectCamera":True, "eventThumbnailOn":True, "eventHeatmapOn":False, "thumbnailwh":"640/480", "heatmapwh":"320/240"
												, "SupportsOnState":True, "SupportsSensorValue":False , "SupportsStatusRequest":False, "AllowOnStateChange":False, "AllowSensorValueChange":False
												},
								folder			=self.folderNameIDCreated,
								)
							devId = dev.id
							if self.decideMyLog("ProtDetails"): self.indiLOG.log(10,"adding  {} to PROTEC list ip:{}".format( dev.name, states["ip"]))
							self.PROTECT[states["id"]] = {"events":{}, "devId":devId, "devName":dev.name, "MAC":states["MAC"] , "lastUpdate":time.time()}
						except	Exception as e:
							errtext = "{}".format(e)
							if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
							if "NameNotUniqueError" in errtext:
								self.indiLOG.log(20,"error with : {}  will try to update the camera id in indigo device and continue, if the error percist, please delete device, will be re-created".format( devName ))
								dev = indigo.devices[devName]
								devId = dev.id
								self.PROTECT[states["id"]]["devId"] = devId
							else:
								self.indiLOG.log(20,"unknown error- please restart plugin, dev : {} / {}   internal list:{}".format( devName , states["id"], self.PROTECT))
								continue

					else:
						devId = self.PROTECT[states["id"]]["devId"]
						dev = indigo.devices[devId]

					if devId ==-1:
						self.indiLOG.log(40,"dev not found ")
						continue

					self.PROTECT[states["id"]]["lastUpdate"] = time.time()

					if dev != "":
						for state in states:
							if self.decideMyLog("ProtDetails"): self.indiLOG.log(10,"checking dev {} state:{} := {}".format(dev.name, state, states[state]))
							if dev.states[state] != states[state]:
								self.addToStatesUpdateList(devId, state, states[state])

					else:
						try:
							dev = indigo.devices[devId]
							devId = dev.id
						except	Exception as e:
							if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
							if "{}".format(e).find("timeout waiting") == -1: 
								if states["id"] in self.PROTECT:
									self.indiLOG.log(30," due to error removing cameraId: {}  from internal list:{}".format(states["id"], self.PROTECT[states["id"]]))
									del self.PROTECT[states["id"]]
							continue


				except	Exception as e:
					if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

			# cleanup old devices not used
			if time.time() - self.lastRefreshProtect < 300:
				delList = {}
				for cameraId in self.PROTECT:
					delEvents = {}
					for eventID in self.PROTECT[cameraId]["events"]:
						if ( time.time() - self.PROTECT[cameraId]["events"][eventID]["eventStart"] > 100 and 
							  self.PROTECT[cameraId]["events"][eventID]["eventEnd"]  == 0 ): delEvents[eventID] = 1

					for eventID in delEvents:
						del self.PROTECT[cameraId]["events"][eventID]

					if self.PROTECT[cameraId]["lastUpdate"] > 24*3600: # we have received no update in > 24 hour 
						try: 	dev = indigo.devices[self.PROTECT[cameraId]["devId"]]
						except Exception as e:
							if "{}".format(e).find("timeout waiting") == -1: 
								delList[cameraId] =1

				for cameraId in delList:
					self.indiLOG.log(30,"removing cameraId: {} after > 24 hours w not activity and indigo dev does not exists either".format(cameraId))
					if cameraId in self.PROTECT: 
						self.indiLOG.log(30,"... internal list:{}".format(self.PROTECT[cameraId]))
						del self.PROTECT[cameraId]

			self.executeUpdateStatesList()
			self.lastRefreshProtect  = time.time()
			#self.indiLOG.log(10,"getProtectIntoIndigo: *********   elapsed time (2):{:.1f}".format(time.time() - elapsedTime))
	
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return



	####-----------------	 ---------
	####----- thread to get new events every x secs   ------
	####-----------------	 ---------
	def getProtectEvents(self):# , startTime):
		self.indiLOG.log(10,"getProtectEvents:  process starting")
		lastGetEvent = time.time()
		lastId = ""
		self.lastEvCheck = time.time()
		lastEvent = {}
		self.lastThumbnailTime = 0
		while True:
			try:
				refreshCameras = False

				if self.cameraSystem != "protect":
					self.indiLOG.log(30,"getProtectEvents: stopping process due to camera off")
					return  
				if self.pluginState == "stop" or self.protectThread["status"] == "stop": 
					self.indiLOG.log(30,"getProtectEvents: stopping process due to stop request")
					return  

				self.sleep(0.2)

				if self.PROTECT == {}: 										continue # no camera defined
				if time.time() - lastGetEvent < self.protecEventSleepTime: 	continue # now yet
				lastGetEvent	= time.time()

				# get new events from controller server
				endTime 		= int(time.time() * 1000)
				dataDict 		= {"end": str(endTime+20), "start": str( endTime - int(max(1,self.protecEventSleepTime)) *1000)}
				events = self.executeCMDOnController(dataSEND=dataDict, pageString="api/events/", jsonAction="protect", cmdType="get", protect=True)
				if False and self.decideMyLog("Protect"):  self.indiLOG.log(10,"getProtectEvents: *********   get events elapsed time (1):{:.2f}, len(events):{} ".format(time.time() - elapsedTime, len(events) ))
				

				# digest new events
				if not self.checkIfEmptyEventCleanup(events): 
					checkIds = self.loopThroughEventsAndFilterCameraEvents(events)
				else:
					checkIds = {}

				self.goThroughNewEventDataGetThumbNailsAndUpdateIndigoDevicesAndVariables(checkIds)

				self.executeUpdateStatesList()

				if False and self.decideMyLog("Protect"): self.indiLOG.log(10,"getProtectEvents: elapsed time (2):{:.1f}".format(time.time() - lastGetEvent))
					

			except	Exception as e:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
				self.sleep(10)
		self.indiLOG.log(30,"comsumeLogData:  stopping process (3)")
		return 

	####-----------------	 ---------
	####-----loop through new evenst and check if any new, changes  ------
	####-----------------	 ---------

	def loopThroughEventsAndFilterCameraEvents(self, events):
		try:
			checkIds = {}
			if events == []: return checkIds 
			for event in events:
				dev = ""
				# first check if everything is here 
				if "modelKey"				not in event: continue
				if event["modelKey"] != "event": 		  continue
				if "camera"				not in event: continue
				if "id"					not in event: continue
				if "start"					not in event: continue
				if "end"					not in event: continue
				if "thumbnail"				not in event: continue
				if "type"					not in event: continue
				if "smartDetectEvents"		not in event: continue
				if "smartDetectTypes"		not in event: continue
				# ignore old events  !
				if time.time() - event["start"]/1000. > 60: continue  # ignore old events 

				## we have a complete event 

				newId = event["id"]

				updateDev = False
				cameraId = event["camera"]
				if cameraId not in self.PROTECT:
					self.lastRefreshProtect = time.time() - self.refreshProtectCameras + 2 
					continue


				#### ignore repeat event info ### start
				if self.PROTECT[cameraId]["events"] != {}:
					if newId in self.PROTECT[cameraId]["events"]:
						double = True
						for xx in event:
							if xx not in self.PROTECT[cameraId]["events"][newId]["rawEvent"]:
								double = False
								break
							if  event[xx] != self.PROTECT[cameraId]["events"][newId]["rawEvent"][xx]:
								double = False
								break
						if not double:
							self.PROTECT[cameraId]["events"][newId]["rawEvent"] = copy.deepcopy(event)
					else:
						double = False

					if double: 
						if self.decideMyLog("Protect"):  
							#self.indiLOG.log(10,"getProtectEvents: camID:{}, evId:{}; skipping = repeat event".format(cameraId, newId) )
							pass
						continue

				#### ignore repeat event info ### END

				if self.decideMyLog("ProtEvents"):
					xxx = copy.deepcopy(event)
					del xxx["camera"]
					del xxx["id"]
					self.indiLOG.log(10,"getProtectEvents: camID:{}, evId:{}; event {}".format(cameraId, newId, xxx))

				smartDetect = ""

				## for the time being ignore list of smart detect events. this is a list of events to follow in the next event listings, we willl deal with them then
				if event["smartDetectEvents"] != []:
					if self.decideMyLog("ProtEvents"): self.indiLOG.log(10,"getProtectEvents: camID:{}, evId:{}; skipping type:{}; smart:{}".format(cameraId, newId, event["type"], event["smartDetectEvents"]))
					continue


				## new event?
				if newId not in self.PROTECT[cameraId]["events"]:
					self.PROTECT[cameraId]["events"][newId] =  {"eventStart":0, "eventEnd":0, "ringTime":0, "eventType":"", "thumbnailLastCopyTime": time.time() + 50, "thumbnailCopied": False, "status": "","rawEvent":copy.deepcopy(event)}
					if dev == "":
						dev = indigo.devices[self.PROTECT[cameraId]["devId"]]

					if self.decideMyLog("ProtEvents"): self.indiLOG.log(10,"getProtectEvents: camID:{}, evId:{}; {}: new event; type:{}".format(cameraId, newId, self.PROTECT[cameraId]["devName"], event["type"]))
					self.PROTECT[cameraId]["events"][newId]["eventStart"] 			= event["start"]/1000.
					self.PROTECT[cameraId]["events"][newId]["eventEnd"]    			= 0

					if self.copyProtectsnapshots == "on" or (self.copyProtectsnapshots == "selectedByDevice" and "eventThumbnailOn" in props and props["eventThumbnailOn"] ):
						self.PROTECT[cameraId]["events"][newId]["thumbnailLastCopyTime"] 	= time.time() + 15 # try to get thumbnail in the next 15 secs
					else:
						self.PROTECT[cameraId]["events"][newId]["thumbnailLastCopyTime"] 	= time.time()      # no thumbnails to be copied

					self.PROTECT[cameraId]["events"][newId]["eventType"]				= event["type"]

					if event["type"] == "ring": 
						self.PROTECT[cameraId]["events"][newId]["ringTime"] 			= event["start"]/1000.

					updateDev = True
					indigo.variable.updateValue("Unifi_Camera_with_Event", self.PROTECT[cameraId]["devName"])
					indigo.variable.updateValue("Unifi_Camera_Event_Date", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
					checkIds[newId] = cameraId
				

				if event["smartDetectEvents"] !=[]:
					for evID in event["smartDetectEvents"]:
						if evID in self.PROTECT[cameraId]["events"]:
							checkIds[evID] = cameraId
							self.PROTECT[cameraId]["events"][evID]["eventEnd"] = time.time()
					if self.PROTECT[cameraId]["events"][newId]["eventEnd"] != 0:  self.PROTECT[cameraId]["events"][newId]["eventEnd"] = time.time()
					checkIds[newId] = cameraId

				# event ended, can be the same event as the start event ie rings?
				if self.PROTECT[cameraId]["events"][newId]["eventEnd"] < self.PROTECT[cameraId]["events"][newId]["eventStart"] and event["end"] is not None:
					if self.decideMyLog("ProtEvents"): self.indiLOG.log(10,"getProtectEvents: camID:{}, evId:{}; event ended devid:{}".format(cameraId, newId, self.PROTECT[cameraId]["devId"]))
					self.PROTECT[cameraId]["events"][newId]["eventEnd"] = event["end"]/1000.
					checkIds[newId] = cameraId

				# other vent types?
				if event["type"] == "disconnected":
					self.PROTECT[cameraId]["events"][newId]["eventStart"]  = event["start"]/1000.
					self.PROTECT[cameraId]["events"][newId]["eventEnd"]    = event["start"]/1000.+1
					checkIds[newId] = cameraId

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return checkIds


	####-----------------	 ---------
	####-----called to check if old events need to be expired / deleted ------
	####-----------------	 ---------
	def checkIfEmptyEventCleanup(self, events):
		try:
			if events != []: return False
			if time.time() - self.lastEvCheck < 10: return True
			self.lastEvCheck = time.time()

			# close old not updated status
			for cameraId in self.PROTECT:
				rmEvent ={}
				if self.PROTECT[cameraId]["devId"] < 1: continue

				for evId in self.PROTECT[cameraId]["events"]:
					testEV = self.PROTECT[cameraId]["events"][evId]
					if testEV["eventStart"]  == 0: 				continue
					if time.time() - testEV["eventStart"] < 40: 	continue # look only at older events 
					if testEV["eventType"]  == "ring" and self.PROTECT[cameraId]["events"][evId]["status"] == "ring":
						dev = indigo.devices[self.PROTECT[cameraId]["devId"]]
						if dev.states["status"] == "ring":
							if self.decideMyLog("ProtEvents"): self.indiLOG.log(10,"getProtectEvents: setting status to CONNECTED for expired ring event {}".format(self.PROTECT[cameraId]["devName"], testEV["thumbnailCopied"]) )
							dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOn)
							self.addToStatesUpdateList(dev.id, "status", "CONNECTED")
							rmEvent[evId] = 1

					elif testEV["eventEnd"] == 0:
						dev = indigo.devices[self.PROTECT[cameraId]["devId"]]
						if dev.states["status"] == testEV["status"]:
							dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOn)
							if self.decideMyLog("ProtDeProtEventstails"): self.indiLOG.log(10,"getProtectEvents: setting status to CONNECTED for expired not ended event {}, Thumbnailcopied:{}".format(self.PROTECT[cameraId]["devName"], testEV["thumbnailCopied"]) )
							self.addToStatesUpdateList(dev.id, "status", "CONNECTED")
							rmEvent[evId] = 1

					if time.time() - testEV["eventStart"]  > 60: # remove rest of events from list after 1 minutes
						if self.decideMyLog("ProtEvents"): self.indiLOG.log(10,"getProtectEvents: removing old {}- event:{}, Thumbnailcopied:{}".format(self.PROTECT[cameraId]["devName"], evId, testEV["thumbnailCopied"]) )
						rmEvent[evId] = 1

				for evId in rmEvent:
					del self.PROTECT[cameraId]["events"][evId]
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return True


	####-----------------	 ---------
	####-----get thumbnails and update dev states ------
	####-----------------	 ---------
	def goThroughNewEventDataGetThumbNailsAndUpdateIndigoDevicesAndVariables(self, checkIds):
		try:
			if time.time() - self.lastThumbnailTime < 2 and checkIds == {}: return
			self.lastThumbnailTime = time.time() 
			debug = True
			# have to wait until end of event to get the thumbnail
			for cameraId in self.PROTECT:
				for evID in self.PROTECT[cameraId]["events"]:
					#if self.decideMyLog("ProtEvents"): self.indiLOG.log(10,"getProtectEvents: camID:{}, evId:{}; evids check :{} eventEnd:{}; copied:{}".format(cameraId, newId, evID, self.PROTECT[cameraId]["events"][evID]["eventEnd"], self.PROTECT[cameraId]["events"][evID]["thumbnailLastCopyTime"]))
					if self.PROTECT[cameraId]["events"][evID]["eventEnd"] >0 or time.time() - self.PROTECT[cameraId]["events"][evID]["eventStart"] > 1.5:
						if time.time() - self.PROTECT[cameraId]["events"][evID]["thumbnailLastCopyTime"] < 0:
							checkIds[evID] = cameraId

			if self.decideMyLog("Protect"): self.indiLOG.log(10,"getProtectEvents: check :{}".format(checkIds))
			for evID in checkIds:
				cameraId 	= checkIds[evID]
				protectEV 	= self.PROTECT[cameraId]["events"][evID]
				smartDetect	= ""
				dev 		= ""
				eventJpeg	= ""
				status		= protectEV["eventType"]
				if protectEV["rawEvent"]["smartDetectTypes"] != []:
					smartDetect = ",".join(protectEV["rawEvent"]["smartDetectTypes"]).strip(",")
					if self.decideMyLog("ProtEvents"):  self.indiLOG.log(10,"getProtectEvents: camID:{}, evId:{}; smartDetect-{} --> {}".format(cameraId, evID, protectEV["rawEvent"]["smartDetectTypes"], smartDetect) )
					status = smartDetect

				if not protectEV["thumbnailCopied"] and ( time.time()-protectEV["thumbnailLastCopyTime"] < 0 and  protectEV["rawEvent"]["thumbnail"] is not None and (time.time() - protectEV["eventStart"] > 5 or protectEV["eventEnd"] >0)):

					###  copy thumbnail to local indigo disk -----
					if self.PROTECT[cameraId]["devId"] > 0:
						dev = indigo.devices[self.PROTECT[cameraId]["devId"]]
						props = dev.pluginProps
						eventJpeg 		= self.changedImagePath.rstrip("/")+"/"+dev.name+"_"+status+"_thumbnail.jpeg"
						snapshotJpeg 	= self.changedImagePath.rstrip("/")+"/"+dev.name+"_"+status+"_snapshot.jpeg"
						wh = props.get("thumbnailwh")
						theDict = {"cameraDeviceSelected":dev.id}
						theDict["whofImage"] = wh
						theDict["fileNameOfImage"]  = snapshotJpeg
						wh = wh.split("/")
						params = {"accessKey": "", "h": wh[1], "w": wh[0]}


						if "eventThumbnailOn" in props and props["eventThumbnailOn"] and "thumbnailwh" in props:
							#self.lastUnifiCookieRequests = 0
							evNumber = protectEV["rawEvent"]["thumbnail"]
							#evNumber = "e-643ec0bc01cd8f03e4000d54"
							if self.decideMyLog("ProtEvents"):  self.indiLOG.log(10,"getProtectEvents: waiting for 5=5 secs for ev#:{}".format(evNumber))


							#as thumbnail might take some time, do a snapshot first
							self.buttonSendCommandToProtectgetSnapshotCALLBACK(theDict)
							indigo.variable.updateValue("Unifi_Camera_Event_PathToThumbnail", snapshotJpeg)
							indigo.variable.updateValue("Unifi_Camera_Event_DateOfThumbNail", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
							dev.updateStateOnServer("eventJpeg",snapshotJpeg)

							# added wait for thumbnail data to be ready, might be  .. 10 secs , if first read not successful, wait 3 secs before next read, then retry every 1 secs
							data = ""
							for ii in range(20):
								if len(data) < 100: 
									if  self.decideMyLog("ProtEvents"): 
										deb1 = self.pluginPrefs["debugConnectionCMD"]; self.pluginPrefs["debugConnectionCMD"] = True
										deb2 = self.pluginPrefs["debugConnectionRET"]; self.pluginPrefs["debugConnectionRET"] = True
										self.setDebugFromPrefs(self.pluginPrefs, writeToLog=False)
									data = self.executeCMDOnController(dataSEND=params, pageString="api/thumbnails/{}".format(evNumber), jsonAction="protect", cmdType="get", protect=True, raw=True, ignore40x=True)
									if  self.decideMyLog("ProtEvents"): 
										self.pluginPrefs["debugConnectionCMD"] = deb1
										self.pluginPrefs["debugConnectionRET"] = deb2
										self.setDebugFromPrefs(self.pluginPrefs, writeToLog=False)
									if len(data) > 100: break
									if ii < 1: self.sleep(5) # if not successsfull imedeately, wait 5 secs
									self.sleep(1)


							if  self.decideMyLog("ProtEvents"): self.indiLOG.log(10,"getProtectEvents: camID:{}, evId:{}; getting thumbnail, datalen:{}; thumbnail: {}; devId:{}".format(cameraId, evID, len(data),  protectEV["rawEvent"]["thumbnail"], self.PROTECT[cameraId]["devId"]))
							if len(data) > 0:
								f = self.openEncoding(eventJpeg,"wb")
								f.write(data)
								f.close()
								protectEV["thumbnailLastCopyTime"] = time.time()
								protectEV["thumbnailCopied"] = True
								indigo.variable.updateValue("Unifi_Camera_Event_PathToThumbnail", eventJpeg)
								indigo.variable.updateValue("Unifi_Camera_Event_DateOfThumbNail", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") )
								dev.updateStateOnServer("eventJpeg",eventJpeg)

								## only do heatmaps when thumbnail is enabled too
								if "eventHeatmapOn" in props and props["eventHeatmapOn"]:
									wh = props["heatmapwh"].split("/")
									params = {"accessKey": "", "h": wh[1], "w": wh[0],}
									data = self.executeCMDOnController(dataSEND=params, pageString="api/heatmaps/{}".format(protectEV["rawEvent"]["heatmap"]), jsonAction="protect", cmdType="get", protect=True, raw=True, ignore40x=True)
									if len(data) > 0:
										f = self.openEncoding(self.changedImagePath.rstrip("/")+"/"+dev.name+"_"+status+"_heatmap.jpeg","wb")
										f.write(data)
										f.close()



							if protectEV["eventEnd"] == 0:  protectEV["eventEnd"] = time.time()



				status = protectEV["eventType"]
				if smartDetect != "":
					status = smartDetect

				if True:
					try:
						if dev == "":
							dev = indigo.devices[self.PROTECT[cameraId]["devId"]]

						if protectEV["eventStart"] != 0: 
							evStart = datetime.datetime.fromtimestamp(protectEV["eventStart"]).strftime("%Y-%m-%d %H:%M:%S")
							if dev.states["eventStart"] != evStart:
								dev.updateStateImageOnServer(indigo.kStateImageSel.SensorTripped)
								self.addToStatesUpdateList(dev.id,"eventStart", evStart)
								protectEV["status"] = status
								rgStart = datetime.datetime.fromtimestamp(protectEV["ringTime"]).strftime("%Y-%m-%d %H:%M:%S")
								if protectEV["ringTime"] != 0 and  rgStart != dev.states["lastRing"]:
									self.addToStatesUpdateList(dev.id,"lastRing", rgStart)
									if self.decideMyLog("ProtEvents"): self.indiLOG.log(10,"getProtectEvents: camID:{}, evId:{}; setting status to ring, ".format(cameraId, evID))

								if status != dev.states["status"]: self.addToStatesUpdateList(dev.id, "status", status)
								protectEV["status"] = status

								try: evN = int(dev.states["eventNumber"])
								except: evN = 0
								self.addToStatesUpdateList(dev.id,"eventNumber", evN+1 )

					
						if protectEV["eventEnd"] != 0 and status != "ring": 
							evEnd = datetime.datetime.fromtimestamp(protectEV["eventEnd"]).strftime("%Y-%m-%d %H:%M:%S")
							if dev.states["eventEnd"] != evEnd:
								if self.decideMyLog("ProtEvents"): self.indiLOG.log(10,"getProtectEvents: camID:{}, evId:{}; setting status to CONNECT, ".format(cameraId, evID))
								self.addToStatesUpdateList(dev.id, "eventEnd", evEnd)
								dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOn)
								self.addToStatesUpdateList(dev.id, "status", "CONNECTED")
								protectEV["status"] = "CONNECTED"

						dt = int(max(-1,protectEV["eventEnd"] - protectEV["eventStart"]))
						if dev.states["eventLength"] != dt:
							self.addToStatesUpdateList(dev.id, "eventLength", dt )

						if eventJpeg != "" and eventJpeg != dev.states["eventJpeg"]:
							self.addToStatesUpdateList(dev.id, "eventJpeg", eventJpeg )

						if protectEV["eventType"]  not in ["", dev.states["eventType"]]:
							self.addToStatesUpdateList(dev.id, "eventType", protectEV["eventType"] )

						if smartDetect != dev.states["smartDetect"]:
							self.addToStatesUpdateList(dev.id, "smartDetect", smartDetect )

					except	Exception as e:
						if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return 


	####-----------------	 ---------
	####-----send commd parameters to cameras through protect ------
	####-----------------	 ---------
	def buttonSendCommandToProtectLcdMessageCALLBACKaction (self, action1=None):
		return self.buttonSendCommandToProtectLcdMessageCALLBACK(valuesDict= action1.props)
	def buttonSendCommandToProtectLcdMessageCALLBACK(self, valuesDict=None, typeId="", devId="",returnCmd=False):
		try:
			area = "lcdMessage"
			valuesDict["MSG"] =  ""
			payload ={area:{}}
			if valuesDict["lcdMessage"]			!= "do not change": payload[area]["text"] 		= valuesDict["lcdMessage"]
			data = self.setupProtectcmd( valuesDict["cameraDeviceSelected"], payload)
			ok = True
			if area not in data: ok = False
			else:
				for xx in data[area]:
					if data[area][xx] != payload[area][xx]: 
						ok = False
						break

			valuesDict["MSG"] =  "ok"  if ok else  "error"
			if self.decideMyLog("ProtDetails"): self.indiLOG.log(10,"setupProtectcmd returned data: {} ".format(data[area]))
			self.addToMenuXML(valuesDict)
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return valuesDict


	####-----------------	 ---------
	def buttonSendCommandToProtectLEDCALLBACKaction (self, action1=None):
		return self.buttonSendCommandToProtectLEDCALLBACK(valuesDict= action1.props)
	def buttonSendCommandToProtectLEDCALLBACK(self, valuesDict=None, typeId="", devId="",returnCmd=False):
		try:
			valuesDict["MSG"] =  ""
			area = "ledSettings"
			payload ={area:{}}
			if valuesDict["blinkRate"]			!= "-1": payload[area]["blinkRate"] 		= int(valuesDict["blinkRate"])
			if valuesDict["camLEDenabled"]		!= "-1": payload[area]["isEnabled"] 		= valuesDict["camLEDenabled"] == "1"
			data = self.setupProtectcmd( valuesDict["cameraDeviceSelected"], payload)
			ok = True
			if area not in data: ok = False
			else:
				for xx in data[area]:
					if data[area][xx] != payload[area][xx]: 
						ok = False
						break

			valuesDict["MSG"] =  "ok"  if ok else  "error"
			if self.decideMyLog("ProtDetails"): self.indiLOG.log(10,"setupProtectcmd returned data: {} ".format(data[area]))
			self.addToMenuXML(valuesDict)
		except	Exception as e:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return valuesDict


	####-----------------	 ---------
	def buttonSendCommandToProtectenableSpeakerCALLBACKaction (self, action1=None):
		return self.buttonSendCommandToProtectenableSpeakerCALLBACK(valuesDict= action1.props)
	def buttonSendCommandToProtectenableSpeakerCALLBACK(self, valuesDict=None, typeId="", devId="",returnCmd=False):
		self.addToMenuXML(valuesDict)
		try:
			"""
			"speakerSettings": {
				"areSystemSoundsEnabled": true, 
				"isEnabled": true, 
				"volume": 100
			}
			"""
			area = "speakerSettings"
			payload ={area:{}}
			if valuesDict["areSystemSoundsEnabled"]	!= "-1": payload[area]["areSystemSoundsEnabled"] 	= valuesDict["areSystemSoundsEnabled"] == "1"
			if valuesDict["isEnabled"] 				!= "-1": payload[area]["isEnabled"] 				= valuesDict["isEnabled"] == "1"
			if valuesDict["volume"] 					!= "-1": payload[area]["volume"] 					= int(valuesDict["volume"])
			data = self.setupProtectcmd( valuesDict["cameraDeviceSelected"], payload)
			ok = True
			if area not in data: ok = False
			else:
				for xx in payload[area]:
					if data[area][xx] != payload[area][xx]: 
						ok = False
						break

			valuesDict["MSG"] =  "ok"  if ok else  "error"
			if self.decideMyLog("ProtDetails"): self.indiLOG.log(10,"setupProtectcmd returned data: {} ".format(data[area]))
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return valuesDict

	####-----------------	 ---------
	def buttonSendCommandToProtectmicVolumeCALLBACKaction (self, action1=None):
		return self.buttonSendCommandToProtectmicVolumeCALLBACK(valuesDict= action1.props)
	def buttonSendCommandToProtectmicVolumeCALLBACK(self, valuesDict=None, typeId="", devId="",returnCmd=False):
		try:
			valuesDict["MSG"] =  ""
			self.addToMenuXML(valuesDict)
			if valuesDict["micVolume"] == "-1":	return valuesDict
			area = "micVolume"
			payload ={area:int(valuesDict[area])}
			data = self.setupProtectcmd(valuesDict["cameraDeviceSelected"],payload )
			ok = True
			if area not in data: ok = False
			if self.decideMyLog("ProtDetails"): self.indiLOG.log(10,"setupProtectcmd returned data: {} ".format(data[area]))
			valuesDict["MSG"] =  "ok"  if ok else  "error"
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return valuesDict

	####-----------------	 ---------
	def buttonSendCommandToProtectRecordCALLBACKaction (self, action1=None):
		return self.buttonSendCommandToProtectRecordCALLBACK(valuesDict= action1.props)

	def buttonSendCommandToProtectRecordCALLBACK(self, valuesDict=None, typeId="", devId="",returnCmd=False):
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
			 {'suppressIlluminationSurge': False, 'postPaddingSecs': 10, 'geofencing': 'off', 'motionAlgorithm': 'stable', 'prePaddingSecs': 1, 'enablePirTimelapse': False, 'minMotionEventTrigger': 0, 'mode': 'motion', 'useNewMotionAlgorithm': False, 'endMotionEventDelay': 3000} 
			"""
			area = "recordingSettings"
			payload ={area:{}}
			if valuesDict["prePaddingSecs"] 				!= "-1":	payload[area]["prePaddingSecs"] 			= int(valuesDict["prePaddingSecs"])
			if valuesDict["postPaddingSecs"] 				!= "-1":	payload[area]["postPaddingSecs"] 			= int(valuesDict["postPaddingSecs"])
			if valuesDict["minMotionEventTrigger"] 			!= "-1":	payload[area]["minMotionEventTrigger"] 		= int(valuesDict["minMotionEventTrigger"])
			if valuesDict["motionRecordEnabledProtect"] 	!= "-1":	payload[area]["mode"] 						= valuesDict["motionRecordEnabledProtect"]
			if valuesDict["suppressIlluminationSurge"] 		!= "-1":	payload[area]["suppressIlluminationSurge"]	= valuesDict["suppressIlluminationSurge"]
			if valuesDict["useNewMotionAlgorithm"] 			!= "-1":	payload[area]["useNewMotionAlgorithm"] 		= valuesDict["useNewMotionAlgorithm"]
			if valuesDict["motionAlgorithm"] 				!= "-1":	payload[area]["motionAlgorithm"] 			= valuesDict["motionAlgorithm"]
			if valuesDict["endMotionEventDelay"] 			!= "-1":	payload[area]["endMotionEventDelay"] 		= valuesDict["endMotionEventDelay"]
			data = self.setupProtectcmd( valuesDict["cameraDeviceSelected"], payload)
			ok = True
			if area not in data: ok = False
			else:
				for xx in payload[area]:
					if data[area][xx] != payload[area][xx]: 
						ok = False
						break

			valuesDict["MSG"] =  "ok"  if ok else  "error"
			if self.decideMyLog("ProtDetails"): self.indiLOG.log(10,"setupProtectcmd returned data: {} ".format(data[area]))

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		self.addToMenuXML(valuesDict)
		return valuesDict

	####-----------------	 ---------
	def buttonSendCommandToProtectIRCALLBACKaction (self, action1=None):
		return self.buttonSendCommandToProtectIRCALLBACK(valuesDict= action1.props)
	def buttonSendCommandToProtectIRCALLBACK(self, valuesDict=None, typeId="", devId="",returnCmd=False):
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


	09 11:37:20 setupProtectcmd  {'ispSettings': {'icrSensitivity': 1, 'irLedMode': 'autoFilterOnly', 'irLedLevel': 100}} , devid:1965914261, name:Camera_Protect_Reserve-UVC G3  Flex_7483C23FD3E5; id:603fe05602f2a503e70003f4
	09 11:37:20 setupProtectcmd returned data: {'icrSensitivity': 1, 'sharpness': 50, 'isPauseMotionEnabled': False, 'isLdcEnabled': True, 'zoomPosition': 0, 'touchFocusX': 0, 'touchFocusY': 0, 'isAggressiveAntiFlickerEnabled': False, 'is3dnrEnabled': True, 'isExternalIrEnabled': False, 'denoise': 50, 'dZoomStreamId': 4, 'irLedLevel': 100, 'aeMode': 'auto', 'contrast': 50, 'dZoomScale': 0, 'hue': 50, 'saturation': 50, 'isFlippedHorizontal': False, 'focusPosition': 0, 'isAutoRotateEnabled': True, 'irLedMode': 'autoFilterOnly', 'focusMode': 'ztrig', 'isFlippedVertical': False, 'brightness': 50, 'wdr': 1, 'dZoomCenterX': 50, 'dZoomCenterY': 50} 
			"""

			area = "ispSettings"
			payload ={area:{}}
			if valuesDict["irLedMode"] 			!= "-1":	payload[area]["irLedMode"] 			= valuesDict["irLedMode"]
			if valuesDict["icrSensitivity"] 	!= "-1":	payload[area]["icrSensitivity"] 	= int(valuesDict["icrSensitivity"])
			if valuesDict["irLedLevel"] 		!= "-1":	payload[area]["irLedLevel"] 		= int(valuesDict["irLedLevel"])
			data = self.setupProtectcmd( valuesDict["cameraDeviceSelected"], payload)
			ok = True
			if area not in data: ok = False
			else:
				for xx in payload[area]:
					if data[area][xx] != payload[area][xx]: 
						ok = False
						break

			valuesDict["MSG"] =  "ok"  if ok else  "error"
			if self.decideMyLog("ProtDetails"): self.indiLOG.log(10,"setupProtectcmd returned data: {} ".format(data[area]))

			self.addToMenuXML(valuesDict)
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return valuesDict

####-----------------	 ---------
	def buttonrefreshProtectCameraSystemCALLBACK(self, valuesDict=None, typeId="", devId="",returnCmd=False):
		self.addToMenuXML(valuesDict)
		self.refreshProtectCameras = 0
		if self.decideMyLog("Protect"): self.indiLOG.log(10,"get protect camera setup initiated ")
		valuesDict["MSG"] =  "request Send" 
		return valuesDict

	####-----------------	 ---------
	def buttonSendCommandToProtectgetSnapshotCALLBACKaction (self, action1=None):
		return self.buttonSendCommandToProtectgetSnapshotCALLBACK(valuesDict= action1.props)
	def buttonSendCommandToProtectgetSnapshotCALLBACK(self, valuesDict=None, typeId="", devId="",returnCmd=False):
		try:
			camId = valuesDict["cameraDeviceSelected"]
			wh = valuesDict["whofImage"].split("/")
			fName = valuesDict["fileNameOfImage"] 
			dev = indigo.devices[int(camId)]
			if self.decideMyLog("Protect"): self.indiLOG.log(10,"getSnapshot  dev {};  vd:{} ".format(dev.name, valuesDict))
			valuesDict["MSG"] = "error"
			params = {
					"accessKey": "",
					"h": wh[1],
					"ts": str(int(time.time())*1000),
					"force": "true",
					"w": wh[0],
			}
			if  self.decideMyLog("ProtEvents"): 
				deb1 = self.pluginPrefs["debugConnectionCMD"]; self.pluginPrefs["debugConnectionCMD"] = True
				deb2 = self.pluginPrefs["debugConnectionRET"]; self.pluginPrefs["debugConnectionRET"] = True
				self.setDebugFromPrefs(self.pluginPrefs, writeToLog=False)

			data = self.executeCMDOnController(dataSEND=params, pageString="api/cameras/{}/snapshot".format(dev.states["id"]), jsonAction="protect", protect=True, cmdType="get", raw=True)

			if  self.decideMyLog("ProtEvents"): 
				self.pluginPrefs["debugConnectionCMD"] = deb1
				self.pluginPrefs["debugConnectionRET"] = deb2
				self.setDebugFromPrefs(self.pluginPrefs, writeToLog=False)

			self.addToMenuXML(valuesDict)

			if len(data) < 10:
				valuesDict["MSG"] = "no data returned"
				self.indiLOG.log(10,"getSnapshot  no data returned data length {} ".format(len(data)))
				return valuesDict

			f = open(fName,"wb")
			f.write(data)
			f.close()
			if self.decideMyLog("Protect"): self.indiLOG.log(10,"getSnapshot  writing data to {};  length {} ".format(fName, len(data)))
			valuesDict["MSG"] = "shapshot done"
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return valuesDict


	####-----------------	 ---------
	def setupProtectcmd(self, devId, payload, cmdType="patch"):

		dev = indigo.devices[int(devId)]
		try:
			if self.cameraSystem != "protect":				return "error protect not enabled"
			if self.decideMyLog("Protect"): self.indiLOG.log(10,"setupProtectcmd  {} , devid:{}, name:{}; id:{}".format(payload, dev.id, dev.name, dev.states["id"]))
					
			data = self.executeCMDOnController(dataSEND=payload, pageString="cameras/{}".format(dev.states["id"]), jsonAction="protect", protect=True, cmdType=cmdType)
			self.lastRefreshProtect = time.time() - self.refreshProtectCameras +1
			return data
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)



	####-----------------  print	  ---------
	def buttonConfirmPrintProtectDeviceInfoCALLBACK(self, valuesDict=None, typeId=""):
		try:
			valuesDict["MSG"] = ""
			self.lastRefreshProtect = 0
			self.getProtectIntoIndigo()
			#                1         2         3         4         5         6         7         8         9         10        11        12        13        14        15        16
			#       1234567891123456789212345678931234567894123456789512345678961234567897123456789812345678991234567890123456789012345678901234567890123456789012345678901234567890
			out  ="Protect Camera devices      START =============================================================================================================================  \n"
			out +="                                                                                   ThumbNail     HeatMap       Device        Events-----------------------------------     is   Volume- ir-LED----------------- stat  \n"
			out +="DevName---------------------- MAC#------------- ip#----------- DevType--- FWV----- On-resolutn   On-resolutn   lastSeen----- last-motion-- lastRing----- ---#of Mode       dark mic spk En  Sens Mode       Lvl LED  \n"
			mapTFtoenDis 	= {"":"?", True:"ena", False:"dis"}
			mapTFtoNight 	= {"":"?", True:"Nite", False:"Day"}
			mapirMode 		= {"":"?", "auto":"auto", "on":"on", "off":"off", "autoFilterOnly":"a-Filt-Onl"}
			for dev in indigo.devices.iter("props.isProtectCamera"):
				props = dev.pluginProps
				cameraId = dev.states["id"] 
				out+= "{:30s}".format(dev.name[:30])
				out+= "{:18s}".format(dev.states["MAC"])
				out+= "{:15s}".format(dev.states["ip"])
				out+= "{:11s}".format(dev.states["type"][4:])
				out+= "{:9s}".format(dev.states["firmwareVersion"])
				out+= "{:3s}".format(mapTFtoenDis[props["eventThumbnailOn"]])
				out+= "-{:10s}".format(props["thumbnailwh"])
				out+= "{:3s}".format(mapTFtoenDis[props["eventHeatmapOn"]])
				out+= "-{:10s}".format(props["heatmapwh"])
				out+= "{:14s}".format(dev.states["lastSeen"][6:])
				out+= "{:14s}".format(dev.states["eventStart"][6:])
				out+= "{:13s}".format(dev.states["lastRing"][6:])
				out+= "{:7d} ".format(dev.states["eventNumber"])
				out+= "{:11s}".format(dev.states["motionRecordingMode"])
				out+= "{:4s}".format(mapTFtoNight[dev.states["isDark"]])
				out+= "{:4d}".format(dev.states["micVolume"])
				out+= "{:4d}".format(dev.states["speakerVolume"])
				out+= " {:4s}".format(mapTFtoenDis[dev.states["isExternalIrEnabled"]])
				out+= "{:5}".format(dev.states["icrSensitivity"])
				out+= "{:11s}".format(mapirMode[dev.states["irLedMode"]])
				out+= "{:3d}".format(dev.states["irLedLevel"])
				out+= " {:3}".format(mapTFtoenDis[dev.states["isLedEnabled"]])
				out +="  \n"
			out +="                                                                     =============================================================================================================================  \n"  
			out +="  \n"
			out+= "================= INSTALL HELP =====================================  \n"
			out+= "To setup: select the querry every time parametes etc  \n"
			out+= "Currently the protect system must be on the same hardware as the controller eg cloudkey 2, UMDpro.    \n"
			out+= "Once started the plugin will query(http) protect and will get all cameras installed and create the appropritate indigo devices    \n"
			out+= "It then will query(http) the protect system for new events every x secs  \n"
			out+= "The events can be of type Motion/Person/Vehicle/Ring. One physical ring can create several events  \n"
			out+= "eg motion+person+ring in differnt sequences depending on how a person approaches the doorbell  \n"
			out+= "Then for each event the variables  \n"
			out+= "- Unifi_Camera_with_Event  \n"
			out+= "- Unifi_Camera_Event_PathToThumbnail  \n"
			out+= "- Unifi_Camera_Event_DateOfThumbNail  \n"
			out+= "- Unifi_Camera_Event_Date  \n"
			out+= "are updated as they come in. The event date is the first variable to be updated, some of the other images can take several seconds to be produced.  \n"
			out+= "You can trigger on any of these variables or on the device states: lastRing or eventStart. eventEnd is set when the event is over. In most cases the thumbnail should be ready.  \n"
			out+= "  \n"
			out+= "In menu / CAMERA - protect Info ...  \n"
			out+= "you can print camera info to the logfile and  get a snap shot and set several parameters on the caameras  \n"
			out+= "in actions you can setup most of the config as as well as get snapshots  \n"
			out +="  \n"
			out +="   uniFiAP                         Protect Camera devices      END   =============================================================================================================================  \n"  

			self.indiLOG.log(20,out)
			valuesDict["MSG"] = "printed"
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return valuesDict

	###########################################
	####------ camera PROTEC ---	-------END
	###########################################


	####-----------------	 ---------
	def doVDmessages(self, lines, ipNumber,apN ):

		self.setBlockAccess("doVDmessages")

		dateUTC = datetime.datetime.utcnow().strftime("%Y%m%d")
		uType = "VDtail"

		try:
			for line in lines:
				if len(line) < 10: continue
				## this is an event tring:
				# logversion 1:
				###1524837857.747 2018-04-27 09:04:17.747/CDT: INFO   Camera[F09FC2C1967B] type:start event:105 clock:58199223 (UVC G3 Micro) in ApplicationEvtBus-15
				###1524837862.647 2018-04-27 09:04:22.647/CDT: INFO   Camera[F09FC2C1967B] type:stop event:105 clock:58204145 (UVC G3 Micro) in ApplicationEvtBus-18
				## new format logVersion 2:
				#1561518324.741 2019-06-25 22:05:24.741/CDT: INFO   [uv.analytics.motion] [AnalyticsService] [FCECDA1F1532|LivingRoom-Window-Flex] MotionEvent type:start event:1049 clock:111842854 in AnalyticsEvtBus-0

				itemsRaw = (line.strip()).split(" INFO ")
				if len(itemsRaw) < 2:
					continue


				try: timeSt= float(itemsRaw[0].split()[0])
				except:
					if self.decideMyLog("Video"):  self.indiLOG.log(10,"MS-VD----  bad float")
					continue

				items= itemsRaw[1].strip().split()
				if len(items) < 5:
					self.indiLOG.log(10,"MS-VD----  less than 5 items, line: "+line)
					continue

				logVersion = 0
				if items[0].find("Camera[") >-1: 			logVersion = 1
				elif itemsRaw[1].find("MotionEvent") >-1:	logVersion = 2
				else:
					if self.decideMyLog("Video"): self.indiLOG.log(10,"MS-VD----  no Camera, line: {}".format(line) )
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
					if self.decideMyLog("Video"): self.indiLOG.log(10,"MS-VD----  bad data, line: {}".format(line) )
					continue

				MAC = c[0:2]+":"+c[2:4]+":"+c[4:6]+":"+c[6:8]+":"+c[8:10]+":"+c[10:12]

				if self.testIgnoreMAC(MAC, fromSystem="doVDmsg"): continue

				evType = itemsRaw[1].split("type:")
				if len(evType) !=2: 
					if self.decideMyLog("Video"): self.indiLOG.log(10,"MS-VD----   no    type, line: {}".format(line) )
					continue
				evType = evType[1].split()[0]

				if evType not in ["start","stop"]:
					if self.decideMyLog("Video"): self.indiLOG.log(10,"MS-VD----  bad eventType {}".format(evType) )
					continue


				event = itemsRaw[1].split("event:")
				if len(event) !=2: 
					if self.decideMyLog("Video"): self.indiLOG.log(10,"MS-VD----   no    event, line: {}".format(line) )
					continue
				evNo = int(event[1].split()[0])


				if self.decideMyLog("Video"): self.indiLOG.log(10,"MS-VD----  parsed items: #{:5d}  {}    {:13.1f}  {} {}".format(evNo, evType, timeSt, MAC, cameraName) )


				if MAC not in self.cameras:
					self.cameras[MAC] = {"cameraName":cameraName,"events":{},"eventsLast":{"start":0,"stop":0},"devid":-1,"uuid":"", "ip":"", "apiKey":""}

				if evNo not in	self.cameras[MAC]["events"]:
					self.cameras[MAC]["events"][evNo] = {"start":0,"stop":0}


				if len(self.cameras[MAC]["events"]) > self.unifiVIDEONumerOfEvents:
					delEvents={}
					for ev in self.cameras[MAC]["events"]:
						try:
							if int(evNo) - int(ev) > self.unifiVIDEONumerOfEvents:
								delEvents[ev]=True
						except:
							self.indiLOG.log(40,"doVDmessages error in ev# {};	  evNo {};	 maxNumberOfEvents: {}\n to fix:  try to rest event count ".format(ev, evNo, self.unifiVIDEONumerOfEvents) )



					if len(delEvents) >0:
						if self.decideMyLog("Video"): self.indiLOG.log(10,"MS-VD----  {} number of events > {}; deleting {} events".format(cameraName, self.unifiVIDEONumerOfEvents, len(delEvents)) )
						for ev in delEvents:
							del	 self.cameras[MAC]["events"][ev]

				self.cameras[MAC]["events"][evNo][evType]  = timeSt


				devFound = False
				if "devid" in self.cameras[MAC]:
					try:
						dev = indigo.devices[self.cameras[MAC]["devid"]]
						devFound = True
					except: pass
				if	not devFound:
					for dev in indigo.devices.iter("props.isCamera"):
						if "MAC" not in dev.states:	   continue
						if dev.states["MAC"] == MAC:
							devFound = True
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
						props["isCamera"] = True
						dev.replacePluginPropsOnServer()
						dev = indigo.devices[dev.id]
						self.saveCameraEventsStatus = True
					except	Exception as e:
							if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
							if "NameNotUniqueError" in "{}".format(e):
								dev = indigo.devices["Camera_"+cameraName+"_"+MAC]
								self.indiLOG.log(10,"states  {}".format(dev.states))
								dev.updateStateOnServer("MAC", MAC)
								dev.updateStateOnServer("eventNumber", -1)
								props = dev.pluginProps
								props["isCamera"] = True
								dev.replacePluginPropsOnServer()
								dev = indigo.devices[dev.id]

							continue
					indigo.variable.updateValue("Unifi_New_Device", "{}/{}".format(dev.name, MAC) )
					self.pendingCommand.append("getConfigFromNVR")

				self.cameras[MAC]["devid"] = dev.id

				if dev.states["eventNumber"] > evNo or ( self.cameras[MAC]["events"][evNo][evType] <= self.cameras[MAC]["eventsLast"][evType]) :
					try:
						if time.time() - self.listenStart[ipNumber][uType] > 30:
							self.indiLOG.log(10,"MS-VD----  "+"rejected event number {}".format(evNo)+" resetting event No ; time after listener lauch: %5.1f"%(time.time() - self.listenStart[ipNumber][uType]))
							self.addToStatesUpdateList(dev.id,"eventNumber", evNo)
					except	Exception as e:
							if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
							self.indiLOG.log(40,"rejected event dump  "+ipNumber+"    {}".format(self.listenStart))
							self.addToStatesUpdateList(dev.id,"eventNumber", evNo)


				if self.decideMyLog("Video"): self.indiLOG.log(10,"MS-VD----  "+"event # {}".format(evNo)+" accepted ; delta T from listener lauch: %5.1f"%(time.time() - self.listenStart[ipNumber][uType]))
				dateStr = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(timeSt))
				if evType == "start":
					self.addToStatesUpdateList(dev.id,"lastEventStart", dateStr )
					self.addToStatesUpdateList(dev.id,"status", "REC")
					if self.imageSourceForEvent == "imageFromNVR":
						if dev.states["eventJpeg"] != self.changedImagePath+dev.name+".jpg": # update only if new
							self.addToStatesUpdateList(dev.id,"eventJpeg",self.changedImagePath+dev.name+"_event.jpg")
						self.getSnapshotfromNVR(dev.id, self.cameraEventWidth, self.changedImagePath+dev.name+"_event.jpg")
					if self.imageSourceForEvent == "imageFromCamera":
						if dev.states["eventJpeg"] != self.changedImagePath+dev.name+".jpg": # update only if new
							self.addToStatesUpdateList(dev.id,"eventJpeg",self.changedImagePath+dev.name+"_event.jpg")
						self.getSnapshotfromCamera(dev.id, self.changedImagePath+dev.name+"_event.jpg")

				elif evType == "stop":
					self.addToStatesUpdateList(dev.id,"lastEventStop", dateStr )
					self.addToStatesUpdateList(dev.id,"status", "off" )
					evLength  = float(self.cameras[MAC]["events"][evNo]["stop"]) - float(self.cameras[MAC]["events"][evNo]["start"])
					self.addToStatesUpdateList(dev.id,"lastEventLength", int(evLength))

					try:
						if self.imageSourceForEvent == "imageFromDirectory":
							if dev.states["uuid"] !="":
								year = dateUTC[0:4]
								mm	 = dateUTC[4:6]
								dd	 = dateUTC[6:8]

								fromDir	   = self.videoPath+dev.states["uuid"]+"/"+year+"/"+mm+"/"+dd+"/meta/"
								toDir	   = self.changedImagePath
								last	   = 0.
								newestFile = ""
								filesInDir = ""

								if not os.path.isdir(fromDir):
										if not os.path.isdir(self.videoPath+dev.states["uuid"]):						os.mkdir(self.videoPath+dev.states["uuid"])
										if not os.path.isdir(self.videoPath+dev.states["uuid"]+"/"+year):				os.mkdir(self.videoPath+dev.states["uuid"]+"/"+year)
										if not os.path.isdir(self.videoPath+dev.states["uuid"]+"/"+year+"/"+mm):		os.mkdir(self.videoPath+dev.states["uuid"]+"/"+year+"/"+mm)
										if not os.path.isdir(self.videoPath+dev.states["uuid"]+"/"+year+"/"+mm+"/"+dd): os.mkdir(self.videoPath+dev.states["uuid"]+"/"+year+"/"+mm+"/"+dd)
										if not os.path.isdir(fromDir):													os.mkdir(fromDir)

								for testFile in os.listdir(fromDir):
									if testFile.find(".jpg") == -1: continue
									timeStampOfFile = os.path.getmtime(os.path.join(fromDir, testFile))
									if	timeStampOfFile > last:
										last = timeStampOfFile
										newestFile = testFile
								if newestFile =="":
									if self.decideMyLog("Video"): self.indiLOG.log(10,"MS-VD-EV-  {}  no file found".format(dev.name))
									continue

								if dev.states["eventJpeg"] != fromDir+newestFile: # update only if new
									self.addToStatesUpdateList(dev.id,"eventJpeg",fromDir+newestFile)
									if os.path.isdir(toDir): # copy to destination directory
										if os.path.isfile(fromDir+newestFile):
											cmd = "cp '"+fromDir+newestFile+"' '"+toDir+dev.name+"_event.jpg' &"
											if self.decideMyLog("Video"): self.indiLOG.log(10,"MS-VD-EV-  copy event file: {}".format(cmd))
											subprocess.Popen(cmd,shell=True)
									else:
										if self.decideMyLog("Video"): self.indiLOG.log(10,"MS-VD-EV-  "+"path "+ self.changedImagePath+"     does not exist.. no event files copied")

					except	Exception as e:
						if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

				self.cameras[MAC]["eventsLast"] = copy.copy(self.cameras[MAC]["events"][evNo])
				self.addToStatesUpdateList(dev.id,"eventNumber", int(evNo) )
				self.executeUpdateStatesList()

		except	Exception as e:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		self.unsetBlockAccess("doVDmessages")
		
		return



	####-----------------	 ---------
	def doGWmessages(self, lines,ipNumber,apN):
		try:
			devType	 = "UniFi"
			isType	 = "isUniFi"
			devName	 = "UniFi"
			suffixN	 = "DHCP"
			xType	 = "UN"

			self.setBlockAccess("doGWmessages")

# looking for dhcp refresh requests
#  Oct 26 22:20:00 GW sudo:		root : TTY=unknown ; PWD=/ ; USER=root ; COMMAND=/bin/sh -c echo -e '192.168.1.180\t iPhone.localdomain\t #on-dhcp-event 18:65:90:6a:b9:c' >> /etc/hosts

			tag = "TTY=unknown ; PWD=/ ; USER=root ; COMMAND=/bin/sh -c echo -e '"
			for line in lines:
				if len(line) < 10: continue
				if line.find(tag) ==-1: continue
				if self.decideMyLog("LogDetails"): self.indiLOG.log(10,"MS-GW---   "+line )
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
						dev = indigo.devices[self.MAC2INDIGO[xType][MAC]["devId"]]
						if dev.deviceTypeId != devType: 1/0
						new = False
					except:
						if self.decideMyLog("LogDetails", MAC=MAC): self.indiLOG.log(10,MAC + "  {}".format(self.MAC2INDIGO[xType][MAC]["devId"]) + " wrong " + devType)
						for dev in indigo.devices.iter("props."+isType):
							if "MAC" not in dev.states: continue
							if dev.states["MAC"] != MAC: continue
							self.MAC2INDIGO[xType][MAC]={}
							self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
							self.MAC2INDIGO[xType][MAC]["devId"] = dev.id
							new = False
							break
						del self.MAC2INDIGO[xType][MAC]
				if not new:
					props=dev.pluginProps
					new = False
					if dev.states["ipNumber"] != ip:
						self.addToStatesUpdateList(dev.id,"ipNumber", ip)
					## if a device asks for dhcp extension, it must be alive,  good for everyone..
					if True: #  Always true, if active request to renew DHCP, must be present  "useWhatForStatus" in props and props["useWhatForStatus"].find("DHCP") >-1:
						if dev.states["status"] != "up":
							self.setImageAndStatus(dev, "up",oldStatus= dev.states["status"],ts=time.time(), level=1, text1=  dev.name.ljust(30) +"  status up        GW-DHCP renew request", iType="STATUS-DHCP",reason="MS-DHCP "+"up")
						else:
							if self.decideMyLog("LogDetails", MAC=MAC): self.indiLOG.log(10,"MS-GW-DHCP {} restarting expTimer due to DHCP renew request from device".format(MAC) )
						self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()

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
							props			={"useWhatForStatus":"DHCP","useAgeforStatusDHCP":"-1",isType:True})
					except	Exception as e:
						if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
						continue
					self.setupStructures(xType, dev, MAC)
					self.setupBasicDeviceStates(dev, MAC, "UN", "", "", "", " status up       GW msg new device", "STATUS-DHCP")
					self.executeUpdateStatesList()
					dev = indigo.devices[dev.id]
					self.setupStructures(xType, dev, MAC)
					indigo.variable.updateValue("Unifi_New_Device","{}/{}/{}".format(dev.name, MAC, ip) )

			self.executeUpdateStatesList()
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		self.executeUpdateStatesList()

		self.unsetBlockAccess("doGWmessages")

		return


	####-----------------	 ---------
	def doSWmessages(self, lines, ipNumber,apN ):
		return

		self.setBlockAccess("doSWmessages")

		try:
			for line in lines:
				if len(line) < 2: continue
				if self.decideMyLog("Log"): self.indiLOG.log(10,"MS-SW---   "+ipNumber+"    " + line)


		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		self.unsetBlockAccess("doSWmessages")
		
		return


	####-----------------	 ---------
	def doAPmessages(self, lines, ipNumberAP, apN, webApiLog=False):

		try:
			self.setBlockAccess("doAPmessages")

			devType = "UniFi"
			isType	= "isUniFi"
			devName = "UniFi"
			suffixN	 = "WiFi"
			xType	=  "UN"


			for line in lines:
				MAC = ""
				GHz = ""
				up = False
				token = ""
				if webApiLog: # message from UDM re-packaged as AP message
					MAC = line["user"]
					up = True
					token = "steady"
					if line["key"].lower().find("disconnected") >-1:
						token = "DISCONNECTED"
						up = False
					if line["key"].lower().find("disassociated") >-1:
						token = "DISCONNECTED"
						up = False

					#### roaming:::::
					elif line["key"].lower().find("roam") >-1:
						if  "IP_to" in line and "IP_from" in line:
							if line["IP_to"] !="" and line["IP_from"] !="":
								self.HANDOVER[MAC] = {"tt":line["time"],"ipNumberNew": line["IP_to"], "ipNumberOld": line["IP_from"]}
								token = "roam"
							else:
								if self.decideMyLog("UDM", MAC=MAC):self.indiLOG.log(10,"MS-AP-WB-E {} roam data wrong (IP_from/to empty) event:{}; ".format(MAC, line))
						elif  "channel_from" in line or "channel_to" in line: # this is just change of channel, no real roaming to other AP
							pass 
						else:
							if self.decideMyLog("UDM", MAC=MAC):self.indiLOG.log(10,"MS-AP-WB-E {} roam data wrong (IP_from/to missing) event:{}; ".format(MAC, line))

					else:
						pass

					GHz = "2"
					if "channel"    in line and int(line["channel"])    >= 12:	GHz = "5"
					if "channel_to" in line and int(line["channel_to"]) >= 12:	GHz = "5"
					timeOfMSG = line["time"]
					if self.decideMyLog("UDM", MAC=MAC):self.indiLOG.log(10,"MS-AP-WB-0 {};  ipNumberAP:{};  GHz:{}; up:{} token:{}, dTime:{:.1f}; api-event:{}; ".format( MAC, ipNumberAP, GHz, up, token, time.time()-timeOfMSG, line))

				else: # regular ap message
					if len(line) < 2: continue
					tags = line.split()
					MAC = ""

					ll = line.find("[HANDOVER]") + 10 +1 ## len of [HANDOVER] + one space
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
					elif line.find("Presence at AP") > -1 and line.find("verified for") > -1:
						MAC = tags[-1]
						if not self.isValidMAC(MAC):					 continue
						ipNumberAP = tags[-4]

					elif line.find("EVENT_STA_JOIN ") > -1 and line.find("verified for") > -1:
							ipNumberAP = tags[-4]

					else:
						try:
							ll = tags.index("STA")
							if ll+1 >=	len(tags):				 		continue
							MAC = tags[ll + 1]
							if not self.isValidMAC(MAC):
								continue
							if	line.find("Authenticating") > 10:
								continue
							if	line.find("STA Leave!!") != -1 :
								continue
							if	line.find("STA enter") != -1:
								continue
						except Exception as e:
							if "{}".format(e).find("not in list") >-1: 		continue
							if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
							continue

					up = True
					token = ""
					if line.lower().find("disassociated") > -1:
						token = "disassociated"
						up = False
					elif line.lower().find("disconnected") > -1:
						token = "DISCONNECTED"
						up = False
					elif line.find(" sta_stats") > -1:
						token = "sta_stats"
						up = False
					if line.find("ath0:") > -1: GHz = "5"
					if line.find("ath1:") > -1: GHz = "2"
					timeOfMSG = time.time()

					if self.decideMyLog("LogDetails", MAC=MAC):self.indiLOG.log(10,"MS-AP-WF-0 {:13s}#{}; {};  GHz:{}; up:{} token:{}, log-event:{}".format( ipNumberAP,apN, MAC , GHz, up, token, line))

				if self.testIgnoreMAC(MAC, fromSystem="AP-msg"): continue


				if MAC != "":

					if MAC in self.HANDOVER:
						if time.time() - self.HANDOVER[MAC]["tt"] <1.3: # protect for 1+ secs when in handover mode
							ipNumber = self.HANDOVER[MAC]["ipNumberNew"]
							up = True
						else:
							del self.HANDOVER[MAC]

					new = True
					if MAC in self.MAC2INDIGO[xType]:
						try:
							dev = indigo.devices[self.MAC2INDIGO[xType][MAC]["devId"]]
							new = False
						except:
							if self.decideMyLog(""): self.indiLOG.log(10,"{}     {} wrong {}".format(MAC, self.MAC2INDIGO[xType][MAC]["devId"], devType) )
							for dev in indigo.devices.iter("props."+isType):
								if "MAC" not in dev.states:		 continue
								if dev.states["MAC"] != MAC:	 continue
								self.MAC2INDIGO[xType][MAC]={}
								self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
								self.MAC2INDIGO[xType][MAC]["devId"] = dev.id
								self.MAC2INDIGO[xType][MAC]["lastAPMessage"] = timeOfMSG
								new = False
								break

					if not new:
						props =	 dev.pluginProps
						devId = "{}".format(dev.id)
						if devId not in self.upDownTimers:
							self.upDownTimers[devId] = {"down": 0, "up": 0}

						if "lastAPMessage" not in self.MAC2INDIGO[xType][MAC]: self.MAC2INDIGO[xType][MAC]["lastAPMessage"] = 0
						if timeOfMSG - self.MAC2INDIGO[xType][MAC]["lastAPMessage"] < -2: 
							if self.decideMyLog("LogDetails", MAC=MAC): self.indiLOG.log(10,"MS-AP-WF-1 ..ignore msg, older than last AP message; lastMSG:{:.1f}, thisMSG:{:.1f}".format(self.MAC2INDIGO[xType][MAC]["lastAPMessage"],timeOfMSG ) )
							continue

						oldIP = dev.states["AP"]
						if ipNumberAP != "" and ipNumberAP != oldIP.split("-")[0]:
							if up:
								self.addToStatesUpdateList(dev.id,"AP", ipNumberAP+"-#{}".format(apN))
							else:
								if self.decideMyLog("LogDetails", MAC=MAC): self.indiLOG.log(10,"MS-AP-WF-2  .. old->new associated AP {}->{}-{} not setting to down, as associated to old AP".format( oldIP, ipNumberAP, apN))
								continue


						if "useWhatForStatus" in props and props["useWhatForStatus"].find("WiFi") > -1:

							if self.decideMyLog("LogDetails", MAC=MAC): self.indiLOG.log(10,"MS-AP-WF-3  .. old->new associated {}->{}#{}".format( oldIP, ipNumberAP, apN) )

							if up: # is up now
								self.MAC2INDIGO[xType][MAC]["idleTime" + suffixN] = 0
								self.upDownTimers[devId]["down"] = 0
								self.upDownTimers[devId]["up"] = time.time()
								if dev.states["status"] != "up":
									if self.decideMyLog("LogDetails", MAC=MAC): self.indiLOG.log(10,"MS-AP-WF-4  .. ipNumberAP:{} 'setting state to UP' from:{}".format( ipNumberAP, dev.states["status"]))
									self.setImageAndStatus(dev, "up",oldStatus= dev.states["status"], ts=time.time(), level=1, text1= "{:30s} status up  AP message received >{}<".format(dev.name,ipNumberAP), iType="MS-AP-WF-4 ",reason="MSG WiFi "+"up")
								if self.decideMyLog("Logic", MAC=MAC): self.indiLOG.log(10,"MS-AP-WF-R   ==> restart exptimer use AP log-msg, exp-time left:{:5.1f}".format(self.getexpT(props) -(time.time()-self.MAC2INDIGO[xType][MAC]["lastUp"]) ))
								self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()

							else: # is down now
								try:
									if devId not in self.upDownTimers:
										self.upDownTimers[devId] = {"down": 0, "up": 0}

									if ipNumberAP == "" or ipNumberAP == oldIP.split("-")[0]: # only if its on the same current AP
										dt = (time.time() - self.upDownTimers[devId]["up"])

										if "useWhatForStatusWiFi" in props and props["useWhatForStatusWiFi"] in ["FastDown","Optimized"]:
											if self.decideMyLog("LogDetails", MAC=MAC): self.indiLOG.log(10,"MS-AP-WF-5  .. checking timer,   token:down;  tt-uptDelay:{:4.1f}".format(dt) )
											if dt > 5.0 and (props["useWhatForStatusWiFi"] == "FastDown" or (time.time() - self.MAC2INDIGO[xType][MAC]["lastUp"]) > self.getexpT(props) ):
												if dev.states["status"] == "up":
													if props["useWhatForStatusWiFi"] == "FastDown":  # in fast down set it down right now
														self.setImageAndStatus(dev, "down",oldStatus="up", ts=time.time(), level=1, text1=MAC +", "+ dev.name.ljust(30)+" status down    AP message received fast down-", iType="MS-AP-WF-5 ",reason="MSG FAST down")
														self.upDownTimers[devId]["down"] = time.time()
													else:  # in optimized give it 3 more secs
														self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time() - self.getexpT(props) + 3
														self.upDownTimers[devId]["down"] = time.time() + 3
													self.upDownTimers[devId]["up"]	  = 0.

										elif dt > 2.:
											if self.decideMyLog("LogDetails", MAC=MAC): self.indiLOG.log(10,"MS-AP-WF-6  .. ipNumberAP:{} 'delay settings updown timer < 2; set uptimer =0, downtimer =tt'".format( ipNumberAP))
											self.upDownTimers[devId]["down"] =	 time.time()  # this is a down message
											self.upDownTimers[devId]["up"]	  = 0.
								except	Exception as e:
									if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)


						if self.updateDescriptions:
							if dev.description.find("=WiFi")==-1 and  len(dev.description) >2:
								dev.description = dev.description+"=WiFi"
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
								props			={"useWhatForStatus":"WiFi","useWhatForStatusWiFi":"Expiration",isType:True})
						except Exception as e:
							if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
							continue
						self.setupStructures(xType, dev, MAC)
						self.addToStatesUpdateList(dev.id,"AP", ipNumberAP+"-#{}".format(apN))
						self.MAC2INDIGO[xType][MAC]["idleTime" + suffixN] = 0
						if "{}".format(dev.id) in self.upDownTimers:
							del self.upDownTimers["{}".format(dev.id)]
						self.setupBasicDeviceStates(dev, MAC,  "UN", "", "", "", "    " +MAC+" status up   AP msg new device", "MS-AP-WF-6 ")
						indigo.variable.updateValue("Unifi_New_Device","{}{}".format(dev.name, MAC) )
						self.executeUpdateStatesList()
						dev = indigo.devices[dev.id]
						self.setupStructures(xType, dev, MAC)
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		self.executeUpdateStatesList()

		self.unsetBlockAccess("doAPmessages")

		return

	####-----------------	 ---------
	### double check up/down with ping
	####-----------------	 ---------
	def doubleCheckWithPing(self,newStatus, ipNumber, props,MAC,debLevel, section, theType,xType):

		if ("usePingUP" in props and props["usePingUP"] and newStatus =="up" ) or ( "usePingDOWN" in props and props["usePingDOWN"] and newStatus !="up") :
			if self.checkPing(ipNumber, nPings=1, waitForPing=500, calledFrom="doubleCheckWithPing") !=0:
				if self.decideMyLog(debLevel, MAC=MAC): self.indiLOG.log(10,theType+"  "+" "+MAC+" "+section+" , status changed - not up , ping test failed" )
				return 1
			else:
				if self.decideMyLog(debLevel, MAC=MAC): self.indiLOG.log(10,theType+"  "+" "+MAC+" "+section+" , status changed - not up , ping test OK" )
				if xType in self.MAC2INDIGO:
					self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
				return 0
		return -1


	####-----------------	 ---------
	### for the dict,
	####-----------------	 ---------
	def comsumeDictData(self):#, startTime):
		self.sleep(1)
		self.indiLOG.log(10,"comsumeDictData: process starting")
		nextItem = "     "
		while True:
			try:
				if self.pluginState == "stop" or self.consumeDataThread["dict"]["status"] == "stop": 
					self.indiLOG.log(30,"comsumeDictData: stopping process due to stop request")
					return 
				self.sleep(0.1)
				consumedTimeQueue = time.time()
				queueItemCount = 0
				while not self.logQueueDict.empty():
					if self.pluginState == "stop" or self.consumeDataThread["dict"]["status"] == "stop": 
						self.indiLOG.log(30,"comsumeDictData: stopping process due to stop request")
						return 

					queueItemCount += 1
					nextItem = self.logQueueDict.get()
					consumedTime = time.time()
					self.updateIndigoWithDictData( nextItem[0], nextItem[1], nextItem[2], nextItem[3], nextItem[4] )
					consumedTime -= time.time()

					if consumedTime < -self.maxConsumedTimeQueueForWarning:	logLevel = 20
					else:													logLevel = 10
					if logLevel == 20:
						self.indiLOG.log(logLevel,"comsumeDictData       excessive time consumed:{:5.1f}[secs]; {:16}-{:2}-{:6} len:{:},  item:{:}".format(-consumedTime, nextItem[1], nextItem[2], nextItem[3], len(nextItem[0]), "{}".format(nextItem[0])[0:100] ) )

					self.logQueueDict.task_done()

					if len(self.sendUpdateToFingscanList) > 0: self.sendUpdatetoFingscanNOW()
					if len(self.sendBroadCastEventsList)  > 0: self.sendBroadCastNOW()

				consumedTimeQueue -= time.time()
				if consumedTimeQueue < -self.maxConsumedTimeQueueForWarning:	logLevel = 20
				else:															logLevel = 10
				if logLevel == 20:
						self.indiLOG.log(logLevel,"comsumeDictData Total excessive time consumed:{:5.1f}[secs]; {:16}-{:2}-{:6}; items:{:2} len:{:},  item:{:}".format(-consumedTimeQueue, nextItem[1], nextItem[2], nextItem[3], queueItemCount, len(nextItem[0]),  "{}".format(nextItem[0])[0:100]) )
	
			except	Exception as e:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		self.indiLOG.log(30,"comsumeDictData: stopping process (3)")
		return 



	####-----------------	 ---------
	def updateIndigoWithDictData(self, apDict, ipNumber, apNumb, uType, unifiDeviceType):

		try:
			#if self.decideMyLog("Special"): self.indiLOG.log(10,"updateIndigoWithDictData apDict[0:100]:{}, ipNumber:{}, apNumb:{}, uType:{}, unifiDeviceType:{}".format("{}".format(apDict)[0:100], ipNumber, apNumb, uType, unifiDeviceType ) )

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
			if unifiDeviceType == "UD" and self.unifiControllerType.find("UDM") > -1:
				doSW 	 = True
				doGW 	 = True
				doAP 	 = True
				apNumbSW = self.numberForUDM["SW"]
				apNumbAP = self.numberForUDM["AP"]

			if self.debugThisDevices(uType, apNumb) or self.decideMyLog("Dict"): 
				dd = "{}".format(apDict)
				self.indiLOG.log(10,"DEVdebug   {} dev #sw:{},ap:{}, uType:{}, unifiDeviceType:{}; dictmessage:\n{} ..\n{}".format(ipNumber, apNumbSW, apNumbAP, uType, unifiDeviceType, dd[:50], dd[-50:] ) )


			if self.decideMyLog("UDM"):  self.indiLOG.log(10,"updDict  ipNumber:{};  apNumb:{};  uType:{};  unifiDeviceType:{};  doGW:{}; ".format(ipNumber,  apNumb, uType, unifiDeviceType, doGW) )
			if unifiDeviceType == "GW" or doGW:
				if self.decideMyLog("UDM"):  self.indiLOG.log(10,"updDict  dict:\n{}".format(apDict) )
				self.doGatewaydictSELF(apDict, ipNumber)
				if self.unifiControllerType.find("UDM") >-1: 
					self.doGWDvi_stats(apDict, ipNumber)
				else:
					self.doGWHost_table(apDict, ipNumber)



			if unifiDeviceType == "SW" or doSW:
				if(	"mac"		  in apDict and 
				  	"port_table" in apDict and
				 	"hostname"	  in apDict and
				  	"ip"		  in apDict ):

					MACSW = apDict["mac"]
					hostname = apDict["hostname"].strip()
					ipNDevice = apDict["ip"]

					#################  update SWs themselves
					self.doSWdictSELF(apDict, apNumbSW, ipNDevice, MACSW, hostname, ipNumber)

					#################  now update the devices on switch
					self.doSWITCHdictClients(apDict, apNumbSW, ipNDevice, MACSW, hostname, ipNumber)
				else:
					pass
##					self.indiLOG.log(10,"DICTDATA    rejected .. mac, port_table, hostname ip not in dict ..{}".format(apDict))


			if unifiDeviceType == "AP" or doAP:
				if(	"mac"		 in apDict and
					"vap_table" in apDict and
					"ip"		 in apDict):

					MACAP		 = apDict["mac"]
					hostname = apDict["hostname"].strip()
					ipNDevice= apDict["ip"]

					clientHostnames = {"2":"","5":""}
					for jj in range(len(apDict["vap_table"])):
						if "usage" in apDict["vap_table"][jj]: #skip if not wireless
							if apDict["vap_table"][jj]["usage"] == "downlink": continue
							if apDict["vap_table"][jj]["usage"] == "uplink":	continue

						channel = "{}".format(apDict["vap_table"][jj]["channel"])
						if int(channel) >= 12:
							GHz = "5"
						else:
							GHz = "2"
						if "sta_table" in apDict["vap_table"][jj] and apDict["vap_table"][jj]["sta_table"] !=[]:
							clientHostnames[GHz] = self.doWiFiCLIENTSdict(apDict["vap_table"][jj]["sta_table"], GHz, ipNDevice, apNumbAP, ipNumber)

						#################  update APs themselves
					self.doAPdictsSELF(apDict, apNumbAP, ipNDevice, MACAP, hostname, ipNumber, clientHostnames)


					############  update neighbors
					if "radio_table" in	 apDict:
						self.doNeighborsdict(apDict["radio_table"], apNumbAP, ipNumber)
				else:
					pass
###					self.indiLOG.log(10,"DICTDATA    rejected .. mac, vap_table,  ip not in dict ..{}".format(apDict))


		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)


		return






	#################  update APs
	####-----------------	 ---------
	def checkInListSwitch(self):

		xType = "UN"
		ignore ={}
		try:
			for dev in indigo.devices.iter("props.isSwitch"):
				nn  = int(dev.states["switchNo"])
				if not self.devsEnabled["SW"][nn]:
					ignore["inListSwitch_{}".format(nn)] = -1
				if  not self.isValidIP(self.ipNumbersOf["SW"][nn]):
					ignore["inListSwitch_{}".format(nn)] = -1

			for nn in range(_GlobalConst_numberOfSW):
				if not self.devsEnabled["SW"][nn]:
					ignore["inListSwitch_{}".format(nn)] = -1
				if  not self.isValidIP(self.ipNumbersOf["SW"][nn]):
					ignore["inListSwitch_{}".format(nn)] = -1

			if not self.devsEnabled["GW"]:
				ignore["inListDHCP"] = 0
				ignore["upTimeDHCP"] = ""
			if  not self.isValidIP(self.ipNumbersOf["GW"]):
				ignore["inListDHCP"] = 0
				ignore["upTimeDHCP"] = ""

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

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return


	####-----------------	 ---------
	#################  update APs
	####-----------------	 ---------
	def doInList(self,suffixN,	wifiIPAP=""):


		suffix = suffixN.split("_")[0]
		try:
			## now check if device is not in dict, if not ==> initiate status --> down
			xType = "UN"
			delMAC={}
			for MAC in self.MAC2INDIGO[xType]:
				if self.MAC2INDIGO[xType][MAC]["inList"+suffixN]  == -1: continue	# do not test
				if self.MAC2INDIGO[xType][MAC]["inList"+suffixN]  ==  1: continue	# is here
				try:
					devId = self.MAC2INDIGO[xType][MAC]["devId"]
					dev	  = indigo.devices[devId]
					aW	  = dev.states["AP"]
					if wifiIPAP =="" or aW == wifiIPAP:
						self.MAC2INDIGO[xType][MAC]["inList"+suffixN] = 0
					if wifiIPAP !="" and aW != wifiIPAP:											 continue
					if dev.states["status"] != "up":											 continue

					props= dev.pluginProps
					if "useWhatForStatus" not in props or props["useWhatForStatus"].find(suffix) == -1:	 continue
				except	Exception as e:
					if "{}".format(e).find("timeout waiting") > -1:
						if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
						self.indiLOG.log(40,"communication to indigo is interrupted")
						return
					if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
					self.indiLOG.log(40,"deleting device from internal lists -- MAC:"+ MAC+";  devId:{}".format(devId))
					delMAC[MAC]=1
					continue

				try:
					lastUpTT   = self.MAC2INDIGO[xType][MAC]["lastUp"]
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


				if dev.states["status"] != status and status !="up":
					if "usePingUP" in props and props["usePingUP"]	and status !="up" and self.sendWakewOnLanAndPing(MAC,dev.states["ipNumber"], props=props, nPings=1, calledFrom="inList") == 0:
							if self.decideMyLog("Logic", MAC=MAC): self.indiLOG.log(10,"List-"+suffix+"    " +dev.states["MAC"]+" check, status changed - not up , ping test ok resetting to up" )
							self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
							continue

					self.setImageAndStatus(dev, status,oldStatus=dev.states["status"], ts=time.time(), level=1, text1= dev.name.ljust(30) + " in list status " + status.ljust(10) + " "+suffixN+"     dt= %5.1f" % dt + ";  expT= %5.1f" % expT+ "  wifi:" +wifiIPAP, iType="STATUS-"+suffix,reason="NotInList "+suffixN+" "+wifiIPAP+" "+status)

			for MAC in delMAC:
				del	 self.MAC2INDIGO[xType][MAC]

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return




	####-----------------	 ---------
	#### this does the unifswitch attached devices
	####-----------------	 ---------
	def doSWITCHdictClients(self, apDict, swNumb, ipNDevice, MACSW, hostnameSW, ipNumber):


		try:

			devType = "UniFi"
			isType	= "isUniFi"
			devName = "UniFi"
			suffix	= "SWITCH"
			xType	= "UN"

			portTable = apDict["port_table"]


			UDMswitch = False
			useIP = ipNumber
			if self.unifiControllerType.find("UDM") > -1 and swNumb == self.numberForUDM["SW"]:
				UDMswitch = True
				if self.decideMyLog("UDM"):  self.indiLOG.log(10,"DC-SW-UDM  using UDM mode  for  IP#Dict:{}  ip#proc#{} ".format(ipNDevice, ipNumber) )


			if useIP not in self.deviceUp["SW"]:
				return

			switchNumber = -1
			for ii in range(_GlobalConst_numberOfSW):
				if not self.devsEnabled["SW"][ii]:				continue
				if useIP != self.ipNumbersOf["SW"][ii]: 	continue
				switchNumber = ii
				break

			if switchNumber < 0:
				return

			self.setBlockAccess("doSWITCHdict")

			swN		= "{}".format(switchNumber)
			suffixN = suffix+"_"+swN


			for MAC in self.MAC2INDIGO[xType]:
				if len(MAC) < 16:
					self.MAC2INDIGO[xType][MAC]["inList"+suffixN] = -1	 # was not here
					continue
				try:
					if "inList"+suffixN not in self.MAC2INDIGO[xType][MAC]:
						self.indiLOG.log(40,"error in doSWITCHdictClients: mac:{}  inList{} not in NMAC2INDIGO:{}".format(MAC,suffix,  self.MAC2INDIGO[xType][MAC]))
						continue
					if self.MAC2INDIGO[xType][MAC]["inList"+suffixN]  > 0:	 # was here was here , need to test
						self.MAC2INDIGO[xType][MAC]["inList"+suffixN] = 0
				except:
						self.indiLOG.log(40,"error in doSWITCHdictClients: mac:{}  MAC2INDIGO:{}".format(MAC, self.MAC2INDIGO[xType][MAC]))
						return
				else:
					self.MAC2INDIGO[xType][MAC]["inList"+suffixN] = -1	 # was not here


			for port in portTable:

				portN = "{}".format(port["port_idx"])
				if "mac_table" not in port: continue
				macTable =	port["mac_table"]
				if macTable == []:	continue
				if "port_idx" in port:
					portN = "{}".format(port["port_idx"])
				else:
					portN = ""
				isUpLink = False
				isDownLink = False

				if "is_uplink"	  in port and port["is_uplink"]:			isUpLink   = True
				elif "lldp_table" in port and len(port["lldp_table"]) > 0:	isDownLink = True

				#if isUpLink:		   continue
				#if isDownLink:		   continue

				for switchDevices in macTable:
					MAC = switchDevices["mac"]
					if self.testIgnoreMAC(MAC, fromSystem="SW-Dict"): continue

					if "vlan" in switchDevices:		vlan	   = switchDevices["vlan"]
					else: vlan = ""

					if "age" in switchDevices:		age	   = switchDevices["age"]
					else: age = ""

					if "ip" in switchDevices:
													ip	   = switchDevices["ip"]
													try:	self.MAC2INDIGO[xType][MAC]["ipNumber"] = ip
													except: continue
					else:							ip = ""

					if "uptime" in switchDevices:	newUp  = "{}".format(switchDevices["uptime"])
					else: newUp = ""

					nameSW = "empty"
					if "hostname" in switchDevices: nameSW = "{}".format(switchDevices["hostname"]).strip()
					if nameSW == "?":    nameSW = "empty"
					if len(nameSW) == 0: nameSW = "empty"

					ipx = self.fixIP(ip)
					new = True
					if MAC in self.MAC2INDIGO[xType]:
						try:
							dev = indigo.devices[self.MAC2INDIGO[xType][MAC]["devId"]]
							if dev.deviceTypeId != devType: 1 / 0
							self.MAC2INDIGO[xType][MAC]["inList"+suffixN] = 1 # is here
							new = False
						except:
							if self.decideMyLog("Logic", MAC=MAC): self.indiLOG.log(10, "{}     {} wrong {}".format(MAC, self.MAC2INDIGO[xType][MAC]["devId"], devType))
							for dev in indigo.devices.iter("props."+isType):
								if "MAC" not in dev.states:			continue
								if dev.states["MAC"] != MAC:		continue
								self.setupStructures(xType, dev, MAC, init=False)
								self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
								self.MAC2INDIGO[xType][MAC]["inList"+suffixN] = 1
								new = False
								break

					if not new:

						self.MAC2INDIGO[xType][MAC]["inList"+suffixN] = 1
						if self.decideMyLog("Dict", MAC=MAC): self.indiLOG.log(10,"DC-SW-00   {:15s}  {}; {}; IP:{}; AGE:{}; newUp:{}; hostN:{}".format(useIP, MAC, dev.name, ip, age, newUp, nameSW))

						if not ( isUpLink or isDownLink ): # this is not for up or downlink 
							poe = ""
							if MACSW in self.MAC2INDIGO["SW"]:  # do we know the switch
								if portN in self.MAC2INDIGO["SW"][MACSW]["ports"]: # is the port in the switch
									if  "nClients" in self.MAC2INDIGO["SW"][MACSW]["ports"][portN] and  self.MAC2INDIGO["SW"][MACSW]["ports"][portN]["nClients"] == 1: 
										if "poe" in self.MAC2INDIGO["SW"][MACSW]["ports"][portN] and self.MAC2INDIGO["SW"][MACSW]["ports"][portN]["poe"]  != "": # if empty dont add "-"
											poe = "-"+self.MAC2INDIGO["SW"][MACSW]["ports"][portN]["poe"]
										if len(dev.states["AP"]) > 5: # fix if direct connect and poe is one can not have wifi for this MAC, must be ethernet, set wifi to "-"
											self.addToStatesUpdateList(dev.id,"AP", "-")

							newPort = swN+":"+portN+poe
							#self.indiLOG.log(10,"portInfo   MACSW: "+MACSW +"   hostnameSW:"+hostnameSW+"  "+useIP +" "+ MAC+"  portN:"+portN+" MACSW-poe:"+ self.MAC2INDIGO["SW"][MACSW]["ports"][portN]["poe"]+"; nameSW:{}".format(nameSW)+"  poe:"+poe+"  newPort:"+newPort)

							if dev.states["SW_Port"] != newPort:
								self.addToStatesUpdateList(dev.id,"SW_Port", newPort)


						props=dev.pluginProps

						newd = False
						devidd = "{}".format(dev.id)
						if ip != "":
							if dev.states["ipNumber"] != ip:
								self.addToStatesUpdateList(dev.id,"ipNumber", ip)
							self.MAC2INDIGO[xType][MAC]["ipNumber"] = ip
						self.MAC2INDIGO[xType][MAC]["age"+suffixN] = age
						if dev.states["name"] != nameSW and nameSW !="empty":
							self.addToStatesUpdateList(dev.id,"name", nameSW)

						if "vlan" in dev.states and dev.states["vlan"] != vlan:
							self.addToStatesUpdateList(dev.id,"vlan", vlan)


						newStatus = "up"
						oldStatus = dev.states["status"]
						oldUp	  = self.MAC2INDIGO[xType][MAC]["upTime" + suffixN]
						self.MAC2INDIGO[xType][MAC]["upTime" + suffixN] = "{}".format(newUp)
						if "useWhatForStatus" in props and props["useWhatForStatus"] in ["SWITCH","OptDhcpSwitch"]:
							if self.decideMyLog("Dict", MAC=MAC): self.indiLOG.log(10,"DC-SW-01    {:15s} {} {}; oldStatus:{}; IP:{}; AGE:{}; newUp:{}; oldUp:{} hostN:{}".format(useIP, MAC, dev.name, oldStatus, ip, age, newUp, oldUp, nameSW))
							if oldUp ==	 newUp and oldStatus =="up":
								if "useupTimeforStatusSWITCH" in props and props["useupTimeforStatusSWITCH"] :
									if "usePingDOWN" in props and props["usePingDOWN"]	and self.sendWakewOnLanAndPing(MAC,dev.states["ipNumber"], props=props, calledFrom ="doSWITCHdictClients") == 0:
										if self.decideMyLog("DictDetails", MAC=MAC): self.indiLOG.log(10,"DC-SW-1    {} reset timer for status up  notuptime const	but answers ping".format(MAC))
										self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
									else:
										if self.decideMyLog("DictDetails", MAC=MAC): self.indiLOG.log(10,"DC-SW-2    {} SW DICT network_table , Uptime not changed, continue expiration timer".format(MAC))
								else: # will only expired if not in list anymore
									if "usePingDOWN" in props and props["usePingDOWN"]	 and status !="up" and self.sendWakewOnLanAndPing(MAC,dev.states["ipNumber"], props=props, calledFrom ="doSWITCHdictClients") != 0:
										if self.decideMyLog("DictDetails", MAC=MAC): self.indiLOG.log(10,"DC-SW-3    {} SW DICT network_table , but does not answer ping, continue expiration timer".format(MAC))
									else:
										if self.decideMyLog("DictDetails", MAC=MAC): self.indiLOG.log(10,"DC-SW-4    {} reset timer for status up     answers ping in  DHCP list".format(MAC))
										self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()


							if oldUp != newUp:
								if "usePingUP" in props and props["usePingUP"] and self.sendWakewOnLanAndPing(MAC,dev.states["ipNumber"], props=props, calledFrom ="doSWITCHdictClients") != 0:
									if self.decideMyLog("Dict", MAC=MAC): self.indiLOG.log(10,"DC-SW-5    {} SW DICT network_table , but does not answer ping, continue expiration timer".format(MAC))
								else:
									self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
									if self.decideMyLog("Dict", MAC=MAC): self.indiLOG.log(10,"DC-SW-6    {} SW DICT network_tablerestart exp timer ".format(MAC))

						if self.updateDescriptions:
							oldIPX = dev.description.split("-")
							if ipx !="" and (oldIPX[0] != ipx or ( (dev.description != ipx + "-" + nameSW or len(dev.description) < 5) and nameSW !="empty"  and  (dev.description).find("=WiFi") ==-1 )) :
								if oldIPX[0] != ipx and oldIPX[0] !="":
									indigo.variable.updateValue("Unifi_With_IPNumber_Change","{}/{}/{}/{}".format(dev.name, dev.states["MAC"], oldIPX[0], ipx) )
								dev.description = ipx + "-" + nameSW
								if self.decideMyLog("DictDetails", MAC=MAC): self.indiLOG.log(10,"DC-SW-7    updating description for {}  to....{}".format(dev.name, dev.description) )
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
								props			={"useWhatForStatus":"SWITCH","useupTimeforStatusSWITCH":"",isType:True})

						except	Exception as e:
							if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
							continue

						self.setupStructures(xType, dev, MAC)
						self.addToStatesUpdateList(dev.id,"SW_Port", "")
						self.MAC2INDIGO[xType][MAC]["age"+suffixN] = age
						self.MAC2INDIGO[xType][MAC]["upTime"+suffixN] = newUp
						self.setupBasicDeviceStates(dev, MAC, xType, ip, "", "", " status up          SWITCH DICT new Device", "STATUS-SW")
						self.MAC2INDIGO[xType][MAC]["inList"+suffixN] = 1
						indigo.variable.updateValue("Unifi_New_Device","{}/{}/{}".format(dev.name, MAC, ipx) )
						self.executeUpdateStatesList()
						dev = indigo.devices[dev.id]
						self.setupStructures(xType, dev, MAC)

			self.doInList(suffixN)
			self.executeUpdateStatesList()



		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		self.unsetBlockAccess("doSWITCHdict")

		return

	####-----------------	 ---------
	def doGWHost_table(self, gwDict, ipNumber):

		self.setBlockAccess("doGWHost_table")


		try:
			devType = "UniFi"
			isType	= "isUniFi"
			devName = "UniFi"
			suffixN = "DHCP"
			xType	= "UN"

			###########	 do DHCP devices

			if "network_table" not in gwDict:
				if self.decideMyLog("Logic"): self.indiLOG.log(10,"DC-DHCP-E0 network_table not in dict {}".format(gwDict[0:100]) )
				return


			host_table = ""
			for item  in gwDict["network_table"]:
				if "host_table" not in item: continue
				host_table = item["host_table"]
				break
			if host_table == "":
				if "host_table" not in gwDict["network_table"]:
					if self.decideMyLog("Logic"): self.indiLOG.log(10,"DC-DHCP-E1 no DHCP in gwateway ?.. skipping info ".format(gwDict["network_table"][0:100]) )
					return # DHCP not enabled on gateway, no info from GW available

			if "connect_request_ip" in gwDict:
				ipNumber = gwDict["connect_request_ip"]
			else:
				ipNumber = "            "

			MAC = ""
			for MAC in self.MAC2INDIGO[xType]:
				self.MAC2INDIGO[xType][MAC]["inList"+suffixN] = 0

			if MAC == "":
				return 

			if self.decideMyLog("DictDetails", MAC=MAC): self.indiLOG.log(10,"DC-DHCP-0  host_table len:{}     {}".format( len(host_table), host_table[0:100]) )
			if len(host_table) > 0:
				for item in host_table:



					if "ip" in item:  ip = item["ip"]
					else:			  ip = ""
					MAC					 = item["mac"]
					if self.testIgnoreMAC(MAC, fromSystem="GW-Dict"): continue
					age					 = item["age"]
					uptime				 = item["uptime"]
					new					 = True
					if MAC in self.MAC2INDIGO[xType]:
						try:
							dev = indigo.devices[self.MAC2INDIGO[xType][MAC]["devId"]]
							if dev.deviceTypeId != devType: 1 / 0
							new = False
							self.MAC2INDIGO[xType][MAC]["inList" + suffixN] = 1
						except:
							if self.decideMyLog("Logic", MAC=MAC): self.indiLOG.log(10,"DC-DHCP-E1 {}  {} wrong {}".format(MAC, self.MAC2INDIGO[xType][MAC], devType) )
							for dev in indigo.devices.iter("props."+isType):
								if "MAC" not in dev.states: continue
								if dev.states["MAC"] != MAC: continue
								self.setupStructures(xType, dev, MAC, init=False)
								self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
								self.MAC2INDIGO[xType][MAC]["inList" + suffixN] = 1
								new = False
								break

					if not new:
							if self.decideMyLog("DictDetails", MAC=MAC): self.indiLOG.log(10,"DC-DHCP-1  {:15s}  {}; {}; ip:{}; age:{}; uptime:{}".format(ipNumber, MAC, dev.name,ip, age, uptime))

							self.MAC2INDIGO[xType][MAC]["inList"+suffixN] = True

							props = dev.pluginProps
							new = False
							if MAC != dev.states["MAC"]:
								self.addToStatesUpdateList(dev.id,"MAC", MAC)
							if ip != "":
								if ip != dev.states["ipNumber"]:
									self.addToStatesUpdateList(dev.id,"ipNumber", ip)
								self.MAC2INDIGO[xType][MAC]["ipNumber"] = ip

							newStatus = "up"
							if "useWhatForStatus" in props and props["useWhatForStatus"] in ["DHCP","OptDhcpSwitch","WiFi,DHCP"]:

								if "useAgeforStatusDHCP" in props and props["useAgeforStatusDHCP"] != "-1"     and float(age) > float( props["useAgeforStatusDHCP"]):
										if dev.states["status"] == "up":
											if "usePingDOWN" in props and props["usePingDOWN"] and self.sendWakewOnLanAndPing(MAC,dev.states["ipNumber"], props=props, calledFrom ="doGWHost_table") == 0:  # did  answer
												if self.decideMyLog("DictDetails", MAC=MAC): self.indiLOG.log(10,"    {} restart exptimer DICT network_table AGE>max:{}, but answers ping, exp-time left:{:5.1f}".format(MAC, props["useAgeforStatusDHCP"], self.getexpT(props) -(time.time()-self.MAC2INDIGO[xType][MAC]["lastUp"]) ))
												self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
												newStatus = "up"
											else:
												if self.decideMyLog("DictDetails", MAC=MAC): self.indiLOG.log(10,"    {} set timer for status down GW DICT network_table AGE>max:{}".format(MAC, props["useAgeforStatusDHCP"]))
												newStatus = "startDown"

								else: # good data, should be up
									if "usePingUP" in props and props["usePingUP"] and dev.states["status"] == "up" and self.sendWakewOnLanAndPing(MAC,dev.states["ipNumber"], props=props, calledFrom ="doGWHost_table") == 1:	# did not answer
											self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time() - self.getexpT(props) # down immediately
											self.setImageAndStatus(dev, "down",oldStatus=dev.states["status"], ts=time.time(), level=1, text1= dev.name.ljust(30) + "set timer for status down    ping does not answer", iType="DC-DHCP-4  ",reason="DICT "+suffixN+" up")
											newStatus = "down"
									elif dev.states["status"] != "up":
											self.setImageAndStatus(dev, "up",oldStatus=dev.states["status"], ts=time.time(), level=1, text1= dev.name.ljust(30) + " status up   GW DICT network_table", iType="DC-DHCP-4  ",reason="DICT "+suffixN+" up")
											newStatus = "up"

								if newStatus == "up":
									self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()

							self.MAC2INDIGO[xType][MAC]["age"+suffixN]		= age
							self.MAC2INDIGO[xType][MAC]["upTime"+suffixN]	= uptime

							if self.updateDescriptions:
								oldIPX = dev.description.split("-")
								ipx = self.fixIP(ip)
								if ipx != "" and oldIPX[0] != ipx and oldIPX[0] != "":
									indigo.variable.updateValue("Unifi_With_IPNumber_Change", "{}/{}/{}/{}".format(dev.name, dev.states["MAC"], oldIPX[0], ipx) )
									oldIPX[0] = ipx
									dev.description = "-".join(oldIPX)
									if self.decideMyLog("DictDetails", MAC=MAC): self.indiLOG.log(10,"updating description for {}  to....{}".format(dev.name, dev.description) )
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
						except	Exception as e:
							if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
							continue

						self.setupStructures(xType, dev, MAC)
						self.MAC2INDIGO[xType][MAC]["age"+suffixN]			= age
						self.MAC2INDIGO[xType][MAC]["upTime"+suffixN]		= uptime
						self.MAC2INDIGO[xType][MAC]["inList"+suffixN]		= True
						self.setupBasicDeviceStates(dev, MAC, xType, ip, "", "", " status up    GW DICT  new device","DC-DHCP-3   ")
						self.executeUpdateStatesList()
						dev = indigo.devices[dev.id]
						self.setupStructures(xType, dev, MAC)
						indigo.variable.updateValue("Unifi_New_Device","{}/{}".format(dev.name, MAC) )



			## now check if device is not in dict, if not ==> initiate status --> down
			self.doInList(suffixN)
			self.executeUpdateStatesList()


		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		self.unsetBlockAccess("doGWHost_table")
		
		return


	####-----------------	 ---------
	def doGWDvi_stats(self, gwDict, ipNumber):

		self.setBlockAccess("doGWDvi_stats")


		try:
			devType = "UniFi"
			isType	= "isUniFi"
			devName = "UniFi"
			suffixN = "DHCP"
			xType	= "UN"

			###########	 do DHCP devices

			### UDM does not have DHCP info use DPI info, cretae an artificial age # by adding rx tx packets
			if self.unifiControllerType.find("UDM") > -1: key = "dpi_stats"
			else:										   key = "dpi-stats"
			if key not in gwDict or gwDict[key] == []: 
				if False and self.decideMyLog("UDM"):  self.indiLOG.log(10,"DC-DPI   dpi-stats not in dict or empty " )
				return 
			dpi_table =[]
			xx = {}
			for dd in gwDict:
				if len(dd) < 1: continue
				if "ip" not in dd: 		
					#if self.decideMyLog("UDM"):  self.indiLOG.log(10,"DC-DPI    \"ip\" not in gWDict" )
					continue
				if type(dd) != type({}): 
					#if self.decideMyLog("UDM"):  self.indiLOG.log(10,"DC-DPI     dict in gwDict :".format(gwDict) )
					continue
				xx = {"age": 99999999999,
					  "authorized": False,
					  "ip": dd["ip"],
					  "mac": dd["mac"],
					  "tx_bytes": 0,
					  "tx_packets": 0,
					  "uptime": 0}
				for yy in gwDict[key]["stats"]:
					xx["rx_packets"] += yy["rx_packets"]
					xx["tx_packets"] += yy["tx_packets"]
				if xx["rx_packets"]  + xx["tx_packets"]  > 0:
					xx["age"] 	 = 0
					xx["uptime"] = int(time.time()*1000 - float(gwDict["initialized"]))
					dpi_table.append(xx)

			for item in dpi_table:
					if "ip" in item: ip = item["ip"]
					else:			  ip = ""
					MAC					 = item["mac"]
					if self.testIgnoreMAC(MAC, fromSystem="GW-Dict"): continue
					age					 = item["age"]
					uptime				 = item["uptime"]
					new					 = True
					if MAC in self.MAC2INDIGO[xType]:
						try:
							dev = indigo.devices[self.MAC2INDIGO[xType][MAC]["devId"]]
							if dev.deviceTypeId != devType: 1 / 0
							new = False
							self.MAC2INDIGO[xType][MAC]["inList" + suffixN] = 1
						except:
							if self.decideMyLog("Logic", MAC=MAC): self.indiLOG.log(10,"DC-DPI-E1  {}     {} wrong devType:{}".format(MAC, self.MAC2INDIGO[xType][MAC], devType) )
							for dev in indigo.devices.iter("props."+isType):
								if "MAC" not in dev.states: continue
								if dev.states["MAC"] != MAC: continue
								self.setupStructures(xType, dev, MAC, init=False)
								self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
								self.MAC2INDIGO[xType][MAC]["inList" + suffixN] = 1
								new = False
								break

					if not new:
							if self.decideMyLog("DictDetails", MAC=MAC): self.indiLOG.log(10,"DC-DPI-1  {} {}  {} ip:{} age:{} uptime:{}".format(ipNumber, MAC, dev.name, ip, age, uptime))

							self.MAC2INDIGO[xType][MAC]["inList"+suffixN] = True

							props = dev.pluginProps
							new = False
							if MAC != dev.states["MAC"]:
								self.addToStatesUpdateList(dev.id,"MAC", MAC)
							if ip != "":
								if ip != dev.states["ipNumber"]:
									self.addToStatesUpdateList(dev.id,"ipNumber", ip)
								self.MAC2INDIGO[xType][MAC]["ipNumber"] = ip

							newStatus = "up"
							if "useWhatForStatus" in props and props["useWhatForStatus"] in ["DHCP","OptDhcpSwitch","WiFi,DHCP"]:

								if "useAgeforStatusDHCP" in props and props["useAgeforStatusDHCP"] != "-1"     and float(age) > float( props["useAgeforStatusDHCP"]):
										if dev.states["status"] == "up":
											if "usePingDOWN" in props and props["usePingDOWN"] and self.sendWakewOnLanAndPing(MAC,dev.states["ipNumber"], props=props, calledFrom = "doGWHost_table") == 0:  # did  answer
												if self.decideMyLog("DictDetails", MAC=MAC): self.indiLOG.log(10,"DC-DPI-2   {} ==> restart exptimer DICT network_table AGE>max, but answers ping {}, exp-time left:{:5.1f}".format(MAC,props["useAgeforStatusDHCP"], self.getexpT(props) -(time.time()-self.MAC2INDIGO[xType][MAC]["lastUp"])))
												self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
												newStatus = "up"
											else:
												if self.decideMyLog("DictDetails", MAC=MAC): self.indiLOG.log(10,"DC-DPI-3   {} set timer for status down GW DICT network_table AGE>max:" .format(MAC,props["useAgeforStatusDHCP"]))
												newStatus = "startDown"

								else: # good data, should be up
									if "usePingUP" in props and props["usePingUP"] and dev.states["status"] == "up" and self.sendWakewOnLanAndPing(MAC,dev.states["ipNumber"], props=props, calledFrom ="doGWHost_table") == 1:	# did not answer
											self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time() - self.getexpT(props) # down immediately
											self.setImageAndStatus(dev, "down",oldStatus=dev.states["status"], ts=time.time(), level=1, text1= dev.name.ljust(30) + "set timer for status down    ping does not answer", iType="DC-DHCP-4  ",reason="DICT "+suffixN+" up")
											newStatus = "down"
									elif dev.states["status"] != "up":
											self.setImageAndStatus(dev, "up",oldStatus=dev.states["status"], ts=time.time(), level=1, text1= dev.name.ljust(30) + " status up  	GW DICT network_table", iType="DC-DHCP-4  ",reason="DICT "+suffixN+" up")
											newStatus = "up"

								if newStatus == "up":
									self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()

							self.MAC2INDIGO[xType][MAC]["age"+suffixN]		= age
							self.MAC2INDIGO[xType][MAC]["upTime"+suffixN]	= uptime

							if self.updateDescriptions:
								oldIPX = dev.description.split("-")
								ipx = self.fixIP(ip)
								if ipx!="" and oldIPX[0] != ipx and oldIPX[0] !="":
									indigo.variable.updateValue("Unifi_With_IPNumber_Change","{}/{}/{}/{}".format(dev.name, dev.states["MAC"], oldIPX[0], ipx) )
									oldIPX[0] = ipx
									dev.description = "-".join(oldIPX)
									if self.decideMyLog("DictDetails", MAC=MAC): self.indiLOG.log(10,"DC-DPI-4   updating description for {}  to: {}".format(dev.name, dev.description) )
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
						except	Exception as e:
							if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
							continue

						self.setupStructures(xType, dev, MAC)
						self.MAC2INDIGO[xType][MAC]["age"+suffixN]			= age
						self.MAC2INDIGO[xType][MAC]["upTime"+suffixN]		= uptime
						self.MAC2INDIGO[xType][MAC]["inList"+suffixN]		= True
						self.setupBasicDeviceStates(dev, MAC, xType, ip, "", "", " status u         GW DICT  new device","DC-DPI-3   ")
						self.executeUpdateStatesList()
						dev = indigo.devices[dev.id]
						self.setupStructures(xType, dev, MAC)
						indigo.variable.updateValue("Unifi_New_Device","{}/{}".format(dev.name, MAC) )



			## now check if device is not in dict, if not ==> initiate status --> down
			self.doInList(suffixN)
			self.executeUpdateStatesList()


		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		self.unsetBlockAccess("doGWDvi_stats")
		
		return




	####-----------------	 ---------
	def doWiFiCLIENTSdict(self,adDict, GHz, ipNDevice, apN, ipNumber):
		try:
	

			if len(adDict) == 0:
				return

			self.setBlockAccess("doWiFiCLIENTSdict")

			if self.decideMyLog("Dict") or self.debugDevs["AP"][int(apN)]: self.indiLOG.log(10,"DC-WF-00   {:13s}#{} ... vap_table..[sta_table]: {}".format(ipNumber,apN, adDict) )

			try:
				devType = "UniFi"
				isType	= "isUniFi"
				devName = "UniFi"
				suffixN = "WiFi"
				xType	= "UN"
				clientHostNames = ""
				for MAC in self.MAC2INDIGO[xType]:
					if "AP" not in self.MAC2INDIGO[xType][MAC]:
						self.indiLOG.log(30,"DC-WF-ER   {} # type:{} is not properly defined, please check config  and fix, then restart plugin".format(MAC, xType) )
						continue
					if self.MAC2INDIGO[xType][MAC]["AP"]  != ipNumber: continue
					if self.MAC2INDIGO[xType][MAC]["GHz"] != GHz:		continue
					self.MAC2INDIGO[xType][MAC]["inList"+suffixN] = 0


				for ii in range(len(adDict)):

					new				= True
					if "mac" not in adDict[ii] : continue
					MAC				= adDict[ii]["mac"]
					if self.testIgnoreMAC(MAC, fromSystem="WF-Dict"): continue
					if "ip" not in adDict[ii]: continue
					ip				= adDict[ii]["ip"]
					txRate			= "{}".format(adDict[ii]["tx_rate"])
					rxRate			= "{}".format(adDict[ii]["rx_rate"])
					rxtx			= rxRate+"/"+txRate+" [Kb]"
					signal			= "{}".format(adDict[ii]["signal"])
					noise			= "{}".format(adDict[ii]["noise"])
					idletime		= "{}".format(adDict[ii]["idletime"])
					try:state		= format(int(adDict[ii]["state"]), '08b')	## not in controller
					except: state	= ""
					newUpTime		= "{}".format(adDict[ii]["uptime"])
					try:
						nameCl		= adDict[ii]["hostname"].strip()
					except:
						nameCl		= ""
					if nameCl !="": clientHostNames += nameCl+"; "
					powerMgmt = "{}".format(adDict[ii]["state_pwrmgt"])
					ipx = self.fixIP(ip)
					#if	 MAC == "54:9f:13:3f:95:25":

					if MAC in self.MAC2INDIGO[xType]:
						try:
							dev = indigo.devices[self.MAC2INDIGO[xType][MAC]["devId"]]
							if dev.deviceTypeId != devType: 1/0
							new = False
							self.MAC2INDIGO[xType][MAC]["AP"]		   		 = ipNumber
							self.MAC2INDIGO[xType][MAC]["inList" + suffixN] = 1
							self.MAC2INDIGO[xType][MAC]["GHz"]		   		 = GHz
						except:
							if self.decideMyLog("Logic", MAC=MAC): self.indiLOG.log(10,"{}; {} has wrong devType:{}".format(MAC, self.MAC2INDIGO[xType][MAC], devType) )
							for dev in indigo.devices.iter("props."+isType):
								if "MAC" not in dev.states: continue
								if dev.states["MAC"] != MAC: continue
								self.setupStructures(xType, dev, MAC, init=False)
								self.MAC2INDIGO[xType][MAC]["lastUp"] 			 =  time.time()
								self.MAC2INDIGO[xType][MAC]["GHz"] 			 = GHz
								self.MAC2INDIGO[xType][MAC]["AP"] 				 = ipNumber
								self.MAC2INDIGO[xType][MAC]["inList" + suffixN] = 1
								new = False
								break
					else:
						pass


					if not new:
							props=dev.pluginProps
							devidd = "{}".format(dev.id)

							oldAssociated =	 dev.states["AP"].split("#")[0]
							newAssociated =	 ipNumber
							try:	 oldIdle =	int(self.MAC2INDIGO[xType][MAC]["idleTime" + suffixN])
							except:	 oldIdle = 0

							# this is for the case when device switches betwen APs and the old one is still sending.. ignore that one
							if dev.states["AP"].split("-")[0] != ipNumber:
								try:
									if oldIdle < 600 and int(idletime) > oldIdle: 
										if self.decideMyLog("DictDetails", MAC=MAC) or self.decideMyLog("Logic") or self.debugDevs["AP"](int[apN]):
											self.indiLOG.log(10,"DC-WF-old  {:15s} oldAP:{}; {};  idletime old:{}/new:{} reject entry, still managed by old AP, not switched yet.. expired?".format(ipNumber, dev.states["AP"], MAC, oldIdle, idletime ))
										continue # oldIdle < 600 is to catch expired devices
								except:
									pass

							if dev.states["AP"] != ipNumber+"-#{}".format(apN):
								self.addToStatesUpdateList(dev.id,"AP", ipNumber+"-#{}".format(apN))

							self.MAC2INDIGO[xType][MAC]["inList"+suffixN] = 1

							if ip != "":
								if dev.states["ipNumber"] != ip:
									self.addToStatesUpdateList(dev.id,"ipNumber", ip)
								self.MAC2INDIGO[xType][MAC]["ipNumber"] = ip

							if dev.states["name"] != nameCl and nameCl !="":
								self.addToStatesUpdateList(dev.id,"name", nameCl)

							if dev.states["GHz"] != GHz:
								self.addToStatesUpdateList(dev.id,"GHz", GHz)

							if dev.states["powerMgmt"+suffixN] != powerMgmt:
								self.addToStatesUpdateList(dev.id,"powerMgmt"+suffixN, powerMgmt)

							if dev.states["rx_tx_Rate"+suffixN] != rxtx:
								self.addToStatesUpdateList(dev.id,"rx_tx_Rate"+suffixN, rxtx)

							if dev.states["noise"+suffixN] != noise:
								uD = True
								try:
									if abs(int(dev.states["noise"+suffixN])- int(noise)) < 3:
										uD=	 False
								except: pass
								if uD: self.addToStatesUpdateList(dev.id,"noise"+suffixN, noise)

							if dev.states["signal"+suffixN] != signal:
								uD = True
								try:
									if abs(int(dev.states["signal"+suffixN])- int(signal)) < 3:
										uD=	 False
								except: pass
								if uD: self.addToStatesUpdateList(dev.id,"signal"+suffixN, signal)

							try:	oldUpTime = "{}".format(int(self.MAC2INDIGO[xType][MAC]["upTime"+suffixN]))
							except: oldUpTime = "0"
							self.MAC2INDIGO[xType][MAC]["upTime"+suffixN] = newUpTime

							if dev.states["state" + suffixN] != state:
								self.addToStatesUpdateList(dev.id,"state" + suffixN, state)

							if dev.states["AP"].split("-")[0] != ipNumber:
								self.addToStatesUpdateList(dev.id,"AP", ipNumber+"-#{}".format(apN) )

							if idletime != "":
								self.MAC2INDIGO[xType][MAC]["idleTime" + suffixN] =  idletime

							oldStatus = dev.states["status"]

							if self.updateDescriptions:
								oldIPX = dev.description.split("-")
								if oldIPX[0] != ipx or (dev.description != ipx + "-" + nameCl+"=WiFi" or len(dev.description) < 5):
									if oldIPX[0] != ipx and oldIPX[0] !="":
										indigo.variable.updateValue("Unifi_With_IPNumber_Change","{}/{}/{}/{}".format(dev.name, dev.states["MAC"], oldIPX[0], ipx) )
									if len(oldIPX) < 2:
										oldIPX.append(nameCl.strip("-"))
									elif len(oldIPX) == 2 and oldIPX[1] == "":
										if nameCl != "":
											oldIPX[1] = nameCl.strip("-")
									oldIPX[0] = ipx
									newDescr = "-".join(oldIPX)
									if (dev.description).find("=WiFi")==-1:
										dev.description = newDescr+"=WiFi"
									else:
										dev.description = newDescr
									dev.replaceOnServer()

							expTime = self.getexpT(props)
							if self.decideMyLog("DictDetails", MAC=MAC) or self.decideMyLog("Logic") or self.debugDevs["AP"][int(apN)]:
								self.indiLOG.log(10,"DC-WF-01   {:15s}  {}; {}; ip:{}; GHz:{}; txRate:{}; rxR:{}; new-oldUPtime:{}-{}; idletime:{}; signal:{}; hostN:{}; powerMgmt:{}; old/new assoc {}/{}; curr status:{}".format(ipNumber, MAC, dev.name, ip, GHz, txRate, rxRate,  newUpTime, oldUpTime, idletime, signal, nameCl, powerMgmt, oldAssociated.split("-")[0], newAssociated, dev.states["status"]))


							# check what is used to determine up / down, make WiFi a priority
							if ( "useWhatForStatus" not in	props ) or ( "useWhatForStatus" in props and props["useWhatForStatus"].find("WiFi") == -1 ):
								try:
									if time.time() - time.mktime(datetime.datetime.strptime(dev.states["created"], "%Y-%m-%d %H:%M:%S").timetuple()) <	 60:
										props = dev.pluginProps
										props["useWhatForStatus"]		= "WiFi,DHCP"
										props["useWhatForStatusWiFi"]	= "Optimized"
										dev.replacePluginPropsOnServer(props)
										props = dev.pluginProps
								except:
									self.addToStatesUpdateList(dev.id,"created", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
									props = dev.pluginProps
									props["useWhatForStatus"]		= "WiFi,DHCP"
									props["useWhatForStatusWiFi"]	= "Optimized"
									dev.replacePluginPropsOnServer(props)
									props = dev.pluginProps

							if "useWhatForStatus" in props and props["useWhatForStatus"].find("WiFi") > -1:

								if "useWhatForStatusWiFi" not in props or ("useWhatForStatusWiFi" in props and	props["useWhatForStatusWiFi"] !="FastDown"):

									try:	 newUpTime = int(newUpTime)
									except:	 newUpTime = int(oldUpTime)
									try:
										idleTimeMaxSecs	 = float(props["idleTimeMaxSecs"])
									except:
										idleTimeMaxSecs = 5

									if "useWhatForStatusWiFi" in props and ( props["useWhatForStatusWiFi"] == "Optimized"):
										if self.decideMyLog("DictDetails", MAC=MAC) or self.decideMyLog("Logic", MAC=MAC): self.indiLOG.log(10,"DC-WF-o1   {:15s}  {}; .. using optimized for status; idle uptimes {} < {} or uptime (new){} != {}(Old)" .format(ipNumber, MAC, idletime, idleTimeMaxSecs, newUpTime, oldUpTime))

										if oldStatus == "up":
											if (  float(newUpTime) != float(oldUpTime)	) or  ( float(idletime)  < idleTimeMaxSecs ):
													if self.decideMyLog("DictDetails", MAC=MAC): self.indiLOG.log(10,"DC-WF-o2R  {:15s}  {}; ==> restart exptimer use idleTime, exp-time left:{:5.1f}".format(ipNumber, MAC, expTime -(time.time()-self.MAC2INDIGO[xType][MAC]["lastUp"])))
													self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
											else:
												if ( oldAssociated.split("-")[0] != newAssociated ): # ignore new AP
													if self.decideMyLog("Logic", MAC=MAC): self.indiLOG.log(10,"DC-WF-o3R  {:15s}  {}; ==> restart exptimer, associated to new AP:{} from:{}, exp-time left:{:5.1f}".format(ipNumber, MAC, oldAssociated, newAssociated, expTime -(time.time()-self.MAC2INDIGO[xType][MAC]["lastUp"])) )
													self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
												else: # same old
													if self.decideMyLog("DictDetails", MAC=MAC): self.indiLOG.log(10,"DC-WF-o4DN {:15s}  {}; set timer to expire in 10 secs use idleTime/uptime".format(ipNumber, MAC))
													self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()- expTime + 10

										else: # old = down
											if ( float(newUpTime) != float(oldUpTime) ) or (  float(idletime) <= idleTimeMaxSecs ):
												if self.decideMyLog("DictDetails", MAC=MAC): self.indiLOG.log(10,"DC-WF-o5   {:15s}  {}; status Down->up; ==> restart exptimer, use idleTime/uptime, exp-time left:{:5.1f}".format(ipNumber, MAC, expTime -(time.time()-self.MAC2INDIGO[xType][MAC]["lastUp"]) ))
												self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
												self.setImageAndStatus(dev, "up",oldStatus=oldStatus,ts=time.time(),reason="DICT "+suffixN+" "+ipNumber+" up Optimized")
											else:
												if ( oldAssociated.split("-")[0] != newAssociated ): # ignore new AP
													if self.decideMyLog("Logic", MAC=MAC): self.indiLOG.log(10,"DC-WF-o6R  {:15s}  {}; ==> restart exptimer, status up new AP; use idleTime/uptime, exp-time left:{:5.1f}".format(ipNumber, MAC, expTime -(time.time()-self.MAC2INDIGO[xType][MAC]["lastUp"])))
													self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()


									elif "useWhatForStatusWiFi" in props and (props["useWhatForStatusWiFi"] =="IdleTime" ):
										if self.decideMyLog("DictDetails", MAC=MAC) or self.decideMyLog("Logic", MAC=MAC): self.indiLOG.log(10,"DC-WF-i0-  {:15s}  {};.  IdleTime..  checking IdleTime {} < {}  old/new associated {}/{}".format(ipNumber, MAC,idletime, idleTimeMaxSecs, oldAssociated.split("-")[0], newAssociated)) 
					
										if float(idletime)	> idleTimeMaxSecs and oldStatus == "up":
											if ( oldAssociated.split("-")[0] == newAssociated ):
												if "usePingDOWN" in props and props["usePingDOWN"] and self.sendWakewOnLanAndPing(MAC,dev.states["ipNumber"], props=props, calledFrom ="doWiFiCLIENTSdict") ==0:
														if self.decideMyLog("DictDetails"): self.indiLOG.log(10,"DC-WF-i1R  {:15s}  {}; reset exptimer, ping was test up, exp-time left:{:5.1f}".format(ipNumber, MAC, expTime -(time.time()-self.MAC2INDIGO[xType][MAC]["lastUp"])) )
														self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
												else:
													if self.decideMyLog("DictDetails", MAC=MAC): self.indiLOG.log(10,"DC-WF-i2DN {:15s}  {}; status down in 10 secs".format(ipNumber, MAC))
													self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()- expTime + 10
											else:
												if self.decideMyLog("DictDetails", MAC=MAC): self.indiLOG.log(10,"DC-WF-i3R  {:15s}  {}; status up new AP use IdleTime, exp-time left:{:5.1f}".format(ipNumber, MAC, expTime -(time.time()-self.MAC2INDIGO[xType][MAC]["lastUp"])))
												self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()

										elif float(idletime)  <= idleTimeMaxSecs:
											if self.decideMyLog("DictDetails", MAC=MAC): self.indiLOG.log(10,"DC-WF-i4R  {:15s}  {}; ==> restart exptimer, use IdleTime, exp-time left:{:5.1f}".format(ipNumber, MAC, expTime -(time.time()-self.MAC2INDIGO[xType][MAC]["lastUp"])))
											self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
											if oldStatus != "up":
												self.setImageAndStatus(dev, "up",oldStatus=oldStatus,ts=time.time(),reason="DICT "+ipNumber+" "+suffixN+" up IdleTime")
												if self.decideMyLog("Logic", MAC=MAC): self.indiLOG.log(10,"DC-WF-i5R  {:15s}  {}; status up, use IdleTime".format(ipNumber, MAC))


									elif "useWhatForStatusWiFi" in props and (props["useWhatForStatusWiFi"] == "UpTime" ):
										if self.decideMyLog("DictDetails", MAC=MAC) or self.decideMyLog("Logic", MAC=MAC): self.indiLOG.log(10,"DC-WF-U1   .. using  UpTime for status" )
										if newUpTime == oldUpTime and oldStatus == "up":
											if "usePingUP" in props and props["usePingUP"] and self.sendWakewOnLanAndPing(MAC,dev.states["ipNumber"], props=props, calledFrom ="doWiFiCLIENTSdict") == 0:
													if self.decideMyLog("DictDetails", MAC=MAC):self.indiLOG.log(10,"DC-WF-u2   {:15s}   {}; ==> restart exptimer, ping test ok, exp-time left:{:5.1f}".format(ipNumber, MAC, expTime -(time.time()-self.MAC2INDIGO[xType][MAC]["lastUp"])) )
													self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
											else:
												if self.decideMyLog("DictDetails", MAC=MAC): self.indiLOG.log(10,"DC-WF-u3DN {:15s}  {}; let timer expire, Uptime is not changed".format(ipNumber, MAC) )

										elif newUpTime != oldUpTime and oldStatus != "up":
											self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
											self.setImageAndStatus(dev, "up",oldStatus=oldStatus, ts=time.time(), level=1, text1=dev.name.ljust(30) + " "+MAC+" status up  WiFi DICT Uptime",iType="DC-WF-U2",reason="DICT "+ipNumber+" "+suffixN+" up time")

										elif oldStatus == "up":
											if self.decideMyLog("DictDetails", MAC=MAC): self.indiLOG.log(10,"DC-WF-u4   {:15s}  {}; ==> restart exptimer, normal extension, exp-time left:{:5.1f}".format(ipNumber, MAC, expTime -(time.time()-self.MAC2INDIGO[xType][MAC]["lastUp"])))
											self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()


									else:
										self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
										if oldStatus != "up":
											self.setImageAndStatus(dev, "up", oldStatus=oldStatus,level=1, text1=dev.name.ljust(30) + " "+MAC+" status up    WiFi DICT general", iType="DC-WF-UE   ",reason="DICT "+suffixN+" "+ipNumber+" up else")
								continue

								#break

					if new and not self.ignoreNewClients:
						try:
							dev = indigo.device.create(
								protocol		=indigo.kProtocol.Plugin,
								address			=MAC,
								name=			devName + "_" + MAC,
								description		=ipx + "-" + nameCl+"=Wifi",
								pluginId		=self.pluginId,
								deviceTypeId	=devType,
								folder			=self.folderNameIDCreated,
								props			={"useWhatForStatus":"WiFi,DHCP", "useWhatForStatusWiFi":"Expiration",isType:True})
						except	Exception as e:
							if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
							try:
								devName += "_"+( "{}".format(time.time() - int(time.time())) ).split(".")[1] # create random name
								self.indiLOG.log(30,"trying again to create device with different name "+devName)
								dev = indigo.device.create(
									protocol		=indigo.kProtocol.Plugin,
									address			=MAC,
									name			=devName + "_" + MAC,
									description		=ipx + "-" + nameCl+"=Wifi",
									pluginId		=self.pluginId,
									deviceTypeId	=devType,
									folder			=self.folderNameIDCreated,
									props			={"useWhatForStatus":"WiFi,DHCP", "useWhatForStatusWiFi":"Expiration",isType:True})
							except	Exception as e:
								if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
								continue


						self.setupStructures(xType, dev, MAC)
						self.setupBasicDeviceStates(dev, MAC, xType, ip, ipNumber, "", " status up   new Device", "DC-AP-WF-f ")
						self.addToStatesUpdateList(dev.id,"AP", ipNumber+"-#{}".format(apN))
						self.addToStatesUpdateList(dev.id,"powerMgmt"+suffixN, powerMgmt)
						self.addToStatesUpdateList(dev.id,"name", nameCl)
						self.addToStatesUpdateList(dev.id,"rx_tx_Rate" + suffixN, rxtx)
						self.addToStatesUpdateList(dev.id,"signal" + suffixN, signal)
						self.addToStatesUpdateList(dev.id,"noise" + suffixN, noise)
						self.MAC2INDIGO[xType][MAC]["idleTime" + suffixN] = idletime
						self.MAC2INDIGO[xType][MAC]["inList"+suffixN] = 1
						self.addToStatesUpdateList(dev.id,"state"+suffixN, state)
						self.MAC2INDIGO[xType][MAC]["upTime"+suffixN] = newUpTime
						self.executeUpdateStatesList()
						dev = indigo.devices[dev.id]
						self.setupStructures(xType, dev, MAC)
						indigo.variable.updateValue("Unifi_New_Device", "{}/{}/{}".format(dev.name, MAC, ipx) )

					self.executeUpdateStatesList()

				self.doInList(suffixN,wifiIPAP=ipNumber)
				self.executeUpdateStatesList()

			except	Exception as e:
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

			self.unsetBlockAccess("doWiFiCLIENTSdict")
			
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return 	clientHostNames




	####-----------------	 ---------
	## AP devices themselves  DICT
	####-----------------	 ---------
	def doAPdictsSELF(self,apDict, apNumb, ipNDevice, MAC, hostname, ipNumber, clientHostNames):

		self.setBlockAccess("doAPdictsSELF")

		if "model_display" in apDict:  model = (apDict["model_display"])
		else:
			self.indiLOG.log(30,"model_display not in dict doAPdicts")
			model = ""


		devType ="Device-AP"
		isType	= "isAP"
		devName = "AP"
		xType	= "AP"
		try:


			for GHz in ["2","5"]:
				nClients = 0
				essid	  = ""
				radio	  = ""
				tx_power  = ""
				for jj in range(len(apDict["vap_table"])):
					shortC	= apDict["vap_table"][jj]
					if "usage" in shortC: #skip if not wireless
						if shortC["usage"] == "downlink": continue
						if shortC["usage"] == "uplink":	  continue
					channel = shortC["channel"]
					if not( GHz == "2" and channel < 14 or GHz == "5" and channel > 13): continue 
					nClients += shortC["num_sta"]
					essid	  += "{}".format(shortC["essid"]) + "; "
					radio	  =  "{}".format(shortC["radio"])
					tx_power  =  "{}".format(shortC["tx_power"])
					#if self.decideMyLog("Special"): self.indiLOG.log(10,"doAPdictsSELF {} - GHz:{}, sta:{}, essid:{}, radio:{}, tx:{}".format(MAC, GHz, nClients, essid, radio, tx_power)  )

					new = True
					if MAC in self.MAC2INDIGO[xType]:
						try:
							dev = indigo.devices[self.MAC2INDIGO[xType][MAC]["devId"]]
							if dev.deviceTypeId != devType: 1 / 0
							new = False
						except:
							if self.decideMyLog("Logic"): self.indiLOG.log(10, "{}  {} wrong {}".format(MAC, self.MAC2INDIGO[xType][MAC], devType) )
							for dev in indigo.devices.iter("props."+isType):
								if "MAC" not in dev.states: continue
								if dev.states["MAC"] != MAC: continue
								self.MAC2INDIGO[xType][MAC]["devId"] = dev.id
								new = False
								break
					if not new:
							if self.decideMyLog("DictDetails", MAC=MAC): self.indiLOG.log(10,"DC-AP---   {} hostname:{} MAC:{}; GHz:{}; essid:{}; channel:{}; nClients:{}; tx_power:{}; radio:{}".format(ipNumber, hostname, MAC, GHz, essid, channel, nClients, tx_power, radio))
							if "uptime" in apDict and apDict["uptime"] !="":
								if "upSince" in dev.states:
									self.addToStatesUpdateList(dev.id,"upSince", time.strftime("%Y-%d-%m %H:%M:%S", time.localtime(time.time() - apDict["uptime"])) )
							if tx_power != dev.states["tx_power_" + GHz]:
								self.addToStatesUpdateList(dev.id,"tx_power_" + GHz, tx_power)
							if "{}".format(channel) != dev.states["channel_" + GHz]:
								self.addToStatesUpdateList(dev.id,"channel_" + GHz, "{}".format(channel) )
							if essid.strip("; ") != dev.states["essid_" + GHz]:
								self.addToStatesUpdateList(dev.id,"essid_" + GHz, essid.strip("; "))
							if "{}".format(nClients) != dev.states["nClients_" + GHz]:
								self.addToStatesUpdateList(dev.id,"nClients_" + GHz, "{}".format(nClients) )
							if radio != dev.states["radio_" + GHz]:
								self.addToStatesUpdateList(dev.id,"radio_" + GHz, radio)
							self.MAC2INDIGO[xType][MAC]["ipNumber"] = ipNumber
							if ipNumber != dev.states["ipNumber"]:
								self.addToStatesUpdateList(dev.id,"ipNumber", ipNumber)
							if hostname != dev.states["hostname"]:
								self.addToStatesUpdateList(dev.id,"hostname", hostname)
							if dev.states["status"] != "up":
								self.setImageAndStatus(dev, "up", oldStatus=dev.states["status"],ts=time.time(),  level=1, text1=dev.name.ljust(30) + " status up            AP    DICT", reason="AP DICT", iType="STATUS-AP")
							self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
							if dev.states["model"] != model and model != "":
								self.addToStatesUpdateList(dev.id,"model", model)
							if dev.states["apNo"] != apNumb:
								self.addToStatesUpdateList(dev.id,"apNo", apNumb)

							self.setStatusUpForSelfUnifiDev(MAC)


					if new:
						try:
							dev = indigo.device.create(
								protocol		=indigo.kProtocol.Plugin,
								address			=MAC,
								name			=devName + "_" + MAC,
								description		=self.fixIP(ipNumber) + "-" + hostname,
								pluginId		=self.pluginId,
								deviceTypeId	=devType,
								folder			=self.folderNameIDCreated,
								props			={"useWhatForStatus":"",isType:True})
							self.setupStructures(xType, dev, MAC)
							self.setupBasicDeviceStates(dev, MAC, "AP", ipNumber,"", "", " status up            AP DICT  new AP", "STATUS-AP")
							self.addToStatesUpdateList(dev.id,"essid_" + GHz, essid)
							self.addToStatesUpdateList(dev.id,"channel_" + GHz, channel)
							self.addToStatesUpdateList(dev.id,"MAC", MAC)
							self.addToStatesUpdateList(dev.id,"hostname", hostname)
							self.addToStatesUpdateList(dev.id,"nClients_" + GHz, "{}".format(nClients) )
							self.addToStatesUpdateList(dev.id,"radio_" + GHz, radio)
							self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
							self.addToStatesUpdateList(dev.id,"model", model)
							self.addToStatesUpdateList(dev.id,"tx_power_" + GHz, tx_power)
							dev = indigo.devices[dev.id]
							self.setupStructures(xType, dev, MAC)
							self.buttonConfirmGetAPDevInfoFromControllerCALLBACK(valuesDict={})
							indigo.variable.updateValue("Unifi_New_Device", "{}/{}/{}".format(dev.name, MAC, ipNumber) )
						except	Exception as e:
								self.indiLOG.log(40,"", exc_info=True)
								self.indiLOG.log(40,"failed to create dev: {}_{}".format(devName, MAC))
								break

					self.addToStatesUpdateList(dev.id,"clientList_"+GHz+"GHz", clientHostNames[GHz].strip("; "))

			self.executeUpdateStatesList()

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		self.unsetBlockAccess("doAPdictsSELF")
		
		return




	####-----------------	 ---------
	def doGatewaydictSELF(self, gwDict, ipNumber):

		self.setBlockAccess("doGatewaydictSELF")

		try:

			devType  = "gateway"
			devName  = "gateway"
			isType	 = "isGateway"
			xType	 = "GW"
			suffixN	 = "DHCP"
			##########	do gateway params  ###


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

			wanSetup	= "wan1 only"


			if self.decideMyLog("UDM"):  self.indiLOG.log(10,"doGw     unifiControllerType:{}; if.. find UDM >-1:{}".format(self.unifiControllerType, self.unifiControllerType.find("UDM") > -1) )

			if self.unifiControllerType.find("UDM") > -1:   

				if "if_table" not in gwDict: 
					if self.decideMyLog("UDM"): self.indiLOG.log(10,"doGw     UDM gateway \"if_table\" not in gwDict")
					return

				if "ip" in gwDict:	   
					publicIP	   = gwDict["ip"].split("/")[0]
				else:
					if self.decideMyLog("UDM"): self.indiLOG.log(10,"doGw    UDM gateway no public IP number found: \"ip\" not in gwDict")
					return 

				nameList = {}
				for table in gwDict["if_table"]:
					if "name" in table: 
						nameList[table["name"]] = ""
						if "mac" in table:
							nameList[table["name"]] = table["mac"]

				for ethName in nameList:
					for table in gwDict["port_table"]:
						if ethName in table:
							if "mac" in table: 
								nameList[ethName] = mac


				###  wan default
				#  udm-pro
				#   wan  = eth8
				#   wan2 = eth9
				# udm has no second wan on the dedicated Unifi lte modem allows inetrnet backup 
				#   not supported yet , only use wan not wan2
				wan = {}
				for table in gwDict["if_table"]:
					if self.unifiControllerType == "UDM":
						if table["ip"] == publicIP:
							wan = table
							if "speedtest-status" in table:
								wan["latency"] 		= table["speedtest-status"]["latency"]
								wan["xput_down"] 		= table["speedtest-status"]["xput_download"]
								wan["xput_up"] 		= table["speedtest-status"]["xput_upload"]
								wan["speedtest_ping"] 	= table["speedtest-status"]["status_ping"]
							if "name" in table:
								if table["name"] in nameList:
									wan["mac"] =  nameList[table["name"]]
							break

					else:
						if table["name"] == "eth8":
							wan = table
							if "speedtest-status" in table:
								wan["latency"] 		= table["speedtest-status"]["latency"]
								wan["xput_down"] 		= table["speedtest-status"]["xput_download"]
								wan["xput_up"] 		= table["speedtest-status"]["xput_upload"]
								wan["speedtest_ping"] 	= table["speedtest-status"]["status_ping"]
							if "name" in table:
								if table["name"] in nameList:
									wan["mac"] =  nameList[table["name"]]
							break


				wan2 = {}
				if self.unifiControllerType != "UDM": # for UDM pro only
					for table in gwDict["if_table"]:
						if table["name"] == "eth9":
							wan2 = table
							if "speedtest-status" in table:
								wan2["latency"] 			= table["speedtest-status"]["latency"]
								wan2["xput_down"] 			= table["speedtest-status"]["xput_download"]
								wan2["xput_up"] 			= table["speedtest-status"]["xput_upload"]
								wan2["speedtest_ping"] 	= table["speedtest-status"]["status_ping"]
							if "name" in table:
								if table["name"] in nameList:
									wan2["mac"] =  nameList[table["name"]]
							break


				lan = {}
				for table in gwDict["if_table"]:
					if "ip" not in table: continue
					if table["ip"] == ipNumber:
						lan = table
						if "name" in table:
							if table["name"] in nameList:
								wan["mac"] =  nameList[table["name"]]
						break

				if lan == {} or wan == {}: 
					if self.decideMyLog("UDM"): self.indiLOG.log(10,"doGw    UDM gateway nameList:{};  ip:{}; wan:{} / lan:{};  not found in \"if_table\"".format(ipNumber, nameList, lan, wan) )
					return 

				ipNDevice = ipNumber

				if self.decideMyLog("UDM"): self.indiLOG.log(10,"doGw    UDM gateway ip:{}; nameList:{}\nwan:{}\nlan:{}".format(ipNumber, lan, wan, nameList) )


			else: # non UDM type 
				if "if_table"			  not in gwDict: 
					return
				if	  "config_port_table"	  in gwDict: table = "config_port_table"
				elif  "config_network_ports"  in gwDict: table = "config_network_ports"
				else:									 
					return

				if "connect_request_ip" in gwDict:
					ipNDevice = self.fixIP(gwDict["connect_request_ip"])
				if ipNDevice == "": 
					return

				if table == "config_network_ports":
						if "LAN" in gwDict[table]:
							ifnameLAN = gwDict[table]["LAN"]
							for xx in range(len(gwDict["if_table"])):
								if "name" in gwDict["if_table"][xx] and gwDict["if_table"][xx]["name"] == ifnameLAN:
									lan = gwDict["if_table"][xx]
						if "WAN" in gwDict[table]:
							ifnameWAN = gwDict[table]["WAN"]
							for xx in range(len(gwDict["if_table"])):
								if "name" in gwDict["if_table"][xx] and gwDict["if_table"][xx]["name"] == ifnameWAN:
									wan = gwDict["if_table"][xx]
						if "WAN2" in gwDict[table]:
							ifnameWAN2 = gwDict[table]["WAN2"]
							for xx in range(len(gwDict["if_table"])):
								if "name" in gwDict["if_table"][xx] and gwDict["if_table"][xx]["name"] == ifnameWAN2:
									wan2 = gwDict["if_table"][xx]

				elif table == "config_port_table":
					for xx in range(len(gwDict[table])):
						if "name" in gwDict[table][xx] and gwDict[table][xx]["name"].lower() == "lan":
							ifnameLAN = gwDict[table][xx]["ifname"]
							if "name" in gwDict["if_table"][xx] and gwDict["if_table"][xx]["name"] == ifnameLAN:
								lan = gwDict["if_table"][xx]
						if "name" in gwDict[table][xx] and gwDict[table][xx]["name"].lower() =="wan":
							ifnameWAN = gwDict[table][xx]["ifname"]
							if "name" in gwDict["if_table"][xx] and gwDict["if_table"][xx]["name"] == ifnameWAN:
								wan = gwDict["if_table"][xx]
						if "name" in gwDict[table][xx] and gwDict[table][xx]["name"].lower() =="wan2":
							ifnameWAN2 = gwDict[table][xx]["ifname"]
							if "name" in gwDict["if_table"][xx] and gwDict["if_table"][xx]["name"] == ifnameWAN2:
								wan2 = gwDict["if_table"][xx]



			if "model_display" 	in gwDict:						model		= gwDict["model_display"]
			else:
				self.indiLOG.log(10,"model_display not in dict doGatewaydict")

			if "uptime" in wan2:								wan2UpTime = self.convertTimedeltaToDaysHoursMin(wan2["uptime"])
			if "uptime" in wan:									wanUpTime  = self.convertTimedeltaToDaysHoursMin(wan["uptime"])

			if "gateways" 		in wan:							gateways		= "-".join(wan["gateways"])
			if "gateways" 		in wan2:						gateways2		= "-".join(wan2["gateways"])
			if "nameservers" 	in wan:							nameservers		= "-".join(wan["nameservers"])
			if "nameservers" 	in wan2:						nameservers2	= "-".join(wan2["nameservers"])
			if "mac" 			in wan:							MAC				= wan["mac"]
			if "mac" 			in wan2:						MACwan2			= wan2["mac"]


			if "up" in wan:									wanUP  = wan["up"]
			if "up" in wan2:									wan2UP = wan2["up"]

			if   not wanUP and wan2UP: 							wanSetup = "failover"
			elif not wanUP and not wan2UP: 						wanSetup = "wan down"
			elif wanUP     and wan2UP: 							wanSetup = "load balancing"
			else: 												wanSetup = "wan1 only"

			if   "ip" in wan  and wan["ip"]  != "" and wanUP: 	publicIP  = wan["ip"].split("/")[0]
			elif "ip" in wan2 and wan2["ip"] != "" and wan2UP:	publicIP2 = wan2["ip"].split("/")[0]


			#if self.decideMyLog("Special"): self.indiLOG.log(10,"gw dict parameters wan:{}, wan2:{}, macwan:{}, macwan2:{}, publicIP:{}, publicIP2:{}".format(wan,wan2,MAC,MACwan2,publicIP,publicIP2))

			if "mac" in lan:				MAClan			= lan["mac"]
			if "system-stats" in gwDict:
				sysStats = gwDict["system-stats"]
				if "cpu" in sysStats:	 cpuPercent = sysStats["cpu"]
				if "mem" in sysStats:	 memPercent = sysStats["mem"]
				for xx in ["temps"]:
					if xx in sysStats:
						if len(sysStats[xx]) > 0:
							if type(sysStats[xx]) == type({}):
								try:
									for key in sysStats[xx]:
										if   key == "Board (CPU)": temperature_Board_CPU 	= GT.getNumber(sysStats[xx][key])
										elif key == "Board (PHY)":	temperature_Board_PHY 	= GT.getNumber(sysStats[xx][key])
										elif key == "CPU": 		temperature_CPU 		= GT.getNumber(sysStats[xx][key])
										elif key == "PHY": 		temperature_PHY 		= GT.getNumber(sysStats[xx][key])
								except Exception as e:
									self.indiLOG.log(30,"doGatewaydictSELF sysStats[temp]err : {}, key:{}, value:{}, error:{}".format(sysStats[xx], key, sysStats[xx][key], e))
							else:
								temperature	 = GT.getNumber(sysStats[xx])
			for xx in ["temperatures"]:
					if xx in gwDict:
						if len(gwDict[xx]) > 0:
							if type(gwDict[xx]) == type([]):
								try:
									for yy in gwDict[xx]:
										if "name" in yy: 
											if yy["name"] == "Local": 	temperature		 	= GT.getNumber(yy["value"])
											if yy["name"] == "PHY":  	temperature_Board_PHY 	= GT.getNumber(yy["value"])
											if yy["name"] == "CPU": 	temperature_Board_CPU 	= GT.getNumber(yy["value"])
								except:
									self.indiLOG.log(30,"doGatewaydictSELF temperatures[temp]err : {}".format(gwDict[xx]))

			if "speedtest_lastrun" in wan and wan["speedtest_lastrun"] !=0:
											wanSpeedTest	= datetime.datetime.fromtimestamp(float(wan["speedtest_lastrun"])).strftime("%Y-%m-%d %H:%M:%S")
			if "speedtest_lastrun" in wan2 and wan2["speedtest_lastrun"] !=0:
											wan2SpeedTest	= datetime.datetime.fromtimestamp(float(wan2["speedtest_lastrun"])).strftime("%Y-%m-%d %H:%M:%S")
			if "speedtest_ping" in wan:	wanPingTime		= "%4.1f" % wan["speedtest_ping"] + "[ms]"
			if "latency" in wan:			wanLatency		= "%4.1f" % wan["latency"] + "[ms]"
			if "xput_down" in wan:			wanDownload		= "%4.1f" % wan["xput_down"] + "[Mb/S]"
			if "xput_up" in wan:			wanUpload		= "%4.1f" % wan["xput_up"] + "[Mb/S]"

			if "speedtest_ping" in wan2:	wan2PingTime	= "%4.1f" % wan2["speedtest_ping"] + "[ms]"
			if "latency" in wan2:			wan2Latency		= "%4.1f" % wan2["latency"] + "[ms]"
			if "xput_down" in wan2:		wan2Download	= "%4.1f" % wan2["xput_down"] + "[Mb/S]"
			if "xput_up" in wan2:			wan2Upload		= "%4.1f" % wan2["xput_up"] + "[Mb/S]"


			if self.decideMyLog("UDM"): self.indiLOG.log(10,"UDM gateway   MAC:{} -MAClan{}".format(MAC,MAClan))

			isNew = True

			if MAC in self.MAC2INDIGO[xType]:
				try:
					dev = indigo.devices[self.MAC2INDIGO[xType][MAC]["devId"]]
					if dev.deviceTypeId != devType: 1 / 0
					isNew = False
				except:
					if self.decideMyLog("Logic", MAC=MAC): self.indiLOG.log(10,"{}     {} wrong {}" .format(MAC, self.MAC2INDIGO[xType][MAC], devType) )
					for dev in indigo.devices.iter("props."+isType):
						if "MAC" not in dev.states:			continue
						if dev.states["MAC"] != MAC:		continue
						self.MAC2INDIGO[xType][MAC]["devId"] = dev.id
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
						props 			= {"useWhatForStatus":"",isType:True, "failoverSettings":"copypublicIP", "useWhichMAC":"MAClan","enableBroadCastEvents":"0"})
					self.setupStructures(xType, dev, MAC)
					self.setupBasicDeviceStates(dev, MAC, xType, ipNDevice, "", "", " status up         GW DICT new gateway if_table", "STATUS-GW")
					self.executeUpdateStatesList()
					dev = indigo.devices[dev.id]
					self.setupStructures(xType, dev, MAC)
					self.executeUpdateStatesList()
					self.setUpDownStateValue(dev)
					dev = indigo.devices[dev.id]
					indigo.variable.updateValue("Unifi_New_Device", "{}/{}/{}".format(dev.name, MAC, ipNDevice) )
					if self.decideMyLog("Dict", MAC=MAC): self.indiLOG.log(10,"DC-GW-1--- {}  ip:{}  {}  new device".format(MAC, ipNDevice, dev.name) )
					isNew = False #  fill the rest in next section
				except	Exception as e:
					if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

			if not isNew:
				if "uptime" in gwDict and gwDict["uptime"] != "" and "upSince" in dev.states:				self.addToStatesUpdateList(dev.id,"upSince",time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()-gwDict["uptime"])) )
				props = dev.pluginProps
				if wanSetup == "failover": 
					if "failoverSettings" in props and props["failoverSettings"] == "copypublicIP":
						publicIP = publicIP2 
						gateways = gateways2 
						nameservers = nameservers2 


				self.MAC2INDIGO[xType][MAC]["ipNumber"] = ipNDevice
				self.MAC2INDIGO[xType][MAC]["lastUp"] 	 = time.time()

				if dev.states["wanSetup"] 				!= wanSetup: 											self.addToStatesUpdateList(dev.id,"wanSetup", wanSetup)
				if dev.states["MAClan"] 				!= MAClan:												self.addToStatesUpdateList(dev.id,"MAClan", MAClan)
				if dev.states["ipNumber"] 				!= ipNDevice: 											self.addToStatesUpdateList(dev.id,"ipNumber", ipNDevice)
				if dev.states["model"] 				!= model and model != "":								self.addToStatesUpdateList(dev.id,"model", model)
				if dev.states["memPercent"] 			!= cpuPercent and memPercent != "":						self.addToStatesUpdateList(dev.id,"memPercent", memPercent)
				if dev.states["cpuPercent"] 			!= cpuPercent and cpuPercent != "":						self.addToStatesUpdateList(dev.id,"cpuPercent", cpuPercent)
				if dev.states["temperature"] 			!= temperature and temperature != "": 					self.addToStatesUpdateList(dev.id,"temperature", temperature)
				if dev.states["temperature_Board_CPU"]	!= temperature_Board_CPU and temperature_Board_CPU != "": self.addToStatesUpdateList(dev.id,"temperature_Board_CPU", temperature_Board_CPU)
				if dev.states["temperature_Board_PHY"]	!= temperature_Board_PHY and temperature_Board_PHY != "": self.addToStatesUpdateList(dev.id,"temperature_Board_PHY", temperature_Board_PHY)
				if dev.states["temperature_CPU"]		!= temperature_CPU 		 and temperature_CPU != "":		self.addToStatesUpdateList(dev.id,"temperature_CPU", temperature_CPU)
				if dev.states["temperature_PHY"]		!= temperature_PHY 		 and temperature_PHY != "":		self.addToStatesUpdateList(dev.id,"temperature_PHY", temperature_PHY)

				if dev.states["wan"] 					!= wanUP:												self.addToStatesUpdateList(dev.id,"wan", "up" if wanUP else "down")	
				if dev.states["MAC"] 					!= MAC:													self.addToStatesUpdateList(dev.id,"MAC", MAC)
				if dev.states["nameservers"]			!= nameservers:											self.addToStatesUpdateList(dev.id,"nameservers", nameservers)
				if dev.states["gateways"] 				!= gateways:											self.addToStatesUpdateList(dev.id,"gateways", gateways)
				if dev.states["publicIP"] 				!= publicIP:											self.addToStatesUpdateList(dev.id,"publicIP", publicIP)
				if dev.states["wanPingTime"] 			!= wanPingTime: 										self.addToStatesUpdateList(dev.id,"wanPingTime", wanPingTime)
				if dev.states["wanLatency"] 			!= wanLatency: 											self.addToStatesUpdateList(dev.id,"wanLatency", wanLatency)
				if dev.states["wanUpload"] 			!= wanUpload:											self.addToStatesUpdateList(dev.id,"wanUpload", wanUpload)
				if dev.states["wanSpeedTest"] 			!= wanSpeedTest:										self.addToStatesUpdateList(dev.id,"wanSpeedTest", wanSpeedTest)
				if dev.states["wanDownload"] 			!= wanDownload:											self.addToStatesUpdateList(dev.id,"wanDownload", wanDownload)
				if dev.states["wanUpTime"] 			!= wanUpTime: 											self.addToStatesUpdateList(dev.id,"wanUpTime", wanUpTime)

				if dev.states["wan2"] 					!= wan2UP:												self.addToStatesUpdateList(dev.id,"wan2", "up" if wan2UP else "down")
				if dev.states["MACwan2"] 				!= MACwan2:												self.addToStatesUpdateList(dev.id,"MACwan2", MACwan2)
				if dev.states["wan2Nameservers"]		!= nameservers2:										self.addToStatesUpdateList(dev.id,"wan2Nameservers", nameservers2)
				if dev.states["wan2Gateways"] 			!= gateways2:											self.addToStatesUpdateList(dev.id,"wan2Gateways", gateways2)
				if dev.states["wan2PublicIP"] 			!= publicIP2:											self.addToStatesUpdateList(dev.id,"wan2PublicIP", publicIP2)
				if dev.states["wan2PingTime"] 			!= wan2PingTime: 										self.addToStatesUpdateList(dev.id,"wan2PingTime", wan2PingTime)
				if dev.states["wan2Latency"] 			!= wan2Latency:											self.addToStatesUpdateList(dev.id,"wan2Latency", wan2Latency)
				if dev.states["wan2Upload"] 			!= wan2Upload:											self.addToStatesUpdateList(dev.id,"wan2Upload", wan2Upload)
				if dev.states["wan2SpeedTest"] 		!= wan2SpeedTest:										self.addToStatesUpdateList(dev.id,"wan2SpeedTest", wan2SpeedTest)
				if dev.states["wan2Download"] 			!= wan2Download:										self.addToStatesUpdateList(dev.id,"wan2Download", wan2Download)
				if dev.states["wan2UpTime"] 			!= wan2UpTime: 											self.addToStatesUpdateList(dev.id,"wan2UpTime", wan2UpTime)

				if dev.states["status"] 				!= "up":												self.setImageAndStatus(dev, "up",oldStatus=dev.states["status"], ts=time.time(), level=1, text1=dev.name.ljust(30) + " status up   GW DICT if_table", reason="gateway DICT", iType="STATUS-GW")


				if self.decideMyLog("Dict", MAC=MAC) or self.decideMyLog("UDM"): self.indiLOG.log(10,"DC-GW-1--  {}     ip:{}    {}   new GW data".format(MAC,ipNDevice, dev.name))

				self.setStatusUpForSelfUnifiDev(MAC)

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		self.unsetBlockAccess("doGatewaydictSELF")
		
		return


	####-----------------	 ---------
	def convertTimedeltaToDaysHoursMin(self,uptime):
		try:
			ret = ""
			uptime = float(uptime)
			xx = "{}".format(datetime.timedelta(seconds=uptime)).replace(" days","").replace(" day","").split(",")
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
		self.setBlockAccess("doNeighborsdict")

		try:
			devType ="neighbor"
			devName ="neighbor"
			isType  = "isNeighbor"
			xType   = "NB"
			for kk in range(len(apDict)):

				shortR = apDict[kk].get("scan_table","")
				for shortC in shortR:
					MAC = "{}".format(shortC.get("bssid",""))
					channel = "{}".format(shortC.get("channel",""))
					essid = "{}".format(shortC.get("essid",""))
					age = "{}".format(shortC.get("age",""))
					adhoc = "{}".format(shortC.get("is_adhoc",""))
					try:
						rssi = "{}".format(shortC.get("rssi",""))
					except:
						rssi = ""
					if "model_display" in shortC:  model = shortC.get("model_display","")
					else:
						model = ""

					new = True
					if int(channel) >= 36:
						GHz = "5"
					else:
						GHz = "2"
					if MAC in self.MAC2INDIGO[xType]:
						try:
							dev = indigo.devices[self.MAC2INDIGO[xType][MAC]["devId"]]
							if dev.deviceTypeId != devType: 1 / 0
							new = False
						except:
							if self.decideMyLog("Logic", MAC=MAC): self.indiLOG.log(10,MAC + "     {}".format(self.MAC2INDIGO[xType][MAC]) + " wrong " + devType)
							for dev in indigo.devices.iter("props."+isType):
								if "MAC" not in dev.states: continue
								if dev.states["MAC"] != MAC: continue
								self.setupStructures(xType, dev, MAC, init=False)
								new = False
								break
					if not new:
							self.MAC2INDIGO[xType][MAC]["ipNumber"] = ipNumber
							if self.decideMyLog("DictDetails", MAC=MAC): self.indiLOG.log(10,"DC-NB-0-   "+ipNumber+ " MAC: " + MAC + " GHz:" + GHz + "     essid:" + essid + " channel:" + channel )
							if MAC != dev.states["MAC"]:
								self.addToStatesUpdateList(dev.id,"MAC", MAC)
							if essid != dev.states["essid"]:
								self.addToStatesUpdateList(dev.id,"essid", essid)
							if channel != dev.states["channel"]:
								self.addToStatesUpdateList(dev.id,"channel", channel)
							if channel != dev.states["adhoc"]:
								self.addToStatesUpdateList(dev.id,"adhoc", adhoc)

							signalOLD = [" " for iii in range(_GlobalConst_numberOfAP)]
							signalNEW = copy.copy(signalOLD)
							if rssi != "":
								signalOLD = dev.states["Signal_at_APs"].split("[")[0].split("/")
								if len(signalOLD) == _GlobalConst_numberOfAP:
									signalNEW = copy.copy(signalOLD)
									signalNEW[apNumb] = "{}".format(int(-90 + float(rssi) / 99. * 40.))
							if signalNEW != signalOLD or dev.states["Signal_at_APs"] == "":
								self.addToStatesUpdateList(dev.id,"Signal_at_APs", "/".join(signalNEW) + "[dBm]")

							if model != dev.states["model"] and model != "":
								self.addToStatesUpdateList(dev.id,"model", model)
							self.MAC2INDIGO[xType][MAC]["age"] = age
							self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
							self.setImageAndStatus(dev, "up",oldStatus=dev.states["status"], ts=time.time(), level=1, text1=dev.name.ljust(30) + " status up           neighbor DICT ", reason="neighbor DICT", iType="DC-NB-1   ")
							if self.updateDescriptions	and dev.description != "Channel= " + channel.rjust(2).replace(" ", "0") + " - SID= " + essid:
								dev.description = "Channel= " + channel.rjust(2).replace(" ", "0") + " - SID= " + essid
								dev.replaceOnServer()


					if new and not self.ignoreNewNeighbors:
						self.indiLOG.log(10,"new: neighbor  " +MAC)
						try:
							dev = indigo.device.create(
								protocol		=indigo.kProtocol.Plugin,
								address			=MAC,
								name			=devName + "_" + MAC,
								description		="Channel= " + channel.rjust(2).replace(" ", "0") + " - SID= " + essid,
								pluginId		=self.pluginId,
								deviceTypeId	=devType,
								folder			=self.folderNameNeighbors,
								props			={"useWhatForStatus":"",isType:True})
						except	Exception as e:
							if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
							continue

						self.setupStructures(xType, dev, MAC)
						self.addToStatesUpdateList(dev.id,"channel", channel)
						signalNEW = [" " for iii in range(_GlobalConst_numberOfAP)]
						if rssi != "":
							signalNEW[apNumb] = "{}".format(int(-90 + float(rssi) / 99. * 40.))
						self.addToStatesUpdateList(dev.id,"Signal_at_APs", "/".join(signalNEW) + "[dBm]")
						self.addToStatesUpdateList(dev.id,"essid", essid)
						self.addToStatesUpdateList(dev.id,"model", model)
						self.MAC2INDIGO[xType][MAC]["age"] = age
						self.addToStatesUpdateList(dev.id,"adhoc", adhoc)
						self.setupBasicDeviceStates(dev, MAC, xType, "", "", "", " status up        neighbor DICT new neighbor", "DC-NB-2   ")
						self.executeUpdateStatesList()
						indigo.variable.updateValue("Unifi_New_Device", "{}".format(dev.name) )
						dev = indigo.devices[dev.id]
						self.setupStructures(xType, dev, MAC)
				self.executeUpdateStatesList()

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		self.unsetBlockAccess("doNeighborsdict")
		
		return




	####-----------------	 ---------
	def doMimiTypeSwitchesWithControllerData(self, apDict, apNumbSW, found):
		try:
				if not self.isMiniSwitch[apNumbSW]: return 
				
				if(	"mac"			in apDict and 
				  	"port_table"	in apDict and
				 	"name"	  		in apDict and
				  	"ip"			in apDict and 
					"model"			in apDict):

					if apDict["model"].find("MINI") == -1: return

					MACSW = apDict["mac"]
					hostname = apDict["name"].strip()
					ipNDevice = apDict["ip"]
					ipNumber = apDict["ip"]
					apDict["model_display"] = hostname
					#self.indiLOG.log(20,"doMimiTypeSwitchesWithControllerData #{}, host:{}, ip:{}, found:{}".format(apNumbSW, hostname, ipNDevice, found))

					#################  update SWs themselves
					self.doSWdictSELF(apDict, apNumbSW, ipNDevice, MACSW, hostname, ipNumber)

					#################  now update the clients on switch, no usefull information
					#self.doSWITCHdictClients(apDict, apNumbSW, ipNDevice, MACSW, hostname, ipNumber)
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)



	####-----------------	 ---------
	#### this does the unifswitch device itself
	####-----------------	 ---------
	def doSWdictSELF(self, theDict, apNumb, ipNDevice, MAC, hostname, ipNumber):

		self.setBlockAccess("doSWdictSELF")

		if "model_display" in theDict:	model = (theDict["model_display"])
		else:
			self.indiLOG.log(30,"model_display not in dict doSWdictSELF")
			model = ""


		devName = "SW"
		xType	= "SW"
		isType	= "isSwitch"

		try:
			if "uptime" not in theDict: return 

			fanLevel	= ""
			if "fan_level" in theDict:
				fanLevel = "{}".format(theDict["fan_level"])

			temperature = ""
			if "general_temperature" in theDict:
				if "{}".format(theDict["general_temperature"]) !="0":
					temperature = GT.getNumber(theDict["general_temperature"])
			if "overheating" in theDict:	overHeating	= theDict["overheating"]# not in UDM
			else:							overHeating = False
			uptime			= "{}".format(theDict.get("uptime",0))
			portTable		= theDict["port_table"]
			nports			= len(portTable)
			nClients		= 0

			if nports not in _numberOfPortsInSwitch:
				for nn in _numberOfPortsInSwitch:
					if nports < nn:
						nports = nn
					if MAC not in self.MAC2INDIGO[xType]:
						self.indiLOG.log(30,"switch device model {} not support: please contact author. This has {} ports; supported are {}   ports only - remember there are extra ports for fiber cables , using next highest..".format(model, nports, _numberOfPortsInSwitch))

			if nports > _numberOfPortsInSwitch[-1]: return


			devType = "Device-SW-{}".format(nports)
			new = True

			if MAC in self.MAC2INDIGO[xType]:
				try:
					dev = indigo.devices[self.MAC2INDIGO[xType][MAC]["devId"]]
					if dev.deviceTypeId != devType: raise error
					new = False
				except:
					if self.decideMyLog("Logic", MAC=MAC): self.indiLOG.log(10,"{}   {}   wrong  {}".format(MAC, self.MAC2INDIGO[xType][MAC], devType) )
					for dev in indigo.devices.iter("props."+isType):
						if "MAC" not in dev.states: continue
						if dev.states["MAC"] != MAC: continue
						self.MAC2INDIGO[xType][MAC]["devId"] = dev.id
						new = False
						break

			UDMswitch = False
			useIP = ipNumber
			if self.unifiControllerType.find("UDM") > -1 and apNumb == self.numberForUDM["SW"]:
				if self.decideMyLog("UDM"):  self.indiLOG.log(10,"DC-SW-UDM  using UDM mode  for  {}; IP process:{}; #Dict{}".format(MAC, ipNumber, ipNDevice ) )



			if not new:
					if self.decideMyLog("DictDetails", MAC=MAC):  self.indiLOG.log(10,"DC-SW-S0   {}/{};   SW  hostname:{}; MAC:{}".format(ipNumber, ipNDevice, hostname, MAC) )
					self.MAC2INDIGO[xType][MAC]["ipNumber"] = ipNumber

					self.deviceUp["SW"][ipNumber]	= time.time()


					if "uptime" in theDict and theDict["uptime"] !="":
						if "upSince" in dev.states:
							self.addToStatesUpdateList(dev.id,"upSince", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()-theDict["uptime"])) )

					ports = {}
					if dev.states["switchNo"] != apNumb:
						self.addToStatesUpdateList(dev.id,"switchNo", apNumb)

					if "ports" not in self.MAC2INDIGO[xType][MAC]:
						self.MAC2INDIGO[xType][MAC]["ports"]={}
					self.MAC2INDIGO[xType][MAC]["nPorts"] = len(portTable)

					for port in portTable:

						if "port_idx" not in port: continue
						ID = port["port_idx"]
						idS = "{:02d}".format(ID) # state name

						if "{}".format(ID) not in self.MAC2INDIGO[xType][MAC]["ports"]:
							self.MAC2INDIGO[xType][MAC]["ports"]["{}".format(ID)] = {"rxLast": 0, "txLast": 0, "timeLast": 0,"poe":"","fullDuplex":"","link":"","nClients":0}
						portsMAC = self.MAC2INDIGO[xType][MAC]["ports"]["{}".format(ID)]
						if portsMAC["timeLast"] != 0. and "tx_bytes" in port:
							try:
								dt = max(5, time.time() - portsMAC["timeLast"]) * 1000
								rxRate = "{:.1f}".format( (port["tx_bytes"] - portsMAC["txLast"]) / dt + 0.5)
								txRate = "{:.1f}".format( (port["rx_bytes"] - portsMAC["rxLast"]) / dt + 0.5)
							except	Exception as e:
								if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
							try:
								errors = "{}".format(port["tx_dropped"] + port["tx_errors"] + port["rx_errors"] + port["rx_dropped"])
							except:
								errors = "?"
							if port["full_duplex"]:
								fullDuplex = "FD"
							else:
								fullDuplex = "HD"
							portsMAC["fullDuplex"] = fullDuplex+"-" + ("{}".format(port["speed"]))

							nDevices = 0
							if "mac_table" in port:
								nDevices = len(port["mac_table"])
							portsMAC["nClients"] = nDevices
							ppp = "#C: {:02d}" .format(nDevices) # of clients


							SWP = ""
							if "is_uplink"  in port and port["is_uplink"]:
								SWP = "UL"
								ppp += ";"+SWP


							### check if another unifi switch or gw is attached to THIS port , add SW:# or GW:0to the port string
							if SWP == "" and "lldp_table"  in port and len(port["lldp_table"]) >0:
								lldp_table = port["lldp_table"][0]
								if "lldp_chassis_id" in lldp_table and "lldp_port_id" in lldp_table and "lldp_system_name" in lldp_table:
									try:
										LinkName = 			lldp_table["lldp_system_name"].lower()
										macUPdowndevice = 	lldp_table["lldp_chassis_id"].lower()
										portID = 			lldp_table["lldp_port_id"].lower()

										if	SWP == "" and macUPdowndevice in self.MAC2INDIGO["GW"]:
											ppp += ";GW"
											SWP  = "GW"

										if	SWP == "" and macUPdowndevice in self.MAC2INDIGO["AP"]:
											ppp += ";AP"
											SWP  = "AP"

										if	SWP == "" and "gatew" in LinkName or "udm" in LinkName and LinkName.find("switch") ==-1:
											ppp += ";GW"
											SWP  = "GW"

										if  SWP == "" and macUPdowndevice in self.MAC2INDIGO[xType]:
											try:	portNatSW = ",P:"+portID.split("/")
											except: portNatSW = ""
											SWP = "DL"
											devIdOfSwitch = self.MAC2INDIGO["SW"][macUPdowndevice]["devId"]
											ppp+= ";"+SWP+":{}".format(indigo.devices[devIdOfSwitch].states["switchNo"])+portNatSW

										if  SWP == "" and "switch" in LinkName:
											ppp += ";DL"
											SWP = "DL"

									except	Exception as e:
											if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

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
							if "poe_enable" in port:
								if port["poe_enable"]:
									if ("poe_good" in port and port["poe_good"])	:
										poe="poe1"
									elif ("poe_mode" in port and port["poe_mode"] == "passthrough") :
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

							if "port_" + idS in dev.states:
								if nDevices > 0:
									ppp += ";" + fullDuplex + "-" + ("{}".format(port["speed"]))
									ppp += "; err:" + errors
									ppp += "; rx-tx[kb/s]:" + rxRate + "-" + txRate
								else:
									ppp += "; ; ;"

								if ppp != dev.states["port_" + idS]:
									self.addToStatesUpdateList(dev.id,"port_" + idS, ppp)




						portsMAC["txLast"]	   = port.get("tx_bytes","")
						portsMAC["rxLast"]	   = port.get("rx_bytes","")
						portsMAC["timeLast"]  = time.time()

					if model != dev.states["model"] and model !="":
						self.addToStatesUpdateList(dev.id,"model", model)
					if uptime != self.MAC2INDIGO[xType][MAC]["upTime"]:
						self.MAC2INDIGO[xType][MAC]["upTime"] =uptime
					if temperature !="" and "temperature" in dev.states and  temperature != dev.states["temperature"]:
						self.addToStatesUpdateList(dev.id,"temperature", temperature)
					if "overHeating" in dev.states and overHeating != dev.states["overHeating"]:
							self.addToStatesUpdateList(dev.id,"overHeating", overHeating)
					if useIP != dev.states["ipNumber"]:
						self.addToStatesUpdateList(dev.id,"ipNumber", useIP)
					if hostname != dev.states["hostname"]:
						self.addToStatesUpdateList(dev.id,"hostname", hostname)
					if dev.states["status"] != "up":
						self.setImageAndStatus(dev, "up",oldStatus=dev.states["status"], ts=time.time(), level=1, text1=dev.name.ljust(30) + " status up            SW    DICT", reason="switch DICT", iType="STATUS-SW")
					self.MAC2INDIGO[xType][MAC]["lastUp"] = time.time()
					if "fanLevel" in dev.states and  fanLevel != "" and fanLevel != dev.states["fanLevel"]:
						self.addToStatesUpdateList(dev.id,"fanLevel", fanLevel)

					if "nClients" in dev.states and  nClients != "" and nClients != dev.states["nClients"]:
						self.addToStatesUpdateList(dev.id,"nClients", nClients)


					if self.updateDescriptions:
						ipx = self.fixIP(useIP)
						oldIPX = dev.description.split("-")
						if oldIPX[0] != ipx or ( (dev.description != ipx + "-" + hostname) or len(dev.description) < 5):
							if oldIPX[0] != ipx and oldIPX[0] !="":
								indigo.variable.updateValue("Unifi_With_IPNumber_Change", "{}/{}/{}/{}".format(dev.name, dev.states["MAC"], oldIPX[0], ipx) )
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
				newName = devName+"_" + MAC
				self.indiLOG.log(30,"creating new unifi switch device:{};  MAC:{};  IP#in dict:{}; ip# dev:{}; Model:{}; devType:{};  nports:{}".format(newName, MAC, ipNDevice, ipNumber, model, devType, nports) )
				try:
					dev = indigo.device.create(
						protocol 		= indigo.kProtocol.Plugin,
						address 		= MAC,
						name 			= newName,
						description 	= self.fixIP(useIP) + "-" + hostname,
						pluginId 		= self.pluginId,
						deviceTypeId 	= devType,
						folder 			= self.folderNameIDCreated,
						props 			= {"useWhatForStatus":"",isType:True})
					self.setupStructures(xType, dev, MAC)
					self.MAC2INDIGO[xType][MAC]["upTime"] = uptime
					self.addToStatesUpdateList(dev.id,"model", model)
					if temperature != "" and "temperature" in dev.states and  temperature != dev.states["temperature"]:
						self.addToStatesUpdateList(dev.id,"temperature", temperature)
					self.addToStatesUpdateList(dev.id,"overHeating", overHeating)
					self.addToStatesUpdateList(dev.id,"hostname", hostname)
					self.addToStatesUpdateList(dev.id,"switchNo", apNumb)
					self.setupBasicDeviceStates(dev, MAC, xType, useIP, "", "", " status up     SW DICT  new SWITCH", "STATUS-SW")
					indigo.variable.updateValue("Unifi_New_Device", "{}/{}/{}".format(dev.name, MAC, useIP) )
					dev = indigo.devices[dev.id]
					self.setupStructures(xType, dev, MAC)
				except	Exception as e:
					if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
					self.indiLOG.log(40,"     for mac#{};  hostname: {}".format(MAC, hostname))
					self.indiLOG.log(40,"MAC2INDIGO: {}".format(self.MAC2INDIGO[xType]))

			self.executeUpdateStatesList()

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		self.unsetBlockAccess("doSWdictSELF")
		

		return

	####----------------- if FINGSCAN is enabled send update signal	 ---------
	def setStatusUpForSelfUnifiDev(self, MAC):
		try:

			if MAC in self.MAC2INDIGO["UN"]:
				self.MAC2INDIGO["UN"][MAC]["lastUp"] = time.time()+20
				devidUN = self.MAC2INDIGO["UN"][MAC]["devId"]
				try:
					devUN = indigo.devices[devidUN]
					if devUN.states["status"] !="up":
						self.addToStatesUpdateList(devidUN,"status", "up")
						self.addToStatesUpdateList(devidUN,"lastStatusChangeReason", "switch message")
						if self.decideMyLog("Logic", MAC=MAC) :  self.indiLOG.log(10,"updateself setStatusUpForSelfUnifiDev:      updating status to up MAC:" + MAC+"  "+devUN.name+"  was: "+ devUN.states["status"] )
					if "{}".format(devUN.displayStateImageSel) !="SensorOn":
						devUN.updateStateImageOnServer(indigo.kStateImageSel.SensorOn)
				except:pass

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
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
							if dev.deviceTypeId != "neighbor" or ( dev.deviceTypeId == "neighbor" and not self.ignoreNeighborForFing) :
								try:
									if self.decideMyLog("Fing"): self.indiLOG.log(10,"FINGSC---   "+"updating fingscan with " + dev.name + " = " + dev.states["status"])
									plug.executeAction("unifiUpdate", props={"deviceId": [devid]})
									self.fingscanTryAgain = False
								except	Exception as e:
									if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
									self.fingscanTryAgain = True

			else:
				devIds	  = []
				devNames  = []
				devValues = {}
				stringToPrint = "\n"
				for dev in indigo.devices.iter(self.pluginId):
					if dev.deviceTypeId == "client": continue
					devIds.append("{}".format(dev.id))
					stringToPrint += dev.name + "= " + dev.states["status"] + "\n"

				if devIds != []:
					for i in range(3):
						if self.decideMyLog("Fing"): self.indiLOG.log(10,"FINGSC---   "+"updating fingscan try# {}".format(i + 1) + ";     with " + stringToPrint )
						plug.executeAction("unifiUpdate", props={"deviceId": devIds})
						self.fingscanTryAgain = False
						break

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
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
					if self.decideMyLog("BC"): self.indiLOG.log(10,"BroadCast-   updating BC with {}".format(msg) )
					indigo.server.broadcastToSubscribers("deviceStatusChanged", json.dumps(msg))
				except	Exception as e:
					if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return x

	####-----------------	 ---------
	def setupBasicDeviceStates(self, dev, MAC, devType, ip, ipNDevice, GHz, text1, type):
		try:
			self.addToStatesUpdateList(dev.id,"created", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
			self.addToStatesUpdateList(dev.id,"MAC", MAC)
			self.MAC2INDIGO[devType][MAC]["lastUp"] = time.time()
			if ip !="":
				self.addToStatesUpdateList(dev.id,"ipNumber", ip)

			self.setImageAndStatus(dev, "up",oldStatus=dev.states["status"], ts=time.time(), level=1, text1=dev.name.ljust(30) + text1, iType=type,reason="initialsetup")
			vendor = self.getVendortName(MAC)
			if vendor != "":
					self.addToStatesUpdateList(dev.id,"vendor", vendor)
					self.moveToUnifiSystem(dev, vendor)
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return

	####-----------------	 ---------
	def testIgnoreMAC(self, MAC,  fromSystem="") :
		ignore = False
		if MAC in self.MACignorelist:
			if self.decideMyLog("IgnoreMAC"):  self.indiLOG.log(10,"{:10}: ignore list.. ignore MAC:{}".format(fromSystem, MAC))
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
				if self.decideMyLog("IgnoreMAC"):  self.indiLOG.log(10,"{:10}: ignore list.. ignore MAC:{};  is member of ignore list:{}" .format(fromSystem, MAC, MACsp))
				return True
		return False

	####-----------------	 ---------
	def moveToUnifiSystem(self,dev,vendor):
		try:
			if vendor.upper().find("UBIQUIT") >-1:
				indigo.device.moveToFolder(dev.id, value=self.folderNameIDSystemID)
				self.indiLOG.log(10,"moving "+dev.name+";  to folderID: {}".format(self.folderNameIDSystemID))
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return

	####-----------------	 ---------
	def getVendortName(self,MAC):
		if self.enableMACtoVENDORlookup !="0" and not self.waitForMAC2vendor:
			self.waitForMAC2vendor = self.M2V.makeFinalTable()

		return	self.M2V.getVendorOfMAC(MAC)


	####-----------------	 ---------
	def setImageAndStatus(self, dev, newStatus, oldStatus="123abc123abcxxx", ts="", level=1, text1="", iType="", force=False, fing=True,reason=""):
		try:
			if "{}".format(dev.id) not in self.xTypeMac: 
				self.indiLOG.log(10,"STAT-Chng  {} not properly setup,  missing in xTypeMac".format(dev.name.ljust(20)) )
				return 

			MAC	  =	 self.xTypeMac["{}".format(dev.id)]["MAC"]
			if self.testIgnoreMAC(MAC, fromSystem="set-image"): return 

			if  self.decideMyLog("", MAC=MAC): self.indiLOG.log(10,"STAT-Chang {} data in: newSt:{}; oldStIn:{}; oldDevSt:{}".format(MAC, newStatus, oldStatus, dev.states["status"]))
			if oldStatus == "123abc123abc":
				oldStatus = dev.states["status"]

			try:	xType = self.xTypeMac["{}".format(dev.id)]["xType"]
			except: 
				self.indiLOG.log(10,"STAT-Chang error for devId:{} xType bad:{}".format(dev.id, self.xTypeMac["{}".format(dev.id)]))
				return

			if oldStatus != newStatus or force:

				if oldStatus != newStatus:
					if fing and oldStatus != "123abc123abcxxx":
						self.sendUpdateToFingscanList["{}".format(dev.id)] = "{}".format(dev.id)
					self.addToStatesUpdateList(dev.id, "status", newStatus)

					if "lastStatusChangeReason" in dev.states and reason != "":
						self.addToStatesUpdateList(dev.id, "lastStatusChangeReason", reason)
					if self.decideMyLog("Logic", MAC=MAC): self.indiLOG.log(10,"STAT-Chang {} st changed  {}->{}; {}".format(dev.states["MAC"], dev.states["status"], newStatus, text1))

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		return

	####-----------------	 ---------
	#### wake on lan and pings	START
	####-----------------	 ---------
	def sendWakewOnLanAndPing(self, MAC,IPNumber, nBC=2, waitForPing=500, countPings=1, waitBeforePing=0.5, waitAfterPing=0.5, nPings =1, calledFrom="", props=""):
		try:
			doWOL = True
			if props != "" and "useWOL" in props and props["useWOL"] =="0": doWOL = False
			if doWOL:
				self.sendWakewOnLan(MAC, calledFrom=calledFrom)
				if nBC ==2:
					self.sleep(0.05)
					self.sendWakewOnLan(MAC, calledFrom=calledFrom)
				self.sleep(waitBeforePing)
			return self.checkPing(IPNumber, waitForPing=waitForPing, countPings=countPings, nPings=nPings, waitAfterPing=waitAfterPing, calledFrom=calledFrom)
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return

	####-----------------	 ---------
	def checkPing(self, IPnumber , waitForPing=100, countPings=1,nPings=1, waitAfterPing=0.5, calledFrom="",verbose=False):
		try:
			Wait = ""
			if waitForPing != "":
				Wait = "-W {}".format(waitForPing)
			Count = "-c 1"

			if countPings != "":
				Count = "-c {}".format(countPings)

			if nPings == 1 :
				waitAfterPing = 0.

			retCode =1
			for nn in range(nPings):
				retCode = subprocess.call('/sbin/ping -o '+Wait+' '+Count+' -q '+IPnumber+' >/dev/null',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE) # "call" will wait until its done and deliver retcode 0 or >0
				if self.decideMyLog("Ping"):  self.indiLOG.log(10,calledFrom+" "+"ping resp:{}  :{}".format(IPnumber,retCode))
				if retCode ==0:  return 0
				if nn != nPings-1: self.sleep(waitAfterPing)
			if retCode !=0 and verbose:  self.indiLOG.log(10,"ping to:{}, dev not responding".format(IPnumber))
			return retCode
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return

	####-----------------	 ---------
	def sendWakewOnLan(self, MAC, calledFrom=""):
		if self.broadcastIP !="9.9.9.255":
			bc = self.broadcastIP
			macaddress = MAC.upper().replace(":",'')
			if sys.version_info[0] > 2:  # >  python 2
				temp = b''
				for i in range(0, len(macaddress), 2):
					temp += struct.pack('B', int(macaddress[i: i + 2], 16))
				data = b'FFFFFFFFFFFF' + temp * 16

			else:
				data = ''.join(['FFFFFFFFFFFF', macaddress * 16])
				data = data.encode("hex")
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
			try:
				sock.sendto(data, (bc, 9))
			except Exception as e:
				if "{}".format(e).find("None") == -1: 
					self.indiLOG.log(30,"", exc_info=True)
					self.indiLOG.log(30,"sendWakewOnLan, type:{},  data:{}  broadcastIP type:{}, {}".format(type(data), data, type(self.broadcastIP), self.broadcastIP))
			if self.decideMyLog("Ping"):  self.indiLOG.log(10,"{} sendWakewOnLan for {};    called from {};  bc ip: {}".format(calledFrom, MAC, calledFrom, self.broadcastIP))
		return

	####-----------------	 ---------
	#### wake on lan and pings	END
	####-----------------	 ---------



####-------------------------------------------------------------------------####
	def getHostFileCheck(self):
		if self.pluginPrefs.get("hostFileCheck","") == "ignore":
			return " yes "
		return " no "


	####-----------------	 ---------
	def manageLogfile(self, apDict, apNumb, unifiDeviceType):
		try:
			if self.decideMyLog("DictFile"):
				self.writeJson( apDict, fName="{}dict-{}#{}.json".format(self.indigoPreferencesPluginDir, unifiDeviceType, apNumb), sort=False, doFormat=True )
		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return


	####-----------------	 ---------
	def exeDisplayStatus(self, dev, status, force=True):
		if status.lower() in ["up","on","connected"] :
			dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOn)
		elif status.lower() in ["down","off","adopting","offline"]:
			dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOff)
		elif status.lower()  in ["expired","rec","event","motion","ring","person","vehicle"]:
			dev.updateStateImageOnServer(indigo.kStateImageSel.SensorTripped)
		elif status.lower()  in ["susp"] :
			dev.updateStateImageOnServer(indigo.kStateImageSel.PowerOff)
		elif status == "" :
			dev.updateStateImageOnServer(indigo.kStateImageSel.SensorTripped)
		if force or status == "":
			dev.updateStateOnServer("displayStatus",self.padDisplay(status)+datetime.datetime.now().strftime("%m-%d %H:%M:%S"))
			dev.updateStateOnServer("status",status)
			dev.updateStateOnServer("onOffState",value= dev.states["status"].lower() in ["up","rec","on","connected"], uiValue= dev.states["displayStatus"])
		return


	####-----------------	 ---------
	def addToStatesUpdateList(self,devid, key, value):
		try:
			devId = "{}".format(devid)
			#if self.decideMyLog("Special") and (key == "status" or key == "displayStatus"): self.indiLOG.log(10,"addToStatesUpdateList (1) devId {} key:{}; value:{}".format(devid, key, value ) )
			### no down during startup .. 100 secs
			if key == "status" and value.lower() not in ["up", "connected", "event", "rec", "motion", "vehicle", "person"]:
				if time.time() - self.pluginStartTime < 0:
					#self.indiLOG.log(10,"in addToStatesUpdateList reject update at startup for devId:{} key:{}; value:{}".format(devid, key, value ) )
					return

			localCopy = copy.deepcopy(self.devStateChangeList)
			if devId not in localCopy:
				localCopy[devId] = {}

			if key in localCopy[devId]:
				if value != localCopy[devId][key]:
					localCopy[devId][key] = {}

			localCopy[devId][key] = value
			self.devStateChangeList = copy.deepcopy(localCopy)
			#if self.decideMyLog("Special") and (key == "status" or key == "displayStatus"): self.indiLOG.log(10,"addToStatesUpdateList (2) devId {} key:{}; value:{}".format(devid, key, value ) )


		except	Exception as e:
			if len("{}".format(e))	> 5 :
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return




	####-----------------	 ---------
	def executeUpdateStatesList(self):
		devId = ""
		key = ""
		local = ""
		try:
			if len(self.devStateChangeList) == 0: return
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
						#if self.decideMyLog("Special"): self.indiLOG.log(10,"executeUpdateStatesList (1) dev {} key:{}; value:{}".format(dev.name, key, value ) )
						if "{}".format(value) != "{}".format(dev.states[key]):
							if devId not in changedOnly: changedOnly[devId]=[]
							changedOnly[devId].append({"key":key,"value":value})
							if key == "status":
								#if "MAC" in dev.states and self.decideMyLog("", MAC=dev.states["MAC"]): self.indiLOG.log(10,"executeUpdateStatesList(2) dev {} key:{}; value:{}".format(dev.name, key, value ) )
								ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
								changedOnly[devId].append({"key":"lastStatusChange", "value":ts})
								if "previousStatusChange" in dev.states:
									changedOnly[devId].append({"key":"previousStatusChange", "value":dev.states["lastStatusChange"]})
								changedOnly[devId].append({"key":"displayStatus",	   "value":self.padDisplay(value)+ts } )
								changedOnly[devId].append({"key":"onOffState",	   "value":value in ["up","rec","ON"],   "uiValue":self.padDisplay(value)+ts } )
								self.exeDisplayStatus(dev, value, force=False)

								self.statusChanged = max(1,self.statusChanged)
								trigList.append(dev.name)
								val = "{}".format(value).lower()
								if self.enableBroadCastEvents !="0" and val in ["up","down","expired","rec","ON", "event"]:
									props = dev.pluginProps
									if	self.enableBroadCastEvents == "all" or	("enableBroadCastEvents" in props and props["enableBroadCastEvents"] == "1" ):
										msg = {"action":"event", "id":"{}".format(dev.id), "name":dev.name, "state":"status", "valueForON":"up", "newValue":val}
										if self.decideMyLog("BC"):	self.indiLOG.log(10,"BroadCast {:30} {}".format(dev.name, msg))
										self.sendBroadCastEventsList.append(msg)



					if devId in changedOnly and changedOnly[devId] !=[]:
						if self.decideMyLog("UpdateStates"):	self.indiLOG.log(10,"update device:{:30}  states:{}".format(dev.name, changedOnly[devId]))

						self.dataStats["updates"]["devs"]	  +=1
						self.dataStats["updates"]["states"] +=len(changedOnly)
						if self.indigoVersion >6:
							try:
								dev.updateStatesOnServer(changedOnly[devId])
							except	Exception as e:
								if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
						else:
							for uu in changedOnly[devId]:
								dev.updateStateOnServer(uu["key"],uu["value"])

			if len(trigList) >0:
				for devName	 in trigList:
					indigo.variable.updateValue("Unifi_With_Status_Change",devName)
				#self.triggerEvent("someStatusHasChanged")
		except	Exception as e:
			if len("{}".format(e))	> 5 :
				if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
				try:
					self.indiLOG.log(40,"{}     {}  {};  devStateChangeList:\n{}".format(dev.name, devId , key, local) )
				except:pass
		if len(self.sendBroadCastEventsList) >0: self.sendBroadCastNOW()
		return

	####-----------------	 ---------
	def padDisplay(self,status):
		if	 status == "up":		 return status.ljust(11)
		elif status == "expired":	 return status.ljust(8)
		elif status == "down":		 return status.ljust(9)
		elif status == "susp":		 return status.ljust(9)
		elif status == "changed":	 return status.ljust(8)
		elif status == "double":	 return status.ljust(8)
		elif status == "ignored":	 return status.ljust(8)
		elif status == "off":		 return status.ljust(11)
		elif status == "REC":		 return status.ljust(9)
		elif status == "ON":		 return status.ljust(10)
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
			indigo.server.log("sent \"{}\" beep request not implemented".format(dev.name) )

		###### STATUS REQUEST ######
		elif action.deviceAction == indigo.kUniversalAction.RequestStatus:
			# Query hardware module (dev) for its current status here:
			# ** IMPLEMENT ME **
			indigo.server.log("sent \"{}\" status request not implemented".format(dev.name) )
		return

	####-----------------
	########################################
	# Sensor Action callback
	######################
	def actionControlSensor(self, action, dev):
		###### TURN ON ######
		if action.sensorAction == indigo.kSensorAction.TurnOn:
			self.setImageAndStatus(dev, "up",oldStatus=dev.states["status"], ts=time.time(), iType="actionControlSensor",reason="TurnOn")

		###### TURN OFF ######
		elif action.sensorAction == indigo.kSensorAction.TurnOff:
			self.setImageAndStatus(dev, "up",oldStatus=dev.states["status"], ts=time.time(), iType="actionControlSensor",reason="TurnOff")

		###### TOGGLE ######
		elif action.sensorAction == indigo.kSensorAction.Toggle:
			if dev.onState:
				self.setImageAndStatus(dev, "up",oldStatus=dev.states["status"], ts=time.time(), iType="actionControlSensor",reason="toggle")
			else:
				self.setImageAndStatus(dev, "up",oldStatus=dev.states["status"], ts=time.time(), iType="actionControlSensor",reason="toggle")

		self.executeUpdateStatesList()
		return


	####---------------- wait for other tasks to finish (ie main and fill messages ) wait max 9 secs ---------
	#### unblock 
	def unsetBlockAccess(self, waitingPgm):
		try:
			qLen = self.blockWaitQueue.qsize()
			if qLen == 0: return 
			if qLen == 1:
				self.blockWaitQueue = PriorityQueue()
				return 

			#if qlengthNow == 1: 
			#	self.blockWaitQueue.get()
			#	return
			tempQueue = PriorityQueue()
			blockingPGM = ""
			for nn in range(qLen):
				try: 
					blockingPGM = self.blockWaitQueue.queue[qLen-nn-1]
				except: 
					tempQueue = PriorityQueue()
					break 
				if blockingPGM == waitingPgm: continue
				tempQueue.put(blockingPGM)

			self.blockWaitQueue = tempQueue

		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		return 

	#### block
	def setBlockAccess(self, waitingPgm):
		try:	
			waitTime = time.time()
			blockingPgm = "None"
			qLenMax = 0
			for ii in range(90):
				qlengthNow = self.blockWaitQueue.qsize()
				qLenMax = max(qLenMax, qlengthNow)
				if qlengthNow == 0:	break
				if blockingPgm == "None":
					try:	blockingPgm = self.blockWaitQueue.queue[0]
					except Exception as e:
						pass
						#if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
						#self.indiLOG.log(40, "setBlockAccess err waiting for: {}, pgmWaiting:{} queue is:{}".format(blockingPgm, waitingPgm, self.blockWaitQueue.queue))
				#self.indiLOG.log(10, "setBlockAccess waiting for: {}, pgmWaiting:{} qlen:{}; queue is:{}".format(blockingPgm, waitingPgm, self.blockWaitQueue.qsize(), self.blockWaitQueue.queue))
				self.sleep(0.1)

			if  not self.blockWaitQueue.empty(): blockingPgm = self.blockWaitQueue.get()
			self.blockWaitQueue.put(waitingPgm)

			## init dicts if not present 
			if "yesterday" not in self.waitTimes:
				self.waitTimes = {"today":{}, "yesterday":{} }

			if "startDate" not in self.waitTimes["today"]:
				self.waitTimes["today"]["startDate"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
				self.waitTimes["today"]["startTime"] = time.time()
				self.waitTimes["today"]["lastPrint"] = time.time()
				self.waitTimes["today"]["WaitingPgm"] = {}
				self.waitTimes["today"]["BlockingPgm"] = {}
				self.waitTimes["today"]["QlenGT1"] = 0
				self.waitTimes["today"]["QlenMax"] = 0

			waitTime = time.time() - waitTime
			if qlengthNow >0: 
				self.waitTimes["today"]["QlenMax"] = max(self.waitTimes["today"]["QlenMax"], qlengthNow)
				if qlengthNow > 1: 
					self.waitTimes["today"]["QlenGT1"] += 1

			for tagCat, waitOrBlock in [["---TOTAL----", "WaitingPgm"], [waitingPgm, "WaitingPgm"], [blockingPgm, "BlockingPgm"], ["---TOTAL----", "BlockingPgm"] ]:
				if tagCat not in self.waitTimes["today"][waitOrBlock]: 
					self.waitTimes["today"][waitOrBlock][tagCat] = {"n":0, "tot":0., "max":0., ".1":0, ".5":0, "1":0, "3":0, "6":0, "12":0, "20":0}
				if waitOrBlock == "BlockingPgm" and blockingPgm == "": continue
				self.waitTimes["today"][waitOrBlock][tagCat]["n"]   += 1
				self.waitTimes["today"][waitOrBlock][tagCat]["tot"] += waitTime
				self.waitTimes["today"][waitOrBlock][tagCat]["max"]  = max(waitTime, self.waitTimes["today"][waitOrBlock][tagCat]["max"])

				if waitTime > 0.1:
					if waitTime <= 0.5: 
						self.waitTimes["today"][waitOrBlock][tagCat][".1"]  += 1
					else:
						if waitTime <= 1: 
							self.waitTimes["today"][waitOrBlock][tagCat][".5"]  += 1
						else:
							if waitTime <= 3: 
								self.waitTimes["today"][waitOrBlock][tagCat]["1"]  += 1
							else: 
								if waitTime <= 6: 
									self.waitTimes["today"][waitOrBlock][tagCat]["3"]  += 1
								else: 
									if waitTime <= 12: 
										self.waitTimes["today"][waitOrBlock][tagCat]["6"]  += 1
									else:
										if waitTime <= 20: 
											self.waitTimes["today"][waitOrBlock][tagCat]["12"]  += 1
										else: 
											self.waitTimes["today"][waitOrBlock][tagCat]["20"]  += 1

			self.waitTimes["today"]["endDate"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)

		return 

	
####-------------------------------------------------------------------------####
	def readPopen(self, cmd):
		try:
			ret, err = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
			return ret.decode('utf-8'), err.decode('utf-8')

		except Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)


####-------------------------------------------------------------------------####
	def openEncoding(self, ff, readOrWrite, showError=True):

		try:
			if readOrWrite == "r":
				if not os.path.exists(ff):
					return "{}"

			if readOrWrite.find("b") >-1:
				return open( ff, readOrWrite)

			if sys.version_info[0]  > 2:
				return open( ff, readOrWrite, encoding="utf-8")

			else:
				return codecs.open( ff, readOrWrite, "utf-8")

		except	Exception as e:
			if showError: self.indiLOG.log(40,"{}".format(ff))
			if showError: self.indiLOG.log(40,"", exc_info=True)
		return {}

########################################
########################################
####-----------------  logging ---------
########################################
########################################


	####-----------------	 ---------
	def decideMyLog(self, msgLevel, MAC=""):
		try:
			if MAC != "" and MAC in self.MACloglist:				return True
			if msgLevel	 == "all" or "all" in self.debugLevel:		return True
			if msgLevel	 == ""  and "all" not in self.debugLevel:	return False
			if msgLevel in self.debugLevel:							return True

		except	Exception as e:
			if "{}".format(e).find("None") == -1: self.indiLOG.log(40,"", exc_info=True)
		return False
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

