from kafka import KafkaProducer
from time import time

## Kafka Monitor class for video encoder container
class KafkaMonitor:
    
    def __init__(self, bootstrap_servers=None, topic=None,key=None):
        if not bootstrap_servers:
            bootstrap_servers = '172.17.0.3:9092'
        self.producer = KafkaProducer(bootstrap_servers = bootstrap_servers)
        self.topic = topic
        self.epoch_num = 0
        self.start_time = None
        self.key=key

    def on_epoch_begin(self, epoch, logs=None):
        self.start_time = time()
        
    def on_epoch_end(self, epoch, logs=None): 
        self.elapsed_time = time()-self.start_time
        kafka_tuple = str((self.epoch_num, self.elapsed_time)).encode('ascii') 
        self.producer.send(self.topic, kafka_tuple,self.key)
        self.producer.flush()
