% Utility function to order vocabulary according to given weights, and 
% print the words together with the weights, in a grid format.
% 
% Doesn't print zeros weights
function print_ordered_grid(vocabulary, weights, N_ROWS, N_COLS, fid, print_format)
% Find the ordered indices to display the terms (decreasing number)
I = find(weights); % Indices of non-zeros elements
[~, order] = sort(weights(I), 'descend'); % Order of non-zeros elements
ordered_I = I(order); % Original indices of non-zeros elements ordered

% Display at most N_ROWS * N_COLS words
n_words = min(length(ordered_I), N_ROWS * N_COLS);
ordered_I = ordered_I(1:n_words);

% Print the words and the weights
for row = 1:min(N_ROWS, n_words)
    for col = 1:N_COLS
        j = (col-1)*N_ROWS + row;
        if(j > n_words)
            continue;
        end
        
        word = vocabulary{ordered_I(j)};
        weight = full(weights(ordered_I(j)));
        fprintf(fid, print_format, weight, word);
    end
    
    fprintf(fid, '\n');
end
end
