#!/usr/bin/env python
import sys
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from transformations_comparaison_one_user import transformations_comparaison_one_user as tcou
from plot_lib_utils import PlotlibDrawer


from matrix_data_utils import *
'''
make the categorized data transformation for all the users
'''
for user_id in MDataExtractor.users_ids_list():
	print("user "+str(user_id)+" on working")
	tcou(user_id)
	
	print("user "+str(user_id)+" extracted")

PlotlibDrawer.show()