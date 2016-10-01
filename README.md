# bnl_larTpc_coldElec_fembTest
Example cold electronic test script. Performs pedestal RMS measurements for 35t/SBND style FEMBs.

## Software Requirements:
- Linux environment and command line (tested with Ubuntu 14, bash shell)
- ROOT and pyRoot libraries (tested with ROOT 6.06)
- 35t or SBND style FEMB readout with UDP interface firmware
- c++11 standard compiler
- python 3 (tested with version 3.5)
- python sqlalchemy package
- python sqlite
- femb_udp_core project

## Interface Requirements:
- UDP interface configured to work with femb_udp_core project
- no power supply or signal generators used

## Method:
- measurement script starts a "run". Each run has a unique timestamp and metadata variables
- each run consists of 32 subruns of pedestal data, each recorded with a different FE-ASIC configuration
- pedestal data is analyzed and RMS measured for each channel in each configuration
- conversion to ENC is NOT done. Note that RMS measurements by themselves are not particularly interesting
- summary plots and RMS measurements are output
- RMS measurements are stored in a database
- measurement script can be run repeatedly in same directory, all output files have unique names

## Output:
- text file containing pedestal RMS measurements in ADC count units for every FE-ASIC configuration and channel.
- PNG image showing plot of measured pedestal RMS values
- list of raw data files
- list of processed data files
- database updated

## Missing:
- measurement status monitor and recovery: if any part of measurement fails or analysis fails the script will not recover gracefully

## Instructions:

1) Check out femb_udp_core and bnl_larTpc_coldElec_fembTest git projects:
- git clone https://github.com/kirbybri/bnl_larTpc_coldElec_fembTest.git
- git clone https://github.com/kirbybri/femb_udp_core.git

2) Setup FEMB UDP readout and verify board is streaming data (more detailed instructions in femb_udp project)
- current script will assume board is in working state, doesn’t run initialization

3) In bnl_larTpc_coldElec_fembTest directory, run setup script:
- source setup_doFembTest_noiseMeasurement.sh
- script compiles executables, if compilation errors occur further debugging is needed

4) In doFembTest_noiseMeasurement.py script manually edit PATH_FEMB_UDP variable to path of femb_udp_core package.

5) Run measurement script from command line:
- python doFembTest_noiseMeasurement.py
- Should loop through 32 different FE-ASIC configurations and record data for all 128 FEMB channels each time. 32 subrun files recorded in total to “data” directory.
- Gain is varied between 4.7,7.8,14,25 mV/fC, shaping time 0.5,1,2,3us and the baseline level between 200/900mV 
- Data files are processed and summarized by analysis programs
- RMS measurements stored in a local sqlite database file
- Check to see if any errors are reported during measurement or analysis steps

6) Check output summary plot and text file containing pedestal RMS measurements for each configuration + channel.
