#!/usr/bin/env python
import sys
import pprint as pp
import os.path
from datetime import *
import time
import json
import collections
from json_utils import JsonUtils
import copy

'''
DateTimeUtils is a utility class about date and time
'''
class DateTimeUtils:
	chrono_start_millis = None
	chrono_end_millis = None
	
	'''
	starts the chronometering
	'''
	@staticmethod
	def start_chrono():
		DateTimeUtils.chrono_end_millis = None
		DateTimeUtils.chrono_start_millis = time.time() * 1000
	

	'''
	ends the chronometering and returns the chronometered time in milliseconds
	'''
	@staticmethod
	def stop_chrono():
		DateTimeUtils.chrono_end_millis = time.time() * 1000
		timing = DateTimeUtils.chrono_end_millis - DateTimeUtils.chrono_start_millis
		
		DateTimeUtils.chrono_end_millis = None
		DateTimeUtils.chrono_start_millis = None
		return timing
		
	
	
	'''
	input: daytime object
	return true if it corresponds to a week end day, false otherwise
	'''
	@staticmethod
	def is_week_end_day(datetime):
		return datetime.weekday()== 5 or datetime.weekday()== 6
		
	
	'''
	input: two datetimes objects. First one corresponds to the start the second one to the end
	return list of datetimes containing all the hours between the two given datetimes(inclusive). 
	i.e 01.01.1970 00:30 and 01.01.1970 00:50 will return [01.01.1970 01:00]
	
	Note that the times of start and begin are rounded to the closest hour
	'''
	@staticmethod
	def hours_between(datetime1 , datetime2):
		if datetime1>datetime2:
			raise Exception("bad ordering Exception : the date "+str(datetime1)+" occurs after "+str(datetime2)+". The first date given as input is the start date.")
	
		rounded_dt1 = DateTimeUtils.round_to_the_closest_hour(datetime1)
		rounded_dt2 = DateTimeUtils.round_to_the_closest_hour(datetime2)
		
		datetimes = [rounded_dt1]
		inbetween_dt = rounded_dt1+timedelta(hours=1)
		
		while inbetween_dt <= rounded_dt2:
			datetimes.append(copy.deepcopy(inbetween_dt))
			inbetween_dt += timedelta(hours=1)
		
		return datetimes
		
	@staticmethod
	def quarterhours_between(datetime1 , datetime2):
		if datetime1>datetime2:
			raise Exception("bad ordering Exception : the date "+str(datetime1)+" occurs after "+str(datetime2)+". The first date given as input is the start date.")
	
		rounded_dt1 = DateTimeUtils.round_to_the_closest_quarterhour(datetime1)
		rounded_dt2 = DateTimeUtils.round_to_the_closest_quarterhour(datetime2)
		
		
		datetimes = [rounded_dt1]
		inbetween_dt = rounded_dt1+timedelta(minutes=15)
		
		while inbetween_dt <= rounded_dt2:
			datetimes.append(copy.deepcopy(inbetween_dt))
			inbetween_dt += timedelta(minutes=15)
		
		return datetimes
		
	
	'''
	input: a datetime object
	return a new datetime object that corresponds the the input rounded to the closest minute
	'''
	@staticmethod
	def round_to_the_closest_minute(one_datetime):
		datetim = copy.deepcopy(one_datetime)
		second = datetim.second
		millisecond = datetim.microsecond
		
		if second>30:
			datetim+=timedelta(minutes=1)
		
		datetim -= timedelta(seconds=second)
		datetim -= timedelta(microseconds=millisecond)
		
		return datetim
		
	
	'''
	input: a datetime object
	return a new datetime object that corresponds the the input rounded to the closest hour
	'''
	@staticmethod
	def round_to_the_closest_hour(one_datetime):
		datetime = DateTimeUtils.round_to_the_closest_minute(one_datetime)
		minute = datetime.minute
		
		if minute>30:
			datetime+= timedelta(hours=1)
		
		datetime -= timedelta(minutes=minute)
		
		return datetime
	
	@staticmethod	
	def round_to_the_closest_quarterhour(one_datetime):
		datetime = DateTimeUtils.round_to_the_closest_minute(one_datetime)
		minute = datetime.minute
		datetime -= timedelta(minutes=minute)
		
		if minute>=7 and minute <=22:
			datetime+= timedelta(minutes=15)
		elif minute >22 and minute <=37:
			datetime+= timedelta(minutes=30)
		elif minute > 37 and minute <= 52:
			datetime+= timedelta(minutes=45)
		elif minute > 52:
			datetime+= timedelta(hours=1)
		
		
		return datetime
		
	
	'''
	input: a datetime object
	return a new datetime object that corresponds the the input rounded to the closest quarterhour before
	'''
	@staticmethod
	def round_to_the_quarter_before(one_datetime):
		datetime = DateTimeUtils.round_to_the_closest_minute(one_datetime)
		minute = datetime.minute
		
		datetime -= timedelta(minutes=minute%15)
		
		return datetime
		
		
	'''
	input: a datetime object
	return a new datetime object that corresponds the the input rounded to the closest hour before
	'''
	@staticmethod
	def round_to_the_hour_before(one_datetime):
		datetime = DateTimeUtils.round_to_the_closest_minute(one_datetime)
		minute = datetime.minute
		
		datetime -= timedelta(minutes=minute)
		
		return datetime

		
	
	'''
	input: a datetime object
	return a new datetime object that corresponds the the input rounded to the closest hour after
	'''
	@staticmethod
	def round_to_the_hour_after(one_datetime):
		datetime = DateTimeUtils.round_to_the_closest_minute(one_datetime)
		minute = datetime.minute
		
		datetime+= timedelta(hours=1)
		datetime -= timedelta(minutes=minute)
		
		return datetime
		
	
		
		
		
		
	