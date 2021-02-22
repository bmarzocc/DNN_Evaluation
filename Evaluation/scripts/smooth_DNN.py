import ROOT
import argparse
import os
import math
from array import array

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
   return min
    
def isPositive(h):
   isPos = True
   for bin in range(1,h.GetNbinsX()+1):
     if h.GetBinContent(bin)<=0.: 
       isPos = False 
       break
   return isPos

def reduceTree(inTree, cut):
  small = inTree.CopyTree(str(cut))
  return small

def makeRatio(h_num,h_denom):
  h_ratio = h_num.Clone()
  h_ratio.Divide(h_denom) 
  return h_ratio

def MakeTree(inputTree, h_ratio, scale, ouputFile):
 outFile = ROOT.TFile(ouputFile, "RECREATE")
 inputTree.SetBranchStatus('bdt_weight',0)
 outTree = inputTree.CloneTree(0)
 bdt_weight = array('f', [0])
 _DNN_weight = outTree.Branch('bdt_weight', bdt_weight, 'bdt_weight/F')     
 nentries = inputTree.GetEntries()
 for i in range(0, nentries):
    inputTree.GetEntry(i)
    if h_ratio.GetBinContent(h_ratio.FindBin(inputTree.evalDNN))!=0.: 
        bdt_weight[0] = scale*float(h_ratio.GetBinContent(h_ratio.FindBin(inputTree.evalDNN)))
    else: bdt_weight[0] = scale 
    outTree.Fill() 
 outFile.cd()
 outTree.Write()
 outFile.Close()

def smoothing(h_bdt,method="SmoothSuper"):
 
 bin_min = h_bdt.GetBinCenter(1)-h_bdt.GetBinWidth(1)/2.
 bin_max = h_bdt.GetBinCenter(h_bdt.GetNbinsX())+h_bdt.GetBinWidth(h_bdt.GetNbinsX())/2.
 h_DNN_smooth = ROOT.TH1F(h_bdt.GetName()+"_smooth",h_bdt.GetName()+"_smooth",h_bdt.GetNbinsX(),float(bin_min),float(bin_max))
 h_DNN_smooth_rnd = ROOT.TH1F(h_bdt.GetName()+"_smooth_rnd",h_bdt.GetName()+"_smooth_rnd",h_bdt.GetNbinsX(),float(bin_min),float(bin_max))
 h_DNN_smooth_up = ROOT.TH1F(h_bdt.GetName()+"_smooth_up",h_bdt.GetName()+"_smooth_up",h_bdt.GetNbinsX(),float(bin_min),float(bin_max))
 h_DNN_smooth_down = ROOT.TH1F(h_bdt.GetName()+"_smooth_down",h_bdt.GetName()+"_smooth_down",h_bdt.GetNbinsX(),float(bin_min),float(bin_max))
 h_diff = ROOT.TH1F(h_bdt.GetName()+"_smoothing_Diff",h_bdt.GetName()+"_smoothing_Diff",200,-20.,20.)

 g_bdt = ROOT.TGraph()
 g_DNN_smooth = ROOT.TGraph() 
 smoother = ROOT.TGraphSmooth()

 for bin in range(0,h_bdt.GetNbinsX()): 
  g_bdt.SetPoint(bin,h_bdt.GetBinCenter(bin+1),h_bdt.GetBinContent(bin+1))
 if method=="SmoothLowess": g_DNN_smooth = smoother.SmoothLowess(g_bdt)
 elif method=="SmoothKern": g_DNN_smooth = smoother.SmoothKern(g_bdt)
 elif method=="SmoothSuper": g_DNN_smooth = smoother.SmoothSuper(g_bdt,"",0)
 else: 
    print "WARNING: unknown smoothing method!"
    return -1

 rnd = ROOT.TRandom()
 x = array('d', [0])
 y = array('d', [0])
 for bin in range(0,h_DNN_smooth.GetNbinsX()): 
  g_DNN_smooth.GetPoint(bin+1,x,y)
  h_DNN_smooth.SetBinContent(bin+1,y[0])
  h_DNN_smooth_rnd.SetBinContent(bin+1,rnd.Poisson(float(y[0])))
  
 h_DNN_smooth.Scale(h_bdt.Integral()/h_DNN_smooth.Integral())
 h_DNN_smooth_rnd.Scale(h_bdt.Integral()/h_DNN_smooth_rnd.Integral())

 for bin in range(0,h_DNN_smooth.GetNbinsX()): 
  y = h_DNN_smooth.GetBinContent(bin+1) 
  if y>=0.: 
     h_DNN_smooth_up.SetBinContent(bin+1,y+math.sqrt(y))
     if (y-math.sqrt(y))>0.: h_DNN_smooth_down.SetBinContent(bin+1,y-math.sqrt(y))
     else: h_DNN_smooth_down.SetBinContent(bin+1,0.)
  else:
     h_DNN_smooth_up.SetBinContent(bin+1,0.)
     h_DNN_smooth_down.SetBinContent(bin+1,0.)
  h_diff.Fill(y-h_bdt.GetBinContent(bin+1)) 

 return [h_DNN_smooth,h_DNN_smooth_up,h_DNN_smooth_down,h_DNN_smooth_rnd,h_diff] 

def compareHistos(hist_data_tmp,hist_bkg_tmp,name,rebin):

   ROOT.gStyle.SetOptStat(0000)
 
   hist_data = hist_data_tmp.Clone()
   hist_data.SetName(hist_data_tmp.GetName()+'_Rebin') 
   hist_data.Rebin(rebin)

   hist_bkg = hist_bkg_tmp.Clone()
   hist_bkg.SetName(hist_bkg_tmp.GetName()+'_Rebin') 
   hist_bkg.Rebin(rebin)
  
   hist_data.SetLineColor(ROOT.kBlack)
   hist_data.SetMarkerColor(ROOT.kBlack)
   hist_data.SetMarkerStyle(20)
   hist_bkg.SetLineColor(ROOT.kBlack)

   #hist_bkg.Scale(hist_data.Integral()/hist_bkg.Integral())

   min = nonZeroMin(hist_bkg)
   if min>nonZeroMin(hist_data): min = nonZeroMin(hist_data)
   max = hist_bkg.GetMaximum()
   if max<hist_data.GetMaximum(): max = hist_data.GetMaximum()
   #hist_bkg.GetYaxis().SetRangeUser(min*0.5,max*2.)
   hist_bkg.GetYaxis().SetRangeUser(3.,200.)

   c = ROOT.TCanvas()
   #if isPositive(hist_bkg) and isPositive(hist_data): c.SetLogy()
   c.SetLogy()
   hist_bkg.Draw("HIST") 
   hist_data.Draw("P,same")
   c.SaveAs(name+".png","png") 
   c.SaveAs(name+".pdf","pdf") 

   ROOT.gStyle.SetOptStat(1111)

def drawHistos(hist,hist_smooth,hist_smooth_up,hist_smooth_down,name):

   ROOT.gStyle.SetOptStat(0000)

   mins = [float(nonZeroMin(hist)),float(nonZeroMin(hist_smooth)),float(nonZeroMin(hist_smooth_up)),float(nonZeroMin(hist_smooth_down))]
   maxs = [float(hist.GetMaximum()),float(hist_smooth.GetMaximum()),float(hist_smooth_up.GetMaximum()),float(hist_smooth_down.GetMaximum())]
   
   minimum = findMin(mins)
   maximum = findMax(maxs)
   hist.SetLineColor(ROOT.kBlack)
   hist_smooth.SetLineColor(ROOT.kRed)
   hist_smooth_up.SetLineColor(ROOT.kGreen)
   hist_smooth_down.SetLineColor(ROOT.kBlue)
   hist.GetYaxis().SetRangeUser(minimum*0.5,2.*maximum)
   hist.GetXaxis().SetTitle('evalDNN')
   
   title = name
   hist.SetTitle(title.replace('h_',''))

   leg = ROOT.TLegend(0.70,0.7,0.85,0.88)
   leg.SetFillColor(ROOT.kWhite)
   leg.SetFillStyle(1000)
   leg.SetLineWidth(0)
   leg.SetLineColor(ROOT.kWhite)
   leg.SetTextFont(42)
   leg.SetTextSize(0.035)
   leg.AddEntry(hist_smooth_up,"Smoothing + #sigma","L")
   leg.AddEntry(hist_smooth,"Smoothing ","L")
   leg.AddEntry(hist_smooth_down,"Smoothing - #sigma","L")
   
   c = ROOT.TCanvas()
   #if isPositive(hist) and isPositive(hist_smooth) and isPositive(hist_smooth_up) and isPositive(hist_smooth_down): c.SetLogy()
   c.SetLogy()
   hist.Draw("HIST") 
   hist_smooth.Draw("HIST,same")
   hist_smooth_up.Draw("HIST,same")
   hist_smooth_down.Draw("HIST,same")
   leg.Draw("same")
   c.SaveAs(name+".png","png") 
   c.SaveAs(name+".pdf","pdf") 

   ROOT.gStyle.SetOptStat(1111)

def drawHisto(hist,name):

   ROOT.gStyle.SetOptStat(1111)

   hist.SetLineColor(ROOT.kBlack)
   
   c = ROOT.TCanvas()
   hist.Draw("HIST") 
   c.SaveAs(name+".png","png") 
   c.SaveAs(name+".pdf","pdf") 

if __name__ == '__main__': 

 ROOT.gROOT.SetBatch(ROOT.kTRUE)

 parser =  argparse.ArgumentParser(description='smooth DNN')
 parser.add_argument('-d', '--inDir', dest='inDir', required=True, type=str)
 parser.add_argument('-n', '--nBins', dest='nBins', required=False, type=int)
 parser.add_argument('-m', '--min', dest='min', required=False, type=float)
 parser.add_argument('-M', '--max', dest='max', required=False, type=float)
 
 args = parser.parse_args()
 inDir = args.inDir
 #inDir = '/eos/user/b/bmarzocc/HHWWgg/January_2021_Production/HHWWyyDNN_binary_noHgg_BalanceYields_allBkgs/'

 nBins = 100
 #print args.nBins,args.min,args.max
 if args.nBins: nBins = args.nBins
 min = 0.1
 if args.min!=0.1: min = args.min
 max = 1.
 if args.max!=1.: max = args.max
 
 print "inDir:",inDir
 print "nBins:",nBins
 print "Min:",min
 print "Max:",max
 
 histo_scale = ROOT.TH1F("histo_scale","",100000,-1.1,1.)
 Cut_noMass = '( evalDNN>'+str(min)+' )'
 Cut_SR = '( CMS_hgg_mass>100. && CMS_hgg_mass<180. && (CMS_hgg_mass > 115 && CMS_hgg_mass < 135) && evalDNN>'+str(min)+' )'
 Cut_SB = '( CMS_hgg_mass>100. && CMS_hgg_mass<180. && !(CMS_hgg_mass > 115 && CMS_hgg_mass < 135) && evalDNN>'+str(min)+' )'

 h_DNN_signal_SB_2017 = ROOT.TH1F("h_DNN_signal_SB_2017","h_DNN_signal_SB_2017",int(nBins),float(min),float(max))
 h_DNN_signal_SR_2017 = ROOT.TH1F("h_DNN_signal_SR_2017","h_DNN_signal_SR_2017",int(nBins),float(min),float(max)) 
 h_DNN_data_SB_2017 = ROOT.TH1F("h_DNN_data_SB_2017","h_DNN_data_SB_2017",int(nBins),float(min),float(max))  
 
 diffBins = nBins
 h_DNN_data_SB_2017_diffBins = ROOT.TH1F("h_DNN_data_SB_2017_diffBins","h_DNN_data_SB_2017_diffBins",diffBins,float(min),float(max))  
 h_DNN_bkg_SB_2017_diffBins = ROOT.TH1F("h_DNN_bkg_SB_2017_diffBins","h_DNN_bkg_SB_2017_diffBins",diffBins,float(min),float(max)) 

 h_DNN_ggHtoGG_SR_2017 = ROOT.TH1F("h_DNN_ggHtoGG_SR_2017","h_DNN_ggHtoGG_SR_2017",int(nBins),float(min),float(max))
 h_DNN_VBFHtoGG_SR_2017 = ROOT.TH1F("h_DNN_VBFHtoGG_SR_2017","h_DNN_VBFHtoGG_SR_2017",int(nBins),float(min),float(max))  
 h_DNN_VHtoGG_SR_2017 = ROOT.TH1F("h_DNN_VHtoGG_SR_2017","h_DNN_VHtoGG_SR_2017",int(nBins),float(min),float(max)) 
 h_DNN_ttHtoGG_SR_2017 = ROOT.TH1F("h_DNN_ttHtoGG_SR_2017","h_DNN_ttHtoGG_SR_2017",int(nBins),float(min),float(max))  
 
 ### 2017 ###
 lumi_2017 = 41.5

 histo_scale.Reset() 
 sig_tree_2017 = ROOT.TChain()
 sig_tree_2017.AddFile(inDir+'/GluGluToHHTo2G2Qlnu_node_cHHH1_2017_HHWWggTag_0_MoreVars.root/GluGluToHHTo2G2Qlnu_node_cHHH1_13TeV_HHWWggTag_0_v1')
 sig_tree_2017.Draw("Leading_Photon_MVA<-1.?-1.1:Leading_Photon_MVA>>histo_scale","weight*0.441*0.00097*31.049*"+Cut_SR)
 sig_scale_2017 = float(histo_scale.Integral())
 sig_tree_2017.Draw("evalDNN>>h_DNN_signal_SB_2017",str(lumi_2017)+"*weight*0.441*0.00097*31.049*"+Cut_SB)  
 sig_tree_2017.Draw("evalDNN>>h_DNN_signal_SR_2017",str(lumi_2017)+"*weight*0.441*0.00097*31.049*"+Cut_SR) 

 ### HtoGG Bkgs ###
 ggHtoGG_tree_2017 = ROOT.TChain()
 ggHtoGG_tree_2017.AddFile(inDir+'/GluGluHToGG_2017_HHWWggTag_0_MoreVars.root/ggh_125_13TeV_HHWWggTag_0_v1')
 ggHtoGG_tree_2017.Draw("evalDNN>>h_DNN_ggHtoGG_SR_2017",str(lumi_2017)+"*weight*"+Cut_SR)  
 VBFHtoGG_tree_2017 = ROOT.TChain()
 VBFHtoGG_tree_2017.AddFile(inDir+'/VBFHToGG_2017_HHWWggTag_0_MoreVars.root/vbf_125_13TeV_HHWWggTag_0_v1')
 VBFHtoGG_tree_2017.Draw("evalDNN>>h_DNN_VBFHtoGG_SR_2017",str(lumi_2017)+"*weight*"+Cut_SR)
 VHtoGG_tree_2017 = ROOT.TChain()
 VHtoGG_tree_2017.AddFile(inDir+'/VHToGG_2017_HHWWggTag_0_MoreVars.root/wzh_125_13TeV_HHWWggTag_0_v1')
 VHtoGG_tree_2017.Draw("evalDNN>>h_DNN_VHtoGG_SR_2017",str(lumi_2017)+"*weight*"+Cut_SR) 
 ttHJetToGG_tree_2017 = ROOT.TChain()
 ttHJetToGG_tree_2017.AddFile(inDir+'/ttHJetToGG_2017_HHWWggTag_0_MoreVars.root/tth_125_13TeV_HHWWggTag_0_v1')
 ttHJetToGG_tree_2017.Draw("evalDNN>>h_DNN_ttHtoGG_SR_2017",str(lumi_2017)+"*weight*"+Cut_SR)   
 
 histo_scale.Reset() 
 data_tree_2017 = ROOT.TChain()
 data_tree_2017.AddFile(inDir+'/Data_2017_HHWWggTag_0_MoreVars.root/Data_13TeV_HHWWggTag_0_v1') 
 data_tree_2017 = reduceTree(data_tree_2017,Cut_noMass)
 data_tree_2017.Draw("Leading_Photon_MVA<-1.?-1.1:Leading_Photon_MVA>>histo_scale",Cut_SB)
 data_scale_2017 = float(histo_scale.Integral())
 data_tree_2017.Draw("evalDNN>>h_DNN_data_SB_2017",Cut_SB)
 data_tree_2017.Draw("evalDNN>>h_DNN_data_SB_2017_diffBins",Cut_SB)
 
 #Bkgs MC samples
 treeNames = [
   #'DiPhotonJetsBox_M40_80_HHWWggTag_0_MoreVars.root/DiPhotonJetsBox_M40_80_Sherpa_13TeV_HHWWggTag_0', #
   'DiPhotonJetsBox_MGG-80toInf_HHWWggTag_0_MoreVars.root/DiPhotonJetsBox_MGG_80toInf_13TeV_Sherpa_13TeV_HHWWggTag_0',
   #'GJet_Pt-20to40_HHWWggTag_0_MoreVars.root/GJet_Pt_20to40_DoubleEMEnriched_MGG_80toInf_TuneCP5_13TeV_Pythia8_13TeV_HHWWggTag_0', #
   #'GJet_Pt-20toInf_HHWWggTag_0_MoreVars.root/GJet_Pt_20toInf_DoubleEMEnriched_MGG_40to80_TuneCP5_13TeV_Pythia8_13TeV_HHWWggTag_0', #
   'GJet_Pt-40toInf_HHWWggTag_0_MoreVars.root/GJet_Pt_40toInf_DoubleEMEnriched_MGG_80toInf_TuneCP5_13TeV_Pythia8_13TeV_HHWWggTag_0',
   #'QCD_Pt-30to40_HHWWggTag_0_MoreVars.root/QCD_Pt_30to40_DoubleEMEnriched_MGG_80toInf_TuneCP5_13TeV_Pythia8_13TeV_HHWWggTag_0', #
   #'QCD_Pt-30toInf_HHWWggTag_0_MoreVars.root/QCD_Pt_30toInf_DoubleEMEnriched_MGG_40to80_TuneCP5_13TeV_Pythia8_13TeV_HHWWggTag_0', #
   #'QCD_Pt-40toInf_HHWWggTag_0_MoreVars.root/QCD_Pt_40toInf_DoubleEMEnriched_MGG_80toInf_TuneCP5_13TeV_Pythia8_13TeV_HHWWggTag_0', #
   #'DYJetsToLL_M-50_HHWWggTag_0_MoreVars.root/DYJetsToLL_M_50_TuneCP5_13TeV_amcatnloFXFX_pythia8_13TeV_HHWWggTag_0', #
   'TTGG_0Jets_HHWWggTag_0_MoreVars.root/TTGG_0Jets_TuneCP5_13TeV_amcatnlo_madspin_pythia8_13TeV_HHWWggTag_0',
   'TTGJets_TuneCP5_HHWWggTag_0_MoreVars.root/TTGJets_TuneCP5_13TeV_amcatnloFXFX_madspin_pythia8_13TeV_HHWWggTag_0',
   #'TTJets_HT-600to800_HHWWggTag_0_MoreVars.root/TTJets_HT_600to800_TuneCP5_13TeV_madgraphMLM_pythia8_13TeV_HHWWggTag_0', #
   #'TTJets_HT-800to1200_HHWWggTag_0_MoreVars.root/TTJets_HT_800to1200_TuneCP5_13TeV_madgraphMLM_pythia8_13TeV_HHWWggTag_0', #
   #'TTJets_HT-1200to2500_HHWWggTag_0_MoreVars.root/TTJets_HT_1200to2500_TuneCP5_13TeV_madgraphMLM_pythia8_13TeV_HHWWggTag_0', #
   #'TTJets_HT-2500toInf_HHWWggTag_0_MoreVars.root/TTJets_HT_2500toInf_TuneCP5_13TeV_madgraphMLM_pythia8_13TeV_HHWWggTag_0', #
   'ttWJets_HHWWggTag_0_MoreVars.root/ttWJets_TuneCP5_13TeV_madgraphMLM_pythia8_13TeV_HHWWggTag_0',
   'TTJets_TuneCP5_extra_HHWWggTag_0_MoreVars.root/TTJets_TuneCP5_13TeV_amcatnloFXFX_pythia8_13TeV_HHWWggTag_0',
   #'W1JetsToLNu_LHEWpT_0-50_HHWWggTag_0_MoreVars.root/W1JetsToLNu_LHEWpT_0_50_TuneCP5_13TeV_amcnloFXFX_pythia8_13TeV_HHWWggTag_0', #
   'W1JetsToLNu_LHEWpT_50-150_HHWWggTag_0_MoreVars.root/W1JetsToLNu_LHEWpT_50_150_TuneCP5_13TeV_amcnloFXFX_pythia8_13TeV_HHWWggTag_0',
   'W1JetsToLNu_LHEWpT_150-250_HHWWggTag_0_MoreVars.root/W1JetsToLNu_LHEWpT_150_250_TuneCP5_13TeV_amcnloFXFX_pythia8_13TeV_HHWWggTag_0',
   'W1JetsToLNu_LHEWpT_250-400_HHWWggTag_0_MoreVars.root/W1JetsToLNu_LHEWpT_250_400_TuneCP5_13TeV_amcnloFXFX_pythia8_13TeV_HHWWggTag_0',
   'W1JetsToLNu_LHEWpT_400-inf_HHWWggTag_0_MoreVars.root/W1JetsToLNu_LHEWpT_400_inf_TuneCP5_13TeV_amcnloFXFX_pythia8_13TeV_HHWWggTag_0',
   #'W2JetsToLNu_LHEWpT_0-50_HHWWggTag_0_MoreVars.root/W2JetsToLNu_LHEWpT_0_50_TuneCP5_13TeV_amcnloFXFX_pythia8_13TeV_HHWWggTag_0', #	
   'W2JetsToLNu_LHEWpT_50-150_HHWWggTag_0_MoreVars.root/W2JetsToLNu_LHEWpT_50_150_TuneCP5_13TeV_amcnloFXFX_pythia8_13TeV_HHWWggTag_0',
   'W2JetsToLNu_LHEWpT_150-250_HHWWggTag_0_MoreVars.root/W2JetsToLNu_LHEWpT_150_250_TuneCP5_13TeV_amcnloFXFX_pythia8_13TeV_HHWWggTag_0',
   'W2JetsToLNu_LHEWpT_250-400_HHWWggTag_0_MoreVars.root/W2JetsToLNu_LHEWpT_250_400_TuneCP5_13TeV_amcnloFXFX_pythia8_13TeV_HHWWggTag_0',
   'W2JetsToLNu_LHEWpT_400-inf_HHWWggTag_0_MoreVars.root/W2JetsToLNu_LHEWpT_400_inf_TuneCP5_13TeV_amcnloFXFX_pythia8_13TeV_HHWWggTag_0',
   #'W3JetsToLNu_HHWWggTag_0_MoreVars.root/W3JetsToLNu_TuneCP5_13TeV_madgraphMLM_pythia8_13TeV_HHWWggTag_0', #
   #'W4JetsToLNu_HHWWggTag_0_MoreVars.root/W4JetsToLNu_TuneCP5_13TeV_madgraphMLM_pythia8_13TeV_HHWWggTag_0', #
   'WGGJets_HHWWggTag_0_MoreVars.root/WGGJets_TuneCP5_13TeV_madgraphMLM_pythia8_13TeV_HHWWggTag_0',
   #'WGJJToLNuGJJ_EWK_HHWWggTag_0_MoreVars.root/WGJJToLNuGJJ_EWK_aQGC_FS_FM_TuneCP5_13TeV_madgraph_pythia8_13TeV_HHWWggTag_0',
   'WGJJToLNu_EWK_QCD_HHWWggTag_0_MoreVars.root/WGJJToLNu_EWK_QCD_TuneCP5_13TeV_madgraph_pythia8_13TeV_HHWWggTag_0', #
   #'WWTo1L1Nu2Q_HHWWggTag_0_MoreVars.root/WWTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8_13TeV_HHWWggTag_0', #
   #'WW_TuneCP5_HHWWggTag_0_MoreVars.root/WW_TuneCP5_13TeV_pythia8_13TeV_HHWWggTag_0', #
   'GluGluHToGG_2017_HHWWggTag_0_MoreVars.root/ggh_125_13TeV_HHWWggTag_0_v1',
   'VBFHToGG_2017_HHWWggTag_0_MoreVars.root/vbf_125_13TeV_HHWWggTag_0_v1',
   'VHToGG_2017_HHWWggTag_0_MoreVars.root/wzh_125_13TeV_HHWWggTag_0_v1', 
   'ttHJetToGG_2017_HHWWggTag_0_MoreVars.root/tth_125_13TeV_HHWWggTag_0_v1' 
 ]

 histo_scale.Reset() 
 bkg_tree_2017 = ROOT.TChain()
 for tree in treeNames: 
   bkg_tree_2017.AddFile(inDir+'/'+tree)
 bkg_tree_2017 = reduceTree(bkg_tree_2017,Cut_noMass)
 bkg_tree_2017.Draw("Leading_Photon_MVA<-1.?-1.1:Leading_Photon_MVA>>histo_scale","weight*"+Cut_SB)
 bkg_scale_2017 = float(histo_scale.Integral())
 bkg_tree_2017.Draw("evalDNN>>h_DNN_bkg_SB_2017_diffBins",str(data_scale_2017/bkg_scale_2017)+"*weight*"+Cut_SB)

 print "2017 Data/bkg SB scale:",data_scale_2017/bkg_scale_2017

 h_DNN_signal_SB = h_DNN_signal_SB_2017.Clone()
 h_DNN_signal_SB.SetName('h_DNN_signal_SB')
 h_DNN_signal_SB.SetTitle('h_DNN_signal_SB')

 h_DNN_signal_SR = h_DNN_signal_SR_2017.Clone()
 h_DNN_signal_SR.SetName('h_DNN_signal_SR')
 h_DNN_signal_SR.SetTitle('h_DNN_signal_SR')

 h_DNN_data_SB = h_DNN_data_SB_2017.Clone()
 h_DNN_data_SB.SetName('h_DNN_data_SB')
 h_DNN_data_SB.SetTitle('h_DNN_data_SB')
 
 h_DNN_data_SB_diffBins = h_DNN_data_SB_2017_diffBins.Clone()
 h_DNN_data_SB_diffBins.SetName('h_DNN_data_SB_diffBins')
 h_DNN_data_SB_diffBins.SetTitle('h_DNN_data_SB_diffBins')

 h_DNN_bkg_SB_diffBins = h_DNN_bkg_SB_2017_diffBins.Clone()
 h_DNN_bkg_SB_diffBins.SetName('h_DNN_bkg_SB_diffBins')
 h_DNN_bkg_SB_diffBins.SetTitle('h_DNN_bkg_SB_diffBins')

 h_DNN_ratio_SB = makeRatio(h_DNN_data_SB_diffBins,h_DNN_bkg_SB_diffBins)

 compareHistos(h_DNN_data_SB_diffBins,h_DNN_bkg_SB_diffBins,"h_DNN_SB",1)

 h_DNN_bkg_SB_weighted_2017 = ROOT.TH1F("h_DNN_bkg_SB_weighted_2017","h_DNN_bkg_SB_weighted_2017",int(nBins),float(min),float(max))
 h_DNN_bkg_SB_weighted_2017_diffBins = ROOT.TH1F("h_DNN_bkg_SB_weighted_2017_diffBins","h_DNN_bkg_SB_weighted_2017_diffBins",diffBins,float(min),float(max))

 h_DNN_bkg_SR_weighted_2017 = ROOT.TH1F("h_DNN_bkg_SR_weighted_2017","h_DNN_bkg_SR_weighted_2017",int(nBins),float(min),float(max))
 
 print "Fill 2017 bkg reweighting..."
 bkg_tree_2017_bdtWeight = ROOT.TChain()
 MakeTree(bkg_tree_2017, h_DNN_ratio_SB, data_scale_2017/bkg_scale_2017, 'file.root')
 bkg_tree_2017_bdtWeight.AddFile('file.root/'+str(treeNames[0].split('/')[1]))
 #bkg_tree_2017_bdtWeight.Draw("evalDNN>>h_DNN_bkg_SB_weighted_2017","bdt_weight*weight*"+Cut_SB)
 #bkg_tree_2017_bdtWeight.Draw("evalDNN>>h_DNN_bkg_SB_weighted_2017_diffBins","bdt_weight*weight*"+Cut_SB)
 #bkg_tree_2017_bdtWeight.Draw("evalDNN>>h_DNN_bkg_SR_weighted_2017","bdt_weight*weight*"+Cut_SR)
 bkg_tree_2017_bdtWeight.Draw("evalDNN>>h_DNN_bkg_SB_weighted_2017",str(data_scale_2017/bkg_scale_2017)+"*weight*"+Cut_SB)
 bkg_tree_2017_bdtWeight.Draw("evalDNN>>h_DNN_bkg_SB_weighted_2017_diffBins",str(data_scale_2017/bkg_scale_2017)+"*weight*"+Cut_SB)
 bkg_tree_2017_bdtWeight.Draw("evalDNN>>h_DNN_bkg_SR_weighted_2017",str(data_scale_2017/bkg_scale_2017)+"*weight*"+Cut_SR)

 h_DNN_bkg_SB_weighted = h_DNN_bkg_SB_weighted_2017.Clone()
 h_DNN_bkg_SB_weighted.SetName('h_DNN_bkg_SB_weighted')
 h_DNN_bkg_SB_weighted.SetTitle('h_DNN_bkg_SB_weighted')

 h_DNN_bkg_SB_weighted_diffBins = h_DNN_bkg_SB_weighted_2017_diffBins.Clone()
 h_DNN_bkg_SB_weighted_diffBins.SetName('h_DNN_bkg_SB_weighted_diffBins')
 h_DNN_bkg_SB_weighted_diffBins.SetTitle('h_DNN_bkg_SB_weighted_diffBins')

 h_DNN_bkg_SR_weighted = h_DNN_bkg_SR_weighted_2017.Clone()
 h_DNN_bkg_SR_weighted.SetName('h_DNN_bkg_SR_weighted')
 h_DNN_bkg_SR_weighted.SetTitle('h_DNN_bkg_SR_weighted')

 compareHistos(h_DNN_data_SB_diffBins,h_DNN_bkg_SB_weighted_diffBins,"h_DNN_SB_weighted",1)

 print "Smooth distributions..."
 algos = ['SmoothSuper']

 for algo in algos:
   outFile = ROOT.TFile(inDir+'/DNN_Histos_smoothing_'+algo+'_bins'+str(nBins)+'.root',"RECREATE")
   outFile.cd()
   hist_smooth = smoothing(h_DNN_bkg_SR_weighted,algo)
   if hist_smooth!=-1: 
     drawHistos(h_DNN_bkg_SR_weighted,hist_smooth[0],hist_smooth[1],hist_smooth[2],h_DNN_bkg_SR_weighted.GetName()+"_smoothing_"+algo+"_nBins_"+str(nBins))
     drawHisto(hist_smooth[4],h_DNN_bkg_SR_weighted.GetName()+"_smoothing_"+algo+"_Diff_nBins_"+str(nBins)) 
     h_DNN_bkg_SR_weighted.Write()
     hist_smooth[0].Write() 
     hist_smooth[1].Write() 
     hist_smooth[2].Write() 
   hist_smooth = smoothing(h_DNN_bkg_SB_weighted,algo)
   if hist_smooth!=-1: 
     drawHistos(h_DNN_bkg_SB_weighted,hist_smooth[0],hist_smooth[1],hist_smooth[2],h_DNN_bkg_SB_weighted.GetName()+"_smoothing_"+algo+"_nBins_"+str(nBins))
     drawHisto(hist_smooth[4],h_DNN_bkg_SB_weighted.GetName()+"_smoothing_"+algo+"_Diff_nBins_"+str(nBins)) 
     h_DNN_bkg_SB_weighted.Write()
     hist_smooth[0].Write() 
     hist_smooth[1].Write() 
     hist_smooth[2].Write()  
   hist_smooth = smoothing(h_DNN_data_SB,algo)
   if hist_smooth!=-1: 
     drawHistos(h_DNN_data_SB,hist_smooth[0],hist_smooth[1],hist_smooth[2],h_DNN_data_SB.GetName()+"_smoothing_"+algo+"_nBins_"+str(nBins))
     drawHisto(hist_smooth[4],h_DNN_data_SB.GetName()+"_smoothing_"+algo+"_Diff_nBins_"+str(nBins)) 
     h_DNN_data_SB.Write()
     hist_smooth[0].Write() 
     hist_smooth[1].Write() 
     hist_smooth[2].Write() 
   h_DNN_signal_SR.Write()
   h_DNN_signal_SB.Write()
   h_DNN_data_SB_diffBins.Write()
   h_DNN_bkg_SB_diffBins.Write()
   h_DNN_bkg_SB_weighted_diffBins.Write()
   h_DNN_ggHtoGG_SR_2017.Write('h_DNN_ggHtoGG_SR')
   h_DNN_VBFHtoGG_SR_2017.Write('h_DNN_VBFHtoGG_SR')
   h_DNN_VHtoGG_SR_2017.Write('h_DNN_VHtoGG_SR')
   h_DNN_ttHtoGG_SR_2017.Write('h_DNN_ttHtoGG_SR')
   outFile.Close()

