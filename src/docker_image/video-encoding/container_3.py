# Video encoder container
import sys
import os
import sys
from encoder import *

container_id = sys.argv[1]
container_topic = sys.argv[2]

kafka_callback = KafkaMonitor(topic=container_topic,key=container_id)

if __name__ == '__main__':

    args = ['mp4/frames-orig','mp4/frames-result','10','580',kafka_callback]
    main(args)
