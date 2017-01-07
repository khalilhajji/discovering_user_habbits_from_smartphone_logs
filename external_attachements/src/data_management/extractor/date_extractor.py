#!/usr/bin/env python

import json
import numpy as np
import time
import logging
import glob
import shutil
import os
from feature_extractor import FeatureExtractor
from datetime import datetime
from time import strftime


class DateExtractor(FeatureExtractor):
    """
    This Basic feature extractor module has been re-written to extract only date/time information for investigation of log sequences.
    Extracts time (in a human readable format) from a validated json user log as csv format.
    """

    # uuid
    # 0 for guid generated by app
    # 1 for imei
    UID_INDEX = 1
    
    # time
    one_day_second = 24 * 60 * 60
    seven_days_second = one_day_second * 7
    two_pi_by_one_day_second = 2 * np.pi / one_day_second
    two_pi_by_seven_days_second = 2 * np.pi / seven_days_second

    # i/o 
    #src_paths = "/data/mixs_logs/json/usrs/*/all/all_in_one_validated_log.json"
    src_paths = "/speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_logs/json/usrs/*/all/all_in_one_validated_log.json"
    dst_dir = "/speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_logs/eutec_widget_date_extraction"

    #src_paths = "/speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_launcher_logs/json/*/all/all_in_one_validated_log.json"
    #dst_dir = "/speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_launcher_logs/eutec_launcher_date_extraction"

    def __init__(self, src_paths = src_paths, dst_dir = dst_dir):
        
        """
        Arguments:
        - `src_paths`: source paths in which logs of a user are assembled to one file.
        - `dst_dir`: distination directory
        """
        super(DateExtractor, self).__init__()

        self.src_paths = src_paths
        self.dst_dir = dst_dir
        
        logger = logging.getLogger("DateExtractor")
        logger.setLevel(logging.INFO)
        logging.basicConfig()
        self.logger = logger

        pass

    def extract(self, ):
        """
        extract json data
        """
        self.logger.info("extract starts")
        st = time.time()

        self._delete_old_data()
        user_log_paths = glob.glob(self.src_paths)
        for user_log_path in user_log_paths: # for each user
            self._extract_usr_log(user_log_path)
            pass
    
        et = time.time()

        self.logger.info("%f [s]" % (et - st))
        self.logger.info("extract finished")
        pass
        
    def _extract_usr_log(self, src_path):
        """
        Arguments:
        - `src_path`: source path
        """
        # read
        fpin = open(src_path)
        json_logs = json.load(fpin)
        fpin.close()

        # uid
        uid = self._extract_uid(json_logs)

        # extract data
        self.logger.info("extracting %s" % uid)
        
        # lognfo
        log_info = json_logs["logInfo"]
        time_seq = log_info.keys()
        time_seq.sort()
        
        data = ""
        
        # header
        data += self._create_header()
        
        # data
        for t in time_seq:
            if 'appLaunch' in log_info[t].keys():
                l = self._create_line(log_info, t)
                data += l
                data += "\n"
                pass
            pass
        
        data = data.strip()

        # save
        self._save(data, uid)
        
        pass

    def _create_line(self, log_info, t):
        """
        Generate time/date information only
        
        Arguments:
        - `src_path`: source path
        """

        l = ""
        appname = log_info[t]["appLaunch"]["appName"]
        l += appname + ","
        l += self._extract_date(t)
        l += ","
        l += t
        

        return l

    def _create_header(self, ):
        """
        """
        header = "label,time_str,time_unix\n"
        return header

    def _extract_uid(self, json_logs):
        """
        
        Arguments:
        - `json_logs`: json log for a user
        """
        
        return json_logs["baseInfo"][self.UID_INDEX]["value"]

        pass

    def _extract_appname(self, log):
        """
        extract appname.
        if appLaunch field does not exist, skip that log but such a log is few like 0.0...01 %.
        
        Arguments:
        - `log`: log at t
        """
        appname = ""
        if "appLaunch" in log:
            appname = log["appLaunch"]["appName"]
        else:
            self.logger.info("no applaunch field")
            self.logger.info(log["event"])
            pass        
        
        return appname

    def _extract_location_xyz(self, log):
        """
        extract location info.
        if location field does not exist, (x,y,x) = (0,0,0)

        Arguments:
        - `log`: log at t
        """

        if "location" in log:
            x = log["location"]["latitude"]
            y = log["location"]["longitude"]
            z = log["location"]["altitude"]
        else:
            self.logger.debug("NaN case")
            x = "NaN" # matlab Nan?
            y = "NaN"
            z = "NaN"
            pass
        return str(x) + "," + str(y) + "," + str(z)

    def _convert_timestamp_2_periodic_time(self, timestamp):
        """
        convert ${unix time}${millisecond} to periodic information on a weekly basis.
        return as string as format x,y

        Arguments:
        - `timestamp`: unix time added millisecond
        """
        
        l = ""

        # daily periodic
        theta = self.two_pi_by_one_day_second * (int(timestamp[0:-3]) % self.one_day_second)
        #x = 1 + np.cos(theta)
        #y = 1 + np.sin(theta)
        x = np.cos(theta)
        y = np.sin(theta)
        l += str(x) + "," + str(y)
        l += ","

        # weekly periodic
        theta = self.two_pi_by_seven_days_second * (int(timestamp[0:-3]) % self.seven_days_second)
        # no need plus one?
        #x = 1 + np.cos(theta)
        #y = 1 + np.sin(theta)
        x = np.cos(theta)
        y = np.sin(theta)
        l += str(x) + "," + str(y)

        return l
        
    def _extract_date(self, timestamp):
        """
        convert ${unix time}${millisecond} to periodic information on a weekly basis.
        return as string as format x,y

        Arguments:
        - `timestamp`: unix time added millisecond
        """
        
        l = ""

        #return date in human readable format
        value = datetime.fromtimestamp(int(timestamp[0:-3]))
        l += value.strftime('%F %H:%M:%S')

        return l
    
    def _save(self, data, uid):
        """
        
        Arguments:
        - `data`: saved dataset
        - `uid`: user id
        """
        fout = "%s/%s.dat" % (self.dst_dir, uid)
        fpout = open(fout, "w")
        fpout.write(data)
        fpout.close()
        pass

    def _delete_old_data(self, ):
        """
        """
        for fin in glob.glob("%s/*" % (self.dst_dir)):
            os.remove(fin)
            pass
        
def main():
    # i/o
    
    #widget logger
    src_paths = "/speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_logs/json/usrs/*/all/all_in_one_validated_log.json"

    dst_dir = "/speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_logs/eutec_widget_date_extraction"

    #launcher logger
    #src_paths = "/speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_launcher_logs/json/*/all/all_in_one_validated_log.json"
    #dst_dir = "/speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_launcher_logs/eutec_launcher_date_extraction"
    
    #src_paths = "/data/_logs/json/usrs/*/all/all_in_one_validated_log.json"
    #dst_dir = "/data/mixs_logs/csv/usrslog/basic"

    extractor = DateExtractor(src_paths = src_paths, dst_dir = dst_dir)
    extractor.extract()

if __name__ == '__main__':
    main()


    