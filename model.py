##
# @file model.py
#
# @brief Simple bio-inspired pain model fo Khepera IV robot.
#
# @author  Louis L'Haridon
# @date    2022/07/02
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
import os
import cstm_serial
import time
import math

# GLOBAL PARAMETERS
# ----------------------------------------------------------------------------------------------------------------------
SIMULATE_VALUES = True # True if simulation, false if real values
TIME_SLEEP = 0.1 # Time between each simulation step
N_US_SENSORS = 5 # Number of UltraSonic Sensors.
N_IR_SENSORS = 12 # Number of IR Sensors.
N_NOCICEPTORS = 8 # Number of Nociceptors.
MANUAL = 0 # Manual control.
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



# The class variable defines a phhysiological variable
class Variable:
    def __init__(self, name, value, min_target, max_target):
        self.name = name
        self.value = 1.0
        self.min_target = min_target
        self.max_target = max_target
        self.deficit = 0.0

    def set_value(self, value):
        """
        This function takes a value and sets the value of the object to that value.
        
        @param value The value of the parameter.
        """
        self.value = value
    
    def get_value(self):
        """
        The function get_value() returns the value of the variable value
        
        @return The value of the instance variable value.
        """
        return self.value

    def get_deficit(self):
        """
        It returns the deficit of the country.
        
        @return The deficit of the object.
        """
        return self.deficit

    def update_deficit(self):
        """
        If the value is less than the minimum target, the deficit is the value minus the minimum target. 
        
        If the value is greater than the maximum target, the deficit is the value minus the maximum target. 
        
        Otherwise, the deficit is zero.
        """
        if self.value < self.min_target :
            self.deficit = self.value - self.min_target
        elif self.value > self.max_target :
            self.deficit = self.value - self.max_target
        else:
            self.deficit = 0.0


    def display(self):
        print("----------------------------------------------------")
        print(self.name + " : " + self.get_value())
        print("----------------------------------------------------")
    
# The class defines a sensor
class sensors:
    def __init__(self, name, size, s_char, r_char, min, max, inv, robot):
        self.val = [0.0] * size 
        self.name = name
        self.size = size
        self.s_char = s_char
        self.r_char = r_char
        self.min = min
        self.max = max
        self.inv = inv # True if the sensor is inverted (the greater the value, the smaller the data)
        self.robot = robot

    def update(self):
        """
        This function updates the value of the sensor.
        """
        success = 0
        while(not success):
            self.robot.send_data(self.s_char)
            data = self.robot.get_data()
            data.replace('\r\n', '')
            if(data != None):
                data = self.robot.decode(data)
                if(data[0] == self.r_char):
                    success=1
                    for i in range(self.size):
                        if self.inv:
                            self.val[i] = 1.0 - ((float(data[i+1])-self.min) / (self.max-self.min))
                        else:
                            self.val[i] = ((float(data[i+1])-self.min) / (self.max-self.min))
                

        



# The class `behavior` defines the behavior and its attributes
class behavior:
    def __init__(self, var, sensor):
        self.cue = 0.0 # cue associated with the behavior
        self.associated_var = var
        self.mot = motivation(var, self.cue, sensor) # motivation associated with the behavior


    def display(self):
        """
        The function takes a cue and a mot as arguments and returns a new instance of the class
        """
        print("----------------------------------------------------")
        print("Cue : " + str(self.cue))
        print("Mot : " + str(self.mot.get_val()))
        print("----------------------------------------------------")


# The class `motivation` defines a motivation and its attributes
class motivation:
    def __init__(self, var, stimulus, drive):
        self.val = 0.0 # value of the motivation
        self.controlled_var = var
        self.stimulus = stimulus
        self.drive = drive

    def compute(self):
        """
        The function computes the motivation to perform the action associated with the variable.
        """
        self.val = self.controlled_var.get_deficit() + (self.controlled_var.get_deficit() * self.stimulus)

    def get_val(self):
        """
        The function get_val() returns the value of the motivation.
        
        @return The value of the instance variable val.
        """
        return self.val


# The class motors has two attributes, left and right, which are both floats. 
class motors:
    def __init__(self,robot):
        self.left = 0.0 # speed of left motor
        self.right = 0.0  # speed of right motor
        self.robot = robot

    def set(self, left, right):
        """
        The function takes two floats as arguments and sets the speed of the left and right motors.
        
        @param left The speed of the left motor.
        @param right The speed of the right motor.
        """
        self.left = left
        self.right = right

    def set_left(self, left):
        """
        The function takes a float as argument and sets the speed of the left motor.
        
        @param left The speed of the left motor.
        """
        self.left = left

    def set_right(self, right):
        """
        The function takes a float as argument and sets the speed of the right motor.
        
        @param right The speed of the right motor.
        """
        self.right = right

    def emergency_stop(self):
        self.left = 0.0
        self.right = 0.0
        self.drive()

    def turn_right(self):
        self.left = -0.5
        self.right = 0.5
        
    def turn_left(self):
        self.left = 0.5
        self.right = -0.5

    def backward(self):
        self.left = -0.5
        self.right = -0.5

    def stop(self):
        self.left = 0.0
        self.right = 0.0

    def forward(self):
        self.left = 1.0
        self.right = 1.0

    def drive(self):
        """
        The function takes a left and right speed as arguments and returns a new instance of the class
        """
        if(self.left != 0.0):
            left = self.left * 2400 - 1200
        else :
            left = 0
        if(self.right != 0.0):
            right = self.right * 2400 - 1200
        else :
            right = 0
        print("l : " + str(left) + " r : " + str(right))
        self.robot.send_data('D,' + str(left) + ',' + str(right))
                
    def drive_lr(self, left, right):
        if(left != 0.0):
            left =  left * 2400 - 1200
        if(right != 0.0):
            right = right * 2400 - 1200
        self.robot.send_data('D,' + str(left) + ',' + str(right))


    def update(self):
        """
        The function updates the speed of the left and right motors.
        """
        self.drive()

# The class `robot` defines the robot and its attributes
class robot:
    def __init__(self,name, port, baudrate):
        """
        A class that defines the robot.
        @brief Class used to define the robot.
        @param name the name of the robot
        """
        #robot infos
        self.name = name
        self.port = port
        self.baudrate = baudrate
    
        #motors
        self.motors = motors(self)


        #physiological variables
        self.energy = Variable("energy", 0.0, 0.8, 1.0)
        self.water = Variable("water", 0.0, 0.9, 1.0)
        self.integrity = Variable("integrity", 0.0, 0.9, 1.0)

        #sensors
        self.us = sensors("us", N_US_SENSORS, 'G', 'g', 0, 1000, 1, self)
        self.prox = sensors("prox", N_IR_SENSORS, 'N', 'n', 0, 1024, 1, self)
        self.amb = sensors("ambiant", N_IR_SENSORS, 'O', 'o', 0, 1024, 0, self)

        #behaviors
        self.eat = behavior(self.energy, motors)
        self.drink = behavior(self.water, motors)
        self.avoid = behavior(self.integrity, motors)

        #robot serial com
        self.com = cstm_serial.SerialPort(port, baudrate)



    def display(self):
        """
        The function display displays the robot's attributes.
        """
        print("----------------------------------------------------")
        print("Robot name      : " + self.name)
        print("Serial          :" + self.port + " | bps :" + str(self.baudrate))
        print("Energy          : " + "{0:0.2f}".format(self.energy.get_value()) +      " | deficit :  "    + "{0:0.2f}".format(self.energy.get_deficit()))
        print("Water           : " + "{0:0.2f}".format(self.water.get_value()) +    " | deficit :  "    + "{0:0.2f}".format(self.water.get_deficit()))
        print("Integrity       : " + "{0:0.2f}".format(self.integrity.get_value()) +   " | deficit :  "    + "{0:0.2f}".format(self.integrity.get_deficit()))
        print("----------------------------------------------------")
        print("MOTORS          : " +  "{0:0.2f}".format(self.motors.left) + " | " + "{0:0.2f}".format(self.motors.right))
        print("----------------------------------------------------")
        print("US              : ", ["{0:0.2f}".format(i) for i in self.us.val])
        print("PROX            : ", ["{0:0.2f}".format(i) for i in self.prox.val])
        print("AMBIANT LIGHT   : ", ["{0:0.2f}".format(i) for i in self.amb.val])
        print("----------------------------------------------------")

    def update(self):
        """
        The update function updates the state of the robot
        """
        self.us.update()
        self.prox.update()
        self.amb.update()
        self.motors.update()


    def decode(self, data):
        """
        A function that take data as argumeent and decode it
        first letter of sentense data is an identifier and then command is applied
        @param data, data string received from serial, data is a string with coomma separator
        @return decoded, data string decoded
        """
        decoded = data.split(",")
        return decoded
        

    def get_data(self):
        """
        The function get_data() returns the data of the robot.
        @return The data of the robot via serial port.
        """
        return self.com.read_until('\n')

    def send_data(self, data):
        """
        function that send data via serial port
        """
        self.com.write(data + '\n')

 
# It creates an object of the class `robot` and assigns it to the variable `khepera`.
khepera = robot("khepera-iv", '/dev/ttyS1', 115200)
user_input = 'e'
for i in range(1000):
    if MANUAL :
        print("z,q,s,d to controll - a to stop : ")
        #user_input = raw_input()
        if user_input == 'a':
            khepera.motors.emergency_stop()
            break
        elif user_input == 'e':
            khepera.motors.stop()
        elif user_input == 'z':
            khepera.motors.forward()
        elif user_input == 'q':
            khepera.motors.turn_left()
        elif user_input == 's':
            khepera.motors.backward()
        elif  user_input == 'd':
            khepera.motors.turn_right()
        else : 
            pass
    
    print(i)
    khepera.update()
    khepera.display()
    time.sleep(TIME_SLEEP)


# for i in range(50):
#     khepera.update()
#     #khepera.display()
#     time.sleep(TIME_SLEEP)