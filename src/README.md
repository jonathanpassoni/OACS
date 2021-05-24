# Real-Time implementation of the OACS

This part of the repository contains the main code of the OACS, as well as the video encoder application, developed by @martinamaggio in [SAVE](https://github.com/martinamaggio/save) and adapted in this work to an interative workload.

## Requirements

In normal ubuntu distribution (LTS), you need to install the following packages:
     python-imaging, python-numpy, python-scipy, mplayer
      
Step-by-step installation:

```bash
   sudo apt-get install mplayer
   sudo apt-get install imagemagick
   sudo apt-get install python-imaging python-numpy python-scipy
```

## How to obtain the frames from an YouTube video

1. Download the Youtube video using services like  http://en.savefrom.net/1-how-to-download-youtube-video/

The video used for the tests mentioned on the manuscript is available [here](https://www.youtube.com/watch?v=xJz6OJgrDnA).

2. On (Ubuntu) terminal, execute 

```bash
mplayer -vo jpeg:quality=100:outdir=./frames-orig \
		  	./mp4/$V.mp4 > /dev/null 2>&1
```

You must specify first the name of the video file(V), which must be copied to the mp4 folder.

## Implementing a test

The file main_MCA_test01.py shows an example of a test implemented.

1. First variables assignment before creating a Resource Manage Instance
	The total amount of resources <em>total_cpus</em>;
	The total number of epochs, for all containers <em>total_epochs</em> , only for the purpose to generate data files.
	
2. For each container to be executed:

	2.1. Variables assignment:
	
	<em>start_step</em> : the moment where the container is set to run, expressed in steps (number of total iterative workloads finished  <em>Manager.MPC_steps</em>)
	
	<em>epochs</em>: number of epochs that the application must execute its workload
	
	<em>sp_list</em>: the set-point list, expressed in execution time, containing the set-point value for each epoch to be executed.
	
	<em>container_type</em> : the corresponding container application defined in the Dockerfile.
	
	2.2. Launching a container:
```bash
while True:
	if Manager.MPC_steps >= start_step:
		Manager.generate_container_id(epochs_,sp_list) 
		break
p = Process(target=start_container, args=(container_type,zoo_ip,servers,Manager))
p.start()
```

