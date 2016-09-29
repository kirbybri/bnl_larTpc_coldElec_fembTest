#!/usr/bin/python3.4
import sys
import string
from subprocess import call
from time import sleep
import os
import ntpath
import glob

#specify location of femb_udp package
PATH_FEMB_UDP = None
class FEMB_TEST:

    def __init__(self):
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
        self.femb_config = FEMB_CONFIG()
        self.femb_rootdata = FEMB_ROOTDATA()

        #set status variables
        self.status_check_setup = 0
        self.status_record_data = 0
        self.status_do_analysis = 0
        self.status_archive_results = 0

    def check_setup(self):
        #CHECK STATUS AND INITIALIZATION
        print("NOISE MEASUREMENT - CHECKING READOUT STATUS")
        self.status_check_setup = 0
        #check if readout is working
        testData = self.femb_rootdata.femb.get_data_packets(1)
        if testData == None:
            print("Error running doFembTest - FEMB is not streaming data.")
            print(" Turn on and initialize FEMB UDP readout.")
            #print(" This script will exit now")
            #sys.exit(0)
            return
        if len(testData) == 0:
            print("Error running doFembTest - FEMB is not streaming data.")
            print(" Turn on and initialize FEMB UDP readout.")
            #print(" This script will exit now")
            #sys.exit(0)
            return

        #check for analysis executables
        if os.path.isfile('./processNtuple') == False:    
            print('processNtuple not found, run setup.sh')
            #sys.exit(0)
            return
        if os.path.isfile('./summaryAnalysis_doFembTest_noiseMeasurement') == False:    
            print('summaryAnalysis_doFembTest_noiseMeasurement not found, run setup.sh')
            #sys.exit(0)
            return
        self.status_check_setup = 1

    def record_data(self):
        if self.status_check_setup == 0:
            print("Please run check_setup method before trying to take data")
            return
        if self.status_record_data == 1:
            print("Data already recorded. Reset/restat GUI to begin a new measurement")
            return
        #MEASUREMENT SECTION
        print("NOISE MEASUREMENT - RECORDING DATA")

        #initialize readout channel range
        self.femb_rootdata.minchan = 0
        self.femb_rootdata.maxchan = 127

        #initialize output filelist
        self.filelist = open("filelist_doFembTest_noiseMeasurement_" + str(self.femb_rootdata.date) + ".txt", "w")
        subrun = 0
        for g in range(0,4,1):
          for s in range(0,4,1):
            for b in range(0,2,1):
                #config FE ASICs
                self.femb_config.configFeAsic(g,s,b)
                sleep(0.5)
                filename = "data/output_femb_rootdata_doFembTest_" + str(self.femb_rootdata.date) + "_"  + str(subrun) + ".root"
                print("Recording " + filename)
                self.femb_rootdata.filename = filename
                self.femb_rootdata.numpacketsrecord = 10
                self.femb_rootdata.run = 0
                self.femb_rootdata.subrun = subrun
                self.femb_rootdata.runtype = 1
                self.femb_rootdata.runversion = 0
                self.femb_rootdata.par1 = 0
                self.femb_rootdata.par2 = 0
                self.femb_rootdata.par3 = 0
                self.femb_rootdata.gain = g
                self.femb_rootdata.shape = s
                self.femb_rootdata.base = b
                self.femb_rootdata.record_data_run()
                self.filelist.write(filename + "\n")
                subrun = subrun + 1
        self.filelist.close()
        self.status_record_data = 1

    def do_analysis(self):
        if self.status_record_data == 0:
            print("Please record data before analysis")
            return
        if self.status_do_analysis == 1:
            print("Analysis already complete")
            return
        #ANALYSIS SECTION
        print("NOISE MEASUREMENT - ANALYZING AND SUMMARIZING DATA")

        #process data
        self.newlist = "filelist_processData_doFembTest_noiseMeasurement_" + str(self.femb_rootdata.date) + ".txt"
        input_file = open(self.filelist.name, 'r')
        output_file = open( self.newlist, "w")
        for line in input_file:
            filename = str(line[:-1])
            #print filename
            call(["./processNtuple", str(line[:-1]) ])
            rootfiles = glob.glob('output_processNtuple_output_femb_rootdata_doFembTest_' + str(self.femb_rootdata.date) + '*.root')
            if len(rootfiles) == 0:
                print("Processing error detected, needs debugging. Exiting now!")
                sys.exit(0)
                #continue
            newname = max(rootfiles, key=os.path.getctime)
            call(["mv",newname,"data/."])
            newname = "data/" + newname
            output_file.write(newname + "\n")
            print(filename)
            print(newname)
        input_file.close()
        output_file.close()
        #run summary program
        call(["./summaryAnalysis_doFembTest_noiseMeasurement", self.newlist ])
        self.status_do_analysis = 1

    def archive_results(self):
        if self.status_do_analysis == 0:
            print("Please analyze data before archiving results")
            return
        if self.status_archive_results == 1:
            print("Results already archived")
            return
        #ANALYSIS SECTION
        print("NOISE MEASUREMENT - STORE RESULTS IN DATABASE")

def main():
    femb_test = FEMB_TEST()
    femb_test.check_setup()
    femb_test.record_data()
    femb_test.do_analysis()
    femb_test.archive_results()

if __name__ == '__main__':
    main()
