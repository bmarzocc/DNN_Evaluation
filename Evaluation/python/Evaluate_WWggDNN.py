import FWCore.ParameterSet.Config as cms

process = cms.PSet()

process.ioFilesOpt = cms.PSet(

    ##dataset type and node
    isBkg = cms.bool(True), 
    nodeNumber = cms.double(1.),

    ##input files
    inputFiles = cms.vstring(
       '/eos/user/b/bmarzocc/HHWWgg/January_2021_Production/2017/Backgrounds/ttWJets_HHWWggTag_0_MoreVars_kinWeight_noHgg_v2.root'
    ),
    #inputDir = cms.string('tagsDumper/trees'), 
    inputDir = cms.string(''),  
    outputDir = cms.string('/eos/user/b/bmarzocc/HHWWgg/January_2021_Production/HHWWyyDNN_binary_EFT_noHgg_noNegWeights_BalanceYields_allBkgs_NLO_Reweighted_20nodes_noPtOverM_withKinWeight_weightSel_Parametrized/'),
    
    ##input DNN
    inputModel = cms.string('/eos/user/b/bmarzocc/HHWWgg/January_2021_Production/HHWWyyDNN_binary_EFT_noHgg_noNegWeights_BalanceYields_allBkgs_NLO_Reweighted_20nodes_noPtOverM_withKinWeight_weightSel_Parametrized/model.pb'),
    inputParams = cms.vstring('dense_1_input:0','dense_6/Sigmoid:0'), 
    inputBranches = cms.vstring(
        'goodJets_0_E', #0
        'goodLepton_phi', #1
        'Subleading_Photon_E', #2
        'Leading_Photon_pt', #3
        'Leading_Photon_MVA', #4
        'goodLepton_eta', #5
        'goodJets_1_E', #6
        'Wmass_goodJets12', #7
        'goodLepton_E', #8
        'goodJets_1_eta', #9
        'goodJets_1_phi', #10
        'Subleading_Photon_eta', #11
        'goodJets_1_bDiscriminator_mini_pfDeepFlavourJetTags_probb', #12
        'goodJets_1_bDiscriminator_mini_pfDeepFlavourJetTags_probbb', #13
        'goodJets_1_bDiscriminator_mini_pfDeepFlavourJetTags_problepb', #14
        'goodLepton_pt', #15
        'goodJets_0_pt', #16
        'Node_Number', #17
        'Subleading_Photon_pt', #18
        'Subleading_Photon_phi', #19
        'goodJets_1_pt', #20
        'N_goodJets', #21
        'goodJets_0_phi', #22
        'METCor_pt', #23
        'Leading_Photon_E', #24
        'Leading_Photon_phi', #25
        'Subleading_Photon_MVA', #26
        'goodJets_0_eta', #27
        'Leading_Photon_eta', #28
        'Wmt_L', #29
        'goodJets_0_bDiscriminator_mini_pfDeepFlavourJetTags_probb', #30
        'goodJets_0_bDiscriminator_mini_pfDeepFlavourJetTags_probbb', #31 
        'goodJets_0_bDiscriminator_mini_pfDeepFlavourJetTags_problepb', #32
        'CMS_hgg_mass' #33
    ),   
    inputVars = cms.vstring(
        'goodJets_0_E', #0
        'goodLepton_phi', #1 
        'Subleading_Photon_E/CMS_hgg_mass', #2
        'Leading_Photon_pt/CMS_hgg_mass', #3
        'Leading_Photon_MVA', #4
        'goodLepton_eta', #5
        'goodJets_1_E', #6
        'Wmass_goodJets12', #7
        'goodLepton_E', #8
        'goodJets_1_eta', #9
        'goodJets_1_phi', #10
        'Subleading_Photon_eta', #11
        'goodJets_1_bDiscriminator_mini_pfDeepFlavourJetTags_probb + goodJets_1_bDiscriminator_mini_pfDeepFlavourJetTags_probbb + goodJets_1_bDiscriminator_mini_pfDeepFlavourJetTags_problepb', #12
        'goodLepton_pt', #13
        'goodJets_0_pt', #14
        'Node_Number', #15
        'Subleading_Photon_pt/CMS_hgg_mass', #16
        'Subleading_Photon_phi', #17
        'goodJets_1_pt', #18
        'N_goodJets', #19
        'goodJets_0_phi', #20
        'METCor_pt', #21
        'Leading_Photon_E/CMS_hgg_mass', #22
        'Leading_Photon_phi', #23
        'Subleading_Photon_MVA', #24
        'goodJets_0_eta', #25
        'Leading_Photon_eta', #26
        'Wmt_L', #27
        'goodJets_0_bDiscriminator_mini_pfDeepFlavourJetTags_probb + goodJets_0_bDiscriminator_mini_pfDeepFlavourJetTags_probbb + goodJets_0_bDiscriminator_mini_pfDeepFlavourJetTags_problepb' #28
    ) 
)   
