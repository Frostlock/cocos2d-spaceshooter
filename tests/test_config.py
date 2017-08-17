import unittest

from spaceshooter.config import load_config, save_config, CONFIG

class TestConfig(unittest.TestCase):

    def test_load(self):
        self.assertIsInstance(CONFIG, dict)

    def test_save(self):
        load_config()
        save_config()

    def test_nbr_of_keys(self):
        nbr_of_keys = CONFIG.keys()
        self.assertGreater(nbr_of_keys, 0)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestConfig)
    unittest.TextTestRunner(verbosity=2).run(suite)