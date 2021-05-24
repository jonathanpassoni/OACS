from multiprocessing import Lock, Queue
from message_receiver import *
import numpy as np
from scipy.optimize import minimize
from scipy.optimize import Bounds
import threading
import pandas as pd
import os
import time

## The cost function are not included on the ResourceManager class only because of
## optimization restrictions
## Remember that param = [alpha, beta]

def simple_ttf_estimation(u, cpus0, ttf0, param):
    ttf = ttf0 -param[1]*(u - cpus0)/(u*cpus0)
    if ttf <= 10.5:
        ttf = 10.5
    return ttf

def direct_cpu_estimation(ttf,param):
    cpus = param[1]/(ttf - param[0])
    return cpus

def direct_ttf_estimation(cpu,param):
    ttf = param[0] + (param[1]/cpu)
    if ttf <= 10.5:
        ttf = 10.5
    return ttf

def cost_function(x, cpu0,ttf0,sp,beta):
    ## cpu0, ttf0,sp and beta are numpy arrays
    u = x**-1
    v = sp - ttf0 + np.dot(cpu0**(-1),np.diagflat(beta))
    J = np.dot(np.dot(u,np.diagflat(np.power(beta,2))),u.T) - 2*np.dot(np.dot(u,np.diagflat(beta)), v.T)
    return J

class ResourceManager:
    ## In order to store all data provided by the running containers, some functions and variables were
    ## added in this class.
    def __init__(self,servers,total_cpus,total_epochs):
        ## total_epochs is mandatory only for the sake of data storage.
        # All data is saved in a dictionary whose elements are different dictionaries
        self.all_data={}
        self.total_epochs=total_epochs
        #Semaphors
        self.allocation_lock = threading.Lock()
        self.new_container_detected = threading.Lock()
        #Queues
        self.container_queue = Queue()
        self.container_cpu0 = Queue()
        self.container_cpu = Queue()
        #Variable
        self.servers = servers
        self.container_counter = 0 # variable used to build unique container ID
        self.total_cpus = total_cpus
        self.available_cpus = total_cpus
        #
        self.containers_alive = {}
        self.MPC_steps = 0
        self.resource_to_allocate = 0
        self.elapsed_time= 0

    def save_data(self, container_id):
        ## Function created only for the purpose of data storage
        self.container_id = container_id
        self.all_data[self.container_id]['step'].append(self.MPC_steps)
        self.all_data[self.container_id]['current_epoch'].append(self.containers_alive[self.container_id]['current_epoch'])
        self.all_data[self.container_id]['time_to_finish'].append(self.containers_alive[self.container_id]['last_time_to_finish'])
        #Parameter Estimation Process
        self.all_data[self.container_id]['alpha'].append(self.containers_alive[self.container_id]['param'][0])
        self.all_data[self.container_id]['beta'].append(self.containers_alive[self.container_id]['param'][1])
        self.all_data[self.container_id]['alpha_hat'].append(self.containers_alive[self.container_id]['param_hat'][1])
        self.all_data[self.container_id]['beta_hat'].append(self.containers_alive[self.container_id]['param_hat'][0])
        self.all_data[self.container_id]['beta_control'].append(self.MPC_beta_control_list[self.MPC_container_element -1])
        #Control
        self.all_data[self.container_id]['set_point'].append(self.containers_alive[self.container_id]['sp'])
        self.all_data[self.container_id]['cpus'].append(self.containers_alive[self.container_id]['last_cpu'])
        self.all_data[self.container_id]['sum_cpus'].append(self.sum_cpus)
        self.all_data[self.container_id]['update_time'].append(self.elapsed_time)
        print 'BETA saved : returned by the estimation: {0} - control: {1}'.format(self.all_data[self.container_id]['beta'][-1], \
                                                                                   self.all_data[self.container_id]['beta_control'][-1])
        if self.MPC_steps == self.total_epochs:
            os.chdir("../Data")
            i=0
            while True:
                if os.path.exists('MCA_testing_{0}_container_1.csv'.format(i)) == True:
                    i +=1
                else:
                    self.create_doc('MCA_testing_{0}_'.format(i))
                    break

    def create_doc(self, doc_name):
        ## Function created only for the purpose of data storage
        self.global_steps = []
        self.sum_cpus = []
        for container in self.all_data.keys():
            #Organizing the data
            self.container_id = []
            self.step = []
            self.current_epoch = []
            self.time_to_finish = []
            self.alpha = []
            self.beta = []
            self.alpha_hat = []
            self.beta_hat = []
            self.beta_control = []
            self.set_point = []
            self.cpus = []
            self.update_time = []
            #print "From {0}, there is {1} epochs data from storage".format(container,len(self.all_data[container]['time_to_finish']))
            for item in range(len(self.all_data[container]['time_to_finish'])):
                self.container_id.append(container)
                self.step.append(self.all_data[container]['step'][item])
                self.global_steps.append(self.all_data[container]['step'][item])
                self.current_epoch.append(self.all_data[container]['current_epoch'][item])
                self.time_to_finish.append(self.all_data[container]['time_to_finish'][item])
                self.alpha.append(self.all_data[container]['alpha'][item])
                self.beta.append(self.all_data[container]['beta'][item])
                self.alpha_hat.append(self.all_data[container]['alpha_hat'][item])
                self.beta_hat.append(self.all_data[container]['beta_hat'][item])
                self.beta_control.append(self.all_data[container]['beta_control'][item])
                self.set_point.append(self.all_data[container]['set_point'][item])
                self.cpus.append(self.all_data[container]['cpus'][item])
                self.sum_cpus.append(self.all_data[container]['sum_cpus'][item])
                self.update_time.append(self.all_data[container]['update_time'][item])
            self.data = {"Step": self.step,"Container ID": self.container_id, "Current Epoch":self.current_epoch,  \
                        "Time to finish":self.time_to_finish, "Alpha":self.alpha, "Beta":self.beta, \
                         "Alpha hat":self.alpha_hat, "Beta hat":self.beta_hat, "Beta control":self.beta_control, "SP":self.set_point, \
                         "CPUS":self.cpus, "Update time":self.update_time}
            self.doc_data = pd.DataFrame.from_dict(self.data)
            doc_container_name = doc_name + str(container) + '.csv'
            self.doc_data.to_csv(doc_container_name)
        self.global_data = {"Step":self.global_steps, "Sum CPUS":self.sum_cpus}
        self.doc_global_data = pd.DataFrame.from_dict(self.global_data)
        doc_sum_cpus = doc_name + 'sum_cpus.csv'
        self.doc_global_data.to_csv(doc_sum_cpus)
        print "Files created and saved"

    ###  System   
    ###  Functionalites developed for the initial phase of container configuration
    
    def include_container(self):
        # This method creates new pairs key/values for both dictionaries implemented
        self.all_data[self.new_container_name] = {'step':[],'current_epoch':[],'time_to_finish':[],'set_point':[],'cpus':[], \
                                       'alpha':[],'beta':[], 'alpha_hat':[],'beta_hat':[],\
                                       'beta_control':[],'update_time':[],'sum_cpus':[]}
        self.containers_alive[self.new_container_name] =  {'last_cpu':None,'last_time_to_finish':None,'param':None, \
                                                'param_bc':None, 'param_hat':None, 'sp':None,'current_epoch':None, \
                                                'total_epochs':None, 'start_time':None,'running_cpu':self.resource_to_allocate}   
        print "{0} included".format(self.new_container_name)

    def generate_container_id(self,container_epochs,sp):
        # This method generates unique identification variables (IDs) to a 
        # container which is about to start its execution
        self.container_counter += 1
        print 'Total number of containers: {0}'.format(self.container_counter)
        print 'Total number of available cpus: {0}'.format(self.available_cpus)
        self.new_container_detected.acquire() 
        # Semaphor waits until all necessary methods recognize this new container
        print "container setup started at {0}".format(time.time())
        self.new_container_id = str(self.container_counter)
        self.new_container_topic = 'topic_' + self.new_container_id
        self.new_container_name = 'container_' + self.new_container_id
        self.new_container_image= 'image_' + self.new_container_id
        self.resource_to_allocate = self.first_resource_allocation(self.new_container_id)
        if self.resource_to_allocate >=0.2:
            print 'Lista de Containers before inclusion: ',self.all_data.keys()
            if self.new_container_name not in self.all_data.keys(): 
                self.include_container()
            else:
                print "Container ID is already assigned to other container"
            print "container data configuration finished at {0}".format(time.time())
            # Queue sent to the Container config Thread in order to start
            # the container execution with the specified amount of resources
            self.container_cpu0.put([self.new_container_name, self.resource_to_allocate,self.new_container_image, self.new_container_topic])
            self.allocation_lock.release()
            Message_Receiver(self.servers,self.new_container_name,self.new_container_topic,self.resource_to_allocate,sp, container_epochs, self).start()

    def first_resource_allocation(self, container_id):
        self.allocation_lock.acquire()
        ## Set up of the initial amount of resources
        if self.available_cpus <= 4.0:
            resource = 0.5*self.available_cpus
        else:
            resource = 0.3*self.available_cpus
        resource = float('%.2f'%(resource))
        if resource < 0.2:
             print 'Insufficient amount of resources to start container {0}'.format(container_id)
        self.available_cpus -= resource ## Updating the available_cpus variable
        return resource

    def allocate_resource(self,container_id,resource):
        ## Apply the resource allocation for all containers except for their first epoch
        os.system("/usr/bin/docker update --cpus={0} {1}".format(resource, container_id))
        print 'cpus updated for {0} on Docker: {1}'.format(container_id, resource)

    def update_container_data(self,container_data):
        ## The Message Receiver demands for container data update
        if container_data[7] <= container_data[8]:
            self.containers_alive[container_data[0]] =  {'last_cpu':container_data[1],'last_time_to_finish':container_data[2], \
                                                         'param':container_data[3],'param_bc':container_data[4],'param_hat':container_data[5], \
                                                         'sp':container_data[6],'current_epoch':container_data[7], 'total_epochs':container_data[8], \
                                                         'start_time':container_data[9]}
        print "data updated from {0}: {1}".format(container_data[0],container_data[1:])

    def container_dead(self, container_id):
        ## Remove all container data from the dictionary with only alive containers
        ## once all epochs for that specific container were already executed.
        self.containers_alive.pop(container_id)
                    
    ## Functions developed so that the MPC could be implemented
    
    def execute_control(self,container_id):
        # This function implements the whole control strategy
        self.allocation_lock.acquire()
        self.MPC_steps += 1
        print 'STEP: ', self.MPC_steps
        ## Preparing data
        ## Lists must be initialized every MPC execution due to the high variability in starting/finishing a new container execution
        self.MPC_container_id_list = []
        self.MPC_cpus0_list = np.array([])
        self.MPC_ttf0_list = np.array([])
        self.MPC_sp_list = np.array([])
        self.MPC_param = []
        self.MPC_u = np.array([])
        self.MPC_ttf_list = np.array([])
        self.MPC_param_bc = []
        self.MPC_param_hat = []
        self.MPC_total_resources = self.total_cpus
        self.sum_cpus = 0.0
        self.Nc = len(self.containers_alive.keys()) # Number of alive containers
        ## Constraints applied on the total amount of resources 
        # Test 01
        """if self.MPC_steps == 57:
            self.total_cpus = 4.5
        elif self.MPC_steps == 80:
            self.total_cpus = 5.0
        elif self.MPC_steps == 110:
            self.total_cpus = 6.0
        elif self.MPC_steps == 145:
            self.total_cpus = 6.5"""
        # Test 03
        if self.MPC_steps == 70:
            self.total_cpus = 5.0
        elif self.MPC_steps == 190:
            self.total_cpus = 6.5
        ##
        self.MPC_total_resources = self.total_cpus
        self.available_cpus = self.MPC_total_resources 
        for container in self.containers_alive.keys():
            # IMPORTANT: for containers in initial epoch execution, due to the lack of information during this specific
            # time, they are not be considered for the control input evaluation.
            # However, their allocation is considered for establishing the right amount of available resources
            # at the time the control strategy is performed.
            if self.containers_alive[container]['current_epoch'] != None:
                self.MPC_container_id_list.append(container)
                self.MPC_sp_list = np.append(self.MPC_sp_list,self.containers_alive[container]['sp'])
                self.MPC_param.append(self.containers_alive[container]['param'])
                self.MPC_param_hat.append(self.containers_alive[container]['param_hat'])
                self.MPC_param_bc.append(self.containers_alive[container]['param_bc'])
                if container == container_id:
                    # For the container which asked for control input evaluation, the most recent data from self.containers_alive will be
                    # considered, since it had just finished an epoch execution
                    self.available_cpus += self.containers_alive[container]['last_cpu']
                    self.MPC_container_element = len(self.MPC_container_id_list)
                    self.MPC_cpus0_list = np.append(self.MPC_cpus0_list,self.containers_alive[container]['last_cpu'])
                    self.MPC_ttf0_list = np.append(self.MPC_ttf0_list,self.containers_alive[container]['last_time_to_finish'])
                else:
                    # For the others, since they are still running an epoch during this evaluation, the most recent allocation
                    # will be considered. For that reason, TTF must be estimated.
                    if self.containers_alive[container]['current_epoch'] != None:
                        self.MPC_cpus0_list = np.append(self.MPC_cpus0_list,self.containers_alive[container]['running_cpu'])
                        self.MPC_ttf0_list = np.append(self.MPC_ttf0_list,simple_ttf_estimation(self.MPC_cpus0_list[-1],self.containers_alive[container]['last_cpu'], \
                                                                                                self.containers_alive[container]['last_time_to_finish'],self.MPC_param[-1]))
                self.sum_cpus += self.MPC_cpus0_list[-1]
                self.available_cpus -= self.MPC_cpus0_list[-1]
            else:
                self.MPC_total_resources -= self.containers_alive[container]['running_cpu'] # the only occasion in which this variable have its value changed in a given step 
                self.available_cpus -= self.containers_alive[container]['running_cpu']
                self.sum_cpus += self.containers_alive[container]['running_cpu']
        self.Nc = len(self.MPC_container_id_list) # The real number of containers considered for control input evaluation
        #### Control Input evaluation
        ## Choosing  the most suitable set of parameters to generate u_inv
        self.MPC_beta_control_list = np.array([self.MPC_param[i][1] for i in range(self.Nc)])
        for i in range(self.Nc):
            # Verifying if a container is far from the desirable operating point
            if ((abs((self.MPC_sp_list[i] - self.MPC_ttf0_list[i])/self.MPC_sp_list[i]) > 0.15) \
                and (self.containers_alive[self.MPC_container_id_list[i]]['current_epoch'] != 1)):
                if (self.MPC_param_hat[i][0] > self.MPC_param[i][1]):
                    print 'u_inv evaluated with param_hat'
                    self.MPC_beta_control_list[i] = self.MPC_param_hat[i][0]
        self.perform_optimal_control()
        print self.control_input, self.MPC_container_element
        self.resource_to_allocate =float('%.2f'%(self.control_input[self.MPC_container_element - 1]))  
        if self.resource_to_allocate > self.available_cpus:
            self.resource_to_allocate = self.available_cpus
        self.available_cpus -= self.resource_to_allocate
        self.containers_alive[container_id]['running_cpu'] = self.resource_to_allocate
        self.allocate_resource(container_id, self.resource_to_allocate)
        self.elapsed_time = time.time() - self.containers_alive[container_id]['start_time']
        self.save_data(container_id)
        self.container_cpu.put([container_id, self.resource_to_allocate]) # Data sent to Message Receiver 
        print 'BETA: returned by the estimation: {0} - control: {1}'.format(self.MPC_param, self.MPC_beta_control_list)

    def perform_UOC(self):
        #Unconstrained Optimal Control
        self.u = np.array([(1/self.MPC_cpus0_list[i]) for i in range(self.Nc)])
        self.beta_vector = np.array([self.MPC_beta_control_list[i] for i in range(self.Nc)])
        self.sp_error = np.array(self.MPC_sp_list - self.MPC_ttf0_list)
        self.u_control =  np.dot(np.diagflat(self.beta_vector**(-1)),self.sp_error) + self.u
        
    def perform_optimal_control(self):
        self.perform_UOC()
        self.rel_sp_error = np.divide(self.sp_error, self.MPC_sp_list)
        for i in range(self.Nc):
            # Verifying if the UOC provides an unfeasible solution (u < 0)
            if (self.u_control[i] < 0) or (self.rel_sp_error[i] < -1.5):
                print 'U negative'
                cpu_bc = direct_cpu_estimation(self.MPC_sp_list[i], self.MPC_param_bc[i])
                cpu_current = direct_cpu_estimation(self.MPC_sp_list[i], self.MPC_param[i])
                if cpu_bc < cpu_current:
                    new_sp = direct_ttf_estimation(cpu_bc,self.MPC_param[i])
                    self.MPC_sp_list[i] = new_sp
                    new_ttf = direct_ttf_estimation(self.MPC_cpus0_list[i],self.MPC_param[i])
                    self.MPC_ttf0_list[i] = new_ttf
                    print 'U negative - compesation available: {0} {1} {2} {3}'.format(cpu_bc, cpu_current, new_sp, new_ttf)
                    self.perform_UOC()
                else:
                    print 'U negative - no compesation available'
        # Constrained Solution
        if sum(self.u_control**(-1)) > self.MPC_total_resources:
            print 'Total amount of cpu requested: {0} - cpu_list: {2} - available: {1}'.format(sum(self.u_control**(-1)), self.MPC_total_resources,self.u_control**(-1))
            cons = [{'type': 'ineq', 'fun': lambda u: np.array([self.total_cpus - sum(u)])}]
            b = [0.2,3.8]
            bnds = Bounds(b[0]*np.ones(self.Nc), b[1]*np.ones(self.Nc))
            solution = minimize(fun=cost_function,x0=self.MPC_cpus0_list, \
                                args=(self.MPC_cpus0_list,self.MPC_ttf0_list,self.MPC_sp_list,self.MPC_beta_control_list),method='SLSQP', \
                                bounds=bnds,constraints=cons,options={'maxiter':500})
            self.control_input = solution.x
        else:
            self.control_input = self.u_control**(-1)
