# -*- coding: utf-8 -*-
"""
Created on Fri Jun 29 16:30:15 2018

@author: Benedikt
"""
import os
import subprocess
import string
import win32gui
import win32ui
import win32con
import win32com.client
from time import sleep
from PIL import Image
import time
import cv2
import numpy as np 

class Camera(object):
    '''
    This is a class to control the picture taking.
    '''

    def __init__(self, folderpath):
        '''
        Initialize all the relevant parameters.
        '''
        self.folderpath = folderpath
        self.windowhandle = self.get_handle_to_NIS_window()
        self.feedhandle = self.get_handle_to_NIS_livefeed()

    # not needed?
    def takeHighResPicture(self,relativePath, filename):
        '''
        This is a function to extract high resolution pictures form the NIS
        Elements using a cmd line macro. The file will be stored to
        self.folderpath.

        Parameters
        ----------
        filename:   string
                    Filename of the picture taken.
        '''
        # Get the full filepath of the picture
        filepath = os.path.join(self.folderpath, relativePath,filename+'.tif')
        fileIn = open(os.path.join(r'C:\Users\VTIB16\Documents\GloveBoxAutomation\Camera','save_img_macro_fast_template.mac'))
        rawTemp = string.Template(fileIn.read())
        fileIn.close()
        output = rawTemp.substitute({'filepath': filepath})
        print(output)
        with open('temp.mac','w') as f:
            f.writelines(output)
        subprocess.call('temp.mac', shell =True)
        
        
#    def takeHighResPicture(self, filename):
#        '''
#        This is a function to extract high resolution pictures form the NIS
#        Elements using a cmd line macro. The file will be stored to
#        self.folderpath.
#
#        Parameters
#        ----------
#
#        filename:   string
#                    Filename of the picture taken.
#        '''
#        # Get the full filepath of the picture
#        filepath = os.path.join(self.folderpath,filename+'.tif')
#        fileIn = open('save_img_macro_fast_template.mac')
#        rawTemp = string.Template(fileIn.read())
#        fileIn.close()
#        output = rawTemp.substitute({'filepath': filepath})
#        print(output)
#        with open('temp.mac','w') as f:
#            f.writelines(output)
#        subprocess.call('temp.mac', shell =True)
#        p = Popen("save_img_macro_fast.mac", cwd=path)
#        stdout, stderr = p.communicate()

        # Rewrite the filepath line in the macro
        # Subprocess.run is waht e
        # Run the macro

#    def takeLowResPicture(self, filename):
#        pass
    


#    # not needed
#    def _get_windows_by_title(self, title_text, exact = True):
#        '''
#        This is a function which takes the title of a window and gives back its 
#        handle(s) of the window in a list.
#            
#        Parameters
#        ----------        
#        title_text:     string
#                        Title of the window for which I want to know the handle(s).                        
#        exact:          bool
#                        If False it gives a list of all handles whose title contain
#                        title_text, if True it gives the handle(s) with matching titles.        
#        Output
#        ------       
#        The output is a list of all handles which correspond to a given title 
#        *title_text*, either it matches exactly with the real title (in case 
#        *exact = True*, default) or *title_text* is only contained in it 
#        (in case *exact = False*).  
#        '''
#        def _window_callback(hwnd, all_windows):
#            all_windows.append((hwnd, win32gui.GetWindowText(hwnd)))
#        windows = []
#        win32gui.EnumWindows(_window_callback, windows)
#        if exact:
#            return [hwnd for hwnd, title in windows if title_text == title]
#        else:
#            return [hwnd for hwnd, title in windows if title_text in title]
#
#
#    # not needed       
#    def _get_windows_by_classname(self, class_name, window_name):
#        '''
#        This function gives the handle to a window, defined by its *class_name*
#        and its *window_name*.
#        
#        Parameters
#        ----------  
#        class_name:     string
#                        The name of the class.                      
#        window_name:    string
#                        The title of the window.    
#        '''
#        handle = win32gui.FindWindow(class_name, window_name)
#        print(handle)
#        return handle
#
#
#    
#    def takeLiveFeedPicture(self,relpath, filename, low_res = False, crop = False):
#        '''
#        This is a function which takes a screenshot of the live feed.
#        The file's name is given by *filename* and its format is .btm.
#        It will be stored to self.folderpath.
#
#        Parameters
#        ----------
#
#        filename:   string
#                    Filename of the picture taken.
#        
#        low_res:    bool
#                    Takes a low resolution picture if True.
#                    
#        crop:       bool
#                    If True the stored image will be cropped.
#        '''
#        # Give the title of the live feed window
#        title_of_the_window = 'NIS-Elements BR [Current user: VTIB16]  - [Live - Fast]'
#        try:
#            hwnd = self._get_windows_by_title(title_of_the_window)
#            if len(hwnd) > 1:
#                print("Be aware, there are more than one window with this name. Specify by exact handle in the code.")
#                return
#            hwnd = hwnd[0]
#            #input direct handle
#            hwnd = int(132370)
#        except IndexError:
#            print("There is no window with the name: " + str(title_of_the_window))
#            return
#        path2 = os.path.join(self.folderpath, relpath)
#        store_path = '{path}\{name}.bmp'.format(path = path2, name = filename)
#        print(store_path)
#        # force full screen
#        shell = win32com.client.Dispatch("WScript.Shell")
#        shell.SendKeys('%')
#        win32gui.SetForegroundWindow(hwnd)
#        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
#        
#        l,t,r,b = win32gui.GetWindowRect(hwnd)
#        h = b - t
#        w = r - l
#        hDC = win32gui.GetWindowDC(hwnd)
#        myDC = win32ui.CreateDCFromHandle(hDC)
#        newDC = myDC.CreateCompatibleDC()       
#        myBitMap = win32ui.CreateBitmap()
#        
#        # creates empty bitmap, to be filled
#        if crop:
#            myBitMap.CreateCompatibleBitmap(myDC, int(w/2), int(h/2))
#        else:
#            myBitMap.CreateCompatibleBitmap(myDC, w, h)
#         
#        newDC.SelectObject(myBitMap)
#        
#        # give time to draw before taking picture
#        sleep(0.1)
#        #sleep(0.05)
#        
#        # fills the empty bitmap: (upper left coord. in empty), 
#        # (width and height of both), myDC, (upper left coord. in source)
#        if crop:
#            newDC.BitBlt((0, 0), (int(w/2), int(h/2)), myDC, (int(w/4), int(h/4)), win32con.SRCCOPY)
#        else:            
#            newDC.BitBlt((0, 0), (w, h), myDC, (0, 0), win32con.SRCCOPY)
#        
#        myBitMap.Paint(newDC)
#        myBitMap.SaveBitmapFile(newDC, store_path)
#        
#        # lower resolution
#        # Trick: setting format = 'png' reduces size but keeps it a .bmp
#        if low_res == True:
#            im = Image.open(store_path)
#            im.save(store_path, format = 'png')
#        
#        # free Resources
#        myDC.DeleteDC()
#        newDC.DeleteDC()
#        win32gui.ReleaseDC(hwnd, hDC)
#        win32gui.DeleteObject(myBitMap.GetHandle())    


    def get_handle_to_NIS_livefeed(self):
        '''
        This function gets the handle to the NIS livefeed.
        '''
        for i in range(1,999999,1):
            try:
                if str(win32gui.GetClassName(i)) == "G5_PICWND_CLASS":               
                    return i
            except:
                pass
        return None

    def get_handle_to_NIS_window(self):
        '''
        This function gets the handle to the NIS window.
        '''
        try:
            handle = win32gui.FindWindow("G5_MAINWND_CLASS", "NIS-Elements D [Current user: Nele]  - [Live - Fast]")
        except:
            return None
        return handle
    
    # not needed?
    def take_livefeed_picture(self, relpath, filename, low_res = False, crop = False):
        '''
        This is a fast livefeed picture function because it does not have to
        search for the handles each time.
        
        Parameters
        ----------        
        relpath:            string
                            relative path from self.folderpath.
        filename:           string
                            Filename of the picture taken.     
        low_res:            bool
                            Takes a low resolution picture if True.                
        crop:               bool
                            If True the stored image will be cropped.
        '''
        handle_to_window = self.windowhandle
        handle_to_feed = self.feedhandle         
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        win32gui.SetForegroundWindow(handle_to_window)
        win32gui.ShowWindow(handle_to_window, win32con.SW_MAXIMIZE) 
        # set path for storage
        path2 = os.path.join(self.folderpath, relpath)
        store_path = '{path}\{name}.bmp'.format(path = path2, name = filename)
        # defining relevant sizes
        l,t,r,b = win32gui.GetWindowRect(handle_to_feed)
        h = b - t
        w = r - l
        hDC = win32gui.GetWindowDC(handle_to_feed)
        myDC = win32ui.CreateDCFromHandle(hDC)
        newDC = myDC.CreateCompatibleDC()       
        myBitMap = win32ui.CreateBitmap()        
        # creates empty bitmap, to be filled
        if crop:
            myBitMap.CreateCompatibleBitmap(myDC, int(w/2), int(h/2))
        else:
            myBitMap.CreateCompatibleBitmap(myDC, w, h)         
        newDC.SelectObject(myBitMap)        
        # give time to draw before taking picture
        sleep(0.1)       
        # fills the empty bitmap: (upper left coord. in empty), 
        # (width and height of both), myDC, (upper left coord. in source)
        if crop:
            newDC.BitBlt((0, 0), (int(w/2), int(h/2)), myDC, (int(w/4), int(h/4)), win32con.SRCCOPY)
        else:            
            newDC.BitBlt((0, 0), (w, h), myDC, (0, 0), win32con.SRCCOPY)     
        myBitMap.Paint(newDC)
        myBitMap.SaveBitmapFile(newDC, store_path)     
        # lower resolution
        # Trick: setting format = 'png' reduces size but keeps it a .bmp
        if low_res == True:
            im = Image.open(store_path)
            im.save(store_path, format = 'png')   
        # free Resources
        myDC.DeleteDC()
        newDC.DeleteDC()
        win32gui.ReleaseDC(handle_to_feed, hDC)
        win32gui.DeleteObject(myBitMap.GetHandle()) 
        

    def take_single_cropped_picture(self, relpath, filename, crop_bottom, crop_top,reduce_size=True):
        '''
        This is a fast livefeed picture function because it does not have to
        search for the handles each time.
        
        Parameters
        ----------        
        relpath:            string
                            relative path from self.folderpath.
        filename:           string
                            Filename of the picture taken.     
        crop_bottom:        int
                            Number of cropped away bottom pixels.
        crop_bottom:        int
                            Number of cropped away top pixels.
        '''
        handle_to_window = self.windowhandle
        handle_to_feed = self.feedhandle     
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        win32gui.SetForegroundWindow(handle_to_window)
        win32gui.ShowWindow(handle_to_window, win32con.SW_MAXIMIZE) 
        # set path for storage
        path2 = os.path.join(self.folderpath, relpath)
        store_path = '{path}\{name}.bmp'.format(path = path2, name = filename)
        # defining relevant sizes
        l,t,r,b = win32gui.GetWindowRect(handle_to_feed)
        h = b - t
        w = r - l
        hDC = win32gui.GetWindowDC(handle_to_feed)
        myDC = win32ui.CreateDCFromHandle(hDC)
        newDC = myDC.CreateCompatibleDC()       
        myBitMap = win32ui.CreateBitmap()        
        # creates empty bitmap, to be filled
        myBitMap.CreateCompatibleBitmap(myDC, w- crop_top - crop_bottom, h )        
        newDC.SelectObject(myBitMap)        
        # give time to draw before taking picture
        sleep(0.1)       
        # fills the empty bitmap: (upper left coord. in empty), 
        # (width and height of both), myDC, (upper left coord. in source)
        newDC.BitBlt((0, 0), (w -crop_bottom - crop_top, h), myDC, 
                     (crop_bottom, 0), win32con.SRCCOPY)    
        myBitMap.Paint(newDC)
        myBitMap.SaveBitmapFile(newDC, store_path) 
        # free Resources
        myDC.DeleteDC()
        newDC.DeleteDC()
        win32gui.ReleaseDC(handle_to_feed, hDC)
        win32gui.DeleteObject(myBitMap.GetHandle()) 
#        if reduce_size:
#            picture_fullres = cv2.imread(store_path)
#            picture_resized = cv2.resize(picture_fullres,(int(np.round(picture_fullres.shape[1]*0.5,0)),int(np.round(picture_fullres.shape[0]*0.5,0))))
#            cv2.imwrite(store_path,picture_resized)



        
        
        
        
#    # not needed
#    def takeLiveFeedPicture(self,relpath, filename, low_res = False, crop = False):
#        '''
#        This is a function which takes a screenshot of the live feed.
#        The file's name is given by *filename* and its format is .btm.
#        It will be stored to self.folderpath.
#
#        Parameters
#        ----------
#        relpath:    string
#                    relative path from self.folderpath.
#        filename:   string
#                    Filename of the picture taken.     
#        low_res:    bool
#                    Takes a low resolution picture if True.                
#        crop:       bool
#                    If True the stored image will be cropped.
#        '''
#        
#        # Arguments: ("Window_Class", "Window_Title")
#        handle_to_window = win32gui.FindWindow("G5_MAINWND_CLASS", "NIS-Elements BR [Current user: VTIB16]  - [Live - Fast]")
#        #handle_to_window = win32gui.FindWindow("G5_PICWND_CLASS", "NIS-Elements BR [Current user: VTIB16]  - [Live - Fast]")
#
#        # Arguments: (handle_to_window, 0, "Control_Class", "Control_Text)
#        #hwnd = win32gui.FindWindowEx(handle_to_window, 0, "G5_PICWND_CLASS", None)
#        
#        hwnd = None
#        # Hard search
#        for i in range(100000,999999,1):
#            try:
#                if str(win32gui.GetClassName(i)) == "G5_PICWND_CLASS":
#                    print(i)    
#                    print("Class Name: "+ str(win32gui.GetClassName(i)))
#                    hwnd = i 
#                    break 
#            except:
#                pass
#
#            
#        #print(win32gui.FindWindowEx(handle_to_window, 0, None,None))
##        print("Window Text: ", win32gui.GetWindowText(int(0x0002007C)))
##        print("Handle to subwindow: ", hwnd)
#        if hwnd == None:
#            hwnd = print("Sub window not found. Please enter the handle manually.")
#            return        
#        # enter handle manually
#        #hwnd = int(594708)
#        
#        # force full screen of the window
#        shell = win32com.client.Dispatch("WScript.Shell")
#        shell.SendKeys('%')
#        win32gui.SetForegroundWindow(handle_to_window)
#        win32gui.ShowWindow(handle_to_window, win32con.SW_MAXIMIZE)
#        
#        # set path for storage
#        path2 = os.path.join(self.folderpath, relpath)
#        store_path = '{path}\{name}.bmp'.format(path = path2, name = filename)
#        print(store_path)
#        
#        l,t,r,b = win32gui.GetWindowRect(hwnd)
#        h = b - t
#        w = r - l
#        hDC = win32gui.GetWindowDC(hwnd)
#        myDC = win32ui.CreateDCFromHandle(hDC)
#        newDC = myDC.CreateCompatibleDC()       
#        myBitMap = win32ui.CreateBitmap()
#        
#        # creates empty bitmap, to be filled
#        if crop:
#            myBitMap.CreateCompatibleBitmap(myDC, int(w/2), int(h/2))
#        else:
#            myBitMap.CreateCompatibleBitmap(myDC, w, h)
#         
#        newDC.SelectObject(myBitMap)
#        
#        # give time to draw before taking picture
#        sleep(0.1)
#        #sleep(0.05)
#        
#        # fills the empty bitmap: (upper left coord. in empty), 
#        # (width and height of both), myDC, (upper left coord. in source)
#        if crop:
#            newDC.BitBlt((0, 0), (int(w/2), int(h/2)), myDC, (int(w/4), int(h/4)), win32con.SRCCOPY)
#        else:            
#            newDC.BitBlt((0, 0), (w, h), myDC, (0, 0), win32con.SRCCOPY)
#        
#        myBitMap.Paint(newDC)
#        myBitMap.SaveBitmapFile(newDC, store_path)
#        
#        # lower resolution
#        # Trick: setting format = 'png' reduces size but keeps it a .bmp
#        if low_res == True:
#            im = Image.open(store_path)
#            im.save(store_path, format = 'png')
#        
#        # free Resources
#        myDC.DeleteDC()
#        newDC.DeleteDC()
#        win32gui.ReleaseDC(hwnd, hDC)
#        win32gui.DeleteObject(myBitMap.GetHandle()) 




if __name__ == "__main__":
#    cam = Camera(r'C:\Users\VTIB16\Documents\GloveBoxAutomation\Camera\Testpics')
    cam = Camera(r'C:\Users\TIM\Desktop')
#    cam.takeLiveFeedPicture('','Finale')
    cam.take_single_cropped_picture(r'C:\Users\TIM\Desktop','TestImage0_13',0,13)


#    image = Image.open(r'C:/Users/TIM/Desktop/TestImage9_13.bmp')
#    width, height = image.size
#    print('width: ',width)
#    print('height: ',height)
    
    
    
    
    
    
    
    
    
    
    
    
    