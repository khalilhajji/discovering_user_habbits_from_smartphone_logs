function x = randcg(mx, Sxx, A, b, Aeq, beq, x0, T)
% RANDCG Random numbers from constrained Gaussian density
%   p(x) = const * N(mx,Sxx), s.t. A*x-b>0, Aeq*x-beq=0
%
% Usage
%   x = randcg(mx, Sxx, A, b, Aeq, beq) draws a random vector from the
%   constrained multivariate Gaussian density.
%
% Input
%   mx          Mean vector
%   Sxx         Covariance matrix
%   A, b        Matrix and vector specifying inequality constraints
%   Aeq, beq    Matrix and vector specifying equality constraints

% Copyright 2009 Mikkel N. Schmidt, ms@it.dk, www.mikkelschmidt.dk

% Dimensionality of data
N = size(mx,1);

% Orthogonal basis of equality constraints + new origin
if isempty(Aeq) % No equality constraints: use standard basis
    P = zeros(0,N);
    K = eye(N);
    cx = zeros(N,1);
else
    [U,S] = svd(Aeq');
    [m,n] = size(Aeq);
    if m>1, s=diag(S); elseif m==1, s=S(1); else s=0; end
    tol = max(m,n)*max(s)*eps;
    r = sum(s>tol);
    P = U(:,1:r)';
    K = U(:,r+1:end)';
    cx = Aeq\beq;
end
if isempty(A) % No inequality constraints
    A = zeros(0,N);
    b = zeros(0,1);
end

% Dimensionality of space that satisfies eq. constraints
M = N-size(P,1);

W = K*(eye(N)-Sxx*P'*((P*Sxx*P')\P));
my = W*bsxfun(@minus,mx,cx);
L = chol(W*Sxx*K');

% Start point
w = L'\bsxfun(@minus, K*bsxfun(@minus, x0, cx), my);

% Precomputations for bounds
E = A*K'*L';
e = bsxfun(@minus, b, A*bsxfun(@plus, K'*my, cx));

% Loop over Gibbs sweeps
for t = 1:T
    % Loop over individual elements
    for m = 1:M
        % All indices except m
        nm = [1:m-1 m+1:M];

        % Compute lower and upper bound
        n = e-E(:,nm)*w(nm,:); %-EW
        d = E(:,m);
        lb = max(bsxfun(@rdivide,n(d>0,:),d(d>0,:)),[],1);
        if isempty(lb), lb = -inf; end
        ub = min(bsxfun(@rdivide,n(d<0,:),d(d<0,:)),[],1);
        if isempty(ub), ub = inf; end;
               
        % Draw from truncated Gaussian density
        w(m,:) = randstgs(lb, ub, w(m,:));
    end
end

% Final result mapped back to the original space
x = bsxfun(@plus, K'*bsxfun(@plus, L'*w, my), cx);

function x = randstgs(l, u, x)
% RANDTG Random numbers from standard truncated Gaussian density
%   p(x) = const * exp(-x^2/2) *I(l < x < u) using slice sampling
%
% Usage
%   x = randtg(l, u, x0) returns an array of random numbers chosen 
%     from the truncated Gaussian density. The size of x is the maximum 
%     common size of the parameters.
%
% Input
%   l, u         Truncation, l < x < u

% Copyright 2009 Mikkel N. Schmidt, ms@it.dk, www.mikkelschmidt.dk

sz = accumarray([1:ndims(l),1:ndims(u),1:ndims(x)]',[size(l),size(u),size(x)]',[],@max)';

z = bsxfun(@plus, -.5*x.^2, log(rand(sz)));
s = sqrt(-2*z);
ll = bsxfun(@max, -s, l);
uu = bsxfun(@min, s, u);
x = rand(sz).*(uu-ll)+ll;