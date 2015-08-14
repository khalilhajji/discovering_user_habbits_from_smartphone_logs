% DISPLAY_DOCS displays a summary of the given documents
%
% DISPLAY_DOCS(sp_occurrences, vocabulary, DOCS_TO_WRITE, ...
%              docs_names, N_ROWS, N_COLS, FILENAME)
% 
% It retrieves the words present in the documents indexed by DOCS_TO_WRITE, 
% and displays the most common words and the total number of words.
%
% A name can be printed with each document by giving docs_names.
%
% To print more or less words for documents, N_ROWS and N_COLS can be given
% (by default, 5x5=25 words are printed for each document).
%
% If no FILENAME is given, the result will be printed on the standard
% output.
%
% INPUT
%   sp_occurrences      VOC_SIZExN_DOCS sparse matrix
%   vocabulary          VOC_SIZEx1 cell array
%   DOCS_TO_WRITE       1xM vector
%   [docs_names]        N_DOCSx1 cell array, optional (default [])
%   [N_ROWS]            scalar, optional (default 5)
%   [N_COLS]            scalar, optional (default 5)
%   [FILENAME]          string, optional (default [])
function display_docs(sp_occurrences, vocabulary, DOCS_TO_WRITE, ...
    docs_names, N_ROWS, N_COLS, FILENAME)

% Set default parameters if needed
if(~exist('docs_names', 'var'))
    docs_names = [];
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

% Write document by document
for i = 1:length(DOCS_TO_WRITE)
    doc_to_write = DOCS_TO_WRITE(i);
    
    % Retrieve number of occurrences of each word for the given document
    sp_doc = sp_occurrences(:, doc_to_write);
    
    % Count the number of tokens, and add the document name if given
    n_tokens = full(sum(sp_doc));
    if(isempty(docs_names))
        fprintf(fid, '# Doc %d (%d tokens)\n', doc_to_write, n_tokens);
    else
        fprintf(fid, '# Doc %d (%d tokens): %s\n', doc_to_write, n_tokens, docs_names{i});
    end
    
    PRINT_FORMAT = ' %3d %-10.10s ';
    print_ordered_grid(vocabulary, sp_doc, N_ROWS, N_COLS, fid, PRINT_FORMAT)
    
    fprintf(fid, '\n');
end

if(fid ~= 1)
    fclose(fid);
end
end

