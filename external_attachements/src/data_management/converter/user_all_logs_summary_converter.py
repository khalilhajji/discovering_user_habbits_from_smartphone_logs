from all_logs_converter import AllLogsConverter
import logging
import glob
import json
import sys,os
import re
import datetime
import time

class UserAllLogsSummaryConverter(AllLogsConverter):
    """
    Convert a converted file by UserAllLogsConverter, or all_in_one_json_log to time line js format (for web ui-based easy summary).
    """

    # base direcotry and pathes
    all_in_one_json_log_path = "/data/mixs_logs/%s/usrs/*/%s/%s" % (AllLogsConverter.json_log_dir, AllLogsConverter.all_in_one_log_dir, AllLogsConverter.all_in_one_json_file)

    USERNAME_IDX = -3
    ALL_IN_ONE_BASE_DIR_IDX = 0
    
    def __init__(self, ):
        """
        init

        """
        super(AllLogsConverter, self).__init__()
        
        logger = logging.getLogger("UserAllLogsSummaryConverter")
        logger.setLevel(logging.INFO)
        logging.basicConfig()
        self.logger = logger
        logger.info("init starts")

        logger.info("init finished")
        pass

    def convert(self, ):
        """
        convert to tljs format.
        """
        self.logger.info("convert starts")
        st = time.time()
        all_in_one_log_paths = self._get_all_in_one_log_paths()
        for path in all_in_one_log_paths:
            self.logger.info("path: %s", path)
            tljs_obj = self._convert(path)
            fout_path = "%s/%s" % (path.split(self.all_in_one_json_file)[self.ALL_IN_ONE_BASE_DIR_IDX], self.all_in_one_gvc_tljs_file)

            
            
            self._save_as_gvc_tljs_format(tljs_obj, fout_path)
            pass
        et = time.time()
        self.logger.info("%f [s]" % (et - st))
        self.logger.info("convert finished")
        pass

    def _save_as_gvc_tljs_format(self, tljs_obj, fout_path):
        """
        save as tljs format
        
        Arguments:
        - `tljs_obj`:
        """
        fpout = open(fout_path, "w")
        fpout.write(json.dumps(tljs_obj, sort_keys = False))
        fpout.close()
        pass

    def _get_all_in_one_log_paths(self, all_in_one_json_log_path = all_in_one_json_log_path):
        """
        Arguments:
        - `all_in_one_json_log_path`: all-in-one json file for a user

        """
        all_in_one_log_paths = glob.glob(all_in_one_json_log_path)
        return all_in_one_log_paths
    
    def _convert(self, all_in_one_log_path):
        """
        convert path file
        
        Arguments:
        - `all_in_one_log_path`:
        """
        
        # read all in one json file
        fp = open(all_in_one_log_path, "r")
        all_in_one_json_log = json.load(fp)
        fp.close()
        
        # marshal to tljs format
        tljs_obj = json.loads("{}")
        self._init_tljs_obj(tljs_obj)
        self._add_base_info(tljs_obj, all_in_one_json_log)        

        time_seq = all_in_one_json_log[self.LOG_INFO].keys()
        time_seq.sort()
        for t in time_seq:
            self.logger.info("time: %d", int(t))
            self.logger.info("seq: %d", all_in_one_json_log[self.LOG_INFO][t][self.EVENT][self.SEQ])

            self._add_log_info(tljs_obj, all_in_one_json_log[self.LOG_INFO][t], t)
            self._add_stats(tljs_obj, all_in_one_json_log[self.LOG_INFO][t], t)
            
        return tljs_obj

    def _init_tljs_obj(self, tljs_obj):
        """
        
        Arguments:
        - `tljs_obj`:
        """
        tljs_obj[self.BASE_INFO] = json.loads("{}")
        tljs_obj[self.LOG_INFO] = json.loads("{}")
        pass

    def _add_stats(self, tljs_obj, log_info_t, t):
        """

        Arguments:
        - `tljs_obj`:
        - `log_info_t`: log info at t
        """
        tljs_obj[self.LOG_INFO][t][self.STATS] = json.loads("{}")
        tljs_obj[self.LOG_INFO][t][self.STATS][self.WIFI_APS] = len(log_info_t[self.WIFI_APS]) if self.WIFI_APS in log_info_t else 0
        tljs_obj[self.LOG_INFO][t][self.STATS][self.WIFI_CONNECTED_AP] = 1 if self.WIFI_CONNECTED_AP in log_info_t else 0
        tljs_obj[self.LOG_INFO][t][self.STATS][self.SENSOR] = len(log_info_t[self.SENSOR]) if self.SENSOR in log_info_t else 0
        tljs_obj[self.LOG_INFO][t][self.STATS][self.BLUETOOTH] = len(log_info_t[self.BLUETOOTH]) if self.BLUETOOTH in log_info_t else 0
        tljs_obj[self.LOG_INFO][t][self.STATS][self.BATTERY] = 1 if self.BATTERY in log_info_t else 0
        tljs_obj[self.LOG_INFO][t][self.STATS][self.HEADSET_PLUG] = 1 if self.HEADSET_PLUG in log_info_t else 0
        tljs_obj[self.LOG_INFO][t][self.STATS][self.NETWORK_INFO] = 1 if self.NETWORK_INFO in log_info_t else 0
        tljs_obj[self.LOG_INFO][t][self.STATS][self.TELEPHONY] = 1 if self.TELEPHONY in log_info_t else 0
        tljs_obj[self.LOG_INFO][t][self.STATS][self.NEIGHBORING_CELL_INFO] = len(log_info_t[self.NEIGHBORING_CELL_INFO]) if self.NEIGHBORING_CELL_INFO in log_info_t else 0

        pass

    def _add_log_info(self, tljs_obj, log_info_t, t):
        """
        
        Arguments:
        - `tljs_obj`:
        - `log_info_t`: log info at t
        """
        
        tljs_obj[self.LOG_INFO][t] = json.loads("{}")

        # applaunch and location
        tljs_obj[self.LOG_INFO][t][self.APP_LAUNCH] = log_info_t[self.APP_LAUNCH] if self.APP_LAUNCH in log_info_t else json.loads("{}")
        tljs_obj[self.LOG_INFO][t][self.LOCATION] = log_info_t[self.LOCATION] if self.LOCATION in log_info_t else json.loads("{}")
        
        # stats
        self._add_stats(tljs_obj, log_info_t, t)
        pass

    def _add_base_info(self, tljs_obj, all_in_one_json_log):
        """
        
        Arguments:
        - `tljs_obj`:
        - `all_in_one_json_log`:
        
        """
        tljs_obj[self.BASE_INFO] = json.loads("{}")
        uuid_idx = 0
        imei_idx = 0
        cnt = 0
        for e in all_in_one_json_log[self.BASE_INFO]:
            if e[self.KEY] == self.UUID:
                uuid_idx = cnt
                pass
            elif e[self.KEY] == self.IMEI:
                imei_idx = cnt
                pass
            cnt += 1
            pass
        
        tljs_obj[self.BASE_INFO][self.UUID] = all_in_one_json_log[self.BASE_INFO][uuid_idx]
        tljs_obj[self.BASE_INFO][self.IMEI] = all_in_one_json_log[self.BASE_INFO][imei_idx]
        
        pass

    def _get_user_name(self, all_in_one_json_log):
        """
        
        Arguments:
        - `all_in_one_log_path`:
        """

        for e in all_in_one_json_log[self.BASE_INFO]: 
            if e[self.KEY] == self.UUID:
                return e[self.VALUE]

def main():
    converter = UserAllLogsSummaryConverter()
    converter.convert()

if __name__ == '__main__':
    main()

