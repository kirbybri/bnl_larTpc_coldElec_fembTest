#!/bin/bash
g++ -std=c++11 -o processNtuple processNtuple.cxx `root-config --cflags --glibs`
g++ -std=c++11 -o summaryAnalysis_doFembTest_noiseMeasurement summaryAnalysis_doFembTest_noiseMeasurement.cxx `root-config --cflags --glibs`
