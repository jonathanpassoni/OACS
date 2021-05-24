## This file contains the function used as a Process
## to initiate every container application.

import sys
from container_config import *
from message_receiver import *

def start_container(container_data,zoo_ip,servers,manager_instance):
    Container_config(container_data,zoo_ip,servers,manager_instance).run()

