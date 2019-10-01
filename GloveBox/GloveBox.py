# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 18:16:48 2018

@author: Benedikt
"""

import sys
import os
PATH = os.path.normpath(r"C:\Users\Nele\Documents\GloveBox\gloveboxnele")
sys.path.append(PATH)
import Microscope.lvecon as lv
import Camera as cm 
import Stage.maerzhaeuser as st
import UserInterface.UserInterface as UI
from UserInterface.UserInterface import UserInterfaceCallBack as UICB
import numpy as np
import cv2
import time
import matplotlib.pyplot as plt
import shutil

class GloveBox():

    def __init__(self, filepath):
#---------------------------------------------------------------------------------------
# SIMULATION        
#---------------------------------------------------------------------------------------        
#        self.microscope = lv.Microscope(True,38000)      
#        self.camera = cm.Camera(filepath)
#        self.stage = st.Marzhauser('COM4',simulation=True)  
#        self.filepath = filepath
#        self.settings = {
#                'magnification': None,
#                'screenwidth': None,
#                'screenheight': None,
#                'mm_to_pixel': None}
#        self.set_magnification()  
#        self.UI = UI()
##        self.number_black_pixels_bottom = self._number_of_pixels_to_crop()[0] + 1
##        self.number_black_pixels_top = self._number_of_pixels_to_crop()[1] - 1
#---------------------------------------------------------------------------------------        
        self.microscope = lv.Microscope()         
        self.camera = cm.Camera(filepath)
        self.stage = st.Marzhauser('COM3')  
        self.filepath = filepath
        self.settings = {
                'magnification': None,
                'screenwidth': None,
                'screenheight': None,
                'mm_to_pixel': None}
        # here the magnification (and all the corresponding setting) are set to 10x
        self.set_magnification()  
        self.UI = UI()
        # these variables define how many pixels are black on a uncropped image
        self.number_black_pixels_bottom = self._number_of_pixels_to_crop()[0] #+ 1
        self.number_black_pixels_top = self._number_of_pixels_to_crop()[1] -1#- 1
#-------------------------------------------------------------------------------------- 



    def get_auto_focus_vectors(self, focus_vectors, magnification):
        '''
        Input is the 2D list focus_vecotrs (for three position) and it 
        calculates a more accurate z-value for each position.
        
        Parameters
        ----------
        focus_vectors:  list
                        list with 3 arrays which are the given positions (x,y,z)
        magnification:  int
                        Magnification
                        
        Output
        ------
        Gives back the same 2D list with modified z-values for all 3 positions.
        '''
        # set correct objective
        self.set_magnification(magnification)
        # defining the arrays with (x,y,z) for all three positions
        pos1 = focus_vectors[0]
        pos2 = focus_vectors[1]
        pos3 = focus_vectors[2]
        # defining paths to the folder where the focus pictures will be stored
        path_pos1 = self.filepath + "\Pictures_Pos1"
        path_pos2 = self.filepath + "\Pictures_Pos2"
        path_pos3 = self.filepath + "\Pictures_Pos3"        
        # check if paths already exist
        if os.path.exists(path_pos1) == True:
            self.UI.message_box("This Folder already exists: " + str(path_pos1))
            print("This Folder already exists: ", path_pos1)
            return
        elif os.path.exists(path_pos2) == True:
            self.UI.message_box("This Folder already exists: " + str(path_pos2))
            print("This Folder already exists: ", path_pos2)
            return
        elif os.path.exists(path_pos3) == True:
            self.UI.message_box("This Folder already exists: " + str(path_pos3))
            print("This Folder already exists: ", path_pos3) 
            return
        # create folders
        os.mkdir(path_pos1)
        os.mkdir(path_pos2)
        os.mkdir(path_pos3)        
##         go to pos3
#        self.stage.goAbsolute(pos3[0],pos3[1]) 
#        self.Take_Focus_Pictures_with_start_value(path_pos1, pos1[2])
#        # go to pos2
#        self.stage.goAbsolute(pos2[0],pos2[1]) 
#        self.Take_Focus_Pictures_with_start_value(path_pos2, pos2[2])        
#        # go to pos1
#        self.stage.goAbsolute(pos1[0],pos1[1]) 
#        self.Take_Focus_Pictures_with_start_value(path_pos3, pos3[2])                 
        # go to pos3
        self.stage.goAbsolute(pos3[0],pos3[1]) 
        self.Take_Focus_Pictures_with_start_value(path_pos3, pos3[2])
        # go to pos2
        self.stage.goAbsolute(pos2[0],pos2[1]) 
        self.Take_Focus_Pictures_with_start_value(path_pos2, pos2[2])        
        # go to pos1
        self.stage.goAbsolute(pos1[0],pos1[1]) 
        self.Take_Focus_Pictures_with_start_value(path_pos1, pos1[2])                 
        # compute z (focus value) for each position
        pos1_focus = self.Get_Focus_Point_From_Picures(path_pos1)
        pos2_focus = self.Get_Focus_Point_From_Picures(path_pos2)
        pos3_focus = self.Get_Focus_Point_From_Picures(path_pos3)
        # delete created folders
        shutil.rmtree(path_pos1, ignore_errors=True)
        shutil.rmtree(path_pos2, ignore_errors=True)
        shutil.rmtree(path_pos3, ignore_errors=True)
        return [np.array([pos1[0],pos1[1],pos1_focus]),
                np.array([pos2[0],pos2[1],pos2_focus]),
                np.array([pos3[0],pos3[1],pos3_focus])]                



    def Take_Focus_Pictures_with_start_value(self, relpath, z_start_value):
        '''
        Function to take pictures to determin the focus point at this position.
        
        Parameters
        ----------
        relpath:        string
                        Relative path to the folder where the pictures will be saved.
        z_start_value:  double
                        Start value for the focus position
        '''     
        print('zStart:',z_start_value)
        if self.settings['magnification'] == 50:
            DeltaZ = 150 
            zPositions = np.linspace(z_start_value-DeltaZ,
                                     z_start_value+DeltaZ, 
                                     30) # each 300/30 = 10 units a picture
        elif self.settings['magnification'] == 20:
            DeltaZ = 120
            zPositions = np.linspace(z_start_value-DeltaZ,
                                     z_start_value+DeltaZ,
                                     20) # each 240/20 = 12 units a picture
        elif self.settings['magnification'] == 10:
            DeltaZ = 200
            zPositions = np.linspace(z_start_value-DeltaZ,
                                     z_start_value+DeltaZ, 
                                     30) # each 400/30 = 13.33 units a picture
        time.sleep(1.0)
        for position in zPositions:
            self.microscope.moveZAbsolute(position)
            time.sleep(1)
            filename = str(int(round(position,0)))
            self.camera.take_single_cropped_picture(relpath, filename,
                                                    self.number_black_pixels_bottom,
                                                    self.number_black_pixels_top)   
            time.sleep(0.05)
        


#    def Take_Focus_Pictures(self, relpath):
#        '''
#        Function to take pictures to determin the focus point at this position.
#        
#        Parameters
#        ----------
#        relpath:    string
#                    Relative path to the folder where the pictures will be saved.
#        '''
##        self.magnification = 10
##        if self.magnification == 50:
##            zPositions = np.linspace(36500, 37500, 50)  
##        elif self.magnification == 10:
##            zPositions = np.linspace(36500, 37500, 50)
#        if self.settings['magnification'] == 50:
#            zPositions = np.linspace(36500, 37500, 70)  
#        elif self.settings['magnification'] == 10:
#            zPositions = np.linspace(36500, 37500, 50)            
#        for position in zPositions:
#            self.microscope.moveZAbsolute(position)
#            filename = str(int(round(position,0)))
#            # high resolution picture without black borders on bottom and top
#            self.camera.take_single_cropped_picture(relpath, filename, 
#                                                    self.number_black_pixels_bottom, 
#                                                    self.number_black_pixels_top)    
#            time.sleep(0.05)        
#
#
    def Get_Focus_Point_From_Picures(self, folderpath):
        '''
        This function defines the focus point via fitting the variation of the
        laplace transformation and looking for its peak. It takes a path
        to the folder in which the focus pictures are.
        
        Parameters
        ----------
        folderpth:  string
                    relative path to a folder where the focus pictures are located.
        '''              
        # Path where we stored the pictures
        folderpath = os.path.normpath(r'{path}'.format(path=folderpath))
        zPositions = []
        sigma_arr = []
        
        # calculating the variation of the laplace
        for i,file in enumerate(os.listdir(folderpath)):
            # Open the image and make a Laplace transformation
            # Calculate the standardeviation of the laplace transformation
            # Save the variable
            zPositions.append(float(file[:-4]))
            image = cv2.imread(os.path.join(folderpath,file))
            laplace = cv2.Laplacian(image,cv2.CV_64F, ksize=1)
            sigma = laplace.var()
            sigma_arr.append(sigma)
                       
        # Plot
        fig = plt.figure()
        plt.plot(zPositions, sigma_arr,'rx')
#        # Fit with Gauss
#        popt_gauss, pcov_gauss = curve_fit(self._gauss, zPositions, sigma_arr,p0 = [np.max(sigma_arr), zPositions[np.argmax(sigma_arr)], 400, 1e13])        
#        plt.plot(zPositions, self._gauss(zPositions,*popt_gauss),'b')   
        plt.savefig(str(self.filepath) + "\\" + str(folderpath[-4:]) + "_" + str(self.settings['magnification']) + "x.jpg", dpi=500)
        plt.close(fig)  
#        return popt_gauss[1]
        return zPositions[np.argmax(sigma_arr)]
#
#
#    # not needed
#    def get_points_to_do_focus(self,x,y,z,t):
#        '''
#        This function takes 3 edge points and gives back 3 points inside the 
#        sample to fucus.
#        
#        Parameters
#        ----------
#        x:      Tuple
#                South point.
#        y:      Tuple
#                South east point.
#        z:      Tubple
#                North east point.
#        t:      float
#                How much into sample. t=0 edge points, t=0.5 in the middle.
#        Output
#        ------
#        The output is 3 tuples corresponding to the 3 focus points. 
#        The order of tuples is: south west, south east, north east.
#        '''
#        a1 = np.subtract(y,x)
#        a2 = np.subtract(z,y)
#        a3 = np.add(a1,a2)       
#        v = np.add(x,0.5*a3)
#        v = (v[0],v[1])
#        a4 = np.subtract(v,y)
#        # defining width and height of the screen plus 5 percent to be sure
##        width = self.screenwidth + 0.05*self.screenwidth
##        height = self.screenheight + 0.05*self.screenheight        
#        width = self.settings['screenwidth'] + 0.05*self.settings['screenwidth']
#        height = self.settings['screenheight'] + 0.05*self.settings['screenheight']               
#        # setting a minimal t to be sure that no edge is on the screen
#        if t <= max(width / (2*np.abs(a3[0])), height / (2*np.abs(a3[1])),
#                    width / (4*np.abs(a4[0])), height / (4*np.abs(a4[1]))):
#            t = max(width / (2*np.abs(a3[0])), height / (2*np.abs(a3[1])),
#                    width / (4*np.abs(a4[0])), height / (4*np.abs(a4[1])))
#        if t > 1:
#            self.UI.message_box("Please check the focus points. The waver may have a too lengthy shape.")
#            print("Please check the focus points. The waver may have a " 
#                  + "too lengthy shape")
#            return         
#        x = np.add(x,t*a3)
#        y = np.add(y,2*t*a4)
#        z = np.subtract(z,t*a3)
#        x = (x[0],x[1])
#        y = (y[0],y[1])
#        z = (z[0],z[1])       
#        return x,y,z
#    
#    
#    # not needed?
#    def get_vectors_of_inner_positions_userinterface(self,x,y,z,t=0.3):
#        '''
#        This function takes three edge tuples and gives back three 3-vectors 
#        of the inner positions in the form of
#        (x_inner_x, x_inner_y, x_inner_zfocus),
#        (y_inner_x, y_inner_y, y_inner_zfocus),
#        (z_inner_x, z_inner_y, z_inner_zfocus)
#        
#        Parameters
#        ----------
#        x:          Tuple
#                    South point.
#        y:          Tuple
#                    South east point.
#        z:          Tubple
#                    North east point.
#        t:          float
#                    How much into sample. t=0 edge points, t=1 in the middle.
#        
#        Output
#        ------
#        Three 3-vectors of inner positions.
#        '''
#        t /= 2.
#        x,y,z = self.get_points_to_do_focus(x,y,z,t)
#        
##        # when magnification is 50x than move it twice. Home position always 10x
##        if self.magnification == 50:
##            self.microscope.moveObjectiveForward()
##            self.microscope.moveObjectiveForward()
#            
#        # defining paths to the folder where the focus pictures will be stored
#        path_x = self.filepath + "\Pictures_Pos1"
#        path_y = self.filepath + "\Pictures_Pos2"
#        path_z = self.filepath + "\Pictures_Pos3"        
#        # check if paths already exist
#        if os.path.exists(path_x) == True:
#            self.UI.message_box("This Folder already exists: " + str(path_x))
#            print("This Folder already exists: ", path_x)
#            return
#        elif os.path.exists(path_y) == True:
#            self.UI.message_box("This Folder already exists: " + str(path_y))
#            print("This Folder already exists: ", path_y)
#            return
#        elif os.path.exists(path_z) == True:
#            self.UI.message_box("This Folder already exists: " + str(path_z))
#            print("This Folder already exists: ", path_z) 
#            return
#        # create folders
#        os.mkdir(path_x)
#        os.mkdir(path_y)
#        os.mkdir(path_z) 
#        
#        # move to z
#        self.stage.goAbsolute(z[0],z[1])        
#        # check if the area is good to focus
#        self.UI.message_box('If this is already a good area to focus click '
#                            '\'OK\'. If not, move in this very neighborhood '
#                            'to a good one and then click \'OK\'.')
##        self.UI.good_focus_area()
##        answer = self.UI.yes_or_no
##        while answer != 'y':
##            self.stage.goRelative(np.round(np.random.uniform(-.3,0),2), 
##                                  np.round(np.random.uniform(-.3,0),2))
##            self.UI.good_focus_area()
##            answer = self.UI.yes_or_no
#        time.sleep(1)
#        # store the current x and y values of position x
#        z_x , z_y = self.stage.getPos()
#        self.Take_Focus_Pictures(path_z)
#
#        # move to y
#        self.stage.goAbsolute(y[0],y[1])
#        # check if the area is good to focus
#        self.UI.message_box('If this is already a good area to focus click '
#                            '\'OK\'. If not, move in this very neighborhood '
#                            'to a good one and then click \'OK\'.')
##        self.UI.good_focus_area()
##        answer = self.UI.yes_or_no
##        while answer != 'y':
##            self.stage.goRelative(np.round(np.random.uniform(-.3,0),2), 
##                                  np.round(np.random.uniform(0,.3),2))
##            self.UI.good_focus_area()
##            answer = self.UI.yes_or_no       
#        time.sleep(1)   
#        # store the current x and y values of position y
#        y_x, y_y = self.stage.getPos() 
#        self.Take_Focus_Pictures(path_y)         
#       
#        # move to x
#        self.stage.goAbsolute(x[0],x[1])
#        # check if the area is good to focus
#        self.UI.message_box('If this is already a good area to focus click '
#                            '\'OK\'. If not, move in this very neighborhood '
#                            'to a good one and then click \'OK\'.')        
##        self.UI.good_focus_area()
##        answer = self.UI.yes_or_no
##        while answer != 'y':
##            self.stage.goRelative(np.round(np.random.uniform(0,.3),2), 
##                                  np.round(np.random.uniform(0,.3),2))
##            self.UI.good_focus_area()
##            answer = self.UI.yes_or_no  
#        time.sleep(1)
#        # store the current x and y values of position x
#        x_x, x_y = self.stage.getPos()
#        self.Take_Focus_Pictures(path_x)  
#           
#        # compute z (focus value) for each position
#        x_focus = self.Get_Focus_Point_From_Picures(path_x)
#        y_focus = self.Get_Focus_Point_From_Picures(path_y)
#        z_focus = self.Get_Focus_Point_From_Picures(path_z)
#        print(x_focus, y_focus, z_focus)
#        # delete created folders
#        shutil.rmtree(path_x, ignore_errors=True)
#        shutil.rmtree(path_y, ignore_errors=True)
#        shutil.rmtree(path_z, ignore_errors=True)
#        
##        # turning back the objective
##        if self.magnification == 50:
##            self.microscope.moveObjectiveBackwards()
##            self.microscope.moveObjectiveBackwards()
#        print("The three 3-vectors for the plane:\nPos1:",
#              np.array([x_x, x_y, x_focus]), '\nPos2:',
#              np.array([y_x, y_y, y_focus]), '\nPos3:',
#              np.array([z_x, z_y, z_focus]))
#        return np.array([x_x, x_y, x_focus]), np.array([y_x, y_y, y_focus]), np.array([z_x, z_y, z_focus])
#        
#
#    # not needed?
#    def calculate_focus_plane_parameters(self,x,y,z):
#        '''
#        This function takes three edge tuples and gives back the focus plane parameters.
#        
#        Parameters
#        ----------
#        x:          Tuple
#                    South point.
#        y:          Tuple
#                    South east point.
#        z:          Tubple
#                    North east point.
#        '''
#        p1, p2, p3 = self.get_vectors_of_inner_positions_userinterface(x, y, z)        
#        v1 = p3 - p1
#        v2 = p2 - p1        
#        normal_vec = np.cross(v1, v2)
#        A, B, C = normal_vec       
#        D = -np.dot(normal_vec, p3)
##        print('The equ. is {a}*x + {b}*y + {c}*z + {d} = 0'.format(a=A, b=B, c=C, d=D))        
#        return [A,B,C,D]
#
#
#    # not needed
#    def scan_sample(self, relstorepath, pos1, pos2, pos3, overlap, sleep_time):
#        '''
#        This function scans the sample. It takes a relative path to 
#        a folder where the pictures will be stored. It stores maximum 200 
#        pictures per folder, if this number is exceeded more folders will be
#        generated automatically. Furthermore the function needs 3 edge points 
#        and then scans the area of the smallest rectangle which encolses all 
#        3 points. It also needs an overlap ranging between 0 and 1.
#        
#        Parameters
#        ----------
#        relstorepath:   string
#                        Relative path where the Pictures will be stored.
#        pos1:           tuple
#                        (x,y)-position of south west point.
#        pos2:           tuple
#                        (x,y)-position of south east point.
#        pos3:           tuple
#                        (x,y)-position of north east point.
#        overlap:        float
#                        Overlap in x-direction (between 0 and 1).
#        '''
#        time_start = time.time()
#        # defining a maximum number of pictures per folder
#        number_of_pictures_per_folder = 200
#        # split in multiple folders when exceeding this number pictures
#        number_of_folders = 1
#        new_path = str(relstorepath) + "\\" + str(number_of_folders)
#        os.mkdir(new_path)        
#        
#        # settings for 50x
#        self.set_magnification(50)
#        # calculating plane parameter of the focus plane for 50x (takes much time)
#        plane_param_50x = self.calculate_focus_plane_parameters(pos1, pos2, pos3)                
#        print("Focus Plane Parameter 50x:", plane_param_50x)     
#        # writing the plane parameters of 50x in a txt file
#        path_plane_param = str(relstorepath) + "\Plane_Parameters.txt"
#        with open(path_plane_param, 'w+') as f:
#            f.write("50x:\n")
#            for parameter in plane_param_50x:
#                f.write("%s\n" % parameter)
#      
#        # settings for 10x
#        self.set_magnification(10)
#        # calculating plane parameter of the focus plane for 10x (takes much time)
#        plane_param_10x = self.calculate_focus_plane_parameters(pos1, pos2, pos3) 
#        print("Focus Plane Parameter 10x:", plane_param_10x)
#        # appending the txt file with the plane parameters for 10x
#        with open(path_plane_param, 'a') as f:
#            f.write("10x:\n")
#            for parameter in plane_param_10x:
#                f.write("%s\n" % parameter)
#    
#        time_end_focus = time.time()     
#        # defining ratio because step to move up is smaller than sideways
#        ratio_height_to_width = self.settings['screenheight'] / self.settings['screenwidth']  
#        # overwriting the positions with the smallest enclosing rectangle       
#        pos1, pos2, pos3, pos4 = self.smallest_rect(pos1, pos2, pos3)
#        # calculatie the left and right boundary lines
#        if np.abs(pos4[0] - pos1[0]) > 1e-12:
#            slope_l_r_boundary = (pos4[1] - pos1[1]) / (pos4[0] - pos1[0])
#            b_l_boundary = pos1[1] - slope_l_r_boundary * pos1[0]    # y intercept
#            b_r_boundary = pos3[1] - slope_l_r_boundary * pos3[0]    # y intercept
#            x_left_boundary = lambda y: (y - b_l_boundary) / slope_l_r_boundary
#            x_right_boundary = lambda y: (y - b_r_boundary) / slope_l_r_boundary
#        # when slope would be infinit
#        else:
#            x_left_boundary = lambda y: pos1[0]
#            x_right_boundary = lambda y: pos2[0]        
#        # calculating x and y of the vecor connecting pos1 and pos2
#        x_proj = pos2[0] - pos1[0]
#        y_proj = pos2[1] - pos1[1] 
#        # calculating the steps in each direction (in mm on substrate)
#        moving_step_x_direction = self.settings['screenwidth'] * (1 - overlap)
#        moving_step_y_direction = moving_step_x_direction * (y_proj / x_proj) 
#        # go to starting position
#        self.stage.goAbsolute(pos1[0], pos1[1])
#        # start with scan in positive x-direction
#        positive_x_direction = True
#        # to not take pictures over the boundary lines
#        recent_up = False
#        # count the number of pictures to not overfill the folders
#        picture_counter = 0  
#        while True:
#            # moving a whole line in positive x-direction
#            if positive_x_direction:  
#                pre_factor = 1.
#            # moving a whole line in negatice x-direction
#            else:
#                pre_factor = -1.
#            while True:
#                if not(recent_up):
#                    # focusing
#                    self.microscope.moveZAbsolute(
#                            self.calculate_z_values_of_plane(
#                                    plane_param_10x, 
#                                    self.stage.getPos()[0], 
#                                    self.stage.getPos()[1]))
#                    time.sleep(0.05)
#                    # giving the taken picture a name
#                    filename = "X_" + str(np.round(self.stage.getPos()[0], 3)) + "_Y_" + str(np.round(self.stage.getPos()[1], 3)) + "_Z_" + str(np.round(self.microscope.getZPosition(), 0))
##                    # changeing "." to "P"
##                    filename = filename.replace(".","P")
#                    # check if need for new folder
#                    if picture_counter >= number_of_folders * number_of_pictures_per_folder:
#                        number_of_folders += 1
#                        new_path = str(relstorepath) + "\\" + str(number_of_folders)
#                        os.mkdir(new_path)
#                    # take cropped picture
#                    self.camera.take_single_cropped_picture(new_path, filename, 
#                                                            self.number_black_pixels_bottom, 
#                                                            self.number_black_pixels_top)
#                    picture_counter += 1
#                # move stage
#                self.stage.goRelative(pre_factor * moving_step_x_direction,
#                                      pre_factor * moving_step_y_direction)
#                time.sleep(sleep_time)
#                recent_up = False
#                # test if x-position exceeds one of the boundary lines
#                if (self.stage.getPos()[0] - moving_step_x_direction > x_right_boundary(self.stage.getPos()[1])) or (self.stage.getPos()[0] + moving_step_x_direction < x_left_boundary(self.stage.getPos()[1])):
#                    # move up along the boundary line
#                    self.stage.goRelative(-ratio_height_to_width * 
#                                          moving_step_y_direction,
#                                          ratio_height_to_width *
#                                          moving_step_x_direction)
#                    time.sleep(sleep_time)
#                    # next scanning line will be in opposite x-direction
#                    positive_x_direction = not(positive_x_direction)
#                    # when recent up than we don't have to take a picture
#                    recent_up = True
#                    break
#            # finished in upper right
#            if not(positive_x_direction):
#                # additional terms because it already moved in y
#                if self.stage.getPos()[1] - moving_step_y_direction - ratio_height_to_width * moving_step_x_direction > pos3[1]:
#                    break
#            # finished in upper left
#            else:
#                # additional terms because it already moved in y
#                if self.stage.getPos()[1] + moving_step_y_direction - ratio_height_to_width * moving_step_x_direction > pos4[1]:
#                    break
#        time_end = time.time()
#        self.UI.message_box("Scan completed! The picures have been stored in " + str(relstorepath))
#        print('Scan completed! The picures have been stored in', relstorepath)
#        print('Time to focus both planes:',time_end_focus-time_start,'\nTime to scan:',time_end-time_end_focus,'\nTime total:',time_end-time_start)        
#        return
#
#    # not needed?
#    def _gauss(self,x, pre_factor, exp_value, standard_deviation, offset):
#        return offset + pre_factor/(standard_deviation*np.sqrt(2*np.pi)) * np.exp((-1./2) * ((x-exp_value)/standard_deviation)**2)
#
#
#    # not needed?
#    def scan_sample_simulation(self, relstorepath, pos1, pos2, pos3, overlap, sleep_time):
#        '''
#        This function scans the sample. It takes a relative path to 
#        a folder where the pictures will be stored. It needs 3 
#        edge points and then scans the area of the smallest rectangle which 
#        encolses all 3 points. Furthermore it needs an overlap beteween 
#        0 and 1.
#        
#        Parameters
#        ----------
#        relstorepath:   string
#                        Relative path where the Pictures will be stored.
#        pos1:           tuple
#                        (x,y)-position of south west point.
#        pos2:           tuple
#                        (x,y)-position of south east point.
#        pos3:           tuple
#                        (x,y)-position of north east point.
#        overlap:        float
#                        Overlap in x-direction (between 0 and 1).
#        '''
#        # defining ratio because step to move up is smaller than sideways
##        ratio_height_to_width = self.screenheight / self.screenwidth
#        
#        self.set_magnification(50)
#        
#        ratio_height_to_width = self.settings['screenheight'] / self.settings['screenwidth']
#        # calculating plane parameter of the focus plane (takes much time)
#        plane_param = [-180.,-51.,-24.,884664.]
#        
#        # ONLY or debugging
#        plt.show()
#        fig,ax = plt.subplots(1)
#        ax.axis('equal')
#        plt.plot([pos1[0],pos2[0],pos3[0]],[pos1[1],pos2[1],pos3[1]],'rx',label='Edge Points')
#               
#        # overwriting the positions with the smallest enclosing rectangle       
#        pos1, pos2, pos3, pos4 = self.smallest_rect(pos1, pos2, pos3)
#        # calculatie the left and right boundary lines
#        if np.abs(pos4[0] - pos1[0]) > 1e-12:
#            slope_l_r_boundary = (pos4[1] - pos1[1]) / (pos4[0] - pos1[0])
#            print("slope: ", slope_l_r_boundary)
#            b_l_boundary = pos1[1] - slope_l_r_boundary * pos1[0]    # y intercept
#            b_r_boundary = pos3[1] - slope_l_r_boundary * pos3[0]    # y intercept
#            x_left_boundary = lambda y: (y - b_l_boundary) / slope_l_r_boundary
#            x_right_boundary = lambda y: (y - b_r_boundary) / slope_l_r_boundary
#        # when slope would be infinit
#        else:
#            print(pos4[0] - pos1[0])
#            x_left_boundary = lambda y: pos1[0]
#            x_right_boundary = lambda y: pos2[0]
#        # calculating x and y of the vecor connecting pos1 and pos2
#        x_proj = pos2[0] - pos1[0]
#        y_proj = pos2[1] - pos1[1] 
#        # calculating the steps in each direction (in mm on substrate)
##        moving_step_x_direction = self.screenwidth * (1 - overlap)
#        moving_step_x_direction = self.settings['screenwidth'] * (1 - overlap)
#        moving_step_y_direction = moving_step_x_direction * (y_proj / x_proj) 
#        # go to starting position
#        self.stage.goAbsolute(pos1[0], pos1[1])
#        # start with scan in positive x-direction
#        positive_x_direction = True
#        # to not take pictures over the boundary lines
#        recent_up = False
#        # split in multiple folders when exceeding 200 pictures
#        number_of_folders = 1                                          
#        new_path = str(relstorepath) + "\\" + str(number_of_folders)    
#        os.mkdir(new_path)
#        picture_counter = 0                                                 
#        while True:
#            # moving a whole line in positive x-direction
#            if positive_x_direction:  
#                pre_factor = 1.
#            # moving a whole line in negatice x-direction
#            else:
#                pre_factor = -1.
#            while True:
#                if not(recent_up):
#                    # focusing
#                    self.microscope.moveZAbsolute(
#                            self.calculate_z_values_of_plane(
#                                    plane_param, 
#                                    self.stage.getPos()[0], 
#                                    self.stage.getPos()[1]))
#                    # take picture
#                    time.sleep(0.05)
#                    # giving the taken picture a name
#                    filename = "X_" + str(np.round(self.stage.getPos()[0], 3)) + "_Y_" + str(np.round(self.stage.getPos()[1], 3)) + "_Z_" + str(np.round(self.microscope.getZPosition(), 0))
##                    # changeing "." to "P"
##                    filename = filename.replace(".","P")
#                    
#                    # ONLY for debugging
##                    with open("TEST.txt","a") as myfile:
##                        myfile.write("X" + str(self.stage.getPos()[0]) + "_Y" + str(self.stage.getPos()[1]) + "_Z" + str(self.microscope.getZPosition()) + "\n")
#                    
#                    # checking if need for new folder
#                    if picture_counter >= number_of_folders * 10:                          
#                        number_of_folders += 1                          
#                        new_path = str(relstorepath) + "\\" + str(number_of_folders)     
#                        os.mkdir(new_path)
#                    # take picture
##                    rect = pat.Rectangle((self.stage.getPos()[0]-self.screenwidth/2,self.stage.getPos()[1]-self.screenheight/2),self.screenwidth,self.screenheight,fill=False,linewidth=0.3,label=picture_counter)
#                    rect = pat.Rectangle((self.stage.getPos()[0]-self.settings['screenwidth']/2,self.stage.getPos()[1]-self.settings['screenheight']/2),self.settings['screenwidth'],self.settings['screenheight'],fill=False,linewidth=0.3,label=picture_counter)
#                    ax.add_patch(rect)
##                    ax.text(self.stage.getPos()[0]-self.screenwidth/2,self.stage.getPos()[1]-self.screenheight/2,str(picture_counter))
#                    ax.text(self.stage.getPos()[0]-self.settings['screenwidth']/2,self.stage.getPos()[1]-self.settings['screenheight']/2,str(picture_counter))
#                    plt.savefig(str(new_path)+"\\"+str(filename)+".png")
#                    # enlarge the total amount of pictures
#                    picture_counter += 1                                
#
#                # move stage
#                self.stage.goRelative(pre_factor * moving_step_x_direction,
#                                      pre_factor * moving_step_y_direction)
#                time.sleep(sleep_time)
#                recent_up = False
#                # test if x-position exceeds one of the boundary lines
#                if (self.stage.getPos()[0] - moving_step_x_direction > x_right_boundary(self.stage.getPos()[1])) or (self.stage.getPos()[0] + moving_step_x_direction < x_left_boundary(self.stage.getPos()[1])):
#                    # move up along the boundary line
#                    self.stage.goRelative(-ratio_height_to_width * 
#                                          moving_step_y_direction,
#                                          ratio_height_to_width *
#                                          moving_step_x_direction)
#                    time.sleep(sleep_time)
#                    # next scanning line will be in opposite x-direction
#                    positive_x_direction = not(positive_x_direction)
#                    # when recent up than we don't have to take a picture
#                    recent_up = True
#                    break
#            # finished in upper right
#            if not(positive_x_direction):
#                # additional terms because it already moved in y
#                if self.stage.getPos()[1] - moving_step_y_direction - ratio_height_to_width * moving_step_x_direction > pos3[1]:
#                    break
#            # finished in upper left
#            else:
#                # additional terms because it already moved in y
#                if self.stage.getPos()[1] + moving_step_y_direction - ratio_height_to_width * moving_step_x_direction > pos4[1]:
#                    break            
#        
#        self.UI.message_box("Scan completed! The picures have been stored in " + str(relstorepath))
#        print('Scan completed! The picures have been stored in', relstorepath)
#        plt.show()       
#        return
    

    def smallest_rect(self, x, y, z):
        '''
        This function takes 3 positions (tuples) and gives back the 4 
        positions (tuples) of the smallest rectangle which encloses all
        the given points.
        
        Parameters
        ----------
        x:      tuple
                South-West point.
        y:      tuple
                South-East point.
        z:      tuble
                North-East point.
        Returns
        -------
        The output is 4 tuples corresponding to the 4 edges of the smallest
        enclosing rectangle. The order of tuples is: South-West, South-East, 
        North-East, North-West.
        
        x_rect: tuple
                South-West point of the smallest enclosing rectangle.
        y_rect: tuple
                South-East point of the smallest enclosing rectangle.
        z_rect: tuple
                North-East point of the smallest enclosing rectangle.
        w_rect: tuple
                North-West point of the smallest enclosing rectangle.       
        '''     
        a1 = np.subtract(y,x)
        a2 = np.subtract(z,y)
        a3 = np.add(a1,a2)        
        proj = np.dot(a3,a1)/np.linalg.norm(a1)
        a1_dir = a1/np.linalg.norm(a1)       
        if proj >= np.linalg.norm(a1):
            y = np.add(y,(proj-np.linalg.norm(a1))*a1_dir)
        else:
            z = np.add(z,(np.linalg.norm(a1)-proj)*a1_dir)
        w = np.subtract(z,np.subtract(y,x))
        x = (x[0],x[1])
        y = (y[0],y[1])
        z = (z[0],z[1])
        w = (w[0],w[1])        
        return x,y,z,w
    
    def parallelogram(self, x, y, z):
        '''
        This function takes 3 positions (tuples) and gives back the 4 
        positions (tuples) of the spanned parallelogram.
        
        Parameters
        ----------
        x:      tuple
                South-West point.
        y:      tuple
                South-East point.
        z:      tuble
                North-East point.
        Returns
        -------
        The output is 4 tuples corresponding to the 4 edges of the spanned
        parallelogram. The order of tuples is: South-West, South-East, 
        North-East, North-West.
        
        x_rect: tuple
                South-West point of the parallelogram.
        y_rect: tuple
                South-East point of the parallelogram.
        z_rect: tuple
                North-East point of the parallelogram.
        w_rect: tuple
                North-West point of the parallelogram.
        ''' 
        x = (x[0],x[1])
        y = (y[0],y[1])
        z = (z[0],z[1])
        w = (x[0]+(z[0]-y[0]),z[1]+(x[1]-y[1]))
        return x,y,z,w        
                


    def calculate_focus_plane_parameters_from_3vectors(self,p1,p2,p3):
        '''
        This function takes three 3-vectors, calculates its plane and 
        gives back the plane parameters A, B, C, D corresponding to the plane 
        equation Ax + By + Cz + D = 0.
        
        Parameters
        ----------
        p1:     list
                The 3-vector of focus point 1 [x_stage, y_stage, z_focus]
        p2:     list
                The 3-vector of focus point 2 [x_stage, y_stage, z_focus]
        p3:     list
                The 3-vector of focus point 3 [x_stage, y_stage, z_focus] 
        Returns
        -------
        plane_param:    list
                        Consisting of the plane parameters [A, B, C, D]
        '''       
        v1 = p3 - p1
        v2 = p2 - p1 
        normal_vec = np.cross(v1, v2)
        A, B, C = normal_vec  
        D = -np.dot(normal_vec, p3)
        return [A,B,C,D]    
        
 
    def calculate_z_values_of_plane(self, plane_par, x, y):
        '''
        This function takes a list with plane parameters and x and y 
        values. It calculates the corresponding z values and returns them.
        
        Parameters
        ----------
        plane_par:  list
                    Plane parameters [A, B, C, D] from the plane equation.
        x:          list
                    List of all x-values of points to calculate z.
        y:          list
                    List of all y-values of points to calculate z.
        Returns
        -------
        z:          list
                    List of all the corresponding z-values for given x and y.
        '''
        
        z = (-plane_par[3]-plane_par[0]*x-plane_par[1]*y)/plane_par[2]
        return z      



    def _number_of_pixels_to_crop(self):
        '''
        This function takes a testpicture at the current position and gives 
        back the number of black pixels on the botton and on top of the image.
        
        Returns
        -------
        bottom:     int
                    Number of black pixels on the bottom of the test picture.
        top:        int
                    Number of black pixels on the top of the test picture.
        '''       
#        self.camera.take_livefeed_picture(self.filepath, 'TestImage')
        self.camera.take_single_cropped_picture(self.filepath, 'TestImage', 0, 0,reduce_size = False)
        path = os.path.join(self.filepath,'TestImage.bmp')
        img = cv2.imread(path, 0)
        right_number = 0
        left_number= 0
        i = 0
        print(np.shape(img))
        while True:
            if img[-1,i] > 200:
                right_number += 1
            if img[-1,-i-1] > 200:
                left_number += 1
            if (img[-1,i] > 200) and (img[-1,-i-1] < 200):
                return left_number, right_number
            i += 1


    def stage_to_sample_coordinates(self, x1, x2, p):
        '''
        Function to calculate the sample coordinates of a point p given in stage
        coordinates. The sample has edge coordinates x1 x2.
    
        Parameters
        ----------    
        x1: tuple
            Tuple containing x and y stage-coordinate of the first edge point 
            of the sample.
        x2: tuple
            Tuple containing x and y stage-coordinate of the second edge point 
            of the sample.
        p:  tuple
            Tuple containing the x and y stage-coordinates of the point on 
            the sample.
    
        Returns
        -------    
        r:  tuple
            Tuple containing x and y sample-coordinates.
        '''
        theta = np.arctan2(x2[1] - x1[1], x2[0] - x1[0]) 
        rot = np.array([[np.cos(theta), -np.sin(theta)],[np.sin(theta), np.cos(theta)]])
        r  = np.dot(np.array(p)-np.array(x1), rot)    
        return r

    
    def sample_to_stage_coordinates(self, x1, x2, p):
        '''
        Function to calculate the stage coordinates of a point p given in sample
        coordinates. The sample has edge coordinates x1 x2.
    
        Parameters
        ----------    
        x1: tuple
            Tuple containing x and y stage-coordinate of the first edge point 
            of the sample
        x2: tuple
            Tuple containing x and y stage-coordinate of the second edge point 
            of the sample
        p:  tuple
            Tuple containing the x and y sample-coordinates of the point on 
            the sample
    
        Returns
        -------    
        r:  tuple
            Tuple containing x and y stage-coordinates.
        '''
        theta = np.arctan2(x2[1] - x1[1], x2[0] - x1[0]) 
        rot = np.array([[np.cos(theta), np.sin(theta)],[-np.sin(theta), np.cos(theta)]])
        r = np.dot(np.array(p), rot) + x1
        return r

        
    
    def move_to_good_flakes_and_take_50x_pictures(self, path_to_files):
        '''
        This function takes pictures with 50x and stores them. The input has 
        to be the path to the folder in which all the txt files are. The store
        folder will be generated and has the name 50x. The sample should not
        be moved after scanning and calling this function.
        
        Additionally it creates txt files with 12 positions (in sample 
        coordinates) each.
        
        Parameters
        ----------
        path_to_files:  string
                        Path to the folder in which all the neccessary files 
                        are located (Plane_Parameters.txt, EdgePoints.txt and
                        GoodFlakes.txt).
        '''
        # XXX new
        # create a counter which counts how many txt files we have with 12 pos each
        number_of_txt_files_with_12_pos = 1
        # give it a name
        name_of_txt_file_with_12_pos = str(path_to_files)+"/Positions_"+str(number_of_txt_files_with_12_pos)+".txt"
        # create an empty txt file which will be filled with 12 positions
        open(name_of_txt_file_with_12_pos, 'w+').close()
        
        
        # set the settings to magnification 10x
        self.set_magnification(10)
        # create path to new folder in which the pictures with 50x will be stored
        path_50x = path_to_files + "\\50x"
        # check if path already exist
        if os.path.exists(path_50x) == True:
            self.UI.message_box("This Folder already exists: " + str(path_50x))
            print("This Folder already exists: ", path_50x)
            return
        # create folder
        os.mkdir(path_50x)       
        # creating our dictionaries
        flake_duden = dict()
        edge_positions = dict()
        # defining the paths to all neccesary files
        path_to_plane_parameters = path_to_files + "\Plane_Parameters.txt"
        path_to_edge_points = path_to_files + "\EdgePoints.txt"
        path_to_good_flakes = path_to_files + "\GoodFlakes.txt"       
        # reading the txtfile of good flakes and adding coordinate lists to dictionary
        # the lists have the structure [x_stage, y_stage, z_10x, x_pixels, y_pixels]
        with open(path_to_good_flakes, 'r') as f:
            for i, line in enumerate(f):
                line = line.split('_')
                flake_duden[i] = [float(line[1]), float(line[3]),
                           float(line[5]), float(line[6]), float(line[7])]
        # reading the edge point file and adding tuples to dictionary
        # the tupels have the form (x_edge, y_edge)
        with open(path_to_edge_points, 'r') as f:
            for i, line in enumerate(f):
                line = line.split(' ')
                edge_positions[i] = (float((line[1])[1:-1]), float((line[2])[:-2]))
        # reading the plane parameter file and storing the parameters in lists
        # the lists have the form [A, B, C, D]
        with open(path_to_plane_parameters, 'r') as f:
            content = f.read()
            content = content.split('\n')
            plane_param_50x = [float(content[1]), float(content[2]), 
                               float(content[3]), float(content[4])]
#            plane_param_10x = [float(content[6]), float(content[7]), 
#                               float(content[8]), float(content[9])] 
        dx = []
        dy = []
        for i in range(len(flake_duden)):
            # dx (dy) is the distances on the x (y) axis away from the center
            dx.append(-self.settings['screenwidth']/2. \
                + (flake_duden[i])[3]/self.settings['mm_to_pixel'])
            dy.append(self.settings['screenheight']/2. \
                - (flake_duden[i])[4]/self.settings['mm_to_pixel'])   
        self.set_magnification(50)
        # moving to the good flakes, focusing and taking pictures
        for i in range(len(flake_duden)):          
            # moving to the i-th good flake
            self.stage.goAbsolute((flake_duden[i])[0] + dx[i],
                                  (flake_duden[i])[1] + dy[i])
            # current positions in stage coord
            x, y = self.stage.getPos()
            # calculating z at this position
            z = self.calculate_z_values_of_plane(plane_param_50x, x, y)
            # focusing
            self.microscope.moveZAbsolute(z)
            # getting the positions in sample coordinates
            (x_sample, y_sample) = self.stage.getPosSampleCoordinates(
                    edge_positions[0], edge_positions[1])
            # defining file name of the 50x picture
            # the filname has the form x_stage_y_stage_z_50x_x_sample_y_sample
            filename =  "X_" + str(np.round(x, 3)) + "_Y_" \
                        + str(np.round(y, 3)) + "_Z_" + str(np.round(z, 0)) \
                        + "_x_" + str(np.round(x_sample, 3)) \
                        + "_y_" + str(np.round(y_sample, 3))
            time.sleep(2)
            # taking a picture and storing it in the 50x folder
            self.camera.take_single_cropped_picture(path_50x, 
                                                    filename, 
                                                    self.number_black_pixels_bottom, 
                                                    self.number_black_pixels_top)
            
            # XXX new
            # write a line in txt file
            with open(name_of_txt_file_with_12_pos,'a') as file:
                file.write('{:<7} {:<7} {:<7}'.format(str((i%12)+1),
                           str(np.round(x_sample, 3)),
                           str(np.round(y_sample, 3))+'\n'))
            # check if already 12 entries in txt file
            # if thats the case make a new one and write the first entry
            if (i+1)%12 == 0:
                # create new txt file
                number_of_txt_files_with_12_pos += 1
                name_of_txt_file_with_12_pos = str(path_to_files)+"/Positions_"+str(number_of_txt_files_with_12_pos)+".txt"
                # create new empty txt file
                open(name_of_txt_file_with_12_pos, 'w+').close()
                # write first line in new txt file
                with open(name_of_txt_file_with_12_pos,'a') as file:
                    file.write('{:<7} {:<7} {:<7}'.format(str((i%12)+1),
                               str(np.round(x_sample, 3)),
                               str(np.round(y_sample, 3))+'\n'))           
                

        # in the very end change magnification back to 10x    
        self.set_magnification(10)


    def move_to_flake(self, title_of_picture_50x): 
        '''
        This function moves the stage to a good flake seen on a 50x image.
        The sample should not be moved after scanning and calling this function.
        
        Parameters
        ----------
        title_of_picture:   string
                            Is the title of the 50x picture on which the flake is.
        pixel_coordinates:  tuple
                            Coordinates of the good flake in pixel-coord. The
                            (0,0) is set at the upper left point of the image.
        
        '''
        self.set_magnification(10)
        title_of_picture_50x = title_of_picture_50x.split('_')
        # the list has the structure [x_stage, y_stage, z_50x, x_sample, y_sample]
        stage_coordinates = [float(title_of_picture_50x[1]), 
                             float(title_of_picture_50x[3]),
                             float(title_of_picture_50x[5]),
                             float(title_of_picture_50x[7]),
                             float(title_of_picture_50x[9])]
        dx = -self.settings['screenwidth']/2. \
            + stage_coordinates[3]/self.settings['mm_to_pixel']
        dy = self.settings['screenheight']/2. \
            - stage_coordinates[4]/self.settings['mm_to_pixel']
        # moving to the flake
        self.stage.goAbsolute(stage_coordinates[0] + dx,
                              stage_coordinates[1] + dy)
        # focusing
        self.microscope.moveZAbsolute(stage_coordinates[2])      

   
    def set_magnification(self, magn=10):
        '''
        This function sets all the settings to the desired magnification 10x
        or 50x.
        '''
        if magn == 10:
            # moving to the right objective
            if self.microscope.getCurrentObjective() == 100:
                self.microscope.moveObjectiveBackwards()
                self.microscope.moveObjectiveBackwards()
                self.microscope.moveObjectiveBackwards()
            elif self.microscope.getCurrentObjective() == 50:
                self.microscope.moveObjectiveBackwards()
                self.microscope.moveObjectiveBackwards()    
            elif self.microscope.getCurrentObjective() == 20:
                self.microscope.moveObjectiveBackwards()
            elif self.microscope.getCurrentObjective() == 5:
                self.microscope.moveObjectiveForward()
            self.settings['magnification'] = magn
            self.settings['screenwidth'] = 1.9749 #0.8660    # mm
            self.settings['screenheight'] = 1.4043 #0.6271   # mm 
            self.settings['mm_to_pixel'] = 647.12 #724.65    # pixel per mm
        elif magn == 50:
            # moving to the right objective
            if self.microscope.getCurrentObjective() == 100:
                self.microscope.moveObjectiveBackwards()
            elif self.microscope.getCurrentObjective() == 20:
                self.microscope.moveObjectiveForward()   
            elif self.microscope.getCurrentObjective() == 10:
                self.microscope.moveObjectiveForward()
                self.microscope.moveObjectiveForward()
            elif self.microscope.getCurrentObjective() == 5:
                self.microscope.moveObjectiveForward()
                self.microscope.moveObjectiveForward()
                self.microscope.moveObjectiveForward()
            self.settings['magnification'] = magn
            self.settings['screenwidth'] = 0.39498 #0.17556    # mm
            self.settings['screenheight'] = 0.28086 #0.12712   # mm  
            self.settings['mm_to_pixel'] = 3235.61 #3571.45   # pixel per mm            
        elif magn == 20:
            # moving to the right objective
            if self.microscope.getCurrentObjective() == 100:
                self.microscope.moveObjectiveBackwards()
                self.microscope.moveObjectiveBackwards()
            elif self.microscope.getCurrentObjective() == 50:
                self.microscope.moveObjectiveBackwards()    
            elif self.microscope.getCurrentObjective() == 10:
                self.microscope.moveObjectiveForward()
            elif self.microscope.getCurrentObjective() == 5:
                self.microscope.moveObjectiveForward()
                self.microscope.moveObjectiveForward()
            self.settings['magnification'] = magn
            self.settings['screenwidth'] = 0.98742 #0.4264    # mm
            self.settings['screenheight'] = 0.70218 #0.3087   # mm 
            self.settings['mm_to_pixel'] = 1294.28 #1470.6    # pixel per mm               
        elif not(magn == 10) and not(magn == 50) and not(magn == 20):
            print("Magnification has to be set to either 10, 20 or 50. Moved to 10x.")
            self.set_magnification(10)
            return        


def scan_sample_complete(sleep_time=1):
    '''
    This function performs a scan of a sample. All the tasks the user has to
    fulfill are displayd on the screen using tkinter. The user only has to 
    follow the instructions given.
    
    '''
    time_start = time.time()
    # defining a maximum number of pictures per folder
    number_of_pictures_per_folder = 5
    # initializing the userinterface class
    UX = UI()
    # starting a userinterface which asks for magnificatin and overlap
    UX.call_initial_program_start()
    # in case the user cancelled
    if UX.cancel == True:
        return    
    # assign the user given magnification and overlap
    given_magnification = UX.mag
    overlap = UX.ovlap
    # popping a dialog which askes for the storpath
    UX.call_startup_message_boxes()
    if UX.cancel == True:
        return
    try:
        storepath = UX.filepath
    except:
        storepath = ''
    if storepath == '':
        return
    # initializing the glovebox class
    GB = GloveBox(storepath)
    print("Pixels to crop bottom:", GB.number_black_pixels_bottom)
    print("Pixels to crop top:", GB.number_black_pixels_top)
    GB.camera.take_single_cropped_picture('','crop_test',GB.number_black_pixels_bottom,GB.number_black_pixels_top)
    # initializing the call-back userinterface
    UXCB = UICB(GB)
    positions = ['South-West', 'South-East', 'North-East']
    # this list will be filled with the edge-tuples
    edges = []
    # this list will be filled with focus-vectors for all 3 positions
    # fist entry is the 3-vector for the focusPos near edge1, etc.
    focus_vectors_given_mag = []
    # same here
    focus_vectors50x = []
    for i in range(len(positions)):
        # set the right objective
        GB.set_magnification(given_magnification)
        UX.message_box('Please move to the Edge: ' + str(positions[i])+ '\n'
                   'and press \'OK\'.')
        if UX.cancel == True:
            return
        edges.append(GB.stage.getPos())
        UXCB.get_focuspos_3vector('Move a little bit into the sample and \n'
                                  'focus manually using the buttons below.')
        focus_vectors_given_mag.append(np.array([GB.stage.getPos()[0],
                                          GB.stage.getPos()[1],
                                          GB.microscope.getZPosition()]))
        if UXCB.cancel == True:
            return
        GB.set_magnification(50)
        UXCB.get_focuspos_3vector('Focus manually in this very neighborhood \n'
                                  'using the buttons below.')
        focus_vectors50x.append(np.array([GB.stage.getPos()[0],
                                          GB.stage.getPos()[1],
                                          GB.microscope.getZPosition()]))
        if UXCB.cancel == True:
            return   
    focus_vectors_given_mag_auto = GB.get_auto_focus_vectors(
            focus_vectors_given_mag, given_magnification)
    focus_vectors50x_auto = GB.get_auto_focus_vectors(
            focus_vectors50x, 50)
    


    
#    focus_vectors_given_mag_auto = [np.array([2.4712e+00, 1.4993e+00, 3.6240e+04]), np.array([1.16749e+01, 1.68400e+00, 3.59170e+04]), np.array([9.9456e+00, 2.0688e+01, 3.5294e+04])]
#    focus_vectors50x_auto = [np.array([2.7556e+00, 1.4410e+00, 3.5385e+04]), np.array([1.20829e+01, 1.67760e+00, 3.50940e+04]), np.array([1.01974e+01, 2.01202e+01, 3.44350e+04])]

    
    GB.set_magnification(given_magnification)
    # split in multiple folders when exceeding this number pictures
    number_of_folders = 1
    # create first folder
    new_path = str(GB.filepath) + "\\" + str(number_of_folders)
    os.mkdir(new_path)        
    # creating txt file with edge points
    path_edges = os.path.normpath(os.path.join(GB.filepath,'EdgePoints.txt'))
    with open(path_edges, 'w+') as f:
        f.write("Pos1: " + str(edges[0]))
        f.write("\nPos2: " + str(edges[1]))
        f.write("\nPos3: " + str(edges[2]))    
    # calculating plane parameter of the focus plane for 50x
#    plane_param_50x = GB.calculate_focus_plane_parameters_from_3vectors(
#            focus_vectors50x[0], focus_vectors50x[1], focus_vectors50x[2])  
    plane_param_50x = GB.calculate_focus_plane_parameters_from_3vectors(
            focus_vectors50x_auto[0], 
            focus_vectors50x_auto[1], 
            focus_vectors50x_auto[2])               
    # writing the plane parameters of 50x in a txt file
    path_plane_param = str(GB.filepath) + "\Plane_Parameters.txt"
    with open(path_plane_param, 'w+') as f:
        f.write("50x:\n")
        for parameter in plane_param_50x:
            f.write("%s\n" % parameter)  
    # calculating plane parameter of the focus plane for 10x
#    plane_param_given_mag = GB.calculate_focus_plane_parameters_from_3vectors(
#            focus_vectors_given_mag[0], focus_vectors_given_mag[1], focus_vectors_given_mag[2]) 
    plane_param_given_mag = GB.calculate_focus_plane_parameters_from_3vectors(
            focus_vectors_given_mag_auto[0], 
            focus_vectors_given_mag_auto[1], 
            focus_vectors_given_mag_auto[2]) 
    # appending the txt file with the plane parameters for 10x
    with open(path_plane_param, 'a') as f:
        f.write(str(given_magnification)+"x:\n")
        for parameter in plane_param_given_mag:
            f.write("%s\n" % parameter)    
    # printing some stuff
    print("Edge Point SW:", edges[0])
    print("Edge Point SE:", edges[1])
    print("Edge Point NE:", edges[2])
    print('Storepath:', GB.filepath)
    print('Focus vectors 50x:', focus_vectors50x)
    print('Focus vectors 50x (auto):', focus_vectors50x_auto)
    print("Focus Plane Parameter 50x (auto):", plane_param_50x) 
    print('Focus vectors '+str(given_magnification)+'x:', focus_vectors_given_mag)
    print('Focus vectors (auto) '+str(given_magnification)+'x:', focus_vectors_given_mag_auto)
    print("Focus Plane Parameter (auto) "+str(given_magnification)+"x:", plane_param_given_mag)    
    time_end_focus = time.time()     
    # defining ratio because step to move up is smaller than sideways
    ratio_height_to_width = GB.settings['screenheight'] / GB.settings['screenwidth']      
    # overwriting the positions with the smallest enclosing rectangle       
    pos1, pos2, pos3, pos4 = GB.smallest_rect(edges[0], edges[1], edges[2])
#    # or with a parallelogram
#    pos1, pos2, pos3, pos4 = GB.parallelogram(edges[0], edges[1], edges[2])
    # calculatie the left and right boundary lines
    if np.abs(pos4[0] - pos1[0]) > 1e-12:
        slope_l_r_boundary = (pos4[1] - pos1[1]) / (pos4[0] - pos1[0])
        b_l_boundary = pos1[1] - slope_l_r_boundary * pos1[0]    # y intercept
        b_r_boundary = pos3[1] - slope_l_r_boundary * pos3[0]    # y intercept
        x_left_boundary = lambda y: (y - b_l_boundary) / slope_l_r_boundary
        x_right_boundary = lambda y: (y - b_r_boundary) / slope_l_r_boundary
    # when slope would be infinit
    else:
        x_left_boundary = lambda y: pos1[0]
        x_right_boundary = lambda y: pos2[0]        
    # calculating x and y of the vecor connecting pos1 and pos2
    x_proj = pos2[0] - pos1[0]
    y_proj = pos2[1] - pos1[1] 
    # calculating the steps in each direction (in mm on substrate)
    print('screenwidth',GB.settings['screenwidth'])
    moving_step_x_direction = GB.settings['screenwidth'] * (1 - overlap)
    moving_step_y_direction = moving_step_x_direction * (y_proj / x_proj) 
    # go to starting position
    GB.stage.goAbsolute(pos1[0], pos1[1])
    # start with scan in positive x-direction
    positive_x_direction = True
    # to not take pictures over the boundary lines
    recent_up = False
    # count the number of pictures to not overfill the folders
    picture_counter = 0  
    while True:
        # moving a whole line in positive x-direction
        if positive_x_direction:  
            pre_factor = 1.
        # moving a whole line in negatice x-direction
        else:
            pre_factor = -1.
        while True:
            if not(recent_up):
                # focusing
                GB.microscope.moveZAbsolute(
                        GB.calculate_z_values_of_plane(
                                plane_param_given_mag, 
                                GB.stage.getPos()[0], 
                                GB.stage.getPos()[1]))
                time.sleep(0.05)
                # giving the taken picture a name
                filename = "X_" + str(np.round(GB.stage.getPos()[0], 3)) + "_Y_" + str(np.round(GB.stage.getPos()[1], 3)) + "_Z_" + str(np.round(GB.microscope.getZPosition(), 0))
                # check if need for new folder
                if picture_counter >= number_of_folders * number_of_pictures_per_folder:
                    number_of_folders += 1
                    new_path = str(GB.filepath) + "\\" + str(number_of_folders)
                    os.mkdir(new_path)
#                    pool = mp.Pool(mp.cpu_count())
                    
                # take cropped picture
                GB.camera.take_single_cropped_picture(new_path, filename, 
                                                        GB.number_black_pixels_bottom, 
                                                        GB.number_black_pixels_top)
                picture_counter += 1
            # move stage
            GB.stage.goRelative(pre_factor * moving_step_x_direction,
                                  pre_factor * moving_step_y_direction)
            time.sleep(sleep_time)
            recent_up = False
            # test if x-position exceeds one of the boundary lines
            if (GB.stage.getPos()[0] - moving_step_x_direction > x_right_boundary(GB.stage.getPos()[1])) or (GB.stage.getPos()[0] + moving_step_x_direction < x_left_boundary(GB.stage.getPos()[1])):
                # move up along the boundary line
                GB.stage.goRelative(-ratio_height_to_width * 
                                      moving_step_y_direction,
                                      ratio_height_to_width *
                                      moving_step_x_direction)
                time.sleep(sleep_time)
                # next scanning line will be in opposite x-direction
                positive_x_direction = not(positive_x_direction)
                # when recent up than we don't have to take a picture
                recent_up = True
                break
        # finished in upper right
        if not(positive_x_direction):
            # additional terms because it already moved in y
            if GB.stage.getPos()[1] - moving_step_y_direction - ratio_height_to_width * moving_step_x_direction > pos3[1]:
                break
        # finished in upper left
        else:
            # additional terms because it already moved in y
            if GB.stage.getPos()[1] + moving_step_y_direction - ratio_height_to_width * moving_step_x_direction > pos4[1]:
                break
    pathtofinish = os.path.join(GB.filepath,r'scan_finished')
    os.mkdir(pathtofinish)
    shutil.copy(os.path.join(GB.filepath,r'EdgePoints.txt'),pathtofinish)
    shutil.copy(os.path.join(GB.filepath,r'Plane_Parameters.txt'),pathtofinish)
    time_end = time.time()
    print('Wait for AI')
    time.sleep(60)
    filepath = r'C:\Users\Nele\Documents\GloveBox\gloveboxnele\NeuralNetwork\scan_finished'
#    GB = GloveBox(r'C:\Users\Nele\Documents\GloveBox\GloveBoxAutomation\NeuralNetwork')
    GB.move_to_good_flakes_and_take_50x_pictures(filepath)
        
    GB.stage.close()
    UX.message_box_only("Scan completed! The picures have been stored in " + str(GB.filepath))
    print('Scan completed! The picures have been stored in', GB.filepath)
    print('Time to focus both planes:',time_end_focus-time_start,'\nTime to scan:',time_end-time_end_focus,'\nTime total:',time_end-time_start)        
    return
    
    



## not needed?         
#def start_program():
#    '''
#    Function that starts the whole program. Output are all the files which
#    the scan produces.
#    '''
#    UX = UI(stage=True)
#    UX.call_startup_message_boxes()
#    if UX.cancel == True:
#        return
#    try:
#        storepath = UX.filepath
#    except:
#        storepath = ''
#    if storepath == '':
#        return
#    pos1, pos2, pos3 = UX.get_edge_points_message_boxes()
#    if pos1 is None:
#        return
#    print("Edge Point SW:", pos1)
#    print("Edge Point SE:", pos2)
#    print("Edge Point NE:", pos3)
#    path = os.path.normpath(os.path.join(storepath,'EdgePoints.txt'))
#    with open(path, 'w+') as f:
#        f.write("Pos1: " + str(pos1))
#        f.write("\nPos2: " + str(pos2))
#        f.write("\nPos3: " + str(pos3))
#    print('Storepath:', storepath)
#    GB = GloveBox(storepath)
#    GB.scan_sample(storepath, pos1, pos2, pos3, 0.1, 1)
#    GB.stage.close()
    
    

def reload_sample():
    '''
    This function moves to a desired position in sample coordinates. First it 
    asks to manually move to the two lower edges of the sample in order to
    calculate the new sample coordinate system. Furthermore it asks for the
    sample coordinates to move to. Being there the focus and objective can be
    set using the userinterface generated with tkinter.
    '''  
    GB = GloveBox(r'C:\Users\VTIB16\Desktop')
    UXCB = UICB(GB)
    UX = UI()
    # reading in edge points
    UX.message_box('Please move to Edge Point: South-West\n'
                   'and press \'OK\'.')
    if UX.cancel == True:
        return
    edge1 = GB.stage.getPos()
    UX.message_box('Please move to Edge Point: South-East\n'
                   'and press \'OK\'.')
    if UX.cancel == True:
        return
    edge2 = GB.stage.getPos()    
    # reading in the desired point in sample-coordinates
    x_sample, y_sample = UX.enter_sample_coordinates()
    if x_sample is None:
        return
    try:
        x_sample = float(x_sample)
        y_sample = float(y_sample)
    except ValueError:
        UX.message_box_only("Please enter only numbers. Restart the program.")
        return    
    GB.stage.goAbsoluteSampleCoordinates(x_sample, y_sample, edge1, edge2)
    UXCB.focusing_and_changing_objectives_manually('Use the buttons below to focus. Use \'Obj-\' '
                                                   '\nand \'Obj+\' to change objective.')

def reload_sample_load_txt():
    '''
    This function loads txt files which contain 12 positions. By pressing
    the corresponding botton the stage automativally moves to this position.
    Prior to that one needs to read in the edges to get the sample coordinate
    system.
    '''  
    GB = GloveBox(r'C:\Users\VTIB16\Desktop')
    UXCB = UICB(GB)
    UX = UI()
    # reading in edge points
    UX.message_box('Please move to Edge Point: South-West\n'
                   'and press \'OK\'.')
    if UX.cancel == True:
        return
    edge1 = GB.stage.getPos()
    UX.message_box('Please move to Edge Point: South-East\n'
                   'and press \'OK\'.')
    if UX.cancel == True:
        return
    edge2 = GB.stage.getPos()    
    # reading in the desired point in sample-coordinates
    UXCB.reload_sample(edge1, edge2)



#def Get_Focus_Point_From_Picures_test(folderpath):
#    '''
#    This function defines the focus point via fitting the variation of the
#    laplace transformation and looking for its peak. It takes a path
#    to the folder in which the focus pictures are.
#    
#    Parameters
#    ----------
#    folderpth:  string
#                relative path to a folder where the focus pictures are located.
#    '''              
#    # Path where we stored the pictures
#    #folderpath = os.path.normpath(r'{path}'.format(path=folderpath))
#    zPositions = []
#    sigma_arr = []
#    # calculating the variation of the laplace
#    for i,file in enumerate(os.listdir(folderpath)):
#        # Open the image and make a Laplace transformation
#        # Calculate the standardeviation of the laplace transformation
#        # Save the variable
#        zPositions.append(float(file[:-4]))
#        image = cv2.imread(os.path.join(folderpath,file))
#        laplace = cv2.Laplacian(image, cv2.CV_64F, ksize=1)
#        cv2.imshow('laplace', laplace)
#        cv2.waitKey(0)
#        sigma = laplace.var()
#        
#        #sigma = cv2.Laplacian(image, cv2.CV_64F).var()
#        
#        sigma_arr.append(sigma)
#    cv2.destroyAllWindows()
#                   
#    # Plot
#    fig = plt.figure()
#    plt.plot(zPositions, sigma_arr,'rx')
##        # Fit with Gauss
##        popt_gauss, pcov_gauss = curve_fit(self._gauss, zPositions, sigma_arr,p0 = [np.max(sigma_arr), zPositions[np.argmax(sigma_arr)], 400, 1e13])        
##        plt.plot(zPositions, self._gauss(zPositions,*popt_gauss),'b')   
#    plt.savefig(str(folderpath[:-13]) + 'Pos1_10' + "x_test2.jpg", dpi=500)
#    plt.close(fig)  
##        return popt_gauss[1]
#    return zPositions[np.argmax(sigma_arr)]


#%%
if __name__ == "__main__": 
    scan_sample_complete(sleep_time=1)
#    time.sleep(60)
#    Get_Focus_Point_From_Picures_test(r'C:\Users\Nele\Pictures\ML\Test_Scan_6\Pictures_Pos1')

#    reload_sample()
    
    
    
#    reload_sample()
#    UX = UI(stage=True)
#    while True:  
#        if UX.cancel == True:
#            break
#        UX.move_focus()
#    GB = GloveBox('')
#    UX = UI(GB)
#    UX.move_focus()
    
#        
#    
#    print(UX.z_pos)
#    UX.stage.close()
    
    
#    filepath = os.path.normpath(r'C:\Users\VTIB16\Documents\GloveBoxAutomation')
##    filepath = os.path.normpath(r'C:\Users\TIM\Documents\GloveBox')
#    GB = GloveBox(filepath)
##    GB.move_to_good_flakes_and_take_50x_pictures(r'C:\Users\VTIB16\Pictures\RevisitChip1-small-section')
##    print(GB.stage.getPos())
#    GB.stage.goAbsoluteSampleCoordinates(3.202595023899138, 0.8867853138705405,(-17.142, -22.0732),(-6.4006, -23.1699))
#    GB.set_magnification(50)
##    print(GB.stage.getPosSampleCoordinates((-3.5302, -28.9442),(7.0735, -27.0352)))
#    GB.stage.close()
#    GB.stage.goAbsoluteSampleCoordinates(15.35581614,23.82488518, (-6.497,-28.4861),(41.7507,-28.5325))
#    time.sleep(4)
#    GB.camera.take_single_cropped_picture(GB.filepath,'RevisitChip1_15.35581614_23.82488518',GB.number_black_pixels_bottom,GB.number_black_pixels_top)
#    GB.stage.close()
    # Chip1
#    print(GB.stage_to_sample_coordinates((-48.033,-47.5069),(0.3734,-46.0737),(-10.948,-31.654)))
    # Chip2
#    print(GB.stage_to_sample_coordinates((-48.9861,-39.1159),(-2.3197,-38.0969),(-20.859,1.207)))
    
    
    
#    GB.move_to_good_flakes_and_take_pictures(r'C:\Users\TIM\Desktop\Test')
#    GB.set_magnification(10)
#    print(GB.settings)
#    GB.set_magnification(50)
#    print(GB.settings)    
#    GB.set_magnification(20)
#    print(GB.settings)    

#    img = cv2.imread(filepath + "\TestImageClassHandle_LowerScreen.bmp", 0)  
#    crop_img = img[57:-58, :]
#    plt.plot(np.arange(len(crop_img[:,0])),crop_img[:,0])
#    print(len(img[0,:]))
#    print(len(crop_img[0,:]))
#    plt.show()

    
#    # taking pictures and focus plots
#    filepath = os.path.normpath(r'C:\Users\VTIB16\Documents\GloveBoxAutomation')
#    GB = GloveBox(filepath)
#    GB.Take_Focus_Pictures(filepath + '\FocusPicturesGraphite50x')
#    GB.Get_Focus_Point_From_Picures(filepath + '\FocusPicturesGraphite50x')
#    GB.stage.close()
    
#    GB.camera.take_single_cropped_picture(filepath, 'TestCrop', GB.number_black_pixels_bottom, GB.number_black_pixels_top)
#    GB.stage.close()
    
#    GB = GloveBox('')
#    print(GB.stage.getPos())
#    GB.stage.close()
#    GB.stage.close()
    
#    filepath = os.path.normpath(r'C:\Users\TIM\Documents\GloveBox')
#    GB = GloveBox(filepath)
##    GB.camera.take_single_cropped_picture(filepath, 'Cropped', 2,1)
##    GB.camera.take_livefeed_picture(filepath, 'Reference_noCrop')
##    img = cv2.imread(filepath + "\Reference_Crop.bmp", 0)
##    print("Total Pixels Reference_Crop:",len(img[:,0]))
##    img2 = cv2.imread(filepath + "\Cropped.bmp", 0)
##    print("Total Pixels Reference_noCrop:",len(img2[:,0]))
#    plt.figure()
#    img2 = cv2.imread(filepath + "\TestImageClassHandle_UpperScreen.bmp", 0)
#    width = len(img2[0,:])
#    height = len(img2[:,0])
#    plt.plot(np.arange(height),img2[:,0])
#    plt.show()
#    
#    #Now we crop the image
#    plt.figure()
#    crop_img = img2[17:-17, :]
#    plt.plot(np.arange(len(crop_img[:,0])),crop_img[:,0])
#    plt.show()
#    print("Total Pixels Reference_noCrop:",len(img2[:,0])    

    
##    GB.scan_sample_simulation(r"C:\Users\TIM\Desktop\Test",(0.,0.),(4.9,0.1),(5.,5.),0.2,0)
##    GB.get_vectors_of_inner_positions_userinterface((0.,0.),(4.9,0.1),(5.,5.))
#    print(GB.number_of_pixels_to_crop('TestImageClassHandle_LowerScreen.bmp'))
    
#      start_program()  
    
#    filepath = os.path.normpath(r'C:\Users\VTIB16\Documents\GloveBoxAutomation')
#    filepath = os.path.normpath(r'C:\Users\TIM\Documents\GloveBox')
#    UX = UI()
#    filepath = UX.get_filepath()
#    print(filepath)
#    #filepath = os.path.normpath(r'\\windata.phys.ethz.ch\nano\POBox\Tim Davatz\Tim\Focus Test Pos 1\Focus_Tim_LowRes_sleep(0.05)')
#    GB = GloveBox(filepath)
#    print(GB.start_program())
#    print(GB.get_points_to_do_focus((0,0),(4.9,0.1),(5.,5.),0.1))
#    GB.stage.setPosZero()
#    print(GB.stage.getPos())
#    GB.scan_sample_simulation(r"C:\Users\TIM\Desktop\Test",(0.,0.),(4.9,0.1),(5.,5.),0.2,0)
#    print(GB.smallest_rect((0.,0.),(5.,0.),(5.,5.)))
#    GB.microscope.moveZAbsolute(35000)
#    time.sleep(0.05*30)
#    print(GB.microscope.getZPosition())
#    GB.microscope.moveZAbsolute(40000)
#    time.sleep(0.05*30)
#    print(GB.microscope.getZPosition())
#    
#    GB.stage.goRelative(-0.5,-0.5)
#    time.sleep(2)
##    GB.stage.setPosZero()
#    print(GB.stage.getPos())
##    GB.stage.goRelative(0,1)
#
##    print(GB.stage.getPos())
#    ____________________________________________________________________________
#    GB.stage.close()
    #print(GB.Get_Focus_Point_From_Picures(filepath))
    #print(GB.compute_focus_plane((1,2),(8,3),(9,7)))
#    GB.scan_sample("myStorePath",(3.8,1.3),(1.,1.),(4.5,2.4),0.3)
#    GB.scan_sample("myStorePath",(-2,0),(1.5,-1.5),(1.6,.3),0.1,'Test2_NOT')
#    print(GB.smallest_rect((-2,-.5),(2,0),(1,1)))
#    GB.get_focus_plane_z_values((1,2),(8,3),(9,7))
#    print(GB.scan_sample("myStorePath",(-2,0),(1.5,-1.5),(1.6,3),0.1))
#    print(GB.smallest_rect((-2,0),(1.5,-1.5),(1.6,3)))




#    # Plot the focus plane    
#    xx, yy = np.meshgrid(range(0,12),range(-7,7))
#    plane_par = GB.calculate_focus_plane_parameters([8.,-3.1276],[5.,2.8724],[2.,-5.1276])
#    zz = GB.calculate_z_values_of_plane(plane_par,xx,yy)   
#    plt3d = plt.figure().gca(projection='3d')
#    plt3d.plot_wireframe(xx, yy, zz, alpha=0.3)
#    plt3d.view_init(30,80)
#    ax = plt.gca()
#    ax.scatter(10.,-4.1276,36211.16,label='Position 1')
#    ax.scatter(8.,-3.1276,36174.47,label='Position 2')
#    ax.scatter(5.,2.8724,36095.91,label='Position 3')
#    ax.scatter(2.,-5.1276,36052.12,label='Position 4')
#    plt.xlabel('X')
#    plt.ylabel('Y')
#    ax.set_zlabel('Z')
#    plt.legend(loc='best')
#    plt.savefig('Plane_Fit2.jpg', dpi=500)#, bbox_inches='tight')
#    plt.show()
#    print("Distance from Position 1 to plane: epsilon = ",(plane_par[0]*10.+plane_par[1]*(-4.1276)+plane_par[2]*36211.16+plane_par[3])/(np.sqrt(plane_par[0]**2+plane_par[1]**2+plane_par[2]**2)))
    
    
    
    
    #%%


    #GB.camera.takeHighResPicture('Test','test2')
    
    #%%
##    t1 = time.time()
##    GB.Focus('Focus_Tim_UltraHighRes')
##    t2 = time.time()
##    print("Delta t = ", t2 - t1)
#    t1 = time.time()
#    GB.Take_Focus_Pictures('Focus_Tim_HighRes_Cropped_Pos4_sleep(0.05)')
#    t2 = time.time()
#    print("Delta t = ", t2 - t1)
   
    #%%
    #print(GB.AnalyzeFocusPoint(r'C:\Users\VTIB16\Documents\FocusTest\Focus1'))


    #%%
    

    
    #(5.0, 5.0, 0.0)
    
    #%%

    
    #(5.9999, 5.9998, 0.0)
    
    #%%
#    GB.Focus('Focus2')
#    GB.AnalyzeFocusPoint(r'C:\Users\VTIB16\Documents\FocusTest\Focus2')
#    #%%
#    GB.stage.goAbsolute(2,2)
#    print(GB.stage.getPos())
#    
#    #%%
#    GB.Focus('Focus4')
#    GB.AnalyzeFocusPoint(r'C:\Users\VTIB16\Documents\FocusTest\Focus4')