import unittest

import shutil
import controller

class TestRaid6(unittest.TestCase):
    def setUp(self):
        self.R = controller.RAID6()
        self.text = "abcdefghijklmnopqrstuvwxyz"


    def test_writing(self):
        a, b = self.R.write_data(self.text)
        self.assertEqual(a, 0)
        self.assertEqual(b, 40)

    def test_reading(self):
        a, b = self.R.write_data(self.text)
        self.assertEqual(self.R.read_data(a, b), self.text)

    def test_recevering_disk(self):
        a, b = self.R.write_data(self.text)
        shutil.rmtree("disks/disk_3")
        self.R.recovering_disks([3])
        self.assertEqual(self.R.read_data(a, b), self.text)

    def test_recevering_disks(self):
        a, b = self.R.write_data(self.text)
        listes = [[0,1]] #,[1,2],[2,3],[3,4],[4,5],[5,0]]
        for liste in listes:
            for i in liste:
                shutil.rmtree("disks/disk_" + str(i))
            self.R.recovering_disks(liste)
            self.assertEqual(self.R.read_data(a, b), self.text)

    def test_auto_recovering(self):
        a, b = self.R.write_data(self.text)
        shutil.rmtree("disks/disk_3")
        shutil.rmtree("disks/disk_5")
        self.assertEqual(self.R.read_data(a, b), self.text)

if __name__ == '__main__':
    unittest.main()
