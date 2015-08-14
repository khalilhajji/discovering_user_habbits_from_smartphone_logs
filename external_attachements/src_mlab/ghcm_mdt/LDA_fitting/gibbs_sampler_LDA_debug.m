% The goal of this function is to substitute GibbsSamplerLDA.c,
% to understand and to debug it.
% 
% [words_counts, docs_counts, topics_vector_out] = gibbs_sampler_LDA_debug(...
%   words_vector, docs_vector, N_TOPICS, N_SWEEPS, ALPHA, BETA, ...
%   SEED, DISPLAY_OUTPUT, topics_vector_in, tokens_to_sample)
function [ words_counts1, docs_counts1, topics_vector_out ] = gibbs_sampler_LDA_debug(...
    words_vector1, docs_vector1, N_TOPICS, N_ITER, ALPHA, BETA, ...
    SEED, DISPLAY_OUTPUT, topics_vector_in, tokens_to_sample)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CONVERT VARIABLE NAMES LIKE MEX GATEWAY FUNCTION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
N_TOKENS = length(words_vector1);

VOC_SIZE = max(words_vector1);
N_DOCS = max(docs_vector1);

topics_vector = topics_vector_in; % Not index shift compared to GibbsSamplerLDA.c
words_vector = words_vector1; % Not index shift compared to GibbsSamplerLDA.c
docs_vector = docs_vector1; % Not index shift compared to GibbsSamplerLDA.c

if(~exist('tokens_to_sample', 'var'))
    tokens_to_sample = 1:N_TOKENS;
end
N_TOKENS_TO_SAMPLE = length(tokens_to_sample);

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MEX ROUTINE FUNCTION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% /* Build the count matrices (and ztot) from previous topic assignation topics_vector */
words_counts = zeros(VOC_SIZE, N_TOPICS);
docs_counts = zeros(N_DOCS, N_TOPICS);
ztot = zeros(1, N_TOPICS);
for i = 1:N_TOKENS
    topic = topics_vector(i);
    words_counts(words_vector(i), topic) = words_counts(words_vector(i), topic) + 1;
    docs_counts(docs_vector(i), topic) = docs_counts(docs_vector(i), topic) + 1;
    ztot(topic) = ztot(topic) + 1;
end

% /* Precompute constant VOC_SIZE*BETA */
VOC_SIZExBETA = VOC_SIZE*BETA;

% /* Generate a random permutation of 1:N_TOKENS */
% /* (=> random update sequence, same for all iterations!) */
previous_seed = rng(SEED); % Use the given seed, for reproductibility
tokens_to_sample = tokens_to_sample(randperm(N_TOKENS_TO_SAMPLE));
rng(previous_seed);

% /* Performs N_ITER iterations over all the tokens */
for iter = 0:N_ITER-1
    if(DISPLAY_OUTPUT >=1 && (mod(iter, 10)==0))
        fprintf('\tIteration %d of %d\n', iter, N_ITER);
    end
    
    % /* Iterate over all tokens, according to 'order' */
    for i = 1:N_TOKENS_TO_SAMPLE
        % /* Get the index of the current token to assess */
        iToken = tokens_to_sample(i);
        
        % /* Get the current topic assigned to token */
        topic = topics_vector(iToken);
        word = words_vector(iToken);
        doc = docs_vector(iToken);
        
        % /* Update counts (remove current token) */
        ztot(topic) = ztot(topic) - 1; %/* substract from counts sums */
        words_counts(word, topic) = words_counts(word, topic) - 1;
        docs_counts(doc, topic) = docs_counts(doc, topic) - 1;
        
        % /* !!! Compute the (unormalized) conditional probas (see paper) !!! */
        probs = zeros(1, N_TOPICS);
        totProb = 0;
        for j = 1:N_TOPICS
            probs(j) = ( words_counts(word, j) + BETA) ...
                / ( ztot(j) + VOC_SIZExBETA) ...
                * (docs_counts(doc, j) + ALPHA);
            
            totProb = totProb + probs(j);
        end
        
        % /* Sample a topic from the resulting (unormalized) distribution */
        % /* Generate a random number 'rand' in [0, totProb] and find the topic */
        % /* for which the cumulative proba sum(probs(topic_i)) exceed 'rand' */
        r = totProb * rand();
        cumSum = probs(1);
        newTopic = 1;
        while (r > cumSum)
            newTopic = newTopic + 1;
            cumSum = cumSum + probs(newTopic);
        end
        
        % /* Assign new topic current token */
        topics_vector(iToken) = newTopic;
        
        % /* Update counts (add newly sampled token) */
        ztot(newTopic) = ztot(newTopic) + 1;
        words_counts(word, newTopic) = words_counts(word, newTopic) + 1;
        docs_counts(doc, newTopic) = docs_counts(doc, newTopic) + 1;        
    end
end


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CONVERT VARIABLE NAMES LIKE MEX GATEWAY FUNCTION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
words_counts1 = sparse(words_counts);
docs_counts1 = sparse(docs_counts);
topics_vector_out = topics_vector;

end
