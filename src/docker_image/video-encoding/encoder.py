## In this file, the encoding process developed by @martinamaggio (GitHub)
## in SAVE (Self-Adaptive Video Encoding) project is adapted to an
## interative workload.
## 
## https://github.com/martinamaggio/save

import math
import sys
sys.path.append('libs')
import os
import random
from PIL import Image
from PIL import ImageOps
from kafka_monitor_vec import *
import numpy as np
import ssim
import threading,multiprocessing
import time

def image_to_matrix(path):
	img = Image.open(str(path))
	img = ImageOps.grayscale(img)
	img_data = img.getdata()
	img_tab = np.array(img_data)
	w,h = img.size
	img_mat = np.reshape(img_tab, (h,w))
	return img_mat

def compute_ssim(path_a, path_b):
	matrix_a = image_to_matrix(path_a)
	matrix_b = image_to_matrix(path_b)
	return ssim.compute_ssim(matrix_a, matrix_b)
        
def encode(i, frame_in, frame_out, quality, sharpen, noise):
        sem.acquire()
        framename = str(i).zfill(8) + '.jpg'
        img_in = frame_in + '/' + framename
        img_out = frame_out + '/' + framename
        # generating os command for conversion
        # sharpen actuator
        if sharpen != 0:
                sharpenstring = ' -sharpen ' + str(sharpen) + ' '
        else:
                sharpenstring = ' '
        # noise actuator
        if noise != 0:
                noisestring = ' -noise ' + str(noise) + ' '
        else:
                noisestring = ' '
        # command setup
        command = 'convert {file_in} -quality {quality} '.format(
                file_in = img_in, quality = quality)
        command += sharpenstring
        command += noisestring
        command += img_out
        # executing conversion
        os.system(command)
        # computing current values of indices
        current_quality = compute_ssim(img_in, img_out)
        current_size = os.path.getsize(img_out)
        print 'IMAGE {0} WAS COMPRESSED'.format(i)
        sem.release()
	#return (current_quality, current_size)

        
# -------------------------------------------------------

def main(args):   
        #parsing arguments
        folder_frame_in = args[0]
        folder_frame_out = args[1]
        setpoint_quality = float(args[2])
        number_epochs = int(args[3])
        kafka_monitor_instance = args[4]
	
        # getting frames and opening result file
        path, dirs, files = os.walk(folder_frame_in).next()
        frame_count = len(files)
        final_frame = frame_count + 1
	
        # fixed values for actuators
        ctl = np.matrix([[setpoint_quality], [0], [0]]) # quality, sharpen, noise
        quality = np.round(ctl.item(0))
        sharpen = np.round(ctl.item(1))
        noise = np.round(ctl.item(2))

        initial_frame = 415 #number of the frame in which the video starts to present frames whose size is around its mean value 
        global sem
        sem = multiprocessing.Semaphore(8) #Number of simulataneous processes allowed at a specific time 
        for epoch in range(1, number_epochs+1):
                kafka_monitor_instance.on_epoch_begin(epoch)
                processes = []
                
                for i in range(33): # Total number of frames processed in a given epoch
                        p = multiprocessing.Process(target=encode, args=(initial_frame, folder_frame_in, folder_frame_out, quality, sharpen, noise,))
                        processes.append(p)
                        p.start()
                        initial_frame += 1
                        
                for process in processes:
                        process.join()

                for process in processes:
                        process.terminate()
                        
                if (initial_frame + 33) >= frame_count:
                        initial_frame = 415
                        
                kafka_monitor_instance.on_epoch_end(epoch) #Send message through Kafka
