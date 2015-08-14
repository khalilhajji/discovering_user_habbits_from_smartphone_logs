% Generate all possibilities, e.g if N_TOPICS = 2 and N_TOKENS = 3
%
%      1     2     1     2     1     2     1     2
%      1     1     2     2     1     1     2     2
%      1     1     1     1     2     2     2     2
%
% Highly inefficient ;)
function topics_vectors = generate_topics_vectors(N_TOPICS, N_TOKENS)

    function vector = generate_next(vector, N_TOPICS)
        pos = 1;
        while(vector(pos) == N_TOPICS)
            pos = pos + 1;
        end
        vector(pos) = vector(pos)+1;
        while(pos > 1)
            pos = pos - 1;
            vector(pos) = 1;
        end
        
    end

topics_vectors = ones(N_TOKENS, N_TOPICS^N_TOKENS);

for index = 2:N_TOPICS^N_TOKENS
    topics_vectors(:, index) = generate_next(topics_vectors(:, index-1), N_TOPICS);
end
end
