#!/usr/bin/env python

"""dose_number.py: Create a file that indicates the number of dose files in the parent folder and their maximum value. Include an additional column that specifies the prescribed dose from the .xlsx file. Output file: 'Date + dose_number.csv'."""

import os
import pydicom as py
import pandas as pd
from datetime import date
import sys
import getopt

def main(argv):
    arg_in = ""
    arg_out = ""
    arg_file = ""
    arg_help = f"{argv[0]} -i <input:db directory> -o <output:output directory> -f <file:path file with dose info>"

    try:
        opts, args = getopt.getopt(argv[1:], "h:i:o:f:", ["help", "input_directory=", "output_directory=", "file_prescripted_dose="])

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
        elif opt in ("-f", "--file"):
            arg_file = arg

    print('input directory:', arg_in)
    print('output directory:', arg_out)
    print('dose file:', arg_file)

    if not arg_in or not arg_out:
        print("Please, specify both the input and output directories.")
        print(arg_help)
        sys.exit(2)

    today = date.today()
    output_file = os.path.join(arg_out, f"{str(today)}_dose_number.csv")

    if os.path.exists(output_file):
        os.remove(output_file)
    ## Create .csv file ##
    header_csv = ['folder_name', 'Patient_ID', 'Patient_name', 'dose file name', 'n. dose', 'maximum dose value', 'planned dose', 'dose difference']
    with open(output_file, mode='w', encoding='utf-8') as s:
        s.write(','.join(header_csv) + '\n')

    path_db = arg_in
    info_to_save = []

    ## Load planned doses from the Excel file if provided ##
    planned_doses = {}
    if arg_file:
        try:
            planned_df = pd.read_excel(arg_file)
            planned_doses = dict(zip(planned_df['Patient_ID'], planned_df['dose_planned']))
        except Exception as e:
            print(f"Error reading the planned dose file: {e}")
            sys.exit(2)
            
    ## Loop on the database's folder ##
    for dirs in os.listdir(path_db):
        if os.path.isdir(os.path.join(path_db, dirs)):
            list_file_dose, list_dose_value, Patient_ID, Patient_name = [], [], [], []
            path_dir = os.path.join(path_db, dirs)
            print(dirs)
            files = [f for f in os.listdir(path_dir) if os.path.isfile(os.path.join(path_dir, f))]
            for f in files:
                if not f.startswith('.'):
                    name_file = os.path.join(path_dir, f)
                    ## Get info to save from each RTDOSE ##
                    if f.endswith('.dcm') or f.endswith('.DCM'):
                        data_dcm = py.read_file(name_file, force=True)
                        if data_dcm.Modality == "RTDOSE":
                            list_file_dose.append(f)
                            Patient_ID.append(data_dcm.PatientID)
                            Patient_name.append(data_dcm.PatientName)
                            list_dose_value.append((data_dcm.pixel_array * data_dcm.DoseGridScaling).max()) # Get the maximum value dose

            folder_name = os.path.basename(os.path.normpath(path_dir))
            n_dose = len(list_file_dose)

            ## Get the planned dose regardless of the number of dose files ##
            planned_dose = None
            if Patient_ID:
                pid = Patient_ID[0]  # Assume all Patient_IDs in the list are the same for the folder
                planned_dose = planned_doses.get(pid, None)

            ## Calculate the dose difference only if there's exactly one dose file ##
            dose_difference = None
            if n_dose == 1 and planned_dose is not None:
                dose_difference = list_dose_value[0] - planned_dose
            
            ## Create db to save ##
            info_to_save.append([folder_name, Patient_ID, Patient_name, list_file_dose, n_dose,
                                 max(list_dose_value) if list_dose_value else None,
                                 planned_dose, dose_difference])
    
    ## Save info in the output file ##
    file_csv = pd.DataFrame(info_to_save)
    file_csv.to_csv(output_file, encoding='utf-8', mode='a', header=False, index=False)


if __name__ == "__main__":
    main(sys.argv)


