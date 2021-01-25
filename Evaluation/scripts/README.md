# Sripts

1) Prepare histograms for categorization:

    * cd DNN_Evaluation/Evaluation/scripts/
    * cmsenv
    * python smooth_DNN.py --inDir /eos/user/b/bmarzocc/HHWWgg/January_2021_Production/HHWWyyDNN_binary_noHgg_BalanceYields_allBkgs_oddSignal_v3/ --nBins 30 --min 0. --max 1.

2) Optimize the boundaries:

    * python optimizeCategories.py -inDir /eos/user/b/bmarzocc/HHWWgg/January_2021_Production/HHWWyyDNN_binary_noHgg_BalanceYields_allBkgs_oddSignal_v3/ -nBins 30 -nCats 1
   
