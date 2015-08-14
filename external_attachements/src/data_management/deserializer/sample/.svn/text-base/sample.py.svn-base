#!/usr/bin/python
import sys,os
abs_path = os.path.dirname(os.path.abspath(__file__))
relative_path = "../../../../java/com/sony/voyagent/mixs/entity/proto/"
proto_path = "%s/%s" % (abs_path, relative_path)
sys.path.append(proto_path)
import LogData_pb2
import gzip

# arg check
if len(sys.argv) != 2:
    print "Usage:", "python", sys.argv[0], "Log_DATA_FILE.gz"
    sys.exit(-1)

# read from serialized file
log_datas = LogData_pb2.LogDatas()
try:

    # ungzip
    f = gzip.open(sys.argv[1], "rb")
    content = f.read()
    f.close()

    # deseriazlie
    log_datas.ParseFromString(content)

    ## print all
    print "----- all log data -----"
    print log_datas
    print "------------------------"
    print "----- baseinfo -----"
    print log_datas.baseInfo,
    print "--------------------"
    print "----- loginfo -----"
    print log_datas.logInfo,
    print "-------------------"
    print "----- main launch app -----"
    print log_datas.mainLaunchApp,
    print "----------------------------"
    
    #print log_datas.logInfo.appLaunch
except IOError:
    print sys.argv[1] + ": Could not open file.  Creating a new one."



