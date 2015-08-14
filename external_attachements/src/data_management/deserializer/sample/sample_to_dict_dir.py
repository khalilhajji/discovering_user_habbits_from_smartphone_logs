#!/usr/bin/python
import sys,os
# NOTE: add path of LogData_pb2.py to PYTHONPATH
#abs_path = os.path.dirname(os.path.abspath(__file__))
#relative_path = "../../../../java/com/sony/voyagent/mixs/entity/proto/"
#proto_path = "%s/%s" % (abs_path, relative_path)
#sys.path.append(proto_path)
import LogData_pb2
import gzip
import glob
from protobuf_to_dict import protobuf_to_dict

# arg check
if len(sys.argv) != 3:
    print "Usage:", "python", sys.argv[0], "/path/to/dir", "filter"
    sys.exit(1)

# read from serialized file
log_datas = LogData_pb2.LogDatas()
dir=sys.argv[1]
filter=sys.argv[2]
glob_str = dir + "/*" + filter + "*"

files = glob.glob(glob_str)
for f in files:
    try:
        # ungzip
        fpin = gzip.open(f, "rb")
        content = fpin.read()
        fpin.close()
        
        # deseriazlie
        log_datas.ParseFromString(content)
        
        # to dict
        ################################################################
        # NOTE
        # $ git clone https://github.com/benhodgson/protobuf-to-dict
        # before using
        ################################################################
        log_datas_dict = protobuf_to_dict(log_datas)
        print "-----", f, "-----"
        #print log_datas_dict
        #print log_datas_dict.keys()
        for data in log_datas_dict["logInfo"]:
            #print data["event"]["seq"], data["appLaunch"], data["location"]
            print data["event"]["seq"], data.keys()
            pass
        print "-----------------"        
    except IOError:
        #print sys.argv[1] + ": Could not open file.  Creating a new one."
        pass

    except KeyError:
        #print sys.argv[1] + ": Could not file key."
        pass
