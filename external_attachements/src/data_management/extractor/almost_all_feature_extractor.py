#!/usr/bin/env python

import json
import numpy as np
import time
import logging
import glob
import shutil
import os
from last_launched_app_feature_extractor import LastLaunchedAppFeatureExtractor
from basic_feature_extractor import BasicFeatureExtractor

class AlmostAllFeatureExtractor(LastLaunchedAppFeatureExtractor):
    """
    Almost All Feature Extractor Feature Extractor extracts labeled feature from the validated json log with the following format.
    ---
    y_1,x_01,x_02,...,x_0d
    y_2,x_11,x_12,...,x_1d
    ...
    y_n,x_n1,x_n2,...,x_nd
    ---

    features are ordered in 
    1. applaunch features
    - MFU ranking with dimension of K which is the number of application
    2. time-related features
    - daily periodicity
    - weekly periodicity
    3. sensor feature
    - e.g., light, gyro, and allcelrometer
    4. continuous feature (except sensor feature)
    - e.g., 
    5. categoricla features (those feature attributes are expressed as 1-of-K vector)
    - e.g., wifi-ap bssid.

    Note: Actual extractor is data info class.

    """
    # output of i/o
    #dst_dir = "/data/mixs_logs/csv/usrslog/almost_all_features"
    #dst_dir = "/speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_launcher_logs/svm_almost_all_features"
    dst_dir = "/speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_logs/svm_almost_all_features"

    def __init__(self, src_paths = BasicFeatureExtractor.src_paths, dst_dir = dst_dir):
        """
        Arguments:
        - `src_paths`: source paths in which logs of a user are assembled to one file.
        - `dst_dir`: distination directory
        """
        super(AlmostAllFeatureExtractor, self).__init__(src_paths, dst_dir)
        
        logger = logging.getLogger("AlmostAllFeatureExtractor")
        logger.setLevel(logging.DEBUG)
        logging.basicConfig()
        self.logger = logger

        pass

    def extract(self, ):
        """
        extract feature from json data for all users
        """
        self.logger.info("extract starts")
        st = time.time()

        self._delete_old_data()
        user_log_paths = glob.glob(self.src_paths)
        self.logger.info(len(user_log_paths))
        for user_log_path in user_log_paths: # for each user
            self._extract_usr_log(user_log_path)
            pass
    
        et = time.time()

        self.logger.info("%f [s]" % (et - st))
        self.logger.info("extract finished")
        pass

    def _extract_usr_log(self, src_path):
        """
        extract feature from json data for a user log

        Arguments:
        - `src_path`: source path
        """
        
        # read
        fpin = open(src_path)
        json_logs = json.load(fpin)
        fpin.close()
        
        # loginfo
        log_info = json_logs["logInfo"]
        time_seq = log_info.keys()
        time_seq.sort()
        
        # uid
        uid = self._extract_uid(json_logs)

        # extract data
        self.logger.info("extracting %s" % uid)
        
        # create data (label,features_attributes)
        data_info = DataInfo(log_info)
        data_info.make_template()
        
        data = ""
        data += data_info.header
        data += "\n"
        
        for i in xrange(len(time_seq)):
            labeled_sample = data_info.create_labeled_sample(i)
            data += labeled_sample
            data += "\n"
            pass
        
        self._save(data, uid)
        pass
    pass

class DataInfo(object):
    """
    Data Information
    This class is used for each user to create (label,sample) data
    
    """

    one_day_second = 24 * 60 * 60
    seven_days_second = one_day_second * 7
    two_pi_by_one_day_second = 2 * np.pi / one_day_second
    two_pi_by_seven_days_second = 2 * np.pi / seven_days_second
    
    def __init__(self, log_info):
        """
        """
        logger = logging.getLogger("DataInfo")
        logger.setLevel(logging.DEBUG)
        logging.basicConfig()
        self.logger = logger

        self.log_info = log_info
        self.time_seq = log_info.keys()
        self.time_seq.sort()

        # num_feature
        self.num_feature = 0

        #######################
        # feature information #
        #######################

        # feature for applaunch in the past
        # used for MRU ranking feature 
        self.mru_ranking_at_n = 15

        self.applaunch_feature_info = {
            "appLaunch": {
                "appName": {
                    "attribute_vals": set(),  # set of attribute_val
                    "attribute_val_idx": {},  # {attribute: index} map
                    },
                },
            }
        
        # time feature 
        self.time_feature_info = {
            "periodicity":{
                "daily": 1,
                "weekly": 1,
                #"monthly": 1, not used since which 30 or 31 should be used?
                },
            "duration": {
                "previsous_launch": 1
                }
            }

        # continuous (including ranking) feature
        self.continuous_feature_info = {
            "location": {
                "latitude": 1,
                "longitude": 1,
                "altitude": 1,
                },

            #"wifiAp": { not used
            #    "level": 1,
            #    "frequency": 1,
            #    },

            "wifiConnectedAp": {
                "linkSpeed": 1,
                },
            
            "battery": {
                "level": 1,
                "health": 1,
                "present": 1,
                "voltage": 1,
                "temperature": 1,
                },

            "headsetPlug": {
                "state": 1,
                "microphone": 1,
                },

            "networkInfo": {
                "connected": 1,
                "available": 1,
                "roaming": 1,
                },

            "telephony": {
                "networkRoming": 1,
                "cdmaCellLocBaseStationId": 1,
                "cdmaCellLocBaseStationLat": 1,
                "cdmaCellLocBaseStationLng": 1,
                },
            }
        
        # categorical feature info
        self.categorical_feature_info = {
            "wifiAps": {                # repeated in protoc-buf
                "bssId": {
                    "attribute_vals": set(),  
                    "attribute_val_idx": {},  
                    },
                },
            "wifiConnectedAp": {
                "bssId": {
                    "attribute_vals": set(), 
                    "attribute_val_idx": {},
                    },
                "networkId": {
                    "attribute_vals": set(), 
                    "attribute_val_idx": {},
                    },
                },
            "bluetooth": {              # repeated in protoc-buf
                "address": {
                    "attribute_vals": set(), 
                    "attribute_val_idx": {}
                    },
                "bondState": {
                    "attribute_vals": set(), 
                    "attribute_val_idx": {}
                    },
                "type": {
                    "attribute_vals": set(), 
                    "attribute_val_idx": {}
                    },
                },
            "battery": {
                "status": {
                    "attribute_vals": set(), 
                    "attribute_val_idx": {},
                    },
                "plugged": {
                    "attribute_vals": set(), 
                    "attribute_val_idx": {}
                    },
                "technology": {
                    "attribute_vals": set(), 
                    "attribute_val_idx": {},
                    },
                },
            "headsetPlug": {
                "name": {
                    "attribute_vals": set(), 
                    "attribute_val_idx": {},
                    },
                },
            "networkInfo": {
                "type": {
                    "attribute_vals": set(), 
                    "attribute_val_idx": {},
                    },
                "subType": {
                    "attribute_vals": set(), 
                    "attribute_val_idx": {},
                    },
                "state": {
                    "attribute_vals": set(), 
                    "attribute_val_idx": {},
                    },
                "detailState": {
                    "attribute_vals": set(), 
                    "attribute_val_idx": {},
                    },
                "reason": {
                    "attribute_vals": set(), 
                    "attribute_val_idx": {},
                    },
                #"extraInfo": {               # comment, since non-ascii char appears
                #    "attribute_vals": set(), 
                #    "attribute_val_idx": {},
                #    },
                },
            "telephony": {
                "phoneType": {
                    "attribute_vals": set(), 
                    "attribute_val_idx": {},
                    },
                "subscriberId": {
                    "attribute_vals": set(), 
                    "attribute_val_idx": {},
                    },
                "networkType": {
                    "attribute_vals": set(), 
                    "attribute_val_idx": {},
                    },
                "networkOperator": {
                    "attribute_vals": set(), 
                    "attribute_val_idx": {},
                    },
                "networkCountryIso": {
                    "attribute_vals": set(), 
                    "attribute_val_idx": {},
                    },
                "gsmCellLocCid": {
                    "attribute_vals": set(), 
                    "attribute_val_idx": {},
                    },
                "gsmCellLocLac": {
                    "attribute_vals": set(), 
                    "attribute_val_idx": {},
                    },
                "gsmCellLocPrc": {
                    "attribute_vals": set(), 
                    "attribute_val_idx": {},
                    },
                "cdmaCellLocNetworkId": {
                    "attribute_vals": set(), 
                    "attribute_val_idx": {},
                    },
                "cdmaCellLocSystemId": {
                    "attribute_vals": set(), 
                    "attribute_val_idx": {},
                    },
                },
            "neighboringCellInfo": {     # repeated in protoc-buf
                "networkType": {
                    "attribute_vals": set(), 
                    "attribute_val_idx": {},
                    },
                "cid": {
                    "attribute_vals": set(), 
                    "attribute_val_idx": {},
                    },
                "lac": {
                    "attribute_vals": set(), 
                    "attribute_val_idx": {},
                    },
                },
            }
        
        # sensor feature
        ## in some sensors, value[0] is only used and the other value[:] are coerced into being padded with 0.
        ## type: value length
        self.sensor_feature_info = {
            "TYPE_ACCELEROMETER": 3,
            "TYPE_MAGNETIC_FIELD": 3,
            "TYPE_GYROSCOPE": 3,
            "TYPE_LIGHT": 1,
            "TYPE_PRESSURE": 1,
            "TYPE_PROXIMITY": 1,
            "TYPE_GRAVITY": 3,
            "TYPE_LINEAR_ACCELERATION": 3,
            # In after API level 18, 5 is correct,
            # see http://developer.android.com/reference/android/hardware/SensorEvent.html#values
            "TYPE_ROTATION_VECTOR": 3, 
            "TYPE_RELATIVE_HUMIDITY": 1,
            "TYPE_AMBIENT_TEMPERATURE": 1,
            }

        #a = {
        #    "TYPE_ACCELEROMETER": {
        #        "x": ,
        #        "y": ,
        #        "z": ,
        #        },
        #    "TYPE_MAGNETIC_FIELD": {
        #        "x": ,
        #        "y": ,
        #        "z": ,
        #        },
        # 
        #    "TYPE_GYROSCOPE": {
        #        "x": ,
        #        "y": ,
        #        "z": ,
        #        },
        # 
        #    "TYPE_LIGHT": {
        #        "x": ,
        #        "y": ,
        #        "z": ,
        #        },
        # 
        #    "TYPE_PRESSURE": {
        #        "x": ,
        #        "y": ,
        #        "z": ,
        #        },
        # 
        #    "TYPE_PROXIMITY": {
        #        "x": ,
        #        "y": ,
        #        "z": ,
        #        },
        # 
        #    "TYPE_GRAVITY": {
        #        "x": ,
        #        "y": ,
        #        "z": ,
        #        },
        # 
        #    "TYPE_LINEAR_ACCELERATION": {
        #        "x": ,
        #        "y": ,
        #        "z": ,
        #        },
        # 
        #    "TYPE_ROTATION_VECTOR": {
        #        "x": ,
        #        "y": ,
        #        "z": ,
        #        },
        # 
        #    "TYPE_RELATIVE_HUMIDITY": {
        #        "x": ,
        #        "y": ,
        #        "z": ,
        #        },
        # 
        #    "TYPE_AMBIENT_TEMPERATURE": {
        #        "x": ,
        #        "y": ,
        #        "z": ,
        #        },
        #    }
        
        self.continuous_features = self.continuous_feature_info.keys()
        self.categorical_features = self.categorical_feature_info.keys()

        # header
        self.header = ""

        # {(feature, attribute, val), index}
        ## val is categorical val if attribute is category attribute
        ## val is -1 if attribute is continuous/ranking
        self.feature_attribute_index = {}

        pass
    
    def make_template(self, ):
        """
        make feature template to create labled sample
        """
    
        # create_applaunch_feature
        self._create_applaunch_feature()
        self._create_applaunch_feature_index()

        # list up category of categorical feautre
        self._list_up_categorical_feature_attribute()

        # categorical feature indexing (local indexing)
        #self._create_categorical_feature_attribute_index()

        # (feature, attr, val) indexing (global indexing)
        self._create_feature_attribute_index()

        pass

    def _create_applaunch_feature(self, ):
        """
        """
        
        for t in self.time_seq:
            if "appLaunch" in self.log_info[t]:
                appname = self.log_info[t]["appLaunch"]["appName"]
                self.applaunch_feature_info["appLaunch"]["appName"]["attribute_vals"].add(appname)
                #self.applaunch_feature_info["appLaunch"]["appName"]["attribute_val_idx"][appname] = idx
                pass
            pass
        pass

    def _create_applaunch_feature_index(self, ):
        idx = 0
        for appname in self.applaunch_feature_info["appLaunch"]["appName"]["attribute_vals"]:
            self.applaunch_feature_info["appLaunch"]["appName"]["attribute_val_idx"][appname] = idx
            idx += 1
            pass
        pass

    def _list_up_categorical_feature_attribute(self, ):
        """
        list up categorical feature attribute
        """
        for t in self.time_seq:
            features = self.log_info[t].keys()
            for feature in features: # feature is like battery
                if feature in self.categorical_features:
                    feature_type = type(self.log_info[t][feature])
                    if feature_type == list: # for feature list e.g., bluetooth
                        attribute_val_list = self.log_info[t][feature]
                        attributes = self.categorical_feature_info[feature].keys()
                        for attribute_val in attribute_val_list:
                            for attribute in attributes:
                                self.categorical_feature_info[feature][attribute]["attribute_vals"].add(str(attribute_val[attribute]))
                                pass
                            pass
                        pass
                    elif feature_type == dict: # for feature e.g., networkInfo, and etc.
                        attribute_val = self.log_info[t][feature]
                        attributes = self.categorical_feature_info[feature].keys()
                        for attribute in attributes:
                            self.categorical_feature_info[feature][attribute]["attribute_vals"].add(str(attribute_val[attribute]))
                            pass
                        pass
                    pass
                pass
            pass
        pass
    
    def _create_categorical_feature_attribute_index(self, ):
        """
        create feature index for categorial features
        """
        categorical_feature_info = self.categorical_feature_info
        features = self.categorical_features
        for feature in features:
            categorical_feature = categorical_feature_info[feature]
            attributes = categorical_feature.keys()
            for attribute in attributes:
                categorical_feature_attribute = categorical_feature[attribute]
                
                # indexing
                idx = 0
                attribute_val_idx = categorical_feature_attribute["attribute_val_idx"]
                attribute_vals = categorical_feature_attribute["attribute_vals"]
                for attribute_val in attribute_vals:
                    attribute_val_idx[attribute_val] = idx
                    idx += 1
                    pass
                pass
            pass
        pass

    def _create_feature_attribute_index(self, ):
        """
        create index for feature, attribute, and val pair
        """

        global_index = 0        # global index
        header = ""             # header

        # app launch feature
        appname_attribute_val_idx = [(val, idx) for (val, idx) in sorted(self.applaunch_feature_info["appLaunch"]["appName"]["attribute_val_idx"].items(), key=lambda x:x[1])]
        for (val, idx) in appname_attribute_val_idx:
            self.feature_attribute_index[("appLaunch", "appName", val)] = global_index
            header += "app_%s" % (idx)
            header += ","
            global_index += 1
            pass
        
        # time feature
        ## periodicity
        attributes = self.time_feature_info["periodicity"].keys()
        for attribute in attributes:
            # cos
            self.feature_attribute_index[("periodicity", "%s_x" % (attribute), -1)] = global_index
            header += "%s_%s_x" % ("periodicity", attribute)
            header += ","
            global_index += 1
            
            # sin
            self.feature_attribute_index[("periodicity", "%s_y" % (attribute), -1)] = global_index
            header += "%s_%s_y" % ("periodicity", attribute)
            header += ","
            global_index += 1
            pass
        
        ## duration
        self.feature_attribute_index[("duration", "previsous_launch", -1)] = global_index
        header += "%s_%s" % ("duration", "previsous_launch")
        header += ","
        global_index += 1

        # sensor feature
        for feature in self.sensor_feature_info.keys():
            for attribute in xrange(0, self.sensor_feature_info[feature]):
                self.feature_attribute_index[(feature, attribute, -1)] = global_index
                header += "%s_%s" % (feature, attribute)
                header += ","
                global_index += 1
                pass
            pass
                
        # continuous feature
        for feature in self.continuous_feature_info.keys():
            attributes = self.continuous_feature_info[feature].keys()
            for attribute in attributes:
                self.feature_attribute_index[(feature, attribute, -1)] = global_index
                header += "%s_%s" % (feature, attribute)
                header += ","
                global_index += 1
                pass
            pass
        
        # categorical feature
        for feature in self.categorical_feature_info.keys():
            attributes = self.categorical_feature_info[feature].keys()
            for attribute in attributes:
                attribute_vals = sorted(self.categorical_feature_info[feature][attribute]["attribute_vals"])
                for val in attribute_vals:
                    self.feature_attribute_index[(feature, attribute, val)] = global_index
                    header += "%s_%s_%s" % (feature, attribute, val)
                    header += ","
                    global_index += 1
                    pass
                pass
            pass

        self.num_feature = global_index
        self.header = "%s,%s" % ("label", header.rstrip(","))
        pass

    def create_labeled_sample(self, i):
        """
        create feature from one applaunch event at event i.
        
        Note: NaN data is paddied with 0.        
        """
        
        label = self.log_info[self.time_seq[i]]["appLaunch"]["appName"]
        sample = np.zeros(self.num_feature)   # NaN is padded with 0
        log = self.log_info[self.time_seq[i]] # one log

        # app launch feature as MRU ranking
        for t in xrange(1, self.mru_ranking_at_n + 1):
            if (i-t) > -1:
                if "appLaunch" in self.log_info[self.time_seq[i-t]]:
                    val = self.log_info[self.time_seq[i-t]]["appLaunch"]["appName"]
                    key = ("appLaunch", "appName", val)
                    idx = self.feature_attribute_index[key]
                    sample[idx] = t
                    pass
                pass
            pass
        
        # time feature
        ## periodicity
        ### daily
        timestamp = self.time_seq[i]
        theta = self.two_pi_by_one_day_second * (int(timestamp[0:-3]) % self.one_day_second)
        idx = self.feature_attribute_index[("periodicity", "daily_x", -1)]
        sample[idx] = np.cos(theta)
        idx = self.feature_attribute_index[("periodicity", "daily_y", -1)]
        sample[idx] = np.sin(theta)

        ### weekly
        theta = self.two_pi_by_seven_days_second * (int(timestamp[0:-3]) % self.seven_days_second)
        idx = self.feature_attribute_index[("periodicity", "weekly_x", -1)]
        sample[idx] = np.cos(theta)
        idx = self.feature_attribute_index[("periodicity", "weekly_y", -1)]
        sample[idx] = np.sin(theta)

        ## duration
        if i > 0:
            duration = int(self.time_seq[i]) - int(self.time_seq[i - 1])
            key = ("duration", "previsous_launch", -1)
            idx = self.feature_attribute_index[key]
            sample[idx] = duration
            pass
        
        # continuous/categorical feature
        features = log.keys()
        for feature in features:
            # get content of log once
            feature_data = log[feature]

            # skip features which is not defined to be used
            condition = feature in self.categorical_feature_info or feature in self.continuous_feature_info or feature == "sensor"

            if not condition:
                continue

            # sensor case
            if feature == "sensor": # list
                for feature_data_elm in feature_data:
                    sensor_type = feature_data_elm["type"]
                    if sensor_type in self.sensor_feature_info:
                        values = feature_data_elm["value"]
                        length = self.sensor_feature_info[sensor_type]
                        for i in xrange(0, length):
                            if np.isnan(values[i]):
                                break
                            
                            feature = sensor_type
                            attribute = i
                            key = (feature, attribute, -1)
                            idx = self.feature_attribute_index[key]                            
                            sample[idx] = values[i]
                            pass
                    else:
                        continue
                    pass
                
                continue
            
            # list case
            if type(feature_data) == list:
                for feature_data_elm in feature_data:
                    for attribute in feature_data_elm.keys():
                        key = (feature, attribute, -1) # continuous case
            
                        if key in self.feature_attribute_index: 
                            idx = self.feature_attribute_index[key]
                            sample[idx] = feature_data_elm[attribute]
                            continue

                        key = (feature, attribute, feature_data_elm[attribute]) # categorical case
                        if key in self.feature_attribute_index: 
                            idx = self.feature_attribute_index[key]
                            sample[idx] = 1
                            continue
                        pass
                    pass
                pass

            # dict case
            elif type(feature_data) == dict:
                for attribute in feature_data.keys():
                    key = (feature, attribute, -1) # continuous case
                    
                    if key in self.feature_attribute_index: 
                        idx = self.feature_attribute_index[key]
                        sample[idx] = feature_data[attribute]
                        continue
                    
                    key = (feature, attribute, feature_data[attribute]) # categorical case
                    if key in self.feature_attribute_index: 
                        idx = self.feature_attribute_index[key]
                        sample[idx] = 1
                        continue
                    pass
                pass
            pass
        return "%s,%s" % (label, ",".join(map(str, sample)))
    
def main():
    
    extractor = AlmostAllFeatureExtractor()
    extractor.extract()

    # e.g., 
    # INFO:BasicInfoPhoneStateFeatureExtractor:2453.897135 [s]
    # with /data/mixs_logs_20140722.tgz
    
    pass

if __name__ == '__main__':
    main()
    
