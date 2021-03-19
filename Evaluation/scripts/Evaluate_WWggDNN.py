import FWCore.ParameterSet.Config as cms

process = cms.PSet()

process.ioFilesOpt = cms.PSet(

    ##input files
    inputFiles = cms.vstring(
       'INPUTFILE'
    ),
    #inputDir = cms.string('tagsDumper/trees'), 
    inputDir = cms.string(''),  
    outputDir = cms.string('/eos/user/b/bmarzocc/HHWWgg/January_2021_Production/HHWWyyDNN_binary_noHgg_noNegWeights_BalanceYields_allBkgs_LOSignals_noPtOverM/'),
    
    ##input DNN
    inputModel = cms.string('/eos/user/b/bmarzocc/HHWWgg/January_2021_Production/HHWWyyDNN_binary_noHgg_noNegWeights_BalanceYields_allBkgs_LOSignals_noPtOverM/model.pb'),
    inputParams = cms.vstring('dense_1_input:0','dense_6/Sigmoid:0'), 
    inputBranches = cms.vstring(
        'goodJets_0_E',
        'goodLepton_phi',
        'Subleading_Photon_E',
        'Leading_Photon_pt',
        'Leading_Photon_MVA',
        'goodLepton_eta',
        'goodJets_1_E',
        'Wmass_goodJets12',
        'goodLepton_E',
        'goodJets_1_eta',
        'goodJets_1_phi',
        'Subleading_Photon_eta',
        'goodJets_1_bDiscriminator_mini_pfDeepFlavourJetTags_probb',
        'goodJets_1_bDiscriminator_mini_pfDeepFlavourJetTags_probbb',
        'goodJets_1_bDiscriminator_mini_pfDeepFlavourJetTags_problepb',
        'goodLepton_pt',
        'goodJets_0_pt',
        'Subleading_Photon_pt',
        'Subleading_Photon_phi',
        'goodJets_1_pt',
        'N_goodJets',
        'goodJets_0_phi',
        'METCor_pt',
        'Leading_Photon_E',
        'Leading_Photon_phi',
        'Subleading_Photon_MVA',
        'goodJets_0_eta',
        'Leading_Photon_eta',
        'Wmt_L',
        'goodJets_0_bDiscriminator_mini_pfDeepFlavourJetTags_probb', 
        'goodJets_0_bDiscriminator_mini_pfDeepFlavourJetTags_probbb', 
        'goodJets_0_bDiscriminator_mini_pfDeepFlavourJetTags_problepb',
        'CMS_hgg_mass'
    ),   
    inputVars = cms.vstring(
        'goodJets_0_E',
        'goodLepton_phi',
        'Subleading_Photon_E/CMS_hgg_mass',
        'Leading_Photon_pt/CMS_hgg_mass',
        'Leading_Photon_MVA',
        'goodLepton_eta',
        'goodJets_1_E',
        'Wmass_goodJets12',
        'goodLepton_E',
        'goodJets_1_eta',
        'goodJets_1_phi',
        'Subleading_Photon_eta',
        'goodJets_1_bDiscriminator_mini_pfDeepFlavourJetTags_probb + goodJets_1_bDiscriminator_mini_pfDeepFlavourJetTags_probbb + goodJets_1_bDiscriminator_mini_pfDeepFlavourJetTags_problepb',
        'goodLepton_pt',
        'goodJets_0_pt',
        'Subleading_Photon_pt/CMS_hgg_mass',
        'Subleading_Photon_phi',
        'goodJets_1_pt',
        'N_goodJets',
        'goodJets_0_phi',
        'METCor_pt',
        'Leading_Photon_E/CMS_hgg_mass',
        'Leading_Photon_phi',
        'Subleading_Photon_MVA',
        'goodJets_0_eta',
        'Leading_Photon_eta',
        'Wmt_L',
        'goodJets_0_bDiscriminator_mini_pfDeepFlavourJetTags_probb + goodJets_0_bDiscriminator_mini_pfDeepFlavourJetTags_probbb + goodJets_0_bDiscriminator_mini_pfDeepFlavourJetTags_problepb'
    ) 
)   
