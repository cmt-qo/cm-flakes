# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 08:49:09 2018

@author: TIM
"""

import tkinter as tk
from tkinter import simpledialog
from tkinter.filedialog import askdirectory
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askopenfile
from tkinter import messagebox
from PIL import ImageTk, Image
#import Stage.maerzhaeuser as st
import time
import numpy as np

class MyDialog(simpledialog.Dialog):
    '''
    This class is used to get numbers as input from the user.   
    '''
    def body(self, master):
        tk.Label(master, text="x-Pos. in Sample Coord:").grid(row=0)
        tk.Label(master, text="y-Pos. in Sample Coord:").grid(row=1)
        self.e1 = tk.Entry(master,width = 50)
        self.e2 = tk.Entry(master, width = 50)
        self.e1.grid(row=0, column=1)
        self.e2.grid(row=1, column=1)

    def apply(self):
        first = self.e1.get()
        second = self.e2.get()
        self.result = {'x_sample': first, 'y_sample': second}
        


class UserInterfaceCallBack():
    '''
    This class is used to have instant feedback on the screen when moving
    stage or microscope. 
    
    '''
    def __init__(self, GB):
        self.GB = GB
        self.cancel = False
    
    def get_focuspos_3vector(self, prompt_text):
        '''
        This function asks the user to move a little bit away from the edge
        and focus manually. When pressing OK the function ends.
        '''
        def up50():
            self.GB.microscope.moveZRelative(50)
            prompt.config(text='{z}'.format(z = str(int(np.floor(self.GB.microscope.getZPosition()/20)))))
            prompt.grid(row=2, column=1)
        def down50():
            self.GB.microscope.moveZRelative(-50)
            prompt.config(text='{z}'.format(z = str(int(np.floor(self.GB.microscope.getZPosition()/20)))))
            prompt.grid(row=2, column=1)            
        def up5():
            self.GB.microscope.moveZRelative(10)
            prompt.config(text='{z}'.format(z = str(int(np.floor(self.GB.microscope.getZPosition()/20)))))
            prompt.grid(row=2, column=1)            
        def down5():
            self.GB.microscope.moveZRelative(-10)
            prompt.config(text='{z}'.format(z = str(int(np.floor(self.GB.microscope.getZPosition()/20)))))
            prompt.grid(row=2, column=1)            
        def ok():
            root.destroy()
            root.quit() 
            return
        def on_closing():
            root.destroy()
            root.quit()
            self.cancel = True
            return
        self.cancel = False
        root = tk.Tk()
        root.geometry("239x113+450+400")
        root.attributes("-topmost", True)          
        root.title('Focus Manually')
        frame = tk.Frame(root)
        frame.grid(row=0)
        message = tk.Label(frame)
        message.config(text=prompt_text)
        message.grid(row=1, columnspan=4)  
        prompt = tk.Label(frame)
        prompt.config(text='{z}'.format(z = str(int(np.floor(self.GB.microscope.getZPosition()/20)))))
        prompt.grid(row=2, column=1)        
        DOWN50_button = tk.Button(frame, text='--', width=10, command=down50)
        DOWN50_button.grid(row=2, column=0)#, columnspan=2)  
        UP50_button = tk.Button(frame, text='++', width=10, command=up50)
        UP50_button.grid(row=2, column=2)#, columnspan=2)  
        DOWN5_button = tk.Button(frame, text='-', width=10, command=down5)
        DOWN5_button.grid(row=3, column=0)#, columnspan=2)  
        UP5_button = tk.Button(frame, text='+', width=10, command=up5)
        UP5_button.grid(row=3, column=2)#, columnspan=2)                  
        OK_button= tk.Button(frame, text='OK', width=10, command=ok)
        OK_button.grid(row=4, column=1)#, columnspan=2) 
        root.protocol("WM_DELETE_WINDOW", on_closing)
        tk.mainloop()          

    def focusing_and_changing_objectives_manually(self, prompt_text):
        '''
        This function lets the user change the objective and focus manually.
        
        '''
        def up50():
            self.GB.microscope.moveZRelative(50)
            z_value.config(text='Pos: {z}'.format(z = str(int(np.floor(self.GB.microscope.getZPosition()/20)))))
            z_value.grid(row=2, column=1)            
        def down50():
            self.GB.microscope.moveZRelative(-50)
            z_value.config(text='Pos: {z}'.format(z = str(int(np.floor(self.GB.microscope.getZPosition()/20)))))
            z_value.grid(row=2, column=1)               
        def up5():
            self.GB.microscope.moveZRelative(10)
            z_value.config(text='Pos: {z}'.format(z = str(int(np.floor(self.GB.microscope.getZPosition()/20)))))
            z_value.grid(row=2, column=1)               
        def down5():
            self.GB.microscope.moveZRelative(-10)
            z_value.config(text='Pos: {z}'.format(z = str(int(np.floor(self.GB.microscope.getZPosition()/20)))))
            z_value.grid(row=2, column=1)               
        def objm():
            self.GB.microscope.moveObjectiveBackwards()
            objective.config(text='Obj: {obj}x'.format(obj = str(self.GB.microscope.getCurrentObjective())))       
            objective.grid(row=3, column=1)            
        def objp():
            self.GB.microscope.moveObjectiveForward()
            objective.config(text='Obj: {obj}x'.format(obj = str(self.GB.microscope.getCurrentObjective())))       
            objective.grid(row=3, column=1)            
        def cancel():
            root.destroy()
            root.quit() 
            self.cancel = True
            return
        self.cancel = False
        root = tk.Tk()
        root.geometry("239x113+450+400")
        root.attributes("-topmost", True)          
        root.title('Focus Manually')
        frame = tk.Frame(root)
        frame.grid(row=0)
        message = tk.Label(frame)
        message.config(text=prompt_text)
        message.grid(row=1, columnspan=4)  
        z_value = tk.Label(frame)
        z_value.config(text='Pos: {z}'.format(z = str(int(np.floor(self.GB.microscope.getZPosition()/20)))))
        z_value.grid(row=2, column=1)
        objective = tk.Label(frame)
        objective.config(text='Obj: {obj}x'.format(obj = str(self.GB.microscope.getCurrentObjective())))       
        objective.grid(row=3, column=1)
        DOWN50_button = tk.Button(frame, text='--', width=10, command=down50)
        DOWN50_button.grid(row=2, column=0)#, columnspan=2)  
        UP50_button = tk.Button(frame, text='++', width=10, command=up50)
        UP50_button.grid(row=2, column=2)#, columnspan=2)  
        DOWN5_button = tk.Button(frame, text='-', width=10, command=down5)
        DOWN5_button.grid(row=3, column=0)#, columnspan=2)  
        UP5_button = tk.Button(frame, text='+', width=10, command=up5)
        UP5_button.grid(row=3, column=2)#, columnspan=2)                  
        OBJM_button= tk.Button(frame, text='Obj-', width=10, command=objm)
        OBJM_button.grid(row=4, column=0)#, columnspan=2) 
        OBJP_button= tk.Button(frame, text='Obj+', width=10, command=objp)
        OBJP_button.grid(row=4, column=2)#, columnspan=2)                 
        CANCEL_button= tk.Button(frame, text='Cancel', width=10, command=cancel)
        CANCEL_button.grid(row=4, column=1)#, columnspan=2) 
        root.protocol("WM_DELETE_WINDOW", cancel)
        tk.mainloop()
        

    def reload_sample(self, edge1, edge2):
        '''
        This functions takes two tuples (which are the edges SW, SE)
        and then opens a userinterface which gives the user the opportunity to 
        load a txt file (with 12 positions each) and move to these positions by
        button click.
        
        Parameters
        ----------
        edge1:      tuple
                    coordinates of edge SW
        edge2:      tuple
                    coordinates of edge SE
        '''
        self.cancel = False
        self.filepath = None
        self.positions = None
        def goTo1():
            if len(self.positions)>0:
                self.GB.stage.goAbsoluteSampleCoordinates(self.positions[0][1], 
                                                          self.positions[0][2],
                                                          edge1, edge2)
                self.focusing_and_changing_objectives_manually('Use the buttons to focus and change objective')   
            return
        def goTo2():
            if len(self.positions)>1:
                self.GB.stage.goAbsoluteSampleCoordinates(self.positions[1][1], 
                                                          self.positions[1][2], 
                                                          edge1, edge2)
                self.focusing_and_changing_objectives_manually('Use the buttons to focus and change objective')   
            return
        def goTo3():
            if len(self.positions)>2:
                self.GB.stage.goAbsoluteSampleCoordinates(self.positions[2][1], 
                                                          self.positions[2][2], 
                                                          edge1, edge2)
                self.focusing_and_changing_objectives_manually('Use the buttons to focus and change objective')   
            return
        def goTo4():
            if len(self.positions)>3:
                self.GB.stage.goAbsoluteSampleCoordinates(self.positions[3][1], 
                                                          self.positions[3][2], 
                                                          edge1, edge2)
                self.focusing_and_changing_objectives_manually('Use the buttons to focus and change objective')   
            return
        def goTo5():
            if len(self.positions)>4:
                self.GB.stage.goAbsoluteSampleCoordinates(self.positions[4][1], 
                                                          self.positions[4][2], 
                                                          edge1, edge2)
                self.focusing_and_changing_objectives_manually('Use the buttons to focus and change objective')   
            return
        def goTo6():
            if len(self.positions)>5:
                self.GB.stage.goAbsoluteSampleCoordinates(self.positions[5][1], 
                                                          self.positions[5][2], 
                                                          edge1, edge2)
                self.focusing_and_changing_objectives_manually('Use the buttons to focus and change objective')   
            return
        def goTo7():
            if len(self.positions)>6:
                self.GB.stage.goAbsoluteSampleCoordinates(self.positions[6][1], 
                                                          self.positions[6][2], 
                                                          edge1, edge2)
                self.focusing_and_changing_objectives_manually('Use the buttons to focus and change objective')   
            return  
        def goTo8():
            if len(self.positions)>7:
                self.GB.stage.goAbsoluteSampleCoordinates(self.positions[7][1], 
                                                          self.positions[7][2], 
                                                          edge1, edge2)
                self.focusing_and_changing_objectives_manually('Use the buttons to focus and change objective')   
            return
        def goTo9():
            if len(self.positions)>8:
                self.GB.stage.goAbsoluteSampleCoordinates(self.positions[8][1], 
                                                          self.positions[8][2], 
                                                          edge1, edge2)
                self.focusing_and_changing_objectives_manually('Use the buttons to focus and change objective')   
            return
        def goTo10():
            if len(self.positions)>9:
                self.GB.stage.goAbsoluteSampleCoordinates(self.positions[9][1], 
                                                          self.positions[9][2], 
                                                          edge1, edge2)
                self.focusing_and_changing_objectives_manually('Use the buttons to focus and change objective')   
            return
        def goTo11():
            if len(self.positions)>10:
                self.GB.stage.goAbsoluteSampleCoordinates(self.positions[10][1], 
                                                          self.positions[10][2], 
                                                          edge1, edge2)
                self.focusing_and_changing_objectives_manually('Use the buttons to focus and change objective')   
            return
        def goTo12():
            if len(self.positions)>11:
                self.GB.stage.goAbsoluteSampleCoordinates(self.positions[11][1], 
                                                          self.positions[11][2], 
                                                          edge1, edge2)
                self.focusing_and_changing_objectives_manually('Use the buttons to focus and change objective')   
            return
                  
        def on_closing():
            self.cancel = True
            root.destroy()
            root.quit()
            return
        def load():
            self.positions = None
            try:
                self.filepath = askopenfile().name
                print(self.filepath)
            except:
                return
            print(self.filepath)
            txt_file_name = self.filepath
            with open(txt_file_name) as f:
                lines = f.readlines()
            lines = [line.rstrip('\n') for line in open(txt_file_name)]
            self.positions = [[] for i in range(len(lines))]
            for i in range(len(lines)):
                lines[i] = lines[i].split(' ')
                for j in range(len(lines[i])):
                    if lines[i][j] != '':
                        self.positions[i].append(float(lines[i][j]))
            for i in range(12):
                tk.Label(mainframe, text='                  ').grid(row = i+1, column = 0)
                tk.Label(mainframe, text='                  ').grid(row = i+1, column = 1)
                tk.Label(mainframe, text='                  ').grid(row = i+1, column = 2)
                if i < len(lines):
                    tk.Label(mainframe, text=int(self.positions[i][0])).grid(row = i+1, column = 0)
                    tk.Label(mainframe, text=self.positions[i][1]).grid(row = i+1, column = 1)
                    tk.Label(mainframe, text=self.positions[i][2]).grid(row = i+1, column = 2)            
            return
            
        root = tk.Tk()
        root.title("Visit good Flakes")
        # Add a grid
        mainframe = tk.Frame(root)
        mainframe.grid(row=0)
        # add coordinates
        tk.Label(mainframe, text="Pos").grid(row = 0, column = 0)
        tk.Label(mainframe, text="X").grid(row = 0, column = 1)
        tk.Label(mainframe, text="Y").grid(row = 0, column = 2)
        
        load_button = tk.Button(mainframe, text='Load .txt file', command=load)
        load_button.grid(row=0, column=3)#, columnspan=2)  

        button_pos1 = tk.Button(mainframe, text='->', command=goTo1)
        button_pos2 = tk.Button(mainframe, text='->', command=goTo2)
        button_pos3 = tk.Button(mainframe, text='->', command=goTo3)
        button_pos4 = tk.Button(mainframe, text='->', command=goTo4)
        button_pos5 = tk.Button(mainframe, text='->', command=goTo5)
        button_pos6 = tk.Button(mainframe, text='->', command=goTo6)
        button_pos7 = tk.Button(mainframe, text='->', command=goTo7)
        button_pos8 = tk.Button(mainframe, text='->', command=goTo8)
        button_pos9 = tk.Button(mainframe, text='->', command=goTo9)
        button_pos10 = tk.Button(mainframe, text='->', command=goTo10)
        button_pos11 = tk.Button(mainframe, text='->', command=goTo11)
        button_pos12 = tk.Button(mainframe, text='->', command=goTo12)
        
        button_pos1.grid(row=1, column=3)#, columnspan=2)  
        button_pos2.grid(row=2, column=3)#, columnspan=2) 
        button_pos3.grid(row=3, column=3)#, columnspan=2) 
        button_pos4.grid(row=4, column=3)#, columnspan=2) 
        button_pos5.grid(row=5, column=3)#, columnspan=2) 
        button_pos6.grid(row=6, column=3)#, columnspan=2) 
        button_pos7.grid(row=7, column=3)#, columnspan=2) 
        button_pos8.grid(row=8, column=3)#, columnspan=2) 
        button_pos9.grid(row=9, column=3)#, columnspan=2) 
        button_pos10.grid(row=10, column=3)#, columnspan=2) 
        button_pos11.grid(row=11, column=3)#, columnspan=2) 
        button_pos12.grid(row=12, column=3)#, columnspan=2) 
        
        root.protocol("WM_DELETE_WINDOW", on_closing)   
        root.mainloop()                         
        


class UserInterface(object):   
    
    def __init__(self): #,stage = False):
#        self.x_pos = None
#        self.y_pos = None
#        if stage:
#            self.stage = st.Marzhauser('COM4', simulation=True)
#        self.yes_or_no = None
#        self.z_pos = 37000
        self.cancel = False
        self.filepath = None

    def message_box(self, text):
        ''' 
        This function generates a messagebox with OK and cancel and displays 
        a given text. It sets self.cancel = True when cancelling the window.
        
        Parameters
        ----------
        text:   string
                The text which will be displayed.
        '''
        root = tk.Tk()
        root.attributes("-topmost", True)          
        root.withdraw()
        self.cancel = not(messagebox.askokcancel("Information", text))
        if self.cancel == True:
            return

    def message_box_only(self, text):
        ''' 
        This function generates a messagebox and displays a given text.
        
        Parameters
        ----------
        text:   string
                The text which will be displayd.
        '''
        root = tk.Tk()
        root.attributes("-topmost", True)          
        root.withdraw()
        messagebox.showinfo("Information", text)

    def enter_sample_coordinates(self):
        '''
        This function generates a window where the user can enter two numbers,
        one for x-value in sample coordinates and one for the y-value. It 
        returns these values.
        
        Returns
        -------
        x_sample:   float
                    x-value given by the user's input.
        y_sample:   float
                    y-value given by the user's input.
        
        '''
        root = tk.Tk()
        root.attributes("-topmost", True)      
        root.title('Enter Sample Coordinates')
        root.withdraw()
        d = MyDialog(root)
        result = d.result
        root.destroy()
        if result is None:
            return None, None
        return result['x_sample'], result['y_sample']

    def call_startup_message_boxes(self):
        self.message_box('Press \'OK\' and select a folder in which the '
                       'pictures should be stored. It should '
                       'not be on a network dirve!')
        if self.cancel == True:
            return
        root_file_diag = tk.Tk()
        root_file_diag.withdraw()
        self.filepath = askdirectory()
        root_file_diag.destroy()
        root_file_diag.quit()





#    # not needed?
#    def call_userinterface_message_boxes(self,position):
#        '''
#        This function opens the user interface. It only needs a string with a 
#        description of the position of the wished point. It gives back the (x,y)-
#        tuple of position where the stage is currently.
#        
#        Parameters
#        ----------
#        position:       string
#                        Describes the position of the desired point. 
#                        E.g. 'South-West'.
#        
#        '''
#        self.x_pos = None
#        self.y_pos = None
#        self.message_box('Move to edge point: {pos} and click \'OK\'.'.format(pos=position))
#        self.x_pos = self.stage.getPos()[0]
#        self.y_pos = self.stage.getPos()[1]
#        return (self.x_pos, self.y_pos)
#
#    # not needed?
#    def call_successfully_stored_message_boxes(self,success):
#        if success == True:
#            self.message_box('The edge points have been stored successfully. '
#                             'Please move to an area somewhere on the chip, '
#                             'press \'OK\' and follow further instructions.')
#        else:
#            return
#        
#    # not needed?
#    def get_edge_points_message_boxes(self):
#        '''
#        This function takes input from the user and gives back the three 
#        edge points.
#        '''
#        position_names = ['South-West', 'South-East', 'North-East'] 
#        positions = []
#        for i in range(len(position_names)):
#            positions.append(self.call_userinterface_message_boxes(position_names[i]))
#            if self.cancel == True:
#                return None, None, None 
#        self.call_successfully_stored_message_boxes(True)
#        self.stage.close()
#        time.sleep(1)        
#        return positions[0], positions[1], positions[2]
#    
#    # not needed?
#    def get_2edge_points_message_boxes(self):
#        '''
#        This function takes input from the user and gives back two edge points.
#        '''
#        position_names = ['South-West', 'South-East'] 
#        positions = []
#        for i in range(len(position_names)):
#            positions.append(self.call_userinterface_message_boxes(position_names[i]))
#            if self.cancel == True:
#                return None, None
#        self.stage.close()
#        time.sleep(1)        
#        return positions[0], positions[1]    
#
#    # not needed anymore
#    def call_successfully_stored(self,success):
#        def killmainloop():
#            root.destroy()
#            root.quit()
#        if success == True:
#            msg_text = 'The edge points have been stored successfully. \nPlease move to an area somewhere on the chip, \nthen press \'OK\' to continue.'
#        else:
#            msg_text = 'You quit the procedure. Start the \nprogram again.'
#        root = tk.Tk()
#        root.geometry("220x80+300+300")
#        root.attributes("-topmost", True)        
#        root.title('Status Report')
#        frame = tk.Frame(root)
#        frame.pack()
#        message = tk.Label(frame)
#        message.config(text=msg_text)
#        message.pack()
#        OK_button = tk.Button(frame, text='OK', command=killmainloop)
#        OK_button.pack() 
#        tk.mainloop()
#       
#    # not needed anymore
#    def call_startup(self): 
#        def get_filepath():
#            '''
#            This function opens a dialog window to choose the path to a folder where
#            the pictures will be stored. It returns this path.
#            '''
#            root.destroy()
#            root.quit()
#            root_file_diag = tk.Tk()
#            root_file_diag.withdraw()
#            self.filepath = askdirectory()
#            print("Store path:", self.filepath)
#            root_file_diag.destroy()
#            root_file_diag.quit()
#    
#        root = tk.Tk()
#        root.geometry("220x80+300+300")
#        root.attributes("-topmost", True)         
#        root.title('Program Startup')
#        frame = tk.Frame(root)
#        frame.pack()
#        message = tk.Label(frame)
#        message.config(text='Press \'OK\' and select a folder in which \nthe '
#                       'pictures should be stored. \nIt should '
#                       'not be on a network dirve!')
#        message.pack()
#        OK_button = tk.Button(frame, text='OK', command=get_filepath)
#        OK_button.pack()      
#        tk.mainloop()
#
#    # not needed anymore       
#    def get_edge_points(self):
#        '''
#        This function takes input from the user and gives back the three 
#        edge points.
#        '''
#        position_names = ['South-West', 'South-East', 'North-East'] 
#        positions = []
#        for i in range(len(position_names)):
#            positions.append(self.call_userinterface(position_names[i]))
#            if (positions[i])[0] is None:
#                self.call_successfully_stored(False)
#                return None, None, None 
#        self.message_box('Thank you, the edge points have been stored successfully. '
#                         'Please move to an area somewhere on the chip and press \'OK\' '
#                         'to continue.')
#        self.stage.close()
#        time.sleep(1)        
#        return positions[0], positions[1], positions[2]
#    
#    # not needed anymore
#    def good_focus_area(self):
#        def yes():
#            self.yes_or_no = 'y'
#            root.destroy()
#            root.quit()
#        def no():
#            self.yes_or_no = 'n'
#            root.destroy()
#            root.quit()
#        self.yes_or_no = None
#        root = tk.Tk()
#        root.geometry("220x80+300+300")
#        root.attributes("-topmost", True)          
#        root.title('Confirm Area')
#        frame = tk.Frame(root)
#        frame.pack()
#        message = tk.Label(frame)
#        message.config(text='Is this a good area for focus pictures?')
#        message.pack()
#        YES_button = tk.Button(frame, text='YES', command=yes)
#        YES_button.pack(side=tk.LEFT)      
#        NO_button = tk.Button(frame, text='NO', command=no)
#        NO_button.pack(side=tk.RIGHT)   
#        tk.mainloop()   
#        
#    # not needed anymore
#    def call_userinterface(self,position):
#        '''
#        This function opens the user interface. It only needs a string with a 
#        description of the position of the wished point. It gives back the (x,y)-
#        tuple of position where the stage is currently.
#        
#        Parameters
#        ----------
#        position:       string
#                        Describes the position of the desired point. 
#                        E.g. 'South-West'.
#        
#        '''
#        def save_edge_point():
#            '''
#            After clicking the 'Store Position' button close the window.
#            '''
#            self.x_pos = self.stage.getPos()[0]
#            self.y_pos = self.stage.getPos()[1]
#            root.destroy()
#            root.quit()
#        self.x_pos = None
#        self.y_pos = None
#        root = tk.Tk()
#        root.geometry("220x80+300+300")
#        root.attributes("-topmost", True)
#        root.title('Input Edge Point \'{pos}\''.format(pos=position))
#        frame = tk.Frame(root)
#        frame.pack()
#        message = tk.Label(frame)
#        message.config(text='Move to edge point: {pos} \nand click \'Store Position\'.'.format(pos=position))
#        message.pack()
#        store_button = tk.Button(frame, text='Store Position', command=save_edge_point)
#        store_button.pack()      
#        tk.mainloop()
#        return (self.x_pos, self.y_pos)
    

    def call_initial_program_start(self):
        '''
        This function generates a menu in which one can set a magnification
        (10x, 20x or 50x) and an overlap in % (between 1 and 99) to perform
        the scan. These parameters are then stored in self.mag and self.ovlap.      
        '''
        self.cancel = False
        self.mag = None
        self.ovlap = None
        def on_closing():
            self.cancel = True
            root.destroy()
            root.quit()
            return
        def ok():
            self.mag = tkvar_mag.get()
            if self.mag == '' or self.ovlap == '':
                self.mag = None
                self.ovlap = None
                self.message_box_only('Please set both, a magnification and an overlap in %')
                return 
            self.mag = int(self.mag[:-1])           
            try:
                self.ovlap = float(overlap.get())
            except:
                self.message_box_only('Please enter a number between 1 and 99 for the overlap in %')
                return
            if type(self.ovlap) != float or self.ovlap<1 or self.ovlap>99:
                self.message_box_only('Please enter a number between 1 and 99 for the overlap in %')
                return
            self.ovlap /= 100.
            root.destroy()
            root.quit() 
            return
        
        root = tk.Tk()
        root.title("Getting started - Settings for scan")
         
        # Add a grid
        mainframe = tk.Frame(root)
        mainframe.grid(row=0)
         
        # Create a Tkinter variable
        tkvar_mag = tk.StringVar(root)
         
        # Dictionary with options
        magnification = { '10x','20x','50x'}
        tkvar_mag.set('10x')
         
        popupMenu_mag = tk.OptionMenu(mainframe, tkvar_mag, *magnification,)
        overlap = tk.Entry(mainframe,width=6)
        tk.Label(mainframe, text="Set magnification").grid(row = 1, column = 0)
        tk.Label(mainframe, text="Set overlap in %").grid(row = 1, column = 2)
        popupMenu_mag.grid(row = 2, column =0)
        overlap.grid(row=2, column=2)

        # on change dropdown value
        def change_dropdown_mag(*args):
            #print("mag:", tkvar_mag.get() )
            pass

        tkvar_mag.trace('w', change_dropdown_mag)
        root.protocol("WM_DELETE_WINDOW", on_closing)   
        OK_button= tk.Button(mainframe, text='OK', width=10, command=ok)
        OK_button.grid(row=4, column=1)#, columnspan=2) 
        root.mainloop()




#    def reload_sample(self):
#        self.cancel = False
#        self.filepath = None
#        self.positions = None
#        def goTo1():
#            if len(self.positions)>0:
#                print(self.positions[0][1], 
#                      self.positions[0][2])
#                self.enter_sample_coordinates()     
#            return
#        def goTo2():
#            if len(self.positions)>1:
#                print(self.positions[1][1], 
#                      self.positions[1][2])
#                self.enter_sample_coordinates()    
#            return
#        def goTo3():
#            if len(self.positions)>2:
#                print(self.positions[2][1], 
#                      self.positions[2][2])
#                self.enter_sample_coordinates()    
#            return
#        def goTo4():
#            if len(self.positions)>3:
#                print(self.positions[3][1], 
#                      self.positions[3][2])
#                self.enter_sample_coordinates()   
#            return
#        def goTo5():
#            if len(self.positions)>4:
#                print(self.positions[4][1], 
#                      self.positions[4][2])
#                self.enter_sample_coordinates()      
#            return
#        def goTo6():
#            if len(self.positions)>5:
#                print(self.positions[5][1], 
#                      self.positions[5][2])
#                self.enter_sample_coordinates()      
#            return
#        def goTo7():
#            if len(self.positions)>6:
#                print(self.positions[6][1], 
#                      self.positions[6][2])
#                self.enter_sample_coordinates()   
#        def goTo8():
#            if len(self.positions)>7:
#                print(self.positions[7][1], 
#                      self.positions[7][2])
#                self.enter_sample_coordinates()      
#            return
#        def goTo9():
#            if len(self.positions)>8:
#                print(self.positions[8][1], 
#                      self.positions[8][2])
#                self.enter_sample_coordinates()      
#            return
#        def goTo10():
#            if len(self.positions)>9:
#                print(self.positions[9][1], 
#                      self.positions[9][2])
#                self.enter_sample_coordinates()      
#            return
#        def goTo11():
#            if len(self.positions)>10:
#                print(self.positions[10][1], 
#                      self.positions[10][2])
#                self.enter_sample_coordinates()       
#            return
#        def goTo12():
#            if len(self.positions)>11:
#                print(self.positions[11][1], 
#                      self.positions[11][2])
#                self.enter_sample_coordinates()    
#            return
#          
#        
#        def on_closing():
#            self.cancel = True
#            root.destroy()
#            root.quit()
#            return
#        def load():
#            self.positions = None
#            try:
#                self.filepath = askopenfile().name
#                print(self.filepath)
#            except:
#                return
#            print(self.filepath)
#            txt_file_name = self.filepath
#            with open(txt_file_name) as f:
#                lines = f.readlines()
#            lines = [line.rstrip('\n') for line in open(txt_file_name)]
#            self.positions = [[] for i in range(len(lines))]
#            for i in range(len(lines)):
#                lines[i] = lines[i].split(' ')
#                for j in range(len(lines[i])):
#                    if lines[i][j] != '':
#                        self.positions[i].append(float(lines[i][j]))
#            for i in range(12):
#                tk.Label(mainframe, text='                  ').grid(row = i+1, column = 0)
#                tk.Label(mainframe, text='                  ').grid(row = i+1, column = 1)
#                tk.Label(mainframe, text='                  ').grid(row = i+1, column = 2)
#                if i < len(lines):
#                    tk.Label(mainframe, text=int(self.positions[i][0])).grid(row = i+1, column = 0)
#                    tk.Label(mainframe, text=self.positions[i][1]).grid(row = i+1, column = 1)
#                    tk.Label(mainframe, text=self.positions[i][2]).grid(row = i+1, column = 2)            
#            return
#            
#        root = tk.Tk()
#        root.title("Visit good Flakes")
#        # Add a grid
#        mainframe = tk.Frame(root)
#        mainframe.grid(row=0)
#        # add coordinates
#        tk.Label(mainframe, text="Pos").grid(row = 0, column = 0)
#        tk.Label(mainframe, text="X").grid(row = 0, column = 1)
#        tk.Label(mainframe, text="Y").grid(row = 0, column = 2)
#        
#        load_button = tk.Button(mainframe, text='Load .txt file', command=load)
#        load_button.grid(row=0, column=3)#, columnspan=2)  
#
#        button_pos1 = tk.Button(mainframe, text='->', command=goTo1)
#        button_pos2 = tk.Button(mainframe, text='->', command=goTo2)
#        button_pos3 = tk.Button(mainframe, text='->', command=goTo3)
#        button_pos4 = tk.Button(mainframe, text='->', command=goTo4)
#        button_pos5 = tk.Button(mainframe, text='->', command=goTo5)
#        button_pos6 = tk.Button(mainframe, text='->', command=goTo6)
#        button_pos7 = tk.Button(mainframe, text='->', command=goTo7)
#        button_pos8 = tk.Button(mainframe, text='->', command=goTo8)
#        button_pos9 = tk.Button(mainframe, text='->', command=goTo9)
#        button_pos10 = tk.Button(mainframe, text='->', command=goTo10)
#        button_pos11 = tk.Button(mainframe, text='->', command=goTo11)
#        button_pos12 = tk.Button(mainframe, text='->', command=goTo12)
#        
#        button_pos1.grid(row=1, column=3)#, columnspan=2)  
#        button_pos2.grid(row=2, column=3)#, columnspan=2) 
#        button_pos3.grid(row=3, column=3)#, columnspan=2) 
#        button_pos4.grid(row=4, column=3)#, columnspan=2) 
#        button_pos5.grid(row=5, column=3)#, columnspan=2) 
#        button_pos6.grid(row=6, column=3)#, columnspan=2) 
#        button_pos7.grid(row=7, column=3)#, columnspan=2) 
#        button_pos8.grid(row=8, column=3)#, columnspan=2) 
#        button_pos9.grid(row=9, column=3)#, columnspan=2) 
#        button_pos10.grid(row=10, column=3)#, columnspan=2) 
#        button_pos11.grid(row=11, column=3)#, columnspan=2) 
#        button_pos12.grid(row=12, column=3)#, columnspan=2) 
#        
#        root.protocol("WM_DELETE_WINDOW", on_closing)   
#        root.mainloop()                    
         

if __name__ == "__main__":
    UI = UserInterface()
#    UI.call_initial_program_start()
    UI.reload_sample()
    print(UI.cancel)
    print(UI.positions)
#    UI.test_ask_file()

#    UICB = UserInterfaceCallBack()
#    UICB.focusing_and_changing_objectives_manually('Hello')
    
#    UI.message_box('Hello')
#    filepath = UI.get_filepath()
#    pos1, pos2, pos3 = UI.get_edge_points()
#    print(filepath)
#    print(pos1,pos2,pos3)
#    UI.good_focus_area()
#    UI.message_box("Hello")
