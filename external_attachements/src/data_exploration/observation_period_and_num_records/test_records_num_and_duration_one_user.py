from records_num_and_duration_one_user import records_num_and_duration_one_user as rnadou
import sys
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from data_utils import DataExtractor

print rnadou(DataExtractor.test_user_id)