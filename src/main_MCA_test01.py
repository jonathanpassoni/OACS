## This script aims to execute a Multiple Containers Execution Test
## Test 01: Constant set-points with change in cloud environments

import sys
import os
import configparser
import time
from multiprocessing import Process,Queue
import threading
from container_Exec import *
from resource_manager_classes import *
from container_config import *
from message_receiver import *
from container_start import *
from frequency_Monitor import *


config = configparser.ConfigParser()
config.read('config/config.cfg')

ip = config['KAFKA']['ip']
port = config['KAFKA']['port']

servers = ip + ':' + port

zoo_ip = config['ZOOKEEPER']['ip']

#remove last containers 
os.system("docker rm container_1")
os.system("docker rm container_2")
os.system("docker rm container_3")
os.system("docker rm container_4")
#Access docker_image directory in order to build new images of containers
os.chdir("docker_image")

total_cpus = 6.5
total_epochs = 245
Manager = ResourceManager(servers,total_cpus,total_epochs)

## Containers input data

start_step0 = 0
epochs_0 = 50
sp_0 = 15.0
sp0_list = [sp_0]*(epochs_0 +1)
container_type0 = 'one'

start_step1 = 4
epochs_1 = 65
sp_1 = 20.0
sp1_list = [sp_1]*(epochs_1 +1)
container_type1 = 'two'

start_step2 = 14
epochs_2 = 80
sp_2 = 25.0
sp2_list = [sp_2]*(epochs_2 +1)
container_type2 = 'three'

start_step3 = 110
epochs_3 = 50
sp_3 = 15.0
sp3_list = [sp_3]*(epochs_3 +1)
container_type3 = 'one'

if __name__ == '__main__':

    f_monitor = threading.Thread(target=Register_CPU_frequency, args=(Manager,total_epochs,))
    f_monitor.start()

    while True:
        if Manager.MPC_steps >= start_step0:
            Manager.generate_container_id(epochs_0,sp0_list) #(container_epochs,sp)
            break
    p0 = Process(target=start_container, args=(container_type0,zoo_ip,servers,Manager))
    p0.start()

    while True:
        if Manager.MPC_steps >= start_step1:
            Manager.generate_container_id(epochs_1,sp1_list) #(container_epochs,sp)
            break
    p1 = Process(target=start_container, args=(container_type1,zoo_ip,servers,Manager))
    p1.start()

    while True:
        if Manager.MPC_steps >= start_step2:
            Manager.generate_container_id(epochs_2,sp2_list) #(container_epochs,sp)
            break
    p2 = Process(target=start_container, args=(container_type2,zoo_ip,servers,Manager))
    p2.start()

    while True:
        if Manager.MPC_steps >= start_step3:
            Manager.generate_container_id(epochs_3,sp3_list) #(container_epochs,sp)
            break
    p3 = Process(target=start_container, args=(container_type3,zoo_ip,servers,Manager))
    p3.start()

