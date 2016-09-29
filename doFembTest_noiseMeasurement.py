#!/usr/bin/python3.4
import sys
import string
from subprocess import call
from time import sleep
import os
import ntpath
import glob

#CHECK STATUS AND INITIALIZATION
print("NOISE MEASUREMENT - CHECKING READOUT STATUS")

#specify location of femb_udp package
PATH_FEMB_UDP = None 
if PATH_FEMB_UDP == None:
    print("Error running doFembTest - PATH_FEMB_UDP not assigned")
    print(" Please specify the path of the femb_udp package by assigning it to the PATH_FEMB_UDP at the top of this script.")
    print(" If you have not checked out the femb_udp package, run the following command: git clone https://github.com/kirbybri/femb_udp.git")
    print(" This script will exit now")
    sys.exit(0)
sys.path.append(PATH_FEMB_UDP)

#import femb_udp modules from femb_udp package
from femb_rootdata import FEMB_ROOTDATA
from femb_config import FEMB_CONFIG
femb_config = FEMB_CONFIG()
femb_rootdata = FEMB_ROOTDATA()

#check if readout is working
testData = femb_rootdata.femb.get_data_packets(1)
if testData == None:
    print("Error running doFembTest - FEMB is not streaming data.")
    print(" Turn on and initialize FEMB UDP readout.")
    print(" This script will exit now")
    sys.exit(0)
if len(testData) == 0:
    print("Error running doFembTest - FEMB is not streaming data.")
    print(" Turn on and initialize FEMB UDP readout.")
    print(" This script will exit now")
    sys.exit(0)

#check for analysis executables
if os.path.isfile('./processNtuple') == False:    
    print('processNtuple not found, exiting')
    sys.exit(0)

if os.path.isfile('./summaryAnalysis_doFembTest_noiseMeasurement') == False:    
    print('summaryAnalysis_doFembTest_noiseMeasurement not found, exiting')
    sys.exit(0)

#MEASUREMENT SECTION
print("NOISE MEASUREMENT - RECORDING DATA")

#initialize readout channel range
femb_rootdata.minchan = 0
femb_rootdata.maxchan = 127

#initialize output filelist
filelist = open("filelist_doFembTest_noiseMeasurement_" + str(femb_rootdata.date) + ".txt", "w")
subrun = 0
for g in range(0,4,1):
  for s in range(0,4,1):
    for b in range(0,2,1):
        #config FE ASICs
        femb_config.configFeAsic(g,s,b)
        sleep(0.5)
        filename = "data/output_femb_rootdata_doFembTest_" + str(femb_rootdata.date) + "_"  + str(subrun) + ".root"
        print("Recording " + filename)
        femb_rootdata.filename = filename
        femb_rootdata.numpacketsrecord = 10
        femb_rootdata.run = 0
        femb_rootdata.subrun = subrun
        femb_rootdata.runtype = 1
        femb_rootdata.runversion = 0
        femb_rootdata.par1 = 0
        femb_rootdata.par2 = 0
        femb_rootdata.par3 = 0
        femb_rootdata.gain = g
        femb_rootdata.shape = s
        femb_rootdata.base = b
        femb_rootdata.record_data_run()
        filelist.write(filename + "\n")
        subrun = subrun + 1
filelist.close()

#ANALYSIS SECTION
print("NOISE MEASUREMENT - ANALYZING AND SUMMARIZING DATA")

#process data
newlist = "filelist_processData_doFembTest_noiseMeasurement_" + str(femb_rootdata.date) + ".txt"
input_file = open(filelist.name, 'r')
output_file = open( newlist, "w")
for line in input_file:
    filename = str(line[:-1])
    #print filename
    call(["./processNtuple", str(line[:-1]) ])
    newname = max(glob.iglob('*.root'), key=os.path.getctime)
    call(["mv",newname,"data/."])
    newname = "data/" + newname
    output_file.write(newname + "\n")
    print(filename)
    print(newname)
input_file.close()
output_file.close()

#run summary program
call(["./summaryAnalysis_doFembTest_noiseMeasurement", newlist ])
