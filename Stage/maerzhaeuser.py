# -*- coding: utf-8 -*-
"""
Created on Sat Sep 15 14:35:05 2017

@author: Benedikt Kratochwil

Adapted code from Yuya from the Immamoglu Group
"""


from __future__ import division, print_function, unicode_literals # python3 compatibility with encode()

import ctypes
import sys
import time
import re
import serial
import threading
import numpy as np

def synchronized(lock):
    """ Synchronization decorator. """
    def wrap(f):
        def newFunction(*args, **kw):
            lock.acquire()
            try:
                return f(*args, **kw)
            finally:
                lock.release()
        return newFunction
    return wrap

rlock = threading.RLock()


## loadTangoDLL
#
# Load the Tango DLL. Some Marzhauser stages use this DLL instead of
# RS-232 based communication.
#
#tango = 0
#def loadTangoDLL():
#    global tango
#    if (tango == 0):
#        tango = ctypes.windll.LoadLibrary("C:\Program Files (x86)\SwitchBoard\Tango_DLL")
#
#instantiated = 0

## MarzhauserRS232
#
# Marzhauser RS232 interface class.
#
class Marzhauser(object):

    ## __init__
    #
    # Connect to the Marzhuaser stage at the specified port.
    #
    # @param port The RS-232 port name (e.g. "COM1").
    # @param wait_time (Optional) How long (in seconds) for a response from the stage.
    #
    def __init__(self, port, wait_time=0.02, simulation=False):
        self.simulation = simulation
        if not self.simulation:
            self.__ser__ = serial.Serial(port, timeout = 1.0, baudrate = 115200)
        self.x = 0.0
        self.y = 0.0
        self.wait_time = wait_time
        self.end_of_line = "\r"
        

    @synchronized(rlock)
    def getStatus(self):
        test = self._rawQuery("?version")
        print(test)

    @synchronized(rlock)
    def getPos(self):
        if self.simulation:
            return (self.x,self.y)
        else:
            ans = self._rawQuery("?pos")
            match = re.search('-?[0-9]+\.[0-9]+\s*-?[0-9]+\.[0-9]+', ans)
            ans = ans[match.span()[0]:match.span()[1]]
            (x, y) = map(float, ans.split())
#            print('x', x)
#            print('y', y)
            return (-x, y)

    @synchronized(rlock)
    def getPosSampleCoordinates(self, edge1, edge2):
        '''
        This function gives pack the position of the stage in sample coord.
        
        Parameters
        ----------
        edge1:  tuple
                Coordinates of SW edge in stage coordinates.
        edge2:  tuple
                Coordinates of SE edge in stage coordinates.
        '''          
        if self.simulation:
            p = (self.x, self.y)
            theta = np.arctan2(edge2[1] - edge1[1], edge2[0] - edge1[0]) 
            rot = np.array([[np.cos(theta), -np.sin(theta)],[np.sin(theta), np.cos(theta)]])
            r  = np.dot(np.array(p)-np.array(edge1), rot)            
            return (r[0], r[1])
        else:
            p = self.getPos()
            theta = np.arctan2(edge2[1] - edge1[1], edge2[0] - edge1[0]) 
            rot = np.array([[np.cos(theta), -np.sin(theta)],[np.sin(theta), np.cos(theta)]])
            r  = np.dot(np.array(p)-np.array(edge1), rot)            
            return (r[0], r[1])

    @synchronized(rlock)
    def setPos(self, x, y):
        if self.simulation:
            self.x = x
            self.y = y
        else:
            self._rawQuery("!pos " + str(-x) + " " + str(y))

    @synchronized(rlock)
    def setPosZero(self):
        if self.simulation:
            self.x =0 
            self.y = 0 
        else:
            self.setPos(0, 0)

    @synchronized(rlock)
    def goAbsolute(self, x, y):
        if self.simulation:
            self.x = x
            self.y = y
        else:
            self._rawWrite("!moa " + str(-x) + " " + str(y))

    @synchronized(rlock)
    def goAbsoluteSampleCoordinates(self, x, y, edge1, edge2):
        '''
        This function moves the stage to the position (x,y) in sample 
        coordinates.
        
        Parameters
        ----------
        x:      float
                Desired x-position in sample coordinates.
        y:      float
                Desired y-position in sample coordinates.
        edge1:  tuple
                Coordinates of SW edge in stage coordinates.
        edge2:  tuple
                Coordinates of SE edge in stage coordinates.
        '''   
        # calculate x and y to stage-coordinates and then goAbsolute
        p = (x, y)
        theta = np.arctan2(edge2[1] - edge1[1], edge2[0] - edge1[0])
        rot = np.array([[np.cos(theta), np.sin(theta)],[-np.sin(theta), np.cos(theta)]])
        r = np.dot(np.array(p), rot) + edge1
        self.goAbsolute(r[0], r[1])

    @synchronized(rlock)
    def goRelativeSampleCoordinates(self, dx, dy, edge1, edge2):    
        '''
        This function moves the stage by dx (dy) in x (y) direction in sample 
        coordinates.
        
        Parameters
        ----------
        dx:     float
                Value to move in x direction in sample coordinates.
        dy:     float
                Value to move in y direction in sample coordinates.
        edge1:  tuple
                Coordinates of SW edge in stage coordinates.
        edge2:  tuple
                Coordinates of SE edge in stage coordinates.
        '''   
        # getting the x and y positions in sample-coordinates
        x_sample, y_sample = self.getPosSampleCoordinates(edge1, edge2)
        # go absolute in samplecoordinates an adding dx, dy
        self.goAbsoluteSampleCoordinates(x_sample+dx, y_sample+dy, edge1, edge2)       

    @synchronized(rlock)
    def goRelative(self, dx, dy):
        if self.simulation:
            self.x += dx
            self.y += dy
        else:
            self._rawWrite("!mor " + str(-dx) + " " + str(dy))

    def _rawWrite(self, command):
        self.__ser__.flush()
        self.__ser__.write( (command + self.end_of_line).encode() )

    def _rawQuery(self, command):
        self._rawWrite(command)
        time.sleep(10 * self.wait_time)
        ans = ""
        ans_len = self.__ser__.inWaiting()
        while ans_len:
            res = self.__ser__.read(ans_len)
            ans += str(res, 'utf-8') # python3: needs conversion to str
            time.sleep(self.wait_time)
            ans_len = self.__ser__.inWaiting()
        if len(ans) > 0:
            return ans

    # For debug
    def rawQuery(self, command):
        return self._rawQuery(command)

    def close(self):
        if self.simulation:
            return
        else:
            self.__ser__.close()


#class MarzhauserDLL(object):
#
#    ## __init__
#    #
#    # Connect to the Marzhuaser stage.
#    #
#    # @param port A RS-232 com port name such as "COM1".
#    #
#    def __init__(self, port):
#        self.wait = 1 # move commands wait for motion to stop
#
#        # Load the Tango library.
#        loadTangoDLL()
#
#        # Check that this class has not already been instantiated.
#        global instantiated
#        assert instantiated == 0, "Attempt to instantiate two Marzhauser stage classes."
#        instantiated = 1
#
#        # Connect to the stage.
#        self.good = 1
#        temp = ctypes.c_int(-1)
#        tango.LSX_CreateLSID(ctypes.byref(temp))
#        self.LSID = temp.value
#        error = tango.LSX_ConnectSimple(self.LSID, 1, port, 115200, 0)
#        if error:
#            print ("Marzhauser error", error)
#            self.good = 0
#
#    ## getStatus
#    #
#    # @return True/False if we are actually connected to the stage.
#    #
#    def getStatus(self):
#        return self.good
#
#    ## goAbsolute
#    #
#    # @param x Stage x position in um.
#    # @param y Stage y position in um.
#    #
#    def goAbsolute(self, x, y):
#        if self.good:
#            # If the stage is currently moving due to a jog command
#            # and then you try to do a positional move everything
#            # will freeze, so we stop the stage first.
#            self.jog(0.0,0.0)
#            X = ctypes.c_double(x)
#            Y = ctypes.c_double(y)
#            ZA = ctypes.c_double(0.0)
#            tango.LSX_MoveAbs(self.LSID, X, Y, ZA, ZA, self.wait)
#
#    ## goRelative
#    #
#    # @param dx Amount to displace the stage in x in um.
#    # @param dy Amount to displace the stage in y in um.
#    #
#    def goRelative(self, dx, dy):
#        if self.good:
#            self.jog(0.0,0.0)
#            dX = ctypes.c_double(dx)
#            dY = ctypes.c_double(dy)
#            dZA = ctypes.c_double(0.0)
#            tango.LSX_MoveRel(self.LSID, dX, dY, dZA, dZA, self.wait)
#
#    def jog(self, x_speed, y_speed):
#        if self.good:
#            c_xs = ctypes.c_double(x_speed)
#            c_ys = ctypes.c_double(y_speed)
#            c_zr = ctypes.c_double(0.0)
#            tango.LSX_SetDigJoySpeed(self.LSID, c_xs, c_ys, c_zr, c_zr)
#
#import time
#import serial
#import threading
#import re
#
#
#
#class Maerzhaeuser(object):
#    '''
#    Class to communicate with the Stage. It allows to handle x, y axis and the
#    rotation.
#    '''
#    def __init__(self, port, wait_time=0.02):
#        '''
#        Initialize the stage and the communications.
#
#        Parameters
#        ----------
#
#        port:   String
#                String telling at which port the stage is connected. For
#                example 'COM4'
#        wait_time:  float (optional)
#                    Float defining the time the program waits for an answer of
#                    the stage.
#        '''
#
#        # Open the serial connection
#        self.__ser__ = serial.Serial(port, timeout=1.0, baudrate=115200)
#        # Defining the x and y parameters of the stage
#        self.x = 0.0
#        self.y = 0.0
#        # Initializing the wait time
#        self.wait_time = wait_time
#        # Initialize the end of line character
#        self.end_of_line = "\r"
#        # TODO: Why do we have to lock
#        self.lock = threading.Lock()
#
#    def getStatus(self):
#        '''
#        Function to get the STatus of the stage'
#        '''
#
#        test = self._rawQuery("?version")
#        print(test)
#
#    def getPos(self):
#        '''
#        Function to get the Position of the stage.
#
#        Return
#        ------
#
#        (x,y):  tuple
#                Returns the tuple with the x and y coordinate
#        '''
#        ans = self._rawQuery("?pos")
#        match = re.search('-?[0-9]+\.[0-9]+\s*-?[0-9]+\.[0-9]+', ans)
#        ans = ans[match.span()[0]:match.span()[1]]
#        (x, y) = map(float, ans.split())
#        return (x, y)
#
#    def setPos(self, x, y):
#        '''
#        Function to set the stage x and y position. When you run this command,
#        it will initialize the current  Position as the (x,y) coordinates given
#        as parameters
#
#        Parameters
#        ----------
#
#        x:  float
#            Float determining the absolute x Axis position of the stage in
#            instrument units.
#        y:  float
#            Float determining the absolute x Axis position of the stage in
#            instrument units.
#        '''
#        self._rawQuery("!pos " + str(x) + " " + str(y))
#
#    def setPosZero(self):
#        '''
#        Initializes the current stage position as (0,0)
#        '''
#
#        self.setPos(0, 0)
#
#    def goAbsolute(self, x, y):
#        '''
#        Movews the stage for the absolute value (x,y)
#
#        Parameters
#        ----------
#        x:  float
#            Moves the stage to the absolute x-Ais value x
#        y:  float
#            Moves the stage to the absolute y-Axis value y
#
#        '''
#        self._rawWrite("!moa " + str(x) + " " + str(y))
#
#    def goRelative(self, dx, dy):
#        '''
#        Function to move the stage for relative values dx and dy.
#
#        Parameters
#        ----------
#        dx: float
#            Value on which the x-Axis value is shifted.
#        dy: float
#            Value on which the y-Axis value is shifted.
#        '''
#        self._rawWrite("!mor " + str(dx) + " " + str(dy))
#
#    def _rawWrite(self, command):
#        '''
#        Private Function whicgh will write the stage commands.
#
#        Parmaters
#        ---------
#
#        command:    string
#                    String command which is send over the serial connection to
#                    the instrument.
#        '''
#        # Flush will make sure that the serial connection waits till all the
#        # data is written
#        self.__ser__.flush()
#        self.__ser__.write((command + self.end_of_line).encode())
#
#    def _rawQuery(self, command):
#        '''
#        Function to handle Queries to the instrument
#
#        The idea is to send the command to the instrument and then we wait
#        10 times the waiting time to listen for an answer.
#
#        In a second step one waits for the answer of the isntrument. We check
#        for a new answer after a timestep defined by the self.wait_time
#        variable. If we don't get a signal anymore we return the answer back
#
#
#        Parameters
#        ----------
#        command:    string
#                    String command which will trigger the query on the
#                    insturment.
#
#        Returns
#        -------
#        ans:    string
#                String containing the instrument answer.
#        '''
#        with self.lock:
#            self._rawWrite(command)
#            time.sleep(10 * self.wait_time)
#            ans = ""
#            ans_len = self.__ser__.inWaiting()
#            while ans_len:
#                ans += self.__ser__.read(ans_len).decode()
#                time.sleep(self.wait_time)
#                ans_len = self.__ser__.inWaiting()
#            if len(ans) > 0:
#                return ans
#
#    # For debug
#    # def rawQuery(self, command):
#    #   return self._rawQuery(command)
#
#    def close(self):
#        '''
#        Function to nicely close the serial connection to the instrument.
#        '''
#        self.__ser__.close()


if __name__ == "__main__":
    mw = Marzhauser("COM3",simulation = False)
    print(mw.getPos())
    #mw.goRelative(0.075,0)
    #mw.goAbsolute(-17.4001, -8.4466)
#    mw.goRelative(1,1)
#    time.sleep(1)
#    print(mw.getPos())
    #mw.getStatus()
    #mw.setPos(0,0)
    #time.sleep(2)
    #print(mw.getPos())
##    import time
##    time.sleep(5)
#    print(mw.getPos())
#    mw.goAbsolute(10,-3)
#    print(mw.getPos())
    
    
    #mw.setPos( 10, 10) 
    #print(mw.getPos())
    #mw.goAbsolute( 12, 12)
    #print(mw.getPos())
#    mw.goRelative(5, 2)
#    time.sleep(2)
#    print(mw.getPos())
    

    # The live feed is mirrored! Still either x or y is in the wrong direction.
    
    mw.close()
   
    
#    setPosZero()
#    goAbsolute(x,y)
#    goRelative(dx,dy)
    
    
    
#    mw.close()
#    time.sleep(1)
#    
#    mw2 =  Marzhauser("COM4",simulation = False)
#    
#    print(mw2.getPos())
#    mw2.close()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    