from mfu_mru_all_info_feature_extractor import LabeledMFUMRUAllInfoFeature
import unittest
import json


class LabeledMFUMRUAllInfoFeatureTestCase(unittest.TestCase):
    """
    check MRU@1 feature.
    it should corresponds to previous label, and its value at corresponding column should be 1.0.
    """

    def setUp(self):
        
        pass
    def tearDown(self):
        pass

    def test_create_labeled_sample_1(self):

        # src path
        src_path = "/data/mixs_logs/json/usrs/357662050800388/all/all_in_one_validated_log.json"

        # read
        fpin = open(src_path)
        json_logs = json.load(fpin)
        fpin.close()
        
        # lognfo
        log_info = json_logs["logInfo"]
        time_seq = log_info.keys()
        time_seq.sort()
        
        # create data (label,features_attributes)
        data_info = LabeledMFUMRUAllInfoFeature(log_info)
        data_info.mru_ranking_at_n = 1
        data_info.make_template()

        # test
        header = data_info.header.split(",")
        ## prev event
        i = 99 
        labeled_sample = data_info.create_labeled_sample(i).split(",")
        label_prev = labeled_sample[0]
        ## current event
        i = 100 
        labeled_sample = data_info.create_labeled_sample(i).split(",")
        label = labeled_sample[0]
        sample = labeled_sample[1:]
        
        key = (("appLaunch", "mru", "%s_%d" % (label_prev, data_info.mru_ranking_at_n - 1)))
        idx = data_info.feature_attribute_index[key]
        sample_at_idx = sample[idx]

        print "-----"
        print "previous label:\t", label_prev
        print "current label:\t", label
        print "index:\t", idx
        print "header_at_idx_plus_1:\t", header[idx + 1].split("_")[2] # since header includes "label"
        print "sample_at_idx:\t", sample_at_idx
        print "-----"
        
        self.assertEqual("1.0", sample_at_idx)
        self.assertEqual(label_prev, header[idx + 1].split("_")[2])
        
        pass

    def test_create_labeled_sample_2(self):

        # src path
        src_path = "/data/mixs_logs/json/usrs/357931050918957/all/all_in_one_validated_log.json"

        # read
        fpin = open(src_path)
        json_logs = json.load(fpin)
        fpin.close()
        
        # lognfo
        log_info = json_logs["logInfo"]
        time_seq = log_info.keys()
        time_seq.sort()
        
        # create data (label,features_attributes)
        data_info = LabeledMFUMRUAllInfoFeature(log_info)
        data_info.mru_ranking_at_n = 1
        data_info.make_template()

        # test
        header = data_info.header.split(",")
        ## prev event
        i = 99 
        labeled_sample = data_info.create_labeled_sample(i).split(",")
        label_prev = labeled_sample[0]
        ## current event
        i = 100 
        labeled_sample = data_info.create_labeled_sample(i).split(",")
        label = labeled_sample[0]
        sample = labeled_sample[1:]
        
        key = (("appLaunch", "mru", "%s_%d" % (label_prev, data_info.mru_ranking_at_n - 1)))
        idx = data_info.feature_attribute_index[key]
        sample_at_idx = sample[idx]

        print "-----"
        print "previous label:\t", label_prev
        print "current label:\t", label
        print "index:\t", idx
        print "header_at_idx_plus_1:\t", header[idx + 1].split("_")[2] # since header includes "label"
        print "sample_at_idx:\t", sample_at_idx
        print "-----"
        
        self.assertEqual("1.0", sample_at_idx)
        self.assertEqual(label_prev, header[idx + 1].split("_")[2])
        
        pass

    def test_create_labeled_sample_3(self):

        # src path
        src_path = "/data/mixs_logs/json/usrs/35686805039034/all/all_in_one_validated_log.json"

        # read
        fpin = open(src_path)
        json_logs = json.load(fpin)
        fpin.close()
        
        # lognfo
        log_info = json_logs["logInfo"]
        time_seq = log_info.keys()
        time_seq.sort()
        
        # create data (label,features_attributes)
        data_info = LabeledMFUMRUAllInfoFeature(log_info)
        data_info.mru_ranking_at_n = 1
        data_info.make_template()

        # test
        header = data_info.header.split(",")
        ## prev event
        i = 99 
        labeled_sample = data_info.create_labeled_sample(i).split(",")
        label_prev = labeled_sample[0]
        ## current event
        i = 100 
        labeled_sample = data_info.create_labeled_sample(i).split(",")
        label = labeled_sample[0]
        sample = labeled_sample[1:]
        
        key = (("appLaunch", "mru", "%s_%d" % (label_prev, data_info.mru_ranking_at_n - 1)))
        idx = data_info.feature_attribute_index[key]
        sample_at_idx = sample[idx]

        print "-----"
        print "previous label:\t", label_prev
        print "current label:\t", label
        print "index:\t", idx
        print "header_at_idx_plus_1:\t", header[idx + 1].split("_")[2] # since header includes "label"
        print "sample_at_idx:\t", sample_at_idx
        print "-----"
        
        self.assertEqual("1.0", sample_at_idx)
        self.assertEqual(label_prev, header[idx + 1].split("_")[2])
        
        pass

    pass

if __name__ == "__main__":
    unittest.main()
