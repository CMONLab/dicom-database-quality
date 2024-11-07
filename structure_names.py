#!/usr/bin/env python

"""structure_names.py: Create a file indicating the list of structures and their frequencies in all databases. Output file: 'Date + structure_names.csv', Date + log_structure_names.csv """

from dicompylercore import dicomparser
import pydicom as py
import csv
import os
from collections import Counter
from datetime import date
import sys
import getopt


## Function to get structures names and their frequencies ##
def get_structure_name(rtssfile):
    struct_name = []
    for f in rtssfile:
        RTss = dicomparser.DicomParser(f)
        RTstructures = RTss.GetStructures()
        struct_name.extend(structure['name'] for structure in RTstructures.values()) #Add the names obtained from the list comprehension to the existing list struct_name
    return struct_name


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

    print('Input directory:', arg_in)
    print('Output directory:', arg_out)

    if not arg_in or not arg_out:
        print("Please, specify both input and output directories.")
        print(arg_help)
        sys.exit(2)

    today = date.today()
    output_file = os.path.join(arg_out, f'{today}_structure_names.csv')
    log_file = os.path.join(arg_out, f'{today}_log_structure_names.csv')

    if os.path.isfile(output_file):
        os.remove(output_file)
        
    if os.path.isfile(log_file):
        os.remove(log_file)

    names_struct_tot = []
    ## Create .csv file ##
    with open(log_file, "w", newline='', encoding='utf-8') as file_log:
        log_writer = csv.writer(file_log)
        log_writer.writerow(['Directory', 'Issue'])  # Header for the log file

        ## Loop on the database's folder ##
        for dirs in os.listdir(arg_in):
            if os.path.isdir(os.path.join(arg_in, dirs)):  # Check if it's a directory
                list_file_str = []
                path_dir = os.path.join(arg_in, dirs)
                print(f'Directory: {dirs}')

                files = [f for f in os.listdir(path_dir) if os.path.isfile(os.path.join(path_dir, f))]
                for f in files:
                    if f.endswith('.dcm') or f.endswith('.DCM'):
                        name_file = os.path.join(path_dir, f)
                        data_dcm = py.read_file(name_file, force=True)
                        if data_dcm.Modality == "RTSTRUCT":
                            list_file_str.append(name_file)

                ## Log problematic cases ##
                if len(list_file_str) > 1:
                    log_writer.writerow([dirs, 'More than one RTSTRUCT file found'])
                    print(f"More than 1 structure file present in {dirs}")

                elif len(list_file_str) == 0:
                    log_writer.writerow([dirs, 'No RTSTRUCT file found'])
                    print(f"No structure file present in {dirs}")

                ## Process files with exactly one RTSTRUCT ##
                if len(list_file_str) == 1:
                    names_struct_pts_esimo = get_structure_name([list_file_str[0]])
                    names_struct_tot.append(names_struct_pts_esimo)

        names_struct_tot_flat = [item for sublist in names_struct_tot for item in sublist]
        info_to_save = Counter(names_struct_tot_flat)

        ## Save the structure names and frequencies to output CSV ##
        with open(output_file, "w", newline='', encoding='utf-8') as file_output:
            writer = csv.writer(file_output)
            writer.writerow(['Structure name', 'Frequency'])  # Header for the output file
            for key, value in info_to_save.items():
                writer.writerow([key, value])





if __name__ == "__main__":
    main(sys.argv)

