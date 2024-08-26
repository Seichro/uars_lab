#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 21 11:43:32 2024

@author: Anthony Abubakar
@lab: UARS Lab
"""

# this will all just output the data for use, find the shape + size

import h5py
# import pydarn
# import pydarnio
import matplotlib.pyplot as plt 

# name of file
filename = "jro20240102drifts.h5"

def traverse_datasets(hdf_file):

    def h5py_dataset_iterator(g, prefix=''):
        for key in g.keys():
            item = g[key]
            path = f'{prefix}/{key}'
            if isinstance(item, h5py.Dataset): # test for dataset
                yield (path, item)
            elif isinstance(item, h5py.Group): # test for group (go down)
                yield from h5py_dataset_iterator(item, path)

    for path, _ in h5py_dataset_iterator(hdf_file):
        yield path

"""
! two keys: data and metadata
notably, metadata does not seem like an important part of this

the time stamps seem to be of size (288, )
the range seems to be of size (64, ) (64 = 2^8)
the velocity (vipn) has a shape of (64, 288)
"""

# function which outputs the path, shape, and data type of all datasets.

with h5py.File(filename, 'r') as f:
    # likely we can instead of printing, also add the information to some array and store it
    for dset in traverse_datasets(f):
        print('\nPath:', dset)
        # x = time
        # if(dset == '/Data/Array Layout/timestamps'):
            
        # y = range
        # my attempt at printing out the data, but did not work
        # range = hp5y file? f?['Data]['Array Layout']['Range']
        # pciel for top
        # vipn, dvipn, pciel
        # convert timezones
        # if(dset == '/Data/Array Layout/range'):
            # print(f[:])
            
        # could possibly be used to create a dataset? can we save the data set into our
        # own array and then model it?
        
        # arr = np.arange(100)
        # dset = f.create_dataset("init", data=arr)
            
        print('Shape:', f[dset].shape)
        print('Data type:', f[dset].dtype)
        print('\n')

"""
now we need to store the data, and then be able to output it into a graph for use
x = time, y = range, z = velocity. restrict it from 200 range onwards
potentially revelant variables?
vipn, range, time stamps
"""

"""
#px.colormesh for images

# attempt to output the data used

# next 3 lines just works to read the file
fitacf_file = 'jro20240102drifts.h5'
fitacf_reader = pydarnio.SDarnRead(fitacf_file)
fitacf_data = fitacf_reader.read_fitacf()

# actual image attempt
pydarn.RTP.plot_range_time(fitacf_data, beam_num=7, parameter='p_l')
plt.show()
"""
file = h5py.File(filename, 'r')

# from data
range_arr = file['Data']['Array Layout']['range']
timestamps_arr = file['Data']['Array Layout']['timestamps']
# velocity in north direction
velocity_arr = file['Data']['Array Layout']['2D Parameters']['vipn']
# error for velocity
error_arr = file['Data']['Array Layout']['2D Parameters']['pciel']