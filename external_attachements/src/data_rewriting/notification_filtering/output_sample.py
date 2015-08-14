from pprint import *
import sys
sys.path.insert(0, "/home/dehajjik/workspace/src/utils")
from data_utils import *
from json_utils import JsonUtils

def output_sample(user_id):
	specific_date_times = {1: [datetime.datetime(year=2014, month=8, day=19, hour=16), datetime.datetime(year=2014, month=8, day=27, hour=15), datetime.datetime(year=2014, month=9, day=5, hour=18), datetime.datetime(year=2014, month=10, day=12, hour=15), datetime.datetime(year=2014, month=9, day=1, hour=1)],
						2: [datetime.datetime(year=2014, month=9, day=25, hour=7),datetime.datetime(year=2014, month=12, day=8, hour=6), datetime.datetime(year=2014, month=9, day=25, hour=1)],
						3: [ datetime.datetime(year=2014, month=9, day=25, hour=17)],
						4: [datetime.datetime(year=2014, month=9, day=5, hour=14), datetime.datetime(year=2015, month=1, day=8, hour=11), datetime.datetime(year=2014, month=9, day=2, hour=13)],
						5: [datetime.datetime(year=2014, month=9, day=22, hour=18), datetime.datetime(year=2015, month=1, day=5, hour=13), datetime.datetime(year=2014, month=12, day=29, hour=13)],
						6: [datetime.datetime(year=2014, month=10, day=26, hour=3), datetime.datetime(year=2014, month=11, day=4, hour=8)],
						7: [datetime.datetime(year=2014, month=7, day=28, hour=10)]}
	
	out_path_prefix = "/home/dehajjik/workspace/resources/filtered_notifs/"
	
	data = DataExtractor.load_json_data(user_id)
	
	
	#for each specific date and hour write the data that occured at that specified to a file. Json format
	for specific_dt in specific_date_times[user_id]:
		selected_data = DataExtractor.select_records_by_date_and_hour(data, specific_dt)
		selected_data = DataOperations.order_chronologically_and_annotate(selected_data)
		#selected_data = DataOperations.annotate(selected_data)
		JsonUtils.save_json_data(out_path_prefix+"u"+str(user_id)+" d"+specific_dt.strftime('%Y-%m-%d %H'), selected_data)
		print(str(json.dumps(selected_data.keys(), indent=4)))