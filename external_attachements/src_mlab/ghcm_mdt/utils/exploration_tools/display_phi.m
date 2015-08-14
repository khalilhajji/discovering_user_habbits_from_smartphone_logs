% Display the distribution of words in topics.
% 
% DISPLAY_PHI(phi, vocabulary, TOPICS_TO_WRITE, ...
%                      topics_names, N_ROWS, N_COLS, FILENAME)
% 
% See also: display_docs.m
%
% INPUT
%   phi                 VOC_SIZExN_TOPICS sparse matrix
%   vocabulary          VOC_SIZEx1 cell array
%   TOPICS_TO_WRITE     1xM vector
%   [topics_names]      N_TOPICSx1 cell array, optional (default [])
%   [N_ROWS]            scalar, optional (default 5)
%   [N_COLS]            scalar, optional (default 5)
%   [FILENAME]          string, optional (default [])
%   [PRINT_FORMAT]      string, optional (default ' %.3f %-10.10s ')
function display_phi(phi, vocabulary, TOPICS_TO_WRITE, ...
    topics_names, N_ROWS, N_COLS, FILENAME, PRINT_FORMAT)

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

if(~exist('PRINT_FORMAT', 'var'))
    PRINT_FORMAT = ' %.3f %-10.10s ';
end

if(exist('FILENAME', 'var') && ~isempty(FILENAME))
    fid = fopen(FILENAME, 'a+');
else
    fid = 1; % Standard output
end

% Write topic by topic
for i = 1:length(TOPICS_TO_WRITE)
    topic_to_write = TOPICS_TO_WRITE(i);
    
    % Retrieve the counts of words for the topic
    topic_phi = phi(:, topic_to_write);
    
    % Count the total number of tokens, and add the topic name if given
    if(isempty(topics_names))
        fprintf(fid, '# Topic %d\n', topic_to_write);
    else
        fprintf(fid, '# Topic %d: %s\n', topic_to_write, topics_names{topic_to_write});
    end
    
    print_ordered_grid(vocabulary, topic_phi, N_ROWS, N_COLS, fid, PRINT_FORMAT)
    
    fprintf(fid, '\n');
end

if(fid ~= 1)
    fclose(fid);
end
end

