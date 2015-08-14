% Important to include the LDA_toolbox folder to path (and subfolders)
addpath(genpath('..')); 

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% CASE 1 (ratings not used)
%% Create a simple term-document matrix
sp_occurrences = sparse(...
   [5  1  1; ...
    5  1  1; ...
    1  1  5; ...
    1  1  5]*100); % NOTE: Multipling makes results less dependent on sampling variability

% Create ratings
rated_docs = [0 0 0]; % No document rated
ratings = [0 0 0]; % Not important, because no document rated

% Run LDA
OUTPUT_PATH = 'micro_test/'; % Must finish with /

N_TOPICS = 2;
ALPHA = 0.1;
BETA = 0.1;

BURNIN_PERIOD = 0;
THINNING_PERIOD = 1;
N_SAMPLES = 10;

run_basic_SLDA(sp_occurrences, OUTPUT_PATH, ...
    N_TOPICS, ALPHA, BETA, ...
    BURNIN_PERIOD, THINNING_PERIOD, N_SAMPLES, ...
    rated_docs, ratings)

% Display the last sample
load([OUTPUT_PATH sprintf('output_SLDA_sample%d.mat', N_SAMPLES)]);

display(topics_distribs);
display(topics_props);

% topics_distribs =
% 
%     0.4480    0.0451
%     0.4557    0.0371
%     0.0520    0.4549
%     0.0443    0.4629
% 
% 
% topics_props =
% 
%     0.9258    0.5100    0.0909
%     0.0742    0.4900    0.9091


% degbu
% topics_distribs =
% 
%     0.0579    0.4424
%     0.0557    0.4445
%     0.4489    0.0508
%     0.4375    0.0622
% 
% 
% topics_props =
% 
%     0.0742    0.4950    0.9283
%     0.9258    0.5050    0.0717


%% Remove the results
rmdir(OUTPUT_PATH, 's');

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% CASE 2 (test influence of rating
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% on topic choice for document)
%% Create a simple term-document matrix
% rmdir(OUTPUT_PATH, 's');

sp_occurrences = sparse(...
   [10  0  0; ...
    10  1  0; ...
    0  1  10; ...
    0  0  10]);

% Create ratings
rated_docs = [1 1 1 ]; % All documents rated
ratings = [0 1 1]; 

% Replicate the structure
REPLICATIONS = 10;
sp_occurrences = repmat(sp_occurrences, 1, REPLICATIONS);
rated_docs = repmat(rated_docs, 1, REPLICATIONS);
ratings = repmat(ratings, 1, REPLICATIONS);


% Run LDA
OUTPUT_PATH = 'micro_test/'; % Must finish with /

N_TOPICS = 2;
ALPHA = 0.1;
BETA = 0.1;

BURNIN_PERIOD = 0;
THINNING_PERIOD = 1;
N_SAMPLES = 10;

SIGMA2 = 1e-6;

run_basic_SLDA(sp_occurrences, OUTPUT_PATH, ...
    N_TOPICS, ALPHA, BETA, ...
    BURNIN_PERIOD, THINNING_PERIOD, N_SAMPLES, ...
    rated_docs, ratings, SIGMA2)

% Display the last sample
load([OUTPUT_PATH sprintf('output_SLDA_sample%d.mat', N_SAMPLES)]);

display(topics_distribs);
% display(topics_props);

topics_props = topics_props(1,:);
topics_props = reshape(topics_props, 3, REPLICATIONS);
mean(topics_props,2)

%% Remove the results
rmdir(OUTPUT_PATH, 's');
