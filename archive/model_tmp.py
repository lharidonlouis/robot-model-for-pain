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

def invert(list):
    """
    The function invert inverts a list of values.
    and returns a float list.
    """
    l=[]
    for i in list:
        print(i)
        l.append(1.0-i)
        print(l)
    return l

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
    def __init__(self, name, var, motors, stimulus, treshold, apeti_consu):
        """        
        @param var The variable that the behavior is associated with.
        @param motors a list of motors that are associated with the variable
        """
        self.name = name
        self.associated_var = var
        self.associated_stimulus = stimulus
        self.motors = motors
        self.treshold = treshold
        self.apeti_consu = apeti_consu

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
        if(self.apeti_consu):
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
        else:
            print("----------------------------------------------------")
            print("--------------------AVOID---------------------------")
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
    def __init__(self, name, controlled_var, drive, stimulus):
        self.name = name
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
        self.variables = []
        #raw sensors for debug
        self.raw_sensors = []
        #sensors
        self.sensors = []
        #behaviors
        self.behaviors = []
        #motivation
        self.motivations = []
        #robot serial com
        self.com = cstm_serial.SerialPort(port, baudrate)

        #info to store file
        timestr = time.strftime("%Y%m%d-%H%M%S")
        #append .dat to timestr
        self.filename = "louis/res/" + timestr + ".csv"   
        file = open(self.filename, 'a+')
        file.write("time,val_energy,val_temperature,val_integrity,def_energy,def_temperature,def_integirty,cue_hunger,cue_cold,cue_danger,mot_hunger,mot_cold,mot_danger,motor_l,motor_r\n")
        file.close()
        self.iter = 0
        
    def add_variable(self, variable):
        """
        The function takes a variable as argument and adds it to the list of variables.
        @param variable The variable to add.
        """
        self.variables.append(variable)

    def add_raw_sensor(self, r_sensor):
        """
        The function takes a raw sensor as argument and adds it to the list of raw sensors.
        @param r_sensor The raw sensor to add.
        """
        self.raw_sensors.append(r_sensor)

    def add_sensor(self, sensor):
        """
        The function takes a sensor as argument and adds it to the list of sensors.
        @param sensor The sensor to add.
        """
        self.sensors.append(sensor)

    def add_behavior(self, behavior):
        """
        The function takes a behavior as argument and adds it to the list of behaviors.
        @param behavior The behavior to add.
        """
        self.behaviors.append(behavior)
    
    def add_motivation(self, motivation):
        """
        The function takes a motivation as argument and adds it to the list of motivations.
        @param motivation The motivation to add.
        """
        self.motivations.append(motivation)
    

    def get_variables(self):
        """
        The function returns the list of variables.
        """
        return self.variables
    
    def get_raw_sensors(self):
        """
        The function returns the list of raw sensors.
        """
        return self.raw_sensors

    def get_sensors(self):
        """
        The function returns the list of sensors.
        """
        return self.sensors

    def get_behaviors(self):
        """
        The function returns the list of behaviors.
        """
        return self.behaviors

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

    def get_var_by_name(self, name):
        """
        The function takes a variable name as argument and returns the variable.
        @param name The name of the variable.
        """
        for var in self.variables:
            if var.name == name:
                return var
        return None
    
    def get_raw_sensor_by_name(self, name):
        """
        The function takes a raw sensor name as argument and returns the raw sensor.
        @param name The name of the raw sensor.
        """
        for r_sensor in self.raw_sensors:
            if r_sensor.name == name:
                return r_sensor
        return None
    
    def get_sensor_by_name(self, name):
        """
        The function takes a sensor name as argument and returns the sensor.
        @param name The name of the sensor.
        """
        for sensor in self.sensors:
            if sensor.name == name:
                return sensor
        return None

    def get_behavior_by_name(self, name):
        """
        The function takes a behavior name as argument and returns the behavior.
        @param name The name of the behavior.
        """
        for behavior in self.behaviors:
            if behavior.name == name:
                return behavior
        return None

    def get_motivation_by_name(self, name):
        """
        The function takes a motivation name as argument and returns the motivation.
        @param name The name of the motivation.
        """
        for motivation in self.motivations:
            if motivation.name == name:
                return motivation
        return None

    def save(self):
        self.iter = self.iter + 1
        with open(self.filename, "a+") as file:
            file.write(str(self.iter) + ",")
            file.write("{0:0.2f}".format(self.energy.get_value()) + "," + "{0:0.2f}".format(self.temperature.get_value()) + "," + "{0:0.2f}".format(self.integrity.get_value()))
            file.write("," + "{0:0.2f}".format(self.energy.get_deficit()) + "," + "{0:0.2f}".format(self.temperature.get_deficit()) + "," + "{0:0.2f}".format(self.integrity.get_deficit()))
            file.write("," + str(mean(self.hunger.stimulus)) + "," + str(mean(self.cold.stimulus)) + "," + str(mean(self.danger.stimulus)))
            file.write("," + str(self.hunger.intensity) + "," + str(self.cold.intensity) + "," + str(self.danger.intensity))
            file.write("," + str(self.motors.left) + "," + str(self.motors.right))
            file.write('\n')


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
        print("TEMP SENSORS    : ", ["{0:0.2f}".format(i) for i in  self.inv_gnd.val])
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
        self.inv_gnd.update()

        #has the robot a shock ?
        shock = 0
        for i in range(0, len(self.prox.val)):
            if(self.prox.val[i] > 0.85):
                shock+= 1
        if shock > 1:
            self.integrity.set_value(self.integrity.get_value() - 0.01)

        #update values
        self.energy.set_value(self.energy.get_value() - 0.01)
        self.temperature.set_value(self.temperature.get_value() - 0.005)



        #update physiological variables
        for v in self.variables:
            v.update_deficit()

        #update motivations
        self.hunger.update()
        self.cold.update()
        self.danger.update()

        #update and select behaviors
        selected_mot = WTA(self.hunger, self.cold, self.danger)
        selected_mot.drive.behave()

        #motor control
        self.motors.update()

        #save data
        self.save()

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

def define_khepera():
    khepera = robot("khepera-iv", '/dev/ttyS1', 115200)
    #add variables
    khepera.add_variable(Variable("energy", 0.91, 0.9, 1.0))
    khepera.add_variable(Variable("temperature", 0.45, 0.4, 0.5))
    khepera.add_variable(Variable("integrity", 1.0, 0.95, 1.0))
    #add raw sensors
    khepera.add_raw_sensor(raw_sensors("r_us", N_US_SENSORS, 'G', 'g', khepera))
    khepera.add_raw_sensor(raw_sensors("r_ir", N_IR_SENSORS, 'N', 'n', khepera))
    khepera.get_raw_sensor_by_name("r_ir").slice(0,8)
    khepera.get_raw_sensor_by_name("r_ir").set_size(8)
    khepera.add_raw_sensor(raw_sensors("r_gnd", N_IR_SENSORS, 'N', 'n', khepera))
    khepera.get_raw_sensor_by_name("r_gnd").slice(8,12)
    khepera.get_raw_sensor_by_name("r_gnd").set_size(4)
    #add sensors 
    khepera.add_sensor(sensors("us", N_US_SENSORS, 'G', 'g', 0, 1000, 1, khepera))
    khepera.add_sensor(sensors("prox", N_IR_SENSORS, 'N', 'n', 0, 1023, 0, khepera))
    khepera.get_sensor_by_name("prox").slice(0,8)
    khepera.get_sensor_by_name("prox").set_size(8)
    khepera.add_sensor(sensors("gnd", N_IR_SENSORS, 'N', 'n', 0, 1023, 1, khepera))
    khepera.get_sensor_by_name("gnd").slice(8,12)
    khepera.get_sensor_by_name("gnd").set_size(4)
    khepera.add_sensor(sensors("inv_gnd", N_IR_SENSORS, 'N', 'n', 0, 1023, 0, khepera))
    khepera.get_sensor_by_name("inv_gnd").slice(8,12)
    khepera.get_sensor_by_name("inv_gnd").set_size(4)
    #add behaviors
    khepera.add_behavior(behavior("eat", khepera.get_var_by_name("energy"),khepera.get_motors(),khepera.get_sensor_by_name("gnd"), 0.5, 1))
    khepera.add_behavior(behavior("heat", khepera.get_var_by_name("temperature"),khepera.get_motors(),khepera.get_sensor_by_name("inv_gnd"), 0.5, 1))
    khepera.add_behavior(behavior("avoid", khepera.get_var_by_name("integrity"),khepera.get_motors(),khepera.get_sensor_by_name("prox"), 0.7, 1))
    #add motivations
    khepera.add_motivation(motivation("hunger", khepera.get_var_by_name("energy"), khepera.get_behavior_by_name("eat"), khepera.get_sensor_by_name("gnd").val))
    khepera.add_motivation(motivation("cold", khepera.get_var_by_name("temperature"), khepera.get_behavior_by_name("heat"), khepera.get_sensor_by_name("inv_gnd").val))
    khepera.add_motivation(motivation("danger", khepera.get_var_by_name("integrity"), khepera.get_behavior_by_name("avoid"), khepera.get_sensor_by_name("us").val))

    return khepera

# MAIN CODE
# ----------------------------------------------------------------------------------------------------------------------
# It creates an object of the class `robot` and assigns it to the variable `khepera`.
khepera = define_khepera()
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
        time.sleep(TIME_SLEEP)
        i=i+1
    except KeyboardInterrupt:
        khepera.motors.emergency_stop()
        print("Emergency stop")
        break
khepera.motors.emergency_stop()
# ----------------------------------------------------------------------------------------------------------------------
