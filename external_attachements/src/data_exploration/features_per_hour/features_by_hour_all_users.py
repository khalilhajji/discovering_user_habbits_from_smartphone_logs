#!/usr/bin/env python
import sys
import pprint as pp
import os.path
import datetime

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from data_utils import *
from plot_lib_utils import PlotlibDrawer
from features_by_hour_one_user import features_by_hour_one_user as fbhou

for user_id in DataExtractor.users_ids_list():
	fbhou(user_id)
	print("user "+str(user_id)+" extracted")
	
PlotlibDrawer.show()