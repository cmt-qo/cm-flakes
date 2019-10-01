import numpy as np
import os
import glob
from distutils.dir_util import copy_tree
import time 


raw_data = 'raw_data'
preproc_data = 'preproc_data'
step1_data = 'step1_data'
step2_data = 'step2_data'
final_data = 'final_data'

model1 = 'models/model1'
model2 = 'models/model2'
model3 = 'models/model3'

from nn_v0_algo import call_nn
from create_pics import pics
folder_number = 1
path = os.path.join(os.path.split(os.path.abspath(__file__))[0])
print(path)
finalpath = 'scan_finished'
while True:
    
    if os.path.exists(os.path.join(path,'{folder_number}'.format(folder_number=folder_number+1))):
        print('here')
        raw_data =  os.path.join(path,'{folder_number}'.format(folder_number=folder_number))
        
    
        
    
    
    
        pics(from_path=raw_data, to_path=preproc_data)
        
        
        
        call_nn(input_folder=preproc_data,
                model_folder=model1,
                output_folder=step1_data
            )
        
        call_nn(input_folder=step1_data,
                model_folder=model2,
                output_folder=step2_data
            )
        
        call_nn(input_folder=step2_data,
                model_folder=model3,
                output_folder=final_data
            )
        
    
    
        
        # This part part is removing dupicates!
        # Use with caution
        final_data_list = glob.glob(final_data+'/*')
        
        files_to_remove = []
        
        for file in final_data_list:
            file_split = file.split('_')
            bigx = file_split[2]
            bigy = file_split[4]
            bigz = file_split[6]
            xcoord = float(file_split[-3])
            ycoord = float(file_split[-2])
            for file2 in final_data_list:
                if (file2 != file) and file2 not in files_to_remove:
                    file_split2 = file2.split('_')
                    bigx2 = file_split2[2]
                    bigy2 = file_split2[4]
                    bigz2 = file_split2[6]
                    if (bigx==bigx2) and (bigy==bigy2) and (bigz==bigz2):
                        xcoord2 = float(file_split2[-3])
                        ycoord2 = float(file_split2[-2])
                        dist = np.sqrt( (xcoord - xcoord2)**2 + (ycoord - ycoord2)**2 )
                        if np.abs(dist) < 100:
                            files_to_remove.append(file)
        
        
        files_to_remove = np.unique(np.array(files_to_remove))
        
        for file in files_to_remove:
            os.remove(file)
        #Clean Up
        for folder in [preproc_data, step1_data, step2_data]:
            files = glob.glob(folder+'/*')
            for f in files:
                os.remove(f)
        folder_number += 1
    
    if os.path.exists(finalpath):
        with open(os.path.join(finalpath,'GoodFlakes.txt'),'w+') as f:
            for element in os.listdir(final_data):
#                print(element)
                if not element.endswith('.png'):
                    print(element)
                    continue
                f.write(element[0:-6]+'\n')
        break
                
                