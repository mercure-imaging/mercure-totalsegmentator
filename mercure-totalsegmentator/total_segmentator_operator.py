import logging
import os
import torch
import shutil
import subprocess
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
# Perform automatic segmentation of 104 regions on CT imaging data with TotalSegmentator
# code resused / adapted from TOTALSegmentator- AIDE, see https://github.com/GSTT-CSC/TotalSegmentator-AIDE
@md.input("input_files", DataPath, IOType.DISK)
@md.output("input_files", DataPath, IOType.DISK)
@md.env(pip_packages=["pydicom >= 2.3.0", "highdicom >= 0.18.2"])
class TotalSegmentatorOperator(Operator):
    """
    TotalSegmentator Operator - perform segmentation on CT imaging data saved as NIFTI file
    """

    def compute(self, op_input: InputContext, op_output: OutputContext, context: ExecutionContext):

        logging.info(f"Begin {self.compute.__name__}")

        input_path = op_input.get("input_files").path
        nii_input_file = os.path.join(input_path,'nii_input','input-ct-dataset.nii.gz')

        if not os.path.exists(nii_input_file):
            NameError('Exception occurred with nii_input_file')
        else:
            logging.info(f"Found nii_input_file: {nii_input_file}")

        # Create TotalSegmentator output directory
        nii_seg_output_path = os.path.join(input_path, 'nii_input', 'nii_seg_output')
        if not os.path.exists(nii_seg_output_path):
            os.makedirs(nii_seg_output_path)

        print("Checking device...")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print("device being used:", device)

        # Run TotalSegmentator
        from dcm2nii_operator import input_modality
        print("Modality of input data:", input_modality)
        if device == torch.device("cuda"):
            print("running full version")
            # check if the input data is MR or CT
            if input_modality == "CT":
                subprocess.run(["TotalSegmentator", "-i", nii_input_file, "-o", nii_seg_output_path,"--ml"])
            elif input_modality == "MR":
                subprocess.run(["TotalSegmentator", "-i", nii_input_file, "-o", nii_seg_output_path,"--ml","--task", "total_mr"])
        else:
            print("running fast version")
            if input_modality == "CT":
                subprocess.run(["TotalSegmentator", "-i", nii_input_file, "-o", nii_seg_output_path,"--fast","--ml"])
            elif input_modality == "MR":
                subprocess.run(["TotalSegmentator", "-i", nii_input_file, "-o", nii_seg_output_path,"--fast","--ml", "--task", "total_mr"])
        

        logging.info(f"Performed TotalSegmentator processing")

        # Set output path for next operator
        op_output.set(DataPath(input_path))  # cludge to avoid op_output not exist error
        op_output_folder_path = op_output.get().path
        op_output_folder_path.mkdir(parents=True, exist_ok=True)

        logging.info(f"End {self.compute.__name__}")
