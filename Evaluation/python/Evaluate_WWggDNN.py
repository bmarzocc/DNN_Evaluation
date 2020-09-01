import FWCore.ParameterSet.Config as cms

process = cms.PSet()

process.ioFilesOpt = cms.PSet(

    ##inputs
    inputFile = cms.string('/afs/cern.ch/work/a/atishelm/public/ForJosh/2017_DataMC_ntuples_moreVars/Signal/ggF_SM_WWgg_qqlnugg_Hadded.root'),
    outputFile = cms.string('ggF_SM_WWgg_qqlnugg_Hadded_evalDNN.root'),
    inputTree = cms.string('tagsDumper/trees/ggF_SM_WWgg_qqlnugg_13TeV_HHWWggTag'),
    categories = cms.vstring('0','1','2'),
 
    ##input DNN
    inputModel = cms.string('/afs/cern.ch/work/j/jthomasw/public/forBadder/HHWWyy_networkfiles/HHWWyyDNN_binary_basictraining_Tag_0_1.pb'),
    inputParams = cms.vstring('dense_1_input:0','dense_6/Sigmoid:0'),   
    inputVars = cms.vstring(
       "N_goodJets",
       "goodJets_0_pt",
       "goodJets_0_eta",
       "goodJets_0_phi",
       "goodJets_0_E",
       "goodJets_0_bDiscriminator_mini_pfDeepFlavourJetTags_probb",
       "goodJets_1_pt",
       "goodJets_1_eta",
       "goodJets_1_phi",
       "goodJets_1_E",
       "goodJets_1_bDiscriminator_mini_pfDeepFlavourJetTags_probb",
       "goodElectrons_0_pt",
       "goodElectrons_0_eta",
       "goodElectrons_0_phi",
       "goodElectrons_0_E",
       "goodMuons_0_pt",
       "goodMuons_0_eta",
       "goodMuons_0_phi",
       "goodMuons_0_E",
       "Leading_Photon_E",
       "Leading_Photon_pt",
       "Leading_Photon_eta",
       "Leading_Photon_phi",
       "Leading_Photon_MVA",
       "Subleading_Photon_E",
       "Subleading_Photon_pt",
       "Subleading_Photon_eta",
       "Subleading_Photon_phi",
       "Subleading_Photon_MVA" 
    ) 

)   
