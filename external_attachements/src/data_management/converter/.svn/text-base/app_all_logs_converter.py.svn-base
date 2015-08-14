#!/usr/bin/env python

from all_logs_converter import AllLogsConverter
import logging
import glob
import json
import sys,os
import re
import time
from collections import defaultdict

class AppAllLogsConverter(AllLogsConverter):
    """
    Convert all json file for each user to one coordinated file for each user.
    """

    def __init__(self, json_usrs_log_path = AllLogsConverter.json_usrs_log_path):
        """
        init

        - `filename`: filname created unser
        """
        super(AppAllLogsConverter, self).__init__()

        logger = logging.getLogger("AppAllLogsConverter")
        logger.setLevel(logging.INFO)
        logging.basicConfig()
        self.logger = logger

        pass
    
    def convert(self, ):
        """
        convert all of all-in-one log for each usrs to app log for each app
        Arguments:
        """

        self.logger.info("convert starts")
        st = time.time()
        
        all_usrs_all_in_one_log_path = glob.glob("%s/*/%s/%s" % (AllLogsConverter.json_usrs_log_path, AllLogsConverter.all_in_one_log_dir, AllLogsConverter.all_in_one_json_file))
        all_apps_info = json.loads("{}")
        #all_apps_info[self.APP_INFO]
        all_apps_info[self.LOG_INFO] = json.loads("{}")
        for path in all_usrs_all_in_one_log_path: ## for each user
            fpin = open(path, "r")
            all_in_one_log = json.load(fpin)
            
            base_info = all_in_one_log[self.BASE_INFO]
            log_info = all_in_one_log[self.LOG_INFO]
            
            for t in log_info.keys():
                # may dupulicate but possibility is very low
                try:
                    appname = log_info[t][self.APP_LAUNCH][self.APP_NAME]
                except Exception:
                    continue
                    pass
                
                if not appname in all_apps_info:
                    all_apps_info[appname] = json.loads("{}")
                    pass
                
                all_apps_info[appname][t] = log_info[t]
                all_apps_info[appname][t][self.BASE_INFO] = base_info
                pass
            pass
        
        # write
        self._save_all_apps_info(all_apps_info)

        et = time.time()
        self.logger.info("%f [s]" % (et - st))
        self.logger.info("convert finished")
        pass

    def _save_all_apps_info(self, all_apps_info):
        """
        
        Arguments:
        - `all_apps_info`:
        """
        
        for appname in all_apps_info:
            app_info = json.loads("{}")
            app_info[self.APP_NAME] = appname
            app_info[self.LOG_INFO] = all_apps_info[appname]
            all_in_one_log_dir_path = "%s/%s/%s" % (AllLogsConverter.json_apps_log_path, appname, AllLogsConverter.all_in_one_log_dir)
            all_in_one_log_path = "%s/%s" % (all_in_one_log_dir_path, AllLogsConverter.all_in_one_json_file)

            if not os.path.exists(all_in_one_log_dir_path):
                os.makedirs(all_in_one_log_dir_path)
                pass

            fpout = open(all_in_one_log_path, "w")
            fpout.write(json.dumps(app_info))
            fpout.close()
            
        pass

        
def main():
    converter = AppAllLogsConverter()
    converter.convert()
    
    pass

if __name__ == '__main__':
    main()

