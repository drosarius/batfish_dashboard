# Batfish DashBoard

 First, I want to say thank you to the Batfish team from making such a great tool!
 
 This dashboard wraps a few features from the tool [Batfish](www.batfish.org) in a "pretty" GUI.

## Quick Start


- Download and run [batfish](https://pybatfish.readthedocs.io/en/latest/getting_started.html):
    - docker pull batfish/allinone
    - docker run --name batfish -v batfish-data:/data -p 8888:8888 -p 9997:9997 -p 9996:9996 batfish/allinone
    
- git clone https://github.com/Marphlap/batfish_dashboard.git
- cd batfish_dashboard/

- docker build -t batfish_dashboard . && docker run -p 8050:8050 batfish_dashboard

If running locally:
   - Open web browser and navigate to:
   - 127.0.0.1:8050

If running on remote machine:
   - Open web browser and navigate to:
   - *remote_machine_ip*:8050
        
Enjoy!

## Features

### Graphs

##### Layer 3 Graph

<img src="/assets/img/Layer_3_Graph.PNG" width="1000" />


##### OSPF Graph

<img src="/assets/img/Ospf_graph.PNG" width="1000" />

##### BGP Graph

<img src="/assets/img/BGP_graph.PNG" width="1000" />

### Ask a Question

<img src="/assets/img/Ask_a_question.PNG" width="1000" />

### Trace Route

<img src="/assets/img/trace_routev2.PNG" width="1000" />

### Refractor ACLs

<img src="/assets/img/ACL_refractored.PNG" width="1000" />

## Roadmap

* Chaos Monkey
* Ask a Question advanced search
* ACL Tester
