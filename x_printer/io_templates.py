from abc import ABC, abstractmethod
import pandas as pd 
import numpy as np 
import random

from .spaces import * 

# Abstract class for defining different types of input files
class Input_Template(ABC): 
    # Load txt-based input file and parameter definition
    @abstractmethod
    def __init__(self): 
        pass  
    # Read in parameter
    @abstractmethod
    def instanciate(self):
        pass  
    # 
    @abstractmethod
    def save(self):
        pass  

# Text-input file reader 
class Txt_Wrapper(Input_Template): 
    
    # Read parameter files (definition and template) and extract key values
    def __init__(self, text_input_path): 

        # Read the parameterized input file
        with open(text_input_path, "r") as file: 
            self.template = str(file.read())

    # Make instance of parameter tempalte and populate with values (for each parameter in df)
    def instanciate(self, df_params, save_path=None):

        # Make new instance
        [num_var_combinations, _] = np.shape(df_params)
        
        var_names = df_params.columns.tolist() 

        instances = []
        for i in range(num_var_combinations): 

            # Make new instance
            instance = self.template

            # Replace instance text
            for _, var in enumerate(var_names):
                value = df_params.loc[i][var]  
                instance = instance.replace(str(var),str(value))
            
            # Save if intended
            if save_path: 
                self.save(instance, save_path)

            instances.append(instance)
            
        return instances 

    # Save file
    def save(self, instance, save_path):
        
        # write input parameters
        with open(save_path, "w") as file: 
            file.write(str(instance)) 

# class to contain a set experiment input files
class Input_Capsule(): 
    def __init__(self, num_experiments, template_path, variable_definition_path, output_path=None): 

        # Read the parameterized input file 
        # TODO: Detect the file type and change the io-wrapper accordingly
        self.text_wrapper    = Txt_Wrapper(template_path)

        # Define parameter space from which to sample 
        self.var_space       = Variable_Space(variable_definition_path = variable_definition_path)

        # Sample parameter variations from parameter space and make set of input files
        vars            = self.var_space.sample(num=num_experiments)
        self.input_list = self.text_wrapper.instanciate(vars, output_path)

    def save(self, instance_num, save_path):
        # Write input parameters
        # TODO: Make sure the approprite save function is working
        self.text_wrapper.save(self.input_list[instance_num], save_path)


# class to contain a set experiment input files
# TODO: Test this 
class DOE_Capsule(): 
    def __init__(self, num_experiments, var_def, output_path=None): 

        # Define parameter space from which to sample 
        self.var_space = Variable_Space(var_def)

        # Sample parameter variations from parameter space and make set of input files
        self.var_sets = self.var_space.sample(num=num_experiments)

        # Generate DOE in the appropriate format using var
        self.experiments = [] 
        for var_set in self.var_sets:
            var_def_instance = var_def 
            for var_name, var_instance in var_set: 
                var_def_instance[var_name].instance = var_instance
            self.experiments.append(var_def_instance)

    def save(self, instance_num, save_path):
        # Write input parameters
        self.vars.to_csv(output_path+"\doe.csv")






