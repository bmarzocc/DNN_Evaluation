import ROOT
import argparse
import os
import math
from array import array
from MyCMSStyle import *

def reduceTree(inTree, cut):
  small = inTree.CopyTree(str(cut))
  return small

def nonZeroMin(h):
   min = 999.
   for bin in range(1,h.GetNbinsX()+1):
      if h.GetBinContent(bin)>0. and h.GetBinContent(bin)<min: min = h.GetBinContent(bin)
   return min

def drawStack(h_bkg,h_stack,h_data,h_sig,leg,name,title,log):

   ROOT.gStyle.SetOptStat(0000)

   h_stackError = h_stack.Clone()
   h_stackError.SetFillStyle(3005)
   h_stackError.SetFillColor(12)
   h_stackError.SetMarkerSize(0)

   mins = [nonZeroMin(h_stack),nonZeroMin(h_data),nonZeroMin(h_sig)]
   maxs = [h_stack.GetMaximum(),h_data.GetMaximum(),h_sig.GetMaximum()]
   minimum = min(mins)
   maximum = max(maxs)
   
   if not log: h_data.GetYaxis().SetRangeUser(0.,2.*maximum) 
   else: h_data.GetYaxis().SetRangeUser(0.8*minimum,1500000.*maximum) 
   h_data.GetXaxis().SetTitle("")
   h_data.GetXaxis().SetLabelSize(0.04)
   h_data.GetXaxis().SetTitleSize(0.045)
   h_data.GetYaxis().SetTitle("Events")
   h_data.GetYaxis().SetTitleOffset(0.85)
   h_data.GetYaxis().SetTitleSize(0.05)

   c1 = 0
   cUp = 0
   cDown = 0

   if not log: c1 = ROOT.TCanvas("c1_"+str(name), "c1_"+str(name), 900, 800) 
   else: c1 = ROOT.TCanvas("c1_"+str(name)+"_log", "c1_"+str(name)+"_log", 900, 800) 
   c1.cd()   
    
   if not log: cUp  = ROOT.TPad("pad_0_"+str(name),"pad_0_"+str(name),0.00,0.30,1.00,1.00)
   else: cUp  = ROOT.TPad("pad_0_"+str(name)+"_log","pad_0_"+str(name)+"_log",0.00,0.30,1.00,1.00) 
   SetPadStyle(cUp)
   
   if not log: cDown = ROOT.TPad("pad_1_"+str(name),"pad_1_"+str(name),0.00,0.00,1.00,0.30)
   else: cDown = ROOT.TPad("pad_1_"+str(name)+"_log","pad_1_"+str(name)+"_log",0.00,0.00,1.00,0.30)
   #SetPadStyle(cDown) 

   cUp.SetTopMargin(0.015)  
   cUp.SetBottomMargin(0.06) 
   cDown.SetTopMargin(0.1) 
   cDown.SetBottomMargin(0.25)

   cUp.Draw()
   cDown.Draw()  

   cUp.cd()
   cUp.SetGridx()

   if log: cUp.SetLogy()
   h_data.Draw("P") 
   h_bkg.Draw("HIST,same")
   h_stackError.Draw("E2,same")
   h_data.Draw("P,same")
   h_sig.Draw("Hist,same") 
   leg.Draw("same")
   
   ROOT.gPad.Update()
   cDown.cd()
   cDown.SetGrid()
   
   
   h_ratio = h_data.Clone()
   if not log: h_ratio.SetName("h_ratio_"+str(name))
   else : h_ratio.SetName("h_ratio_"+str(name)+"_log") 
   h_ratio.Divide(h_stack)
   h_ratio.GetXaxis().SetTitle(title)
   h_ratio.GetXaxis().SetTitleSize(0.1)
   h_ratio.GetXaxis().SetLabelSize(0.095)
   h_ratio.GetYaxis().SetTitle("Data/MC")
   h_ratio.GetYaxis().SetTitleOffset(0.45)
   h_ratio.GetYaxis().SetTitleSize(0.09)
   h_ratio.GetYaxis().SetLabelSize(0.06)
   h_ratio.SetMaximum(4)
   h_ratio.SetMinimum(0)
   h_ratio.SetMarkerColor(ROOT.kBlack)
   h_ratio.SetLineColor(ROOT.kBlack)
   h_ratio.SetMarkerStyle(20)
   h_ratio.SetMarkerSize(1.) 
   h_ratio.Draw("ep") 
   ROOT.gPad.Update() 
   if not log:
     c1.SaveAs(name+".png","png") 
     c1.SaveAs(name+".pdf","pdf") 
   else:
     c1.SaveAs(name+"_log.png","png") 
     c1.SaveAs(name+"_log.pdf","pdf")
   #c1.Delete() 

if __name__ == '__main__': 

 ROOT.gROOT.SetBatch(ROOT.kTRUE)

 parser =  argparse.ArgumentParser(description='smooth DNN')
 parser.add_argument('-d', '--inDir',     dest='inDir',     required=True,  type=str)
 parser.add_argument('-w', '--kinWeight', dest='kinWeight', required=False, type=bool)
 parser.add_argument('-l', '--log',       dest='log',       required=False, type=bool)
 
 args = parser.parse_args()
 inDir = args.inDir
 #inDir = '/eos/user/b/bmarzocc/HHWWgg/January_2021_Production/2017/'

 useKinWeight = False
 useLog = False
 if args.kinWeight==True: useKinWeight = True
 elif args.kinWeight==False: useKinWeight = False
 if args.log==True: useLog = True
 elif args.log==False: useLog = False
 
 print "inDir:       ",inDir
 print "useKinWeight:",useKinWeight
 print "useLog:      ",useLog
 
 histo_scale = ROOT.TH1F("histo_scale","",100000,-1.2,1.1)
 Cut_noMass = '( CMS_hgg_mass>100. && CMS_hgg_mass<180. )'
 Cut_SR = '( CMS_hgg_mass>100. && CMS_hgg_mass<180. && (CMS_hgg_mass > 115 && CMS_hgg_mass < 135) )'
 Cut_SB = '( CMS_hgg_mass>100. && CMS_hgg_mass<180. && !(CMS_hgg_mass > 115 && CMS_hgg_mass < 135) )'
 
 ### 2017 ###
 lumi_2017 = 41.5

 histo_scale.Reset() 
 sig_tree_2017 = ROOT.TChain()
 #sig_tree_2017.AddFile(inDir+'/Signal/SL_NLO_2017_hadded/GluGluToHHTo2G2Qlnu_node_cHHH1_2017_HHWWggTag_0_MoreVars.root/GluGluToHHTo2G2Qlnu_node_cHHH1_13TeV_HHWWggTag_0_v1')
 sig_tree_2017.AddFile(inDir+'/GluGluToHHTo2G2Qlnu_node_cHHH1_2017_HHWWggTag_0_MoreVars.root/GluGluToHHTo2G2Qlnu_node_cHHH1_13TeV_HHWWggTag_0_v1')
 sig_tree_2017 = reduceTree(sig_tree_2017,Cut_SB)
 
 histo_scale.Reset() 
 data_tree_2017 = ROOT.TChain()
 #data_tree_2017.AddFile(inDir+'/Data/Data_2017_HHWWggTag_0_MoreVars.root/Data_13TeV_HHWWggTag_0_v1') 
 data_tree_2017.AddFile(inDir+'/Data_2017_HHWWggTag_0_MoreVars.root/Data_13TeV_HHWWggTag_0_v1') 
 data_tree_2017 = reduceTree(data_tree_2017,Cut_SB)
 data_tree_2017.Draw("Leading_Photon_MVA<-1.?-1.1:Leading_Photon_MVA>>histo_scale",Cut_SB)
 data_scale_2017 = float(histo_scale.Integral())
 
 #Bkgs MC samples
 treeNames = [
   #['DiPhotonJetsBox_M40_80_HHWWggTag_0_MoreVars.root/DiPhotonJetsBox_M40_80_Sherpa_13TeV_HHWWggTag_0','DiPhoton',ROOT.kOrange],
   ['DiPhotonJetsBox_MGG-80toInf_HHWWggTag_0_MoreVars.root/DiPhotonJetsBox_MGG_80toInf_13TeV_Sherpa_13TeV_HHWWggTag_0','DiPhoton',ROOT.kOrange],
   #['GJet_Pt-20to40_HHWWggTag_0_MoreVars.root/GJet_Pt_20to40_DoubleEMEnriched_MGG_80toInf_TuneCP5_13TeV_Pythia8_13TeV_HHWWggTag_0','GJet',ROOT.kBlue],
   #['GJet_Pt-20toInf_HHWWggTag_0_MoreVars.root/GJet_Pt_20toInf_DoubleEMEnriched_MGG_40to80_TuneCP5_13TeV_Pythia8_13TeV_HHWWggTag_0','GJet',ROOT.kBlue],
   ['GJet_Pt-40toInf_HHWWggTag_0_MoreVars.root/GJet_Pt_40toInf_DoubleEMEnriched_MGG_80toInf_TuneCP5_13TeV_Pythia8_13TeV_HHWWggTag_0','GJet',ROOT.kBlue],
   #['QCD_Pt-30to40_HHWWggTag_0_MoreVars.root/QCD_Pt_30to40_DoubleEMEnriched_MGG_80toInf_TuneCP5_13TeV_Pythia8_13TeV_HHWWggTag_0','QCD'ROOT.kCyan+1],
   #['QCD_Pt-30toInf_HHWWggTag_0_MoreVars.root/QCD_Pt_30toInf_DoubleEMEnriched_MGG_40to80_TuneCP5_13TeV_Pythia8_13TeV_HHWWggTag_0','QCD',ROOT.kCyan+1],
   #['QCD_Pt-40toInf_HHWWggTag_0_MoreVars.root/QCD_Pt_40toInf_DoubleEMEnriched_MGG_80toInf_TuneCP5_13TeV_Pythia8_13TeV_HHWWggTag_0','QCD',ROOT.kCyan+1],
   #['DYJetsToLL_M-50_HHWWggTag_0_MoreVars.root/DYJetsToLL_M_50_TuneCP5_13TeV_amcatnloFXFX_pythia8_13TeV_HHWWggTag_0','DY',ROOT.kYellow+2],
   ['TTGG_0Jets_HHWWggTag_0_MoreVars.root/TTGG_0Jets_TuneCP5_13TeV_amcatnlo_madspin_pythia8_13TeV_HHWWggTag_0','TTGsJets',ROOT.kViolet],
   ['TTGJets_TuneCP5_HHWWggTag_0_MoreVars.root/TTGJets_TuneCP5_13TeV_amcatnloFXFX_madspin_pythia8_13TeV_HHWWggTag_0','TTGsJets',ROOT.kViolet],
   #['TTJets_HT-600to800_HHWWggTag_0_MoreVars.root/TTJets_HT_600to800_TuneCP5_13TeV_madgraphMLM_pythia8_13TeV_HHWWggTag_0','TTGsJets',ROOT.kViolet],
   #['TTJets_HT-800to1200_HHWWggTag_0_MoreVars.root/TTJets_HT_800to1200_TuneCP5_13TeV_madgraphMLM_pythia8_13TeV_HHWWggTag_0','TTGsJets',ROOT.kViolet],
   #['TTJets_HT-1200to2500_HHWWggTag_0_MoreVars.root/TTJets_HT_1200to2500_TuneCP5_13TeV_madgraphMLM_pythia8_13TeV_HHWWggTag_0','TTGsJets',ROOT.kViolet],
   #['TTJets_HT-2500toInf_HHWWggTag_0_MoreVars.root/TTJets_HT_2500toInf_TuneCP5_13TeV_madgraphMLM_pythia8_13TeV_HHWWggTag_0','TTGsJets',ROOT.kViolet],
   ['ttWJets_HHWWggTag_0_MoreVars.root/ttWJets_TuneCP5_13TeV_madgraphMLM_pythia8_13TeV_HHWWggTag_0','TTGsJets',ROOT.kGreen+1],
   ['TTJets_TuneCP5_extra_HHWWggTag_0_MoreVars.root/TTJets_TuneCP5_13TeV_amcatnloFXFX_pythia8_13TeV_HHWWggTag_0','TTGsJets',ROOT.kViolet],
   #['W1JetsToLNu_LHEWpT_0-50_HHWWggTag_0_MoreVars.root/W1JetsToLNu_LHEWpT_0_50_TuneCP5_13TeV_amcnloFXFX_pythia8_13TeV_HHWWggTag_0','WGsJets',ROOT.kViolet],
   ['W1JetsToLNu_LHEWpT_50-150_HHWWggTag_0_MoreVars.root/W1JetsToLNu_LHEWpT_50_150_TuneCP5_13TeV_amcnloFXFX_pythia8_13TeV_HHWWggTag_0','WGsJets',ROOT.kViolet],
   ['W1JetsToLNu_LHEWpT_150-250_HHWWggTag_0_MoreVars.root/W1JetsToLNu_LHEWpT_150_250_TuneCP5_13TeV_amcnloFXFX_pythia8_13TeV_HHWWggTag_0','WGsJets',ROOT.kViolet],
   ['W1JetsToLNu_LHEWpT_250-400_HHWWggTag_0_MoreVars.root/W1JetsToLNu_LHEWpT_250_400_TuneCP5_13TeV_amcnloFXFX_pythia8_13TeV_HHWWggTag_0','WGsJets',ROOT.kViolet],
   ['W1JetsToLNu_LHEWpT_400-inf_HHWWggTag_0_MoreVars.root/W1JetsToLNu_LHEWpT_400_inf_TuneCP5_13TeV_amcnloFXFX_pythia8_13TeV_HHWWggTag_0','WGsJets',ROOT.kViolet],
   #['W2JetsToLNu_LHEWpT_0-50_HHWWggTag_0_MoreVars.root/W2JetsToLNu_LHEWpT_0_50_TuneCP5_13TeV_amcnloFXFX_pythia8_13TeV_HHWWggTag_0','WGsJets',ROOT.kViolet],
   ['W2JetsToLNu_LHEWpT_50-150_HHWWggTag_0_MoreVars.root/W2JetsToLNu_LHEWpT_50_150_TuneCP5_13TeV_amcnloFXFX_pythia8_13TeV_HHWWggTag_0','WGsJets',ROOT.kViolet],
   ['W2JetsToLNu_LHEWpT_150-250_HHWWggTag_0_MoreVars.root/W2JetsToLNu_LHEWpT_150_250_TuneCP5_13TeV_amcnloFXFX_pythia8_13TeV_HHWWggTag_0','WGsJets',ROOT.kViolet],
   ['W2JetsToLNu_LHEWpT_250-400_HHWWggTag_0_MoreVars.root/W2JetsToLNu_LHEWpT_250_400_TuneCP5_13TeV_amcnloFXFX_pythia8_13TeV_HHWWggTag_0','WGsJets',ROOT.kViolet],
   ['W2JetsToLNu_LHEWpT_400-inf_HHWWggTag_0_MoreVars.root/W2JetsToLNu_LHEWpT_400_inf_TuneCP5_13TeV_amcnloFXFX_pythia8_13TeV_HHWWggTag_0','WGsJets',ROOT.kViolet],
   #['W3JetsToLNu_HHWWggTag_0_MoreVars.root/W3JetsToLNu_TuneCP5_13TeV_madgraphMLM_pythia8_13TeV_HHWWggTag_0','WGsJets',ROOT.kViolet],
   #['W4JetsToLNu_HHWWggTag_0_MoreVars.root/W4JetsToLNu_TuneCP5_13TeV_madgraphMLM_pythia8_13TeV_HHWWggTag_0','WGsJets',ROOT.kViolet],
   ['WGGJets_HHWWggTag_0_MoreVars.root/WGGJets_TuneCP5_13TeV_madgraphMLM_pythia8_13TeV_HHWWggTag_0','WGsJets',ROOT.kViolet],
   ['WGJJToLNu_EWK_QCD_HHWWggTag_0_MoreVars.root/WGJJToLNu_EWK_QCD_TuneCP5_13TeV_madgraph_pythia8_13TeV_HHWWggTag_0','WGsJets',ROOT.kViolet],
   #['WWTo1L1Nu2Q_HHWWggTag_0_MoreVars.root/WWTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8_13TeV_HHWWggTag_0','WW',ROOT.kOrange],
   #['WW_TuneCP5_HHWWggTag_0_MoreVars.root/WW_TuneCP5_13TeV_pythia8_13TeV_HHWWggTag_0','WW',ROOT.kOrange], 
   #['GluGluHToGG_2017_HHWWggTag_0_MoreVars.root/ggh_125_13TeV_HHWWggTag_0_v1','Hgg',ROOT.kRed],
   #['VBFHToGG_2017_HHWWggTag_0_MoreVars.root/vbf_125_13TeV_HHWWggTag_0_v1','Hgg',ROOT.kRed],
   #['VHToGG_2017_HHWWggTag_0_MoreVars.root/wzh_125_13TeV_HHWWggTag_0_v1','Hgg',ROOT.kRed], 
   #['ttHJetToGG_2017_HHWWggTag_0_MoreVars.root/tth_125_13TeV_HHWWggTag_0_v1','Hgg',ROOT.kRed] 
 ]

 nBins = 50
 vars = [
   ["N_goodJets","N_goodJets", "N goodJets",12,-0.5,11.5],
   ["goodJets_0_pt","goodJets_0_pt","goodJets_0 pt [GeV]",nBins,0.,550.],
   ["goodJets_0_eta","goodJets_0_eta","goodJets_0 #eta [GeV]",nBins,-2.6,2.6],
   ["goodJets_0_phi","goodJets_0_phi","goodJets_0 #phi",nBins,-3.2,3.2],
   ["goodJets_0_E","goodJets_0_E","goodJets_0 E [GeV]",nBins,0.,550.],
   ["goodJets_0_bDiscriminator_mini_pfDeepFlavourJetTags_probb + goodJets_0_bDiscriminator_mini_pfDeepFlavourJetTags_probbb + goodJets_0_bDiscriminator_mini_pfDeepFlavourJetTags_problepb","goodJets_0_bScore","goodJets_0 bScore",nBins,0.,1.],
   ["goodJets_1_pt","goodJets_1_pt","goodJets_1 pt [GeV]",nBins,0.,550.],
   ["goodJets_1_eta","goodJets_1_eta","goodJets_1 #eta",nBins,-2.6,2.6],
   ["goodJets_1_phi","goodJets_1_phi","goodJets_1 #phi",nBins,-3.2,3.2],
   ["goodJets_1_E","goodJets_1_E","goodJets_1 E [GeV]",nBins,0.,550.],
   ["goodJets_1_bDiscriminator_mini_pfDeepFlavourJetTags_probb + goodJets_1_bDiscriminator_mini_pfDeepFlavourJetTags_probbb + goodJets_1_bDiscriminator_mini_pfDeepFlavourJetTags_problepb","goodJets_1_bScore","goodJets_1 bScore",nBins,0.,1.],
   ["goodLepton_pt","goodLepton_pt","goodLepton pt [GeV]",nBins,0.,550.],
   ["goodLepton_eta","goodLepton_eta","goodLepton #eta",nBins,-2.6,2.6],
   ["goodLepton_phi","goodLepton_phi","goodLepton ]phi",nBins,-3.2,3.2],
   ["goodLepton_E","goodLepton_E","goodLepton E [GeV]",nBins,0,550.],
   ["Leading_Photon_E/CMS_hgg_mass","Leading_Photon_E_over_CMS_hgg_mass","Leading_Photon E/hgg_mass",nBins,0,3.],
   ["Leading_Photon_pt/CMS_hgg_mass","Leading_Photon_pt_over_CMS_hgg_mass","Leading_Photon pt/hgg_mass",nBins,0.,3.],
   ["Leading_Photon_eta","Leading_Photon_eta","Leading_Photon #eta",nBins,-2.6,2.6],
   ["Leading_Photon_phi","Leading_Photon_phi","Leading_Photon #phi",nBins,-3.2,3.2],
   ["Leading_Photon_MVA","Leading_Photon_MVA","Leading_Photon MVA",nBins,0.,1.],
   ["Subleading_Photon_E/CMS_hgg_mass","Subleading_Photon_E_over_CMS_hgg_mass","Subleading_Photon E/hgg_mass",nBins,0.,3.],
   ["Subleading_Photon_pt/CMS_hgg_mass","Subleading_Photon_pt_over_CMS_hgg_mass","Subleading_Photon pt/hgg_mass",nBins,0.,3.],
   ["Subleading_Photon_eta","Subleading_Photon_eta","Subleading_Photon #eta",nBins,-2.6,2.6],
   ["Subleading_Photon_phi","Subleading_Photon_phi","Subleading_Photon #phi",nBins,-3.2,3.2],
   ["Subleading_Photon_MVA","Subleading_Photon_MVA","Subleading_Photon MVA",nBins,0.,1.],
   ["METCor_pt","MET","MET [GeV]",nBins,0.,550.],
   ["Wmt_L","MT_leptonMet","MT leptonMet [GeV]",nBins,0.,550.],
   ["Wmass_goodJets12","Wmass_goodJets12","Wmass leadingJetss [GeV]",nBins,0.,2000.],
   ["CMS_hgg_mass","hgg_mass","hgg_mass [GeV]",80,100.,180.],
   ["evalDNN","evalDNN","DNN Score",nBins,0.,1.]
 ]

 histo_scale.Reset() 
 bkg_tree_2017 = ROOT.TChain()
 process_ID = []
 colors = []
 for tree in treeNames: 
   treeName = tree[0]
   if useKinWeight: treeName = tree[0].replace('.root','_kinWeight_noHgg.root')
   bkg_tree_2017.AddFile(inDir+'/'+treeName) 
   if tree[1] not in process_ID: process_ID.append(tree[1])
   if tree[2] not in colors: colors.append(tree[2])
 bkg_tree_2017 = reduceTree(bkg_tree_2017,Cut_SB)
 if not useKinWeight: bkg_tree_2017.Draw("Leading_Photon_MVA<-1.?-1.1:Leading_Photon_MVA>>histo_scale","weight*"+Cut_SB)
 else: bkg_tree_2017.Draw("Leading_Photon_MVA<-1.?-1.1:Leading_Photon_MVA>>histo_scale","kinWeight*weight*"+Cut_SB)
 bkg_scale_2017 = float(histo_scale.Integral())
 
 print "2017 Data/bkg SB scale:",data_scale_2017/bkg_scale_2017
 
 signal_histos = []
 data_histos = []

 for i,var in enumerate(vars):

   h = ROOT.TH1F("h_"+str(var[1])+"_signal","",int(var[3]),float(var[4]),float(var[5]))  
   sig_tree_2017.Draw(var[0]+">>h_"+var[1]+"_signal",str(lumi_2017)+"*2000*weight*2*0.441*0.00097*31.049*"+Cut_SB)
   h.SetLineColor(ROOT.kCyan+1)
   h.SetLineWidth(2)
   signal_histos.append(h)
   
   h = ROOT.TH1F("h_"+str(var[1])+"_data","",int(var[3]),float(var[4]),float(var[5]))  
   data_tree_2017.Draw(var[0]+">>h_"+var[1]+"_data",Cut_SB)
   h.SetMarkerStyle(20)
   h.SetMarkerColor(ROOT.kBlack)
   data_histos.append(h) 

 bkg_histos = []
 
 for i,id in enumerate(process_ID):
   process_tree = ROOT.TChain()
   for tree in treeNames: 
     treeName = tree[0]
     if useKinWeight: treeName = tree[0].replace('.root','_kinWeight_noHgg.root')
     if tree[1] == id: process_tree.AddFile(inDir+'/'+treeName)  
   process_tree = reduceTree(process_tree,Cut_SB) 
   h_vars = []
   for var in vars:
     #print id,var[0]
     h = ROOT.TH1F("h_"+str(var[1])+"_"+str(id),"",int(var[3]),float(var[4]),float(var[5]))
     h.SetFillColor(colors[i])
     h.SetLineColor(colors[i])  
     if not useKinWeight: process_tree.Draw(var[0]+">>h_"+var[1]+"_"+id,str(data_scale_2017/bkg_scale_2017)+"*weight*"+Cut_SB)    
     else: process_tree.Draw(var[0]+">>h_"+var[1]+"_"+id,str(data_scale_2017/bkg_scale_2017)+"*kinWeight*weight*"+Cut_SB)      
     h_vars.append(h)   
   bkg_histos.append(h_vars) 

 leg = ROOT.TLegend(0.73,0.5,0.85,0.96)
 leg.SetFillColor(ROOT.kWhite)
 leg.SetFillStyle(1000)
 leg.SetLineWidth(0)
 leg.SetLineColor(ROOT.kWhite)
 leg.SetTextFont(42)
 leg.SetTextSize(0.03)
 
 for i,var in enumerate(vars):
   h_stack = ROOT.THStack(var[1],var[1]+";"+var[1])
   for j,id in enumerate(process_ID):
     h_stack.Add(bkg_histos[j][i]) 
     leg.AddEntry(bkg_histos[j][i],str(id),"F")  
   leg.AddEntry(data_histos[i],"Data","PL")  
   leg.AddEntry(signal_histos[i],"Signal x 2000","L")  
   h_bkg = h_stack.GetStack().Last()
   if not useLog: drawStack(h_stack,h_bkg,data_histos[i],signal_histos[i],leg,var[1],var[2],False)
   else: drawStack(h_stack,h_bkg,data_histos[i],signal_histos[i],leg,var[1],var[2],True) 
   leg.Clear()
     


 
