'''
for each user, plots the number of records of some features he has by day.

As output, plots one plot by user
'''

#!/usr/bin/env python
import sys
import pprint as pp
import os.path

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from features_by_day_one_user import features_by_day_one_user as fbdou
from data_utils import DataExtractor
from plot_lib_utils import PlotlibDrawer


for user_id in DataExtractor.users_ids_list():
	dict = fbdou(user_id)
	print("user "+str(user_id)+" extracted")
	
PlotlibDrawer.show()