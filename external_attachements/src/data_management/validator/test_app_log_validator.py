from app_log_validator import AppLogValidator
from collections import defaultdict

import unittest
import numpy as np

class TestAppLogValidator(unittest.TestCase):
    
    def setUp(self):
        self.instance = AppLogValidator()

        pass
    
    def tearDown(self):
        
        pass


    def _add_dummy_log(self, loginfo, t, appname):
        """
        
        Arguments:
        - `t`:
        - `appname`:
        """

        loginfo[t] = {}
        loginfo[t]["appLaunch"] = {}
        loginfo[t]["appLaunch"]["appName"] = appname
        
        pass

    def test_correct_seq_1(self, ):
        # com.coverscreen.cover

        # dummy data
        loginfo = {}
        self._add_dummy_log(loginfo, 0, "a")
        self._add_dummy_log(loginfo, 1, "com.coverscreen.cover")
        self._add_dummy_log(loginfo, 2, "b")
        self._add_dummy_log(loginfo, 3, "com.coverscreen.cover")
        self._add_dummy_log(loginfo, 4, "b")
        self._add_dummy_log(loginfo, 5, "com.coverscreen.cover")
        self._add_dummy_log(loginfo, 6, "b")
        self._add_dummy_log(loginfo, 7, "com.coverscreen.cover")
        self._add_dummy_log(loginfo, 8, "b")
        self._add_dummy_log(loginfo, 9, "c")
        self._add_dummy_log(loginfo, 10, "com.coverscreen.cover")
        self._add_dummy_log(loginfo, 11, "a")

        loginfo = self.instance._correct_seq(loginfo)

        # extected
        loginfo_extected = {}
        self._add_dummy_log(loginfo_extected, 0, "a")
        self._add_dummy_log(loginfo_extected, 2, "b")
        self._add_dummy_log(loginfo_extected, 9, "c")
        self._add_dummy_log(loginfo_extected, 11, "a")
        
        print "expected:", loginfo_extected
        print "actual:", loginfo
        
        self.assertEqual(loginfo_extected, loginfo)
        pass

    def test_correct_seq_2(self, ):
        # com.coverscreen.cover

        # dummy data
        loginfo = {}
        self._add_dummy_log(loginfo, 0, "a")
        self._add_dummy_log(loginfo, 1, "com.coverscreen.cover")
        self._add_dummy_log(loginfo, 2, "a")
        self._add_dummy_log(loginfo, 3, "com.coverscreen.cover")
        self._add_dummy_log(loginfo, 4, "a")
        self._add_dummy_log(loginfo, 5, "c")
        self._add_dummy_log(loginfo, 6, "d")
        self._add_dummy_log(loginfo, 7, "com.coverscreen.cover")
        self._add_dummy_log(loginfo, 8, "d")
        self._add_dummy_log(loginfo, 9, "e")
        self._add_dummy_log(loginfo, 10, "com.coverscreen.cover")
        self._add_dummy_log(loginfo, 11, "b")

        loginfo = self.instance._correct_seq(loginfo)

        # extected
        loginfo_extected = {}
        self._add_dummy_log(loginfo_extected, 0, "a")
        self._add_dummy_log(loginfo_extected, 5, "c")
        self._add_dummy_log(loginfo_extected, 6, "d")
        self._add_dummy_log(loginfo_extected, 9, "e")
        self._add_dummy_log(loginfo_extected, 11, "b")
        
        print "expected:", loginfo_extected
        print "actual:", loginfo
        
        self.assertEqual(loginfo_extected, loginfo)
        pass

    
if __name__ == '__main__':
    unittest.main()

    pass
