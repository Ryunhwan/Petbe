port = 8016
# test BLE Scanning software
# One Raspberry Pi3 B+ model connected with two beacon
# 7/23/2018
import threading

import blescan
import sys
import bluetooth._bluetooth as bluez
from datetime import datetime
import socket
from time import sleep

def integrate(val, dt):
    return array([sum(val[0:i]) for i in range(0, len(val))])*dt
from numpy import *
from filter import *

DeviceName = "S1" #Sub raspi1, Eatting motion detect

# Create socket (client)
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #create socket
hostip = '192.168.1.52'	#Server ip address
#port = 8030 #port number, must be same with server's
while True:
	try:
		s.connect( (hostip, port) )
		print '...Socket Connected to [' + hostip + ']'
		break
	except socket.error:
		print 'connect fail. retry'


#kalmal filter setting
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

dev_id = 0
try:
	sock = bluez.hci_open_dev(dev_id)
	print "ble thread started"

except:
	print "error accessing bluetooth device..."
    	sys.exit(1)

blescan.hci_le_set_scan_parameters(sock)
blescan.hci_enable_le_scan(sock)

while True:
        _x = 0 # filtering value of mint estimote's RSSI
        __x = 0 # filtering value of DISTANCE between raspi and mint estimote
        _y = 0 # filtering value of skyblue estimote's RSSI
        __y = 0 # filtering value of DISTANCE between raspi and skyblue estimote
        returnedList = blescan.parse_events_get_distance(sock, 100)
        now = datetime.now()
        now = str(now)
        n = len(returnedList)
        for i in range(n) :
                data = ''
                sm_distance = 0.0
                dummyList = returnedList[i].split(',') # [0]:MAC Addr / [1]:Major number / [2]:Tx Power / [3]:RSSI
                #if "da:66:3d:70:27:1f" == dummyList[0]: # Trouble Location Beacon
                if "10:ce:a9:f5:68:4a" == dummyList[0]: # Trouble Location Beacon
                        print "----- trouble beacon(", dummyList[0], ") -----"
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
                        __x = filter_KF_mint_distance.update(distance) #filtering distance between raspi and mint estimote
                        a__KF[i] = __x.item(2,0) #filtering value
                        v__KF[i] = __x.item(1,0)
                        x__KF[i] = __x.item(0,0)
                        sm_distance = float(__x.item(2,0))
                        sm_distance = str(sm_distance)
                        data = DeviceName + '@' + "toTrouble" + '@' + sm_distance # DeviceName @ to destination @ distance
			data += '&'
                        print data, "\n"
                        s.send(data) #send the encoding data
                elif "94:e3:6d:54:96:7c" == dummyList[0]: # dog beacon
                        print "----- dog beacon(", dummyList[0], ") -----"
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
                        __y = filter_KF_skyblue_distance.update(distance) #filtering distance between raspi and skyblue estimote
                        a____KF[i] = __y.item(2,0) #filtering value
                        v____KF[i] = __y.item(1,0)
                        x____KF[i] = __y.item(0,0)
                        sm_distance = float(__y.item(2,0))
                        sm_distance = str(sm_distance)
                        data = DeviceName + '@' + "toDog" + '@' + sm_distance # DeviceName @ to destination @ distance
                        data += '&'
			print data, "\n"
                        s.send(data) #send the encoding data
