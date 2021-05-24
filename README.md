# OACS
**Optimal Self-Adaptive Control Strategy for dynamic resource allocation**

This project presents part of the work developed from a collaboration between NACAD - the High Performance Computing Center (@ the Federal University of Rio de Janeiro) and the R&D Center of Dell-EMC.

Requiring as input only the expected execution time for an application, the OACS allows the resource allocation to provide the right amount of resources (# of cores) to satisfy such requirement. 

No data about the workload is required. The solution implemented in this work embodies an online estimator that identifies all essential parameters.

## Directory structure

```bash
OACS/
├── README.md 			# overview of the project
├── documentation/ 		# manuscript and presentation files of all developed work (presented in March,2021)
└── src/ 			# contains the code developed
    ├── README.md 		# describes how to implement a test
    ├── docker_image/		# contains the code of the video encoding application implemented on a Docker container
    └── ...
```

## Description

The main objective was to conceive an algorithm that provides to each application running in a server the sufficient amount of computational resources, allowing them to satisfy their SLA (Service Level Agreement). 
   
### Using Control Theory to address the resource allocation problem

The approach adopted in this work applied Control Theory, known as a model-based technique. Therefore, each application running in a server should be modelled in a mathematical form, aiming to establish a relationship between # of cores (the computational resource) and Execution Time (the SLA to be respected).

Although a mathematical form is not well defined for such case, this work analyzes some candidates, taking into account the curve defined by Amdalh's Law.

Due to the strong varying behavior and the large diversity of workload profiles, this work focuses on allocating computational resources only to **iterative workloads**. Such workloads consist of identical small jobs that run in succession, allowing the workload characteristic to vary much less than other sorts of workloads.


#### First approach: an Adaptive Control Strategy to allocate resources to a single application

This part of the work focuses on validating a model for the workload characteristic, as well as the coupling mechanism associating an online estimation process (Recursive Least Squares) to the control action.

![Control System Block Diagram - Adaptive Control Strategy](/sca.png)

#### Second approach: an Optimal Self-Adaptive Control Strategy to manage the resource allocation to multiple applications

This final part of the work focuses on the real-time implementation of the control strategy, now consisting by an optimal adaptive technique.

A centralized control module, **Resource Manager**, was conceived to take all required data from applications and then determine the right amount of resources to be allocated to an application. Taking the resource constraint at run-time into account, an optimal solution is evaluated.

![Global Resource Manager - OACS](/resource_manager.png)

## Requirements

The iterative workloads are implemented as Docker containers. Additionally, the data transfer from a container to the Resource Manager is implemented through Kafka.

A simple Kafka installation tutorial is available in https://hub.docker.com/r/ches/kafka/ 

The OACS was developed in Python.
