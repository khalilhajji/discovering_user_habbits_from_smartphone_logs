% Display the (sampled) counts of words in topics.
% 
% DISPLAY_WORDS_COUNTS(words_counts, vocabulary, TOPICS_TO_WRITE, ...
%                      topics_names, N_ROWS, N_COLS, FILENAME)
%
% See also: display_docs.m
%
% INPUT
%   words_counts:       VOC_SIZExN_TOPICS sparse matrix
%   vocabulary:         VOC_SIZEx1 cell array
%   TOPICS_TO_WRITE:    1xM vector
%   [topics_names]:     N_TOPICSx1 cell array, optional (default [])
%   [N_ROWS]:           scalar, optional (default 5)
%   [N_COLS]:           scalar, optional (default 5)
%   [FILENAME]:         string, optional (default [])
function display_words_counts(words_counts, vocabulary, TOPICS_TO_WRITE, ...
    topics_names, N_ROWS, N_COLS, FILENAME)

% Set default parameters if needed
if(~exist('topics_names', 'var'))
    topics_names = [];
end

if(~exist('N_ROWS', 'var'))
    N_ROWS = 5;
end

if(~exist('N_COLS', 'var'))
    N_COLS = 5;
end

if(exist('FILENAME', 'var'))
    fid = fopen(FILENAME, 'a+');
else
    fid = 1; % Standard output
end

% Write topic by topic
for i = 1:length(TOPICS_TO_WRITE)
    topic_to_write = TOPICS_TO_WRITE(i);
    
    % Retrieve the counts of words for the topic
    topic_words_counts = words_counts(:, topic_to_write);
    
    % Count the total number of tokens, and add the topic name if given
    n_tokens = full(sum(topic_words_counts));
    if(isempty(topics_names))
        fprintf(fid, '# Topic %d (%d tokens)\n', topic_to_write, n_tokens);
    else
        fprintf(fid, '# Topic %d (%d tokens): %s\n', topic_to_write, n_tokens, topics_names{i});
    end
    
    PRINT_FORMAT = ' %4d %-10.10s ';
    print_ordered_grid(vocabulary, topic_words_counts, N_ROWS, N_COLS, fid, PRINT_FORMAT)
    
    fprintf(fid, '\n');
end

if(fid ~= 1)
    fclose(fid);
end
end

