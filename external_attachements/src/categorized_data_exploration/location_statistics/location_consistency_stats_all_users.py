'''
for each user, outputs statistics that tests the consistency of the locations extracted:
	-show the distribution of frequencies of the clusters
	-show the distribution of the most frequent locations by hour of the day
'''

#!/usr/bin/env python
import sys
import pprint as pp
import os.path

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from location_distribution_per_hour_one_user import location_distribution_per_hour_one_user as ldphou
from location_visits_distribution_one_user import location_visits_distribution_one_user as lvdou
from categorized_data_utils import DataExtractor
from plot_lib_utils import *


for user_id in DataExtractor.users_ids_list():
	for option in ["week_end", "week_days", "all"]:
		ldphou(user_id,option)
	lvdou(user_id)
	print("user "+str(user_id)+" extracted")
	
PlotlibDrawer.show()