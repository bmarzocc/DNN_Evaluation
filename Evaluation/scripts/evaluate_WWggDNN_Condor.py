#!/usr/bin/python
import numpy as n
from ROOT import *
import sys, getopt
from array import array
import itertools
from optparse import OptionParser
import operator
import os

def replaceString1(fileName,inputFile):
  with open(fileName) as f:
    newText=f.read().replace('INPUTFILE', inputFile)
  with open(fileName, "w") as f:
    f.write(newText)

def replaceString2(fileName,node):
  with open(fileName) as f:
    newText=f.read().replace('NODE', "%.0f"%float(node))
  with open(fileName, "w") as f:
    f.write(newText)


if __name__ == '__main__':


  parser = OptionParser()
  parser.add_option( "-i", "--inList", dest="inList", default="", type="string", help="inList" )
  parser.add_option( "-n", "--node",   dest="node",   default="", type="string",    help="node" )
  (options, args) = parser.parse_args() 

  inList = options.inList
  node = options.node
  print "inList:",inList
  print "node:  ",node
  
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
    
+JobFlavour             = "workday"
+AccountingGroup        = "group_u_CMS.CAF.ALCA"
queue arguments from arguments.txt
'''

  with open("condor_job.txt", "w") as cnd_out:
     cnd_out.write(condor)

  outputDir = os.getcwd()

  script = '''#!/bin/sh -e

JOBID=$1; 
LOCAL=$2; 
CONFIG=$3

echo -e "Evaluate DNN"
cd ${LOCAL}/
eval `scramv1 ru -sh`
Evaluate_WWggDNN ${CONFIG}
rm ${CONFIG}

echo -e "DONE";
'''
  arguments=[]
  with open(str(inList)) as f_List:
    data_List = f_List.read()
  lines_List = data_List.splitlines() 
  for i,line in enumerate(lines_List):
    if(line.find("#") != -1):
       continue
    print "JobID ",i,": ",line  
    cfg_name = str('Evaluate_WWggDNN.py').replace('.py','_job'+str(i)+'_NodeNumber'+str(node)+'.py') 
    os.system('cp Evaluate_WWggDNN.py '+cfg_name)  
    replaceString1(cfg_name,line)
    replaceString2(cfg_name,node)
    arguments.append("{} {} {}".format(i,local,cfg_name))  

  with open("arguments.txt", "w") as args:
     args.write("\n".join(arguments)) 
  with open("run_script.sh", "w") as rs:
     rs.write(script) 

