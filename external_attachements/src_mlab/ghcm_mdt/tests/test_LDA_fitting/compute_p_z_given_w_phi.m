% Compute the exact value of p(z|w, phi), feasible only for very small cases, 
% check reference for details
function p_z_given_w_phi = compute_p_z_given_w_phi(words_vector, docs_vector, topics_vector, phi, ...
    N_DOCS, VOC_SIZE, N_TOPICS, ALPHA, BETA)

p_z_w_given_phi = compute_p_z_w_given_phi(words_vector, docs_vector, topics_vector, phi, ...
    N_DOCS, VOC_SIZE, N_TOPICS, ALPHA, BETA);

p_w_given_phi = compute_p_w_given_phi(words_vector, docs_vector, phi, N_DOCS, VOC_SIZE, N_TOPICS, ALPHA, BETA);

p_z_given_w_phi =  p_z_w_given_phi / p_w_given_phi;
    
end

% Compute p(w|phi) by summing p(w,z|phi) over all possible z
function p_w = compute_p_w_given_phi(words_vector, docs_vector, phi, N_DOCS, VOC_SIZE, N_TOPICS, ALPHA, BETA)
N_TOKENS = length(words_vector);

topics_vectors = generate_topics_vectors(N_TOPICS, N_TOKENS);

p_w = 0;
for i = 1:size(topics_vectors, 2)
    p_w = p_w + compute_p_z_w_given_phi(words_vector, docs_vector, topics_vectors(:,i), phi,...
        N_DOCS, VOC_SIZE, N_TOPICS, ALPHA, BETA);
end

end

% Basic formula for p(z,w|phi), where phi and theta have been integrated out
function p_z_w = compute_p_z_w_given_phi(words_vector, docs_vector, topics_vector, phi, N_DOCS, VOC_SIZE, N_TOPICS, ALPHA, BETA)
[~, docs_counts] = compute_counts(...
    words_vector, docs_vector, topics_vector, N_TOPICS, VOC_SIZE, N_DOCS);

part1 = (gamma(N_TOPICS*ALPHA)/gamma(ALPHA)^N_TOPICS)^N_DOCS;
part2 = prod(prod(gamma(ALPHA+docs_counts),2)./gamma(N_TOPICS*ALPHA+sum(docs_counts,2)), 1);

part3 = prod(phi(VOC_SIZE*(topics_vector-1)+words_vector)); % Access as a vector

p_z_w =  part1 * part2 * part3;

end
