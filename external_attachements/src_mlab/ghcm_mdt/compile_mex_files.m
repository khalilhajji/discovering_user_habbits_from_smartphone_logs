% This script compile mex files used in LDA toolbox
% 
% Make sure to be at the root of the LDA toolbox to do this!
 

% Here is the documentation of interest for the mex function
%
% mex   Compile mex-function
% 
% -O
% Optimize the object code. Optimization is enabled by default and
% by including this option on the command line. If the -g option
% appears without the -O option, optimization is disabled.
% 
% -largeArrayDims
% Build a mex-file using the MATLAB large-array-handling API. This
% API can handle arrays with more than 2^31-1 elements when
% compiled on 64-bit platforms. (See also the -compatibleArrayDims
% option.)

% Save the current path (to return after compiling every script), and
% display warning message.
current_path = pwd;
fprintf('### To compile mex file, make sure to be at the root of the LDA toolbox\n')
fprintf('### Current path: %s\n', current_path);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Compile LDA
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
GIBBS_SAMPLER_LDA_PATH = 'LDA_fitting/';

cd(GIBBS_SAMPLER_LDA_PATH);
mex -O -largeArrayDims gibbs_sampler_LDA.c
cd(current_path)

fprintf('gibbs_sampler_LDA compiled\n')

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Compile fixed LDA
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
GIBBS_SAMPLER_FIXED_LDA_PATH = 'LDA_fitting/';

cd(GIBBS_SAMPLER_FIXED_LDA_PATH);
mex -O -largeArrayDims gibbs_sampler_fixed_LDA.c
cd(current_path)

fprintf('gibbs_sampler_fixed_LDA compiled\n')

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Compile sLDA
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
GIBBS_SAMPLER_SLDA_PATH = 'SLDA_fitting/';

cd(GIBBS_SAMPLER_SLDA_PATH);
mex -O -largeArrayDims gibbs_sampler_SLDA.c
cd(current_path)

fprintf('gibbs_sampler_SLDA compiled\n')

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Compile conversion tool
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
CONVERSION_TOOLS_PATH = 'utils/data_conversion/';

cd(CONVERSION_TOOLS_PATH);
mex generate_replicated_vectors.c
cd(current_path)

fprintf('generate_replicated_vectors compiled\n')
