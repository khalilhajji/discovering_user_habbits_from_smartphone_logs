% fit_LDA_basic Produces LDA samples using Gibbs sampling
% 
% fit_LDA_basic(docs_vector, words_vector, OUTPUT_PATH, ...
%     N_TOPICS, ALPHA, BETA, ...
%     BURNIN_PERIOD, THINNING_PERIOD, N_SAMPLES, INIT_SEED)
% 
% Perform sampling with (docs_vector, words_vector), for a  LDA model with
% parameters N_TOPICS, ALPHA and BETA. N_SAMPLES samples are written in
% OUTPUT_PATH, with the first sample taken after BURNIN_PERIOD sampling
% iterations, and the following samples taken every THINNING_PERIOD
% sampling iterations.
% 
% Optionaly, INIT_SEED can be given (e.g. if performing multiple restarts).
% 
% To start with a term-document sparse matrix, use sp_occurrences_to_vectors to
% obtain the (docs_vector, words_vector) format.
% 
% INPUT
%   docs_vector         N_TOKENSx1 vector
%   words_vector        N_TOKENSx1 vector
%   OUTPUT_PATH         string
%   N_TOPICS            scalar
%   ALPHA               scalar
%   BETA                scalar
%   BURNIN_PERIOD       scalar
%   THINNING_PERIOD     scalar
%   N_SAMPLES           scalar
%   INIT_SEED           scalar, optional
function fit_LDA_basic(docs_vector, words_vector, OUTPUT_PATH, ...
    N_TOPICS, ALPHA, BETA, ...
    BURNIN_PERIOD, THINNING_PERIOD, N_SAMPLES, INIT_SEED)

SHOW_LDA_DETAILS = 1; % To show some details

N_TOKENS = length(docs_vector);

% Create the output directory
mkdir(OUTPUT_PATH);

% Generate random initial topics (usually denoted by z)
if(~exist('INIT_SEED', 'var'))
    INIT_SEED = 1; % If the function has been called without a seed
end
rng(INIT_SEED); % To be able to reproduce results
topics_vector = randi(N_TOPICS, N_TOKENS, 1);

% Allows to restart an aborted training
sample = find_sample_to_start_with(OUTPUT_PATH);
if(sample > 1) 
    fprintf('### Restarting at saved sample %d \n### (to fully restart, please remove files in output directory)\n', sample-1);
    LDA_OUTPUT_FILENAME = get_LDA_output_filename(OUTPUT_PATH, sample-1);
    load(LDA_OUTPUT_FILENAME);
end

% Run the sampling inference algorithm to collect the desired number of
% samples
while(sample <= N_SAMPLES)
    seed = sample; % Need to be changed every time
    
    if(sample == 1)
        n_sampling_steps = BURNIN_PERIOD;
    else
        n_sampling_steps = THINNING_PERIOD;
    end
    
    fprintf('# Sampling\n');
    tic;
    [words_counts, docs_counts, topics_vector] = ...
        gibbs_sampler_LDA(words_vector, docs_vector, N_TOPICS, ...
        n_sampling_steps , ALPHA , BETA , seed , SHOW_LDA_DETAILS, topics_vector);
    sampling_time = toc;
    display(sampling_time);
    
    fprintf('# Computing estimates for topics distributions and topics proportions\n');
    phi = estimate_phi(words_counts, BETA); %#ok<*NASGU>
    theta = estimate_theta(docs_counts, ALPHA);
    
    fprintf('# Saving sample\n')
    LDA_OUTPUT_FILENAME = get_LDA_output_filename(OUTPUT_PATH, sample);
    display(LDA_OUTPUT_FILENAME);
    save(LDA_OUTPUT_FILENAME, 'N_TOPICS', 'ALPHA', 'BETA', ...
        'phi', 'theta', 'topics_vector', 'sampling_time', ...
        'INIT_SEED', 'BURNIN_PERIOD', 'THINNING_PERIOD', 'N_SAMPLES', '-v7.3');
    
    sample = sample + 1;
end

end

function LDA_OUTPUT_FILENAME = get_LDA_output_filename(OUTPUT_PATH, sample)
LDA_OUTPUT_FILENAME = sprintf([OUTPUT_PATH 'output_LDA_sample%d.mat'], sample);
end

function sample = find_sample_to_start_with(OUTPUT_PATH)
sample = 1;
while(exist(get_LDA_output_filename(OUTPUT_PATH, sample), 'file'))
    sample = sample + 1;
end
end
