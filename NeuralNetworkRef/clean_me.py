import os
import glob

raw_data = 'raw_data'
preproc_data = 'preproc_data'
step1_data = 'step1_data'
step2_data = 'step2_data'
final_data = 'final_data'


for folder in [preproc_data, step1_data, step2_data, final_data]:
    files = glob.glob(folder+'/*')
    for f in files:
        os.remove(f)
