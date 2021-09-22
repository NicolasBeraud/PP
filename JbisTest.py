import unittest
from Jbis import Jbi
from Jbis_compare import compare
import os.path


class JbisTest(unittest.TestCase):

    def test_no_rotation(self):
        file = Jbi("u_angle.APT", "DEMO", False)
        print(file.files)
        for name in file.files:
            print(name)
            self.assertTrue(os.path.exists(name))
            self.assertTrue(compare(name, "result/" + name))

#    def test_basic(self):
 #       print("toto")
  #      file = Jbi("u_test1.APT", "DEMO", False)
   #     print(file.files)
    #    for name in file.files:
     #       print(name)
      #      self.assertTrue(os.path.exists(name))
       #     self.assertTrue(compare(name, "result/" + name))

    def test_tourne(self):
        file = Jbi("u_tourne.APT", "DEMO", True)
        print(file.files)
        for name in file.files:
            print(name)
            self.assertTrue(os.path.exists(name))
            self.assertTrue(compare(name, "result/" + name))

    def test_tourne_dep_x(self):
        file = Jbi("u_tourne3.APT", "DEMO", True, 90)
        print(file.files)
        for name in file.files:
            print(name)
            self.assertTrue(os.path.exists(name))
            self.assertTrue(compare(name, "result/" + name))

    def test_tourne_no_rotaion(self):
        file = Jbi("u_tourne2.APT", "DEMO", False)
        print(file.files)
        for name in file.files:
            print(name)
            self.assertTrue(os.path.exists(name))
            self.assertTrue(compare(name, "result/" + name))

if __name__ == '__main__':
    unittest.main()
