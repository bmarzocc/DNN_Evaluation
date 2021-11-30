#!/usr/bin/python
import numpy as n
from ROOT import *
import sys, getopt
from array import array
import itertools
import argparse
import operator
import os



if __name__ == '__main__':

  parser =  argparse.ArgumentParser(description='cat MVA')
  parser.add_argument('-d', '--inDir', dest='inDir', required=True, type=str)
  parser.add_argument('-m', '--min', dest='min', required=False, type=float)
  parser.add_argument('-M', '--max', dest='max', required=False, type=float)
  parser.add_argument('-r', '--massMin', dest='massMin', required=False, type=float)
  parser.add_argument('-R', '--massMax', dest='massMax', required=False, type=float)
  parser.add_argument('-n', '--nStep', dest='nStep', required=False, type=int)
  parser.add_argument('-N', '--node', dest='node', required=True, type=int)
   
  args = parser.parse_args()
  inDir = args.inDir
  #inDir='/eos/user/b/bmarzocc/HHWWgg/January_2021_Production/HHWWyyDNN_binary_EFT_noHgg_noNegWeights_BalanceYields_allBkgs_NLO_Reweighted_20nodes_noPtOverM_withKinWeight_weightSel/'

  min = 0.1
  if args.min: min = args.min
  max = 1.
  if args.max: max = args.max
  massMin = 120.
  if args.massMin: massMin = args.massMin
  massMax = 130.
  if args.massMax: massMax = args.massMax
  nStep = 4 
  if args.nStep: nStep = args.nStep
  node = 1
  if args.node: node = args.node

  print "inDir:",inDir
  print "bdtMin:",min
  print "bdtMax:",max
  print "massMin:",massMin
  print "massMin:",massMax
  print "nStep:",nStep
  print "Node:",node
  
  local = os.getcwd()
  if not os.path.isdir('error'): os.mkdir('error') 
  if not os.path.isdir('output'): os.mkdir('output') 
  if not os.path.isdir('log'): os.mkdir('log') 
   
  # Prepare condor jobs
  condor = '''executable              = run_script.sh
output                  = output/strips.$(ClusterId).$(ProcId).out
error                   = error/strips.$(ClusterId).$(ProcId).err
log                     = log/strips.$(ClusterId).log
transfer_input_files    = run_script.sh
on_exit_remove          = (ExitBySignal == False) && (ExitCode == 0)
periodic_release        = (NumJobStarts < 3) && ((CurrentTime - EnteredCurrentStatus) > (60*60))
    
+JobFlavour             = "longlunch"
+AccountingGroup        = "group_u_CMS.CAF.ALCA"
queue arguments from arguments.txt
'''

  with open("condor_job.txt", "w") as cnd_out:
     cnd_out.write(condor)

  outputDir = os.getcwd()

  script = '''#!/bin/sh -e

JOBID=$1; 
LOCAL=$2; 
INPUTDIR=$3;
NBINS=$4;
MIN=$5
MAX=$6
MASSMIN=$7
MASSMAX=$8
NODE=$9

echo -e "evaluate"
eval `scramv1 ru -sh`

echo -e "smoothing...";
python ${LOCAL}/smooth_DNN.py -d ${INPUTDIR} -n ${NBINS} --min ${MIN} --max ${MAX} --massMin ${MASSMIN} --massMax ${MASSMAX} -N ${NODE}

echo -e "DONE";
'''

  arguments=[]
  nBins = [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,380,760,1520]
  for iBin in nBins:
     for i  in range(0,nStep): 
        arguments.append("{} {} {} {} {} {} {} {} {}".format(1,local,inDir+"/",iBin,min,max,massMin+i,massMax-i,node))     
  with open("arguments.txt", "w") as args:
     args.write("\n".join(arguments)) 
  with open("run_script.sh", "w") as rs:
     rs.write(script) 

