% This function create a diagram of a corpus with topics assigned to words
% It is similar to Steyvers2007 diagrams
function plot_corpus(docs_vector, words_vector, topics_vector)

n_tokens = length(docs_vector);
n_docs = max(docs_vector);
n_words = max(words_vector);

symbols = {'xb', 'or', 'sg', '*k'};
% http://www.mathworks.de/de/help/matlab/ref/linespec.html

figure_handle = gcf;
clf(figure_handle) % clear the figure
set(figure_handle, 'Position', [0, 1000, n_words*150, n_docs*20]);
% plot([], [])
xlim([0 n_words+1])
ylim([0 n_docs])
axis off
set(figure_handle, 'Color', 'w')
hold on

% To plot token of same doc-topic shifted
[occurence_no] = compute_occurence_no(docs_vector, words_vector);
max_occurence_no = max(occurence_no);


% Plot each token in the corresponding doc and word, using a symbol
% depending on the assigned topic
for i=1:n_tokens
    shift = occurence_no(i) / max_occurence_no / 2;
    plot(words_vector(i)+shift, n_docs+1-docs_vector(i), symbols{topics_vector(i)})
end

% Display doc numbers
for d=1:n_docs
    text(0, n_docs+1-d, sprintf('doc %d', d))
end

hold off

end


% Utility function for 'plot_sample.m' to know for each token how many times the
% word-topic has already appeared before
% Careful: may not be very efficient for large datasets
function [occurence_no] = compute_occurence_no(docs_vector, words_vector)
n_tokens = length(docs_vector);

occurence_no = zeros(1, n_tokens);
docs_words_occurence_count = zeros(length(docs_vector), length(words_vector));

for i=1:n_tokens
    d = docs_vector(i);
    w = words_vector(i);
    occurence_no(i) = docs_words_occurence_count(d,w);
    docs_words_occurence_count(d,w) = docs_words_occurence_count(d,w)+1;
end

end