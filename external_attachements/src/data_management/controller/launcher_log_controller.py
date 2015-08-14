import sys,os
import gzip
import re
import glob
import json
import shutil
import logging
import time
import controller
from collections import defaultdict
from controller import Controller
from mixs_log_importer import MixsLogImporter
from user_all_logs_converter import UserAllLogsConverter
from mixs_log_transporter import MixsLogTransporter

class LauncherLogController(Controller):
    """
    Launcher Log Controller controls sequence from downloadnig to parsing, for launchger log.
    """

    raw_log_path = "/data/mixs_launcher_logs/raw"
    json_usrs_log_path = "/data/mixs_launcher_logs/json"
    local_data_path = "/data/mixs_launcher_logs"

    file_filters = ["VALauncherLogger"]
    
    def __init__(self, ):
        """
        init
        """
        super(LauncherLogController, self).__init__()
        
        logger = logging.getLogger("LauncherLogController")
        logger.setLevel(logging.INFO)
        logging.basicConfig()
        self.logger = logger
        
        self.mixs_log_importer = MixsLogImporter(raw_log_path = self.raw_log_path,
                                                 json_usrs_log_path = self.json_usrs_log_path,
                                                 file_filters = self.file_filters
                                                 )
        self.user_all_logs_converter = UserAllLogsConverter(json_usrs_log_path = self.json_usrs_log_path)
        self.transporter = MixsLogTransporter(local_data_path = self.local_data_path)

        pass
    
    def control(self, ):
        """
        control
        """

        self.logger.info("controll starts")
        st = time.time()

        # import
        self.mixs_log_importer.imports()

        # convert
        self.user_all_logs_converter.convert()

        # transport
        self.transporter.transport()

        et = time.time()
        self.logger.info("total time: %f[s]" % (et-st))
        self.logger.info("controll finished")
        pass

    pass

def main():
    controller = LauncherLogController()
    controller.control()

    pass

if __name__ == '__main__':
    main()
    
