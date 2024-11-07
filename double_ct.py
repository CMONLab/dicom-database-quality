#!/usr/bin/env python

"""double_ct.py: Create a file indicating the number of structure and CT files present in the parent folder and the count of unique dates. Output file: 'Date + double_ct.csv' """

import os
import pydicom as py
import pandas as pd
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
        print("Please, specify both the input and output directories.")
        print(arg_help)
        sys.exit(2)

    today = date.today()
    output_file = os.path.join(arg_out, f"{str(today)}_double_ct.csv")

    if os.path.exists(output_file):
        os.remove(output_file)
        
    ## Create .csv file ##
    if not os.path.isfile(output_file):
        header_csv = ['folder_name', 'filename', 'Patient_ID', 'n. file structure', 'n. different dates structure', 'n. different dates ct']
        with open(output_file, mode='w', encoding='utf-8') as s:
            s.write(','.join(header_csv) + '\n')


    ## Loop on the database's folder ##
    info_to_save = []
    for dirs in os.listdir(arg_in):
        if os.path.isdir(os.path.join(arg_in, dirs)):
            list_file_str, date_str, patient_ID = [], [], []
            list_file_ct, date_ct = [], []
            path_dir = os.path.join(arg_in, dirs)
            print(dirs)

            for root, dirs, files in os.walk(path_dir):
                for f in files:
                    if not f.startswith('.'):
                        name_file = os.path.join(root, f)
                        if f.endswith('.dcm') or f.endswith('.DCM'):
                            data_dcm = py.read_file(name_file, force=True)
                            ## Get info to save from each RTSTRUCT ##
                            if data_dcm.Modality == "RTSTRUCT":
                                list_file_str.append(f)
                                date_str.append(data_dcm.StructureSetDate)
                                patient_ID.append(data_dcm.PatientID)
                            ## Get info to save from each CT ##
                            elif data_dcm.Modality == "CT":
                                list_file_ct.append(f)
                                date_ct.append(data_dcm.StudyDate)
            
            ## Get unique date of CT &  RTSTRUCT ##
            date_structure_unique = set(date_str)
            date_ct_unique = set(date_ct)

            ## Create db to save ##
            folder_name = os.path.basename(os.path.normpath(path_dir))
            info_to_save.append([folder_name, list_file_str, patient_ID, len(list_file_str), len(date_structure_unique), len(date_ct_unique)])
    
    ## Save info in the output file ##
    file_csv = pd.DataFrame(info_to_save)
    file_csv.to_csv(output_file, encoding='utf-8', mode='a', header=False, index=False)

if __name__ == "__main__":
    main(sys.argv)

