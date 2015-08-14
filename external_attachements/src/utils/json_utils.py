#!/usr/bin/env python
import sys
import pprint as pp
import os.path
import datetime
import json
import collections

'''
Json utils contains some utils functions about Json
'''
class JsonUtils:

	'''
	returns the json data of the specified file
	'''
	@staticmethod
	def load_json_data(file):
		if not file.endswith(".json"):
			file = file+".json"
		json_data=open(file).read()
		data = json.loads(json_data)
		
		return data
	
	'''
	writes the json data to the specified file
	'''
	@staticmethod
	def save_json_data(file, json_data):
		with open(file+".json", 'w') as outfile:
			json.dump(json_data, outfile)
			
	
	'''
	outputs a good string format of a dictionary.
	This good string format is as the json string format.
	'''
	@staticmethod
	def dict_as_json_str(dict):
		return str(json.dumps(dict, indent=4))
		
	
	'''
	outputs a dictionary in a Json structure.
	'''
	@staticmethod
	def json_str_as_dict(json_str):
		return json.loads(json_str)
		