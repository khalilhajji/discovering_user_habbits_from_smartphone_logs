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
from almost_all_feature_extractor import AlmostAllFeatureExtractor
from almost_all_feature_extractor import DataInfo


class MRURankingAllFeatureExtractor(AlmostAllFeatureExtractor):
    """
    """
    # output of i/o
    dst_dir = "/data/mixs_logs/csv/usrslog/mru_ranking_all_features"
    
    def __init__(self, src_paths = BasicFeatureExtractor.src_paths, dst_dir = dst_dir):
        """
        """
        super(MRURankingAllFeatureExtractor, self).__init__(src_paths, dst_dir)
        
        logger = logging.getLogger("MRURankingAllFeatureExtractor")
        logger.setLevel(logging.DEBUG)
        logging.basicConfig()
        self.logger = logger

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
        data_info = MRURankingDataInfo(log_info)
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

class MRURankingDataInfo(DataInfo):
    def __init__(self, log_info):
        """
        """
        super(MRURankingDataInfo, self).__init__(log_info)
        
        logger = logging.getLogger("MRURankingDataInfo")
        logger.setLevel(logging.DEBUG)
        logging.basicConfig()
        self.logger = logger

def main():
    extractor = MRURankingAllFeatureExtractor()
    extractor.extract()

    # e.g., 
    # INFO:BasicInfoPhoneStateFeatureExtractor:2453.897135 [s]
    # with /data/mixs_logs_20140722.tgz
    
    pass

if __name__ == '__main__':
    main()
    
