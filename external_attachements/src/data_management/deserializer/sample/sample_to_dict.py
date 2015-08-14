#!/usr/bin/python
import sys,os
# NOTE: add path of LogData_pb2.py to PYTHONPATH
#abs_path = os.path.dirname(os.path.abspath(__file__))
#relative_path = "../../../../java/com/sony/voyagent/mixs/entity/proto/"
#proto_path = "%s/%s" % (abs_path, relative_path)
#sys.path.append(proto_path)
import LogData_pb2
import gzip
from protobuf_to_dict import protobuf_to_dict

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
    
    # to dict
    ################################################################
    # NOTE
    # $ git clone https://github.com/benhodgson/protobuf-to-dict
    # before using
    ################################################################
    log_datas_dict = protobuf_to_dict(log_datas)
    #print log_datas_dict
    print log_datas_dict.keys()

    print "-----"
    for dat in log_datas_dict["baseInfo"]:
        print dat.keys()
        print dat
    
    print "-----"
    for dat in log_datas_dict["logInfo"]:
        print dat["appLaunch"]["seq"], dat.keys()

except IOError:
    print sys.argv[1] + ": Could not open file.  Creating a new one."



