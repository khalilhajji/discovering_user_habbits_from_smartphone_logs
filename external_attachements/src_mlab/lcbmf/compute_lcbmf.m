function compute_lcbmf(x_mat_path, x_mat_name, a_cons_path, b_cons_path, equality_key, inequality_key, coefs_key, biais_key, k, a_mat_path, b_mat_path )
%input: path to a matrix x , x_mat_name name of matrix as stored in doc
%       path to constrains a
%       path to constrains b
%       equality_key, inequality_key, coefs_key, biais_key the strings as
%       stored in the docs indicating to the inequality constrains to the
%       equality constrains to the coefs and to the biais specified by the
%       constrains
%       k: integer in a representing the number of sources (or hidden
%       topics) desired
%       path to output matrix a
%       path to output matrix b
%   
%computes the linear constrained baesyian matrix factorization of 
%x_mat= a_mat*b_mat under the linear constrains a and b.
%a are linear constrains imposed for a and b linear constrains imposed for
%b.
%writes the resulted matrices a_mat and b_mat in the indicated paths. 
x_mat_struc = load(x_mat_path , x_mat_name);
x_mat = x_mat_struc.(x_mat_name);

%Loading the linear constrains indicated for a_mat matrix
%Loading the coefs (co) and the biais (bi) of the equality such that
a_cons = load(a_cons_path);
%the coefficients of the a_mat constrains equality
%co*a-b=0
aa_cons_eq = double(a_cons.(strcat(equality_key,coefs_key)));
%the biais of a_mat constains equality
ab_cons_eq = double(a_cons.(strcat(equality_key,biais_key)));
%Loading the coefs (co) and the biais (bi) of the inequality such that
%co*a-b>=0
aa_cons_ineq = double(a_cons.(strcat(inequality_key,coefs_key)));
%the biais of a constains equality
ab_cons_ineq = double(a_cons.(strcat(inequality_key,biais_key)));

%Load in the same manner the constrains for b_mat matrix
b_cons = load(b_cons_path);

ba_cons_eq = double(b_cons.(strcat(equality_key,coefs_key)));
%the biais of a_mat constains equality
bb_cons_eq = double(b_cons.(strcat(equality_key,biais_key)));
%Loading the coefs (co) and the biais (bi) of the inequality such that
%co*a-b>=0
ba_cons_ineq = double(b_cons.(strcat(inequality_key,coefs_key)));
%the biais of a constains equality
bb_cons_ineq = double(b_cons.(strcat(inequality_key,biais_key)));

n = int64(str2double(k));
iterations = 10000;

[a_mat , b_mat] = lcbmf(x_mat, n, iterations, aa_cons_ineq, ab_cons_ineq, aa_cons_eq, ab_cons_eq, ba_cons_ineq, bb_cons_ineq, ba_cons_eq, bb_cons_eq);

%write a_mat
save(a_mat_path,'a_mat')

%write b_mat
save(b_mat_path,'b_mat')



end




