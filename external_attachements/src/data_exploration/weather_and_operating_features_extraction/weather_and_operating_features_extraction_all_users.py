#!/usr/bin/env python
import sys


sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from data_utils import *
from weather_and_operating_features_extraction_one_user import weather_and_operating_features_extraction_one_user as waofeou



for user_id in DataExtractor.users_ids_list():
	waofeou(user_id)
	print("user "+str(user_id)+" extracted")