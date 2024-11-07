#!/usr/bin/env python

"""folder_id_check.py: Create a file indicating the number of files present in the parent folder,
if the files have all the same ID, and how many files have a specific ID.
Output file: 'Date + folder_id_check.csv' """

import os
import pydicom as py
import pandas as pd
from collections import Counter
from datetime import date
import sys
import getopt  
def main(argv):
    arg_in = ""
    arg_out = ""
    arg_help = f"{argv[0]} -i <input:db directory> -o <output:output directory>"

    try:
        opts, args = getopt.getopt(argv[1:], "h:i:o:", ["help", "input_directory=", "output_directory="])

    except getopt.GetoptError:
        print(arg_help)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(arg_help)
            sys.exit(2)
        elif opt in ("-i", "--input"):
            arg_in = arg
        elif opt in ("-o", "--output"):
            arg_out = arg

    print('input directory:', arg_in)
    print('output directory:', arg_out)

    if not arg_in or not arg_out:
        print("Please, specify both input and output directories.")
        print(arg_help)
        sys.exit(2)

    today = date.today()
    output_file = os.path.join(arg_out, f'{today}_folder_id_check.csv')

    if os.path.isfile(output_file):
        os.remove(output_file)
    
    ## Create .csv file ##
    header_csv = ['folder_name', 'Patient_ID', 'filename', 'n. file', 'unique', 'count_unique']
    with open(output_file, mode='w', encoding='utf-8') as s:
        s.write(','.join(header_csv) + '\n')
    
    ## Loop on the database's folder ##
    info_to_save = []
    for dirs in os.listdir(arg_in):
        if os.path.isfile(dirs) is False:
            info_file, patient_ID = [], []
            path_dir = os.path.join(arg_in, dirs)
            print(dirs)
            files = [f for f in os.listdir(path_dir) if os.path.isfile(os.path.join(path_dir, f))]
            for f in files:
                ## Get info to save from each file ##
                if not os.path.isfile(f) and not f.startswith('.'):
                    name_file = os.path.join(path_dir, f)
                    if f.endswith('.dcm') or f.endswith('.DCM'):
                        info_file.append(f)
                        data_dcm = py.read_file(name_file, force=True)
                        patient_ID.append(data_dcm.PatientID)

            ## Create db to save ##
            folder_name = os.path.basename(os.path.normpath(path_dir))
            unique_id = set(patient_ID)
            info_to_save.append([folder_name, patient_ID, info_file, len(info_file), unique_id, Counter(patient_ID)])
            
    ## Save info in the output file ##
    file_csv = pd.DataFrame(info_to_save)
    file_csv.to_csv(output_file, encoding='utf-8', mode='a', header=False, index=False)


if __name__ == "__main__":
    main(sys.argv)

