from all_logs_converter import AllLogsConverter
import logging
import glob
import json
import sys,os
import re
import datetime
import time

# Deprecated
class UserAllLogs2TLJSConverter(AllLogsConverter):
    """
    Deprecated. Since timeline.js is used for personal history purpose.
    Convert a converted file by UserAllLogsConverter to time line js format.
    """

    # base direcotry and pathes
    all_in_one_tljs_file = "all_in_one_tljs_log.json"
    all_in_one_json_log_path = "/data/mixs_logs/%s/*/%s/%s" % (AllLogsConverter.json_log_dir, AllLogsConverter.all_in_one_log_dir, AllLogsConverter.all_in_one_json_file)

    USERNAME_IDX = -3
    ALL_IN_ONE_BASE_DIR_IDX = 0
    
    def __init__(self, ):
        """
        init

        """
        super(AllLogsConverter, self).__init__()

        logger = logging.getLogger("UserAllLogs2TLJSConverter")
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
            fout_path = "%s/%s" % (path.split(self.all_in_one_json_file)[self.ALL_IN_ONE_BASE_DIR_IDX], self.all_in_one_tljs_file)
            self._save_as_tljs_format(tljs_obj, fout_path)
            pass
        et = time.time()
        self.logger.info("%f [s]" % (et - st))
        self.logger.info("convert finished")
        pass

    def _save_as_tljs_format(self, tljs_obj, fout_path):
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
        username = self._get_user_name(all_in_one_json_log)
        self._add_header(tljs_obj, username)
        self._add_all_components(tljs_obj, all_in_one_json_log)
        
        return tljs_obj

    def _get_user_name(self, all_in_one_json_log):
        """
        
        Arguments:
        - `all_in_one_log_path`:
        """

        for e in all_in_one_json_log[self.BASE_INFO]: 
            if e[self.KEY] == self.UUID:
                return e[self.VALUE]

    def _init_tljs_obj(self, tljs_obj):
        """
        init emmpty js object
        Arguments:
        - `tljs_obj`: empty json object
        """
        
        tljs_obj["timeline"] = json.loads("{}")
        tljs_obj["timeline"]["date"] = json.loads("[]")
        tljs_obj["timeline"]["era"] = json.loads("{}")
        pass

    def _add_all_components(self, tljs_obj, all_in_one_json_log):
        """
        
        Arguments:
        - `tljs_obj`: time line js object
        - `all_in_one_json_log`: all in one json format
        """
        
        time_seq = all_in_one_json_log[self.LOG_INFO].keys()
        time_seq.sort()
        for t in time_seq:
            self.logger.info("time: %d", int(t))
            self.logger.info("seq: %d", all_in_one_json_log[self.LOG_INFO][t][self.EVENT][self.SEQ])
            self._add_tljs_date_obj(tljs_obj, all_in_one_json_log[self.LOG_INFO][t])
            pass
        pass

    def _add_header(self, tljs_obj, usernmae):
        """
        
        Arguments:
        - `tljs_obj`:
        """
        
        tljs_obj["timeline"]["headline"] = "Log History" 
        tljs_obj["timeline"]["type"] = "default"
        tljs_obj["timeline"]["text"] = "user id = %s" % (usernmae)
        tljs_obj["timeline"]["asset"] =  json.loads("{}")
        tljs_obj["timeline"]["asset"]["media"] = ""
        tljs_obj["timeline"]["asset"]["creadit"] = ""
        tljs_obj["timeline"]["asset"]["caption"] = ""

        pass

    def _add_tljs_date_obj(self, tljs_obj, js_obj):
        """
        convert tljs_obj with a specific format to tljs date format
        
        """

        _tljs_date_obj = json.loads("{}")
        date_time = datetime.datetime.fromtimestamp(js_obj[self.EVENT][self.TIME]/1000).strftime("%Y,%m,%d,%H,%M,%S")
        _tljs_date_obj["startDate"] = date_time
        _tljs_date_obj["endDate"] = ""
        
        _tljs_date_obj["headline"] = js_obj[self.APP_LAUNCH][self.APP_NAME] if self.APP_LAUNCH in js_obj else "non"
        _tljs_date_obj["text"] = js_obj[self.EVENT][self.TIMEZONE]
        _tljs_date_obj["tag"] = ""
        _tljs_date_obj["classname"] = ""
        _tljs_date_obj["asset"] = json.loads("{}")
        _tljs_date_obj["asset"]["media"] = ""
        _tljs_date_obj["asset"]["thumbnail"] = ""
        _tljs_date_obj["asset"]["credit"] = ""
        _tljs_date_obj["asset"]["caption"] = ""
        tljs_obj["timeline"]["date"].append(_tljs_date_obj)
        pass


def main():
    converter = UserAllLogs2TLJSConverter()
    converter.convert()

if __name__ == '__main__':
    main()

