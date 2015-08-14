% The goal of this function is to substitute GibbsSamplerLDA.c,
% to understand and to debug it
%
% MODIFIED TO WRITE WHEN SAMPLE IS DIFFERENT DUE TO RATING Y
function [ WP,DP,Z ] = gibbs_sampler_SLDA( WS,DS,T,N_ITER,ALPHA,BETA,SEED,OUTPUT,ZIN, ...
    RATED_DOCS, YS, ETA, SIGMA2)

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CONVERT VARIABLE NAMES LIKE MEX GATEWAY FUNCTION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
N_TOKENS = length(WS);
N_TOPICS = T;

W = max(WS);
D = max(DS);

z = ZIN; % Not index shift compared to GibbsSamplerLDA.c
ws = WS; % Not index shift compared to GibbsSamplerLDA.c
ds = DS; % Not index shift compared to GibbsSamplerLDA.c

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MEX ROUTINE FUNCTION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% /* Build the count matrices (and ztot) from previous topic assignation z */
wp = zeros(W, N_TOPICS);
dp = zeros(D, N_TOPICS);
ztot = zeros(1, N_TOPICS);
for i = 1:N_TOKENS
    topic = z(i);
    wp(ws(i), topic) = wp(ws(i), topic) + 1;
    dp(ds(i), topic) = dp(ds(i), topic) + 1;
    ztot(topic) = ztot(topic) + 1;
end

% /* Precompute the number of tokens per document */
n_tokens_by_doc = sum(dp, 2);

% /* Precompute constant W*BETA */
WBETA = W*BETA;

% /* Generate a random permutation of 1:N_TOKENS */
% /* (=> random update sequence, same for all iterations!) */
order = randperm(N_TOKENS);

% /* Performs N_ITER iterations over all the tokens */
for iter = 0:N_ITER-1
    if(OUTPUT >=1 && (mod(iter, 10)==0))
        fprintf('\tIteration %d of %d\n', iter, N_ITER);
    end
    
    % /* Iterate over all tokens, according to 'order' */
    for i = 1:N_TOKENS
        % /* Get the index of the current token to assess */
        iToken = order(i);
        
        % /* Get the current topic assigned to token */
        topic = z(iToken);
        word = ws(iToken);
        doc = ds(iToken);
        
        % /* Update counts (remove current token) */
        ztot(topic) = ztot(topic) - 1; %/* substract from counts sums */
        wp(word, topic) = wp(word, topic) - 1;
        dp(doc, topic) = dp(doc, topic) - 1;
        
        % /* Check whether the document of this token has an associated rating */
        if(RATED_DOCS(doc) == 1)
            y = YS(doc);
            N_d = n_tokens_by_doc(doc);
            
            lp_y_given_z = zeros(1, N_TOPICS);
            
            for j = 1:N_TOPICS
                dp(doc, j) = dp(doc, j) + 1;
                
                tmp_double = 0;
                for k = 1:N_TOPICS
                    tmp_double = tmp_double + ETA(k) * dp(doc, k);
                end
                
                tmp_double = tmp_double / N_d;
                tmp_double = tmp_double - y;
                lp_y_given_z(j) = -tmp_double*tmp_double/(2*SIGMA2);
                
                %                     fprintf('p_y_given_z: %f \n', p_y_given_z);
                
                dp(doc, j) = dp(doc, j) - 1;
            end
            
            % /* Rescale log proba, to avoid that everything becomes 0 when using exp() */
            lp_y_given_z = lp_y_given_z - max(lp_y_given_z);
            
            p_y_given_z = exp(lp_y_given_z);
        else
            p_y_given_z = ones(1, N_TOPICS);
        end
        
        % /* !!! Compute the (unormalized) conditional probas (see paper) !!! */
        probs = zeros(1, N_TOPICS);
        totProb = 0;
        probsLDA = zeros(1, N_TOPICS);
        totProbLDA = 0;
        for j = 1:N_TOPICS
            probs(j) = ( wp(word, j) + BETA) ...
                / ( ztot(j) + WBETA) ...
                * (dp(doc, j) + ALPHA) ...
                * p_y_given_z(j);
            
            totProb = totProb + probs(j);
            
            probsLDA(j) = ( wp(word, j) + BETA) ...
                / ( ztot(j) + WBETA) ...
                * (dp(doc, j) + ALPHA);
            
            totProbLDA = totProbLDA + probsLDA(j);
        end
        
        % /* Sample a topic from the resulting (unormalized) distribution */
        % /* Generate a random number 'rand' in [0, totProb] and find the topic */
        % /* for which the cumulative proba sum(probs(topic_i)) exceed 'rand' */
        rand_generated = rand();
        r = totProb * rand_generated;
        cumSum = probs(1);
        
        rLDA = totProbLDA * rand_generated;
        cumSumLDA = probsLDA(1);
        newTopic = 1;
        while (r > cumSum)
            if(rLDA<cumSumLDA)
                fprintf('SLDA makes a difference (token %d)\n', i)
            end
            newTopic = newTopic + 1;
            cumSum = cumSum + probs(newTopic);
            cumSumLDA = cumSumLDA + probsLDA(newTopic);
        end
        if(rLDA>cumSumLDA)
                fprintf('SLDA makes a difference (token %d)\n', i)
        end
        
        % /* Assign new topic current token */
        z(iToken) = newTopic;
        
        % /* Update counts (add newly sampled token) */
        ztot(newTopic) = ztot(newTopic) + 1;
        wp(word, newTopic) = wp(word, newTopic) + 1;
        dp(doc, newTopic) = dp(doc, newTopic) + 1;
    end
end


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CONVERT VARIABLE NAMES LIKE MEX GATEWAY FUNCTION
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
WP = sparse(wp);
DP = sparse(dp);
Z = z;

end