function [X_diag] = test_fun(X, r)
    %construct a matrix with r repetitions of X along the diagonal of the
    %matrix X_diag
    X_diag = zeros(r*size(X));
    [N,M] = size(X);
    for i = 1:r
        X_diag((i-1)*N+1:i*N, (i-1)*M+1: i*M)=X;
    end
    
end

