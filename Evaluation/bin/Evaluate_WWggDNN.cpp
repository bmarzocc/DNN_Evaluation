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

void SplitString(const std::string& str, vector<string>& cont, char delim = ' ')
{
    std::stringstream ss(str);
    std::string token;
    while (std::getline(ss, token, delim)) {
        cont.push_back(token);
    }
}

vector<string> ListTrees(TDirectory* dir)
{
    vector<string> names;
    TIter next(dir->GetListOfKeys());
    TObject* object = 0;
    while ((object = next())){
           names.push_back(string(object->GetName()));
           //std::cout << "ListTrees: " << dir->GetName() << " - " << object->GetName() << std::endl; 
    }
    return names;
}

vector<string> ListTrees(TFile* file)
{
    vector<string> names;
    TIter next(file->GetListOfKeys());
    TObject* object = 0;
    while ((object = next())){
           names.push_back(string(object->GetName()));
           //std::cout << "ListTrees: " << object->GetName() << std::endl; 
    }
    return names;
}

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
   vector<string> inputFiles_ = filesOpt.getParameter<vector<string>>( "inputFiles" );
   string inputDir_           = filesOpt.getParameter<string>( "inputDir" );
   string outputDir_          = filesOpt.getParameter<string>( "outputDir" );

   string inputModel_          = filesOpt.getParameter<string>( "inputModel" );
   vector<string> inputParams_ = filesOpt.getParameter<vector<string>>( "inputParams" );
   vector<string> inputVars_   = filesOpt.getParameter<vector<string>>( "inputVars" );

   // create a DNN session
   std::cout << "inputModel: " << inputModel_.c_str() << std::endl;
   tensorflow::Session* session = tensorflow::createSession(tensorflow::loadGraphDef(inputModel_.c_str()));

   float evalDNN = -999.;
   for(unsigned int iFile=0; iFile<inputFiles_.size(); iFile++)
   {
       TFile* inFile = TFile::Open(inputFiles_.at(iFile).c_str());
       vector<string> categories_;
       
       if(inputDir_!=""){
          TDirectory* dir =(TDirectory*)inFile->Get(inputDir_.c_str());
          categories_ = ListTrees(dir);
       }else{
          categories_ = ListTrees(inFile);  
       }
	
       vector<string> split_str;
       SplitString(inputFiles_.at(iFile), split_str, '/');
       
       TFile* outFile = new TFile((outputDir_+split_str.at(split_str.size()-1)).c_str(),"recreate");
       outFile->cd();

       if(inputDir_!="") inputDir_ = inputDir_ + '/';
       for(unsigned int iCat=0; iCat<categories_.size(); iCat++)
       { 
           if(!inFile->Get((inputDir_+categories_.at(iCat)).c_str())){
              std::cout << "WARNING ----> NOT FOUND: " << (inputDir_+categories_.at(iCat)).c_str() << std::endl;         
              continue;
           }

           TTree* inTree = (TTree*)inFile->Get((inputDir_+categories_.at(iCat)).c_str());
           inTree->SetBranchStatus("evalDNN",0);
           TTree* copyTree = (TTree*)inTree->CopyTree("");
           copyTree->SetName(categories_.at(iCat).c_str());
           copyTree->SetTitle(categories_.at(iCat).c_str());

           vector<float> branchVals; 
           vector<TBranch*> branchRefs;
           SetTree(copyTree, &branchVals, &branchRefs, &inputVars_);
           TBranch* evalDNNBranch = copyTree->Branch("evalDNN",&evalDNN,"evalDNN/F");
   
           // Loop over all entries of the Tree
           for(int entry = 0; entry < copyTree->GetEntries(); entry++)
           {  
               //if(entry>0) continue;
               if(entry%1000==0) std::cout << "--- Reading " << categories_.at(iCat).c_str() << " = " << entry << std::endl;
               copyTree->GetEntry(entry);

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
       }
       outFile->Write();
       outFile->Close(); 
   }
   // cleanup
   tensorflow::closeSession(session);


}

