# OACS
**Optimal Self-Adaptive Control Strategy for dynamic resource allocation**

This repository presents the final work developed in a collaborative project between the R&D Center of Dell-EMC and NACAD - the High Performance Computing Center (@ the Federal University of Rio de Janeiro).

Requiring as input only the expected execution time for an application, the OACS allows the resource allocation to provide the right amount of resources (# of cores) to satisfy such specification. 

No data about the workload is required. The solution implemented embodies an online estimator that identifies all essential parameters.

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

The main objective was to conceive an algorithm that provides to each application running in a server the right amount of computational resources, allowing them to satisfy their SLA (Service Level Agreement). 
   
### Using Control Theory to address the resource allocation problem

The approach adopted in this work applied Control Theory, known as a model-based technique. Therefore, each application running in a server should be modelled in a mathematical form, aiming to establish a relationship between # of cores (the computational resource) and Execution Time (the SLA to be respected).

Although a mathematical form is not well defined for such case, this work analyzes some candidates, taking into account the curve defined by Amdalh's Law.

Due to the strong varying behavior and the large diversity of workload profiles, this work focuses on allocating computational resources only to **iterative workloads**. Such workloads consist of identical small jobs that run in succession, allowing the workload characteristic to vary much less than other sorts of workloads.

#### Main Concept

The main concept of this project has already been the object of:

- a patent ([Resource Adaptation Using Nonlinear Relationship Between System Performance Metric and Resource Usage](https://patents.google.com/patent/US20210149727A1/en)), presenting an initial resource allocation algorithm using control strategies that takes advantage of the Amdalh's Law to establish a mathematical model for software applications.

- a conference paper ([Control strategies for adaptive resource allocation in cloud computing](https://www.sciencedirect.com/science/article/pii/S2405896320325933)) presented at IFAC 2020, which presents the same initial strategy and the first results of a simple test case performed.

A broader testing campaign, including different input values, was led and carefully analysed in section 1.2 of [Manuscript](/documentation/manuscript.pdf). As a result, a new control strategy was intended to be designed. Its development was split in two parts, using the agile methodology:


#### First Part: an Adaptive Control Strategy to allocate resources to a single application

This part of the work focuses on validating a model for the workload characteristic, as well as the coupling mechanism associating an online estimation process (Recursive Least Squares method) to the control action.

![Control System Block Diagram - Adaptive Control Strategy](/sca.png)


#### Final Part: an Optimal Self-Adaptive Control Strategy to manage the resource allocation to multiple applications

This final part of the work focuses on the real-time implementation of the control strategy, now consisting of an optimal adaptive technique.

A centralized control module, **Resource Manager**, was conceived to take all required data from applications and then determine the right amount of resources to be allocated to an application. Taking the resource constraint at run-time into account, an optimal solution is evaluated.

![Global Resource Manager - OACS](/resource_manager.png)

## Requirements

The iterative workloads are implemented as Docker containers. Additionally, the data transfer from a container to the Resource Manager is implemented through Kafka.

A simple Kafka installation tutorial is available in https://hub.docker.com/r/ches/kafka/ 

The OACS was developed in Python.
