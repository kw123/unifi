#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# by Karl Wachs,  May 18, 2024, v 2.2

#  this program will 
#     test connections to the unifi controller by trying out web port number, home pages, login etc
#     test ssh connection to an AP or switch 
#  will print  
#     logging of connect tries and 
#     the parameters you should use in unifi plugin config, eg:
#
#=====finished======================================== in unifi plugin config set the indicated fields to the value shown:
#                             "field name" = "value"
#    "http: web UserID for CONTROLLER/UDM" = "xxx userid xxx"
#       and next field      "..  password" = "xxx password xxx"
#  "ssh unix UserID of AP,SW,GW - not UDM" = "xxx userid xxx"
#       and next field       ".. password" = "xxx password xxx"
#              ".. ipNumber of Controller" = "192.168.x.x"
#       "site ID (not name) in eg http .." = "default"
# "..controller port#, leave empty for .." = "443"
#                      "check port Number" = "do not check if port number ..."
#=====finished======================================== END 

#
# call :
#  python3 testUnifi.py ipNumberOfController httpUseridOfController httpPasswordOfController IPNumberofAPorSwitch sshUserID sshPassword
#    ipNumberOfController should the ip number of the unfi controller
#    httpUseridOfController should be from field "http:  web UserID for CONTROLLER/UDM"  password from the next field
#    sshUserID and sshPassword should be from : "ssh unix UserID of AP,SW,GW - not UDM" and next password field
#    IPNumberofAPorSwitch should the ip number of any of your AP or switches
#    the userid and password of ssh can and should be different to the userid/password of http web access 
#

import json
import sys
import time
import os
import subprocess
import traceback
import requests
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


### methods  ###
def isValidIP(ip0):
	try:
		if ip0 == "localhost": 							return True

		ipx = ip0.split(".")
		if len(ipx) != 4:								return False

		else:
			for ip in ipx:
				try:
					if int(ip) < 0 or  int(ip) > 255: 	return False
				except:
														return False
		return True
	except	Exception as e:
		print("error {}".format(traceback.format_exc()))
	return False


def checkPing(IPnumber):
	try:
		for nn in range(2): # call ping twice max 
			#  wait 5 secs, do ping max twice per call
			retCode = subprocess.call('/sbin/ping -o -W 5 -c 2 '+IPnumber+' >/dev/null', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) # "call" will wait until its done and deliver retcode 0 or >0
			if retCode == 0: return 0 # ok 
			if nn == 0: time.sleep(1)

	except	Exception as e:
		print("error {}".format(traceback.format_exc()))
	return 1 # did not work 


def checkSSH(ip2, sshUid, sshPwd, sshFN):

	try:
		# create exp file for ssh to log into unifi device 
		f = open(sshFN, "w")
		f.write('set userID [lindex $argv 0 ] \n')
		f.write('set password [lindex $argv 1 ] \n')
		f.write('set ipNumber [lindex $argv 2 ] \n')
	
		f.write('set timeout 5\n')
		f.write('if {[lindex $argv 3] == "yes"} {spawn  ssh -o StrictHostKeyChecking=no $userID@$ipNumber} else {spawn  ssh $userID@$ipNumber}\n')
		f.write('expect {\n')
		f.write('    "(yes/no" {send "yes\\r"\n')  
		f.write('        expect "assword" { send "$password\n"} \n')
		f.write('    }\n')
		f.write('    "assword"    {  send "$password\r" \n')
		f.write('        expect {\n')
		f.write('            ":"     { send "exit\r" \n')
		f.write('                    }\n')
		f.write('            "refused"     {  exit 1  } \n')
		f.write('             "denied"     {  exit 2  } \n')
		f.write('        }\n')
		f.write('    }\n')
		f.write('}\n')
		f.write('expect eof\n')
		f.close()
		# execute ssh file
		cmd = "/usr/bin/expect -d test.exp '" + sshUid + "' '" + sshPwd + "' " + ip2 +" yes"
		print('ssh call: {} '.format(cmd))
		ret, err = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

		# do not remove temp exp file just created, should be done manually
		# os.remove(sshFN)

		return ret.decode('utf-8'), err.decode('utf-8')

	except	Exception as e:
		print("error {}".format(traceback.format_exc()))
	return "","" 


### here the testing is done  ###
def execTest(ip, uid, pwd, ip2, sshUid, sshPwd):
	# 
	try:

		# parameters used
		testPorts =  ["8443", "443"]
		param = { "200": {"os":"unifi_os", "unifiApiLoginPath":"/api/auth/login", "unifiApiWebPage":"/proxy/network/api/s" },
				  "302": {"os":"std",      "unifiApiLoginPath":"/api/login",      "unifiApiWebPage":"/api/s" }  }
		requestTimeout = 10
		sshLoginTags = ["busybox", "welcome","unifi","debian","edge","ubiquiti","ubnt","login"]
		usePort = ""
		unifiType = ""
		unifiControllerOS = ""
		sitename = ""
		sshFN = "test.exp"

		# print welcome message 
		print('\n')
		print('web http test: http ip: {:15s} , web uid: {:10s}, web pwd: {} '.format(ip,   uid,    pwd))
		print('ssh      test: AP   ip: {:15s} , ssh uid: {:10s}, ssh pwd: {} '.format(ip2, sshUid, sshPwd))
		print('  it will create a file "{}" for ssh tests, can be deleted when finished'.format(sshFN))
		print('===================== starting unifi connect test =======================================\n')

		# first test
		print('>>>>>>>getting port number ================================================ START')
		for port in testPorts:
			url = "https://{}:{}".format(ip, port)
			print('try :requests.head("{}", verify=False, timeout={}) '.format(url, requestTimeout))
			resp = requests.head(url, verify=False, timeout=10)
			if str(resp.status_code) in ["200", "302"]:
				print('response code ok: "{}"'.format(resp.status_code))
				usePort = port
				unifiType = str(resp.status_code)
				unifiControllerOS = param[unifiType]["os"]
				break
			else:
				print('response code bad:"{}"\n'.format(resp.status_code))


		if usePort == "":
			print('port search failed, tried: {}'.format(testPorts))
			return 

		session	 = requests.Session()
		print('port number search ok, use: {}; \ncontinuing test with params:{}=========='.format(usePort, param[unifiType]))
		print('getting port number ============ END\n')



		# second test
		url = "https://"+ip+":"+usePort+param[unifiType]["unifiApiLoginPath"]
		loginHeaders = {"Accept": "application/json", "Content-Type": "application/json", "referer": "/login"}
		dataLogin = json.dumps({"username":uid,"password":pwd}) 

		print(">>>>>>>requests trying to login ================================================ START")
		print(" with     url:{}\n   dataLogin:{}\nloginHeaders:{}".format(url, dataLogin, loginHeaders) )
		resp  = session.post(url,  headers=loginHeaders, data = dataLogin, timeout=requestTimeout, verify=False)
		if isinstance(resp, str):
			print("failed :{};".format(resp) )
			return 

		print("response code:{}".format( resp.status_code) )
		print("headers ----------")
		print(">>{}<<".format( resp.headers) )
		print("headers ----------END" )
		print("json site info  returned ----------")
		print(">>{}<<".format( resp.text) )
		print("site info ----------END" )

		if resp.text.find("AUTHENTICATION_FAILED_LIMIT_REACHED") > -1: 
			print("\nrequests login FAILED:    wait one minute and retry\n" )
			return 
		if resp.text.find("AUTHENTICATION_FAILED_INVALID_CREDENTIALS") > -1: 
			print("\nrequests login FAILED:    bad userid or password\n" )
			return 

		print("requests login =====END\n")



		# third test
		if 'X-CSRF-Token' in resp.headers:
			csrfToken = resp.headers['X-CSRF-Token']


		headers = {"Accept": "application/json", "Content-Type": "application/json"}
		if csrfToken != "":
			headers['X-CSRF-Token'] = csrfToken


		cookies_dict = requests.utils.dict_from_cookiejar(session.cookies)
		if unifiType == "200":
			cookies = {"TOKEN": cookies_dict.get('TOKEN')}
		else:
			cookies = {"unifises": cookies_dict.get('unifises'), "csrf_token": cookies_dict.get('csrf_token')}

		url	= "https://"+ip+":"+usePort+"/proxy/network/api/self/sites"
		print('>>>>>>>getting site name   ================================================ START ')
		print('with: session.get({}, cookies=cookies, headers=headers, timeout={}, verify=False) '.format(url, requestTimeout))
		ret	= session.get(url, cookies=cookies, headers=headers, timeout=requestTimeout, verify=False)
		print('response code: "{}"'.format(ret.status_code))

		try: sitename = json.loads(ret.text)["data"][0]["name"]
		except	Exception as e:
			print('>>{}<<'.format(ret.text))
			print("error {}".format(e))
			return 

		print('returned json----------')
		print('>>{}<<'.format(ret.text))
		print('returned json----------END')
		print("getting site name =====END\n")
	
	
		# fourth test
		print('>>>>>>>testing ssh to AP or SWITCH   ================================================ START ')
		print('looking for any of these ssh login tags: {}'.format(sshLoginTags))
		ret, err = checkSSH(ip2, sshUid, sshPwd, sshFN)
		ret = ret.replace("\r\n","\n").replace("\n\r","\n").replace("\r\r","\n").replace("\n\n","\n").replace("\n\n","\n").replace("\n\n","\n")
		test = ret.lower()
		loggedIn = ""
		for tag in sshLoginTags:
			if tag in test: 
				loggedIn = tag
				break
		if loggedIn != "":
			print('communication: via ssh: ------Start')
			print("stdOut>>\n"+ret+"<<")
			print('communication: via ssh: ------END')
			print('ssh test to AP/SWITCH successful;  tag: "{}" found'.format(loggedIn))
		else:
			print('ssh test to AP/SWITCH Failed;  none of the ssh login tags: {} found'.format(sshLoginTags))
			print('communication: via ssh: ------Start')
			print("stdOut>>\n"+ret+"<<")
			print("stdErr>>\n"+err+"<<")
			print('communication: via ssh: ------END')
		print("ssh test         =====END\n")


	except	Exception as e:
		print("error {}".format(traceback.format_exc()))
		return 

	## print result 
	print('\n=====finished======================================== in unifi plugin config set the indicated fields to the value shown:')
	print('                             "field name" = "value"' )
	print('    "http: web UserID for CONTROLLER/UDM" = "{}"'.format(uid) )
	print('       and next field     "...  password" = "{}"'.format(pwd) )
	if loggedIn:
		print('  "ssh unix UserID of AP,SW,GW - not UDM" = "{}"'.format(sshUid))
		print('       and next field       ".. password" = "{}"'.format(sshPwd))
	else:
		print('ssh test to AP/Switch Failed')
	print('               "..ipNumber of Controller" = "{}"'.format(ip) )
	print('       "site ID (not name) in eg http .." = "{}"'.format(sitename) )
	print(' "..controller port#, leave empty for .." = "{}"'.format(usePort) )
	print('                      "check port Number" = "do not check if port number ..."')

	print('=====finished======================================== END \n')

	return 
#############  end of methods #################



#############  main pgm starts here ##################
print('===================== starting unifi connect test, v 2.1 ================================')


###prel checks:
if len(sys.argv) != 7:
	print ("incorrect call should be: python3 testUnifi.py ipNumberOfController httpUseridOfController httpPasswordOfController    IPNumberofAPorSwitch sshUserID sshPassword")
	print ("Given:{}".format(sys.argv))
	exit()

if not isValidIP(sys.argv[1]):
	print ('incorrect call: bad ip number ipNumberOfController: "{}"'.format(sys.argv[1]))
	exit()

if checkPing(sys.argv[1]):
	print ('incorrect call: bad ip number ipNumberOfController: "{}"  does not answer'.format(sys.argv[1]))
	exit()

if not isValidIP(sys.argv[4]):
	print ('incorrect call: bad ip number IPNumberofAPorSwitch: "{}"'.format(sys.argv[4]))
	exit()

if checkPing(sys.argv[4]):
	print ('incorrect call: bad ip number IPNumberofAPorSwitch: "{}"  does not answer'.format(sys.argv[4]))
	exit()


## execute test 
execTest(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
exit()

