#!/usr/bin/env python
import sys
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from evaluation_on_location_prediction_one_user import evaluation_on_location_prediction_one_user as eolpou
from logs_file_writer import LogsFileWriter
from matrix_data_utils import *
from evaluation_on_feature_prediction_all_users import evaluation_on_feature_prediction_all_users as eofpal

eofpal("applaunch")