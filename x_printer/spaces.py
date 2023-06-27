import pandas as pd 
import numpy as np 
import random

# Helper function to enable dot-indexing for dicts 
class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

# Class with common variable definition (of a dimension or a set)
class Var(dotdict): 
    def __init__(self, _name=None, _type=None, _format=None, _values=None, _default=None, _precision=None, _conditional_var=None, _condition_type=None, _condition_def=None, **kwargs): 
        self.instance  = _instance

        self.name      = _name 
        self.type      = _type
        self.format    = _format
        self.vals      = _values
        self.precision = _precision 

        self.default  = _default  
        self.instance = _default

        self.conditional_var = _conditional_var 
        self.condition_type  = _condition_type  
        self.condition_def   = _condition_def   

    def set(self, value):
        # TODO: Add checks for valid parameter entry
        self.instance = value

        return None

# Container class for all variables (with dot-indexible attributes according to variable name)
class Vars(dotdict): 
    def __init__(self, vars):
        super().__init__()
        for var in vars: 
            self[var.name] = var
        self.kwargs = {} 
        return None 

# Class to read variable definition, verify parameter values, and resolve dependencies
class Variable_Space(): 
    def __init__(self, vars_def = None, variable_definition_path = None):

        if vars_def and not variable_definition_path: 
            self.__init_from_vars__(vars_def)

        elif variable_definition_path and not vars_def: 
            self.__init_from_csv__(variable_definition_path)
        else: 
            print("Please define either vars_def or variable_definition_path, not both.")

    def __init_from_csv__(self, variable_definition_path):

        self.var_def         = pd.read_csv(variable_definition_path) 
        self.names           = self.var_def["var"].to_list()
        self.var_types       = self.var_def["var_type"].to_list()
        self.conditioned_var = self.var_def["conditional_var"].to_list()
        self.condition_type  = self.var_def["condition_type"].to_list()

        self.var_vals  = []
        for i in range(len(self.names)): 

            # Read and reformat parameter values 
            if self.var_def["var_format"][i] == "RANGE": 
                precision      = int(self.var_def["precision"][i]); 
                start_inc_stop = self.var_def["var_def"][i].split(";"); 

                start = round(float(start_inc_stop[0]), precision)
                inc   = round(float(start_inc_stop[1]), precision)
                stop  = round(float(start_inc_stop[2]), precision)

                #self.var_def["var_def"][i] = list(np.linspace(start, stop, int((stop-start + inc)/inc)))
                vals = [start + inc*i for i in range(int(np.floor((stop-start)/inc))+1)]
                if vals[len(vals)-1] != stop: 
                    vals.append(stop)
                self.var_def.at[i,'var_def'] = vals
                
            elif self.var_def["var_format"][i] == "VALUES":
                valList = self.var_def["var_def"][i].split(";")
                if self.var_def["var_type"][i] == "float": 
                    valList = [float(valList[j]) for j in range(len(valList))]
                self.var_def.at[i,'var_def'] = valList

    def __init_from_vars__(self, vars_def):

        self.var_def         = pd.DataFrane(columns = {"var","var_type","conditional_var","condition_type",""}) 
        
        self.names           = self.var_def["var"].to_list()
        self.var_types       = self.var_def["var_type"].to_list()
        self.conditioned_var = self.var_def["conditional_var"].to_list()
        self.condition_type  = self.var_def["condition_type"].to_list()

        self.var_def         = vars_def
        self.names           = vars_def.keys()

        #self.var_types       = self.var_def["var_type"].to_list()
        #self.conditioned_var = self.var_def["conditional_var"].to_list()
        #self.condition_type  = self.var_def["condition_type"].to_list()

        self.var_vals  = []
        for i in range(len(self.names)): 

            # Read parameter values 
            if self.var_def["var_format"][i] == "RANGE": 
                precision      = int(self.var_def["precision"][i]); 
                start_inc_stop = self.var_def["var_def"][i].split(";"); 

                start = round(float(start_inc_stop[0]), precision)
                inc   = round(float(start_inc_stop[1]), precision)
                stop  = round(float(start_inc_stop[2]), precision)

                #self.var_def["var_def"][i] = list(np.linspace(start, stop, int((stop-start + inc)/inc)))
                vals = [start + inc*i for i in range(int(np.floor((stop-start)/inc))+1)]
                if vals[len(vals)-1] != stop: 
                    vals.append(stop)
                self.var_def.at[i,'var_def'] = vals
                
            elif self.var_def["var_format"][i] == "VALUES":
                valList = self.var_def["var_def"][i].split(";")
                if self.var_def["var_type"][i] == "float": 
                    valList = [float(valList[j]) for j in range(len(valList))]
                self.var_def.at[i,'var_def'] = valList


    # Get parameter names
    def names(self): 
        return self.names

    def check_and_sample(val, start, stop, inc): 
        if val < start or val > stop: 
            val = round(random.sample(np.linspace(start, stop, int((stop-start)/inc)),1)[0],4)
        return val, 1

    def __sample_list(self, sample_list, s_type): 
        if s_type == "random": 
            return random.sample(sample_list, 1)[0] 
        else: 
            print("Sample type '{}' not an option. Returning random sample... ".format(s_type))
            return random.sample(sample_list, 1)[0]

    # Get the minimum value of a given parameter
    def sample(self, num=1, s_type="random"): 
        samples = []

        for i in range(num): 
            got_all_params = False 
            vid = 0
            sample = {}
            while not got_all_params: 
                
                var                 = self.names[vid]
                conditional_var     = self.conditioned_var[vid]
                need_condition      = not isinstance(conditional_var, type(np.nan))
                condition_in_sample = conditional_var in list(sample.keys())

                if var not in list(sample.keys()) and (not need_condition or condition_in_sample): 

                    var_def_subset = self.var_def[self.var_def["var"] == var]

                    if not need_condition: 
                        sample[var] = self.__sample_list(var_def_subset["var_def"].tolist()[0],s_type)
                       
                    else: 
                        condition = var_def_subset["conditional_var"].tolist()[0] # Assumes only one condition
                        cond_type = var_def_subset["condition_type"].tolist()[0]  
                        cond_val  = sample[condition] 
                        
                        if cond_type == "=": 
                            var_def_subset = var_def_subset[var_def_subset["condition_def"] == cond_val]
                        else: 
                            print("'{}' is not a valid option for 'condition_type' Only '=' is valid at this time.".format(cond_type))
                        
                        # There should only be one row in this df
                        [rows, _] = np.shape(var_def_subset) 
                        if rows == 1: 
                            sample[var] = self.__sample_list(var_def_subset["var_def"].tolist()[0],s_type)
                        else: 
                            print("Only one row should satisfy the {} {} {} condition, but {} were found".format(condition, cond_type, cond_val, rows))
                            sample[var] = None 

                    # Need to force precision before even/odd or the precision update can counter the even/odd correction
                    if var_def_subset["force_precision"].tolist()[0]: 
                        sample[var] = self.force_precision(sample[var], var_def_subset["precision"].tolist()[0])

                    if not (var_def_subset["force_odd"].tolist()[0] and var_def_subset["force_even"].tolist()[0]):
                        if var_def_subset["force_odd"].tolist()[0]: 
                            sample[var] = self.force_odd(sample[var])
                        if var_def_subset["force_even"].tolist()[0]: 
                            sample[var] = self.force_even(sample[var])

                    # Need to force precision after even/odd to solve numerical precision problem with eveb/odd update
                    if var_def_subset["force_precision"].tolist()[0]: 
                        sample[var] = self.force_precision(sample[var], var_def_subset["precision"].tolist()[0])

                # Check if we have all parameters
                if len(sample) == len(np.unique(self.names)): 
                    got_all_params = True
                
                # Check if we need to restart from the beginning
                vid = vid + 1
                if vid == len(self.names): 
                    vid = 0

            samples.append(sample)
        return pd.DataFrame(samples)

    def exhaustive(self, vars): 
        # If any are continuous, abort or use default
        # --- all samples and sample combinations 
        # 
        # 
        return None

    # Helper formatting functions
    def force_odd(self, num): 
        precision  = str(num)[::-1].find('.')
        last_digit = int(str(num)[-1])
        if last_digit % 2 == 0:
            num += 10**(-precision)
        return num

    def force_even(self, num): 
        precision  = str(num)[::-1].find('.')
        last_digit = int(str(num)[-1])
        if last_digit % 2 == 1:
            num -= 10**(-precision)
        return num

    def force_precision(self, num, precision): 
        if precision == 0: 
            num = int(num)
        else: 
            num = float(int(num*(10**precision)))/(10**precision)
        return num


