##
# @file model.py
#
# @brief Simple bio-inspired pain model for Khepera IV robot.
#
# @author  Louis L'Haridon
# @date    2022/07/02
# @last update    2022/09/15
# @version 0.2
#
# @section description_doxygen_example Description
# In a Two Resources Problem (TRP), the robot has to choose between two resources to maintain its viability. 
# This model is used to then, induce artifical pain and observe the robot's reaction.
#
# @section notes_doxygen_example Notes
# - This model is built originaly for Khepera-IV but is meant to be adaptable to any robots.
# - The model is meant to communicate with robot via serial port.
# - If you want to change the robot see Motors.drive() and Sensors.update()
#
# @section requirements_doxygen_example Run
# //clean folder with
# rm louis/res/*
# //fake serial with
# socat -d -d pty,raw,echo=0,link=/dev/ttyS0 pty,raw,echo=0,link=/dev/ttyS1 &
# //run the server with
# ./server &
# //run the client with
# python louis/model.py -r lower_limit_food upper_limit_food lower_limit_shade upper_limit_shade "name_of_run"   
# -d can be used for debug mode (no motor activated)
#
# @section todo_doxygen_example TODO
# - debug motor control
# - lauch experiments
#
# Copyright (c) 2022 Louis L'Haridon.  All rights reserved.

# Modules
from re import S
import cstm_serial
import random
import time
import sys
import os
import math

# GLOBAL PARAMETERS
# ----------------------------------------------------------------------------------------------------------------------
TIME_SLEEP = 0.05   #Time between each simulation step
N_US_SENSORS = 5    #Number of UltraSonic Sensors.
N_IR_SENSORS = 12   #Number of IR Sensors.
SPEED_ROBOT = 500   #Constant for speed. 1200 MAX
GAIN = 0.05        #constant for gain when consume resource
LOOS = 0.0005      #constant for loose when behave
# ----------------------------------------------------------------------------------------------------------------------


# Python program to get average of a list
def mean(
        lst # type: list
    ):
    """
    It returns the mean of a list of numbers.
    
    @param lst
    
    @return The mean of the list
    """
    if((sum(lst) != 0) and (len(lst) != 0)):
        return sum(lst)/len(lst)
    else:
        return 0

def invert(
        list # type: list
    ):
    """
    The function invert inverts a list of values.
    and returns a float list.
    """
    l=[]
    for i in list:
        l.append(1.0-i)
    
    return l

def normalize(
        list # type: list
    ):
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

# The class motors has two attributes, left and right, which are both floats. 
class Motors:
    def __init__(self, robot):
        self.left = 0.0 # speed of left motor (from -1.0 to 1.0)
        self.right = 0.0  # speed of right motor (from -1.0 to 1.0)
        self.speed = SPEED_ROBOT
        self.robot = robot

    def set_speed(self, speed):
        self.speed = speed

    def get_left_speed(self):
        """
        The function returns the speed of the left motor.
        """
        return self.left

    
    def get_right_speed(self):
        """
        The function returns the speed of the right motor.
        """
        return self.right

    def set(
            self, 
            left, # type: float
            right # type: float
        ):
        """
        The function takes two floats as arguments and sets the speed of the left and right motors.
        
        @param left The speed of the left motor -1.0 to 1.0
        @param right The speed of the right motor -1.0 to 1.0
        """
        self.left = left
        self.right = right

    def set_left(
            self, 
            left # type: float
        ):
        """
        The function takes a float as argument and sets the speed of the left motor.
        
        @param left The speed of the left motor - 1.0 to 1.0
        """
        self.left = left

    def set_right(
            self, 
            right # type: float
        ):
        """
        The function takes a float as argument and sets the speed of the right motor.
        
        @param right The speed of the right motor -1.0 to 1.0
        """
        self.right = right

    def emergency_stop(self, simulation = False):
        self.left = 0.0
        self.right = 0.0
        self.drive(simulation)

    def turn_right(self):
        self.left = -0.25
        self.right = 0.75
        
    def turn_left(self):
        self.left = 0.75
        self.right = -0.25

    def backward(self):
        self.left = -0.5
        self.right = -0.5

    def stop(self):
        self.left = 0.0
        self.right = 0.0

    def forward(self):
        self.left = 1.0
        self.right = 1.0

    def drive(self, simulation=False):
        """
        The function takes a left and right speed as arguments and returns a new instance of the class
        """
        if(self.left != 0.0):
            left = self.left * self.speed
        else :
            left = 0
        if(self.right != 0.0):
            right = self.right * self.speed
        else :
            right = 0
        if not simulation:
            self.robot.send_data('D,' + str(left) + ',' + str(right))
                
    def drive_lr(
            self, 
            left, # type: float
            right # type: float
        ):
        """
        The function takes a left and right speed as arguments and returns a new instance of the class
        @param left : float the speed of the left motor from -1.0 to 1.0
        @param right : float the speed of the right motor from -1.0 to 1.0
        """
        if(left != 0.0):
            left =  left * self.speed
        if(right != 0.0):
            right = right * self.speed
        self.robot.send_data('D,' + str(left) + ',' + str(right))

    def rage(
        self, 
        bonus_malus # type: float
    ):
        if self.left > 0 :
            self.left = self.left + self.left*bonus_malus
        else:
            self.left = self.left - self.left*bonus_malus 
        if self.right > 0 : 
            self.right = self.right + self.ri

    def update(self, simulation = False):
        """
        The function updates the speed of the left and right motors.
        """
        self.drive(simulation)

# The class variable defines a phhysiological variable
class Variable:
    def __init__(
            self, 
            name,       #type: str
            value,      #type: float
            ideal,      #type: float 
            margin,     #type: float
            decrease,   #type: bool
            step        #type: float
        ):
        self.name = name
        self.value = value
        self.ideal = ideal
        self.margin = margin
        self.decrease = decrease
        self.step = step
        self.error = 0.0

    def __iter__(self):
        return self

    def set_value(
            self, 
            value #type: float
        ):
        """
        This function takes a value and sets the value of the object to that value.
        
        @param value The value of the parameter.
        """
        self.value = value
    
    def get_name(self):
        """
        This function returns the name of the variable.
        """
        return self.name

    def get_value(self):
        """
        The function get_value() returns the value of the variable value
        
        @return The value of the instance variable value.
        """
        return self.value

    def get_error(self):
        """
        It returns the error of the country.
        
        @return The error of the object.
        """
        return self.error

    def update_error(self):
        """
        The function update_error() updates the error of the object.
        The error is computed as the difference between the ideal value and the current value with a margin of tolerance. 
        """
        if(self.value < (self.ideal - self.margin)):
            self.error = abs((self.ideal - self.margin) - self.value) / (self.ideal - self.margin)
        elif(self.value > (self.ideal + self.margin)):
            self.error = abs((self.value - (self.ideal + self.margin)) / (1.0 - self.ideal + self.margin) )
        else:
            self.error = 0.0


    def update(self):
        """
        The function `update` calls the functions `update_value` and `update_error` on the object `self`
        """
        self.update_error()

    def display(self):
        """
        The function takes a string as an argument, and returns a string.
        """
        print("----------------------------------------------------")
        print(self.name + " : " + self.get_value())
        print("----------------------------------------------------")
    
# The class defines a sensor
class Sensor:
    def __init__(
            self, 
            name,   #type: str
            size,   #type: int
            s_char, #type: str
            r_char, #type: str
            min,    #type: int
            max,    #type: int
            inv,    #type: bool
            start,  #type: int
            end,    #type: int
            robot
        ):
        self.raw_val = [0] * size 
        self.norm_val = [0.0] * size 
        self.name = name
        self.size = size
        self.s_char = s_char
        self.r_char = r_char
        self.min = min
        self.max = max
        self.inv = inv # True if the sensor is inverted (the greater the value, the smaller the data)
        self.start = start
        self.end = end
        self.robot = robot

    def get_name(self):
        """
        This function returns the name of the sensor.
        """
        return self.name

    def get_raw_val(self):
        """
        This function returns the raw value of the sensor.
        
        @return The raw value of the sensor.
        """
        return self.raw_val

    def get_norm_val(self):
        """
        This function returns the normalized value of the sensor.
        
        @return The normalized value of the sensor.
        """
        return self.norm_val

    def set_size(
            self, 
            size #type: int
        ):
        """
        This function sets the size of the sensor.
        
        @param size The size of the sensor.
        """
        self.size = size

    def slice(
            self, 
            start, #type: int 
            end    #type: int
        ):
        """
        This function returns a slice of the sensor.
        
        @param start The start of the slice.
        @param end The end of the slice.
        @return The slice of the sensor.
        """
        self.norm_val=self.norm_val[start:end]
        self.raw_val=self.raw_val[start:end]
        #self.size = len(self.norm_val)

    def update(self, simulation = False):
        """
        This function updates the value of the sensor.
        """
        if simulation:
                for i in range(len(self.norm_val)):
                    self.raw_val[i] = random.randint(self.min, self.max)
                    self.norm_val[i] = ( (float(self.raw_val[i]) - self.min) / (self.max - self.min) )
        else:
            success = 0
            while(not success):
                self.robot.send_data(self.s_char)
                data = self.robot.get_data()
                data.replace('\r\n', '')
                if(data != None):
                    data = self.robot.decode(data)
                    if(data[0] == self.r_char):
                        success=1
                        self.raw_val = [0] * self.size 
                        self.norm_val = [0.0] * self.size 
                        for i in range(self.size):
                            #normalized
                            if self.inv:
                                self.norm_val[i] = 1.0 - ((float(data[i+1])-self.min) / (self.max-self.min))
                            else:
                                self.norm_val[i] = ((float(data[i+1])-self.min) / (self.max-self.min))  
                            #raw              
                            self.raw_val[i] = int(data[i+1])
                        self.slice(self.start, self.end)

#The class `Nociceptor` defines a nociceptor
class Nociceptor:
    def __init__(        
        self,
        sensor,     #type: Sensor        
        ):
        self.val = [0.0] * sensor.size
        self.speed_val = [0.0] * sensor.size
        self.circular_val = [0.0] * sensor.size
        self.sensor = sensor  
        self.data = self.sensor.get_norm_val()[:]
        self.prev_data = self.sensor.get_norm_val()[:]

    def compute_speed_impact(self):
        #A function that that takes data actual and previous value to compute
        #the value of the nociceptor as a speed
        for i in range(len(self.data)):
            #compute dist and speed
            dist = abs(self.data[i] - self.prev_data[i])
            speed = dist/TIME_SLEEP
            #meaning of actual and previous speed to smooth data
            self.speed_val[i] = (speed + self.speed_val[i])/2

    def compute_circular_impact(self):
        #a function that takes actual and previous value to compute the circular speed
        #speed is computed for each sensor as the difference between the actual and previous value of its neighbours
        l_dist = [0.0] * len(self.data)
        r_dist = [0.0] * len(self.data)
        dist = [0.0] * len(self.data)
        #right circular speed
        for i in range(len(self.data)):
            if(i == 0):
                r_dist[i] = abs(self.data[i] - self.data[len(self.data)-1])  
            elif (i == len(self.data)-1):
                r_dist[i] = abs(self.data[i] - self.data[0])
            else:
                r_dist[i] = abs(self.data[i] - self.data[i-1])
        #left circular speed
        for i in range(len(self.data)-1,0,-1):
            if(i == len(self.data)-1):
                l_dist[i] = abs(self.data[i] - self.data[0])  
            elif (i == 0):
                l_dist[i] = abs(self.data[i] - self.data[len(self.data)-1])
            else:
                l_dist[i] = abs(self.data[i] - self.data[i+1])
        #circular speed
        for i in range(len(self.data)):
            #mean of right and left circular speed
            dist[i] = (r_dist[i] + l_dist[i])/2
            #meaning
            self.circular_val[i] = (dist[i] + self.circular_val[i] )/ 2.0
            #compute speed
            self.circular_val[i] = self.circular_val[i] * ((math.pi/6.0)*5.5)/TIME_SLEEP

    def pain_irradiation(self):
        #
        #    We induce damage irradiation using a Gaussian that propagates intensity to each nociceptor s neighbors
        #    1) Generate a 2d of size len(self.val) len(self.val)        
        #    2) for i in range(0, len(self.val)):
        #        a) array[i]=self.val
        #        b) take array[i][i] as center of gaussian and then radiates to neighbors
        #    3) for i in range(0,len(self.val))
        #        a) self.val[i] = 0
        #        b) for j in range(0,len(self.val))
        #            i) self.val[i] += array[i][j]
        #        c) self.val[i] = self.val[i]/len(self.val)
        #
        array = [0.0] * len(self.val)
        for i in range(0, len(self.val)):
            array[i] = self.val[:]
            for j in range(0, len(self.val)):
                array[i][j] = array[i][j] * math.exp(-((i-j)**2)/2.0)
        for i in range(0,len(self.val)):
            self.val[i] = 0
            for j in range(0,len(self.val)):
                self.val[i] += array[i][j]
            self.val[i] = self.val[i]/len(self.val)

    def get_val(self):
        return self.val[:]

    def update(self):
        self.prev_data = self.data[:]
        self.data = self.sensor.get_norm_val()[:]
        self.circular_val = self.circular_val[0:len(self.data)]
        self.speed_val = self.speed_val[0:len(self.data)]
        self.val = self.val[0:len(self.data)]
        self.compute_speed_impact()
        self.compute_circular_impact()
        for i in range(len(self.data)):
            self.val[i] = (self.speed_val[i] + self.circular_val[i])/2.0
        self.pain_irradiation()


#The class `Stimulus` defines a stimulus
class Stimulus:
    def  __init__(
            self, 
            name,       #type: str
            sensor,     #type: Sensor
            min_val,    #type: int 
            max_val,    #type: int
            inv         #type: bool
        ):
        self.name = name
        self.sensor = sensor
        self.size = len(sensor.get_norm_val())
        self.data = [0.0] * self.size
        if(self.sensor.inv):
            self.min_val = 1.0 - (float(min_val) / float(self.sensor.max-self.sensor.min))
            self.max_val = 1.0 - float(max_val) / float(self.sensor.max-self.sensor.min)
        else:
            self.min_val = float(min_val) / float(self.sensor.max-self.sensor.min)
            self.max_val = float(max_val) / float(self.sensor.max-self.sensor.min)
        self.inv = inv

    def get_data(self):
        """
        This function returns the data of the stimulus.
        
        @return The data of the stimulus.
        """
        return self.data

    def incentive(self, salience):
        for i in range(self.size):
            self.data[i] = max(0.0, min(1.0, self.data[i] + self.data[i]*salience))
    def process_stimulus(self):
        """
        This function processes the stimulus.
        """
        self.size = len(self.data)
        #print(str(self.name), " , ", str(self.size))
        #print(self.min_val, self.max_val)
        #print(self.data)
        if self.inv:
            for i in range(self.size):
                self.data[i] = 1.0 - ((self.data[i] - self.min_val) / (self.max_val - self.min_val))                    
        else:
            for i in range(self.size):
                self.data[i] = ((self.data[i] - self.min_val) / (self.max_val - self.min_val))
        for i in range(self.size):
            if(self.data[i] > 1.0):            
                self.data[i] = 1.0 - (1.0 - self.data[i])
                if self.data[i] >1.0:
                    self.data[i] = 0.0
                elif self.data[i]<0.0:
                    self.data[i] = 0.0
            elif self.data[i] < 0.0:
                self.data[i] = 0.0
        #print(self.data)

    def update(self):
        """
        This function updates the stimulus.
        """
        self.data = self.sensor.get_norm_val()[:]
        self.process_stimulus()

    def get_name(self):
        """
        This function returns the name of the stimulus.
        
        @return The name of the stimulus.
        """
        return self.name


# The class `Effect` defines an effect of a behavior
class Effect:
    def __init__(
            self, 
            name,       #type: str 
            var,        #type: Variable 
            decrease,   #type: bool
            step,       #type: float
        ):
        self.name = name
        self.var = var
        self.decrease = decrease
        self.step = step
    
    def get_name(self):
        """
        This function returns the name of the effect.
        
        @return The name of the effect.
        """
        return self.name

    def impact(self):
        """
        It takes a variable, a step size, and a boolean value, and then creates a function that will either
        increase or decrease the variable by the step size
        """
        if self.decrease:
            if self.var.get_value() - self.step > 0.0:
                self.var.set_value(self.var.get_value() - self.step)
            else:
                self.var.set_value(0.0)
        else:
            if self.var.get_value() + self.step < 1.0:
                self.var.set_value(self.var.get_value() + self.step)
            else:
                self.var.set_value(1.0)

# The class `Drive` defines the drive and its attributes`
class Drive:
    def __init__(
            self, 
            name,               #type: str
            increase_decrease,  #type: bool
            associated_var      #type: Variable
        ):
        self.name = name
        self.increase_decrease = increase_decrease
        self.associated_var = associated_var
    
    def get_name(self):

        """
        This function returns the name of the drive.
        
        @return The name of the drive.
        """
        return self.name


# The class `behavior` defines the behavior and its attributes
class Behavior:
    def __init__(
            self, 
            name,       #type: str
            motors,     #type: Motors
            stimulus,   #type: Stimulus
            treshold,   #type: float
        ):
        self.name = name
        self.associated_stimulus = stimulus
        self.motors = motors
        self.treshold = treshold
        self.main_effect = None #type: Effect
        self.secondary_effects = [Effect] * 0 #a list of secondary effects

    def get_main_effect(self):
        """
        This function returns the main effect of the behavior.
        
        @return The main effect of the behavior.
        """
        return self.main_effect

    def get_secondary_effects(self):
        """
        This function returns the secondary effects of the behavior.
        
        @return The secondary effects of the behavior.
        """
        return self.secondary_effects

    def get_name(self):
        """
        This function returns the name of the behavior.
        
        @return The name of the behavior.
        """
        return self.name

    def set_main_effect(
        self,
        effect #type: Effect
    ):
        """
        This function sets the main effect of the behavior.
        
        @param effect The main effect of the behavior.
        """
        self.main_effect = effect
    

    def add_secondary_effect(
            self,
            effect #type: Effect
        ):
        """
        This function adds an effect to the behavior.
        
        @param effect The effect to add.
        """
        self.secondary_effects.append(effect)

    def main_impact(self):
        self.main_effect.impact()

    def secondary_impact(self):
        for e in self.secondary_effects:
            e.impact()



# The class `Appetititve` is an inherited class of behavior
class Appettitive(Behavior):
    def can_behave(self):
        """
        This function checks if the behavior can be executed.
        
        @return True if the behavior can be executed, False otherwise.
        """
        return True

    def behave(self):
        """
        The function behave takes associated stimulus to determine left and right speed
        first half of associated stimulus represents left stimulus and second right stimulus
        The greater the stimulus is, the faster the opposite wheel will be
        """
        left_drive = 0.0
        right_drive = 0.0
        if(mean(self.associated_stimulus.data)>0.1):
            for i in range(int(len(self.associated_stimulus.data)/2)):
                right_drive = right_drive + self.associated_stimulus.data[i]
                left_drive = left_drive + self.associated_stimulus.data[i+int(len(self.associated_stimulus.data)/2)]
            left_drive = left_drive / (int(len(self.associated_stimulus.data)/2))
            right_drive = right_drive / (int(len(self.associated_stimulus.data)/2))
            left = left_drive * 2 
            right = right_drive * 2
        else:
            left = 0.5 + ((0.5 - (random.random()))/5)
            right = 0.5 + ((0.5 - (random.random()))/5)
        self.motors.set(left, right)

        if(self.main_effect != None):
            self.main_impact()
        self.secondary_impact()
        

# The class `Consumatory` is an inherited class of behavior
class Consumatory(Behavior):
    def can_behave(self):
        """
        The function can_consume takes in associated stimulus and check if mean is above a treshold
        @param treshold the treshold to check if the mean is above
        @return True if resource can be consumed, 0 otherwise
        """
        if mean(self.associated_stimulus.data) > self.treshold:
            return True
        else:
            return False

    def behave(self):
        """
        The function behave update thte assoociated var and lauch consumatory animation
        """
        if(self.main_effect != None):
            self.main_impact()
        self.secondary_impact()

        self.motors.turn_left()
        time.sleep(0.2)
        self.motors.turn_right()
        time.sleep(0.2)

# The class `Reflexive` is an inherited class of behavior
class Reactive(Behavior):
    def can_behave(self):
        """
        This function checks if the behavior can be executed.
        
        @return True if the behavior can be executed, False otherwise.
        """
        return True

    def is_excited(self):
        """
        This will be redifined in the child classes
        """
        if((mean(self.associated_stimulus.data))>self.treshold):
            return True
        else:
            for i in self.associated_stimulus.data :
                if i > 0.95:
                    return True
            return False

    def behave(self):
        """
        The function behave takes associated stimulus to determine left and right speed
        first half represent left stimulus and second right stimulus
        The greater the stimulus will be, the faster the associated wheel will be
        and the faster the opposite wheel will go in inverted direction
        """
        left_drive = 0.0
        right_drive = 0.0
        for i in range(int(len(self.associated_stimulus.data)/2)):
            left_drive = left_drive + self.associated_stimulus.data[i]
            right_drive = right_drive + self.associated_stimulus.data[i+int(len(self.associated_stimulus.data)/2)]
        left_drive = left_drive / (int(len(self.associated_stimulus.data)/2))
        right_drive = right_drive / (int(len(self.associated_stimulus.data)/2))
        left = left_drive * 2 
        right = - right_drive * 2 
        self.motors.set(left, right)

        if(self.main_effect != None):
            self.main_impact()
        self.secondary_impact()

# The class `BehavioralSystem` defines the behavioral system and its attributes
# A behavioral system contains a list of behaviors sorted in order of priority of execution
class BehavioralSystem:
    def __init__(
            self,
            name,      #type: str
            drive      #type: Drive
        ):
        self.name = name
        self.drive = drive
        self.behaviors = [Behavior] * 0 #type : list[Type[Behavior]]

    def get_drive(self):
        """
        This function returns the drive of the behavioral system.
        
        @return The drive of the behavioral system.
        """
        return self.drive

    def add_behavior(
            self,
            behavior,   #type: Behavior
        ):
        """
        This function adds a behavior to the behavioral system.
        
        @param behavior The behavior to add.
        """
        self.behaviors.append(behavior)
    
    def get_behaviors(self):
        """
        This function returns the behaviors of the behavioral system.
        
        @return The behaviors of the behavioral system.
        """
        return self.behaviors

    def get_name(self):
        """
        This function returns the name of the behavioral system.
        
        @return The name of the behavioral system.
        """
        return self.name


#The class ``Led'' dfines a led and its artibutes
class Led:
    def __init__(
        self,
        red,    #type: int (0-63)
        green,  #type: int (0-63)
        blue   #type: int (0-63)
    ):
        self.red = red
        self.green = green
        self.blue = blue

    def turn_off(self):
        red = 0
        green = 0
        blue = 0

    def set_rvb(self,red,green,blue):
        self.red = red
        self.green = green
        self.blue = blue

    def set_led(
        self,
        color   #type: str
    ):
        if color == "red":
            self.set_rvb(63,0,0)
        elif color== "green":
            self.set_rvb(0,63,0)
        elif color == "blue":
            self.set_rvb(0,0,63)
        elif color == "yellow":
            self.set_rvb(31,31,0)
        elif color == "purple":
            self.set_rvb(63,0,63)
        elif color == "cyan":
            self.set_rvb(0,63,63)
        elif color == "magenta":
            self.set_rvb(63,0,63)
        elif color == "white":
            self.set_rvb(63,63,63)
        elif color == "rose":
            self.set_rvb(63,0,31)
        elif color == "orange":
            self.set_rvb(63,31,0)

    def set_led_intensity(
        self, 
        color,      #type: str
        intensity   #type: float [0,1]
    ):
        value = int(63*intensity)
        if color == "red":
            self.set_rvb(value,0,0)
        elif color== "green":
            self.set_rvb(0,value,0)
        elif color == "blue":
            self.set_rvb(0,0,value)
        elif color == "orange":
            self.set_rvb(value, (value/2),0)

    def toStr(self):
        return str(self.red) + "," + str(self.green) + "," + str(self.blue)

# The class `motivation` defines a motivation and its attributes
class Motivation:
    def __init__(
            self, 
            name,           #type: str
            controlled_var, #type: Variable
            stimulus,        #type: Stimulus
        ):
        self.name = name
        self.intensity = 0.0 # intensity of the motivation
        self.controlled_var = controlled_var # variable controlled by the motivation
        self.drive = Drive("increase-" + controlled_var.get_name(), True, controlled_var) #by default, increase associated variable
        self.stimulus = stimulus
        self.signal_grabber = -1

    def compute(self):
        """
        The function computes the motivation to perform the action associated with the variable.
        """
        if self.signal_grabber == -1:
            self.intensity = self.controlled_var.get_error() * (1 + mean(self.stimulus.get_data()))
        else : 
            t = sorted(self.stimulus.get_data()[:], reverse=True)
            self.intensity = mean(t[:self.signal_grabber])



    def get_drive(self):
        """
        This function returns the drive of the motivation.
        
        @return The drive of the motivation.
        """
        return self.drive

    def get_intensity(self):
        """
        The function get_val() returns the value of the motivation.
        
        @return The value of the instance variable val.
        """
        return self.intensity
    
    def set_size_attention_grabber(
            self, 
            size #type: int
        ):
        self.signal_grabber = size

    def get_name(self):
        """
        This function returns the name of the motivation.
        
        @return The name of the motivation.
        """
        return self.name

    def set_stimulus(
            self, 
            stimulus #type: Stimulus
        ):
        """
        > The function `set_stimulus` takes a `Stimulus` object as an argument and assigns it to the
        `stimulus` attribute of the `Neuron` object
        
        @param stimulus The stimulus to be presented to the subject.
        """
        self.stimulus = stimulus

    def update(self):
        """
        `update` is a function that calls `compute` and `stimulus.update`
        """
        self.compute()

    def set_drive(
            self, 
            drive #type: Drive
        ):
        """
        Set the drive of the robot.
        
        @param drive The drive to be used for the backup.
        """
        self.drive = drive


class ReactiveMot(Motivation):
    def __init__(
            self, 
            name,            #type: str
            controlled_var,  #type: Variable
            stimulus,        #type: Stimulus
            ReacStim         #type: Nociceptor
        ):
        self.name = name
        self.intensity = 0.0 # intensity of the motivation
        self.controlled_var = controlled_var # variable controlled by the motivation
        self.drive = Drive("increase-" + controlled_var.get_name(), True, controlled_var) #by default, increase associated variable
        self.stimulus = stimulus
        self.signal_grabber = -1
        self.ReacStim = ReacStim
        self.intensity = 0.0 # intensity of the motivation
        self.signal_grabber = -1

    def set_ReacStim(self, ReacStim):
        self.ReacStim = ReacStim

    def compute(self):
        error = self.ReacStim.get_val()
        for e in error:
            #e = 1.0 - e
            pass
        if self.signal_grabber == -1:
            self.intensity = (mean(error) + mean(self.stimulus.get_data()))
            #self.intensity = math.log(10*mean(self.stimulus.get_data()+1)) * (1+ mean(error))
        else : 
            t = sorted(self.stimulus.get_data()[:], reverse=True)
            self.intensity = (mean(error) + mean(t[:self.signal_grabber]))
            #self.intensity = math.log(10*mean(t[:self.signal_grabber]) + 1) * (1 + (mean(error)))

        
        if self.intensity >= 1.0:
            self.intensity = 1.0

        


#The class `Hormone` defines a hormone and its attributes
class Hormone:
    def __init__(
            self,
            name,                #type: str
            nociceptor           #type: Nociceptor
        ):
        self.name = name
        self.concentration = 0.0
        self.alpha = 0.0
        self.decay_rate = 0.01
        self.release_rate = 0.0
        self.nociceptor = nociceptor

    def set_nociceptor(self, nociceptor):
        self.nociceptor = nociceptor

    def set_decay_rate(self, val):
        self.decay_rate = val

    def set_alpha(self, val):
        self.alpha = val

    def update_gland(self):
        self.release_rate = self.alpha * mean(self.nociceptor.get_val()) 

    def update(self):
        self.update_gland()
        print(self.release_rate)
        print(self.decay_rate)
        print(self.concentration + self.release_rate - self.decay_rate)
        self.concentration = max(0,min(1.0, self.concentration + self.release_rate - self.decay_rate))


# The class `robot` defines the robot and its attributes
class Robot:
    def __init__(
            self,
            name,       #type: str 
            port,       #type: str 
            baudrate,   #type: str
            simulation = False, #type: bool
        ):
        """
        A class that defines the robot.
        @brief Class used to define the robot.
        """
        #robot infos
        self.name = name
        self.port = port
        self.baudrate = baudrate
        #robot leds
        self.leds = [Led(0,0,0), Led(0,0,0), Led(0,0,0)]      #type : list[Type[Led]]
        #motors
        self.motors = Motors(self)
        #physiological variables
        self.variables = [Variable] * 0
        #sensors
        self.sensors = [Sensor] * 0
        #stimuli
        self.stimuli = [Stimulus] * 0
        #behaviors
        self.behavior_systems = [BehavioralSystem] * 0
        #motivation
        self.motivations = [Motivation] * 0
        #nociceptor
        self.nociceptor = Nociceptor
        #hormones
        self.cortisol_hormone = Hormone("cortisol", self.nociceptor)
        #internalstate
        self.wellbeing_val = 0.0
        #pain
        self.pain = 0.0

        #robot serial com
        if not simulation:
            self.com = cstm_serial.SerialPort(port, baudrate)
        
    def add_variable(
            self, 
            variable    #type: Variable
        ):
        """
        The function takes a variable as argument and adds it to the list of variables.
        @param variable The variable to add.
        """
        self.variables.append(variable)

    def add_sensor(
            self, 
            sensor      #type: Sensor
        ):
        """
        The function takes a sensor as argument and adds it to the list of sensors.
        @param sensor The sensor to add.
        """
        self.sensors.append(sensor)

    def add_behavioral_system(
            self, 
            behaviorsystem    #type: BehavioralSystem
        ):
        """
        The function takes a behavior as argument and adds it to the list of behaviors.
        @param behavior The behavior to add.
        """
        self.behavior_systems.append(behaviorsystem)

    def add_motivation(
            self, 
            motivation    #type: Motivation
        ):
        """
        The function takes a motivation as argument and adds it to the list of motivations.
        @param motivation The motivation to add.
        """
        self.motivations.append(motivation)
    
    def add_stimulus(
            self, 
            stimulus    #type: Stimulus
        ):
        """
        The function takes a stimulus as argument and adds it to the list of stimuli.
        @param stimulus The stimulus to add.
        """
        self.stimuli.append(stimulus)


    def get_variables(self):
        """
        The function returns the list of variables.
        """
        return self.variables
    
    def get_sensors(self):
        """
        The function returns the list of sensors.
        """
        return self.sensors

    def get_cortisol_hormone(self):
        """
        The function returns the list of hormones.
        """
        return self.cortisol_hormone

    def get_stimuli(self):
        """
        The function returns the list of stimuli.
        """
        return self.stimuli

    def get_behavior_systems(self):
        """
        The function returns the list of behaviors.
        """
        return self.behavior_systems

    def get_motivations(self):
        """
        The function returns the list of motivations.
        """
        return self.motivations

    def get_motors(self):
        """
        The function returns the list of motors.
        """
        return self.motors

    def get_var_by_name(
            self, 
            name    #type: str
        ):
        """
        The function takes a variable name as argument and returns the variable.
        @param name The name of the variable.
        """
        for var in self.variables:
            if var.get_name() == name:
                return var
        return None
        
    def get_sensor_by_name(
            self, 
            name    #type: str
        ):
        """
        The function takes a sensor name as argument and returns the sensor.
        @param name The name of the sensor.
        """
        for sensor in self.sensors:
            if sensor.get_name() == name:
                return sensor
        return None

    def get_stimulus_by_name(
            self, 
            name    #type: str
        ):
        """
        The function takes a stimulus name as argument and returns the stimulus.
        @param name The name of the stimulus.
        """
        for stimulus in self.stimuli:
            if stimulus.get_name() == name:
                return stimulus
        return None

    def get_behavior_systems_by_name(
            self, 
            name    #type: str
        ):
        """
        The function takes a behavior name as argument and returns the behavior.
        @param name The name of the behavior.
        """
        for bhv_s in self.behavior_systems:
            if bhv_s.get_name() == name:
                return bhv_s
        return None


    def get_motivation_by_name(
            self, 
            name    #type: str
        ):
        """
        The function takes a motivation name as argument and returns the motivation.
        @param name The name of the motivation.
        """
        for motivation in self.motivations:
            if motivation.get_name() == name:
                return motivation
        return None

    def get_left_led(self):
        #type : () -> Led
        """
        The function returns the left led.
        """
        return self.leds[0]

    def get_right_led(self):
        #type : () -> Led
        """
        The function returns the right led.
        """
        return self.leds[1]
    
    def get_back_led(self):
        #type : () -> Led
        """
        The function returns the back led.
        """
        return self.leds[2]

    def get_nociceptor(self):
        #type : () -> Nociceptor
        """
        The function returns the nociceptor.
        """
        return self.nociceptor

    def set_led(
        self, 
        led,    #type: Led
        color   #type: str
    ):
        """
        The function sets the color of a led.
        @param led The led to set.
        @param color The color to set.
        """
        led.set_led(color)
    

    def set_led_intensity(
        self,
        led,        #type: Led
        color,      #type: str
        intensity,  #type: float
    ):
        """
        The function sets the color of a led.
        @param led The led to set.
        @param color The color to set.
        @param intensity The intensity to set.
        """
        led.set_led_intensity(color, intensity)

    def set_nociceptor(        
        self,
        sensor,     #type: Sensor        
        ):
        """
        The function defines a nociceptor
        """
        self.nociceptor = Nociceptor(sensor)

    def write_header_data(
            self, 
            filename    #type: str
        ):
        """
        This function writes the header data to the file
        
        @param filename the name of the file to write to
        
        @return The iter+1 is being returned.
        """
        with open(filename, "w") as file:
            file.write("iter" +  ",")
            file.write("time" +  ",")
            for v in self.variables:
                file.write("val_" + v.get_name() + ",")
            for v in self.variables:
                file.write("def_" + v.get_name() + ",")
            for s in self.stimuli:
                file.write("stim_" + s.get_name() +  ",")
            for m in self.motivations:
                file.write("mot_" + m.get_name() + ",")
            file.write("motor_left" + ",")
            file.write("motor_right"+",")
            for s in self.sensors:
                for i in range(len(s.get_norm_val())):
                    file.write("sensor_" + s.get_name() + "_" + str(i) + ",")
            for i in range(len(self.nociceptor.speed_val)):
                file.write("speed_" + str(i) + ",")
            for i in range(len(self.nociceptor.circular_val)):
                file.write("circ_" + str(i) + ",")
            for i in range(len(self.nociceptor.val)):
                file.write("noci_" + str(i) + ",")
            file.write("noci_mean" + ",")
            file.write("gland_release_rate" + ",")
            file.write("hormonal_concentration" + ",")
            file.write("wellbeing" + ",")
            file.write("pain")
            file.write("\n")


    def save(
            self, 
            filename,   #type: str
            time,       #type: int
            iter        #type: float
        ):
        """ 
        The function saves the robot in a file.
        @param filename The name of the file.
        @return iteration
        """
        with open(filename, "a+") as file:
            file.write(str(iter) + ",")
            file.write(str(int(time)) + ",")
            for v in self.variables:
                file.write(str(v.get_value()) + ",")
            for v in self.variables:
                file.write(str(v.get_error()) + ",")
            for s in self.stimuli:
                file.write(str(mean(s.get_data())) + ",")
            for m in self.motivations:
                file.write(str(m.get_intensity()) + ",")
            file.write(str(self.motors.get_left_speed()) + ",")
            file.write(str(self.motors.get_right_speed())+",")
            for s in self.sensors:
                for i in range(len(s.get_norm_val())):
                    file.write(str(s.get_norm_val()[i]) + ",")
            for i in range(len(self.nociceptor.speed_val)):
                file.write(str(self.nociceptor.speed_val[i])+",")
            for i in range(len(self.nociceptor.circular_val)):
                file.write(str(self.nociceptor.circular_val[i])+",")
            for i in range(len(self.nociceptor.val)):
                file.write(str(self.nociceptor.val[i])+",")
            file.write(str(mean(self.nociceptor.val))+",")
            file.write(str(self.cortisol_hormone.release_rate)+",")
            file.write(str(self.cortisol_hormone.concentration)+",")
            file.write(str(self.wellbeing_val)+",")
            file.write(str(self.pain))
            file.write("\n")
        return iter+1        

    def WTA(self):
        #type : () -> Motivation
        if len(self.motivations)>0:
            max = self.motivations[0]
            for m in self.motivations:
                if m.intensity > max.intensity:
                    max = m
            return max
        else :
            return None


    def is_alive(self):
        """
        The function is_alive returns true if the robot is alive.
        """
        for v in self.variables:
            if v.decrease:
                if v.get_value() <= 0.0:
                    return False
            else:
                if v.get_value() >= 1.0:
                    return False
        return True

    def has_shock(
            self,
            var,    #type: Variable 
            stim    #type: Stimulus
        ):
        """
        The function has_shock returns true if the robot has a shock.
        It impacts choosed variable with a malus
        
        @param var the variable that is being modified
        @param stim the stimulus that the robot is currently experiencing
        
        @return The function has_shock returns true if the robot has a shock.
        """
        shock = 0 
        for i in range(0, len(stim.data)):
            if(stim.data[i] > 0.85):
                shock += 1
        if(shock > 1):
            var.set_value(var.get_value() - 0.01)
            return True
        return False

    def update_leds(self, simulation = False):
        """
        The function update_leds updates the leds of the robot and send data to update visual control
        string sent to robot is as follows : "K, lr,lg,lb,rr,rg,rb,br,bg,bb"
        """
        if not simulation:
            print("----------------------LED---------------------------")
            str = "K," + self.get_left_led().toStr() + "," + self.get_right_led().toStr() + "," + self.get_back_led().toStr()
            print(str)
            self.send_data(str)
            print("----------------------------------------------------")

    def die(self, simulation = False):
        if not simulation:
            self.get_left_led().set_led("white")
            self.get_right_led().set_led("white")
            self.get_back_led().set_led("white")
            self.update_leds(simulation)

    def wellbeing(self):
        sum = 0.0
        for v in self.variables:
            sum = sum + v.get_error()
        self.wellbeing_val = 1.0 - sum/len(self.variables)

    def update_pain(self):
        self.pain = max(0.0,min(1.0, mean(self.nociceptor.val[:]) * (1 + 0.2*(1.0-self.wellbeing_val) + self.cortisol_hormone.concentration)))


    def update(self, debug = False, simulation = False):
        """
        The update function updates the state of the robot
        """
        #update sensors
        for s in self.sensors:
            s.update(simulation)
        #update physiological variables
        for v in self.variables:
            v.update()
        #update leds for variables
        self.get_left_led().set_led_intensity("blue", self.variables[1].get_value())
        self.get_right_led().set_led_intensity("red", self.variables[0].get_value())
        #update reactive stimulus
        for s in self.stimuli:
            s.update()        
        #update motivations
        for m in self.motivations:
            m.update()
        #nociceptor update
        self.nociceptor.update()
        #gland and hormone update
        self.cortisol_hormone.update()
        #Internal state update
        self.wellbeing()
        #pain
        self.update_pain()        


        #select motivation
        selected_mot = self.WTA()
        
        print("selected_mot : " + selected_mot.get_name())
        print("selected drive " + str(selected_mot.get_drive().get_name()))
        print ("------")
        #select behavior
        #first we get througt all the behavioral systems
        for b_s in self.behavior_systems:
            #if a behavioral system corresponds to the selected motivation
            if(b_s.get_drive() == selected_mot.get_drive()):
                print("b_s selected: " + b_s.get_name())
                for b in b_s.get_behaviors():
                    if(b.can_behave()):
                        print("behavior selected: " + b.get_name())
                        print ("---")
                        b.behave()
                        if b.get_name() == "cool-down":
                            self.get_back_led().set_led("blue")
                        elif b.get_name() == "seek-shade":
                            self.get_back_led().set_led("cyan")
                        elif b.get_name() == "eat":
                            self.get_back_led().set_led("red")
                        elif b.get_name() == "seek-food":
                            self.get_back_led().set_led("magenta")
                        elif b.get_name() == "withdraw":                                
                            self.get_back_led().set_led("white")
                        else:
                            self.get_back_led().set_led("green")
                        break


        #effect on system
        for s in self.stimuli:
            s.incentive(self.cortisol_hormone.concentration)
        self.motors.set_speed(int(SPEED_ROBOT + (self.pain * 400) ))


        #motor control
        if not debug:
            self.motors.update(simulation)

        #led update
        self.update_leds(simulation)


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

############################################################################################################
########################################## MAIN CODE #######################################################
############################################################################################################

def define_khepera(simulation = False):
    #type: (...) -> Robot
    """
    We create a robot called khepera, add variables, sensors, stimuli, drives, motivations, effects, and
    behavioral systems
    
    @return A robot object
    """
    khepera = Robot("khepera-iv", '/dev/ttyS1', 115200, simulation)
    #add variables
    khepera.add_variable(Variable("energy", 0.5, 1.0, 0.05, True, 0.01))
    khepera.add_variable(Variable("temperature", 0.5, 0.0, 0.05, False, 0.01))
    khepera.add_variable(Variable("integrity", 1.0, 1.0, 0.05, True, 0))
    #add sensors 
    khepera.add_sensor(Sensor("us", N_US_SENSORS, 'G', 'g', 0, 1000, 1, 0, N_US_SENSORS, khepera))
    khepera.add_sensor(Sensor("prox", N_IR_SENSORS, 'N', 'n', 0, 1023, 0, 0, 7, khepera))
    khepera.add_sensor(Sensor("gnd", N_IR_SENSORS, 'N', 'n', 0, 1023, 1, 8, 12, khepera))
    #add our stimuli
    lower_bound_food = int(sys.argv[2]) if len(sys.argv) > 2 else 940
    upper_bound_food = int(sys.argv[3]) if len(sys.argv) > 3 else 955
    khepera.add_stimulus(Stimulus("food", khepera.get_sensor_by_name("gnd"), lower_bound_food, upper_bound_food, False))
    lower_bound_shade = int(sys.argv[4]) if len(sys.argv) > 4 else 400
    upper_bound_shade = int(sys.argv[5]) if len(sys.argv) > 5 else 555
    khepera.add_stimulus(Stimulus("shade", khepera.get_sensor_by_name("gnd"), lower_bound_shade, upper_bound_shade, False))
    khepera.add_stimulus(Stimulus("wall", khepera.get_sensor_by_name("prox"), 0, 1023, False))
    #declare drives
    dr_increase_energy = Drive("increase-energy",True, khepera.get_var_by_name("energy"))
    dr_decrease_temperature = Drive("decrease-temperature", False, khepera.get_var_by_name("temperature"))
    dr_avoid = Drive("avoid", True, khepera.get_var_by_name("integrity"))
    #add motivations and their drives
    khepera.add_motivation(Motivation("hunger", khepera.get_var_by_name("energy"), khepera.get_stimulus_by_name("food"))) 
    khepera.get_motivation_by_name("hunger").set_drive(dr_increase_energy)  
    khepera.add_motivation(Motivation("cold", khepera.get_var_by_name("temperature"), khepera.get_stimulus_by_name("shade")))
    khepera.get_motivation_by_name("cold").set_drive(dr_decrease_temperature)
    khepera.add_motivation(ReactiveMot("danger", khepera.get_var_by_name("integrity"), khepera.get_stimulus_by_name("wall"),None))
    khepera.get_motivation_by_name("danger").set_drive(dr_avoid)
    khepera.get_motivation_by_name("danger").set_size_attention_grabber(2)
    #create effects
    e_increase_energy = Effect("increase-energy", khepera.get_var_by_name("energy"), False, GAIN )
    e_decrease_temperature = Effect("decrease-temperature", khepera.get_var_by_name("temperature"), True, GAIN)
    e_decrease_energy = Effect("decrease-energy", khepera.get_var_by_name("energy"), True, LOOS)
    e_increase_temperature = Effect("increase-temperature", khepera.get_var_by_name("temperature"), False, LOOS)
    #eat and seek food behavior
    food = BehavioralSystem("food", dr_increase_energy)
    eat = Consumatory("eat", khepera.get_motors(), khepera.get_stimulus_by_name("food"), 0.3)
    eat.set_main_effect(e_increase_energy)
    eat.add_secondary_effect(e_increase_temperature)
    seek_food = Appettitive("seek-food", khepera.get_motors(), khepera.get_stimulus_by_name("food"), 0.15)
    seek_food.add_secondary_effect(e_decrease_energy)
    seek_food.add_secondary_effect(e_increase_temperature)
    food.add_behavior(eat)
    food.add_behavior(seek_food)
    #cool down and seek shade behavior
    shade = BehavioralSystem("shade", dr_decrease_temperature)
    cool_down = Consumatory("cool-down", khepera.get_motors(), khepera.get_stimulus_by_name("shade"), 0.1)
    cool_down.set_main_effect(e_decrease_temperature)
    cool_down.add_secondary_effect(e_decrease_energy)
    seek_shade = Appettitive("seek-shade", khepera.get_motors(), khepera.get_stimulus_by_name("shade"), 0.1)
    seek_shade.add_secondary_effect(e_decrease_energy)
    seek_shade.add_secondary_effect(e_increase_temperature)
    shade.add_behavior(cool_down)
    shade.add_behavior(seek_shade)
    #withdraw behavior
    avoid = BehavioralSystem("avoid", dr_avoid)
    withdraw = Reactive("withdraw", khepera.get_motors(), khepera.get_stimulus_by_name("wall"), 0.55)
    withdraw.add_secondary_effect(e_decrease_energy)
    withdraw.add_secondary_effect(e_increase_temperature)
    avoid.add_behavior(withdraw)
    #behavioral system
    khepera.add_behavioral_system(food)
    khepera.add_behavioral_system(shade)
    khepera.add_behavioral_system(avoid)
    #set nociceptor
    khepera.set_nociceptor(khepera.get_sensor_by_name("prox"))
    khepera.get_motivation_by_name("danger").set_ReacStim(khepera.get_nociceptor())
    #hormone
    khepera.get_cortisol_hormone().set_nociceptor(khepera.get_nociceptor())
    khepera.get_cortisol_hormone().set_alpha(0.025)
    khepera.get_cortisol_hormone().set_decay_rate(0.005)


    return khepera

def display(
        robot,  #type: Robot
        i,      #type: int
        t       #type: int
    ):
    """
    It displays the robot's attributes
    
    @param robot the robot object
    """
    os.system('clear')
    print("-------------------INFO-----------------------------")
    print("time : " + "{0:0.2f}".format(float(t/1000)) + "s")
    print("iter : " + str(i))
    print("Robot name      : " + robot.name)
    print("Serial          : " + robot.port + " | bps : " + str(robot.baudrate))
    print("-------------------VAL------------------------------")
    for v in robot.variables:
        print(v.name + " : " + "{0:0.2f}".format(v.get_value()) + " | error : " + "{0:0.2f}".format(v.get_error()))
    print("-----------------RAW SENSORS------------------------")
    for s in robot.sensors:
        print(s.name + " : ",  [i for i in s.get_raw_val()])
    print("-------------------SENSORS--------------------------")
    for s in robot.sensors:
        print(s.name + " : ",  ["{0:0.2f}".format(i) for i in s.get_norm_val()])
    print("-------------------STIMULI--------------------------")
    for s in robot.stimuli:
        print(s.name + " : ", "{0:0.2f}".format(mean(s.get_data())), " " , ["{0:0.2f}".format(i) for i in s.get_data()])
    print("--------------------NOCICEPTOR----------------------")
    print("speed      : ", ["{0:0.2f}".format(i) for i in robot.nociceptor.speed_val])
    print("circular   : ", ["{0:0.2f}".format(i) for i in robot.nociceptor.circular_val])
    print("nociceptor : ", ["{0:0.2f}".format(i) for i in robot.nociceptor.val])
    print("---------------------cortisol-------------------------")
    print("nociceptor mean      : ", "{0:0.2f}".format(mean(robot.nociceptor.val[:])))
    print("gland release rate   : ", "{0:0.2f}".format(robot.cortisol_hormone.release_rate))
    print("hormone concetration : ", "{0:0.2f}".format(robot.cortisol_hormone.concentration))
    print("---------------------PAIN---------------------------")
    print("Pain : ", "{0:0.2f}".format(robot.pain))
    print("-------------------MOTIVATIONS----------------------")
    for m in robot.motivations:
        print(m.name + " : " + "{0:0.2f}".format(m.get_intensity()))
    print("---------------------MOTORS-------------------------")
    print("left : " + "{0:0.2f}".format(robot.get_motors().get_left_speed()) + " | right : " + "{0:0.2f}".format(robot.get_motors().get_right_speed()))
    print("----------------------------------------------------")
    print("")


# MAIN CODE
# ----------------------------------------------------------------------------------------------------------------------
if not sys.argv[1] or sys.argv[1] == "-h":
    print("usage : model.py -[option] [lower_bound_food] [upper_bound_food] [lower_bound_shade] [upper_bound_shade] [name_of_file (without extension)]")
    print("options :")
    print("\t-r: run")
    print("\t-d: debug")
    print("\t-s: simulation")
    print("\t-m : manual")
    print("\t-h : help")
    print("values :")
    print("\tlower_bound_food : lower bound of the food stimulus - def 940")
    print("\tupper_bound_food : upper bound of the food stimulus - def 955")
    print("\tlower_bound_shade : lower bound of the shade stimulus - def 450")
    print("\tupper_bound_shade : upper bound of the shade stimulus - def 550")
    print("\tname_of_file : name of the file where the data will be saved - def data.csv")
    print("example : ")
    print('\tmodel.py -r 940 955 450 550 "expriment_1"')
    exit(0)
elif ((sys.argv[1] == "-r") or (sys.argv[1] == "-s") or (sys.argv[1] == '-d') or (sys.argv[1] == '-m')):
    #check if this is a simulation or a debug mode
    debug = False
    simulation = False
    if sys.argv[1] == "-d":
        debug = True
    elif sys.argv[1] == "-s":
        simulation = True

    # It creates an object of the class `robot` and assigns it to the variable `khepera`.
    khepera = define_khepera(simulation)

    #info to store data
    if sys.argv[1] == "-r":
        filename = "louis/res/"+sys.argv[6] + ".csv"  if len(sys.argv) > 6 else "louis/res/data.csv"
    else:
        filename =  sys.argv[6] + ".csv"  if len(sys.argv) > 6 else "data_analysis/data.csv"

    #manual control
    if sys.argv[1] == "-m":
        user_input = 'e'
        while(khepera.is_alive()):
            try:
                print("z,q,s,d to controll - a to stop : ")
                user_input = raw_input()
                if user_input == 'a':
                    khepera.motors.emergency_stop()
                    break
                elif user_input == 'e':
                    khepera.motors.stop()
                elif user_input == 'z':
                    khepera.motors.forward()
                elif user_input == 'q':
                    khepera.motors.turn_right()
                elif user_input == 's':
                    khepera.motors.backward()
                elif  user_input == 'd':
                    khepera.motors.turn_left()
                else : 
                    pass
                khepera.motors.update(False)
                time.sleep(TIME_SLEEP)
            except KeyboardInterrupt:
                khepera.motors.emergency_stop()
                print("Emergency stop")
                break
    #run, debug or simulation mode
    elif sys.argv[1] == "-r" or sys.argv[1] == "-s" or sys.argv[1] == "-d":
        #if not simulation wait 3s to unplug robot
        if sys.argv[1] == "-r":
            time.sleep(1)
        #get start time
        ts = float(time.time() * 1000)
        iter = 0
        #while robot is alive, loop
        while(khepera.is_alive()):
            #catch keyboard interruption
            try:
                #update
                khepera.update(debug, simulation)
                #compute time and iteration
                time_since_start = float(time.time() * 1000) - ts
                if iter == 0 :
                    khepera.write_header_data(filename)
                iter = khepera.save(filename, time_since_start, iter)
                #display
                display(khepera, iter, time_since_start)
                #wait until next iteration
                time.sleep(TIME_SLEEP)
            except KeyboardInterrupt:
                khepera.motors.emergency_stop(simulation)
                print("Emergency stop")
                break
        #end of run
        khepera.motors.emergency_stop(simulation)
        print("robot is dead")
        khepera.die(simulation)    
else:
    print("error : unknown option")
    print("python3 model.py -h for help")
    exit(0)
# ----------------------------------------------------------------------------------------------------------------------