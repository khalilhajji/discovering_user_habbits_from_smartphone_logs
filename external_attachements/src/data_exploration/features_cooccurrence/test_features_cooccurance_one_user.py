from features_cooccurance_one_user import UserFeaturesCooccurences as UFC
from pprint import *
import sys
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from numpy_utils import Numpy as n


ufc = UFC('/speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_launcher_logs/json/352136065015162/all/all_in_one_log.json')
print("features")
print(ufc.features)
print("\n\nco occurences rates")
print(n.str(ufc.cooccurences_rates))
print("\n\nco occurences numbers")
print(n.str(ufc.cooccurences_number))
print("\n\noccurences rates")
print(n.str(ufc.occurences_number))