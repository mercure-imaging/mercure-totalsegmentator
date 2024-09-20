# **mercure-totalsegmentator**
<br>

Mercure module to deploy [TotalSegmentator](https://github.com/wasserth/TotalSegmentator) tool for segmentation of 104 classes in CT images and 56 classes in MR images. This module runs as a docker container in mercure, it can be added to an existing mercure installation using docker tag : 
`mercureimaging/mercure-totalsegmentator:v2`.
<br>
The current version of the module is configured to run the TotalSegmentator at a lower resolution (3mm) if only CPU is available and at high resolution when GPU (cuda device) is available.
Also, the pipeline will automatically run the correct subcommand for TotalSegmentator depending on whether the input data is 'CT' or 'MR'.
<br>

# Installation
<br>


## Add module to existing Mercure installation
Follow instructions on [Mercure website](https://mercure-imaging.org) on how to add a new module. Use the docker tag *mercureimaging/mercure-totalsegmentator*.

<br>


## Install new Mercure test environment and deploy totalsegmentator module

<br>

Install [virtual box](https://www.virtualbox.org/) and [vagrant](https://www.vagrantup.com/) and follow jupyter notebook tutorial [*tutorial_mercure-totalsegmentator.ipynb*](./tutorial_mercure-totalsegmentator.ipynb) (less than 1hr to complete).

<br>

## Build module for local testing and development
1. Clone repo.
2. Build Docker container locally by running make (modify makefile with new docker tag as needed).
3. Test container :\
`docker run -it -v /input_data:/input -v /output_data:/output --env MERCURE_IN_DIR=/input  --env MERCURE_OUT_DIR=/output --shm-size 1G *docker-tag*`

### Note
The default shared memory (shm) size for Docker container might not be sufficient to run the container. Thus, `--shm-size 1G` is included in the above command. Similarly, when configuring this module in Mercure, add the following as one of the docker arguments:
`"shm_size": "1G"`

<br>

# Output
<br>

Segmentations are written to specified output directory in three different formats :
- DICOM RTSTRUCT ( with segmentated VOI volume ( mm<sup>3</sup> ) in description field )
- DICOM SEG
- DICOM RGB ( with masks of each VOI overlaid )

<br>
<br>


![image.png](seg_image.png)

<br>
<br>

## Acknowledgments

<br>
MAP operators and code adapted from GSTT-CSC TotalSegmentator-AIDE repository: https://github.com/GSTT-CSC/TotalSegmentator-AIDE
<br>



