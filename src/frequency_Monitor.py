## This script aims to register the CPU frequency in every second
## until all steps for a given test are executed.

import threading
import subprocess, time, re
import pandas as pd
import os

def Register_CPU_frequency(Manager,total_steps):
    cpu_frequency =[]
    result_time_list = []
    step_list = []
    while True:
        if Manager.MPC_steps < total_steps:
            result = subprocess.check_output('lscpu | grep MHz',stderr=subprocess.STDOUT,shell=True).decode("utf-8").splitlines()
            result_time = time.time()
            cpu_frequency.append(float(result[0][-8:]))
            result_time_list.append(result_time)
            step_list.append(Manager.MPC_steps)
            time.sleep(1)
        else:
            print 'CPU Clock Speed Doc being created - Steps registered: {0}'.format(len(cpu_frequency))
            data = {"CPU Frequency": cpu_frequency, "Time":result_time_list,"Step":step_list}
            doc_data = pd.DataFrame.from_dict(data)
            i=0
            while True:
                if os.path.exists('MCA_testing_{0}_container_1.csv'.format(i)) == True:
                    i +=1
                else:
                    i -= 1
                    doc_data.to_csv('frequency_monitoring_test_{0}.csv'.format(i))
                    break
            break
        
