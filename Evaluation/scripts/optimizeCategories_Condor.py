#!/usr/bin/python
import numpy as n
from ROOT import *
import sys, getopt
from array import array
import itertools
from optparse import OptionParser
import operator
import os



if __name__ == '__main__':


  parser = OptionParser()
  parser.add_option( "-d", "--inDir",   dest="inDir",    default="",   type="string", help="inDir" )
  parser.add_option( "-r", "--massMin", dest='massMin',  default=120., type="float",  help="massMin")
  parser.add_option( "-R", "--massMax", dest='massMax',  default=130., type="float",  help="massMax")
  parser.add_option( "-n", "--nStep",   dest='nStep',    default=1,    type="int",      help="nStep")
  (options, args) = parser.parse_args()  

  inDir = options.inDir
  massMin = options.massMin
  massMax = options.massMax
  nStep = options.nStep
  #inDir = '/eos/user/b/bmarzocc/HHWWgg/January_2021_Production/HHWWyyDNN_binary_noHgg_noNegWeights_BalanceYields_allBkgs_LOSignals_noPtOverM/'

  print "inDir:  ",inDir
  print "massMin:",massMin
  print "massMax:",massMax
  print "nStep:",nStep
  
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
NCATS=$5;
MASSMIN=$6
MASSMAX=$7
SMOOTH=$8
WEIGHT=$9

echo -e "evaluate"
eval `scramv1 ru -sh`

echo -e "Optimize significance";
python ${LOCAL}/optimizeCategories.py -d ${INPUTDIR}/ -n ${NBINS} -c ${NCATS} --massMin ${MASSMIN} --massMax ${MASSMAX} -s ${SMOOTH} -w ${WEIGHT}

echo -e "DONE";
'''
  arguments=[]
  nBins = [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,380,760,1520]
  for iBin in nBins: 
     for nCat in range(1,6):
        for i  in range(0,nStep):  
           for j in range(0,2): 
              for k in range(0,2): 
                 if iBin == 380 and nCat == 5: continue
                 if iBin > 380 and nCat > 3: continue
                 arguments.append("{} {} {} {} {} {} {} {} {}".format(nCat,local,inDir+"/",iBin,nCat,massMin+i,massMax-i,j,k))     
  with open("arguments.txt", "w") as args:
     args.write("\n".join(arguments)) 
  with open("run_script.sh", "w") as rs:
     rs.write(script) 

