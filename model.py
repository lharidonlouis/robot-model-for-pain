##
# @file model.py
#
# @brief Simple bio-inspired pain model fo Khepera IV robot.
#
# @author  Louis L'Haridon
# @date    2022/06/20
# @version 0.1
#
# @section description_doxygen_example Description
# In a Two Resources Problem (TRP), the robot has to choose between two resources to maintain its viability. 
# This model is used to then, induce artifical pain and observe the robot's reaction.
#
# @section notes_doxygen_example Notes
# - This model is built originaly for Khepera-IV but is meant to be adaptable to any robots.
#
# @section todo_doxygen_example TODO
# - Physiological variables.
# - Motor control.  
# - Main program.
#
# Copyright (c) 2022 Louis L'Haridon.  All rights reserved.

# Modules
import random
import matplotlib.pyplot as plt
import numpy as np 
import time
import math


# GLOBAL PARAMETERS
# ----------------------------------------------------------------------------------------------------------------------
SIMULATE_VALUES = True # True if simulation, false if real values
TIME_SLEEP = 0.1 # Time between each simulation step
N_US_SENSORS = 8 # Number of UltraSonic Sensors.
N_IR_SENSORS = 8 # Number of InfraRed Sensors.
N_GROUND_SENSORS = 4 # Number of Ground Sensors.
N_NOCICEPTORS = 8 # Number of Nociceptors.
# ----------------------------------------------------------------------------------------------------------------------


# Python program to get average of a list
def mean(lst):
    if((sum(lst) != 0) and (len(lst) != 0)):
        return sum(lst)/len(lst)
    else:
        return 0

def normalize(list):
    """
    The function normalize normalizes a list of values.
    and returns a float list.
    If max is 0, the function returns a list of 0.
    If max is greater than 1, the funtion returns a normalized list
    If max is between 0 and 1, the function returns the original list
    """
    if(max(list) > 0):
        if(max(list)>1.0):
            return [float(i)/max(list) for i in list]
        else:
            return [float(i) for i in list]
    else:
        return [0.0 for i in list]

# The class var is a container for the three physiological variables of the phisiology.
class variables:
    def __init__(self):
        #actual values
        self.energy = 1.0 # physological variable for ernergy
        self.tegument = 1.0 # physological variable for tegument
        self.integrity = 1.0 # physological variable for integrity
        #ideal target
        self.ideal_energy  = 1.0 # ideal target for ernergy
        self.ideal_tegument = 1.0 # ideal target  for tegument
        self.ideal_integrity = 1.0 # ideal target  for integrity


# A motivation object has three attributes: energy, tegument, and integrity. Each attribute is a
class motivations:
    def __init__(self):
        """
        The function __init__() is a special function in Python classes. It is known as a constructor and is
        used for initializing the attributes of an object
        """
        self.energy = 1.0 # motivation for ernergy
        self.tegument = 1.0 # motivation for tegument
        self.integrity = 1.0 # motivation for integrity
        
# The class deficits is a container for the three deficits that are used in the model.
class deficits:
    def __init__(self):
        self.energy = 0.0 # energy deficit
        self.tegument = 0.0 # tegument deficit
        self.integrity = 0.0 # integrity deficit

# A class that contains the cues for a robot.
class cues:
    def __init__(self):
        self.energy = 0.0 # energy cue
        self.tegument = 0.0 # tegument cue
        self.integrity = 0.0 # integrity cue



# The physiology class is a class that contains the variables, deficits, cues, and motivations
# classes. It also contains functions that update the values of the variables, deficits, cues, and
# motivations
class physiology:
    def __init__(self, parent):
        self.var = variables() #physiolocial variables
        self.defi  = deficits() #deficits
        self.cue = cues() #cues
        self.mot  = motivations() #motivations
        self.parent = parent

    def update_var(self):
        """
        The update_var function decreases the energy and tegument variables by 0.1 and 0.05 respectively.
        """
        self.var.energy -= 0.001
        self.var.tegument -= 0.0005
    
    def update_def(self):
        """
        The function update_def() updates the values of the variables in the class deficit
        """
        self.defi.energy = self.var.ideal_energy - self.var.energy
        self.defi.integrity = self.var.ideal_integrity - self.var.integrity
        self.defi.tegument = self.var.ideal_tegument - self.var.tegument

    def update_cue(self, parent):
        """
        The function update_cue() updates the cue object with the values of the environment
        """
        #simulation of values
        #TODO actual perception of environment
        self.cue.energy = mean(parent.sensor.food)
        self.cue.tegument = mean(parent.sensor.tegument)
        self.cue.integrity = mean(parent.sensor.US)
    
    def update_mot(self):
        """
        The function takes the values of the cue and defi objects and adds them together, then multiplies
        them by the cue object's values
        """
        self.mot.energy = self.defi.energy + (self.defi.energy * self.cue.energy)
        self.mot.tegument = self.defi.tegument + (self.defi.tegument * self.cue.tegument)
        self.mot.integrity = self.defi.integrity + (self.defi.integrity * self.cue.integrity)

    def display(self):
        """
        The function display displays the values of the variables, deficits, cues, and motivations of the robot
        """
        print("----------------------------------------------------")
        print("Energy      : "+"{:.2f}".format(self.var.energy)+
                "  | def : "+"{:.2f}".format(self.defi.energy)+
                " | cue : "+"{:.2f}".format(self.cue.energy)+
                " | mot "+"{:.2f}".format(self.mot.energy))
        print("Tegument    : "+"{:.2f}".format(self.var.tegument)+
                "  | def : "+"{:.2f}".format(self.defi.tegument)+
                " | cue : "+"{:.2f}".format(self.cue.tegument)+ 
                " | mot "+"{:.2f}".format(self.mot.tegument))   
        print("Integrity   : "+"{:.2f}".format(self.var.integrity)+
                "  | def : "+"{:.2f}".format(self.defi.integrity)+
                " | cue : "+"{:.2f}".format(self.cue.integrity)+
                " | mot "+"{:.2f}".format(self.mot.integrity))                
        print("----------------------------------------------------")

    def update(self):
        """
        The function `update` updates the variables, definitions, cues, and motives of robot
        """
        self.update_var()
        self.update_def()
        self.update_cue(self.parent)
        self.update_mot()

    



# The class motors has two attributes, left and right, which are both floats. 
class motors:
    def __init__(self):
        self.left = 0.0 # speed of left motor
        self.right = 0.0  # speed of right motor


class nociceptor:
    def __init__(self, parent):
        self.parent = parent
        self.nociceptor = [0.0] * N_NOCICEPTORS # nociceptors
        self.speed_nociceptor = [0.0] * N_NOCICEPTORS # Speed nociceptors
        self.circ_nociceptor = [0.0] * N_NOCICEPTORS # Circular nociceptors

        self.treshold = 0.3 # treshold for nociceptors
        if(SIMULATE_VALUES):
            self.random_nociceptor()

    def gaussian(self,val, dist):
        """
        The function gaussian() returns gaussian curve value at index i with peak value val
        @param val: peak value of gaussian curve
        @param dist: distance from peak value of gaussian curve
        """
        if(val>0):
            return (1/(dist*math.sqrt(2*math.pi)))*math.exp(-((val-dist)**2)/(2*dist**2))
        else:
            return 0.0


    def sumcol(self, list, i):
        """
        Function that compute sum of given column in a 2D list
        @param list: 2D list
        @param i: id of column to sum
        @return: sum of ith column of 2D list list
        """
        return sum([row[i] for row in list])

    def radiate(self):
        """
        Function that when a nociceptor value is above a treshold 
        radiates with gaussian curve to neighboor nociceptors
        """
        tmp_nociceptor = [[0.0 for i in range (N_NOCICEPTORS)] for j in range(N_NOCICEPTORS)] # temporary nociceptors

        for i in range(N_NOCICEPTORS):
            # Each nociceptor generates a gaussian curve
            if self.nociceptor[i] > self.treshold:
                for j in range(N_NOCICEPTORS):
                    if(j!=i):
                        tmp_nociceptor[i][j] = self.gaussian(self.nociceptor[i], abs(j-i))
                    else:
                        tmp_nociceptor[i][j] = self.nociceptor[i]
        # Each nociceptor gets value of sum of its temporary nociceptors
        for i in range(N_NOCICEPTORS):
            self.nociceptor[i] = self.sumcol(tmp_nociceptor,i)

        # Normalisation of nociceptors
        self.nociceptor = normalize(self.nociceptor)


    def update(self):
        """
        The function update() updates the nociceptors
        """
        self.compute_noci()
        self.radiate()


    def compute_speed(self):
        """
        The function takes parent sensor US and computes speed of object approaching
        using TIME_SLEEP
        """
        self.speed_nociceptor = [self.parent.sensor.diffUS[i]/TIME_SLEEP for i in range(N_NOCICEPTORS)]

    def compute_circ(self):
        """
        The function computes the circular difference between the current and previous US sensor values, and
        stores the result in the circ_nociceptor array
        """
        r = [i for i in range(N_US_SENSORS-1)]
        r.append(1)
        for i in range(N_US_SENSORS):
            self.circ_nociceptor[i] = (abs(self.parent.sensor.US[i] - self.parent.sensor.prevUS[r[i]]))/TIME_SLEEP


    def compute_noci(self):
        """
        It computes the nociceptor values by averaging the speed and circ nociceptor values.
        """
        self.compute_speed()
        self.compute_circ()
        self.nociceptor = [(self.speed_nociceptor[i] + self.circ_nociceptor[i])/2 for i in range(N_NOCICEPTORS)]


    def display(self):
        """
        The function display() displays the nociceptors
        """
        print("----------------------------------------------------")
        print ("CNocicept: ", ["{0:0.2f}".format(i) for i in self.circ_nociceptor])
        print ("SNocicept: ", ["{0:0.2f}".format(i) for i in self.speed_nociceptor])
        print ("Nocicept : ", ["{0:0.2f}".format(i) for i in self.nociceptor])
        print("----------------------------------------------------")

    def random_nociceptor(self):
        """
        The function random_nociceptor() generates a random nociceptor
        """
        self.nociceptor = [random.uniform(0,1)/3 for i in range(N_NOCICEPTORS)]
            
        
class sensors:
    def __init__(self):
        self.US = [0.0] * N_US_SENSORS # Ultrasonic Sensors
        self.IR = [0.0] * N_IR_SENSORS # InfraRed Sensors
        self.GROUND = [0.0] * N_GROUND_SENSORS # Ground Sensors
        self.prevUS = [0.0] * N_US_SENSORS # Previous Ultrasonic Sensors
        self.prevIR = [0.0] * N_IR_SENSORS # Previous InfraRed Sensors
        self.prevGROUND = [0.0] * N_GROUND_SENSORS # Previous Ground Sensors
        self.diffUS = [0.0] * N_US_SENSORS # Differential US Sensors
        self.diffIR = [0.0] * N_IR_SENSORS # Differential IR Sensors
        self.diffGROUND = [0.0] * N_GROUND_SENSORS # Differential Ground Sensors
        self.food = [0.0] * 2 # food sensoor
        self.tegument = [0.0] *2 # tegument sensor

    def update(self):
        """
        The update function is called every time the robot is updated. It stores the previous values of the
        robot, gets the new values, computes the difference between the new and old values, and computes the
        food and tegument values
        """
        #TODO get values of robot
        self.store_prev()
        if(SIMULATE_VALUES):
            self.random_val()
        else:
            #GET VALUES FROM ROBOT
            pass
        self.compute_diff()
        self.compute_food()
        self.compute_tegument()

    def store_prev(self):
        """
        The function store_prev() stores the current values of the sensors in the previous values of the
        sensors
        """
        self.prevUS = self.US
        self.prevIR = self.IR
        self.prevGROUND = self.GROUND
            
    def compute_diff(self):
        """
        It computes the difference between the current and previous sensor readings
        """
        self.diffUS = [abs(self.US[i]-self.prevUS[i]) for i in range(N_US_SENSORS)]
        self.diffIR = [abs(self.IR[i]-self.prevIR[i]) for i in range(N_IR_SENSORS)]
        self.diffGROUND = [abs(self.GROUND[i]-self.prevGROUND[i]) for i in range(N_GROUND_SENSORS)]

    def compute_food(self):
        """
        #function that takes GROUND values and computes food value (0.0 to 1.0)
        # food resources ar represented as high values in the GROUND sensors
        # food is computed as the mean of the GROUND values 
        # if N_GROUND_SENSORS is pair, each tegument is computed as the mean of the half of sensors
        # else if N_GROUND_SENSORS is unpair, each tegument is computed as the mean of the half of sensors plus middle sensor
        """
        if N_GROUND_SENSORS % 2 == 0:
            self.food[0] = mean(self.GROUND[0:N_GROUND_SENSORS//2])
            self.food[1] = mean(self.GROUND[N_GROUND_SENSORS//2:N_GROUND_SENSORS])
        else:
            self.food[0] = mean(self.GROUND[0:((N_GROUND_SENSORS//2)+1)])
            self.food[1] = mean(self.GROUND[((N_GROUND_SENSORS//2)+1):N_GROUND_SENSORS])


    def compute_tegument(self):
        """
        function that takes GROUND values and computes tegument value (0.0 to 1.0)
        # tegument resources are represented as low values in the GROUND sensors
        # tegument is computed as the mean of the inverse of the GROUND values
        # if N_GROUND_SENSORS is pair, each tegument is computed as the mean of the half of sensors
        # else if N_GROUND_SENSORS is unpair, each tegument is computed as the mean of the half of sensors plus middle sensor
        """
        if N_GROUND_SENSORS % 2 == 0:
            self.tegument[0] = 1.0 - mean(self.GROUND[0:N_GROUND_SENSORS//2])
            self.tegument[1] = 1.0 - mean(self.GROUND[N_GROUND_SENSORS//2:N_GROUND_SENSORS])
        else:
            self.tegument[0] = 1.0 - mean(self.GROUND[0:((N_GROUND_SENSORS//2)+1)])
            self.tegument[1] = 1.0 - mean(self.GROUND[((N_GROUND_SENSORS//2)+1):N_GROUND_SENSORS])


    def display(self):
        """
        The function display each value of sensors, each value is displayed with 2 digits after the decimal point
        """
        print("----------------------------------------------------")
        print ("US       : ", ["{0:0.2f}".format(i) for i in self.US])
        print ("IR       : ", ["{0:0.2f}".format(i) for i in self.IR])
        print ("GROUND   : ", ["{0:0.2f}".format(i) for i in self.GROUND])
        print ("Food     : ", ["{0:0.2f}".format(i) for i in self.food])
        print ("Tegument : ", ["{0:0.2f}".format(i) for i in self.tegument])
        print("----------------------------------------------------")
        

    def random_val(self):
        """
        It takes the current state of the robot, and returns the next state of the robot
        """
        for i in range(N_US_SENSORS):
            self.US[i] = random.random()
        for i in range(N_IR_SENSORS):
            self.IR[i] = random.random()    
        for i in range(N_GROUND_SENSORS):
            self.GROUND[i] = random.random()


# The class `robot` defines the robot and its attributes
class robot:
    def __init__(self,name):
        """
        A class that defines the robot.
        @brief Class used to define the robot.
        @param name the name of the robot
        """
        #robot infos
        self.name = name
        self.socket = "XXXXXX"
        #motor control
        self.motor = motors()
        #physiology
        self.phys = physiology(self)
        #sensors
        self.sensor = sensors()
        #nociceptor
        self.noci = nociceptor(self)

    def update(self):
        """
        The update function updates the sensor and physioloogy of the object
        """
        self.sensor.update()
        self.noci.update()
        self.phys.update()

    def display(self):
        """
        The display function displays the sensor and physioloogy of the object
        """
        self.sensor.display()
        self.phys.display()
        self.noci.display()




# It creates an object of the class `robot` and assigns it to the variable `khepera`.
khepera = robot("khepera-iv")


print(khepera.name)
for i in range(50):
    khepera.update()
    khepera.display()
    time.sleep(TIME_SLEEP)