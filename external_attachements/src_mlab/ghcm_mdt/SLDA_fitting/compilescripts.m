% Note that we must be in the folder to do this!

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
mex -O -largeArrayDims GibbsSamplerSLDA.c
