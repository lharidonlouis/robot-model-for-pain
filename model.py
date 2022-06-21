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



# The physiology class contains the variables, deficits, cues, and motivations.
class physiology:
    def __init__(self):
        self.var = variables()
        self.defi = deficits()
        self.cues = cues()
        self.mot = motivations()


# The class motors has two attributes, left and right, which are both floats.
class motors:
    def __init__(self):
        self.left = 0.0 # speed of left motor
        self.right = 0.0  # speed of right motor


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
        #physiolocial variables
        self.var = variables()
        #deficits
        self.defi  = deficits()
        #cues
        self.cue = cues()
        #motivations
        self.mot  = motivations()
        
    def update_var(self):
        """
        The update_var function decreases the energy and tegument variables by 0.1 and 0.05 respectively.
        """
        self.var.energy -= 0.1
        self.var.tegument -= 0.05
    
    def update_def(self):
        """
        The function update_def() updates the values of the variables in the class deficit
        """
        self.defi.energy = self.var.ideal_energy - self.var.energy
        self.defi.integrity = self.var.ideal_integrity - self.var.integrity
        self.defi.tegument = self.var.ideal_tegument - self.var.tegument

    def update_cue(self):
        """
        The function update_cue() updates the cue object with the values of the environment
        """
        #simulation of values
        #TO DO actual perception of environment
        self.cue.energy = 0.6
        self.cue.tegument = 0.3
        self.cue.integrity = 0.1
    
    def update_mot(self):
        """
        The function takes the values of the cue and defi objects and adds them together, then multiplies
        them by the cue object's values
        """
        self.mot.energy = self.defi.energy + (self.defi.energy * self.cue.energy)
        self.mot.tegument = self.defi.tegument + (self.defi.tegument * self.cue.tegument)
        self.mot.integrity = self.defi.integrity + (self.defi.integrity * self.cue.integrity)


    def update(self):
        """
        The function `update` updates the variables, definitions, cues, and motives of the `Game` object
        """
        self.update_var()
        self.update_def()
        self.update_cue()
        self.update_mot()


 

# It creates an object of the class `robot` and assigns it to the variable `khepera`.
khepera = robot("khepera-iv")

print(khepera.name)
khepera.update()
print(khepera.mot_energy)