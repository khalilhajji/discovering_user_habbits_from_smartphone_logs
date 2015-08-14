from features_by_day_one_user import features_by_day_one_user as fbdou
import sys
from pprint import *
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from data_utils import DataExtractor
from plot_lib_utils import PlotlibDrawer

pprint(fbdou(DataExtractor.test_user_id))
PlotlibDrawer.show()