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
  parser.add_option( "-d", "--inDir",    dest="inDir",    default="",   type="string", help="inDir" )
  parser.add_option( "-n", "--nBins",    dest="nBins",    default=190,  type="int",    help="nBins" )
  parser.add_option( "-g", "--genMass",  dest="genMass",  default=60,   type="int",    help="genMass" )
  (options, args) = parser.parse_args()  

  nBins = options.nBins
  inDir = options.inDir
  mass = options.genMass
  #inDir = /eos/user/t/twamorka/h4g_fullRun2/TrainingApplied_9Dec2020/dataset_PhoMVA_manyKinVars_fullRun2_datamix_old_kinWeight_dataSBScaling_m60/

  print "Mass :",mass
  print "inDir:",inDir
  print "nBins:",nBins
  
  local = os.getcwd()
  if not os.path.isdir('error_m'+str(mass)): os.mkdir('error_m'+str(mass)) 
  if not os.path.isdir('output_m'+str(mass)): os.mkdir('output_m'+str(mass)) 
  if not os.path.isdir('log_m'+str(mass)): os.mkdir('log_m'+str(mass)) 
   
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
  condor = condor.replace('output/strips','output_m'+str(mass)+'/strips')
  condor = condor.replace('error/strips','error_m'+str(mass)+'/strips')
  condor = condor.replace('log/strips','log_m'+str(mass)+'/strips') 

  with open("condor_job.txt", "w") as cnd_out:
     cnd_out.write(condor)

  outputDir = os.getcwd()

  script = '''#!/bin/sh -e

JOBID=$1; 
LOCAL=$2; 
INPUTDIR=$3;
NBINS=$4;
NCATS=$5;

echo -e "evaluate"
eval `scramv1 ru -sh`

echo -e "Optimize significance";
python ${LOCAL}/optimizeCategories.py -d ${INPUTDIR}/ -n ${NBINS} -c ${NCATS}

echo -e "DONE";
'''
  arguments=[]
  for iBunch in range(1,6):
     arguments.append("{} {} {} {} {}".format(iBunch,local,inDir,nBins,iBunch))     
  with open("arguments.txt", "w") as args:
     args.write("\n".join(arguments)) 
  with open("run_script.sh", "w") as rs:
     rs.write(script) 

