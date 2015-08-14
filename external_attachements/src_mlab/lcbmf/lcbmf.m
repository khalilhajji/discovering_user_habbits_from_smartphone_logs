function [a_mat , b_mat] = lcbmf(X, N, T, AA, bA, AAeq, bAeq, BA, Bb, BAeq, Bbeq)
%% Parameters


% Get data dimensions
[I,J] = size(X);

%% Initialization

% Precompute sum of squares
x = sum(X(:).^2)/2;

% Initialize A
A = rand(I,N);

% Initialize B
B = rand(N,J);
B = bsxfun(@rdivide, B, sum(B,1));

% Initialize noise variance
sigma = 1;


%% Run Gibbs sampler

N

% For each Gibbs sample
for t = 1:T
   
    % Generate A
    C = B*B'; D = X*B';
    Mu = D/C; S = (sigma*eye(N))/C;       
    A = randcg(Mu', S', AA, bA, AAeq, bAeq, A', 1)';

    % Generate noise variance
    sigma = 1/gamrnd((I*J)/2+1, 1/(x+sum(sum(A.*(A*C-2*D)))/2));
    
    % Generate B
    E = A'*A; F = A'*X;
    Mu = E\F; S = E\(sigma*eye(N));
    B = randcg(Mu, S, BA, Bb, BAeq, Bbeq, B,1);    
end

a_mat = A;
b_mat = B;
end



