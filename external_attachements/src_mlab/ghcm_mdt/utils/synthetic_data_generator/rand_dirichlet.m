% RAND_DIRICHLET Sample from dirichlet distribution with parameter alpha
% 
% [samples] = RAND_DIRICHLET(N_SAMPLES, N_DIM, ALPHA)
% 
% INPUT
%   N_SAMPLES    the number of samples (= multinomial distribs.) to generate
%   N_DIM       the dimensionality of the simplex
%   ALPHA       the dirichlet parameter (either a scalar or a vector)
%
% Uses gammar1 function from Statbox 4.2:
% If X_i~Gamma(k=alpha_i, theta=1), 
% Then (X_1, ..., X_n)/sum(X_i)~Dirichlet(alpha)

function [samples] = rand_dirichlet(N_SAMPLES, N_DIM, ALPHA)
assert(length(ALPHA) == N_DIM || length(ALPHA) == 1); % Check correct param

if(length(ALPHA) == 1) % If alpha is scalar, transform into a vector
    ALPHA = repmat(ALPHA, N_DIM, 1);
end

% Generate gamma samples with shape alpha_i (= k) and scale 1 (= theta)
shape = ALPHA;
X = zeros(N_DIM, N_SAMPLES);
for s=1:N_SAMPLES
    for d=1:N_DIM
       X(d,s) = gammar1(shape(d)); 
    end
end

% If alpha is very small, it can be that the sum of some column of X is 0,
% due to approximation error. In this case, we set randomly one of the X_i
% to 1.
for index = find(sum(X,1)==0)
    X(randi(N_DIM), index) = 1;
end

% Transform into dirichlet samples (in each column)
samples = bsxfun(@rdivide, X, sum(X, 1));

end


%GAMMAR Generates a gamma random deviate.
%	GAMMAR(A) is a random deviate from the standard gamma
%	distribution with shape parameter A.  A must be a scalar.
%
%	B*GAMMAR(A) is a random deviate from the gamma distribution
%	with shape parameter A and scale parameter B.  The distribution
%	then has mean A*B and variance A*B^2.
%
%	See GAMMAP, GAMMAQ, RAND.

% GKS 31 July 93

% Algorithm for A >= 1 is Best's rejection algorithm XG
% Adapted from L. Devroye, "Non-uniform random variate
% generation", Springer-Verlag, New York, 1986, p. 410.

% Algorithm for A < 1 is rejection algorithm GS from
% Ahrens, J.H. and Dieter, U. Computer methods for sampling
% from gamma, beta, Poisson and binomial distributions.
% Computing, 12 (1974), 223 - 246.  Adapted from Netlib
% Fortran routine.

% Source: Statbox4.2
function gam = gammar1(a)

a = a(1);
if a < 0,
   gam = NaN;
elseif a == 0,
   gam = 0;
elseif a >= 1,
   b = a-1;
   c = 3*a-0.75;
   accept = 0;
   while accept == 0,
      u = rand(2,1);
      w = u(1)*(1-u(1));
      y = sqrt(c/w)*(u(1)-0.5);
      gam = b+y;
      if gam >= 0,
         z = 64*w^3*u(2)^2;
         accept = ( z<=1-2*y^2/gam );
         if accept == 0,
            if b == 0,
                accept = ( log(z)<=-2*y );
            else
                accept = ( log(z)<=2*(b*log(gam/b)-y) );
            end;
         end;
      end;
   end;
else
   aa = 0;
   b = 1 + .3678794*a;
   accept = 0;
   while accept == 0,
      p = b*rand(1);
      if p < 1, 
         gam = exp(log(p)/a);
         accept = (-log(rand(1)) >= gam);
      else
         gam = -log((b-p)/a);
         accept = (-log(rand(1)) >= (1-a)*log(gam));
      end;
   end;
end;
end
