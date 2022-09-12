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
# - Behaviors.
# - Motivations.
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

# Python for Winner takes all
def WTA(a, b, c):
    if (a.intensity >= b.intensity) and (a.intensity >= c.intensity):
        wta = a
    elif (b.intensity >= a.intensity) and (b.intensity >= c.intensity):
        wta = b
    else:
        wta = c       
    return wta

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
        self.value = value
        self.min_target = min_target
        self.max_target = max_target
        self.deficit = 0.0

    def __iter__(self):
        return self

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
            self.deficit = abs(self.value - self.min_target)
        elif self.value > self.max_target :
            self.deficit = abs(self.value - self.max_target)
        else:
            self.deficit = 0.0


    def display(self):
        print("----------------------------------------------------")
        print(self.name + " : " + self.get_value())
        print("----------------------------------------------------")
    
# The class defines a raw sensor
class raw_sensors:
    def __init__(self, name, size, s_char, r_char, robot):
        self.val = [0.0] * size 
        self.name = name
        self.size = size
        self.s_char = s_char
        self.r_char = r_char
        self.robot = robot

    def set_size(self, size):
        """
        This function sets the size of the sensor.
        
        @param size The size of the sensor.
        """
        self.size = size

    def slice(self, start, end):
        """
        This function returns a slice of the sensor.
        
        @param start The start of the slice.
        @param end The end of the slice.
        @return The slice of the sensor.
        """
        self.val=self.val[start:end]
        self.size = len(self.val)

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
                        self.val[i] = float(data[i+1])


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

    def set_size(self, size):
        """
        This function sets the size of the sensor.
        
        @param size The size of the sensor.
        """
        self.size = size

    def slice(self, start, end):
        """
        This function returns a slice of the sensor.
        
        @param start The start of the slice.
        @param end The end of the slice.
        @return The slice of the sensor.
        """
        self.val=self.val[start:end]
        self.size = len(self.val)

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
    def __init__(self, var, motors, stimulus, treshold):
        """        
        @param var The variable that the behavior is associated with.
        @param motors a list of motors that are associated with the variable
        """
        self.associated_var = var
        self.associated_stimulus = stimulus
        self.motors = motors
        self.treshold = treshold

    def update_associated_var(self, val):
        """
        The function takes in a value, adds it to the value of the associated variable, and then updates the
        associated variable with the new value
        
        @param val the value to be added to the associated variable
        """
        if self.associated_var.get_value() + val > 1.0:
            self.associated_var.set_value(1.0)
        else:
            self.associated_var.set_value(self.associated_var.get_value() + val)

    def can_consume(self, treshold):
        """
        The function can_consume takes in associated stimulus and check if mean is above a treshold
        @param treshold the treshold to check if the mean is above
        @return 1 if resource can be consumed, 0 otherwise
        """
        if mean(self.associated_stimulus) > treshold:
            return 1
        else:
            return 0

    def behave(self):
        if(self.can_consume(self.treshold)):
            print("----------------------------------------------------")
            print("-------------------CONSU----------------------------")
            print("----------------------------------------------------")
            self.consumatory()
        else:
            print("----------------------------------------------------")
            print("--------------------APETI---------------------------")
            print("----------------------------------------------------")
            self.appetitive()

    def appetitive(self):
        """
        The function appettitive takes associated drive to determine left and right speed
        first half of associated drive represents left drive and second right drive
        The greater the drive is, the faster the opposite wheel will be
        """
        left_drive = 0.0
        right_drive = 0.0
        for i in range(len(self.associated_stimulus)/2):
            left_drive = left_drive + self.associated_stimulus[i]
            right_drive = right_drive + self.associated_stimulus[i+len(self.associated_stimulus)/2]
        left_drive = left_drive / (len(self.associated_stimulus)/2)
        right_drive = right_drive / (len(self.associated_stimulus)/2)
        left = left_drive * 2 - 0.5
        right = right_drive * 2 - 0.5
        self.motors.set(left, right)
        
    def consumatory(self):
        """
        The function consumatory update thte assoociated var and lauch consumatory animation
        """
        self.update_associated_var(0.15)
        self.motors.turn_left()
        time.sleep(0.2)
        self.motors.turn_right()
        time.sleep(0.2)

# The class `motivation` defines a motivation and its attributes
class motivation:
    def __init__(self, controlled_var, drive, stimulus):
        self.cue = 0.0 # cue of the motivation
        self.intensity = 0.0 # intensity of the motivation
        self.controlled_var = controlled_var
        self.drive = drive
        self.stimulus = stimulus

    def compute(self):
        """
        The function computes the motivation to perform the action associated with the variable.
        """
        self.intensity = self.controlled_var.get_deficit() + (self.controlled_var.get_deficit() * mean(self.stimulus))

    def get_intensity(self):
        """
        The function get_val() returns the value of the motivation.
        
        @return The value of the instance variable val.
        """
        return self.intensity

    def update(self):
        self.compute()

# The class motors has two attributes, left and right, which are both floats. 
class motors:
    def __init__(self,robot):
        self.left = 0.0 # speed of left motor (from -1.0 to 1.0)
        self.right = 0.0  # speed of right motor (from -1.0 to 1.0)
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
            left = self.left * 1200
        else :
            left = 0
        if(self.right != 0.0):
            right = self.right * 1200
        else :
            right = 0
        self.robot.send_data('D,' + str(left) + ',' + str(right))
                
    def drive_lr(self, left, right):
        if(left != 0.0):
            left =  left * 1200
        if(right != 0.0):
            right = right * 1200
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
        self.energy = Variable("energy", 0.91, 0.9, 1.0)
        self.temperature = Variable("temperature", 0.45, 0.4, 0.5)
        self.integrity = Variable("integrity", 1.0, 0.95, 1.0)

        #raw sensors for debug
        self.r_us = raw_sensors("r_us", N_US_SENSORS, 'G', 'g', self)
        self.r_ir = raw_sensors("r_ir", N_IR_SENSORS, 'N', 'n', self)
        self.r_ir.slice(0,8) ###get only prox sensors
        self.r_ir.set_size(8)
        self.r_gnd = raw_sensors("r_gnd", N_IR_SENSORS, 'N', 'n', self)
        self.r_gnd.slice(8,12) ###get only prox sensors
        self.r_ir.set_size(4)

        #sensors
        self.us = sensors("us", N_US_SENSORS, 'G', 'g', 0, 1000, 1, self)
        self.prox = sensors("prox", N_IR_SENSORS, 'N', 'n', 0, 1023, 0, self)
        self.prox.slice(0,8) ###get only prox sensors
        self.prox.set_size(8)
        self.gnd = sensors("ambiant", N_IR_SENSORS, 'N', 'n', 0, 1023, 1, self)
        self.gnd.slice(8,12) ###get only ground sensors
        self.gnd.set_size(4)

        #behaviors
        self.eat = behavior(self.energy, self.motors, self.gnd.val, 0.5)
        self.heat = behavior(self.temperature, self.motors, [1.0-x for x in self.gnd.val], 0.5)
        self.avoid = behavior(self.integrity, self.motors, self.prox.val ,0.7)

        #motivation
        self.hunger = motivation(self.energy, self.eat, self.gnd.val) 
        self.cold = motivation(self.temperature, self.heat, [1.0-x for x in self.gnd.val]) 
        self.danger = motivation(self.integrity, self.avoid, self.us.val) 

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
        print("Temperature     : " + "{0:0.2f}".format(self.temperature.get_value()) +    " | deficit :  "    + "{0:0.2f}".format(self.temperature.get_deficit()))
        print("Integrity       : " + "{0:0.2f}".format(self.integrity.get_value()) +   " | deficit :  "    + "{0:0.2f}".format(self.integrity.get_deficit()))
        print("----------------------------------------------------")
        print("RAW US          : ", ["{0:0.0f}".format(i) for i in self.r_us.val])
        print("RAW PROX        : ", ["{0:0.0f}".format(i) for i in self.r_ir.val])
        print("RAW GND SENSORS : ", ["{0:0.0f}".format(i) for i in self.r_gnd.val])
        print("----------------------------------------------------")
        print("US              : ", ["{0:0.2f}".format(i) for i in self.us.val])
        print("PROX            : ", ["{0:0.2f}".format(i) for i in self.prox.val])
        print("GROUND SENSORS  : ", ["{0:0.2f}".format(i) for i in self.gnd.val])
        print("----------------------------------------------------")
        print("ENERGY SENSORS  : ", ["{0:0.2f}".format(i) for i in self.gnd.val])
        print("TEMP SENSORS    : ", ["{0:0.2f}".format(i) for i in  [1.0-x for x in self.gnd.val]])
        print("----------------------------------------------------")
        print("HUNGER cue      : ", mean(self.hunger.stimulus))
        print("COLD cue        : ", mean(self.cold.stimulus))
        print("DANGER cue      : ", mean(self.danger.stimulus))
        print("----------------------------------------------------")
        print("HUNGER MOT      : ", self.hunger.intensity)
        print("COLD MOT        : ", self.cold.intensity)
        print("DANGER MOT      : ", self.danger.intensity)
        print("----------------------------------------------------")
        print("MOTORS          : " +  "{0:0.2f}".format(self.motors.left) + " | " + "{0:0.2f}".format(self.motors.right))
        print("----------------------------------------------------")

    def is_alive(self):
        """
        The function is_alive returns true if the robot is alive.
        """
        if(self.energy.get_value() > 0.0 and self.temperature.get_value() > 0.0 and self.integrity.get_value() > 0.0):
            return True
        else:
            return False

    def update(self):
        """
        The update function updates the state of the robot
        """
        #RAW update 
        self.r_us.update()
        self.r_ir.update()
        self.r_gnd.update()

        #get sensors values
        self.us.update()
        self.prox.update()
        self.gnd.update()

        #has the robot a shock ?
        shock = 0
        for i in range(0, len(self.prox.val)):
            if(self.prox.val[i] > 0.85):
                shock+= 1
        if shock > 1:
            self.integrity.set_value(self.integrity.get_value() - 0.05)

        #update values
        self.energy.set_value(self.energy.get_value() - 0.01)
        self.temperature.set_value(self.temperature.get_value() - 0.005)



        #update physiological variables
        self.energy.update_deficit()
        self.temperature.update_deficit()
        self.integrity.update_deficit()

        #update motivations
        self.hunger.update()
        self.cold.update()
        self.danger.update()

        #update and select behaviors
        selected_mot = WTA(self.hunger, self.cold, self.danger)
        selected_mot.drive.behave()

        #motor control
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

# MAIN CODE
# ----------------------------------------------------------------------------------------------------------------------
# It creates an object of the class `robot` and assigns it to the variable `khepera`.
khepera = robot("khepera-iv", '/dev/ttyS1', 115200)
user_input = 'e'
i=0
while(khepera.is_alive()):
    try:
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
        time.sleep(1)
        i=i+1
    except KeyboardInterrupt:
        khepera.motors.emergency_stop()
        print("Emergency stop")
        break
khepera.motors.emergency_stop()
# ----------------------------------------------------------------------------------------------------------------------
