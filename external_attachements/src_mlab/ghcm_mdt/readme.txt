###########################################################################
#########                       LDA toolbox                       #########
###########################################################################

LDA toolbox aims to provide a clear and efficient tools to work with LDA.

The toolbox is structured in the following way:
- 'LDA_fitting/'  contains functions to fit and estimate LDA parameters.
- 'utils/' contains functions for visualization, conversion, synthetic data 
   generation.
- 'wiki_example/' contains scripts to test LDA toolbox on a small dataset.
- 'references/' contains documents explaining how LDA and this toolbox work.
- 'tests/' contains automated tests of the implementation.
- 'slda/' contains a functions for a supervised variation of LDA.

# Important for usage
To use LDA toolbox, mex files must first be compiled. For this, we must be 
at the root of the LDA toolbox and run 'compile_mex_files.m'.

To test and understand LDA toolbox, first have a look at 'wiki_example/'.

Some of the most important functions in 'LDA_fitting/':
- 'GibbsSamplerLDA.c/m' provides the core algorithm to perform fast sampling.
- 'fit_LDA_advanced.m' provides various options for LDA model fitting.

# Notes
Note that GibbsSamplerLDA.c/m originaly comes from topictoolbox, available at 
http://psiexp.ss.uci.edu/research/programs_data/toolbox.htm
It has been commented compared to the code available online.

This toolbox was developed by Frederic Sabatier in 2014.
