% Compute the exact value of p(z|w), feasible only for very small cases, 
% check reference for details
function p_z_given_w = compute_p_z_given_w(words_vector, docs_vector, topics_vector, ...
    N_DOCS, VOC_SIZE, N_TOPICS, ALPHA, BETA)

p_z_w = compute_p_z_w(words_vector, docs_vector, topics_vector, N_DOCS, VOC_SIZE, N_TOPICS, ALPHA, BETA);

p_w = compute_p_w(words_vector, docs_vector, N_DOCS, VOC_SIZE, N_TOPICS, ALPHA, BETA);

p_z_given_w =  p_z_w / p_w;
    
end

% Compute p(w) by summing p(w,z) over all possible z
function p_w = compute_p_w(words_vector, docs_vector, N_DOCS, VOC_SIZE, N_TOPICS, ALPHA, BETA)
N_TOKENS = length(words_vector);

topics_vectors = generate_topics_vectors(N_TOPICS, N_TOKENS);

p_w = 0;
for i = 1:size(topics_vectors, 2)
    p_w = p_w + compute_p_z_w(words_vector, docs_vector, topics_vectors(:,i), ...
        N_DOCS, VOC_SIZE, N_TOPICS, ALPHA, BETA);
end

end

% Basic formula for p(z,w), where phi and theta have been integrated out
function p_z_w = compute_p_z_w(words_vector, docs_vector, topics_vector, N_DOCS, VOC_SIZE, N_TOPICS, ALPHA, BETA)
[words_counts, docs_counts] = compute_counts(...
    words_vector, docs_vector, topics_vector, N_TOPICS, VOC_SIZE, N_DOCS);

part1 = (gamma(N_TOPICS*ALPHA)/gamma(ALPHA)^N_TOPICS)^N_DOCS;
part2 = prod(prod(gamma(ALPHA+docs_counts),2)./gamma(N_TOPICS*ALPHA+sum(docs_counts,2)), 1);
part3 = (gamma(VOC_SIZE*BETA)/gamma(BETA)^VOC_SIZE)^N_TOPICS;
part4 = prod(prod(gamma(BETA+words_counts),1)./gamma(VOC_SIZE*BETA+sum(words_counts,1)),2);

p_z_w =  part1 * part2 * part3 * part4;

end
