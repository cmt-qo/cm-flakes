# -*- coding: utf-8 -*-
"""
Created on Fri Jun 29 16:50:58 2018

@author: Benedikt
"""

import win32com.client


class Microscope(object):

    def __init__(self, simulation=False, z0=None):
        '''
        Parameters
        ----------
        z0:         int
                    only used when in simulation. It is in instrument units!
        '''
        self.simulation = simulation
        if not self.simulation:
            self.microscopeObject = win32com.client.Dispatch('Nikon.LvMic.NikonLv')
            self.zPos = None
            self.currentObjective = None
            self.ObjectivPositions = [5, 10, 20, 50, 100]
        else:
            self.zPos = z0
            self.ObjectivPositions = [5, 10, 20, 50, 100]
            self.currentObjectiveIndex = 1
            self.currentObjective = self.ObjectivPositions[self.currentObjectiveIndex]
     #   self.getZPosition()

#        self.currentObjective = self.getCurrentObjective()
        pass

    def moveObjectiveForward(self):
        '''
        Function to move to the next higher Objective.
        '''
        # self.isMoveallowed()
        if self.simulation:
            self.currentObjectiveIndex += 1
            self.currentObjective = self.ObjectivPositions[self.currentObjectiveIndex]
        else:          
            self.microscopeObject.Nosepiece.Forward()
            self.currentObjective = self.getCurrentObjective()

    def moveObjectiveBackwards(self):
        '''
        Function to move to the next lower Objective
        '''
        # self.isMoveAllowed()
        if self.simulation:
            self.currentObjectiveIndex -= 1
            self.currentObjective = self.ObjectivPositions[self.currentObjectiveIndex]
        else:          
            self.microscopeObject.Nosepiece.Reverse()
            self.currentObjective = self.getCurrentObjective()

    def moveZAbsolute(self, value): #here no conversion factor?
        if self._isAbsoluteMoveAllowed(value):
            if self.simulation:
                self.zPos = value
            else:
                self.microscopeObject.ZDrive.MoveAbsolute(value)
            
        else:
            print("Move not allowed")
    
    def getCurrentObjective(self):
        '''
        Function to get the current Objective

        Returns
        -------
        current_obj:    int
                        Integer 5, 10, 20, 50 or 100.
        '''
        if self.simulation:
            return self.currentObjective
        else:
            self.currentObjective = self.microscopeObject.Nosepiece.Position()
            # This gives an integer 5, 10, 20, 50 or 100
            return self.ObjectivPositions[self.currentObjective - 1]

    def moveZRelative(self, dz):    #here no conversion factor?
        '''
        Function to move the Objective relative to the current position.

        Parameters
        ----------
        dz: int
            Integer value by which the current posistion is shifted.
        '''
        if self._isRelativeMoveAllowed(dz):       
            if self.simulation:
                self.zPos += dz
            else:
                # self.isMoveAllowed 
                self.microscopeObject.ZDrive.MoveRelative(dz)
                self.getZPosition()
        else:
            print("Move not allowed")
            

    def getZPosition(self):
        '''
        Function that returns the microscope position.

        Returns
        -------
        zPos:   int
                Microscope position in instrument units.
        '''
        if self.simulation:
            return self.zPos
        else:
            self.zPos = self.microscopeObject.ZDrive.Position()
            return self.zPos * 20   #conversion factor 

    def _isRelativeMoveAllowed(self, dz):
        limit_in_instrument_units = 30000 # bertram: 24000   #20*1200
        if self.getZPosition() + dz <= limit_in_instrument_units:
            return False
        else:
            return True

    def _isAbsoluteMoveAllowed(self, z):
        limit_in_instrument_units = 30000   #20*1200
        if z <= limit_in_instrument_units:
            return False
        else:
            return True
                

    def getObjectiveInformation(self):
        '''
        Function that prints the used Objectives and their position.
        '''
        for objective in self.microscopeObject.Nosepiece.Objectives:
            print('Objective Name:', objective.Name)
            print('Objective Position:', objective.Position)



if __name__ == "__main__":
    mic = Microscope()
    #mic.moveObjectiveBackwards()
    #mic.moveZAbsolute(35000)
    print(mic.getZPosition())
    #mic.moveZRelative(-50)
    #mic.moveObjectiveForward()
    #mic.moveZRelative(-499)

    #print(mic.getZPosition())

    #print(mic.microscopeObject.zDrive.ValuePerUnit())
    
#    mic.moveObjectiv1eBackwards()
#    print(mic.getCurrentObjective())
#    mic.moveObjectiveBackwards()
#    mic.moveObjectiveForward()
#    print(mic.getZPosition())
#    mic.moveZRelative(10)
#    print(mic.getZPosition())    

#    mic.moveZAbsolute(36816)
#    print(mic.getZPosition())








