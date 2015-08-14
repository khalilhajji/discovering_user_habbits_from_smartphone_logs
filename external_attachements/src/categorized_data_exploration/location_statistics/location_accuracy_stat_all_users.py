'''
for each user, outputs statistics that tests the consistency of the locations extracted:
	-show the distribution of frequencies of the clusters
	-show the distribution of the most frequent locations by hour of the day
'''

#!/usr/bin/env python
import sys
import pprint as pp
import os.path
import matplotlib.pyplot as plt

sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from location_time_coverage_one_user import location_time_coverage_one_user as tc_categorized

sys.path.insert(0, "/home/dehajjik/workspace/src/clean_data_exploration")
from location_time_coverage_one_user_clean import location_time_coverage_one_user_clean as tc_clean


from plot_lib_utils import *
from numpy_utils import *

from categorized_data_utils import DataExtractor
from plot_lib_utils import *


coverage_cat = np.zeros(len(DataExtractor.users_ids_list()))
coverage_clean = np.zeros(len(DataExtractor.users_ids_list()))



i = 0
for user_id in DataExtractor.users_ids_list():
	coverage_cat[i] = tc_categorized(user_id)
	coverage_clean[i] = tc_clean(user_id)
	
	i+=1

	print("user "+str(user_id)+" extracted")

print coverage_cat
print coverage_clean
fig, ax = plt.subplots()

index = np.arange(len(DataExtractor.users_ids_list()))
bar_width = 0.35

rects1 = plt.bar(index, coverage_cat, bar_width,
                 color='b',
                 label='transformed')

rects2 = plt.bar(index + bar_width, coverage_clean, bar_width,
                 color='r',
                 label='old')

labels = []
for i in index:
	labels.append("User "+str(i+1))

plt.xlabel('Users')
plt.ylabel('Minutes')
plt.title('Time coverage of the location information')
plt.xticks(index + bar_width, labels)
plt.legend()

plt.tight_layout()
plt.show()

	
PlotlibDrawer.show()