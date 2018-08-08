# -*- coding: utf-8 -*-

# BLE Scanning & get data from two Raspberry Pi use TCP/IP socket protocol
# One Raspberry Pi3 B+ model connected with two beacon
# 8/01/2018
import threading

import blescan
import sys
import bluetooth._bluetooth as bluez
import datetime
import socket
from time import sleep
import requests,json
headers = {'Content-Type' : 'application/json; charset=utf-8'}

def integrate(val, dt):
    return array([sum(val[0:i]) for i in range(0, len(val))])*dt
from numpy import *
from filter import *

HOST = '192.168.1.150' #Server ip address
PORT1 = 8000 #same with Sub1
PORT2 = 8001 #same with Sub2
deviceId = 1 #device id. only main raspi, every user's different

# Create socket1. Communicate with Sub1
s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create socket
print 'Socket1 Created!'
try:
	s1.bind( (HOST,PORT1) )
except socket.error:
	print 'Bind Failed..'
	sys.exit()
s1.listen(2)
print '..Socket Awaiting Messages..'
(conn1, addr1) = s1.accept()
print 'Connected with ', addr1

# Create socket2. Communicate with Sub2
s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create socket
print 'Socket2 Created!'
try:
        s2.bind( (HOST,PORT2) )
except socket.error:
        print 'Bind Failed..'
        sys.exit()
s2.listen(2)
print '..Socket Awaiting Messages..'
(conn2, addr2) = s2.accept()
print 'Connected with ', addr2
# ===================================================================================
data_num = 100
mu = 0
sigma = 0.3
x = linspace(0, 2*pi, data_num)
dt = 2*pi / data_num

a_trueval = sin(x)
v_trueval = integrate(a_trueval, dt)
x_trueval = integrate(v_trueval, dt)

#a_measured = a_trueval + random.normal(mu, sigma, data_num)
a_measured = random.normal(mu, sigma, data_num)
v_measured = integrate(a_measured, dt)
x_measured = integrate(v_measured, dt)

# Kalman Filter
F = matrix([[1, dt, (dt**2)/2], [0, 1, dt], [0, 0, 1]])
H = matrix([[0.0, 0.0, 1.0]])
Q = matrix([[0,0,0],[0,0,0],[0,0,0.001]])
R = matrix([[0.1]])
# --- mint filter ingredient ---
x_0 = matrix([[0], [0], [a_measured[0]]])
P_0 = matrix([[0,0,0],[0,0,0],[0,0,sigma**2]])
x__0 = matrix([[0], [0], [a_measured[0]]])
P__0 = matrix([[0,0,0],[0,0,0],[0,0,sigma**2]])
# --- skyblue filter ingredient ---
y_0 = matrix([[0], [0], [a_measured[0]]])
Q_0 = matrix([[0,0,0],[0,0,0],[0,0,sigma**2]])
y__0 = matrix([[0], [0], [a_measured[0]]])
Q__0 = matrix([[0,0,0],[0,0,0],[0,0,sigma**2]])
# --- value set of mint estimote(I'm not sure its correct) ---
filter_KF_mint_estimote = KF(F, H, Q, R, x_0, P_0)
filter_KF_mint_distance = KF(F, H, Q, R, x__0, P__0)
a_KF = [0.0]*data_num
v_KF = [0.0]*data_num
x_KF = [0.0]*data_num
a_KF[0] = x_0.item(2,0)
v_KF[0] = x_0.item(1,0)
x_KF[0] = x_0.item(0,0)
a__KF = [0.0]*data_num
v__KF = [0.0]*data_num
x__KF = [0.0]*data_num
a__KF[0] = x__0.item(2,0)
v__KF[0] = x__0.item(1,0)
x__KF[0] = x__0.item(0,0)
# --- value set of skyblue estimote(I'm not sure its correct) ---
filter_KF_skyblue_estimote = KF(F, H, Q, R, y_0, Q_0)
filter_KF_skyblue_distance = KF(F, H, Q, R, y__0, Q__0)
a___KF = [0.0]*data_num
v___KF = [0.0]*data_num
x___KF = [0.0]*data_num
a___KF[0] = y_0.item(2,0)
v___KF[0] = y_0.item(1,0)
x___KF[0] = y_0.item(0,0)
a____KF = [0.0]*data_num
v____KF = [0.0]*data_num
x____KF = [0.0]*data_num
a____KF[0] = y__0.item(2,0)
v____KF[0] = y__0.item(1,0)
x____KF[0] = y__0.item(0,0)
# ===================================================================================

dev_id = 0
try:
	sock = bluez.hci_open_dev(dev_id)
	print "ble thread started"

except:
	print "error accessing bluetooth device..."
    	sys.exit(1)

blescan.hci_le_set_scan_parameters(sock)
blescan.hci_enable_le_scan(sock)

sub1_ble1 = 0.0 #distance between sub1(eat) and ble1(dog)
sub1_ble2 = 0.0 #distance between sub1(eat) and ble2(trouble)
sub2_ble1 = 0.0 #distance between sub2(wait) and ble1(dog)
sub2_ble2 = 0.0 #distance between sub2(wait) and ble2(trouble)
main_ble1 = 0.0 #distance between main(sleep) and ble1(dog)
main_ble2 = 0.0 #distance between main(sleep) and ble2(trouble)

#sleepCnt = 0
eatstartTime = datetime.datetime(2018,1,1) # just initialization
waitstartTime = datetime.datetime(2018,1,1)
sleepstartTime = datetime.datetime(2018,1,1)
troublestartTime = datetime.datetime(2018,1,1)
#eatCnt = 0
#waitCnt = 0
#troubleCnt = 0
petStatus = 0 # 0:plain 1:eat 2:wait 3:sleep 4:trouble
res = requests.post('http://114.108.81.223:3000/getStatusFromRpi', headers=headers, data=json.dumps({'rpiId':1}))
post = res.json()
petStatus = post['status'] # get before status from server

# send data to server using device id and pet status
def sendStatus(device, status):
	res = requests.post('http://114.108.81.223:3000/setStatus', headers=headers, data=json.dumps({'rpiId':deviceId, 'status':petStatus}))

# get distance data from sub1 and sub2
def mappingdatafromSubs():
	global sub1_ble1
	global sub1_ble2
	global sub2_ble1
	global sub2_ble2
        data = conn1.recv(1024)
        if len(data) < 1:
                return 0
        connList = data.split('&')
        n = len(connList)
        for i in range(n):
                dummyList = connList[i].split('@')
                if len(dummyList) != 3:
                        break
                if len(dummyList[2]) < 1:
                        break
                if dummyList[0] == "S1" and dummyList[1] == "toTrouble":
                        dist = float(dummyList[2])
                        sub1_ble2 = dist
                elif dummyList[0] == "S1" and dummyList[1] == "toDog":
                        dist = float(dummyList[2])
                        sub1_ble1 = dist
        data = conn2.recv(1024)
        if len(data) < 1:
                return 0
        connList = data.split('&')
        n = len(connList)
        for i in range(n):
                dummyList = connList[i].split('@')
                if len(dummyList) != 3:
                        break
                if len(dummyList[2]) < 1:
                        break
                if dummyList[0] == "S2" and dummyList[1] == "toTrouble":
                        dist = float(dummyList[2])
                        sub2_ble2 = dist
                elif dummyList[0] == "S2" and dummyList[1] == "toDog":
                        dist = float(dummyList[2])
                        sub2_ble1 = dist

def checkEat(r,t): #1
        global petStatus
        global eatstartTime
        range = r
	keeptime = t
        if sub1_ble1 <= range and petStatus != 1 and eatstartTime == datetime.datetime(2018,1,1) :
                print "start counting eat time"
                eatstartTime = datetime.datetime.now()
        staytime = (datetime.datetime.now()-eatstartTime).total_seconds()
        print "eat staytime: ", staytime
        if 0 < staytime < 1000 and sub1_ble1 > range :
                print "count reset"
                eatstartTime = datetime.datetime(2018,1,1)
        if keeptime < staytime < 1000 and petStatus != 1 :
                print "My pet is eatting"
                eatstartTime = datetime.datetime(2018,1,1)
                petStatus = 1
                sendStatus(deviceId, petStatus)
                return 1
        elif petStatus == 1 and sub1_ble1 > range :
                print "My pet finish eatting"
                petStatus = 0
                sendStatus(deviceId, petStatus)
                return 0

def checkWait(r,t): #2
        global petStatus
        global waitstartTime
        range = r
	keeptime = t
        if sub2_ble1 <= range and petStatus != 2 and waitstartTime == datetime.datetime(2018,1,1) :
                print "start counting wait time"
                waitstartTime = datetime.datetime.now()
        staytime = (datetime.datetime.now()-waitstartTime).total_seconds()
        print "wait staytime: ", staytime
        if 0 < staytime < 1000 and sub2_ble1 > range :
                print "count reset"
                waitstartTime = datetime.datetime(2018,1,1)
        if keeptime < staytime < 1000 and petStatus != 2 :
                print "My pet is waiting"
                waitstartTime = datetime.datetime(2018,1,1)
                petStatus = 2
                sendStatus(deviceId, petStatus)
                return 2
        elif petStatus == 2 and sub2_ble1 > range :
                print "My pet finish waiting"
                petStatus = 0
                sendStatus(deviceId, petStatus)
                return 0

def checkSleep(r,t,pdist): #3
        global petStatus
        global sleepstartTime
        range = r
	keeptime = t
	if pdist == 0: #starting value
		return 0
	distgap = abs(main_ble1 - pdist)
        if main_ble1 <= range and distgap < 0.1 and petStatus != 3 and sleepstartTime == datetime.datetime(2018,1,1) :
                print "start counting sleep time"
                sleepstartTime = datetime.datetime.now()
        staytime = (datetime.datetime.now()-sleepstartTime).total_seconds()
        print "sleep staytime: ", staytime
        if 0 < staytime < 1000 and main_ble1 > range :
                print "count reset"
                sleepstartTime = datetime.datetime(2018,1,1)
        if keeptime < staytime < 1000 and petStatus != 3 :
                print "My pet is sleeping"
                sleepstartTime = datetime.datetime(2018,1,1)
                petStatus = 3
                sendStatus(deviceId, petStatus)
                return 3
        elif petStatus == 3 and main_ble1 > range :
                print "My pet finish sleeping"
                petStatus = 0
                sendStatus(deviceId, petStatus)
                return 0

def checkTrouble(r,t): #4
        global petStatus
        global troublestartTime
        range = r
	keeptime = t
        dist = ( (main_ble2-main_ble1)**2+(sub1_ble2-sub1_ble1)**2+(sub2_ble2-sub2_ble1)**2 )**0.5
        print "distance between dog and trouble area: ", dist
        if dist <= range and petStatus != 4 and troublestartTime == datetime.datetime(2018,1,1) :
                print "start counting trouble time"
                troublestartTime = datetime.datetime.now()
        staytime = (datetime.datetime.now()-troublestartTime).total_seconds()
        print "trouble staytime: ", staytime
        if 0 < staytime < 1000 and dist > range :
                print "count reset"
                troublestartTime = datetime.datetime(2018,1,1)
        if keeptime < staytime < 1000 and petStatus != 4 :
                print "My pet is trouble maker"
                troublestartTime = datetime.datetime(2018,1,1)
                petStatus = 4
                sendStatus(deviceId, petStatus)
                return 4
        elif petStatus == 4 and dist > range :
                print "My pet finish troubling"
                petStatus = 0
                sendStatus(deviceId, petStatus)
                return 0

while True:
	_x = 0 # filtering value of beacon1's RSSI
	__x = 0 # filtering value of DISTANCE between raspi and beacon1
	_y = 0 # filtering value of beacon2's RSSI
	__y = 0 # filtering value of DISTANCE between raspi and beacon2
	past_sub1_ble1 = sub1_ble1
	past_sub1_ble2 = sub1_ble2
	past_sub2_ble1 = sub2_ble1
	past_sub2_ble2 = sub2_ble2
	past_main_ble1 = main_ble1
	past_main_ble2 = main_ble2

	returnedList = blescan.parse_events_get_distance(sock, 100)
	n = len(returnedList)
	for i in range(n) :
		dummyList = returnedList[i].split(',') # [0]:MAC Addr / [1]:Major number / [2]:Tx Power / [3]:RSSI
		#if "da:66:3d:70:27:1f" == dummyList[0]: # Trouble Location Beacon
		#	#print "----- mint estimote(", dummyList[0], ") -----"
                if "10:ce:a9:f5:68:4a" == dummyList[0]: # Trouble Location Beacon
                        #print "----- mint estimote(", dummyList[0], ") -----"
			#print "not smoothing rssi: ", dummyList[3]
			rssi = float(dummyList[3])
			_x = filter_KF_mint_estimote.update(rssi) #filtering mint estimote rssi
		        a_KF[i] = _x.item(2,0) #filtering value
		        v_KF[i] = _x.item(1,0)
		        x_KF[i] = _x.item(0,0)
			sm_rssi = float(_x.item(2,0))
			#print "RSSI: ", sm_rssi
			tx = float(dummyList[2])
			squareRoot = (tx-sm_rssi)/20
			#print "squareRoot: ", squareRoot
			distance = 10 ** squareRoot
			#print "not smoothing distance: ", distance
			__x = filter_KF_mint_distance.update(distance) #filtering distance between raspi and beacon1
                        a__KF[i] = __x.item(2,0) #filtering value
                        v__KF[i] = __x.item(1,0)
                        x__KF[i] = __x.item(0,0)
			sm_distance = float(__x.item(2,0))
			#print "Distance: ", sm_distance, "\n"
			main_ble2 = sm_distance
                elif "94:e3:6d:54:96:7c" == dummyList[0]: # Dog Beacon
                        #print "----- deepblue estimote(", dummyList[0], ") -----"
                        #print "not smoothing rssi: ", dummyList[3]
                        rssi = float(dummyList[3])
                        _y = filter_KF_skyblue_estimote.update(rssi) #filtering skyblue estimote rssi
                        a___KF[i] = _y.item(2,0) #filtering value
                        v___KF[i] = _y.item(1,0)
                        x___KF[i] = _y.item(0,0)
                        sm_rssi = float(_y.item(2,0))
                        #print "RSSI: ", sm_rssi
                        tx = float(dummyList[2])
                        squareRoot = (tx-sm_rssi)/20
                        #print "squareRoot: ", squareRoot
                        distance = 10 ** squareRoot
                        #print "not smoothing distance: ", distance
                        __y = filter_KF_skyblue_distance.update(distance) #filtering distance between raspi and beacon2
                        a____KF[i] = __y.item(2,0) #filtering value
                        v____KF[i] = __y.item(1,0)
                        x____KF[i] = __y.item(0,0)
                        sm_distance = float(__y.item(2,0))
                        #print "Distance: ", sm_distance, "\n"
			main_ble1 = sm_distance
	#get data from two sub raspberry pi
	mappingdatafromSubs()

#	data = conn1.recv(1024)
#	if len(data) < 1:
#		continue
#	connList = data.split('&')
#	n = len(connList)
#	for i in range(n):
#		dummyList = connList[i].split('@')
#		if len(dummyList) != 3:
#			break
#		if len(dummyList[2]) < 1:
#			break
#		if dummyList[0] == "S1" and dummyList[1] == "toTrouble":
#			dist = float(dummyList[2])
#			sub1_ble2 = dist
#		elif dummyList[0] == "S1" and dummyList[1] == "toDog":
#			dist = float(dummyList[2])
#			sub1_ble1 = dist
#
#	data = conn2.recv(1024)
#	if len(data) < 1:
#		continue
#	connList = data.split('&')
#	n = len(connList)
#	for i in range(n):
#		dummyList = connList[i].split('@')
#		if len(dummyList) != 3:
#			break
#		if len(dummyList[2]) < 1:
#			break
#		if dummyList[0] == "S2" and dummyList[1] == "toTrouble":
#			dist = float(dummyList[2])
#			sub2_ble2 = dist
#		elif dummyList[0] == "S2" and dummyList[1] == "toDog":
#			dist = float(dummyList[2])
#			sub2_ble1 = dist

	checkEat(0.15,5) #range(meter), stay time(sec)
	checkWait(0.15,10) #range(meter), stay time(sec)
	checkSleep(0.15,10,past_main_ble1) #range(meter), stay time(sec), last queue distance(main to dog)
	checkTrouble(0.8,10) #range(meter), stay time(sec)

	print " ----- RESULT -----"
	print datetime.datetime.now()
	print "main_ble1: ", main_ble1
	print "main_ble2: ", main_ble2
	print "sub1_ble1: ", sub1_ble1
	print "sub1_ble2: ", sub1_ble2
	print "sub2_ble1: ", sub2_ble1
	print "sub2_ble2: ", sub2_ble2
	print "==================="
	if petStatus == 0:
		print "plain status"
	elif petStatus == 1:
		print "eat status"
	elif petStatus == 2:
		print "wait status"
	elif petStatus == 3:
		print "sleep status"
	elif petStatus == 4:
		print "trouble status"
	print "==================="
