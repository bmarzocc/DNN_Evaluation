#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSetReader/interface/ParameterSetReader.h"
#include "PhysicsTools/Utilities/macros/setTDRStyle.C"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Utilities/interface/InputTag.h"

#include "PhysicsTools/TensorFlow/interface/TensorFlow.h"

#include "TFile.h"
#include "TTree.h"
#include "TROOT.h"
#include "TChain.h"
#include "TGraphErrors.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TCanvas.h"
#include "TVector2.h"
#include "TMath.h"
#include "TLegend.h"
#include "TEfficiency.h"
#include "TProfile.h"
#include "TStyle.h"
#include "TTreeReader.h"
#include <algorithm> 
#include <iostream>
#include <utility>

using namespace std;

void SetTree(TTree* tree, vector<float>* branchVals, vector<TBranch*>* branchRefs, vector<string>* inputVars)
{

   size_t nBranches = tree->GetListOfBranches()->GetEntries();
   branchVals->resize(inputVars->size());
   branchRefs->resize(inputVars->size()); 

   for(unsigned int iVar = 0; iVar < inputVars->size(); ++iVar)
   {
       for(size_t i = 0; i < nBranches; ++i)
       {
           TBranch *br =dynamic_cast<TBranch*>(tree->GetListOfBranches()->At(i));
           if(string(br->GetName()) == inputVars->at(iVar)) tree->SetBranchAddress(br->GetName(), &branchVals->at(iVar), &branchRefs->at(iVar)); 
       }
   }

}

int main(int argc, char** argv)
{
   const edm::ParameterSet &process         = edm::readPSetsFrom( argv[1] )->getParameter<edm::ParameterSet>( "process" );
   const edm::ParameterSet &filesOpt        = process.getParameter<edm::ParameterSet>( "ioFilesOpt" );
    
   // config inputs
   string inputFile_           = filesOpt.getParameter<string>( "inputFile" );
   string outputFile_          = filesOpt.getParameter<string>( "outputFile" );
   string inputTree_           = filesOpt.getParameter<string>( "inputTree" );
   vector<string> categories_  = filesOpt.getParameter<vector<string>>( "categories" );

   string inputModel_          = filesOpt.getParameter<string>( "inputModel" );
   vector<string> inputParams_ = filesOpt.getParameter<vector<string>>( "inputParams" );
   vector<string> inputVars_   = filesOpt.getParameter<vector<string>>( "inputVars" );

   // create a DNN session
   tensorflow::Session* session = tensorflow::createSession(tensorflow::loadGraphDef(inputModel_.c_str()));

   TFile* inFile = TFile::Open(inputFile_.c_str());
   TFile* outFile = TFile::Open(outputFile_.c_str(),"recreate");

   float evalDNN = -999.;
   
   for(unsigned int iCat=0; iCat<categories_.size(); iCat++)
   {
       TTree* inTree = (TTree*)inFile->Get((inputTree_+"_"+categories_.at(iCat)).c_str());
       TTree* copyTree = (TTree*)inTree->CopyTree("");
       copyTree->SetName(("13TeV_HHWWggTag_"+categories_.at(iCat)).c_str());
       copyTree->SetTitle(("13TeV_HHWWggTag_"+categories_.at(iCat)).c_str());

       vector<float> branchVals; 
       vector<TBranch*> branchRefs;
       SetTree(inTree, &branchVals, &branchRefs, &inputVars_);
       TBranch* evalDNNBranch = copyTree->Branch("evalDNN",&evalDNN,"evalDNN/F");
   
       // Loop over all entries of the Tree
       for(int entry = 0; entry < copyTree->GetEntries(); entry++)
       {  
           //if(entry>0) continue;
           if(entry%1000==0) std::cout << "--- Reading " << (inputTree_+"_"+categories_.at(iCat)).c_str() << " = " << entry << std::endl;
           inTree->GetEntry(entry);

           // fill input variables
           unsigned int shape = branchVals.size();
           tensorflow::Tensor inputVals(tensorflow::DT_FLOAT, {1,shape});
           for(unsigned int i = 0; i < shape; i++){
               if(branchVals[i] == -999) inputVals.matrix<float>()(0,i) =  -9.;
               else inputVals.matrix<float>()(0,i) =  float(branchVals[i]);
           } 
        
           // evaluate DNN
           std::vector<tensorflow::Tensor> outputs;
           tensorflow::run(session, { {inputParams_[0].c_str(), inputVals} } , { inputParams_[1].c_str() }, &outputs);

           evalDNN = outputs[0].matrix<float>()(0, 0);
           evalDNNBranch->Fill(); 

       }
       outFile->Write(); 
   }
   outFile->Close();

   // cleanup
   tensorflow::closeSession(session);


}

