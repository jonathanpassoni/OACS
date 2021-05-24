## The Class presented in this file is responsible for
## providing to Docker the mandatory arguments to
## build a container image as well as to set the same container
## to start its execution.

import os
import numpy as np

class Container_config:
    def __init__(self, container_data,zk_id,servers, manager):
        self.container_data = container_data
        self.zookeeper_id = zk_id
        self.servers = servers
        self.manager = manager
        
    def run(self):
        ## Set up of container configuration inside Docker Engine
        #Mandatory arguments
        self.data = self.manager.container_cpu0.get()
        self.container_name = self.data[0]
        self.initial_cpus = self.data[1]
        self.image = self.data[2]
        self.topic = self.data[3]
        self.container_code = self.container_data
        print "Code: {0} - Container name: {1} - Initial allocation: {2}".format(self.container_code, self.container_name, self.initial_cpus)
        #Execute Docker commands
        self.config_setup()

    def config_setup(self):
        print 'Image building ' + self.container_name
        #Build the container
        if self.container_code == 'three':
            os.chdir("video-encoding")
        else:
            os.chdir("ml")
        os.system("docker build --build-arg container_code={0} --build-arg container_name={1} --build-arg container_topic={3} -t {2} .".format(self.container_code,self.container_name, self.image, self.topic))
        print 'Container starting ' + self.container_name
        #Start the container execution
        os.system('/usr/bin/docker run -e "container_code={0}" -e "container_name={1}" -e "container_topic={4}" --cpus={2} --name={1}  {3} > cpu_{2}'.format(self.container_code, self.container_name, self.initial_cpus, self.image, self.topic))
    
