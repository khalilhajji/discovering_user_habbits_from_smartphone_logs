#!/usr/bin/env python

import json
import numpy as np
import time
import logging
import glob
import shutil
import os
import pickle

from collections import defaultdict
from last_launched_app_feature_extractor import LastLaunchedAppFeatureExtractor
from basic_feature_extractor import BasicFeatureExtractor
from almost_all_feature_extractor import AlmostAllFeatureExtractor
from almost_all_feature_extractor import DataInfo

class MFUMRUAllInfoFeatureExtractor(AlmostAllFeatureExtractor):
    """
    """
    # output of i/o
    dst_dir = "/data/mixs_logs/csv/usrslog/mfu_mru_all_info_features"

    def __init__(self, src_paths = BasicFeatureExtractor.src_paths, dst_dir = dst_dir):
        """
        """
        super(MFUMRUAllInfoFeatureExtractor, self).__init__(src_paths, dst_dir)
        
        logger = logging.getLogger("MFUMRUAllInfoFeatureExtractor")
        logger.setLevel(logging.DEBUG)
        logging.basicConfig()

        self.logger = logger

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
        
        # lognfo
        log_info = json_logs["logInfo"]
        time_seq = log_info.keys()
        time_seq.sort()
        
        # uid
        uid = self._extract_uid(json_logs)

        # extract data
        self.logger.info("extracting %s" % uid)
        
        # create data (label,features_attributes)
        data_info = LabeledMFUMRUAllInfoFeature(log_info)
        data_info.make_template()
        
        data = ""
        data += data_info.header.strip()
        data += "\n"
        
        for i in xrange(len(time_seq)):
            labeled_sample = data_info.create_labeled_sample(i)
            data += labeled_sample
            data += "\n"
            pass

        # dump appname-id map for a user
        appname_attribute_val_idx = [(val, idx) for (val, idx) in sorted(data_info.applaunch_feature_info["appLaunch"]["appName"]["attribute_val_idx"].items(), key=lambda x:x[1])]
        appname_index_map = {}
        for (val, idx) in appname_attribute_val_idx:
            appname_index_map[val] = idx
            pass
        dumppath = "%s_extra_info/%s" % (self.dst_dir, uid)
        if not os.path.exists(dumppath):
            os.makedirs(dumppath)
            pass
        with open("%s/appname_index.out" % dumppath, "w") as fpout:
            pickle.dump(appname_index_map, fpout)
            pass

        # save dataset
        self._save(data.strip(), uid)
        
        pass
    pass

class LabeledMFUMRUAllInfoFeature(DataInfo):

    def __init__(self, log_info):
        """
        """
        super(LabeledMFUMRUAllInfoFeature, self).__init__(log_info)
        
        logger = logging.getLogger("LabeledMFUMRUAllInfoFeature")
        logger.setLevel(logging.DEBUG)
        logging.basicConfig()
        self.logger = logger

        self.mfu = defaultdict(int)

        pass

    def _create_feature_attribute_index(self, ):
        """
        create index for feature, attribute, and val pair
        """

        global_index = 0        # global index
        header = ""             # header

        # app launch feature
        appname_attribute_val_idx = [(val, idx) for (val, idx) in sorted(self.applaunch_feature_info["appLaunch"]["appName"]["attribute_val_idx"].items(), key=lambda x:x[1])]
        ## mfu
        for (val, idx) in appname_attribute_val_idx:
            self.feature_attribute_index[("appLaunch", "mfu", "%s" % val)] = global_index
            header += "mfu_app_%s" % (idx)
            header += ","
            global_index += 1
            pass

        ## mru as boolean-valued feature
        for i in xrange(self.mru_ranking_at_n):
            for (val, idx) in appname_attribute_val_idx:
                self.feature_attribute_index[("appLaunch", "mru", "%s_%d" % (val, i))] = global_index
                # TODO: re-chnage index to val if it is more suitable than using ${appname}
                #header += "mru_app_%s_%d" % (idx, i + 1)
                header += "mru_app_%s_%d" % (val, i + 1)
                header += ","
                global_index += 1
                pass
            pass

        # dump app
        
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

        # app launch feature
        ## mfu
        if i > 0:
            self.mfu[self.log_info[self.time_seq[i-1]]["appLaunch"]["appName"]] += 1 # create mfu on run-time
            s = 0
            for (k, v) in self.mfu.items():
                s += v
                pass
            for (k, v) in self.mfu.items(): # make ratio
                key = ("appLaunch", "mfu", "%s" % (k))
                idx = self.feature_attribute_index[key]
                sample[idx] = 1.0 * v/s
                pass
            pass
            
        ## mru
        for t in xrange(0, self.mru_ranking_at_n):
            if (i-t-1) > -1:
                val = self.log_info[self.time_seq[i-t-1]]["appLaunch"]["appName"] # i-t-1, since t starts from 0
                key = ("appLaunch", "mru", "%s_%d" % (val, t))
                idx = self.feature_attribute_index[key]
                sample[idx] = 1
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

# test purpose
def main():
    
    src_paths = "/data/mixs_logs_20140827/json/usrs/*/all/all_in_one_validated_log.json"
    dst_dir = "/data/mixs_logs_20140827/csv/usrslog/mfu_mru_all_info_features"
    
    extractor = MFUMRUAllInfoFeatureExtractor(src_paths, dst_dir)
    #extractor = MFUMRUAllInfoFeatureExtractor()
    extractor.extract()

    # e.g., 
    # 2616.392142 [s]
    # with /data/tmp/mixs_logs_20140728
    
    pass

if __name__ == '__main__':
    main()
