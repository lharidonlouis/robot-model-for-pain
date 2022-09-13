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
import cstm_serial
import time

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
def mean(lst : list):
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

def normalize(list : list):
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
        self.robot = Robot(robot)

    def set(self, left : float, right : float):
        """
        The function takes two floats as arguments and sets the speed of the left and right motors.
        
        @param left The speed of the left motor -1.0 to 1.0
        @param right The speed of the right motor -1.0 to 1.0
        """
        self.left = left
        self.right = right

    def set_left(self, left :float):
        """
        The function takes a float as argument and sets the speed of the left motor.
        
        @param left The speed of the left motor - 1.0 to 1.0
        """
        self.left = left

    def set_right(self, right : float):
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
        self.robot.send_data('D,' + str(left) + ',' + str(right))
                
    def drive_lr(self, left : float, right : float):
        """
        The function takes a left and right speed as arguments and returns a new instance of the class
        @param left : float the speed of the left motor from -1.0 to 1.0
        @param right : float the speed of the right motor from -1.0 to 1.0
        """
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

# The class variable defines a phhysiological variable
class Variable:
    def __init__(self, name : str, value : float, ideal : float, margin : float, decrease : bool, step : float):
        self.name = name
        self.value = value
        self.ideal = ideal
        self.margin = margin
        self.decrease = decrease
        self.step = step
        self.deficit = 0.0

    def __iter__(self):
        return self

    def set_value(self, value : float):
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

    def get_deficit(self):
        """
        It returns the deficit of the country.
        
        @return The deficit of the object.
        """
        return self.deficit

    def update_deficit(self):
        """
        The function update_deficit() updates the deficit of the object.
        The deficit is computed as the difference between the ideal value and the current value with a margin of tolerance. 
        """
        if(self.value < (self.ideal - self.margin)):
            self.deficit = abs((self.ideal - self.margin) - self.value)
        elif(self.value > (self.ideal + self.margin)):
            self.deficit = abs((self.ideal + self.margin) - self.value)
        else:
            self.deficit = 0.0

    def update_value(self):
        if self.decrease:
            self.value = self.value - self.step
        else:
            self.value = self.value + self.step

    def update(self):
        self.update_value()
        self.update_deficit()

    def display(self):
        print("----------------------------------------------------")
        print(self.name + " : " + self.get_value())
        print("----------------------------------------------------")
    
# The class defines a sensor
class Sensor:
    def __init__(self, name : str , size : int, s_char : str, r_char : str, min : int, max : int, inv : bool, robot):
        self.raw_val = [0] * size 
        self.norm_val = [0.0] * size 
        self.name = name
        self.size = size
        self.s_char = s_char
        self.r_char = r_char
        self.min = min
        self.max = max
        self.inv = inv # True if the sensor is inverted (the greater the value, the smaller the data)
        self.robot = Robot(robot)

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

    def set_size(self, size : int):
        """
        This function sets the size of the sensor.
        
        @param size The size of the sensor.
        """
        self.size = size

    def slice(self, start : int, end : int):
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
    def  __init__(self, name : str, data : float):
        self.name = name
        self.data = data
        self.size = len(data)





# The class `behavior` defines the behavior and its attributes
class Behavior:
    def __init__(self, name : str, var : Variable, motors : Motors, stimulus : Stimulus, treshold : float, apeti_consu : bool):
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

    def update_associated_var(self, val : float):
        """
        The function takes in a value, adds it to the value of the associated variable, and then updates the
        associated variable with the new value
        
        @param val the value to be added to the associated variable
        """
        if self.associated_var.get_value() + val > 1.0:
            self.associated_var.set_value(1.0)
        else:
            self.associated_var.set_value(self.associated_var.get_value() + val)

    def can_consume(self, treshold : float):
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
        If the bhv is seek_consume, it will consume if it can, otherwise it will be appetitive. If the agent
        is not seek_consume, it will be reflexive
        """
        if(self.apeti_consu):
            if(self.can_consume(self.treshold)):
                print("-------------------CONSU----------------------------")
                self.consumatory()
            else:
                print("--------------------APETI---------------------------")
                self.appetitive()
        else:
            print("--------------------REFLEX---------------------------")
            self.reflex()

    def appetitive(self):
        """
        The function appettitive takes associated stimulus to determine left and right speed
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

    def reflex(self):
        """
        The function reflex takes associated stimulus to determine left and right speed
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
        
    def consumatory(self):
        """
        The function consumatory update thte assoociated var and lauch consumatory animation
        """
        self.update_associated_var(0.15)
        self.motors.turn_left()
        time.sleep(0.2)
        self.motors.turn_right()
        time.sleep(0.2)

# The class `Drive` defines the drive and its attributes`
class Drive:
    def __init__(self, name : str, increase_decrease : bool, associated_var : Variable):
        self.name = name
        self.increase_decrease = increase_decrease
        self.associated_var = associated_var
    

# The class `motivation` defines a motivation and its attributes
class Motivation:
    def __init__(self, name : str, controlled_var: Variable, stimulus : Stimulus):
        self.name = name
        self.intensity = 0.0 # intensity of the motivation
        self.controlled_var = controlled_var
        self.drive = Drive("increase-"+controlled_var.get_name(), True, controlled_var) #by default, increase associated variable
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

    def set_drive(self, drive : Drive):
        self.drive = drive


# The class `robot` defines the robot and its attributes
class Robot:
    def __init__(self,name : str, port : str, baudrate : str):
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
        self.motors = Motors(self)
        #physiological variables
        self.variables = [Variable]
        #sensors
        self.sensors = [Sensor]
        #behaviors
        self.behaviors = [Behavior]
        #motivation
        self.motivations = [Motivation]
        #robot serial com
        self.com = cstm_serial.SerialPort(port, baudrate)

        #info to store file
        timestr = time.strftime("%Y%m%d-%H%M%S")
        #append .dat to timestr
        self.filename = "louis/res/" + timestr + ".csv"   
        file = open(self.filename, 'a+')
        file.write(
            "time,val_energy,val_temperature,val_integrity,def_energy,def_temperature,def_integirty," + 
            "cue_hunger,cue_cold,cue_danger,mot_hunger,mot_cold,mot_danger,motor_l,motor_r\n"
        )
        file.close()
        self.iter = 0
        
    def add_variable(self, variable : Variable):
        """
        The function takes a variable as argument and adds it to the list of variables.
        @param variable The variable to add.
        """
        self.variables.append(variable)

    def add_sensor(self, sensor : Sensor):
        """
        The function takes a sensor as argument and adds it to the list of sensors.
        @param sensor The sensor to add.
        """
        self.sensors.append(sensor)

    def add_behavior(self, behavior : Behavior):
        """
        The function takes a behavior as argument and adds it to the list of behaviors.
        @param behavior The behavior to add.
        """
        self.behaviors.append(behavior)
    
    def add_motivation(self, motivation : Motivation):
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

    def get_var_by_name(self, name : str):
        """
        The function takes a variable name as argument and returns the variable.
        @param name The name of the variable.
        """
        for var in self.variables:
            if var.name == name:
                return var
        return None
    
    def get_raw_sensor_by_name(self, name : str):
        """
        The function takes a raw sensor name as argument and returns the raw sensor.
        @param name The name of the raw sensor.
        """
        for r_sensor in self.raw_sensors:
            if r_sensor.name == name:
                return r_sensor
        return None
    
    def get_sensor_by_name(self, name : str):
        """
        The function takes a sensor name as argument and returns the sensor.
        @param name The name of the sensor.
        """
        for sensor in self.sensors:
            if sensor.name == name:
                return sensor
        return None

    def get_behavior_by_name(self, name : str):
        """
        The function takes a behavior name as argument and returns the behavior.
        @param name The name of the behavior.
        """
        for behavior in self.behaviors:
            if behavior.name == name:
                return behavior
        return None

    def get_motivation_by_name(self, name : str):
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
            file.write(
                "{0:0.2f}".format(self.energy.get_value()) + "," + 
                "{0:0.2f}".format(self.temperature.get_value()) + "," + "{0:0.2f}".format(self.integrity.get_value())
            )                
            file.write(
                "," + "{0:0.2f}".format(self.energy.get_deficit()) + "," + 
                "{0:0.2f}".format(self.temperature.get_deficit()) + "," + "{0:0.2f}".format(self.integrity.get_deficit())
            )
            file.write("," + str(mean(self.hunger.stimulus)) + "," + str(mean(self.cold.stimulus)) + "," + str(mean(self.danger.stimulus)))
            file.write("," + str(self.hunger.intensity) + "," + str(self.cold.intensity) + "," + str(self.danger.intensity))
            file.write("," + str(self.motors.left) + "," + str(self.motors.right))
            file.write('\n')

    def WTA(self) -> Motivation:
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
        if(self.energy.get_value() > 0.0 and self.temperature.get_value() > 0.0 and self.integrity.get_value() > 0.0):
            return True
        else:
            return False

    def update(self):
        """
        The update function updates the state of the robot
        """
        #has the robot a shock ?
        # shock = 0
        # for i in range(0, len(self.prox.val)):
        #     if(self.prox.val[i] > 0.85):
        #         shock+= 1
        # if shock > 1:
        #     self.integrity.set_value(self.integrity.get_value() - 0.01)

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
    khepera = Robot("khepera-iv", '/dev/ttyS1', 115200)
    #add variables
    khepera.add_variable(Variable("energy", 0.95, 1.0, 0.05, True, 0.01))
    khepera.add_variable(Variable("temperature", 1.0, 1.0, 0.1, False, 0.005))
    #add sensors 
    khepera.add_sensor(Sensor("us", N_US_SENSORS, 'G', 'g', 0, 1000, 1, khepera))
    khepera.add_sensor(Sensor("prox", N_IR_SENSORS, 'N', 'n', 0, 1023, 0, khepera))
    khepera.get_sensor_by_name("prox").slice(0,8)
    khepera.get_sensor_by_name("prox").set_size(8)
    khepera.add_sensor(Sensor("gnd", N_IR_SENSORS, 'N', 'n', 0, 1023, 1, khepera))
    khepera.get_sensor_by_name("gnd").slice(8,12)
    khepera.get_sensor_by_name("gnd").set_size(4)
    #compute our stimuli
    food = Stimulus("food", khepera.get_sensor_by_name("gnd"))
    shade = Stimulus("shade", khepera.get_sensor_by_name("gnd"))
    wall = Stimulus("wall", khepera.get_sensor_by_name("prox"))
    #add motivations and their drive
    khepera.add_motivation(Motivation("hunger", khepera.get_var_by_name("energy"), khepera.get_sensor_by_name("gnd").norm_val)) #hunger
    khepera.get_motivation_by_name("increase_energy").set_drive(Drive("increase_energy",True, khepera.get_var_by_name("energy")))    
    khepera.add_motivation(Motivation("coldness", khepera.get_var_by_name("temperature"), khepera.get_sensor_by_name("inv_gnd").norm_val))
    khepera.get_motivation_by_name("coldness").set_drive(Drive("decrease_temperature",True, khepera.get_var_by_name("temperature")))

    #add behaviors
    khepera.add_behavior(Behavior("eat", khepera.get_var_by_name("energy"),khepera.get_motors(),khepera.get_sensor_by_name("gnd"), 0.5, True))
    khepera.add_behavior(Behavior("cool-down", khepera.get_var_by_name("temperature"),khepera.get_motors(),khepera.get_sensor_by_name("gnd"), 0.5, True))
    khepera.add_behavior(Behavior("withdraw", khepera.get_var_by_name("integrity"),khepera.get_motors(),khepera.get_sensor_by_name("prox"), 0.7, False))

    return khepera

def display(robot : Robot):
    """
    The function display displays the robot's attributes.
    """
    print("----------------------------------------------------")
    print("Robot name      : " + robot.name)
    print("Serial          :" + robot.port + " | bps :" + str(robot.baudrate))
    print("----------------------------------------------------")
    print("Energy          : " + "{0:0.2f}".format(robot.get_var_by_name("energy").get_value()) +      
        " | deficit :  "    + "{0:0.2f}".format(robot.get_var_by_name("energy").get_deficit()))
    print("Temperature     :" + "{0:0.2f}".format(robot.get_var_by_name("temperature").get_value()) +      
        " | deficit :  "    + "{0:0.2f}".format(robot.get_var_by_name("temperature").get_deficit()))
    print("----------------------------------------------------")
    print("RAW US          : ", ["{0:0.0f}".format(i) for i in robot.get_sensor_by_name("us").raw_val])
    print("RAW PROX        : ", ["{0:0.0f}".format(i) for i in robot.get_sensor_by_name("prox").raw_val])
    print("RAW GND SENSORS : ", ["{0:0.0f}".format(i) for i in robot.get_sensor_by_name("gnd").raw_val])
    print("----------------------------------------------------")
    print("US              : ", ["{0:0.2f}".format(i) for i in robot.get_sensor_by_name("us").norm_val])
    print("PROX            : ", ["{0:0.2f}".format(i) for i in robot.get_sensor_by_name("prox").norm_val])
    print("GROUND SENSORS  : ", ["{0:0.2f}".format(i) for i in robot.get_sensor_by_name("gnd").norm_val])
    print("----------------------------------------------------")
    print("ENERGY SENSORS  : ", ["{0:0.2f}".format(i) for i in robot.gnd.val])
    print("TEMP SENSORS    : ", ["{0:0.2f}".format(i) for i in  robot.inv_gnd.val])
    print("----------------------------------------------------")
    print("HUNGER cue      : ", mean(robot.hunger.stimulus))
    print("COLD cue        : ", mean(robot.cold.stimulus))
    print("DANGER cue      : ", mean(robot.danger.stimulus))
    print("----------------------------------------------------")
    print("HUNGER MOT      : ", robot.hunger.intensity)
    print("COLD MOT        : ", robot.cold.intensity)
    print("DANGER MOT      : ", robot.danger.intensity)
    print("----------------------------------------------------")
    print("MOTORS          : " +  "{0:0.2f}".format(robot.motors.left) + " | " + "{0:0.2f}".format(robot.motors.right))
    print("----------------------------------------------------")


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
