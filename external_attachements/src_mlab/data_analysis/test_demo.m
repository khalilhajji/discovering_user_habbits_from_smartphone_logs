function  test_demo( )
%% Parameters

% Number of hidden sources
N = 3; 

% Number of Gibbs samples
T = 10000; % This will take a while to run

%% Load data

% Load data, X, from mat file
load mixeddigits


X = [0.6, 0.3, 0.4, 0.5, 0.4, 0.5;
    0.4, 0.5, 0.6, 0.3, 0.4, 0.5; 
    0.4, 0.5, 0.4, 0.5, 0.6, 0.3;
    0.6, 0.4, 0.4, 0.6, 0.5, 0.5;
    0.4, 0.6, 0.6, 0.4, 0.5, 0.5];
X


% Get data dimensions
[I,J] = size(X);




%% Display data

% Create a figure with white background
%figure(1); set(gcf,'Name','Data','Color','w');

% Plot N random data images
%plotfun(X(:,randi(J, N, 1)));

%%Mean and covariance
%initialize zero mean for A and B


% Initialize A
A = rand(I,N);
disp('begin generating 8...')
A_vec = vectorize_A(A);
disp('begin generating 9...')

% Initialize B
B = rand(N,J);
disp('begin generating 10...')
B = bsxfun(@rdivide, B, sum(B,1));


% Initialize noise variance
sigma = 1;


%% Constraints

% A: Between zero and one
AA = [eye(I*N);-eye(I*N)];
bA = [zeros(I*N,1);-1*ones(I*N,1)];

% B: Greater than zero
BA = eye(N);
Bb = zeros(N,1);

% B: Sum to one
BAeq = ones(1,N);
Bbeq = 1;
%% Initialization

% Precompute sum of squares
x = sum(X(:).^2)/2;



I
J

%% Run Gibbs sampler

% Create a figure with white background
figure(2); set(gcf,'Name','Result','Color','w');
disp('entering the Gibbs loop')
% For each Gibbs sample
for t = 1:T
    t
    
     % Generate A
    C = B*B'; D = X*B';
    Mu = D/C; S = (sigma*eye(N))/C;
    Mu_vec = vectorize_A(Mu);
    S_vec = diagonalize(S, I);
    A_vec = randcg(Mu_vec, S_vec, AA, bA, [], [], A_vec, 1);
    
    A = matrix_A(A_vec, I, N);

    % Generate noise variance
    sigma = 1/gamrnd((I*J)/2+1, 1/(x+sum(sum(A.*(A*C-2*D)))/2));
    
    % Generate B
    E = A'*A; F = A'*X;
    Mu = E\F; S = E\(sigma*eye(N));
    B = randcg(Mu, S, BA, Bb, BAeq, Bbeq, B,1);

    % Plot the hidden sources
    %plotfun(A);    
end
A

end

% Function for plotting data and sources
function plotfun(X)
    % Set colormap to 256 level gray scale
    colormap(interp1([0;255],[1 1 1;0 0 0],0:255));
    
    % Get number of objects to plot
    N = size(X,2);
    
    % Compute number of rows and columns in plot
    rows = round(sqrt(N/2)); cols = ceil(N/rows);
    
    % For each image
    for n = 1:N
        % Make an axis
        subplot(rows, cols, n)
        
        % Plot the image
        image(reshape(X(:,n), [28 28])'*256)
        
        % Adjust the axis
        axis image off;
    end
    
    % Update display
    drawnow;
end


function [X_vec] = vectorize_data(X)
    %return [X(1,:),X(2,:)...,X(J,:)] <=> concatenates the rows of x
    X_transpose = X';  
    X_vec = X_transpose(:);
end

function [N_vec] = vectorize_noise(N)
    %return [X(1,:),X(2,:)...,X(J,:)] <=> concatenates the rows of x
    N_transpose = N';  
    N_vec = N_transpose(:);
end

function [A_vec] = vectorize_A(A)
    %return [X(1,:),X(2,:)...,X(J,:)] <=> concatenates the rows of x
    A_transpose = A';  
    A_vec = A_transpose(:);
end

function [A] = matrix_A(A_vec, I, N)
    A = reshape(A_vec, [N,I])';
   
end


function [B_vec] = vectorize_B(B)
    %return [X(:,1),X(:,2)...,X(:,J)] <=> concatenates the columns of x
    B_vec = B(:);
end

function [B] = matrix_B(B_vec, J, N)
    B = reshape(B_vec, [N,J]);
   
end

function [X_diag] = diagonalize(X, r)
    %construct a matrix with r repetitions of X along the diagonal of the
    %matrix X_diag
    X_diag = zeros(r*size(X));
    [N,M] = size(X);
    for i = 1:r
        X_diag((i-1)*N+1:i*N, (i-1)*M+1: i*M)=X;
    end
    
end




