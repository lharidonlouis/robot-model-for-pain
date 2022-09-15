# Robot model for pain
Basic bio-inspired pain model for autonomous robot in python 

## Installation
As the robot we use is a khepera-IV we use inbuilt server client to communicate with the robot.
The client was rebuilt to be able to communicate with an inside serial port and not via bluetooth

Modified version of server is in the folder server. To install it, compile it with the following command:
```
make server
```
Make you have installed the khepera-IV libraries, see [here for more infos](https://ftp.k-team.com/KheperaIV/software/Gumstix%20COM%20Y/UserManual/Khepera%20IV%20User%20Manual%204.x.pdf).

Upload the compiled server, model.py and cstm_serial.py into the robot (see library for infos)

A python serial library functional within khepera is provided in cstm_serial.py


## Changing robot ?
This model is built originaly for Khepera-IV but is meant to be adaptable to any robots.
The model is meant to communicate with robot via serial port.
If you want to change the robot see Model.Motors.drive() and Model.ensors.update()

## run

We will use a custome serial port to be able to embodied server and model inside the robot
To run the model, simply run the following command:
```
socat -d -d pty,raw,echo=0,link=/dev/ttyS0 pty,raw,echo=0,link=/dev/ttyS1 &
./server &
python model.py 
```

## Author
This work is done by Louis L'Haridon, phd student.

## License
[ETIS lab CNRS (UMR 8051)](https://www.etis-lab.fr/)
