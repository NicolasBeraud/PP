import unittest
from jbis import Jbi
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
        file = Jbi("u_tourne3.APT", "DEMO", True, False, 90)
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

    def test_tourne_AB(self):
        file = Jbi("u_tourne4.APT", "DEMO", True, True, 90)
        print(file.files)
        for name in file.files:
            print(name)
            self.assertTrue(os.path.exists(name))
            self.assertTrue(compare(name, "result/" + name))

    def test_tourne_AB(self):
        self.classic_test("u_incl_bra.APT", False, False, 0)

        self.classic_test("u_incl_braA0.APT", True, False, 0)
        self.classic_test("u_incl_braA1.APT", True, False, 90)
        self.classic_test("u_incl_braA2.APT", True, False, 180)
        self.classic_test("u_incl_braA3.APT", True, False, 270)

        self.classic_test("u_incl_braAB0.APT", True, True, 90)
        self.classic_test("u_incl_braAB1.APT", True, True, -90)
        self.classic_test("u_incl_braAB3.APT", True, True, -90)


    def classic_test(self, file_name: str, with_A, with_B, default_angle):
        file = Jbi(file_name, "DEMO", with_A, with_B, default_angle)
        print(file.files)
        for name in file.files:
            print(name)
            self.assertTrue(os.path.exists(name))
            self.assertTrue(compare(name, "result/" + name))



if __name__ == '__main__':
    unittest.main()
