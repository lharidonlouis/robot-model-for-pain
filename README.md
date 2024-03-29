# Robot model for pain
Basic model for autonomous robot in python, with pain emotion modeling. Work used to study pain and emotions with social and autonomous robots. 

## Publication

Find related publication about this work published at 2023 AFFECTIVE COMPUTING & INTELLIGENT INTERACTION conference. [The effects of stress and predation on pain perception in
robots](https://hal.science/hal-04195283/document)

## Installation
As the robot we use is a khepera-IV we use inbuilt server client to communicate with the robot.
The client was rebuilt to be able to communicate with an inside serial port and not via bluetooth
Modified version of server is in the folder server. To install it, compile it with the following command:
```
make server
```
Make you have installed the khepera-IV libraries, see [here for more infos](https://ftp.k-team.com/KheperaIV/software/Gumstix%20COM%20Y/UserManual/Khepera%20IV%20User%20Manual%204.x.pdf).

Upload the compiled ``server``, ``model.py`` and ``cstm_serial.py`` into the robot (see library for infos).

A python serial library functional within khepera is provided in cstm_serial.py.


## Changing robot ?
This model is built originaly for Khepera-IV but is meant to be adaptable to any robots.
The model is meant to communicate with robot via serial port.
If you want to change the robot see ``Model.Motors.drive()`` and ``Model.update()`` and its contained functions

## run

We will use a custome serial port to be able to embodied server and model inside the robot
To run the model, simply run the following command:
```
//clean folder with
rm louis/res/*
//fake serial with
socat -d -d pty,raw,echo=0,link=/dev/ttyS0 pty,raw,echo=0,link=/dev/ttyS1 &
//run the server with
./server &
//run the client with
// python louis/model.py
```

## command infos 
``model.py`` has different options to run with a simulation mode, a debug mode, a manual mode and a run mode

### usage :
- ``model.py -[option] [lower_bound_food] [upper_bound_food] [lower_bound_shade] [upper_bound_shade] [name_of_file (without extension)``

### options :
- -r: run
- -d: debug
- -s: simulation
- -m : manual
- -h : help

### values :
- lower_bound_food : lower bound of the food stimulus - default : 940
- upper_bound_food : upper bound of the food stimulus - default : 955
- lower_bound_shade : lower bound of the shade stimulus - default : 450
- tupper_bound_shade : upper bound of the shade stimulus - default : 550
- name_of_file : name of the file where the data will be saved - default : data.csv

### example : 
- model.py -r 940 955 450 550 "expriment_1"


## Author
This work is done by Louis L'Haridon, phd student.

## License
[ETIS lab CNRS (UMR 8051)](https://www.etis-lab.fr/)
