#!/usr/bin/env python

"""remove_double_ct.py: This script scans DICOM files in the specified input folder,
filters for files with Modality 'CT' or 'RTSTRUCT', and removes any duplicate files
based on their SOPInstanceUID."""

import os
import pydicom as py
import sys
import getopt  # to read argument input

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

    if not arg_in:
        print("Please, specify the input directory.")
        print(arg_help)
        sys.exit(2)

    ## Loop on the database's folder ##
    for dirs in os.listdir(arg_in):
        if not os.path.isfile(dirs):
            path_dir = os.path.join(arg_in, dirs)
            ## Set to track unique SOPInstanceUIDs ##
            unique_files = set()
            files = [f for f in os.listdir(path_dir) if f.endswith('.dcm') and not f.startswith('.')]

            for f in files:
                name_file = os.path.join(path_dir, f)
                try:
                    data_dcm = py.read_file(name_file, force=True)
                    ## Check for modality 'CT' or 'RTSTRUCT' ##
                    if data_dcm.Modality in ["CT", "RTSTRUCT"]:
                        sop_instance_uid = data_dcm.SOPInstanceUID  # Unique identifier for each DICOM file

                        ## Check if the SOPInstanceUID is already in the set ##
                        if sop_instance_uid not in unique_files:
                            unique_files.add(sop_instance_uid)  # Mark as unique
                        else:
                            # Duplicate found, delete the file
                            print(f"Duplicate found and removed: {name_file}")
                            os.remove(name_file)
                except Exception as e:
                    print(f"Error reading file {name_file}: {e}")

if __name__ == "__main__":
    main(sys.argv)

