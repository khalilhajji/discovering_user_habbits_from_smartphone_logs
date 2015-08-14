#!/usr/bin/env python

import json
import numpy as np
import time
import logging
import glob
import os
from feature_extractor import FeatureExtractor
from collections import defaultdict
import pprint   

class BasicFeaturePlusWIFIPlusNotExtractor(FeatureExtractor):
    """
    Feature extractor extracts time, loc, Wifi features, notifications and Acrivity Engine output from a validated json user log as csv format.
    """

    # uuid
    # 0 for guid generated by app
    # 1 for imei
    UID_INDEX = 1
    
    #configuration for duplicate event filtering
    DUPLICATE_FILTER = True #True=filter duplicate events; False=no filtering
    DUPLICATE_DURATION = 1000 #time (ms) under which events are considered duplicate launches
    
    # Maximum number of WIFI networks in the list odf crossed networks
    MAX_N_WNET = 1023
    
    # time
    one_day_second = 24 * 60 * 60
    seven_days_second = one_day_second * 7
    two_pi_by_one_day_second = 2 * np.pi / one_day_second
    two_pi_by_seven_days_second = 2 * np.pi / seven_days_second

    #input source and output destination
    #src_paths = "/speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_logs/json/usrs/*/all/all_in_one_validated_log.json"
    #dst_dir = "/speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_logs/DATE_eutec_widget_features"

    src_paths = "/speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_launcher_logs/json/*/all/all_in_one_validated_log.json"
    dst_dir = "/speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_launcher_logs/DATE_eutec_launcher_features"

    #notification feature creation
    mask_notification = 0;

    def __init__(self, src_paths = src_paths, dst_dir = dst_dir):
        
        """
        Arguments:
        - `src_paths`: source paths in which logs of a user are assembled to one file.
        - `dst_dir`: distination directory
        """
        super(BasicFeaturePlusWIFIPlusNotExtractor, self).__init__()
        
        logger = logging.getLogger("BasicFeatureExtractor")
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

        #show extraction filtering params
        self.logger.info("\n--------------------------- PARAMETERS USED FOR FILTERING -----------------------------")

        if self.DUPLICATE_FILTER:
            self.logger.info("Extracting data with duplicate filtering active (time=%d ms)" % self.DUPLICATE_DURATION)
        else:
            self.logger.info("Extracting data with no duplicate filtering")

        self.logger.info("\n---------------------------------------------------------------------------------------")

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

        #list of collected notifications
        notificationList = []
        
        #last activity engine result (detected motion and time)
        self.aeLast = ("unknown", 0)

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

        # Build a set wifi networks
        #dict((a[el],el) for el in reversed(range(len(a)))
        dic_wnet=defaultdict(lambda: 0)
        self.logger.info("Occurrences ---> %s" % len(time_seq))
        for t in time_seq:
            log=log_info[t];
            if "wifiAps" in log:
                wifiAps = log["wifiAps"]
                #self.logger.info("         %s" % len(wifiAps))
                for wnet in wifiAps:
                    dic_wnet[wnet["bssId"]]+=1
                    
                pass              
            pass
        pass
        list_wnet=sorted(dic_wnet, key=dic_wnet.get, reverse=True)[0:self.MAX_N_WNET] # takes the MAX_N_WNET most frequent networks

        # convert the set into dictionary of wifi networks {wnet1:idx1 , wnet2:idx2}
        #   idx is the corresponding index in the mask array
        self.dic_wnet = {list_wnet[e]:e for e in range(len(list_wnet))}
        
        #Build notification set
        dic_nots=defaultdict(lambda: 0)
        self.logger.info("Occurrences ---> %s" % len(time_seq))
        for t in time_seq:
            log=log_info[t];
            if "notifications" in log:
                notList = log["notifications"]
                #self.logger.info("         %s" % len(notList))
                for nots in notList:
                    dic_nots[nots["packageName"]]+=1 
                pass              
            pass
        pass
        list_notifications=sorted(dic_nots, key=dic_nots.get, reverse=True) # sort my frequency, but keep all
        
        # convert set into dictionary of notifications {not1:idx1 , not2:idx2}
        # idx is the corresponding index in the mask array
        self.dic_nots = {list_notifications[e]:e for e in range(len(list_notifications))}
        
        #output notification dictionary for debug purposes
        self.logger.info("Size of notification dictionary for " + str(uid) + " : " + str(len(self.dic_nots)) + " packages")
        self._displayNotificationDictionary()

        # header
        data += self._create_header()
 
        #filtering and storage for durations between last launch
        filteredAppLaunches = 0
        lastLaunchTime = defaultdict()
        lastLaunchTime["appName"] = {}

        # data handling
        for t in time_seq:
            #data comes from app launch so create line in feature file
            if 'appLaunch' in log_info[t].keys():

                ### filter duplicate app launches ###
                if self.DUPLICATE_FILTER:
                    # get launched app details
                    launchedAppName = log_info[t].get("appLaunch").get("appName")
                    launchedAppTime = log_info[t].get("appLaunch").get("createDate")

                    #check conditions for filtering
                    if launchedAppName not in lastLaunchTime["appName"]:

                        #new app, no need to filter
                        lastLaunchTime["appName"][launchedAppName] = launchedAppTime

                        l = self._create_line(log_info, t)
                        data += l
                        data += "\n"
                        pass
                    else: #known app
                        duration = launchedAppTime - lastLaunchTime["appName"][launchedAppName]
                        if ( duration >= self.DUPLICATE_DURATION ):
                            #keep it
                            l = self._create_line(log_info, t)
                            data += l
                            data += "\n"
                            pass
                        else: #drop it
                            self.logger.info(" %s dropped with %d ms since last launch" % (launchedAppName, duration))
                            filteredAppLaunches+=1
                            pass

                        lastLaunchTime["appName"][launchedAppName] = launchedAppTime
                        pass
                    pass

                else: #no filtering
                    l = self._create_line(log_info, t)
                    data += l
                    data += "\n"
                    pass

                #clear notification list/notification mask
                notificationList = []
                self.mask_notification = 0;

            else:
                #data comes from periodic event so collect notifications/last activity engine result for next feature
                #print "process periodic event"
 
                if 'notifications' in log_info[t].keys():
                    #print("notifications found")
                    notifications = log_info[t].get('notifications')
                    
                    # this list may be useful later
                    for notification in notifications:
                        posttime = notification.get('postTime')
                        creationtime = notification.get('createDate')
                        trigerApp = notification.get('packageName')
                        notificationList.append( (trigerApp, posttime, creationtime) )
                    pass

                    # notification mask
                    for notification in notifications:
                        if notification["packageName"] in self.dic_nots:
                            self.mask_notification=self.mask_notification | 1<<self.dic_nots[notification["packageName"]] # binary mask get 1 at index corresponding to notification package name
                        pass
                    pass
                pass

                #activity engine motion event
                if 'activityRecognitionResult' in log_info[t].keys():
                    #print("activity engine result found")
                    aeEvent = log_info[t].get('activityRecognitionResult')
                    
                    # save event type and time
                    aeMotionType = aeEvent.get('motion')
                    if aeMotionType=="":
                        aeMotionType="unknown" #empty field interpreted as unknown
                        pass
                    aeTime = aeEvent.get('time')
                    self.aeLast = (aeMotionType, aeTime)
                pass
            pass
        pass

        self.logger.info("Number of filtered Apps = %s" % filteredAppLaunches)
        
        # tidy and save
        data = data.strip()
        self._save(data, uid)
        pass

    def _create_line(self, log_info, t):
        """
        Arguments:
        - `src_path`: source path
        """
        
        #only create new

        l = ""
        appname = log_info[t]["appLaunch"]["appName"]
        l += appname + ","
        l += self._extract_location_xyz(log_info[t]) + ","
        l += self._convert_timestamp_2_periodic_time(t) + ","
        l += self._extract_wifi_networks(log_info[t]) + ","
        l += self._extract_notifications()  + ","
        l += self._extract_activityEngineMotion() + ","
        l += self._extract_duration(log_info[t])

        return l

    def _create_header(self, ):
        """
        """
        header = "label,lat,lon,alt,daily_periodicity_x,daily_periodicity_y,weekly_periodicity_x,weekly_periodicity_y,wifiConnectedAp_bssId,wifiAps_strongest,wifiAps_available,notifications,activityEngineMotion,duration\n"
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

    def _extract_wifi_networks(self, log):
        """
        extract wifi info.
      
        Arguments:
        - `log`: log at t
        """
        # connect wifi
        if "wifiConnectedAp" in log:
            wifiConnectedAp_bssId = log["wifiConnectedAp"]["bssId"]
            if wifiConnectedAp_bssId == "00:00:00:00:00:00":
                self.logger.debug("NaN case")
                wifiConnectedAp_bssId = "NaN" 
            pass
        else:
            self.logger.debug("NaN case")
            wifiConnectedAp_bssId = "NaN"
            pass
        mask_wnet = 0; #mask_wnet  mask converted into long
        if "wifiAps" in log:
            wifiAps = log["wifiAps"]
            ##  best network
            best_level=-10000 #initial very low value
            wifiAps_strongest = "NaN"
            for wnet in wifiAps:
                
                if wnet["bssId"] in self.dic_wnet:
                    mask_wnet=mask_wnet | 1<<self.dic_wnet[wnet["bssId"]] # binary mask get 1 at index correponding to wnet network
                if wnet["level"]>best_level: 
                    wifiAps_strongest=wnet["bssId"]
                    best_level=wnet["level"]
                pass
            pass  
            
            ## network mask
            
        else:
            self.logger.debug("NaN case")
            wifiAps_strongest = "NaN" 
            pass   
            
        return  wifiConnectedAp_bssId + "," + wifiAps_strongest + "," + str(hex(mask_wnet))
        
    def _extract_notifications(self):
        """
        extract notification info.

        Arguments:
        """   

        return str(hex(self.mask_notification))

    def _extract_activityEngineMotion(self):
        """
        process activity engine info.

        Arguments:
        """

        return str(self.aeLast[0]) #field 0 id activity motion
        
    def _extract_duration(self, log):
        """
        process duration info.

        Arguments:
        """

        # get time of app launch
        launchedTime = log.get("appLaunch").get("createDate")

        return str(launchedTime)

    def _convert_timestamp_2_periodic_time(self, timestamp):
        """
        convert ${unix time}${millisecond} to periodic information on a weekly basis.
        return as string as format x,y

        Arguments:cd py 
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

    def _displayNotificationDictionary(self):
        """
        Display notification dictionary for debug purposes
        Applies to one user only
        """

        for k, v in self.dic_nots.items():
            print k, v
            pass
        pass

def main():
    #input source and output destination
    #src_paths = "/speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_logs/json/usrs/*/all/all_in_one_validated_log.json"
    #dst_dir = "/speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_logs/DATE_eutec_widget_features"

    src_paths = "/speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_launcher_logs/json/*/all/all_in_one_validated_log.json"
    dst_dir = "/speech/dbwork/mul/reco1/AppPrediction/SonyLogging/Logs/from_TKY/pulled_from_TKY/mixs_launcher_logs/DATE_eutec_launcher_features"

    extractor = BasicFeaturePlusWIFIPlusNotExtractor(src_paths = src_paths, dst_dir = dst_dir)
    extractor.extract()

if __name__ == '__main__':
    main()
