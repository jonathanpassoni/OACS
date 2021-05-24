import threading
import time
import os

class Container_Config(threading.Thread):
    def __init__(self, ResourceManager_instance, zk_id):
        threading.Thread.__init__(self)
        self.zookeeper_id = zk_id
        self.manager = ResourceManager_instance

    def run(self):
        #The configuration of a new container only starts if the function config is called
        self.manager.config_container.acquire()
        self.config(self.manager.new_container_data)
        self.manager.new_container = False
        #Delete an old topic with the same name and replace it by a new one
        os.system('/usr/bin/docker run --rm ches/kafka kafka-topics.sh --delete --topic {0}  --zookeeper {1}:2181'.format(self.topic_name, self.zookeeper_id))
        os.system('docker run --rm ches/kafka kafka-topics.sh --list --zookeeper 172.17.0.2:2181')
        os.system('/usr/bin/docker run --rm ches/kafka kafka-topics.sh --create --topic {0} --replication-factor 1 --partitions 1 --zookeeper {1}:2181'.format(self.topic_name, self.zookeeper_id))
        #Include container in ResourceManager_instance list
        self.image_name = 'image' + self.id
        print 'Image building' + self.container_name
        #Build the container
        os.system("docker build --build-arg container_code={0} --build-arg container_topic={1} -t {2} .".format(self.container_code,self.topic_name, self.image_name))
        print 'Container starting' + self.container_name
        #Allocate the initial amount of resource
        os.system('/usr/bin/docker run -e "container_code={0}" --cpus={1} --name={2}  {3} > cpu_{2}'.format(self.container_code, self.initial_cpus, self.container_name, self.image_name))

    def config(self,container_data):
        #Semaphor used in order to generate unique names for topic, image and container
        self.manager.names_lock.acquire()
        self.container_code = container_data[0]
        self.initial_cpus = container_data[1]
        self.id = str(len(self.manager.all_data.keys()) +1)
        self.topic_name = 'topic' + self.id
        self.manager.new_container_topic = self.topic_name
        self.manager.new_container = True
        self.container_name = 'container' + self.id
        self.manager.include_container(self.topic_name, self.container_name)
        self.manager.names_lock.release()    


    
    
        
