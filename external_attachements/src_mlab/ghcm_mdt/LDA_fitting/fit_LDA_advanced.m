% fit_LDA_advanced Fit LDA, with possibility to automatically stop when the model
% seems stable, and to automatically fit hyperparameters using ML estimates.
%
% fit_LDA_advanced(docs_vector, words_vector, OUTPUT_FILENAME, PARAMS)
%
% Perform sampling with (docs_vector, words_vector), for a  LDA model with
% parameters PARAMS.N_TOPICS, PARAMS.ALPHA and PARAMS.BETA.
%
% N_SWEEPS_PER_ITER sweeps are performed at each iteration.
% Doing several sweeps per iteration allows to stay in the mex routine, and
% therefore avoid 'translation' overhead. However, few sweeps per iteration
% can allow to detect convergence faster (and also to save more regularly
% to restart in case of crash).
%
% At most PARAMS.MAX_ITERS iterations are performed, therefore at most
% PARAMS.MAX_ITERS * PARAMS.N_SWEEPS_PER_ITER sweeps are performed.
%
% To enable convergence detection, set PARAMS.AUTO_STOP=true. The smoothing
% of the convergence criterion can be set through PARAMS.STOP_AVG_ITERS.
%
% To enable automatic hyperparameter fitting, set PARAMS.AUTO_FIT_ALPHA=true
% and/or PARAMS.AUTO_FIT_BETA=true. The automatic estimation will only
% start after PARAMS.AUTO_FIT_BURNIN iterations (PARAMS.ALPHA/BETA are used
% until this point). Moreover, to improve speed, automatic estimation will
% only be performed every PARAMS.AUTO_FIT_PERIOD iterations.
%
% To enable robust theta/phi estimation, set PARAMS.ROBUST_ESTIMATES=true.
%
% The function displays the evolution of the convergence criterion in real
% time, as well as the maximum-likelihood estimates for alpha and beta
% (even if automatic convergence and/or hyperparameter fitting is disabled).
%
% Note that the directory which will contain OUTPUT_FILENAME must exist.
% A single sample will be produced in OUTPUT_FILENAME (but state is saved
% every PARAMS.N_SWEEPS_PER_ITER to allow restarts).
% Its most important variables are:
% - PARAMS          parameters used to fit the model
% - iters_done      scalar, number of iteration performed to obtain this sample
% - topics_vector   N_TOKENS x 1 vector, topic assigned to each token
% - phi             VOC_SIZE x N_TOPICS matrix, words distributions by topic
% - theta           N_TOPICS x N_DOCS matrix, topics distributions by document
% [- robust_phi     present only if PARAMS.ROBUST_ESTIMATES=true]
% [- robust_theta   present only if PARAMS.ROBUST_ESTIMATES=true]
%
% For more details about the possibilities, please have a look at
% references/GibbsSamplingForLDA.pdf.
%
% INPUT
%   docs_vector     Nx1 vector
%   words_vector    Nx1 vector
%   OUTPUT_FILENAME string
%   PARAMS          structure with doubles (and logical)
%    .N_TOPICS          default: 50
%    .ALPHA             default: 0.1
%    .BETA              default: 0.1
%
%    .N_SWEEPS_PER_ITER default: 10
%
%    .MAX_ITERS         default: 20
%    .AUTO_STOP         default: false
%    .STOP_AVG_ITERS    default: 5
%
%    .AUTO_FIT_ALPHA    default: false
%    .AUTO_FIT_BETA     default: false
%    .AUTO_FIT_BURNIN   default: 5
%    .AUTO_FIT_PERIOD   default: 5
%
%    .INIT_SEED         default: 1
%    .SHOW_DETAILS      default: 1
%
%    .ROBUST_ESTIMATES  default: false
%    .N_SAMPLES_FOR_PHI default: 10
%    .N_SAMPLES_FOR_THETA default: 10
%    .BURNIN_FOR_THETA  default: 10
function fit_LDA_advanced(docs_vector, words_vector, OUTPUT_FILENAME, PARAMS)

% Set default params if needed
PARAMS = handle_params(PARAMS);

% Set useful constant
N_TOKENS = length(docs_vector);

% Generate random initial topics (usually denoted by z)
rng(PARAMS.INIT_SEED); % To be able to reproduce results
topics_vector = randi(PARAMS.N_TOPICS, N_TOKENS, 1);

% Initialize vector keeping track various quantities
distances = nan(1, PARAMS.MAX_ITERS);
alphas_mle = nan(1, PARAMS.MAX_ITERS);
betas_mle = nan(1, PARAMS.MAX_ITERS);
iterations_times = nan(1, PARAMS.MAX_ITERS);

% Allow to restart an aborted training
if(exist(OUTPUT_FILENAME, 'file'))
    load(OUTPUT_FILENAME)
    fprintf('### Restarting after %d sweeps \n', iters_done); %#ok<NODEF>
    fprintf('### (to fully restart, please remove output file)\n')
    plot_diagnostics(distances, alphas_mle, betas_mle, theta, phi); %#ok<NODEF>
else
    iters_done = 0;
end

% Run the sampling inference algorithm until we reach the maximum number of
% iteration is reached, or until the convergence criterion is met (if
% enabled).
should_stop = false;
while(iters_done < PARAMS.MAX_ITERS && ~should_stop)
    fprintf('\n### Iteration %d / %d\n', iters_done + 1, PARAMS.MAX_ITERS);
    tic;
    seed = iters_done; % Need to be changed every time
    
    % For the stopping criterion, we need to keep track of the
    % previous phi in order to compute the distance.
    if(iters_done == 0)
        [init_words_counts, ~] = compute_counts(words_vector, docs_vector, topics_vector, PARAMS.N_TOPICS);
        old_phi = estimate_phi(init_words_counts, PARAMS.BETA);
    else
        old_phi = phi;
    end
    
    % Set values for hyperparameters alpha and beta (automatically or not)
    if(PARAMS.AUTO_FIT_ALPHA && iters_done >= PARAMS.AUTO_FIT_BURNIN)
        alpha = alphas_mle(iters_done - 1); % Use the MLE
    else
        alpha = PARAMS.ALPHA;
    end
    if(PARAMS.AUTO_FIT_BETA && iters_done >= PARAMS.AUTO_FIT_BURNIN)
        beta = betas_mle(iters_done - 1); % Use the MLE
    else
        beta = PARAMS.BETA;
    end
    
    % Perform the necessary number of sampling sweeps
    fprintf('# Sampling\n');
    [words_counts, docs_counts, topics_vector] = ...
        gibbs_sampler_LDA(words_vector, docs_vector, PARAMS.N_TOPICS, ...
        PARAMS.N_SWEEPS_PER_ITER, alpha ,beta , seed , ...
        PARAMS.SHOW_DETAILS, topics_vector);
    
    % Update current number of iterations
    iters_done = iters_done + 1;
    
    % Compute phi and theta
    fprintf('# Computing estimates for phi and theta\n');
    phi = estimate_phi(words_counts, beta);
    theta = estimate_theta(docs_counts, alpha);
    
    % Compute current distance
    distances_per_topic = 1/2*sum(abs(old_phi - phi), 1);
    distances(iters_done) = mean(distances_per_topic);
    
    % Compute MLE for alpha and beta, every AUTO_FIT_PERIOD iteration
    if(mod(iters_done, PARAMS.AUTO_FIT_PERIOD) == 1 || PARAMS.AUTO_FIT_PERIOD == 1)
        alphas_mle(iters_done) = estimate_dirichlet_mle(docs_counts');
        betas_mle(iters_done) = estimate_dirichlet_mle(words_counts);
    else
        alphas_mle(iters_done) = alphas_mle(iters_done-1);
        betas_mle(iters_done) = betas_mle(iters_done-1);
    end
    
    % Plot diagnotics
    plot_diagnostics(distances, alphas_mle, betas_mle, theta, phi);
    
    % Check the convergence
    if(PARAMS.AUTO_STOP)
        should_stop = check_convergence(distances, iters_done, PARAMS.STOP_AVG_ITERS);
    end
    
    % Compute and display time needed for the iteration
    iterations_times(iters_done) = toc;
    display(iterations_times(iters_done));
    
    % Save the current state
    fprintf('# Saving (restart) sample\n')
    save(OUTPUT_FILENAME, 'PARAMS', ...
        'phi', 'theta', 'topics_vector', 'iterations_times', 'iters_done', ...
        'distances','alphas_mle', 'betas_mle', '-v7.3');
    
    % If required, compute robust estimates of phi and theta at the end
    if(PARAMS.ROBUST_ESTIMATES && (iters_done == PARAMS.MAX_ITERS || should_stop))
        fprintf('# Computing and saving robust estimates for phi and theta\n')
        
        [robust_phi, ~] = estimate_robust_phi(...
            words_vector, docs_vector, topics_vector, alpha, beta, ...
            PARAMS.N_SAMPLES_FOR_PHI);
        
        [robust_theta, ~] = estimate_robust_theta(...
            words_vector, docs_vector, topics_vector, alpha, ...
            robust_phi, PARAMS.N_SAMPLES_FOR_THETA, PARAMS.N_SAMPLES_FOR_PHI); %#ok<ASGLU>
        
        save(OUTPUT_FILENAME, '-append', 'robust_phi', 'robust_theta');
    end
end

end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Set default params if needed
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function PARAMS = handle_params(PARAMS)
% Model parameters
if(~isfield(PARAMS, 'N_TOPICS'));           PARAMS.N_TOPICS = 50;           end
if(~isfield(PARAMS, 'ALPHA'));              PARAMS.ALPHA = 0.1;             end
if(~isfield(PARAMS, 'BETA'));               PARAMS.BETA = 0.1;              end

% Iteration size
% Doing several sweeps per iteration allows to stay in the mex routine, and
% therefore avoid 'translation' overhead. However, few sweeps per iteration
% can allow to detect convergence faster (and also to save more regularly
% to restart in case of crash).
if(~isfield(PARAMS, 'N_SWEEPS_PER_ITER'));	PARAMS.N_SWEEPS_PER_ITER = 10;  end

% Convergence parameters
if(~isfield(PARAMS, 'MAX_ITERS'));          PARAMS.MAX_ITERS = 20;          end
if(~isfield(PARAMS, 'AUTO_STOP'));          PARAMS.AUTO_STOP = false;       end
if(~isfield(PARAMS, 'STOP_AVG_ITERS'));     PARAMS.STOP_AVG_ITERS = 5;      end

% Auto-fit parameters
if(~isfield(PARAMS, 'AUTO_FIT_ALPHA'));     PARAMS.AUTO_FIT_ALPHA = false;  end
if(~isfield(PARAMS, 'AUTO_FIT_BETA'));      PARAMS.AUTO_FIT_BETA = false;   end
if(~isfield(PARAMS, 'AUTO_FIT_BURNIN'));    PARAMS.AUTO_FIT_BURNIN = 5;     end
if(~isfield(PARAMS, 'AUTO_FIT_PERIOD'));    PARAMS.AUTO_FIT_PERIOD = 5;     end

% Seed
if(~isfield(PARAMS, 'INIT_SEED'));          PARAMS.INIT_SEED = 1;           end

% Display
if(~isfield(PARAMS, 'SHOW_DETAILS'));       PARAMS.SHOW_DETAILS = 1;        end

% Robust estimators
if(~isfield(PARAMS, 'ROBUST_ESTIMATES'));   PARAMS.ROBUST_ESTIMATES = false;end
if(~isfield(PARAMS, 'N_SAMPLES_FOR_PHI'));  PARAMS.N_SAMPLES_FOR_PHI = 10;  end
if(~isfield(PARAMS, 'N_SAMPLES_FOR_THETA'));PARAMS.N_SAMPLES_FOR_THETA = 10;end
if(~isfield(PARAMS, 'BURNIN_FOR_THETA'));   PARAMS.BURNIN_FOR_THETA = 10;   end

display(PARAMS);
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Plot diagnostics (all distances/alphas_mle/betas_mle available)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function plot_diagnostics(distances, alphas_mle, betas_mle, theta, phi)
MAX_ITER = length(distances);

N_ROWS = 2;
N_COLS = 3;

FIG_WIDTH = 1000;
FIG_HEIGHT = 600;
set(gcf, 'Position', [0, 0, FIG_WIDTH, FIG_HEIGHT])

subplot(N_ROWS, N_COLS, 1)
plot(alphas_mle)
title('MLE for alpha')
xlim([1 MAX_ITER])
ylim([0 max(alphas_mle)])
xlabel('Number of iterations')

subplot(N_ROWS, N_COLS, 4)
plot(betas_mle)
title('MLE for beta')
xlim([1 MAX_ITER])
ylim([0 max(betas_mle)])
xlabel('Number of iterations')

% Plot current theta and phi
N_TOPICS_TO_SHOW = min(100, size(theta, 1));
N_DOCS_TO_SHOW = min(100, size(theta, 2));
N_WORDS_TO_SHOW = min(100, size(phi, 1));

subplot(N_ROWS, N_COLS, 2)
theta_reduced = theta(:, 1:N_DOCS_TO_SHOW);
sorted_theta = sort(theta_reduced, 1, 'descend');
imagesc(log(sorted_theta(1:N_TOPICS_TO_SHOW, :)));
title('Log theta (topics presences in documents)')
xlabel('Documents')
ylabel('Topics sorted by importance')
colorbar

subplot(N_ROWS, N_COLS, 5)
sorted_phi = sort(phi, 1, 'descend');
imagesc(log(sorted_phi(1:N_WORDS_TO_SHOW, 1:N_TOPICS_TO_SHOW)))
title('Log phi (words presences in topics)')
xlabel('Topics')
ylabel('Words sorted by importance')
colorbar

% Plot convergence criterion
subplot(N_ROWS, N_COLS, 3)
plot(distances)
title('Phi variation')
xlim([1 MAX_ITER])
ylim([0 max(distances)])
xlabel('Number of iterations')

end


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Check the convergence
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function should_stop = check_convergence(distances, sweeps_done, STOP_AVG_SWEEPS)
% Check for convergence only after each STOP_AVG_SWEEPS sweeps
if(mod(sweeps_done, STOP_AVG_SWEEPS) ~= 0)
    should_stop = false;
else
    % Compute old and new (averaged) distance between successive phi (averaging
    % is done over STOP_AVG_SWEEPS samples)
    if(sweeps_done < 2*STOP_AVG_SWEEPS)
        old_distance = Inf;
    else
        old_distance = mean(...
            distances(sweeps_done-2*STOP_AVG_SWEEPS+1:sweeps_done-STOP_AVG_SWEEPS));
    end
    new_distance = mean(distances(sweeps_done-STOP_AVG_SWEEPS+1:sweeps_done));
    
    % If the distance is non-decreasing, we consider that convergence is
    % reached (corresponds to saying that variability of samples stop
    % decreasing).
    if(new_distance >= old_distance)
        should_stop = true;
    else
        should_stop = false;
    end
end
end

