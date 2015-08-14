#!/user/bin/env python

import logging
import glob
import json
import sys,os
import re
import time
import datetime as dt
from validator import Validator
from collections import defaultdict

class AppLogValidator(Validator):
    """
    Applicaiton Log Validator validates launched application such that

    # if applaunch is missing, then delete such log,
    # launcher application is deleted,
    # if lockscreen application logs are included, change sequence, see _correct_seq in more detail.

    This app log validator is used ONLY for the widget logs
    """

    ## block apps
    #block_apps = {
    #    "com.google.android.googlequicksearchbox": 1,
    #    "com.coverscreen.cover": 1,
    #    "ginlemon.flowerfree": 1,
    #    "com.gau.go.launcherex": 1,
    #    "com.buzzpia.aqua.launcher.buzzhome": 1,
    #    "com.jiubang.goscreenlock": 1,
    #    #"com.sony.activityengine.app.fusedvehicledetectorapp": 1,
    #    }

    # simple block apps (e.g., launcher/home app)
    simply_blocked_apps = {
        "com.google.android.googlequicksearchbox": 1,
        "ginlemon.flowerfree": 1,
        "com.gau.go.launcherex": 1,
        "com.buzzpia.aqua.launcher.buzzhome": 1,
        "com.sony.voyagent.mixs.launcher2": 1,
        "com.sony.voyagent.mixs.hello01": 1,
        "com.sony.voyagent.mixs.icongetter": 1,
        "com.sony.voyagent.mixs.mixswidget": 1,
        "com.sony.voyagent.mixs.packager": 1,
        "com.sony.voyagent.mixs.rawdatalogger": 1,
        #"com.sony.activityengine.app.fusedvehicledetectorapp": 1,
        }

    # complex apps (i.e., lockscreen) cause app sequence to change
    changing_seq_apps = {
        "com.sony.voyagent.mixs.mixslockscreen": 1,
        "com.coverscreen.cover": 1,
        "com.jiubang.goscreenlock": 1,
        }
    
    def __init__(self, ):
        """
        """
        # logger
        logger = logging.getLogger("AppLogValidator")
        logger.setLevel(logging.INFO)
        logging.basicConfig()
        self.logger = logger

        self.logger.info("init starts")
        # init base class 
        super(AppLogValidator, self).__init__()

        self.logger.info("init finished")

        pass

    def validate_app(self, user_log):
        """
        
        Arguments:
        - `loginfo`:
        """
        
        # output data
        out_data = {}
        out_data["baseInfo"] = user_log["baseInfo"]
        out_data["logInfo"] = user_log["logInfo"]

        # simple exclusion
        out_data["logInfo"] = self._exclude_app(out_data["logInfo"])

        # correct event sequence
        out_data["logInfo"] = self._correct_seq(out_data["logInfo"])

        return out_data
        
    def _exclude_app(self, loginfo):
        """
        exclude application such as launcher app

        Arguments:
        - `appname`: application name
        """

        _loginfo = {}
        seq_t = loginfo.keys()
        seq_t.sort()
        for t in seq_t:
            if not "appLaunch" in loginfo[t]: # applaunch is missing
                continue
            appname = loginfo[t]["appLaunch"]["appName"]
            
            # exclude app
            if appname in self.simply_blocked_apps:
                pass
            else:
                _loginfo[t] = loginfo[t]
                pass
            pass

        return _loginfo

    def _correct_seq(self, loginfo):
        """
        divide loginfo into applaunch and the others and call self._correct_seq_app to the first divided part,
        then marge corrected loginfo having only applaunch and loginfo having the others.
        """

        loginfo_app = {}    # having applaunch key
        loginfo_other = {}  # having the other key

        # divide
        for t in loginfo:
            loginfo_t = loginfo[t]
            if loginfo_t["event"]["type"] == "applaunch":
                loginfo_app[t] = loginfo_t
                pass
            else:
                loginfo_other[t] = loginfo_t
            pass
            
            pass

        # correct seq app
        loginfo_app = self._correct_seq_app(loginfo_app)

        # merge
        ## t is not duplicate
        for t in loginfo_other:
            loginfo_app[t] = loginfo_other[t]
            pass

        return loginfo_app


    def _correct_seq_app(self, loginfo):
        """
        correct user log sequence as follows.
        From original sequence, 
        app_i -> changing_seq_apps[k] -> app_i -> changing_seq_apps[k] -> app_i -> changing_seq_apps[k] -> app_{j != j}.
        To 
        1. app_i -> changing_seq_apps[k] -> app_i -> changing_seq_apps[k] -> app_{j != j} ...
        2. app_i -> changing_seq_apps[k] -> app_{j != j} ...
        3. appbi -> app_{j != j} ...

        i.e., 
        sequence like app_i -> changing_seq_apps[k] -> app_i is coerced into app_i, which corresponds to 1 and 2,
        since changing_seq_apps[k] was logged differently from user intension and if changing_seq_apps[k] was not logged, app_i is the same as app_i, in other words, if changing_seq_apps[k], e.g., lockscreen applicaiton was not installed, app_i would only be logged.
        
        sequence like app_i -> changing_seq_apps[k] -> app_{j != i} is coereced into app_i -> app_{j != j} ... ,
        since changing_seq_apps[k] such as lockscreen app is logged differently from user intension.
        
        Arguments:
        - `loginfo`: user log information in which app launch events are recorded
        """

        # original log
        seq_t = loginfo.keys()
        seq_t.sort()
        seq_time_len = len(seq_t)

        # begining of boundary
        _loginfo = {}
        _loginfo[seq_t[0]] = loginfo[seq_t[0]]
        
        # middle
        i = 1
        while True:
            appname_t_minus = loginfo[seq_t[i-1]]["appLaunch"]["appName"]
            appname_t = loginfo[seq_t[i]]["appLaunch"]["appName"]
            appname_t_plus = loginfo[seq_t[i+1]]["appLaunch"]["appName"]

            # apps such as lockscreen 
            if appname_t in self.changing_seq_apps:
                if appname_t_minus == appname_t_plus:
                    # do nothing
                    i += 2
                    pass
                else:
                    # do nothing
                    i += 1
                    pass
            else:
                # add log
                _loginfo[seq_t[i]] = loginfo[seq_t[i]]
                i += 1
                pass
        
            # breaking condition
            if i >= (seq_time_len - 1):
                break
            pass

        # end boundary
        if i > (seq_time_len - 1):
            # do nothing
            pass
        else: # (i == seq_time_len) case
            appname_t = loginfo[seq_t[seq_time_len - 1]]["appLaunch"]["appName"]
            if appname_t in self.changing_seq_apps:
                # do nothing
                pass
            else:
                _loginfo[seq_t[seq_time_len - 1]] = loginfo[seq_t[seq_time_len - 1]]
            pass
        
        return _loginfo

            
    
