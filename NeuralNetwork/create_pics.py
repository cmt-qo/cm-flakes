#-------------------------------------------------------------------------------
# Filename: create_pics.py
# Description: creates square pictures out of a picture which is mostly empty
#    for training a neural network later.
# The parameters to fool around with include:
#    factor: scaled down image for faster image processing
#    sq_size: size of square that is used to construct the standard-deviation  map
#    cutoff: cutoff for standard deviation
# Authors: Mark H Fischer, Eliska Greplova
#-------------------------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from os import listdir, path, makedirs
import argparse
import sys

# class MyParser(argparse.ArgumentParser):
#     def error(self, message):
#         sys.stderr.write('error: %s\n' % message)
#         self.print_help()
#         sys.exit(2)

def pics(from_path='raw_data',to_path='preproc_data'):
    # parser = MyParser()
    # parser.add_argument('input_folder', nargs='+')
    # parser.add_argument('output_folder', nargs='+')
    # args = parser.parse_args()

    # from_path = args.input_folder[0]

    if not from_path[-1]=='/':
        from_path+=('/')
    # to_path = args.output_folder[0]

    if not to_path[-1]=='/':
        to_path+=('/')

    #check whether input path exists
    if not path.exists(from_path):
        raise IOError("input directory {0} does not exist, exiting script".format(from_path))

    #possible image file extensions.
    exts = ['.jpg', '.png', '.tif', '.bmp']

    # input file dimensions 
    # UPDATED VALUES FOR THE SECOND GLOVEBOX
    xdim = 1278 #1330 #2560
    ydim = 909#884 #1920

    # output file dimensions
    dim = 80 #256

    export_ext = '.png' #extension files will be saved

    #first, find all the image file in the directory
    files = listdir(from_path)
    filenames = []
    extensions = []
    for f in files:
        name, ext = path.splitext(from_path+f)
        if ext in exts:
            filenames.append(name)
            extensions.append(ext)

    print("found {0} image files in folder {1}".format(len(filenames), from_path))

    total_flakes = 0
    good_flakes = 0
    missed_flakes = 0
    #start the actual work of cutting the pictures into smaller pictures
    for i, filename in enumerate(filenames):
        print("starting with new image file: {0}{1}".format(filename,
            extensions[i]))
        #first, check for the .csv file with the coordinates of good flakes
        good_ones = []
        try:
            with open(filename+".csv") as f:
                content = f.read().splitlines()

            for line in content:
                good_ones.append(line.split(','))
        except IOError:
            print("Warning: Couldn't find file {0}.csv, assume there's no good flakes".format(filename))

        # open image
        full_im = Image.open(filename+extensions[i])

        Lx = full_im.size[0] #x dimension of picture
        Ly = full_im.size[1] #y dimension of picture

        # we want to work on pictures of equal size, so if they are not the right
        # size, we rescale them.
        scalex = 1.
        scaley = 1.
        if not Lx == xdim:
            scalex = float(xdim) / Lx
            scaley = float(ydim) / Ly
            full_im = full_im.resize((xdim, ydim))
            print("picture is too big, resizing to ({0}, {1})".format(xdim, ydim))

        #to speed up the whole work, we resize the image for the first step
        factor = 8
        lx = int(xdim/factor) # resized x dimension
        ly = int(ydim/factor) # resized y dimension
        small_im = full_im.resize((lx, ly))

        sq_size = dim//factor # size of square in resized image
        cutoff = 5 #was 2.75 # cutoff for standard deviation

        #calculate the standard deviation of the black and white images
        # (convert('L') returns a BW image)
        stds = np.zeros((lx-sq_size, ly-sq_size))
        for k in range(lx-sq_size):
            for l in range(ly-sq_size):
                tmp_im = small_im.crop((k, l, k+sq_size, l+sq_size))
                stds[k,l] = np.std(list(tmp_im.convert('L').getdata()))

        Lstds = np.reshape(stds, (lx-sq_size)*(ly-sq_size))
        sorted_stds = np.argsort(Lstds)

        centers = []
        for j in reversed(sorted_stds):
            if Lstds[j]< cutoff: break
            ix = int(j/(ly-sq_size))+sq_size/2
            iy = j%(ly-sq_size)+sq_size/2
            included = False
            for c in centers:
                if (abs(c[0]-ix) < sq_size) and (abs(c[1]-iy)<sq_size):
                    included = True
                    continue
            if included: continue
            ix = min(max(sq_size, ix), lx-sq_size)
            iy = min(max(sq_size, iy), ly-sq_size)
            centers.append((ix, iy))

        print("identified {0} potential candidates in image {1}".format(len(centers), filename))
        total_flakes += len(centers)
        squares = []
        coordinates = []
        for c in centers:
            ix = c[0]*factor
            iy = c[1]*factor
            coordinates.append([ix, iy])
            x0 = ix - factor*sq_size
            x1 = ix + factor*sq_size
            y0 = iy - factor*sq_size
            y1 = iy + factor*sq_size
            squares.append(full_im.crop((x0, y0, x1, y1)))

        if not path.exists(to_path):
            print("{0} does not exist yet, creating it".format(to_path))
            makedirs(to_path)

        found = np.zeros(len(good_ones)) # to make sure we found all good ones
        for k in range(len(squares)):
            x = coordinates[k][0]
            y = coordinates[k][1]
            bad = True
            name = filename.split('/')[-1]
            for j, good in enumerate(good_ones):
                g0 = scalex*float(good[0])
                g1 = scaley*float(good[1])
                if (abs(g0-x) < factor*sq_size) and (abs(g1-y)<factor*sq_size):
                    this_file = to_path+name+"_" + str(coordinates[k][0])\
                          + "_" + str(coordinates[k][1])+"_0A"+ export_ext
                    squares[k].resize((dim, dim)).save(this_file)
                    for t in range(5):
                        this_file = to_path+name + "_" + str(coordinates[k][0]) + \
                              "_" + str(coordinates[k][1])+"_{0}A".format(t+1)+ export_ext
                        squares[k].transpose(t).resize((dim, dim)).save(this_file)
                    found[j]=1
                    bad = False
                    good_flakes += 1
            if not bad: continue
            this_file = to_path + name +"_" + str(coordinates[k][0]) + "_" + \
                  str(coordinates[k][1])+"_B" + export_ext
            squares[k].resize((dim, dim)).save(this_file)

        if np.sum(found)<len(good_ones):
            missed_flakes += len(good_ones) - np.sum(found)
            print("Warning: We have missed a good one in {0}".format(filename))
            print("(should have found {0}, found {1}instead".format( \
                    len(good_ones), np.sum(found)))

    print("")
    print("total flakes found: {0}".format(total_flakes))
    print("of which are good : {0}".format(good_flakes))
    print("good flakes missed: {0}".format(int(missed_flakes)))
