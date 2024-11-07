#!/usr/bin/env python

"""dose_sum_up.py: Create a new dicom dose file if there are more than one dose cube (sum of). Output file: dose_tot.dcm"""

import numpy as np
import pydicom as py
import os
from dicompylercore import dose # to sum the dose files
import sys
import getopt


back = "/"

## Function to sum the doses from up to 5 different files. It saves the sum in the patient's folder (dose_tot.dcm) ##
def sum_multi_dose(list_file_dose):
    grid, sum_dose = [], []
    
    name_directory = os.path.dirname(os.path.abspath(list_file_dose[0]))
    
    if (len(list_file_dose) == 2):
        for f in range(len(list_file_dose)):
            grid.append(dose.DoseGrid(list_file_dose[f]))
            
        print("sum two cubes in :", name_directory )
        sum_dose = grid[0] + grid[1]
        sum_dose.save_dcm(name_directory + back + "dose_tot.dcm")
        
    if (len(list_file_dose) == 3):
        for f in range(len(list_file_dose)):
            grid.append(dose.DoseGrid(list_file_dose[f]))
         
        print("sum three cubes in :", name_directory )
        sum_dose = grid[0] + grid[1] + grid[2]
        sum_dose.save_dcm(name_directory + back + "dose_tot.dcm")
        
    if (len(list_file_dose) == 4):
        for f in range(len(list_file_dose)):
            grid.append(dose.DoseGrid(list_file_dose[f]))
            
        print("sum four cubes in :", name_directory )
        sum_dose = grid[0] + grid[1] + grid[2] + grid[3]
        sum_dose.save_dcm(name_directory + back + "dose_tot.dcm")
        
    if (len(list_file_dose) == 5):
        for f in range(len(list_file_dose)):
            grid.append(dose.DoseGrid(list_file_dose[f]))
            
        print("sum five cubes in :", name_directory )
        sum_dose = grid[0] + grid[1] + grid[2] + grid[3] + grid[4]
        sum_dose.save_dcm(name_directory + back + "dose_tot.dcm")
        
    if (len(list_file_dose) > 5):
        print("More than 5 file to sum up: check it before continuing")



def main(argv):

    arg_in = ""
    arg_help = f"{argv[0]} -i <input:db directory>"

    try:
        opts, args = getopt.getopt(argv[1:], "h:i:", ["help", "input_directory="])

    except getopt.GetoptError:
        print(arg_help)
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(arg_help)
            sys.exit(2)
        elif opt in ("-i", "--input"):
            arg_in = arg
            
    print('Input directory:', arg_in)
    
    if not arg_in :
        print("Please, specify input directory.")
        print(arg_help)
        sys.exit(2)

    ## Loop on the database's folder ##
    for dirs in os.listdir(arg_in):
        if os.path.isfile(dirs) is False:
            list_file_dose = []
            path_dir = arg_in + back + dirs
            print(dirs)
            files = [f for f in os.listdir(path_dir) if os.path.isfile(os.path.join(path_dir, f))]
            for f in files:
                if(os.path.isfile(f) == False):
                    if not f.startswith('.'):
                        name_file = path_dir + back + f
                        if f.endswith('.dcm') or f.endswith('.DCM'):
                            data_dcm = py.read_file(name_file, force=True)
                            ## Select the RTDOSE ##
                            if data_dcm.Modality == "RTDOSE" and f!= 'dose_tot.dcm':
                                list_file_dose.append(name_file)
                                
            ## Sum the doses if they are greater than 1 ##
            if len(list_file_dose) >= 1:
                sum_multi_dose(list_file_dose)

  

if __name__ == "__main__":
    main(sys.argv)

