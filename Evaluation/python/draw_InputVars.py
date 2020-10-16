#!/usr/bin/python
import numpy as n
from ROOT import *
from array import array
import operator
import math  
import sys
import os
import argparse
import random
from math import *

def drawHisto(h1,name,var):

   gStyle.SetOptStat(0000)

   h1.SetMarkerStyle(20)
   h1.SetMarkerColor(kBlack) 
   h1.SetLineColor(kBlack) 
   h1.SetLineWidth(2) 
   #h1.Scale(1./h1.Integral())
   h1.GetXaxis().SetTitle(var)
   
   maximum = 1.01*h1.GetMaximum()
   
   h1.GetYaxis().SetRangeUser(0.,maximum)
   c = TCanvas()
   h1.Draw("HIST")
   c.SaveAs(name+".png","png") 
   c.SaveAs(name+".pdf","pdf") 

   h1.GetYaxis().SetRangeUser(0.001,maximum*20.)
   c.SetLogy() 
   h1.Draw("HIST")
   c.SaveAs(name+"_log.png","png") 
   c.SaveAs(name+"_log.pdf","pdf") 

if __name__ == '__main__':

  gROOT.SetBatch(kTRUE)

  parser = argparse.ArgumentParser()
  parser.add_argument("-i", "--inputFile", type=str, help="inputFile", required=True)
  parser.add_argument("-t", "--inputTree", type=str, help="inputTree", required=True)
  parser.add_argument("-l", "--inputList", type=str, help="inputList", required=True)
  args = parser.parse_args()

  inFile = TFile(args.inputFile)
  tree = inFile.Get(args.inputTree)

  with open(args.inputList) as f_list:
     data_list = f_list.read()
  lines = data_list.splitlines() 
  for iLine,line in enumerate(lines):
     print iLine, line
     inputs = line.split()
     hist_tmp = TH1F("h_"+str(inputs[0]),str(inputs[0]),int(inputs[1]),float(inputs[2]),float(inputs[3]))
     tree.Draw(str(inputs[0])+">>h_"+str(inputs[0]))
     drawHisto(hist_tmp,str(inputs[0]),inputs[4])

  
