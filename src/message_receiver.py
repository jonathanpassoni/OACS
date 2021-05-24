## This file contains the Message Receiver class, resposible for
## dealing with messages arriving from containers through Kafka.

import threading
import time
from kafka import KafkaConsumer
from adaptation import *
import os
import numpy as np

class Message_Receiver(threading.Thread):
    def __init__(self,servers, container_name, container_topic, cpus_0, sp, total_epochs, manager):
        threading.Thread.__init__(self)
        self.servers = servers
        self.manager = manager
        self.name = container_name
        self.topic = container_topic
        self.current_epoch = 0
        self.cpus = cpus_0
        self.sp = sp
        self.total_epochs = total_epochs
        self.consumer = KafkaConsumer(self.topic,bootstrap_servers=self.servers)

    def run(self):
        self.manager.new_container_detected.release()
        print 'Container Name: {0} - Topic: {1}'.format(self.name, self.topic)
        print 'Container {0} a espera'.format(self.name)
        print 'Lista de Containers after inclusion: ', self.manager.all_data.keys()
        ## Receiving messages from Kafka
        for msg in self.consumer:
            start_time = time.time()
            self.container_id = str(msg[5]) ## key
            self.time_to_finish = float(str(msg[6]).split(',')[1][1:-2])
            self.current_epoch = float(str(msg[6]).split(',')[0][1:])
            # Determine the initial guess for the estimated parameter beta so that
            # the estimator can be initialized
            if self.current_epoch == 1:
                beta_guess = 10.0
                while True:
                    value = (beta_guess/self.cpus) - self.time_to_finish
                    if value >0:
                        beta_guess -= 10.0
                        print 'INITIAL VALUE FOR THE ESTIMATED PARAMETER BETA: {0}'.format(beta_guess)
                        break
                    else:
                        beta_guess += 10.0
                self.estimator =  AdaptationEngine(w=np.array([beta_guess,0.0]))
            print 'Epoch: {0} - CPUS: {1} - TTF:{2}'.format(self.current_epoch, self.cpus, self.time_to_finish)
            ## Estimation
            self.estimator.update_parameters(self.cpus,self.time_to_finish)
            self.param = self.estimator.get_param()
            self.param_bc = self.estimator.get_param_bc()
            self.param_hat = self.estimator.get_param_hat()
            ## Control aspect: Preparing data to be sent to Resource Manager
            self.container_data = [self.container_id, self.cpus, self.time_to_finish, \
                                   self.param, self.param_bc, self.param_hat, self.sp[int(self.current_epoch)], \
                                   self.current_epoch, self.total_epochs, start_time]
            self.manager.update_container_data(self.container_data)
            self.manager.execute_control(self.container_id)
            ## Receiving from the Resource Manager the data with the right resource allocation already updated
            self.container_data = self.manager.container_cpu.get()
            if self.container_data[0] == self.container_id:
                self.cpus = self.container_data[1]
                print 'cpus updated inside container {0} execution: {1}'.format(self.container_id,self.cpus)
            if self.current_epoch == self.total_epochs:
                self.manager.container_dead(self.container_id)
            self.manager.allocation_lock.release() # end of allocation operation
                
