import glob
import logging
import os
import shutil
import subprocess
import pydicom
from pathlib import Path


import monai.deploy.core as md
from monai.deploy.core import (
    Application,
    DataPath,
    ExecutionContext,
    Image,
    InputContext,
    IOType,
    Operator,
    OutputContext,
    resource
)

global input_modality
input_modality = None

# DICOM to NIfTI conversion operator
# code resused / adapted from TOTALSegmentator- AIDE, see https://github.com/GSTT-CSC/TotalSegmentator-AIDE
@md.input("input_files", DataPath, IOType.DISK)
@md.output("input_files", DataPath, IOType.DISK)
@md.env(pip_packages=["pydicom >= 2.3.0", "highdicom >= 0.18.2"])
class Dcm2NiiOperator(Operator):
    """
    DICOM to NIfTI Operator
    """

    def compute(self, op_input: InputContext, op_output: OutputContext, context: ExecutionContext):

        logging.info(f"Begin {self.compute.__name__}")

        input_path = str(op_input.get("input_files").path)

        # Set local_testing = True if doing local testing
        local_testing = True
        if local_testing:
            input_files = sorted(os.listdir(input_path))  # assumes .dcm in input/
        else:
            input_files = parse_recursively_dcm_files(input_path)  # assumes AIDE MinIO structure

        # Read the first input file from input files and extract the modality from the dicom tags
        reference_file = None
        for f in input_files:
            if f.endswith('.dcm'):
                reference_file = f
                break
        modality = None
        try:
            file_path = os.path.join(input_path, reference_file)
            dicom_file = pydicom.dcmread(file_path)
            modality = dicom_file.Modality
        except Exception as e:
            logging.error(f"Error reading DICOM file: {e}")
        # Set a global variable named input_modality to be used in the other file
        global input_modality
        input_modality = modality

        # create directories and move input DICOM files for later
        current_dir = os.getcwd()
        dcm_input_path = os.path.join(current_dir, 'dcm_input')
        if not os.path.exists(dcm_input_path):
            os.makedirs(dcm_input_path)

        nii_input_path = os.path.join(current_dir, 'nii_input')
        if not os.path.exists(nii_input_path):
            os.makedirs(nii_input_path)


        for f in input_files:
            if not f.endswith('.json'):
                shutil.move(os.path.join(input_path, f), dcm_input_path)

        
        print(dcm_input_path)
        # Run dcm2niix
        subprocess.run(["dcm2niix", "-z", "y", "-o", nii_input_path, "-f", "input-ct-dataset", dcm_input_path])


        # Set output path for next operator
        op_output.set(DataPath(current_dir))

        logging.info(f"Performed dcm2niix conversion")

        logging.info(f"End {self.compute.__name__}")


def parse_recursively_dcm_files(input_path):
    """
    Recursively parse Minio folder structure to extract paths to .dcm files
    Minio file structure:
    /var/monai/input
        StudyUID (folder)
            SeriesUID (folders)
                InstanceUID (files)
    :param input_path:
    :return dcm_paths:
    """

    logging.info(f"input_path: {os.getcwd()}")
    logging.info(f"listdir(input_path): {os.listdir(input_path)}")

    for item in os.listdir(input_path):
        item = os.path.join(input_path, item)
        if os.path.isdir(item):
            study_path = item
        else:
            NameError('Exception occurred with study_path')

    logging.info(f"study_path: {study_path}")

    try:
        series_paths = []
        series_dirs = os.listdir(study_path)
        for sd in series_dirs:
            series_paths.append(os.path.join(study_path, sd))
    except:
        print('Exception occurred with series_paths')

    logging.info(f"series_paths: {series_paths}")

    dcm_files = []
    for sp in series_paths:
        series_files = os.listdir(sp)
        for file in series_files:
            if '.dcm' in Path(file).suffix:
                dcm_files.append(file)

    dcm_paths = [os.path.join(a, b) for a, b in zip(series_paths, dcm_files)]

    logging.info(f"dcm_paths: {dcm_paths}")

    return dcm_paths
