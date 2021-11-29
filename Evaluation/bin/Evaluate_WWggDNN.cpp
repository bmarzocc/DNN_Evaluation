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

void SetTree(TTree* tree, vector<float>* branchVals, vector<TBranch*>* branchRefs, vector<string>* inputBranches)
{

   size_t nBranches = tree->GetListOfBranches()->GetEntries();
   branchVals->resize(inputBranches->size());
   branchRefs->resize(inputBranches->size()); 

   for(unsigned int iVar = 0; iVar < inputBranches->size(); ++iVar)
   {
       for(size_t i = 0; i < nBranches; ++i)
       {
           TBranch *br =dynamic_cast<TBranch*>(tree->GetListOfBranches()->At(i));
           if(string(br->GetName()) == inputBranches->at(iVar)){ 
              //if(i==5) continue;
              //std::cout << "Branch: " << i << " - " << br->GetName() << std::endl;  
              tree->SetBranchAddress(br->GetName(), &branchVals->at(iVar), &branchRefs->at(iVar)); 
           }
       }
   }

}

void SetValues(vector<float>* inputVals, vector<float>* branchVals, bool isBkg_, float nodeNumber)
{
   for(unsigned int iBranch =0; iBranch<branchVals->size(); iBranch++){
       if(isnan(branchVals->at(iBranch))) std::cout << "SetValues --> Bad iBranch NAN: " << iBranch << std::endl; 
       if(isinf(branchVals->at(iBranch))) std::cout << "SetValues --> Bad iBranch INF: " << iBranch << std::endl;  
   }  

   inputVals->push_back(branchVals->at(0)); //0: goodJets_0_E
   inputVals->push_back(branchVals->at(1)); //1: goodLepton_phi
   inputVals->push_back(branchVals->at(2)/branchVals->at(33)); //2: Subleading_Photon_E/CMS_hgg_mass
   inputVals->push_back(branchVals->at(3)/branchVals->at(33)); //3: Leading_Photon_pt/CMS_hgg_mass
   inputVals->push_back(branchVals->at(4)); //4: Leading_Photon_MVA
   inputVals->push_back(branchVals->at(5)); //5: goodLepton_eta
   inputVals->push_back(branchVals->at(6)); //6: goodJets_1_E
   inputVals->push_back(branchVals->at(7)); //7: Wmass_goodJets12
   inputVals->push_back(branchVals->at(8)); //8: goodLepton_E
   inputVals->push_back(branchVals->at(9)); //9: goodJets_1_eta
   inputVals->push_back(branchVals->at(10)); //10: goodJets_1_phi
   inputVals->push_back(branchVals->at(11)); //11: Subleading_Photon_eta
   inputVals->push_back(branchVals->at(12)+branchVals->at(13)+branchVals->at(14)); //12: goodJets_1_bTagging 
   inputVals->push_back(branchVals->at(15)); //13: goodLepton_pt
   inputVals->push_back(branchVals->at(16)); //14: goodJets_0_pt
   if(isBkg_) inputVals->push_back(nodeNumber); //15: Node_Number 
   else inputVals->push_back(branchVals->at(17)); //15: Node_Number
   inputVals->push_back(branchVals->at(18)/branchVals->at(33)); //16: Subleading_Photon_pt/CMS_hgg_mass
   inputVals->push_back(branchVals->at(19)); //17: Subleading_Photon_phi
   inputVals->push_back(branchVals->at(20)); //18: goodJets_1_pt
   inputVals->push_back(branchVals->at(21)); //19: N_goodJets
   inputVals->push_back(branchVals->at(22)); //20: goodJets_0_phi
   inputVals->push_back(branchVals->at(23)); //21: METCor_pt
   inputVals->push_back(branchVals->at(24)/branchVals->at(33)); //22: Leading_Photon_E/CMS_hgg_mass
   inputVals->push_back(branchVals->at(25)); //23: Leading_Photon_phi
   inputVals->push_back(branchVals->at(26)); //24: Subleading_Photon_MVA
   inputVals->push_back(branchVals->at(27)); //25: goodJets_0_eta
   inputVals->push_back(branchVals->at(28)); //26: Leading_Photon_eta
   inputVals->push_back(branchVals->at(29)); //27: Wmt_L
   inputVals->push_back(branchVals->at(30)+branchVals->at(31)+branchVals->at(32)); //28: goodJets_0_bTagging 

   //std::cout << "Input values size: " << inputVals->size() << std::endl;  
}

int main(int argc, char** argv)
{
   const edm::ParameterSet &process         = edm::readPSetsFrom( argv[1] )->getParameter<edm::ParameterSet>( "process" );
   const edm::ParameterSet &filesOpt        = process.getParameter<edm::ParameterSet>( "ioFilesOpt" );
    
   // config inputs
   bool isBkg_                   = filesOpt.getParameter<bool>( "isBkg" );
   double nodeNumber_            = filesOpt.getParameter<double>( "nodeNumber" );
   vector<string> inputFiles_    = filesOpt.getParameter<vector<string>>( "inputFiles" );
   string inputDir_              = filesOpt.getParameter<string>( "inputDir" );
   string outputDir_             = filesOpt.getParameter<string>( "outputDir" );

   string inputModel_            = filesOpt.getParameter<string>( "inputModel" );
   vector<string> inputParams_   = filesOpt.getParameter<vector<string>>( "inputParams" );
   vector<string> inputBranches_ = filesOpt.getParameter<vector<string>>( "inputBranches" );
   vector<string> inputVars_     = filesOpt.getParameter<vector<string>>( "inputVars" );

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
       std::string outputName = outputDir_+split_str.at(split_str.size()-1);
       if(isBkg_==true) outputName.replace(outputName.end()-5,outputName.end(),string("_nodeNumber"+to_string(int(nodeNumber_))+".root"));

       TFile* outFile = new TFile(outputName.c_str(),"recreate");
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

           vector<float> inputValues; 
           vector<float> branchVals; 
           vector<TBranch*> branchRefs;
           SetTree(copyTree, &branchVals, &branchRefs, &inputBranches_);
           TBranch* evalDNNBranch = copyTree->Branch("evalDNN",&evalDNN,"evalDNN/F");
   
           // Loop over all entries of the Tree
           for(int entry = 0; entry < copyTree->GetEntries(); entry++)
           {  
               //if(entry>0) continue;
               if(entry%1000==0) std::cout << "--- Reading " << categories_.at(iCat).c_str() << " = " << entry << std::endl;
               copyTree->GetEntry(entry);

               //if( entry < 10000 ) continue;
               inputValues.clear();
               SetValues(&inputValues, &branchVals, isBkg_, nodeNumber_);
 
               // fill input variables
               unsigned int shape = inputValues.size();
               tensorflow::Tensor inputVals(tensorflow::DT_FLOAT, {1,shape});
               for(unsigned int i = 0; i < shape; i++){
                   //if(std::isinf(inputValues[i])) std::cout << "inf: " << i << std::endl; 
                   if(inputValues[i]<-25. || std::isinf(inputValues[i]) || std::isnan(inputValues[i])) inputVals.matrix<float>()(0,i) = -9.;
                   else inputVals.matrix<float>()(0,i) =  float(inputValues.at(i));
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

