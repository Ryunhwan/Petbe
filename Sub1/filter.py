# filter.py
 
from numpy import *
from numpy.linalg import *
 
# Low Pass Filter
class LPF:
    def __init__(self, a, x_0):
        self.a = a
        self.x_last = x_0
 
    def update(self, z):
        x = self.a*self.x_last + (1.0-self.a)*z
        self.x_last = x
        return x
 
# Linear Kalman Filter
class KF:
    def __init__(self, F, H, Q, R, x_0, P_0):
        self.F_last = F
        self.H_last = H
        self.Q_last = Q
        self.R_last = R
        self.x_last = x_0
        self.P_last = P_0
 
    def update(self, z, F=None, H=None, Q=None, R=None):
        # update old data
        if not F: F = self.F_last
        else: self.F_last = F
        if not H: H = self.H_last
        else: self.H_last = H
        if not Q: Q = self.Q_last
        else: self.Q_last = Q
        if not R: R = self.R_last
        else: self.R_last = R
        # Run Linear Kalman Filter Algorithm
        x = F*self.x_last                                    # predict x
        P = F*self.P_last*F.transpose() + Q                    # predict Q
        K_k = P*H.transpose() * inv(H*P*H.transpose() + R)    # calc Kalman gain
        x = x + K_k*(z - H*x)                                # calc x
        P = P - K_k*H*P                                        # calc P
        # update old data
        self.x_last = x
        self.P_last = P 
        # return
        return x

