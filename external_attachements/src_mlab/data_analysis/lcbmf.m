function  lcbmf( )
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
figure(1); set(gcf,'Name','Data','Color','w');

% Plot N random data images
%plotfun(X(:,randi(J, N, 1)));

%%Mean and covariance
%initialize zero mean for A and B
muA = zeros(I*N,1);
disp('begin generating 1...')
muB = zeros(N*J,1);
disp('begin generating 2...')

sigmaA = eye(I*N);
disp('begin generating 3...')
sigmaB = eye(N*J);
disp('begin generating 4...')
sigmaAB = zeros(I*N,N*J);
disp('begin generating 5...')
sigmaBA = sigmaAB';
disp('begin generating 6...')

X_vec = vectorize_data(X);
disp('begin generating 7...')

% Initialize A
A = rand(I,N);
disp('begin generating 8...')
A_vec = vectorize_A(A);
disp('begin generating 9...')

% Initialize B
B = rand(N,J);
disp('begin generating 10...')
B = bsxfun(@rdivide, B, sum(B,1));
disp('begin generating 11...')
B_vec = vectorize_B(B);
disp('begin generating 12...')

% Initialize noise variance
noise_sigma = ones(I,J);
disp('begin generating 13...')
noise_sigma_vec = vectorize_noise(noise_sigma);
disp('begin generating 14...')
sigma = 1;
disp('begin generating 15...')


%% Constraints

% A: Between zero and one
disp('begin generating 16...')
AA = [eye(I*N);-eye(I*N)];
disp('begin generating 17...')
bA = [zeros(I*N,1);-1*ones(I*N,1)];

% B: Greater than zero
disp('begin generating 18...')
BA = eye(J*N);
disp('begin generating 19...')
Bb = zeros(J*N,1);
disp('begin generating 20...')
% B: Sum to one
vec = ones(1,N);
disp('begin generating 21...')
BAeq = diagonalize(vec, J);
disp('begin generating 22...')
Bbeq = ones(J,1);
disp('begin generating 23...')

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
    
    %disp('begin generating A...')
    %Generate A_vec
    mu_tilda = muA + sigmaAB*(sigmaB\(B_vec-muB));
    sigma_tilda = sigmaA-sigmaAB*(sigmaB\sigmaBA);
    
    %disp('a_tildas computed')
    %size(diagonalize(B,I)')
    %size(diag(noise_sigma_vec))
    %size(noise_sigma_vec)
    sigma_bar = inv(inv(sigma_tilda)+diagonalize(B,I)*(diag(noise_sigma_vec)\(diagonalize(B,I)')));
    mu_bar = sigma_bar*(sigma_tilda\mu_tilda+ diagonalize(B,I)* (diag(noise_sigma_vec)\X_vec));
   
    %disp('a_bars computed')
    
    A_vec = randcg(mu_bar, sigma_bar, AA, bA, [], [], A_vec, 1);
    
    %disp('new a_vec generated')
   
    A = matrix_A(A_vec, I, N);
    
    %disp('new a_mat constructed')
    
    % Generate noise variance
    C = B*B'; D = X*B';
    sigma = 1/gamrnd((I*J)/2+1, 1/(x+sum(sum(A.*(A*C-2*D)))/2));
    noise_sigma = sigma * ones(I,J);
    
    %disp('noise_mat generated')
    
    noise_sigma_vec = vectorize_noise(noise_sigma);
    
    
    %disp('noise_vec constructed')
    
    
    
    
    %Generate B_vec
    %disp('begin generating B...')
    mu_tilda = muB + sigmaBA*(sigmaA\(A_vec-muA));
    sigma_tilda = sigmaB - sigmaBA*(sigmaA\sigmaAB);
    
    %disp('b_tildas computed')
    %size(noise_sigma_vec)
    %size(diag(noise_sigma_vec))
    
    sigma_bar = inv(inv(sigma_tilda)+diagonalize(A,J)'*(diag(noise_sigma_vec)\(diagonalize(A,J))));
    mu_bar = sigma_bar*(sigma_tilda\mu_tilda + diagonalize(A,J)'*(diag(noise_sigma_vec)\X_vec));
    
    %disp('b_bars computed')
    
    B_vec = randcg(mu_bar, sigma_bar, BA, Bb, BAeq, Bbeq, B_vec,1);
    
    %disp('new b_vec generated')
    
    B = matrix_B(B_vec, J, N);
    
    %disp('new b_mat constructed')
    
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



