
function demo
%% Parameters

% Number of hidden sources
N = 40; 

% Number of Gibbs samples
T = 10000; % This will take a while to run

%% Load data

% Load data, X, from mat file
load mixeddigits

% Get data dimensions
[I,J] = size(X);


%% Display data

% Create a figure with white background
figure(1); set(gcf,'Name','Data','Color','w');

% Plot N random data images
plotfun(X(:,randi(J, N, 1)));

%% Constraints

% A: Between zero and one
AA = [eye(N);-eye(N)];
bA = [zeros(N,1);-1*ones(N,1)];

% B: Greater than zero
BA = eye(N);
Bb = zeros(N,1);

% B: Sum to one
BAeq = ones(1,N);
Bbeq = 1;

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

I
J

%% Run Gibbs sampler

% Create a figure with white background
figure(2); set(gcf,'Name','Result','Color','w');

% For each Gibbs sample
for t = 1:T
    t
    % Generate A
    C = B*B'; D = X*B';
    Mu = D/C; S = (sigma*eye(N))/C;       
    A = randcg(Mu', S', AA, bA, [], [], A', 1)';

    % Generate noise variance
    sigma = 1/gamrnd((I*J)/2+1, 1/(x+sum(sum(A.*(A*C-2*D)))/2));
    
    % Generate B
    E = A'*A; F = A'*X;
    Mu = E\F; S = E\(sigma*eye(N));
    B = randcg(Mu, S, BA, Bb, BAeq, Bbeq, B,1);

    % Plot the hidden sources
    plotfun(A);    
end

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