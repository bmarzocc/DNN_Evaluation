#!/usr/bin/python
import numpy as n
import ROOT 
import sys, getopt
from array import array
from optparse import OptionParser
import operator
import math  

#mu = 2*0.441*0.00097*31.049
mu = 1.

def findMin(vec):
  min = 999.
  for i in vec:
    if i<min: min=i
  return min  

def findMax(vec):
  max = -999.
  for i in vec:
    if i>max: max=i
  return max    

def nonZeroMin(h):
   min = 999.
   for bin in range(1,h.GetNbinsX()+1):
      if h.GetBinContent(bin)>0. and h.GetBinContent(bin)<min: min = h.GetBinContent(bin)

def reduceTree(inTree, cut):
  small = inTree.CopyTree(str(cut))
  return small

def computeSignificance(s,b,m,d,d_noSmooth):
  significance = ((2*(s+b)*math.log(1+(s/b))) - 2*s) 
  if significance>0. and d_noSmooth>=8. and b>0.: return math.sqrt(significance)
  #significance = s/math.sqrt(b)
  #if b>0: return significance
  else: return -999. 

#def computeSignificance(s,b,m,d,d_noSmooth):
#  significance=-999.
#  if b>0 : significance = s/math.sqrt(b)
#  if significance>0. and d_noSmooth>=8. and b>0.: return significance
#  if significance>0. and b>0. and d_noSmooth>0.: return math.sqrt(significance)
#  else: return -999.  

def sumSignificance(partition, h_sig_SR, h_bkg_SR, h_bkg_SB, h_data_SB,h_data_SB_noSmooth):
  sum = 0.
  for pair in partition:
    s = mu*h_sig_SR.Integral(pair[0],pair[1])   
    b = h_bkg_SR.Integral(pair[0],pair[1])
    m = h_bkg_SB.Integral(pair[0],pair[1])
    d = h_data_SB.Integral(pair[0],pair[1])
    d_noSmooth = h_data_SB_noSmooth.Integral(pair[0],pair[1])
    significance = computeSignificance(s,b,m,d,d_noSmooth)
    #print h_sig_SR.GetBinCenter(pair[0])-h_DNN_signal_SR.GetBinWidth(pair[0])/2.,significance,b 
    if significance>0.: sum += significance*significance   
    else: return -999.  
  return math.sqrt(sum)

def drawHistos(hist_sig, hist_bkg, isSB, name):

   ROOT.gStyle.SetOptStat(0000)
 
   if not isSB:
     hist_sig.SetLineColor(ROOT.kRed+1)
     hist_sig.SetMarkerColor(ROOT.kRed+1)
     hist_sig.SetMarkerStyle(20)
     hist_sig.SetLineColor(ROOT.kRed+1)
     hist_sig.SetFillColor(ROOT.kRed+1) 
   else:
     hist_sig.SetLineColor(ROOT.kBlack)
     hist_sig.SetMarkerColor(ROOT.kBlack)
     hist_sig.SetMarkerStyle(20)
     hist_sig.SetLineColor(ROOT.kBlack)
     hist_sig.SetFillColor(ROOT.kBlack) 

   hist_bkg.SetLineColor(ROOT.kCyan+2)
   hist_bkg.SetMarkerColor(ROOT.kCyan+2)
   hist_bkg.SetMarkerStyle(20)
   hist_bkg.SetLineColor(ROOT.kCyan+2)
   hist_bkg.SetFillColor(ROOT.kCyan+2) 
   
   hist_bkg.GetYaxis().SetRangeUser(hist_sig.GetMinimum()*0.5,hist_bkg.GetMaximum()*2.) 
   hist_bkg.SetTitle("")
   hist_bkg.GetXaxis().SetTitle("evalDNN")

   if not isSB:
     print "Bkg integral: ",hist_bkg.Integral() 
     print "Sig integral: ",hist_sig.Integral()
   else:
     print "Bkg integral: ",hist_bkg.Integral() 
     print "Data integral: ",hist_sig.Integral() 

   c = ROOT.TCanvas()
   c.SetLogy()
   hist_bkg.Draw("HIST") 
   if not isSB: hist_sig.Draw("HIST,same")
   else: hist_sig.Draw("P,same")
   c.SaveAs(name+".png","png") 
   c.SaveAs(name+".pdf","pdf") 

   ROOT.gStyle.SetOptStat(1111)

if __name__ == '__main__':

  ROOT.gROOT.SetBatch(ROOT.kTRUE)

  parser = OptionParser()
  parser.add_option( "-d", "--inDir",    dest="inDir",    default="",   type="string", help="inDir" )
  parser.add_option( "-n", "--nBins",    dest="nBins",    default=190,  type="int",    help="nBins" )
  parser.add_option( "-c", "--nCats",    dest="nCats",    default=5,    type="int",    help="nCats" )
  parser.add_option( "-s", "--smooth",   dest="smooth",   default=True)
  (options, args) = parser.parse_args()  

  nBins = options.nBins
  inDir = options.inDir
  nCats = options.nCats
  smooth = options.smooth
  #inDir = '/eos/user/b/bmarzocc/HHWWgg/January_2021_Production/HHWWyyDNN_binary_noHgg_BalanceYields_allBkgs/'
  #inDir = '/eos/user/b/bmarzocc/HHWWgg/January_2021_Production/HHWWyyDNN_binary_noHgg_BalanceYields_allBkgs_oddSignal/'

  print "inDir: ",inDir
  print "nBins: ",nBins
  print "nCats: ",nCats
  print "Smooth:",smooth 

  inFile = ROOT.TFile(inDir+"/DNN_Histos_smoothing_SmoothSuper_bins"+str(nBins)+".root","READ")

  h_DNN_signal_SR = inFile.Get("h_DNN_signal_SR")
  h_DNN_bkg_SR_weighted = inFile.Get("h_DNN_bkg_SR_weighted")
  h_DNN_bkg_SB_weighted = inFile.Get("h_DNN_bkg_SB_weighted")
  h_DNN_data_SB = inFile.Get("h_DNN_data_SB")
  if smooth==True: 
    h_DNN_bkg_SR_weighted_smooth = inFile.Get("h_DNN_bkg_SR_weighted_smooth")
    h_DNN_bkg_SB_weighted_smooth = inFile.Get("h_DNN_bkg_SB_weighted_smooth") 
    h_DNN_data_SB_smooth = inFile.Get("h_DNN_data_SB_smooth") 
  else:
    h_DNN_bkg_SR_weighted_smooth = inFile.Get("h_DNN_bkg_SR_weighted")
    h_DNN_bkg_SB_weighted_smooth = inFile.Get("h_DNN_bkg_SB_weighted") 
    h_DNN_data_SB_smooth = inFile.Get("h_DNN_data_SB") 
  h_DNN_ggHtoGG_SR = inFile.Get("h_DNN_ggHtoGG_SR") 
  h_DNN_VBFHtoGG_SR = inFile.Get("h_DNN_VBFHtoGG_SR") 
  h_DNN_VHtoGG_SR = inFile.Get("h_DNN_VHtoGG_SR") 
  h_DNN_ttHtoGG_SR = inFile.Get("h_DNN_ttHtoGG_SR") 

 
  significance_final = -999.
  partition_final = []
  
  #1 categories
  if nCats == 1:

   for i in range(1,nBins+1):
       partition = [[i,nBins]]
       significance = sumSignificance(partition, h_DNN_signal_SR, h_DNN_bkg_SR_weighted_smooth, h_DNN_bkg_SB_weighted_smooth, h_DNN_data_SB_smooth, h_DNN_data_SB)
       if significance>significance_final:
         significance_final = significance
         partition_final = partition 
   
   print nCats," - Best category: ",h_DNN_signal_SR.GetBinCenter(partition_final[0][0])-h_DNN_signal_SR.GetBinWidth(partition_final[0][0])/2,"1. --->",significance_final    

  #2 categories
  elif nCats == 2:

   for i in range(1,nBins+1):
    for j in range(i+1,nBins+1): 
     partition = [[1,i],[j,nBins]]  
     if abs(i-j)==1: 
       #print partition 
       significance = sumSignificance(partition, h_DNN_signal_SR, h_DNN_bkg_SR_weighted_smooth, h_DNN_bkg_SB_weighted_smooth, h_DNN_data_SB_smooth, h_DNN_data_SB)
       if significance>significance_final:
         significance_final = significance
         partition_final = partition 
   
   print nCats," - Best categories: ",h_DNN_signal_SR.GetBinCenter(partition_final[0][0])-h_DNN_signal_SR.GetBinWidth(partition_final[0][0])/2,h_DNN_signal_SR.GetBinCenter(partition_final[1][0])-h_DNN_signal_SR.GetBinWidth(partition_final[1][0])/2,"1. --->",significance_final    
  
  #3 categories
  elif nCats == 3:

   for i in range(1,nBins+1):
    for j in range(i+1,nBins+1): 
     for k in range(j+1,nBins+1):  
      partition = [[1,i],[j,k-1],[k,nBins]] 
      if abs(i-j)==1: 
        #print partition 
        significance = sumSignificance(partition, h_DNN_signal_SR, h_DNN_bkg_SR_weighted_smooth, h_DNN_bkg_SB_weighted_smooth, h_DNN_data_SB_smooth, h_DNN_data_SB)
        if significance>significance_final:
          significance_final = significance
          partition_final = partition   
   
   print nCats," - Best categories: ",h_DNN_signal_SR.GetBinCenter(partition_final[0][0])-h_DNN_signal_SR.GetBinWidth(partition_final[0][0])/2, h_DNN_signal_SR.GetBinCenter(partition_final[1][0])-h_DNN_signal_SR.GetBinWidth(partition_final[1][0])/2, h_DNN_signal_SR.GetBinCenter(partition_final[2][0])-h_DNN_signal_SR.GetBinWidth(partition_final[2][0])/2, "1. --->",significance_final  
   
  #4 categories
  elif nCats == 4:

   for i in range(1,nBins+1):
    for j in range(i+1,nBins+1): 
     for k in range(j+1,nBins+1):  
      for d in range(k+1,nBins+1):  
       partition = [[1,i],[j,k-1],[k,d-1],[d,nBins]]   
       if abs(i-j)==1: 
         #print partition 
         significance = sumSignificance(partition, h_DNN_signal_SR, h_DNN_bkg_SR_weighted_smooth, h_DNN_bkg_SB_weighted_smooth, h_DNN_data_SB_smooth, h_DNN_data_SB)
         if significance>significance_final:
           significance_final = significance
           partition_final = partition   
 
   print "partition_final:",partition_final
   print nCats," - Best categories: ",h_DNN_signal_SR.GetBinCenter(partition_final[0][0])-h_DNN_signal_SR.GetBinWidth(partition_final[0][0])/2, h_DNN_signal_SR.GetBinCenter(partition_final[1][0])-h_DNN_signal_SR.GetBinWidth(partition_final[1][0])/2, h_DNN_signal_SR.GetBinCenter(partition_final[2][0])-h_DNN_signal_SR.GetBinWidth(partition_final[2][0])/2, h_DNN_signal_SR.GetBinCenter(partition_final[3][0])-h_DNN_signal_SR.GetBinWidth(partition_final[3][0])/2, "1. --->",significance_final  
  
  #5 categories
  elif nCats == 5:
   for i in range(1,nBins+1):
    for j in range(i+1,nBins+1): 
     for k in range(j+1,nBins+1):  
      for d in range(k+1,nBins+1):  
       for f in range(d+1,nBins+1):  
        partition = [[1,i],[j,k-1],[k,d-1],[d,f-1],[f,nBins]]    
        if abs(i-j)==1: 
          #print partition 
          significance = sumSignificance(partition, h_DNN_signal_SR, h_DNN_bkg_SR_weighted_smooth, h_DNN_bkg_SB_weighted_smooth, h_DNN_data_SB_smooth, h_DNN_data_SB)
          if significance>significance_final:
            significance_final = significance
            partition_final = partition 

   print nCats," - Best categories: ",h_DNN_signal_SR.GetBinCenter(partition_final[0][0])-h_DNN_signal_SR.GetBinWidth(partition_final[0][0])/2, h_DNN_signal_SR.GetBinCenter(partition_final[1][0])-h_DNN_signal_SR.GetBinWidth(partition_final[1][0])/2, h_DNN_signal_SR.GetBinCenter(partition_final[2][0])-h_DNN_signal_SR.GetBinWidth(partition_final[2][0])/2, h_DNN_signal_SR.GetBinCenter(partition_final[3][0])-h_DNN_signal_SR.GetBinWidth(partition_final[3][0])/2, h_DNN_signal_SR.GetBinCenter(partition_final[4][0])-h_DNN_signal_SR.GetBinWidth(partition_final[4][0])/2, "1. --->",significance_final     

  else: 
   print "Number of categories not supported, choose: 1, 2, 3, 4 or 5!"
   sys.exit()
  
  #final details
  outFileName = ""
  if smooth==True: outFileName = inDir+"/categorize_nBins_"+str(nBins)+"_nCat_"+str(nCats)+"_v2.txt"
  else: outFileName = inDir+"/categorize_nBins_"+str(nBins)+"_nCat_"+str(nCats)+"_v2_noSmooth.txt"
  outFile = open(outFileName,"w+") 
  print "Final details:"
  for pair in partition_final:
    s = mu*h_DNN_signal_SR.Integral(pair[0],pair[1])   
    b = h_DNN_bkg_SR_weighted_smooth.Integral(pair[0],pair[1])
    m = h_DNN_bkg_SB_weighted_smooth.Integral(pair[0],pair[1])
    d = h_DNN_data_SB_smooth.Integral(pair[0],pair[1])
    d_noSmooth = h_DNN_data_SB.Integral(pair[0],pair[1])
    significance = computeSignificance(s,b,m,d,d_noSmooth)
    print h_DNN_signal_SR.GetBinCenter(pair[0])-h_DNN_signal_SR.GetBinWidth(pair[0])/2., h_DNN_signal_SR.GetBinCenter(pair[1])+h_DNN_signal_SR.GetBinWidth(pair[1])/2., " --> Significance:", significance, " - N Sig:", s, "- N Bkg_SR:", b, "- N Bkg_SB:", m, "- N Data_SB:", d, "- N Data_SB (no smooth):", d_noSmooth
    outFile.write(str(h_DNN_signal_SR.GetBinCenter(pair[0])-h_DNN_signal_SR.GetBinWidth(pair[0])/2.))
    outFile.write("  ")
    outFile.write(str(h_DNN_signal_SR.GetBinCenter(pair[1])+h_DNN_signal_SR.GetBinWidth(pair[1])/2.))
    outFile.write(" Significance: %s"%(str(significance)) )
    outFile.write(" NSig: %s"%(s))
    outFile.write(" NBkg_SR: %s"%(b))
    outFile.write(" NBkg_SB: %s"%(m))
    outFile.write(" NData_SB: %s"%(d))
    outFile.write(" NData_SB (no smooth): %s"%(d_noSmooth))
    #outFile.write(" NggHtoGG_SR: %s"%(h_DNN_ggHtoGG_SR.Integral(pair[0],pair[1])))
    #outFile.write(" NVBFHtoGG_SR: %s"%(h_DNN_VBFHtoGG_SR.Integral(pair[0],pair[1])))
    #outFile.write(" NVHtoGG_SR: %s"%(h_DNN_VHtoGG_SR.Integral(pair[0],pair[1])))
    #outFile.write(" NttHtoGG_SR: %s"%(h_DNN_ttHtoGG_SR.Integral(pair[0],pair[1])))
    outFile.write("\n")
  outFile.write("\n")
  outFile.write("Tot_Significance: %s"%(significance_final))
  outFile.close()

  drawHistos(h_DNN_signal_SR, h_DNN_bkg_SR_weighted_smooth, False, "h_DNN_optimization_bins"+str(nBins)+"_SR")  
  drawHistos(h_DNN_data_SB, h_DNN_bkg_SB_weighted, True, "h_DNN_optimization_bins"+str(nBins)+"_SB")


