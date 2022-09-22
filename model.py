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
# @section todo_doxygen_example TODO
# - Debug values.
# - Check for stimuli and drive.
#
# Copyright (c) 2022 Louis L'Haridon.  All rights reserved.

# Modules
import cstm_serial
import random
import time

# GLOBAL PARAMETERS
# ----------------------------------------------------------------------------------------------------------------------
SIMULATION = True # True if simulation, false if real values
TIME_SLEEP = 0.1 # Time between each simulation step
N_US_SENSORS = 5 # Number of UltraSonic Sensors.
N_IR_SENSORS = 12 # Number of IR Sensors.
N_NOCICEPTORS = 8 # Number of Nociceptors.
MANUAL = 0 # Manual control.
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
        print(i)
        l.append(1.0-i)
        print(l)
    
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
        self.robot = robot

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

        if not SIMULATION:
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
            left =  left * 1200
        if(right != 0.0):
            right = right * 1200
        if not SIMULATION:
            self.robot.send_data('D,' + str(left) + ',' + str(right))


    def update(self):
        """
        The function updates the speed of the left and right motors.
        """
        self.drive()

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
            self.error = abs((self.ideal - self.margin) - self.value)
        elif(self.value > (self.ideal + self.margin)):
            self.error = abs((self.ideal + self.margin) - self.value)
        else:
            self.error = 0.0

    def update_value(self):
        """
        The function update_value() updates the value of the object by adding or subtracting the step value
        """
        if self.decrease:
            self.value = self.value - self.step
        else:
            self.value = self.value + self.step

    def update(self):
        """
        The function `update` calls the functions `update_value` and `update_error` on the object `self`
        """
        self.update_value()
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
        self.size = len(self.norm_val)

    def update(self):
        """
        This function updates the value of the sensor.
        """
        if SIMULATION:
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
                        for i in range(self.size):
                            #normalized
                            if self.inv:
                                self.norm_val[i] = 1.0 - ((float(data[i+1])-self.min) / (self.max-self.min))
                            else:
                                self.norm_val[i] = ((float(data[i+1])-self.min) / (self.max-self.min))  
                            #raw              
                            self.raw_val = int(data[i+1])

#The class `Stimulus` defines a stimulus
class Stimulus:
    def  __init__(
            self, 
            name,       #type: str
            data,       #type: list[float]
            min_val,    #type:float 
            max_val,    #type: float
            inv         #type: bool
        ):
        self.name = name
        self.data = data
        self.size = len(data)
        self.min_val = min_val
        self.max_val = max_val
        self.inv = inv

    def get_data(self):
        """
        This function returns the data of the stimulus.
        
        @return The data of the stimulus.
        """
        return self.data

    def process_stimulus(self):
        """
        This function processes the stimulus.
        """
        if self.inv:
            for i in range(self.size):
                self.data[i] = 1.0 - ((self.data[i] - self.min_val) / (self.max_val - self.min_val))
        else:
            for i in range(self.size):
                self.data[i] = ((self.data[i] - self.min_val) / (self.max_val - self.min_val))
    

    def update(self):
        """
        This function updates the stimulus.
        """
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
        self.secondary_effects = [Effect] #a list of secondary effects

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


# The class `Appetititve` is an inherited class of behavior
class Appettitive(Behavior):
    def behave(self):
        """
        The function behave takes associated stimulus to determine left and right speed
        first half of associated stimulus represents left stimulus and second right stimulus
        The greater the stimulus is, the faster the opposite wheel will be
        """
        left_drive = 0.0
        right_drive = 0.0
        for i in range(len(self.associated_stimulus)/2):
            right_drive = right_drive + self.associated_stimulus[i]
            left_drive = left_drive + self.associated_stimulus[i+len(self.associated_stimulus)/2]
        left_drive = left_drive / (len(self.associated_stimulus)/2)
        right_drive = right_drive / (len(self.associated_stimulus)/2)
        left = left_drive * 2 - 0.5
        right = right_drive * 2 - 0.5
        self.motors.set(left, right)
        

# The class `Consumatory` is an inherited class of behavior
class Consumatory(Behavior):
    
    def can_consume(
        self, 
        treshold #type: float
    ):
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
        """
        The function behave update thte assoociated var and lauch consumatory animation
        """
        if self.can_consume(self.treshold):
            self.main_effect.impact()
        for e in self.secondary_effects:
            e.impact()
        self.motors.turn_left()
        time.sleep(0.2)
        self.motors.turn_right()
        time.sleep(0.2)

# The class `Reflexive` is an inherited class of behavior
class Reactive(Behavior):
    def behave(self):
        """
        The function behave takes associated stimulus to determine left and right speed
        first half represent left stimulus and second right stimulus
        The greater the stimulus will be, the faster the associated wheel will be
        and the faster the opposite wheel will go in inverted direction
        """
        left_drive = 0.0
        right_drive = 0.0
        for i in range(len(self.associated_stimulus)/2):
            left_drive = left_drive + self.associated_stimulus[i]
            right_drive = right_drive + self.associated_stimulus[i+len(self.associated_stimulus)/2]
        left_drive = left_drive / (len(self.associated_stimulus)/2)
        right_drive = right_drive / (len(self.associated_stimulus)/2)
        left = left_drive * 2 - 0.5
        right = - right_drive * 2 - 0.5
        self.motors.set(left, right)


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
    

# The class `motivation` defines a motivation and its attributes
class Motivation:
    def __init__(
            self, 
            name,           #type: str
            controlled_var, #type: Variable
            stimulus        #type: Stimulus
        ):
        self.name = name
        self.intensity = 0.0 # intensity of the motivation
        self.controlled_var = controlled_var # variable controlled by the motivation
        self.drive = Drive("increase-" + controlled_var.get_name(), True, controlled_var) #by default, increase associated variable
        self.stimulus = stimulus

    def compute(self):
        """
        The function computes the motivation to perform the action associated with the variable.
        """
        self.intensity = self.controlled_var.get_error() + (self.controlled_var.get_error() * mean(self.stimulus.get_data()))

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
        self.stimulus.update()
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


# The class `robot` defines the robot and its attributes
class Robot:
    def __init__(
            self,
            name,       #type: str 
            port,       #type: str 
            baudrate    #type: str
        ):
        """
        A class that defines the robot.
        @brief Class used to define the robot.
        """
        #robot infos
        self.name = name
        self.port = port
        self.baudrate = baudrate
        #motors
        self.motors = Motors(self)
        #physiological variables
        self.variables = [Variable] * 0
        #sensors
        self.sensors = [Sensor] * 0
        #stimuli
        self.stimuli = [Stimulus] * 0
        #behaviors
        self.behaviors = [Behavior] * 0
        #motivation
        self.motivations = [Motivation] * 0
        #robot serial com
        if not SIMULATION:
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

    def add_behavior(
            self, 
            behavior    #type: Behavior
        ):
        """
        The function takes a behavior as argument and adds it to the list of behaviors.
        @param behavior The behavior to add.
        """
        self.behaviors.append(behavior)
    
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

    def get_stimuli(self):
        """
        The function returns the list of stimuli.
        """
        return self.stimuli

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

    def get_behavior_by_name(
            self, 
            name    #type: str
        ):
        """
        The function takes a behavior name as argument and returns the behavior.
        @param name The name of the behavior.
        """
        for behavior in self.behaviors:
            if behavior.get_name() == name:
                return behavior
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


    def write_header_data(
            self, 
            filename    #type: str
        ):
        """
        This function writes the header data to the file
        
        @param filename the name of the file to write to
        
        @return The iter+1 is being returned.
        """
        with open(filename, "a") as file:
            file.write("time" +  ",")
            i = 1
            print(i)
            for v in self.variables:
                file.write("val_" + v.get_name() + ",")
            for v in self.variables:
                file.write("def_" + v.get_name() + ",")
            for s in self.stimuli:
                file.write("stim_" + s.get_name() +  ",")
            for m in self.motivations:
                file.write("mot_" + m.get_name() + ",")
            file.write("motor_left" + ",")
            file.write("motor_right")
            file.write("\n")


    def save(
            self, 
            filename,   #type: str
            iter        #type: int
        ):
        """ 
        The function saves the robot in a file.
        @param filename The name of the file.
        @return iteration
        """
        with open(filename, "a+") as file:
            file.write(str(iter) + ",")
            for v in self.variables:
                file.write(str(v.get_value()) + ",")
            for v in self.variables:
                file.write(str(v.get_error()) + ",")
            for s in self.stimuli:
                file.write(str(mean(s.get_data())) + ",")
            for m in self.motivations:
                file.write(str(m.get_intensity()) + ",")
            file.write(str(self.motors.get_left_speed()) + ",")
            file.write(str(self.motors.get_right_speed()))
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
                if v.get_value() < 0.0:
                    return False
            else:
                if v.get_value() > 1.01:
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

    def update(self):
        """
        The update function updates the state of the robot
        """
        #update sensors
        for s in self.sensors:
            s.update()
        #update physiological variables
        for v in self.variables:
            v.update()
        #update motivations
        for m in self.motivations:
            m.update()
        #select motivation
        selected_mot = self.WTA()
        #select behavior

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

############################################################################################################

def define_khepera():
    #type: (...) -> Robot
    """
    The function defines a robot named "khepera-iv" with a serial port "/dev/ttyS1" and a baud rate of
    115200. It has two variables, "energy" and "temperature", and three sensors, "us", "prox", and
    "gnd". It has three stimuli, "food", "shade", and "wall". It has two motivations, "hunger" and
    "coldness", and three behaviors, "eat", "cool-down", and "withdraw"

    @return A robot object
    """
    khepera = Robot("khepera-iv", '/dev/ttyS1', 115200)
    #add variables
    khepera.add_variable(Variable("energy", 0.95, 1.0, 0.05, True, 0.01))
    khepera.add_variable(Variable("temperature", 0.0, 0.1, 0.1, False, 0.005))
    #add sensors 
    khepera.add_sensor(Sensor("us", N_US_SENSORS, 'G', 'g', 0, 1000, 1, khepera))
    khepera.add_sensor(Sensor("prox", N_IR_SENSORS, 'N', 'n', 0, 1023, 0, khepera))
    khepera.add_sensor(Sensor("gnd", N_IR_SENSORS, 'N', 'n', 0, 1023, 1, khepera))
    khepera.get_sensor_by_name("prox").slice(0,7)
    khepera.get_sensor_by_name("prox").set_size(8)
    khepera.get_sensor_by_name("gnd").slice(8,12)
    khepera.get_sensor_by_name("gnd").set_size(4)
    #add our stimuli
    khepera.add_stimulus(Stimulus("food", khepera.get_sensor_by_name("gnd").get_norm_val(), 0.7, 0.8, False))
    khepera.add_stimulus(Stimulus("shade", khepera.get_sensor_by_name("gnd").get_norm_val(), 0.9, 1.0, False))
    khepera.add_stimulus(Stimulus("wall", khepera.get_sensor_by_name("prox").get_norm_val(), 0, 1.0, True))
    #add motivations and their drive
    print(khepera.get_stimulus_by_name("food").get_data())
    khepera.add_motivation(Motivation("hunger", khepera.get_var_by_name("energy"), khepera.get_stimulus_by_name("food"))) 
    khepera.get_motivation_by_name("hunger").set_drive(Drive("increase_energy",True, khepera.get_var_by_name("energy")))  

    khepera.add_motivation(Motivation("coldness", khepera.get_var_by_name("temperature"), khepera.get_stimulus_by_name("shade")))
    khepera.get_motivation_by_name("coldness").set_drive(Drive("decrease_temperature",True, khepera.get_var_by_name("temperature")))
    #add behaviors and their effects
    khepera.add_behavior(Behavior("eat", khepera.get_motors(), khepera.get_stimulus_by_name("food"), 0.5, True))
    khepera.get_behavior_by_name("eat").add_effect(Effect("increase_energy", khepera.get_var_by_name("energy"), False, 0.1))

    khepera.add_behavior(Behavior("cool-down", khepera.get_motors(), khepera.get_stimulus_by_name("shade"), 0.5, True))
    khepera.get_behavior_by_name("cool-down").add_effect(Effect("decrease_temperature", khepera.get_var_by_name("temperature"), True, 0.1))

    khepera.add_behavior(Behavior("withdraw", khepera.get_motors(), khepera.get_stimulus_by_name("wall"), 0.75, False))

    return khepera

def display(
        robot #type: Robot
    ):
    """
    It displays the robot's attributes
    
    @param robot the robot object
    """
    print("-------------------INFO-----------------------------")
    print("Robot name      : " + robot.name)
    print("Serial          : " + robot.port + " | bps : " + str(robot.baudrate))
    print("-------------------VAL------------------------------")
    for v in robot.variables:
        print(v.name + " : " + "{0:0.2f}".format(v.get_value()) + " | error : " + "{0:0.2f}".format(v.get_error()))
    print("-----------------RAW SENSORS------------------------")
    for s in robot.sensors:
        print(s.name + " : ",  ["{0:0.0f}".format(i) for i in s.get_raw_val()])
    print("-------------------SENSORS--------------------------")
    for s in robot.sensors:
        print(s.name + " : ",  ["{0:0.2f}".format(i) for i in s.get_norm_val()])
    print("-------------------STIMULI--------------------------")
    for s in robot.stimuli:
        print(s.name + " : ", "{0:0.2f}".format(mean(s.get_data())))
    print("-------------------MOTIVATIONS----------------------")
    for m in robot.motivations:
        print(m.name + " : " + "{0:0.2f}".format(m.get_intensity()))
    print("---------------------MOTORS-------------------------")
    print("left : " + "{0:0.2f}".format(robot.get_motors().get_left_speed()) + " | right : " + "{0:0.2f}".format(robot.get_motors().get_right_speed()))
    print("----------------------------------------------------")


# MAIN CODE
# ----------------------------------------------------------------------------------------------------------------------
# It creates an object of the class `robot` and assigns it to the variable `khepera`.
khepera = define_khepera()
#info to store file
timestr = time.strftime("%Y%m%d-%H%M%S")
#append .dat to timestr
if SIMULATION:
    filename = "test.csv"
else:
    filename = "louis/res/" + timestr + ".csv"   
khepera.write_header_data(filename)
iter = 0
user_input = 'e'
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
        khepera.update()
        #khepera.has_shock(khepera.get_var_by_name("integrity"), khepera.get_stimulus_by_name("wall"))
        display(khepera)
        iter = khepera.save(filename, iter)
        time.sleep(TIME_SLEEP)
    except KeyboardInterrupt:
        khepera.motors.emergency_stop()
        print("Emergency stop")
        break
khepera.motors.emergency_stop()
# ----------------------------------------------------------------------------------------------------------------------
