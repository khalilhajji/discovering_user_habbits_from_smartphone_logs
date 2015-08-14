#!/usr/bin/env python

import logging
import glob
import json
import time
from user_log_validator import UserLogValidator
from app_log_validator import AppLogValidator
from coordinator import Coordinator

class AllInOneLauncherJsonLogCoordinator(Coordinator):
    """
    Coordinator coordinates all_in_one json log to all_in_one_validated json log from two aspects,
    validating user and validating application.

    see Validator Class in more detail for validation process.
    """
    #src_paths = "/data/mixs_logs/json/usrs/*/all/all_in_one_log.json"
    src_paths = "/speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_launcher_logs/json/*/all/all_in_one_log.json"    

    dst_filename = "all_in_one_validated_log.json"

    def __init__(self, src_paths = src_paths):
        """
        - `src_path`: src path in which all_in_one json log for a user is coordinated with validator.
        """

        # logger
        logger = logging.getLogger("AllInOneLauncherJsonLogCoordinator")
        logger.setLevel(logging.INFO)
        logging.basicConfig()
        self.logger = logger

        self.logger.info("init starts")

        self.src_paths = src_paths
        self.user_log_validator = UserLogValidator()
        self.logger.info("init finished")

        
        pass

    def coordinate(self, ):
        """
        coordinate all_in_one json file with (app, user)-validator
        """
        st = time.time()
        self.logger.info("coordinate starts")

        paths = glob.glob(self.src_paths)
        
        for path in paths:
            self.logger.info("processing user=%s" % path)
            # input data
            fpin = open(path, "r")
            user_log = json.load(fpin)

            # validate user
            if not self.user_log_validator.validate_user(user_log):
                continue

            # validate appe
            ## no need to validate an applitcaiton since launcher logger does not log lockscreen/launcher app(itself).
            
            parent_dir = "/".join(path.split("/")[0:-1])
            fpout = open("%s/%s" % (parent_dir, self.dst_filename), "w")
            json.dump(user_log, fpout)
            fpout.close()
            fpin.close()
            pass
        et = time.time()
        self.logger.info("%f [s]" % (et - st))
        self.logger.info("coordinate finished")
        
        pass
    pass

def main():

    #src_paths = "/data/mixs_launcher_logs/json/*/all/all_in_one_log.json"
    src_paths = "/speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_launcher_logs/json/*/all/all_in_one_log.json"     

    coordinator = AllInOneLauncherJsonLogCoordinator(src_paths = src_paths)
    coordinator.coordinate()
    # INFO:AllInOneLauncherJsonLogCoordinator:271.243620 [s] with dataset ending at 9/B

if __name__ == '__main__':
    main()
    
