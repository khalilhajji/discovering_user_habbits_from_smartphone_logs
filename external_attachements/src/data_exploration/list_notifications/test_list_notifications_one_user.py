#!/usr/bin/env python
import sys
import pprint as pp
from list_notifications_one_user import list_notifications_one_user as lnou
import json

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from data_utils import DataExtractor

print(str(json.dumps(lnou(3), indent=4)))