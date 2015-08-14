#!/usr/bin/env python
import json

from filter_notifications_one_user import filter_notifications_one_user as fnou
data = fnou(1)
#print str(json.dumps(data.keys(), indent=4))