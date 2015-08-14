#!/bin/sh
# $1:path_matlab_dir, $2:x_mat_path,  $3:x_mat_name, $4:a_cons_path, $5:b_cons_path, $6:eq_key, $7:ineq_key, $8:coefs_key, $9:biais_key, $10:k, $11:a_mat_path, §12:b_mat_path

args=( "$@" )
current_path=$PWD
cd $1

PATH=$PATH:/usr/local/sony/bin/:/soft/csw/matlab2/r2015a/bin/
export PATH

soft matlab2015a
matlab matlab -nodesktop -r "compute_lcbmf('$2','$3','$4','$5','$6','$7','$8','$9','${args[9]}','${args[10]}','${args[11]}'); exit; quit"

cd $current_path