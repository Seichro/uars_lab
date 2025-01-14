# -*- coding: utf-8 -*-
"""
Created on Friday Nov 8

@author: Anthony Abubakar
@lab: UARS Lab

This lab attempts to get multiple days and read every single one of them.
"""

"""
command to download all files
globalDownload.py --verbose --url=http://igp.gob.pe/observatorios/radio-observatorio-jicamarca/madrigal --outputDir=/Users/seich/uars/julia-mp-isr/multiple-days.py --user_fullname="Anthony+Abubakar" --user_email=axa210277@utdallas.edu --user_affiliation="The+University+of+Texas+at+Dallas" --format="hdf5" --startDate="01/01/1950" --endDate="12/31/2024" --inst=12

globalDownload.py --verbose --url=http://www.igp.gob.pe/observatorios/radio-observatorio-jicamarca/madrigal --outputDir=/Users/seich/uars/julia-mp-isr --user_fullname="Anthony+Abubakar" --user_email=axa210277@utdallas.edu --user_affiliation="The+University+of+Texas+at+Dallas" --format="hdf5" --startDate="01/01/1950" --endDate="12/31/2024" --inst=12 

globalDownload.py --verbose --url=http://www.igp.gob.pe/observatorios/radio-observatorio-jicamarca/madrigal --outputDir=/Users/seich/uars/julia-mp-isr/multiple-days.py --user_fullname="Anthony+Abubakar" --user_email=axa210277@utdallas.edu --user_affiliation="The+University+of+Texas+at+Dallas" --format="hdf5" --startDate="12/01/2022" --endDate="12/31/2024" --inst=12 
"""
import h5py
import math
import matplotlib.pyplot as plt 
import numpy as np
import calendar
from datetime import datetime, timedelta
import matplotlib
from os import listdir
from os.path import isfile, join

mypath = "/Users/seich/uars/julia-mp-isr"

# finds all the files in the directory
# only files becomes a bunch of strings
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

# print(list(onlyfiles))
namesArr = []
count_file = 0

for x in onlyfiles:
    if "avg" in x:
        continue
    if "drifts" not in x:
        continue
    split = x.split("drifts")
    print(split)
    # print(split[0])
    if(len(split) != 2):
        continue
    # if((split[1] != ".5.hdf5")):
        # continue
    # if(split[1] == "_avg.h5.hdf5"):
        # continue

    x = split[0]
    print(x)
    
# print(onlyfiles)
# print(list(namesArr))
# for x in namesArr:
    h5 = "drifts.h5.hdf5"
    temp = x
    filename = x + h5
    name = x

    for x in namesArr:
        filename = namesArr[x]
        temp = namesArr.split(".")
        name = temp[0]

    file = h5py.File(filename, 'r')

    # data recieved from files
    range_arr = file['Data']['Array Layout']['range']
    timestamps_arr = file['Data']['Array Layout']['timestamps']
    # velocity in north direction
    velocity_arr = file['Data']['Array Layout']['2D Parameters']['vipn']
    # signal-to-noise ratio array
    old_signal_arr = file['Data']['Array Layout']['2D Parameters']['pacwl']
    signal_arr = [i * 10 for i in old_signal_arr]
    # echo arr
    echo_arr = file['Data']['Array Layout']['2D Parameters']['pdiel']
    error_arr = file['Data']['Array Layout']['2D Parameters']['dvipn']

    """
    Converting times from the radar format into the hour format for use.
    """
    datetime_arr = []

    count = 0
    for x in timestamps_arr:
        # subtracts five hours from every single 
        date_object = datetime.fromtimestamp(x) + timedelta(hours=-5)
        # appends the times into a new datetime arr
        datetime_arr.append(date_object);
    
        # save the very first one for the use
        if (count == 0):
            cur_day = date_object.day  
            cur_hour = date_object.hour
            cur_minutes = date_object.minute
            cur_seconds = date_object.second
        
        count += 1
    
    duration = 0
    total_seconds = 0 
    datetime_to_hours_arr = []
    seconds_in_hour = 60*60

    """
    This needs to change for every single time.
    """

    day_time_seconds = timedelta(days = cur_day, hours = cur_hour, minutes = cur_minutes, seconds = cur_seconds).total_seconds()

    for x in datetime_arr:
        duration = timedelta(days = x.day, seconds = x.second, minutes = x.minute, hours = x.hour)
        total_seconds = (duration.total_seconds())
        datetime_to_hours_arr.append((total_seconds-day_time_seconds)/(seconds_in_hour))
    """
    Irregularity finding, the echo detection in Smith's paper
    """
    snr_array = np.array(signal_arr)
    
    # attempts to correct empty gaps within the code
    count = 0
    temp_datetime = np.full(shape=288, fill_value=np.nan)
    temp_velocity_arr = np.full(shape=(64, 288), fill_value=np.nan)
    temp_snr_arr = np.full(shape=(64,288), fill_value=np.nan)
    for i in range(0, 288):
        temp_datetime[i] = i*(5/60)
        
    for i in range(288):
        # Use np.isclose for floating-point comparison
        if count < len(datetime_to_hours_arr) and np.isclose(temp_datetime[i], datetime_to_hours_arr[count], atol=1e-5):
            temp_velocity_arr[:, i] = velocity_arr[:, count]
            temp_snr_arr[:, i] = snr_array[:, count]
            count += 1  # Increment only if match is found
            
    snr_array = temp_snr_arr
    velocity_arr = temp_velocity_arr
    datetime_to_hours_arr = temp_datetime
    
    # thresholds used
    echo_count_threshold = 4
    threshold = 16

    # Initialize an irregularity map with zeros
    irregularity_map = np.zeros(snr_array.shape, dtype=int)

    # Define height and time intervals based on bin sizes
    n_height_steps = 2  # the current bin is of 15km, so by using 2 we step by 30km
    n_time_steps = 3 # time intervals are of 5 minutes, so we can use 3 to step by 15 mins
    
    # range starting from 0 going to the end with these steps
    for i in range(0, snr_array.shape[0], n_height_steps):
        for j in range(0, snr_array.shape[1], n_time_steps):
            bin_section = snr_array[i:i+n_height_steps, j:j+n_time_steps]
            
            if (np.count_nonzero(bin_section > threshold) >= echo_count_threshold):
                irregularity_map[i:i+n_height_steps, j:j+n_time_steps] = 1 # Mark as irregularity (red)
            else:
                irregularity_map[i:i+n_height_steps, j:j+n_time_steps] = 0 # Mark as non-irregularity (blue)

    """
    This finds the means for the vertical drift mapping along with the
    standard deviation.
    
    Also filters out all values where the error reported by Jicamarca
    is greater than 10.
    """
    
    """
    for i in range (0, velocity_arr.shape[0]):
        for j in range (0, velocity_arr.shape[1]):
            if(error_arr[i][j] > 10):
                velocity_arr[i][j] = np.NaN
    """
                
    new_range_arr = np.array(range_arr)
    height_mask = (new_range_arr >= 200) & (new_range_arr <= 400)
    filtered_velocity_arr = velocity_arr
    filtered_irregularity_map = irregularity_map[height_mask, :]

    error_arr = error_arr[height_mask, :]
    new_error_arr = np.copy(error_arr.shape[1])

    for i in range (0, filtered_irregularity_map.shape[0], n_height_steps):
        for j in range (0, filtered_irregularity_map.shape[1], n_time_steps):
            bin_section = filtered_velocity_arr[i:i+n_height_steps, j:j+n_time_steps]
            x = filtered_irregularity_map[i][j]
            if(x == 1):
                filtered_velocity_arr[i:i+n_height_steps, j:j+n_time_steps] = np.NaN

    # no filter so from 200-800km
    temp_filtered_velocity_arr = filtered_velocity_arr
    # filtered from 200-400km
    filtered_velocity_arr = filtered_velocity_arr[height_mask, :]
    
    mean_velocity = []

    for j in range (0, filtered_velocity_arr.shape[1], n_time_steps):
        bin_section = filtered_velocity_arr[:, j:j+n_time_steps]
        mean_velocity.append(np.nanmean(bin_section))
     
    mean_velocity = np.array(mean_velocity)

    adjusted_datetime_to_hours_arr = datetime_to_hours_arr[::3]

    std_dev_means = []

    for j in range (0, filtered_velocity_arr.shape[1], n_time_steps):
        bin_section = filtered_velocity_arr[:, j:j+n_time_steps]
        std_dev_means.append(np.nanstd(bin_section))
     
    std_dev_means = np.array(std_dev_means)

    """
    Outputting and displaying the data
    """
    fig1, (ax1, ax2, ax3, ax4) = plt.subplots(4,1, figsize=(10,16))
    fig3, (ax6, ax5, ax7) = plt.subplots(3,1, figsize=(8,8))
    fig2, (ax8, ax9, ax10) = plt.subplots(3,1, figsize=(8,8))

    vel_min, vel_max = -50, 50
    sig_min, sig_max = 0, 40

    echo_min, echo_max = np.nanmax(echo_arr), np.nanmin(echo_arr)

    time_font = {'family':'sans-serif','color':'black','size':18}
    text_fonts = {'family':'sans-serif','color':'black','size':12}

    # color bar finder
    ticks_drifts_colorbar = [np.floor(vel_min),np.ceil((vel_min + vel_max)/2),np.ceil(vel_max)]
    ticks_signal_colorbar = [np.floor(sig_min),np.ceil((sig_min + sig_max)/2),np.ceil(sig_max)]

    # create cmap
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["blue","green","red"])

    # color bar creation
    c = ax2.pcolormesh(datetime_to_hours_arr, range_arr, velocity_arr, cmap = 'coolwarm', vmin = vel_min, vmax = vel_max)
    plt.colorbar(c, ticks = ticks_drifts_colorbar, aspect = 12)

    # color bar for signals
    d = ax1.pcolormesh(datetime_to_hours_arr, range_arr, snr_array, cmap ='jet', vmin = sig_min, vmax = sig_max)
    plt.colorbar(d, ticks = ticks_signal_colorbar, aspect = 12)

    # ticks for plotting
    ticks = [0,3,6,9,12,15,18,21,24]

    # echo graph
    ax1.pcolormesh(datetime_to_hours_arr, range_arr, snr_array, cmap = 'jet', vmin = 0, vmax = 40)
    ax1.set_ylabel('Height [km]', fontdict = text_fonts)
    ax1.set_ylim(200, 900)
    ax1.set_xticks(ticks)
    
    date_output = temp.replace("jro", "")
    year = date_output[:4]
    month = date_output[4] + date_output[5]
    day = date_output[6] + date_output[7]
    string_month = calendar.month_abbr[int(month)]


    title = "(a) " + day + "-" + string_month + "-" + year + " SNR+1 [dB]"

    ax1.set_title(title, fontdict = text_fonts)

    # vetucal drift graph
    ax2.pcolormesh(datetime_to_hours_arr, range_arr, velocity_arr, cmap ='coolwarm', vmin = -50, vmax = 50)
    ax2.set_ylabel('Height [km]', fontdict = text_fonts)
    ax2.set_ylim(200, 900)
    ax2.set_xticks(ticks)
    ax2.set_title('(b) Vertical Drift [m/s]', fontdict = text_fonts)

    # vertical drift graph #2
    ax6.pcolormesh(datetime_to_hours_arr, range_arr, velocity_arr, cmap ='coolwarm', vmin = -50, vmax = 50)
    ax6.set_ylabel('Height [km]', fontdict = text_fonts)
    ax6.set_ylim(200, 900)
    ax6.set_xticks(ticks)
    ax6.set_title('(b) Vertical Drift [m/s]', fontdict = text_fonts)

    # echo detection graph
    ax3.pcolormesh(datetime_to_hours_arr, range_arr, irregularity_map, cmap ='jet', shading = 'nearest')
    ax3.set_ylabel('Height [km]', fontdict = text_fonts)
    ax3.set_ylim(200, 900)
    ax3.set_xticks(ticks)
    ax3.set_title('(c) Echo Detection', fontdict = text_fonts)

    # means graph
    ax4.plot(adjusted_datetime_to_hours_arr, mean_velocity, label = 'Mean Velocity', color = 'Black')
    ax4.grid
    ax4.set_ylabel('Velocity [m/s]', fontdict = text_fonts)
    ax4.set_xlabel('Local time [hh:mm]', fontdict = time_font, size = 8)
    ax4.errorbar(adjusted_datetime_to_hours_arr, mean_velocity, yerr=std_dev_means, linestyle='None', capsize=3, color = 'black')
    ax4.set_ylim(-50,50)
    ax4.set_xlim(0,24)
    ax4.set_xticks(ticks)
    ax4.grid(True, color="gray", lw=0.5)
    ax4.set_title('(d) Mean Vert. Drift', fontdict = text_fonts)

    # filtered echo map graphing
    ax5.pcolormesh(datetime_to_hours_arr, range_arr[height_mask], filtered_velocity_arr, cmap ='coolwarm', shading = 'nearest')
    ax5.set_ylabel('Height [km]', fontdict = text_fonts)
    ax5.set_ylim(200, 400)
    ax5.set_xticks(ticks)
    ax5.set_title('(e) Filtered echo map', fontdict = text_fonts)

    # mean vertical drift w/ filtered echo map (the same thing?)
    ax7.plot(adjusted_datetime_to_hours_arr, mean_velocity, label = 'Mean Velocity', color = 'Black')
    ax7.set_ylim(-50,50)
    ax7.set_xlim(0,24)
    ax7.set_xticks(ticks)
    ax7.grid(True, color="gray", lw=0.5)
    ax7.grid
    ax7.set_ylabel('Velocity [m/s]', fontdict = text_fonts)
    ax7.set_xlabel('Local time [hh:mm]', fontdict = time_font, size = 8)
    ax7.set_title('(d) Mean Vert. Drift', fontdict = text_fonts)
    ax7.errorbar(adjusted_datetime_to_hours_arr, mean_velocity, yerr=std_dev_means, linestyle='None', capsize=3, color = 'black')
    
    # echo detection for 3rd graph
    ax8.pcolormesh(datetime_to_hours_arr, range_arr, irregularity_map, cmap ='jet', shading = 'nearest')
    ax8.set_ylabel('Height [km]', fontdict = text_fonts)
    ax8.set_ylim(200, 900)
    ax8.set_xticks(ticks)
    ax8.set_title('(c) Echo Detection', fontdict = text_fonts)
    
    # vertical drift graph for 3rd area
    ax9.pcolormesh(datetime_to_hours_arr, range_arr, velocity_arr, cmap ='coolwarm', vmin = -50, vmax = 50)
    ax9.set_ylabel('Height [km]', fontdict = text_fonts)
    ax9.set_ylim(200, 900)
    ax9.set_xticks(ticks)
    ax9.set_title('(b) Vertical Drift [m/s]', fontdict = text_fonts)
    
    ax10.pcolormesh(datetime_to_hours_arr, range_arr, temp_filtered_velocity_arr, cmap ='coolwarm', shading = 'nearest')
    ax10.set_ylabel('Height [km]', fontdict = text_fonts)
    ax10.set_ylim(200, 900)
    ax10.set_xticks(ticks)
    ax10.set_title('(e) Filtered echo map w/ no height restrictions', fontdict = text_fonts)

    # formatting
    fig1.tight_layout()
    fig2.tight_layout()
    fig3.tight_layout()

    dir_graphs = "graphs/v4/"
    dir_means = "means/v4/"
    img1 = "img1"
    img2 = "img2"
    img3 = "img3"
    means = "means"
    png = ".png"
    npy = ".npy"

    x = dir_graphs + name + img1 + png
    y = dir_graphs + name + img2 + png
    z = dir_graphs + name + img3 + png

    fig1.savefig(x, format = 'png')
    fig3.savefig(y, format = 'png')
    fig2.savefig(z, format = 'png')

    x = dir_means + name + means + npy

    np.save(x, mean_velocity)
    
    # stores every single time for every string in our data
    string_time = "times/v1/"
    arr_name = "times_hours_arr"
    time_name = string_time + arr_name + name + npy
    np.save(time_name, adjusted_datetime_to_hours_arr)
    
    fig1.show()
    fig3.show()
    fig2.show()