#!/usr/bin/env python

import sys,os
import gzip
import re
import glob
import json
import shutil
import logging
import time
from collections import defaultdict
from mixs_log_importer import MixsLogImporter
from power_sampler_log_importer import PowerSamplerLogImporter
from user_all_logs_converter import UserAllLogsConverter
from user_all_logs_summary_converter import UserAllLogsSummaryConverter
from all_users_all_logs_summary_converter import AllUsersAllLogsSummaryConverter
from app_all_logs_converter import AppAllLogsConverter
from app_all_logs_summary_converter import AppAllLogsSummaryConverter
from all_apps_all_logs_summary_converter import AllAppsAllLogsSummaryConverter
from mixs_log_transporter import MixsLogTransporter
from power_sampler_log_importer import PowerSamplerLogImporter

class Controller(object):
    """
    Controller controls sequence from downloadnig to parsing.
    As default for widget logger.
    """
    
    def __init__(self, ):
        """
        init
        """

        logger = logging.getLogger("Controller")
        logger.setLevel(logging.INFO)
        logging.basicConfig()
        self.logger = logger
        
        self.mixs_log_importer = MixsLogImporter()
        self.power_sampler_log_importer = PowerSamplerLogImporter()
        self.user_all_logs_converter = UserAllLogsConverter()
        self.user_all_logs_summary_converter = UserAllLogsSummaryConverter()
        self.all_users_all_logs_summary_converter = AllUsersAllLogsSummaryConverter()
        self.app_all_logs_converter = AppAllLogsConverter()
        self.app_all_logs_summary_converter = AppAllLogsSummaryConverter()
        self.all_apps_all_logs_summary_converter = AllAppsAllLogsSummaryConverter()
        self.transporter = MixsLogTransporter()

        pass
    
    def control(self, ):
        """
        control
        """

        self.logger.info("controll starts")
        st = time.time()

        #self.power_sampler_log_importer.imports()

        self.mixs_log_importer.imports()
        self.user_all_logs_converter.convert()
        self.user_all_logs_summary_converter.convert()
        self.all_users_all_logs_summary_converter.convert()
        
        self.app_all_logs_converter.convert()
        self.app_all_logs_summary_converter.convert()
        self.all_apps_all_logs_summary_converter.convert()

        self.transporter.transport()

        et = time.time()
        self.logger.info("total time: %f[s]" % (et-st))
        self.logger.info("controll finished")
        pass

    pass

def main():
    controller = Controller()
    controller.control()

    pass

if __name__ == '__main__':
    main()
    
