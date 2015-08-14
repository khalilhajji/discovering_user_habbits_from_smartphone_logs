"""
this class is a utility class that represents a writer of the logs file. It contains methods like open, write and close.
it writes the files in ~/workspace/logs/. It adds also the current date of the log as a prefix in the log file name.
That is log files names will have the form daymonthyearhourminutesecondsuffix. The suffix is specified as a method input.

Moreover the log writer puts the date and the time in the beginning of the file.
"""
#!/usr/bin/env python
import sys
import os
import time
from json_utils import JsonUtils

class LogsFileWriter(object):
	log_dir = "/home/dehajjik/workspace/logs/"
	@staticmethod
	def open(file_suffix):
		t = time.strftime("%Y%m%d")
		t = t+""+time.strftime("%H%M%S")
		log_file_name = LogsFileWriter.log_dir+t+file_suffix
		f = open(log_file_name,'a')
		f.write("Date: "+ time.strftime("%d/%m/%Y")+" "+time.strftime("%H:%M:%S")+ "\n\n\n")
		return f
		
	@staticmethod	
	def write(content, f):
		f.write(content)
	
	@staticmethod	
	def close(f):
		f.close()
		
		

class JsonLogsFileWriter(object):
	log_dir = "/home/dehajjik/workspace/logs/"
	
	@staticmethod
	def write(content, file_suffix):
		t = time.strftime("%Y%m%d")
		t = t+""+time.strftime("%H%M%S")
		log_file_name = LogsFileWriter.log_dir+t+file_suffix
		JsonUtils.save_json_data(log_file_name, content)
		
	